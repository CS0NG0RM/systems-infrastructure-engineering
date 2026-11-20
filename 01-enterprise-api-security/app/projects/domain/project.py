from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class ProjectClassification(str, Enum):
    """Supported enterprise information classifications."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AIApproval(str, Enum):
    """Explicit AI data-access approval states."""

    APPROVED = "approved"
    DENIED = "denied"


@dataclass(frozen=True)
class Project:
    """Represent an enterprise project and its governing data attributes."""

    project_id: str
    client_id: str
    project_name: str
    project_status: str
    proposed_fee_eur: Decimal
    budget_eur: Decimal
    wip_eur: Decimal
    win_probability: Decimal
    project_manager: str
    classification: ProjectClassification
    ai_access: AIApproval

    def __post_init__(self):
        """Enforce project data types and business invariants."""

        required_fields = (
            self.project_id,
            self.client_id,
            self.project_name,
            self.project_status,
            self.project_manager,
        )

        if any(not isinstance(value, str) for value in required_fields):
            raise TypeError("Required project fields must be strings")

        if any(not value.strip() for value in required_fields):
            raise ValueError("Required project fields cannot be empty")

        monetary_values = (
            self.proposed_fee_eur,
            self.budget_eur,
            self.wip_eur,
        )

        if not all(isinstance(value, Decimal) for value in monetary_values):
            raise TypeError("Project financial values must use Decimal")

        if not isinstance(self.win_probability, Decimal):
            raise TypeError("Win probability must use Decimal")

        if any(
            not value.is_finite() or value < 0
            for value in monetary_values
        ):
            raise ValueError(
                "Project financial values must be finite and non-negative"
            )

        if (
            not self.win_probability.is_finite()
            or not Decimal("0") <= self.win_probability <= Decimal("1")
        ):
            raise ValueError("Win probability must be between 0 and 1")

        if not isinstance(self.classification, ProjectClassification):
            raise TypeError("Invalid project classification")

        if not isinstance(self.ai_access, AIApproval):
            raise TypeError("Invalid AI approval value")

    @property
    def is_ai_eligible(self) -> bool:
        """Determine whether this project can be retrieved by AI services."""

        return (
            self.classification in {
                ProjectClassification.PUBLIC,
                ProjectClassification.INTERNAL,
            }
            and self.ai_access == AIApproval.APPROVED
        )

@dataclass(frozen=True)
class ProjectSummary:
    """Represent a project without exposing financial information."""

    project_id: str
    project_name: str
    project_status: str


@dataclass(frozen=True)
class ProjectAIEligibility:
    """Represent the minimum information required for AI eligibility decisions."""

    project_id: str
    project_name: str
    project_status: str
    classification: ProjectClassification
    ai_access: AIApproval

    @property
    def is_ai_eligible(self) -> bool:
        """Determine whether this project is approved for AI retrieval."""

        return (
            self.classification in {
                ProjectClassification.PUBLIC,
                ProjectClassification.INTERNAL,
            }
            and self.ai_access == AIApproval.APPROVED
        )
