"""FINAL FIX - Playwright with Proper Element Detection"""
import asyncio
import random
import re
import time
import threading
import os
from typing import Dict, Optional
from playwright.async_api import async_playwright
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
    """Worker with explicit waits and proper element detection"""
    count = 0
    print(f"  ⚡ Worker {worker_id} started")
    
    # Wait for page
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=10000)
    except:
        pass
    
    while not stop_event.is_set():
        try:
            # Generate name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # ---- STEP 1: Click on group name ----
            clicked = False
            
            # Method 1: Click on the group name header
            try:
                # Find any div with role="button" that has text
                header = page.locator('div[role="button"]').first
                if await header.count() > 0:
                    # Check if it has text (group name)
                    text = await header.text_content()
                    if text and len(text) > 0:
                        await header.click(force=True)
                        await asyncio.sleep(0.3)
                        clicked = True
                        print(f"  ✅ Worker {worker_id}: Clicked header")
            except Exception as e:
                pass
            
            # Method 2: Click info panel button
            if not clicked:
                try:
                    info_btn = page.locator('svg[aria-label="Conversation information"]').first
                    if await info_btn.count() > 0:
                        await info_btn.click(force=True)
                        await asyncio.sleep(0.3)
                        
                        # Click "Change name" button
                        rename_btn = page.locator('button:has-text("Change name")').first
                        if await rename_btn.count() > 0:
                            await rename_btn.click(force=True)
                            await asyncio.sleep(0.3)
                            clicked = True
                            print(f"  ✅ Worker {worker_id}: Clicked via info panel")
                except Exception as e:
                    pass
            
            if not clicked:
                await asyncio.sleep(0.1)
                continue
            
            # ---- STEP 2: Find and fill input ----
            input_field = None
            
            # Try multiple selectors
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
                await asyncio.sleep(0.05)
                continue
            
            # Fill the name
            try:
                await input_field.fill(name)
                await asyncio.sleep(0.1)
                print(f"  📝 Worker {worker_id}: Filled: {name}")
            except:
                try:
                    await input_field.click(force=True)
                    await input_field.fill(name)
                    await asyncio.sleep(0.1)
                except:
                    pass
            
            # ---- STEP 3: Click Save button ----
            saved = False
            
            # Try multiple save selectors
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
                        saved = True
                        print(f"  💾 Worker {worker_id}: Saved!")
                        break
                except:
                    continue
            
            if saved:
                count += 1
                if count % 5 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} changes")
                
                # Wait between changes
                await asyncio.sleep(0.3)
            else:
                # Try pressing Enter key as fallback
                try:
                    await page.keyboard.press("Enter")
                    count += 1
                    await asyncio.sleep(0.3)
                except:
                    pass
            
        except Exception as e:
            await asyncio.sleep(0.1)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner with 2 tabs (for stability)"""
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
        
        num_tabs = 2  # Reduced to 2 for stability
        print(f"  🌐 Opening {num_tabs} tabs...")
        
        pages = []
        for i in range(num_tabs):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=30000)
                pages.append(page)
                print(f"  ✅ Tab {i+1} loaded")
            except Exception as e:
                print(f"  ⚠️ Tab {i+1} failed: {e}")
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers...")
        
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

    return f"⚡ FINAL FIX: 2 tabs with proper saving! Use !ncstop to stop."
