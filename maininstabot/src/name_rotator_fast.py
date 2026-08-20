"""ULTRA-FAST name rotation using Playwright with Xvfb - TERMUX COMPATIBLE"""
import asyncio
import random
import re
import time
import threading
import os
import subprocess
from typing import Dict, Optional
from playwright.async_api import async_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

# ---- Speed tuning ----
CONCURRENT_TABS = 10          # 10 parallel browser tabs (reduce for Termux)
BASE_DELAY = 0.002            # 2ms
EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]

_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}
_xvfb_process = None

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

def start_xvfb():
    """Start Xvfb virtual display"""
    global _xvfb_process
    try:
        # Check if Xvfb is already running
        result = subprocess.run(['pgrep', 'Xvfb'], capture_output=True)
        if result.returncode == 0:
            print("  ✅ Xvfb already running")
            return True
        
        # Start Xvfb on display :99
        _xvfb_process = subprocess.Popen(
            ['Xvfb', ':99', '-screen', '0', '1280x720x24'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.environ['DISPLAY'] = ':99'
        time.sleep(1)  # Give Xvfb time to start
        print("  ✅ Xvfb started on display :99")
        return True
    except Exception as e:
        print(f"  ❌ Failed to start Xvfb: {e}")
        return False

async def ultra_fast_rename(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """Single worker that renames as fast as possible"""
    used_names = set()
    count = 0
    errors = 0
    
    while not stop_event.is_set() and errors < 20:
        try:
            # Generate unique name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 1000:
                used_names.clear()
            
            # Click rename button
            try:
                # Try different selectors
                selectors = [
                    'button[aria-label="Change group name"]',
                    'div[aria-label="Change group name"][role="button"]',
                    'button:has-text("Change name")',
                    'button:has-text("Edit group name")',
                ]
                
                clicked = False
                for selector in selectors:
                    try:
                        btn = page.locator(selector).first
                        if await btn.count() > 0 and await btn.is_visible():
                            await btn.click(force=True, timeout=100)
                            await asyncio.sleep(0.001)
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    # Try opening info panel first
                    info_btn = page.locator('svg[aria-label="Conversation information"]').first
                    if await info_btn.count() > 0:
                        await info_btn.click(force=True, timeout=100)
                        await asyncio.sleep(0.001)
                        
                        # Try rename button again
                        for selector in selectors:
                            try:
                                btn = page.locator(selector).first
                                if await btn.count() > 0:
                                    await btn.click(force=True, timeout=100)
                                    await asyncio.sleep(0.001)
                                    clicked = True
                                    break
                            except:
                                continue
            except:
                pass
            
            # Find input field
            input_selectors = [
                'input[aria-label="Group name"]',
                'input[name="change-group-name"]',
                '[role="dialog"] input[type="text"]',
                'input[placeholder*="group name"]',
            ]
            
            input_field = None
            for selector in input_selectors:
                try:
                    field = page.locator(selector).first
                    if await field.count() > 0:
                        input_field = field
                        break
                except:
                    continue
            
            if input_field:
                try:
                    await input_field.fill(name, timeout=100)
                    await asyncio.sleep(0.001)
                except:
                    try:
                        await input_field.click(force=True)
                        await input_field.fill(name, timeout=100)
                        await asyncio.sleep(0.001)
                    except:
                        pass
            
            # Click save button
            save_selectors = [
                'button:has-text("Save")',
                'div[role="button"]:has-text("Save")',
                '[role="dialog"] button:has-text("Save")',
            ]
            
            for selector in save_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.count() > 0:
                        await btn.click(force=True, timeout=100)
                        break
                except:
                    continue
            
            count += 1
            errors = 0
            
            if count % 100 == 0:
                print(f"  ⚡ Worker {worker_id}: {count} updates")
            
            await asyncio.sleep(BASE_DELAY + random.uniform(-0.001, 0.001))
            
        except Exception as e:
            errors += 1
            if errors % 10 == 0:
                print(f"  ⚠️ Worker {worker_id} error: {str(e)[:50]}")
            await asyncio.sleep(0.01)
    
    print(f"  ✅ Worker {worker_id} finished: {count} updates")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Launch multiple concurrent browser tabs with Xvfb"""
    # Start Xvfb if not running
    if not start_xvfb():
        print("  ❌ Xvfb failed to start, using headless mode")
    
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # Always headless in Termux
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu-compositing',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        context = await browser.new_context(
            locale="en-US",
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Load session cookie
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
        
        print(f"  🌐 Opening {CONCURRENT_TABS} browser tabs...")
        
        # Create multiple pages
        pages = []
        for i in range(CONCURRENT_TABS):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_load_state('networkidle', timeout=5000)
                pages.append(page)
                print(f"  ✅ Tab {i+1} loaded")
            except Exception as e:
                print(f"  ⚠️ Tab {i+1} failed: {e}")
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers...")
        
        # Start all workers
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                ultra_fast_rename(page, base_name, stop_event, i+1)
            ))
        
        # Run for duration
        await asyncio.sleep(duration)
        stop_event.set()
        
        # Wait for all workers to finish
        await asyncio.gather(*tasks, return_exceptions=True)
        
        elapsed = time.time() - start_time
        
        # Close everything
        await context.close()
        await browser.close()
        
        print(f"\n  🎯 Rotation completed in {elapsed:.1f}s")

def start(query: str, thread_id: str, cl=None) -> str:
    """Start ultra-fast name rotation"""
    parts = query.strip().rsplit(maxsplit=1)
    if len(parts) != 2:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"

    base_name, duration_text = parts
    duration = parse_duration(duration_text)
    if not base_name or duration is None:
        return "Usage: !nc <base name> <duration>\nExample: !nc CHU LOVERS 10m"
    if duration < 5:
        return "⏳ Duration must be at least 5 seconds."
    if duration > 3600:
        return "⏳ Duration cannot exceed 60 minutes."

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

    return f"⚡ ULTRA-FAST rotation started! {CONCURRENT_TABS} tabs, 2ms delay! Use !ncstop to stop."