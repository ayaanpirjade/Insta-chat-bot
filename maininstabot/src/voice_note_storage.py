# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI - Voice Note Storage
#          !dvn (Save) & !pvn (Play)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from instagrapi import Client

# ── Constants ──
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VN_DATA_DIR = os.path.join(BASE_DIR, "data", "voice_notes")
os.makedirs(VN_DATA_DIR, exist_ok=True)

def extract_vn_url_from_message(msg) -> Optional[str]:
    """Extract voice note URL with 'Omega-Robust' recursive scanning"""
    try:
        if not msg:
            return None
        
        def find_url(obj, depth=0):
            if depth > 10: return None
            if not obj: return None
            
            # 1. If string, check for audio/video URL patterns
            if isinstance(obj, str):
                low = obj.lower()
                # Check for common audio/video extensions or Instagram specific paths
                if any(x in low for x in ['.m4a', '.mp3', '.mp4', '/audio', 'audio_src', 'video_versions', 'dash']):
                     # Must look like a URL
                     if low.startswith('http'):
                         return obj
            
            # 2. If dict, search values
            if isinstance(obj, dict):
                # Prioritize common keys
                for priority_key in ['audio_src', 'url', 'target_url', 'audio_url', 'video_url']:
                    if priority_key in obj:
                        res = find_url(obj[priority_key], depth + 1)
                        if res: return res
                for v in obj.values():
                    res = find_url(v, depth + 1)
                    if res: return res
            
            # 3. If list/tuple, search items
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    res = find_url(item, depth + 1)
                    if res: return res
            
            # 4. If object with attributes (Instagrapi models)
            try:
                # Prioritize common attributes
                for attr in ['voice_media', 'media', 'audio', 'clip', 'video_versions']:
                    val = getattr(obj, attr, None)
                    if val:
                        res = find_url(val, depth + 1)
                        if res: return res
                
                # Full scan of attributes
                for attr in dir(obj):
                    if attr.startswith('_'): continue
                    try:
                        val = getattr(obj, attr)
                        if not val or callable(val): continue
                        res = find_url(val, depth + 1)
                        if res: return res
                    except: continue
            except: pass
            
            return None

        url = find_url(msg)

        if url:
            # Clean URL (unescape slashes and remove JSON escapes)
            url = url.replace('\\/', '/')
            if url.startswith('"') and url.endswith('"'):
                url = url[1:-1]
            return url
            
        return None
    except Exception as e:
        print(f"  ⚠️ VN extract failed: {e}")
        return None

def handle_dvn_command(query: str, user_id: str, username: str, thread_id: str, cl: Client, msg=None) -> str:
    """
    !dvn <name> - Save a replied voice note
    """
    name = query.strip().lower().replace(" ", "_")
    if not name:
        return "📝 Please provide a name to save the voice note.\nExample: !dvn funny_laugh"
    
    if not msg:
        return "❌ This command must be used as a reply to a voice note."

    # Get replied message
    from .reel import get_replied_message
    replied = get_replied_message(cl, thread_id, msg)
    
    if not replied:
        return "❌ Please REPLY to a voice note with !dvn <name>"
    
    vn_url = extract_vn_url_from_message(replied)
    if not vn_url:
        return "❌ The replied message is not a valid voice note."
    
    print(f"\n📥 Saving voice note as: {name}")
    
    try:
        file_path = os.path.join(VN_DATA_DIR, f"{name}.m4a")
        
        # Download
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(vn_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
            
        print(f"  ✅ Saved to: {file_path}")
        return f"✅ **Voice note saved as '{name}'!**\nUse `!pvn {name}` to play it anywhere."
        
    except Exception as e:
        print(f"  ⚠️ Save failed: {e}")
        return f"❌ Failed to save voice note: {str(e)}"

def handle_pvn_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> str:
    """
    !pvn <name> - Play a saved voice note
    """
    name = query.strip().lower().replace(" ", "_")
    if not name:
        # List available VNs if no name provided
        files = [f.replace(".m4a", "") for f in os.listdir(VN_DATA_DIR) if f.endswith(".m4a")]
        if not files:
            return "📁 No saved voice notes found. Save one with `!dvn <name>`"
        return "📁 **Saved Voice Notes:**\n" + ", ".join(files) + f"\n\nUse `!pvn <name>` to play."
    
    file_path = os.path.join(VN_DATA_DIR, f"{name}.m4a")
    if not os.path.exists(file_path):
        return f"❌ Voice note '{name}' not found."
    
    print(f"\n📤 Playing voice note: {name}")
    
    try:
        cl.direct_send_voice(Path(file_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Sent!")
        return "" # Success usually returns no text in this bot's style
    except Exception as e:
        print(f"  ⚠️ Play failed: {e}")
        return f"❌ Failed to send voice note '{name}': {str(e)}"
