# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          💋 AYAAN AI - SEDUCTIVE MOAN VOICE 💋
#   !tts & !speak Commands - Samantha API + gTTS Fallback
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
COOLDOWN_SECONDS = 8
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Language Support ──
LANGUAGE_CODES = {
    "hi": "hi", "en": "en", "ta": "ta", "te": "te", "ml": "ml",
    "kn": "kn", "ur": "ur", "bn": "bn", "mr": "mr", "gu": "gu",
    "pa": "pa", "or": "or"
}

# ── 🌶️ SEDUCTIVE MOAN PHRASES ──
SEDUCTIVE_MOANS = [
    "mmm... ", "ahh... ", "ohh... ", "hmm... ", 
    "mmm-hmm... ", "oh baby... ", "hmm yes... ",
    "ahh baby... ", "mmhh... ", "mmm... oh..."
]

SEDUCTIVE_PREFIXES = [
    "Hey baby, ", "Listen baby, ", "Oh my god, ",
    "Guess what, ", "You know what, ", "Let me tell you, ",
    "Are you ready, ", "Trust me, ", "Baby, ", "Sweetheart, "
]

SEDUCTIVE_SUFFIXES = [
    " baby.", " honey.", " sweetie.", " darling.", 
    " my love.", " my dear.", " sexy.", " cutie."
]

# ── 🔥 SEDUCTIVE SENTENCE STRUCTURES ──
def make_seductive_with_moan(text: str) -> str:
    """Make text seductive with moan effects"""
    
    # Remove existing prefixes/suffixes
    for prefix in SEDUCTIVE_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    
    for suffix in SEDUCTIVE_SUFFIXES:
        if text.lower().endswith(suffix.lower()):
            text = text[:-len(suffix)].strip()
    
    # Add moan effect (50% chance)
    if random.random() < 0.5:
        moan = random.choice(SEDUCTIVE_MOANS)
        text = f"{moan}{text}"
    
    # Add prefix (30% chance)
    if random.random() < 0.3:
        prefix = random.choice(SEDUCTIVE_PREFIXES)
        text = f"{prefix}{text}"
    
    # Add suffix (40% chance)
    if random.random() < 0.4:
        suffix = random.choice(SEDUCTIVE_SUFFIXES)
        text = f"{text}{suffix}"
    
    # Add seductive punctuation
    text = text.replace("!", "~")
    text = text.replace("?", "?~")
    
    # Add breathy effects (occasional)
    if len(text) > 20 and random.random() < 0.3:
        parts = text.split(" ")
        if len(parts) > 3:
            insert_pos = random.randint(1, len(parts)-2)
            parts.insert(insert_pos, "...")
            text = " ".join(parts)
    
    return text


def detect_language(text: str) -> str:
    """Detect language from text"""
    hindi_pattern = re.compile(r'[\u0900-\u097F]')
    return "hi" if hindi_pattern.search(text) else "en"


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


# ═══════════════════════════════════════════════════════════════
#  🎤 SAMANTHA API - INDIAN FEMALE VOICE (FREE)
# ═══════════════════════════════════════════════════════════════

def generate_tts_samantha(text: str, lang: str = "en") -> Optional[str]:
    """Generate TTS using Samantha API - FREE Indian female voice"""
    try:
        # Make text seductive with moan
        seductive_text = make_seductive_with_moan(text)
        
        # Clean text for filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"samantha_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔥 Generating seductive Indian female voice...")
        print(f"  📝 Original: {text[:50]}...")
        print(f"  💋 Seductive: {seductive_text[:50]}...")
        print(f"  🌐 Language: {lang}")
        
        # Samantha Voice API
        url = "https://iamsudeep-samanthaai.hf.space/tts"
        
        payload = {
            "text": seductive_text,
            "lang": lang
        }
        
        print(f"  📡 Sending request to Samantha API...")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(response.content)
            
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                size_kb = os.path.getsize(filename) / 1024
                print(f"  ✅ Seductive Indian voice generated ({size_kb:.1f} KB) 💋")
                return filename
        else:
            print(f"  ⚠️ Samantha API error: {response.status_code}")
            if response.text:
                print(f"  📝 Error: {response.text[:200]}")
            print("  🔄 Falling back to gTTS...")
            return generate_tts_gtts(text, lang)
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Samantha API failed: {e}")
        print("  🔄 Falling back to gTTS...")
        return generate_tts_gtts(text, lang)


# ═══════════════════════════════════════════════════════════════
#  🆓 gTTS - FREE FALLBACK
# ═══════════════════════════════════════════════════════════════

def generate_tts_gtts(text: str, lang: str = "en") -> Optional[str]:
    """Generate TTS using gTTS as fallback with seductive tone"""
    try:
        if not GTTS_AVAILABLE:
            print("  ⚠️ gTTS not installed!")
            return None
        
        # Make text seductive
        seductive_text = make_seductive_with_moan(text)
        
        # Clean text for filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"gtts_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔊 Using gTTS fallback...")
        
        # ✅ SLOW = more seductive, pitch effect via language
        tts = gTTS(text=seductive_text, lang=lang, slow=True)
        tts.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ Voice generated ({size_kb:.1f} KB) - FREE!")
            return filename
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ gTTS failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  📦 MAIN TTS FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_tts(text: str, lang: str = "en") -> Optional[str]:
    """Main TTS function - tries Samantha then falls back to gTTS"""
    
    # Try Samantha first (better quality)
    audio = generate_tts_samantha(text, lang)
    if audio:
        return audio
    
    # Fallback to gTTS
    return generate_tts_gtts(text, lang)


def convert_to_voice_note(input_path: str) -> Optional[str]:
    """Convert MP3 to M4A voice note format"""
    try:
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            print("  ⚠️ ffmpeg not found, sending as MP3")
            return input_path
        
        output_path = input_path.replace(".mp3", "_voice.m4a")
        
        ffmpeg_cmd = [
            ffmpeg_path, "-y", "-i", input_path,
            "-acodec", "aac", "-ac", "1", "-ar", "16000", output_path
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
    """Get a concise reply from AI"""
    try:
        # Enhanced prompt for seductive responses
        enhanced_query = f"Give a short, flirty, seductive response in 2-3 sentences to: {query} Make it playful with emojis."
        
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
    """Handle !tts command - seductive voice note ONLY"""
    text = text.strip()
    if not text:
        return "🔊 Please provide text to speak.\nExample: !tts Hello baby"
    
    if len(text) > 500:
        return "⚠️ Text too long! Max 500 characters."
    
    lang = detect_language(text)
    lang_code = LANGUAGE_CODES.get(lang, "en")
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    print(f"\n🔥 Processing TTS with seductive moan voice: {text[:50]}...")
    
    # Generate TTS
    audio_path = generate_tts(text, lang_code)
    
    if not audio_path:
        return f"❌ Failed to generate TTS.\n\nText: {text[:200]}"
    
    # Convert to voice note
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
        # Send ONLY voice note
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋🔥")
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"🔊 Voice generated but failed to send."


def handle_speak_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !speak command - AI Reply + Seductive Voice Note ONLY"""
    query = query.strip()
    if not query:
        return "🔊 Please ask something.\nExample: !speak Tell me something interesting"
    
    if len(query) > 300:
        return "⚠️ Question too long! Max 300 characters."
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    print(f"\n🔥 Processing speak with seductive moan voice: {query[:50]}...")
    
    # Get AI reply
    reply = get_ai_reply(query, user_id=user_id, conversation_id=f"{thread_id}:{user_id}")
    
    if not reply:
        return "❌ Failed to get AI reply."
    
    # Generate seductive voice
    lang = detect_language(reply)
    lang_code = LANGUAGE_CODES.get(lang, "en")
    
    audio_path = generate_tts(reply, lang_code)
    
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
        # Send ONLY voice note
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋🔥")
        
        # Cleanup
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        return f"❌ Voice generated but failed to send."


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
   💋 AYAAN AI - SEDUCTIVE MOAN VOICE 💋
    Samantha API + gTTS Fallback
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
    print("1. Test !tts (Seductive Moan TTS)")
    print("2. Test !speak (AI Voice - ONLY Voice Note)")
    choice = input("Choose (1/2): ").strip()
    
    thread_id = input("📱 Enter thread_id: ").strip()
    
    if choice == "1":
        text = input("🔊 Enter text: ").strip()
        print("\n▶️ Testing !tts with seductive moan voice...")
        print("-" * 50)
        result = handle_tts_command(text, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Seductive moan voice sent! 💋🔥")
        else:
            print(f"ℹ️ {result}")
            
    elif choice == "2":
        query = input("🔊 Ask something: ").strip()
        print("\n▶️ Testing !speak with seductive moan voice...")
        print("-" * 50)
        result = handle_speak_command(query, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Seductive moan voice sent! 💋🔥")
        else:
            print(f"ℹ️ {result}")
    
    print("\n✨ Test complete!")
