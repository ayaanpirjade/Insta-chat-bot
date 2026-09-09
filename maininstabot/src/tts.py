# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#   💋 AYAAN AI - FAST SEDUCTIVE VOICE (Termux Compatible) 💋
#   Fish Audio + Edge TTS Hybrid - No Local Model Needed
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
import re
import random
import subprocess
import shutil
import requests
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
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

# ── Indian Female Voice IDs ──
VOICE_IDS = {
    "en": "a6630e2dd6c14ea799c2a7c078e0d8de",  # Indian Female (Professional)
    "hi": "818b74f842624571839985d02def5ac2",  # Hindi Female Narrator
    "seductive": "a6630e2dd6c14ea799c2a7c078e0d8de"  # Best seductive tone
}

# ── 🌶️ SEDUCTIVE MOAN EFFECTS ──
SEDUCTIVE_MOANS = ["mmm... ", "ahh... ", "ohh... ", "hmm... ", "mmhh... "]
SEDUCTIVE_SUFFIXES = [" baby.", " honey.", " darling.", " my love.", " sexy."]
SEDUCTIVE_PREFIXES = ["Hey baby, ", "Listen, ", "Oh my god, ", "Trust me, "]

def make_seductive(text: str) -> str:
    """Add seductive moan effects to text"""
    text = re.sub(r'[^\w\s.,!?]', '', text)  # Remove emojis
    
    if random.random() < 0.4:
        text = f"{random.choice(SEDUCTIVE_MOANS)}{text}"
    
    if random.random() < 0.3:
        text = f"{random.choice(SEDUCTIVE_PREFIXES)}{text}"
    
    if random.random() < 0.4:
        text = f"{text}{random.choice(SEDUCTIVE_SUFFIXES)}"
    
    # Add breathy effect
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
#  🎤 FISH AUDIO - FAST & HUMAN-LIKE (Termux Compatible)
# ═══════════════════════════════════════════════════════════════

def generate_tts_fish(text: str, lang: str = "en") -> Optional[str]:
    """Generate TTS using Fish Audio - Fast & Human-like"""
    try:
        if FISH_API_KEY == "YOUR_FREE_FISH_API_KEY":
            print("  ⚠️ Fish API key missing! Get free key from fish.audio")
            return None
        
        seductive_text = make_seductive(text)
        
        # Limit to 500 chars (Fish free tier limit)
        if len(seductive_text) > 500:
            seductive_text = seductive_text[:497] + "..."
        
        filename = os.path.join(DOWNLOAD_DIR, f"fish_{int(time.time())}.mp3")
        
        print(f"  🔊 Generating seductive Indian voice (Fish Audio)...")
        print(f"  💋 Text: {seductive_text[:50]}...")
        
        headers = {
            "Authorization": f"Bearer {FISH_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": seductive_text,
            "voice_id": VOICE_IDS.get(lang, VOICE_IDS["seductive"]),
            "model": "s2.1-pro-free",  # ✅ Free tier model
            "format": "mp3"
        }
        
        response = requests.post(
            FISH_API_URL,
            headers=headers,
            json=payload,
            timeout=15  # Fast timeout
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
            print(f"  📝 {response.text[:100]}")
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Fish TTS error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🔄 FALLBACK: Edge TTS (FREE & FAST)
# ═══════════════════════════════════════════════════════════════

def generate_tts_edge(text: str, lang: str = "en") -> Optional[str]:
    """Edge TTS fallback - FREE & Fast"""
    try:
        if not EDGE_AVAILABLE:
            print("  ⚠️ edge-tts not installed!")
            return None
        
        seductive_text = make_seductive(text)
        filename = os.path.join(DOWNLOAD_DIR, f"edge_{int(time.time())}.mp3")
        
        voice = "en-IN-NeerjaNeural" if lang == "en" else "hi-IN-SwaraNeural"
        
        print(f"  🔄 Using Edge TTS fallback...")
        
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
#  📦 MAIN TTS FUNCTION (FAST + TERMUX READY)
# ═══════════════════════════════════════════════════════════════

def generate_tts(text: str, lang: str = "en") -> Optional[str]:
    """Main TTS - Fish Audio first, fallback Edge TTS"""
    
    # ✅ Try Fish Audio first (best quality)
    audio = generate_tts_fish(text, lang)
    if audio:
        return audio
    
    # 🔄 Fallback to Edge TTS
    return generate_tts_edge(text, lang)


# ═══════════════════════════════════════════════════════════════
#  📤 SEND VOICE NOTE
# ═══════════════════════════════════════════════════════════════

def convert_to_voice_note(input_path: str) -> Optional[str]:
    """Convert MP3 to M4A (optional)"""
    try:
        output_path = input_path.replace(".mp3", "_voice.m4a")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-acodec", "aac", "-ac", "1", "-ar", "16000", output_path
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, timeout=30)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        
        return input_path
        
    except Exception as e:
        print(f"  ⚠️ Conversion skipped: {e}")
        return input_path


def handle_speak_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !speak command - Fast voice only"""
    query = query.strip()
    if not query:
        return "🔊 Ask something, baby~"
    
    # Cooldown
    if user_id in _last_used:
        elapsed = time.monotonic() - _last_used[user_id]
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down, baby! Wait {round(COOLDOWN_SECONDS - elapsed, 1)}s"
    _last_used[user_id] = time.monotonic()
    
    print(f"\n🔥 Processing voice: {query[:40]}...")
    
    # Get AI reply
    try:
        from . import ai
        reply = ai.ask_ai(
            f"Give a short, flirty, seductive response (2-3 sentences) to: {query}",
            user_id=user_id
        )
        if not reply:
            reply = "Sorry baby, I couldn't think of anything~"
    except:
        reply = "Hmm, tell me more, baby~"
    
    # Generate voice
    lang = detect_language(reply)
    lang_code = "hi" if lang == "hi" else "en"
    
    audio_path = generate_tts(reply, lang_code)
    
    if not audio_path:
        return f"❌ Voice generation failed, baby~"
    
    # Convert to voice note
    voice_path = convert_to_voice_note(audio_path)
    
    # Cleanup MP3
    if audio_path != voice_path and os.path.exists(audio_path):
        try: os.remove(audio_path)
        except: pass
    
    if not voice_path or not os.path.exists(voice_path):
        return "❌ Failed to convert audio~"
    
    # Send voice note ONLY
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋🔥")
        
        # Cleanup
        try: os.remove(voice_path)
        except: pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Send failed: {e}")
        return "❌ Voice generated but failed to send~"


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
   💋 AYAAN AI - FAST SEDUCTIVE VOICE 💋
    Fish Audio + Edge TTS (Termux Ready)
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
    query = input("💬 Ask something: ").strip()
    
    print("\n▶️ Testing...")
    print("-" * 50)
    result = handle_speak_command(query, "test_user", "tester", thread_id, cl)
    print("-" * 50)
    
    if result is None:
        print("🎉 Seductive voice sent! 💋🔥")
    else:
        print(f"ℹ️ {result}")
