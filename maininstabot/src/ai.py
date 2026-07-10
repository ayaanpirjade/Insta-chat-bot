# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#     Groq AI Chat + Gemini Fallback (Auto-load from .env)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
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


# ── Per-user conversation memory ──
_conversations: dict[str, list] = {}
MAX_HISTORY = 6


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


def ask_ai(user_message: str, user_id: str = "default") -> str:
    """Send message to AI with Groq primary + Gemini fallback"""
    try:
        # Get or create conversation history
        if user_id not in _conversations:
            _conversations[user_id] = []

        history = _conversations[user_id]
        
        # ── TRY GROQ FIRST ──
        try:
            print(f"  🤖 Groq: {user_message[:30]}...")
            reply = ask_groq(user_message, history)
            if reply:
                print(f"  ✅ Groq responded!")
                _save_history(user_id, user_message, reply)
                return reply
        except Exception as e:
            error_str = str(e).lower()
            print(f"  ⚠️ Groq failed: {e}")
            
            # If rate limit, try Gemini
            if "429" in error_str or "rate_limit" in error_str:
                print(f"  🔄 Rate limit, trying Gemini...")
            else:
                print(f"  🔄 Groq error, trying Gemini...")
        
        # ── FALLBACK TO GEMINI ──
        try:
            print(f"  🤖 Gemini Flash: {user_message[:30]}...")
            reply = ask_gemini(user_message, history)
            if reply:
                print(f"  ✅ Gemini responded!")
                _save_history(user_id, user_message, reply)
                return reply
        except Exception as e:
            print(f"  ⚠️ Gemini failed: {e}")
        
        # ── ULTIMATE FALLBACK ──
        return "⚠️ All AI services are busy. Please try again in a few minutes. 🙏"
        
    except Exception as e:
        print(f"  ⚠️ AI error: {e}")
        return "Oops, my brain glitched for a sec 🤖💥 Try again!"


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
    """Clear conversation history for a user."""
    _conversations.pop(user_id, None)
    return "🧹 History cleared! Fresh start! ✨"
