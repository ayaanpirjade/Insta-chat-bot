import unittest
import sys
import os
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

from src import voice_note_storage as vn_storage

class VNStorageTests(unittest.TestCase):
    def test_extract_vn_url(self):
        # Mock message with voice_media
        msg = SimpleNamespace(
            voice_media=SimpleNamespace(
                media=SimpleNamespace(
                    audio={'audio_src': 'https://example.com/audio.m4a'}
                )
            )
        )
        url = vn_storage.extract_vn_url_from_message(msg)
        self.assertEqual(url, 'https://example.com/audio.m4a')

    def test_recursive_url_detection(self):
        # Deeply nested URL in a custom structure
        msg = SimpleNamespace(
            something=SimpleNamespace(
                nested=[
                    {'random': 'data'},
                    {'audio_link': 'https://cdninstagram.com/v/t50/audio_src_123.m4a?token=xyz'}
                ]
            )
        )
        url = vn_storage.extract_vn_url_from_message(msg, robust=True)
        self.assertIn('audio_src_123.m4a', url)

    def test_handle_pvn_no_file(self):
        # Mock client
        class FakeClient:
            def direct_send_voice(self, path, thread_ids):
                pass
        
        cl = FakeClient()
        result = vn_storage.handle_pvn_command("non_existent_vn", "user", "username", "tid", cl)
        self.assertIn("not found", result)

    def test_handle_pvn_list_files(self):
        # Ensure directory exists
        os.makedirs(vn_storage.VN_DATA_DIR, exist_ok=True)
        # Mock client
        class FakeClient:
            pass
        
        cl = FakeClient()
        # Should return a list or "No saved voice notes found"
        result = vn_storage.handle_pvn_command("", "user", "username", "tid", cl)
        self.assertTrue(isinstance(result, str))

if __name__ == "__main__":
    unittest.main()
