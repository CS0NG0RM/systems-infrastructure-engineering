import csv
import sqlite3

import pytest

from pipelines import ingest_finance


def test_transaction_corrections(tmp_path, monkeypatch, capsys):
    # Keep correction tests separate from the enterprise database.
    database_path = tmp_path / "test_enterprise.db"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()

    def import_test_transaction(filename, amount):
        csv_path = tmp_path / filename

        transaction = {
            "transaction_id": "990001",
            "transaction_date": "2026-07-01",
            "business_unit": "Strategy Consulting",
            "cost_center": "STR-001",
            "project_id": "STR-TEST-001",
            "client_id": "CL-001",
            "transaction_type": "Revenue",
            "category": "Consulting Fees",
            "description": "Correction test transaction",
            "counterparty_id": "CLIENT-001",
            "amount_eur": str(amount),
            "classification": "confidential",
            "source_system": "Test ERP",
        }

        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=transaction.keys())
            writer.writeheader()
            writer.writerow(transaction)

        ingest_finance.ingest_transactions(csv_path)
        return capsys.readouterr().out

    # First export inserts the transaction.
    first = import_test_transaction("original.csv", 12500)
    assert "Transactions inserted: 1" in first

    # Corrected export updates the existing transaction.
    second = import_test_transaction("corrected.csv", 11500)
    assert "Transactions updated: 1" in second

    # Another export with identical values makes no database changes.
    third = import_test_transaction("unchanged.csv", 11500)
    assert "Transactions unchanged: 1" in third

    with sqlite3.connect(database_path) as connection:
        records = connection.execute(
            """
            SELECT transaction_id, amount_eur
            FROM consulting_transactions
            WHERE transaction_id = 990001
            """
        ).fetchall()

    # The correction replaces the amount without duplicating the transaction.
    assert records == [(990001, 11500.0)]

def test_invalid_batch_rolls_back(tmp_path, monkeypatch):
    """Reject the entire batch if one transaction is invalid."""

    database_path = tmp_path / "test_enterprise.db"
    csv_path = tmp_path / "invalid_batch.csv"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()

    valid_transaction = {
        "transaction_id": "990002",
        "transaction_date": "2026-07-01",
        "business_unit": "Strategy Consulting",
        "cost_center": "STR-001",
        "project_id": "STR-TEST-002",
        "client_id": "CL-001",
        "transaction_type": "Revenue",
        "category": "Consulting Fees",
        "description": "Valid batch transaction",
        "counterparty_id": "CLIENT-001",
        "amount_eur": "12500",
        "classification": "confidential",
        "source_system": "Test ERP",
    }

    invalid_transaction = valid_transaction.copy()
    invalid_transaction["transaction_id"] = "990003"
    invalid_transaction["business_unit"] = ""

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=valid_transaction.keys())
        writer.writeheader()
        writer.writerows([valid_transaction, invalid_transaction])

    with pytest.raises(ValueError, match="Missing required field: business_unit"):
        ingest_finance.ingest_transactions(csv_path)

    with sqlite3.connect(database_path) as connection:
        transaction_count = connection.execute(
            "SELECT COUNT(*) FROM consulting_transactions"
        ).fetchone()[0]

        completed_count = connection.execute(
            """
            SELECT COUNT(*)
            FROM finance_ingestion_history
            WHERE status = 'completed'
            """
        ).fetchone()[0]

    assert transaction_count == 0
    assert completed_count == 0


def test_failed_import_records_error(tmp_path, monkeypatch):
    """Record a rejected import without saving its transactions."""

    database_path = tmp_path / "test_enterprise.db"
    csv_path = tmp_path / "invalid_import.csv"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()

    transaction = {
        "transaction_id": "990004",
        "transaction_date": "2026-07-01",
        "business_unit": "",
        "cost_center": "STR-001",
        "project_id": "STR-TEST-004",
        "client_id": "CL-001",
        "transaction_type": "Revenue",
        "category": "Consulting Fees",
        "description": "Invalid import test",
        "counterparty_id": "CLIENT-001",
        "amount_eur": "12500",
        "classification": "confidential",
        "source_system": "Test ERP",
    }

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=transaction.keys())
        writer.writeheader()
        writer.writerow(transaction)

    with pytest.raises(ValueError, match="Missing required field: business_unit"):
        ingest_finance.ingest_transactions(csv_path)

    with sqlite3.connect(database_path) as connection:
        history = connection.execute(
            """
            SELECT status, error_message
            FROM finance_ingestion_history
            WHERE file_path = ?
            """,
            (csv_path.name,),
        ).fetchone()

        transaction_count = connection.execute(
            "SELECT COUNT(*) FROM consulting_transactions"
        ).fetchone()[0]

    assert history == (
        "failed",
        "Missing required field: business_unit",
    )
    assert transaction_count == 0

def test_security_financial_data_poisoning(tmp_path, monkeypatch, capsys):
    """SEC-BIZ-001: Test whether a manipulated CSV can overwrite revenue."""
    database_path = tmp_path / "security_test.db"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()

    def import_csv(filename, amount):
        csv_path = tmp_path / filename

        transaction = {
            "transaction_id": "990001",
            "transaction_date": "2026-07-01",
            "business_unit": "Strategy Consulting",
            "cost_center": "STR-001",
            "project_id": "STR-TEST-001",
            "client_id": "CL-001",
            "transaction_type": "Revenue",
            "category": "Consulting Fees",
            "description": "Security test transaction",
            "counterparty_id": "CLIENT-001",
            "amount_eur": str(amount),
            "classification": "confidential",
            "source_system": "Test ERP",
        }

        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=transaction.keys())
            writer.writeheader()
            writer.writerow(transaction)

        ingest_finance.ingest_transactions(csv_path)
        capsys.readouterr()

    # Establish the legitimate financial record.
    import_csv("original.csv", 12500)

    with sqlite3.connect(database_path) as connection:
        original_amount = connection.execute(
            "SELECT amount_eur FROM consulting_transactions WHERE transaction_id = ?",
            (990001,),
        ).fetchone()[0]

    # Simulate a manipulated source file reusing the same transaction ID.
    import_csv("manipulated.csv", 1)

    with sqlite3.connect(database_path) as connection:
        modified_amount = connection.execute(
            "SELECT amount_eur FROM consulting_transactions WHERE transaction_id = ?",
            (990001,),
        ).fetchone()[0]

    print(f"SEC-BIZ-001 original amount: EUR {original_amount}")
    print(f"SEC-BIZ-001 modified amount: EUR {modified_amount}")

    assert original_amount == 12500.0
    assert modified_amount == 1.0