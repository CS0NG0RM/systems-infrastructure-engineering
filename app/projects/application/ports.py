from typing import Protocol

from app.projects.domain.project import (
    Project,
    ProjectAIEligibility,
    ProjectSummary,
)


class ProjectRepositoryPort(Protocol):
    """Define persistence operations required by project services."""

    def get_strategy_projects(self) -> list[ProjectSummary]:
        """Retrieve Strategy project summaries."""

    def get_ai_project_candidates(self) -> list[ProjectAIEligibility]:
        """Retrieve minimum data required for AI eligibility evaluation."""

    def get_all_projects(self) -> list[Project]:
        """Retrieve complete project domain entities."""
