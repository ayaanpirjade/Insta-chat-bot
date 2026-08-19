import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

from src import group_admin


class FakeClient:
    user_id = 100
    uuid = "test-uuid"

    def __init__(self):
        self.add_calls = []
        self.title_calls = []
        self.private_calls = []

    def user_info_by_username(self, username):
        return SimpleNamespace(pk=200)

    def direct_thread(self, thread_id):
        return SimpleNamespace(is_group=True, admin_user_ids=[100])

    def direct_thread_add_users(self, thread_id, user_ids):
        self.add_calls.append((thread_id, user_ids))
        return True

    def direct_thread_update_title(self, thread_id, title):
        self.title_calls.append((thread_id, title))
        return True

    def private_request(self, *args, **kwargs):
        self.private_calls.append((args, kwargs))
        return {"status": "ok"}


class GroupAdminTests(unittest.TestCase):
    def setUp(self):
        group_admin._last_used.clear()

    def test_add_uses_supported_instagram_helper(self):
        client = FakeClient()
        result = group_admin.handle_add_command("@target", "100", "owner", "123", client)
        self.assertIn("added to the group", result)
        self.assertEqual(client.add_calls, [(123, [200])])

    def test_change_name_uses_supported_instagram_helper(self):
        client = FakeClient()
        result = group_admin.handle_changename_command("New name", "100", "owner", "123", client)
        self.assertIn("Group name changed", result)
        self.assertEqual(client.title_calls, [(123, "New name")])

    def test_permission_error_is_user_safe(self):
        message = group_admin._group_action_error("add @target", RuntimeError("403 error_code=1545037"))
        self.assertIn("group admin", message)
        self.assertNotIn("1545037", message)


if __name__ == "__main__":
    unittest.main()
