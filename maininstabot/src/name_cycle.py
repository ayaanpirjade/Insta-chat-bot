"""Bounded group-name rotation for the Instagram bot.

This module deliberately uses a conservative interval and requires an explicit
stop command. It does not contain preset group names or session credentials.
"""

import random
import re
import threading
import time
from typing import Dict, Optional


MIN_DELAY_SECONDS = 30.0
MAX_DURATION_SECONDS = 3600.0
EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}


def parse_duration(value: str) -> Optional[float]:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)?", value.strip().lower())
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or "s"
    return amount * {"s": 1, "m": 60, "h": 3600}[unit]


def stop(thread_id: str) -> bool:
    key = str(thread_id)
    event = _stop_events.pop(key, None)
    thread = _threads.pop(key, None)
    if event is None:
        return False
    event.set()
    return thread is not None and thread.is_alive()


def stop_command(thread_id: str) -> str:
    return "🛑 Group-name rotation stopped." if stop(thread_id) else "ℹ️ No active group-name rotation in this group."


def _safe_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "1545037" in text or "403" in text or "permission" in text or "admin" in text:
        return "Instagram rejected the title update; the account or group may not allow this action."
    return "The group-name update failed. Check the bot log for the local error."


def start(query: str, thread_id: str, client) -> str:
    """Start a bounded rotation using the name and duration supplied by the user."""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <group name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <group name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < MIN_DELAY_SECONDS:
        return "⏳ Duration must be at least 30 seconds."
    if duration > MAX_DURATION_SECONDS:
        return "⏳ Duration cannot exceed 60 minutes."

    stop(str(thread_id))
    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    def worker() -> None:
        deadline = time.monotonic() + duration
        try:
            while not event.is_set() and time.monotonic() < deadline:
                title = f"{base_name[:95]} {random.choice(EMOJIS)}"
                updater = getattr(client, "direct_thread_update_title", None)
                if not callable(updater):
                    raise RuntimeError("The installed Instagram client has no group-title method")
                if updater(int(thread_id), title) is False:
                    raise RuntimeError("Instagram rejected the group-title update")
                remaining = max(0.0, deadline - time.monotonic())
                event.wait(min(MIN_DELAY_SECONDS, remaining))
        except Exception as exc:
            print(f"  ⚠️ Name rotation stopped: {_safe_error(exc)}")
        finally:
            _stop_events.pop(key, None)
            _threads.pop(key, None)

    thread = threading.Thread(target=worker, name=f"name-cycle-{key}", daemon=True)
    _threads[key] = thread
    thread.start()
    return f"🔄 Group-name rotation started for {duration_text}. Updates every 30 seconds. Use !ncstop to stop it."
