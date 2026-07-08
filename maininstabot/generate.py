# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎨 AYAAN AI - Image Generator
#      !generate <prompt> - Generate images using Pollinations API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
import requests
import io
from pathlib import Path
from typing import Optional, Dict
from instagrapi import Client

# ── Constants ──
USER_COOLDOWN = 15  # Per user cooldown
GLOBAL_COOLDOWN = 10  # ⬅️ 10 seconds global cooldown (kisi bhi user ki request ke baad)
_last_used: Dict[str, float] = {}  # Per user
_last_global_request: float = 0  # Global last request time
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ── API Settings ──
POLLINATIONS_API = "https://image.pollinations.ai/prompt/"


def check_global_cooldown() -> Optional[float]:
    """Check if global cooldown is active"""
    global _last_global_request
    elapsed = time.time() - _last_global_request
    if elapsed < GLOBAL_COOLDOWN:
        return GLOBAL_COOLDOWN - elapsed
    return None


def wait_for_global_cooldown():
    """Wait if global cooldown is active"""
    remaining = check_global_cooldown()
    if remaining:
        print(f"  ⏳ Global cooldown: {remaining:.1f}s remaining...")
        time.sleep(remaining + 0.5)


def update_global_request_time():
    """Update global request time after processing"""
    global _last_global_request
    _last_global_request = time.time()


def human_like_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    """Random human-like delay"""
    time.sleep(random.uniform(min_sec, max_sec))


def sanitize_prompt(prompt: str) -> str:
    """Clean prompt for URL"""
    prompt = re.sub(r'[^a-zA-Z0-9\s\-_,.!?]', '', prompt)
    prompt = prompt.replace(' ', '%20')
    return prompt


def generate_image(prompt: str) -> Optional[bytes]:
    """
    Generate image using Pollinations API
    Returns image bytes or None
    """
    try:
        clean_prompt = sanitize_prompt(prompt)
        url = f"{POLLINATIONS_API}{clean_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}"
        
        print(f"  🎨 Generating image...")
        print(f"  📝 Prompt: {prompt[:50]}...")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
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
    """Send image using photo_download_by_url style"""
    temp_path = None
    try:
        prompt_clean = re.sub(r'[^a-zA-Z0-9]', '_', prompt[:30])
        temp_path = os.path.join(DOWNLOAD_DIR, f"generate_{prompt_clean}_{int(time.time())}.jpg")
        
        with open(temp_path, 'wb') as f:
            f.write(image_bytes)
        
        print(f"  💾 Saved: {temp_path}")
        
        cl.direct_send_photo(temp_path, thread_ids=[str(thread_id)])
        print(f"  ✅ Image sent!")
        
        time.sleep(1)
        cl.direct_send(f"🎨 *Generated: {prompt[:200]}*", thread_ids=[str(thread_id)])
        
        return True
        
    except Exception as e:
        print(f"  ⚠️ Send failed: {e}")
        return False
        
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                print(f"  🧹 Cleaned up: {temp_path}")
            except:
                pass


# ═══════════════════════════════════════════════════════════════════
#  🎮 COMMAND HANDLER
# ═══════════════════════════════════════════════════════════════════

def handle_generate_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    Handle !generate command
    - 15 seconds per user cooldown
    - 10 seconds global cooldown (sab users ke liye)
    """
    query = query.strip()
    
    if not query:
        return "🎨 Please provide a prompt!\nExample: !generate a cat sitting on a moon"
    
    if len(query) > 200:
        return "⚠️ Prompt too long! Maximum 200 characters."
    
    # ── 1. CHECK GLOBAL COOLDOWN (10 seconds) ──
    global_remaining = check_global_cooldown()
    if global_remaining:
        return f"⏳ Bot is busy! Please wait {round(global_remaining, 1)}s before trying again."
    
    # ── 2. CHECK USER COOLDOWN (15 seconds) ──
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < USER_COOLDOWN:
            remaining = round(USER_COOLDOWN - elapsed, 1)
            return f"⏳ Slow down @{username}! Try again in {remaining}s."
    
    # ── Update timestamps ──
    _last_used[user_id] = time.monotonic()
    update_global_request_time()  # ⬅️ Global cooldown start
    
    # ── Human-like delay ──
    human_like_delay(1.0, 3.0)
    
    print(f"\n🎨 Generating image for: {username}")
    print(f"  📝 Prompt: {query}")
    print(f"  ⏳ Global cooldown: {GLOBAL_COOLDOWN}s started")
    
    # Send acknowledgment
    try:
        cl.direct_send(f"🎨 *Generating: {query[:50]}...*", thread_ids=[str(thread_id)])
    except:
        pass
    
    # Generate image
    image_bytes = generate_image(query)
    
    if not image_bytes:
        return "❌ Failed to generate image. Please try again with a different prompt."
    
    # Send image
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


# ═══════════════════════════════════════════════════════════════════
#  🧪 STANDALONE TEST
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        import config
        print(f"✅ config.py loaded successfully!")
    except ImportError as e:
        print(f"❌ config.py not found: {e}")
        sys.exit(1)
    
    print("""
========================================
   🎨 AYAAN AI - Image Generator
       Standalone Test Mode
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
    print("Commands:")
    print("  !generate <prompt>  - Generate image")
    print("  !gen <prompt>       - Short alias")
    print("  !imagine <prompt>   - Imagine alias")
    print("\n⏳ Rate Limits:")
    print(f"  • Per User: {USER_COOLDOWN} seconds")
    print(f"  • Global: {GLOBAL_COOLDOWN} seconds (sab users ke liye)")
    print("-" * 50)
    
    thread_id = input("📱 Enter thread_id: ").strip()
    prompt = input("🎨 Enter prompt: ").strip()
    
    print("\n▶️ Testing !generate...")
    print("-" * 50)
    
    result = handle_generate_command(prompt, "test_user", "tester", thread_id, cl)
    
    print("-" * 50)
    if result is None:
        print("🎉 Image generated and sent!")
    else:
        print(f"ℹ️ {result}")
    
    print("\n✨ Test complete!")
