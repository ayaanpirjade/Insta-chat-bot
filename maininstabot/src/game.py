# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Interactive Games Logic
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import random
import config
import src.store as store

# ── Loaded Game Data ──────────────────
TRIVIA = []
FACTS = []
JOKES = []
QUOTES = []
ROASTS = []
EIGHT_BALL = []
WYR = []
EMOJI = []
TOD = {}
HOROSCOPE = {}


def load_game_data():
    """Load all JSON database files into memory."""
    global TRIVIA, FACTS, JOKES, QUOTES, ROASTS, EIGHT_BALL, WYR, EMOJI, TOD, HOROSCOPE
    try:
        with open(os.path.join(config.DATA_DIR, "trivia.json"), "r", encoding="utf-8") as f:
            TRIVIA = json.load(f)
        with open(os.path.join(config.DATA_DIR, "facts.json"), "r", encoding="utf-8") as f:
            FACTS = json.load(f)
        with open(os.path.join(config.DATA_DIR, "jokes.json"), "r", encoding="utf-8") as f:
            JOKES = json.load(f)
        with open(os.path.join(config.DATA_DIR, "quotes.json"), "r", encoding="utf-8") as f:
            QUOTES = json.load(f)
        with open(os.path.join(config.DATA_DIR, "roasts.json"), "r", encoding="utf-8") as f:
            ROASTS = json.load(f)
        with open(os.path.join(config.DATA_DIR, "8ball.json"), "r", encoding="utf-8") as f:
            EIGHT_BALL = json.load(f)
        with open(os.path.join(config.DATA_DIR, "wouldYouRather.json"), "r", encoding="utf-8") as f:
            WYR = json.load(f)
        with open(os.path.join(config.DATA_DIR, "emojiPuzzles.json"), "r", encoding="utf-8") as f:
            EMOJI = json.load(f)
        with open(os.path.join(config.DATA_DIR, "truthOrDare.json"), "r", encoding="utf-8") as f:
            TOD = json.load(f)
        with open(os.path.join(config.DATA_DIR, "horoscope.json"), "r", encoding="utf-8") as f:
            HOROSCOPE = json.load(f)
        print("✅ Game data files loaded successfully!")
    except Exception as e:
        print(f"⚠️ Failed to load game data files: {e}")


# ── Active Sessions ───────────────────
# Format: { thread_id: { "game": "trivia|guess|...", "state": {...} } }
active_games = {}


def get_active_game(thread_id: str) -> dict | None:
    """Return the active game session for this thread, if any."""
    return active_games.get(thread_id)


def quit_game(thread_id: str) -> str:
    """End any active game session in this thread."""
    if thread_id in active_games:
        game = active_games[thread_id]["game"]
        del active_games[thread_id]
        return f"🚪 You left the game of {game.upper()}. Play again soon!"
    return "❌ No game is currently active in this chat."


# ── 1. Trivia Game ────────────────────
def start_trivia(thread_id: str) -> str:
    if not TRIVIA:
        return "❌ Trivia questions are not loaded."
    q = random.choice(TRIVIA)
    active_games[thread_id] = {
        "game": "trivia",
        "state": {
            "question": q["question"],
            "options": q["options"],
            "answer": q["answer"].upper(),
            "category": q.get("category", "General"),
        },
    }
    opts = "\n".join(q["options"])
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "        🧠 AYAAN AI TRIVIA 🧠     \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 Category: {q.get('category', 'General').upper()}\n\n"
        f"❓ Question:\n{q['question']}\n\n"
        f"Options:\n{opts}\n\n"
        "💡 Reply with A, B, C, or D!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_trivia(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    ans = text.strip().upper()
    if ans not in ["A", "B", "C", "D"]:
        return "⚠️ Invalid choice. Please reply with A, B, C, or D (or !quit to exit)."

    correct = state["answer"]
    del active_games[thread_id]  # End game

    if ans == correct:
        store.add_score(user_id, "trivia", points=10, username=username)
        return (
            "🎉 CORRECT! You got it right! 🎉\n"
            f"🏅 Answer: {correct}\n"
            "⭐ Score: +10 Points added to your profile!"
        )
    else:
        store.add_loss(user_id, "trivia", username=username)
        return (
            "❌ INCORRECT! Better luck next time.\n"
            f"🏅 Correct Answer: {correct}"
        )


# ── 2. Number Guessing ────────────────
def start_guess(thread_id: str) -> str:
    secret = random.randint(1, 100)
    active_games[thread_id] = {
        "game": "guess",
        "state": {"secret": secret, "attempts": 0},
    }
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔢 NUMBER GUESSING 🔢      \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 I'm thinking of a number between 1 and 100.\n"
        "💬 Type your guess!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_guess(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    try:
        guess = int(text.strip())
    except ValueError:
        return "⚠️ Please enter a valid number (or !quit to exit)."

    state["attempts"] += 1
    secret = state["secret"]

    if guess == secret:
        attempts = state["attempts"]
        del active_games[thread_id]
        points = max(20 - (attempts * 2), 5)
        store.add_score(user_id, "guess", points=points, username=username)
        return (
            f"🎉 CONGRATULATIONS! You guessed it in {attempts} attempts! 🎉\n"
            f"🏅 The secret number was {secret}.\n"
            f"⭐ Score: +{points} Points added to your profile!"
        )
    elif guess < secret:
        return f"📈 Higher! (Attempt {state['attempts']})"
    else:
        return f"📉 Lower! (Attempt {state['attempts']})"


# ── 3. Word Scramble ──────────────────
# Simple local word list fallback
WORDS = ["python", "instagram", "android", "database", "developer", "computer", "algorithm", "security"]


def start_scramble(thread_id: str) -> str:
    word = random.choice(WORDS)
    scrambled = "".join(random.sample(word, len(word)))
    while scrambled == word:
        scrambled = "".join(random.sample(word, len(word)))

    active_games[thread_id] = {
        "game": "scramble",
        "state": {"word": word, "scrambled": scrambled, "hint_given": False},
    }
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🔤 WORD SCRAMBLE 🔤        \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧩 Scrambled: {scrambled.upper()}\n"
        f"💬 Unscramble the word! (Type !hint if stuck)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_scramble(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    word = state["word"]
    guess = text.strip().lower()

    if guess == "!hint":
        if state["hint_given"]:
            return f"💡 Hint: The word starts with '{word[0].upper()}' and ends with '{word[-1].upper()}'."
        state["hint_given"] = True
        return f"💡 Hint: The word starts with '{word[0].upper()}'."

    if guess == word:
        del active_games[thread_id]
        points = 10 if not state["hint_given"] else 5
        store.add_score(user_id, "scramble", points=points, username=username)
        return (
            "🎉 CORRECT! You unscrambled it! 🎉\n"
            f"🏅 Word: {word.upper()}\n"
            f"⭐ Score: +{points} Points added to your profile!"
        )
    else:
        return "❌ Wrong answer! Try again (or type !hint for help, !quit to exit)."


# ── 4. Rock Paper Scissors ────────────
def start_rps(thread_id: str) -> str:
    active_games[thread_id] = {"game": "rps", "state": {}}
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "    ✂️ ROCK PAPER SCISSORS ✂️     \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "✊ Choose Rock\n"
        "✋ Choose Paper\n"
        "✌️ Choose Scissors\n"
        "💬 Type Rock, Paper, or Scissors!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_rps(thread_id: str, text: str, user_id: str, username: str) -> str:
    player = text.strip().lower()
    choices = ["rock", "paper", "scissors"]
    emoji_map = {"rock": "✊ Rock", "paper": "✋ Paper", "scissors": "✌️ Scissors"}

    if player not in choices:
        return "⚠️ Invalid choice. Choose Rock, Paper, or Scissors (or !quit to exit)."

    computer = random.choice(choices)
    del active_games[thread_id]  # End game

    result = ""
    points = 0
    if player == computer:
        result = "🤝 It's a TIE!"
        store.add_loss(user_id, "rps", username=username)
    elif (
        (player == "rock" and computer == "scissors")
        or (player == "paper" and computer == "rock")
        or (player == "scissors" and computer == "paper")
    ):
        result = "🎉 YOU WIN! 🎉"
        points = 10
        store.add_score(user_id, "rps", points=points, username=username)
    else:
        result = "😢 YOU LOSE! Better luck next time."
        store.add_loss(user_id, "rps", username=username)

    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🧑 You     : {emoji_map[player]}\n"
        f"🤖 Bot     : {emoji_map[computer]}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 Result  : {result}\n"
        f"⭐ Score   : +{points} Points" if points > 0 else f"📢 Result  : {result}"
    )


# ── 5. Would You Rather ───────────────
def start_wyr(thread_id: str) -> str:
    if not WYR:
        return "❌ Would You Rather questions are not loaded."
    q = random.choice(WYR)
    active_games[thread_id] = {"game": "wyr", "state": {}}
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "      🤔 WOULD YOU RATHER 🤔       \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔴 Option A: {q['optionA']}\n"
        "      --- OR ---\n"
        f"🔵 Option B: {q['optionB']}\n\n"
        "💬 Reply with A or B to make your choice!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_wyr(thread_id: str, text: str, user_id: str, username: str) -> str:
    ans = text.strip().upper()
    if ans not in ["A", "B"]:
        return "⚠️ Please reply with A or B (or !quit to exit)."

    del active_games[thread_id]  # End game
    # Show fun statistics (mock percentages to make it engaging)
    a_pct = random.randint(30, 70)
    b_pct = 100 - a_pct

    choice_str = "Option A" if ans == "A" else "Option B"
    return (
        f"👍 Choice registered! You chose {choice_str}.\n"
        f"📊 Other users' choices:\n"
        f"🔴 Option A: {a_pct}%\n"
        f"🔵 Option B: {b_pct}%"
    )


# ── 6. Emoji Puzzle ───────────────────
def start_emoji(thread_id: str) -> str:
    if not EMOJI:
        return "❌ Emoji puzzles are not loaded."
    q = random.choice(EMOJI)
    active_games[thread_id] = {
        "game": "emoji",
        "state": {
            "emojis": q["emojis"],
            "answer": q["answer"].strip().lower(),
            "hint": q["hint"],
            "hint_given": False,
        },
    }
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       🧩 EMOJI PUZZLE 🧩         \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 Category: {q.get('category', 'Movie').upper()}\n"
        f"👀 Puzzle: {q['emojis']}\n"
        f"💬 Guess the answer! (Type !hint if stuck)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_emoji(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    answer = state["answer"]
    guess = text.strip().lower()

    if guess == "!hint":
        state["hint_given"] = True
        return f"💡 Hint: {state['hint']}"

    # Allow partial match or exact
    if guess == answer or (len(guess) > 3 and guess in answer):
        del active_games[thread_id]
        points = 15 if not state["hint_given"] else 5
        store.add_score(user_id, "emoji", points=points, username=username)
        return (
            "🎉 CORRECT! Awesome job! 🎉\n"
            f"🏅 Answer: {answer.upper()}\n"
            f"⭐ Score: +{points} Points added to your profile!"
        )
    else:
        return "❌ Incorrect guess! Try again (or type !hint for help, !quit to exit)."


# ── 7. Truth or Dare ──────────────────
def start_tod(thread_id: str) -> str:
    active_games[thread_id] = {"game": "tod", "state": {}}
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "      🔥 TRUTH OR DARE 🔥         \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 Type 'Truth' or 'Dare'!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_tod(thread_id: str, text: str, user_id: str, username: str) -> str:
    choice = text.strip().lower()
    if choice not in ["truth", "dare"]:
        return "⚠️ Please type 'Truth' or 'Dare' (or !quit to exit)."

    del active_games[thread_id]  # End game

    if choice == "truth":
        q = random.choice(TOD.get("truths", ["What is your biggest secret?"]))
        return f"🧐 TRUTH:\n{q}\n\n💬 Be honest!"
    else:
        d = random.choice(TOD.get("dares", ["Send a funny emoji to your crush."]))
        return f"🔥 DARE:\n{d}\n\n💬 Do you accept the challenge?"


# ── 8. Wordseek Game (Wordle Style) ──
def start_wordseek(thread_id: str) -> str:
    word_pool = [
        "LIONS", "BIRDS", "STARS", "EARTH", "SOLAR", "SPACE", "WATER", "PLANT", "FLAME", 
        "APPLE", "PEACH", "PIZZA", "SWEET", "HAPPY", "SMILE", "SMART", "GREEN", "WHITE", 
        "SHARK", "CLOUD", "WORLD", "DANCE", "HOUSE", "SOUND", "MUSIC", "NOVEL", "TRAIN", 
        "PLANE", "BEACH", "NIGHT", "CLOCK", "LIGHT", "DRAFT", "ANGLE"
    ]
    word = random.choice(word_pool).upper()

    active_games[thread_id] = {
        "game": "wordseek",
        "state": {
            "word": word,
            "attempts": 0,
            "history": [],
            "hint_given": False,
        },
    }

    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        " 🔎 WORDSEEK (WORDLE) 🔎\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 Guess the 5-letter\n"
        "   secret word!\n"
        "🎯 Attempts: 0/6\n"
        "\n"
        "💬 Type a 5-letter word!\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


def handle_wordseek(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    secret = state["word"]
    guess = text.strip().upper()

    if guess == "!HINT":
        state["hint_given"] = True
        return f"💡 Hint: Starts with '{secret[0]}' and has letters from {sorted(list(set(secret[:3])))}."

    # Validate 5 letters
    if len(guess) != 5 or not guess.isalpha():
        return "⚠️ Please enter a valid 5-letter word (or !quit)!"

    state["attempts"] += 1
    attempts = state["attempts"]

    # Wordle matching algorithm
    feedback = ["⬛"] * 5
    secret_used = [False] * 5
    guess_used = [False] * 5

    # 1st Pass: Greens (Correct position)
    for i in range(5):
        if guess[i] == secret[i]:
            feedback[i] = "🟩"
            secret_used[i] = True
            guess_used[i] = True

    # 2nd Pass: Yellows (Wrong position but present)
    for i in range(5):
        if not guess_used[i]:
            for j in range(5):
                if not secret_used[j] and guess[i] == secret[j]:
                    feedback[i] = "🟨"
                    secret_used[j] = True
                    break

    # Add attempt to history
    guess_spaced = " ".join(list(guess))
    feedback_str = " ".join(feedback)
    state["history"].append(f"{guess_spaced}\n👉 {feedback_str}")

    # Build history display
    history_display = "\n\n".join(state["history"])

    # Win condition
    if guess == secret:
        del active_games[thread_id]
        points = 20 if not state["hint_given"] else 10
        store.add_score(user_id, "wordseek", points=points, username=username)
        return (
            "🎉 CORRECT! You got it! 🎉\n"
            f"🏅 Word: {secret}\n"
            f"🎯 Attempts: {attempts}/6\n"
            f"⭐ Score: +{points} Points added!"
        )

    # Lose condition
    if attempts >= 6:
        del active_games[thread_id]
        store.add_loss(user_id, "wordseek", username=username)
        return (
            "😢 GAME OVER! Out of turns.\n"
            f"🏅 The word was: {secret}\n"
            "Better luck next time!"
        )

    # Continue game
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        " 🔎 WORDSEEK (WORDLE) 🔎\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{history_display}\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎯 Attempts: {attempts}/6\n"
        "💬 Enter your next guess!\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


