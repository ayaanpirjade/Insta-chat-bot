"""speak_command.py - Threaded wrapper for tts.py (NO text reply)"""

import threading
from . import tts as seductive_voice
from instagrapi import Client
from typing import Optional

_active_jobs = {}
_jobs_lock = threading.Lock()


def handle_speak_command(
    cl: Client,
    thread_id: str,
    msg,
    user_id: str,
    username: str,
    args: str = ""
) -> Optional[str]:
    """Threaded wrapper - runs in background, NO text reply"""
    
    args = (args or "").strip()
    
    if not args:
        return (
            "💋 **SPEAK Command**\n\n"
            "Usage:\n"
            "  • `!speak <text>` - AI reply + voice\n\n"
            "Example:\n"
            "  • `!speak hi baby`\n"
            "  • `!speak kya haal hai`"
        )

    # Prevent spam
    with _jobs_lock:
        if user_id in _active_jobs:
            return None  # Silent if already processing
        _active_jobs[user_id] = True

    def _worker():
        try:
            seductive_voice.handle_speak_command(
                cl=cl,
                thread_id=thread_id,
                msg=msg,
                user_id=user_id,
                username=username,
                args=args
            )
        except Exception as e:
            print(f"  ⚠️ Speak worker error: {e}")
        finally:
            with _jobs_lock:
                _active_jobs.pop(user_id, None)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()

    return None  # ✅ NO text message - sirf voice note aayega