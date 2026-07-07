# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Profile & PFP Commands - FINAL WORKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
from typing import Optional, Dict
from instagrapi import Client

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
    
    # Sirf pehla word lo
    text = text.split()[0] if text else None
    
    return text


# ═══════════════════════════════════════════════════════════════════
#  📸 !pfp - SIRF PROFILE PICTURE
# ═══════════════════════════════════════════════════════════════════

def handle_pfp_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str = None) -> Optional[str]:
    """Handle !pfp command - Sirf profile picture bhejo"""
    
    # Cooldown check
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
    
    try:
        # ── Get user info ──
        user_info = cl.user_info_by_username(target)
        if not user_info:
            return f"❌ User '@{target}' not found!"
        
        # ── Download PFP ──
        pic_path = cl.photo_download_by_url(
            user_info.profile_pic_url_hd,
            folder=DOWNLOAD_DIR
        )
        
        if not pic_path:
            return f"❌ Failed to download profile picture for @{target}"
        
        # ── Send PFP ──
        cl.direct_send_photo(pic_path, thread_ids=[str(thread_id)])
        print(f"  ✅ PFP sent!")
        
        # Cleanup
        if os.path.exists(pic_path):
            os.remove(pic_path)
            print(f"  🧹 Cleaned up: {pic_path}")
        
        return None  # No text reply, just photo
        
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        return f"❌ Failed to get profile picture: {str(e)}"


# ═══════════════════════════════════════════════════════════════════
#  👤 !profile - SIRF TEXT INFO (JAISE STALK)
# ═══════════════════════════════════════════════════════════════════

def handle_profile_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str = None) -> Optional[str]:
    """Handle !profile command - Sirf text info (jaise stalk)"""
    
    # Cooldown check
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
        # ── Get user info ──
        user_info = cl.user_info_by_username(target)
        if not user_info:
            return f"❌ User '@{target}' not found!"
        
        # ── Format profile info (jaise stalk) ──
        is_private = "Yes 🔒" if user_info.is_private else "No 🔓"
        bio = user_info.biography if user_info.biography else "No bio."
        
        # ✅ SIMPLE TEXT - same as stalk command
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
        
        return response  # ✅ Sirf text return karo
        
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        return f"❌ Could not retrieve profile data for @{target}. User might not exist or session is limited."


# ═══════════════════════════════════════════════════════════════════
#  🖼️ !fullprofile - PFP + TEXT (DONO ALAG ALAG)
# ═══════════════════════════════════════════════════════════════════

def handle_fullprofile_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, session_id: str = None) -> Optional[str]:
    """
    Handle !fullprofile command - PFP + Text dono alag alag bhejo
    """
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    target = extract_username_from_input(query) if query else None
    
    if not target:
        return "👤 Please provide a username!\nExample: !fullprofile @username"
    
    print(f"\n👤 Getting full profile for: {target}")
    
    pic_path = None
    
    try:
        # ── Get user info ──
        user_info = cl.user_info_by_username(target)
        if not user_info:
            return f"❌ User '@{target}' not found!"
        
        # ── 1. Download and send PFP ──
        try:
            pic_path = cl.photo_download_by_url(
                user_info.profile_pic_url_hd,
                folder=DOWNLOAD_DIR
            )
            
            if pic_path:
                cl.direct_send_photo(pic_path, thread_ids=[str(thread_id)])
                print(f"  ✅ PFP sent!")
                time.sleep(2)  # ⬅️ Important: Wait 2 seconds before text
        except Exception as e:
            print(f"  ⚠️ PFP send failed: {e}")
        
        # ── 2. Format and send profile text ──
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
        
        # Return text (will be sent as separate message)
        return response
        
    except Exception as e:
        print(f"  ⚠️ Error: {e}")
        return f"❌ Could not retrieve profile data for @{target}. User might not exist or session is limited."
    
    finally:
        # Cleanup
        if pic_path and os.path.exists(pic_path):
            try:
                os.remove(pic_path)
                print(f"  🧹 Cleaned up: {pic_path}")
            except:
                pass
