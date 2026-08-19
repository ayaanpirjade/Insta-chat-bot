#          ✨ AYAAN AI ✨
#        Provider-agnostic conversational AI engine

from __future__ import annotations

import logging
import os
import threading
import time
from collections import deque
from typing import Callable

import requests

import config

try:
    from groq import Groq
except ImportError:  # Optional dependency for installations using OpenAI only.
    Groq = None

try:
    import google.generativeai as genai
except ImportError:  # Optional dependency for installations using OpenAI/Groq.
    genai = None

logger = logging.getLogger(__name__)

_conversations: dict[str, list[dict[str, str]]] = {}
_usage: dict[str, deque[float]] = {}
_last_request: dict[str, float] = {}
_lock = threading.RLock()
_groq_client = None
_gemini_model = None
MAX_MESSAGE_CHARS = 4000

FRIENDLY_FAILURE = "⚠️ My AI services are unavailable right now. Please try again in a moment."
COOLDOWN_FAILURE = "⏳ I’m still processing recent AI requests. Please try again shortly."


def _safe_error(exc: Exception) -> str:
    """Return a log-safe error description without credentials or request bodies."""
    message = str(exc).replace("\n", " ")
    for secret in (config.OPENAI_API_KEY, config.GROQ_API_KEY, config.GEMINI_API_KEY, config.SESSION_ID):
        if secret:
            message = message.replace(secret, "[REDACTED]")
    return message[:300]


def _history_for(key: str) -> list[dict[str, str]]:
    with _lock:
        return list(_conversations.setdefault(key, []))


def _can_request(key: str) -> bool:
    now = time.monotonic()
    with _lock:
        last = _last_request.get(key)
        if last is not None and now - last < config.AI_COOLDOWN_SECONDS:
            return False
        timestamps = _usage.setdefault(key, deque())
        while timestamps and now - timestamps[0] >= 60:
            timestamps.popleft()
        if len(timestamps) >= config.MAX_AI_REQUESTS_PER_MINUTE:
            return False
        _last_request[key] = now
        timestamps.append(now)
        return True


def _save_history(key: str, user_message: str, reply: str) -> None:
    with _lock:
        history = _conversations.setdefault(key, [])
        history.extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": reply},
        ])
        max_messages = config.MAX_HISTORY_MESSAGES
        if len(history) > max_messages:
            del history[:-max_messages]


def _openai(user_message: str, history: list[dict[str, str]], system_prompt: str) -> str | None:
    if not config.OPENAI_API_KEY:
        return None
    response = requests.post(
        f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions",
        headers={
            "Authorization": f"Bearer {config.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": config.OPENAI_MODEL,
            "messages": [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}],
            "max_tokens": 700,
            "temperature": 0.75,
        },
        timeout=45,
    )
    response.raise_for_status()
    choices = response.json().get("choices") or []
    content = choices[0].get("message", {}).get("content", "") if choices else ""
    return content.strip() or None


def _get_groq_client():
    global _groq_client
    if Groq is None or not config.GROQ_API_KEY:
        return None
    if _groq_client is None:
        _groq_client = Groq(api_key=config.GROQ_API_KEY)
    return _groq_client


def _groq(user_message: str, history: list[dict[str, str]], system_prompt: str) -> str | None:
    client = _get_groq_client()
    if client is None:
        return None

    messages = [{"role": "system", "content": system_prompt}, *history, {"role": "user", "content": user_message}]
    models = [config.AI_MODEL]
    configured_models = [
        config.GROQ_FALLBACK_MODEL,
        *getattr(config, "GROQ_FALLBACK_MODELS", []),
    ]
    for model in configured_models:
        if model and model not in models:
            models.append(model)

    response = None
    for index, model in enumerate(models):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=700,
                temperature=0.75,
            )
            break
        except Exception as exc:
            error_text = str(exc).lower()
            model_unavailable = "model_not_found" in error_text or "does not exist" in error_text
            if not model_unavailable or index == len(models) - 1:
                raise
            next_model = models[index + 1]
            logger.warning("Groq model '%s' unavailable; trying fallback model '%s'", model, next_model)

    if response is not None:
        logger.info("Groq model responded: %s", models[index])
    content = response.choices[0].message.content if response and response.choices else ""
    return (content or "").strip() or None


def _get_gemini_model():
    global _gemini_model
    if genai is None or not config.GEMINI_API_KEY:
        return None
    if _gemini_model is None:
        genai.configure(api_key=config.GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    return _gemini_model


def _gemini(user_message: str, history: list[dict[str, str]], system_prompt: str) -> str | None:
    model = _get_gemini_model()
    if model is None:
        return None
    context = "\n".join(f"{h['role'].title()}: {h['content']}" for h in history)
    prompt = f"{system_prompt}\n\nPrevious conversation:\n{context}\n\nUser: {user_message}\nAssistant:"
    response = model.generate_content(prompt)
    return (getattr(response, "text", "") or "").strip() or None


PROVIDERS: dict[str, Callable[[str, list[dict[str, str]], str], str | None]] = {
    "openai": _openai,
    "groq": _groq,
    "gemini": _gemini,
}


def _provider_order() -> list[str]:
    selected = config.AI_PROVIDER if config.AI_PROVIDER in PROVIDERS else "openai"
    configured_fallbacks = [
        item.strip().lower()
        for item in os.getenv("AI_FALLBACK_PROVIDERS", "groq,gemini").split(",")
        if item.strip().lower() in PROVIDERS and item.strip().lower() != selected
    ]
    return [selected, *configured_fallbacks]


def ask_ai(
    user_message: str,
    user_id: str = "default",
    conversation_id: str | None = None,
    system_prompt: str | None = None,
    use_memory: bool = True,
) -> str:
    """Ask the selected provider with safe fallback and isolated bounded memory."""
    user_message = (user_message or "").strip()[:MAX_MESSAGE_CHARS]
    if not user_message:
        return "Please send a question or message for me to answer."
    key = conversation_id or user_id
    if not _can_request(key):
        return COOLDOWN_FAILURE
    history = _history_for(key) if use_memory else []
    prompt = system_prompt or config.BOT_SYSTEM_PROMPT

    for provider_name in _provider_order():
        try:
            reply = PROVIDERS[provider_name](user_message, history, prompt)
            if reply:
                if use_memory:
                    _save_history(key, user_message, reply)
                logger.info("AI provider responded: %s", provider_name)
                return reply
        except Exception as exc:
            logger.warning("AI provider %s failed: %s", provider_name, _safe_error(exc))

    logger.error("All configured AI providers failed or are unavailable")
    return FRIENDLY_FAILURE


def ask_task(task: str, text: str, user_id: str, conversation_id: str) -> str:
    """Run a reusable one-shot AI utility through the same provider engine."""
    prompt = f"{config.BOT_SYSTEM_PROMPT}\nTask mode: {task}. Follow the task exactly and return only the useful result."
    return ask_ai(text, user_id=user_id, conversation_id=conversation_id, system_prompt=prompt, use_memory=False)


def clear_history(conversation_id: str) -> str:
    with _lock:
        _conversations.pop(conversation_id, None)
    return "🧹 Chat memory cleared. Fresh start! ✨"


def reset_runtime_state() -> None:
    """Clear in-memory state for deterministic tests and controlled restarts."""
    with _lock:
        _conversations.clear()
        _usage.clear()
        _last_request.clear()
