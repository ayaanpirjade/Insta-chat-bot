"""speak_command.py - Threaded wrapper for tts.py"""

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
    """Threaded wrapper - Non-blocking"""
    
    args = (args or "").strip()
    
    # Empty args → usage message
    if not args:
        return (
            "💋 **SPEAK Command**\n\n"
            "Usage:\n"
            "  • `!speak <text>` - Main bolungi\n"
            "  • `!speak ai <text>` - AI reply + voice\n\n"
            "Example:\n"
            "  • `!speak hello baby`\n"
            "  • `!speak ai kya haal hai`"
        )

    # Prevent spam
    with _jobs_lock:
        if user_id in _active_jobs:
            return f"⏳ Ruko jaan! Pehle wali voice ban rahi hai 💋"
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

    return "🎤 Voice ban rahi hai jaan, 3-5 second mein aayegi 💋"