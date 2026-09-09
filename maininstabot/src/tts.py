# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          💋 AYAAN AI - REAL HUMAN SEDUCTIVE VOICE 💋
#   Edge TTS - Microsoft's FREE Human-like Indian Female Voices
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
import re
import random
import subprocess
import shutil
import logging
import asyncio
import edge_tts
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── Install: pip install edge-tts ──
try:
    import edge_tts
    EDGE_AVAILABLE = True
except ImportError:
    EDGE_AVAILABLE = False
    print("⚠️ Install edge-tts: pip install edge-tts")

# ── Constants ──
COOLDOWN_SECONDS = 8
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── Language & Voice Mapping ──
VOICE_MAP = {
    "en": "en-IN-NeerjaNeural",  # Indian English - Female
    "hi": "hi-IN-SwaraNeural",   # Hindi - Female
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

def make_seductive_with_moan(text: str) -> str:
    """Make text seductive with moan effects"""
    # Remove existing prefixes/suffixes
    for prefix in SEDUCTIVE_PREFIXES:
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
    
    for suffix in SEDUCTIVE_SUFFIXES:
        if text.lower().endswith(suffix.lower()):
            text = text[:-len(suffix)].strip()
    
    # Remove emojis for better TTS
    text = re.sub(r'[^\w\s.,!?]', '', text)
    
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
    
    # Add breathy effects
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
#  🎤 EDGE TTS - REAL HUMAN VOICE (FREE)
# ═══════════════════════════════════════════════════════════════

async def generate_tts_edge(text: str, lang: str = "en") -> Optional[str]:
    """Generate TTS using Edge TTS - FREE Human-like voice"""
    try:
        if not EDGE_AVAILABLE:
            print("  ⚠️ edge-tts not installed!")
            return None
        
        # Make text seductive and remove emojis
        seductive_text = make_seductive_with_moan(text)
        
        # Get voice
        voice = VOICE_MAP.get(lang, "en-IN-NeerjaNeural")
        
        # Clean filename
        safe_text = re.sub(r'[^\w\s-]', '', text[:30]).strip()
        safe_text = re.sub(r'[-\s]+', '_', safe_text) if safe_text else "speech"
        filename = os.path.join(DOWNLOAD_DIR, f"edge_{safe_text}_{int(time.time())}.mp3")
        
        print(f"  🔥 Generating REAL human seductive voice...")
        print(f"  💋 Text: {seductive_text[:60]}...")
        print(f"  🎤 Voice: {voice}")
        print(f"  🌐 Language: {lang}")
        
        # ✅ Edge TTS - Real human voice
        communicate = edge_tts.Communicate(
            text=seductive_text,
            voice=voice,
            rate="+0%",
            volume="+0%"
        )
        
        await communicate.save(filename)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_kb = os.path.getsize(filename) / 1024
            print(f"  ✅ REAL human voice generated ({size_kb:.1f} KB) 💋🔥")
            return filename
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Edge TTS failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
#  📦 MAIN TTS FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_tts(text: str, lang: str = "en") -> Optional[str]:
    """Main TTS - Edge TTS only (real human voice)"""
    
    # Try Edge TTS
    try:
        audio = asyncio.run(generate_tts_edge(text, lang))
        if audio:
            return audio
    except Exception as e:
        print(f"  ⚠️ Edge TTS error: {e}")
    
    print("  ❌ All TTS engines failed!")
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
        enhanced_query = f"Give a short, flirty, seductive response in 2-3 sentences to: {query} Make it playful. Keep it short and sweet."
        
        from . import ai
        reply = ai.ask_ai(
            enhanced_query,
            user_id=user_id,
            conversation_id=conversation_id or f"voice:{user_id}",
        )
        
        # Remove emojis for better TTS
        if reply:
            reply = re.sub(r'[^\w\s.,!?]', '', reply)
        
        return reply[:max_tokens] if reply else None
    except Exception as error:
        print(f"  ⚠️ AI failed: {type(error).__name__}")
        return None


# ═══════════════════════════════════════════════════════════════
#  🎯 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

def handle_tts_command(text: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !tts command - Real human voice ONLY"""
    text = text.strip()
    if not text:
        return "🔊 Please provide text to speak.\nExample: !tts Hello baby"
    
    if len(text) > 500:
        return "⚠️ Text too long! Max 500 characters."
    
    # Remove emojis from input
    text = re.sub(r'[^\w\s.,!?]', '', text)
    
    lang = detect_language(text)
    lang_code = "hi" if lang == "hi" else "en"
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    print(f"\n🔥 Processing REAL human voice: {text[:50]}...")
    
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
        return f"❌ Failed to convert audio."
    
    print(f"  📤 Sending voice note...")
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋🔥")
        
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
    """Handle !speak command - AI Reply + Real Human Voice ONLY"""
    query = query.strip()
    if not query:
        return "🔊 Please ask something.\nExample: !speak Tell me something interesting"
    
    if len(query) > 300:
        return "⚠️ Question too long! Max 300 characters."
    
    # Remove emojis from query
    query = re.sub(r'[^\w\s.,!?]', '', query)
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    print(f"\n🔥 Processing real human voice: {query[:50]}...")
    
    # Get AI reply
    reply = get_ai_reply(query, user_id=user_id, conversation_id=f"{thread_id}:{user_id}")
    
    if not reply:
        return "❌ Failed to get AI reply."
    
    # Remove emojis from reply
    reply = re.sub(r'[^\w\s.,!?]', '', reply)
    
    # Generate voice
    lang = detect_language(reply)
    lang_code = "hi" if lang == "hi" else "en"
    
    audio_path = generate_tts(reply, lang_code)
    
    if not audio_path:
        return f"❌ Voice generation failed."
    
    voice_path = convert_to_voice_note(audio_path)
    
    if audio_path != voice_path and os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except:
            pass
    
    if not voice_path or not os.path.exists(voice_path):
        return f"❌ Voice conversion failed."
    
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice note sent! 💋🔥")
        
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
   💋 AYAAN AI - REAL HUMAN VOICE 💋
    Edge TTS - Indian Female Voice
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
    print("1. Test !tts (Real Human Voice)")
    print("2. Test !speak (AI Voice - ONLY Voice Note)")
    choice = input("Choose (1/2): ").strip()
    
    thread_id = input("📱 Enter thread_id: ").strip()
    
    if choice == "1":
        text = input("🔊 Enter text: ").strip()
        print("\n▶️ Testing real human voice...")
        print("-" * 50)
        result = handle_tts_command(text, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Real human voice sent! 💋🔥")
        else:
            print(f"ℹ️ {result}")
            
    elif choice == "2":
        query = input("🔊 Ask something: ").strip()
        print("\n▶️ Testing real human voice...")
        print("-" * 50)
        result = handle_speak_command(query, "test_user", "tester", thread_id, cl)
        print("-" * 50)
        if result is None:
            print("🎉 Real human voice sent! 💋🔥")
        else:
            print(f"ℹ️ {result}")
    
    print("\n✨ Test complete!")
