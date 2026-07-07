# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎬 AYAAN AI - Reel Command
#          FINAL WORKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# !reel / !dreel - Download and send reel video
# !audio - Extract audio from reel and send as voice note

import os
import re
import time
import random
import requests
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict
from instagrapi import Client

# ── Constants ──
COOLDOWN_SECONDS = 15
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


def ensure_request_gap():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 2.0:
        time.sleep(2.0 - elapsed + random.uniform(0, 0.5))
    _last_request_time = time.time()


def extract_reel_id_from_url(url: str) -> Optional[str]:
    patterns = [
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/tv/([A-Za-z0-9_-]+)',
        r'instagr\.am/([A-Za-z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


# ═══════════════════════════════════════════════════════════════
#  !reel / !dreel - DOWNLOAD AND SEND REEL VIDEO
# ═══════════════════════════════════════════════════════════════

def download_instagram_reel(url: str) -> Optional[str]:
    """Download Instagram reel using yt-dlp"""
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        reel_id = extract_reel_id_from_url(url)
        if not reel_id:
            return None
        
        filename = os.path.join(DOWNLOAD_DIR, f"reel_{reel_id}_{int(time.time())}.mp4")
        
        yt_dlp_path = find_executable("yt-dlp")
        if not yt_dlp_path:
            print("  ⚠️ yt-dlp not installed")
            return None
        
        cmd = [
            yt_dlp_path,
            "-f", "bestvideo+bestaudio/best",
            "-o", filename,
            "--no-warnings",
            url
        ]
        
        print(f"  📥 Downloading reel...")
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            print(f"  ✅ Downloaded ({size_mb:.1f} MB)")
            return filename
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Download failed: {e}")
        return None


def handle_reel_command(url: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !reel command"""
    url = url.strip()
    if not url:
        return "🎬 Please provide a reel link.\nExample: !reel https://www.instagram.com/reel/xxxxx/"
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    time.sleep(random.uniform(1.0, 2.0))
    ensure_request_gap()
    
    print(f"\n🎬 Processing reel: {url}")
    
    if not find_executable("yt-dlp"):
        return "⚠️ yt-dlp not installed. Install with: pip install yt-dlp"
    
    filename = download_instagram_reel(url)
    
    if not filename:
        return "❌ Failed to download reel. Make sure link is correct and reel is public."
    
    print(f"  📤 Sending reel to chat...")
    try:
        cl.direct_send_video(Path(filename), thread_ids=[str(thread_id)])
        print(f"  ✅ Reel sent successfully!")
    except Exception as e:
        print(f"  ⚠️ Send failed: {e}")
        try:
            cl.direct_send(Path(filename), thread_ids=[str(thread_id)])
            print(f"  ✅ Reel sent successfully!")
        except Exception as e2:
            print(f"  ⚠️ Fallback failed: {e2}")
            return f"❌ Failed to send reel: {e2}"
    
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"  🗑️ Cleaned up")
    except:
        pass
    
    return "🎬 **Reel sent successfully!**"


# ═══════════════════════════════════════════════════════════════
#  !audio - EXTRACT AUDIO FROM REEL AND SEND AS VOICE NOTE
# ═══════════════════════════════════════════════════════════════

def download_reel_audio_via_instagrapi(client: Client, url: str) -> Optional[tuple[str, str]]:
    """
    Download Instagram reel audio using instagrapi + ffmpeg
    """
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        reel_id = extract_reel_id_from_url(url)
        if not reel_id:
            return None, None
        
        # Get media info via instagrapi
        media_pk = client.media_pk_from_url(url)
        if not media_pk:
            print(f"  ⚠️ Could not get media PK")
            return None, None
        
        media = client.media_info(media_pk)
        if not media:
            print(f"  ⚠️ Could not get media info")
            return None, None
        
        # Get video URL
        video_url = None
        if hasattr(media, 'video_url') and media.video_url:
            video_url = media.video_url
        elif hasattr(media, 'video_versions') and media.video_versions:
            video_url = media.video_versions[0]['url']
        
        if not video_url:
            print(f"  ⚠️ No video URL found")
            return None, None
        
        # Download video
        temp_video = os.path.join(DOWNLOAD_DIR, f"temp_reel_{reel_id}_{int(time.time())}.mp4")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.instagram.com/",
        }
        
        print(f"  📥 Downloading video...")
        response = requests.get(video_url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        with open(temp_video, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Extract audio using ffmpeg
        audio_path = os.path.join(DOWNLOAD_DIR, f"reel_audio_{reel_id}_{int(time.time())}.mp3")
        
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            print(f"  ⚠️ ffmpeg not installed")
            try:
                if os.path.exists(temp_video):
                    os.remove(temp_video)
            except:
                pass
            return None, None
        
        print(f"  🔄 Extracting audio...")
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", temp_video,
            "-vn",
            "-acodec", "libmp3lame",
            audio_path
        ]
        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
        
        # Clean up temp video
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
        except:
            pass
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            title = getattr(media, 'caption_text', 'Reel Audio') or 'Reel Audio'
            return audio_path, title[:50]
        
        return None, None
        
    except Exception as e:
        print(f"  ⚠️ Audio extraction failed: {e}")
        return None, None


def send_audio_as_voice_note(client: Client, thread_id: str, audio_path: str) -> bool:
    try:
        # Convert to voice note format (m4a, mono, 16kHz)
        voice_path = audio_path.replace(".mp3", "_voice.m4a")
        
        ffmpeg_path = find_executable("ffmpeg")
        if ffmpeg_path:
            print(f"  🔄 Converting to voice note...")
            ffmpeg_cmd = [
                ffmpeg_path,
                "-y",
                "-i", audio_path,
                "-acodec", "aac",
                "-ac", "1",
                "-ar", "16000",
                voice_path
            ]
            subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)
            
            if os.path.exists(voice_path) and os.path.getsize(voice_path) > 0:
                client.direct_send_voice(Path(voice_path), thread_ids=[str(thread_id)])
                try:
                    if os.path.exists(voice_path):
                        os.remove(voice_path)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                except:
                    pass
                return True
        
        # Fallback: Send as voice directly
        client.direct_send_voice(Path(audio_path), thread_ids=[str(thread_id)])
        return True
        
    except Exception as e:
        print(f"  ⚠️ Failed to send audio: {e}")
        return False


def handle_audio_command(url: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !audio command - Extract audio from Instagram reel and send as voice note
    """
    url = url.strip()
    if not url:
        return "🎵 Please provide a reel link.\nExample: !audio https://www.instagram.com/reel/xxxxx/"
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    time.sleep(random.uniform(1.0, 2.0))
    ensure_request_gap()
    
    print(f"\n🎵 Processing audio from reel: {url}")
    
    # Check ffmpeg
    if not find_executable("ffmpeg"):
        return "⚠️ ffmpeg not installed. Download from https://ffmpeg.org/"
    
    # Extract audio via instagrapi
    audio_path, title = download_reel_audio_via_instagrapi(cl, url)
    
    if not audio_path:
        return "❌ Failed to extract audio. Make sure the link is correct and reel is public."
    
    print(f"  ✅ Extracted audio: {title}")
    
    # Send as voice note
    print(f"  📤 Sending voice note...")
    sent = send_audio_as_voice_note(cl, thread_id, audio_path)
    
    # Clean up
    try:
        if os.path.exists(audio_path):
            os.remove(audio_path)
    except:
        pass
    
    if sent:
        print(f"  ✅ Voice note sent!")
        return None
    else:
        return "❌ Failed to send audio."


# ── Aliases ──
def handle_dreel_command(url: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    return handle_reel_command(url, user_id, username, thread_id, cl)