"""ULTRA-FAST name rotation using direct Instagram API calls"""
import time
import random
import threading
import re
from typing import Dict, Optional

EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
MIN_DELAY = 0.05  # 50ms between changes (fast enough, but respects API limits)
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
    return "🛑 Rotation stopped." if stop(thread_id) else "ℹ️ No active rotation."

def start(query: str, thread_id: str, cl=None) -> str:
    """Start ultra-fast name rotation using direct API calls"""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 10:
        return "⏳ Duration must be at least 10 seconds."
    if duration > 3600:
        return "⏳ Duration cannot exceed 60 minutes."

    # Stop previous rotation
    stop(str(thread_id))

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    def worker():
        deadline = time.time() + duration
        used_names = set()
        update_count = 0
        
        while not event.is_set() and time.time() < deadline:
            try:
                # Import here to avoid circular imports
                from .session_manager import RotatingSessionManager
                session_manager = RotatingSessionManager()
                client, _ = session_manager.get_client()
                
                emoji = random.choice(EMOJIS)
                name = f"{base_name[:95]} {emoji}"
                
                # Avoid exact duplicates
                if name in used_names:
                    name = f"{name} {random.randint(1,99)}"
                used_names.add(name)
                if len(used_names) > 500:
                    used_names.clear()
                
                # Change group name using instagrapi
                client.direct_thread_update_title(int(thread_id), name)
                update_count += 1
                
                # Print progress every 10 updates
                if update_count % 10 == 0:
                    print(f"  ⚡ Update #{update_count}: {name}")
                
                # Ultra-fast delay
                time.sleep(MIN_DELAY)
                
            except Exception as e:
                print(f"  ⚠️ Rotation error: {e}")
                time.sleep(0.5)  # Brief backoff on error
        
        # Cleanup
        _stop_events.pop(key, None)
        _threads.pop(key, None)
        print(f"  ✅ Rotation stopped after {update_count} updates")

    thread = threading.Thread(target=worker, daemon=True)
    _threads[key] = thread
    thread.start()

    return f"⚡ ULTRA-FAST rotation started for {duration_text} with '{base_name}'. Use !ncstop to stop."