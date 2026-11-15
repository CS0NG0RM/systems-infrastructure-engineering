import csv
import sqlite3

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