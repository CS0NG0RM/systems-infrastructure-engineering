"""Exact monetary conversion for EUR financial records."""

from decimal import Decimal, InvalidOperation


MAX_SQLITE_INTEGER = 2**63 - 1
MIN_SQLITE_INTEGER = -(2**63)


def eur_to_cents(value) -> int:
    """Convert a monetary value into exact integer euro cents."""

    try:
        amount = Decimal(str(value))

    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError("Invalid monetary amount") from error

    if not amount.is_finite():
        raise ValueError("Monetary amount must be finite")

    if amount.is_zero():
        return 0

    # Reject extreme magnitudes before integer conversion.
    if amount.adjusted() > 16:
        raise ValueError("Monetary amount exceeds storage limits")

    if amount.adjusted() < -2:
        raise ValueError("Monetary amount exceeds cent precision")

    sign, digits, exponent = amount.as_tuple()
    shift = exponent + 2

    # Reject fractional cents while permitting trailing zeros.
    if shift < 0:
        cut = -shift

        if any(digits[-cut:]):
            raise ValueError("Monetary amount exceeds cent precision")

        digits = digits[:-cut]
        shift = 0

    cents = int("".join(str(digit) for digit in digits))
    cents *= 10**shift

    if sign:
        cents = -cents

    if not MIN_SQLITE_INTEGER <= cents <= MAX_SQLITE_INTEGER:
        raise ValueError("Monetary amount exceeds storage limits")

    return cents


def cents_to_eur(cents: int) -> Decimal:
    """Convert integer euro cents into an exact decimal amount."""

    if type(cents) is not int:
        raise ValueError("Monetary cents must be an integer")

    sign = int(cents < 0)
    digits = tuple(int(digit) for digit in str(abs(cents)))

    return Decimal((sign, digits, -2))