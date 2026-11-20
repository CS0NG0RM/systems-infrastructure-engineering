from app.projects.application.project_service import ProjectService
from app.projects.infrastructure.project_repository import ProjectRepository


def get_project_service() -> ProjectService:
    """Construct the project service with its persistence implementation."""

    repository = ProjectRepository()

    return ProjectService(repository)
