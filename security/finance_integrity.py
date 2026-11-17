"""Security policy for financial transaction corrections."""
import sqlite3

class UnapprovedCorrectionError(ValueError):
    """Raised when a financial correction lacks approval."""


def require_correction_approval(
    existing_record: bool,
    record_changed: bool,
    approved: bool,
) -> None:
    """Require approval before changing an existing financial record."""

    if existing_record and record_changed and not approved:
        raise UnapprovedCorrectionError(
            "Financial correction requires explicit approval"
        )

def initialize_correction_approvals(connection) -> None:
    """Create the registry for explicitly approved financial corrections."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS finance_correction_approvals (
            transaction_id INTEGER NOT NULL,
            proposed_record_hash TEXT NOT NULL,
            approved_by TEXT NOT NULL,
            approved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            consumed_at TEXT,
            PRIMARY KEY (transaction_id, proposed_record_hash)
        )
        """
    )

def calculate_correction_hash(transaction: dict) -> str:
    """Fingerprint the exact proposed financial transaction values."""
    import hashlib
    import json

    fields = (
        "transaction_id",
        "transaction_date",
        "business_unit",
        "cost_center",
        "project_id",
        "client_id",
        "transaction_type",
        "category",
        "description",
        "counterparty_id",
        "amount_eur",
        "classification",
        "source_system",
    )

    canonical_record = {
        field: transaction[field]
        for field in fields
    }

    canonical_record["transaction_id"] = int(
        canonical_record["transaction_id"]
    )
    # Use exact integer cents for financial approval fingerprints.
    from pipelines.money import eur_to_cents

    canonical_record["amount_cents"] = eur_to_cents(
        canonical_record.pop("amount_eur")
    )

    # Distinguish exact monetary fingerprints from legacy approvals.
    canonical_record["hash_version"] = 2

    serialized = json.dumps(
        canonical_record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def consume_correction_approval(
    connection,
    transaction: dict,
) -> None:
    """Require and consume an exact, unused correction approval."""

    transaction_id = int(transaction["transaction_id"])
    proposed_hash = calculate_correction_hash(transaction)

    cursor = connection.execute(
        """
        UPDATE finance_correction_approvals
        SET consumed_at = CURRENT_TIMESTAMP
        WHERE transaction_id = ?
          AND proposed_record_hash = ?
          AND consumed_at IS NULL
        """,
        (transaction_id, proposed_hash),
    )

    if cursor.rowcount != 1:
        raise UnapprovedCorrectionError(
            "Financial correction requires an exact, unused approval"
        )

def create_correction_approval(
    connection,
    transaction: dict,
    approver_token: str,
) -> None:
    """Register a correction approval from an authenticated Finance approver."""

    from security.identity import authenticate_identity

    approver = authenticate_identity(approver_token)

    if approver is None:
        raise PermissionError("Authenticated approver required")

    if approver.identity_type != "human":
        raise PermissionError("Human Finance approver required")

    if approver.role != "finance_approver":
        raise PermissionError("Finance approver role required")

    try:
        connection.execute(
            """
            INSERT INTO finance_correction_approvals (
                transaction_id,
                proposed_record_hash,
                approved_by
            )
            VALUES (?, ?, ?)
            """,
            (
                int(transaction["transaction_id"]),
                calculate_correction_hash(transaction),
                approver.identity_id,
            ),
        )
    except sqlite3.IntegrityError as error:
        raise ValueError(
            "This exact financial correction has already been approved"
        ) from error

