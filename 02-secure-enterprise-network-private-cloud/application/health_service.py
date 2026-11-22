import json
import os
import signal
import threading
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

# Fixed service identity for the synthetic enterprise environment.
SERVICE_NAME = "enterprise-platform"
SERVICE_VERSION = "1.0.1"
STARTED_AT = datetime.now(timezone.utc)


def build_health_response():
    # Calculate process uptime for operational monitoring.
    uptime = datetime.now(timezone.utc) - STARTED_AT

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "healthy",
        "environment": "isolated-laboratory",
        "uptime_seconds": int(uptime.total_seconds()),
    }


def build_service_response():
    # Return metadata without exposing sensitive configuration.
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "data_classification": "synthetic",
    }


def route_request(path):
    # Allow only explicitly defined application endpoints.
    if path == "/health":
        return 200, build_health_response()

    if path == "/":
        return 200, build_service_response()

    return 404, {"error": "Endpoint not found"}


class ServiceHandler(BaseHTTPRequestHandler):

    def setup(self):
        super().setup()

        # Prevent inactive clients from blocking the server indefinitely.
        self.connection.settimeout(5)

    def do_GET(self):
        status, payload = route_request(self.path)
        response = json.dumps(payload).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        self.wfile.write(response)


def register_shutdown_handlers(server):
    shutdown_requested = threading.Event()

    def handle_shutdown(signum, frame):
        # Prevent duplicate shutdown requests.
        if shutdown_requested.is_set():
            return

        shutdown_requested.set()

        print(
            f"Shutdown requested by signal {signum}",
            flush=True,
        )

        # Run shutdown separately to avoid blocking serve_forever().
        threading.Thread(
            target=server.shutdown,
            daemon=True,
        ).start()

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)


def main():
    # Default to loopback unless deployment explicitly overrides it.
    host = os.environ.get("SERVICE_HOST", "127.0.0.1")
    port = int(os.environ.get("SERVICE_PORT", "8080"))

    with HTTPServer((host, port), ServiceHandler) as server:
        register_shutdown_handlers(server)

        print(
            f"{SERVICE_NAME} {SERVICE_VERSION} listening on port {port}",
            flush=True,
        )

        server.serve_forever()

    print("Graceful shutdown completed", flush=True)


if __name__ == "__main__":
    main()