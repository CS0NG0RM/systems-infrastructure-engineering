# Central permission rules for the enterprise platform.
# All roles are fictional and used for local security testing.

ACCESS_POLICIES = {
    "finance_reports": {"finance"},
    "strategy_projects": {"strategy", "finance"},
    "ai_approved_data": {"ai_service", "strategy", "finance", "employee"},
    "ingestion_monitoring": {"finance"},
}


# Explicit permissions assigned to each human or machine role.
ROLE_PERMISSIONS = {
    "finance": {
        "finance.read",
        "strategy_projects.read",
        "ai_approved_data.read",
        "documents.read",
        "ingestion_monitoring.read",
    },
    "strategy": {
        "strategy_projects.read",
        "ai_approved_data.read",
        "documents.read",
    },
    "ai_service": {
        "ai_approved_data.read",
    },
    "employee": {
        "ai_approved_data.read",
        "documents.read",
    },
}


def is_access_allowed(role: str, resource: str) -> bool:
    """Check whether a role is permitted to access a resource."""

    # Unknown resources have no permissions and are denied by default.
    allowed_roles = ACCESS_POLICIES.get(resource, set())

    return role in allowed_roles


def is_permission_allowed(role: str, permission: str) -> bool:
    """Check whether an identity's role has an explicit permission."""

    # Unknown roles and permissions are denied by default.
    allowed_permissions = ROLE_PERMISSIONS.get(role, set())

    return permission in allowed_permissions


def is_ai_data_allowed(classification: str, ai_access: str) -> bool:
    """Check whether a record is approved for retrieval by an AI service."""

    # Unknown classifications or approval values are denied by default.
    valid_classifications = {
        "public",
        "internal",
        "confidential",
        "restricted",
    }

    if classification not in valid_classifications:
        return False

    # Confidential and restricted records cannot be retrieved by AI.
    if classification in {"confidential", "restricted"}:
        return False

    # The record must also have explicit AI approval.
    return ai_access == "approved"