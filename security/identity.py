
import sqlite3
from dataclasses import dataclass
from pathlib import Path


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


def initialize_identity_registry():
    """Create the persistent identity registry and register demo identities."""

    with sqlite3.connect(IDENTITY_DATABASE_PATH) as connection:
        # Store identity attributes and activation status independently of Finance.
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

        # Register new identities without resetting existing activation states.
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


def is_identity_enabled(identity_id: str) -> bool:
    """Check whether a registered identity is currently enabled."""

    # Ensure the registry exists before checking an identity's status.
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

    # Ensure that only registered identities can have their status changed.
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

        # Return False when the requested identity does not exist.
        return result.rowcount == 1


def authenticate_identity(token: str | None) -> Identity | None:
    """Resolve a credential to an enabled identity."""

    if token is None:
        return None

    # Resolve the supplied credential against the registered identities.
    identity = DEMO_IDENTITIES.get(token)

    if identity is None:
        return None

    # Disabled identities cannot authenticate with previously valid credentials.
    if not is_identity_enabled(identity.identity_id):
        return None

    return identity
