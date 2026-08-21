"""FINAL WORKING - Proper waits, single tab, ULTRA FAST!"""
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

async def rename_worker(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """FINAL WORKING - Proper waits!"""
    count = 0
    print(f"  ⚡ Worker {worker_id} started (FINAL)")
    
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=5000)
    except:
        pass
    
    while not stop_event.is_set():
        try:
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # ---- STEP 1: Click on group name ----
            clicked = False
            
            # Method 1: Click div[role="button"]
            try:
                header = page.locator('div[role="button"]').first
                if await header.count() > 0:
                    await header.click(force=True)
                    await asyncio.sleep(0.05)  # Wait for menu to open
                    clicked = True
            except:
                pass
            
            # Method 2: Info panel
            if not clicked:
                try:
                    info_btn = page.locator('svg[aria-label="Conversation information"]').first
                    if await info_btn.count() > 0:
                        await info_btn.click(force=True)
                        await asyncio.sleep(0.05)
                        rename_btn = page.locator('button:has-text("Change name")').first
                        if await rename_btn.count() > 0:
                            await rename_btn.click(force=True)
                            await asyncio.sleep(0.05)
                            clicked = True
                except:
                    pass
            
            if not clicked:
                await asyncio.sleep(0.01)
                continue
            
            # ---- STEP 2: Find input field ----
            input_field = None
            selectors = [
                'input[aria-label="Group name"]',
                '[role="dialog"] input[type="text"]',
                'input[name="change-group-name"]',
                'input[placeholder*="Group name"]',
                'input'
            ]
            
            for selector in selectors:
                try:
                    field = page.locator(selector).first
                    if await field.count() > 0 and await field.is_visible():
                        input_field = field
                        break
                except:
                    continue
            
            if not input_field:
                await asyncio.sleep(0.01)
                continue
            
            # ---- STEP 3: Fill name ----
            try:
                await input_field.fill(name)
            except:
                try:
                    await input_field.click(force=True)
                    await input_field.fill(name)
                except:
                    pass
            
            await asyncio.sleep(0.02)  # Wait for input to register
            
            # ---- STEP 4: Click Save with proper wait ----
            saved = False
            save_selectors = [
                'button:has-text("Save")',
                '[role="dialog"] button:has-text("Save")',
                'div[role="button"]:has-text("Save")',
                'button[type="submit"]'
            ]
            
            for selector in save_selectors:
                try:
                    save_btn = page.locator(selector).first
                    if await save_btn.count() > 0 and await save_btn.is_visible():
                        await save_btn.click(force=True)
                        await asyncio.sleep(0.02)  # Wait for save to complete
                        saved = True
                        break
                except:
                    continue
            
            if saved:
                count += 1
                if count % 10 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} changes")
                await asyncio.sleep(0.01)  # 10ms delay
            else:
                await asyncio.sleep(0.01)
            
        except Exception as e:
            await asyncio.sleep(0.01)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner"""
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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
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
        
        print(f"  🌐 Opening tab...")
        
        page = await context.new_page()
        try:
            await page.goto(dm_url, wait_until='domcontentloaded', timeout=20000)
            print(f"  ✅ Tab loaded")
        except Exception as e:
            print(f"  ⚠️ Tab failed: {e}")
        
        print(f"  🔥 Starting worker (FINAL)...")
        await rename_worker(page, base_name, stop_event, 1)
        
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

    return f"⚡ FINAL: Single tab with proper waits! Use !ncstop to stop."
