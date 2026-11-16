import sqlite3

from config import DATABASE_PATH

def reconcile_projects(database_path=None):
    """Compare active project fees with revenue recorded in Finance."""

    # Link departmental projects to their transactions in central Finance.
    # LEFT JOIN keeps projects even when no financial transactions exist.
    query = """
        SELECT
            p.project_id,
            p.project_name,
            p.proposed_fee_eur,
            COALESCE(
                SUM(
                    CASE
                        WHEN f.transaction_type = 'Revenue'
                        THEN f.amount_eur
                        ELSE 0
                    END
                ), 0
            ) AS invoiced_revenue
        FROM department_projects p
        LEFT JOIN consulting_transactions f
            ON p.project_id = f.project_id
        WHERE p.project_status = 'Active'
        GROUP BY
            p.project_id,
            p.project_name,
            p.proposed_fee_eur
        ORDER BY p.project_id
    """

    # Use the enterprise database unless a test database is provided.
    if database_path is None:
        database_path = DATABASE_PATH

    # Run the same reconciliation query against the selected database.
    with sqlite3.connect(database_path) as connection:
        results = connection.execute(query).fetchall()

    return results


if __name__ == "__main__":
    for project_id, name, proposed_fee, revenue in reconcile_projects():

        # Identify projects invoiced above the fee recorded in the project register.
        difference = round(revenue - proposed_fee, 2)

        status = (
            "REVIEW REQUIRED"
            if difference > 0
            else "WITHIN PROPOSED FEE"
        )

        # Display the financial differences for manual investigation.
        print(
            f"{project_id} | {name} | "
            f"Proposed: EUR {proposed_fee:,.2f} | "
            f"Invoiced: EUR {revenue:,.2f} | "
            f"Difference: EUR {difference:,.2f} | "
            f"{status}"
        )