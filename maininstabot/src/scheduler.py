# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#     Scheduler / Reminder System
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import re
import time
import datetime
import threading

# ── Scheduled reminders ───────────────
scheduled_messages: list[tuple[datetime.datetime, str, str]] = []
_lock = threading.Lock()


def parse_reminder(text: str):
    """
    Parse reminder from text.
    Formats:
      !remind in 10 minutes: message
      !remind in 2 hours: message
      !remind at 9:30pm: message
    Returns (send_at, message) or (None, None)
    """
    now = datetime.datetime.now()

    # "in X minutes/hours"
    m = re.search(r"in\s+(\d+)\s+(minute|minutes|min|hour|hours|hr|hrs)", text, re.IGNORECASE)
    if m:
        amount = int(m.group(1))
        unit = m.group(2).lower()
        if "hour" in unit or "hr" in unit:
            delta = datetime.timedelta(hours=amount)
        else:
            delta = datetime.timedelta(minutes=amount)
        send_at = now + delta
        msg_match = re.search(r":\s*(.+)$", text, re.DOTALL)
        msg = msg_match.group(1).strip() if msg_match else "⏰ Time's up!"
        return send_at, msg

    # "at HH:MM am/pm"
    m = re.search(r"at\s+(\d{1,2}):(\d{2})\s*(am|pm)?", text, re.IGNORECASE)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        meridiem = m.group(3)
        if meridiem:
            if meridiem.lower() == "pm" and hour != 12:
                hour += 12
            elif meridiem.lower() == "am" and hour == 12:
                hour = 0
        send_at = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if send_at <= now:
            send_at += datetime.timedelta(days=1)
        msg_match = re.search(r":\s*(.+)$", text, re.DOTALL)
        msg = msg_match.group(1).strip() if msg_match else "⏰ Time's up!"
        return send_at, msg

    return None, None


def add_reminder(send_at: datetime.datetime, thread_id: str, message: str):
    """Add a reminder to the queue."""
    with _lock:
        scheduled_messages.append((send_at, thread_id, message))


def scheduler_loop(send_fn):
    """
    Background loop that checks for due reminders.
    send_fn(thread_id, message) should send the message.
    """
    while True:
        now = datetime.datetime.now()
        due = []
        with _lock:
            for item in scheduled_messages[:]:
                if item[0] <= now:
                    due.append(item)
                    scheduled_messages.remove(item)

        for _, tid, msg in due:
            try:
                send_fn(tid, f"⏰ Reminder: {msg}")
                print(f"  ⏰ Reminder sent: {msg}")
            except Exception as e:
                print(f"  ⚠️ Reminder failed: {e}")

        time.sleep(10)


def format_reminder_confirm(send_at: datetime.datetime, message: str) -> str:
    """Format a confirmation message for a set reminder."""
    return (
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "       ⏰ REMINDER SET ⏰         \n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 Time: {send_at.strftime('%I:%M %p')}\n"
        f"💬 Message: \"{message}\"\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
