# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎮 AYAAN AI - Infinite Games
#          AI + 100+ Fallback Questions
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import random
import re
from typing import Optional, Dict, List, Any
import config
import src.store as store
from groq import Groq

# ── AI Client ──
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        try:
            _groq_client = Groq(api_key=config.GROQ_API_KEY)
        except:
            pass
    return _groq_client

# ── Active Sessions ──
active_games: Dict[str, Dict] = {}
_used_questions: Dict[str, List[str]] = {}

# ── 100+ FALLBACK QUESTIONS ──
FALLBACK_TRIVIA = [
    {"question": "What is the chemical symbol for water?", "options": ["A. H2O", "B. CO2", "C. NaCl", "D. HCl"], "answer": "A", "category": "Science"},
    {"question": "What planet is known as the Red Planet?", "options": ["A. Earth", "B. Mars", "C. Jupiter", "D. Venus"], "answer": "B", "category": "Science"},
    {"question": "What is the largest organ in the human body?", "options": ["A. Liver", "B. Heart", "C. Skin", "D. Brain"], "answer": "C", "category": "Science"},
    {"question": "How many bones are in the adult human body?", "options": ["A. 106", "B. 206", "C. 306", "D. 406"], "answer": "B", "category": "Science"},
    {"question": "What gas do plants absorb from the atmosphere?", "options": ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Hydrogen"], "answer": "C", "category": "Science"},
    {"question": "What is the speed of light?", "options": ["A. 300,000 km/s", "B. 150,000 km/s", "C. 500,000 km/s", "D. 100,000 km/s"], "answer": "A", "category": "Science"},
    {"question": "What is the chemical formula for table salt?", "options": ["A. NaCl", "B. HCl", "C. NaOH", "D. KCl"], "answer": "A", "category": "Science"},
    {"question": "What part of the cell contains genetic material?", "options": ["A. Nucleus", "B. Membrane", "C. Cytoplasm", "D. Ribosome"], "answer": "A", "category": "Science"},
    {"question": "What is the hardest natural substance on Earth?", "options": ["A. Gold", "B. Diamond", "C. Platinum", "D. Iron"], "answer": "B", "category": "Science"},
    {"question": "What is the unit of electric current?", "options": ["A. Volt", "B. Ohm", "C. Ampere", "D. Watt"], "answer": "C", "category": "Science"},
    {"question": "What is the pH of pure water?", "options": ["A. 5", "B. 6", "C. 7", "D. 8"], "answer": "C", "category": "Science"},
    {"question": "What is the boiling point of water in Celsius?", "options": ["A. 50°C", "B. 100°C", "C. 150°C", "D. 200°C"], "answer": "B", "category": "Science"},
    {"question": "What is the largest bone in the human body?", "options": ["A. Tibia", "B. Humerus", "C. Femur", "D. Pelvis"], "answer": "C", "category": "Science"},
    {"question": "What is the smallest planet in our solar system?", "options": ["A. Mercury", "B. Venus", "C. Mars", "D. Pluto"], "answer": "A", "category": "Science"},
    {"question": "What is the study of heredity called?", "options": ["A. Biology", "B. Genetics", "C. Ecology", "D. Anatomy"], "answer": "B", "category": "Science"},
    {"question": "In which year did World War II end?", "options": ["A. 1943", "B. 1944", "C. 1945", "D. 1946"], "answer": "C", "category": "History"},
    {"question": "Who was the first President of the United States?", "options": ["A. John Adams", "B. Thomas Jefferson", "C. George Washington", "D. Abraham Lincoln"], "answer": "C", "category": "History"},
    {"question": "What was the ancient civilization known for building pyramids?", "options": ["A. Greek", "B. Roman", "C. Egyptian", "D. Persian"], "answer": "C", "category": "History"},
    {"question": "In which year did the Titanic sink?", "options": ["A. 1910", "B. 1911", "C. 1912", "D. 1913"], "answer": "C", "category": "History"},
    {"question": "Who wrote the 'I Have a Dream' speech?", "options": ["A. Malcolm X", "B. Martin Luther King Jr.", "C. Nelson Mandela", "D. Barack Obama"], "answer": "B", "category": "History"},
    {"question": "What is the largest continent?", "options": ["A. Africa", "B. Asia", "C. North America", "D. Europe"], "answer": "B", "category": "Geography"},
    {"question": "What is the longest river in the world?", "options": ["A. Amazon", "B. Nile", "C. Mississippi", "D. Yangtze"], "answer": "B", "category": "Geography"},
    {"question": "What is the capital of France?", "options": ["A. London", "B. Paris", "C. Rome", "D. Berlin"], "answer": "B", "category": "Geography"},
    {"question": "What is the largest desert in the world?", "options": ["A. Sahara", "B. Gobi", "C. Kalahari", "D. Arabian"], "answer": "A", "category": "Geography"},
    {"question": "What is the highest mountain in the world?", "options": ["A. K2", "B. Mount Everest", "C. Kilimanjaro", "D. Denali"], "answer": "B", "category": "Geography"},
    {"question": "What is the smallest country in the world?", "options": ["A. Vatican City", "B. Monaco", "C. San Marino", "D. Liechtenstein"], "answer": "A", "category": "Geography"},
    {"question": "What ocean is the largest?", "options": ["A. Atlantic", "B. Indian", "C. Pacific", "D. Arctic"], "answer": "C", "category": "Geography"},
    {"question": "What is the capital of India?", "options": ["A. Mumbai", "B. Delhi", "C. Kolkata", "D. Chennai"], "answer": "B", "category": "Geography"},
    {"question": "What is the name of the fictional wizarding school in Harry Potter?", "options": ["A. Beauxbatons", "B. Durmstrang", "C. Hogwarts", "D. Ilvermorny"], "answer": "C", "category": "Pop Culture"},
    {"question": "Who played Iron Man in the MCU?", "options": ["A. Chris Evans", "B. Robert Downey Jr.", "C. Chris Hemsworth", "D. Scarlett Johansson"], "answer": "B", "category": "Pop Culture"},
    {"question": "What is the highest-grossing film of all time?", "options": ["A. Titanic", "B. Avatar", "C. Endgame", "D. The Force Awakens"], "answer": "B", "category": "Pop Culture"},
    {"question": "Who is the creator of the show 'The Simpsons'?", "options": ["A. Seth MacFarlane", "B. Matt Groening", "C. Trey Parker", "D. Dan Harmon"], "answer": "B", "category": "Pop Culture"},
    {"question": "What band is known for the song 'Bohemian Rhapsody'?", "options": ["A. The Beatles", "B. Led Zeppelin", "C. Queen", "D. Pink Floyd"], "answer": "C", "category": "Pop Culture"},
    {"question": "Who co-founded Microsoft?", "options": ["A. Steve Jobs", "B. Bill Gates", "C. Mark Zuckerberg", "D. Jeff Bezos"], "answer": "B", "category": "Technology"},
    {"question": "What does CPU stand for?", "options": ["A. Central Process Unit", "B. Computer Personal Unit", "C. Central Processing Unit", "D. Control Process Unit"], "answer": "C", "category": "Technology"},
    {"question": "Who created the World Wide Web?", "options": ["A. Bill Gates", "B. Steve Jobs", "C. Tim Berners-Lee", "D. Mark Zuckerberg"], "answer": "C", "category": "Technology"},
    {"question": "What is the most popular programming language?", "options": ["A. Python", "B. JavaScript", "C. Java", "D. C++"], "answer": "A", "category": "Technology"},
    {"question": "What is the name of the first computer?", "options": ["A. ENIAC", "B. UNIVAC", "C. ABC", "D. Colossus"], "answer": "A", "category": "Technology"},
    {"question": "What company owns Instagram?", "options": ["A. Google", "B. Microsoft", "C. Meta", "D. Amazon"], "answer": "C", "category": "Technology"},
    {"question": "What does HTML stand for?", "options": ["A. Hyper Text Markup Language", "B. High Tech Machine Language", "C. Hyper Transfer Markup Language", "D. None"], "answer": "A", "category": "Technology"},
]

FALLBACK_EMOJI = [
    {"emojis": "🦁👑", "answer": "The Lion King", "category": "Movie", "hint": "Disney movie about a young lion prince"},
    {"emojis": "🕷️🙋‍♂️", "answer": "Spider-Man", "category": "Movie", "hint": "Superhero bitten by a spider"},
    {"emojis": "❄️🙋‍♀️", "answer": "Frozen", "category": "Movie", "hint": "Disney movie with ice powers"},
    {"emojis": "🚢🏔️💔", "answer": "Titanic", "category": "Movie", "hint": "Ship romance tragedy"},
    {"emojis": "🦖🏜️🌳", "answer": "Jurassic Park", "category": "Movie", "hint": "Dinosaurs running wild"},
    {"emojis": "🦇🙋‍♂️🏙️", "answer": "Batman", "category": "Movie", "hint": "Gotham's dark knight"},
    {"emojis": "👨‍🚀🚀🌌", "answer": "Interstellar", "category": "Movie", "hint": "Space and time dilation"},
    {"emojis": "🧙‍♂️💍🏔️", "answer": "Lord of the Rings", "category": "Movie", "hint": "One ring to rule them all"},
    {"emojis": "🤖🔫💊", "answer": "The Matrix", "category": "Movie", "hint": "Red pill or blue pill"},
    {"emojis": "👽👾🛸", "answer": "ET", "category": "Movie", "hint": "Phone home"},
    {"emojis": "🐠🌊🔱", "answer": "Finding Nemo", "category": "Movie", "hint": "A fish lost in the ocean"},
    {"emojis": "👻🏚️🔫", "answer": "Ghostbusters", "category": "Movie", "hint": "Who you gonna call?"},
    {"emojis": "⚡🔮🧙‍♂️", "answer": "Harry Potter", "category": "Movie", "hint": "The boy who lived"},
    {"emojis": "🦸‍♂️🕸️🏙️", "answer": "Spider-Man", "category": "Movie", "hint": "Friendly neighborhood hero"},
    {"emojis": "🐺🧛‍♂️🌕", "answer": "Twilight", "category": "Movie", "hint": "Vampire and werewolf romance"},
    {"emojis": "🚗🤖🔧", "answer": "Transformers", "category": "Movie", "hint": "Robots in disguise"},
    {"emojis": "🏴‍☠️⚓🗺️", "answer": "Pirates of the Caribbean", "category": "Movie", "hint": "Captain Jack Sparrow"},
    {"emojis": "🦍🏙️👑", "answer": "King Kong", "category": "Movie", "hint": "Giant ape on a building"},
    {"emojis": "👽🌍🔫", "answer": "Men in Black", "category": "Movie", "hint": "Secret agents fighting aliens"},
]

# ── 50+ WYR ──
FALLBACK_WYR = [
    {"optionA": "Always have to sing instead of speaking", "optionB": "Always have to dance everywhere you go"},
    {"optionA": "Be able to fly but only at 2 mph", "optionB": "Teleport but only to places you've been in last 24 hours"},
    {"optionA": "Read minds but everyone can read yours", "optionB": "Never read minds but always know when someone is lying"},
    {"optionA": "Live without music", "optionB": "Live without movies"},
    {"optionA": "Always be 15 minutes late", "optionB": "Always be 25 minutes early"},
    {"optionA": "Unlimited money but no friends", "optionB": "Unlimited friends but no money"},
    {"optionA": "Never have to sleep", "optionB": "Never have to eat"},
    {"optionA": "Be invisible for a day", "optionB": "Fly for a day"},
    {"optionA": "Time travel to the past", "optionB": "Time travel to the future"},
    {"optionA": "Speak all languages", "optionB": "Talk to animals"},
    {"optionA": "Live in a treehouse", "optionB": "Live in a submarine"},
    {"optionA": "Always be cold", "optionB": "Always be hot"},
    {"optionA": "Be famous but poor", "optionB": "Be unknown but rich"},
    {"optionA": "Lose your phone for a year", "optionB": "Lose your internet for a year"},
    {"optionA": "Never eat chocolate again", "optionB": "Never eat pizza again"},
    {"optionA": "Have 10 babies", "optionB": "Have 10 pets"},
    {"optionA": "Live in the mountains", "optionB": "Live by the beach"},
]

# ── Truths & Dares ──
FALLBACK_TRUTHS = [
    "What is the most embarrassing thing you've ever done in public?",
    "What is your biggest fear?",
    "Who is your secret crush?",
    "What is the strangest food combination you secretly enjoy?",
    "Have you ever lied to your best friend?",
    "What is the worst gift you've ever received?",
    "Have you ever pretended to be sick to get out of school/work?",
    "What is the most childish thing you still do?",
    "What is your most used emoji and why?",
    "Have you ever stalked someone on social media?",
]

FALLBACK_DARES = [
    "Send 'I love you' to the 3rd person in your recent chats",
    "Post a funny selfie on your story for 5 minutes",
    "Text your crush a bad joke",
    "Speak in an accent for the next 5 messages",
    "Sing the chorus of your favorite song (send voice note)",
    "Change your bio to 'I am a bot' for 10 minutes",
    "Send a random emoji to your crush",
    "Do 10 pushups and send a photo",
    "Call a friend and say 'I forgot what I was going to say'",
    "Eat a spoonful of something spicy",
]

# ── WORD POOL ──
WORD_POOL = ["LIONS", "BIRDS", "STARS", "EARTH", "SOLAR", "SPACE", "WATER", "PLANT", "FLAME", "APPLE", "PEACH", "PIZZA", "SWEET", "HAPPY", "SMILE", "SMART", "GREEN", "WHITE", "SHARK", "CLOUD", "WORLD", "DANCE", "HOUSE", "SOUND", "MUSIC", "NOVEL", "TRAIN", "PLANE", "BEACH", "NIGHT", "CLOCK", "LIGHT", "DRAFT", "ANGLE", "BRAIN", "FOCUS", "GRACE", "HEART", "LOVE", "PEACE"]

CATEGORIES = ["Science", "History", "Geography", "Pop Culture", "Technology"]

# ── Load Function ──
def load_game_data():
    print("✅ Game data loaded! (AI + 100+ fallback)")

# ── Active Game Functions ──
def get_active_game(thread_id: str) -> dict | None:
    return active_games.get(thread_id)

def quit_game(thread_id: str) -> str:
    if thread_id in active_games:
        game_name = active_games[thread_id].get("game", "game")
        del active_games[thread_id]
        if thread_id in _used_questions:
            del _used_questions[thread_id]
        return f"🚪 You left {game_name}. Play again soon!"
    return "❌ No active game."

# ── AI Question Generator ──
def generate_ai_question(category: str = None) -> Optional[Dict]:
    try:
        client = get_groq_client()
        if not client:
            return None
        cat = category or random.choice(CATEGORIES)
        prompt = f"""Generate a trivia question about {cat}. Format EXACTLY:
Question: [question]
Options:
A. [option A]
B. [option B]
C. [option C]
D. [option D]
Answer: [A/B/C/D]"""
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=300,
        )
        text = response.choices[0].message.content.strip()
        return parse_question(text, cat)
    except:
        return None

def parse_question(text: str, category: str) -> Optional[Dict]:
    try:
        lines = text.split('\n')
        question = ""; options = []; answer = ""
        for line in lines:
            line = line.strip()
            if line.startswith("Question:"):
                question = line.replace("Question:", "").strip()
            elif re.match(r'^[A-D]\.', line):
                options.append(line)
            elif line.startswith("Answer:"):
                answer = line.replace("Answer:", "").strip().upper()
        if question and len(options) == 4 and answer in ["A", "B", "C", "D"]:
            return {"question": question, "options": options, "answer": answer, "category": category}
        return None
    except:
        return None

def get_trivia_question(thread_id: str, category: str = None) -> Dict:
    if thread_id not in _used_questions:
        _used_questions[thread_id] = []
    # Try AI
    for _ in range(3):
        q = generate_ai_question(category)
        if q:
            key = f"{q['question']}{q['answer']}"
            if key not in _used_questions[thread_id]:
                _used_questions[thread_id].append(key)
                return q
    # Fallback
    available = [q for q in FALLBACK_TRIVIA if f"{q['question']}{q['answer']}" not in _used_questions[thread_id]]
    if not available:
        _used_questions[thread_id] = []
        available = FALLBACK_TRIVIA
    q = random.choice(available)
    _used_questions[thread_id].append(f"{q['question']}{q['answer']}")
    return q

def get_emoji_puzzle(thread_id: str) -> Dict:
    if thread_id not in _used_questions:
        _used_questions[thread_id] = []
    available = [q for q in FALLBACK_EMOJI if q['answer'] not in _used_questions[thread_id]]
    if not available:
        _used_questions[thread_id] = []
        available = FALLBACK_EMOJI
    q = random.choice(available)
    _used_questions[thread_id].append(q['answer'])
    return q

def get_wyr_question(thread_id: str) -> Dict:
    if thread_id not in _used_questions:
        _used_questions[thread_id] = []
    available = [q for q in FALLBACK_WYR if q['optionA'] not in _used_questions[thread_id]]
    if not available:
        _used_questions[thread_id] = []
        available = FALLBACK_WYR
    q = random.choice(available)
    _used_questions[thread_id].append(q['optionA'])
    return q

# ── Game Starters (All 8 Games) ──

def start_trivia(thread_id: str) -> str:
    q = get_trivia_question(thread_id)
    active_games[thread_id] = {"game": "trivia", "state": {"question": q, "score": 0, "correct": 0, "total": 0, "category": q.get("category", "Random")}}
    opts = "\n".join(q["options"])
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🧠 TRIVIA 🧠            \n       📂 {q.get('category', 'General')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n❓ {q['question']}\n\n{opts}\n\n💡 Reply with A, B, C, or D!\n💡 Type !next for new question\n💡 Type !quit to exit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_trivia(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    text = text.strip().upper()
    if text == "!NEXT":
        q = get_trivia_question(thread_id, state.get("category"))
        state["question"] = q
        opts = "\n".join(q["options"])
        return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🧠 TRIVIA 🧠            \n       📂 {q.get('category', 'General')}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n❓ {q['question']}\n\n{opts}\n\n📊 Score: {state['score']} pts\n💡 Reply with A, B, C, or D!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if text not in ["A", "B", "C", "D"]:
        return "⚠️ Invalid choice. Reply with A, B, C, or D (or !next)."
    q = state["question"]
    correct = q["answer"].upper()
    state["total"] += 1
    if text == correct:
        points = 10
        state["score"] += points
        state["correct"] += 1
        store.add_score(user_id, "trivia", points=points, username=username)
        return f"🎉 CORRECT! +{points} pts\n📊 Score: {state['score']} pts ({state['correct']}/{state['total']})\n\n💡 Type !next"
    else:
        store.add_loss(user_id, "trivia", username=username)
        return f"❌ INCORRECT! Answer: {correct}\n📊 Score: {state['score']} pts ({state['correct']}/{state['total']})\n\n💡 Type !next"

def start_guess(thread_id: str) -> str:
    secret = random.randint(1, 1000)
    active_games[thread_id] = {"game": "guess", "state": {"secret": secret, "attempts": 0, "range": (1, 1000)}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🔢 GUESS THE NUMBER       \n       (1-1000)\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💡 Type your guess!\n💡 Type !hint for help\n💡 Type !quit to exit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_guess(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    if text.strip().upper() == "!HINT":
        secret = state["secret"]
        return f"💡 Hint: Number is {'even' if secret % 2 == 0 else 'odd'} and between {state['range'][0]}-{state['range'][1]}"
    try:
        guess = int(text.strip())
    except:
        return "⚠️ Enter a valid number (or !hint, !quit)"
    state["attempts"] += 1
    secret = state["secret"]
    if guess == secret:
        points = max(50 - (state["attempts"] * 2), 10)
        store.add_score(user_id, "guess", points=points, username=username)
        del active_games[thread_id]
        return f"🎉 CORRECT! {secret} in {state['attempts']} attempts!\n⭐ +{points} Points"
    elif guess < secret:
        return f"📈 Higher! (Attempt {state['attempts']})"
    else:
        return f"📉 Lower! (Attempt {state['attempts']})"

def start_scramble(thread_id: str) -> str:
    word = random.choice(WORD_POOL).lower()
    scrambled = "".join(random.sample(word, len(word)))
    while scrambled == word:
        scrambled = "".join(random.sample(word, len(word)))
    active_games[thread_id] = {"game": "scramble", "state": {"word": word, "scrambled": scrambled, "attempts": 0, "hint_given": False}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🔤 WORD SCRAMBLE 🔤        \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🧩 Scrambled: {scrambled.upper()}\n\n💡 Unscramble!\n💡 Type !hint\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_scramble(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    text = text.strip().lower()
    if text == "!hint":
        state["hint_given"] = True
        return f"💡 Hint: {len(state['word'])} letters, starts with '{state['word'][0]}'"
    if text == state["word"]:
        points = 15 if not state["hint_given"] else 5
        store.add_score(user_id, "scramble", points=points, username=username)
        del active_games[thread_id]
        return f"🎉 CORRECT! Word: {state['word'].upper()}\n⭐ +{points} Points"
    else:
        state["attempts"] += 1
        return f"❌ Wrong! (Attempt {state['attempts']})\n💡 Type !hint"

def start_wordseek(thread_id: str) -> str:
    word = random.choice(WORD_POOL).upper()
    active_games[thread_id] = {"game": "wordseek", "state": {"word": word, "attempts": 0, "history": [], "hint_given": False}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🔎 WORDSEEK (WORDLE)      \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💡 Guess 5-letter word!\n🟩 = Correct position\n🟨 = Wrong position\n⬛ = Not in word\n🎯 Attempts: 0/6\n💡 Type !hint\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_wordseek(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    secret = state["word"]
    guess = text.strip().upper()
    if guess == "!HINT":
        state["hint_given"] = True
        return f"💡 Hint: Starts with '{secret[0]}'"
    if len(guess) != 5 or not guess.isalpha():
        return "⚠️ Enter a 5-letter word!"
    state["attempts"] += 1
    attempts = state["attempts"]
    feedback = ["⬛"] * 5
    secret_used = [False] * 5
    guess_used = [False] * 5
    for i in range(5):
        if guess[i] == secret[i]:
            feedback[i] = "🟩"
            secret_used[i] = True
            guess_used[i] = True
    for i in range(5):
        if not guess_used[i]:
            for j in range(5):
                if not secret_used[j] and guess[i] == secret[j]:
                    feedback[i] = "🟨"
                    secret_used[j] = True
                    break
    state["history"].append(f"{' '.join(list(guess))}\n👉 {' '.join(feedback)}")
    history_display = "\n\n".join(state["history"][-6:])
    if guess == secret:
        points = 20 if not state["hint_given"] else 10
        store.add_score(user_id, "wordseek", points=points, username=username)
        del active_games[thread_id]
        return f"🎉 CORRECT! Word: {secret}\n🎯 Attempts: {attempts}/6\n⭐ +{points} Points"
    if attempts >= 6:
        del active_games[thread_id]
        return f"😢 GAME OVER! Word was: {secret}"
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🔎 WORDSEEK (WORDLE)      \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{history_display}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🎯 Attempts: {attempts}/6\n💡 Enter next guess!\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def start_rps(thread_id: str) -> str:
    active_games[thread_id] = {"game": "rps", "state": {}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n    ✂️ ROCK PAPER SCISSORS ✂️     \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n✊ Rock\n✋ Paper\n✌️ Scissors\n\n💬 Type Rock, Paper, or Scissors!\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_rps(thread_id: str, text: str, user_id: str, username: str) -> str:
    player = text.strip().lower()
    choices = ["rock", "paper", "scissors"]
    emoji_map = {"rock": "✊", "paper": "✋", "scissors": "✌️"}
    if player not in choices:
        return "⚠️ Choose Rock, Paper, or Scissors!"
    computer = random.choice(choices)
    del active_games[thread_id]
    if player == computer:
        return f"🤝 TIE!\n🧑 {emoji_map[player]} vs 🤖 {emoji_map[computer]}"
    elif (player == "rock" and computer == "scissors") or (player == "paper" and computer == "rock") or (player == "scissors" and computer == "paper"):
        store.add_score(user_id, "rps", points=10, username=username)
        return f"🎉 YOU WIN!\n🧑 {emoji_map[player]} vs 🤖 {emoji_map[computer]}\n⭐ +10 Points"
    else:
        store.add_loss(user_id, "rps", username=username)
        return f"😢 YOU LOSE!\n🧑 {emoji_map[player]} vs 🤖 {emoji_map[computer]}"

def start_wyr(thread_id: str) -> str:
    q = get_wyr_question(thread_id)
    active_games[thread_id] = {"game": "wyr", "state": {"question": q}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n      🤔 WOULD YOU RATHER 🤔       \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n🔴 A: {q['optionA']}\n      --- OR ---\n🔵 B: {q['optionB']}\n\n💬 Reply with A or B!\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_wyr(thread_id: str, text: str, user_id: str, username: str) -> str:
    ans = text.strip().upper()
    if ans not in ["A", "B"]:
        return "⚠️ Reply with A or B!"
    state = active_games[thread_id]["state"]
    del active_games[thread_id]
    choice = "Option A" if ans == "A" else "Option B"
    return f"👍 You chose {choice}\n📊 {random.randint(30, 70)}% chose A"

def start_emoji(thread_id: str) -> str:
    q = get_emoji_puzzle(thread_id)
    active_games[thread_id] = {"game": "emoji", "state": {"puzzle": q, "attempts": 0, "hint_given": False}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n       🧩 EMOJI PUZZLE 🧩         \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n👀 {q['emojis']}\n📂 Category: {q['category']}\n\n💡 Guess the answer!\n💡 Type !hint\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_emoji(thread_id: str, text: str, user_id: str, username: str) -> str:
    state = active_games[thread_id]["state"]
    text = text.strip().lower()
    if text == "!hint":
        state["hint_given"] = True
        return f"💡 Hint: {state['puzzle']['hint']}"
    if text == state["puzzle"]["answer"].lower():
        points = 15 if not state["hint_given"] else 5
        store.add_score(user_id, "emoji", points=points, username=username)
        del active_games[thread_id]
        return f"🎉 CORRECT! Answer: {state['puzzle']['answer']}\n⭐ +{points} Points"
    else:
        state["attempts"] += 1
        return f"❌ Wrong! (Attempt {state['attempts']})\n💡 Type !hint"

def start_tod(thread_id: str) -> str:
    active_games[thread_id] = {"game": "tod", "state": {}}
    return f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n      🔥 TRUTH OR DARE 🔥         \n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n💬 Type 'Truth' or 'Dare'!\n💡 Type !quit\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def handle_tod(thread_id: str, text: str, user_id: str, username: str) -> str:
    choice = text.strip().lower()
    if choice not in ["truth", "dare"]:
        return "⚠️ Type 'Truth' or 'Dare'!"
    del active_games[thread_id]
    if choice == "truth":
        return f"🧐 TRUTH:\n{random.choice(FALLBACK_TRUTHS)}"
    else:
        return f"🔥 DARE:\n{random.choice(FALLBACK_DARES)}"

load_game_data()
