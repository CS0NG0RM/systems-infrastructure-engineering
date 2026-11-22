import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import validate_infrastructure as validator


class InfrastructureValidationTests(unittest.TestCase):

    def simulate_validation(self, overrides=None):
        # Simulated server responses avoid network connections.
        responses = {
            "hostname": "labapp01",
            "whoami": "labadmin",
            "getenforce": "Enforcing",
            "systemctl is-active sshd": "active",
            "systemctl is-active firewalld": "active",
            "ip -4 route show default": "",
            "ip -6 route show default": "",
            "sysctl -n net.ipv4.ip_forward": "0",
        }

        responses.update(overrides or {})

        def fake_remote(command):
            output = responses.get(command, "")

            if isinstance(output, Exception):
                raise output

            return {
                "exit_code": 0,
                "output": output,
                "error": "",
            }

        # Temporary reports preserve genuine validation evidence.
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(validator, "REPORT_DIR", Path(directory)):
                with patch.object(
                    validator, "run_remote", side_effect=fake_remote
                ):
                    exit_code = validator.main()

            report_path = Path(directory) / "infrastructure_validation.json"
            report = json.loads(report_path.read_text())

        return exit_code, report

    def test_compliant_server(self):
        code, report = self.simulate_validation()
        self.assertEqual(code, 0)
        self.assertTrue(report["summary"]["compliant"])

    def test_selinux_disabled(self):
        code, report = self.simulate_validation({
            "getenforce": "Disabled"
        })
        self.assertEqual(code, 1)
        self.assertFalse(report["summary"]["compliant"])

    def test_unexpected_default_route(self):
        code, report = self.simulate_validation({
            "ip -4 route show default": "default via 10.20.20.1"
        })
        self.assertEqual(code, 1)
        self.assertFalse(report["summary"]["compliant"])

    def test_firewall_inactive(self):
        code, report = self.simulate_validation({
            "systemctl is-active firewalld": "inactive"
        })
        self.assertEqual(code, 1)
        self.assertFalse(report["summary"]["compliant"])

    def test_forwarding_enabled(self):
        code, report = self.simulate_validation({
            "sysctl -n net.ipv4.ip_forward": "1"
        })
        self.assertEqual(code, 1)
        self.assertFalse(report["summary"]["compliant"])

    def test_connection_timeout(self):
        code, report = self.simulate_validation({
            "hostname": subprocess.TimeoutExpired("ssh", 20)
        })
        self.assertEqual(code, 1)
        self.assertEqual(report["checks"][0]["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
