import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

import server


class FakeClient:
    def __init__(self, error=None):
        self.sent = []
        self.error = error

    def direct_send(self, text, thread_ids):
        if self.error:
            raise self.error
        self.sent.append((text, thread_ids))


class FakeSessionManager:
    def __init__(self, client):
        self.client = client

    def get_client(self):
        return self.client, "bot"


class ServerDeliveryTests(unittest.TestCase):
    def test_successful_delivery_returns_true_and_uses_string_thread_id(self):
        client = FakeClient()
        original = server.session_manager
        server.session_manager = FakeSessionManager(client)
        try:
            self.assertTrue(server.send_message(123, "hello"))
            self.assertEqual(client.sent, [("hello", ["123"])])
        finally:
            server.session_manager = original

    def test_failed_delivery_returns_false(self):
        client = FakeClient(RuntimeError("403 error_code=1404006"))
        original = server.session_manager
        server.session_manager = FakeSessionManager(client)
        try:
            self.assertFalse(server.send_message("thread", "hello"))
            self.assertEqual(client.sent, [])
        finally:
            server.session_manager = original

    def test_empty_delivery_returns_false(self):
        client = FakeClient()
        original = server.session_manager
        server.session_manager = FakeSessionManager(client)
        try:
            self.assertFalse(server.send_message("thread", ""))
            self.assertEqual(client.sent, [])
        finally:
            server.session_manager = original


if __name__ == "__main__":
    unittest.main()
