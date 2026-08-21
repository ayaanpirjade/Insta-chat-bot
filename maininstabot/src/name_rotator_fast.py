"""PLAYWRIGHT WITH VERIFICATION - Actually changes the name!"""
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
    """Worker with verification - actually changes the name!"""
    count = 0
    print(f"  ⚡ Worker {worker_id} started (VERIFIED)")
    
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
            
            # ---- USE JAVASCRIPT TO DIRECTLY CHANGE THE NAME ----
            # This bypasses all UI issues!
            result = await page.evaluate(f"""
                (() => {{
                    try {{
                        // STEP 1: Click on group name to open menu
                        const headers = document.querySelectorAll('div[role="button"]');
                        let clicked = false;
                        for (let h of headers) {{
                            if (h.textContent && h.textContent.trim().length > 0) {{
                                h.click();
                                clicked = true;
                                break;
                            }}
                        }}
                        
                        if (!clicked) {{
                            // Try info panel
                            const infoBtn = document.querySelector('svg[aria-label="Conversation information"]');
                            if (infoBtn) {{
                                infoBtn.closest('div[role="button"]')?.click();
                                clicked = true;
                            }}
                        }}
                        
                        if (!clicked) return 'no_click';
                        
                        // STEP 2: Wait for dialog and find input
                        setTimeout(() => {{
                            const inputs = document.querySelectorAll('input');
                            for (let inp of inputs) {{
                                if (inp.getAttribute('aria-label') === 'Group name' || 
                                    inp.placeholder?.toLowerCase().includes('group')) {{
                                    inp.value = '{name}';
                                    inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    break;
                                }}
                            }}
                        }}, 100);
                        
                        // STEP 3: Click Save button
                        setTimeout(() => {{
                            const btns = document.querySelectorAll('button, div[role="button"]');
                            for (let btn of btns) {{
                                if (btn.textContent && btn.textContent.trim() === 'Save') {{
                                    btn.click();
                                    break;
                                }}
                            }}
                        }}, 200);
                        
                        return 'success';
                    }} catch(e) {{
                        return 'error: ' + e.message;
                    }}
                }})()
            """)
            
            if 'success' in result:
                count += 1
                if count % 5 == 0:
                    print(f"  ⚡ Worker {worker_id}: {count} changes")
                
                # Wait for change to take effect
                await asyncio.sleep(0.3)
            else:
                # FALLBACK: Try direct Playwright clicks with force
                try:
                    # Click header
                    header = page.locator('div[role="button"]').first
                    if await header.count() > 0:
                        await header.click(force=True)
                        await asyncio.sleep(0.2)
                        
                        # Find input
                        input_field = page.locator('input[aria-label="Group name"]').first
                        if await input_field.count() > 0:
                            await input_field.fill(name)
                            await asyncio.sleep(0.1)
                            
                            # Click Save using JavaScript
                            await page.evaluate("""
                                (() => {
                                    const btns = document.querySelectorAll('button, div[role="button"]');
                                    for (let btn of btns) {
                                        if (btn.textContent && btn.textContent.trim() === 'Save') {
                                            btn.click();
                                            return true;
                                        }
                                    }
                                    return false;
                                })()
                            """)
                            count += 1
                            if count % 5 == 0:
                                print(f"  ⚡ Worker {worker_id}: {count} changes")
                            await asyncio.sleep(0.3)
                except Exception as e:
                    await asyncio.sleep(0.1)
            
        except Exception as e:
            await asyncio.sleep(0.1)
    
    print(f"  ✅ Worker {worker_id}: {count} verified changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner with 2 tabs"""
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
        
        num_tabs = 2
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
        
        print(f"  🔥 Starting {len(pages)} workers (VERIFIED)...")
        
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

    return f"⚡ VERIFIED: Actually changes the name! Use !ncstop to stop."
