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
from config import DATABASE_PATH
from app.api.routes.projects import router as projects_router

# Create the API application.
app = FastAPI(title="Secure Enterprise Data & AI Platform")

app.include_router(projects_router)


# Fictional documents used to demonstrate information access controls.
DOCUMENTS = {
    1: {"title": "Employee Handbook", "classification": "public"},
    2: {"title": "Financial Forecast", "classification": "confidential"},
}

@app.get("/health")
def health_check():
    """Check API availability and read-only database connectivity."""
    import sqlite3

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
            "proposed_fee_eur": format(proposed_fee, ".2f"),
            "invoiced_revenue_eur": format(revenue, ".2f"),
        }
        for project_id, name, proposed_fee, revenue in results
    ]

@app.get("/operations/ingestion-status")
def get_ingestion_status(
    identity: Identity = Depends(require_identity("ingestion_monitoring")),
):
    """Return aggregate Finance ingestion statistics to authorised users."""
    import sqlite3

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