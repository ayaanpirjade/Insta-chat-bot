# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#   !tts & !speak Commands - gTTS Version (FREE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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

# ── gTTS (Free Google TTS) ──
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# ── Groq AI ──
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# ── Constants ──
COOLDOWN_SECONDS = 15
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Language Codes ──
LANGUAGE_CODES = {
    "hi": "hi",      # Hindi
    "en": "en",      # English
    "ta": "ta",      # Tamil
    "te": "te",      # Telugu
    "ml": "ml",      # Malayalam
    "kn": "kn",      # Kannada
    "ur": "ur",      # Urdu
    "bn": "bn",      # Bengali
    "mr": "mr",      # Marathi
    "gu": "gu",      # Gujarati
    "pa": "pa",      # Punjabi
    "or": "or",      # Odia
}


def detect_language(text: str) -> str:
    """Detect language from text"""
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    if hindi_pattern.search(text):
        return "hi"
    return "en"


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


def human_like_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    time.sleep(random.uniform(min_seconds, max_seconds))


def ensure_request_gap(min_gap: float = 1.0):
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < min_gap:
        time.sleep(min_gap - elapsed + random.uniform(0, 0.5))
    _last_request_time = time.time()


# ═══════════════════════════════════════════════════════════════
#  🆓 gTTS - FREE TEXT TO SPEECH
# ═══════════════════════════════════════════════════════════════

def generate_tts_gtts(text: str, lang: str = "en") -> Optional[str]:
    """
    Generate TTS using gTTS (FREE - NO CREDITS NEEDED)
    """
    try:
        if not GTTS_AVAILABLE:
            print("  ⚠️ gTTS not installed. Install with: pip install gTTS")
            return None
        
        # Clean text for filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"tts_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔊 Generating voice with gTTS...")
        print(f"  📝 Text length: {len(text)} chars")
        print(f"  🌐 Language: {lang}")
        
        # ✅ gTTS - SLOW but FREE!
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ Voice generated ({size_kb:.1f} KB) - FREE!")
            return filename
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ gTTS failed: {e}")
        return None


def convert_to_voice_note(input_path: str) -> Optional[str]:
    """Convert MP3 to M4A voice note format"""
    try:
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            print("  ⚠️ ffmpeg not found, sending as MP3")
            return input_path  # Send as MP3 if ffmpeg not available
        
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
        
        return input_path  # Fallback to MP3
        
    except Exception as e:
        print(f"  ⚠️ Conversion failed: {e}")
        return input_path  # Fallback to MP3


# ═══════════════════════════════════════════════════════════════
#  🤖 AI REPLY FOR !speak
# ═══════════════════════════════════════════════════════════════

def get_ai_reply(query: str, max_tokens: int = 300) -> Optional[str]:
    """Get AI reply using Groq"""
    try:
        if not GROQ_AVAILABLE:
            return None
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("  ⚠️ GROQ_API_KEY not set")
            return None
        
        client = Groq(api_key=api_key)
        
        print(f"  🤖 Getting AI reply...")
        
        # ✅ Short replies for TTS (max 300 chars)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are AYAAN AI. Give concise, informative replies under 300 characters."},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=200,  # ⬇️ Small for TTS
        )
        
        reply = completion.choices[0].message.content.strip()
        print(f"  ✅ AI reply: {reply[:50]}... ({len(reply)} chars)")
        return reply[:500]  # Limit to 500 chars for TTS
        
    except Exception as e:
        print(f"  ⚠️ AI failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🎯 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

def handle_tts_command(text: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !tts command - Convert text to speech using gTTS
    """
    text = text.strip()
    if not text:
        return "🔊 Please provide text to speak.\nExample: !tts Hello everyone"
    
    if len(text) > 500:
        return "⚠️ Text too long! Maximum 500 characters for TTS."
    
    lang = detect_language(text)
    lang_code = LANGUAGE_CODES.get(lang, "en")
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 2.0)
    ensure_request_gap(1.0)
    
    print(f"\n🔊 Processing TTS: {text[:50]}...")
    
    if not GTTS_AVAILABLE:
        return "⚠️ gTTS not installed. Install with: pip install gTTS"
    
    # ✅ Generate TTS using gTTS (FREE)
    audio_path = generate_tts_gtts(text, lang_code)
    
    if not audio_path:
        return f"❌ Failed to generate TTS.\n\nText: {text[:200]}"
    
    # ✅ Convert to voice note format
    voice_path = convert_to_voice_note(audio_path)
    
    # Cleanup MP3
    if audio_path != voice_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass
    
    if not voice_path or not os.path.exists(voice_path):
        return f"❌ Failed to convert audio.\n\nText: {text[:200]}"
    
    print(f"  📤 Sending voice note...")
    try:
        # ✅ Send as voice note
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent!")
        
        # ✅ Send text too (so user can read)
        time.sleep(1)
        cl.direct_send(f"🔊 {text[:200]}{'...' if len(text) > 200 else ''}", thread_ids=[str(thread_id)])
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 TTS generated but failed to send.\n\nText: {text[:200]}"


def handle_speak_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !speak command - AI Reply + Voice Note
    """
    query = query.strip()
    if not query:
        return "🔊 Please ask something.\nExample: !speak What is the weather today?"
    
    if len(query) > 300:
        return "⚠️ Question too long! Maximum 300 characters."
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 2.0)
    ensure_request_gap(1.0)
    
    print(f"\n🔊 Processing speak: {query[:50]}...")
    
    if not GTTS_AVAILABLE:
        return "⚠️ gTTS not installed. Install with: pip install gTTS"
    
    if not GROQ_AVAILABLE:
        return "⚠️ Groq not installed."
    
    # Get AI reply
    reply = get_ai_reply(query)
    
    if not reply:
        return "❌ Failed to get AI reply."
    
    # Send acknowledgment
    try:
        cl.direct_send("🎙️ Generating voice...", thread_ids=[str(thread_id)])
    except:
        pass
    
    # Generate voice using gTTS
    lang = detect_language(reply)
    lang_code = LANGUAGE_CODES.get(lang, "en")
    
    audio_path = generate_tts_gtts(reply, lang_code)
    
    if not audio_path:
        # Fallback: Send AI reply as text
        return f"🤖 AI Reply (voice failed):\n\n{reply[:300]}"
    
    voice_path = convert_to_voice_note(audio_path)
    
    # Cleanup MP3
    if audio_path != voice_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass
    
    if not voice_path or not os.path.exists(voice_path):
        return f"🤖 AI Reply (voice failed):\n\n{reply[:300]}"
    
    try:
        # ✅ Send voice note
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent!")
        
        # ✅ Send text too (so user can read)
        time.sleep(1)
        cl.direct_send(f"🤖 {reply[:200]}{'...' if len(reply) > 200 else ''}", thread_ids=[str(thread_id)])
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 Voice generated but failed to send.\n\n{reply[:300]}"


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
       gTTS Version (FREE!)
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
    print("2. Test !speak (AI Voice)")
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
