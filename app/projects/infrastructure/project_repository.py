import sqlite3
from contextlib import closing
from decimal import Decimal
from pathlib import Path

from config import DATABASE_PATH
from app.projects.domain.project import (
    AIApproval,
    Project,
    ProjectAIEligibility,
    ProjectClassification,
    ProjectSummary,
)


class ProjectRepository:
    """Provide read-only SQLite persistence for project domain objects."""

    def __init__(self, database_path: Path | None = None):
        self.database_path = Path(database_path or DATABASE_PATH)

    def _connect(self):
        """Open the enterprise database in read-only mode."""

        database_uri = self.database_path.resolve().as_uri() + "?mode=ro"

        connection = sqlite3.connect(database_uri, uri=True)
        connection.row_factory = sqlite3.Row

        return connection

    @staticmethod
    def _to_domain(record: sqlite3.Row) -> Project:
        """Convert a complete database record into a Project entity."""

        return Project(
            project_id=record["project_id"],
            client_id=record["client_id"],
            project_name=record["project_name"],
            project_status=record["project_status"],
            proposed_fee_eur=Decimal(str(record["proposed_fee_eur"])),
            budget_eur=Decimal(str(record["budget_eur"])),
            wip_eur=Decimal(str(record["wip_eur"])),
            win_probability=Decimal(str(record["win_probability"])),
            project_manager=record["project_manager"],
            classification=ProjectClassification(record["classification"]),
            ai_access=AIApproval(record["ai_access"]),
        )

    def get_strategy_projects(self) -> list[ProjectSummary]:
        """Retrieve Strategy summaries without financial information."""

        query = """
            SELECT project_id, project_name, project_status
            FROM department_projects
            WHERE project_id LIKE ?
            ORDER BY project_id
        """

        with closing(self._connect()) as connection:
            records = connection.execute(query, ("STR-%",)).fetchall()

        return [
            ProjectSummary(
                project_id=record["project_id"],
                project_name=record["project_name"],
                project_status=record["project_status"],
            )
            for record in records
        ]

    def get_ai_project_candidates(self) -> list[ProjectAIEligibility]:
        """Retrieve only fields required for AI eligibility evaluation."""

        query = """
            SELECT
                project_id,
                project_name,
                project_status,
                classification,
                ai_access
            FROM department_projects
            ORDER BY project_id
        """

        with closing(self._connect()) as connection:
            records = connection.execute(query).fetchall()

        return [
            ProjectAIEligibility(
                project_id=record["project_id"],
                project_name=record["project_name"],
                project_status=record["project_status"],
                classification=ProjectClassification(record["classification"]),
                ai_access=AIApproval(record["ai_access"]),
            )
            for record in records
        ]

    def get_all_projects(self) -> list[Project]:
        """Retrieve complete project entities for authorized operations."""

        query = """
            SELECT
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
            FROM department_projects
            ORDER BY project_id
        """

        with closing(self._connect()) as connection:
            records = connection.execute(query).fetchall()

        return [self._to_domain(record) for record in records]
