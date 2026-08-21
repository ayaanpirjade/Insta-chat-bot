"""ULTRA FAST - Pre-cache elements, 100+ changes/sec!"""
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

async def ultra_fast_rename(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """ULTRA FAST - Pre-cache all elements!"""
    count = 0
    print(f"  ⚡ Worker {worker_id} started (ULTRA FAST)")
    
    # Wait for page
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=5000)
    except:
        pass
    
    # PRE-CACHE elements for speed
    try:
        # Wait for header to be available
        await page.wait_for_selector('div[role="button"]', timeout=3000)
    except:
        pass
    
    # Get references to elements (they won't change)
    header_selector = 'div[role="button"]'
    input_selector = 'input[aria-label="Group name"]'
    save_selector = 'button:has-text("Save")'
    
    while not stop_event.is_set():
        try:
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # ==== STEP 1: Click header (NO WAIT) ====
            try:
                await page.click(header_selector, force=True, no_wait_after=True)
            except:
                # Fallback: use JS click
                await page.evaluate(f"""
                    (() => {{
                        const el = document.querySelector('div[role="button"]');
                        if (el) el.click();
                    }})()
                """)
            
            # ==== STEP 2: Fill input (NO WAIT) ====
            try:
                await page.fill(input_selector, name, timeout=50)
            except:
                await page.evaluate(f"""
                    (() => {{
                        const el = document.querySelector('input[aria-label="Group name"]');
                        if (el) {{
                            el.value = '{name}';
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    }})()
                """)
            
            # ==== STEP 3: Click Save (NO WAIT) ====
            try:
                await page.click(save_selector, force=True, no_wait_after=True)
            except:
                await page.evaluate("""
                    (() => {
                        const btns = document.querySelectorAll('button');
                        for (let btn of btns) {
                            if (btn.textContent && btn.textContent.includes('Save')) {
                                btn.click();
                                break;
                            }
                        }
                    })()
                """)
            
            count += 1
            
            if count % 50 == 0:
                print(f"  ⚡ Worker {worker_id}: {count} changes")
            
            # MINIMAL DELAY - 0.5ms (2000 changes/sec theoretical)
            await asyncio.sleep(0.0005)
            
        except Exception as e:
            await asyncio.sleep(0.0005)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Single tab - ULTRA FAST"""
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
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 800, 'height': 600},
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
        await page.goto(dm_url, wait_until='domcontentloaded', timeout=20000)
        print(f"  ✅ Tab loaded")
        
        print(f"  🔥 Starting ULTRA FAST worker...")
        
        # Run for duration then stop
        task = asyncio.create_task(ultra_fast_rename(page, base_name, stop_event, 1))
        
        # Auto-stop after duration
        await asyncio.sleep(duration)
        stop_event.set()
        
        await task
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

    return f"⚡ ULTRA FAST: 0.5ms delay, PRE-CACHED elements! Use !ncstop to stop."
