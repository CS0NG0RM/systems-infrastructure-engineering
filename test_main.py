from fastapi.testclient import TestClient
from main import app
import pytest
from security import audit_log

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["service"] == "enterprise-api-security-testing"


def test_employee_cannot_access_confidential_document():
    response = client.get(
        "/documents/2",
        headers={"x-demo-token": "demo-employee-token"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"


def test_finance_can_access_confidential_document():
    response = client.get(
        "/documents/2",
        headers={"x-demo-token": "demo-finance-token"}
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Financial Forecast"


def test_unauthenticated_request_is_rejected():
    response = client.get("/documents/2")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

def test_nonexistent_document_returns_404():
    response = client.get(
        "/documents/999",
        headers={"x-demo-token": "demo-employee-token"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

def test_finance_user_can_access_project_reporting():
    # Finance users should be able to retrieve protected project figures.
    response = client.get(
        "/finance/projects",
        headers={"x-demo-token": "demo-finance-token"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["project_id"] == "STR-2026-001"


def test_employee_cannot_access_project_reporting():
    # Employees without Finance permissions must not receive financial data.
    response = client.get(
        "/finance/projects",
        headers={"x-demo-token": "demo-employee-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

def test_ai_cannot_access_confidential_financial_reporting():
    # AI integrations must not inherit access to confidential Finance records.
    response = client.get(
        "/finance/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

def test_strategy_user_can_access_department_projects():
    # Strategy employees can retrieve approved project information.
    response = client.get(
        "/departments/strategy/projects",
        headers={"x-demo-token": "demo-strategy-token"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 5

    # Financial details must not appear in the project summary.
    for project in response.json():
        assert set(project) == {
            "project_id",
            "project_name",
            "project_status",
        }


def test_ai_cannot_access_strategy_projects():
    # AI applications cannot automatically access departmental records.
    response = client.get(
        "/departments/strategy/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied"

def test_ai_receives_only_approved_project_data():
    # AI applications must receive only explicitly approved project summaries.
    response = client.get(
        "/ai/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 200

    projects = response.json()

    # Only the approved internal project should be returned.
    assert len(projects) == 1
    assert projects[0]["project_id"] == "STR-2026-005"

    # Confidential projects and financial fields must not leak.
    assert set(projects[0]) == {
        "project_id",
        "project_name",
        "project_status",
    }

def test_unauthenticated_ai_request_is_rejected():
    # The AI data endpoint must not expose records without authentication.
    response = client.get("/ai/projects")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"

@pytest.mark.parametrize(
    "token, document_id, expected_status",
    [
        ("demo-finance-token", 1, 200),
        ("demo-finance-token", 2, 200),
        ("demo-strategy-token", 1, 200),
        ("demo-strategy-token", 2, 403),
        ("demo-employee-token", 1, 200),
        ("demo-employee-token", 2, 403),
        ("demo-ai-token", 1, 403),
        ("demo-ai-token", 2, 403),
    ],
)
def test_document_access_permission_matrix(
    token, document_id, expected_status, tmp_path, monkeypatch
):
    # Keep test audit events separate from the operational security log.
    log_path = tmp_path / "security_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", log_path)

    response = client.get(
        f"/documents/{document_id}",
        headers={"x-demo-token": token},
    )

    assert response.status_code == expected_status