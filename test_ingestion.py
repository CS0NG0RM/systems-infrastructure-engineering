import csv
import sqlite3

import pytest

from pipelines import ingest_finance
from security import identity
from security.finance_integrity import create_correction_approval


def test_transaction_corrections(tmp_path, monkeypatch, capsys):
    # Keep correction tests separate from the enterprise database.
    database_path = tmp_path / "test_enterprise.db"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)
    monkeypatch.setattr(
    identity,
    "IDENTITY_DATABASE_PATH",
    tmp_path / "test_identity.db",
                        )
    identity.initialize_identity_registry()

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

    # Prepare the exact proposed correction.
    proposed_correction = {
        "transaction_id": 990001,
        "transaction_date": "2026-07-01",
        "business_unit": "Strategy Consulting",
        "cost_center": "STR-001",
        "project_id": "STR-TEST-001",
        "client_id": "CL-001",
        "transaction_type": "Revenue",
        "category": "Consulting Fees",
        "description": "Correction test transaction",
        "counterparty_id": "CLIENT-001",
        "amount_eur": 11500.0,
        "classification": "confidential",
        "source_system": "Test ERP",
    }

    # Authorize the exact correction.
    with sqlite3.connect(database_path) as connection:
        create_correction_approval(
            connection,
            proposed_correction,
            "demo-finance-approver-token",
        )

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


def test_security_financial_data_poisoning(
    tmp_path, monkeypatch, capsys
):
    """SEC-BIZ-001: Reject unauthorized financial transaction manipulation."""
    database_path = tmp_path / "security_test.db"

    monkeypatch.setattr(
        ingest_finance, "PROJECT_ROOT", tmp_path
    )
    monkeypatch.setattr(
        ingest_finance, "DATABASE_PATH", database_path
    )

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

        with csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=transaction.keys()
            )
            writer.writeheader()
            writer.writerow(transaction)

        ingest_finance.ingest_transactions(csv_path)
        return capsys.readouterr().out

    # Establish the legitimate financial record.
    import_csv("original.csv", 12500)

    with sqlite3.connect(database_path) as connection:
        original_amount = connection.execute(
            """
            SELECT amount_eur
            FROM consulting_transactions
            WHERE transaction_id = ?
            """,
            (990001,),
        ).fetchone()[0]

    # Attempt an unauthorized financial manipulation.
    from security.finance_integrity import UnapprovedCorrectionError

    with pytest.raises(UnapprovedCorrectionError):
        import_csv("manipulated.csv", 1)

    with sqlite3.connect(database_path) as connection:
        rejected_amount = connection.execute(
            """
            SELECT amount_eur
            FROM consulting_transactions
            WHERE transaction_id = ?
            """,
            (990001,),
        ).fetchone()[0]

        failed_import = connection.execute(
            """
            SELECT status
            FROM finance_ingestion_history
            WHERE file_path = ?
            """,
            ("manipulated.csv",),
        ).fetchone()

    print(f"SEC-BIZ-001 original amount: EUR {original_amount}")
    print(f"SEC-BIZ-001 amount after rejected manipulation: EUR {rejected_amount}")

    assert original_amount == 12500.0
    assert rejected_amount == 12500.0
    assert failed_import == ("failed",)

def test_approved_financial_correction(
    tmp_path, monkeypatch, capsys
):
    """Verify an authorized correction succeeds through actual ingestion."""

    database_path = tmp_path / "approved_correction.db"

    monkeypatch.setattr(
        ingest_finance, "PROJECT_ROOT", tmp_path
    )
    monkeypatch.setattr(
        ingest_finance, "DATABASE_PATH", database_path
    )
    monkeypatch.setattr(
    identity,
    "IDENTITY_DATABASE_PATH",
    tmp_path / "test_identity.db",
    )

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()
    identity.initialize_identity_registry()

    def create_csv(filename, amount):
        csv_path = tmp_path / filename

        transaction = {
            "transaction_id": "990010",
            "transaction_date": "2026-07-01",
            "business_unit": "Strategy Consulting",
            "cost_center": "STR-001",
            "project_id": "STR-TEST-010",
            "client_id": "CL-001",
            "transaction_type": "Revenue",
            "category": "Consulting Fees",
            "description": "Approved correction test",
            "counterparty_id": "CLIENT-001",
            "amount_eur": str(amount),
            "classification": "confidential",
            "source_system": "Test ERP",
        }

        with csv_path.open(
            "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=transaction.keys()
            )
            writer.writeheader()
            writer.writerow(transaction)

        return csv_path, transaction

    # Insert the original financial transaction.
    original_csv, _ = create_csv("approved_original.csv", 12500)
    ingest_finance.ingest_transactions(original_csv)
    capsys.readouterr()

    # Prepare the exact proposed correction.
    corrected_csv, corrected_record = create_csv(
        "approved_correction.csv", 11500
    )

    # Authorize the correction using the dedicated Finance approver.
    with sqlite3.connect(database_path) as connection:
        from security.finance_integrity import (
            initialize_correction_approvals,
        )

        initialize_correction_approvals(connection)

        create_correction_approval(
            connection,
            corrected_record,
            "demo-finance-approver-token",
        )

    # Process the approved correction through the real ingestion function.
    output = ingest_finance.ingest_transactions(corrected_csv)
    captured = capsys.readouterr().out

    with sqlite3.connect(database_path) as connection:
        amount = connection.execute(
            """
            SELECT amount_eur
            FROM consulting_transactions
            WHERE transaction_id = ?
            """,
            (990010,),
        ).fetchone()[0]

        approval = connection.execute(
            """
            SELECT consumed_at
            FROM finance_correction_approvals
            WHERE transaction_id = ?
            """,
            (990010,),
        ).fetchone()

    assert "Transactions updated: 1" in captured
    assert amount == 11500.0
    assert approval is not None
    assert approval[0] is not None

    print("PASS: Authorized correction accepted")
    print("PASS: Financial amount updated to EUR 11,500")
    print("PASS: Approval consumption recorded")


    # Simulate restoration of the original record before a replay attempt.
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            UPDATE consulting_transactions
            SET amount_eur = ?
            WHERE transaction_id = ?
            """,
            (12500.0, 990010),
        )

    # Create a new import file containing the previously approved correction.
    replay_csv, _ = create_csv(
        "approved_correction_replay.csv", 11500
    )

    from security.finance_integrity import UnapprovedCorrectionError

    # The previously consumed approval must not authorize another correction.
    with pytest.raises(UnapprovedCorrectionError):
        ingest_finance.ingest_transactions(replay_csv)

    # Verify that the restored financial record remains unchanged.
    with sqlite3.connect(database_path) as connection:
        replay_amount = connection.execute(
            """
            SELECT amount_eur
            FROM consulting_transactions
            WHERE transaction_id = ?
            """,
            (990010,),
        ).fetchone()[0]

        replay_status = connection.execute(
            """
            SELECT status
            FROM finance_ingestion_history
            WHERE file_path = ?
            """,
            ("approved_correction_replay.csv",),
        ).fetchone()

    assert replay_amount == 12500.0
    assert replay_status == ("failed",)

    print("PASS: Previously consumed approval rejected on replay")
    print("PASS: Original financial amount preserved after replay")

def test_failed_correction_rolls_back_approval_consumption(
    tmp_path, monkeypatch
):
    """A failed financial update must not consume its approval."""

    database_path = tmp_path / "atomicity_test.db"
    csv_path = tmp_path / "correction.csv"

    monkeypatch.setattr(ingest_finance, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(ingest_finance, "DATABASE_PATH", database_path)
    monkeypatch.setattr(
        identity, "IDENTITY_DATABASE_PATH", tmp_path / "identity.db"
    )

    ingest_finance.initialize_database()
    ingest_finance.initialize_ingestion_history()
    identity.initialize_identity_registry()

    transaction = {
        "transaction_id": "990020",
        "transaction_date": "2026-07-01",
        "business_unit": "Strategy Consulting",
        "cost_center": "STR-001",
        "project_id": "STR-TEST-020",
        "client_id": "CL-001",
        "transaction_type": "Revenue",
        "category": "Consulting Fees",
        "description": "Atomicity regression test",
        "counterparty_id": "CLIENT-001",
        "amount_eur": "12500",
        "classification": "confidential",
        "source_system": "Test ERP",
    }

    def write_csv(record):
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=record.keys())
            writer.writeheader()
            writer.writerow(record)

    # Insert the original transaction.
    write_csv(transaction)
    ingest_finance.ingest_transactions(csv_path)

    # Prepare and authorize a changed financial amount.
    corrected = dict(transaction, amount_eur="11500")
    corrected_csv = tmp_path / "approved_correction.csv"

    with corrected_csv.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=corrected.keys())
        writer.writeheader()
        writer.writerow(corrected)

    with sqlite3.connect(database_path) as connection:
        create_correction_approval(
            connection,
            corrected,
            "demo-finance-approver-token",
        )

        # This trigger deliberately rejects the financial update.
        connection.execute("""
            CREATE TRIGGER reject_financial_update
            BEFORE UPDATE ON consulting_transactions
            BEGIN
                SELECT RAISE(ABORT, 'Simulated financial update failure');
            END
        """)

    # Approval consumption happens before the deliberately failed update.
    with pytest.raises(
        sqlite3.IntegrityError,
        match="Simulated financial update failure",
    ):
        ingest_finance.ingest_transactions(corrected_csv)

    with sqlite3.connect(database_path) as connection:
        amount = connection.execute(
            """
            SELECT amount_eur
            FROM consulting_transactions
            WHERE transaction_id = 990020
            """
        ).fetchone()[0]

        consumed_at = connection.execute(
            """
            SELECT consumed_at
            FROM finance_correction_approvals
            WHERE transaction_id = 990020
            """
        ).fetchone()[0]

        failure_status = connection.execute(
            """
            SELECT status
            FROM finance_ingestion_history
            WHERE file_path = ?
            """,
            ("approved_correction.csv",),
        ).fetchone()

    assert amount == 12500.0
    assert consumed_at is None
    assert failure_status == ("failed",)
