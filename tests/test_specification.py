import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "maininstabot"))

# Allow the focused tests to run even before optional production dependencies are installed.
if "dotenv" not in sys.modules:
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda: None
    sys.modules["dotenv"] = dotenv_stub
if "groq" not in sys.modules:
    groq_stub = types.ModuleType("groq")
    groq_stub.Groq = object
    sys.modules["groq"] = groq_stub

import config
from src import ai
from src.command_parser import parse_command
from src.text_utils import split_message


class SpecificationTests(unittest.TestCase):
    def setUp(self):
        ai.reset_runtime_state()
        self.original = {
            "provider": config.AI_PROVIDER,
            "fallbacks": __import__("os").getenv("AI_FALLBACK_PROVIDERS"),
            "cooldown": config.AI_COOLDOWN_SECONDS,
            "limit": config.MAX_AI_REQUESTS_PER_MINUTE,
            "history": config.MAX_HISTORY_MESSAGES,
            "openai": config.OPENAI_API_KEY,
            "groq": config.GROQ_API_KEY,
            "gemini": config.GEMINI_API_KEY,
        }
        config.AI_PROVIDER = "openai"
        config.AI_COOLDOWN_SECONDS = 0
        config.MAX_AI_REQUESTS_PER_MINUTE = 10
        config.MAX_HISTORY_MESSAGES = 4
        config.OPENAI_API_KEY = "test-openai-key"
        config.GROQ_API_KEY = ""
        config.GEMINI_API_KEY = ""

    def tearDown(self):
        import os
        config.AI_PROVIDER = self.original["provider"]
        config.AI_COOLDOWN_SECONDS = self.original["cooldown"]
        config.MAX_AI_REQUESTS_PER_MINUTE = self.original["limit"]
        config.MAX_HISTORY_MESSAGES = self.original["history"]
        config.OPENAI_API_KEY = self.original["openai"]
        config.GROQ_API_KEY = self.original["groq"]
        config.GEMINI_API_KEY = self.original["gemini"]
        if self.original["fallbacks"] is None:
            os.environ.pop("AI_FALLBACK_PROVIDERS", None)
        else:
            os.environ["AI_FALLBACK_PROVIDERS"] = self.original["fallbacks"]
        ai.reset_runtime_state()

    def test_provider_selection_prefers_selected_provider(self):
        calls = []
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {
            "openai": lambda message, history, prompt: calls.append("openai") or "openai reply",
            "groq": lambda message, history, prompt: calls.append("groq") or "groq reply",
            "gemini": lambda message, history, prompt: calls.append("gemini") or "gemini reply",
        }
        try:
            self.assertEqual(ai.ask_ai("hello", conversation_id="thread-a:user-a"), "openai reply")
            self.assertEqual(calls, ["openai"])
        finally:
            ai.PROVIDERS = original

    def test_provider_fallback_is_used_after_failure(self):
        calls = []
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {
            "openai": lambda message, history, prompt: calls.append("openai") or (_ for _ in ()).throw(RuntimeError("provider down")),
            "groq": lambda message, history, prompt: calls.append("groq") or "fallback reply",
            "gemini": lambda message, history, prompt: calls.append("gemini") or "gemini reply",
        }
        try:
            import os
            os.environ["AI_FALLBACK_PROVIDERS"] = "groq,gemini"
            self.assertEqual(ai.ask_ai("hello", conversation_id="thread-a:user-a"), "fallback reply")
            self.assertEqual(calls, ["openai", "groq"])
        finally:
            ai.PROVIDERS = original

    def test_memory_isolated_and_bounded(self):
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {name: (lambda message, history, prompt: f"reply:{message}") for name in original}
        try:
            for value in ("one", "two", "three"):
                ai.ask_ai(value, conversation_id="thread-a:user-a")
            ai.ask_ai("other", conversation_id="thread-b:user-b")
            self.assertEqual(len(ai._conversations["thread-a:user-a"]), 4)
            self.assertEqual(len(ai._conversations["thread-b:user-b"]), 2)
            self.assertNotIn("other", str(ai._conversations["thread-a:user-a"]))
        finally:
            ai.PROVIDERS = original

    def test_cooldown_and_minute_limit(self):
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {name: (lambda message, history, prompt: "ok") for name in original}
        try:
            config.AI_COOLDOWN_SECONDS = 100
            self.assertEqual(ai.ask_ai("one", conversation_id="limited"), "ok")
            self.assertEqual(ai.ask_ai("two", conversation_id="limited"), ai.COOLDOWN_FAILURE)
            ai.reset_runtime_state()
            config.AI_COOLDOWN_SECONDS = 0
            config.MAX_AI_REQUESTS_PER_MINUTE = 2
            self.assertEqual(ai.ask_ai("one", conversation_id="minute-limit"), "ok")
            self.assertEqual(ai.ask_ai("two", conversation_id="minute-limit"), "ok")
            self.assertEqual(ai.ask_ai("three", conversation_id="minute-limit"), ai.COOLDOWN_FAILURE)
        finally:
            ai.PROVIDERS = original

    def test_group_trigger_rules(self):
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {name: (lambda message, history, prompt: f"reply:{message}") for name in original}
        try:
            from src import router
            config.USERNAME = "ayaanbot_"
            config.BOT_NAME = "AYAAN AI"
            config.GROUP_AI_MODE = False
            self.assertIsNone(router.process_message("hello everyone", "group-a", "user-a", "alice", True, None, my_id="bot"))
            self.assertEqual(router.process_message("@ayaanbot_ hello", "group-a", "user-a", "alice", True, None, my_id="bot"), "reply:hello")
            self.assertEqual(router.process_message("AYAAN AI help me", "group-a", "user-a", "alice", True, None, my_id="bot"), "reply:help me")
            self.assertEqual(router.process_message("!ai tell me a joke", "group-a", "user-a", "alice", True, None, my_id="bot"), "reply:tell me a joke")
            self.assertEqual(router.process_message("hello from a DM", "dm-a", "user-a", "alice", False, None, my_id="bot"), "reply:hello from a DM")

            class Reply:
                user_id = "bot"
            class Message:
                replied_to_message = Reply()
            self.assertIsNone(router.process_message("what next?", "group-a", "user-a", "alice", True, None, msg=Message(), my_id="bot"))
        finally:
            ai.PROVIDERS = original

    def test_groq_model_not_found_uses_fallback_model(self):
        class Message:
            content = "fallback works"
        class Choice:
            message = Message()
        class Response:
            choices = [Choice()]
        class Completions:
            def __init__(self):
                self.models = []
            def create(self, **kwargs):
                self.models.append(kwargs["model"])
                if len(self.models) == 1:
                    raise RuntimeError("model_not_found: model does not exist")
                return Response()
        class Client:
            chat = type("Chat", (), {"completions": Completions()})()

        original_client = ai._groq_client
        original_model = config.AI_MODEL
        original_fallback = config.GROQ_FALLBACK_MODEL
        original_key = config.GROQ_API_KEY
        try:
            config.GROQ_API_KEY = "test-groq-key"
            ai._groq_client = Client()
            config.AI_MODEL = "missing-model"
            config.GROQ_FALLBACK_MODEL = "fallback-model"
            self.assertEqual(ai._groq("hello", [], "system"), "fallback works")
            self.assertEqual(ai._groq_client.chat.completions.models, ["missing-model", "fallback-model"])
        finally:
            ai._groq_client = original_client
            config.AI_MODEL = original_model
            config.GROQ_FALLBACK_MODEL = original_fallback
            config.GROQ_API_KEY = original_key

    def test_provider_failure_is_user_safe(self):
        original = ai.PROVIDERS.copy()
        ai.PROVIDERS = {name: (lambda message, history, prompt: (_ for _ in ()).throw(RuntimeError("secret-key-should-not-be-shown"))) for name in original}
        try:
            result = ai.ask_ai("hello", conversation_id="failure")
            self.assertEqual(result, ai.FRIENDLY_FAILURE)
            self.assertNotIn("secret-key", result)
        finally:
            ai.PROVIDERS = original

    def test_parser_and_splitter(self):
        self.assertEqual(parse_command("!AI hello world"), ("ai", "hello world"))
        self.assertEqual(parse_command("hello"), (None, "hello"))
        self.assertEqual(parse_command("!"), ("", ""))
        samples = ["short", "line one\n\nline two", "🙂" * 1200, "```python\n" + "x = 1\n" * 400 + "```"]
        for sample in samples:
            chunks = split_message(sample, limit=120)
            self.assertTrue(chunks)
            self.assertTrue(all(len(chunk) <= 120 for chunk in chunks))
            self.assertEqual("".join(chunks).replace(" ", ""), sample.replace(" ", "").strip())


if __name__ == "__main__":
    unittest.main()
