"""ORIGINAL WORKING - SPEED BOOSTED!"""
import asyncio
import random
import re
import time
import threading
import os
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

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

async def ensure_info_panel_open(page):
    info_selectors = [
        'svg[aria-label="Conversation information"]',
        '[aria-label="Conversation information"]',
        'button[aria-label*="Details"]',
        'button:has-text("Info")',
        'button:has-text("Details")',
        'svg[aria-label*="Info"]',
    ]
    for sel in info_selectors:
        try:
            loc = page.locator(sel)
            if await loc.count():
                await loc.first.click(force=True)
                await asyncio.sleep(0.01)  # FAST
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
        'text="Change name"',
        'text="Edit group name"',
    ]
    for sel in triggers:
        try:
            btn = page.locator(sel)
            if await btn.count():
                await btn.first.click(force=True)
                await asyncio.sleep(0.01)  # FAST
                return True
        except Exception:
            continue
    return False

async def get_rename_controls(page):
    input_selectors = [
        'input[aria-label="Group name"]',
        'input[name="change-group-name"]',
        '[role="dialog"] input[type="text"]',
        'input[placeholder*="Group name"]',
    ]
    save_selectors = [
        '[role="dialog"] button:has-text("Save")',
        'button:has-text("Save")',
        '[role="dialog"] div[role="button"]:has-text("Save")',
        'div[role="button"]:has-text("Save")'
    ]
    for _ in range(3):
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
        await asyncio.sleep(0.01)
        await open_rename_dialog(page)
    return None, None

async def rename_worker(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """FAST VERSION - 10x speed boost!"""
    count = 0
    print(f"  ⚡ Worker {worker_id} started (FAST MODE)")
    
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=5000)
    except:
        pass
    
    while not stop_event.is_set():
        try:
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # FAST: Open dialog
            ok = await open_rename_dialog(page)
            if not ok:
                await ensure_info_panel_open(page)
                ok = await open_rename_dialog(page)
            
            if not ok:
                await asyncio.sleep(0.01)
                continue
            
            # FAST: Get controls
            inp, save_btn = await get_rename_controls(page)
            if not inp or not save_btn:
                await asyncio.sleep(0.01)
                continue
            
            # FAST: Fill name
            try:
                await inp.fill(name, timeout=500)
            except Exception:
                try:
                    await inp.click(force=True)
                    await inp.fill(name, timeout=500)
                except Exception:
                    pass
            
            await asyncio.sleep(0.005)  # 5ms
            
            # FAST: Check disabled
            try:
                disabled = await save_btn.get_attribute("aria-disabled")
                if disabled == "true":
                    await page.keyboard.press("Escape")
                    await asyncio.sleep(0.005)
                    continue
            except Exception:
                pass
            
            # FAST: Click Save
            await save_btn.click(force=True)
            count += 1
            
            if count % 20 == 0:  # Print less often
                print(f"  ⚡ Worker {worker_id}: {count} changes")
            
            # FAST DELAY - 20ms (50 changes/sec)
            await asyncio.sleep(0.02)  # 20ms
            
        except Exception as e:
            await asyncio.sleep(0.01)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner with 3 tabs for more speed"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
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
        
        num_tabs = 3  # More tabs = more speed
        print(f"  🌐 Opening {num_tabs} tabs...")
        
        pages = []
        for i in range(num_tabs):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=20000)
                pages.append(page)
                print(f"  ✅ Tab {i+1} loaded")
            except Exception as e:
                print(f"  ⚠️ Tab {i+1} failed: {e}")
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers (FAST MODE)...")
        
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                rename_worker(page, base_name, stop_event, i+1)
            ))
        
        await asyncio.sleep(duration)
        stop_event.set()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        await browser.close()

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

    dm_url = f"https://www.instagram.com/direct/t/{thread_id}/"

    key = str(thread_id)
    event = threading.Event()
    _stop_events[key] = event

    def run_async():
        asyncio.run(async_runner(dm_url, base_name, event, duration))

    thread = threading.Thread(target=run_async, daemon=True)
    _threads[key] = thread
    thread.start()

    return f"⚡ FAST MODE: 3 tabs, 20ms delay! Use !ncstop to stop."
