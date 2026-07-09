# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#   Super Mobile-Optimized Menus
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import config

P = config.PREFIX
U = config.USERNAME
B = config.BRAND

# Total width including borders = 22 characters (Ultra Mobile Compact!)
BOX_WIDTH = 28
INNER_WIDTH = 25

# ── Box Drawing Characters ──
TL = "╔"  # Top-Left
TR = "╗"  # Top-Right
BL = "╚"  # Bottom-Left
BR = "╝"  # Bottom-Right
H = "═"   # Horizontal
V = "║"   # Vertical
L = "╠"   # Left-T
R = "╣"   # Right-T
T = "╦"   # Top-T
Btm = "╩" # Bottom-T
C = "╬"   # Cross


def make_line(left: str, right: str) -> str:
    """Format a line as '║ left [spaces] right ║' of exact BOX_WIDTH (22)."""
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


def make_header(title: str) -> str:
    """Center a title inside '║ title ║' of exact BOX_WIDTH (22)."""
    title_str = str(title)
    if len(title_str) >= INNER_WIDTH:
        title_str = title_str[:INNER_WIDTH]

    spaces_left = (INNER_WIDTH - len(title_str)) // 2
    spaces_right = INNER_WIDTH - len(title_str) - spaces_left
    return f"{V} {' ' * spaces_left}{title_str}{' ' * spaces_right} {V}"


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
    return f"{L}{H * (BOX_WIDTH - 2)}{R}"


def main_menu():
    """Main menu optimized for ultra-narrow mobile screens (22 chars width)."""
    lines = [
        "",
        "┌────────────────────┐",
        "│ ✨ 𝗔𝗬𝗔𝗔𝗡 𝗔𝗜 ✨   │",
        "│ ═══════════════════ │",
        "│ 🎮 𝗙𝗨𝗡 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦  │",
        "│ ═══════════════════ │",
        make_line(f"{P}help", "📋 Menu"),
        make_line(f"{P}ping", "🏓 Speed"),
        make_line(f"{P}info", "ℹ️ Details"),
        make_line(f"{P}joke", "😂 Joke"),
        make_line(f"{P}fact", "🧠 Fact"),
        make_line(f"{P}quote", "💬 Quote"),
        make_line(f"{P}roast", "🔥 @user"),
        make_line(f"{P}8ball", "🎱 Query"),
        make_line(f"{P}roll", "🎲 Dice"),
        make_line(f"{P}flip", "🪙 Coin"),
        make_line(f"{P}choose", "🤔 Pick"),
        make_line(f"{P}meme", "🚀 Meme"),
        make_line(f"{P}play", "🎵 Song"),
        make_line(f"{P}vn", "🎤 Voice"),
        make_line(f"{P}tts", "🔊 Speak"),
        make_line(f"{P}reel", "🎬 Reel"),   
        make_line(f"{P}audio", "🎵 Audio"), 
        make_line(f"{P}speak", "🧠 AI Voice"),
        make_line(f"{P}profile", "👤 Profile Info"),
        "│ ═══════════════════ │",
        "│ 🛠️ 𝗧𝗢𝗢𝗟𝗦 & 𝗨𝗧𝗜𝗟𝗦 │",
        "│ ═══════════════════ │",
        make_line(f"{P}calc", "➗ Math"),
        make_line(f"{P}time", "🕐 Clock"),
        make_line(f"{P}weather", "🌤️ Forecast"),
        make_line(f"{P}stalk", "🕵️ Instagram"),
        make_line(f"{P}remind", "⏰ Reminder"),
        make_line(f"{P}horoscope", "🔮 Zodiac"),
        "│ ═══════════════════ │",
        "│ 🕹️ 𝗚𝗔𝗠𝗘𝗦 & 𝗦𝗧𝗔𝗧𝗦 │",
        "│ ═══════════════════ │",
        make_line(f"{P}trivia", "❓ Quiz"),
        make_line(f"{P}guess", "🔢 Guess"),
        make_line(f"{P}scramble", "🔤 Word"),
        make_line(f"{P}wordseek", "🔎 Wordle"),
        make_line(f"{P}rps", "✂️ RPS"),
        make_line(f"{P}wyr", "⚡ Rather"),
        make_line(f"{P}emoji", "😄 Emoji"),
        make_line(f"{P}tod", "🎯 T/D"),
        make_line(f"{P}score", "⭐ Stats"),
        make_line(f"{P}top", "🏆 Leader"),
        make_line(f"{P}daily", "🎁 Daily"),
        "│ ═══════════════════ │",
        "│ 🤖 𝗔𝗜 𝗖𝗛𝗔𝗧𝗙𝗔𝗟𝗟  │",
        "│ ═══════════════════ │",
        make_line(f"@{U}", "💬 Chat AI"),
        "└────────────────────┘",
        " ✨ AYAAN AI • ⚡ Groq",
        "──────────────────────",
    ]
    return "\n".join(lines)


def games_menu():
    """Games menu optimized for 22 chars width."""
    lines = [
        "",
        "┌────────────────────┐",
        "│ 🎮 𝗚𝗔𝗠𝗘𝗦 𝗠𝗘𝗡𝗨   │",
        "│ ═══════════════════ │",
        "│ 🧠 𝗕𝗥𝗔𝗜𝗡 𝗣𝗨𝗭𝗭𝗟𝗘𝗦 │",
        "│ ═══════════════════ │",
        make_line(f"{P}trivia", "❓ Quiz"),
        make_line(f"{P}scramble", "🔤 Word"),
        make_line(f"{P}wordseek", "🔎 Wordle"),
        make_line(f"{P}emoji", "😄 Emoji"),
        "│ ═══════════════════ │",
        "│ 🎲 𝗤𝗨𝗜𝗖𝗞 𝗣𝗟𝗔𝗬    │",
        "│ ═══════════════════ │",
        make_line(f"{P}guess", "🔢 Guess"),
        make_line(f"{P}rps", "✂️ RPS"),
        make_line(f"{P}wyr", "⚡ Rather"),
        make_line(f"{P}tod", "🎯 T/D"),
        "│ ═══════════════════ │",
        "│ 📊 𝗣𝗘𝗥𝗙𝗢𝗥𝗠𝗔𝗡𝗖𝗘  │",
        "│ ═══════════════════ │",
        make_line(f"{P}score", "⭐ My Stats"),
        make_line(f"{P}top", "🏆 Leaderboard"),
        "└────────────────────┘",
        f" 💫 Type {P}quit to exit",
        "──────────────────────",
    ]
    return "\n".join(lines)


def bot_info():
    """Bot info card - Final"""
    return "\n".join([
        "",
        ".      ✨ AYAAN AI ✨",
        "      🤖 BOT STATUS",
        "─────────────────",
        "🤖 Name      : AYAAN AI",
        "📌 Version   : 2.3.0",
        "⚡ AI Model  : Groq LLaMA",
        "🛠️ Engine   : Python 3",
        "👨‍💻 Dev     : @ayaanplugs",
        "📡 Status   : 🟢 Online",
        "─────────────────",
        "      📊 FEATURES",
        "─────────────────",
        "🎮 Games    : 8+ Games",
        "🛠️ Utils    : 10+ Tools",
        "🎨 Generate : Image AI",
        "🎵 Music    : YouTube Music",
        "🔊 TTS      : Text to Speech",
        "🎬 Reels    : Download & Audio",
        "🎥 Post     : Feed Post",
        "─────────────────",
        "    💬 Type !help",
        "",
    ])


def welcome_message(username: str = "there"):
    """Welcome message optimized for 22 chars width."""
    lines = [
        "",
        "┌────────────────────┐",
        f"│ 👋 @{username[:12]}       │",
        "│ ═══════════════════ │",
        "│ ✨ 𝗔𝗬𝗔𝗔𝗡 𝗔𝗜 ✨   │",
        "│ ═══════════════════ │",
        f"│ Type {P}help to start │",
        f"│ Tag @{U[:12]} to chat │",
        "└────────────────────┘",
        "──────────────────────",
    ]
    return "\n".join(lines)


def score_card(username: str, stats: dict):
    """User score card optimized for 22 chars width."""
    trivia = stats.get("trivia_wins", 0)
    guess = stats.get("guess_wins", 0)
    scramble = stats.get("scramble_wins", 0)
    wordseek = stats.get("wordseek_wins", 0)
    rps = stats.get("rps_wins", 0)
    total = stats.get("total_score", 0)
    streak = stats.get("streak", 0)

    lines = [
        "",
        "┌────────────────────┐",
        f"│ 🏆 @{username[:10]}     │",
        "│ ═══════════════════ │",
        make_line("🧠 Trivia", f"{trivia}"),
        make_line("🔢 Guess", f"{guess}"),
        make_line("🔤 Scramble", f"{scramble}"),
        make_line("🔎 Wordseek", f"{wordseek}"),
        make_line("✂️ RPS", f"{rps}"),
        "│ ═══════════════════ │",
        make_line("⭐ Total", f"{total} pts"),
        make_line("🔥 Streak", f"{streak} days"),
        "└────────────────────┘",
        "──────────────────────",
    ]
    return "\n".join(lines)


def leaderboard(players: list):
    """Global leaderboard card optimized for 22 chars width."""
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [
        "",
        "┌────────────────────┐",
        "│ 🏆 𝗟𝗘𝗔𝗗𝗘𝗥𝗕𝗢𝗔𝗥𝗗 │",
        "│ ═══════════════════ │",
    ]

    if not players:
        lines.append("│ No scores yet!     │")
    else:
        for i, (name, score) in enumerate(players[:10]):
            medal = medals[i] if i < len(medals) else str(i + 1)
            name = name[:10]
            lines.append(make_line(f"{medal} @{name}", f"{score}"))

    lines.append("└────────────────────┘")
    lines.append("──────────────────────")
    return "\n".join(lines)
