import csv
import sqlite3

from config import DATABASE_PATH, DEPARTMENT_PROJECTS_CSV

def ingest_projects():
    """Import departmental consulting projects into the enterprise database."""

    # Read the team's project register, including active and pipeline projects.
    with DEPARTMENT_PROJECTS_CSV.open(
            newline="", encoding="utf-8-sig"
    ) as file:
        projects = list(csv.DictReader(file))

    inserted = 0
    duplicates = 0

    # Import all projects within a single database transaction.
    with sqlite3.connect(DATABASE_PATH) as connection:
        for project in projects:

            # Use parameterised SQL to safely insert project information.
            # Existing project IDs are skipped to prevent duplicate records.
            cursor = connection.execute(
                """
                INSERT INTO department_projects (
                    project_id,
                    client_id,
                    project_name,
                    project_status,
                    proposed_fee_eur,
                    budget_eur,
                    wip_eur,
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
                    float(project["proposed_fee_eur"]),
                    float(project["budget_eur"]),
                    float(project["wip_eur"]),
                    float(project["win_probability"]),
                    project["project_manager"],
                    project["classification"],
                    project["ai_access"],
                ),
            )

            # Track newly imported projects and records already in the database.
            if cursor.rowcount == 1:
                inserted += 1
            else:
                duplicates += 1

    print(f"Projects inserted: {inserted}")
    print(f"Existing projects skipped: {duplicates}")


if __name__ == "__main__":
    ingest_projects()