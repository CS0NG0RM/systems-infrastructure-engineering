"""Database-level financial integrity tests."""

import sqlite3

import pytest

from pipelines.finance_schema import (
    create_finance_schema,
    create_projects_schema,
)


@pytest.fixture
def database():
    connection = sqlite3.connect(":memory:")
    create_finance_schema(connection)
    create_projects_schema(connection)
    yield connection
    connection.close()


def insert_transaction(connection, amount):
    connection.execute(
        """
        INSERT INTO consulting_transactions (
            transaction_id,
            transaction_date,
            business_unit,
            cost_center,
            transaction_type,
            category,
            description,
            amount_cents,
            classification,
            source_system
        )
        VALUES (
            1001, '2026-07-01', 'Strategy Consulting',
            'STR-001', 'Revenue', 'Consulting Fees',
            'Fictional financial test', ?, 'confidential',
            'Test ERP'
        )
        """,
        (amount,),
    )


def insert_project(connection, fee, budget, wip):
    connection.execute(
        """
        INSERT INTO department_projects (
            project_id,
            client_id,
            project_name,
            project_status,
            proposed_fee_cents,
            budget_cents,
            wip_cents,
            win_probability,
            project_manager,
            classification,
            ai_access
        )
        VALUES (
            'STR-001', 'CL-001', 'Fictional project',
            'Active', ?, ?, ?, 0.9,
            'Test Manager', 'confidential', 'denied'
        )
        """,
        (fee, budget, wip),
    )


@pytest.mark.parametrize(
    "amount",
    [
        125045,
        -25035,
        9223372036854775807,
        -9223372036854775808,
    ],
)
def test_exact_transaction_storage(database, amount):
    insert_transaction(database, amount)

    result = database.execute(
        """
        SELECT amount_cents, typeof(amount_cents)
        FROM consulting_transactions
        """
    ).fetchone()

    assert result == (amount, "integer")


@pytest.mark.parametrize(
    "amount",
    [125045.5, "invalid", None, b"100"],
)
def test_invalid_transaction_storage_rejected(database, amount):
    with pytest.raises(sqlite3.IntegrityError):
        insert_transaction(database, amount)


def test_exact_project_storage(database):
    insert_project(database, 8500000, 4800000, 1250000)

    result = database.execute(
        """
        SELECT proposed_fee_cents, budget_cents, wip_cents
        FROM department_projects
        """
    ).fetchone()

    assert result == (8500000, 4800000, 1250000)


@pytest.mark.parametrize(
    "fee, budget, wip",
    [
        (8500000.5, 4800000, 1250000),
        (8500000, 4800000.5, 1250000),
        (8500000, 4800000, 1250000.5),
    ],
)
def test_fractional_project_cents_rejected(
    database, fee, budget, wip
):
    with pytest.raises(sqlite3.IntegrityError):
        insert_project(database, fee, budget, wip)


def test_exact_database_aggregation(database):
    insert_transaction(database, 10)

    database.execute(
        """
        INSERT INTO consulting_transactions
        SELECT
            1002, transaction_date, business_unit,
            cost_center, project_id, client_id,
            transaction_type, category, description,
            counterparty_id, 20, classification,
            source_system
        FROM consulting_transactions
        WHERE transaction_id = 1001
        """
    )

    result = database.execute(
        "SELECT SUM(amount_cents) FROM consulting_transactions"
    ).fetchone()

    assert result == (30,)