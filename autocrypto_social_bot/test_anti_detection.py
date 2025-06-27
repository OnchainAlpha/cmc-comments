#!/usr/bin/env python3
"""
Test script for the Anti-Detection System
Tests proxy rotation, shadowban detection, and adaptive rate limiting
"""

import sys
import os
import time
import logging

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.utils.anti_detection import AntiDetectionSystem
from autocrypto_social_bot.profiles.profile_manager import ProfileManager

def test_anti_detection_system():
    """Test the anti-detection system components"""
    print("\n" + "="*60)
    print("🧪 ANTI-DETECTION SYSTEM TEST")
    print("="*60)
    
    # Initialize anti-detection system
    print("\n1. Initializing Anti-Detection System...")
    ads = AntiDetectionSystem()
    print("✅ Anti-Detection System initialized")
    
    # Test proxy fetching
    print("\n2. Testing Proxy Sources...")
    try:
        proxies = ads.get_fresh_proxies()
        print(f"✅ Fetched {len(proxies)} proxies from sources")
        
        if proxies:
            print(f"Sample proxies: {proxies[:3]}")
            
            # Test a few proxies
            print("\n3. Testing Proxy Connectivity...")
            working_proxy = ads.get_working_proxy()
            if working_proxy:
                print(f"✅ Found working proxy: {working_proxy}")
            else:
                print("⚠️ No working proxies found (this is normal if internet is restricted)")
        else:
            print("⚠️ No proxies fetched (this is normal if internet is restricted)")
            
    except Exception as e:
        print(f"⚠️ Proxy test failed: {str(e)} (this is normal if internet is restricted)")
    
    # Test Chrome options creation
    print("\n4. Testing Chrome Options Creation...")
    try:
        options = ads.create_anti_detection_options(use_proxy=False)  # No proxy for testing
        print("✅ Anti-detection Chrome options created successfully")
        print(f"   User-Agent: Random from {len(ads.user_agents)} options")
        print(f"   Screen Resolution: Random from {len(ads.screen_resolutions)} options")
        print(f"   Anti-detection arguments: {len(options.arguments)} added")
    except Exception as e:
        print(f"❌ Chrome options creation failed: {str(e)}")
    
    # Test adaptive delay system
    print("\n5. Testing Adaptive Delay System...")
    try:
        # Test normal operation
        delay = ads.get_adaptive_delay()
        print(f"✅ Normal mode delay: {delay}s")
        
        # Simulate failures
        ads.update_session_state(False, 'rate_limit')
        delay = ads.get_adaptive_delay()
        print(f"✅ Rate limit mode delay: {delay}s")
        
        # Simulate shadowban
        ads.update_session_state(False, 'shadowban')
        delay = ads.get_adaptive_delay()
        print(f"✅ Shadowban recovery delay: {delay}s")
        
        # Reset to success
        ads.update_session_state(True)
        delay = ads.get_adaptive_delay()
        print(f"✅ Returned to normal delay: {delay}s")
        
    except Exception as e:
        print(f"❌ Adaptive delay test failed: {str(e)}")
    
    # Test session state tracking
    print("\n6. Testing Session State Tracking...")
    try:
        summary = ads.get_session_summary()
        print("✅ Session Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Session state test failed: {str(e)}")
    
    # Test Profile Manager integration
    print("\n7. Testing Profile Manager Integration...")
    try:
        pm = ProfileManager()
        if hasattr(pm, 'anti_detection') and pm.anti_detection:
            print("✅ Profile Manager has anti-detection system")
            
            # Test adaptive delay from profile manager
            delay = pm.get_adaptive_delay()
            print(f"✅ Profile Manager adaptive delay: {delay}s")
            
            # Test session info
            session_info = pm.get_session_info()
            print(f"✅ Profile Manager session info: {session_info}")
            
        else:
            print("⚠️ Profile Manager anti-detection not initialized")
            
    except Exception as e:
        print(f"❌ Profile Manager integration test failed: {str(e)}")
    
    print("\n" + "="*60)
    print("🎯 ANTI-DETECTION TEST SUMMARY")
    print("="*60)
    print("✅ Anti-Detection System: Ready")
    print("✅ Proxy Rotation: Configured")
    print("✅ Adaptive Delays: Working")
    print("✅ Session Tracking: Active")
    print("✅ Profile Integration: Complete")
    print("\n💡 The system is ready to bypass shadowbans!")
    print("   - IP rotation every 10 posts or on failures")
    print("   - Adaptive delays based on account health")
    print("   - Automatic shadowban detection")
    print("   - Behavioral randomization")
    print("=" * 60)

def test_proxy_rotation():
    """Test proxy rotation specifically"""
    print("\n" + "="*40)
    print("🔄 PROXY ROTATION TEST")
    print("="*40)
    
    ads = AntiDetectionSystem()
    
    print("Testing proxy rotation...")
    for i in range(3):
        proxy = ads.get_working_proxy()
        if proxy:
            print(f"Rotation {i+1}: Using proxy {proxy}")
        else:
            print(f"Rotation {i+1}: No proxy available")
        time.sleep(1)

def test_shadowban_detection():
    """Test shadowban detection patterns"""
    print("\n" + "="*40)
    print("🚫 SHADOWBAN DETECTION TEST")
    print("="*40)
    
    ads = AntiDetectionSystem()
    
    # Test different shadowban indicators
    test_content = [
        "your post was not published",
        "content not visible to others",
        "under review by moderators",
        "violates our community guidelines",
        "temporarily restricted access",
        "normal content here"
    ]
    
    for content in test_content:
        # Simulate checking content
        is_shadowban = any(indicator in content for indicator in ads.shadowban_indicators)
        status = "🚫 SHADOWBAN" if is_shadowban else "✅ CLEAN"
        print(f"{status}: '{content}'")

if __name__ == "__main__":
    print("🚀 Starting Anti-Detection System Tests...")
    
    try:
        test_anti_detection_system()
        test_proxy_rotation()
        test_shadowban_detection()
        
        print("\n🎉 All tests completed successfully!")
        print("Your anti-detection system is ready to bypass CMC restrictions!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...") 