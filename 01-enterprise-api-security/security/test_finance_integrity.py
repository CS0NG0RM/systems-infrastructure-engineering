
"""Regression tests for financial correction approval."""

import sqlite3
import pytest

from security.finance_integrity import (
    UnapprovedCorrectionError,
    require_correction_approval,
    initialize_correction_approvals,
    calculate_correction_hash,
    create_correction_approval,
    consume_correction_approval,
)


def test_unapproved_correction_rejected():
    with pytest.raises(
        UnapprovedCorrectionError,
        match="Financial correction requires explicit approval",
    ):
        require_correction_approval(True, True, False)


@pytest.mark.parametrize(
    "existing_record, record_changed, approved",
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
    ],
)
def test_permitted_financial_operations(
    existing_record, record_changed, approved
):
    require_correction_approval(
        existing_record, record_changed, approved
    )


@pytest.fixture
def approval_database():
    db = sqlite3.connect(":memory:")
    initialize_correction_approvals(db)
    yield db
    db.close()


@pytest.fixture
def fictional_transaction():
    return {
        "transaction_id": 1001,
        "transaction_date": "2026-07-01",
        "business_unit": "Strategy Consulting",
        "cost_center": "STR-001",
        "project_id": "STR-TEST-001",
        "client_id": "CL-001",
        "transaction_type": "Revenue",
        "category": "Consulting Fees",
        "description": "Fictional correction test",
        "counterparty_id": "CLIENT-001",
        "amount_eur": 11500.0,
        "classification": "confidential",
        "source_system": "Test ERP",
    }


def test_approval_requires_authorized_finance_approver(
    approval_database,
    fictional_transaction,
    tmp_path,
    monkeypatch,
):
    from security import identity

    monkeypatch.setattr(
        identity,
        "IDENTITY_DATABASE_PATH",
        tmp_path / "test_identity.db",
    )
    identity.initialize_identity_registry()

    with pytest.raises(PermissionError):
        create_correction_approval(
            approval_database,
            fictional_transaction,
            "demo-employee-token",
        )

    with pytest.raises(PermissionError):
        create_correction_approval(
            approval_database,
            fictional_transaction,
            "demo-finance-token",
        )

    create_correction_approval(
        approval_database,
        fictional_transaction,
        "demo-finance-approver-token",
    )

    approval = approval_database.execute(
        """
        SELECT transaction_id, approved_by
        FROM finance_correction_approvals
        """
    ).fetchone()

    assert approval == (1001, "finance-approver-001")


def test_exact_approval_can_only_be_consumed_once(
    approval_database,
    fictional_transaction,
    tmp_path,
    monkeypatch,
):
    from security import identity

    monkeypatch.setattr(
        identity,
        "IDENTITY_DATABASE_PATH",
        tmp_path / "test_identity.db",
    )
    identity.initialize_identity_registry()

    create_correction_approval(
        approval_database,
        fictional_transaction,
        "demo-finance-approver-token",
    )

    consume_correction_approval(
        approval_database,
        fictional_transaction,
    )

    with pytest.raises(UnapprovedCorrectionError):
        consume_correction_approval(
            approval_database,
            fictional_transaction,
        )


def test_approval_does_not_authorize_different_transaction(
    approval_database,
    fictional_transaction,
    tmp_path,
    monkeypatch,
):
    from security import identity

    monkeypatch.setattr(
        identity,
        "IDENTITY_DATABASE_PATH",
        tmp_path / "test_identity.db",
    )
    identity.initialize_identity_registry()

    create_correction_approval(
        approval_database,
        fictional_transaction,
        "demo-finance-approver-token",
    )

    manipulated = dict(fictional_transaction, amount_eur=1.0)

    with pytest.raises(UnapprovedCorrectionError):
        consume_correction_approval(
            approval_database,
            manipulated,
        )

    # The original approval remains available for its exact transaction.
    consume_correction_approval(
        approval_database,
        fictional_transaction,
    )

    assert calculate_correction_hash(
        fictional_transaction
    ) != calculate_correction_hash(manipulated)

def test_duplicate_approval_is_rejected(
    approval_database,
    fictional_transaction,
    tmp_path,
    monkeypatch,
):
    from security import identity

    monkeypatch.setattr(
        identity,
        "IDENTITY_DATABASE_PATH",
        tmp_path / "test_identity.db",
    )
    identity.initialize_identity_registry()

    create_correction_approval(
        approval_database,
        fictional_transaction,
        "demo-finance-approver-token",
    )

    with pytest.raises(
        ValueError,
        match="already been approved",
    ):
        create_correction_approval(
            approval_database,
            fictional_transaction,
            "demo-finance-approver-token",
        )

def test_equivalent_amounts_produce_identical_hashes(fictional_transaction):
    first = dict(fictional_transaction, amount_eur="11500.10")
    second = dict(fictional_transaction, amount_eur="11500.1000")

    assert calculate_correction_hash(first) == calculate_correction_hash(second)


def test_one_cent_difference_changes_hash(fictional_transaction):
    first = dict(fictional_transaction, amount_eur="11500.10")
    second = dict(fictional_transaction, amount_eur="11500.11")

    assert calculate_correction_hash(first) != calculate_correction_hash(second)


def test_fractional_cent_hash_rejected(fictional_transaction):
    transaction = dict(fictional_transaction, amount_eur="11500.105")

    with pytest.raises(ValueError):
        calculate_correction_hash(transaction)


def test_legacy_approval_cannot_authorize_correction(
    approval_database,
    fictional_transaction,
):
    import hashlib
    import json

    legacy_record = dict(fictional_transaction)
    legacy_record["transaction_id"] = int(legacy_record["transaction_id"])
    legacy_record["amount_eur"] = float(legacy_record["amount_eur"])

    serialized = json.dumps(
        legacy_record,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    legacy_hash = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    approval_database.execute(
        """
        INSERT INTO finance_correction_approvals (
            transaction_id,
            proposed_record_hash,
            approved_by
        )
        VALUES (?, ?, ?)
        """,
        (1001, legacy_hash, "finance-approver-001"),
    )

    with pytest.raises(UnapprovedCorrectionError):
        consume_correction_approval(
            approval_database,
            fictional_transaction,
        )

    approval = approval_database.execute(
        "SELECT consumed_at FROM finance_correction_approvals"
    ).fetchone()

    assert approval == (None,)