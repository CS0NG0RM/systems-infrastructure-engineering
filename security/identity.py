import hashlib
import secrets
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4


# Keep identity records separate from Finance and departmental data.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
IDENTITY_DATABASE_PATH = PROJECT_ROOT / "identity.db"


@dataclass(frozen=True)
class Identity:
    """Represent an authenticated user or service."""

    identity_id: str
    identity_type: str
    role: str


# Fictional identities for local IAM testing.
# Production systems would use an external identity provider.
DEMO_IDENTITIES = {
    "demo-employee-token": Identity("employee-001", "human", "employee"),
    "demo-finance-token": Identity("finance-001", "human", "finance"),
    "demo-strategy-token": Identity("strategy-001", "human", "strategy"),
    "demo-ai-token": Identity("ai-service-001", "service", "ai_service"),
}

def hash_credential(token: str) -> str:
    """Generate a SHA-256 fingerprint of a credential."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generate_credential() -> str:
    """Generate a cryptographically secure API credential."""
    return secrets.token_urlsafe(32)

def initialize_identity_registry():
    """Create the persistent identity registry and register demo identities."""

    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        # Store identities separately from Finance data.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS identities (
                identity_id TEXT PRIMARY KEY,
                identity_type TEXT NOT NULL,
                role TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
                    CHECK (enabled IN (0, 1))
            )
            """
        )



        # Register demo identities without resetting their status.
        connection.executemany(
            """
            INSERT OR IGNORE INTO identities (
                identity_id, identity_type, role, enabled
            )
            VALUES (?, ?, ?, 1)
            """,
            [
                (identity.identity_id, identity.identity_type, identity.role)
                for identity in DEMO_IDENTITIES.values()
            ],
        )

        # Store credentials separately for expiration and revocation.
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS credentials (
                credential_id TEXT PRIMARY KEY,
                identity_id TEXT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                revoked_at TEXT,
                FOREIGN KEY (identity_id)
                    REFERENCES identities(identity_id)
            )
            """
        )

        # Register demo credentials without replacing existing records.
        created_at = datetime.now(timezone.utc).isoformat()

        connection.executemany(
            """
            INSERT OR IGNORE INTO credentials (
                credential_id,
                identity_id,
                token_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            [
                (
                    str(uuid4()),
                    identity.identity_id,
                    hash_credential(token),
                    created_at,
                )
                for token, identity in DEMO_IDENTITIES.items()
            ],
        )

def is_identity_enabled(identity_id: str) -> bool:
    """Check whether a registered identity is currently enabled."""

    # Ensure the registry exists before checking identity status.
    initialize_identity_registry()

    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        result = connection.execute(
            """
            SELECT enabled
            FROM identities
            WHERE identity_id = ?
            """,
            (identity_id,),
        ).fetchone()

    # Unknown identities are denied by default.
    return bool(result[0]) if result is not None else False


def set_identity_enabled(identity_id: str, enabled: bool) -> bool:
    """Enable or disable a registered identity persistently."""

    if not isinstance(enabled, bool):
        raise TypeError("Identity status must be a boolean")

    # Only registered identities can have their status changed.
    initialize_identity_registry()

    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        result = connection.execute(
            """
            UPDATE identities
            SET enabled = ?
            WHERE identity_id = ?
            """,
            (int(enabled), identity_id),
        )

        return result.rowcount == 1

def rotate_credential(identity_id: str, old_token: str) -> str | None:
    """Replace an active credential without disabling its identity."""

    initialize_identity_registry()

    new_token = generate_credential()
    timestamp = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        # Revoke only the matching active credential.
        result = connection.execute(
            """
            UPDATE credentials
            SET revoked_at = ?
            WHERE identity_id = ?
              AND token_hash = ?
              AND revoked_at IS NULL
              AND (expires_at IS NULL OR expires_at > ?)
              AND EXISTS (
                  SELECT 1
                  FROM identities
                  WHERE identity_id = ?
                    AND enabled = 1
              )
            """,
            (
                timestamp,
                identity_id,
                hash_credential(old_token),
                timestamp,
                identity_id,
            ),
        )

        if result.rowcount != 1:
            return None

        # Store only the new credential's hash.
        connection.execute(
            """
            INSERT INTO credentials (
                credential_id,
                identity_id,
                token_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                identity_id,
                hash_credential(new_token),
                timestamp,
            ),
        )

    return new_token

def authenticate_identity(token: str | None) -> Identity | None:
    """Authenticate a credential against the persistent registry."""

    if not token:
        return None

    initialize_identity_registry()

    # Resolve the token hash and check both credential and identity status.
    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        result = connection.execute(
            """
            SELECT i.identity_id, i.identity_type, i.role
            FROM credentials AS c
            JOIN identities AS i ON i.identity_id = c.identity_id
            WHERE c.token_hash = ?
              AND c.revoked_at IS NULL
              AND (c.expires_at IS NULL OR c.expires_at > ?)
              AND i.enabled = 1
            """,
            (
                hash_credential(token),
                datetime.now(timezone.utc).isoformat(),
            ),
        ).fetchone()

    if result is None:
        return None

    return Identity(
        identity_id=result[0],
        identity_type=result[1],
        role=result[2],
    )
