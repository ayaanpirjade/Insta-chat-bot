"""LIGHTNING FAST - Single Account, No Browser, Pure API with Ultra-Fast Threading"""
import time
import random
import threading
import re
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor

EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}
_executor = ThreadPoolExecutor(max_workers=20)  # 20 concurrent threads

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

def rename_worker(thread_id: str, base_name: str, stop_event: threading.Event, worker_id: int):
    """Single worker - FAST and RELIABLE"""
    from .session_manager import RotatingSessionManager
    sm = RotatingSessionManager()
    
    try:
        client, _ = sm.get_client()
    except:
        # If session expired, create new one
        sm = RotatingSessionManager()
        client, _ = sm.get_client()
    
    used_names = set()
    count = 0
    errors = 0
    start_time = time.time()
    
    print(f"  🔥 Worker {worker_id} started")
    
    while not stop_event.is_set():
        try:
            # Generate unique name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 100:
                used_names.clear()
            
            # DIRECT API CALL - FASTEST METHOD
            client.direct_thread_update_title(int(thread_id), name)
            count += 1
            errors = 0
            
            # Print progress
            if count % 100 == 0:
                elapsed = time.time() - start_time
                speed = count / elapsed if elapsed > 0 else 0
                print(f"  ⚡ Worker {worker_id}: {count} updates ({speed:.0f}/sec)")
            
            # ULTRA-FAST delay (0.5ms)
            time.sleep(0.0005)
            
        except Exception as e:
            errors += 1
            error_str = str(e).lower()
            
            if "rate" in error_str or "limit" in error_str or "429" in error_str:
                # Rate limit - back off briefly
                time.sleep(0.1)
            elif "login" in error_str or "session" in error_str:
                # Session expired - refresh
                try:
                    sm = RotatingSessionManager()
                    client, _ = sm.get_client()
                    print(f"  🔄 Worker {worker_id}: Session refreshed")
                except:
                    time.sleep(1)
            else:
                if errors % 10 == 0:
                    print(f"  ⚠️ Worker {worker_id} error: {str(e)[:50]}")
                time.sleep(0.001)
    
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

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    # Start 20 workers in parallel
    threads = []
    for i in range(20):
        t = threading.Thread(
            target=rename_worker,
            args=(thread_id, base_name, event, i+1),
            daemon=True
        )
        t.start()
        threads.append(t)
    
    # Store threads for cleanup
    _threads[key] = threads

    return f"⚡ LIGHTNING FAST: 20 workers, 0.5ms delay! Use !ncstop to stop."

def clean_up():
    """Clean up old threads"""
    for key in list(_stop_events.keys()):
        stop(key)