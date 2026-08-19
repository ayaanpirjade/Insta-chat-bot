"""ULTRA-FAST name rotation using asyncio + concurrent API calls"""
import asyncio
import random
import re
import time
import threading
from typing import Dict, Optional

EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
CONCURRENT_TASKS = 20  # 20 concurrent workers
BASE_DELAY = 0.001     # 1ms delay
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

async def rename_worker(thread_id: str, base_name: str, stop_event: threading.Event, worker_id: int):
    """Single worker that continuously renames the group"""
    used_names = set()
    count = 0
    
    # Get client once per worker
    client = get_shared_client()
    if not client:
        return
    
    while not stop_event.is_set():
        try:
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 1000:
                used_names.clear()
            
            # Make the API call (this is the bottleneck)
            client.direct_thread_update_title(int(thread_id), name)
            count += 1
            
            # Print progress occasionally
            if count % 50 == 0:
                print(f"  ⚡ Worker {worker_id}: {count} updates")
            
            # Ultra-fast delay
            await asyncio.sleep(BASE_DELAY)
            
        except Exception as e:
            error = str(e).lower()
            if "rate" in error or "limit" in error or "429" in error:
                await asyncio.sleep(0.5)
            else:
                await asyncio.sleep(0.01)

async def async_runner(thread_id: str, base_name: str, stop_event: threading.Event, duration: float):
    """Run multiple concurrent workers"""
    tasks = []
    for i in range(CONCURRENT_TASKS):
        tasks.append(asyncio.create_task(rename_worker(thread_id, base_name, stop_event, i+1)))
    
    # Wait for duration then stop
    await asyncio.sleep(duration)
    stop_event.set()
    
    # Wait for all workers to finish
    await asyncio.gather(*tasks, return_exceptions=True)

def start(query: str, thread_id: str, cl=None) -> str:
    """Start ultra-fast async rotation"""
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

    def run_async():
        asyncio.run(async_runner(thread_id, base_name, event, duration))

    thread = threading.Thread(target=run_async, daemon=True)
    _threads[key] = thread
    thread.start()

    return f"⚡ ULTRA-FAST async rotation started for {duration_text} with '{base_name}' ({CONCURRENT_TASKS} workers, 1ms delay). Use !ncstop to stop."