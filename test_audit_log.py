import json

from fastapi.testclient import TestClient

from main import app
from security import audit_log


def test_denied_finance_access_creates_audit_event(tmp_path, monkeypatch):
    # Keep test events separate from the operational audit log.
    log_path = tmp_path / "security_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", log_path)

    client = TestClient(app)
    response = client.get(
        "/finance/projects",
        headers={"x-demo-token": "demo-ai-token"},
    )

    assert response.status_code == 403

    events = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["role"] == "ai_service"
    assert events[0]["resource"] == "finance_reports"
    assert events[0]["decision"] == "denied"
    assert "timestamp" in events[0]
    assert "demo-ai-token" not in json.dumps(events)


def test_allowed_finance_access_creates_audit_event(tmp_path, monkeypatch):
    # Record successful authorization without exposing the demo token.
    log_path = tmp_path / "security_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", log_path)

    client = TestClient(app)
    response = client.get(
        "/finance/projects",
        headers={"x-demo-token": "demo-finance-token"},
    )

    assert response.status_code == 200

    events = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["role"] == "finance"
    assert events[0]["resource"] == "finance_reports"
    assert events[0]["decision"] == "allowed"
    assert "timestamp" in events[0]
    assert "demo-finance-token" not in json.dumps(events)

def test_unauthenticated_finance_access_creates_audit_event(
    tmp_path, monkeypatch
):
    # Keep authentication failure events out of the operational log.
    log_path = tmp_path / "security_audit.jsonl"
    monkeypatch.setattr(audit_log, "AUDIT_LOG_PATH", log_path)

    client = TestClient(app)
    response = client.get("/finance/projects")

    assert response.status_code == 401

    events = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
    ]

    assert len(events) == 1
    assert events[0]["role"] == "unauthenticated"
    assert events[0]["resource"] == "finance_reports"
    assert events[0]["decision"] == "denied"
    assert "timestamp" in events[0]
    assert "x-demo-token" not in json.dumps(events)