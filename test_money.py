from decimal import Decimal

import pytest

from pipelines.money import eur_to_cents, cents_to_eur


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("0.10", 10),
        ("0.20", 20),
        ("1250.45", 125045),
        ("-250.35", -25035),
        ("0.00", 0),
        ("12.3400", 1234),
        ("92233720368547758.07", 9223372036854775807),
        ("-92233720368547758.08", -9223372036854775808),
    ],
)
def test_exact_monetary_conversion(amount, expected):
    assert eur_to_cents(amount) == expected


@pytest.mark.parametrize(
    "amount",
    [
        "12.345",
        "-12.345",
        "NaN",
        "Infinity",
        "-Infinity",
        "invalid",
        "",
        None,
        "92233720368547758.08",
        "-92233720368547758.09",
    ],
)
def test_invalid_monetary_amounts(amount):
    with pytest.raises(ValueError):
        eur_to_cents(amount)


def test_exact_financial_addition():
    assert eur_to_cents("0.10") + eur_to_cents("0.20") == 30


def test_exact_financial_reconciliation():
    proposed = eur_to_cents("1250.45")
    invoiced = eur_to_cents("1250.46")

    assert invoiced - proposed == 1


def test_credit_note_adjustment():
    revenue = eur_to_cents("1500.45")
    credit_note = eur_to_cents("-250.35")

    assert revenue + credit_note == 125010


def test_conversion_back_to_eur():
    assert cents_to_eur(125045) == Decimal("1250.45")


@pytest.mark.parametrize("value", [1.5, "100", None, True])
def test_invalid_cent_values(value):
    with pytest.raises(ValueError):
        cents_to_eur(value)

@pytest.mark.parametrize(
    "amount",
    [
        "1e100000000",
        "-1e100000000",
        "1e-100000000",
        "-1e-100000000",
    ],
)
def test_extreme_monetary_exponents_rejected(amount):
    with pytest.raises(ValueError):
        eur_to_cents(amount)


@pytest.mark.parametrize(
    "amount",
    ["0e100000000", "0e-100000000"],
)
def test_extreme_zero_exponents(amount):
    assert eur_to_cents(amount) == 0


def test_monetary_conversion_ignores_decimal_context():
    from decimal import localcontext

    with localcontext() as context:
        context.prec = 4

        assert eur_to_cents("92233720368547758.07") == 9223372036854775807

        assert cents_to_eur(9223372036854775807) == Decimal(
            "92233720368547758.07"
        )