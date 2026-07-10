# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#   Boxed Menus - Width 19 (borders included)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import config

P = config.PREFIX
U = config.USERNAME

# ── Box Width 19 ──
BOX_WIDTH = 20
INNER_WIDTH = 26  # Content inside borders

# ── Left Label Width (including colon) ──
LEFT_WIDTH = 12

# ── Box Characters ──
TL = "┌"
TR = "┐"
BL = "└"
BR = "┘"
H = "─"
V = "│"
L = "├"
R = "┤"


def make_line(left: str, right: str) -> str:
    """Format: │ left: [right] │ with fixed left width"""
    left_str = str(left)
    right_str = str(right)
    
    # Add colon and pad left to LEFT_WIDTH
    left_part = left_str + ":"
    if len(left_part) < LEFT_WIDTH:
        left_part = left_part.ljust(LEFT_WIDTH)
    
    # Combine: left_part + space + right_str
    combined = len(left_part) + 1 + len(right_str)
    if combined <= INNER_WIDTH:
        spaces = " " * (INNER_WIDTH - combined)
        return f"{V}{left_part} {right_str}{spaces}{V}"
    else:
        # Truncate right_str to fit
        max_right = INNER_WIDTH - len(left_part) - 2  # -2 for space and one extra?
        if max_right < 0:
            max_right = 0
        right_str = right_str[:max_right]
        spaces = " " * (INNER_WIDTH - len(left_part) - 1 - len(right_str))
        return f"{V}{left_part} {right_str}{spaces}{V}"


def make_header(title: str) -> str:
    """Center title inside borders"""
    title_str = str(title)
    if len(title_str) > INNER_WIDTH:
        title_str = title_str[:INNER_WIDTH]
    spaces_left = (INNER_WIDTH - len(title_str)) // 2
    spaces_right = INNER_WIDTH - len(title_str) - spaces_left
    return f"{V}{' ' * spaces_left}{title_str}{' ' * spaces_right}{V}"


def top_box(title: str = "") -> str:
    """Top border with optional title"""
    if title:
        title_str = f" {title} "
        padding = (BOX_WIDTH - len(title_str) - 2) // 2
        return f"{TL}{H * padding}{title_str}{H * (BOX_WIDTH - len(title_str) - padding - 2)}{TR}"
    return f"{TL}{H * (BOX_WIDTH - 2)}{TR}"


def bottom_box() -> str:
    return f"{BL}{H * (BOX_WIDTH - 2)}{BR}"


def divider() -> str:
    return f"{L}{H * (BOX_WIDTH - 2)}{R}"


# ── MAIN MENU ──

def main_menu():
    lines = [
        "",
        top_box("AYAAN AI"),
        make_header("🤖 BOT MENU"),
        divider(),
        make_header("📋 COMMANDS"),
        divider(),
        make_line("!help  ", "📋 Menu"),
        make_line("!ping  ", "🏓 Speed"),
        make_line("!info  ", "ℹ️ Details"),
        make_line("!profile  ", "👤 Profile"),
        make_line("!stalk  ", "🕵️ Insta"),
        divider(),
        make_header("🎵 MUSIC"),
        divider(),
        make_line("!musiccmd  ", "🎵 All"),
        divider(),
        make_header("🎬 REELS"),
        divider(),
        make_line("!reelcmd  ", "🎬 All"),
        divider(),
        make_header("🎨 GENERATE"),
        divider(),
        make_line("!generate  ", "🖼️ Image"),
        divider(),
        make_header("🎮 GAMES"),
        divider(),
        make_line("!gamescmd  ", "🎮 All"),
        divider(),
        make_header("🛠️ UTILITIES"),
        divider(),
        make_line("!utilscmd  ", "🛠️ All"),
        divider(),
        make_header("👑 ADMIN"),
        divider(),
        make_line("!admincmd  ", "👑 Admin"),
        divider(),
        make_header("💬 AI CHAT"),
        divider(),
        make_line(f"@{U[:10]}  ", "🤖 Chat"),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── MUSIC MENU ──

def music_menu():
    lines = [
        "",
        top_box("MUSIC MENU"),
        make_line("!play  ", "🎵 Play Song"),
        make_line("!vn  ", "🎤 Voice Note"),
        make_line("!tts  ", "🔊 TTS"),
        make_line("!speak  ", "🧠 AI Voice"),
        make_line("!audio  ", "🎵 Reel Audio"),
        divider(),
        make_header("💡 Usage"),
        make_line("!play song  ", ""),
        make_line("!vn link  ", ""),
        make_line("!tts text  ", ""),
        make_line("!speak q  ", ""),
        make_line("!audio link  ", ""),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── REEL MENU ──

def reel_menu():
    lines = [
        "",
        top_box("REEL MENU"),
        make_line("!reel  ", "📥 Download"),
        make_line("!dreel  ", "📥 Download"),
        make_line("!audio  ", "🎵 Audio"),
        make_line("!post  ", "📸 Repost"),
        divider(),
        make_header("💡 Usage"),
        make_line("!reel link/reply  ", ""),
        make_line("!audio link/reply  ", ""),
        make_line("!post link  ", ""),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── GAMES MENU ──

def games_menu():
    lines = [
        "",
        top_box("GAMES MENU"),
        make_line("!trivia  ", "❓ Quiz"),
        make_line("!guess  ", "🔢 Guess"),
        make_line("!scramble  ", "🔤 Scramble"),
        make_line("!wordseek  ", "🔎 Wordle"),
        make_line("!rps  ", "✂️ RPS"),
        make_line("!wyr  ", "⚡ WYR"),
        make_line("!emoji  ", "😄 Emoji"),
        make_line("!tod  ", "🎯 T/D"),
        divider(),
        make_line("!score  ", "⭐ Stats"),
        make_line("!top  ", "🏆 Leader"),
        make_line("!daily  ", "🎁 Daily"),
        divider(),
        make_header("💡 !quit to exit"),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── UTILITIES MENU ──

def utils_menu():
    lines = [
        "",
        top_box("UTILITIES"),
        make_line("!calc  ", "➗ Calc"),
        make_line("!time  ", "🕐 Time"),
        make_line("!weather  ", "🌤️ Weather"),
        make_line("!horoscope  ", "🔮 Zodiac"),
        make_line("!choose  ", "🤔 Pick"),
        make_line("!remind  ", "⏰ Remind"),
        make_line("!generate  ", "🎨 Image"),
        divider(),
        make_line("!joke  ", "😂 Joke"),
        make_line("!fact  ", "🧠 Fact"),
        make_line("!quote  ", "💬 Quote"),
        make_line("!roast  ", "🔥 Roast"),
        make_line("!8ball  ", "🎱 8Ball"),
        make_line("!roll  ", "🎲 Roll"),
        make_line("!flip  ", "🪙 Flip"),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── ADMIN MENU ──

def admin_menu():
    lines = [
        "",
        top_box("ADMIN MENU"),
        make_line("!evil  ", "👿 Evil AI"),
        make_line("!evilclear  ", "🧹 Clear"),
        make_line("!addadmin  ", "➕ Add"),
        make_line("!removeadmin  ", "➖ Remove"),
        make_line("!listadmins  ", "📋 List"),
        make_line("!toggle  ", "🔧 Toggle"),
        make_line("!cmdstatus  ", "📊 Status"),
        divider(),
        make_line("!add  ", "👤 Add User"),
        make_line("!remove  ", "👤 Remove"),
        make_line("!changename  ", "📝 Name"),
        make_line("!changepfp  ", "🖼️ PFP"),
        make_line("!groupinfo  ", "📊 Info"),
        make_line("!groupadmins  ", "👑 Admins"),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── BOT INFO (FIXED) ──

def bot_info():
    """Bot info card - Owner name fixed, aligned with colons"""
    return "\n".join([
        "",
        top_box("AYAAN AI"),
        make_header("🤖 STATUS"),
        divider(),
        make_line("Name  ", "AYAAN AI"),
        make_line("Version  ", "2.3.0"),
        make_line("AI  ", "Groq LLaMA"),
        make_line("Engine  ", "Python 3"),
        make_line("Owner  ", "@ayaanplugs"),  # ✅ Dev → Owner
        make_line("Status  ", "🟢 Online"),
        divider(),
        make_header("📊 FEATURES"),
        divider(),
        make_line("Games  ", "8+"),
        make_line("Utils  ", "10+"),
        make_line("Generate  ", "Image AI"),
        make_line("Music  ", "YouTube"),
        make_line("TTS  ", "Text to Speech"),
        make_line("Reels  ", "DL + Audio"),
        make_line("Post  ", "Feed Post"),
        divider(),
        make_header("💬 Type !help"),
        bottom_box(),
        "",
    ])


# ── WELCOME ──

def welcome_message(username: str = "there"):
    return "\n".join([
        "",
        top_box(f"@{username[:10]}"),
        make_header("✨ AYAAN AI ✨"),
        divider(),
        make_line(f"Type {P}help  ", ""),
        make_line(f"Tag @{U[:10]} ", "🤖 Chat"),
        bottom_box(),
        "",
    ])


# ── SCORE CARD ──

def score_card(username: str, stats: dict):
    trivia = stats.get("trivia_wins", 0)
    guess = stats.get("guess_wins", 0)
    scramble = stats.get("scramble_wins", 0)
    wordseek = stats.get("wordseek_wins", 0)
    rps = stats.get("rps_wins", 0)
    total = stats.get("total_score", 0)
    streak = stats.get("streak", 0)

    lines = [
        "",
        top_box(f"🏆 {username[:10]}"),
        make_line("Trivia", str(trivia)),
        make_line("Guess", str(guess)),
        make_line("Scramble", str(scramble)),
        make_line("Wordseek", str(wordseek)),
        make_line("RPS", str(rps)),
        divider(),
        make_line("Total", f"{total} pts"),
        make_line("Streak", f"{streak} days"),
        bottom_box(),
        "",
    ]
    return "\n".join(lines)


# ── LEADERBOARD ──

def leaderboard(players: list):
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [
        "",
        top_box("LEADERBOARD"),
    ]
    if not players:
        lines.append(make_line("No scores", ""))
    else:
        for i, (name, score) in enumerate(players[:10]):
            medal = medals[i] if i < len(medals) else str(i + 1)
            name = name[:8]
            lines.append(make_line(f"{medal} @{name}", str(score)))
    lines.append(bottom_box())
    lines.append("")
    return "\n".join(lines)


# ── MENU DISPATCHER ──

def get_menu(menu_name: str) -> str:
    menus = {
        "main": main_menu,
        "music": music_menu,
        "reel": reel_menu,
        "games": games_menu,
        "utils": utils_menu,
        "admin": admin_menu,
    }
    return menus.get(menu_name, main_menu)()


# ── TEST ──

if __name__ == "__main__":
    print("\n" + "=" * 30)
    print("  MENU PREVIEW (Width 19)")
    print("=" * 30)
    print("\n1. MAIN MENU")
    print("-" * 30)
    print(main_menu())

    print("\n2. BOT INFO")
    print("-" * 30)
    print(bot_info())

    print("\n✨ All Menus Loaded!")
