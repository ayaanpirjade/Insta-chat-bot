"""Ultra‑fast group‑name rotation – works in any group, no URL needed."""
import asyncio
import random
import re
import time
import threading
import os
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

# ---- Speed tuning ----
CONCURRENT_TASKS = 5          # parallel rename workers (adjust as needed)
BASE_DELAY = 0.002            # ~2ms between updates
MAX_PER_MINUTE = 900          # stay under Instagram's radar
EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]

_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}

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

# ---- Async helpers ----
async def ensure_info_panel_open(page):
    selectors = [
        'svg[aria-label="Conversation information"]',
        '[aria-label="Conversation information"]',
        'button[aria-label*="Details"]',
        'button:has-text("Info")',
    ]
    for sel in selectors:
        try:
            loc = page.locator(sel)
            if await loc.count():
                await loc.first.click(force=True)
                await asyncio.sleep(0.02)
                return True
        except Exception:
            continue
    return False

async def open_rename_dialog(page):
    triggers = [
        'div[aria-label="Change group name"][role="button"]',
        'button:has-text("Change group name")',
        'button:has-text("Change name")',
        'text="Change group name"',
    ]
    for sel in triggers:
        try:
            btn = page.locator(sel)
            if await btn.count():
                await btn.first.click(force=True)
                await asyncio.sleep(0.02)
                return True
        except Exception:
            continue
    return False

async def get_rename_controls(page):
    input_selectors = [
        'input[aria-label="Group name"]',
        'input[name="change-group-name"]',
        '[role="dialog"] input[type="text"]',
    ]
    save_selectors = [
        '[role="dialog"] button:has-text("Save")',
        'button:has-text("Save")',
        'div[role="button"]:has-text("Save")'
    ]
    for _ in range(5):
        for inp_sel in input_selectors:
            try:
                inp = page.locator(inp_sel)
                if await inp.count():
                    for sv_sel in save_selectors:
                        sv = page.locator(sv_sel)
                        if await sv.count():
                            return inp.first, sv.first
            except Exception:
                continue
        await asyncio.sleep(0.02)
        await open_rename_dialog(page)
    return None, None

async def rename_worker(page, base_name: str, stop_event: threading.Event):
    per_minute = 0
    minute_start = time.time()
    used_names = set()

    while not stop_event.is_set():
        try:
            now = time.time()
            if now - minute_start >= 60:
                minute_start = now
                per_minute = 0
            if per_minute >= MAX_PER_MINUTE:
                await asyncio.sleep(0.5)
                per_minute = 0
                minute_start = time.time()

            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 1000:
                used_names.clear()

            # Open rename dialog
            ok = await open_rename_dialog(page)
            if not ok:
                await ensure_info_panel_open(page)
                ok = await open_rename_dialog(page)

            inp, save_btn = await get_rename_controls(page)
            if not inp or not save_btn:
                await asyncio.sleep(0.01)
                continue

            try:
                await inp.fill(name, timeout=1000)
            except Exception:
                await inp.click(force=True)
                await inp.fill(name, timeout=1000)

            try:
                await save_btn.click(force=True)
            except Exception:
                pass

            per_minute += 1

            delay = BASE_DELAY + random.uniform(-0.001, 0.001)
            if delay < 0:
                delay = 0
            await asyncio.sleep(delay)

        except PWTimeout:
            try:
                await page.reload(wait_until='domcontentloaded', timeout=30000)
                await ensure_info_panel_open(page)
            except Exception:
                pass
        except Exception:
            pass

# ---- Main entry point ----
def start(query: str, thread_id: str, client=None) -> str:
    """Start ultra‑fast rotation in the group where the command was sent."""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 30:
        return "⏳ Duration must be at least 30 seconds."
    if duration > 3600:
        return "⏳ Duration cannot exceed 60 minutes."

    # Stop previous rotation for this group
    stop(str(thread_id))

    # Build the group URL from thread_id (no .env needed)
    dm_url = f"https://www.instagram.com/direct/t/{thread_id}/"

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    def run_async():
        asyncio.run(async_runner(dm_url, base_name, event, duration))

    thread = threading.Thread(target=run_async, daemon=True)
    _threads[key] = thread
    thread.start()

    return f"🔄 Ultra‑fast rotation started for {duration_text} with base: '{base_name}'. Use !ncstop to stop."

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        context = await browser.new_context(
            locale="en-US",
            extra_http_headers={"Referer": "https://www.instagram.com/"},
            viewport=None
        )
        # Load session cookie from .env
        load_dotenv()
        session_id = os.getenv("SESSION_ID")
        if session_id:
            await context.add_cookies([{
                "name": "sessionid",
                "value": session_id,
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "None"
            }])

        # Create multiple pages
        pages = [await context.new_page() for _ in range(CONCURRENT_TASKS)]
        tasks = []
        for page in pages:
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=60000)
                await ensure_info_panel_open(page)
            except Exception:
                pass
            tasks.append(asyncio.create_task(rename_worker(page, base_name, stop_event)))

        # Stop after duration
        await asyncio.sleep(duration)
        stop_event.set()

        await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()