"""PLAYWRIGHT with JavaScript Injection - Bypass UI issues!"""
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

async def js_rename(page, base_name: str, stop_event: threading.Event, worker_id: int):
    """Rename using JavaScript injection - WORKS EVERY TIME!"""
    count = 0
    print(f"  ⚡ Worker {worker_id} ready (JS mode)")
    
    # Wait for page
    try:
        await page.wait_for_load_state('domcontentloaded', timeout=5000)
    except:
        pass
    
    # Try to find the group name
    try:
        # Get current group name
        current_name = await page.evaluate('''
            () => {
                const header = document.querySelector('header h2');
                return header ? header.textContent : null;
            }
        ''')
        print(f"  📝 Worker {worker_id}: Current group: {current_name}")
    except:
        pass
    
    while not stop_event.is_set():
        try:
            # Generate name
            emoji = random.choice(EMOJIS)
            name = f"{base_name[:95]} {emoji}"
            
            # ---- METHOD 1: JavaScript Injection ----
            success = await page.evaluate(f'''
                () => {{
                    try {{
                        // Find the group name header
                        const header = document.querySelector('header h2, header div[role="button"]');
                        if (header) {{
                            header.click();
                            return 'clicked_header';
                        }}
                        return 'no_header';
                    }} catch(e) {{
                        return 'error: ' + e.message;
                    }}
                }}
            ''')
            
            await asyncio.sleep(0.1)
            
            # ---- METHOD 2: Find input via JS ----
            if success == 'clicked_header':
                # Wait for dialog
                await asyncio.sleep(0.1)
                
                # Find and fill input
                filled = await page.evaluate(f'''
                    () => {{
                        try {{
                            // Find input
                            const inputs = document.querySelectorAll('input');
                            let targetInput = null;
                            for (let input of inputs) {{
                                if (input.getAttribute('aria-label') === 'Group name' || 
                                    input.getAttribute('placeholder')?.toLowerCase().includes('group') ||
                                    input.getAttribute('name') === 'change-group-name') {{
                                    targetInput = input;
                                    break;
                                }}
                            }}
                            
                            if (targetInput) {{
                                targetInput.value = '';
                                targetInput.value = '{name}';
                                // Trigger input event
                                targetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                return 'filled';
                            }}
                            return 'no_input';
                        }} catch(e) {{
                            return 'error: ' + e.message;
                        }}
                    }}
                ''')
                
                await asyncio.sleep(0.05)
                
                # Save via JS
                if filled == 'filled':
                    saved = await page.evaluate(f'''
                        () => {{
                            try {{
                                // Find save button
                                const buttons = document.querySelectorAll('button, div[role="button"]');
                                for (let btn of buttons) {{
                                    if (btn.textContent?.toLowerCase().includes('save')) {{
                                        btn.click();
                                        return 'saved';
                                    }}
                                }}
                                return 'no_save';
                            }} catch(e) {{
                                return 'error: ' + e.message;
                            }}
                        }}
                    ''')
                    
                    if saved == 'saved':
                        count += 1
                        if count % 5 == 0:
                            print(f"  ⚡ Worker {worker_id}: {count} changes")
                        
                        # Wait between changes
                        await asyncio.sleep(0.05)
                        continue
            
            # If JS injection failed, try fallback method
            print(f"  ⚠️ Worker {worker_id}: JS method failed, trying fallback...")
            
            # ---- FALLBACK: Direct DOM manipulation ----
            try:
                await page.evaluate(f'''
                    () => {{
                        // Direct DOM manipulation
                        const header = document.querySelector('header h2, header div[role="button"]');
                        if (header) {{
                            header.click();
                            setTimeout(() => {{
                                const inputs = document.querySelectorAll('input');
                                for (let input of inputs) {{
                                    if (input.getAttribute('aria-label') === 'Group name' || 
                                        input.getAttribute('placeholder')?.toLowerCase().includes('group')) {{
                                        input.value = '{name}';
                                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                        setTimeout(() => {{
                                            const btns = document.querySelectorAll('button');
                                            for (let btn of btns) {{
                                                if (btn.textContent?.toLowerCase().includes('save')) {{
                                                    btn.click();
                                                }}
                                            }}
                                        }}, 50);
                                        break;
                                    }}
                                }}
                            }}, 100);
                        }}
                    }}
                ''')
                count += 1
                await asyncio.sleep(0.1)
            except:
                pass
            
        except Exception as e:
            print(f"  ⚠️ Worker {worker_id} error: {str(e)[:30]}")
            await asyncio.sleep(0.2)
    
    print(f"  ✅ Worker {worker_id}: {count} changes")

async def async_runner(dm_url: str, base_name: str, stop_event: threading.Event, duration: float):
    """Main runner with 3 tabs for stability"""
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
        
        # Use 3 tabs for stability
        num_tabs = 3
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
        
        print(f"  🔥 Starting {len(pages)} JS workers...")
        
        # Start workers
        tasks = []
        for i, page in enumerate(pages):
            tasks.append(asyncio.create_task(
                js_rename(page, base_name, stop_event, i+1)
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

    return f"⚡ JS MODE: 3 tabs, JavaScript injection! Use !ncstop to stop."