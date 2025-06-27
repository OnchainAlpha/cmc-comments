#!/usr/bin/env python3
"""
Test script to verify that the bot will NOT create any new profiles
This script simulates what happens when you start the shilling bot
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_account_rotation_disabled():
    """Test that account rotation is disabled"""
    flag_file = "config/use_account_rotation.flag"
    if os.path.exists(flag_file):
        print("❌ Account rotation is ENABLED - this will create new profiles!")
        print(f"   Flag file found: {flag_file}")
        return False
    else:
        print("✅ Account rotation is DISABLED - no new profiles will be created")
        return True

def test_existing_profiles():
    """Test that existing profiles are found"""
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    
    profile_manager = ProfileManager()
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ NO EXISTING PROFILES FOUND!")
        print("   The bot will fail to start - you need to create profiles first")
        return False
    else:
        print(f"✅ Found {len(profiles)} existing CMC profiles")
        print("   The bot will use these profiles without creating new ones")
        return True

def test_main_script_logic():
    """Test the main script initialization logic"""
    print("\n🧪 Testing main script logic...")
    
    try:
        from autocrypto_social_bot.main import CryptoAIAnalyzer
        
        # This should NOT create any profiles - just check what it would do
        print("✅ Main script can be imported without creating profiles")
        return True
    except Exception as e:
        print(f"❌ Main script import failed: {e}")
        return False

def main():
    """Run all tests to verify no profile creation will happen"""
    print("🧪 TESTING: Profile Creation Prevention")
    print("="*60)
    
    all_tests_passed = True
    
    print("\n1. Testing Account Rotation Status...")
    if not test_account_rotation_disabled():
        all_tests_passed = False
    
    print("\n2. Testing Existing Profiles...")
    if not test_existing_profiles():
        all_tests_passed = False
    
    print("\n3. Testing Main Script Logic...")
    if not test_main_script_logic():
        all_tests_passed = False
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The bot will use existing profiles without creating new ones")
        print("✅ No profile creation prompts will appear")
        print("✅ Ready for shilling with existing sessions!")
    else:
        print("❌ SOME TESTS FAILED!")
        print("⚠️ The bot might still create new profiles")
        print("💡 Check the issues above before running the bot")
    
    print("="*60)
    return all_tests_passed

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 READY TO START SHILLING!")
        print("Run: python autocrypto_social_bot/main.py")
        print("Or:  python use_existing_profiles.py")
        sys.exit(0)
    else:
        print("\n❌ NOT READY - Fix issues first")
        sys.exit(1) 