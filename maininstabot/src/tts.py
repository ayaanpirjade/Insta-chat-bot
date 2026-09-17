# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💋 AYAAN AI - tts.py
#   Edge TTS (Primary - Free) + Fish Audio (Optional Fallback)
#   LADKI Brain + Female Voice
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import uuid
import json
import random
import asyncio
import threading
import subprocess
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List
from instagrapi import Client
from dotenv import load_dotenv

# ── Load .env ──
load_dotenv()

# ── Optional: Edge TTS ──
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False
    print("⚠️ edge-tts not installed! Run: pip install edge-tts")

# ── Constants ──
COOLDOWN_SECONDS = 8
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Fish Audio (Optional - only if credit available) ──
FISH_API_KEY = os.getenv("FISH_AUDIO_API_KEY", "")
FISH_API_URL = "https://api.fish.audio/v1/tts"
CUSTOM_VOICE_ID = "7981ebac70314924bbc9ace34ce8f775"

# ── Edge TTS Female Voices (FREE) ──
EDGE_VOICES = {
    "en": "en-IN-NeerjaNeural",      # Indian English Female
    "hi": "hi-IN-SwaraNeural",       # Hindi Female
}

# ── Seductive Effects ──
SEDUCTIVE_MOANS = ["mmm... ", "ahh... ", "ohh... ", "hmm... "]
SEDUCTIVE_SUFFIXES = [" baby.", " honey.", " jaan.", " darling."]
SEDUCTIVE_PREFIXES = ["Hey baby, ", "Listen jaan, ", "Oh my god, "]

# ── AI Config ──
AI_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL = "llama-3.3-70b-versatile"
AI_KEY = os.getenv("GROQ_API_KEY", "")
AI_TIMEOUT = 30
AI_MAX_WORDS = 50

# ── LADKI PERSONA ──
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

# ── Memory ──
MEMORY_FILE = Path(DOWNLOAD_DIR) / "speak_memory.json"
MEMORY_TTL = 86400
CONTEXT_MSGS = 10
memory_store = {}
mem_lock = threading.Lock()

# ── TTS Lock ──
tts_lock = threading.Lock()


# ═══════════════════════════════════════════════════════════════
#  MEMORY
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


def clean_text(t: str) -> str:
    t = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", t)
    t = re.sub(r'[*_~`]', '', t)
    t = re.sub(r'https?://\S+', '', t)
    return t.strip()


def trim_words(t: str, n: int) -> str:
    w = t.split()
    return " ".join(w[:n]) if len(w) > n else t


def make_seductive(text: str) -> str:
    text = re.sub(r'[^\w\s.,!?]', '', text)
    if random.random() < 0.3:
        text = f"{random.choice(SEDUCTIVE_MOANS)}{text}"
    if random.random() < 0.2:
        text = f"{random.choice(SEDUCTIVE_PREFIXES)}{text}"
    if random.random() < 0.3:
        text = f"{text}{random.choice(SEDUCTIVE_SUFFIXES)}"
    return text


def detect_language(text: str) -> str:
    return "hi" if re.search(r'[\u0900-\u097F]', text) else "en"


# ═══════════════════════════════════════════════════════════════
#  🎤 EDGE TTS (PRIMARY - FREE, UNLIMITED)
# ═══════════════════════════════════════════════════════════════

def generate_tts_edge(text: str, lang: str = "en") -> Optional[str]:
    """Edge TTS - Free, unlimited, female Indian voice"""
    try:
        if not EDGE_AVAILABLE:
            print("  ⚠️ edge-tts not installed!")
            return None

        seductive_text = make_seductive(text)
        filename = os.path.join(DOWNLOAD_DIR, f"edge_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp3")

        voice = EDGE_VOICES.get(lang, EDGE_VOICES["en"])

        print(f"  🎤 Edge TTS ({voice})...")

        # Edge TTS is async - run in new event loop
        communicate = edge_tts.Communicate(seductive_text, voice)
        asyncio.run(communicate.save(filename))

        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ Edge voice ready ({size_kb:.1f} KB)")
            return filename

        return None

    except Exception as e:
        print(f"  ⚠️ Edge TTS error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🎣 FISH AUDIO (OPTIONAL FALLBACK)
# ═══════════════════════════════════════════════════════════════

def generate_tts_fish(text: str, lang: str = "en") -> Optional[str]:
    """Fish Audio - only if API credit available"""
    try:
        if not FISH_API_KEY:
            return None

        seductive_text = make_seductive(text)
        if len(seductive_text) > 500:
            seductive_text = seductive_text[:497] + "..."

        filename = os.path.join(DOWNLOAD_DIR, f"fish_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp3")

        print(f"  🎣 Trying Fish Audio (custom voice)...")

        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "text": seductive_text,
            "reference_id": CUSTOM_VOICE_ID,
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
                print(f"  ✅ Fish voice ready ({size_kb:.1f} KB) 💋")
                return filename
        elif response.status_code == 402:
            print(f"  ⚠️ Fish: No API credit (using Edge TTS)")
        elif response.status_code == 401:
            print(f"  ⚠️ Fish: Invalid API key")
        else:
            print(f"  ⚠️ Fish error: {response.status_code}")

        return None

    except Exception as e:
        print(f"  ⚠️ Fish TTS error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  📦 MAIN TTS FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_tts(text: str, lang: str = "en") -> Optional[str]:
    """
    Main TTS - Edge TTS first (free & reliable), Fish optional
    """
    # 🔥 Edge TTS PRIMARY (free, always works)
    audio = generate_tts_edge(text, lang)
    if audio:
        return audio

    # Fallback: Fish Audio (only if Edge fails, rare)
    print(f"  🔄 Edge failed, trying Fish Audio...")
    return generate_tts_fish(text, lang)


# ═══════════════════════════════════════════════════════════════
#  📤 VOICE NOTE CONVERSION
# ═══════════════════════════════════════════════════════════════

def convert_to_voice_note(input_path: str) -> Optional[str]:
    """Convert MP3 to M4A (Instagram voice note format)"""
    try:
        output_path = input_path.replace(".mp3", "_voice.m4a")

        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-acodec", "aac", "-ac", "1", "-ar", "16000",
            "-af", "highpass=f=80,lowpass=f=9000",
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
    if not AI_KEY:
        print("  ⚠️ No GROQ_API_KEY in .env!")
        return None

    msgs = [{"role": "system", "content": PERSONA}]
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
#  🔊 MAIN HANDLER
# ═══════════════════════════════════════════════════════════════

def handle_speak_command(
    cl: Client,
    thread_id: str,
    msg,
    user_id: str,
    username: str,
    args: str = ""
) -> Optional[str]:
    """!speak command handler"""

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

        mem_add(thread_id, username, prompt)

        t0 = time.time()
        reply = ai_reply(thread_id, prompt, username)
        if not reply:
            return "❌ Brain offline hai jaan~"
        print(f"  ✅ LADKI AI reply ({time.time() - t0:.1f}s): {reply[:60]}...")

        mem_add(thread_id, "AYAAN AI", reply)

        lang = detect_language(reply)

        audio_path = generate_tts(reply, lang)
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

# Debug
if not EDGE_AVAILABLE:
    print("⚠️ edge-tts not installed! Run: pip install edge-tts")
else:
    print("✅ Edge TTS ready (free, unlimited)")

if FISH_API_KEY:
    print(f"✅ Fish API key loaded (optional): {FISH_API_KEY[:15]}...")
else:
    print("ℹ️ Fish API key not set (Edge TTS only)")

if AI_KEY:
    print(f"✅ Groq API key loaded")
else:
    print("⚠️ GROQ_API_KEY missing in .env!")