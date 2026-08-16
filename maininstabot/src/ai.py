# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#     Groq AI Chat + Gemini Fallback (Auto-load from .env)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
import requests
import config
from groq import Groq

# ── Gemini Setup (Fallback) ──
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Initialize clients
_client = None
_gemini_model = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def _get_gemini_model():
    """Initialize Gemini model from config"""
    global _gemini_model
    if _gemini_model is None and GEMINI_AVAILABLE:
        try:
            api_key = config.GEMINI_API_KEY  # ⬅️ config se load
            if api_key:
                genai.configure(api_key=api_key)
                _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
                print("✅ Gemini Flash initialized!")
        except Exception as e:
            print(f"⚠️ Gemini init failed: {e}")
    return _gemini_model


# ── Per-chat conversation memory ──
# Keying by chat + user prevents a private conversation from leaking into another chat.
_conversations: dict[str, list] = {}
MAX_HISTORY = 8
MAX_MESSAGE_CHARS = 4000


def ask_openai(user_message: str, history: list) -> str | None:
    """Send a message to ChatGPT through the OpenAI-compatible chat completions API."""
    if not config.OPENAI_API_KEY:
        return None

    messages = [
        {"role": "system", "content": config.BOT_PERSONALITY},
        *history,
        {"role": "user", "content": user_message},
    ]
    response = requests.post(
        f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.OPENAI_MODEL,
            "messages": messages,
            "max_tokens": 450,
            "temperature": 0.75,
        },
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    choices = data.get("choices") or []
    if not choices:
        return None
    content = choices[0].get("message", {}).get("content", "")
    return content.strip() or None


def ask_groq(user_message: str, history: list) -> str:
    """Send message to Groq AI"""
    client = _get_client()
    
    messages = [
        {"role": "system", "content": config.BOT_PERSONALITY},
        *history,
        {"role": "user", "content": user_message},
    ]
    
    response = client.chat.completions.create(
        model=config.AI_MODEL,
        messages=messages,
        max_tokens=250,
        temperature=0.8,
    )
    
    return response.choices[0].message.content.strip()


def ask_gemini(user_message: str, history: list) -> str:
    """Fallback to Gemini Flash (FREE 1M tokens/day)"""
    model = _get_gemini_model()
    if not model:
        return None
    
    # Build context from history
    context = ""
    for h in history[-10:]:
        role = "User" if h["role"] == "user" else "Assistant"
        context += f"{role}: {h['content']}\n"
    
    prompt = f"""{config.BOT_PERSONALITY}

Previous conversation:
{context}
User: {user_message}
Assistant:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  ⚠️ Gemini error: {e}")
        return None


def ask_ai(user_message: str, user_id: str = "default", conversation_id: str | None = None) -> str:
    """Send a message to ChatGPT first, then use configured AI fallbacks."""
    user_message = (user_message or "").strip()[:MAX_MESSAGE_CHARS]
    memory_key = conversation_id or user_id

    try:
        history = _conversations.setdefault(memory_key, [])

        # ChatGPT is the primary provider when OPENAI_API_KEY is configured.
        if config.OPENAI_API_KEY:
            try:
                print(f"  🤖 ChatGPT: {user_message[:30]}...")
                reply = ask_openai(user_message, history)
                if reply:
                    print("  ✅ ChatGPT responded!")
                    _save_history(memory_key, user_message, reply)
                    return reply
            except Exception as e:
                print(f"  ⚠️ ChatGPT failed: {e}")

        # Existing providers remain available as fallbacks.
        if config.GROQ_API_KEY:
            try:
                print(f"  🤖 Groq fallback: {user_message[:30]}...")
                reply = ask_groq(user_message, history)
                if reply:
                    _save_history(memory_key, user_message, reply)
                    return reply
            except Exception as e:
                print(f"  ⚠️ Groq failed: {e}")

        try:
            reply = ask_gemini(user_message, history)
            if reply:
                _save_history(memory_key, user_message, reply)
                return reply
        except Exception as e:
            print(f"  ⚠️ Gemini failed: {e}")

        return "⚠️ My AI services are busy right now. Please try again in a moment."
    except Exception as e:
        print(f"  ⚠️ AI error: {e}")
        return "Oops, my brain glitched for a second. Please try again!"


def _save_history(user_id: str, user_message: str, reply: str):
    """Save conversation to history"""
    if user_id not in _conversations:
        _conversations[user_id] = []
    
    _conversations[user_id].append({"role": "user", "content": user_message})
    _conversations[user_id].append({"role": "assistant", "content": reply})
    
    # Keep only last MAX_HISTORY messages
    if len(_conversations[user_id]) > MAX_HISTORY:
        _conversations[user_id] = _conversations[user_id][-MAX_HISTORY:]


def clear_history(user_id: str):
    """Clear conversation history for a user or chat context."""
    _conversations.pop(user_id, None)
    return "🧹 Chat memory cleared. Fresh start! ✨"
