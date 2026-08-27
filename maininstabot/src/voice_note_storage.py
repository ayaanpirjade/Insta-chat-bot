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

# ── Cache ──
_vn_cache: Dict[str, str] = {}

def cache_vn(thread_id: str, url: str):
    if url:
        _vn_cache[thread_id] = url

def get_cached_vn(thread_id: str) -> Optional[str]:
    return _vn_cache.get(thread_id)

def extract_vn_url_from_message(msg, cl: Optional[Client] = None, robust: bool = False) -> Optional[str]:
    """
    Extract voice note URL.
    - If robust=False (default): Uses fast, safe paths only (for background caching).
    - If robust=True: Uses deep scanning and API fallback (for explicit commands).
    """
    try:
        if not msg: return None
        
        def get_v(o, k):
            if isinstance(o, dict): return o.get(k)
            return getattr(o, k, None)

        # ── PHASE 1: FAST PATHS (Safe for background) ──
        
        # 1. Direct Voice Media
        vm = get_v(msg, 'voice_media')
        if vm:
            m = get_v(vm, 'media')
            if m:
                audio = get_v(m, 'audio')
                if audio:
                    url = get_v(audio, 'audio_src')
                    if url: return str(url).replace('\\/', '/')
                vv = get_v(m, 'video_versions')
                if vv and isinstance(vv, list) and len(vv) > 0:
                    url = get_v(vv[0], 'url')
                    if url: return str(url).replace('\\/', '/')

        # 2. Clips/Reels (Fast check)
        clip = get_v(msg, 'clip')
        if clip:
            vv = get_v(clip, 'video_versions')
            if vv and isinstance(vv, list) and len(vv) > 0:
                url = get_v(vv[0], 'url')
                if url: return str(url).replace('\\/', '/')

        if not robust: return None

        # ── PHASE 2: ROBUST PATHS (Only for explicit commands) ──

        # 3. Recursive Omni-Scan (Catch-all)
        def omni_scan(obj, depth=0):
            if depth > 10: return None # Reduced depth for safety
            if not obj: return None
            
            if isinstance(obj, str) and obj.startswith('http'):
                low = obj.lower()
                if any(x in low for x in ['.m4a', '.mp3', '.mp4', '/audio', 'audio_src']):
                    return obj.replace('\\/', '/')
            
            if isinstance(obj, dict):
                for k in ['audio_src', 'url', 'video_url', 'audio_url', 'target_url']:
                    res = omni_scan(obj.get(k), depth + 1)
                    if res: return res
                for v in obj.values():
                    if isinstance(v, (str, dict, list, tuple)):
                        res = omni_scan(v, depth + 1)
                        if res: return res
            
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    res = omni_scan(item, depth + 1)
                    if res: return res
            
            # Safe object scan (avoid dir() on complex objects)
            if hasattr(obj, '__dict__') or not isinstance(obj, (str, int, float, bool)):
                for attr in ['voice_media', 'media', 'audio', 'clip', 'video_versions', 'audio_src', 'url']:
                    try:
                        val = getattr(obj, attr, None)
                        if val:
                            res = omni_scan(val, depth + 1)
                            if res: return res
                    except: continue
            return None

        url = omni_scan(msg)
        if url: return url

        # 4. API Fallback
        if cl:
            media_id = None
            if vm: media_id = get_v(vm, 'media_id') or get_v(get_v(vm, 'media'), 'pk')
            if not media_id: media_id = get_v(get_v(msg, 'clip'), 'pk') or get_v(get_v(msg, 'media_share'), 'pk')
            if not media_id: media_id = get_v(msg, 'pk') or get_v(msg, 'id')

            if media_id and str(media_id).isdigit() and 10 <= len(str(media_id)) <= 20:
                try:
                    info = cl.media_info(media_id)
                    if info:
                        return getattr(info, 'video_url', None) or getattr(info, 'audio_url', None) or (info.video_versions[0].get('url') if info.video_versions else None)
                except: pass

        return None
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
    
    # 1. Try Cache First (Fastest)
    vn_url = get_cached_vn(thread_id)
    
    # 2. Try Reply Detection (Robust mode)
    if not vn_url and msg:
        from .reel import get_replied_message
        replied = get_replied_message(cl, thread_id, msg)
        if replied:
            vn_url = extract_vn_url_from_message(replied, cl, robust=True)
    
    if not vn_url:
        return "❌ Please REPLY to a voice note with `!dvn <name>` or use it right after a VN is sent."
    
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
        
        # Clear cache after saving to prevent accidental reuse
        if thread_id in _vn_cache:
            del _vn_cache[thread_id]
            
        return f"✅ **Voice note saved as '{name}'!**\nUse `!pvn {name}` to play it anywhere."
        
    except Exception as e:
        print(f"  ⚠️ Save failed: {e}")
        return f"❌ Failed to save voice note: {str(e)}"

def handle_pvn_command(query: str, user_id: str, username: str, thread_id: str, cl: Client) -> str:
    """
    !pvn <name> - Play a saved voice note with friendly error handling
    """
    name = query.strip().lower().replace(" ", "_")
    
    # Get list of available VNs
    files = [f.replace(".m4a", "") for f in os.listdir(VN_DATA_DIR) if f.endswith(".m4a")]
    
    if not name:
        if not files:
            return "📁 **No saved voice notes found!**\n\nSave one by replying to a VN with `!dvn <name>`"
        return "📁 **Available Voice Notes:**\n\n" + "\n".join([f"• {f}" for f in files]) + f"\n\n💡 Use `!pvn <name>` to play."
    
    file_path = os.path.join(VN_DATA_DIR, f"{name}.m4a")
    if not os.path.exists(file_path):
        if not files:
            return f"❌ **Voice note '{name}' not found!**\n\nStorage is currently empty. Save some VNs first! 🎤"
        
        # Suggest similar names or show list
        return (
            f"❌ **Voice note '{name}' not found!**\n\n"
            f"Available notes are:\n" + ", ".join(files[:10]) + ("..." if len(files) > 10 else "") +
            f"\n\nCheck the name and try again! ✨"
        )
    
    print(f"\n📤 Playing voice note: {name}")
    
    try:
        cl.direct_send_voice(Path(file_path), thread_ids=[str(thread_id)])
        print(f"  ✅ Sent!")
        return "" # Success usually returns no text in this bot's style
    except Exception as e:
        print(f"  ⚠️ Play failed: {e}")
        return f"❌ Failed to send voice note '{name}': {str(e)}"
