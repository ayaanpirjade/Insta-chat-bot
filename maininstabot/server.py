# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Instagram Chatbot Server
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import config
import src.game as game
import src.router as router
import src.scheduler as scheduler
import src.menu as menu
from src.session_manager import RotatingSessionManager

# Reconfigure console streams to UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── Thread Pool ──
executor = ThreadPoolExecutor(max_workers=2)

# ── Session Manager ──
session_manager = RotatingSessionManager()

# ── Track processed messages ──
processed_ids = set()


def send_message(thread_id: str, text: str):
    """Send message through active client"""
    try:
        cl, _ = session_manager.get_client()
        cl.direct_send(text, thread_ids=[thread_id])
        time.sleep(1)  # Delay between sends
    except Exception as e:
        print(f"  ⚠️ Send failed: {e}")


def handle_incoming_message(msg, thread, my_id: str):
    """Processes incoming message"""
    try:
        msg_id = str(msg.id)
        
        if msg_id in processed_ids:
            return
        processed_ids.add(msg_id)
        
        if len(processed_ids) > 5000:
            processed_ids.clear()

        thread_id = thread.id
        user_id = str(msg.user_id)

        if user_id == my_id:
            return

        username = "friend"
        for user in thread.users:
            if str(user.pk) == user_id:
                username = user.username
                break

        text = msg.text.strip() if msg.text else ""
        is_group = thread.is_group or len(thread.users) > 1

        if not text:
            return

        print(f"💬 @{username}: {text[:50]}")

        cl, _ = session_manager.get_client()

        reply = router.process_message(
            text=text,
            thread_id=thread_id,
            user_id=user_id,
            username=username,
            is_group=is_group,
            cl=cl,
            msg=msg
        )

        if reply:
            send_message(thread_id, reply)
            print(f"  → Replied")

    except Exception as e:
        print(f"  ⚠️ Error: {e}")


def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("         ✨ AYAAN AI ✨          ")
    print("   Starting Instagram Chatbot... ")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    game.load_game_data()

    if not config.SESSION_ID:
        print("❌ ERROR: SESSION_ID not found in .env file.")
        return

    print("Connecting to Instagram...")
    try:
        cl, my_username = session_manager.get_client()
        my_id = session_manager.get_my_id()
        print(f"✅ Logged in as @{my_username} (ID: {my_id})\n")
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return

    # Start reminders
    def send_scheduler_msg(thread_id, text):
        send_message(thread_id, text)

    threading.Thread(
        target=scheduler.scheduler_loop,
        args=(send_scheduler_msg,),
        daemon=True,
    ).start()
    print("⏰ Reminders started.")

    # Tracking
    last_seen_message_ids = {}
    known_members = {}

    print("Scanning chats...")
    try:
        threads = cl.direct_threads(amount=15)  # Reduced from 20
        for thread in threads:
            tid = thread.id
            if thread.messages:
                last_seen_message_ids[tid] = thread.messages[0].id
            known_members[tid] = {str(u.pk) for u in thread.users}
            title = thread.thread_title or "DM"
            print(f"  📌 '{title[:20]}' ({len(thread.users)} members)")
    except Exception as e:
        print(f"⚠️ Chat scan error: {e}")
        print("📌 Bot will retry in next polling cycle...")

    print(f"\n🤖 LIVE! Polling every {config.POLL_INTERVAL} seconds...\n")

    while True:
        try:
            cl, _ = session_manager.get_client()
            my_id = session_manager.get_my_id()

            threads = cl.direct_threads(amount=15)  # Reduced from 20
            for thread in threads:
                tid = thread.id
                current_members = {str(u.pk) for u in thread.users}

                # New thread
                if tid not in known_members:
                    print(f"🆕 New chat: '{thread.thread_title or 'DM'}'")
                    known_members[tid] = current_members
                    if thread.messages:
                        last_seen_message_ids[tid] = thread.messages[0].id
                    continue

                # New members
                new_members = current_members - known_members[tid]
                for user_id in new_members:
                    username = "there"
                    for u in thread.users:
                        if str(u.pk) == user_id:
                            username = u.username
                            break
                    welcome = menu.welcome_message(username)
                    send_message(tid, welcome)
                    print(f"  👤 Welcomed @{username}")
                known_members[tid] = current_members

                # New messages
                if not thread.messages:
                    continue

                new_messages = []
                for msg in thread.messages:
                    if tid in last_seen_message_ids and msg.id == last_seen_message_ids[tid]:
                        break
                    if msg.item_type == "text" and msg.text:
                        new_messages.append(msg)

                # Process messages (with delay)
                for msg in reversed(new_messages):
                    executor.submit(handle_incoming_message, msg, thread, my_id)
                    time.sleep(0.5)  # Delay between message processing

                # Update last seen
                if thread.messages:
                    last_seen_message_ids[tid] = thread.messages[0].id

        except KeyboardInterrupt:
            print("\n🛑 Stopped.")
            break
        except Exception as e:
            print(f"⚠️ Polling error: {e}")
            if "403" in str(e):
                print("🔴 Account blocked or rate limited!")
                print("💡 Try:")
                print("   • Use VPN or mobile hotspot")
                print("   • Wait 30-60 minutes")
                print("   • Use different account")
                time.sleep(60)  # Wait 60 seconds before retry

        time.sleep(config.POLL_INTERVAL)


if __name__ == "__main__":
    main()
