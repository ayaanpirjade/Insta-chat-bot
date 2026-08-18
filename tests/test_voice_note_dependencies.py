import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

from src import voice_note


class VoiceNoteDependencyTests(unittest.TestCase):
    def test_deno_user_install_path_is_found_without_path_entry(self):
        def is_file(path):
            return path == "/home/test/.deno/bin/deno"

        with patch.object(voice_note.shutil, "which", return_value=None), \
             patch.object(voice_note.os.path, "expanduser", return_value="/home/test"), \
             patch.object(voice_note.os.path, "isfile", side_effect=is_file), \
             patch.object(voice_note.os, "access", return_value=True):
            self.assertEqual(
                voice_note.find_executable("deno"),
                "/home/test/.deno/bin/deno",
            )


if __name__ == "__main__":
    unittest.main()
