from pathlib import Path
import subprocess

from prefect import flow, task


# Locate the existing project and its Python environment.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"


@task(name="Ingest Finance Data", retries=1)
def ingest_finance():
    """Run the existing financial data ingestion pipeline."""

    # Run the ingestion script as a module so package imports work correctly.
    subprocess.run(
        [str(PYTHON), "-m", "pipelines.ingest_finance"],
        cwd=PROJECT_ROOT,
        check=True,
    )

@task(name="Process Incoming Finance Files", retries=1)
def process_incoming_finance():
    """Discover and ingest new Finance CSV exports."""

    # Discover files using the existing pipeline module.
    discovery = subprocess.run(
        [str(PYTHON), "-m", "pipelines.discover_finance"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )

    print(discovery.stdout)

    incoming_folder = PROJECT_ROOT / "data" / "incoming" / "finance"

    # Process each incoming CSV using the shared ingestion function.
    for csv_path in sorted(incoming_folder.glob("*.csv")):
        subprocess.run(
            [
                str(PYTHON),
                "-c",
                (
                    "from pipelines.ingest_finance import "
                    "initialize_database, ingest_transactions; "
                    "initialize_database(); "
                    "ingest_transactions(__import__('sys').argv[1])"
                ),
                str(csv_path),
            ],
            cwd=PROJECT_ROOT,
            check=True,
        )

@task(name="Reconcile Project Finances")
def reconcile_finance():
    """Compare project fees against invoiced revenue."""

    subprocess.run(
        [str(PYTHON), str(PROJECT_ROOT / "pipelines" / "reconcile_finance.py")],
        cwd=PROJECT_ROOT,
        check=True,
    )


@flow(name="Enterprise Finance Pipeline", log_prints=True)
def enterprise_finance_pipeline():
    """Coordinate Finance ingestion and reconciliation."""

    # Load the original export, then process new Finance files.
    ingest_finance()
    process_incoming_finance()

    # Reconcile project finances after both ingestion steps finish.
    reconcile_finance()


if __name__ == "__main__":
    # Register a daily schedule and keep the local runner available.
    enterprise_finance_pipeline.serve(
        name="daily-finance-pipeline",
        interval=86400,
    )