import unittest

from application.health_service import (
    build_health_response,
    build_service_response,
    route_request,
)


class HealthServiceTests(unittest.TestCase):

    def test_health_status(self):
        response = build_health_response()
        self.assertEqual(response["status"], "healthy")

    def test_service_identity(self):
        response = build_health_response()
        self.assertEqual(response["service"], "enterprise-platform")

    def test_uptime_is_non_negative(self):
        response = build_health_response()
        self.assertGreaterEqual(response["uptime_seconds"], 0)

    def test_data_classification(self):
        response = build_service_response()
        self.assertEqual(response["data_classification"], "synthetic")

    def test_health_endpoint(self):
        status, response = route_request("/health")
        self.assertEqual(status, 200)
        self.assertEqual(response["status"], "healthy")

    def test_root_endpoint(self):
        status, response = route_request("/")
        self.assertEqual(status, 200)
        self.assertEqual(response["service"], "enterprise-platform")

    def test_unknown_endpoint(self):
        status, response = route_request("/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(response["error"], "Endpoint not found")

    def test_undefined_admin_endpoint(self):
        status, _ = route_request("/admin")
        self.assertEqual(status, 404)

    def test_no_sensitive_metadata_fields(self):
        response = build_service_response()
        self.assertEqual(
            set(response),
            {"service", "version", "data_classification"},
        )


if __name__ == "__main__":
    unittest.main()