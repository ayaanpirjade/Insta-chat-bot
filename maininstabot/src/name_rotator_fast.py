"""HYBRID - API with Smart Rate Limiting (20+ changes/sec)"""
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
    return thread is not None and thread.is_alive()

def stop_command(thread_id: str) -> str:
    return "🛑 Rotation stopped." if stop(thread_id) else "ℹ️ No active rotation."

def rename_worker(thread_id: str, base_name: str, stop_event: threading.Event, worker_id: int, duration: float):
    client = get_client()
    if not client:
        return
    
    count = 0
    used_names = set()
    start_time = time.time()
    deadline = start_time + duration
    
    print(f"  ⚡ Worker {worker_id} started (API)")
    
    while not stop_event.is_set() and time.time() < deadline:
        try:
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            suffix = random.randint(1, 999)
            full_name = f"{name} {suffix}"
            
            client.direct_thread_update_title(int(thread_id), full_name)
            count += 1
            
            if count % 20 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed if elapsed > 0 else 0
                print(f"  ⚡ Worker {worker_id}: {count} updates ({speed:.0f}/sec)")
            
            # 50ms delay = 20 changes/sec per worker
            time.sleep(0.05)
            
        except Exception as e:
            error = str(e).lower()
            if "429" in error or "rate" in error:
                print(f"  ⚠️ Worker {worker_id}: Rate limit, waiting...")
                time.sleep(2)
            else:
                time.sleep(0.1)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

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

    return f"⚡ API: {num_workers} workers, 20 changes/sec each! Use !ncstop to stop."
