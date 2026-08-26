import unittest
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

from src import reel

class ReelDetectionTests(unittest.TestCase):
    def test_extract_reel_from_clip(self):
        msg = SimpleNamespace(
            clip=SimpleNamespace(
                code="C12345",
                user=SimpleNamespace(username="testuser")
            )
        )
        data = reel.extract_reel_from_message(msg)
        self.assertIsNotNone(data)
        self.assertEqual(data['code'], "C12345")
        self.assertEqual(data['source'], "clip")

    def test_extract_reel_from_media_share(self):
        msg = SimpleNamespace(
            media_share=SimpleNamespace(
                code="M67890",
                user=SimpleNamespace(username="shareuser")
            )
        )
        data = reel.extract_reel_from_message(msg)
        self.assertIsNotNone(data)
        self.assertEqual(data['code'], "M67890")
        self.assertEqual(data['source'], "media_share")

    def test_get_replied_message_various_formats(self):
        # Test reply_to_item_id
        msg1 = SimpleNamespace(reply_to_item_id="111")
        # Test replied_to_message
        msg2 = SimpleNamespace(replied_to_message=SimpleNamespace(id="222"))
        # Test reply object with item_type (full message)
        msg3 = SimpleNamespace(reply=SimpleNamespace(item_type="clip", code="333"))
        
        # Mock client
        class FakeClient:
            def direct_messages(self, tid, amount):
                return [
                    SimpleNamespace(id="111", item_type="text", text="hi"),
                    SimpleNamespace(id="222", item_type="text", text="hello")
                ]
        
        cl = FakeClient()
        
        # Case 1: reply_to_item_id
        replied1 = reel.get_replied_message(cl, "tid", msg1)
        self.assertEqual(replied1.id, "111")
        
        # Case 2: replied_to_message
        replied2 = reel.get_replied_message(cl, "tid", msg2)
        self.assertEqual(replied2.id, "222")
        
        # Case 3: full reply object (no fetch needed)
        replied3 = reel.get_replied_message(cl, "tid", msg3)
        self.assertEqual(replied3.code, "333")

if __name__ == "__main__":
    unittest.main()
