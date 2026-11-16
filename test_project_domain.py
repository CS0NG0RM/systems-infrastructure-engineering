from decimal import Decimal

import pytest

from app.projects.domain.project import (
    AIApproval,
    Project,
    ProjectClassification,
)


def create_project(
    classification=ProjectClassification.INTERNAL,
    ai_access=AIApproval.APPROVED,
    **overrides,
):
    values = {
        "project_id": "STR-TEST-001",
        "client_id": "CL-TEST-001",
        "project_name": "Fictional Enterprise Project",
        "project_status": "Active",
        "proposed_fee_eur": Decimal("85000.00"),
        "budget_eur": Decimal("48000.00"),
        "wip_eur": Decimal("12500.00"),
        "win_probability": Decimal("1.0"),
        "project_manager": "PM-TEST-001",
        "classification": classification,
        "ai_access": ai_access,
    }

    values.update(overrides)

    return Project(**values)


def test_valid_project_can_be_created():
    project = create_project()

    assert project.project_id == "STR-TEST-001"
    assert project.proposed_fee_eur == Decimal("85000.00")


@pytest.mark.parametrize(
    "classification",
    [
        ProjectClassification.PUBLIC,
        ProjectClassification.INTERNAL,
    ],
)
def test_approved_public_and_internal_projects_are_ai_eligible(classification):
    project = create_project(classification=classification)

    assert project.is_ai_eligible is True


@pytest.mark.parametrize(
    "classification",
    [
        ProjectClassification.CONFIDENTIAL,
        ProjectClassification.RESTRICTED,
    ],
)
def test_confidential_and_restricted_projects_are_not_ai_eligible(classification):
    project = create_project(classification=classification)

    assert project.is_ai_eligible is False


def test_unapproved_project_is_not_ai_eligible():
    project = create_project(ai_access=AIApproval.DENIED)

    assert project.is_ai_eligible is False


@pytest.mark.parametrize(
    "field",
    [
        "proposed_fee_eur",
        "budget_eur",
        "wip_eur",
    ],
)
def test_negative_financial_values_are_rejected(field):
    with pytest.raises(ValueError):
        create_project(**{field: Decimal("-1.00")})


@pytest.mark.parametrize(
    "probability",
    [
        Decimal("-0.01"),
        Decimal("1.01"),
    ],
)
def test_invalid_win_probability_is_rejected(probability):
    with pytest.raises(ValueError):
        create_project(win_probability=probability)


def test_empty_project_name_is_rejected():
    with pytest.raises(ValueError):
        create_project(project_name=" ")


def test_project_is_immutable():
    project = create_project()

    with pytest.raises(AttributeError):
        project.project_name = "Modified Project"

def test_financial_values_reject_strings():
    with pytest.raises(TypeError):
        create_project(proposed_fee_eur="85000")


def test_probability_rejects_float():
    with pytest.raises(TypeError):
        create_project(win_probability=1.0)


def test_classification_rejects_plain_string():
    with pytest.raises(TypeError):
        create_project(classification="internal")


def test_ai_approval_rejects_unknown_value():
    with pytest.raises(TypeError):
        create_project(ai_access="approved")
