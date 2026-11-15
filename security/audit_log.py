import json
import logging
from datetime import datetime, timezone
from pathlib import Path


# Keep security events separate from application data.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_LOG_PATH = PROJECT_ROOT / "logs" / "security_audit.jsonl"


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