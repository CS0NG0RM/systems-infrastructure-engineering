import csv
import sqlite3
import hashlib
from pathlib import Path

from pipelines.validate_finance import validate_transaction


# Keep project files and the database in predictable locations.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "enterprise.db"


def initialize_database():
    """Create the central Finance table if it does not already exist."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS consulting_transactions (
                transaction_id INTEGER PRIMARY KEY,
                transaction_date TEXT NOT NULL,
                business_unit TEXT NOT NULL,
                cost_center TEXT NOT NULL,
                project_id TEXT,
                client_id TEXT,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                counterparty_id TEXT,
                amount_eur REAL NOT NULL,
                classification TEXT NOT NULL,
                source_system TEXT NOT NULL
            )
        """)

    print("Consulting finance database initialized successfully.")


def initialize_projects_table():
    """Create the table used for departmental project information."""

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS department_projects (
                project_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                project_name TEXT NOT NULL,
                project_status TEXT NOT NULL,
                proposed_fee_eur REAL NOT NULL,
                budget_eur REAL NOT NULL,
                wip_eur REAL NOT NULL,
                win_probability REAL NOT NULL,
                project_manager TEXT NOT NULL,
                classification TEXT NOT NULL,
                ai_access TEXT NOT NULL
            )
        """)

    print("Department projects table initialized successfully.")


def ingest_transactions(csv_path=None):
    """Validate and import financial transactions from a selected CSV file."""

    # Use the original Finance export unless another file is provided.
    if csv_path is None:
        csv_path = PROJECT_ROOT / "data" / "consulting_finance_transactions.csv"

    csv_path = Path(csv_path)

    # Read the fictional ERP export into a list of transactions.
    with csv_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        transactions = list(reader)

    inserted = 0
    updated = 0
    unchanged = 0

    # Identify the source file before importing its transactions.
    file_path = csv_path.resolve()
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
    file_hash = calculate_file_hash(file_path)

    # Skip files whose exact contents were successfully processed before.
    if is_file_processed(file_path):
        print(f"Already processed, skipping: {file_path.name}")
        return

    # Process the import as one database transaction.
    # If validation fails, the current batch is rolled back.
    with sqlite3.connect(DATABASE_PATH) as connection:
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
                    amount_eur,
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
                    amount_eur = excluded.amount_eur,
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
                    OR consulting_transactions.amount_eur IS NOT excluded.amount_eur
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
                    float(transaction["amount_eur"]),
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

def initialize_ingestion_history():
    """Create a table to track successfully processed Finance files."""

    # Store file fingerprints so unchanged exports can be skipped safely.
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS finance_ingestion_history (
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                processed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                PRIMARY KEY (file_path, file_hash)
            )
            """
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