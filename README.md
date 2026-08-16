# ✨ AYAAN AI — Instagram Chatbot

> A feature-rich, multi-purpose Instagram DM/Group chatbot built with Python and instagrapi.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Instagram](https://img.shields.io/badge/Instagram-API-purple.svg)](https://instagram.com)

---

## 🚀 Features

| Command | Description |
|---------|-------------|
| `!play <song>` | Send music sticker |
| `!vn <song>` | Voice note from YouTube |
| `!tts <text>` | Text to speech voice note |
| `!speak <question>` | AI reply + voice note |
| `!reel <link>` | Download & send reel video |
| `!audio <link>` | Extract audio from reel |
| `!sticker <category>` | Send native Instagram sticker |
| `!gif <query>` | Send native GIF |
| `!help` | Show full menu |
| `!games` | Show games menu |
| `!ping` | Check bot status |
| `!info` | Bot info |
| `!joke` | Random joke |
| `!fact` | Random fact |
| `!quote` | Random quote |
| `!roast @user` | Roast someone |
| `!8ball <question>` | Magic 8-ball |
| `!roll` | Roll dice |
| `!flip` | Flip coin |
| `!meme` | Text meme |
| `!calc <expr>` | Calculator |
| `!time` | Current time |
| `!weather <city>` | Weather forecast |
| `!stalk @user` | Instagram profile info |
| `!horoscope <sign>` | Daily horoscope |
| `!choose <options>` | Choose randomly |
| `!trivia` | Trivia game |
| `!guess` | Guess number game |
| `!scramble` | Word scramble |
| `!wordseek` | Wordle game |
| `!rps` | Rock Paper Scissors |
| `!wyr` | Would You Rather |
| `!emoji` | Emoji game |
| `!tod` | Truth or Dare |
| `!score` | Your stats |
| `!top` | Leaderboard |
| `!daily` | Daily bonus |
| `!remind` | Set reminder |

---

## 🎭 Voice Commands

| Command | Description |
|---------|-------------|
| `!avoice <num> <text>` | Anime character voice |
| `!amultivoice <nums> <text>` | Multiple anime characters |
| `!avoices` | List all voices |

### Available Anime Voices

| # | Name | Style |
|---|------|-------|
| 1 | Urokodaki | Deep masculine |
| 2 | Kanae | Soft feminine |
| 3 | Uppermoon | Dark creepy |
| 4 | Tanjiro | Heroic |
| 5 | Nezuko | Cute |
| 6 | Zenitsu | Scared whiny |
| 7 | Inosuke | Wild aggressive |
| 8 | Muzan | Evil calm |
| 9 | Shinobu | Gentle deadly |
| 10 | Giyu | Silent serious |

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Instagram Session ID
- Groq API Key (optional)
- ElevenLabs API Key (optional)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ayaan-ai-bot.git
cd ayaan-ai-bot
```

## ChatGPT Conversation

The bot now supports a direct ChatGPT conversation flow. In a direct message, ordinary text is answered by the AI automatically. In a group chat, mention the bot or use a prefixed command so the bot does not interrupt unrelated conversations.

| Command | Description |
|---------|-------------|
| `!ai <question>` | Ask ChatGPT anything from a DM or group chat |
| `!chat <question>` | Alias for `!ai` |
| `!chatgpt <question>` | Alias for `!ai` |
| `!resetai` | Clear conversation memory for the current chat and user |

Set `OPENAI_API_KEY` in your `.env` file to enable ChatGPT. The default model is `gpt-4o-mini`, and it can be changed with `OPENAI_MODEL`. ChatGPT is attempted first; the existing Groq and Gemini integrations remain available as fallbacks when their keys are configured. Conversation history is scoped to the current Instagram thread and user, and long answers are split into readable messages before delivery.

### Environment Setup

Copy the template and fill in your credentials:

```bash
cp .env.example .env
```

Never commit `.env`, Instagram session data, cookies, or private user files. The repository now ignores newly generated local secrets and Python cache files.

### Examples

```text
!ai explain recursion with a simple example
!chat write a friendly caption for my travel photo
!resetai
```

When a user sends `@BOT_USERNAME what should I learn today?` in a group, the bot removes its mention and sends the remaining question to ChatGPT.
