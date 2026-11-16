import json
import subprocess
import sys
import sqlite3
import pytest
from fastapi.testclient import TestClient

from main import app
from security import audit_log, identity as identity_module
from security.identity import (
    authenticate_identity,
    hash_credential,
    initialize_identity_registry,
    is_identity_enabled,
    set_identity_enabled,
)


@pytest.fixture(autouse=True)
def isolated_identity_database(tmp_path, monkeypatch):
    # Give each test an independent identity database.
    database_path = tmp_path / "test_identity.db"
    monkeypatch.setattr(
        identity_module,
        "IDENTITY_DATABASE_PATH",
        database_path,
    )

    # Register the fictional identities in the temporary database.
    initialize_identity_registry()


def test_registered_identity_authenticates():
    # Verify that a registered Finance credential resolves to its identity.
    identity = authenticate_identity("demo-finance-token")

    assert identity is not None
    assert identity.identity_id == "finance-001"
    assert identity.identity_type == "human"
    assert identity.role == "finance"


def test_disabled_identity_cannot_authenticate():
    # Disable the AI service identity while retaining its registered credential.
    assert set_identity_enabled("ai-service-001", False) is True

    # Verify that disabled identities cannot authenticate with existing credentials.
    assert is_identity_enabled("ai-service-001") is False
    assert authenticate_identity("demo-ai-token") is None


def test_reenabled_identity_can_authenticate():
    # Disable the AI service identity before testing its reactivation.
    set_identity_enabled("ai-service-001", False)

    # Restore the identity's active status.
    assert set_identity_enabled("ai-service-001", True) is True

    # Verify that the previously disabled identity can authenticate again.
    identity = authenticate_identity("demo-ai-token")

    assert identity is not None
    assert identity.identity_id == "ai-service-001"


def test_unknown_identity_is_disabled():
    # Unknown identities must be denied by default.
    assert is_identity_enabled("unknown-identity") is False


def test_unknown_identity_cannot_be_modified():
    # Identity lifecycle operations must reject unregistered identities.
    assert set_identity_enabled("unknown-identity", False) is False
    assert set_identity_enabled("unknown-identity", True) is False


def test_invalid_credential_cannot_authenticate():
    # Credentials not present in the identity registry must be rejected.
    assert authenticate_identity("invalid-token") is None

def test_disabled_ai_identity_cannot_access_approved_projects(
    tmp_path, monkeypatch
):
    # Keep test audit events separate from the operational security log.
    log_path = tmp_path / "security_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", log_path)

    # Disable the AI service identity before attempting API access.
    assert set_identity_enabled("ai-service-001", False) is True

    client = TestClient(app)

    # Verify that a previously valid AI credential is rejected.
    response = client.get(
        "/ai/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

    # Verify that rejected authentication generates an audit event.
    events = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["role"] == "unauthenticated"
    assert events[0]["resource"] == "ai_approved_data"
    assert events[0]["decision"] == "denied"

def test_disabling_ai_identity_does_not_affect_other_identities():
    # Disable the AI service identity without changing other account statuses.
    assert set_identity_enabled("ai-service-001", False) is True

    # Verify that the other registered identities remain enabled.
    assert is_identity_enabled("employee-001") is True
    assert is_identity_enabled("finance-001") is True
    assert is_identity_enabled("strategy-001") is True

    # Confirm that the other identities can still authenticate.
    assert authenticate_identity("demo-employee-token") is not None
    assert authenticate_identity("demo-finance-token") is not None
    assert authenticate_identity("demo-strategy-token") is not None

    # Confirm that the disabled AI service can no longer authenticate.
    assert authenticate_identity("demo-ai-token") is None

def test_disabled_identity_remains_disabled_after_registry_reinitialization():
    # Disable the AI service identity in the persistent identity registry.
    assert set_identity_enabled("ai-service-001", False) is True

    # Reinitialize the registry without resetting existing identity states.
    initialize_identity_registry()

    # Verify that the disabled identity remains unable to authenticate.
    assert is_identity_enabled("ai-service-001") is False
    assert authenticate_identity("demo-ai-token") is None

def test_disabled_identity_remains_disabled_in_new_process(
    tmp_path, monkeypatch
):
    # Use the isolated identity database created by the test fixture.
    database_path = identity_module.IDENTITY_DATABASE_PATH

    # Disable the AI service identity in the current Python process.
    assert set_identity_enabled("ai-service-001", False) is True

    # Start a separate Python process against the same database.
    script = """
import sys
from pathlib import Path
from security import identity

identity.IDENTITY_DATABASE_PATH = Path(sys.argv[1])

assert identity.is_identity_enabled("ai-service-001") is False
assert identity.authenticate_identity("demo-ai-token") is None

print("Persistent identity revocation verified")
"""

    result = subprocess.run(
        [sys.executable, "-c", script, str(database_path)],
        capture_output=True,
        text=True,
        check=True,
    )

    # Verify that the new process independently rejected the disabled identity.
    assert "Persistent identity revocation verified" in result.stdout

def test_credential_hashing():
    # The same credential must always produce the same fingerprint.
    token = "test-service-credential"

    first_hash = hash_credential(token)
    second_hash = hash_credential(token)

    assert first_hash == second_hash
    assert first_hash != token

    # Different credentials must produce different fingerprints.
    assert hash_credential("another-credential") != first_hash
    assert len(first_hash) == 64

def test_revoked_credential_cannot_authenticate():
    """Revoked credentials cannot authenticate an enabled identity."""

    token = "demo-finance-token"

    # Confirm the credential works before revocation.
    assert authenticate_identity(token) is not None

    with sqlite3.connect(identity_module.IDENTITY_DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE credentials
            SET revoked_at = ?
            WHERE token_hash = ?
            """,
            (
                "2026-11-16T00:00:00+00:00",
                hash_credential(token),
            ),
        )

    # Revocation must not disable the underlying identity.
    assert is_identity_enabled("finance-001") is True
    assert authenticate_identity(token) is None

def test_expired_credential_cannot_authenticate():
    """Expired credentials cannot authenticate an enabled identity."""

    token = "demo-strategy-token"

    # Confirm the credential is valid before expiration.
    assert authenticate_identity(token) is not None

    with sqlite3.connect(identity_module.IDENTITY_DATABASE_PATH) as connection:
        connection.execute(
            """
            UPDATE credentials
            SET expires_at = ?
            WHERE token_hash = ?
            """,
            (
                "2020-01-01T00:00:00+00:00",
                hash_credential(token),
            ),
        )

    # Expiration must not disable the underlying identity.
    assert is_identity_enabled("strategy-001") is True
    assert authenticate_identity(token) is None