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
    """Extract voice note URL from a message object with multiple detection layers"""
    try:
        if not msg:
            return None
        
        # 1. Check item_type - if it's voice_media, it's definitely a VN
        item_type = getattr(msg, 'item_type', '').lower()
        
        # 2. Layered detection across different instagrapi message shapes
        url = None
        
        # Method A: voice_media.media.audio
        if hasattr(msg, 'voice_media') and msg.voice_media:
            vm = msg.voice_media
            if hasattr(vm, 'media') and vm.media:
                m = vm.media
                if hasattr(m, 'audio') and m.audio:
                    url = m.audio.get('audio_src')
                if not url and hasattr(m, 'video_versions') and m.video_versions:
                    url = m.video_versions[0].get('url')
        
        # Method B: clip (shared reels)
        if not url and hasattr(msg, 'clip') and msg.clip:
            c = msg.clip
            if hasattr(c, 'video_versions') and c.video_versions:
                url = c.video_versions[0].get('url')
        
        # Method C: media_share
        if not url and hasattr(msg, 'media_share') and msg.media_share:
            ms = msg.media_share
            if hasattr(ms, 'video_versions') and ms.video_versions:
                url = ms.video_versions[0].get('url')
        
        # Method D: direct audio/video versions on the message
        if not url and hasattr(msg, 'video_versions') and msg.video_versions:
            url = msg.video_versions[0].get('url')
        
        if not url and hasattr(msg, 'audio') and msg.audio:
            url = getattr(msg.audio, 'audio_src', None)

        # Method E: Raw XMA detection (for newer Instagram formats)
        if not url and hasattr(msg, 'raw_xma') and msg.raw_xma:
            xma = msg.raw_xma
            if isinstance(xma, dict):
                # Look for audio/clip references in XMA
                for key in ['xma_audio', 'xma_clip', 'xma_media_share']:
                    items = xma.get(key, [])
                    if items and isinstance(items, list):
                        content = items[0].get('serialized_content_ref')
                        if content:
                            try:
                                import json
                                data = json.loads(content) if isinstance(content, str) else content
                                url = data.get('target_url') or data.get('audio_url')
                                if url: break
                            except: pass

        # Method F: Recursive search (Catch-all)
        if not url:
            def find_url(obj, depth=0):
                if depth > 5: return None
                if isinstance(obj, str) and ('instagram.com' in obj or 'cdninstagram.com' in obj) and ('/audio' in obj or '.m4a' in obj or '.mp3' in obj or 'audio_src' in obj):
                    return obj
                if isinstance(obj, dict):
                    for v in obj.values():
                        res = find_url(v, depth + 1)
                        if res: return res
                if hasattr(obj, '__dict__'):
                    for v in vars(obj).values():
                        res = find_url(v, depth + 1)
                        if res: return res
                if isinstance(obj, list):
                    for v in obj:
                        res = find_url(v, depth + 1)
                        if res: return res
                return None
            url = find_url(msg)

        if url:
            # Clean URL (unescape slashes)
            url = url.replace('\\/', '/')
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
