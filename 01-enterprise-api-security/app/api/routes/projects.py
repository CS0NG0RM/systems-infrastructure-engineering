from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_project_service
from app.projects.application.project_service import ProjectService
from security.access_policy import is_permission_allowed
from security.audit_log import record_access_event
from security.dependencies import require_identity
from security.identity import Identity


router = APIRouter()


@router.get("/departments/strategy/projects")
def get_strategy_projects(
    identity: Identity = Depends(require_identity("strategy_projects")),
    service: ProjectService = Depends(get_project_service),
):
    """Return Strategy project information to authorised users."""

    role = identity.role

    if not is_permission_allowed(role, "strategy_projects.read"):
        record_access_event(role, "strategy_projects", "denied")
        raise HTTPException(status_code=403, detail="Access denied")

    record_access_event(role, "strategy_projects", "allowed")

    return service.get_strategy_projects()


@router.get("/ai/projects")
def get_ai_approved_projects(
    identity: Identity = Depends(require_identity("ai_approved_data")),
    service: ProjectService = Depends(get_project_service),
):
    """Return project summaries explicitly approved for AI retrieval."""

    role = identity.role

    if not is_permission_allowed(role, "ai_approved_data.read"):
        record_access_event(role, "ai_approved_data", "denied")
        raise HTTPException(status_code=403, detail="Access denied")

    record_access_event(role, "ai_approved_data", "allowed")

    return service.get_ai_approved_projects()
