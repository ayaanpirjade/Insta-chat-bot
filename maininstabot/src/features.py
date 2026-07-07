# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Fun Commands & Utilities
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import re
import random
import datetime
import src.game as game
import src.store as store
import config


# ── 1. Jokes ──────────────────────────
def get_joke() -> str:
    if not game.JOKES:
        return "Why did the robot go on vacation? To recharge its batteries! 🔋"
    j = random.choice(game.JOKES)
    return f"✨ {j['setup']}\n\n→ {j['punchline']}"


# ── 2. Facts ──────────────────────────
def get_fact() -> str:
    if not game.FACTS:
        return "🧠 A day on Venus is longer than a year on Venus!"
    return random.choice(game.FACTS)


# ── 3. Quotes ─────────────────────────
def get_quote() -> str:
    if not game.QUOTES:
        return "✨ 'The only way to do great work is to love what you do.' — Steve Jobs"
    q = random.choice(game.QUOTES)
    return f"💬 \"{q['quote']}\"\n\n— {q['author']}"


# ── 4. Roast ──────────────────────────
def get_roast(target: str) -> str:
    if not game.ROASTS:
        return f"Roasting {target}:\nYou're like a cloud — when you disappear, it's a beautiful day. ☀️"
    r = random.choice(game.ROASTS)
    return f"🔥 Roasting {target}:\n{r}"


# ── 5. 8-Ball ─────────────────────────
def get_8ball(question: str) -> str:
    if not game.EIGHT_BALL:
        return "🎱 Yes, definitely!"
    ans = random.choice(game.EIGHT_BALL)
    return f"🎱 Question: {question}\n→ Response: {ans}" if question else f"🎱 Response: {ans}"


# ── 6. Dice Roll ──────────────────────
def roll_dice(args: str) -> str:
    m = re.search(r"(\d+)d(\d+)", args.lower())
    if m:
        count = min(int(m.group(1)), 10)
        sides = int(m.group(2))
        if count <= 0 or sides <= 0:
            return "🎲 Invalid dice specification! Try rolling standard dice like 1d6."
        rolls = [random.randint(1, sides) for _ in range(count)]
        return f"🎲 Rolling {count}d{sides}:\n🎲 Rolls: {rolls}\n📊 Total: {sum(rolls)}"
    return f"🎲 Rolled a standard dice: {random.randint(1, 6)}!"


# ── 7. Coin Flip ──────────────────────
def flip_coin() -> str:
    return f"🪙 Coin Toss:\n→ {'Heads! 👑' if random.random() > 0.5 else 'Tails! 🔄'}"


# ── 8. Choose ─────────────────────────
def choose_option(options_text: str) -> str:
    opts = [o.strip() for o in re.split(r"[,/|]| or ", options_text) if o.strip()]
    if not opts:
        return "⚠️ Give options separated by commas!\nExample: !choose pizza, burger, sushi"
    return f"🤔 I choose: **{random.choice(opts)}**!"


# ── 9. Calculator ─────────────────────
def calculator(expr: str) -> str:
    # Sanitize and evaluate simple math expression
    clean = re.sub(r"[^0-9\+\-\*\/\(\)\. ]", "", expr)
    if not clean.strip():
        return "⚠️ Please provide a math expression.\nExample: !calc 5 * (3 + 2)"
    try:
        # Safe evaluation of basic math
        res = eval(clean, {"__builtins__": None}, {})
        return f"🔢 Equation: {expr}\n✨ Result: {res}"
    except Exception:
        return "❌ Invalid math expression. Use standard operators (+, -, *, /)."


# ── 10. Time ──────────────────────────
def get_time() -> str:
    now = datetime.datetime.now()
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "         ⏰ SYSTEM TIME ⏰        \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"🕒 Time: {now.strftime('%I:%M:%S %p')}\n"
        f"🌐 Zone: Local Server Time\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ── 11. Weather ───────────────────────
WEATHERS = ["Sunny ☀️", "Rainy 🌧️", "Cloudy ☁️", "Stormy ⛈️", "Windy 💨", "Snowy ❄️"]


def get_weather(city: str) -> str:
    city = city.strip().title()
    if not city:
        return "⚠️ Please specify a city.\nExample: !weather Mumbai"

    # Mocking weather nicely with deterministic values based on city name characters
    temp = 15 + (sum(ord(c) for c in city) % 25)
    condition = WEATHERS[sum(ord(c) for c in city) % len(WEATHERS)]
    humidity = 30 + (sum(ord(c) for c in city) % 60)

    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       🌤️ WEATHER — {city.upper()} 🌤️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"🌦️ Condition  : {condition}\n"
        f"💧 Humidity   : {humidity}%\n"
        f"💨 Wind Speed : {humidity // 5} km/h\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ── 12. Profile Stalker ────────────────
def stalk_profile(target: str, cl) -> str:
    target = target.strip().replace("@", "")
    if not target:
        return "⚠️ Please specify an Instagram handle to stalk.\nExample: !stalk ayaan_ai"

    try:
        user_info = cl.user_info_by_username(target)
        is_private = "Yes 🔒" if user_info.is_private else "No 🔓"
        bio = user_info.biography if user_info.biography else "No bio."

        return (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"       🕵️ PROFILE: @{user_info.username.upper()} 🕵️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Full Name : {user_info.full_name}\n"
            f"🆔 User ID   : {user_info.pk}\n"
            f"👥 Followers : {user_info.follower_count:,}\n"
            f"🗣️ Following : {user_info.following_count:,}\n"
            f"📸 Posts     : {user_info.media_count}\n"
            f"🔒 Private   : {is_private}\n"
            f"📝 Biography :\n{bio}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    except Exception as e:
        # Fallback if profile not found or API fails
        print(f"  ⚠️ Profile stalk failed: {e}")
        return f"❌ Could not retrieve profile data for @{target}. User might not exist or session is limited."


# ── 13. Horoscope ─────────────────────
def get_horoscope(sign: str) -> str:
    sign = sign.strip().lower()
    if sign not in game.HOROSCOPE:
        valid_signs = ", ".join(game.HOROSCOPE.keys()) if game.HOROSCOPE else "Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn, Aquarius, Pisces"
        return f"⚠️ Invalid Zodiac Sign!\n🔮 Valid Signs: {valid_signs}\nExample: !horoscope Leo"

    msg = random.choice(game.HOROSCOPE[sign])
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"       🔮 DAILY HOROSCOPE — {sign.upper()} 🔮\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{msg}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


# ── 14. Text Memes ────────────────────
MEMES = [
    "Programmer:\nMy code doesn't work. 🤷\n*fixes a typo*\nMy code works, and I have\nno idea why. 🙃",
    "How to solve a bug:\n1. Copy error message 📝\n2. Search on Google 🔍\n3. Open StackOverflow 🌐\n4. Copy paste 📋\n5. Pray 🙏",
    "An SQL query walks into a\nbar, walks up to two tables\nand asks:\n'Can I join you?' 📊",
    "Why do programmers prefer\ndark mode? 🕶️\nBecause light attracts bugs! 🐛",
    "Client: Need this in 3 days.\nDev: That's impossible.\nClient: There's a bonus.\nDev: *chugs coffee* ☕⚡"
]


def get_meme() -> str:
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "    🚀 AYAAN MEME 🚀  \n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{random.choice(MEMES)}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


# ── 15. Daily Claim ───────────────────
def claim_daily(user_id: str, username: str) -> str:
    data = store.get_user(user_id, username)
    today = datetime.date.today().isoformat()

    if data.get("last_daily") == today:
        return (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "   🎁 DAILY BONUS 🎁  \n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ Claimed today!\n"
            "Come back tomorrow! ⏰\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    data["last_daily"] = today
    data["total_score"] = data.get("total_score", 0) + 50
    store.save_user(user_id, data)
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "   🎁 DAILY BONUS 🎁  \n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎉 Success! Claimed daily\n"
        "   bonus of +50 points! 🪙\n"
        f"⭐ Score: {data['total_score']} pt\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

