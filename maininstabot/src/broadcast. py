# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          📢 AYAAN AI - Broadcast Command
#          !broad <message>  →  sends to ALL existing threads (DM + groups)
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

# ── Reuse your existing admin check ──
from .evil import is_admin

# ── Config ──
MIN_DELAY = 15          # seconds between threads (min)
MAX_DELAY = 30          # seconds between threads (max)
BATCH_SIZE = 30         # pause after this many
BATCH_PAUSE = 120       # seconds to pause between batches

# ── State ──
_broadcast_lock = threading.Lock()
_broadcast_running = False


def _human_delay():
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


def _get_all_thread_ids(cl: Client) -> List[str]:
    """Fetch every DM + group thread the bot is currently in."""
    try:
        threads = cl.direct_threads(amount=0)   # 0 = fetch all
        ids = [str(t.id) for t in threads]
        print(f"  📋 Found {len(ids)} threads")
        return ids
    except Exception as e:
        print(f"  ⚠️ Failed to fetch threads: {e}")
        return []


def _run_broadcast(cl: Client, message: str, ack_thread_id: str):
    """Background worker — sends message to every thread with safe delays."""
    global _broadcast_running

    thread_ids = _get_all_thread_ids(cl)
    if not thread_ids:
        _broadcast_running = False
        try:
            cl.direct_send("❌ Broadcast aborted: no threads found.", thread_ids=[str(ack_thread_id)])
        except Exception:
            pass
        return

    total = len(thread_ids)
    sent, failed = 0, 0

    print(f"\n📢 Broadcasting to {total} threads...")

    for i, tid in enumerate(thread_ids, 1):
        if not _broadcast_running:          # !stopbroad kill-switch
            print("  🛑 Cancelled by user")
            break

        try:
            # Tiny suffix variation so IG doesn't flag identical spam
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

        # Batch pause
        if i % BATCH_SIZE == 0 and i < total:
            print(f"  💤 Batch pause ({BATCH_PAUSE}s)...")
            time.sleep(BATCH_PAUSE)
        else:
            _human_delay()

    _broadcast_running = False

    # Report back
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


# ── !broad / !broadcast ──

def handle_broad_command(query: str, user_id: str, username: str,
                         thread_id: str, cl: Client) -> Optional[str]:
    """Owner-only broadcast to every thread the bot is in."""

    global _broadcast_running

    # Same admin gate as the rest of your bot
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

    if _broadcast_running:
        return "⏳ A broadcast is already running. Use `!stopbroad` to cancel."

    if not _broadcast_lock.acquire(blocking=False):
        return "⏳ Broadcast already in progress."

    _broadcast_running = True

    # Ack in current thread
    try:
        cl.direct_send(
            f"📢 *Broadcast started...*\n_{query[:100]}_",
            thread_ids=[str(thread_id)],
        )
    except Exception:
        pass

    # Run in background so the bot stays responsive
    threading.Thread(
        target=_run_broadcast,
        args=(cl, query, thread_id),
        daemon=True,
    ).start()

    return None


# ── !stopbroad ──

def handle_stopbroad_command(query: str, user_id: str, username: str,
                             thread_id: str, cl: Client) -> Optional[str]:
    """Kill switch — stops the currently running broadcast."""
    global _broadcast_running

    if not is_admin(user_id):
        return "🔒 ADMIN ONLY! 😈"

    if not _broadcast_running:
        return "ℹ️ No broadcast is currently running."

    _broadcast_running = False
    return "🛑 Broadcast cancel requested. It will stop after the current thread."


# ── Aliases ──
def handle_broadcast_command(q, u, n, t, c):
    return handle_broad_command(q, u, n, t, c)