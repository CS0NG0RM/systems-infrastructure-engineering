from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    """Represent an authenticated user or service."""

    identity_id: str
    identity_type: str
    role: str


# Fictional identities for local IAM testing.
# Production systems would use an external identity provider.
DEMO_IDENTITIES = {
    "demo-employee-token": Identity("employee-001", "human", "employee"),
    "demo-finance-token": Identity("finance-001", "human", "finance"),
    "demo-strategy-token": Identity("strategy-001", "human", "strategy"),
    "demo-ai-token": Identity("ai-service-001", "service", "ai_service"),
}


# Maintain the activation status of registered identities.
# All fictional identities start as enabled.
IDENTITY_STATUS = {
    identity.identity_id: True
    for identity in DEMO_IDENTITIES.values()
}


def is_identity_enabled(identity_id: str) -> bool:
    """Check whether a registered identity is enabled."""

    # Unknown identities are treated as disabled.
    return IDENTITY_STATUS.get(identity_id, False)


def set_identity_enabled(identity_id: str, enabled: bool) -> bool:
    """Enable or disable a registered identity."""

    # Only identities already present in the registry can be modified.
    if identity_id not in IDENTITY_STATUS:
        return False

    IDENTITY_STATUS[identity_id] = enabled
    return True


def authenticate_identity(token: str | None) -> Identity | None:
    """Resolve a credential to an enabled identity."""

    if token is None:
        return None

    identity = DEMO_IDENTITIES.get(token)

    if identity is None:
        return None

    # Disabled identities cannot authenticate, even with a valid token.
    if not is_identity_enabled(identity.identity_id):
        return None

    return identity