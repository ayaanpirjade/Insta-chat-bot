"""ULTRA PLAYWRIGHT - 100+ changes/second, Termux Optimized!"""
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
    """Start Xvfb for headless display (required for Termux)"""
    global _xvfb_process
    try:
        # Check if Xvfb is running
        result = subprocess.run(['pgrep', '-f', 'Xvfb :99'], capture_output=True)
        if result.returncode == 0:
            os.environ['DISPLAY'] = ':99'
            return True
        
        # Start Xvfb
        _xvfb_process = subprocess.Popen(
            ['Xvfb', ':99', '-screen', '0', '1280x720x24', '-ac'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        os.environ['DISPLAY'] = ':99'
        time.sleep(1)
        return True
    except:
        return False

async def ultra_fast_rename(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """ULTRA-FAST rename worker - 100+ changes/sec"""
    count = 0
    errors = 0
    print(f"  ⚡ Worker {worker_id} started")
    
    # Pre-load page
    try:
        await page.wait_for_load_state('networkidle', timeout=5000)
    except:
        pass
    
    # Pre-find elements for speed
    header_selector = 'header h2, header div[role="button"]'
    info_selector = 'svg[aria-label="Conversation information"]'
    rename_btn_selector = 'button:has-text("Change name"), button:has-text("Change group name")'
    input_selector = 'input[aria-label="Group name"], input[name="change-group-name"], [role="dialog"] input[type="text"]'
    save_selector = 'button:has-text("Save"), div[role="button"]:has-text("Save")'
    
    used_names = set()
    
    while not stop_event.is_set():
        try:
            # Generate name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            if name in used_names:
                name = f"{name} {random.randint(1,999)}"
            used_names.add(name)
            if len(used_names) > 50:
                used_names.clear()
            
            # ---- STEP 1: Open rename dialog (ULTRA-FAST) ----
            clicked = False
            
            # Method 1: Click header (fastest)
            try:
                header = page.locator(header_selector).first
                if await header.count() > 0:
                    await header.click(force=True, no_wait_after=True)
                    await asyncio.sleep(0.001)
                    clicked = True
            except:
                pass
            
            # Method 2: Info panel (if header fails)
            if not clicked:
                try:
                    info_btn = page.locator(info_selector).first
                    if await info_btn.count() > 0:
                        await info_btn.click(force=True, no_wait_after=True)
                        await asyncio.sleep(0.001)
                        rename_btn = page.locator(rename_btn_selector).first
                        if await rename_btn.count() > 0:
                            await rename_btn.click(force=True, no_wait_after=True)
                            await asyncio.sleep(0.001)
                            clicked = True
                except:
                    pass
            
            if not clicked:
                errors += 1
                if errors % 10 == 0:
                    print(f"  ⚠️ Worker {worker_id}: Dialog open failed")
                await asyncio.sleep(0.001)
                continue
            
            # ---- STEP 2: Fill input (ULTRA-FAST) ----
            input_field = page.locator(input_selector).first
            if await input_field.count() > 0:
                try:
                    await input_field.fill(name, timeout=50)
                except:
                    try:
                        await input_field.click(force=True)
                        await input_field.fill(name, timeout=50)
                    except:
                        pass
                await asyncio.sleep(0.001)
            
            # ---- STEP 3: Click Save (ULTRA-FAST) ----
            save_btn = page.locator(save_selector).first
            if await save_btn.count() > 0:
                await save_btn.click(force=True, no_wait_after=True)
                count += 1
                errors = 0
                
                if count % 50 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} changes")
                
                # MINIMAL delay (1ms)
                await asyncio.sleep(0.001)
            else:
                errors += 1
                await asyncio.sleep(0.001)
            
        except Exception as e:
            errors += 1
            if errors % 20 == 0:
                print(f"  ⚠️ Worker {worker_id} error: {str(e)[:30]}")
            await asyncio.sleep(0.001)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner with 20 concurrent tabs for max speed"""
    # Start Xvfb
    start_xvfb()
    
    async with async_playwright() as p:
        # Launch with optimized args
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
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-ipc-flooding-protection',
                '--disable-sync',
                '--disable-default-apps',
                '--disable-extensions',
                '--disable-component-extensions-with-background-pages',
                '--disable-plugins',
                '--disable-images',  # Speed up! Don't load images
                '--blink-settings=imagesEnabled=false',
                '--disk-cache-size=1'
            ]
        )
        
        # Optimized context
        context = await browser.new_context(
            viewport={'width': 800, 'height': 600},  # Smaller viewport = faster
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
            }
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
        
        # Open 20 tabs for maximum speed
        num_tabs = 20
        print(f"  🌐 Opening {num_tabs} tabs...")
        
        pages = []
        for i in range(num_tabs):
            page = await context.new_page()
            try:
                await page.goto(dm_url, wait_until='domcontentloaded', timeout=10000)
                await page.wait_for_load_state('networkidle', timeout=3000)
                pages.append(page)
                if (i+1) % 5 == 0:
                    print(f"  ✅ {i+1} tabs loaded")
            except:
                pages.append(page)
        
        print(f"  🔥 Starting {len(pages)} workers (ULTRA SPEED)...")
        print(f"  ⚡ Target: 100+ changes/second!")
        
        # Start all workers
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                ultra_fast_rename(page, base_name, stop_event, i+1)
            ))
        
        # Run for duration
        await asyncio.sleep(duration)
        stop_event.set()
        
        # Wait for workers to finish
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

    return f"⚡ ULTRA SPEED: 20 tabs, 1ms delay! Target: 100+ changes/sec! Use !ncstop to stop."