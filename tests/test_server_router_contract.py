import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ServerRouterContractTests(unittest.TestCase):
    def test_changegroupname_alias_is_supported(self):
        source = (ROOT / "maininstabot" / "src" / "router.py").read_text()
        self.assertIn('"changegroupname"', source)
        self.assertIn("group_admin.handle_changename_command", source)

    def test_name_cycle_commands_are_supported(self):
        source = (ROOT / "maininstabot" / "src" / "router.py").read_text()
        self.assertIn('"nc"', source)
        self.assertIn('"ncstop"', source)
        self.assertIn("group_admin.handle_nc_command", source)
        self.assertIn("group_admin.handle_nc_stop_command", source)

    def test_server_passes_group_flag_to_router(self):
        source = (ROOT / "maininstabot" / "server.py").read_text()
        tree = ast.parse(source)
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "process_message":
                    calls.append(node)
        self.assertEqual(len(calls), 1)
        keyword_names = {keyword.arg for keyword in calls[0].keywords}
        self.assertIn("is_group", keyword_names)
        self.assertIn("my_id", keyword_names)


if __name__ == "__main__":
    unittest.main()
