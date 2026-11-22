import json
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


# Define the approved private application endpoints.
SERVICES = {
    "enterprise-health": "http://10.20.20.10:8080/health",
    "enterprise-api": "http://127.0.0.1:18000/health",
}

# Use the existing dedicated laboratory SSH identity.
SSH_COMMAND = [
    "ssh",
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=yes",
    "-o", "IdentitiesOnly=yes",
    "-o", "ConnectTimeout=5",
    "-i", str(Path.home() / ".ssh/lab_automation_ed25519"),
    "labadmin@10.20.20.10",
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Prevent requests from following unexpected redirects."""

    def redirect_request(self, *args, **kwargs):
        return None


# Disable HTTP proxies and redirect handling.
OPENER = urllib.request.build_opener(
    urllib.request.ProxyHandler({}),
    NoRedirect(),
)


def check_service(name: str, url: str) -> dict:
    """Measure application availability and response latency."""

    started = time.perf_counter()

    try:
        with OPENER.open(url, timeout=5) as response:

            payload = json.loads(response.read())

            elapsed = round(
                (time.perf_counter() - started) * 1000, 2
            )

            healthy = (
                response.status == 200
                and payload.get("status") == "healthy"
            )

            if name == "enterprise-api":
                healthy = healthy and (
                    payload.get("service")
                    == "enterprise-api-security-testing"
                )

            return {
                "service": name,
                "healthy": healthy,
                "http_status": response.status,
                "response_time_ms": elapsed,
                "application_status": payload.get("status"),
            }

    except Exception as error:
        return {
            "service": name,
            "healthy": False,
            "error_type": type(error).__name__,
        }


def execute_remote(command: str) -> str:
    """Execute a fixed monitoring command over private SSH."""

    result = subprocess.run(
        SSH_COMMAND + [command],
        capture_output=True,
        text=True,
        timeout=15,
        check=True,
    )

    return result.stdout.strip()


def check_containers() -> dict:
    """Verify the state of both operational containers."""

    states = {}

    for name in SERVICES:
        output = execute_remote(
            "podman inspect --format "
            "'{{.State.Status}}' " + name
        )

        states[name] = output

    return {
        "healthy": all(
            state == "running"
            for state in states.values()
        ),
        "containers": states,
    }


def check_storage() -> dict:
    """Monitor filesystem capacity supporting persistent data."""

    output = execute_remote(
        "df -Pk /home/labadmin | tail -n 1"
    )

    fields = output.split()

    total_kb = int(fields[1])
    available_kb = int(fields[3])
    used_percent = int(fields[4].rstrip("%"))

    # Flag filesystem utilization of 90% or higher.
    return {
        "healthy": used_percent < 90,
        "total_gib": round(total_kb / 1048576, 2),
        "available_gib": round(available_kb / 1048576, 2),
        "used_percent": used_percent,
        "warning_threshold_percent": 90,
    }


def main() -> int:
    """Collect infrastructure metrics and report overall health."""

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": [
            check_service(name, url)
            for name, url in SERVICES.items()
        ],
    }

    # Continue monitoring when an individual check fails.
    for name, check in (
        ("container_status", check_containers),
        ("storage_status", check_storage),
    ):
        try:
            report[name] = check()

        except Exception as error:
            report[name] = {
                "healthy": False,
                "error_type": type(error).__name__,
            }

    healthy = (
        all(item["healthy"] for item in report["services"])
        and report["container_status"]["healthy"]
        and report["storage_status"]["healthy"]
    )

    report["overall_status"] = (
        "healthy" if healthy else "degraded"
    )

    print(json.dumps(report, indent=2))

    # Return a nonzero exit code when intervention is required.
    return 0 if healthy else 1


if __name__ == "__main__":
    sys.exit(main())