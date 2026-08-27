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

def extract_vn_url_from_message(msg, cl: Optional[Client] = None) -> Optional[str]:
    """Extract voice note URL with focused media-id detection and deep scanning"""
    try:
        if not msg:
            return None
        
        def get_val(obj, key):
            if isinstance(obj, dict): return obj.get(key)
            return getattr(obj, key, None)

        # 1. Targeted ID collection (Avoid message item_ids)
        media_ids = []
        
        # Check voice_media container specifically
        vm = get_val(msg, 'voice_media')
        if vm:
            # Try to get media_id or pk from voice_media
            for k in ['media_id', 'pk', 'id']:
                v = get_val(vm, k)
                if v: media_ids.append(str(v))
            # Try deeper in media object
            m = get_val(vm, 'media')
            if m:
                for k in ['pk', 'id', 'media_id']:
                    v = get_val(m, k)
                    if v: media_ids.append(str(v))

        # Check other media containers
        for container in ['clip', 'media_share']:
            c_obj = get_val(msg, container)
            if c_obj:
                for k in ['pk', 'id', 'media_id']:
                    v = get_val(c_obj, k)
                    if v: media_ids.append(str(v))

        # 2. Try API with valid-looking media PKs
        if cl:
            for mid in list(set(media_ids)):
                try:
                    # Media PKs are typically digits and not extremely long (unlike item_ids)
                    if mid.isdigit() and 10 <= len(mid) <= 20:
                        print(f"  🔍 Fetching fresh media info for ID: {mid}")
                        info = cl.media_info(mid)
                        if info:
                            for attr in ['video_url', 'audio_url']:
                                url = getattr(info, attr, None)
                                if url: return str(url)
                            if hasattr(info, 'video_versions') and info.video_versions:
                                return str(info.video_versions[0].get('url'))
                except: pass

        # 3. Recursive Deep Scan (Catch-All for embedded URLs)
        def deep_scan(obj, depth=0):
            if depth > 15: return None
            if not obj: return None
            
            if isinstance(obj, str):
                low = obj.lower()
                if low.startswith('http'):
                    if any(x in low for x in ['.m4a', '.mp3', '.mp4', '/audio', 'audio_src', 'video_versions', 'dash']):
                         return obj.replace('\\/', '/').strip('"')
            
            if isinstance(obj, dict):
                for k in ['audio_src', 'url', 'video_url', 'audio_url', 'target_url', 'uri']:
                    res = deep_scan(obj.get(k), depth + 1)
                    if res: return res
                for v in obj.values():
                    res = deep_scan(v, depth + 1)
                    if res: return res
            
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    res = deep_scan(item, depth + 1)
                    if res: return res
            
            try:
                # Prioritize common media attributes
                for attr in ['voice_media', 'media', 'audio', 'clip', 'video_versions']:
                    val = getattr(obj, attr, None)
                    if val:
                        res = deep_scan(val, depth + 1)
                        if res: return res
                
                # Scan other attributes
                for attr in dir(obj):
                    if attr.startswith('_') or attr in ['voice_media', 'media', 'audio', 'clip', 'video_versions']: 
                        continue
                    try:
                        val = getattr(obj, attr)
                        if not val or callable(val): continue
                        res = deep_scan(val, depth + 1)
                        if res: return res
                    except: continue
            except: pass
            return None

        return deep_scan(msg)
    except Exception as e:
        print(f"  ⚠️ Extract failed: {e}")
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
    
    vn_url = extract_vn_url_from_message(replied, cl)
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
