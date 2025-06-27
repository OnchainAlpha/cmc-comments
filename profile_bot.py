#!/usr/bin/env python3
"""
CMC Profile Interaction Bot - Visits stored profiles and likes their posts
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager

class CMCProfileInteractionBot:
    def __init__(self, use_account_rotation=True):
        print("🤖 CMC Profile Interaction Bot initialized")
        self.profile_manager = ProfileManager()
        self.use_account_rotation = use_account_rotation
        self.profiles_storage_file = "stored_cmc_profiles.json"
        self.stored_profiles = self._load_stored_profiles()
        self.driver = None
        print(f"   Stored Profiles: {len(self.stored_profiles)}")
        self._load_profile()

    def _load_profile(self):
        """Load a browser profile"""
        try:
            profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            if not profiles:
                raise Exception("No CMC profiles found")
            profile_name = profiles[0]
            print(f"🔄 Loading profile: {profile_name}")
            self.driver = self.profile_manager.load_profile(profile_name)
            print(f"✅ Profile loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
            raise

    def _load_stored_profiles(self):
        """Load stored profiles from JSON"""
        try:
            if os.path.exists(self.profiles_storage_file):
                with open(self.profiles_storage_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}

    def _save_stored_profiles(self):
        """Save profiles to JSON"""
        try:
            with open(self.profiles_storage_file, 'w') as f:
                json.dump(self.stored_profiles, f, indent=2)
            print(f"💾 Saved {len(self.stored_profiles)} profiles")
        except Exception as e:
            print(f"❌ Error saving: {e}")

    def add_manual_profile(self, profile_url, profile_name=None):
        """Add a profile URL"""
        try:
            print(f"\n📝 ADDING PROFILE")
            if not profile_url.startswith('https://coinmarketcap.com/community/profile/'):
                print("❌ Invalid URL format")
                return False
            
            if not profile_name:
                profile_name = profile_url.split('/')[-2] if profile_url.endswith('/') else profile_url.split('/')[-1]
            
            profile_data = {
                'url': profile_url,
                'name': profile_name,
                'detected_at': datetime.now().isoformat(),
                'total_interactions': 0
            }
            
            self.stored_profiles[profile_name] = profile_data
            self._save_stored_profiles()
            
            print(f"✅ Added: {profile_name}")
            print(f"🔗 URL: {profile_url}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def list_stored_profiles(self):
        """List all stored profiles"""
        print(f"\n📋 STORED PROFILES ({len(self.stored_profiles)})")
        print("="*40)
        
        if not self.stored_profiles:
            print("❌ No profiles stored")
            return
        
        for i, (name, data) in enumerate(self.stored_profiles.items(), 1):
            print(f"{i:2d}. {name}")
            print(f"     🔗 {data['url']}")
            print()

    def close(self):
        """Clean up"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Browser closed")
        except:
            pass


print("✅ CMC Profile Interaction Bot module loaded successfully") 