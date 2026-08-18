# ✨ AYAAN AI — Instagram Chatbot

> A feature-rich Instagram DM and group chatbot built with Python and `instagrapi`, with a provider-agnostic conversational AI engine.

## Overview

AYAAN AI preserves the existing games, utilities, media commands, reminders, profile tools, and voice features while adding a natural AI assistant. The AI engine supports OpenAI, Groq, and Gemini through a shared provider interface. The selected provider can be changed with configuration; the router and commands do not need to change.

## Installation

The project requires Python 3.11 or newer and an Instagram session ID. Install the declared dependencies from the repository root:

```bash
git clone https://github.com/ayaanpirjade/Insta-chat-bot.git
cd Insta-chat-bot
python3 -m pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` before starting the bot:

```bash
python3 maininstabot/server.py
```

The bot requires a valid Instagram session. Live Instagram behavior cannot be tested safely without the account owner’s private session and account access.

## AI Configuration

`AI_PROVIDER` selects the first provider attempted. `AI_FALLBACK_PROVIDERS` controls the optional fallback order. The providers use the same conversation engine and never expose credentials in user-facing replies.

| Variable | Purpose | Example |
|---|---|---|
| `AI_PROVIDER` | Primary provider: `openai`, `groq`, or `gemini` | `openai` |
| `AI_FALLBACK_PROVIDERS` | Comma-separated fallback providers | `groq,gemini` |
| `OPENAI_API_KEY` | OpenAI API credential | `...` |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `OPENAI_BASE_URL` | Optional OpenAI-compatible endpoint | `https://api.openai.com/v1` |
| `GROQ_API_KEY` | Optional Groq credential | `...` |
| `AI_MODEL` | Groq model name | `llama-3.1-8b-instant` |
| `GEMINI_API_KEY` | Optional Gemini credential | `...` |

## Personality, Memory, and Protection

Personality is configured rather than scattered through handlers. Supported values are `friendly`, `professional`, `funny`, `concise`, and `technical`. `AI_SYSTEM_PROMPT` can replace the generated system prompt, and `BOT_LANGUAGE` sets the default language instruction.

| Variable | Default | Purpose |
|---|---:|---|
| `BOT_NAME` | `AYAAN AI` | Display and personality name |
| `BOT_PERSONALITY` | `friendly` | Personality style |
| `BOT_LANGUAGE` | `en` | Default language code |
| `AI_SYSTEM_PROMPT` | Generated | Optional full system-prompt override |
| `MAX_HISTORY_MESSAGES` | `20` | Maximum stored messages per conversation |
| `AI_COOLDOWN_SECONDS` | `3` | Per-conversation AI cooldown |
| `MAX_AI_REQUESTS_PER_MINUTE` | `10` | Per-conversation rolling request limit |
| `GROUP_AI_MODE` | `false` | Retained for compatibility; ordinary group replies remain disabled |

Conversation memory is isolated by `thread_id:user_id`. It is bounded and can be cleared with `!resetai`, `!forget`, or `!clearchat`.

## AI Commands

All AI utilities use the same engine with task-specific prompts.

| Command | Description |
|---|---|
| `!ai <question>` | Ask the conversational assistant |
| `!ask <question>` | Alias for `!ai` |
| `!chat <message>` | Alias for `!ai` |
| `!chatgpt <question>` | Alias for `!ai` |
| `!summarize <text>` | Summarize text |
| `!translate <text>` | Translate text into the requested or configured language |
| `!rewrite <text>` | Rewrite text clearly while preserving meaning |
| `!caption <topic>` | Generate three Instagram caption options |
| `!explain <topic>` | Explain a topic simply with an example |
| `!resetai` | Clear the current conversation memory |
| `!forget` | Alias for `!resetai` |
| `!clearchat` | Alias for `!resetai` |
| `!speak <question>` | Shared AI reply converted into a voice note |

## DM and Group Behavior

In direct messages, ordinary text such as `hello`, `what is Python?`, or `write an Instagram caption` is answered naturally without a tag. In group chats, the bot replies only when its Instagram username is mentioned or when users say `AYAAN AI`; ordinary group messages and replies to previous bot messages are ignored. Explicit prefixed commands such as `!ai` continue to work in groups. `GROUP_AI_MODE` is retained for compatibility but does not enable automatic group replies.

Long replies are split at paragraph, sentence, or whitespace boundaries. The splitter is tested with short text, multiline content, Unicode and emoji, code blocks, and extremely long messages.

## Existing Features

The project retains the existing music, voice-note, text-to-speech, reel, audio, sticker, GIF, image-generation, repost, profile, group administration, games, utilities, leaderboard, daily reward, and reminder features. Use `!help`, `!games`, `!musiccmd`, `!reelcmd`, or `!utilscmd` inside Instagram to see the current menus.

Common commands include `!play`, `!vn`, `!tts`, `!reel`, `!audio`, `!generate`, `!profile`, `!joke`, `!fact`, `!quote`, `!roast`, `!calc`, `!weather`, `!trivia`, `!guess`, `!rps`, `!score`, `!top`, `!daily`, and `!remind`.

## Security

Never commit `.env`, API keys, Instagram session IDs, cookies, authentication tokens, session settings, generated user state, or Python cache files. These paths are ignored by `.gitignore`, and previously tracked runtime artifacts were removed from the repository index while remaining available locally for an existing installation. Rotate any credential that may have appeared in earlier Git history.

Runtime errors are logged with credential-like values redacted, while users receive friendly provider-failure messages. The bot does not add automation intended to evade Instagram detection or rate limits.

## Testing and Validation

Run the focused regression suite and syntax validation from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q maininstabot
git diff --check
```

The tests cover provider selection, fallback, bounded memory, memory isolation, cooldowns, rolling request limits, safe provider failures, command parsing, long-message splitting, and DM/group AI trigger behavior. Import validation also covers `config`, `ai`, `command_parser`, `text_utils`, and `router` with the declared dependencies installed.

## Troubleshooting

If the bot reports that `SESSION_ID` is missing, verify `.env` is in the repository root and that the session value is current. If AI replies fail, verify `AI_PROVIDER`, the selected provider key, model name, and network access; configure a fallback provider if desired. If a command is not recognized, use `!help` and confirm the command has not been disabled by the command-toggle system.

If Instagram login or media operations fail, inspect the sanitized console error, confirm the account session is valid, and avoid committing any generated session or cookie files.
