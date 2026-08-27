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
    """Extract voice note URL using 'Direct-Hit' layered detection"""
    try:
        if not msg:
            return None
        
        def get_v(o, k):
            if isinstance(o, dict): return o.get(k)
            return getattr(o, k, None)

        # 1. Direct Hit: Check common instagrapi voice note paths
        # voice_media -> media -> audio -> audio_src
        vm = get_v(msg, 'voice_media')
        if vm:
            m = get_v(vm, 'media')
            if m:
                audio = get_v(m, 'audio')
                if audio:
                    url = get_v(audio, 'audio_src')
                    if url: return str(url).replace('\\/', '/')
                
                # Check video_versions (sometimes VNs are served as video)
                vv = get_v(m, 'video_versions')
                if vv and isinstance(vv, list) and len(vv) > 0:
                    url = get_v(vv[0], 'url')
                    if url: return str(url).replace('\\/', '/')

        # 2. Check clip (shared reels)
        clip = get_v(msg, 'clip')
        if clip:
            vv = get_v(clip, 'video_versions')
            if vv and isinstance(vv, list) and len(vv) > 0:
                url = get_v(vv[0], 'url')
                if url: return str(url).replace('\\/', '/')

        # 3. Recursive Quick Scan (Now with object support)
        def deep_search(obj, depth=0):
            if depth > 8: return None
            if not obj: return None
            
            if isinstance(obj, str) and obj.startswith('http'):
                low = obj.lower()
                if any(x in low for x in ['.m4a', '.mp3', '.mp4', '/audio', 'audio_src']):
                    return obj.replace('\\/', '/')
            
            if isinstance(obj, dict):
                for k in ['audio_src', 'url', 'audio_url', 'video_url', 'target_url']:
                    res = deep_search(obj.get(k), depth + 1)
                    if res: return res
                for v in obj.values():
                    if not isinstance(v, (str, dict, list, tuple)): continue
                    res = deep_search(v, depth + 1)
                    if res: return res
            
            if isinstance(obj, (list, tuple)):
                for item in obj:
                    res = deep_search(item, depth + 1)
                    if res: return res
            
            # If it's an object, check attributes
            if hasattr(obj, '__dict__') or not isinstance(obj, (str, int, float, bool)):
                for attr in ['voice_media', 'media', 'audio', 'clip', 'video_versions', 'audio_src', 'url']:
                    try:
                        val = getattr(obj, attr, None)
                        if val:
                            res = deep_search(val, depth + 1)
                            if res: return res
                    except: continue
            return None

        url = deep_search(msg)
        if url: return url

        # 4. API Fallback (Only if we have a valid media ID)
        if cl:
            media_id = None
            if vm:
                media_id = get_v(vm, 'media_id') or get_v(get_v(vm, 'media'), 'pk')
            if not media_id and clip:
                media_id = get_v(clip, 'pk') or get_v(clip, 'id')
            if not media_id:
                media_id = get_v(msg, 'pk') or get_v(msg, 'id')

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
