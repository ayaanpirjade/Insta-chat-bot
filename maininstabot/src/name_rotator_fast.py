"""ULTRA-FAST name rotation using direct Instagram API calls - SHARED CLIENT"""
import time
import random
import threading
import re
from typing import Dict, Optional

EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
MIN_DELAY = 0.002  # 2ms - ULTRA FAST!
_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}
_shared_client = None  # Shared client across all rotations
_client_lock = threading.Lock()

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

def get_shared_client():
    """Get or create a shared client instance"""
    global _shared_client
    with _client_lock:
        if _shared_client is None:
            try:
                from .session_manager import RotatingSessionManager
                session_manager = RotatingSessionManager()
                client, _ = session_manager.get_client()
                _shared_client = client
                print("  ✅ Created shared client for name rotation")
            except Exception as e:
                print(f"  ❌ Failed to create shared client: {e}")
                return None
        return _shared_client

def start(query: str, thread_id: str, cl=None) -> str:
    """Start ultra-fast name rotation using shared client"""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 5:
        return "⏳ Duration must be at least 5 seconds."
    if duration > 3600:
        return "⏳ Duration cannot exceed 60 minutes."

    # Stop previous rotation
    stop(str(thread_id))

    # Get shared client once
    client = get_shared_client()
    if not client:
        return "❌ Failed to create Instagram client. Check your session."

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    def worker():
        deadline = time.time() + duration
        used_names = set()
        update_count = 0
        start_time = time.time()
        
        # Use the shared client
        local_client = get_shared_client()
        if not local_client:
            print("  ❌ No client available")
            return
        
        print(f"  ⚡ Starting ultra-fast rotation (2ms speed)")
        
        while not event.is_set() and time.time() < deadline:
            try:
                emoji = random.choice(EMOJIS)
                name = f"{base_name[:95]} {emoji}"
                
                # Avoid exact duplicates
                if name in used_names:
                    name = f"{name} {random.randint(1,99)}"
                used_names.add(name)
                if len(used_names) > 500:
                    used_names.clear()
                
                # Change group name using shared client
                local_client.direct_thread_update_title(int(thread_id), name)
                update_count += 1
                
                # Print progress every 100 updates
                if update_count % 100 == 0:
                    elapsed = time.time() - start_time
                    speed = update_count / elapsed if elapsed > 0 else 0
                    print(f"  ⚡ Update #{update_count} ({speed:.0f}/sec): {name}")
                
                # ULTRA-FAST delay
                time.sleep(MIN_DELAY)
                
            except Exception as e:
                error = str(e).lower()
                if "rate" in error or "limit" in error or "429" in error:
                    print(f"  ⚠️ Rate limit hit, waiting 1s...")
                    time.sleep(1)
                else:
                    print(f"  ⚠️ Error: {e}")
                    time.sleep(0.1)
        
        # Cleanup
        _stop_events.pop(key, None)
        _threads.pop(key, None)
        elapsed = time.time() - start_time
        speed = update_count / elapsed if elapsed > 0 else 0
        print(f"  ✅ Rotation stopped after {update_count} updates in {elapsed:.1f}s ({speed:.0f}/sec)")

    thread = threading.Thread(target=worker, daemon=True)
    _threads[key] = thread
    thread.start()

    return f"⚡ ULTRA-FAST rotation started for {duration_text} with '{base_name}' (2ms speed). Use !ncstop to stop."

# Force client refresh if needed
def refresh_client():
    global _shared_client
    with _client_lock:
        _shared_client = None
        print("  🔄 Client refreshed for name rotation")