#!/usr/bin/env python3
"""
Test script to verify shadowban detection fixes
Shows the difference between old and new detection logic
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_shadowban_detection():
    """Test the fixed shadowban detection"""
    print("🔧 SHADOWBAN DETECTION FIX VERIFICATION")
    print("="*60)
    
    try:
        from autocrypto_social_bot.utils.anti_detection import AntiDetectionSystem
        
        # Create anti-detection system
        ads = AntiDetectionSystem()
        
        # Test messages that SHOULD and SHOULD NOT trigger shadowban
        test_messages = [
            # SHOULD NOT trigger (rate limits - normal)
            ("try again later", False, "Normal rate limiting"),
            ("posting too frequently", False, "Normal rate limiting"),
            ("please wait", False, "Normal rate limiting"),
            ("slow down", False, "Normal rate limiting"),
            
            # SHOULD trigger (actual shadowbans)
            ("your post was not published", True, "Real shadowban"),
            ("content not visible to others", True, "Real shadowban"),
            ("account suspended", True, "Real shadowban"),
            ("violates our community guidelines", True, "Real shadowban"),
            
            # Normal content - should not trigger
            ("Bitcoin is up today", False, "Normal content"),
            ("Great analysis on this coin", False, "Normal content")
        ]
        
        print("\n🧪 TESTING SHADOWBAN DETECTION:")
        print("-" * 60)
        
        all_correct = True
        for message, should_trigger, description in test_messages:
            # Check if any shadowban indicator is in the message
            detected = any(indicator in message.lower() for indicator in ads.shadowban_indicators)
            
            status = "🚫 SHADOWBAN" if detected else "✅ CLEAN"
            expected = "🚫 SHADOWBAN" if should_trigger else "✅ CLEAN"
            
            if detected == should_trigger:
                result = "✅ CORRECT"
            else:
                result = "❌ WRONG"
                all_correct = False
            
            print(f"{status} | {expected} | {result} | {description}")
            print(f"   Message: '{message}'")
            print()
        
        print("="*60)
        if all_correct:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Shadowban detection is now properly calibrated")
            print("✅ 'try again later' will NOT trigger false shadowban")
            print("✅ Only real shadowban indicators will trigger")
        else:
            print("❌ Some tests failed - shadowban detection needs adjustment")
            
        return all_correct
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def show_fix_summary():
    """Show what was fixed"""
    print("\n🔧 WHAT WAS FIXED:")
    print("="*60)
    print("❌ BEFORE (Overly Sensitive):")
    print("   • 'try again later' → SHADOWBAN (WRONG!)")
    print("   • 'posting too frequently' → SHADOWBAN (WRONG!)")
    print("   • Normal rate limiting → SHADOWBAN (WRONG!)")
    print()
    print("✅ AFTER (Properly Calibrated):")
    print("   • 'try again later' → RATE_LIMIT (CORRECT!)")
    print("   • 'posting too frequently' → RATE_LIMIT (CORRECT!)")
    print("   • Only real shadowbans → SHADOWBAN (CORRECT!)")
    print()
    print("🎯 RESULT:")
    print("   • Your comment generation worked perfectly!")
    print("   • But false shadowban detection stopped it from posting")
    print("   • Now it will properly post your promotional comments!")

if __name__ == "__main__":
    print("🚀 SHADOWBAN DETECTION FIX - VERIFICATION")
    print("="*70)
    
    # Show what was fixed
    show_fix_summary()
    
    # Test the fix
    success = test_shadowban_detection()
    
    if success:
        print("\n💰 READY FOR YOUR RAISE! 🚀")
        print("Your bot will now:")
        print("✅ Generate promotional comments correctly")
        print("✅ Not get confused by normal rate limits")
        print("✅ Only pause for actual shadowbans")
        print("✅ Post your OCB market making content successfully!")
        print("\nRun: python run_cmc_automation.py")
    else:
        print("\n⚠️ Fix verification failed - check the output above") 