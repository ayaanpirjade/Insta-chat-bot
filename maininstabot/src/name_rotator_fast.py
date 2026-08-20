"""ULTIMATE ULTRA-FAST - Single Account, Browser Automation"""
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

CONCURRENT_TABS = 15
EMOJIS = ["✨", "🔥", "💫", "🌙", "💎", "🌈", "😎", "🚀", "🎵", "🌟"]
_stop_events: Dict[str, threading.Event] = {}
_threads: Dict[str, threading.Thread] = {}
_xvfb_running = False

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

def ensure_xvfb():
    """Start Xvfb if not running"""
    global _xvfb_running
    if _xvfb_running:
        return True
    
    try:
        # Check if Xvfb is running
        result = subprocess.run(['pgrep', '-f', 'Xvfb :99'], capture_output=True)
        if result.returncode == 0:
            _xvfb_running = True
            os.environ['DISPLAY'] = ':99'
            return True
        
        # Start Xvfb
        subprocess.Popen(
            ['Xvfb', ':99', '-screen', '0', '1280x720x24', '-ac'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.environ['DISPLAY'] = ':99'
        time.sleep(2)
        _xvfb_running = True
        print("  ✅ Xvfb started")
        return True
    except Exception as e:
        print(f"  ⚠️ Xvfb start failed: {e}")
        return False

async def ultra_rename_worker(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """ULTRA-FAST rename worker"""
    used_names = set()
    count = 0
    errors = 0
    success_count = 0
    
    # Wait for page to be ready
    try:
        await page.wait_for_load_state('networkidle', timeout=10000)
    except:
        pass
    
    print(f"  🔥 Worker {worker_id} ready")
    
    while not stop_event.is_set():
        try:
            # Generate unique name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 500:
                used_names.clear()
            
            # ---- STEP 1: Open rename dialog ----
            dialog_opened = False
            
            # Method 1: Click group name header
            try:
                header = page.locator('header h2, header div[role="button"]').first
                if await header.count() > 0:
                    await header.click(force=True, no_wait_after=True)
                    await asyncio.sleep(0.001)
                    dialog_opened = True
            except:
                pass
            
            # Method 2: Click info button
            if not dialog_opened:
                try:
                    info_btn = page.locator('svg[aria-label="Conversation information"]').first
                    if await info_btn.count() > 0:
                        await info_btn.click(force=True, no_wait_after=True)
                        await asyncio.sleep(0.001)
                        # Click rename in info panel
                        rename_btn = page.locator('button:has-text("Change name"), div[role="button"]:has-text("Change name")').first
                        if await rename_btn.count() > 0:
                            await rename_btn.click(force=True, no_wait_after=True)
                            await asyncio.sleep(0.001)
                            dialog_opened = True
                except:
                    pass
            
            # Method 3: Click more options
            if not dialog_opened:
                try:
                    dots_btn = page.locator('svg[aria-label="More options"]').first
                    if await dots_btn.count() > 0:
                        await dots_btn.click(force=True, no_wait_after=True)
                        await asyncio.sleep(0.001)
                        rename_btn = page.locator('div[role="menuitem"]:has-text("Change name"), div[role="menuitem"]:has-text("Edit group name")').first
                        if await rename_btn.count() > 0:
                            await rename_btn.click(force=True, no_wait_after=True)
                            await asyncio.sleep(0.001)
                            dialog_opened = True
                except:
                    pass
            
            if not dialog_opened:
                errors += 1
                if errors % 10 == 0:
                    print(f"  ⚠️ Worker {worker_id}: Can't open dialog")
                await asyncio.sleep(0.01)
                continue
            
            # ---- STEP 2: Find and fill input ----
            input_field = None
            input_selectors = [
                'input[aria-label="Group name"]',
                'input[name="change-group-name"]',
                '[role="dialog"] input[type="text"]',
                'input[placeholder*="group name"]',
                'input[placeholder*="Group name"]',
                '[role="dialog"] input',
            ]
            
            for selector in input_selectors:
                try:
                    field = page.locator(selector).first
                    if await field.count() > 0 and await field.is_visible():
                        input_field = field
                        break
                except:
                    continue
            
            if not input_field:
                errors += 1
                await asyncio.sleep(0.01)
                continue
            
            # Fill the name
            try:
                await input_field.fill(name, timeout=100)
            except:
                try:
                    await input_field.click(force=True)
                    await input_field.fill(name, timeout=100)
                except:
                    pass
            
            await asyncio.sleep(0.001)
            
            # ---- STEP 3: Click Save ----
            save_clicked = False
            save_selectors = [
                'button:has-text("Save")',
                'div[role="button"]:has-text("Save")',
                '[role="dialog"] button:has-text("Save")',
                '[role="dialog"] div[role="button"]:has-text("Save")',
            ]
            
            for selector in save_selectors:
                try:
                    btn = page.locator(selector).first
                    if await btn.count() > 0 and await btn.is_visible():
                        await btn.click(force=True, no_wait_after=True)
                        save_clicked = True
                        success_count += 1
                        break
                except:
                    continue
            
            if save_clicked:
                count += 1
                errors = 0
                
                if count % 50 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} updates")
            else:
                errors += 1
            
            # ULTRA-FAST DELAY
            await asyncio.sleep(0.001)  # 1ms
            
        except Exception as e:
            errors += 1
            if errors % 20 == 0:
                print(f"  ⚠️ Worker {worker_id} error: {str(e)[:50]}")
            await asyncio.sleep(0.01)
    
    print(f"  ✅ Worker {worker_id}: {count} successful updates")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main async runner"""
    # Start Xvfb
    ensure_xvfb()
    
    start_time = time.time()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu-compositing',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        context = await browser.new_context(
            locale="en-US",
            viewport={'width': 1280, 'height': 720},
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
        
        print(f"  🌐 Opening {CONCURRENT_TABS} tabs...")
        
        # Create tabs
        pages = []
        for i in range(CONCURRENT_TABS):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=30000)
                pages.append(page)
            except:
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers...")
        
        # Start workers
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                ultra_rename_worker(page, base_name, stop_event, i+1)
            ))
        
        # Run for duration
        await asyncio.sleep(duration)
        stop_event.set()
        
        # Wait for workers
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Close
        await browser.close()
        
        elapsed = time.time() - start_time
        print(f"  🎯 Completed in {elapsed:.1f}s")

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

    return f"⚡ ULTIMATE ULTRA-FAST: {CONCURRENT_TABS} tabs, 1ms delay! Use !ncstop to stop."