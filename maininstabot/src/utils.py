# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🔧 AYAAN AI - Utility Functions
#          FFmpeg Image-to-Video Bypass (No OpenCV)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import json
import html
import shutil
import requests
import random
import subprocess
from pathlib import Path
from typing import Optional
from instagrapi import Client

# ── Image processing (Pillow only, no OpenCV) ──
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow not installed. Install: pip install Pillow")


def convert_image_to_mp4_ffmpeg(image_path: str, output_video_path: str, duration_sec: int = 3) -> bool:
    """
    Converts a static image to MP4 video using FFmpeg.
    This is the same method used in Sebi's bot – works perfectly on Termux.
    """
    if not os.path.exists(image_path):
        print(f"  ❌ Source image not found: {image_path}")
        return False

    try:
        # FFmpeg command: loop image, scale to 1080x1080, output H.264 video
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", image_path,
            "-c:v", "libx264",
            "-t", str(duration_sec),
            "-pix_fmt", "yuv420p",
            "-vf", "scale=1080:1080",
            output_video_path
        ]
        # Run silently
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  ✅ Converted image to {duration_sec}s video via FFmpeg")
        return True
    except Exception as e:
        print(f"  ⚠️ FFmpeg conversion failed: {e}")
        return False


def upload_media_to_dm(cl: Client, thread_id: str, file_path: str, caption: str = "") -> bool:
    """
    Upload media to Instagram DM – using the same multi-method approach as Sebi's bot.
    Falls back to FFmpeg video conversion when photo upload fails.
    NEVER sends file path as text.
    """
    thread_id = str(thread_id)
    abs_path = os.path.abspath(file_path)

    print(f"  📤 Uploading: {os.path.basename(file_path)}")

    # ── Send caption first ──
    if caption:
        try:
            cl.direct_send(caption, thread_ids=[thread_id])
            time.sleep(1.0)
        except Exception as e:
            print(f"  ⚠️ Caption send failed: {e}")

    # ── Method 1: Direct photo upload ──
    try:
        time.sleep(0.5)
        cl.direct_send_photo(abs_path, thread_ids=[thread_id])
        print("  ✅ Image sent as photo")
        return True
    except Exception as e:
        print(f"  ⚠️ Photo send failed: {e}")

    # ── Method 2: Manual upload via private_request (as in Sebi's bot) ──
    try:
        upload_id = str(int(time.time() * 1000))
        with open(abs_path, 'rb') as f:
            photo_data = f.read()

        cl.private_request(
            f"rupload_igphoto/{upload_id}",
            data=photo_data,
            with_signature=False,
            headers={
                "X-Instagram-Rupload-Params": json.dumps({
                    "upload_id": upload_id,
                    "media_type": "1",
                    "image_compression": json.dumps({"lib_name": "moz", "lib_version": "3.1.m", "quality": "87"}),
                }),
                "X-Entity-Type": "image/jpeg",
                "X-Entity-Name": f"direct_temp_{upload_id}",
                "X-Entity-Length": str(len(photo_data)),
                "Content-Type": "application/octet-stream",
                "Offset": "0",
            }
        )

        cl.private_request(
            "direct_v2/threads/broadcast/configure_photo/",
            data={
                "action": "send_item",
                "thread_ids": json.dumps([int(thread_id)]),
                "upload_id": upload_id,
                "_uuid": cl.uuid,
            },
            with_signature=False,
        )
        print("  ✅ Image sent via manual upload")
        return True
    except Exception as e:
        print(f"  ⚠️ Manual upload failed: {e}")

    # ── Method 3: Convert to MP4 video using FFmpeg (Instagram bypass) ──
    print("  🔄 Converting image to MP4 video via FFmpeg...")
    temp_video_path = abs_path.rsplit('.', 1)[0] + "_bypass.mp4"

    if convert_image_to_mp4_ffmpeg(abs_path, temp_video_path, duration_sec=3):
        try:
            time.sleep(1.0)
            cl.direct_send_video(temp_video_path, thread_ids=[thread_id])
            print("  ✅ Image sent as 3-second video (bypass)")
            # Cleanup
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            return True
        except Exception as e:
            print(f"  ⚠️ Video send failed: {e}")
        finally:
            if os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except:
                    pass

    # ── If all methods fail, send error message ──
    print("  ❌ All upload methods failed.")
    try:
        cl.direct_send("❌ Failed to send image. Please try again.", thread_ids=[thread_id])
    except:
        pass
    return False


def send_image_safe(cl: Client, thread_id: str, file_path: str, caption: str = "") -> bool:
    """Alias for upload_media_to_dm"""
    return upload_media_to_dm(cl, thread_id, file_path, caption)


def download_pfp_old_method(cl: Client, username: str, download_dir: str = "downloads") -> Optional[str]:
    """Download profile picture using photo_download_by_url"""
    try:
        user_info = cl.user_info_by_username(username)
        if not user_info or not user_info.profile_pic_url:
            return None

        Path(download_dir).mkdir(exist_ok=True)

        file_path = cl.photo_download_by_url(
            user_info.profile_pic_url_hd or user_info.profile_pic_url,
            folder=download_dir
        )

        if file_path and os.path.exists(file_path):
            return str(file_path)
        return None
    except Exception as e:
        print(f"  ⚠️ Old method download failed: {e}")
        return None


def download_pfp_mirror(username: str, download_dir: str = "downloads") -> Optional[str]:
    """Download profile picture using imginn.com mirror"""
    try:
        Path(download_dir).mkdir(exist_ok=True)

        url = f"https://imginn.com/{username}/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return None

        matches = re.findall(r'<div class="avatar"[^>]*>\s*<img src="([^"]+)"', resp.text)
        if not matches:
            matches = re.findall(r'class="avatar"[^>]*>.*?src="([^"]+)"', resp.text, re.DOTALL)
        if not matches:
            matches = re.findall(r'https://[^\s"\']+cdninstagram\.com/[^\s"\']+', resp.text)

        if not matches:
            return None

        pfp_url = html.unescape(matches[0].replace("&amp;", "&"))
        pfp_resp = requests.get(pfp_url, headers=headers, timeout=10)
        pfp_resp.raise_for_status()

        file_path = Path(download_dir) / f"pfp_mirror_{username}_{int(time.time())}.jpg"
        with open(file_path, "wb") as f:
            f.write(pfp_resp.content)

        return str(file_path)
    except Exception as e:
        print(f"  ⚠️ Mirror download failed: {e}")
        return None


def cleanup_file(file_path: str):
    """Safely delete a file"""
    if file_path and os.path.exists(str(file_path)):
        try:
            os.remove(str(file_path))
            print(f"  🧹 Cleaned up: {file_path}")
        except Exception as e:
            print(f"  ⚠️ Cleanup failed: {e}")