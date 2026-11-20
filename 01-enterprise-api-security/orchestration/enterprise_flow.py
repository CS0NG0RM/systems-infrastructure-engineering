
from prefect import flow, task

from pipelines.ingest_finance import (
    initialize_database,
    initialize_projects_table,
    initialize_ingestion_history,
    ingest_transactions,
)
from pipelines.ingest_projects import ingest_projects
from pipelines.discover_finance import discover_finance_files
from pipelines.reconcile_finance import reconcile_projects


@task(name="Initialize Enterprise Data")
def initialize_enterprise_data():
    """Prepare the database tables required by the platform."""

    initialize_database()
    initialize_projects_table()
    initialize_ingestion_history()


@task(name="Ingest Finance Data", retries=1)
def ingest_finance():
    """Import the original Finance export."""

    ingest_transactions()


@task(name="Ingest Department Projects", retries=1)
def ingest_department_projects():
    """Import departmental project information."""

    ingest_projects()


@task(name="Process Incoming Finance Files", retries=1)
def process_incoming_finance():
    """Discover and process incoming Finance exports."""

    files = discover_finance_files()

    print(f"Finance files discovered: {len(files)}")

    for csv_path in files:
        print(f"Processing: {csv_path.name}")
        ingest_transactions(csv_path)


@task(name="Reconcile Project Finances")
def reconcile_finance():
    """Compare project fees against invoiced revenue."""

    results = reconcile_projects()

    for project_id, name, proposed_fee, revenue in results:
        difference = round(revenue - proposed_fee, 2)

        status = (
            "REVIEW REQUIRED"
            if difference > 0
            else "WITHIN PROPOSED FEE"
        )

        print(
            f"{project_id} | {name} | "
            f"Proposed: EUR {proposed_fee:,.2f} | "
            f"Invoiced: EUR {revenue:,.2f} | "
            f"Difference: EUR {difference:,.2f} | "
            f"{status}"
        )


@flow(name="Enterprise Finance Pipeline", log_prints=True)
def enterprise_finance_pipeline():
    """Coordinate enterprise data processing."""

    initialize_enterprise_data()
    ingest_finance()
    ingest_department_projects()
    process_incoming_finance()
    reconcile_finance()


if __name__ == "__main__":
    enterprise_finance_pipeline.serve(
        name="daily-finance-pipeline",
        interval=86400,
    )
