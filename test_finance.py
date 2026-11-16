import csv
from pathlib import Path

import pytest

from pipelines.validate_finance import validate_transaction


# Use the synthetic Finance dataset for validation tests.
DATA_FILE = (
    Path(__file__).resolve().parent
    / "data"
    / "consulting_finance_transactions.csv"
)


def sample_transaction():
    """Load a sample transaction for testing."""
    with DATA_FILE.open(newline="", encoding="utf-8-sig") as file:
        return next(csv.DictReader(file))


def test_valid_financial_transaction():
    transaction = sample_transaction()

    assert validate_transaction(transaction) is True


def test_invalid_financial_amount():
    transaction = sample_transaction()
    transaction["amount_eur"] = "ABC"

    # Malformed financial amounts must be rejected.
    with pytest.raises(ValueError, match="Invalid transaction amount"):
        validate_transaction(transaction)


def test_missing_business_unit():
    transaction = sample_transaction()
    transaction["business_unit"] = ""

    with pytest.raises(ValueError, match="Missing required field: business_unit"):
        validate_transaction(transaction)


def test_invalid_security_classification():
    transaction = sample_transaction()
    transaction["classification"] = "unclassified-secret"

    # Unknown classifications must not be treated as safe.
    with pytest.raises(ValueError, match="Invalid data classification"):
        validate_transaction(transaction)


def test_invalid_transaction_date():
    transaction = sample_transaction()
    transaction["transaction_date"] = "2026-15-45"

    with pytest.raises(ValueError, match="Invalid transaction date"):
        validate_transaction(transaction)

@pytest.mark.parametrize(
    "transaction_type, category, amount",
    [
        ("Revenue", "Credit Note", "-2000"),
        ("Revenue", "Revenue Reversal", "-12500"),
        ("Expense", "Expense Refund", "-500"),
    ],
)

def test_valid_negative_financial_adjustments(
    transaction_type, category, amount
):
    # Approved adjustments can reduce revenue or expenses.
    transaction = sample_transaction()
    transaction["transaction_type"] = transaction_type
    transaction["category"] = category
    transaction["amount_eur"] = amount

    assert validate_transaction(transaction) is True


@pytest.mark.parametrize(
    "transaction_type, category, amount",
    [
        ("Revenue", "Consulting Fees", "-5000"),
        ("Expense", "Operating Costs", "-500"),
        ("Revenue", "Credit Note", "0"),
    ],
)

def test_invalid_financial_adjustments(
    transaction_type, category, amount
):
    # Reject unexplained negative amounts and zero-value transactions.
    transaction = sample_transaction()
    transaction["transaction_type"] = transaction_type
    transaction["category"] = category
    transaction["amount_eur"] = amount

    with pytest.raises(ValueError, match="Invalid transaction amount"):
        validate_transaction(transaction)


def test_required_field_cannot_be_none():
    """Reject missing values in mandatory transaction fields."""

    transaction = sample_transaction()
    transaction["business_unit"] = None

    with pytest.raises(ValueError, match="Missing required field: business_unit"):
        validate_transaction(transaction)