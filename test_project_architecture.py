import sqlite3
from decimal import Decimal

import pytest

from app.projects.domain.project import (
    Project,
    ProjectAIEligibility,
    ProjectSummary,
)
from app.projects.infrastructure.project_repository import ProjectRepository
from app.projects.application.project_service import ProjectService


def create_test_database(database_path):
    """Create an isolated database with fictional project records."""

    with sqlite3.connect(database_path) as connection:
        connection.execute("""
            CREATE TABLE department_projects (
                project_id TEXT PRIMARY KEY,
                client_id TEXT NOT NULL,
                project_name TEXT NOT NULL,
                project_status TEXT NOT NULL,
                proposed_fee_cents INTEGER NOT NULL,
                budget_cents INTEGER NOT NULL,
                wip_cents INTEGER NOT NULL,
                win_probability REAL NOT NULL,
                project_manager TEXT NOT NULL,
                classification TEXT NOT NULL,
                ai_access TEXT NOT NULL
            )
        """)

        connection.executemany(
            """
            INSERT INTO department_projects VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            [
                (
                    "STR-TEST-001", "CL-001", "Strategy Project A",
                    "Active", 8500000, 4800000, 1250000, 1.0,
                    "PM-001", "confidential", "denied",
                ),
                (
                    "STR-TEST-002", "CL-002", "Strategy Project B",
                    "Pipeline", 12000000, 7200000, 1850000, 0.65,
                    "PM-002", "internal", "approved",
                ),
                (
                    "FIN-TEST-001", "CL-003", "Finance Project",
                    "Active", 5000000, 3000000, 800000, 1.0,
                    "PM-003", "public", "approved",
                ),
            ],
        )


def test_repository_returns_only_strategy_projects(tmp_path):
    database_path = tmp_path / "projects.db"
    create_test_database(database_path)

    repository = ProjectRepository(database_path)

    projects = repository.get_strategy_projects()

    assert len(projects) == 2
    assert all(isinstance(project, ProjectSummary) for project in projects)

    assert [project.project_id for project in projects] == [
        "STR-TEST-001",
        "STR-TEST-002",
    ]

    assert not hasattr(projects[0], "proposed_fee_eur")


def test_repository_retrieves_only_required_ai_candidate_fields(tmp_path):
    database_path = tmp_path / "projects.db"
    create_test_database(database_path)

    repository = ProjectRepository(database_path)

    candidates = repository.get_ai_project_candidates()

    assert len(candidates) == 3
    assert all(
        isinstance(candidate, ProjectAIEligibility)
        for candidate in candidates
    )

    assert not hasattr(candidates[0], "proposed_fee_eur")
    assert not hasattr(candidates[0], "budget_eur")
    assert not hasattr(candidates[0], "wip_eur")
    assert not hasattr(candidates[0], "project_manager")


def test_repository_retrieves_complete_project_entities(tmp_path):
    database_path = tmp_path / "projects.db"
    create_test_database(database_path)

    repository = ProjectRepository(database_path)

    projects = repository.get_all_projects()

    assert len(projects) == 3
    assert all(isinstance(project, Project) for project in projects)

    strategy_project = next(
        project
        for project in projects
        if project.project_id == "STR-TEST-001"
    )

    assert strategy_project.proposed_fee_eur == Decimal("85000.0")
    assert strategy_project.budget_eur == Decimal("48000.0")


def test_repository_enforces_read_only_database_access(tmp_path):
    database_path = tmp_path / "projects.db"
    create_test_database(database_path)

    repository = ProjectRepository(database_path)

    connection = repository._connect()

    try:
        with pytest.raises(sqlite3.OperationalError):
            connection.execute(
                """
                UPDATE department_projects
                SET project_name = ?
                WHERE project_id = ?
                """,
                ("Modified Project", "STR-TEST-001"),
            )
    finally:
        connection.close()

    with sqlite3.connect(database_path) as connection:
        name = connection.execute(
            """
            SELECT project_name
            FROM department_projects
            WHERE project_id = ?
            """,
            ("STR-TEST-001",),
        ).fetchone()[0]

    assert name == "Strategy Project A"


def test_project_service_filters_ai_data_and_minimises_output(tmp_path):
    database_path = tmp_path / "projects.db"
    create_test_database(database_path)

    repository = ProjectRepository(database_path)
    service = ProjectService(repository)

    projects = service.get_ai_approved_projects()

    assert len(projects) == 2

    assert {
        project["project_id"] for project in projects
    } == {
        "STR-TEST-002",
        "FIN-TEST-001",
    }

    for project in projects:
        assert set(project) == {
            "project_id",
            "project_name",
            "project_status",
        }

        assert "proposed_fee_eur" not in project
        assert "budget_eur" not in project
        assert "wip_eur" not in project
