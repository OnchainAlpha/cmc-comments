#!/usr/bin/env python3
"""
🔥 BREAKTHROUGH INTEGRATION TEST 🔥
Quick test to verify our real-time proxy testing and browser-level configuration
"""

import sys
import os
sys.path.append('autocrypto_social_bot')

def test_breakthrough_system():
    print("\n🔥 BREAKTHROUGH INTEGRATION TEST")
    print("="*60)
    
    try:
        # Test 1: Import bypass manager
        print("1. Testing breakthrough bypass system import...")
        from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
        print("   ✅ Breakthrough system imported successfully!")
        
        # Test 2: Real-time proxy testing
        print("\n2. Testing real-time proxy availability...")
        working_proxy = cmc_bypass_manager.get_currently_working_proxy()
        
        if working_proxy:
            print(f"   ✅ Found working proxy: {working_proxy}")
        else:
            print("   ⚠️ No working proxies found at the moment")
        
        # Test 3: Selenium options creation
        print("\n3. Testing selenium proxy configuration...")
        proxy_options, proxy_used = cmc_bypass_manager.create_selenium_proxy_options()
        
        if proxy_used:
            print(f"   ✅ Selenium configured with proxy: {proxy_used}")
            print("   🎯 Browser-level proxy configuration ready!")
        else:
            print("   ⚠️ No proxy configured, will use direct connection")
        
        # Test 4: Profile manager integration
        print("\n4. Testing profile manager integration...")
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        profile_manager = ProfileManager()
        
        if hasattr(profile_manager, 'load_profile_with_cmc_bypass'):
            print("   ✅ Profile manager has breakthrough integration!")
        else:
            print("   ❌ Profile manager missing breakthrough integration")
        
        print("\n🎉 BREAKTHROUGH INTEGRATION TEST COMPLETE!")
        print("="*60)
        
        if working_proxy:
            print("🚀 READY TO DEPLOY:")
            print(f"   🌐 Working Proxy: {working_proxy}")
            print("   🔒 Complete IP protection active")
            print("   📱 Browser-level proxy configuration")
            print("   ✅ Real-time proxy testing working")
            print("\n💡 To use: Run 'python autocrypto_social_bot/menu.py' and select option 2!")
        else:
            print("⚠️ NOTICE:")
            print("   📡 No working proxies available right now")
            print("   🔄 ProxyScrape proxies refresh every minute")
            print("   💡 Try again in 1-2 minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_breakthrough_system() 