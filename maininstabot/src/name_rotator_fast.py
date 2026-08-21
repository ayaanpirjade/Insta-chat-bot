"""ULTIMATE API ROTATOR - MAX SPEED without rate limits!"""
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
_rate_limit_active = False
_rate_limit_lock = threading.Lock()

def parse_duration(value: str) -> Optional[float]:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(s|m|h)?", value.strip().lower())
    if not match:
        return None
    amount = float(match.group(1))
    unit = match.group(2) or "s"
    return amount * {"s": 1, "m": 60, "h": 3600}[unit]

def get_client():
    global _shared_client
    with _client_lock:
        if _shared_client is None:
            try:
                from .session_manager import RotatingSessionManager
                sm = RotatingSessionManager()
                client, _ = sm.get_client()
                _shared_client = client
                print("  ✅ Shared client created")
            except Exception as e:
                print(f"  ❌ Failed: {e}")
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
    """Worker with dynamic speed - MAXIMUM without rate limits!"""
    client = get_client()
    if not client:
        return
    
    used_names = set()
    count = 0
    errors = 0
    start_time = time.time()
    deadline = start_time + duration
    delay = 0.05  # Start with 50ms (20 changes/sec)
    global _rate_limit_active
    
    print(f"  ⚡ Worker {worker_id} started (ULTIMATE API)")
    
    while not stop_event.is_set() and time.time() < deadline:
        try:
            # Check global rate limit
            with _rate_limit_lock:
                if _rate_limit_active:
                    print(f"  ⏳ Worker {worker_id}: Rate limit pause...")
                    time.sleep(2)
                    continue
            
            # Generate name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            suffix = random.randint(1, 999)
            full_name = f"{name} {suffix}"
            
            # DIRECT API CALL - THIS ACTUALLY WORKS!
            client.direct_thread_update_title(int(thread_id), full_name)
            count += 1
            errors = 0
            
            # Dynamic speed adjustment
            if count > 50 and delay > 0.02:
                delay -= 0.001  # Speed up gradually
            
            if count % 20 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed if elapsed > 0 else 0
                print(f"  ⚡ Worker {worker_id}: {count} updates ({speed:.1f}/sec)")
            
            # Dynamic delay
            time.sleep(delay)
            
        except Exception as e:
            errors += 1
            error_str = str(e).lower()
            
            if "429" in error_str or "rate" in error_str or "limit" in error_str:
                with _rate_limit_lock:
                    _rate_limit_active = True
                print(f"  ⚠️ Worker {worker_id}: Rate limit! Pausing 5s...")
                time.sleep(5)
                with _rate_limit_lock:
                    _rate_limit_active = False
                delay = max(0.05, delay + 0.02)  # Increase delay
                # Refresh client
                with _client_lock:
                    global _shared_client
                    _shared_client = None
                    client = get_client()
                    if not client:
                        break
            else:
                if errors % 5 == 0:
                    print(f"  ⚠️ Worker {worker_id} error: {str(e)[:50]}")
                time.sleep(0.1)
    
    elapsed = time.time() - start_time
    speed = count / elapsed if elapsed > 0 else 0
    print(f"  ✅ Worker {worker_id}: {count} updates ({speed:.1f}/sec)")

def start(query: str, thread_id: str, cl=None) -> str:
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 5:
        return "⏳ Duration must be at least 5 seconds."

    stop(str(thread_id))
    
    client = get_client()
    if not client:
        return "❌ Failed to create client"

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    # OPTIMAL workers - 3 is best balance
    num_workers = 3
    threads = []
    for i in range(num_workers):
        t = threading.Thread(
            target=rename_worker,
            args=(thread_id, base_name, event, i+1, duration),
            daemon=True
        )
        t.start()
        threads.append(t)
    
    def monitor():
        for t in threads:
            t.join()
        _stop_events.pop(key, None)
        _threads.pop(key, None)
    
    monitor_thread = threading.Thread(target=monitor, daemon=True)
    _threads[key] = monitor_thread
    monitor_thread.start()

    return f"⚡ ULTIMATE API: {num_workers} workers, SMART speed! Use !ncstop to stop."
