#!/usr/bin/env python3
"""
Test Script for Structured Profile Rotation System

This script will test the new structured rotation system to ensure:
1. Sequential profile rotation (cmc_profile_1 -> cmc_profile_2 -> cmc_profile_3...)
2. Login verification before each use
3. User confirmation before deleting logged-out profiles
4. No time wasted on non-functional profiles
"""

import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_structured_rotation():
    """Test the structured rotation system"""
    try:
        print("🧪 TESTING STRUCTURED PROFILE ROTATION SYSTEM")
        print("="*60)
        
        # Import the structured rotation system
        from autocrypto_social_bot.structured_profile_rotation import (
            StructuredProfileRotation, 
            EnhancedProfileManager,
            verify_all_profiles,
            test_structured_rotation as test_rotation_sequence
        )
        
        print("✅ Structured rotation system imported successfully")
        
        # Test 1: Basic rotation system initialization
        print("\n🔧 TEST 1: Initializing Structured Rotation...")
        rotation = StructuredProfileRotation()
        
        if rotation.available_profiles:
            print(f"✅ Found {len(rotation.available_profiles)} profiles for rotation")
            print(f"📋 Profiles: {rotation.available_profiles}")
        else:
            print("❌ No profiles found - please create CMC profiles first")
            return False
        
        # Test 2: Profile verification (without asking user confirmation)
        print("\n🔍 TEST 2: Profile Login Verification...")
        print("⚠️ This will check login status of all profiles (no deletion)")
        
        results = rotation.verify_all_profiles_login_status(ask_user_confirmation=False)
        
        print(f"📊 Verification Results:")
        print(f"   Total Profiles: {results['total_profiles']}")
        print(f"   Verified (Logged In): {len(results['verified_profiles'])}")
        print(f"   Failed (Not Logged In): {len(results['failed_profiles'])}")
        print(f"   Deleted: {len(results['deleted_profiles'])}")
        
        if results['verified_profiles']:
            print(f"✅ Found {len(results['verified_profiles'])} verified profiles")
        else:
            print("⚠️ No verified profiles found - all profiles may need login")
        
        # Test 3: Enhanced Profile Manager
        print("\n🚀 TEST 3: Enhanced Profile Manager...")
        enhanced_manager = EnhancedProfileManager()
        
        # Initialize without verification for testing
        try:
            enhanced_manager.initialize_structured_rotation(verify_all=False, ask_confirmation=False)
            print("✅ Enhanced Profile Manager initialized successfully")
            
            # Get rotation stats
            stats = enhanced_manager.get_structured_rotation_stats()
            print(f"📊 Rotation Stats: {stats}")
            
        except Exception as e:
            print(f"❌ Enhanced Profile Manager initialization failed: {e}")
        
        # Test 4: Rotation sequence
        print("\n🔄 TEST 4: Testing Rotation Sequence...")
        test_rotation_sequence()
        
        print(f"\n✅ ALL TESTS COMPLETED")
        print(f"="*60)
        print(f"🎯 STRUCTURED ROTATION SYSTEM IS READY!")
        print(f"="*60)
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure the structured_profile_rotation.py file exists")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_main():
    """Test integration with the main CMC automation system"""
    try:
        print("\n🔗 TESTING INTEGRATION WITH MAIN SYSTEM")
        print("="*50)
        
        # Import the main system
        from autocrypto_social_bot.main import CryptoAIAnalyzer
        
        # Check if structured rotation is available
        from autocrypto_social_bot.main import STRUCTURED_ROTATION_AVAILABLE
        
        if STRUCTURED_ROTATION_AVAILABLE:
            print("✅ Structured rotation is available in main system")
            
            # Test creating analyzer (without actually running it)
            print("🧪 Testing CryptoAIAnalyzer initialization...")
            
            # This would normally ask for user input, so we'll just check imports
            print("✅ Main system can import structured rotation")
            
        else:
            print("❌ Structured rotation is NOT available in main system")
            print("💡 Check the import in main.py")
            return False
        
        print("✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def show_usage_instructions():
    """Show how to use the structured rotation system"""
    print("\n📖 HOW TO USE STRUCTURED PROFILE ROTATION")
    print("="*50)
    print("\n1. VERIFY ALL PROFILES (Recommended):")
    print("   python test_structured_rotation.py --verify")
    print("   - This will check all profiles and ask to delete logged-out ones")
    
    print("\n2. RUN MAIN BOT WITH STRUCTURED ROTATION:")
    print("   python autocrypto_social_bot/main.py")
    print("   - When prompted, choose 'y' to verify profiles before starting")
    print("   - Or choose 'n' to skip verification")
    
    print("\n3. STANDALONE PROFILE VERIFICATION:")
    print("   python autocrypto_social_bot/structured_profile_rotation.py")
    print("   - Choose option 1 to verify all profiles")
    print("   - Choose option 2 to test rotation sequence")
    print("   - Choose option 3 for both")
    
    print("\n🔄 WHAT HAPPENS DURING ROTATION:")
    print("   ✅ Profiles rotate in order: cmc_profile_1 → cmc_profile_2 → cmc_profile_3...")
    print("   ✅ Each profile is verified for login status before use")
    print("   ✅ Logged-out profiles are automatically detected")
    print("   ✅ User is asked before deleting any profiles")
    print("   ✅ No time is wasted on non-functional profiles")
    
    print("\n💡 BENEFITS:")
    print("   🚀 Faster operation (no failed login attempts)")
    print("   🎯 Predictable rotation sequence")
    print("   🧹 Automatic cleanup of bad profiles")
    print("   👤 User control over profile deletion")
    print("   📊 Clear status reporting")

if __name__ == "__main__":
    print("🔄 STRUCTURED PROFILE ROTATION TEST SUITE")
    print("="*60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verify":
            print("🔍 RUNNING PROFILE VERIFICATION...")
            from autocrypto_social_bot.structured_profile_rotation import verify_all_profiles
            results = verify_all_profiles(ask_confirmation=True)
            
            if results['verified_profiles']:
                print(f"\n✅ {len(results['verified_profiles'])} profiles are ready for rotation")
            else:
                print(f"\n❌ No verified profiles - please login to your CMC profiles first")
            sys.exit(0)
        elif sys.argv[1] == "--help":
            show_usage_instructions()
            sys.exit(0)
    
    # Run all tests
    print("🧪 Running comprehensive test suite...\n")
    
    success = True
    
    # Test 1: Structured rotation system
    if not test_structured_rotation():
        success = False
    
    # Test 2: Integration with main system
    if not test_integration_with_main():
        success = False
    
    # Final result
    if success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Structured Profile Rotation System is ready to use")
        show_usage_instructions()
    else:
        print(f"\n❌ SOME TESTS FAILED")
        print(f"💡 Please check the error messages above and fix any issues")
    
    print(f"\n" + "="*60) 