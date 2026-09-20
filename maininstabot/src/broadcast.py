# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          📢 AYAAN AI - Broadcast Command  (v3 — Lock-safe)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import time
import random
import threading
from typing import Optional, Dict, List

from instagrapi import Client
from instagrapi.exceptions import (
    ClientError,
    RateLimitError,
    PleaseWaitFewMinutes,
    DirectThreadNotFound,
)

from .evil import is_admin

# ── Config ──
MIN_DELAY = 15
MAX_DELAY = 30
BATCH_SIZE = 30
BATCH_PAUSE = 120
STALE_LOCK_SECONDS = 30 * 60

# ── State ──
_broadcast_lock = threading.Lock()
_broadcast_running = False
_broadcast_started_at = 0.0


def _human_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def _get_all_thread_ids(cl: Client) -> List[str]:
    try:
        threads = cl.direct_threads(amount=0)
        ids = [str(t.id) for t in threads]
        print(f"  📋 Found {len(ids)} threads")
        return ids
    except Exception as e:
        print(f"  ⚠️ Failed to fetch threads: {e}")
        return []


def _run_broadcast(cl: Client, message: str, ack_thread_id: str):
    """Background worker — ALWAYS resets the running flag via finally."""
    global _broadcast_running

    sent, failed, total = 0, 0, 0

    try:
        thread_ids = _get_all_thread_ids(cl)
        if not thread_ids:
            try:
                cl.direct_send("❌ Broadcast aborted: no threads found.",
                               thread_ids=[str(ack_thread_id)])
            except Exception:
                pass
            return

        total = len(thread_ids)
        print(f"\n📢 Broadcasting to {total} threads...")

        for i, tid in enumerate(thread_ids, 1):
            if not _broadcast_running:
                print("  🛑 Cancelled by user")
                break

            try:
                suffix = random.choice(["", " ", ".", "…"])
                cl.direct_send(f"{message}{suffix}", thread_ids=[tid])
                sent += 1
                print(f"  ✅ [{i}/{total}] → {tid}")

            except DirectThreadNotFound:
                failed += 1
                print(f"  ⚠️ [{i}/{total}] Thread not found")

            except (RateLimitError, PleaseWaitFewMinutes) as e:
                print(f"  🚨 Rate limited — stopping: {e}")
                failed += total - i + 1
                break

            except ClientError as e:
                failed += 1
                print(f"  ⚠️ [{i}/{total}] ClientError: {e}")

            except Exception as e:
                failed += 1
                print(f"  ⚠️ [{i}/{total}] Unexpected: {e}")

            if i % BATCH_SIZE == 0 and i < total:
                print(f"  💤 Batch pause ({BATCH_PAUSE}s)...")
                time.sleep(BATCH_PAUSE)
            else:
                _human_delay()

    except BaseException as fatal:
        print(f"  💥 Broadcast crashed: {fatal!r}")

    finally:
        _broadcast_running = False
        print("  🔓 Broadcast flag reset")

        summary = (
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "      📢 BROADCAST FINISHED\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ Sent   : {sent}\n"
            f"❌ Failed : {failed}\n"
            f"📋 Total  : {total}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            cl.direct_send(summary, thread_ids=[str(ack_thread_id)])
        except Exception:
            pass


def handle_broad_command(query: str, user_id: str, username: str,
                         thread_id: str, cl: Client) -> Optional[str]:
    global _broadcast_running, _broadcast_started_at

    if not is_admin(user_id):
        return "🔒 Broadcast is ADMIN ONLY! 😈"

    query = query.strip()
    if not query:
        return (
            "📢 *Broadcast Command*\n"
            "Usage: `!broad <message>`\n"
            "Example: `!broad Server is back online 🚀`"
        )

    if len(query) > 500:
        return "⚠️ Message too long (max 500 chars)."

    # Watchdog: auto-clear stale locks
    if _broadcast_running:
        age = time.time() - _broadcast_started_at
        if age > STALE_LOCK_SECONDS:
            print(f"  🧹 Clearing stale broadcast flag (age {age:.0f}s)")
            _broadcast_running = False
            # Also force-release a possibly stuck lock
            try:
                _broadcast_lock.release()
            except RuntimeError:
                pass  # lock wasn't held — that's fine
        else:
            return f"⏳ Broadcast already running ({age:.0f}s ago). Use `!stopbroad` to cancel."

    if not _broadcast_lock.acquire(blocking=False):
        return "⏳ Broadcast lock busy — try again in a moment."

    _broadcast_running = True
    _broadcast_started_at = time.time()
    print("  🔒 Broadcast lock acquired")

    try:
        cl.direct_send(
            f"📢 *Broadcast started...*\n_{query[:100]}_",
            thread_ids=[str(thread_id)],
        )
    except Exception:
        pass

    def _worker():
        try:
            _run_broadcast(cl, query, thread_id)
        finally:
            # 🔑 Release the lock HERE — in the worker's finally
            try:
                _broadcast_lock.release()
                print("  🔓 Broadcast lock fully released")
            except RuntimeError:
                pass  # already released — safe

    threading.Thread(target=_worker, daemon=True).start()

    return None


def handle_stopbroad_command(query: str, user_id: str, username: str,
                             thread_id: str, cl: Client) -> Optional[str]:
    global _broadcast_running

    if not is_admin(user_id):
        return "🔒 ADMIN ONLY! 😈"

    if not _broadcast_running:
        return "ℹ️ No broadcast is currently running."

    _broadcast_running = False
    return "🛑 Broadcast cancel requested. It will stop after the current thread."


def handle_broadstatus_command(query: str, user_id: str, username: str,
                               thread_id: str, cl: Client) -> Optional[str]:
    if not is_admin(user_id):
        return "🔒 ADMIN ONLY! 😈"

    if _broadcast_running:
        age = time.time() - _broadcast_started_at
        return f"📢 Broadcast is RUNNING (started {age:.0f}s ago)."
    return "✅ No broadcast running — you're free to start one."


# ── Aliases ──
def handle_broadcast_command(q, u, n, t, c):
    return handle_broad_command(q, u, n, t, c)