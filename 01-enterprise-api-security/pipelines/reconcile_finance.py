"""Read-only financial reconciliation using exact monetary arithmetic."""

import sqlite3
from pathlib import Path

from config import DATABASE_PATH
from pipelines.money import cents_to_eur


def reconcile_projects(database_path=None):
    query = """
        SELECT
            p.project_id,
            p.project_name,
            p.proposed_fee_cents,
            COALESCE(
                SUM(
                    CASE
                        WHEN f.transaction_type = 'Revenue'
                        THEN f.amount_cents
                        ELSE 0
                    END
                ),
                0
            ) AS invoiced_revenue_cents
        FROM department_projects p
        LEFT JOIN consulting_transactions f
            ON p.project_id = f.project_id
        WHERE p.project_status = 'Active'
        GROUP BY
            p.project_id,
            p.project_name,
            p.proposed_fee_cents
        ORDER BY p.project_id
    """

    if database_path is None:
        database_path = DATABASE_PATH

    database_uri = Path(database_path).resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(database_uri, uri=True) as connection:
        results = connection.execute(query).fetchall()

    return [
        (
            project_id,
            name,
            cents_to_eur(proposed_fee),
            cents_to_eur(revenue),
        )
        for project_id, name, proposed_fee, revenue in results
    ]


if __name__ == "__main__":
    for project_id, name, proposed_fee, revenue in reconcile_projects():
        difference = revenue - proposed_fee

        status = (
            "REVIEW REQUIRED"
            if difference > 0
            else "WITHIN PROPOSED FEE"
        )

        print(
            f"{project_id} | {name} | "
            f"Proposed: EUR {proposed_fee:,.2f} | "
            f"Invoiced: EUR {revenue:,.2f} | "
            f"Difference: EUR {difference:,.2f} | {status}"
        )