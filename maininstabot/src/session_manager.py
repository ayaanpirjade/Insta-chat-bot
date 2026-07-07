# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#      Simple Session Manager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import config
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientForbiddenError


class RotatingSessionManager:
    """
    Simple Session Manager - NO ROTATION
    """
    
    def __init__(self):
        self._client = None
        self._username = None
        self._user_id = None
        self._settings_file = "session_settings.json"
        self._last_error = 0
        self._error_count = 0
    
    def get_client(self) -> tuple[Client, str]:
        """Get active client (single session only)"""
        if self._client is None:
            session_id = config.SESSION_ID.split(",")[0].strip() if hasattr(config, 'SESSION_ID') else None
            
            if not session_id:
                raise ValueError("No SESSION_ID found in .env")
            
            self._client = self._create_client(session_id)
        
        return self._client, self._username
    
    def _create_client(self, session_id: str) -> Client:
        """Create and login client"""
        cl = Client()
        cl.set_user_agent("Instagram 410.0.0.0.96 Android (33/13; 480dpi; 1080x2400; xiaomi; M2007J20CG; surya; qcom; en_US; 641123490)")
        
        # Try to load cached settings
        if os.path.exists(self._settings_file):
            try:
                cl.load_settings(self._settings_file)
                print("📁 Loaded cached settings")
            except Exception as e:
                print(f"⚠️ Could not load settings: {e}")
        
        try:
            print("🔑 Logging in...")
            cl.login_by_sessionid(session_id)
            
            # Get user info
            me = cl.account_info()
            self._username = me.username
            self._user_id = str(me.pk)
            
            # Save settings
            cl.dump_settings(self._settings_file)
            
            print(f"✅ Logged in as @{self._username} (ID: {self._user_id})")
            return cl
            
        except ClientForbiddenError as e:
            print(f"❌ Login failed: Account blocked or rate limited!")
            print("📌 This usually means:")
            print("   1. Too many requests from this IP")
            print("   2. Account temporarily blocked")
            print("   3. Need to change IP address")
            print("\n💡 Solutions:")
            print("   • Use VPN or mobile hotspot")
            print("   • Wait 30-60 minutes")
            print("   • Use a different Instagram account")
            raise
        except LoginRequired as e:
            print(f"❌ Login failed: Session expired! {e}")
            print("📌 Please update SESSION_ID in .env file")
            raise
        except Exception as e:
            print(f"❌ Login failed: {e}")
            raise
    
    def get_my_id(self) -> str:
        """Get current user ID"""
        if self._user_id is None:
            _, _ = self.get_client()
        return self._user_id
    
    def rotate_and_get(self):
        """NO ROTATION - just return current client"""
        print("⚠️ Rotation disabled - using single session")
        return self.get_client()