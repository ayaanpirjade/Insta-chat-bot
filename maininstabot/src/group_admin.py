# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          👑 AYAAN AI - Group Commands
#          FINAL WORKING - Clean Version
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import re
import time
import random
import json
import threading
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── Constants ──
COOLDOWN_SECONDS = 30
_last_used: Dict[str, float] = {}
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

NC_MIN_DELAY_SECONDS = 30.0
NC_MAX_DURATION_SECONDS = 3600.0
NC_EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
_name_cycle_stop: Dict[str, threading.Event] = {}
_name_cycle_threads: Dict[str, threading.Thread] = {}


def _group_action_error(action: str, exc: Exception) -> str:
    """Return a useful message without leaking raw Instagram request details."""
    text = str(exc).lower()
    if "1545037" in text or "403" in text or "permission" in text or "admin" in text:
        return (
            f"❌ Instagram rejected the request to {action}. "
            "The bot account must be a group admin and Instagram must allow this action."
        )
    return f"❌ Failed to {action}: {str(exc)}"


def _parse_duration(value: str) -> Optional[float]:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)?", value.strip().lower())
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or "s"
    multiplier = {"s": 1, "m": 60, "h": 3600}[unit]
    return amount * multiplier


def _stop_name_cycle(thread_id: str) -> bool:
    stop_event = _name_cycle_stop.pop(str(thread_id), None)
    thread = _name_cycle_threads.pop(str(thread_id), None)
    if stop_event is None:
        return False
    stop_event.set()
    return thread is not None and thread.is_alive()


def handle_nc_stop_command(thread_id: str) -> str:
    stopped = _stop_name_cycle(thread_id)
    return "🛑 Group-name rotation stopped." if stopped else "ℹ️ No active group-name rotation in this group."


def handle_nc_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> str:
    """Rotate a group title at a safe bounded interval until duration expires."""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <group name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = _parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <group name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < NC_MIN_DELAY_SECONDS:
        return "⏳ Duration must be at least 30 seconds."
    if duration > NC_MAX_DURATION_SECONDS:
        return "⏳ Duration cannot exceed 60 minutes."

    # Name changes are attempted directly; Instagram decides whether this
    # member/session is allowed to update the group title.
    _stop_name_cycle(thread_id)

    stop_event = threading.Event()
    key = str(thread_id)
    _name_cycle_stop[key] = stop_event

    def worker() -> None:
        deadline = time.monotonic() + duration
        try:
            while not stop_event.is_set() and time.monotonic() < deadline:
                title = f"{base_name[:95]} {random.choice(NC_EMOJIS)}"
                updater = getattr(cl, "direct_thread_update_title", None)
                if not callable(updater):
                    raise RuntimeError("The installed Instagram client has no group-title method")
                if updater(int(thread_id), title) is False:
                    raise RuntimeError("Instagram rejected the group-title update")
                remaining = max(0.0, deadline - time.monotonic())
                stop_event.wait(min(NC_MIN_DELAY_SECONDS, remaining))
        except Exception as exc:
            print(f"  ⚠️ Name rotation stopped: {_group_action_error('rotate the group name', exc)}")
        finally:
            _name_cycle_stop.pop(key, None)
            _name_cycle_threads.pop(key, None)

    thread = threading.Thread(target=worker, name=f"name-cycle-{key}", daemon=True)
    _name_cycle_threads[key] = thread
    thread.start()
    return f"🔄 Group-name rotation started for {duration_text}. Updates every 30 seconds. Use !ncstop to stop it."


def _require_group_admin(cl: Client, thread_id: str) -> Optional[str]:
    """Validate the target is a group and reject known non-admin sessions early."""
    try:
        thread = cl.direct_thread(int(thread_id))
        if thread is not None and hasattr(thread, "is_group") and not thread.is_group:
            return "❌ This command works only in group chats."

        admin_ids = getattr(thread, "admin_user_ids", None) if thread is not None else None
        if admin_ids:
            normalized = {str(getattr(item, "pk", getattr(item, "id", item))) for item in admin_ids}
            if str(getattr(cl, "user_id", "")) not in normalized:
                return "❌ The bot account is not a group admin, so Instagram will reject this action."
    except Exception:
        # Let Instagram perform the authoritative permission check when thread
        # metadata is unavailable or a lightweight mock client is used.
        pass
    return None


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
        
        permission_error = _require_group_admin(cl, thread_id)
        if permission_error:
            return permission_error

        try:
            add_users = getattr(cl, "direct_thread_add_users", None)
            if callable(add_users):
                success = add_users(int(thread_id), [int(target_user_id)])
                if success is False:
                    raise RuntimeError("Instagram returned a failed add-user response")
            else:
                cl.private_request(
                    f"direct_v2/threads/{thread_id}/add_user/",
                    data={"_uuid": cl.uuid, "user_ids": json.dumps([str(target_user_id)])},
                    with_signature=False,
                )
            print(f"  ✅ User added successfully!")
            return f"✅ **@{target_username} added to the group!**"

        except Exception as e:
            print(f"  ⚠️ Failed: {e}")
            return _group_action_error(f"add @{target_username}", e)
        
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
        
        permission_error = _require_group_admin(cl, thread_id)
        if permission_error:
            return permission_error

        try:
            cl.private_request(
                f"direct_v2/threads/{thread_id}/remove_user/",
                data={"_uuid": cl.uuid, "user_ids": json.dumps([str(target_user_id)])},
                with_signature=False,
            )
            print(f"  ✅ User removed successfully!")
            return f"✅ **@{target_username} removed from the group!**"

        except Exception as e:
            print(f"  ⚠️ Failed: {e}")
            return _group_action_error(f"remove @{target_username}", e)
        
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
    
    # Instagram is the authority for title-change permissions. Do not block
    # members locally when the group allows public title changes.
    try:
        update_title = getattr(cl, "direct_thread_update_title", None)
        if callable(update_title):
            success = update_title(int(thread_id), new_name)
            if success is False:
                raise RuntimeError("Instagram returned a failed group-title response")
        else:
            legacy_update = getattr(cl, "update_group_title", None)
            if not callable(legacy_update):
                raise RuntimeError("The installed Instagram client has no group-title method")
            success = legacy_update(thread_id, new_name)
            if success is False:
                raise RuntimeError("Instagram returned a failed group-title response")
        print(f"  ✅ Group name updated!")
        return f"📝 **Group name changed to:** {new_name}"

    except Exception as e:
        print(f"  ⚠️ Failed to change name: {e}")
        return _group_action_error("change the group name", e)


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
