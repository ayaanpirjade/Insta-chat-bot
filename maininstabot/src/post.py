# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Post Command - !post <reel_link>
#      WITH THUMBNAIL GENERATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
COOLDOWN_SECONDS = 60
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def find_executable(name: str) -> Optional[str]:
    return shutil.which(name)


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


def get_reel_info_via_instagrapi(cl: Client, url: str) -> Optional[Dict]:
    try:
        media_pk = cl.media_pk_from_url(url)
        if not media_pk:
            print(f"  ⚠️ Could not get media PK")
            return None
        
        media = cl.media_info(media_pk)
        if not media:
            print(f"  ⚠️ Could not get media info")
            return None
        
        caption = ""
        if hasattr(media, 'caption_text') and media.caption_text:
            caption = media.caption_text
        elif hasattr(media, 'caption') and media.caption:
            caption = media.caption
        
        username = ""
        if hasattr(media, 'user') and media.user:
            username = media.user.username
        
        info = {
            "id": str(media.id),
            "code": media.code,
            "media_type": media.media_type,
            "caption": caption,
            "title": caption[:100] if caption else "No caption",
            "user": {
                "pk": str(media.user.pk) if hasattr(media, 'user') and media.user else None,
                "username": username,
            }
        }
        
        return info
        
    except Exception as e:
        print(f"  ⚠️ Failed to get reel info: {e}")
        return None


def download_reel_via_ytdlp(url: str) -> Optional[str]:
    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        reel_id = extract_reel_id_from_url(url)
        if not reel_id:
            return None
        
        filename = os.path.join(DOWNLOAD_DIR, f"repost_{reel_id}_{int(time.time())}.mp4")
        
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


def generate_thumbnail(video_path: str) -> Optional[str]:
    """Generate thumbnail from video using ffmpeg"""
    try:
        thumbnail_path = video_path + ".jpg"
        
        ffmpeg_path = find_executable("ffmpeg")
        if not ffmpeg_path:
            print("  ⚠️ ffmpeg not found, skipping thumbnail")
            return None
        
        # Extract frame at 1 second
        cmd = [
            ffmpeg_path,
            "-y",
            "-i", video_path,
            "-ss", "00:00:01",
            "-vframes", "1",
            "-vf", "scale=1080:1080:force_original_aspect_ratio=decrease,pad=1080:1080:(ow-iw)/2:(oh-ih)/2",
            thumbnail_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
            print(f"  ✅ Thumbnail generated")
            return thumbnail_path
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Thumbnail generation failed: {e}")
        return None


def post_video_to_profile(cl: Client, video_path: str, caption: str, thumbnail_path: Optional[str] = None) -> Optional[str]:
    """Post video to bot's profile"""
    try:
        print(f"  📤 Posting to bot's profile...")
        
        # Add delay before posting
        time.sleep(random.uniform(3.0, 6.0))
        
        # Upload video with thumbnail if available
        if thumbnail_path and os.path.exists(thumbnail_path):
            result = cl.video_upload(
                path=video_path,
                caption=caption[:2200],
                thumbnail=thumbnail_path,
            )
        else:
            result = cl.video_upload(
                path=video_path,
                caption=caption[:2200],
            )
        
        print(f"  ✅ Video posted! Media ID: {result}")
        return str(result)
        
    except Exception as e:
        print(f"  ⚠️ Post failed: {e}")
        return None


def handle_post_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str) -> Optional[str]:
    """Handle !post command"""
    query = query.strip()
    if not query:
        return "📎 Please provide a reel link.\nExample: !post https://instagram.com/reel/abc123"
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    if not any(x in query for x in ['instagram.com', 'instagr.am']):
        return "❌ Please provide a valid Instagram reel URL."
    
    print(f"\n🎬 Reposting reel for: {username}")
    print(f"  📎 Link: {query}")
    
    video_path = None
    thumbnail_path = None
    
    try:
        # ── 1. Get reel info ──
        info = get_reel_info_via_instagrapi(cl, query)
        
        if not info:
            return "❌ Failed to fetch reel info. Make sure the reel is public and accessible."
        
        if info['media_type'] != 2:
            return "❌ This is not a video. Only video reels can be reposted."
        
        print(f"  📝 Title: {info['title'][:50]}...")
        print(f"  👤 Original: @{info['user']['username']}")
        
        # ── 2. Download video ──
        if not find_executable("yt-dlp"):
            return "⚠️ yt-dlp not installed. Install with: pip install yt-dlp"
        
        video_path = download_reel_via_ytdlp(query)
        
        if not video_path:
            return "❌ Failed to download reel. Make sure link is correct and reel is public."
        
        # ── 3. Generate thumbnail ──
        if find_executable("ffmpeg"):
            thumbnail_path = generate_thumbnail(video_path)
        else:
            print("  ⚠️ ffmpeg not found, posting without thumbnail")
        
        # ── 4. Prepare caption ──
        caption = info['caption'] if info['caption'] else "🎬 Reel"
        
        if info['user'] and info['user']['username']:
            caption = f"{caption}\n\n📸 Credit: @{info['user']['username']}"
        
        caption = f"{caption}\n\n#reel #instagram #repost"
        
        # ── 5. Post to profile ──
        media_id = post_video_to_profile(cl, video_path, caption, thumbnail_path)
        
        if not media_id:
            return "❌ Failed to post to profile. Please try again."
        
        # ── 6. Send confirmation ──
        confirmation = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "     ✅ REEL POSTED SUCCESSFULLY!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📱 Media ID: {media_id}\n"
            f"📝 Title: {info['title'][:50]}...\n"
            f"👤 Original: @{info['user']['username']}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🔗 Check your profile to see the post!"
        )
        
        cl.direct_send(confirmation, thread_ids=[str(thread_id)])
        print(f"  ✅ Post complete!")
        return None
        
    except Exception as e:
        error_msg = str(e).lower()
        print(f"  ⚠️ Post failed: {e}")
        
        if "login" in error_msg or "session" in error_msg:
            return "⚠️ Session expired. Please try again after relogin."
        elif "rate" in error_msg or "too many" in error_msg:
            return "⚠️ Rate limited! Please wait a few minutes and try again."
        else:
            return f"❌ Failed to post reel: {str(e)}"
    
    finally:
        # Cleanup
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
                print(f"  🧹 Cleaned up: {video_path}")
            except:
                pass
        
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                os.remove(thumbnail_path)
                print(f"  🧹 Cleaned up: {thumbnail_path}")
            except:
                pass
