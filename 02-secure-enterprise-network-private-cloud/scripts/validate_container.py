import argparse
import errno
import json
import os
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler

# Disable proxy handling and restrict HTTP checks to local loopback.
BASE_URL = "http://127.0.0.1:8080"
HTTP = build_opener(ProxyHandler({}))


def read_process_security():
    attributes = {}

    for line in Path("/proc/1/status").read_text().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            attributes[key] = value.strip()

    return attributes


def verify_read_only_filesystem():
    # Attempt a harmless write and require a read-only filesystem error.
    target = Path("/app/.security_validation")

    try:
        with target.open("x") as file:
            file.write("synthetic security test")

    except OSError as error:
        return error.errno == errno.EROFS

    else:
        target.unlink()
        return False


def verify_endpoint(path, expected_status):
    try:
        with HTTP.open(
            BASE_URL + path,
            timeout=5,
        ) as response:
            return response.status == expected_status

    except HTTPError as error:
        return error.code == expected_status

    except OSError:
        return False


def verify_network_interfaces(profile):
    # Isolated deployments must contain only the loopback interface.
    interfaces = set(os.listdir("/sys/class/net"))

    if profile == "isolated":
        return interfaces == {"lo"}

    # Private deployments must contain only the expected interfaces.
    return interfaces == {"lo", "eth0"}


def verify_ipv4_routes():
    routes = Path("/proc/net/route").read_text()

    # An IPv4 default route would weaken the intended isolation.
    for line in routes.splitlines()[1:]:
        fields = line.split()

        if len(fields) > 1 and fields[1] == "00000000":
            return False

    return True


def verify_ipv6_routes():
    routes = Path("/proc/net/ipv6_route").read_text()

    for line in routes.splitlines():
        fields = line.split()

        # Ignore kernel-generated loopback routing entries.
        if (
            len(fields) >= 10
            and fields[0] == "0" * 32
            and fields[1] == "00"
            and fields[-1] != "lo"
        ):
            return False

    return True


def verify_resolver_configuration():
    # Reject explicitly configured DNS servers.
    resolver = Path("/etc/resolv.conf")

    if not resolver.exists():
        return True

    return not any(
        line.strip().split()[:1] == ["nameserver"]
        for line in resolver.read_text().splitlines()
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--profile",
        choices=["isolated", "private"],
        default="isolated",
    )

    args = parser.parse_args()
    security = read_process_security()

    # Inspect kernel-enforced security and resource restrictions.
    checks = {
        "non_root_uid": os.getuid() == 10001,
        "non_root_gid": os.getgid() == 10001,
        "effective_capabilities": (
            int(security["CapEff"], 16) == 0
        ),
        "no_new_privileges": security["NoNewPrivs"] == "1",
        "seccomp_filtering": security["Seccomp"] == "2",
        "memory_limit": (
            Path("/sys/fs/cgroup/memory.max").read_text().strip()
            == "134217728"
        ),
        "process_limit": (
            Path("/sys/fs/cgroup/pids.max").read_text().strip()
            == "32"
        ),
        "read_only_filesystem": verify_read_only_filesystem(),
        "network_interfaces": verify_network_interfaces(
            args.profile
        ),
        "no_ipv4_default_route": verify_ipv4_routes(),
        "no_ipv6_default_route": verify_ipv6_routes(),
        "no_configured_dns_servers": (
            verify_resolver_configuration()
        ),
        "health_endpoint": verify_endpoint("/health", 200),
        "metadata_endpoint": verify_endpoint("/", 200),
        "undefined_endpoint": verify_endpoint("/unknown", 404),
        "undefined_admin_endpoint": verify_endpoint("/admin", 404),
    }

    passed = sum(checks.values())
    total = len(checks)

    report = {
        "profile": args.profile,
        "checks": checks,
        "passed": passed,
        "total": total,
        "compliant": passed == total,
    }

    print(json.dumps(report, indent=2))

    for name, result in checks.items():
        print(f"{'PASS' if result else 'FAIL'}: {name}")

    print(f"\nContainer validation: {passed}/{total} passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())