import signal
import unittest
from unittest.mock import Mock, patch

from application.health_service import register_shutdown_handlers


class ServiceLifecycleTests(unittest.TestCase):

    @patch("application.health_service.signal.signal")
    def test_shutdown_signal_registration(self, register_signal):
        server = Mock()

        register_shutdown_handlers(server)

        registered_signals = {
            call.args[0]
            for call in register_signal.call_args_list
        }

        self.assertEqual(
            registered_signals,
            {signal.SIGTERM, signal.SIGINT},
        )

    @patch("application.health_service.threading.Thread")
    @patch("application.health_service.signal.signal")
    def test_shutdown_uses_separate_thread(
        self, register_signal, thread_factory
    ):
        server = Mock()

        register_shutdown_handlers(server)

        handler = register_signal.call_args_list[0].args[1]
        handler(signal.SIGTERM, None)

        thread_factory.assert_called_once_with(
            target=server.shutdown,
            daemon=True,
        )

        thread_factory.return_value.start.assert_called_once()

    @patch("application.health_service.threading.Thread")
    @patch("application.health_service.signal.signal")
    def test_duplicate_shutdown_requests(
        self, register_signal, thread_factory
    ):
        server = Mock()

        register_shutdown_handlers(server)

        handler = register_signal.call_args_list[0].args[1]

        handler(signal.SIGTERM, None)
        handler(signal.SIGTERM, None)

        thread_factory.assert_called_once()


if __name__ == "__main__":
    unittest.main()