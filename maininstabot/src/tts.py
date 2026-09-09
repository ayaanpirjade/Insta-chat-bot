# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI - SEDUCTIVE VOICE ✨
#   !tts & !speak Commands - Fish Audio API + gTTS Fallback
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
import re
import random
import subprocess
import shutil
import logging
import requests
import json
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── gTTS (Free Fallback) ──
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
COOLDOWN_SECONDS = 10  # Reduced cooldown for better experience
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Fish Audio API Configuration ──
FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY", "YOUR_FISH_AUDIO_API_KEY_HERE")
FISH_AUDIO_API_URL = "https://api.fish.audio/v1/tts"

# ── Seductive Female Voice Configuration ──
SEDUCTIVE_VOICE_CONFIG = {
    "voice_id": "female-seductive",  # Fish Audio voice ID for seductive female
    "speed": 0.9,  # Slightly slower for seductive effect
    "pitch": 1.1,  # Slightly higher pitch
    "emotion": "seductive"
}

# ── Language Support ──
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

# ── Hinglish Seductive Phrases for Better Voice ──
SEDUCTIVE_PREFIXES = [
    "Hey baby, ",
    "Listen carefully, ",
    "Oh my god, ",
    "Guess what, ",
    "You know what, ",
    "Let me tell you something, ",
    "Are you ready for this, ",
    "Trust me, "
]

SEDUCTIVE_SUFFIXES = [
    " baby.",
    " honey.",
    " sweetie.",
    " darling.",
    " cutie.",
    " handsome.",
    " beautiful.",
    " my love.",
    " my dear."
]


def detect_language(text: str) -> str:
    """Detect language from text"""
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    if hindi_pattern.search(text):
        return "hi"
    return "en"


def make_seductive(text: str) -> str:
    """Make text more seductive for voice generation"""
    # Remove existing greetings to avoid duplication
    for prefix in SEDUCTIVE_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    
    # Randomly add seductive prefix/suffix (30% chance)
    if random.random() < 0.3:
        prefix = random.choice(SEDUCTIVE_PREFIXES)
        suffix = random.choice(SEDUCTIVE_SUFFIXES)
        return f"{prefix}{text}{suffix}"
    return text


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
#  🎤 FISH AUDIO API - SEDUCTIVE FEMALE VOICE
# ═══════════════════════════════════════════════════════════════

def generate_tts_fish_audio(text: str, lang: str = "en") -> Optional[str]:
    """
    Generate TTS using Fish Audio API with seductive female voice
    """
    try:
        # Make text seductive
        seductive_text = make_seductive(text)
        
        # Clean text for filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"tts_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔊 Generating seductive female voice...")
        print(f"  📝 Original: {text[:50]}...")
        print(f"  💋 Seductive: {seductive_text[:50]}...")
        print(f"  🌐 Language: {lang}")
        
        # Check if API key is configured
        if FISH_AUDIO_API_KEY == "YOUR_FISH_AUDIO_API_KEY_HERE":
            print("  ⚠️ Fish Audio API key not configured! Falling back to gTTS...")
            return generate_tts_gtts(text, lang)
        
        # ✅ Fish Audio API Request
        headers = {
            "Authorization": f"Bearer {FISH_AUDIO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": seductive_text,
            "voice_id": SEDUCTIVE_VOICE_CONFIG["voice_id"],
            "speed": SEDUCTIVE_VOICE_CONFIG["speed"],
            "pitch": SEDUCTIVE_VOICE_CONFIG["pitch"],
            "emotion": SEDUCTIVE_VOICE_CONFIG["emotion"],
            "language": lang,
            "format": "mp3"
        }
        
        response = requests.post(
            FISH_AUDIO_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save audio file
            with open(filename, "wb") as f:
                f.write(response.content)
            
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                size_kb = os.path.getsize(filename) / 1024
                print(f"  ✅ Seductive voice generated ({size_kb:.1f} KB) 🎀")
                return filename
        else:
            print(f"  ⚠️ Fish Audio API error: {response.status_code} - {response.text}")
            print("  🔄 Falling back to gTTS...")
            return generate_tts_gtts(text, lang)
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Fish Audio failed: {e}")
        print("  🔄 Falling back to gTTS...")
        return generate_tts_gtts(text, lang)


# ═══════════════════════════════════════════════════════════════
#  🆓 gTTS - FREE FALLBACK
# ═══════════════════════════════════════════════════════════════

def generate_tts_gtts(text: str, lang: str = "en") -> Optional[str]:
    """
    Generate TTS using gTTS as fallback (FREE)
    """
    try:
        if not GTTS_AVAILABLE:
            print("  ⚠️ gTTS not installed. Install with: pip install gTTS")
            return None
        
        # Make text slightly seductive
        seductive_text = make_seductive(text)
        
        # Clean text for filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"tts_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔊 Using gTTS fallback...")
        
        # ✅ gTTS - SLOW but FREE!
        tts = gTTS(text=seductive_text, lang=lang, slow=True)  # Slow = more seductive
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
            return input_path
        
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
        
        return input_path
        
    except Exception as e:
        print(f"  ⚠️ Conversion failed: {e}")
        return input_path


# ═══════════════════════════════════════════════════════════════
#  🤖 AI REPLY FOR !speak
# ═══════════════════════════════════════════════════════════════

def get_ai_reply(query: str, max_tokens: int = 300, user_id: str = "default", conversation_id: str | None = None) -> Optional[str]:
    """Get a concise reply from the shared provider-agnostic AI engine."""
    try:
        # Enhanced prompt for more engaging responses
        enhanced_query = f"Give a short, engaging, and slightly playful response to: {query}"
        
        from . import ai
        reply = ai.ask_ai(
            enhanced_query,
            user_id=user_id,
            conversation_id=conversation_id or f"voice:{user_id}",
        )
        return reply[:max_tokens] if reply else None
    except Exception as error:
        print(f"  ⚠️ AI failed: {type(error).__name__}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🎯 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

def handle_tts_command(text: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !tts command - Convert text to speech with seductive female voice
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
    
    print(f"\n🔊 Processing TTS with seductive voice: {text[:50]}...")
    
    # ✅ Generate TTS with seductive voice
    audio_path = generate_tts_fish_audio(text, lang_code)
    
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
        # ✅ Send as voice note ONLY (no text)
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋")
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 Voice generated but failed to send.\n\nText: {text[:200]}"


def handle_speak_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !speak command - AI Reply + Seductive Voice Note ONLY (no text)
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
    
    print(f"\n🔊 Processing speak with seductive voice: {query[:50]}...")
    
    # Get AI reply through the shared engine
    reply = get_ai_reply(query, user_id=user_id, conversation_id=f"{thread_id}:{user_id}")
    
    if not reply:
        return "❌ Failed to get AI reply."
    
    # Generate seductive voice
    lang = detect_language(reply)
    lang_code = LANGUAGE_CODES.get(lang, "en")
    
    audio_path = generate_tts_fish_audio(reply, lang_code)
    
    if not audio_path:
        return f"❌ Voice generation failed.\n\nAI Reply: {reply[:200]}"
    
    voice_path = convert_to_voice_note(audio_path)
    
    # Cleanup MP3
    if audio_path != voice_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass
    
    if not voice_path or not os.path.exists(voice_path):
        return f"❌ Voice conversion failed.\n\nAI Reply: {reply[:200]}"
    
    try:
        # ✅ Send ONLY voice note (no text)
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋")
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"❌ Voice generated but failed to send.\n\nAI Reply: {reply[:200]}"


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
   💋 AYAAN AI - SEDUCTIVE VOICE
       Fish Audio + gTTS Fallback
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
    print("1. Test !tts (Seductive Text to Speech)")
    print("2. Test !speak (AI Voice - ONLY Voice Note)")
    choice = input("Choose (1/2): ").strip()
    
    thread_id = input("📱 Enter thread_id: ").strip()
    
    if choice == "1":
        text = input("🔊 Enter text: ").strip()
        print("\n▶️ Testing !tts with seductive voice...")
        print("-" * 50)
        result = handle_tts_command(text, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Seductive voice sent! 💋")
        else:
            print(f"ℹ️ {result}")
            
    elif choice == "2":
        query = input("🔊 Ask something: ").strip()
        print("\n▶️ Testing !speak with seductive voice...")
        print("-" * 50)
        result = handle_speak_command(query, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Seductive voice sent! 💋")
        else:
            print(f"ℹ️ {result}")
    
    print("\n✨ Test complete!")
