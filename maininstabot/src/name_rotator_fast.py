"""TERMUX-OPTIMIZED Playwright - 5 tabs, FAST!"""
import asyncio
import random
import re
import time
import threading
import os
import subprocess
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

async def fast_rename(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """FAST rename worker - Termux optimized"""
    count = 0
    errors = 0
    print(f"  ⚡ Worker {worker_id} ready")
    
    # Wait for page
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=5000)
    except:
        pass
    
    # Try to find elements once
    try:
        # Click on group name header
        header = page.locator('header h2, header div[role="button"]').first
        if await header.count() > 0:
            await header.click()
            await asyncio.sleep(0.2)
    except:
        pass
    
    while not stop_event.is_set():
        try:
            # Generate name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # ---- OPEN RENAME DIALOG ----
            clicked = False
            
            # Try clicking the group name again
            try:
                header = page.locator('header h2, header div[role="button"]').first
                if await header.count() > 0:
                    await header.click()
                    await asyncio.sleep(0.1)
                    clicked = True
            except:
                pass
            
            # If that fails, try info panel
            if not clicked:
                try:
                    info_btn = page.locator('svg[aria-label="Conversation information"]').first
                    if await info_btn.count() > 0:
                        await info_btn.click()
                        await asyncio.sleep(0.1)
                        rename_btn = page.locator('button:has-text("Change name")').first
                        if await rename_btn.count() > 0:
                            await rename_btn.click()
                            await asyncio.sleep(0.1)
                            clicked = True
                except:
                    pass
            
            if not clicked:
                errors += 1
                if errors % 5 == 0:
                    print(f"  ⚠️ Worker {worker_id}: Can't open dialog")
                await asyncio.sleep(0.2)
                continue
            
            # ---- FIND INPUT ----
            input_field = None
            try:
                input_field = page.locator('input[aria-label="Group name"]').first
                if await input_field.count() == 0:
                    input_field = page.locator('[role="dialog"] input[type="text"]').first
                if await input_field.count() == 0:
                    input_field = page.locator('input').first
            except:
                pass
            
            if not input_field or await input_field.count() == 0:
                errors += 1
                await asyncio.sleep(0.1)
                continue
            
            # ---- FILL NAME ----
            try:
                await input_field.fill(name)
                await asyncio.sleep(0.05)
            except:
                try:
                    await input_field.click()
                    await input_field.fill(name)
                    await asyncio.sleep(0.05)
                except:
                    pass
            
            # ---- SAVE ----
            saved = False
            try:
                save_btn = page.locator('button:has-text("Save")').first
                if await save_btn.count() > 0:
                    await save_btn.click()
                    saved = True
            except:
                pass
            
            if saved:
                count += 1
                errors = 0
                
                if count % 10 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} changes")
                
                # Wait between changes
                await asyncio.sleep(0.1)
            else:
                errors += 1
                await asyncio.sleep(0.05)
            
        except Exception as e:
            errors += 1
            if errors % 10 == 0:
                print(f"  ⚠️ Worker {worker_id} error: {str(e)[:30]}")
            await asyncio.sleep(0.2)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner - optimized for Termux"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--disable-images',
                '--blink-settings=imagesEnabled=false'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 800, 'height': 600},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Load session
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
        
        # Use 5 tabs (Termux optimized)
        num_tabs = 5
        print(f"  🌐 Opening {num_tabs} tabs...")
        
        pages = []
        for i in range(num_tabs):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=15000)
                pages.append(page)
                print(f"  ✅ Tab {i+1} loaded")
            except Exception as e:
                print(f"  ⚠️ Tab {i+1} failed: {e}")
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers...")
        
        # Start workers
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                fast_rename(page, base_name, stop_event, i+1)
            ))
        
        # Run for duration
        await asyncio.sleep(duration)
        stop_event.set()
        
        # Wait for workers
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

    return f"⚡ FAST: 5 tabs optimized for Termux! Use !ncstop to stop."