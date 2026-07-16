# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎨 AYAAN AI - Image Generation
#          Using New Image Send Method
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
import requests
from pathlib import Path
from typing import Optional, Dict
from instagrapi import Client

# ✅ Import utils
from .utils import upload_media_to_dm, cleanup_file

# ── Constants ──
USER_COOLDOWN = 15
GLOBAL_RATE_LIMIT = 5
_last_used: Dict[str, float] = {}
_last_request_time: float = 0
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── API Settings ──
POLLINATIONS_API = "https://image.pollinations.ai/prompt/"


def ensure_global_rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < GLOBAL_RATE_LIMIT:
        wait_time = GLOBAL_RATE_LIMIT - elapsed + random.uniform(0, 1)
        time.sleep(wait_time)
    _last_request_time = time.time()


def human_like_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    time.sleep(random.uniform(min_sec, max_sec))


def sanitize_prompt(prompt: str) -> str:
    prompt = re.sub(r'[^a-zA-Z0-9\s\-_,.!?]', '', prompt)
    prompt = prompt.replace(' ', '%20')
    return prompt


def generate_image(prompt: str) -> Optional[bytes]:
    """Generate image using Pollinations API"""
    try:
        ensure_global_rate_limit()
        
        clean_prompt = sanitize_prompt(prompt)
        url = f"{POLLINATIONS_API}{clean_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}"
        
        print(f"  🎨 Generating image...")
        print(f"  📝 Prompt: {prompt[:50]}...")
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        if response.content and len(response.content) > 1000:
            size_kb = len(response.content) / 1024
            print(f"  ✅ Image generated ({size_kb:.1f} KB)")
            return response.content
        
        return None
        
    except Exception as e:
        print(f"  ⚠️ Generation failed: {e}")
        return None


def send_image(cl: Client, thread_id: str, image_bytes: bytes, prompt: str) -> bool:
    """Send image using new upload method (with video bypass)"""
    temp_path = None
    try:
        clean_prompt = re.sub(r'[^a-zA-Z0-9]', '_', prompt[:30])
        temp_path = os.path.join(DOWNLOAD_DIR, f"generate_{clean_prompt}_{int(time.time())}.jpg")
        
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"  💾 Saved: {temp_path}")
        
        caption = f"🎨 *Generated: {prompt[:200]}*"
        success = upload_media_to_dm(cl, thread_id, temp_path, caption)
        return success
        
    except Exception as e:
        print(f"  ⚠️ Send failed: {e}")
        return False
        
    finally:
        cleanup_file(temp_path)


def handle_generate_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """Handle !generate command"""
    query = query.strip()
    
    if not query:
        return "🎨 Please provide a prompt!\nExample: !generate a cat sitting on a moon"
    
    if len(query) > 200:
        return "⚠️ Prompt too long! Maximum 200 characters."
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < USER_COOLDOWN:
            remaining = round(USER_COOLDOWN - elapsed, 1)
            return f"⏳ Slow down @{username}! Try again in {remaining}s."
    _last_used[user_id] = time.monotonic()
    
    human_like_delay(1.0, 3.0)
    
    print(f"\n🎨 Generating image for: {username}")
    print(f"  📝 Prompt: {query}")
    
    try:
        cl.direct_send(f"🎨 *Generating: {query[:50]}...*", thread_ids=[str(thread_id)])
    except:
        pass
    
    image_bytes = generate_image(query)
    
    if not image_bytes:
        return "❌ Failed to generate image. Please try again with a different prompt."
    
    success = send_image(cl, thread_id, image_bytes, query)
    
    if success:
        return None
    else:
        return "❌ Failed to send image."


# ── Aliases ──
def handle_gen_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    return handle_generate_command(query, user_id, username, thread_id, cl)

def handle_imagine_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    return handle_generate_command(query, user_id, username, thread_id, cl)