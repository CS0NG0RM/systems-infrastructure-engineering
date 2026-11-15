from fastapi import Header, HTTPException

from security.audit_log import record_access_event
from security.identity import Identity, authenticate_identity


def require_identity(resource: str):
    """Create an authentication dependency for a protected resource."""

    def dependency(
        x_demo_token: str | None = Header(default=None),
    ) -> Identity:
        # Resolve the supplied credential through the central identity registry.
        identity = authenticate_identity(x_demo_token)

        if identity is None:
            # Record failed authentication without storing the supplied token.
            record_access_event("unauthenticated", resource, "denied")
            raise HTTPException(
                status_code=401,
                detail="Authentication required",
            )

        return identity

    return dependency