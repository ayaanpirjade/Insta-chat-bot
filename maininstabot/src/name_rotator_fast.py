"""LIGHTNING FAST - Single Account, Single Login, Ultra-Fast"""
import time
import random
import threading
import re
from typing import Dict, Optional

EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}
_shared_client = None
_client_lock = threading.Lock()

def parse_duration(value: str) -> Optional[float]:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)?", value.strip().lower())
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or "s"
    return amount * {"s": 1, "m": 60, "h": 3600}[unit]

def get_client():
    """Get shared client - SINGLE LOGIN ONLY"""
    global _shared_client
    with _client_lock:
        if _shared_client is None:
            try:
                from .session_manager import RotatingSessionManager
                sm = RotatingSessionManager()
                client, _ = sm.get_client()
                _shared_client = client
                print("  ✅ Shared client created (single login)")
            except Exception as e:
                print(f"  ❌ Failed to create client: {e}")
                return None
        return _shared_client

def stop(thread_id: str) -> bool:
    key = str(thread_id)
    event = _stop_events.pop(key, None)
    thread = _threads.pop(key, None)
    if event is None:
        return False
    event.set()
    if thread and thread.is_alive():
        thread.join(timeout=1)
    return True

def stop_command(thread_id: str) -> str:
    return "🛑 Rotation stopped." if stop(thread_id) else "ℹ️ No active rotation."

def rename_worker(thread_id: str, base_name: str, stop_event: threading.Event, worker_id: int, duration: float):
    """Single worker - FAST and RELIABLE with rate limit handling"""
    client = get_client()
    if not client:
        return

    used_names = set()
    count = 0
    errors = 0
    start_time = time.time()
    deadline = start_time + duration
    rate_limit_wait = 0

    print(f"  🔥 Worker {worker_id} started")

    while not stop_event.is_set() and time.time() < deadline:
        try:
            # If rate limited, wait
            if rate_limit_wait > 0:
                time.sleep(rate_limit_wait)
                rate_limit_wait = 0
                continue

            # Generate unique name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 100:
                used_names.clear()

            # DIRECT API CALL
            client.direct_thread_update_title(int(thread_id), name)
            count += 1
            errors = 0

            # Print speed every 50 updates
            if count % 50 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed if elapsed > 0 else 0
                print(f"  ⚡ Worker {worker_id}: {count} updates ({speed:.0f}/sec)")

            # ULTRA-FAST delay (1ms)
            time.sleep(0.001)

        except Exception as e:
            errors += 1
            error_str = str(e).lower()

            if "403" in error_str or "rate" in error_str or "limit" in error_str:
                rate_limit_wait = 2.0  # Wait 2 seconds
                print(f"  ⚠️ Worker {worker_id}: Rate limit, waiting...")
            elif "login" in error_str or "session" in error_str:
                # Refresh session
                with _client_lock:
                    global _shared_client
                    _shared_client = None
                    client = get_client()
                    if not client:
                        break
            else:
                if errors % 5 == 0:
                    print(f"  ⚠️ Worker {worker_id} error: {str(e)[:50]}")
                time.sleep(0.01)

    elapsed = time.time() - start_time
    speed = count / elapsed if elapsed > 0 else 0
    print(f"  ✅ Worker {worker_id}: {count} updates ({speed:.0f}/sec)")

def start(query: str, thread_id: str, cl=None) -> str:
    """Start lightning-fast rotation"""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 5:
        return "⏳ Duration must be at least 5 seconds."

    # Stop previous rotation
    stop(str(thread_id))

    # Create shared client ONCE
    client = get_client()
    if not client:
        return "❌ Failed to create Instagram client"

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    # Start workers (10 is optimal to avoid rate limits)
    num_workers = 10
    threads = []
    for i in range(num_workers):
        t = threading.Thread(
            target=rename_worker,
            args=(thread_id, base_name, event, i+1, duration),
            daemon=True
        )
        t.start()
        threads.append(t)

    # Store main thread for stop command
    def monitor():
        for t in threads:
            t.join()
        _stop_events.pop(key, None)
        _threads.pop(key, None)

    monitor_thread = threading.Thread(target=monitor, daemon=True)
    _threads[key] = monitor_thread
    monitor_thread.start()

    return f"⚡ LIGHTNING FAST: {num_workers} workers, 1ms delay! Use !ncstop to stop."

def clean_up():
    """Clean up"""
    for key in list(_stop_events.keys()):
        stop(key)