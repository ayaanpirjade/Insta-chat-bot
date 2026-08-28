import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_example():
    values = {}
    for line in (ROOT / ".env.example").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


class ConfigurationTests(unittest.TestCase):
    def test_requested_safe_settings(self):
        values = load_example()
        self.assertEqual(values["OWNER_ID"], "39285878504")
        self.assertEqual(values["OWNER_IDS"], "39285878504")
        self.assertEqual(values["BOT_USERNAME"], "manus_automate")
        self.assertEqual(values["POLL_INTERVAL"], "2")
        self.assertEqual(values["AI_PROVIDER"], "groq")
        self.assertEqual(values["AI_MODEL"], "openai/gpt-oss-120b")
        self.assertEqual(values["GROQ_FALLBACK_MODEL"], "openai/gpt-oss-20b")
        self.assertIn("groq/compound", values["GROQ_FALLBACK_MODELS"])
        self.assertEqual(values["GROUP_AI_MODE"], "false")

    def test_example_contains_no_live_secrets(self):
        text = (ROOT / ".env.example").read_text()
        self.assertNotIn("SESSION_ID=35577929144", text)
        self.assertNotIn("GROQ_API_KEY=gsk_", text)
        self.assertNotIn("GEMINI_API_KEY=AQ.", text)


if __name__ == "__main__":
    unittest.main()
