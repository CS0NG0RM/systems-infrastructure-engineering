import pytest
from fastapi.testclient import TestClient

from main import app
from app.api.dependencies import get_project_service
from app.api.routes import projects as projects_routes


class FakeProjectService:
    """Provide controlled responses for API integration tests."""

    def __init__(self):
        self.strategy_calls = 0
        self.ai_calls = 0

    def get_strategy_projects(self):
        self.strategy_calls += 1

        return [
            {
                "project_id": "STR-TEST-001",
                "project_name": "Fictional Strategy Project",
                "project_status": "Active",
            }
        ]

    def get_ai_approved_projects(self):
        self.ai_calls += 1

        return [
            {
                "project_id": "STR-TEST-002",
                "project_name": "Approved AI Project",
                "project_status": "Pipeline",
            }
        ]


@pytest.fixture
def client(monkeypatch):
    """Provide an isolated API client without writing audit events."""

    monkeypatch.setattr(
        projects_routes,
        "record_access_event",
        lambda *args: None,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_project_service, None)


def test_strategy_endpoint_uses_injected_service(client):
    service = FakeProjectService()

    app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(
        "/departments/strategy/projects",
        headers={"x-demo-token": "demo-strategy-token"},
    )

    assert response.status_code == 200
    assert response.json()[0]["project_id"] == "STR-TEST-001"
    assert service.strategy_calls == 1
    assert service.ai_calls == 0


def test_ai_endpoint_uses_injected_service(client):
    service = FakeProjectService()

    app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(
        "/ai/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 200
    assert response.json()[0]["project_id"] == "STR-TEST-002"
    assert service.ai_calls == 1
    assert service.strategy_calls == 0


def test_employee_cannot_execute_strategy_service(client):
    service = FakeProjectService()

    app.dependency_overrides[get_project_service] = lambda: service

    response = client.get(
        "/departments/strategy/projects",
        headers={"x-demo-token": "demo-employee-token"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Access denied"}
    assert service.strategy_calls == 0


def test_unauthenticated_request_cannot_execute_ai_service(client):
    service = FakeProjectService()

    app.dependency_overrides[get_project_service] = lambda: service

    response = client.get("/ai/projects")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required"
    }
    assert service.ai_calls == 0
