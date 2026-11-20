from app.projects.application.ports import ProjectRepositoryPort


class ProjectService:
    """Coordinate project retrieval and domain-level data governance."""

    def __init__(self, repository: ProjectRepositoryPort):
        self.repository = repository

    def get_strategy_projects(self) -> list[dict]:
        """Retrieve Strategy project summaries."""

        projects = self.repository.get_strategy_projects()

        return [
            {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_status": project.project_status,
            }
            for project in projects
        ]

    def get_ai_approved_projects(self) -> list[dict]:
        """Return only explicitly approved AI-accessible project summaries."""

        projects = self.repository.get_ai_project_candidates()

        return [
            {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "project_status": project.project_status,
            }
            for project in projects
            if project.is_ai_eligible
        ]
