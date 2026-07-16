# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          👤 AYAAN AI - Profile Commands
#          Using New Image Send Method
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
from typing import Optional, Dict
from instagrapi import Client

# ✅ Import utils
from .utils import upload_media_to_dm, download_pfp_old_method, download_pfp_mirror, cleanup_file

# ── Constants ──
COOLDOWN_SECONDS = 15
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def extract_username_from_input(text: str) -> str:
    """Extract username from various formats"""
    if not text:
        return None
    
    text = text.strip()
    
    if text.startswith('@'):
        text = text[1:]
    
    url_pattern = r'instagram\.com/([A-Za-z0-9_.-]+)'
    match = re.search(url_pattern, text)
    if match:
        return match.group(1)
    
    if text.endswith('/'):
        text = text[:-1]
    
    if '?' in text:
        text = text.split('?')[0]
    
    text = text.split()[0] if text else None
    return text


# ── !pfp ──

def handle_pfp_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str = None) -> Optional[str]:
    """Handle !pfp command - Sirf profile picture bhejo"""
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    target = extract_username_from_input(query) if query else None
    
    if not target:
        return "👤 Please provide a username!\nExample: !pfp @username"
    
    print(f"\n🖼️ Getting PFP for: {target}")
    
    # ── Try Mirror download first ──
    file_path = download_pfp_mirror(target)
    
    # ── If mirror fails, use old method ──
    if not file_path:
        file_path = download_pfp_old_method(cl, target)
    
    if not file_path:
        return f"❌ Could not download profile picture for @{target}."
    
    # ── Send using new upload method (with video bypass) ──
    caption = f"📸 Profile picture for @{target}:"
    success = upload_media_to_dm(cl, thread_id, file_path, caption)
    
    cleanup_file(file_path)
    
    if success:
        return None
    else:
        return "❌ Failed to send profile picture."


# ── !profile ──

def handle_profile_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str = None) -> Optional[str]:
    """Handle !profile command - Sirf text info"""
    
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    target = extract_username_from_input(query) if query else None
    
    if not target:
        return "👤 Please provide a username!\nExample: !profile @username"
    
    print(f"\n👤 Getting profile info for: {target}")
    
    try:
        user_info = cl.user_info_by_username(target)
        if not user_info:
            return f"❌ User '@{target}' not found!"
        
        is_private = "Yes 🔒" if user_info.is_private else "No 🔓"
        bio = user_info.biography if user_info.biography else "No bio."
        
        response = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"       👤 PROFILE: @{user_info.username}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Full Name : {user_info.full_name or 'No name'}\n"
            f"🆔 User ID   : {user_info.pk}\n"
            f"👥 Followers : {user_info.follower_count:,}\n"
            f"🗣️ Following : {user_info.following_count:,}\n"
            f"📸 Posts     : {user_info.media_count}\n"
            f"🔒 Private   : {is_private}\n"
            f"✅ Verified  : {'Yes ✅' if user_info.is_verified else 'No ❌'}\n"
            f"🔗 Link      : {user_info.external_url or 'No link'}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📝 Biography :\n{bio}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        
        return response
        
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        return f"❌ Could not retrieve profile data for @{target}."