# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#        Configuration Loader
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
from dotenv import load_dotenv

load_dotenv()

# ── Instagram ─────────────────────────
SESSION_ID      = os.getenv("SESSION_ID", "")

# ── Groq AI ───────────────────────────
GROQ_API_KEY    = os.getenv("GROQ_API_KEY", "")
AI_MODEL        = os.getenv("AI_MODEL", "llama-3.1-8b-instant")

# ── Bot Identity ──────────────────────
BOT_NAME        = os.getenv("BOT_NAME", "AYAAN AI")
USERNAME        = os.getenv("BOT_USERNAME", "ayaanbot_")
PREFIX          = os.getenv("PREFIX", "!")
BRAND           = os.getenv("BRAND", "AYAAN AI • Your Smart Instagram Buddy")

# ── Polling ───────────────────────────
POLL_INTERVAL   = int(os.getenv("POLL_INTERVAL", "2"))

# ── AI Personality ────────────────────
BOT_PERSONALITY = (
    f"You are {BOT_NAME}, a fun, witty, and helpful AI assistant in an Instagram chat. "
    "Keep replies SHORT (2-3 sentences max), conversational, and use emojis occasionally. "
    "Be friendly, sarcastic when appropriate, and always entertaining. "
    "Never break character. Never mention being a language model."
)

# ── Paths ─────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
DATA_DIR        = os.path.join(BASE_DIR, "data")
USERS_DIR       = os.path.join(BASE_DIR, "users")
