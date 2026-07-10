# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Central Message Router - FULL WITH TOGGLE SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import re
import datetime
import logging
from typing import Optional

# ✅ Import from src package
from . import game as game
from . import voice_note as voice_note
from . import tts as tts
from . import features as features
from . import menu as menu
from . import scheduler as scheduler
from . import store as store
from . import ai as ai
from . import music as music
from . import reel as reel
from . import profile as profile
from . import post as post
from . import generate as generate
from . import evil as evil
from . import command_toggle as command_toggle

import config


def check_command_permission(cmd: str, user_id: str, username: str) -> Optional[str]:
    """
    Check if user can use this command based on toggle system
    Returns: None if allowed, error message if not
    """
    can_use, reason = command_toggle.can_user_use_command(cmd, user_id)
    if not can_use:
        if reason == "admin_only":
            return f"🔒 Command '!{cmd}' is ADMIN ONLY! Only admins can use it. 😈"
        elif reason == "unknown":
            return f"⚠️ Unknown command '!{cmd}'. Type !help for commands."
        else:
            return f"❌ You don't have permission to use '!{cmd}'."
    return None


def process_message(text: str, thread_id: str, user_id: str, username: str, is_group: bool, cl, msg=None) -> str | None:
    """
    Main message router. Receives incoming message, parses commands,
    manages active games, and falls back to Groq AI if mentioned.
    Returns the string reply to send, or None if no action.
    """
    text = text.strip()
    text_lower = text.lower()
    p = config.PREFIX

    # ── 1. Check for Active Game Session ──
    active_session = game.get_active_game(thread_id)
    if active_session:
        # Quit override
        if text_lower in [f"{p}quit", f"{p}exit", "quit", "exit"]:
            return game.quit_game(thread_id)

        # Route to game handler
        game_name = active_session["game"]
        if game_name == "trivia":
            return game.handle_trivia(thread_id, text, user_id, username)
        elif game_name == "guess":
            return game.handle_guess(thread_id, text, user_id, username)
        elif game_name == "scramble":
            return game.handle_scramble(thread_id, text, user_id, username)
        elif game_name == "rps":
            return game.handle_rps(thread_id, text, user_id, username)
        elif game_name == "wyr":
            return game.handle_wyr(thread_id, text, user_id, username)
        elif game_name == "emoji":
            return game.handle_emoji(thread_id, text, user_id, username)
        elif game_name == "tod":
            return game.handle_tod(thread_id, text, user_id, username)
        elif game_name == "wordseek":
            return game.handle_wordseek(thread_id, text, user_id, username)

        return None

    # ── 2. Handle Commands (Start with Prefix) ──
    if text.startswith(p):
        cmd_part = text[len(p) :].strip()
        cmd_lower = cmd_part.lower()

        # Split command and arguments
        parts = cmd_part.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].strip() if len(parts) > 1 else ""

        # ── 🔧 COMMAND TOGGLE SYSTEM (Admin Only) ──
        if cmd in ["toggle", "togglecmd"]:
            if not evil.is_admin(user_id):
                return "🚫 Only admins can toggle commands! Bhosdike! 😈"
            result = command_toggle.handle_toggle_command(args, user_id, username)
            return result

        elif cmd == "togglepublic":
            if not evil.is_admin(user_id):
                return "🚫 Only admins can do this! Bhosdike! 😈"
            result = command_toggle.handle_togglepublic_command(args, user_id, username)
            return result

        elif cmd == "toggleadmin":
            if not evil.is_admin(user_id):
                return "🚫 Only admins can do this! Bhosdike! 😈"
            result = command_toggle.handle_toggleadmin_command(args, user_id, username)
            return result

        elif cmd in ["cmdstatus", "commandstatus"]:
            result = command_toggle.handle_cmdstatus_command(args, user_id)
            return result

        elif cmd == "resettoggle":
            if not evil.is_admin(user_id):
                return "🚫 Only admins can reset! Bhosdike! 😈"
            result = command_toggle.handle_reset_toggle_command(user_id)
            return result

        # ── 👿 EVIL/WORMGPT COMMANDS (Admin Only by Default) ──
        elif cmd in ["evil", "worm", "wormgpt"]:
            # Check permission
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = evil.handle_evil_command(
                query=args,
                user_id=user_id,
                username=username,
                thread_id=thread_id,
                cl=cl
            )
            return result

        elif cmd in ["evilclear", "wormclear"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = evil.handle_evil_clear_command(
                user_id=user_id,
                username=username
            )
            return result

        elif cmd in ["addadmin", "addowner"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = evil.handle_addadmin_command(
                query=args,
                user_id=user_id,
                username=username
            )
            return result

        elif cmd in ["removeadmin", "removeowner"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = evil.handle_removeadmin_command(
                query=args,
                user_id=user_id,
                username=username
            )
            return result

        elif cmd == "listadmins":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = evil.handle_listadmins_command(user_id)
            return result

        # ── 🎬 REEL COMMANDS (WITH REPLY DETECTION) ──
        elif cmd in ["reel", "dreel", "dlreel"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = reel.handle_reel_command(
                cl=cl,
                thread_id=thread_id,
                msg=msg,
                user_id=user_id,
                username=username,
                args=args
            )
            return result

        # ── 🎵 AUDIO EXTRACT ──
        elif cmd in ["audio", "reelaudio"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = reel.handle_audio_command(
                cl=cl,
                thread_id=thread_id,
                msg=msg,
                user_id=user_id,
                username=username,
                args=args
            )
            return result

        # ── 🎨 IMAGE GENERATION ──
        elif cmd in ["generate", "gen", "imagine"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = generate.handle_generate_command(
                query=args,
                user_id=user_id,
                username=username,
                thread_id=thread_id,
                cl=cl
            )
            return result

        # ── 📸 POST/REEL REPOST ──
        elif cmd in ["post", "repost", "share"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = post.handle_post_command(
                query=args,
                user_id=user_id,
                username=username,
                thread_id=thread_id,
                cl=cl,
                session_id=config.SESSION_ID
            )
            return result

        # ── 👤 PROFILE COMMANDS ──
        elif cmd in ["pfp", "profilepic"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = profile.handle_pfp_command(
                query=args,
                user_id=user_id,
                username=username,
                thread_id=thread_id,
                cl=cl
            )
            return result

        elif cmd in ["profile", "info", "userinfo"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = profile.handle_profile_command(
                query=args,
                user_id=user_id,
                username=username,
                thread_id=thread_id,
                cl=cl
            )
            return result

        # ── 🎵 VOICE NOTE (YouTube) ──
        elif cmd in ["vn", "voicenote"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = voice_note.handle_vn_command(args, user_id, username, thread_id, cl)
            return result

        # ── 🔊 TEXT TO SPEECH ──
        elif cmd in ["tts", "say"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = tts.handle_tts_command(args, user_id, username, thread_id, cl)
            return result

        # ── 🤖 AI + VOICE ──
        elif cmd in ["speak", "ask", "voiceai"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = tts.handle_speak_command(args, user_id, username, thread_id, cl)
            return result

        # ── 🎵 MUSIC ──
        elif cmd == "play":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            result = music.play_song(args, user_id, username, thread_id, cl)
            return result

        # ── 📊 STATS COMMANDS ──
        elif cmd == "score":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            stats = store.get_user(user_id, username)
            return menu.score_card(username, stats)

        elif cmd in ["top", "leaderboard"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            players = store.get_leaderboard()
            return menu.leaderboard(players)

        elif cmd == "daily":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            return features.claim_daily(user_id, username)

        # ── 🎮 GAMES COMMANDS ──
        elif cmd == "trivia":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_trivia(thread_id)

        elif cmd == "guess":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_guess(thread_id)

        elif cmd == "scramble":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_scramble(thread_id)

        elif cmd == "rps":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_rps(thread_id)

        elif cmd == "wyr":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_wyr(thread_id)

        elif cmd == "emoji":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_emoji(thread_id)

        elif cmd == "tod":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_tod(thread_id)

        elif cmd == "wordseek":
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            return game.start_wordseek(thread_id)

        # ── 📅 SCHEDULER ──
        elif cmd in ["remind", "reminder", "schedule"]:
            perm_check = check_command_permission(cmd, user_id, username)
            if perm_check:
                return perm_check
            
            send_at, message = scheduler.parse_reminder(args)
            if send_at and message:
                scheduler.add_reminder(send_at, thread_id, message)
                return scheduler.format_reminder_confirm(send_at, message)
            else:
                return (
                    "❌ Invalid reminder format! Try:\n"
                    f"👉 {p}remind in 10 minutes: take break\n"
                    f"👉 {p}remind at 9:30pm: drink water"
                )

        # ── 🛠️ UTILITY COMMANDS ──
        elif cmd == "help":
            return menu.main_menu()

        elif cmd == "games":
            return menu.games_menu()

        elif cmd == "ping":
            return "🏓 Pong! I'm alive and kicking. ⚡"

        elif cmd in ["joke", "jokes"]:
            return features.get_joke()

        elif cmd in ["fact", "facts"]:
            return features.get_fact()

        elif cmd in ["quote", "quotes"]:
            return features.get_quote()

        elif cmd == "roast":
            target = args if args else f"@{username}"
            return features.get_roast(target)

        elif cmd in ["8ball", "8 ball"]:
            return features.get_8ball(args)

        elif cmd == "roll":
            return features.roll_dice(args)

        elif cmd == "flip":
            return features.flip_coin()

        elif cmd == "meme":
            return features.get_meme()

        elif cmd == "calc":
            return features.calculator(args)

        elif cmd == "time":
            return features.get_time()

        elif cmd == "weather":
            return features.get_weather(args)

        elif cmd == "stalk":
            return features.stalk_profile(args, cl)

        elif cmd == "horoscope":
            return features.get_horoscope(args)

        elif cmd == "choose":
            return features.choose_option(args)

        # If prefix used but command unknown
        return f"⚠️ Unknown command. Type {p}help to see the full menu!"

    # ── 3. Handle Mentions & AI Chat Fallback ──
    bot_tag = f"@{config.USERNAME}".lower()
    bot_name = config.BOT_NAME.lower()

    # Determine if we should reply using AI
    should_reply_ai = False

    # A: If bot is tagged
    if bot_tag in text_lower or bot_name in text_lower:
        should_reply_ai = True
        # Clean the tag out of the message
        clean_text = re.sub(rf"({re.escape(bot_tag)}|{re.escape(bot_name)})", "", text, flags=re.IGNORECASE).strip()
    # B: If in 1-on-1 DM (any text that isn't a command is an AI chat)
    elif not is_group:
        should_reply_ai = True
        clean_text = text

    if should_reply_ai:
        if not clean_text:
            return f"Hey @{username}! Need help? Type {p}help to see my commands! 😉"
        return ai.ask_ai(clean_text, user_id=user_id)

    # ── 4. Ignore Non-Commands in Group Chat ──
    return None
