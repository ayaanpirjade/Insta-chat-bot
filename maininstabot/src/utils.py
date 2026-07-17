# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🔧 AYAAN AI - Utility Functions
#          Image to 3-Second Video Converter (Bypass Block)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import json
import html
import shutil
import requests
import random
from pathlib import Path
from typing import Optional
from instagrapi import Client

# ── Image processing libraries ──
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ Pillow not installed. Run: pip install Pillow")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV not installed. Run: pip install opencv-python")


def convert_image_to_mp4(image_path: str, output_video_path: str, duration_sec: int = 3) -> bool:
    """
    Converts static image to 3-second MP4 video.
    Instagram blocks images but allows videos.
    """
    if not PIL_AVAILABLE or not CV2_AVAILABLE:
        print("  ⚠️ PIL or OpenCV missing. Install: pip install Pillow opencv-python")
        return False

    try:
        # Load and resize image (1080x1080 for Instagram)
        img = Image.open(image_path).convert("RGB")
        img = img.resize((1080, 1080), Image.LANCZOS)
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Video writer
        fps = 24
        total_frames = fps * duration_sec
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (1080, 1080))

        for _ in range(total_frames):
            out.write(frame)
        out.release()

        print(f"  ✅ Converted image to {duration_sec}s video: {output_video_path}")
        return True
    except Exception as e:
        print(f"  ⚠️ Video conversion failed: {e}")
        return False


def upload_media_to_dm(cl: Client, thread_id: str, file_path: str, caption: str = "") -> bool:
    """
    Upload media to Instagram DM:
    1. Try sending as photo (one attempt)
    2. If fails, convert to 3-sec MP4 video and send
    3. NEVER send file path as text
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

    # ── 1. Try direct photo upload ──
    try:
        time.sleep(0.5)
        cl.direct_send_photo(abs_path, thread_ids=[thread_id])
        print("  ✅ Image sent as photo")
        return True
    except Exception as e:
        print(f"  ⚠️ Photo send failed: {e}")

    # ── 2. Convert to 3-second MP4 video (Bypass) ──
    if CV2_AVAILABLE and PIL_AVAILABLE:
        try:
            print("  🔄 Converting image to 3-second video...")
            temp_video_path = abs_path.rsplit('.', 1)[0] + "_3sec.mp4"

            if convert_image_to_mp4(abs_path, temp_video_path, duration_sec=3):
                time.sleep(1.0)
                cl.direct_send_video(temp_video_path, thread_ids=[thread_id])
                print("  ✅ Image sent as 3-second video (bypass)")

                # Cleanup
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
                return True
        except Exception as e:
            print(f"  ⚠️ Video bypass failed: {e}")
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            except:
                pass

    # ── 3. If all fails, send error (NO FILE PATH) ──
    print("  ❌ All upload methods failed.")
    try:
        cl.direct_send("❌ Failed to send image. Try again.", thread_ids=[thread_id])
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