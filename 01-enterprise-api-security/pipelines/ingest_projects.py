import csv
import sqlite3

from config import DATABASE_PATH, DEPARTMENT_PROJECTS_CSV
from pipelines.money import eur_to_cents


def ingest_projects():
    """Import departmental consulting projects into the enterprise database."""

    with DEPARTMENT_PROJECTS_CSV.open(
        newline="", encoding="utf-8-sig"
    ) as file:
        projects = list(csv.DictReader(file))

    inserted = 0
    duplicates = 0

    with sqlite3.connect(DATABASE_PATH) as connection:
        for project in projects:

            cursor = connection.execute(
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO NOTHING
                """,
                (
                    project["project_id"],
                    project["client_id"],
                    project["project_name"],
                    project["project_status"],
                    eur_to_cents(project["proposed_fee_eur"]),
                    eur_to_cents(project["budget_eur"]),
                    eur_to_cents(project["wip_eur"]),
                    float(project["win_probability"]),
                    project["project_manager"],
                    project["classification"],
                    project["ai_access"],
                ),
            )

            if cursor.rowcount == 1:
                inserted += 1
            else:
                duplicates += 1

    print(f"Projects inserted: {inserted}")
    print(f"Existing projects skipped: {duplicates}")


if __name__ == "__main__":
    ingest_projects()