#!/usr/bin/env python3
"""
Helper script to run the CMC bot using ONLY existing profiles
No new profiles will be created - the bot will use what already exists
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.main import CryptoAIAnalyzer

def check_existing_profiles():
    """Check what profiles are available"""
    print("\n" + "="*60)
    print("🔍 CHECKING EXISTING PROFILES")
    print("="*60)
    
    profile_manager = ProfileManager()
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ NO CMC PROFILES FOUND!")
        print("\nYou need to create profiles first before running the shilling bot.")
        print("Please use one of these methods to create profiles:")
        print("\n1. Run the menu system:")
        print("   python autocrypto_social_bot/menu.py")
        print("\n2. Or create profiles manually in the Profile Management menu")
        print("\nAfter creating profiles, run this script again.")
        return False
    
    print(f"✅ Found {len(profiles)} existing CMC profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"   {i}. {profile}")
    
    print(f"\n✅ Ready to use existing profiles for shilling!")
    print("The bot will rotate between these profiles without creating new ones.")
    return True

def run_shilling_bot():
    """Run the shilling bot with existing profiles only"""
    print("\n" + "="*60)
    print("🚀 STARTING SHILLING BOT (EXISTING PROFILES ONLY)")
    print("="*60)
    print("✅ No new profiles will be created")
    print("✅ Using existing profiles for rotation")
    print("✅ Ready for automated shilling")
    print("="*60)
    
    # Start the bot - it will now use existing profiles only
    analyzer = CryptoAIAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    print("🤖 CMC Shilling Bot - Existing Profiles Mode")
    print("This script ensures no new profiles are created")
    
    # Check if we have existing profiles
    if check_existing_profiles():
        # Confirm with user
        print("\n" + "="*60)
        confirm = input("Start shilling with existing profiles? (y/n): ").strip().lower()
        if confirm == 'y':
            run_shilling_bot()
        else:
            print("Operation cancelled.")
    else:
        print("\nPlease create profiles first, then run this script again.") 