# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🔧 AYAAN AI - Command Toggle System
#          Admin can toggle commands public/admin only
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
from typing import List, Dict, Optional
import config

# ── Constants ──
TOGGLE_FILE = "command_toggle.json"
OWNER_ID = "43241663914"  # Hardcoded owner

# ── Default Settings ──
DEFAULT_SETTINGS = {
    # Admin Only Commands (default)
    "admin_only": [
        "evil",
        "worm",
        "wormgpt",
        "evilclear",
        "wormclear",
        "addadmin",
        "removeadmin",
        "listadmins",
        "toggle",
        "toggleadmin",
        "togglepublic",
        "status",
        "cmdstatus",
    ],
    # Public Commands (default)
    "public": [
        "help",
        "ping",
        "info",
        "joke",
        "fact",
        "quote",
        "roast",
        "8ball",
        "roll",
        "flip",
        "meme",
        "play",
        "vn",
        "voicenote",
        "tts",
        "say",
        "speak",
        "ask",
        "voiceai",
        "reel",
        "dreel",
        "dlreel",
        "audio",
        "reelaudio",
        "pfp",
        "profilepic",
        "profile",
        "userinfo",
        "post",
        "repost",
        "share",
        "generate",
        "gen",
        "imagine",
        "calc",
        "time",
        "weather",
        "stalk",
        "horoscope",
        "choose",
        "trivia",
        "guess",
        "scramble",
        "rps",
        "wyr",
        "emoji",
        "tod",
        "wordseek",
        "score",
        "top",
        "leaderboard",
        "daily",
        "remind",
        "reminder",
        "schedule",
    ]
}


def load_toggle_settings() -> Dict[str, List[str]]:
    """Load toggle settings from file"""
    if os.path.exists(TOGGLE_FILE):
        try:
            with open(TOGGLE_FILE, 'r') as f:
                data = json.load(f)
                # Ensure both keys exist
                if 'admin_only' not in data:
                    data['admin_only'] = DEFAULT_SETTINGS['admin_only']
                if 'public' not in data:
                    data['public'] = DEFAULT_SETTINGS['public']
                return data
        except:
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()


def save_toggle_settings(settings: Dict[str, List[str]]):
    """Save toggle settings to file"""
    with open(TOGGLE_FILE, 'w') as f:
        json.dump(settings, f, indent=2)


def is_admin(user_id: str) -> bool:
    """Check if user is admin or owner"""
    if str(user_id) == OWNER_ID:
        return True
    # Load admins from evil module
    try:
        from .evil import load_admins
        admins = load_admins()
        return str(user_id) in admins
    except:
        return False


def is_command_public(cmd: str) -> bool:
    """Check if a command is public"""
    settings = load_toggle_settings()
    cmd = cmd.lower().replace('!', '')
    return cmd in settings.get('public', [])


def is_command_admin_only(cmd: str) -> bool:
    """Check if a command is admin only"""
    settings = load_toggle_settings()
    cmd = cmd.lower().replace('!', '')
    return cmd in settings.get('admin_only', [])


def can_user_use_command(cmd: str, user_id: str) -> tuple[bool, str]:
    """
    Check if user can use a command
    Returns: (can_use, reason)
    """
    cmd = cmd.lower().replace('!', '')
    
    # If command is public, anyone can use
    if is_command_public(cmd):
        return (True, "public")
    
    # If command is admin only, check admin status
    if is_command_admin_only(cmd):
        if is_admin(user_id):
            return (True, "admin")
        else:
            return (False, "admin_only")
    
    # If command not in any list, default to admin only
    return (False, "unknown")


def get_command_status(cmd: str) -> Dict:
    """Get status of a command"""
    cmd = cmd.lower().replace('!', '')
    settings = load_toggle_settings()
    
    is_public = cmd in settings.get('public', [])
    is_admin_only = cmd in settings.get('admin_only', [])
    
    if is_public:
        status = "public"
        status_icon = "🌐"
        description = "Anyone can use this command"
    elif is_admin_only:
        status = "admin_only"
        status_icon = "🔒"
        description = "Only admins can use this command"
    else:
        status = "unknown"
        status_icon = "❓"
        description = "Command not found in toggle system"
    
    return {
        "command": cmd,
        "status": status,
        "icon": status_icon,
        "description": description
    }


# ── Toggle Handlers ──

def handle_toggle_command(query: str, user_id: str, username: str) -> Optional[str]:
    """
    !toggle <command> - Toggle a command between public and admin only
    Example: !toggle evil - toggles evil command
    """
    # Only admin can toggle
    if not is_admin(user_id):
        return "🚫 Only admins can toggle commands! Bhosdike! 😈"

    query = query.strip()
    if not query:
        return (
            "🔧 **Command Toggle System**\n\n"
            "Usage: !toggle <command>\n\n"
            "Examples:\n"
            "  !toggle evil     - Toggle evil command\n"
            "  !toggle vn       - Toggle voice note command\n"
            "  !toggle all      - Toggle all commands\n\n"
            "📋 Use !cmdstatus <command> to check status"
        )

    cmd = query.lower().strip()
    settings = load_toggle_settings()
    
    # Handle "all" toggle
    if cmd == "all":
        all_commands = list(set(settings.get('public', []) + settings.get('admin_only', [])))
        # Move everything to public
        settings['public'] = all_commands
        settings['admin_only'] = []
        save_toggle_settings(settings)
        return f"🌐 **All commands are now PUBLIC!**\n\nAnyone can use any command. Use !toggleadmin all to revert."

    # Check if command exists in either list
    is_public = cmd in settings.get('public', [])
    is_admin_only = cmd in settings.get('admin_only', [])
    
    if not is_public and not is_admin_only:
        # Command not found, add to admin_only by default
        settings['admin_only'].append(cmd)
        save_toggle_settings(settings)
        return f"🔒 Command '{cmd}' added as **ADMIN ONLY**!\nUse !toggle {cmd} again to make it public."

    # Toggle the command
    if is_public:
        # Move from public to admin_only
        settings['public'].remove(cmd)
        if cmd not in settings['admin_only']:
            settings['admin_only'].append(cmd)
        status = "ADMIN ONLY"
        icon = "🔒"
    else:
        # Move from admin_only to public
        settings['admin_only'].remove(cmd)
        if cmd not in settings['public']:
            settings['public'].append(cmd)
        status = "PUBLIC"
        icon = "🌐"
    
    save_toggle_settings(settings)
    return f"{icon} Command '{cmd}' is now **{status}**!"


def handle_togglepublic_command(query: str, user_id: str, username: str) -> Optional[str]:
    """
    !togglepublic <command> - Make a command public
    """
    if not is_admin(user_id):
        return "🚫 Only admins can do this! Bhosdike! 😈"

    query = query.strip()
    if not query:
        return "Usage: !togglepublic <command>"

    cmd = query.lower().strip()
    settings = load_toggle_settings()
    
    # Remove from admin_only if present
    if cmd in settings['admin_only']:
        settings['admin_only'].remove(cmd)
    # Add to public if not already
    if cmd not in settings['public']:
        settings['public'].append(cmd)
    
    save_toggle_settings(settings)
    return f"🌐 Command '{cmd}' is now **PUBLIC**! Anyone can use it."


def handle_toggleadmin_command(query: str, user_id: str, username: str) -> Optional[str]:
    """
    !toggleadmin <command> - Make a command admin only
    """
    if not is_admin(user_id):
        return "🚫 Only admins can do this! Bhosdike! 😈"

    query = query.strip()
    if not query:
        return "Usage: !toggleadmin <command>"

    cmd = query.lower().strip()
    settings = load_toggle_settings()
    
    # Remove from public if present
    if cmd in settings['public']:
        settings['public'].remove(cmd)
    # Add to admin_only if not already
    if cmd not in settings['admin_only']:
        settings['admin_only'].append(cmd)
    
    save_toggle_settings(settings)
    return f"🔒 Command '{cmd}' is now **ADMIN ONLY**! Only admins can use it."


def handle_cmdstatus_command(query: str, user_id: str) -> Optional[str]:
    """
    !cmdstatus <command> - Check status of a command
    """
    query = query.strip()
    if not query:
        # Show all commands status
        settings = load_toggle_settings()
        lines = ["📋 **Command Status Summary**:", ""]
        
        lines.append("🔒 **ADMIN ONLY:**")
        if settings.get('admin_only'):
            for cmd in sorted(settings['admin_only']):
                lines.append(f"  • !{cmd}")
        else:
            lines.append("  (None)")
        
        lines.append("")
        lines.append("🌐 **PUBLIC:**")
        if settings.get('public'):
            for cmd in sorted(settings['public'])[:20]:  # Show first 20
                lines.append(f"  • !{cmd}")
            if len(settings['public']) > 20:
                lines.append(f"  ... and {len(settings['public']) - 20} more")
        else:
            lines.append("  (None)")
        
        lines.append("")
        lines.append("💡 Use !cmdstatus <command> for specific command")
        return "\n".join(lines)

    cmd = query.lower().strip()
    status = get_command_status(cmd)
    
    return (
        f"📋 **Command Status**: !{status['command']}\n"
        f"{status['icon']} **Status**: {status['status'].upper()}\n"
        f"📝 {status['description']}"
    )


def handle_reset_toggle_command(user_id: str) -> Optional[str]:
    """
    !resettoggle - Reset all commands to default settings
    """
    if not is_admin(user_id):
        return "🚫 Only admins can reset! Bhosdike! 😈"
    
    save_toggle_settings(DEFAULT_SETTINGS)
    return "🔄 **All commands reset to default!**\n\nUse !cmdstatus to see current settings."


# ── Standalone Test ──
if __name__ == "__main__":
    print("""
========================================
   🔧 Command Toggle System Test
========================================
    """)
    
    print("📋 Current Settings:")
    settings = load_toggle_settings()
    print(f"  Admin Only: {len(settings['admin_only'])} commands")
    print(f"  Public: {len(settings['public'])} commands")
    
    print("\n📝 Commands:")
    print("  !toggle <cmd>      - Toggle command")
    print("  !togglepublic <cmd> - Make public")
    print("  !toggleadmin <cmd>  - Make admin only")
    print("  !cmdstatus <cmd>   - Check status")
    print("  !resettoggle       - Reset to default")
    print("  !cmdstatus         - Show all status")
    
    print("\n✨ Test complete!")
