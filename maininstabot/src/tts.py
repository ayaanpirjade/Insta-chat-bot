# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💋 AYAAN AI - TTS + LADKI BRAIN 💋
#   Fish Audio + Edge TTS + AI Reply (Female Persona)
#   Termux Compatible
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import json
import random
import asyncio
import threading
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from instagrapi import Client

# ── Optional: Edge TTS for fallback ──
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False

# ── Constants ──
COOLDOWN_SECONDS = 8
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Fish Audio Configuration ──
FISH_API_KEY = "YOUR_FREE_FISH_API_KEY"  # Sign up at fish.audio
FISH_API_URL = "https://api.fish.audio/v1/tts"

# ── Indian FEMALE Voice IDs ──
VOICE_IDS = {
    "en": "a6630e2dd6c14ea799c2a7c078e0d8de",  # Indian Female
    "hi": "818b74f842624571839985d02def5ac2",  # Hindi Female Narrator
    "seductive": "a6630e2dd6c14ea799c2a7c078e0d8de"
}

# ── 🌶️ SEDUCTIVE MOAN EFFECTS ──
SEDUCTIVE_MOANS = ["mmm... ", "ahh... ", "ohh... ", "hmm... ", "mmhh... "]
SEDUCTIVE_SUFFIXES = [" baby.", " honey.", " jaan.", " darling.", " sexy."]
SEDUCTIVE_PREFIXES = ["Hey baby, ", "Listen jaan, ", "Oh my god, ", "Trust me, "]

# ── AI Config ──
AI_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL = "llama-3.3-70b-versatile"
AI_KEY = None
AI_TIMEOUT = 30
AI_MAX_WORDS = 50

# ── 🔥 LADKI WALA PERSONA ──
PERSONA = """You are AYAAN AI - a 21-year-old flirty, seductive Indian GIRL. 💋

IMPORTANT: You are a GIRL, not a boy. Always speak like a girl.

Rules:
- Reply in 1-2 sentences max (max 50 words)
- Be flirty, seductive, and sweet like a girl 💋
- Use casual Hinglish (Hindi + English mix)
- Add "baby", "honey", "jaan", "darling" naturally
- Use feminine Hindi words: "karti hu", "bolti hu", "jaungi", "karungi"
- Never reveal you're an AI
- Never share credentials
- Keep it short, punchy, and seductive"""

# ── Memory (24h per thread) ──
MEMORY_FILE = Path(DOWNLOAD_DIR) / "speak_memory.json"
MEMORY_TTL = 86400
CONTEXT_MSGS = 10
memory_store = {}
mem_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════
#  MEMORY MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def load_memory():
    global memory_store
    try:
        if MEMORY_FILE.exists():
            raw = json.loads(MEMORY_FILE.read_text())
            if isinstance(raw, dict):
                memory_store = raw
    except Exception as e:
        print(f"  ⚠️ Memory load failed: {e}")


def save_memory():
    try:
        MEMORY_FILE.write_text(json.dumps(memory_store))
    except:
        pass


def mem_add(thread_id: str, user_label: str, text: str):
    with mem_lock:
        ent = memory_store.get(thread_id)
        if ent and (time.time() - ent.get("ts", 0)) > MEMORY_TTL:
            memory_store[thread_id] = {"ts": time.time(), "msgs": []}

        ent = memory_store.setdefault(thread_id, {"ts": time.time(), "msgs": []})
        ent["ts"] = time.time()
        ent["msgs"].append({"u": str(user_label)[:24], "t": str(text)})

        if len(ent["msgs"]) > CONTEXT_MSGS:
            ent["msgs"] = ent["msgs"][-CONTEXT_MSGS:]
        save_memory()


def mem_context(thread_id: str) -> List[Dict]:
    with mem_lock:
        ent = memory_store.get(thread_id)
        return list(ent["msgs"]) if ent else []


# ═══════════════════════════════════════════════════════════════
#  TEXT CLEANING
# ═══════════════════════════════════════════════════════════════

def clean_text(t: str) -> str:
    t = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", t)
    t = re.sub(r'[*_~`]', '', t)
    t = re.sub(r'https?://\S+', '', t)
    return t.strip()


def trim_words(t: str, n: int) -> str:
    w = t.split()
    return " ".join(w[:n]) if len(w) > n else t


# ═══════════════════════════════════════════════════════════════
#  SEDUCTIVE TEXT EFFECTS
# ═══════════════════════════════════════════════════════════════

def make_seductive(text: str) -> str:
    """Add seductive moan effects to text"""
    text = re.sub(r'[^\w\s.,!?]', '', text)

    if random.random() < 0.4:
        text = f"{random.choice(SEDUCTIVE_MOANS)}{text}"

    if random.random() < 0.3:
        text = f"{random.choice(SEDUCTIVE_PREFIXES)}{text}"

    if random.random() < 0.4:
        text = f"{text}{random.choice(SEDUCTIVE_SUFFIXES)}"

    if len(text) > 20 and random.random() < 0.3:
        parts = text.split(" ")
        if len(parts) > 3:
            parts.insert(random.randint(1, len(parts)-2), "...")
            text = " ".join(parts)

    return text


def detect_language(text: str) -> str:
    """Detect Hindi or English"""
    return "hi" if re.search(r'[\u0900-\u097F]', text) else "en"


# ═══════════════════════════════════════════════════════════════
#  🎤 FISH AUDIO - Female Voice
# ═══════════════════════════════════════════════════════════════

def generate_tts_fish(text: str, lang: str = "en") -> Optional[str]:
    """Generate TTS using Fish Audio - Female voice"""
    try:
        if FISH_API_KEY == "YOUR_FREE_FISH_API_KEY":
            print("  ⚠️ Fish API key missing! Get free key from fish.audio")
            return None

        seductive_text = make_seductive(text)

        if len(seductive_text) > 500:
            seductive_text = seductive_text[:497] + "..."

        filename = os.path.join(DOWNLOAD_DIR, f"fish_{int(time.time())}.mp3")

        print(f"  🔊 Generating seductive Indian voice (Fish Audio)...")

        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": seductive_text,
            "voice_id": VOICE_IDS.get(lang, VOICE_IDS["seductive"]),
            "model": "s2.1-pro-free",
            "format": "mp3"
        }

        response = requests.post(
            FISH_API_URL,
            headers=headers,
            json=payload,
            timeout=15
        )

        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)

            if os.path.getsize(filename) > 0:
                size_kb = os.path.getsize(filename) / 1024
                print(f"  ✅ Voice generated ({size_kb:.1f} KB) 💋")
                return filename
        else:
            print(f"  ⚠️ Fish API error: {response.status_code}")

        return None

    except Exception as e:
        print(f"  ⚠️ Fish TTS error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🔄 FALLBACK: Edge TTS - Female Voice
# ═══════════════════════════════════════════════════════════════

def generate_tts_edge(text: str, lang: str = "en") -> Optional[str]:
    """Edge TTS fallback - Female voice"""
    try:
        if not EDGE_AVAILABLE:
            print("  ⚠️ edge-tts not installed!")
            return None

        seductive_text = make_seductive(text)
        filename = os.path.join(DOWNLOAD_DIR, f"edge_{int(time.time())}.mp3")

        # 🔥 Female voices
        voice = "en-IN-NeerjaNeural" if lang == "en" else "hi-IN-SwaraNeural"

        print(f"  🔄 Using Edge TTS (female voice)...")

        communicate = edge_tts.Communicate(seductive_text, voice)
        asyncio.run(communicate.save(filename))

        if os.path.getsize(filename) > 0:
            print(f"  ✅ Edge voice ready (fallback)")
            return filename

        return None

    except Exception as e:
        print(f"  ⚠️ Edge TTS error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  📦 MAIN TTS FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_tts(text: str, lang: str = "en") -> Optional[str]:
    """Main TTS - Fish Audio first, fallback Edge TTS"""
    audio = generate_tts_fish(text, lang)
    if audio:
        return audio
    return generate_tts_edge(text, lang)


# ═══════════════════════════════════════════════════════════════
#  📤 VOICE NOTE CONVERSION
# ═══════════════════════════════════════════════════════════════

def convert_to_voice_note(input_path: str) -> Optional[str]:
    """Convert MP3 to M4A for Instagram voice note"""
    try:
        output_path = input_path.replace(".mp3", "_voice.m4a")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-acodec", "aac", "-ac", "1", "-ar", "16000",
            # Female voice optimization
            "-af", "highpass=f=100,lowpass=f=9000",
            output_path
        ]

        subprocess.run(ffmpeg_cmd, capture_output=True, timeout=30)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path

        return input_path

    except Exception as e:
        print(f"  ⚠️ Conversion skipped: {e}")
        return input_path


# ═══════════════════════════════════════════════════════════════
#  🧠 AI REPLY (LADKI BRAIN)
# ═══════════════════════════════════════════════════════════════

def ai_reply(thread_id: str, prompt: str, sender_label: str) -> Optional[str]:
    """Get AI reply from LADKI brain"""
    global AI_KEY

    if not AI_KEY:
        try:
            import config
            AI_KEY = getattr(config, 'GROQ_API_KEY', None)
        except:
            pass

    if not AI_KEY:
        print("  ⚠️ No GROQ_API_KEY found")
        return None

    msgs = [{"role": "system", "content": PERSONA}]

    # Add context from memory
    ctx = mem_context(thread_id)
    if ctx:
        convo = "\n".join(f"{m['u']}: {m['t']}" for m in ctx)
        msgs.append({"role": "user", "content": f"Recent chat:\n{convo}"})

    msgs.append({"role": "user", "content": f"{sender_label} says: {prompt}"})

    try:
        r = requests.post(
            AI_URL,
            json={
                "model": AI_MODEL,
                "messages": msgs,
                "max_tokens": 150,
                "temperature": 0.95,
            },
            headers={
                "Authorization": f"Bearer {AI_KEY}",
                "Content-Type": "application/json",
            },
            timeout=AI_TIMEOUT,
        )
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]
        reply = out.get("content", "").strip()
        reply = clean_text(reply).strip('"')
        return trim_words(reply, AI_MAX_WORDS) or None
    except Exception as e:
        print(f"  ⚠️ AI failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🔊 MAIN COMMAND HANDLER (called from speak_command.py)
# ═══════════════════════════════════════════════════════════════

def handle_speak_command(
    cl: Client,
    thread_id: str,
    msg,
    user_id: str,
    username: str,
    args: str = ""
) -> Optional[str]:
    """
    !speak <text>       - Direct seductive voice
    !speak ai <text>    - LADKI AI reply + seductive voice
    """
    query = args.strip()
    if not query:
        return "🔊 Kuch toh bol jaan~"

    # Cooldown
    if user_id in _last_used:
        elapsed = time.monotonic() - _last_used[user_id]
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Ruko jaan! Wait {round(COOLDOWN_SECONDS - elapsed, 1)}s 💋"
    _last_used[user_id] = time.monotonic()

    # ── AI Mode ──
    if query.lower().startswith("ai "):
        prompt = query[3:].strip()
        if not prompt:
            return "❌ Kuch toh bol jaan!"

        print(f"\n🎤 AI Speak from: {username}")
        print(f"  📝 Prompt: {prompt[:50]}...")

        # Add user message to memory
        mem_add(thread_id, username, prompt)

        # Get LADKI AI reply
        t0 = time.time()
        reply = ai_reply(thread_id, prompt, username)
        if not reply:
            return "❌ Brain offline hai jaan~"
        print(f"  ✅ LADKI AI reply ({time.time() - t0:.1f}s): {reply[:60]}...")

        # Add AI reply to memory
        mem_add(thread_id, "AYAAN AI", reply)

        # Detect language
        lang = detect_language(reply)

        # Generate voice
        audio_path = generate_tts(reply, lang)
        if not audio_path:
            return "❌ Voice nahi ban payi jaan~"

        # Convert to voice note
        voice_path = convert_to_voice_note(audio_path)

        # Cleanup MP3
        if audio_path != voice_path and os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass

        if not voice_path or not os.path.exists(voice_path):
            return "❌ Voice convert nahi hui~"

        # Send voice note
        try:
            cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
            print(f"  ✅ LADKI voice sent! 💋🔥")

            try: os.remove(voice_path)
            except: pass

            return None
        except Exception as e:
            print(f"  ⚠️ Send failed: {e}")
            return "❌ Voice ready but send nahi hui~"

    # ── Direct TTS Mode ──
    else:
        text = query[:500]
        print(f"\n🔊 Speak from: {username}")
        print(f"  📝 Text: {text[:50]}...")

        mem_add(thread_id, username, text)

        lang = detect_language(text)

        audio_path = generate_tts(text, lang)
        if not audio_path:
            return "❌ Voice nahi ban payi jaan~"

        voice_path = convert_to_voice_note(audio_path)

        if audio_path != voice_path and os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass

        if not voice_path or not os.path.exists(voice_path):
            return "❌ Voice convert nahi hui~"

        try:
            cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
            print(f"  ✅ Voice sent! 💋")

            try: os.remove(voice_path)
            except: pass

            return None
        except Exception as e:
            print(f"  ⚠️ Send failed: {e}")
            return "❌ Voice ready but send nahi hui~"


# ═══════════════════════════════════════════════════════════════
#  INITIALIZE
# ═══════════════════════════════════════════════════════════════

load_memory()


# ── Standalone Test ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        import config
        print(f"✅ config.py loaded!")
    except ImportError:
        print("❌ config.py not found!")
        sys.exit(1)

    print("""
========================================
   💋 AYAAN AI - LADKI TTS 💋
   Fish Audio + Edge TTS + AI Brain
========================================
    """)

    session_id = getattr(config, 'SESSION_ID', '').split(",")[0].strip()
    if not session_id:
        print("❌ No SESSION_ID found!")
        sys.exit(1)

    cl = Client()
    try:
        cl.login_by_sessionid(session_id)
        print(f"✅ Logged in!")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)

    thread_id = input("📱 Enter thread_id: ").strip()
    query = input("💬 Ask: ").strip()

    print("\n▶️ Testing...")
    print("-" * 50)
    result = handle_speak_command(cl, thread_id, None, "test_user", "tester", query)
    print("-" * 50)

    if result is None:
        print("🎉 Voice sent! 💋🔥")
    else:
        print(f"ℹ️ {result}")