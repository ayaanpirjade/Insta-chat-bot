import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PATHS = (
    ".env",
    "maininstabot/cookies.txt",
    "maininstabot/session_settings.json",
)
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
)


class SecurityTests(unittest.TestCase):
    def tracked_files(self):
        output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
        return [line for line in output.splitlines() if line]

    def test_private_runtime_paths_are_not_tracked(self):
        tracked = set(self.tracked_files())
        self.assertFalse(tracked.intersection(PRIVATE_PATHS))
        self.assertFalse(any(path.startswith("maininstabot/users/") for path in tracked))
        self.assertFalse(any("__pycache__/" in path for path in tracked))

    def test_obvious_credential_patterns_are_absent(self):
        for relative_path in self.tracked_files():
            path = ROOT / relative_path
            if not path.is_file() or path.stat().st_size > 2_000_000:
                continue
            content = path.read_text(errors="ignore")
            for pattern in SECRET_PATTERNS:
                self.assertIsNone(pattern.search(content), f"Credential-like value in {relative_path}")


if __name__ == "__main__":
    unittest.main()
