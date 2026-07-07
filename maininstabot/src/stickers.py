# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          🎨 AYAAN AI - Sticker & GIF
#          (Optional - Not Integrated)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import re
import time
import json
import random
import os
import sys
import logging
import requests
from typing import Optional, Dict, Any
from instagrapi import Client

GRAPHQL_URL = "https://www.instagram.com/api/graphql"
STICKER_SEND_DOC_ID = "32089613413987432"

POPULAR_STICKERS = {
    "ok": "3rxRkNNqrx7BKvcS9O",
    "heart": "3rxRkNNqrx7BKvcS9O",
    "love": "3rxRkNNqrx7BKvcS9O",
}

def send_native_sticker(client: Client, thread_id: str, sticker_id: str) -> bool:
    try:
        cookies = {}
        for cookie in client.private.cookies:
            cookies[cookie.name] = cookie.value
        
        variables = {
            "data": {
                "is_random": False,
                "is_sticker": True,
                "reply_to_message_id": None,
                "sticker_id": sticker_id
            },
            "send_data": {
                "forwarded_from_thread_id": None,
                "is_forwarded_from_own_message": None,
                "offline_threading_id": str(int(time.time() * 1000)),
                "recipient_users": None,
                "reply_to_message_id": None,
                "send_attribution": "thread_view",
                "thread_id": str(thread_id)
            }
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "x-ig-app-id": "936619743392459",
            "x-csrftoken": cookies.get("csrftoken", ""),
            "x-fb-friendly-name": "IGDirectAnimatedMediaSendMutation",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/direct/inbox/",
        }
        
        data = {
            "doc_id": STICKER_SEND_DOC_ID,
            "variables": json.dumps(variables),
        }
        
        session = requests.Session()
        session.cookies.update(cookies)
        
        response = session.post(GRAPHQL_URL, headers=headers, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if "errors" not in result:
                return True
        return False
        
    except Exception as e:
        print(f"Sticker send failed: {e}")
        return False

def handle_sticker_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> Optional[str]:
    query = query.strip()
    if not query:
        return "🎨 Please specify a sticker.\nExample: !sticker ok"
    
    sticker_id = None
    for key, sid in POPULAR_STICKERS.items():
        if key in query.lower() or query.lower() in key:
            sticker_id = sid
            break
    
    if not sticker_id:
        return f"❌ No sticker found for '{query}'\nAvailable: {', '.join(POPULAR_STICKERS.keys())}"
    
    sent = send_native_sticker(cl, thread_id, sticker_id)
    return None if sent else "❌ Failed to send sticker."