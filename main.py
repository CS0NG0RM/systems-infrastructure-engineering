from pipelines.reconcile_finance import reconcile_projects
from fastapi import Depends, FastAPI, HTTPException
from security.access_policy import (
    is_access_allowed,
    is_permission_allowed,
    is_ai_data_allowed,
)
from security.audit_log import record_access_event
from security.dependencies import require_identity
from security.identity import Identity

# Create the API application.
app = FastAPI(title="Secure Enterprise Data & AI Platform")


# Fictional documents used to demonstrate information access controls.
DOCUMENTS = {
    1: {"title": "Employee Handbook", "classification": "public"},
    2: {"title": "Financial Forecast", "classification": "confidential"},
}

@app.get("/health")
def health_check():
    """Check API availability and read-only database connectivity."""
    import sqlite3

    from pipelines.ingest_finance import DATABASE_PATH

    try:
        database_uri = DATABASE_PATH.resolve().as_uri() + "?mode=ro"

        with sqlite3.connect(database_uri, uri=True) as connection:
            connection.execute("SELECT 1").fetchone()

    except (sqlite3.Error, OSError):
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable",
        )

    return {
        "status": "healthy",
        "service": "enterprise-api-security-testing",
    }


@app.get("/documents/{document_id}")
def get_document(
    document_id: int,
    identity: Identity = Depends(require_identity("documents")),
):
    
    # Retrieve the authenticated user's role.
    role = identity.role

    # Check whether the requested document exists.
    document = DOCUMENTS.get(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Require explicit permission to access enterprise documents.
    if not is_permission_allowed(role, "documents.read"):
        record_access_event(role, "documents", "denied")
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    # Confidential documents remain restricted to Finance identities.
    if document["classification"] == "confidential" and role != "finance":
        record_access_event(role, "documents", "denied")
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    record_access_event(role, "documents", "allowed")

    return document

@app.get("/finance/projects")
def get_finance_projects(
    identity: Identity = Depends(require_identity("finance_reports")),
):
    """Return project financial reconciliation results to Finance users."""

    # Retrieve the authenticated user's role.
    role = identity.role

    # Require explicit permission to read confidential Finance reports.
    if not is_permission_allowed(role, "finance.read"):
        record_access_event(role, "finance_reports", "denied")
        raise HTTPException(status_code=403, detail="Access denied")
    
    record_access_event(role, "finance_reports", "allowed")

    # Retrieve reconciled financial results from the enterprise database.
    results = reconcile_projects()

    return [
        {
            "project_id": project_id,
            "project_name": name,
            "proposed_fee_eur": proposed_fee,
            "invoiced_revenue_eur": revenue,
        }
        for project_id, name, proposed_fee, revenue in results
    ]

@app.get("/departments/strategy/projects")
def get_strategy_projects(
    identity: Identity = Depends(require_identity("strategy_projects")),
):
    """Return Strategy Consulting project information to authorised users."""

    # Retrieve the authenticated user's role.
    role = identity.role

    # Require explicit permission to read Strategy project information.
    if not is_permission_allowed(role, "strategy_projects.read"):
        record_access_event(role, "strategy_projects", "denied")
        raise HTTPException(status_code=403, detail="Access denied")

    record_access_event(role, "strategy_projects", "allowed")

    # Retrieve project information without returning confidential fee figures.
    import sqlite3
    from pathlib import Path

    database_path = Path(__file__).resolve().parent / "enterprise.db"

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row

        projects = connection.execute(
            """
            SELECT project_id, project_name, project_status
            FROM department_projects
            WHERE project_id LIKE ?
            ORDER BY project_id
            """,
            ("STR-%",),
        ).fetchall()

    return [dict(project) for project in projects]

@app.get("/ai/projects")
def get_ai_approved_projects(
    identity: Identity = Depends(require_identity("ai_approved_data")),
):
    """Return project summaries explicitly approved for AI retrieval."""

    # Retrieve the authenticated service or user's role.
    role = identity.role

    # Require explicit permission to retrieve AI-approved data.
    if not is_permission_allowed(role, "ai_approved_data.read"):
        record_access_event(role, "ai_approved_data", "denied")
        raise HTTPException(status_code=403, detail="Access denied")

    record_access_event(role, "ai_approved_data", "allowed")

    import sqlite3
    from pathlib import Path

    database_path = Path(__file__).resolve().parent / "enterprise.db"

    # Read project classifications and approval flags from the database.
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row

        projects = connection.execute(
            """
            SELECT project_id, project_name, project_status,
                   classification, ai_access
            FROM department_projects
            ORDER BY project_id
            """
        ).fetchall()

    # Filter records before returning anything to the requesting application.
    approved_projects = []

    for project in projects:
        if is_ai_data_allowed(
            project["classification"],
            project["ai_access"],
        ):
            # Return only the fields approved for this demonstration endpoint.
            approved_projects.append({
                "project_id": project["project_id"],
                "project_name": project["project_name"],
                "project_status": project["project_status"],
            })

    return approved_projects

@app.get("/operations/ingestion-status")
def get_ingestion_status(
    identity: Identity = Depends(require_identity("ingestion_monitoring")),
):
    """Return aggregate Finance ingestion statistics to authorised users."""
    import sqlite3

    from pipelines.ingest_finance import DATABASE_PATH

    role = identity.role

    # Require explicit permission to view operational statistics.
    if not is_permission_allowed(role, "ingestion_monitoring.read"):
        record_access_event(role, "ingestion_monitoring", "denied")
        raise HTTPException(status_code=403, detail="Access denied")

    # Read aggregate results without exposing transaction or file details.
    try:
        database_uri = DATABASE_PATH.resolve().as_uri() + "?mode=ro"

        with sqlite3.connect(database_uri, uri=True) as connection:
            successful, failed = connection.execute(
                """
                SELECT
                    COUNT(CASE WHEN status = 'completed' THEN 1 END),
                    COUNT(CASE WHEN status = 'failed' THEN 1 END)
                FROM finance_ingestion_history
                """
            ).fetchone()

    except (sqlite3.Error, OSError):
        # Report database failures without misclassifying them as access denials.
        raise HTTPException(
            status_code=503,
            detail="Monitoring temporarily unavailable",
        )

    record_access_event(role, "ingestion_monitoring", "allowed")

    return {
        "total_imports": successful + failed,
        "successful_imports": successful,
        "failed_imports": failed,
    }