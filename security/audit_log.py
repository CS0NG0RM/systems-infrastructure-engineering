import json
from datetime import datetime, timezone
from config import AUDIT_LOG_PATH


def record_access_event(role: str, resource: str, decision: str):
    """Record an access-control decision as a structured JSON event."""

    if decision not in {"allowed", "denied"}:
        raise ValueError("Invalid audit decision")

    # Create the log directory if it does not exist.
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "role": role,
        "resource": resource,
        "decision": decision,
    }

    # JSON Lines stores one audit event per line.
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")

    return event
