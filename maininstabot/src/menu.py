# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#   Super Mobile-Optimized Menus
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import config

P = config.PREFIX
U = config.USERNAME
B = config.BRAND

# ── Constants ──
BOX_WIDTH = 28
INNER_WIDTH = 25

# ── Box Drawing Characters ──
TL = "╔"
TR = "╗"
BL = "╚"
BR = "╝"
H = "═"
V = "║"


def make_line(left: str, right: str) -> str:
    """Format a line as '║ left [spaces] right ║'"""
    left_str = str(left)
    right_str = str(right)
    combined_len = len(left_str) + len(right_str)
    if combined_len <= INNER_WIDTH:
        spaces = " " * (INNER_WIDTH - combined_len)
        return f"{V} {left_str}{spaces}{right_str} {V}"
    else:
        max_right_len = INNER_WIDTH - len(left_str) - 1
        trunc_right = right_str[:max_right_len] if max_right_len > 0 else ""
        spaces = " " * (INNER_WIDTH - len(left_str) - len(trunc_right))
        return f"{V} {left_str}{spaces}{trunc_right} {V}"


def top_box(title: str = "") -> str:
    """Create top border with optional title"""
    if title:
        title_str = f" {title} "
        padding = (BOX_WIDTH - len(title_str) - 2) // 2
        return f"{TL}{H * padding}{title_str}{H * (BOX_WIDTH - len(title_str) - padding - 2)}{TR}"
    return f"{TL}{H * (BOX_WIDTH - 2)}{TR}"


def bottom_box() -> str:
    """Create bottom border"""
    return f"{BL}{H * (BOX_WIDTH - 2)}{BR}"


def divider() -> str:
    """Create divider line"""
    return f"{V}{H * (BOX_WIDTH - 2)}{V}"


# ═══════════════════════════════════════════════════════════════
#  MAIN MENU - Small & Clean
# ═══════════════════════════════════════════════════════════════

def main_menu():
    """Main menu - Small and clean"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     ✨ AYAAN AI ✨       │",
        "│     🤖 BOT MENU         │",
        "├──────────────────────────┤",
        "│ 📋 COMMANDS             │",
        "├──────────────────────────┤",
        make_line(f"{P}help", "📋 Menu"),
        make_line(f"{P}ping", "🏓 Speed"),
        make_line(f"{P}info", "ℹ️ Details"),
        make_line(f"{P}profile", "👤 Profile"),
        make_line(f"{P}stalk", "🕵️ Instagram"),
        "├──────────────────────────┤",
        "│ 🎵 MUSIC                │",
        "├──────────────────────────┤",
        make_line(f"{P}musiccmd", "🎵 All Music"),
        "├──────────────────────────┤",
        "│ 🎬 REELS                │",
        "├──────────────────────────┤",
        make_line(f"{P}reelcmd", "🎬 All Reel"),
        "├──────────────────────────┤",
        "│ 🎨 GENERATE             │",
        "├──────────────────────────┤",
        make_line(f"{P}generate", "🖼️ AI Image"),
        "├──────────────────────────┤",
        "│ 🎮 GAMES                │",
        "├──────────────────────────┤",
        make_line(f"{P}gamescmd", "🎮 All Games"),
        "├──────────────────────────┤",
        "│ 🛠️ UTILITIES            │",
        "├──────────────────────────┤",
        make_line(f"{P}utilscmd", "🛠️ All Utils"),
        "├──────────────────────────┤",
        "│ 👑 ADMIN                │",
        "├──────────────────────────┤",
        make_line(f"{P}admincmd", "👑 Admin"),
        "├──────────────────────────┤",
        "│ 💬 AI CHAT              │",
        "├──────────────────────────┤",
        make_line(f"@{U}", "🤖 Chat AI"),
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  MUSIC COMMANDS MENU
# ═══════════════════════════════════════════════════════════════

def music_menu():
    """All music commands"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     🎵 MUSIC MENU       │",
        "│     All Music Commands  │",
        "├──────────────────────────┤",
        make_line(f"{P}play", "🎵 Play Song"),
        make_line(f"{P}vn", "🎤 Voice Note"),
        make_line(f"{P}tts", "🔊 Text to Speech"),
        make_line(f"{P}speak", "🧠 AI Voice"),
        make_line(f"{P}audio", "🎵 Reel Audio"),
        "├──────────────────────────┤",
        "│ 💡 Usage:               │",
        "│ !play song_name         │",
        "│ !vn youtube_link        │",
        "│ !tts text_to_speak      │",
        "│ !speak question         │",
        "│ !audio reel_link        │",
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  REEL COMMANDS MENU
# ═══════════════════════════════════════════════════════════════

def reel_menu():
    """All reel commands"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     🎬 REEL MENU        │",
        "│     All Reel Commands   │",
        "├──────────────────────────┤",
        make_line(f"{P}reel", "📥 Download Reel"),
        make_line(f"{P}dreel", "📥 Download Reel"),
        make_line(f"{P}audio", "🎵 Reel Audio"),
        make_line(f"{P}post", "📸 Repost Reel"),
        "├──────────────────────────┤",
        "│ 💡 Usage:               │",
        "│ !reel link_or_reply     │",
        "│ !audio link_or_reply    │",
        "│ !post link              │",
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  GAMES MENU
# ═══════════════════════════════════════════════════════════════

def games_menu():
    """All games commands"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     🎮 GAMES MENU       │",
        "│     All Games Commands  │",
        "├──────────────────────────┤",
        make_line(f"{P}trivia", "❓ Quiz"),
        make_line(f"{P}guess", "🔢 Guess Number"),
        make_line(f"{P}scramble", "🔤 Word Scramble"),
        make_line(f"{P}wordseek", "🔎 Wordle"),
        make_line(f"{P}rps", "✂️ Rock Paper"),
        make_line(f"{P}wyr", "⚡ Would You Rather"),
        make_line(f"{P}emoji", "😄 Emoji Guess"),
        make_line(f"{P}tod", "🎯 Truth or Dare"),
        "├──────────────────────────┤",
        make_line(f"{P}score", "⭐ My Stats"),
        make_line(f"{P}top", "🏆 Leaderboard"),
        make_line(f"{P}daily", "🎁 Daily Bonus"),
        "├──────────────────────────┤",
        "│ 💡 Type !quit to exit   │",
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  UTILITIES MENU
# ═══════════════════════════════════════════════════════════════

def utils_menu():
    """All utility commands"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     🛠️ UTILITIES MENU   │",
        "│     All Utils Commands  │",
        "├──────────────────────────┤",
        make_line(f"{P}calc", "➗ Calculator"),
        make_line(f"{P}time", "🕐 Current Time"),
        make_line(f"{P}weather", "🌤️ Weather"),
        make_line(f"{P}horoscope", "🔮 Horoscope"),
        make_line(f"{P}choose", "🤔 Pick One"),
        make_line(f"{P}remind", "⏰ Reminder"),
        make_line(f"{P}generate", "🎨 AI Image"),
        "├──────────────────────────┤",
        make_line(f"{P}joke", "😂 Joke"),
        make_line(f"{P}fact", "🧠 Fact"),
        make_line(f"{P}quote", "💬 Quote"),
        make_line(f"{P}roast", "🔥 Roast"),
        make_line(f"{P}8ball", "🎱 8Ball"),
        make_line(f"{P}roll", "🎲 Roll Dice"),
        make_line(f"{P}flip", "🪙 Flip Coin"),
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  ADMIN MENU
# ═══════════════════════════════════════════════════════════════

def admin_menu():
    """Admin commands menu"""
    lines = [
        "",
        "┌──────────────────────────┐",
        "│     👑 ADMIN MENU       │",
        "│     Admin Commands      │",
        "├──────────────────────────┤",
        make_line(f"{P}evil", "👿 Evil AI"),
        make_line(f"{P}evilclear", "🧹 Clear Evil"),
        make_line(f"{P}addadmin", "➕ Add Admin"),
        make_line(f"{P}removeadmin", "➖ Remove Admin"),
        make_line(f"{P}listadmins", "📋 List Admins"),
        make_line(f"{P}toggle", "🔧 Toggle Command"),
        make_line(f"{P}cmdstatus", "📊 Command Status"),
        "├──────────────────────────┤",
        make_line(f"{P}add", "👤 Add User"),
        make_line(f"{P}remove", "👤 Remove User"),
        make_line(f"{P}changename", "📝 Change Group Name"),
        make_line(f"{P}changepfp", "🖼️ Change Group PFP"),
        make_line(f"{P}groupinfo", "📊 Group Info"),
        make_line(f"{P}groupadmins", "👑 Group Admins"),
        "└──────────────────────────┘",
        "",
    ]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  BOT INFO
# ═══════════════════════════════════════════════════════════════

def bot_info():
    """Bot info card"""
    return "\n".join([
        "",
        "       ✨ AYAAN AI ✨",
        "      🤖 BOT STATUS",
        "──────────────────────────",
        "🤖 Name      : AYAAN AI",
        "📌 Version   : 2.3.0",
        "⚡ AI Model  : Groq LLaMA",
        "🛠️ Engine   : Python 3",
        "👨‍💻 Dev     : @ayaanplugs",
        "📡 Status   : 🟢 Online",
        "──────────────────────────",
        "      📊 FEATURES",
        "──────────────────────────",
        "🎮 Games    : 8+ Games",
        "🛠️ Utils    : 10+ Tools",
        "🎨 Generate : Image AI",
        "🎵 Music    : YouTube Music",
        "🔊 TTS      : Text to Speech",
        "🎬 Reels    : Download & Audio",
        "🎥 Post     : Feed Post",
        "──────────────────────────",
        "    💬 Type !help",
        "",
    ])


# ═══════════════════════════════════════════════════════════════
#  WELCOME MESSAGE
# ═══════════════════════════════════════════════════════════════

def welcome_message(username: str = "there"):
    """Welcome message"""
    return "\n".join([
        "",
        "┌──────────────────────────┐",
        f"│ 👋 @{username[:15]}    │",
        "├──────────────────────────┤",
        "│     ✨ AYAAN AI ✨       │",
        "├──────────────────────────┤",
        f"│ Type {P}help to start  │",
        f"│ Tag @{U[:12]} to chat  │",
        "└──────────────────────────┘",
        "",
    ])


# ═══════════════════════════════════════════════════════════════
#  SCORE CARD
# ═══════════════════════════════════════════════════════════════

def score_card(username: str, stats: dict):
    """User score card"""
    trivia = stats.get("trivia_wins", 0)
    guess = stats.get("guess_wins", 0)
    scramble = stats.get("scramble_wins", 0)
    wordseek = stats.get("wordseek_wins", 0)
    rps = stats.get("rps_wins", 0)
    total = stats.get("total_score", 0)
    streak = stats.get("streak", 0)

    return "\n".join([
        "",
        "┌──────────────────────────┐",
        f"│ 🏆 @{username[:12]}    │",
        "├──────────────────────────┤",
        make_line("🧠 Trivia", f"{trivia}"),
        make_line("🔢 Guess", f"{guess}"),
        make_line("🔤 Scramble", f"{scramble}"),
        make_line("🔎 Wordseek", f"{wordseek}"),
        make_line("✂️ RPS", f"{rps}"),
        "├──────────────────────────┤",
        make_line("⭐ Total", f"{total} pts"),
        make_line("🔥 Streak", f"{streak} days"),
        "└──────────────────────────┘",
        "",
    ])


# ═══════════════════════════════════════════════════════════════
#  LEADERBOARD
# ═══════════════════════════════════════════════════════════════

def leaderboard(players: list):
    """Global leaderboard"""
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [
        "",
        "┌──────────────────────────┐",
        "│ 🏆 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗     │",
        "├──────────────────────────┤",
    ]

    if not players:
        lines.append("│ No scores yet!          │")
    else:
        for i, (name, score) in enumerate(players[:10]):
            medal = medals[i] if i < len(medals) else str(i + 1)
            name = name[:10]
            lines.append(make_line(f"{medal} @{name}", f"{score}"))

    lines.append("└──────────────────────────┘")
    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  MENU DISPATCHER
# ═══════════════════════════════════════════════════════════════

def get_menu(menu_name: str) -> str:
    """Get menu by name"""
    menus = {
        "main": main_menu,
        "music": music_menu,
        "reel": reel_menu,
        "games": games_menu,
        "utils": utils_menu,
        "admin": admin_menu,
    }
    return menus.get(menu_name, main_menu)()


# ═══════════════════════════════════════════════════════════════
#  STANDALONE TEST
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("     📋 MENU PREVIEW")
    print("=" * 60)

    print("\n1. MAIN MENU")
    print("-" * 40)
    print(main_menu())

    print("\n2. MUSIC MENU")
    print("-" * 40)
    print(music_menu())

    print("\n3. REEL MENU")
    print("-" * 40)
    print(reel_menu())

    print("\n4. GAMES MENU")
    print("-" * 40)
    print(games_menu())

    print("\n5. UTILITIES MENU")
    print("-" * 40)
    print(utils_menu())

    print("\n6. ADMIN MENU")
    print("-" * 40)
    print(admin_menu())

    print("\n" + "=" * 60)
    print("✨ All Menus Loaded!")
