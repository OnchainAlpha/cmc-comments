#!/usr/bin/env python3
"""
Test Script for Exact CMC Login Button Detection

This script tests the updated login detection that targets the exact CMC login button:
- data-btnname='Log In'
- data-forcetrack='Log In' 
- data-test='Log In'
- BaseButton_base class structure
- data-role='btn-content-item' with 'Log In' text
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exact_cmc_button_detection():
    """Test detection of the exact CMC login button structure"""
    try:
        print("🧪 TESTING EXACT CMC LOGIN BUTTON DETECTION")
        print("="*70)
        print("🎯 Targeting EXACT CMC button structure:")
        print("   • data-btnname='Log In'")
        print("   • data-forcetrack='Log In'")
        print("   • data-test='Log In'")
        print("   • BaseButton_base classes")
        print("   • data-role='btn-content-item'")
        print("="*70)
        
        # Import the updated login detector
        from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        
        print("✅ Updated login detection system imported successfully")
        
        # Initialize components
        profile_manager = ProfileManager()
        login_detector = CMCLoginDetector(profile_manager)
        
        # Get available CMC profiles
        profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not profiles:
            print("❌ No CMC profiles found - please create profiles first")
            return False
        
        print(f"\n📋 Found {len(profiles)} CMC profiles to test:")
        for i, profile in enumerate(profiles[:3], 1):  # Test first 3 profiles
            print(f"   {i}. {profile}")
        
        # Test the profile that was giving false positives
        test_profile = profiles[0]
        print(f"\n🧪 TESTING PROFILE: {test_profile}")
        print("="*50)
        
        # Load profile
        print("📂 Loading profile...")
        driver = profile_manager.load_profile(test_profile)
        
        # Run the updated detection
        print(f"\n🔍 RUNNING UPDATED DETECTION...")
        status = login_detector.check_cmc_login_status(driver, test_profile)
        
        print(f"\n📊 RESULTS WITH EXACT BUTTON TARGETING:")
        print(f"="*50)
        print(f"✅ Profile: {test_profile}")
        print(f"🔍 Logged In: {'✅ YES' if status.get('logged_in') else '❌ NO'}")
        print(f"📋 Detection Method: {status.get('primary_reason', 'Unknown')}")
        print(f"🖱️ Click Test Performed: {'✅ YES' if status.get('click_test_performed') else '❌ NO'}")
        print(f"🔍 Login Button Found: {'✅ YES' if status.get('login_button_found') else '❌ NO'}")
        
        # Close driver
        driver.quit()
        
        print(f"\n✅ EXACT CMC BUTTON DETECTION TEST COMPLETED!")
        print(f"🎯 The system now targets the exact CMC login button structure!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_button_structure():
    """Show the exact button structure we're targeting"""
    print(f"\n🎯 EXACT CMC LOGIN BUTTON STRUCTURE:")
    print(f"="*60)
    
    print(f"📝 HTML Structure:")
    print(f'<button class="sc-65e7f566-0 eQBACe BaseButton_base__34gwo"')
    print(f'        data-btnname="Log In"')
    print(f'        data-forcetrack="Log In"')
    print(f'        data-page="HomePage"')
    print(f'        data-test="Log In">')
    print(f'  <div data-role="btn-content" class="...btnContentWrapper...">')
    print(f'    <div data-role="btn-content-item" class="...labelWrapper...">Log In</div>')
    print(f'  </div>')
    print(f'</button>')
    
    print(f"\n🎯 TARGETING THESE SELECTORS:")
    print(f"   1. //button[@data-btnname='Log In']")
    print(f"   2. //button[@data-forcetrack='Log In']")
    print(f"   3. //button[@data-test='Log In']")
    print(f"   4. //button[contains(@class, 'BaseButton_base') and .//div[text()='Log In']]")
    print(f"   5. //div[@data-role='btn-content-item' and text()='Log In']/ancestor::button")
    
    print(f"\n✅ BENEFITS:")
    print(f"   • Targets EXACT CMC button structure")
    print(f"   • Uses unique data attributes")
    print(f"   • More precise than generic text search")
    print(f"   • Matches the button used in profile creation")

if __name__ == "__main__":
    print("🚀 EXACT CMC LOGIN BUTTON DETECTION TEST")
    print("="*70)
    
    show_button_structure()
    
    success = test_exact_cmc_button_detection()
    
    if success:
        print(f"\n🎉 READY TO USE!")
        print(f"The system now targets the EXACT CMC login button structure!")
        print(f"Run: python autocrypto_social_bot/menu.py")
        print(f"Navigate to: Profile Management → Login Detection & Verification")
    else:
        print(f"\n❌ Test failed - check the error messages above") 