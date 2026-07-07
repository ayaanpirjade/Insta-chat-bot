# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#   !tts & !speak Commands
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# !tts <text> - Convert text to speech
# !speak <question> - AI reply + voice note (NO TEXT)

import os
import time
import re
import random
import subprocess
import shutil
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── ElevenLabs ──
try:
    from elevenlabs.client import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# ── Groq AI ──
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── Constants ──
COOLDOWN_SECONDS = 20  # ⬆️ Increased for longer responses
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"

# ── Voice Settings ──
DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"
DEFAULT_MODEL = "eleven_multilingual_v2"

LANGUAGE_VOICES = {
    "hi": "EXAVITQu4L4TnTtW5C",
    "en": "JBFqnCBsd6RMkjVDRZzb",
}


def detect_language(text: str) -> str:
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    if hindi_pattern.search(text):
        return "hi"
    return "en"


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


def human_like_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    time.sleep(random.uniform(min_seconds, max_seconds))


def ensure_request_gap(min_gap: float = 1.5):
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < min_gap:
        time.sleep(min_gap - elapsed + random.uniform(0, 0.5))
    _last_request_time = time.time()


def generate_tts_elevenlabs(text: str, lang: str = "en") -> Optional[str]:
    try:
        if not ELEVENLABS_AVAILABLE:
            return None
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("  ⚠️ ELEVENLABS_API_KEY not set")
            return None
        
        client = ElevenLabs(api_key=api_key)
        voice_id = LANGUAGE_VOICES.get(lang, DEFAULT_VOICE_ID)
        
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"speak_{safe_text}_{int(time.time())}.mp3")
        
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        print(f"  🔊 Generating voice...")
        print(f"  📝 Text length: {len(text)} chars")
        
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=DEFAULT_MODEL,
            output_format="mp3_44100_128",
        )
        
        with open(filename, 'wb') as f:
            for chunk in audio:
                if isinstance(chunk, bytes):
                    f.write(chunk)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ Voice generated ({size_kb:.1f} KB)")
            return filename
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ TTS failed: {e}")
        return None


def convert_to_voice_note(input_path: str) -> Optional[str]:
    try:
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            return None
        
        output_path = input_path.replace(".mp3", "_voice.m4a")
        
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", input_path,
            "-acodec", "aac",
            "-ac", "1",
            "-ar", "16000",
            output_path
        ]
        
        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Conversion failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  !speak - AI REPLY + VOICE NOTE (NO TEXT REPLY)
# ═══════════════════════════════════════════════════════════════

def get_ai_reply(query: str) -> Optional[str]:
    try:
        if not GROQ_AVAILABLE:
            return None
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("  ⚠️ GROQ_API_KEY not set")
            return None
        
        client = Groq(api_key=api_key)
        
        print(f"  🤖 Getting AI reply...")
        
        # ✅ Detect if user wants a long story/explanation
        is_long = any(word in query.lower() for word in ["story", "explain", "detail", "minute", "paragraph", "long"])
        
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are AYAAN AI, a helpful assistant."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=500 if is_long else 150,  # ✅ Longer for stories
        )
        
        reply = completion.choices[0].message.content.strip()
        print(f"  ✅ AI reply: {reply[:50]}... ({len(reply)} chars)")
        return reply
        
    except Exception as e:
        print(f"  ⚠️ AI failed: {e}")
        return None


def handle_speak_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !speak command - SIRF VOICE NOTE (NO TEXT)
    """
    query = query.strip()
    if not query:
        return "🔊 Please ask something.\nExample: !speak What is the weather today?"
    
    if len(query) > 300:
        return "⚠️ Question too long! Maximum 300 characters."
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 2.0)
    ensure_request_gap(1.5)
    
    print(f"\n🔊 Processing speak: {query[:50]}...")
    
    if not ELEVENLABS_AVAILABLE:
        return "⚠️ ElevenLabs not installed."
    
    if not GROQ_AVAILABLE:
        return "⚠️ Groq not installed."
    
    if not find_executable("ffmpeg"):
        return "⚠️ ffmpeg missing."
    
    # Get AI reply
    reply = get_ai_reply(query)
    
    if not reply:
        return "❌ Failed to get AI reply."
    
    # ✅ Send a quick text acknowledgment
    try:
        cl.direct_send("🎙️ Generating voice...", thread_ids=[str(thread_id)])
    except:
        pass
    
    # Generate voice
    audio_path = generate_tts_elevenlabs(reply, detect_language(reply))
    
    if not audio_path:
        return "❌ Failed to generate voice."
    
    voice_path = convert_to_voice_note(audio_path)
    
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except:
        pass
    
    if not voice_path:
        return "❌ Failed to convert audio."
    
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent!")
        
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 Voice generated but failed to send."


# ── TTS (Text to Speech) ──
def handle_tts_command(text: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    text = text.strip()
    if not text:
        return "🔊 Please provide text to speak.\nExample: !tts Hello everyone"
    
    if len(text) > 1000:
        return "⚠️ Text too long! Maximum 1000 characters."
    
    lang = detect_language(text)
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 2.0)
    ensure_request_gap(1.5)
    
    print(f"\n🔊 Processing TTS: {text[:50]}...")
    
    if not ELEVENLABS_AVAILABLE:
        return "⚠️ ElevenLabs not installed."
    
    if not find_executable("ffmpeg"):
        return "⚠️ ffmpeg missing."
    
    audio_path = generate_tts_elevenlabs(text, lang)
    
    if not audio_path:
        return "❌ Failed to generate TTS."
    
    voice_path = convert_to_voice_note(audio_path)
    
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except:
        pass
    
    if not voice_path:
        return "❌ Failed to convert audio."
    
    print(f"  📤 Sending voice note...")
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent!")
        
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 TTS generated but failed to send."


# ── Standalone Test ──
if __name__ == "__main__":
    import sys
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        import config
        print(f"✅ config.py loaded successfully!")
    except ImportError as e:
        print(f"❌ config.py not found: {e}")
        sys.exit(1)
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    print("""
========================================
   🔊 AYAAN AI - TTS & Speak
       Standalone Test Mode
========================================
    """)
    
    session_id = config.SESSION_ID.split(",")[0].strip() if hasattr(config, 'SESSION_ID') else None
    if not session_id:
        print("❌ No SESSION_ID found")
        sys.exit(1)

    print("🔑 Logging in...")
    
    cl = Client()
    try:
        cl.login_by_sessionid(session_id)
        print(f"✅ Logged in as pk={cl.user_id}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        sys.exit(1)
    
    print("\n" + "-" * 50)
    print("1. Test !tts (Text to Speech)")
    print("2. Test !speak (AI Voice - NO TEXT)")
    choice = input("Choose (1/2): ").strip()
    
    thread_id = input("📱 Enter thread_id: ").strip()
    
    if choice == "1":
        text = input("🔊 Enter text: ").strip()
        print("\n▶️ Testing !tts...")
        print("-" * 50)
        result = handle_tts_command(text, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 TTS sent!")
        else:
            print(f"ℹ️ {result}")
            
    elif choice == "2":
        query = input("🔊 Ask something: ").strip()
        print("\n▶️ Testing !speak...")
        print("-" * 50)
        result = handle_speak_command(query, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Voice sent!")
        else:
            print(f"ℹ️ {result}")
    
    print("\n✨ Test complete!")