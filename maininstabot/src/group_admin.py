# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          👑 AYAAN AI - Group Commands
#          FINAL WORKING - Clean Version
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── Constants ──
COOLDOWN_SECONDS = 30
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_image_from_msg(msg) -> Optional[str]:
    """Download image from any message (reply or swipe)"""
    try:
        if not msg:
            return None
        
        url = None
        
        # Method 1: Check visual_media
        if hasattr(msg, 'visual_media') and msg.visual_media:
            media = msg.visual_media
            if hasattr(media, 'thumbnail_url') and media.thumbnail_url:
                url = media.thumbnail_url
            elif hasattr(media, 'url') and media.url:
                url = media.url
        
        # Method 2: Check media
        if not url and hasattr(msg, 'media') and msg.media:
            media = msg.media
            if hasattr(media, 'thumbnail_url') and media.thumbnail_url:
                url = media.thumbnail_url
            elif hasattr(media, 'url') and media.url:
                url = media.url
        
        # Method 3: Check image_versions2
        if not url and hasattr(msg, 'image_versions2') and msg.image_versions2:
            if hasattr(msg.image_versions2, 'candidates') and msg.image_versions2.candidates:
                candidates = msg.image_versions2.candidates
                if candidates and len(candidates) > 0:
                    url = candidates[0].url
        
        if not url:
            return None
        
        # Download image
        filename = os.path.join(DOWNLOAD_DIR, f"group_pfp_{int(time.time())}.jpg")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return filename
        
    except Exception as e:
        print(f"  ⚠️ Download failed: {e}")
        return None


# ── !changepfp - Change Group Profile Picture ──

def handle_changepfp_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, msg=None) -> Optional[str]:
    """
    !changepfp - Download image and send back for manual setting
    Usage: Reply to an image OR swipe image with !changepfp
    """
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    if not msg:
        return "📸 Please REPLY to an image or SWIPE an image with !changepfp"
    
    image_path = None
    
    # Check if user replied to a message
    replied_msg = None
    if hasattr(msg, 'reply') and msg.reply:
        replied_msg = msg.reply
    elif hasattr(msg, 'replied_to_message') and msg.replied_to_message:
        replied_msg = msg.replied_to_message
    
    if replied_msg:
        print(f"\n📸 Got image from reply")
        image_path = download_image_from_msg(replied_msg)
    
    # If no reply, check if current message itself has image (swipe)
    if not image_path:
        print(f"\n📸 Checking swiped image...")
        image_path = download_image_from_msg(msg)
    
    if not image_path:
        return "❌ Failed to download image. Make sure you replied to or swiped a valid image."
    
    try:
        # Send the image back to user
        cl.direct_send_photo(image_path, thread_ids=[str(thread_id)])
        print(f"  ✅ Image sent back!")
        
        # Cleanup
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"  🧹 Cleaned up: {image_path}")
            except:
                pass
        
        return (
            "🖼️ **Image downloaded!**\n\n"
            "📌 To set this as group profile picture:\n"
            "1. Tap the image above\n"
            "2. Tap '...' (three dots)\n"
            "3. Select 'Set as Group Photo'\n\n"
            "💡 Instagram doesn't allow bots to change group PFP directly."
        )
        
    except Exception as e:
        print(f"  ⚠️ Failed: {e}")
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        return f"❌ Failed to process image: {str(e)}"


# ── !add - Add User to Group ──

def handle_add_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    !add <username> - Add user to group chat
    Usage: !add @username or !add username
    """
    
    query = query.strip()
    if not query:
        return "👤 Please provide a username to add!\nExample: !add @username"
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    target_username = query.strip().replace('@', '').split()[0]
    if not target_username:
        return "👤 Please provide a valid username!"
    
    print(f"\n👤 Adding user to group for: {username}")
    print(f"  👤 Target: @{target_username}")
    
    try:
        # Get user ID from username
        user_info = cl.user_info_by_username(target_username)
        if not user_info:
            return f"❌ User '@{target_username}' not found!"
        
        target_user_id = str(user_info.pk)
        
        # ✅ WORKING METHOD: Direct API call
        try:
            # instagrapi ka internal method
            cl._send_private_request(
                f"direct_v2/threads/{thread_id}/add_user/",
                {'user_ids': f'[{target_user_id}]'}
            )
            print(f"  ✅ User added successfully!")
            return f"✅ **@{target_username} added to the group!**"
            
        except Exception as e:
            print(f"  ⚠️ Failed: {e}")
            return f"❌ Failed to add user: {str(e)}"
        
    except Exception as e:
        print(f"  ⚠️ Failed to add user: {e}")
        error_msg = str(e).lower()
        if "already" in error_msg:
            return f"⚠️ @{target_username} is already in the group!"
        else:
            return f"❌ Failed to add user: {str(e)}"


# ── !remove - Remove User from Group ──

def handle_remove_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    !remove <username> - Remove user from group chat
    Usage: !remove @username or !remove username
    """
    
    query = query.strip()
    if not query:
        return "👤 Please provide a username to remove!\nExample: !remove @username"
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    target_username = query.strip().replace('@', '').split()[0]
    if not target_username:
        return "👤 Please provide a valid username!"
    
    print(f"\n👤 Removing user from group for: {username}")
    print(f"  👤 Target: @{target_username}")
    
    try:
        user_info = cl.user_info_by_username(target_username)
        if not user_info:
            return f"❌ User '@{target_username}' not found!"
        
        target_user_id = str(user_info.pk)
        
        if target_user_id == user_id:
            return "⚠️ You cannot remove yourself! Use !leave to leave the group."
        
        # ✅ WORKING METHOD: Direct API call
        try:
            cl._send_private_request(
                f"direct_v2/threads/{thread_id}/remove_user/",
                {'user_ids': f'[{target_user_id}]'}
            )
            print(f"  ✅ User removed successfully!")
            return f"✅ **@{target_username} removed from the group!**"
            
        except Exception as e:
            print(f"  ⚠️ Failed: {e}")
            return f"❌ Failed to remove user: {str(e)}"
        
    except Exception as e:
        print(f"  ⚠️ Failed to remove user: {e}")
        error_msg = str(e).lower()
        if "not found" in error_msg or "not in" in error_msg:
            return f"⚠️ @{target_username} is not in the group!"
        else:
            return f"❌ Failed to remove user: {str(e)}"


# ── !changename - Change Group Name ──

def handle_changename_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    !changename <new name> - Change group chat name
    """
    
    query = query.strip()
    if not query:
        return "📝 Please provide a new group name!\nExample: !changename My New Group"
    
    # Cooldown check
    last = _last_used.get(user_id)
    if last is not None:
        elapsed = time.monotonic() - last
        if elapsed < COOLDOWN_SECONDS:
            return f"⏳ Slow down @{username}! Try again in {round(COOLDOWN_SECONDS - elapsed, 1)}s."
    _last_used[user_id] = time.monotonic()
    
    new_name = query[:100]
    if len(query) > 100:
        print(f"  ⚠️ Name truncated to 100 chars")
    
    print(f"\n📝 Changing group name for: {username}")
    print(f"  📛 New name: {new_name}")
    
    try:
        cl.update_group_title(thread_id, new_name)
        print(f"  ✅ Group name updated!")
        return f"📝 **Group name changed to:** {new_name}"
        
    except Exception as e:
        print(f"  ⚠️ Failed to change name: {e}")
        return f"❌ Failed to change group name: {str(e)}"


# ── !leave - Leave Group ──

def handle_leave_command(user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    """
    !leave - User khud group chhodta hai
    """
    print(f"\n👋 {username} is leaving the group...")
    
    try:
        cl.direct_thread_leave(thread_id)
        print(f"  ✅ {username} left the group!")
        return "👋 **You have left the group!**"
        
    except Exception as e:
        print(f"  ⚠️ Failed to leave group: {e}")
        return f"❌ Failed to leave group: {str(e)}"


# ── !groupinfo - Get Group Info ──

def handle_groupinfo_command(thread_id: str, cl: Client) -> Optional[str]:
    """
    !groupinfo - Get group information
    """
    try:
        thread = cl.direct_thread(thread_id)
        if not thread:
            return "❌ Could not get group info"
        
        title = thread.thread_title or "No title"
        member_count = len(thread.users) if hasattr(thread, 'users') else 0
        is_group = thread.is_group if hasattr(thread, 'is_group') else False
        
        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"       📊 GROUP INFO\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📛 Name        : {title}\n"
            f"👥 Members     : {member_count}\n"
            f"📌 Type        : {'Group' if is_group else 'DM'}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    except Exception as e:
        return f"❌ Failed to get group info: {str(e)}"


# ── !groupadmins - Get Group Admins ──

def handle_groupadmins_command(thread_id: str, cl: Client) -> Optional[str]:
    """
    !groupadmins - Get list of group admins
    """
    try:
        thread = cl.direct_thread(thread_id)
        if not thread:
            return "❌ Could not get group info"
        
        admin_names = []
        admin_ids = []
        
        if hasattr(thread, 'admin_user_ids') and thread.admin_user_ids:
            admin_ids = [str(a) for a in thread.admin_user_ids]
        
        if hasattr(thread, 'creator_id') and thread.creator_id:
            creator_id = str(thread.creator_id)
            if creator_id not in admin_ids:
                admin_ids.append(creator_id)
        
        if hasattr(thread, 'users') and thread.users:
            for user in thread.users:
                if str(user.pk) in admin_ids:
                    admin_names.append(f"@{user.username}")
        
        if not admin_names:
            admin_names = ["No admins found"]
        
        response = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       👑 GROUP ADMINS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for admin in admin_names:
            response += f"👤 {admin}\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        
        return response
    except Exception as e:
        return f"❌ Failed to get admins: {str(e)}"


# ── Standalone Test ──

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        import config
        print(f"✅ config.py loaded!")
    except ImportError as e:
        print(f"❌ config.py not found: {e}")
        sys.exit(1)

    print("""
========================================
   👑 AYAAN AI - Group Commands
   FINAL WORKING
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
    print("Commands (Sabke Liye):")
    print("  !changepfp (reply to image) - Download image for group PFP")
    print("  !changename <name> - Change group name")
    print("  !add <username> - Add user to group")
    print("  !remove <username> - Remove user from group")
    print("  !leave - Leave group")
    print("  !groupinfo - Get group info")
    print("  !groupadmins - Get group admins")
    print("-" * 50)

    thread_id = input("📱 Enter thread_id: ").strip()
    choice = input("\nChoose command (1-7): ").strip()

    if choice == "1":
        print("\n📸 Reply to an image and press Enter...")
        input("Press Enter after replying...")
        result = handle_changepfp_command("", cl.user_id, "tester", thread_id, cl, None)
        print(f"\n📝 Result: {result}")

    elif choice == "2":
        name = input("📝 Enter new group name: ").strip()
        result = handle_changename_command(name, cl.user_id, "tester", thread_id, cl)
        print(f"\n📝 Result: {result}")

    elif choice == "3":
        username_add = input("👤 Enter username to add: ").strip()
        result = handle_add_command(username_add, cl.user_id, "tester", thread_id, cl)
        print(f"\n📝 Result: {result}")

    elif choice == "4":
        username_remove = input("👤 Enter username to remove: ").strip()
        result = handle_remove_command(username_remove, cl.user_id, "tester", thread_id, cl)
        print(f"\n📝 Result: {result}")

    elif choice == "5":
        result = handle_leave_command(cl.user_id, "tester", thread_id, cl)
        print(f"\n📝 Result: {result}")

    elif choice == "6":
        result = handle_groupinfo_command(thread_id, cl)
        print(f"\n📝 Result: {result}")

    elif choice == "7":
        result = handle_groupadmins_command(thread_id, cl)
        print(f"\n📝 Result: {result}")

    print("\n✨ Test complete!") 
