#!/usr/bin/env python3
"""
Test Script for Improved CMC Login Detection

This script tests the improved login detection that focuses on the "Log In" button
in the top right header of the CMC website.
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_login_detection():
    """Test the improved login detection system"""
    try:
        print("🧪 TESTING IMPROVED CMC LOGIN DETECTION")
        print("="*60)
        
        # Import the login detector
        from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        
        print("✅ Login detection system imported successfully")
        
        # Initialize components
        profile_manager = ProfileManager()
        login_detector = CMCLoginDetector(profile_manager)
        
        # Get available profiles
        profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not profiles:
            print("❌ No CMC profiles found - please create profiles first")
            return False
        
        print(f"📋 Found {len(profiles)} CMC profiles to test")
        
        # Test login detection on first profile
        test_profile = profiles[0]
        print(f"\n🔍 TESTING LOGIN DETECTION ON: {test_profile}")
        print("="*50)
        
        # Load profile
        print(f"📂 Loading profile: {test_profile}")
        driver = profile_manager.load_profile(test_profile)
        
        # Wait for profile to load
        import time
        time.sleep(3)
        
        # Test the improved login detection
        print(f"\n🎯 RUNNING IMPROVED LOGIN DETECTION...")
        status = login_detector.check_cmc_login_status(driver, test_profile)
        
        # Show results
        print(f"\n📊 DETECTION RESULTS:")
        print(f"="*30)
        print(f"✅ Profile: {test_profile}")
        print(f"🔍 Logged In: {status.get('logged_in', False)}")
        print(f"📋 Primary Reason: {status.get('primary_reason', 'Unknown')}")
        
        if status.get('login_button_found'):
            print(f"❌ Login Button Found: {status.get('login_button_details', [])}")
        
        if status.get('logged_in_indicators_found'):
            print(f"✅ Logged-in Indicators: {status.get('logged_in_details', [])}")
        
        if status.get('suspicious_text'):
            print(f"⚠️ Suspicious Text: {status.get('suspicious_text', [])}")
        
        # Test quick login check
        print(f"\n🚀 TESTING QUICK LOGIN CHECK...")
        quick_result = login_detector.quick_login_check(driver)
        print(f"🔍 Quick Check Result: {quick_result}")
        
        # Close driver
        try:
            driver.quit()
        except:
            pass
        
        print(f"\n✅ LOGIN DETECTION TEST COMPLETED")
        print(f"="*60)
        
        # Summary
        if status.get('logged_in'):
            print(f"🎉 RESULT: Profile appears to be LOGGED IN")
            print(f"💡 The bot will use this profile for posting")
        else:
            print(f"⚠️ RESULT: Profile appears to be NOT LOGGED IN")
            print(f"💡 The bot will skip this profile or ask to delete it")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_all_profiles():
    """Test login detection on all available profiles"""
    try:
        print("\n🔍 TESTING ALL PROFILES")
        print("="*50)
        
        # Import components
        from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        
        profile_manager = ProfileManager()
        login_detector = CMCLoginDetector(profile_manager)
        
        # Get all profiles
        profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not profiles:
            print("❌ No profiles found")
            return False
        
        logged_in_count = 0
        logged_out_count = 0
        
        for i, profile_name in enumerate(profiles, 1):
            print(f"\n{'='*40}")
            print(f"🔍 TESTING PROFILE {i}/{len(profiles)}: {profile_name}")
            print(f"{'='*40}")
            
            try:
                # Load profile
                driver = profile_manager.load_profile(profile_name)
                
                # Quick test (don't show full output)
                status = login_detector.check_cmc_login_status(driver, profile_name)
                
                if status.get('logged_in'):
                    print(f"✅ LOGGED IN: {profile_name}")
                    logged_in_count += 1
                else:
                    print(f"❌ NOT LOGGED IN: {profile_name}")
                    print(f"   Reason: {status.get('primary_reason', 'Unknown')}")
                    logged_out_count += 1
                
                # Close driver
                try:
                    driver.quit()
                except:
                    pass
                
            except Exception as e:
                print(f"❌ ERROR testing {profile_name}: {str(e)}")
                logged_out_count += 1
        
        # Summary
        print(f"\n📊 SUMMARY")
        print(f"="*30)
        print(f"✅ Logged In Profiles: {logged_in_count}")
        print(f"❌ Logged Out Profiles: {logged_out_count}")
        print(f"📋 Total Profiles: {len(profiles)}")
        
        if logged_in_count > 0:
            print(f"\n🎉 You have {logged_in_count} working profiles for the bot!")
        else:
            print(f"\n⚠️ No logged-in profiles found - please log into your CMC profiles")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing all profiles: {e}")
        return False

if __name__ == "__main__":
    print("🔍 CMC LOGIN DETECTION TEST SUITE")
    print("="*60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            test_all_profiles()
            sys.exit(0)
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python test_login_detection.py        # Test first profile")
            print("  python test_login_detection.py --all  # Test all profiles")
            sys.exit(0)
    
    # Run single profile test
    success = test_login_detection()
    
    if success:
        print(f"\n💡 To test all profiles, run:")
        print(f"   python test_login_detection.py --all")
    
    print(f"\n" + "="*60) 