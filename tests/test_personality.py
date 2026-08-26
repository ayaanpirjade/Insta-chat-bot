import unittest
from maininstabot import config

class PersonalityTests(unittest.TestCase):
    def test_system_prompt_contains_friendly_guidance(self):
        prompt = config.BOT_SYSTEM_PROMPT.lower()
        self.assertIn("friendly", prompt)
        self.assertIn("warm", prompt)
        self.assertIn("conversational", prompt)

    def test_system_prompt_contains_language_restriction(self):
        prompt = config.BOT_SYSTEM_PROMPT.lower()
        self.assertIn("english", prompt)
        self.assertIn("hinglish", prompt)
        self.assertIn("only", prompt)
        self.assertIn("do not use any other languages", prompt)

if __name__ == "__main__":
    unittest.main()
