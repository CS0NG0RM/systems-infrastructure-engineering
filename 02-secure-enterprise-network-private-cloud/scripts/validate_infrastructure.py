import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Fixed destination within the isolated laboratory.
HOST = "10.20.20.10"
USER = "labadmin"
KEY = Path.home() / ".ssh/lab_automation_ed25519"

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def run_remote(command):
    # Use the dedicated key and require a previously verified host identity.
    result = subprocess.run(
        [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=yes",
            "-o", "IdentitiesOnly=yes",
            "-o", "ConnectTimeout=5",
            "-i", str(KEY),
            f"{USER}@{HOST}",
            command,
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )

    return {
        "exit_code": result.returncode,
        "output": result.stdout.strip(),
        "error": result.stderr.strip(),
    }


def main():
    # Each check has an explicit expected result.
    checks = [
        ("hostname", "hostname", "labapp01"),
        ("user_identity", "whoami", "labadmin"),
        ("selinux", "getenforce", "Enforcing"),
        ("ssh_service", "systemctl is-active sshd", "active"),
        ("host_firewall", "systemctl is-active firewalld", "active"),
        ("no_ipv4_default_route", "ip -4 route show default", ""),
        ("no_ipv6_default_route", "ip -6 route show default", ""),
        ("ipv4_forwarding", "sysctl -n net.ipv4.ip_forward", "0"),
    ]

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "target": HOST,
        "checks": [],
    }

    for name, command, expected in checks:
        try:
            result = run_remote(command)

            passed = (
                result["exit_code"] == 0
                and result["output"] == expected
            )

            report["checks"].append({
                "name": name,
                "expected": expected,
                "actual": result["output"],
                "error": result["error"],
                "status": "PASS" if passed else "FAIL",
            })

            print(f"{'PASS' if passed else 'FAIL'}: {name}")

        except (subprocess.TimeoutExpired, OSError) as error:
            report["checks"].append({
                "name": name,
                "status": "ERROR",
                "error": str(error),
            })

            print(f"ERROR: {name}")

    # Collect resource information separately from compliance checks.
    report["resources"] = {}

    for name, command in [
        ("memory", "free -m"),
        ("storage", "df -h /"),
        ("system_load", "uptime"),
        ("routing", "ip -4 route"),
    ]:
        try:
            report["resources"][name] = run_remote(command)
        except (subprocess.TimeoutExpired, OSError) as error:
            report["resources"][name] = {"error": str(error)}

    passed = sum(
        check["status"] == "PASS"
        for check in report["checks"]
    )

    total = len(report["checks"])

    report["summary"] = {
        "passed": passed,
        "total": total,
        "compliant": passed == total,
    }

    # Store structured evidence locally for later analysis.
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / "infrastructure_validation.json"

    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(f"\nValidation result: {passed}/{total} checks passed")
    print(f"Report saved: {report_path}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
