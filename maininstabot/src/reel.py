# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎬 AYAAN AI - Reel Command
#          FINAL - FIXED VERSION (No API Calls!)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
import requests
import subprocess
import shutil
import sys
import json
import atexit
from pathlib import Path
from typing import Optional, Dict, Any, List
from instagrapi import Client
from instagrapi.types import DirectMessage

# ── Constants ──
COOLDOWN_SECONDS = 30
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_temp_files: List[str] = []
_last_swipe_cache: Dict[str, Dict[str, Any]] = {}


def cleanup_temp_files():
    for file_path in _temp_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
    _temp_files.clear()


atexit.register(cleanup_temp_files)


def add_temp_file(file_path: str):
    if file_path and os.path.exists(file_path):
        _temp_files.append(file_path)


def cleanup_file(file_path: str):
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            if file_path in _temp_files:
                _temp_files.remove(file_path)
            return True
        except:
            return False
    return False


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


def human_like_delay(min_sec: float = 2.0, max_sec: float = 5.0):
    time.sleep(random.uniform(min_sec, max_sec))


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


def extract_link_from_text(text: str) -> Optional[str]:
    patterns = [
        r'https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[A-Za-z0-9_-]+/?',
        r'https?://instagr\.am/[A-Za-z0-9_-]+/?',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_reel_from_xma(msg) -> Optional[Dict[str, Any]]:
    try:
        if not msg:
            return None

        if hasattr(msg, 'raw_xma') and msg.raw_xma:
            raw_xma = msg.raw_xma
            if isinstance(raw_xma, dict):
                # Check for xma_clip
                xma_clip = raw_xma.get('xma_clip')
                if xma_clip and isinstance(xma_clip, list) and len(xma_clip) > 0:
                    clip_data = xma_clip[0]
                    serialized = clip_data.get('serialized_content_ref')
                    if serialized:
                        if isinstance(serialized, str):
                            try:
                                serialized = json.loads(serialized)
                            except:
                                pass
                        if isinstance(serialized, dict):
                            target_url = serialized.get('target_url')
                            if target_url:
                                target_url = target_url.replace('\\/', '/')
                                code = extract_reel_id_from_url(target_url)
                                if code:
                                    return {
                                        'code': code,
                                        'url': target_url,
                                        'username': serialized.get('username', ''),
                                        'source': 'xma_clip'
                                    }

                # Check for xma_media_share (post share)
                xma_media = raw_xma.get('xma_media_share')
                if xma_media and isinstance(xma_media, list) and len(xma_media) > 0:
                    media_data = xma_media[0]
                    serialized = media_data.get('serialized_content_ref')
                    if serialized:
                        if isinstance(serialized, str):
                            try:
                                serialized = json.loads(serialized)
                            except:
                                pass
                        if isinstance(serialized, dict):
                            target_url = serialized.get('target_url')
                            if target_url:
                                target_url = target_url.replace('\\/', '/')
                                if '/reel/' in target_url or '/p/' in target_url:
                                    code = extract_reel_id_from_url(target_url)
                                    if code:
                                        return {
                                            'code': code,
                                            'url': target_url,
                                            'username': serialized.get('username', ''),
                                            'source': 'xma_media_share'
                                        }
        return None
    except Exception as e:
        print(f"  ⚠️ XMA extract failed: {e}")
        return None


def extract_reel_from_message(msg) -> Optional[Dict[str, Any]]:
    if not msg: return None

    # 1. Check direct reel_share
    if hasattr(msg, 'reel_share') and msg.reel_share:
        code = getattr(msg.reel_share, 'code', None)
        if code:
            return {
                'code': code,
                'url': f"https://www.instagram.com/reel/{code}/",
                'username': getattr(msg.reel_share.user, 'username', '') if hasattr(msg.reel_share, 'user') else '',
                'source': 'reel_share'
            }

    # 2. Check clip (direct reel share)
    if hasattr(msg, 'clip') and msg.clip:
        code = getattr(msg.clip, 'code', None)
        if code:
            return {
                'code': code,
                'url': f"https://www.instagram.com/reel/{code}/",
                'username': getattr(msg.clip.user, 'username', '') if hasattr(msg.clip, 'user') else '',
                'source': 'clip'
            }

    # 3. Check media_share
    if hasattr(msg, 'media_share') and msg.media_share:
        code = getattr(msg.media_share, 'code', None)
        if code:
            return {
                'code': code,
                'url': f"https://www.instagram.com/reel/{code}/",
                'username': getattr(msg.media_share.user, 'username', '') if hasattr(msg.media_share, 'user') else '',
                'source': 'media_share'
            }

    # 4. Check text/link
    if hasattr(msg, 'text') and msg.text:
        url = extract_link_from_text(msg.text)
        if url:
            code = extract_reel_id_from_url(url)
            if code:
                return {'code': code, 'url': url, 'username': '', 'source': 'text'}

    return None


def get_replied_message(cl: Client, thread_id: str, msg) -> Optional[DirectMessage]:
    try:
        replied_to_id = None

        if hasattr(msg, 'reply') and msg.reply:
            reply = msg.reply
            if hasattr(reply, 'item_type'):
                return reply
            if hasattr(reply, 'id'):
                replied_to_id = reply.id
            elif hasattr(reply, 'item_id'):
                replied_to_id = reply.item_id

        if not replied_to_id and hasattr(msg, 'reply_to_item_id'):
            replied_to_id = msg.reply_to_item_id

        if not replied_to_id and hasattr(msg, 'reply_to_message_id'):
            replied_to_id = msg.reply_to_message_id

        if not replied_to_id and hasattr(msg, 'replied_to_message'):
            replied = msg.replied_to_message
            if hasattr(replied, 'item_type'):
                return replied
            if hasattr(replied, 'id'):
                replied_to_id = replied.id
            elif hasattr(replied, 'item_id'):
                replied_to_id = replied.item_id

        if not replied_to_id:
            return None

        messages = cl.direct_messages(thread_id, amount=50)
        for m in messages:
            if str(m.id) == str(replied_to_id):
                return m
        return None

    except Exception as e:
        return None


def get_reel_from_reply(cl: Client, thread_id: str, msg) -> Optional[Dict[str, Any]]:
    try:
        replied = get_replied_message(cl, thread_id, msg)
        if not replied:
            return None

        media_id = getattr(replied, 'pk', None) or getattr(replied, 'id', None)
        if hasattr(replied, 'clip'):
            media_id = getattr(replied.clip, 'pk', media_id)
        elif hasattr(replied, 'media_share'):
            media_id = getattr(replied.media_share, 'pk', media_id)

        if media_id and cl:
            try:
                info = cl.media_info(media_id)
                if info and getattr(info, 'code', None):
                    return {
                        'code': info.code,
                        'url': f"https://www.instagram.com/reel/{info.code}/",
                        'username': getattr(info.user, 'username', ''),
                        'source': 'api'
                    }
            except:
                pass

        return extract_reel_from_message(replied)
    except:
        return None


def cache_reel(thread_id: str, reel_data: Dict[str, Any]):
    if reel_data and reel_data.get('code'):
        _last_swipe_cache[thread_id] = reel_data


def get_cached_reel(thread_id: str) -> Optional[Dict[str, Any]]:
    return _last_swipe_cache.get(thread_id)


def get_reel_url(cl: Client, thread_id: str, msg, args: str = "") -> Optional[str]:
    if args:
        url = extract_link_from_text(args)
        if url:
            return url
        if re.match(r'^[A-Za-z0-9_-]+$', args.strip()):
            return f"https://www.instagram.com/reel/{args.strip()}/"

    if msg:
        reel_data = get_reel_from_reply(cl, thread_id, msg)
        if reel_data:
            return reel_data['url']

    cached = get_cached_reel(thread_id)
    if cached:
        return cached['url']

    return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔥 FIXED: download_reel_audio - COMPLETELY NO API!
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def download_reel_audio(cl: Client, url: str) -> Optional[str]:
    try:
        human_like_delay(2.0, 4.0)

        reel_id = extract_reel_id_from_url(url)
        if not reel_id:
            print(f"  ⚠️ Could not extract reel ID from URL")
            return None

        temp_video = os.path.join(DOWNLOAD_DIR, f"temp_{reel_id}_{int(time.time())}.mp4")
        add_temp_file(temp_video)

        yt_dlp_path = find_executable("yt-dlp")
        if not yt_dlp_path:
            print("  ⚠️ yt-dlp not installed")
            return None

        # Download with yt-dlp - NO API CALLS!
        cmd = [
            yt_dlp_path,
            "-f", "bestvideo+bestaudio/best",
            "-o", temp_video,
            "--no-warnings",
            url
        ]

        print(f"  📥 Downloading video with yt-dlp...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            print(f"  ⚠️ yt-dlp failed: {result.stderr[:200]}")
            cleanup_file(temp_video)
            return None

        if not os.path.exists(temp_video) or os.path.getsize(temp_video) == 0:
            print(f"  ⚠️ Downloaded file is empty or missing")
            cleanup_file(temp_video)
            return None

        audio_path = os.path.join(DOWNLOAD_DIR, f"audio_{reel_id}_{int(time.time())}.mp3")
        add_temp_file(audio_path)

        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            print(f"  ⚠️ ffmpeg not installed")
            cleanup_file(temp_video)
            return None

        print(f"  🔄 Extracting audio...")
        ffmpeg_cmd = [
            ffmpeg_path,
            "-y",
            "-i", temp_video,
            "-vn",
            "-acodec", "libmp3lame",
            "-b:a", "128k",
            audio_path
        ]
        subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)

        cleanup_file(temp_video)

        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
            size_kb = os.path.getsize(audio_path) / 1024
            print(f"  ✅ Audio extracted ({size_kb:.1f} KB)")
            return audio_path

        cleanup_file(audio_path)
        return None

    except subprocess.TimeoutExpired:
        print(f"  ⚠️ Download timed out")
        return None
    except Exception as e:
        print(f"  ⚠️ Audio extraction failed: {e}")
        return None


def download_instagram_reel(url: str) -> Optional[str]:
    try:
        human_like_delay(2.0, 4.0)

        reel_id = extract_reel_id_from_url(url)
        if not reel_id:
            return None

        filename = os.path.join(DOWNLOAD_DIR, f"reel_{reel_id}_{int(time.time())}.mp4")
        add_temp_file(filename)

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

        cleanup_file(filename)
        return None

    except Exception as e:
        print(f"  ⚠️ Download failed: {e}")
        return None


def send_video_with_retry(cl: Client, thread_id: str, file_path: str, retry: int = 0) -> bool:
    try:
        human_like_delay(2.0, 4.0)
        cl.direct_send_video(Path(file_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Video sent!")
        return True
    except Exception as e:
        if retry < 2:
            human_like_delay(5.0, 10.0)
            try:
                cl.direct_send(Path(file_path), thread_ids=[str(thread_id)])
                print(f"  ✅ Video sent as file!")
                return True
            except:
                return send_video_with_retry(cl, thread_id, file_path, retry + 1)
        return False


def send_audio_with_retry(cl: Client, thread_id: str, file_path: str, retry: int = 0) -> bool:
    try:
        human_like_delay(2.0, 4.0)
        cl.direct_send_voice(Path(file_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Voice sent!")
        return True
    except Exception as e:
        if retry < 2:
            human_like_delay(5.0, 10.0)
            return send_audio_with_retry(cl, thread_id, file_path, retry + 1)
        return False


# ═══════════════════════════════════════════════════════════════
#  MAIN COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════

def handle_reel_command(cl: Client, thread_id: str, msg, user_id: str, username: str, args: str = "") -> Optional[str]:
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()

    human_like_delay(1.0, 3.0)

    print(f"\n🎬 Reel command from: {username}")

    url = get_reel_url(cl, thread_id, msg, args)

    if not url:
        return (
            "🎬 Please REPLY to a reel or provide link!\n\n"
            "Usage:\n"
            "  • Reply to a reel: !reel\n"
            "  • Direct link: !reel https://instagram.com/reel/xxxxx/"
        )

    print(f"  📥 Downloading: {url[:50]}...")

    if not find_executable("yt-dlp"):
        return "⚠️ yt-dlp not installed. Install with: pip install yt-dlp"

    filename = download_instagram_reel(url)

    if not filename:
        return "❌ Failed to download reel."

    print(f"  📤 Sending reel...")
    success = send_video_with_retry(cl, thread_id, filename)
    cleanup_file(filename)

    if success:
        return "🎬 **Reel sent!**"
    else:
        return "❌ Failed to send reel."


def handle_audio_command(cl: Client, thread_id: str, msg, user_id: str, username: str, args: str = "") -> Optional[str]:
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()

    human_like_delay(1.0, 3.0)

    print(f"\n🎵 Audio command from: {username}")

    url = get_reel_url(cl, thread_id, msg, args)

    if not url:
        return (
            "🎵 Please REPLY to a reel or provide link!\n\n"
            "Usage:\n"
            "  • Reply to a reel: !audio\n"
            "  • Direct link: !audio https://instagram.com/reel/xxxxx/"
        )

    print(f"  📥 Extracting audio from: {url[:50]}...")

    if not find_executable("ffmpeg"):
        return "⚠️ ffmpeg not installed. Download from https://ffmpeg.org/"

    if not find_executable("yt-dlp"):
        return "⚠️ yt-dlp not installed. Install with: pip install yt-dlp"

    # 🔥 FIX: Add delay before extraction to avoid rate limiting
    print(f"  ⏳ Waiting 5 seconds before extraction...")
    time.sleep(5.0)

    audio_path = download_reel_audio(cl, url)

    if not audio_path:
        return "❌ Failed to extract audio."

    print(f"  📤 Sending voice note...")
    success = send_audio_with_retry(cl, thread_id, audio_path)
    cleanup_file(audio_path)

    if success:
        return "🎵 **Voice note sent!**"
    else:
        return "❌ Failed to send audio."


def handle_dreel_command(cl: Client, thread_id: str, msg, user_id: str, username: str, args: str = "") -> Optional[str]:
    return handle_reel_command(cl, thread_id, msg, user_id, username, args)


# ═══════════════════════════════════════════════════════════════
#  🧪 STANDALONE TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        import config
        print(f"✅ config.py loaded!")
    except ImportError as e:
        print(f"❌ config.py not found: {e}")
        sys.exit(1)

    print("""
========================================
   🎬 AYAAN AI - Reel & Audio
   FINAL FIXED VERSION
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
    print("🎬 Reel & Audio commands loaded successfully!")
    print("   • !reel [link/reply] - Download and send reel")
    print("   • !audio [link/reply] - Extract and send audio")
    print("   • !dreel [link/reply] - Download and send reel (alias)")
    print("-" * 50 + "\n")