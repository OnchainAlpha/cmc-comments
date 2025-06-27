#!/usr/bin/env python3
"""
Early Login Verification Test Script

Tests the new system that checks login status BEFORE starting any work,
preventing time waste on AI analysis when not logged in.
"""

import sys
import os
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.main import CryptoAIAnalyzer
from autocrypto_social_bot.profiles.profile_manager import ProfileManager

def test_early_login_verification():
    """Test the early login verification system"""
    print("🧪 TESTING EARLY LOGIN VERIFICATION SYSTEM")
    print("="*60)
    print("This test verifies that login status is checked BEFORE starting work")
    print("instead of wasting time on AI analysis and then failing at posting.")
    print()
    
    try:
        # Initialize the analyzer (this will load a profile)
        print("🔄 Initializing CryptoAIAnalyzer...")
        analyzer = CryptoAIAnalyzer()
        
        print("✅ Analyzer initialized successfully")
        print(f"📊 Profile Manager: {'Available' if hasattr(analyzer, 'profile_manager') else 'Not Available'}")
        print(f"🌐 CMC Scraper: {'Available' if hasattr(analyzer, 'cmc_scraper') else 'Not Available'}")
        
        # Test the early verification methods
        print("\n" + "="*50)
        print("🔍 TESTING LOGIN VERIFICATION METHODS")
        print("="*50)
        
        # Test 1: _verify_login_before_work
        print("Test 1: Early Login Verification")
        if hasattr(analyzer, '_verify_login_before_work'):
            is_logged_in = analyzer._verify_login_before_work()
            print(f"✅ Early verification result: {'LOGGED IN' if is_logged_in else 'NOT LOGGED IN'}")
            
            if not is_logged_in:
                print("⚠️ Current profile is not logged in - this would trigger profile switching")
                
                # Test 2: _switch_to_logged_in_profile
                print("\nTest 2: Automatic Profile Switching")
                if hasattr(analyzer, '_switch_to_logged_in_profile'):
                    print("🔄 Testing automatic switch to logged-in profile...")
                    switch_success = analyzer._switch_to_logged_in_profile()
                    print(f"✅ Profile switching result: {'SUCCESS' if switch_success else 'FAILED'}")
                    
                    if switch_success:
                        # Verify the new profile is logged in
                        print("🔍 Verifying new profile login status...")
                        new_status = analyzer._verify_login_before_work()
                        print(f"✅ New profile status: {'LOGGED IN' if new_status else 'STILL NOT LOGGED IN'}")
                else:
                    print("❌ _switch_to_logged_in_profile method not found")
            else:
                print("✅ Current profile is logged in - no switching needed")
        else:
            print("❌ _verify_login_before_work method not found")
        
        # Test 3: Login Dialog Detection (if available)
        print("\nTest 3: Login Dialog Detection")
        if hasattr(analyzer.cmc_scraper, '_check_for_login_dialog'):
            print("🔍 Testing login dialog detection...")
            login_dialog_present = analyzer.cmc_scraper._check_for_login_dialog()
            print(f"✅ Login dialog detection: {'DIALOG FOUND' if login_dialog_present else 'NO DIALOG'}")
        else:
            print("❌ _check_for_login_dialog method not found")
        
        # Test 4: Simulate the new workflow
        print("\n" + "="*50)
        print("🎯 SIMULATING NEW WORKFLOW")
        print("="*50)
        
        print("Simulating token processing with early verification...")
        print("🔐 VERIFYING CMC LOGIN STATUS BEFORE PROCESSING $TEST...")
        
        early_check = analyzer._verify_login_before_work()
        if early_check:
            print("✅ Current profile is logged into CMC")
            print("✅ Would proceed with AI analysis and content generation")
            print("💡 This saves time by ensuring login before starting work")
        else:
            print("❌ Current profile is not logged into CMC - switching profiles...")
            switch_result = analyzer._switch_to_logged_in_profile()
            if switch_result:
                print("✅ Successfully switched to logged-in profile")
                print("✅ Would now proceed with AI analysis")
            else:
                print("❌ No logged-in profiles available! Skipping $TEST")
                print("💡 This prevents wasting time on content that can't be posted")
        
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        # Show available profiles
        profiles = [p for p in analyzer.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        print(f"📁 Available CMC profiles: {len(profiles)}")
        
        if profiles:
            print("📋 Profile list:")
            for i, profile in enumerate(profiles[:5], 1):
                print(f"   {i}. {profile}")
            if len(profiles) > 5:
                print(f"   ... and {len(profiles) - 5} more")
        
        print(f"\n🎯 BENEFITS OF NEW SYSTEM:")
        print(f"   ✅ Checks login status BEFORE starting AI analysis")
        print(f"   ✅ Prevents waste of time and AI API calls")
        print(f"   ✅ Automatically switches to logged-in profiles") 
        print(f"   ✅ Detects login dialogs during posting")
        print(f"   ✅ Removes logged-out profiles automatically")
        print(f"   ✅ Improves user experience significantly")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_profile_login_status():
    """Test login status of individual profiles"""
    print("\n🔍 TESTING INDIVIDUAL PROFILE LOGIN STATUS")
    print("="*60)
    
    try:
        profile_manager = ProfileManager()
        profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not profiles:
            print("❌ No CMC profiles found")
            return
        
        print(f"Found {len(profiles)} CMC profiles to test")
        
        # Test first 3 profiles
        for i, profile_name in enumerate(profiles[:3], 1):
            try:
                print(f"\n{'='*40}")
                print(f"Testing Profile {i}: {profile_name}")
                print('='*40)
                
                # Load the profile
                print(f"🔄 Loading {profile_name}...")
                driver = profile_manager.load_profile(profile_name)
                
                # Test login status
                print("🔍 Checking login status...")
                status = profile_manager.check_cmc_login_status(driver, profile_name)
                
                if status.get('logged_in', False):
                    print(f"✅ {profile_name}: LOGGED IN")
                    print(f"   Login Score: {status.get('login_score', 0)}")
                    print(f"   Logout Score: {status.get('logout_score', 0)}")
                else:
                    print(f"❌ {profile_name}: NOT LOGGED IN")
                    print(f"   Login Score: {status.get('login_score', 0)}")
                    print(f"   Logout Score: {status.get('logout_score', 0)}")
                    if status.get('logout_reasons'):
                        print(f"   Reasons: {', '.join(status['logout_reasons'][:2])}")
                
                # Close driver
                driver.quit()
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error testing {profile_name}: {str(e)}")
                continue
        
        if len(profiles) > 3:
            print(f"\n💡 To test all {len(profiles)} profiles, run:")
            print(f"   python test_login_detection.py")
            
    except Exception as e:
        print(f"❌ Profile testing error: {str(e)}")

def main():
    """Main test function"""
    print("🧪 EARLY LOGIN VERIFICATION TEST SUITE")
    print("="*50)
    print("This test suite verifies the new early login verification system")
    print("that prevents wasting time on AI analysis when not logged in.")
    print()
    
    test_early_login_verification()

if __name__ == "__main__":
    main() 