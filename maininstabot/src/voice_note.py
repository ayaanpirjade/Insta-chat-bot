# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#        !vn Command (Voice Note)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import re
import time
import os
import json
import subprocess
import logging
import random
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── Constants ──
COOLDOWN_SECONDS = 10
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"
MAX_DURATION_SECONDS = 180


def find_executable(name: str) -> Optional[str]:
    """Find executable in PATH or common locations"""
    path = shutil.which(name)
    if path:
        return path
    
    if name == "ffmpeg":
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    
    if name == "yt-dlp":
        common_paths = [
            r"C:\Users\ayaan\AppData\Local\Programs\Python\Python311\Scripts\yt-dlp.exe",
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    
    if name == "deno":
        common_paths = [
            r"C:\Users\ayaan\.deno\bin\deno.exe",
            r"C:\Program Files\deno\deno.exe",
        ]
        for p in common_paths:
            if os.path.exists(p):
                return p
    
    return None


def check_dependencies():
    """Check if yt-dlp, ffmpeg and deno are available"""
    missing = []
    
    if not find_executable("yt-dlp"):
        missing.append("yt-dlp")
    
    if not find_executable("ffmpeg"):
        missing.append("ffmpeg")
    
    # Deno is now required for YouTube
    if not find_executable("deno"):
        missing.append("deno (JavaScript runtime)")
    
    if missing:
        print(f"⚠️ Missing: {', '.join(missing)}")
        return False
    
    return True


def human_like_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def ensure_request_gap(min_gap: float = 1.5):
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < min_gap:
        wait_time = min_gap - elapsed + random.uniform(0, 0.5)
        time.sleep(wait_time)
    _last_request_time = time.time()


def download_and_convert(query: str) -> tuple[Optional[str], Optional[str]]:
    """
    Download audio from YouTube and convert to voice note format
    """
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        yt_dlp_path = find_executable("yt-dlp")
        ffmpeg_path = find_executable("ffmpeg")
        deno_path = find_executable("deno")
        
        if not yt_dlp_path or not ffmpeg_path or not deno_path:
            return None, None
        
        output_template = os.path.join(DOWNLOAD_DIR, f"%(id)s.%(ext)s")
        
        # Step 1: Download audio with Deno support
        print(f"  🎵 Searching YouTube for: {query}")
        
        ytdlp_cmd = [
            yt_dlp_path,
            f"ytsearch1:{query}",
            "-x",
            "--audio-format", "mp3",
            "--no-playlist",
            "-o", output_template,
            "--print", "filename",
            "--print", "title",
            "--print", "id",
            "--no-simulate",
            "--ffmpeg-location", os.path.dirname(ffmpeg_path),
            "--js-runtimes", f"deno:{deno_path}",  # ✅ Deno for JavaScript
            "--remote-components", "ejs:npm"  # ✅ Enable EJS
        ]
        
        result = subprocess.run(
            ytdlp_cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode != 0:
            print(f"  ⚠️ yt-dlp error: {result.stderr}")
            return None, None
        
        lines = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        if len(lines) < 3:
            return None, None
        
        mp3_path = lines[0]
        title = lines[1]
        video_id = lines[2]
        
        if not os.path.exists(mp3_path):
            expected_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
            if os.path.exists(expected_path):
                mp3_path = expected_path
            else:
                return None, None
        
        print(f"  ✅ Downloaded: {title}")
        
        # Step 2: Convert to voice note
        voice_filename = f"{video_id}_voice.m4a"
        voice_path = os.path.join(DOWNLOAD_DIR, voice_filename)
        
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", mp3_path,
            "-acodec", "aac",
            "-ac", "1",
            "-ar", "16000",
            "-t", str(MAX_DURATION_SECONDS),
            voice_path
        ]
        
        print(f"  🔄 Converting to voice note ({MAX_DURATION_SECONDS}s max)...")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            return None, None
        
        if not os.path.exists(voice_path) or os.path.getsize(voice_path) == 0:
            return None, None
        
        size_mb = os.path.getsize(voice_path) / (1024 * 1024)
        print(f"  ✅ Voice note ready ({size_mb:.1f} MB)")
        
        # Clean up
        try:
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
        except:
            pass
        
        return voice_path, title
        
    except Exception as e:
        print(f"  ⚠️ Download failed: {e}")
        return None, None


def handle_vn_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !vn command"""
    query = query.strip()
    if not query:
        return "🎵 Please specify a song.\nExample: !vn Blinding Lights"
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 2.0)
    ensure_request_gap(1.5)
    
    print(f"\n🎵 Processing voice note: {query}")
    
    # Check dependencies
    if not check_dependencies():
        return "⚠️ Missing dependencies.\nInstall: yt-dlp, ffmpeg, deno"
    
    # Download and convert
    voice_path, title = download_and_convert(query)
    
    if not voice_path or not title:
        return f"❌ Could not find or download: {query}"
    
    # Send voice note
    print(f"  📤 Sending voice note...")
    try:
        cl.direct_send_voice(Path(voice_path), thread_ids=[thread_id])
        print(f"  ✅ Voice note sent!")
        
        try:
            if os.path.exists(voice_path):
                os.remove(voice_path)
        except:
            pass
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Failed to send: {e}")
        try:
            cl.direct_send_voice(thread_id, voice_path)
            return None
        except:
            return f"🎵 Found: {title}\n❌ Failed to send voice note."


def handle_voice_note_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    return handle_vn_command(query, user_id, username, thread_id, cl)