import pytest

from security.access_policy import (
    is_access_allowed,
    is_ai_data_allowed,
    is_permission_allowed,
)


def test_finance_can_access_finance_reports():
    assert is_access_allowed("finance", "finance_reports") is True


def test_strategy_cannot_access_finance_reports():
    assert is_access_allowed("strategy", "finance_reports") is False


def test_ai_cannot_access_finance_reports():
    assert is_access_allowed("ai_service", "finance_reports") is False


def test_strategy_can_access_department_projects():
    assert is_access_allowed("strategy", "strategy_projects") is True


def test_unknown_resources_are_denied():
    assert is_access_allowed("finance", "unknown_resource") is False


def test_ai_can_access_explicitly_approved_internal_data():
    assert is_ai_data_allowed("internal", "approved") is True


def test_ai_cannot_access_confidential_data():
    assert is_ai_data_allowed("confidential", "approved") is False


def test_ai_cannot_access_unapproved_internal_data():
    assert is_ai_data_allowed("internal", "denied") is False


def test_ai_rejects_unknown_classifications():
    assert is_ai_data_allowed("unknown", "approved") is False


@pytest.mark.parametrize(
    "role, permission",
    [
        ("finance", "finance.read"),
        ("finance", "strategy_projects.read"),
        ("finance", "ai_approved_data.read"),
        ("strategy", "strategy_projects.read"),
        ("strategy", "ai_approved_data.read"),
        ("ai_service", "ai_approved_data.read"),
        ("employee", "ai_approved_data.read"),
        ("finance", "documents.read"),
        ("strategy", "documents.read"),
        ("employee", "documents.read"),
    ],
)
def test_authorized_roles_have_expected_permissions(role, permission):
    assert is_permission_allowed(role, permission) is True


@pytest.mark.parametrize(
    "role, permission",
    [
        ("strategy", "finance.read"),
        ("ai_service", "finance.read"),
        ("employee", "finance.read"),
        ("employee", "strategy_projects.read"),
        ("unknown_role", "finance.read"),
        ("finance", "unknown.permission"),
        ("ai_service", "documents.read"),
    ],
)
def test_unauthorized_roles_are_denied_permissions(role, permission):
    assert is_permission_allowed(role, permission) is False

