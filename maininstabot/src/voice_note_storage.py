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
    """Extract voice note URL with 'God-Mode' exhaustive detection"""
    try:
        if not msg:
            return None
        
        def get_val(obj, key):
            if isinstance(obj, dict): return obj.get(key)
            return getattr(obj, key, None)

        # 1. Exhaustive ID collection for API fallback
        potential_ids = []
        
        # Check direct properties
        for attr in ['pk', 'id', 'item_id', 'media_id']:
            val = get_val(msg, attr)
            if val: potential_ids.append(str(val))
            
        # Check nested media properties
        for container in ['voice_media', 'clip', 'media_share', 'media']:
            c_obj = get_val(msg, container)
            if c_obj:
                for attr in ['pk', 'id', 'media_id']:
                    val = get_val(c_obj, attr)
                    if val: potential_ids.append(str(val))
                # Even deeper
                m_obj = get_val(c_obj, 'media')
                if m_obj:
                    for attr in ['pk', 'id', 'media_id']:
                        val = get_val(m_obj, attr)
                        if val: potential_ids.append(str(val))

        # 2. Try API with all collected IDs
        if cl:
            for mid in list(set(potential_ids)):
                try:
                    # Only try IDs that look like Instagram media PKs (long digits)
                    if mid.isdigit() and len(mid) > 10:
                        print(f"  🔍 Trying API media_info for ID: {mid}")
                        info = cl.media_info(mid)
                        if info:
                            # Check all possible URL locations in media info
                            for attr in ['video_url', 'audio_url']:
                                url = getattr(info, attr, None)
                                if url: return str(url)
                            if hasattr(info, 'video_versions') and info.video_versions:
                                return str(info.video_versions[0].get('url'))
                except: pass

        # 3. Final Recursive Scan (The Catch-All)
        def deep_scan(obj, depth=0):
            if depth > 15: return None
            if not obj: return None
            
            # String URL check
            if isinstance(obj, str):
                low = obj.lower()
                # Must look like a URL
                if low.startswith('http'):
                    # Check for common audio/video extensions or Instagram specific paths
                    if any(x in low for x in ['.m4a', '.mp3', '.mp4', '/audio', 'audio_src', 'video_versions', 'dash']) or 'instagram.com' in low:
                         return obj.replace('\\/', '/').strip('"')
            
            # Dictionary scan
            if isinstance(obj, dict):
                # Check priority keys first
                for k in ['audio_src', 'url', 'video_url', 'audio_url', 'target_url', 'uri']:
                    res = deep_scan(obj.get(k), depth + 1)
                    if res: return res
                for v in obj.values():
                    res = deep_scan(v, depth + 1)
                    if res: return res
            
            # List scan
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    res = deep_scan(item, depth + 1)
                    if res: return res
            
            # Object attribute scan
            try:
                for attr in dir(obj):
                    if attr.startswith('_'): continue
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
        print(f"  ⚠️ God-Mode extract failed: {e}")
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
