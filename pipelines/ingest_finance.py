import csv
import sqlite3
import hashlib
from contextlib import contextmanager
from pathlib import Path

from pipelines.validate_finance import validate_transaction
from pipelines.money import eur_to_cents, cents_to_eur
from security.finance_integrity import (
    initialize_correction_approvals,
    calculate_correction_hash,
    consume_correction_approval,
)
from config import (
    DATABASE_PATH,
    DEFAULT_FINANCE_CSV,
    PROJECT_ROOT,
)

def initialize_database():
    """Create the integer-based Finance storage table."""

    from pipelines.finance_schema import create_finance_schema

    with sqlite3.connect(DATABASE_PATH) as connection:
        create_finance_schema(connection)

    print("Consulting finance database initialized successfully.")


def initialize_projects_table():
    """Create the integer-based departmental project storage table."""

    from pipelines.finance_schema import create_projects_schema

    with sqlite3.connect(DATABASE_PATH) as connection:
        create_projects_schema(connection)

    print("Department projects table initialized successfully.")


def ingest_transactions(csv_path=None):
    """Validate and import financial transactions from a selected CSV file."""

    from io import StringIO

    if csv_path is None:
        csv_path = DEFAULT_FINANCE_CSV

    # Read and fingerprint the same source content.
    file_path = Path(csv_path).resolve()
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    source_content = file_path.read_bytes()
    file_hash = hashlib.sha256(source_content).hexdigest()

    inserted = 0
    updated = 0
    unchanged = 0

    with track_ingestion_failure(relative_path, file_hash), sqlite3.connect(DATABASE_PATH) as connection:

        connection.execute("BEGIN IMMEDIATE")

        # Check ingestion history within the locked transaction.
        processed = connection.execute(
            """
            SELECT 1
            FROM finance_ingestion_history
            WHERE file_path = ?
              AND file_hash = ?
              AND status = 'completed'
            """,
            (relative_path, file_hash),
        ).fetchone()

        if processed is not None:
            print(f"Already processed, skipping: {file_path.name}")
            return

        # Parse the exact content used to calculate the fingerprint.
        with StringIO(
            source_content.decode("utf-8-sig"), newline=""
        ) as source:
            transactions = list(csv.DictReader(source))

        initialize_correction_approvals(connection)

        for transaction in transactions:

            # Reject incomplete or invalid financial records before insertion.
            validate_transaction(transaction)
            # Check whether this transaction is already in the database.
            existing = connection.execute(
                """
                SELECT 1
                FROM consulting_transactions
                WHERE transaction_id = ?
                """,
                (int(transaction["transaction_id"]),),
            ).fetchone()

            # Require an exact, unused approval before changing an existing record.
            if existing is not None:
                current_record = connection.execute(
                    """
                    SELECT
                        transaction_id,
                        transaction_date,
                        business_unit,
                        cost_center,
                        project_id,
                        client_id,
                        transaction_type,
                        category,
                        description,
                        counterparty_id,
                        amount_cents,
                        classification,
                        source_system
                    FROM consulting_transactions
                    WHERE transaction_id = ?
                    """,
                    (int(transaction["transaction_id"]),),
                ).fetchone()

                incoming_record = dict(transaction)
                incoming_record["transaction_id"] = int(
                    incoming_record["transaction_id"]
                )
                incoming_record["amount_eur"] = cents_to_eur(
                    eur_to_cents(incoming_record["amount_eur"])
                )

                current_fields = (
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

                current_values = dict(zip(current_fields, current_record))
                current_values["amount_eur"] = cents_to_eur(
                    current_values["amount_eur"]
                )

                if calculate_correction_hash(current_values) != calculate_correction_hash(incoming_record):
                    consume_correction_approval(connection, incoming_record)

            # Use parameterized SQL to insert new transactions or update corrections.
            # Identical records are left unchanged.
            cursor = connection.execute(
                """
                INSERT INTO consulting_transactions (
                    transaction_id,
                    transaction_date,
                    business_unit,
                    cost_center,
                    project_id,
                    client_id,
                    transaction_type,
                    category,
                    description,
                    counterparty_id,
                    amount_cents,
                    classification,
                    source_system
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    transaction_date = excluded.transaction_date,
                    business_unit = excluded.business_unit,
                    cost_center = excluded.cost_center,
                    project_id = excluded.project_id,
                    client_id = excluded.client_id,
                    transaction_type = excluded.transaction_type,
                    category = excluded.category,
                    description = excluded.description,
                    counterparty_id = excluded.counterparty_id,
                    amount_cents = excluded.amount_cents,
                    classification = excluded.classification,
                    source_system = excluded.source_system
                WHERE
                    consulting_transactions.transaction_date IS NOT excluded.transaction_date
                    OR consulting_transactions.business_unit IS NOT excluded.business_unit
                    OR consulting_transactions.cost_center IS NOT excluded.cost_center
                    OR consulting_transactions.project_id IS NOT excluded.project_id
                    OR consulting_transactions.client_id IS NOT excluded.client_id
                    OR consulting_transactions.transaction_type IS NOT excluded.transaction_type
                    OR consulting_transactions.category IS NOT excluded.category
                    OR consulting_transactions.description IS NOT excluded.description
                    OR consulting_transactions.counterparty_id IS NOT excluded.counterparty_id
                    OR consulting_transactions.amount_cents IS NOT excluded.amount_cents
                    OR consulting_transactions.classification IS NOT excluded.classification
                    OR consulting_transactions.source_system IS NOT excluded.source_system
                """,
                (
                    int(transaction["transaction_id"]),
                    transaction["transaction_date"],
                    transaction["business_unit"],
                    transaction["cost_center"],
                    transaction["project_id"],
                    transaction["client_id"],
                    transaction["transaction_type"],
                    transaction["category"],
                    transaction["description"],
                    transaction["counterparty_id"],
                    eur_to_cents(transaction["amount_eur"]),
                    transaction["classification"],
                    transaction["source_system"],
                ),
            )

        # Distinguish new transactions, corrections and unchanged records.
            if cursor.rowcount == 0:
                unchanged += 1
            elif existing is None:
                inserted += 1
            else:
                updated += 1

        # Record successful processing with the imported transactions.
        connection.execute(
            """
            INSERT OR REPLACE INTO finance_ingestion_history (
                file_path,
                file_hash,
                status,
                processed_at
            )
            VALUES (?, ?, 'completed', CURRENT_TIMESTAMP)
            """,
            (relative_path, file_hash),
        )

    print(f"Transactions inserted: {inserted}")
    print(f"Transactions updated: {updated}")
    print(f"Transactions unchanged: {unchanged}")

def calculate_file_hash(csv_path):
    """Calculate a SHA-256 fingerprint of a Finance export."""

    # Read the file in chunks so large exports don't fill memory.
    file_hash = hashlib.sha256()

    with Path(csv_path).open("rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            file_hash.update(chunk)

    return file_hash.hexdigest()

def record_ingestion_failure(relative_path, file_hash, error_message):
    """Save a failed import separately from the transaction batch."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            INSERT INTO finance_ingestion_history (
                file_path,
                file_hash,
                status,
                error_message,
                processed_at
            )
            VALUES (?, ?, 'failed', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(file_path, file_hash) DO UPDATE SET
                status = 'failed',
                error_message = excluded.error_message,
                processed_at = CURRENT_TIMESTAMP
            WHERE finance_ingestion_history.status != 'completed'
            """,
            (relative_path, file_hash, str(error_message)),
        )

@contextmanager
def track_ingestion_failure(relative_path, file_hash):
    """Record an import failure after the database transaction rolls back."""
    try:
        yield
    except Exception as error:
        record_ingestion_failure(relative_path, file_hash, str(error))
        raise


def initialize_ingestion_history():
    """Create and update the Finance ingestion history table."""

    # Store file fingerprints so unchanged exports can be skipped safely.
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS finance_ingestion_history (
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                error_message TEXT,
                PRIMARY KEY (file_path, file_hash)
            )
            """
        )

        columns = {
            row[1]
            for row in connection.execute(
                "PRAGMA table_info(finance_ingestion_history)"
            )
        }

        if "error_message" not in columns:
            connection.execute(
                "ALTER TABLE finance_ingestion_history ADD COLUMN error_message TEXT"
            )

def is_file_processed(csv_path):
    """Check whether this exact version of a file was imported successfully."""

    # Identify the file by its relative path and content fingerprint.
    file_path = Path(csv_path).resolve()
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
    file_hash = calculate_file_hash(file_path)

    # Only successful imports count as processed.
    with sqlite3.connect(DATABASE_PATH) as connection:
        result = connection.execute(
            """
            SELECT 1
            FROM finance_ingestion_history
            WHERE file_path = ?
              AND file_hash = ?
              AND status = 'completed'
            """,
            (relative_path, file_hash),
        ).fetchone()

    return result is not None

if __name__ == "__main__":
    # Prepare the database tables before importing financial data.
    initialize_database()
    initialize_projects_table()
    initialize_ingestion_history()
    ingest_transactions()