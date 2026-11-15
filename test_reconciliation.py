import sqlite3

from pipelines.reconcile_finance import reconcile_projects


def test_reconciliation_identifies_financial_discrepancies(tmp_path):
    # Keep test transactions separate from the enterprise database.
    database_path = tmp_path / "test_finance.db"

    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            CREATE TABLE department_projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                proposed_fee_eur REAL NOT NULL,
                project_status TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE consulting_transactions (
                transaction_id INTEGER PRIMARY KEY,
                project_id TEXT,
                transaction_type TEXT NOT NULL,
                amount_eur REAL NOT NULL
            )
        """)

        # Use predictable project fees and financial transactions.
        connection.executemany(
            """
            INSERT INTO department_projects
                (project_id, project_name, proposed_fee_eur, project_status)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("STR-TEST-001", "Strategy Project A", 85000, "Active"),
                ("STR-TEST-002", "Strategy Project B", 120000, "Active"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO consulting_transactions
                (transaction_id, project_id, transaction_type, amount_eur)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, "STR-TEST-001", "Revenue", 100000),
                (2, "STR-TEST-001", "Revenue", 62500),
                (3, "STR-TEST-002", "Revenue", 152507),
                (4, "STR-TEST-002", "Expense", 5000),
                (5, "STR-TEST-001", "Revenue", -2000),
            ],
        )

    # Reconcile the test database rather than changing operational records.
    results = reconcile_projects(database_path)

    projects = {
        project_id: {
            "proposed_fee": proposed_fee,
            "revenue": revenue,
        }
        for project_id, name, proposed_fee, revenue in results
    }

    # Credit notes reduce the project's net invoiced revenue.
    assert projects["STR-TEST-001"]["revenue"] == 160500
    assert projects["STR-TEST-002"]["revenue"] == 152507

    assert projects["STR-TEST-001"]["revenue"] > projects["STR-TEST-001"]["proposed_fee"]
    assert projects["STR-TEST-002"]["revenue"] > projects["STR-TEST-002"]["proposed_fee"]