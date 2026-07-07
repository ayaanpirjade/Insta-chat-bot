import os
import json

# Ensure data directory exists
os.makedirs("d:/insta ai bot/data", exist_ok=True)

# 1. Jokes
jokes = [
    {"setup": "Why don't scientists trust atoms?", "punchline": "Because they make up everything! 😂", "category": "science"},
    {"setup": "Why did the scarecrow win an award?", "punchline": "Because he was outstanding in his field! 🌾", "category": "dad"},
    {"setup": "I told my wife she was drawing her eyebrows too high.", "punchline": "She looked surprised. 😳", "category": "dad"},
    {"setup": "Why can't you give Elsa a balloon?", "punchline": "Because she'll let it go! 🎈", "category": "pun"},
    {"setup": "What do you call a fake noodle?", "punchline": "An impasta! 🍝", "category": "pun"},
    {"setup": "Why did the bicycle fall over?", "punchline": "Because it was two-tired! 🚲", "category": "dad"},
    {"setup": "What do you call cheese that isn't yours?", "punchline": "Nacho cheese! 🧀", "category": "pun"},
    {"setup": "I'm reading a book about anti-gravity.", "punchline": "It's impossible to put down! 📚", "category": "science"},
    {"setup": "Why did the math book look so sad?", "punchline": "Because it had too many problems! 📖", "category": "tech"},
    {"setup": "What is an astronaut's favorite key on a keyboard?", "punchline": "The space bar! 🚀", "category": "tech"},
    {"setup": "Why did the computer go to the doctor?", "punchline": "Because it had a virus! 💻", "category": "tech"},
    {"setup": "How many programmers does it take to change a light bulb?", "punchline": "None, that's a hardware problem! 💡", "category": "tech"},
    {"setup": "Why do programmers wear glasses?", "punchline": "Because they can't C#! 🤓", "category": "tech"},
    {"setup": "What is a database administrator's favorite song?", "punchline": "No SQL, No Cry. 🎵", "category": "tech"}
]
with open("d:/insta ai bot/data/jokes.json", "w", encoding="utf-8") as f:
    json.dump(jokes, f, indent=2, ensure_ascii=False)

# 2. Facts
facts = [
    "🧠 Honey never spoils. Edible honey was found in 3000-year-old Egyptian tombs!",
    "🐙 Octopuses have three hearts and blue blood!",
    "🌍 A day on Venus is longer than a year on Venus.",
    "🦈 Sharks are older than trees — around for 450 million years!",
    "🍫 It takes 400 cocoa beans to make one pound of chocolate.",
    "🐝 Bees can recognize human faces.",
    "🌙 The moon drifts away from Earth by 3.8cm every year.",
    "🦦 Sea otters hold hands while sleeping so they don't drift apart. 🥹",
    "🐘 Elephants are the only animals that can't jump.",
    "🍌 Bananas are berries, but strawberries aren't!",
    "🍍 Pineapples take almost three years to grow and mature.",
    "🥑 Avocados are fruits, not vegetables. They are technically single-seeded berries.",
    "🦩 Flamingos are pink because of the shrimp and algae they eat.",
    "🐧 Gentoo penguins propose to their lifepars with a pebble.",
    "🐨 Koalas have unique fingerprints, just like humans!",
    "🐈 Cats have fewer toes on their back paws than their front paws."
]
with open("d:/insta ai bot/data/facts.json", "w", encoding="utf-8") as f:
    json.dump(facts, f, indent=2, ensure_ascii=False)

# 3. Quotes
quotes = [
    {"quote": "The only way to do great work is to love what you do.", "author": "Steve Jobs", "category": "success"},
    {"quote": "Life is what happens when you're busy making other plans.", "author": "John Lennon", "category": "life"},
    {"quote": "The mind is everything. What you think you become.", "author": "Buddha", "category": "wisdom"},
    {"quote": "It is during our darkest moments that we must focus to see the light.", "author": "Aristotle", "category": "wisdom"},
    {"quote": "The only thing we have to fear is fear itself.", "author": "Franklin D. Roosevelt", "category": "life"},
    {"quote": "Be yourself; everyone else is already taken.", "author": "Oscar Wilde", "category": "life"},
    {"quote": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein", "category": "motivation"},
    {"quote": "Your time is limited, don't waste it living someone else's life.", "author": "Steve Jobs", "category": "success"},
    {"quote": "I have not failed. I've just found 10,000 ways that won't work.", "author": "Thomas A. Edison", "category": "motivation"},
    {"quote": "Whether you think you can or think you can't, you're right.", "author": "Henry Ford", "category": "success"}
]
with open("d:/insta ai bot/data/quotes.json", "w", encoding="utf-8") as f:
    json.dump(quotes, f, indent=2, ensure_ascii=False)

# 4. Roasts
roasts = [
    "You're the reason they put instructions on shampoo bottles. 💀",
    "I'd roast you harder but my mom said I'm not allowed to burn trash. 🔥",
    "You're not stupid, you just have bad luck thinking. 😬",
    "I've seen better heads on a cauliflower. 🥦",
    "You're like a cloud — when you disappear, it's a beautiful day. ☀️",
    "If laughter is the best medicine, your face must be curing diseases. 💊",
    "You're not completely useless — you can always serve as a bad example. 😅",
    "I'd agree with you but then we'd both be wrong. 🤷",
    "Light travels faster than sound. This is why some people appear bright until you hear them speak. ⚡",
    "You possess a mind like a steel trap: always closed. 🚪",
    "I'm not saying you're slow, but you make snails look like drag racers. 🐌"
]
with open("d:/insta ai bot/data/roasts.json", "w", encoding="utf-8") as f:
    json.dump(roasts, f, indent=2, ensure_ascii=False)

# 5. 8ball
eight_ball = [
    "It is certain ✅", "Without a doubt ✅", "Yes, definitely ✅",
    "You may rely on it ✅", "Most likely ✅",
    "Reply hazy, try again 🤔", "Ask again later 🤔", "Cannot predict now 🤔",
    "Don't count on it ❌", "My reply is no ❌", "Very doubtful ❌"
]
with open("d:/insta ai bot/data/8ball.json", "w", encoding="utf-8") as f:
    json.dump(eight_ball, f, indent=2, ensure_ascii=False)

# 6. Trivia
trivia = [
    {"question": "What is the capital of France?", "options": ["A. London", "B. Berlin", "C. Paris", "D. Rome"], "answer": "C", "category": "geography"},
    {"question": "Which planet is known as the Red Planet?", "options": ["A. Earth", "B. Mars", "C. Jupiter", "D. Saturn"], "answer": "B", "category": "science"},
    {"question": "What is the largest ocean on Earth?", "options": ["A. Atlantic Ocean", "B. Indian Ocean", "C. Arctic Ocean", "D. Pacific Ocean"], "answer": "D", "category": "geography"},
    {"question": "Who painted the Mona Lisa?", "options": ["A. Vincent van Gogh", "B. Pablo Picasso", "C. Leonardo da Vinci", "D. Michelangelo"], "answer": "C", "category": "pop_culture"},
    {"question": "What is the chemical symbol for gold?", "options": ["A. Go", "B. Gd", "C. Au", "D. Ag"], "answer": "C", "category": "science"},
    {"question": "Which gas do plants absorb from the atmosphere?", "options": ["A. Oxygen", "B. Nitrogen", "C. Carbon Dioxide", "D. Hydrogen"], "answer": "C", "category": "science"},
    {"question": "In what year did World War II end?", "options": ["A. 1918", "B. 1939", "C. 1945", "D. 1950"], "answer": "C", "category": "history"},
    {"question": "What is the fastest land animal?", "options": ["A. Lion", "B. Cheetah", "C. Leopard", "D. Gazelle"], "answer": "B", "category": "science"}
]
with open("d:/insta ai bot/data/trivia.json", "w", encoding="utf-8") as f:
    json.dump(trivia, f, indent=2, ensure_ascii=False)

# 7. Would You Rather
would_you_rather = [
    {"optionA": "Always have to sing instead of speaking", "optionB": "Always have to dance everywhere you go"},
    {"optionA": "Be able to fly but only at a speed of 2 mph", "optionB": "Be able to teleport but only to places you've been in the last 24 hours"},
    {"optionA": "Read minds but everyone can read yours too", "optionB": "Never be able to read minds but always know when someone is lying"},
    {"optionA": "Live without music", "optionB": "Live without movies"},
    {"optionA": "Always be 15 minutes late", "optionB": "Always be 25 minutes early"},
    {"optionA": "Have unlimited money but no friends", "optionB": "Have unlimited friends but no money"}
]
with open("d:/insta ai bot/data/wouldYouRather.json", "w", encoding="utf-8") as f:
    json.dump(would_you_rather, f, indent=2, ensure_ascii=False)

# 8. Emoji Puzzles
emoji_puzzles = [
    {"emojis": "🦁👑", "answer": "The Lion King", "hint": "A Disney animated movie about a young lion prince.", "category": "movie"},
    {"emojis": "🕷️🙋‍♂️", "answer": "Spider-Man", "hint": "A superhero movie about a boy bitten by a spider.", "category": "movie"},
    {"emojis": "❄️🙋‍♀️", "answer": "Frozen", "hint": "A Disney movie about two sisters, one of whom has ice powers.", "category": "movie"},
    {"emojis": "🚢🏔️💔", "answer": "Titanic", "hint": "A famous romantic tragedy set on a ship.", "category": "movie"},
    {"emojis": "🦖🏜️🌳", "answer": "Jurassic Park", "hint": "A movie about cloned dinosaurs running wild.", "category": "movie"},
    {"emojis": "🦇🙋‍♂️🏙️", "answer": "Batman", "hint": "A hero who protects Gotham City.", "category": "movie"}
]
with open("d:/insta ai bot/data/emojiPuzzles.json", "w", encoding="utf-8") as f:
    json.dump(emoji_puzzles, f, indent=2, ensure_ascii=False)

# 9. Truth or Dare
truth_or_dare = {
    "truths": [
        "What is the most embarrassing thing you've ever done in public?",
        "Have you ever lied about your age to get into something?",
        "What is your biggest fear?",
        "Who is your secret crush?",
        "What is the strangest food combination you secretly enjoy?",
        "What is the worst gift you have ever received?",
        "Have you ever pretended to be sick to get out of school/work?"
    ],
    "dares": [
        "Send a message saying 'I love you' to the third person in your recent chats.",
        "Post a funny selfie with a weird caption on your story for 5 minutes.",
        "Text your crush and tell them a bad joke.",
        "Talk in an accent of the bot's choice for the next 5 messages.",
        "Sing the chorus of your favorite song and send a voice note (if possible).",
        "Change your bio to 'I am a bot helper' for 10 minutes."
    ]
}
with open("d:/insta ai bot/data/truthOrDare.json", "w", encoding="utf-8") as f:
    json.dump(truth_or_dare, f, indent=2, ensure_ascii=False)

# 10. Horoscope
horoscope = {
    "aries": [
        "Today is a great day to start new projects! Your energy levels are high. 🚀",
        "Be patient. Good things take time, Aries. Keep grinding!"
    ],
    "taurus": [
        "Financial gains are on the horizon. Stay focused on your goals! 💼",
        "Take a moment to relax today. You've been working hard."
    ],
    "gemini": [
        "Your communication skills are peak today. Speak your mind! 🗣️",
        "A surprise encounter might brighten your day. Keep your eyes open."
    ],
    "cancer": [
        "Trust your intuition. It will guide you to make the right choice today. 🔮",
        "Spend time with family or close friends. You need that warmth."
    ],
    "leo": [
        "You are shining bright today! Grab the spotlight and show them what you got. 🌟",
        "Remember to stay humble, Leo. Leadership requires listening."
    ],
    "virgo": [
        "Organize your workspace. A tidy desk brings a tidy mind today. 📐",
        "Don't overthink everything. Sometimes you just need to let go."
    ],
    "libra": [
        "Balance is key today. Take equal time for work and play. ⚖️",
        "A creative breakthrough is coming. Keep brainstorming!"
    ],
    "scorpio": [
        "Your passion is intense today. Focus it on something productive. 🔥",
        "A secret might be revealed. Stay observant."
    ],
    "sagittarius": [
        "Adventure awaits! Even if it is just a walk in a new neighborhood. 🗺️",
        "Keep your optimism high, it is contagious to others."
    ],
    "capricorn": [
        "Hard work will pay off sooner than you think. Stay disciplined! 📈",
        "Take some time to appreciate how far you've come."
    ],
    "aquarius": [
        "Your unique ideas are your superpower today. Share them with the world. 💡",
        "Connect with a friend you haven't spoken to in a while."
    ],
    "pisces": [
        "Your dreams are vivid and creative. Express them through art or writing. 🎨",
        "Go with the flow today. Don't fight things out of your control."
    ]
}
with open("d:/insta ai bot/data/horoscope.json", "w", encoding="utf-8") as f:
    json.dump(horoscope, f, indent=2, ensure_ascii=False)

print("Data files generated successfully!")
