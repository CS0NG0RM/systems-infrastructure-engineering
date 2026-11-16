from datetime import date
from decimal import Decimal, InvalidOperation


# Only recognised transaction types and sensitivity levels are accepted.
ALLOWED_CLASSIFICATIONS = {"public", "internal", "confidential", "restricted"}
ALLOWED_TRANSACTION_TYPES = {"Revenue", "Expense"}
# Negative amounts are permitted only for recognised financial adjustments.
NEGATIVE_AMOUNT_CATEGORIES = {
    "Revenue": {"Credit Note", "Revenue Reversal"},
    "Expense": {"Expense Refund"},
}


def validate_transaction(transaction):
    """Check that a financial record meets our data-quality rules."""

    # These fields are required for reliable reporting and data classification.
    required_fields = [
        "transaction_id",
        "transaction_date",
        "business_unit",
        "cost_center",
        "transaction_type",
        "category",
        "description",
        "amount_eur",
        "classification",
        "source_system",
    ]

    # Reject records with missing or empty mandatory fields.
    for field in required_fields:
        value = transaction.get(field)

        if value is None or not str(value).strip():
            raise ValueError(f"Missing required field: {field}")

    # Transaction IDs must be positive integers.
    try:
        transaction_id = int(transaction["transaction_id"])

        if transaction_id <= 0:
            raise ValueError("Transaction ID must be positive")

    except (TypeError, ValueError):
        raise ValueError("Invalid transaction ID")

    # Ensure dates follow a valid ISO calendar format.
    try:
        date.fromisoformat(transaction["transaction_date"])

    except (TypeError, ValueError):
        raise ValueError("Invalid transaction date")

    # Decimal avoids floating-point issues during financial validation.
    try:
        amount = Decimal(transaction["amount_eur"])

        if not amount.is_finite():
            raise ValueError("Amount must be finite")

        # Zero amounts are invalid, and negative amounts need an approved category.
        if amount == 0:
            raise ValueError("Amount cannot be zero")

        if amount < 0:
            transaction_type = transaction["transaction_type"]
            category = transaction["category"]

            if category not in NEGATIVE_AMOUNT_CATEGORIES.get(transaction_type, set()):
                raise ValueError("Negative amount requires an approved adjustment category")

    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid transaction amount")

    # Prevent unexpected transaction categories from entering financial reports.
    if transaction["transaction_type"] not in ALLOWED_TRANSACTION_TYPES:
        raise ValueError("Invalid transaction type")

    # Reject unknown classifications rather than treating them as non-sensitive.
    if transaction["classification"] not in ALLOWED_CLASSIFICATIONS:
        raise ValueError("Invalid data classification")

    return True