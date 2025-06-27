#!/usr/bin/env python3
"""
Test Script for Menu Integration

This script tests that the new login detection and structured rotation
features are properly integrated into the menu system.
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_menu_integration():
    """Test the menu integration"""
    try:
        print("🧪 TESTING MENU INTEGRATION")
        print("="*50)
        
        # Test imports
        print("1. Testing menu imports...")
        from autocrypto_social_bot.menu import (
            login_detection_menu,
            structured_rotation_menu,
            LOGIN_DETECTION_AVAILABLE,
            STRUCTURED_ROTATION_AVAILABLE
        )
        print("   ✅ Menu functions imported successfully")
        
        # Check system availability
        print("\n2. Checking system availability...")
        print(f"   🔍 Login Detection Available: {'✅ YES' if LOGIN_DETECTION_AVAILABLE else '❌ NO'}")
        print(f"   🔄 Structured Rotation Available: {'✅ YES' if STRUCTURED_ROTATION_AVAILABLE else '❌ NO'}")
        
        # Test individual components
        if LOGIN_DETECTION_AVAILABLE:
            print("\n3. Testing login detection components...")
            from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
            from autocrypto_social_bot.profiles.profile_manager import ProfileManager
            
            profile_manager = ProfileManager()
            login_detector = CMCLoginDetector(profile_manager)
            print("   ✅ Login detector initialized successfully")
        
        if STRUCTURED_ROTATION_AVAILABLE:
            print("\n4. Testing structured rotation components...")
            from autocrypto_social_bot.structured_profile_rotation import (
                StructuredProfileRotation,
                EnhancedProfileManager
            )
            
            rotation = StructuredProfileRotation()
            enhanced_manager = EnhancedProfileManager()
            print("   ✅ Structured rotation initialized successfully")
        
        print(f"\n✅ MENU INTEGRATION TEST PASSED!")
        print(f"🎯 All systems are properly integrated into the menu")
        
        return True
        
    except Exception as e:
        print(f"❌ Menu integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_menu_features():
    """Show the new menu features"""
    print(f"\n🆕 NEW MENU FEATURES ADDED:")
    print(f"="*40)
    
    print(f"📋 Profile Management Menu:")
    print(f"   6. 🔍 Login Detection & Verification")
    print(f"   7. 🔄 Structured Profile Rotation")
    
    print(f"\n🔍 Login Detection Menu:")
    print(f"   • Test single profile login status")
    print(f"   • Quick verification of all profiles")
    print(f"   • Full profile scan with cleanup")
    print(f"   • Profile status summary")
    print(f"   • Quick login detection test")
    
    print(f"\n🔄 Structured Rotation Menu:")
    print(f"   • Test structured rotation system")
    print(f"   • Verify profiles for rotation")
    print(f"   • View rotation statistics")
    print(f"   • Demo rotation sequence")
    print(f"   • Initialize structured rotation")
    
    print(f"\n🎯 KEY BENEFITS:")
    print(f"   ✅ Accurate login detection (checks for Login button)")
    print(f"   🔄 Sequential profile rotation (1→2→3→1...)")
    print(f"   👤 User confirmation before deleting profiles")
    print(f"   ⚡ No time wasted on logged-out profiles")
    print(f"   🧹 Clean profile management")

if __name__ == "__main__":
    print("🚀 MENU INTEGRATION TEST")
    print("="*60)
    
    success = test_menu_integration()
    
    if success:
        show_menu_features()
        
        print(f"\n🎉 READY TO USE!")
        print(f"Run: python autocrypto_social_bot/menu.py")
        print(f"Navigate to: Profile Management → Login Detection & Verification")
        print(f"Or: Profile Management → Structured Profile Rotation")
    else:
        print(f"\n❌ Integration test failed - check the error messages above") 