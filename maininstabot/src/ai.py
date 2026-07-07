# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#     Groq AI Chat (Super Fast)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from groq import Groq
import config

# Initialize Groq client
_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


# ── Per-user conversation memory (last few messages) ──
_conversations: dict[str, list] = {}
MAX_HISTORY = 6  # keep last 6 messages per user


def ask_ai(user_message: str, user_id: str = "default") -> str:
    """Send a message to Groq AI and get a response."""
    try:
        client = _get_client()

        # Build conversation history
        if user_id not in _conversations:
            _conversations[user_id] = []

        history = _conversations[user_id]
        history.append({"role": "user", "content": user_message})

        # Trim to max history
        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
            _conversations[user_id] = history

        messages = [
            {"role": "system", "content": config.BOT_PERSONALITY},
            *history,
        ]

        response = client.chat.completions.create(
            model=config.AI_MODEL,
            messages=messages,
            max_tokens=250,
            temperature=0.8,
        )

        reply = response.choices[0].message.content.strip()

        # Save assistant reply to history
        history.append({"role": "assistant", "content": reply})
        if len(history) > MAX_HISTORY:
            _conversations[user_id] = history[-MAX_HISTORY:]

        return reply

    except Exception as e:
        print(f"  ⚠️ Groq AI error: {e}")
        return "Oops, my brain glitched for a sec 🤖💥 Try again!"


def clear_history(user_id: str):
    """Clear conversation history for a user."""
    _conversations.pop(user_id, None)
