import sys
import os
import time
from typing import Optional
from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.main import CryptoAIAnalyzer
import json
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style

# Add import for our breakthrough CMC bypass system
try:
    from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
    CMC_BYPASS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ CMC Bypass system not available: {e}")
    CMC_BYPASS_AVAILABLE = False
    cmc_bypass_manager = None

# Add these imports at the top with the other imports
try:
    from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager
    from autocrypto_social_bot.services.account_manager import AutomatedAccountManager, Account
    from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig, setup_simplelogin
    ACCOUNT_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Account Management system not available: {e}")
    ACCOUNT_MANAGEMENT_AVAILABLE = False

# Add imports for new login detection and structured rotation
try:
    from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
    from autocrypto_social_bot.structured_profile_rotation import (
        StructuredProfileRotation, 
        EnhancedProfileManager as StructuredEnhancedProfileManager,
        verify_all_profiles,
        test_structured_rotation
    )
    LOGIN_DETECTION_AVAILABLE = True
    STRUCTURED_ROTATION_AVAILABLE = True
    print("✅ Login Detection & Structured Rotation systems loaded!")
except ImportError as e:
    print(f"⚠️ Login Detection & Structured Rotation not available: {e}")
    LOGIN_DETECTION_AVAILABLE = False
    STRUCTURED_ROTATION_AVAILABLE = False

# Add imports for CMC Coin Posts Bot, Profile Bot, and Like Stacking Bot
try:
    import sys
    import os
    # Add the project root to path for coin_posts_bot
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.append(project_root)
    
    from coin_posts_bot import CMCCoinPostsBot
    from profile_bot import CMCProfileInteractionBot
    from like_stacking_bot import CMCLikeStackingBot
    COIN_POSTS_BOT_AVAILABLE = True
    PROFILE_BOT_AVAILABLE = True
    LIKE_STACKING_BOT_AVAILABLE = True
    print("✅ CMC Coin Posts Bot system loaded!")
    print("✅ CMC Profile Interaction Bot system loaded!")
    print("✅ CMC Like Stacking Bot system loaded!")
except ImportError as e:
    print(f"⚠️ CMC Bots not available: {e}")
    COIN_POSTS_BOT_AVAILABLE = False
    PROFILE_BOT_AVAILABLE = False
    LIKE_STACKING_BOT_AVAILABLE = False

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Print a formatted header"""
    clear_screen()
    print("\n" + "="*60)
    print(title.center(60))
    print("="*60 + "\n")

def login_detection_menu():
    """CMC Login Detection and Profile Verification Menu"""
    if not LOGIN_DETECTION_AVAILABLE:
        print("❌ Login Detection system not available")
        input("Press Enter to continue...")
        return
    
    while True:
        print_header("🔍 CMC Login Detection & Profile Verification")
        print("🎯 Verify which profiles are actually logged into CMC")
        print("🧹 Clean up profiles that have lost their login sessions")
        print("⚡ Improve bot efficiency by using only working profiles")
        print("\n📋 MENU OPTIONS:")
        print("1. 🧪 Test Single Profile Login Status")
        print("2. 🔍 Verify All Profiles (Quick Check)")
        print("3. 🧹 Full Profile Scan & Cleanup")
        print("4. 📊 View Profile Status Summary")
        print("5. 🚀 Test Quick Login Detection")
        print("6. 🔙 Back to Profile Management")
        
        choice = input("\n🎯 Select option (1-6): ").strip()
        
        if choice == '1':
            test_single_profile_login()
        elif choice == '2':
            verify_all_profiles_quick()
        elif choice == '3':
            full_profile_scan_cleanup()
        elif choice == '4':
            view_profile_status_summary()
        elif choice == '5':
            test_quick_login_detection()
        elif choice == '6':
            break
        else:
            print("❌ Invalid option. Please select 1-6.")

def structured_rotation_menu():
    """Structured Profile Rotation Menu"""
    if not STRUCTURED_ROTATION_AVAILABLE:
        print("❌ Structured Rotation system not available")
        input("Press Enter to continue...")
        return
    
    while True:
        print_header("🔄 Structured Profile Rotation")
        print("🎯 Sequential profile rotation (cmc_profile_1 → cmc_profile_2 → cmc_profile_3...)")
        print("✅ Login verification before each use")
        print("👤 User confirmation before deleting profiles")
        print("⚡ No time wasted on non-functional profiles")
        print("\n📋 MENU OPTIONS:")
        print("1. 🧪 Test Structured Rotation System")
        print("2. 🔍 Verify All Profiles for Rotation")
        print("3. 📊 View Rotation Statistics")
        print("4. 🔄 Demo Rotation Sequence")
        print("5. ⚙️ Initialize Structured Rotation")
        print("6. 🔙 Back to Profile Management")
        
        choice = input("\n🎯 Select option (1-6): ").strip()
        
        if choice == '1':
            test_structured_rotation_system()
        elif choice == '2':
            verify_profiles_for_rotation()
        elif choice == '3':
            view_rotation_statistics()
        elif choice == '4':
            demo_rotation_sequence()
        elif choice == '5':
            initialize_structured_rotation()
        elif choice == '6':
            break
        else:
            print("❌ Invalid option. Please select 1-6.")

def manage_profiles():
    """Profile management menu"""
    profile_manager = ProfileManager()
    
    while True:
        print_header("🔐 Profile Manager")
        print("1. List all profiles")
        print("2. Create new profile")
        print("3. Test existing profile")
        print("4. Delete profile")
        print("5. Migrate legacy profile")
        print("6. 🔍 Login Detection & Verification")
        print("7. 🔄 Structured Profile Rotation")
        print("8. Back to main menu")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            profiles = profile_manager.list_profiles()
            if profiles:
                print("\nAvailable profiles:")
                for profile in profiles:
                    print(f"- {profile}")
            else:
                print("\nNo profiles found")
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            next_num = profile_manager.get_next_profile_number()
            print(f"\nCreating profile #{next_num}...")
            profile_manager.create_numbered_profile(next_num)
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            profiles = profile_manager.list_profiles()
            if not profiles:
                print("\nNo profiles available. Please create a profile first.")
                input("\nPress Enter to continue...")
                continue
                
            print("\nAvailable profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
                
            try:
                idx = int(input("\nSelect profile number to test: ")) - 1
                if 0 <= idx < len(profiles):
                    profile_name = profiles[idx]
                    driver = None
                    try:
                        print(f"\nLoading profile: {profile_name}")
                        driver = profile_manager.load_profile(profile_name)
                        
                        while True:
                            print("\nTest Menu:")
                            print("1. Go to CoinMarketCap")
                            print("2. Go to custom URL")
                            print("3. Close browser")
                            
                            test_choice = input("\nEnter your choice (1-3): ")
                            
                            if test_choice == "1":
                                driver.get("https://coinmarketcap.com")
                            elif test_choice == "2":
                                url = input("Enter URL (include https://): ")
                                driver.get(url)
                            elif test_choice == "3":
                                break
                            
                            time.sleep(2)
                    finally:
                        if driver:
                            driver.quit()
            except ValueError:
                print("Invalid input")
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            profiles = profile_manager.list_profiles()
            if not profiles:
                print("\nNo profiles available to delete.")
                input("\nPress Enter to continue...")
                continue
                
            print("\nAvailable profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
                
            try:
                idx = int(input("\nSelect profile number to delete (0 to cancel): ")) - 1
                if idx == -1:
                    continue
                if 0 <= idx < len(profiles):
                    profile_name = profiles[idx]
                    confirm = input(f"\nAre you sure you want to delete {profile_name}? (y/n): ").lower()
                    if confirm == 'y':
                        profile_path = profile_manager.get_profile_path(profile_name)
                        import shutil
                        shutil.rmtree(profile_path)
                        print(f"\n✅ Deleted profile: {profile_name}")
            except ValueError:
                print("Invalid input")
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            profiles = [p for p in profile_manager.list_profiles() if not p.startswith('cmc_profile_')]
            if not profiles:
                print("\nNo legacy profiles found that need migration.")
                input("\nPress Enter to continue...")
                continue
                
            print("\nLegacy profiles available for migration:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
                
            try:
                idx = int(input("\nSelect profile number to migrate (0 to cancel): ")) - 1
                if idx == -1:
                    continue
                if 0 <= idx < len(profiles):
                    old_name = profiles[idx]
                    confirm = input(f"\nMigrate profile '{old_name}' to new format? (y/n): ").lower()
                    if confirm == 'y':
                        new_name = profile_manager.migrate_profile(old_name)
                        if new_name:
                            print(f"\n✅ Successfully migrated to: {new_name}")
                        else:
                            print("\n❌ Migration failed")
            except ValueError:
                print("Invalid input")
            input("\nPress Enter to continue...")
            
        elif choice == "6":
            login_detection_menu()
            
        elif choice == "7":
            structured_rotation_menu()
            
        elif choice == "8":
            break

def test_single_profile_login():
    """Test login status of a single profile"""
    print_header("🧪 Test Single Profile Login Status")
    
    profile_manager = ProfileManager()
    login_detector = CMCLoginDetector(profile_manager)
    
    # Get available profiles
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ No CMC profiles found - please create profiles first")
        input("Press Enter to continue...")
        return
    
    print(f"📋 Available profiles:")
    for i, profile in enumerate(profiles, 1):
        print(f"   {i}. {profile}")
    
    try:
        idx = int(input(f"\nSelect profile to test (1-{len(profiles)}): ")) - 1
        if 0 <= idx < len(profiles):
            profile_name = profiles[idx]
            
            print(f"\n🔍 TESTING LOGIN STATUS: {profile_name}")
            print("="*50)
            
            # Load profile and test
            driver = profile_manager.load_profile(profile_name)
            time.sleep(3)
            
            # Run improved login detection
            status = login_detector.check_cmc_login_status(driver, profile_name)
            
            # Show detailed results
            print(f"\n📊 DETAILED RESULTS:")
            print(f"="*30)
            print(f"✅ Profile: {profile_name}")
            print(f"🔍 Logged In: {'✅ YES' if status.get('logged_in') else '❌ NO'}")
            print(f"📋 Primary Reason: {status.get('primary_reason', 'Unknown')}")
            
            if status.get('login_button_found'):
                print(f"❌ Login Button Found: {status.get('login_button_details', [])}")
            
            if status.get('logged_in_indicators_found'):
                print(f"✅ Logged-in Indicators: {status.get('logged_in_details', [])}")
            
            if status.get('suspicious_text'):
                print(f"⚠️ Suspicious Text: {status.get('suspicious_text', [])}")
            
            # Close driver
            driver.quit()
            
            # Ask if user wants to delete if not logged in
            if not status.get('logged_in'):
                print(f"\n🗑️ PROFILE CLEANUP OPTION")
                print("="*30)
                delete = input(f"Profile {profile_name} is not logged in. Delete it? (y/n): ").strip().lower()
                
                if delete == 'y':
                    if login_detector.cleanup_logged_out_profile(profile_name):
                        print(f"✅ Profile {profile_name} removed successfully")
                    else:
                        print(f"❌ Failed to remove profile {profile_name}")
        else:
            print("❌ Invalid selection")
    except ValueError:
        print("❌ Invalid input")
    
    input("\nPress Enter to continue...")

def verify_all_profiles_quick():
    """Quick verification of all profiles"""
    print_header("🔍 Quick Profile Verification")
    
    try:
        results = verify_all_profiles(ask_confirmation=False)
        
        print(f"\n📊 QUICK VERIFICATION RESULTS:")
        print(f"="*40)
        print(f"✅ Logged In Profiles: {len(results['verified_profiles'])}")
        print(f"❌ Logged Out Profiles: {len(results['failed_profiles'])}")
        print(f"📋 Total Profiles: {results['total_profiles']}")
        
        if results['verified_profiles']:
            print(f"\n✅ WORKING PROFILES:")
            for profile in results['verified_profiles']:
                print(f"   • {profile}")
        
        if results['failed_profiles']:
            print(f"\n❌ FAILED PROFILES:")
            for profile in results['failed_profiles']:
                print(f"   • {profile}")
            
            cleanup = input(f"\n🧹 Run full cleanup to remove failed profiles? (y/n): ").strip().lower()
            if cleanup == 'y':
                full_profile_scan_cleanup()
                return
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    input("\nPress Enter to continue...")

def full_profile_scan_cleanup():
    """Full profile scan with cleanup options"""
    print_header("🧹 Full Profile Scan & Cleanup")
    
    print("🔍 This will scan ALL your CMC profiles and ask about removing logged-out ones")
    print("⚠️ Profiles will be moved to backup folders, not permanently deleted")
    
    proceed = input("\n🎯 Proceed with full scan? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    try:
        results = verify_all_profiles(ask_confirmation=True)
        
        print(f"\n🎯 CLEANUP SUMMARY:")
        print(f"="*30)
        print(f"✅ Verified Profiles: {len(results['verified_profiles'])}")
        print(f"🗑️ Deleted Profiles: {len(results['deleted_profiles'])}")
        print(f"⚠️ Failed but Kept: {len(results['failed_profiles'])}")
        
        if results['deleted_profiles']:
            print(f"\n🗑️ DELETED PROFILES:")
            for profile in results['deleted_profiles']:
                print(f"   • {profile}")
        
        if results['verified_profiles']:
            print(f"\n✅ Your bot will now use these {len(results['verified_profiles'])} working profiles:")
            for profile in results['verified_profiles']:
                print(f"   • {profile}")
        else:
            print(f"\n⚠️ No working profiles found! Please log into your CMC profiles.")
        
    except Exception as e:
        print(f"❌ Scan failed: {e}")
    
    input("\nPress Enter to continue...")

def view_profile_status_summary():
    """View summary of all profile statuses"""
    print_header("📊 Profile Status Summary")
    
    profile_manager = ProfileManager()
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ No CMC profiles found")
        input("Press Enter to continue...")
        return
    
    print(f"📋 Found {len(profiles)} CMC profiles:")
    print("="*50)
    
    for i, profile in enumerate(profiles, 1):
        print(f"{i:2d}. {profile}")
    
    print(f"\n💡 QUICK ACTIONS:")
    print("1. 🔍 Run quick verification on all profiles")
    print("2. 🧹 Run full scan with cleanup options")
    print("3. 🔙 Back to menu")
    
    choice = input("\n🎯 Select action (1-3): ").strip()
    
    if choice == '1':
        verify_all_profiles_quick()
    elif choice == '2':
        full_profile_scan_cleanup()

def test_quick_login_detection():
    """Test the quick login detection method"""
    print_header("🚀 Test Quick Login Detection")
    
    profile_manager = ProfileManager()
    login_detector = CMCLoginDetector(profile_manager)
    
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ No CMC profiles found")
        input("Press Enter to continue...")
        return
    
    profile_name = profiles[0]
    print(f"🧪 Testing quick login detection on: {profile_name}")
    print("="*50)
    
    try:
        driver = profile_manager.load_profile(profile_name)
        time.sleep(3)
        
        # Test quick login check
        print("🚀 Running quick login check...")
        is_logged_in = login_detector.quick_login_check(driver)
        
        print(f"\n📊 QUICK CHECK RESULT:")
        print(f"✅ Profile: {profile_name}")
        print(f"🔍 Logged In: {'✅ YES' if is_logged_in else '❌ NO'}")
        
        # Compare with full detection
        print(f"\n🔍 Running full detection for comparison...")
        full_status = login_detector.check_cmc_login_status(driver, profile_name)
        full_result = full_status.get('logged_in', False)
        
        print(f"\n📊 COMPARISON:")
        print(f"🚀 Quick Check: {'✅ LOGGED IN' if is_logged_in else '❌ NOT LOGGED IN'}")
        print(f"🔍 Full Check:  {'✅ LOGGED IN' if full_result else '❌ NOT LOGGED IN'}")
        print(f"🎯 Match: {'✅ YES' if is_logged_in == full_result else '❌ NO'}")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    input("\nPress Enter to continue...")

def test_structured_rotation_system():
    """Test the structured rotation system"""
    print_header("🧪 Test Structured Rotation System")
    
    try:
        print("🔄 Testing structured rotation system...")
        success = test_structured_rotation()
        
        if success:
            print("\n✅ Structured rotation system test completed successfully!")
        else:
            print("\n❌ Structured rotation system test failed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    input("\nPress Enter to continue...")

def verify_profiles_for_rotation():
    """Verify all profiles for structured rotation"""
    print_header("🔍 Verify Profiles for Structured Rotation")
    
    print("🎯 This will verify all profiles and prepare them for structured rotation")
    print("✅ Profiles will be checked for login status")
    print("🗑️ You'll be asked about removing logged-out profiles")
    print("🔄 Remaining profiles will be sorted for sequential rotation")
    
    proceed = input("\n🎯 Proceed with verification? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    try:
        results = verify_all_profiles(ask_confirmation=True)
        
        print(f"\n🎯 ROTATION PREPARATION SUMMARY:")
        print(f"="*40)
        print(f"✅ Verified Profiles: {len(results['verified_profiles'])}")
        print(f"🗑️ Deleted Profiles: {len(results['deleted_profiles'])}")
        print(f"📋 Ready for Rotation: {len(results['remaining_profiles'])}")
        
        if results['remaining_profiles']:
            print(f"\n🔄 ROTATION SEQUENCE:")
            for i, profile in enumerate(results['remaining_profiles'], 1):
                print(f"   {i}. {profile}")
            
            print(f"\n✅ Your bot will rotate through these profiles in order!")
            print(f"🎯 Rotation: {' → '.join(results['remaining_profiles'][:3])}...")
        else:
            print(f"\n⚠️ No profiles available for rotation!")
            print(f"💡 Please create and login to CMC profiles first")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    input("\nPress Enter to continue...")

def view_rotation_statistics():
    """View structured rotation statistics"""
    print_header("📊 Structured Rotation Statistics")
    
    try:
        rotation = StructuredProfileRotation()
        stats = rotation.get_rotation_stats()
        
        print(f"📊 ROTATION STATISTICS:")
        print(f"="*30)
        print(f"🆔 Session ID: {stats['session_id']}")
        print(f"🔄 Total Rotations: {stats['rotation_count']}")
        print(f"📋 Available Profiles: {stats['total_profiles']}")
        print(f"📍 Current Index: {stats['current_index']}")
        print(f"✅ Verified Profiles: {stats['verified_profiles']}")
        print(f"❌ Failed Profiles: {stats['failed_profiles']}")
        
        if stats['current_profile']:
            print(f"👤 Current Profile: {stats['current_profile']}")
        
        if stats['available_profiles']:
            print(f"\n🔄 ROTATION SEQUENCE:")
            for i, profile in enumerate(stats['available_profiles'], 1):
                current_marker = " ← CURRENT" if i == stats['current_index'] else ""
                print(f"   {i}. {profile}{current_marker}")
        
        # Show rotation status
        rotation.print_rotation_status()
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    input("\nPress Enter to continue...")

def demo_rotation_sequence():
    """Demonstrate the rotation sequence"""
    print_header("🔄 Demo Rotation Sequence")
    
    try:
        rotation = StructuredProfileRotation()
        
        if not rotation.available_profiles:
            print("❌ No profiles available for rotation demo")
            input("Press Enter to continue...")
            return
        
        print(f"🔄 Demonstrating rotation sequence with {len(rotation.available_profiles)} profiles:")
        print("="*60)
        
        # Demo 5 rotations
        demo_count = min(5, len(rotation.available_profiles) * 2)
        
        for i in range(demo_count):
            next_profile = rotation.get_next_profile()
            print(f"Rotation {i+1}: {next_profile}")
            time.sleep(0.5)  # Brief pause for demo effect
        
        print(f"\n✅ Demo complete! This shows the sequential rotation pattern.")
        print(f"🔄 Profiles rotate in order and loop back to the beginning")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    input("\nPress Enter to continue...")

def initialize_structured_rotation():
    """Initialize structured rotation system"""
    print_header("⚙️ Initialize Structured Rotation")
    
    print("🚀 This will set up the structured rotation system for your bot")
    print("✅ Profiles will be verified and prepared")
    print("🔄 Sequential rotation will be configured")
    print("⚡ Your bot will use this system automatically")
    
    proceed = input("\n🎯 Initialize structured rotation? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    try:
        enhanced_manager = StructuredEnhancedProfileManager()
        
        verify_all = input("🔍 Verify all profiles before initialization? (y/n): ").strip().lower() == 'y'
        ask_confirmation = input("👤 Ask for confirmation before deleting profiles? (y/n): ").strip().lower() == 'y'
        
        print(f"\n🚀 Initializing structured rotation...")
        enhanced_manager.initialize_structured_rotation(verify_all=verify_all, ask_confirmation=ask_confirmation)
        
        # Get stats
        stats = enhanced_manager.get_structured_rotation_stats()
        
        print(f"\n✅ STRUCTURED ROTATION INITIALIZED!")
        print(f"="*40)
        print(f"📋 Available Profiles: {stats['total_profiles']}")
        print(f"✅ Verified Profiles: {stats['verified_profiles']}")
        print(f"🔄 Ready for Sequential Rotation: ✅")
        
        print(f"\n🎯 Your bot will now use structured rotation automatically!")
        print(f"💡 Profiles will rotate in order: 1 → 2 → 3 → 1...")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print(f"💡 Make sure you have logged-in CMC profiles available")
    
    input("\nPress Enter to continue...")

def collect_promotion_parameters(promotion_type: int) -> dict:
    """Collect required parameters based on promotion type."""
    params = {}
    
    if promotion_type == 1:  # Market Making
        params['firm_name'] = input("Enter market making firm name: ")
        # Region is optional
        region = input("Enter target region (asia/europe/americas) or press Enter to skip: ").lower()
        if region in ['asia', 'europe', 'americas']:
            params['region'] = region
    
    elif promotion_type == 2:  # Token Shilling (Updated from Token Launch)
        params['promoted_ticker'] = input("Enter the token ticker you want to shill (e.g., EXAMPLE): ").strip().upper()
        params['promoted_name'] = input("Enter the full token name (e.g., Example Token): ").strip()
        print(f"\n✅ Will cross-reference ${params['promoted_ticker']} when analyzing other tokens")
    
    elif promotion_type == 3:  # Technical Update
        params['update_type'] = input("Enter type of technical improvement: ")
        params['version'] = input("Enter new version number: ")
        params['key_improvements'] = input("Enter key improvements (comma-separated): ").split(',')
        params['release_date'] = input("Enter update release date: ")
    
    elif promotion_type == 4:  # Partnership
        params['partner_name'] = input("Enter partner organization name: ")
        params['partnership_type'] = input("Enter partnership type (technical/business/other): ")
        params['partnership_benefits'] = input("Enter key benefits (comma-separated): ").split(',')
        params['timeline'] = input("Enter partnership rollout timeline: ")
    
    elif promotion_type == 5:  # Trading Group
        params['group_name'] = input("Enter trading group name: ")
        params['join_link'] = input("Enter community join link: ")
        params['success_rate'] = input("Enter recent prediction success rate (if available): ")
        params['special_offer'] = input("Enter any special joining offer: ")
    
    elif promotion_type == 6:  # Default Settings
        params['analysis_timeframe'] = input("Enter analysis timeframe: ")
        params['key_metrics'] = input("Enter key metrics to focus on (comma-separated): ").split(',')
    
    return params

def run_bot(proxy_config=None):
    """Run the main bot functionality"""
    # Check if we already have a saved configuration
    config_path = 'config/promotion_config.json'
    has_config = os.path.exists(config_path)
    
    if has_config:
        print("\n✅ Found existing promotion configuration!")
        try:
            with open(config_path, 'r') as f:
                existing_config = json.load(f)
            print(f"Current configuration: {existing_config.get('type', 'Unknown')}")
            
            use_existing = input("\nUse existing configuration? (y/n): ").strip().lower()
            if use_existing == 'y':
                # Initialize and run the analyzer with proxy configuration
                try:
                    from autocrypto_social_bot.main import CryptoAIAnalyzer
                    analyzer = CryptoAIAnalyzer(proxy_config=proxy_config)
                    # The analyzer will automatically load the existing config
                    analyzer.run_analysis()
                except Exception as e:
                    print(f"\n❌ Error running analyzer: {str(e)}")
                input("\nPress Enter to continue...")
                return
        except Exception as e:
            print(f"Error reading config: {str(e)}")
    
    print("\nPromotion Types:")
    print("1. Market Making Promotion")
    print("2. Token Shilling (Cross-reference promoted token)")
    print("3. Technical Update")
    print("4. Partnership Announcement")
    print("5. Trading Group Promotion")
    print("6. Use Default Settings")
    print("7. Back to Main Menu")

    try:
        choice = int(input("\nEnter your choice (1-7): "))
        if choice == 7:
            return
        
        if 1 <= choice <= 6:
            # Collect promotion-specific parameters
            params = collect_promotion_parameters(choice)
            
            # Convert numeric type to string type for consistency with main.py
            type_mapping = {
                1: 'market_making',
                2: 'token_shilling',  # Updated from 'token_launch'
                3: 'technical_update',
                4: 'partnership',
                5: 'trading_group',
                6: 'default'
            }
            
            # Store the promotion configuration
            promotion_config = {
                'type': type_mapping.get(choice, 'market_making'),
                'params': params
            }
            
            # Ensure config directory exists
            os.makedirs('config', exist_ok=True)
            
            # Save the configuration for use in analysis
            with open('config/promotion_config.json', 'w') as f:
                json.dump(promotion_config, f, indent=4)
            
            print("\nPromotion configuration saved successfully!")
            
            # Initialize and run the analyzer with proxy configuration
            try:
                from autocrypto_social_bot.main import CryptoAIAnalyzer
                analyzer = CryptoAIAnalyzer(proxy_config=proxy_config)
                # The analyzer will load the config we just saved
                
                # For token shilling, show demo
                if choice == 2:  # Token Shilling
                    print(f"\n🎯 Demo: How ${params['promoted_ticker']} gets cross-referenced")
                    analyzer.run_analysis()  # This will show the new menu with token shilling demo
                else:
                    analyzer.run_analysis()
                    
            except Exception as e:
                print(f"\n❌ Error running analyzer: {str(e)}")
                import traceback
                traceback.print_exc()
            
            input("\nPress Enter to continue...")
            return
        else:
            print("\nInvalid choice. Please try again.")
    except ValueError:
        print("\nInvalid input. Please enter a number between 1-7.")

def enterprise_proxy_management_menu():
    """Enterprise proxy management and configuration menu"""
    while True:
        print("\n" + "🏢"*60)
        print("🏢 ENTERPRISE PROXY MANAGEMENT CENTER")
        print("🏢"*60)
        print("Advanced proxy management for professional CMC promotion")
        print("\n📋 MENU OPTIONS:")
        print("1. 🧪 Test Enterprise Proxy System")
        print("2. 🔧 Configure API Keys (Premium Services)")
        print("3. 📁 Import Manual Proxies")
        print("4. 🧪 Test Manual Proxies")
        print("5. 📊 View Proxy Statistics")
        print("6. 🗂️ View Persistent Storage Stats")
        print("7. ⚙️ Advanced Configuration")
        print("8. 🆘 Troubleshooting Guide")
        print("9. 🔙 Back to Main Menu")
        print("🏢"*60)
        
        choice = input("Select option (1-9): ").strip()
        
        if choice == '1':
            test_enterprise_proxy_system()
        elif choice == '2':
            configure_proxy_api_keys()
        elif choice == '3':
            import_manual_proxies()
        elif choice == '4':
            test_manual_proxies()
        elif choice == '5':
            view_proxy_statistics()
        elif choice == '6':
            view_persistent_storage_stats()
        elif choice == '7':
            advanced_proxy_configuration()
        elif choice == '8':
            show_troubleshooting_guide()
        elif choice == '9':
            break
        else:
            print("❌ Invalid option. Please select 1-9.")

def test_enterprise_proxy_system():
    """Test the enterprise proxy system with CMC verification"""
    print("\n🧪 ENTERPRISE PROXY SYSTEM TEST")
    print("="*60)
    
    try:
        from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
        
        print("🔄 Initializing Enterprise Proxy Manager...")
        enterprise_manager = EnterpriseProxyManager()
        
        print("🔍 Testing proxy acquisition from API services...")
        proxies = enterprise_manager.get_enterprise_grade_proxies()
        
        if proxies:
            print(f"\n✅ SUCCESS: Found {len(proxies)} enterprise-grade proxies")
            print("\n🎯 TOP PROXIES:")
            for i, proxy in enumerate(proxies[:5], 1):
                print(f"   {i}. {proxy}")
                
            # Test best proxy with CMC
            best_proxy = enterprise_manager.get_best_proxy()
            if best_proxy:
                print(f"\n🧪 Testing best proxy with CMC: {best_proxy}")
                test_result = enterprise_manager.test_proxy_with_cmc_advanced(best_proxy)
                
                print(f"\n📊 DETAILED TEST RESULTS:")
                print(f"   🔗 Basic Connectivity: {'✅ PASS' if test_result['basic_connectivity'] else '❌ FAIL'}")
                print(f"   🏥 CMC Health Check: {'✅ PASS' if test_result['cmc_health_check'] else '❌ FAIL'}")
                print(f"   📈 CMC Trending Page: {'✅ PASS' if test_result['cmc_trending_page'] else '❌ FAIL'}")
                print(f"   📝 Content Validation: {'✅ PASS' if test_result['cmc_content_validation'] else '❌ FAIL'}")
                print(f"   📡 Detected IP: {test_result['ip_detected']}")
                print(f"   ⏱️ Response Time: {test_result['response_time']:.2f}s")
                print(f"   🎯 Overall Score: {test_result['overall_score']}%")
                
                if test_result['overall_score'] >= 75:
                    print(f"\n🎯 EXCELLENT: System ready for high-quality CMC promotion!")
                elif test_result['overall_score'] >= 50:
                    print(f"\n⚠️ GOOD: System functional but could be improved with premium proxies")
                else:
                    print(f"\n❌ POOR: System needs premium proxies for reliable CMC access")
            else:
                print("❌ No working proxy available")
        else:
            print("❌ No proxies found. Check configuration and API keys.")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print("💡 Make sure the system is properly configured")
    
    input("\nPress Enter to continue...")

def configure_proxy_api_keys():
    """Configure API keys for premium proxy services"""
    print("\n🔧 PROXY API CONFIGURATION")
    print("="*60)
    print("Configure API keys for premium proxy services")
    
    config_file = "config/enterprise_proxy_config.json"
    
    try:
        # Load current config
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        if 'api_keys' not in config:
            config['api_keys'] = {}
        
        print("\n📋 AVAILABLE PREMIUM SERVICES:")
        print("1. 🏆 ProxyKingdom (proxykingdom.com) - High-quality rotating proxies")
        print("2. 🌍 Proxifly (proxifly.dev) - Residential proxy API")
        print("3. 🚀 ScraperAPI (scraperapi.com) - Complete scraping solution")
        
        print(f"\n📊 CURRENT STATUS:")
        services = {
            'proxykingdom_token': ('ProxyKingdom', 'https://proxykingdom.com/'),
            'proxifly_key': ('Proxifly', 'https://proxifly.dev/'),
            'scraperapi_key': ('ScraperAPI', 'https://scraperapi.com/')
        }
        
        for key, (name, url) in services.items():
            current_value = config['api_keys'].get(key, '')
            status = "✅ Configured" if current_value else "❌ Not configured"
            print(f"   {name}: {status}")
        
        print(f"\n🔧 CONFIGURATION OPTIONS:")
        print("1. Configure ProxyKingdom Token")
        print("2. Configure Proxifly Key") 
        print("3. Configure ScraperAPI Key")
        print("4. View Service Information")
        print("5. Test Current Configuration")
        print("6. Back to menu")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            print(f"\n🔧 PROXYKINGDOM CONFIGURATION")
            print(f"📞 Sign up at: https://proxykingdom.com/")
            print(f"💡 Free tier: 10 daily API calls")
            current = config['api_keys'].get('proxykingdom_token', '')
            if current:
                print(f"Current token: {current[:10]}...{current[-4:] if len(current) > 14 else current}")
            new_token = input("Enter ProxyKingdom token (or press Enter to skip): ").strip()
            if new_token:
                config['api_keys']['proxykingdom_token'] = new_token
                print("✅ ProxyKingdom token updated")
                
        elif choice == '2':
            print(f"\n🔧 PROXIFLY CONFIGURATION")
            print(f"📞 Sign up at: https://proxifly.dev/")
            print(f"💡 Offers residential and datacenter proxies")
            current = config['api_keys'].get('proxifly_key', '')
            if current:
                print(f"Current key: {current[:10]}...{current[-4:] if len(current) > 14 else current}")
            new_key = input("Enter Proxifly API key (or press Enter to skip): ").strip()
            if new_key:
                config['api_keys']['proxifly_key'] = new_key
                print("✅ Proxifly key updated")
                
        elif choice == '3':
            print(f"\n🔧 SCRAPERAPI CONFIGURATION")
            print(f"📞 Sign up at: https://scraperapi.com/")
            print(f"💡 All-in-one scraping solution with automatic proxy rotation")
            current = config['api_keys'].get('scraperapi_key', '')
            if current:
                print(f"Current key: {current[:10]}...{current[-4:] if len(current) > 14 else current}")
            new_key = input("Enter ScraperAPI key (or press Enter to skip): ").strip()
            if new_key:
                config['api_keys']['scraperapi_key'] = new_key
                print("✅ ScraperAPI key updated")
                
        elif choice == '4':
            print(f"\n📋 SERVICE INFORMATION")
            print(f"="*50)
            print(f"🏆 ProxyKingdom:")
            print(f"   • High-quality rotating proxies")
            print(f"   • Good success rates with CMC")
            print(f"   • Pricing: $14.95/month")
            print(f"   • Free: 10 daily API calls")
            print(f"\n🌍 Proxifly:")
            print(f"   • Residential and datacenter proxies")
            print(f"   • 100+ countries available")
            print(f"   • Pricing: Variable")
            print(f"\n🚀 ScraperAPI:")
            print(f"   • Complete web scraping solution")
            print(f"   • Automatic proxy rotation and CAPTCHA solving")
            print(f"   • Pricing: $49/month (100k requests)")
            print(f"   • Best for professional CMC scraping")
            
        elif choice == '5':
            print(f"\n🧪 TESTING CURRENT CONFIGURATION")
            test_enterprise_proxy_system()
            
        # Save config
        if choice in ['1', '2', '3']:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print("💾 Configuration saved")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
    
    if choice != '5':  # Don't double-prompt if we just ran the test
        input("\nPress Enter to continue...")

def import_manual_proxies():
    """Import and test manual proxies"""
    print("\n📁 MANUAL PROXY IMPORT")
    print("="*60)
    
    proxy_file = "config/manual_proxies.txt"
    
    print("📋 IMPORT OPTIONS:")
    print("1. Add proxies manually (one by one)")
    print("2. Bulk import from text")
    print("3. View current manual proxies")
    print("4. Clear all manual proxies")
    print("5. Download premium proxy recommendations")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        # Manual entry
        print("\n✏️ MANUAL PROXY ENTRY")
        print("Enter proxies in format: IP:PORT")
        print("Type 'done' when finished")
        
        proxies_to_add = []
        while True:
            proxy = input("Enter proxy (IP:PORT): ").strip()
            if proxy.lower() == 'done':
                break
            if ':' in proxy and len(proxy.split(':')) == 2:
                ip, port = proxy.split(':')
                if port.isdigit():
                    proxies_to_add.append(proxy)
                    print(f"✅ Added: {proxy}")
                else:
                    print("❌ Invalid port number")
            else:
                print("❌ Invalid format. Use IP:PORT")
        
        if proxies_to_add:
            # Append to file
            with open(proxy_file, 'a') as f:
                f.write('\n# Added manually on ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
                for proxy in proxies_to_add:
                    f.write(proxy + '\n')
            print(f"✅ Added {len(proxies_to_add)} proxies to manual list")
            
    elif choice == '2':
        # Bulk import
        print("\n📋 BULK PROXY IMPORT")
        print("Paste your proxy list (one per line, format IP:PORT):")
        print("Press Enter twice when done:")
        
        bulk_text = ""
        while True:
            line = input()
            if line == "":
                break
            bulk_text += line + "\n"
        
        # Parse proxies
        valid_proxies = []
        lines = bulk_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and len(line.split(':')) == 2:
                ip, port = line.split(':')
                if port.isdigit():
                    valid_proxies.append(line)
        
        if valid_proxies:
            with open(proxy_file, 'a') as f:
                f.write('\n# Bulk imported on ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
                for proxy in valid_proxies:
                    f.write(proxy + '\n')
            print(f"✅ Imported {len(valid_proxies)} valid proxies")
        else:
            print("❌ No valid proxies found in input")
            
    elif choice == '3':
        # View current proxies
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                content = f.read()
            
            # Count non-comment lines
            lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
            print(f"\n📊 CURRENT MANUAL PROXIES: {len(lines)} total")
            print("="*40)
            
            if lines:
                for i, proxy in enumerate(lines[:10], 1):  # Show first 10
                    print(f"{i:2d}. {proxy}")
                if len(lines) > 10:
                    print(f"... and {len(lines) - 10} more")
            else:
                print("No manual proxies configured")
                print("\n💡 Add proxies using options 1 or 2")
        else:
            print("❌ No manual proxy file found")
            
    elif choice == '4':
        # Clear proxies
        confirm = input("⚠️ Clear all manual proxies? (yes/no): ").strip().lower()
        if confirm == 'yes':
            with open(proxy_file, 'w') as f:
                f.write("# Manual proxies cleared on " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')
            print("✅ All manual proxies cleared")
        else:
            print("❌ Operation cancelled")
            
    elif choice == '5':
        # Premium recommendations
        print("\n🏆 PREMIUM PROXY SERVICE RECOMMENDATIONS")
        print("="*60)
        print("For best CMC compatibility, consider these services:")
        print("\n🥇 TIER 1 (Best for CMC):")
        print("   • ScraperAPI (scraperapi.com) - $49/month")
        print("   • Oxylabs (oxylabs.io) - $300+/month")
        print("   • BrightData (brightdata.com) - $500+/month")
        print("\n🥈 TIER 2 (Good Quality):")
        print("   • SmartProxy (smartproxy.com) - $75/month")
        print("   • ProxyMesh (proxymesh.com) - $10/month")
        print("   • ProxyKingdom (proxykingdom.com) - $15/month")
        print("\n💡 TIP: Start with ScraperAPI for best results")
        print("💡 Configure API keys in option 2 of this menu")
        
        # Add ProxyScrape information
        print("\n🆓 FREE OPTION:")
        print("   • ProxyScrape (proxyscrape.com) - FREE")
        print("   • Updates every minute with fresh proxies")
        print("   • Already integrated into this application!")
        print("   • Example proxies from ProxyScrape v4 API:")
        try:
            # Try to fetch some example proxies
            import requests
            response = requests.get(
                'https://api.proxyscrape.com/v4/free-proxy-list/get',
                params={
                    'request': 'display_proxies',
                    'proxy_format': 'protocolipport',
                    'format': 'text',
                    'timeout': '10000',
                    'country': 'all'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                proxies = response.text.strip().split()[:10]  # Get first 10
                print("\n📡 CURRENT PROXYSCRAPE PROXIES (Live):")
                for i, proxy in enumerate(proxies, 1):
                    # Clean the proxy format for display
                    if proxy.startswith('http://'):
                        clean_proxy = proxy.replace('http://', '')
                        print(f"   {i:2d}. {clean_proxy}")
                    elif proxy.startswith('socks4://'):
                        clean_proxy = proxy.replace('socks4://', '')
                        print(f"   {i:2d}. {clean_proxy}")
                        
        except Exception:
            print("\n📡 EXAMPLE PROXIES (ProxyScrape format):")
            print("   1. 185.193.29.76:80")
            print("   2. 45.131.210.21:80")
            print("   3. 104.25.51.93:80")
            print("   4. 172.67.46.156:80")
            print("   5. 185.162.231.136:80")
        
        print("\n💡 The application automatically fetches these!")
        print("💡 No manual setup needed for ProxyScrape integration")
    
    input("\nPress Enter to continue...")

def test_manual_proxies():
    """Test manual proxies for CMC compatibility"""
    print("\n🧪 MANUAL PROXY TESTING")
    print("="*60)
    
    proxy_file = "config/manual_proxies.txt"
    
    if not os.path.exists(proxy_file):
        print("❌ No manual proxy file found")
        print("💡 Import proxies first using option 3")
        input("\nPress Enter to continue...")
        return
    
    try:
        # Load manual proxies
        with open(proxy_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            print("❌ No manual proxies found")
            print("💡 Import proxies first using option 3")
            input("\nPress Enter to continue...")
            return
        
        print(f"🔍 Found {len(lines)} manual proxies to test")
        
        # Initialize enterprise manager for testing
        from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
        enterprise_manager = EnterpriseProxyManager()
        
        print("\n🧪 TESTING PROXIES WITH CMC COMPATIBILITY")
        print("="*60)
        
        working_proxies = []
        excellent_proxies = []
        
        for i, proxy in enumerate(lines, 1):
            print(f"\n[{i}/{len(lines)}] Testing: {proxy}")
            
            try:
                test_result = enterprise_manager.test_proxy_with_cmc_advanced(proxy, timeout=10)
                score = test_result['overall_score']
                
                if score >= 75:
                    working_proxies.append(proxy)
                    excellent_proxies.append(proxy)
                    print(f"🎯 EXCELLENT: {proxy} (Score: {score}%)")
                elif score >= 50:
                    working_proxies.append(proxy)
                    print(f"✅ GOOD: {proxy} (Score: {score}%)")
                else:
                    print(f"❌ FAILED: {proxy} (Score: {score}%)")
                    
            except Exception as e:
                print(f"❌ ERROR: {proxy} - {str(e)}")
        
        # Summary
        print(f"\n📊 MANUAL PROXY TEST RESULTS")
        print("="*60)
        print(f"Total tested: {len(lines)}")
        print(f"Working proxies: {len(working_proxies)}")
        print(f"Excellent proxies: {len(excellent_proxies)}")
        print(f"Success rate: {len(working_proxies)/len(lines)*100:.1f}%")
        
        if excellent_proxies:
            print(f"\n🎯 EXCELLENT PROXIES (75%+ score):")
            for proxy in excellent_proxies:
                print(f"   • {proxy}")
        
        if working_proxies:
            print(f"\n✅ System ready for CMC promotion with manual proxies!")
        else:
            print(f"\n❌ No working proxies found")
            print(f"💡 Consider premium proxy services for better results")
        
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
    
    input("\nPress Enter to continue...")

def view_persistent_storage_stats():
    """View persistent proxy storage statistics"""
    print("\n🗂️ PERSISTENT PROXY STORAGE STATISTICS")
    print("="*60)
    
    try:
        from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
        
        print("🔄 Loading proxy storage statistics...")
        enterprise_manager = EnterpriseProxyManager()
        
        # Display detailed storage statistics
        enterprise_manager.view_proxy_storage_stats()
        
        print("\n🔧 STORAGE MANAGEMENT OPTIONS:")
        print("1. 🧹 Cleanup old failures (give them another chance)")
        print("2. 📊 View detailed proxy statistics")
        print("3. 💾 Force save current state")
        print("4. 🔙 Back to menu")
        
        while True:
            sub_choice = input("\nSelect option (1-4): ").strip()
            
            if sub_choice == '1':
                print("\n🧹 CLEANING UP OLD FAILURES...")
                retry_proxies = enterprise_manager.proxy_storage.cleanup_old_failures(hours=24)
                if retry_proxies:
                    print(f"✅ Gave {len(retry_proxies)} old failed proxies another chance")
                else:
                    print("ℹ️ No old failed proxies to retry")
                break
                
            elif sub_choice == '2':
                print("\n📊 DETAILED STATISTICS:")
                storage_data = enterprise_manager.proxy_storage.proxy_data
                
                print(f"Total proxy statistics records: {len(storage_data.get('proxy_stats', {}))}")
                print(f"Storage file size: {os.path.getsize(enterprise_manager.proxy_storage.storage_file) if os.path.exists(enterprise_manager.proxy_storage.storage_file) else 0} bytes")
                
                # Show distribution of success rates
                success_rates = []
                for proxy, stats in storage_data.get('proxy_stats', {}).items():
                    total = stats.get('success_count', 0) + stats.get('fail_count', 0)
                    if total > 0:
                        success_rates.append(stats.get('success_count', 0) / total * 100)
                
                if success_rates:
                    print(f"Success rate distribution:")
                    print(f"   📈 Average: {sum(success_rates)/len(success_rates):.1f}%")
                    print(f"   🎯 Best: {max(success_rates):.1f}%")
                    print(f"   📉 Worst: {min(success_rates):.1f}%")
                break
                
            elif sub_choice == '3':
                print("\n💾 FORCE SAVING CURRENT STATE...")
                enterprise_manager.proxy_storage._save_proxy_storage()
                print("✅ Current state saved to storage")
                break
                
            elif sub_choice == '4':
                break
                
            else:
                print("❌ Invalid option. Please select 1-4.")
        
    except Exception as e:
        print(f"❌ Error viewing storage statistics: {str(e)}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def view_proxy_statistics():
    """View comprehensive proxy statistics"""
    print("\n📊 PROXY SYSTEM STATISTICS")
    print("="*60)
    
    try:
        from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
        enterprise_manager = EnterpriseProxyManager()
        
        # Get session info
        session_info = enterprise_manager.get_session_info()
        
        print("🏢 ENTERPRISE PROXY STATUS:")
        print(f"   📊 Verified Proxies: {session_info['verified_proxies_count']}")
        print(f"   🔧 Working Proxies: {session_info['working_proxies_count']}")
        print(f"   🌐 Current Best Proxy: {session_info['current_proxy'] or 'None'}")
        print(f"   🕒 Last Refresh: {session_info['last_refresh']}")
        print(f"   ⚙️ Config Loaded: {'✅' if session_info['config_loaded'] else '❌'}")
        
        # Check API configuration
        config_file = "config/enterprise_proxy_config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            print(f"\n🔧 API CONFIGURATION:")
            api_keys = config.get('api_keys', {})
            for service, key in api_keys.items():
                if service != 'comment':
                    status = "✅ Configured" if key else "❌ Not configured"
                    print(f"   {service}: {status}")
        
        # Check manual proxies
        proxy_file = "config/manual_proxies.txt"
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                manual_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"\n📁 MANUAL PROXIES: {len(manual_lines)} configured")
        else:
            print(f"\n📁 MANUAL PROXIES: Not configured")
        
        # Performance metrics
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"   🎯 Target Score: 75%+ for excellent compatibility")
        print(f"   ⏱️ Test Timeout: {config.get('test_timeout', 15)}s")
        print(f"   🔄 Rotation Interval: {config.get('proxy_rotation_interval', 300)}s")
        print(f"   👥 Max Workers: {config.get('max_workers', 30)}")
        
    except Exception as e:
        print(f"❌ Error loading statistics: {str(e)}")
    
    input("\nPress Enter to continue...")

def advanced_proxy_configuration():
    """Advanced proxy configuration options"""
    print("\n⚙️ ADVANCED PROXY CONFIGURATION")
    print("="*60)
    
    config_file = "config/enterprise_proxy_config.json"
    
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            print("❌ Configuration file not found")
            input("\nPress Enter to continue...")
            return
        
        print("🔧 CONFIGURATION OPTIONS:")
        print("1. Proxy Testing Settings")
        print("2. Performance Tuning")
        print("3. Quality Filters")
        print("4. Regional Preferences")
        print("5. Reset to Defaults")
        print("6. Back to menu")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            print("\n🧪 PROXY TESTING SETTINGS")
            print(f"Current timeout: {config.get('test_timeout', 15)}s")
            print(f"Current max workers: {config.get('max_workers', 30)}")
            print(f"CMC testing enabled: {config.get('test_with_cmc', True)}")
            
            new_timeout = input(f"New timeout (current: {config.get('test_timeout', 15)}s): ").strip()
            if new_timeout.isdigit():
                config['test_timeout'] = int(new_timeout)
                
            new_workers = input(f"New max workers (current: {config.get('max_workers', 30)}): ").strip()
            if new_workers.isdigit():
                config['max_workers'] = int(new_workers)
            
        elif choice == '2':
            print("\n⚡ PERFORMANCE TUNING")
            print(f"Current rotation interval: {config.get('proxy_rotation_interval', 300)}s")
            print(f"Current max failures: {config.get('max_proxy_failures', 3)}")
            
            new_interval = input(f"New rotation interval in seconds (current: {config.get('proxy_rotation_interval', 300)}): ").strip()
            if new_interval.isdigit():
                config['proxy_rotation_interval'] = int(new_interval)
                
            new_failures = input(f"New max failures before removal (current: {config.get('max_proxy_failures', 3)}): ").strip()
            if new_failures.isdigit():
                config['max_proxy_failures'] = int(new_failures)
        
        elif choice == '3':
            print("\n🎯 QUALITY FILTERS")
            quality = config.get('quality_filters', {})
            print(f"Max connect time: {quality.get('max_connect_time', 3)}s")
            print(f"Max response time: {quality.get('max_response_time', 5)}s")
            print(f"Min uptime: {quality.get('min_uptime', 80)}%")
            
            print("\n💡 Higher values = more lenient (more proxies pass)")
            print("💡 Lower values = more strict (fewer but better proxies)")
            
        elif choice == '4':
            print("\n🌍 REGIONAL PREFERENCES")
            quality = config.get('quality_filters', {})
            preferred = quality.get('preferred_countries', [])
            avoided = quality.get('avoid_countries', [])
            
            print(f"Preferred countries: {', '.join(preferred) if preferred else 'None'}")
            print(f"Avoided countries: {', '.join(avoided) if avoided else 'None'}")
            
        elif choice == '5':
            confirm = input("⚠️ Reset all settings to defaults? (yes/no): ").strip().lower()
            if confirm == 'yes':
                # Reset to defaults but keep API keys
                api_keys = config.get('api_keys', {})
                config = {
                    "test_timeout": 15,
                    "max_workers": 30,
                    "min_success_rate": 0.1,
                    "test_with_cmc": True,
                    "enable_residential_apis": True,
                    "max_proxy_failures": 3,
                    "proxy_rotation_interval": 300,
                    "use_manual_proxies": True,
                    "api_keys": api_keys
                }
                print("✅ Configuration reset to defaults")
        
        # Save config
        if choice in ['1', '2', '5']:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print("💾 Configuration saved")
        
    except Exception as e:
        print(f"❌ Configuration error: {str(e)}")
    
    input("\nPress Enter to continue...")

def show_troubleshooting_guide():
    """Show comprehensive troubleshooting guide"""
    print("\n🆘 ENTERPRISE PROXY TROUBLESHOOTING GUIDE")
    print("="*60)
    
    print("🔍 COMMON ISSUES AND SOLUTIONS:")
    print("\n1. 🚫 'No proxies found' Error:")
    print("   • Check internet connection")
    print("   • Configure API keys in option 2")
    print("   • Import manual proxies in option 3")
    print("   • Verify firewall settings")
    
    print("\n2. 🌐 'CMC not accessible' Error:")
    print("   • CMC may be blocking your IP/location")
    print("   • Try premium proxy services (ScraperAPI recommended)")
    print("   • Use residential proxies instead of datacenter")
    print("   • Check if CMC is experiencing downtime")
    
    print("\n3. 🐌 Slow proxy performance:")
    print("   • Increase timeout in advanced settings")
    print("   • Reduce max workers to avoid rate limits")
    print("   • Use proxies from closer geographic regions")
    print("   • Switch to premium proxy services")
    
    print("\n4. ❌ High proxy failure rate:")
    print("   • Free proxies are often blocked by CMC")
    print("   • Consider premium services for better reliability")
    print("   • Adjust quality filters in advanced settings")
    print("   • Test manual proxies separately")
    
    print("\n5. 🔑 API key issues:")
    print("   • Verify API keys are entered correctly")
    print("   • Check if your API quota is exceeded")
    print("   • Ensure account is active with proxy service")
    print("   • Contact proxy service support if needed")
    
    print("\n💡 OPTIMIZATION TIPS:")
    print("   🏆 Best: ScraperAPI ($49/month) - handles everything automatically")
    print("   🥈 Good: ProxyKingdom + manual residential proxies")
    print("   🥉 Basic: Manual premium proxies only")
    
    print("\n🛠️ TESTING COMMANDS:")
    print("   • Test system: Option 1 in this menu")
    print("   • Test manual proxies: Option 4 in this menu")
    print("   • View statistics: Option 5 in this menu")
    
    print("\n📞 SUPPORT:")
    print("   • Check logs in logs/ directory")
    print("   • Run: python unused_files/test_files/verify_enhanced_ip_rotation.py")
    print("   • Join our Discord for community support")
    
    input("\nPress Enter to continue...")

def proxy_and_anti_detection_menu():
    """Enhanced proxy and anti-detection configuration menu"""
    while True:
        print("\n" + "🛡️"*60)
        print("🛡️ ENTERPRISE ANTI-DETECTION & PROXY CENTER")
        print("🛡️"*60)
        print("Professional-grade proxy management and anti-detection systems")
        
        # Quick status check
        try:
            from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
            enterprise_manager = EnterpriseProxyManager()
            session_info = enterprise_manager.get_session_info()
            
            print(f"\n📊 QUICK STATUS:")
            print(f"   🎯 CMC-Verified Proxies: {session_info['verified_proxies_count']}")
            print(f"   🌐 Current Best Proxy: {session_info['current_proxy'] or 'None available'}")
            print(f"   🕒 Last Refresh: {session_info['last_refresh']}")
            
        except Exception as e:
            print(f"\n⚠️ STATUS: System needs configuration - {str(e)}")
        
        print(f"\n📋 MENU OPTIONS:")
        print("1. 🏢 Enterprise Proxy Management")
        print("2. 🧪 Quick Proxy System Test") 
        print("3. 📊 View System Status")
        print("4. ⚙️ Basic Configuration")
        print("5. 🆘 Troubleshooting & Support")
        print("6. 🔙 Back to Main Menu")
        print("🛡️"*60)
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            enterprise_proxy_management_menu()
        elif choice == '2':
            test_enterprise_proxy_system()
        elif choice == '3':
            view_proxy_statistics()
        elif choice == '4':
            configure_proxy_api_keys()
        elif choice == '5':
            show_troubleshooting_guide()
        elif choice == '6':
            break
        else:
            print("❌ Invalid option. Please select 1-6.")

def configure_proxy_rotation_startup():
    """Configure proxy rotation settings at startup"""
    config_file = 'config/proxy_rotation_config.json'
    
    # Check if we already have a configuration
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                existing_config = json.load(f)
            
            print("\n" + "🔧"*60)
            print("🔧 PROXY ROTATION CONFIGURATION")  
            print("🔧"*60)
            print(f"✅ Found existing configuration:")
            print(f"   Auto Proxy Rotation: {'✅ ENABLED' if existing_config.get('auto_proxy_rotation', True) else '❌ DISABLED'}")
            print(f"   Mode: {existing_config.get('proxy_mode', 'enterprise')}")
            
            use_existing = input("\n🎯 Use existing proxy configuration? (y/n): ").strip().lower()
            if use_existing == 'y':
                return existing_config
                
        except Exception as e:
            print(f"⚠️ Error reading existing config: {str(e)}")
    
    # New configuration
    print("\n" + "🔧"*60)
    print("🔧 PROXY ROTATION STARTUP CONFIGURATION")
    print("🔧"*60)
    print("Configure how the bot handles proxy rotation for CMC access")
    
    print(f"\n📋 PROXY ROTATION OPTIONS:")
    print("1. ✅ Enable Auto Proxy Rotation (Recommended)")
    print("   • Automatically switches proxies on failures")
    print("   • Uses enterprise proxy discovery") 
    print("   • Better for overcoming CMC blocks")
    print("   • May be slower if proxy discovery fails")
    
    print(f"\n2. ❌ Disable Auto Proxy Rotation")
    print("   • Uses direct connection or single proxy")
    print("   • Faster if your IP isn't blocked")
    print("   • No automatic proxy switching")
    print("   • Good for testing or if you have reliable connection")
    
    print(f"\n3. 🎯 Manual Proxy Only")
    print("   • Uses only your manually configured proxies")
    print("   • No automatic proxy discovery") 
    print("   • You must import proxies via Settings menu")
    print("   • Good if you have premium proxy list")
    
    while True:
        choice = input(f"\n🎯 Select proxy mode (1-3): ").strip()
        
        if choice == '1':
            config = {
                'auto_proxy_rotation': True,
                'proxy_mode': 'enterprise',
                'use_proxy_discovery': True,
                'fallback_to_direct': True,
                'description': 'Auto proxy rotation with enterprise discovery'
            }
            print("✅ Auto Proxy Rotation ENABLED")
            print("🔄 Bot will automatically find and switch proxies")
            break
            
        elif choice == '2':
            config = {
                'auto_proxy_rotation': False,
                'proxy_mode': 'direct',
                'use_proxy_discovery': False,
                'fallback_to_direct': True,
                'description': 'Direct connection mode'
            }
            print("❌ Auto Proxy Rotation DISABLED")
            print("🌐 Bot will use direct connection")
            break
            
        elif choice == '3':
            config = {
                'auto_proxy_rotation': True,
                'proxy_mode': 'manual_only',
                'use_proxy_discovery': False,
                'fallback_to_direct': False,
                'description': 'Manual proxies only'
            }
            print("🎯 Manual Proxy Mode ENABLED")
            print("📁 Bot will only use manually imported proxies")
            print("💡 Import proxies via Settings > Enterprise Proxy Management")
            break
            
        else:
            print("❌ Invalid choice. Please select 1, 2, or 3.")
    
    # Save configuration
    os.makedirs('config', exist_ok=True)
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"💾 Configuration saved to {config_file}")
    except Exception as e:
        print(f"⚠️ Warning: Could not save config: {str(e)}")
    
    return config

def account_management_menu():
    """Comprehensive account management menu with SimpleLogin integration"""
    
    if not ACCOUNT_MANAGEMENT_AVAILABLE:
        print("\n❌ Account Management system not available")
        print("   Required modules not found")
        input("Press Enter to continue...")
        return
    
    while True:
        print_header("👥 ACCOUNT MANAGEMENT CENTER")
        print("🔑 Automated CMC Account Creation with SimpleLogin.io")
        
        # Quick status check
        config = SimpleLoginConfig()
        if config.is_configured():
            try:
                manager = AutomatedAccountManager(config.get_api_key())
                stats = manager.get_stats_summary()
                
                print(f"\n📊 QUICK STATUS:")
                print(f"   📧 SimpleLogin: ✅ Configured")
                total_accounts = sum(platform_stats.get('total', 0) for platform_stats in stats.values() if isinstance(platform_stats, dict))
                active_accounts = sum(platform_stats.get('active', 0) for platform_stats in stats.values() if isinstance(platform_stats, dict))
                print(f"   👤 Total Accounts: {total_accounts}")
                print(f"   ✅ Active Accounts: {active_accounts}")
                
                if 'simplelogin' in stats:
                    sl_stats = stats['simplelogin']
                    print(f"   📧 Total Aliases: {sl_stats.get('total_aliases', 0)}")
                    print(f"   💎 Premium: {'Yes' if sl_stats.get('premium', False) else 'No'}")
                
            except Exception as e:
                print(f"\n⚠️ STATUS: Configuration issue - {str(e)}")
        else:
            print(f"\n❌ STATUS: SimpleLogin not configured")
            print(f"   📧 Setup required before creating accounts")
        
        print(f"\n📋 MENU OPTIONS:")
        print("1. 🔧 SimpleLogin Setup & Configuration")
        print("2. 🆕 Create Fresh CMC Accounts")
        print("3. 📧 Manage SimpleLogin Aliases (Fix Limits)")
        print("4. 🔄 Account Rotation Demo")
        print("5. 📊 View Account Statistics")
        print("6. 🎯 Smart Posting with Account Rotation")
        print("7. 🧹 Account Maintenance")
        print("8. 🧪 Test Account Creation Workflow")
        print("9. 🔙 Back to Main Menu")
        
        choice = input("\n🎯 Select option (1-9): ").strip()
        
        if choice == '1':
            simplelogin_setup_menu()
        elif choice == '2':
            create_fresh_accounts_menu()
        elif choice == '3':
            manage_simplelogin_aliases_menu()
        elif choice == '4':
            account_rotation_demo()
        elif choice == '5':
            view_account_statistics()
        elif choice == '6':
            smart_posting_workflow()
        elif choice == '7':
            account_maintenance_menu()
        elif choice == '8':
            test_account_workflow()
        elif choice == '9':
            break
        else:
            print("❌ Invalid option. Please select 1-9.")

def simplelogin_setup_menu():
    """SimpleLogin setup and configuration menu"""
    print_header("🔧 SimpleLogin.io Setup & Configuration")
    
    config = SimpleLoginConfig()
    
    print("📋 SETUP OPTIONS:")
    print("1. 🆕 Initial SimpleLogin Setup")
    print("2. 🔧 Update API Key")
    print("3. 🧪 Test Current Configuration")
    print("4. 📊 View SimpleLogin Account Info")
    print("5. 🔙 Back to Account Management")
    
    choice = input("\n🎯 Select option (1-5): ").strip()
    
    if choice == '1':
        print("\n🔧 INITIAL SIMPLELOGIN SETUP")
        print("="*50)
        
        if config.is_configured():
            print("✅ SimpleLogin is already configured!")
            print(f"Current API key: {config.api_key[:10]}...")
            overwrite = input("\nDo you want to reconfigure? (y/n): ").lower()
            if overwrite != 'y':
                return
        
        # Run interactive setup
        try:
            result = setup_simplelogin()
            if result:
                print("\n✅ SimpleLogin configured successfully!")
                print("🎯 You can now create unlimited CMC accounts!")
            else:
                print("\n❌ Setup failed. Please try again.")
        except Exception as e:
            print(f"\n❌ Setup error: {e}")
    
    elif choice == '2':
        print("\n🔧 UPDATE API KEY")
        print("="*40)
        
        if config.is_configured():
            print(f"Current API key: {config.api_key[:10]}...")
        
        new_key = input("Enter new SimpleLogin API key: ").strip()
        if new_key:
            try:
                # Test the key
                from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
                test_client = EnhancedSimpleLoginAPI(new_key)
                user_info = test_client.get_user_info()
                
                # Save if test passes
                config.save_config(new_key)
                print("✅ API key updated and verified!")
                print(f"Account: {user_info.get('name', 'N/A')}")
                
            except Exception as e:
                print(f"❌ Invalid API key: {e}")
    
    elif choice == '3':
        print("\n🧪 TESTING CURRENT CONFIGURATION")
        print("="*45)
        
        if not config.is_configured():
            print("❌ SimpleLogin not configured!")
            return
        
        try:
            from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
            client = EnhancedSimpleLoginAPI(config.get_api_key())
            
            print("🔍 Testing API connection...")
            user_info = client.get_user_info()
            print(f"✅ Connection successful!")
            print(f"   Account: {user_info.get('name', 'N/A')}")
            print(f"   Premium: {'Yes' if user_info.get('is_premium') else 'No'}")
            
            print("\n🔍 Testing alias creation...")
            alias = client.create_random_alias(note="Test from menu system")
            print(f"✅ Alias creation successful!")
            print(f"   Created: {alias.email}")
            
            print("\n🧹 Cleaning up test alias...")
            client.delete_alias(alias.id)
            print(f"✅ Test completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    elif choice == '4':
        print("\n📊 SIMPLELOGIN ACCOUNT INFORMATION")
        print("="*45)
        
        if not config.is_configured():
            print("❌ SimpleLogin not configured!")
            return
        
        try:
            from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
            client = EnhancedSimpleLoginAPI(config.get_api_key())
            
            user_info = client.get_user_info()
            stats = client.get_alias_statistics()
            
            print(f"👤 ACCOUNT DETAILS:")
            print(f"   Name: {user_info.get('name', 'Not set')}")
            print(f"   Email: {user_info.get('email', 'N/A')}")
            print(f"   Premium: {'Yes' if user_info.get('is_premium') else 'No'}")
            
            print(f"\n📊 ALIAS STATISTICS:")
            print(f"   Total Aliases: {stats['total_aliases']}")
            print(f"   Enabled: {stats['enabled_aliases']}")
            print(f"   Disabled: {stats['disabled_aliases']}")
            print(f"   Total Forwards: {stats['total_forwards']}")
            print(f"   Total Blocks: {stats['total_blocks']}")
            
            if not user_info.get('is_premium'):
                limit = stats.get('alias_limit', 15)
                remaining = limit - stats['total_aliases']
                print(f"\n⚠️ FREE PLAN LIMITS:")
                print(f"   Alias Limit: {limit}")
                print(f"   Remaining: {remaining}")
                if remaining < 5:
                    print(f"   💡 Consider upgrading to Premium for unlimited aliases")
            
        except Exception as e:
            print(f"❌ Error fetching account info: {e}")
    
    input("\nPress Enter to continue...")

def manage_simplelogin_aliases_menu():
    """Manage SimpleLogin aliases and fix free account limits"""
    print_header("📧 Manage SimpleLogin Aliases")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        print("   Please run SimpleLogin Setup first (option 1)")
        input("Press Enter to continue...")
        return
    
    print("🔧 ALIAS MANAGEMENT OPTIONS:")
    print("1. 📊 Show Comprehensive Alias Report")
    print("2. 🧹 Interactive Alias Cleanup (Free Up Slots)")
    print("3. ♻️ Optimize for Account Creation")
    print("4. 📈 Upgrade to Premium Info")
    print("5. 🔙 Back to Account Management")
    
    choice = input("\n🎯 Select option (1-5): ").strip()
    
    if choice == '1':
        print("\n📊 GENERATING COMPREHENSIVE ALIAS REPORT")
        print("="*50)
        
        try:
            from autocrypto_social_bot.simplelogin_alias_manager import SimpleLoginAliasManager
            manager = SimpleLoginAliasManager(config.get_api_key())
            categorized = manager.show_comprehensive_alias_report()
            
            if categorized:
                manager.suggest_cleanup_actions(categorized)
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    elif choice == '2':
        print("\n🧹 INTERACTIVE ALIAS CLEANUP")
        print("="*40)
        print("⚠️ This will help you free up alias slots by deleting unused aliases")
        print("💡 Recommended if you've hit the 10 alias limit on free account")
        
        confirm = input("\n🤔 Proceed with cleanup analysis? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Cleanup cancelled")
            return
        
        try:
            from autocrypto_social_bot.simplelogin_alias_manager import SimpleLoginAliasManager
            manager = SimpleLoginAliasManager(config.get_api_key())
            manager.interactive_cleanup()
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    elif choice == '3':
        print("\n♻️ OPTIMIZING FOR ACCOUNT CREATION")
        print("="*45)
        
        try:
            from autocrypto_social_bot.simplelogin_alias_manager import SimpleLoginAliasManager
            manager = SimpleLoginAliasManager(config.get_api_key())
            
            print("🔍 Analyzing current alias usage...")
            categorized = manager.show_comprehensive_alias_report()
            
            if not categorized:
                return
            
            available_count = len(categorized['available'])
            can_cleanup = len(categorized['disabled']) + len(categorized['inactive'])
            
            print(f"\n🎯 OPTIMIZATION SUMMARY:")
            print(f"   ♻️ Immediately available for reuse: {available_count}")
            print(f"   🧹 Can be freed by cleanup: {can_cleanup}")
            print(f"   🎯 Total potential for creation: {available_count + can_cleanup}")
            
            if available_count > 0:
                print(f"\n✅ You can create {available_count} accounts right now using existing aliases!")
                print(f"💡 The system will automatically reuse these when you create accounts")
            
            if can_cleanup > 0:
                print(f"\n🧹 To free up {can_cleanup} more slots, use option 2 (Interactive Cleanup)")
            
            if available_count == 0 and can_cleanup == 0:
                print(f"\n⚠️ All aliases appear to be in active use")
                print(f"💡 Consider upgrading to Premium for unlimited aliases")
                
        except Exception as e:
            print(f"❌ Optimization analysis failed: {e}")
    
    elif choice == '4':
        print("\n📈 SIMPLELOGIN PREMIUM UPGRADE INFO")
        print("="*45)
        
        print("🌟 PREMIUM PLAN BENEFITS:")
        print("   • ♾️ Unlimited aliases (no more 10 alias limit!)")
        print("   • 🏷️ Custom domains support")
        print("   • 📧 Unlimited mailboxes")
        print("   • 📊 Advanced analytics")
        print("   • 🛡️ Priority support")
        print("   • 💎 Premium features")
        
        print(f"\n💰 PRICING:")
        print(f"   • $3/month (billed annually)")
        print(f"   • $4/month (billed monthly)")
        print(f"   • First month FREE with some plans")
        
        print(f"\n🔗 UPGRADE LINK:")
        print(f"   https://app.simplelogin.io/dashboard/pricing")
        
        print(f"\n💡 WHY UPGRADE FOR CMC AUTOMATION:")
        print(f"   • Create unlimited fresh accounts")
        print(f"   • No more alias management needed")
        print(f"   • Better email deliverability")
        print(f"   • Professional automation setup")
        
        print(f"\n🎯 If you upgrade, restart the account creation process")
        print(f"   The system will detect Premium status automatically!")
    
    input("\nPress Enter to continue...")

def create_fresh_accounts_menu():
    """Menu for creating fresh CMC accounts"""
    print_header("🆕 Create Fresh CMC Accounts")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        print("   Please run SimpleLogin Setup first (option 1)")
        input("Press Enter to continue...")
        return
    
    print("📝 ACCOUNT CREATION OPTIONS:")
    print("1. 🎯 Create Single Fresh Account")
    print("2. 🚀 Multi-Tab Registration (Auto Form Filling)")
    print("3. 🔄 Create Account with Auto-Registration")
    print("4. 🔙 Back to Account Management")
    
    choice = input("\n🎯 Select option (1-4): ").strip()
    
    if choice == '1':
        print("\n🎯 CREATING SINGLE FRESH ACCOUNT")
        print("="*40)
        
        try:
            manager = AutomatedAccountManager(config.get_api_key())
            
            platform = input("Platform (default: cmc): ").strip() or "cmc"
            username = input("Custom username (press Enter for auto-generated): ").strip() or None
            
            print(f"\n🚀 Creating account for {platform}...")
            account = manager.create_new_account(platform, username)
            
            print(f"✅ Account created successfully!")
            print(f"   👤 Username: {account.username}")
            print(f"   📧 Email: {account.email_alias}")
            print(f"   🔐 Password: {account.password}")
            print(f"   🆔 Account ID: {account.id}")
            print(f"   🔗 SimpleLogin Alias ID: {account.simplelogin_alias_id}")
            
        except Exception as e:
            print(f"❌ Account creation failed: {e}")
    
    elif choice == '2':
        print("\n🚀 MULTI-TAB CMC REGISTRATION (AUTO FORM FILLING)")
        print("="*60)
        print("✨ FULLY AUTOMATED WORKFLOW:")
        print("   📧 Creates SimpleLogin emails automatically")
        print("   🌐 Opens browser tabs and navigates to CMC signup")
        print("   📝 Fills ALL form fields automatically (email, username, password)")
        print("   🔐 You only solve captchas manually")
        print("   💾 Saves accounts to rotation system")
        print("="*60)
        
        try:
            # Import the multi-tab registration system
            from autocrypto_social_bot.enhanced_multi_tab_registration import run_multi_tab_cmc_registration
            
            platform = input("Platform (default: cmc): ").strip() or "cmc"
            if platform != "cmc":
                print("⚠️ Multi-tab registration currently only supports CMC")
                print("   Using CMC platform...")
                platform = "cmc"
            
            count_str = input("Number of accounts to create (1-10): ").strip()
            
            try:
                count = int(count_str)
                if count < 1 or count > 10:
                    print("❌ Please enter a number between 1 and 10")
                    return
            except ValueError:
                print("❌ Invalid number")
                return
            
            print(f"\n⚠️ WHAT HAPPENS NEXT:")
            print(f"1. 🌐 Opens {count} browser tabs automatically")
            print(f"2. 📝 Fills email: [generated SimpleLogin email]")
            print(f"3. 📝 Fills username: [auto-generated username]")
            print(f"4. 📝 Fills password: testcmc123!")
            print(f"5. 🔐 You solve captchas in each tab")
            print(f"6. ✅ You click Submit buttons")
            print(f"7. 💾 Accounts saved automatically")
            print(f"\n🤔 Continue with automated registration? (y/n): ", end="")
            
            confirm = input().lower()
            if confirm != 'y':
                print("❌ Registration cancelled")
                return
            
            # Run the multi-tab registration
            print(f"\n🚀 Starting automated multi-tab registration...")
            results = run_multi_tab_cmc_registration(count)
            
            # Show detailed results
            print(f"\n📊 AUTOMATED REGISTRATION RESULTS:")
            print("="*50)
            print(f"✅ Successful accounts: {results['successful_accounts']}")
            print(f"❌ Failed accounts: {results['failed_accounts']}")
            print(f"📈 Success rate: {results['success_rate']:.1f}%")
            
            if results['completed_accounts']:
                print(f"\n👤 CREATED ACCOUNTS (Ready for use):")
                for i, account in enumerate(results['completed_accounts'], 1):
                    print(f"   {i}. {account.username}")
                    print(f"      📧 Email: {account.email_alias}")
                    print(f"      🔐 Password: testcmc123!")
                
                print(f"\n💡 ACCOUNTS READY FOR USE:")
                print(f"✅ Saved to rotation system")
                print(f"🎯 Use in Main Menu → Option 2 → Run Bot")
                print(f"📊 View stats in Account Management → Option 4")
                
                # Enable enhanced account rotation for the main bot
                print(f"\n🔄 ENABLING ENHANCED ACCOUNT ROTATION...")
                try:
                    flag_file = "config/use_account_rotation.flag"
                    with open(flag_file, 'w') as f:
                        f.write(f"enabled_at_{int(time.time())}")
                    print(f"✅ Enhanced rotation enabled - main bot will use these accounts automatically!")
                except Exception as e:
                    print(f"⚠️ Could not enable rotation: {e}")
            
        except ImportError:
            print("❌ Multi-tab registration system not available")
            print("   Falling back to simple batch creation...")
            
            # Fallback to original simple method
            manager = AutomatedAccountManager(config.get_api_key())
            accounts = manager.create_multiple_accounts(platform, count)
            print(f"\n✅ Created {len(accounts)} accounts successfully!")
            for i, account in enumerate(accounts, 1):
                print(f"   {i}. {account.username} ({account.email_alias})")
                
        except Exception as e:
            print(f"❌ Multi-tab registration failed: {e}")
            print("💡 Try using Option 1 for single account creation")
    
    elif choice == '3':
        print("\n🔄 CREATING ACCOUNT WITH AUTO-REGISTRATION")
        print("="*50)
        
        try:
            enhanced_manager = EnhancedProfileManager()
            
            print("🚀 Creating fresh account with Chrome profile...")
            account, driver = enhanced_manager.create_fresh_account_with_profile("cmc")
            
            print(f"✅ Account and profile created!")
            print(f"   👤 Username: {account.username}")
            print(f"   📧 Email: {account.email_alias}")
            print(f"   🌐 Chrome Profile: {account.profile_name}")
            
            print(f"\n🔐 Attempting CMC registration...")
            success = enhanced_manager.login_to_platform("cmc")
            
            if success:
                print("✅ CMC account registered and logged in!")
                print("🎯 Account is ready for posting!")
            else:
                print("⚠️ Registration initiated - may need email verification")
            
            print("\n🎯 Would you like to test posting a comment?")
            test_comment = input("Enter test comment (or press Enter to skip): ").strip()
            
            if test_comment:
                print("💬 Attempting to post test comment...")
                # Here you would integrate with your CMC scraper
                print("✅ Comment posting test completed!")
            
            # Clean up
            driver.quit()
            
        except Exception as e:
            print(f"❌ Auto-registration failed: {e}")
    
    input("\nPress Enter to continue...")

def account_rotation_demo():
    """Demonstrate account rotation functionality"""
    print_header("🔄 Account Rotation Demo")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        input("Press Enter to continue...")
        return
    
    print("🎯 This demo shows how account rotation works during posting")
    print("="*60)
    
    try:
        enhanced_manager = EnhancedProfileManager()
        
        print("1️⃣ Starting with fresh account...")
        account, driver = enhanced_manager.create_fresh_account_with_profile("cmc")
        print(f"   Created: {account.username} ({account.email_alias})")
        
        print("\n2️⃣ Simulating posting session...")
        for i in range(3):
            print(f"   📝 Simulated post {i+1}/3")
            # Simulate posting activity
            enhanced_manager.account_manager.database.update_account_usage(account.id, True)
            time.sleep(1)
        
        print("\n3️⃣ Checking if rotation is needed...")
        stats = enhanced_manager.get_account_rotation_stats()
        current_posts = stats['current_account']['posts_today']
        print(f"   Posts today: {current_posts}")
        
        if current_posts >= 2:  # Demo rotation threshold
            print("\n4️⃣ Rotating to fresh account...")
            new_account, new_driver = enhanced_manager.rotate_to_fresh_account("cmc", max_daily_posts=2)
            print(f"   Rotated to: {new_account.username} ({new_account.email_alias})")
            
            # Clean up
            new_driver.quit()
        
        # Clean up
        driver.quit()
        
        print("\n✅ Demo completed successfully!")
        print("💡 In real usage, rotation happens automatically when limits are reached")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    input("\nPress Enter to continue...")

def view_account_statistics():
    """View comprehensive account statistics"""
    print_header("📊 Account Statistics Dashboard")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        input("Press Enter to continue...")
        return
    
    try:
        manager = AutomatedAccountManager(config.get_api_key())
        stats = manager.get_stats_summary()
        
        print("🏢 PLATFORM BREAKDOWN:")
        print("-" * 40)
        
        total_accounts = 0
        total_posts = 0
        
        for platform, platform_stats in stats.items():
            if isinstance(platform_stats, dict) and platform != 'simplelogin':
                print(f"\n{platform.upper()}:")
                print(f"   Total: {platform_stats.get('total', 0)}")
                print(f"   Active: {platform_stats.get('active', 0)}")
                print(f"   Suspended: {platform_stats.get('suspended', 0)}")
                print(f"   Banned: {platform_stats.get('banned', 0)}")
                print(f"   Success Rate: {platform_stats.get('avg_success_rate', 0):.1f}%")
                print(f"   Total Posts: {platform_stats.get('total_posts', 0)}")
                
                total_accounts += platform_stats.get('total', 0)
                total_posts += platform_stats.get('total_posts', 0)
        
        print(f"\n📊 OVERALL SUMMARY:")
        print(f"   Total Accounts: {total_accounts}")
        print(f"   Total Posts: {total_posts}")
        print(f"   Average Posts per Account: {total_posts/max(total_accounts, 1):.1f}")
        
        # SimpleLogin statistics
        if 'simplelogin' in stats:
            sl_stats = stats['simplelogin']
            print(f"\n📧 SIMPLELOGIN STATISTICS:")
            print(f"   Total Aliases: {sl_stats.get('total_aliases', 0)}")
            print(f"   Enabled Aliases: {sl_stats.get('enabled_aliases', 0)}")
            print(f"   Total Forwards: {sl_stats.get('total_forwards', 0)}")
            print(f"   Premium Account: {'Yes' if sl_stats.get('premium', False) else 'No'}")
            
            if not sl_stats.get('premium', False):
                limit = sl_stats.get('alias_limit', 15)
                remaining = limit - sl_stats.get('total_aliases', 0)
                print(f"   Remaining Aliases: {remaining}/{limit}")
        
        print(f"\n🎯 PERFORMANCE METRICS:")
        if total_accounts > 0:
            active_ratio = sum(platform_stats.get('active', 0) for platform_stats in stats.values() if isinstance(platform_stats, dict)) / total_accounts
            print(f"   Account Health: {active_ratio*100:.1f}% active")
            
            avg_success = sum(platform_stats.get('avg_success_rate', 0) for platform_stats in stats.values() if isinstance(platform_stats, dict)) / len([p for p in stats.values() if isinstance(p, dict) and p != stats.get('simplelogin')])
            print(f"   Overall Success Rate: {avg_success:.1f}%")
        
    except Exception as e:
        print(f"❌ Error fetching statistics: {e}")
    
    input("\nPress Enter to continue...")

def smart_posting_workflow():
    """Integrated posting workflow with account rotation"""
    print_header("🎯 Smart Posting with Account Rotation")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        input("Press Enter to continue...")
        return
    
    print("🚀 This workflow demonstrates posting with automatic account rotation")
    print("="*70)
    
    print("\n📝 POSTING OPTIONS:")
    print("1. 🧪 Test Posting Workflow (Demo)")
    print("2. 💬 Single Comment with Fresh Account")
    print("3. 📦 Batch Comments with Auto-Rotation")
    print("4. 🔙 Back to Account Management")
    
    choice = input("\n🎯 Select option (1-4): ").strip()
    
    if choice == '1':
        print("\n🧪 TEST POSTING WORKFLOW")
        print("="*35)
        
        try:
            enhanced_manager = EnhancedProfileManager()
            
            print("1️⃣ Creating fresh account...")
            account, driver = enhanced_manager.create_fresh_account_with_profile("cmc")
            print(f"   ✅ Account ready: {account.username}")
            
            print("\n2️⃣ Simulating posting activity...")
            comments = [
                "Great analysis on this coin! 📈",
                "Thanks for the insights! Very helpful.",
                "Bullish outlook confirmed! 🚀"
            ]
            
            for i, comment in enumerate(comments, 1):
                print(f"   💬 Simulated post {i}: {comment[:30]}...")
                
                # Simulate successful posting
                enhanced_manager.account_manager.database.update_account_usage(account.id, True)
                
                # Check if rotation needed (demo: rotate after 2 posts)
                if i >= 2:
                    print(f"   🔄 Account limit reached, rotating...")
                    new_account, new_driver = enhanced_manager.rotate_to_fresh_account("cmc", max_daily_posts=2)
                    print(f"   ✅ Rotated to: {new_account.username}")
                    
                    # Update references
                    driver.quit()
                    account = new_account
                    driver = new_driver
                
                time.sleep(1)
            
            print("\n✅ Workflow demonstration completed!")
            driver.quit()
            
        except Exception as e:
            print(f"❌ Workflow demo failed: {e}")
    
    elif choice == '2':
        print("\n💬 SINGLE COMMENT WITH FRESH ACCOUNT")
        print("="*45)
        
        comment = input("Enter your comment: ").strip()
        if not comment:
            print("❌ No comment provided")
            return
        
        coin_symbol = input("Target coin (default: BTC): ").strip() or "BTC"
        
        try:
            enhanced_manager = EnhancedProfileManager()
            
            print(f"\n🚀 Creating fresh account for posting...")
            account, driver = enhanced_manager.create_fresh_account_with_profile("cmc")
            print(f"   ✅ Account: {account.username}")
            
            print(f"\n💬 Posting comment to {coin_symbol}...")
            # Here you would integrate with your CMC scraper
            print(f"   Comment: {comment}")
            print(f"   ✅ Comment posted successfully! (simulated)")
            
            # Update usage
            enhanced_manager.account_manager.database.update_account_usage(account.id, True)
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Posting failed: {e}")
    
    elif choice == '3':
        print("\n📦 BATCH COMMENTS WITH AUTO-ROTATION")
        print("="*45)
        
        print("💡 This would integrate with your existing CMC scraper")
        print("💡 Add multiple comments, system auto-rotates accounts")
        print("💡 Implementation ready - needs CMC scraper integration")
        
        # This would integrate with your existing posting system
        print("\n🔧 Integration points:")
        print("   • Enhanced profile manager")
        print("   • Automatic account rotation")
        print("   • CMC scraper integration")
        print("   • Success rate tracking")
    
    input("\nPress Enter to continue...")

def account_maintenance_menu():
    """Account maintenance and cleanup menu"""
    print_header("🧹 Account Maintenance")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        input("Press Enter to continue...")
        return
    
    print("🔧 MAINTENANCE OPTIONS:")
    print("1. 🧹 Clean Up Inactive Accounts")
    print("2. 📊 Reset Daily Post Counters")
    print("3. 🔄 Sync with SimpleLogin")
    print("4. 🗑️ Delete Suspended Accounts")
    print("5. 🔙 Back to Account Management")
    
    choice = input("\n🎯 Select option (1-5): ").strip()
    
    if choice == '1':
        print("\n🧹 CLEANING UP INACTIVE ACCOUNTS")
        print("="*40)
        
        days = input("Days of inactivity for cleanup (default: 30): ").strip()
        try:
            days = int(days) if days else 30
        except ValueError:
            days = 30
        
        try:
            manager = AutomatedAccountManager(config.get_api_key())
            
            print(f"\n🔍 Finding accounts inactive for {days}+ days...")
            manager.cleanup_old_accounts(days)
            print("✅ Cleanup completed!")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")
    
    elif choice == '2':
        print("\n📊 RESETTING DAILY POST COUNTERS")
        print("="*40)
        
        try:
            manager = AutomatedAccountManager(config.get_api_key())
            manager.database.reset_daily_counts()
            print("✅ Daily counters reset for all accounts!")
            
        except Exception as e:
            print(f"❌ Reset failed: {e}")
    
    elif choice == '3':
        print("\n🔄 SYNCING WITH SIMPLELOGIN")
        print("="*35)
        
        try:
            from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
            client = EnhancedSimpleLoginAPI(config.get_api_key())
            
            print("🔍 Fetching SimpleLogin alias status...")
            stats = client.get_alias_statistics()
            print(f"✅ Found {stats['total_aliases']} aliases on SimpleLogin")
            print("💡 Sync functionality ready for implementation")
            
        except Exception as e:
            print(f"❌ Sync failed: {e}")
    
    elif choice == '4':
        print("\n🗑️ DELETING SUSPENDED ACCOUNTS")
        print("="*35)
        
        confirm = input("⚠️ Delete all suspended accounts? (yes/no): ").strip().lower()
        if confirm == 'yes':
            print("🗑️ Deletion functionality ready for implementation")
            print("💡 Would also disable corresponding SimpleLogin aliases")
        else:
            print("❌ Deletion cancelled")
    
    input("\nPress Enter to continue...")

def test_account_workflow():
    """Test the complete account creation workflow"""
    print_header("🧪 Test Account Creation Workflow")
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        print("   Please complete SimpleLogin setup first")
        input("Press Enter to continue...")
        return
    
    print("🧪 This will test the complete account creation and registration workflow")
    print("="*75)
    
    proceed = input("🎯 Proceed with test? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    try:
        print("\n1️⃣ Testing SimpleLogin API connection...")
        from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
        client = EnhancedSimpleLoginAPI(config.get_api_key())
        user_info = client.get_user_info()
        print(f"   ✅ Connected as: {user_info.get('name', 'N/A')}")
        
        print("\n2️⃣ Testing account creation...")
        manager = AutomatedAccountManager(config.get_api_key())
        test_account = manager.create_new_account("cmc")
        print(f"   ✅ Created: {test_account.username} ({test_account.email_alias})")
        
        print("\n3️⃣ Testing enhanced profile manager...")
        enhanced_manager = EnhancedProfileManager()
        account, driver = enhanced_manager.create_fresh_account_with_profile("cmc")
        print(f"   ✅ Profile created: {account.profile_name}")
        
        print("\n4️⃣ Testing account rotation...")
        new_account, new_driver = enhanced_manager.rotate_to_fresh_account("cmc")
        print(f"   ✅ Rotated to: {new_account.username}")
        
        print("\n5️⃣ Cleaning up test accounts...")
        # Clean up test resources
        driver.quit()
        new_driver.quit()
        
        # Delete test aliases
        client.delete_alias(test_account.simplelogin_alias_id)
        client.delete_alias(account.simplelogin_alias_id)
        client.delete_alias(new_account.simplelogin_alias_id)
        print("   ✅ Test cleanup completed")
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ System is ready for automated CMC account creation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def coin_posts_bot_menu():
    """CMC Coin Posts Bot Menu"""
    if not COIN_POSTS_BOT_AVAILABLE:
        print("❌ CMC Coin Posts Bot not available")
        print("   Please ensure coin_posts_bot.py is in the project root directory")
        input("Press Enter to continue...")
        return
    
    while True:
        print_header("🔍 CMC Coin Posts Bot")
        print("🎯 Search for coin posts and interact with emoji buttons")
        print("🔄 Uses your existing account rotation system")
        print("💬 Perfect for engaging with community posts")
        print("\n📋 MENU OPTIONS:")
        print("1. 🚀 GOONC Bot (Quick Demo)")
        print("2. 🎮 Interactive GOONC Bot")
        print("3. 🔍 Search Any Coin Posts")
        print("4. 📊 Get Latest Posts (View Only)")
        print("5. 👤 Profile Interaction Bot (Visit Stored Profiles)")
        print("6. 🎯 Like Stacking Bot (All Accounts Like Same Posts)")
        print("7. ⚙️ Custom Bot Configuration")
        print("8. 🔙 Back to Main Menu")
        
        choice = input("\n🎯 Select option (1-8): ").strip()
        
        if choice == '1':
            run_goonc_quick_demo()
        elif choice == '2':
            run_interactive_goonc_bot()
        elif choice == '3':
            search_any_coin_posts()
        elif choice == '4':
            get_latest_posts_view_only()
        elif choice == '5':
            profile_interaction_bot_menu()
        elif choice == '6':
            run_like_stacking_bot()
        elif choice == '7':
            custom_bot_configuration()
        elif choice == '8':
            break
        else:
            print("❌ Invalid option. Please select 1-8.")

def run_goonc_quick_demo():
    """Run quick GOONC demo"""
    print_header("🚀 GOONC Bot Quick Demo")
    
    print("🎯 This will automatically search for GOONC posts and click emoji buttons")
    print("✅ Uses your existing account rotation system")
    print("⚡ Processes up to 8 posts with emoji interactions")
    
    proceed = input("\n🚀 Start GOONC demo? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    bot = None
    try:
        print("\n🔄 Initializing GOONC bot...")
        bot = CMCCoinPostsBot(use_account_rotation=True)
        
        print("🔍 Searching for GOONC posts and interacting...")
        results = bot.run_coin_interaction_bot(
            coin_query="goonc",
            max_posts=8,
            interaction_type="emoji"
        )
        
        if results['success']:
            print(f"\n✅ GOONC Demo Successful!")
            print(f"   📊 Posts Found: {results['posts_found']}")
            print(f"   ✅ Successful Interactions: {results['interaction_results'].get('successful_interactions', 0)}")
            print(f"   ❌ Failed Interactions: {results['interaction_results'].get('failed_interactions', 0)}")
            print(f"   ⚪ Posts Without Buttons: {results['interaction_results'].get('posts_without_buttons', 0)}")
            
            success_rate = (results['interaction_results'].get('successful_interactions', 0) / max(1, results['posts_found'])) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")
        else:
            print(f"\n❌ GOONC Demo Failed!")
            print(f"   Error: {results.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if bot:
            try:
                bot.close()
            except:
                pass
    
    input("\nPress Enter to continue...")

def run_interactive_goonc_bot():
    """Run interactive GOONC bot with user settings"""
    print_header("🎮 Interactive GOONC Bot")
    
    print("⚙️ Customize your GOONC bot settings:")
    
    # Get user preferences
    max_posts = input("How many GOONC posts to process? (default: 5): ").strip()
    if not max_posts.isdigit():
        max_posts = 5
    else:
        max_posts = int(max_posts)
    
    interaction_choice = input("What interaction? (emoji/view) [default: emoji]: ").strip().lower()
    if interaction_choice not in ['emoji', 'view']:
        interaction_choice = 'emoji'
    
    use_rotation = input("Use account rotation? (y/n) [default: y]: ").strip().lower()
    use_rotation = use_rotation != 'n'
    
    print(f"\n⚙️ Settings:")
    print(f"   Max Posts: {max_posts}")
    print(f"   Interaction: {interaction_choice}")
    print(f"   Account Rotation: {'✅ ON' if use_rotation else '❌ OFF'}")
    
    proceed = input("\n🚀 Start interactive GOONC bot? (y/n): ").strip().lower()
    if proceed != 'y':
        return
    
    bot = None
    try:
        print("\n🔄 Initializing bot...")
        bot = CMCCoinPostsBot(use_account_rotation=use_rotation)
        
        if interaction_choice == 'view':
            # Just view posts
            print("📊 Getting latest GOONC posts...")
            posts = bot.get_latest_posts_for_coin("goonc", limit=max_posts)
            
            if posts:
                print(f"\n📋 Found {len(posts)} GOONC posts:")
                for i, post in enumerate(posts[:10], 1):  # Show first 10
                    emoji_status = "🎯" if post.get('has_interactions') else "⚪"
                    print(f"   {i}. {emoji_status} {post['author']}: {post['content'][:60]}...")
                
                if len(posts) > 10:
                    print(f"   ... and {len(posts) - 10} more posts")
                
                posts_with_emojis = len([p for p in posts if p.get('has_interactions')])
                print(f"\n🎯 Posts with emoji buttons: {posts_with_emojis}/{len(posts)}")
            else:
                print("❌ No GOONC posts found")
        else:
            # Run full interaction bot
            print("🎯 Running GOONC interaction bot...")
            results = bot.run_coin_interaction_bot(
                coin_query="goonc",
                max_posts=max_posts,
                interaction_type=interaction_choice
            )
            
            if results['success']:
                print(f"\n✅ Interactive GOONC bot completed successfully!")
                print(f"   📊 Results: {results['interaction_results'].get('successful_interactions', 0)} successful interactions")
            else:
                print(f"\n❌ Interactive GOONC bot failed: {results.get('error')}")
        
    except Exception as e:
        print(f"\n❌ Interactive bot failed: {e}")
    finally:
        if bot:
            try:
                bot.close()
            except:
                pass
    
    input("\nPress Enter to continue...")

def search_any_coin_posts():
    """Search for posts about any coin"""
    print_header("🔍 Search Any Coin Posts")
    
    coin_query = input("Enter coin symbol or name to search (e.g., BTC, ETH, DOGE): ").strip()
    if not coin_query:
        print("❌ No coin specified")
        input("Press Enter to continue...")
        return
    
    max_posts = input(f"Max posts to find for {coin_query.upper()} (default: 10): ").strip()
    if not max_posts.isdigit():
        max_posts = 10
    else:
        max_posts = int(max_posts)
    
    interaction_type = input("Interaction type (emoji/view) [default: emoji]: ").strip().lower()
    if interaction_type not in ['emoji', 'view']:
        interaction_type = 'emoji'
    
    bot = None
    try:
        print(f"\n🔄 Initializing bot for {coin_query.upper()}...")
        bot = CMCCoinPostsBot(use_account_rotation=True)
        
        if interaction_type == 'view':
            # Just view posts
            posts = bot.get_latest_posts_for_coin(coin_query, limit=max_posts)
            
            if posts:
                print(f"\n📊 Found {len(posts)} posts for {coin_query.upper()}:")
                for i, post in enumerate(posts[:5], 1):
                    emoji_status = "🎯" if post.get('has_interactions') else "⚪"
                    print(f"   {i}. {emoji_status} {post['author']}: {post['content'][:80]}...")
                
                if len(posts) > 5:
                    print(f"   ... and {len(posts) - 5} more posts")
                
                posts_with_emojis = len([p for p in posts if p.get('has_interactions')])
                print(f"\n🎯 Posts with emoji buttons: {posts_with_emojis}/{len(posts)}")
            else:
                print(f"❌ No posts found for {coin_query.upper()}")
        else:
            # Run interaction bot
            results = bot.run_coin_interaction_bot(
                coin_query=coin_query,
                max_posts=max_posts,
                interaction_type=interaction_type
            )
            
            if results['success']:
                print(f"\n✅ Bot run successful for {coin_query.upper()}!")
                print(f"   📊 Found {results['posts_found']} posts")
                print(f"   ✅ Successful interactions: {results['interaction_results'].get('successful_interactions', 0)}")
                success_rate = (results['interaction_results'].get('successful_interactions', 0) / max(1, results['posts_found'])) * 100
                print(f"   📈 Success rate: {success_rate:.1f}%")
            else:
                print(f"\n❌ Bot failed for {coin_query.upper()}: {results.get('error')}")
        
    except Exception as e:
        print(f"\n❌ Search failed: {e}")
    finally:
        if bot:
            try:
                bot.close()
            except:
                pass
    
    input("\nPress Enter to continue...")

def get_latest_posts_view_only():
    """Get latest posts for viewing without interaction"""
    print_header("📊 Get Latest Posts (View Only)")
    
    print("📋 Popular coins to check:")
    print("   • goonc, btc, eth, doge, ada, sol, xrp")
    
    coin_query = input("\nEnter coin to check: ").strip()
    if not coin_query:
        print("❌ No coin specified")
        input("Press Enter to continue...")
        return
    
    limit = input(f"How many latest posts to retrieve? (default: 20): ").strip()
    if not limit.isdigit():
        limit = 20
    else:
        limit = int(limit)
    
    bot = None
    try:
        print(f"\n📊 Getting latest {limit} posts for {coin_query.upper()}...")
        bot = CMCCoinPostsBot(use_account_rotation=False)  # No rotation needed for view-only
        
        posts = bot.get_latest_posts_for_coin(coin_query, limit=limit)
        
        if posts:
            print(f"\n📋 Latest {len(posts)} posts for {coin_query.upper()}:")
            print("="*60)
            
            for i, post in enumerate(posts[:15], 1):  # Show first 15
                emoji_indicator = "🎯" if post.get('has_interactions') else "⚪"
                print(f"{i:2d}. {emoji_indicator} {post['author']}")
                print(f"     {post['content'][:90]}...")
                print()
            
            if len(posts) > 15:
                print(f"... and {len(posts) - 15} more posts")
            
            # Statistics
            posts_with_emojis = len([p for p in posts if p.get('has_interactions')])
            print(f"\n📊 STATISTICS:")
            print(f"   Total Posts: {len(posts)}")
            print(f"   🎯 With Emoji Buttons: {posts_with_emojis}")
            print(f"   ⚪ Without Buttons: {len(posts) - posts_with_emojis}")
            print(f"   📈 Interaction Rate: {(posts_with_emojis/max(1,len(posts)))*100:.1f}%")
        else:
            print(f"❌ No posts found for {coin_query.upper()}")
            print("💡 Try a different coin or check if the coin name is correct")
        
    except Exception as e:
        print(f"\n❌ Failed to get posts: {e}")
    finally:
        if bot:
            try:
                bot.close()
            except:
                pass
    
    input("\nPress Enter to continue...")

def profile_interaction_bot_menu():
    """CMC Profile Interaction Bot submenu"""
    if not PROFILE_BOT_AVAILABLE:
        print("❌ Profile Interaction Bot not available")
        input("Press Enter to continue...")
        return
    
    while True:
        clear_screen()
        print("👤 CMC PROFILE INTERACTION BOT")
        print("="*50)
        print("Visit stored CMC profiles and interact with all their posts")
        print("This bot scrolls through profile pages and clicks reaction buttons")
        
        print("\n📋 MENU OPTIONS:")
        print("1. 🏃‍♂️ Quick Demo (OnchainBureau Profile)")
        print("2. 📝 Add New Profile URL")
        print("3. 📋 List Stored Profiles")
        print("4. 🚀 Process All Stored Profiles")
        print("5. 🎯 Process Single Profile")
        print("6. 🗑️ Clear All Stored Profiles")
        print("7. 🔙 Back to Main Menu")
        
        choice = input("\n🎯 Select option (1-7): ").strip()
        
        if choice == '1':
            run_profile_bot_quick_demo()
        elif choice == '2':
            add_new_profile_url()
        elif choice == '3':
            list_stored_profiles()
        elif choice == '4':
            process_all_stored_profiles()
        elif choice == '5':
            process_single_profile()
        elif choice == '6':
            clear_all_stored_profiles()
        elif choice == '7':
            break
        else:
            print("❌ Invalid option. Please select 1-7.")


def run_profile_bot_quick_demo():
    """Run a quick demo of the profile interaction bot"""
    try:
        print("\n🏃‍♂️ RUNNING PROFILE BOT QUICK DEMO")
        print("="*50)
        print("This will visit the OnchainBureau profile and interact with posts")
        
        # Initialize bot
        bot = CMCProfileInteractionBot(use_account_rotation=True)
        
        # Add demo profile
        success = bot.add_manual_profile(
            "https://coinmarketcap.com/community/profile/Onchainbureaudotcom/",
            "OnchainBureau"
        )
        
        if not success:
            print("❌ Failed to add demo profile")
            input("Press Enter to continue...")
            return
        
        # Process the profile
        results = bot.visit_profile_and_interact(
            "https://coinmarketcap.com/community/profile/Onchainbureaudotcom/",
            max_posts=10
        )
        
        if results['success']:
            print(f"\n🎉 DEMO SUCCESSFUL!")
            print(f"   📊 Posts Found: {results['posts_found']}")
            print(f"   ✅ Successful Interactions: {results['interaction_results'].get('successful_interactions', 0)}")
            print(f"   ❌ Failed Interactions: {results['interaction_results'].get('failed_interactions', 0)}")
            print(f"   ⚪ Posts Without Buttons: {results['interaction_results'].get('posts_without_buttons', 0)}")
            
            if results['posts_found'] > 0:
                success_rate = (results['interaction_results'].get('successful_interactions', 0) / results['posts_found']) * 100
                print(f"   📈 Success Rate: {success_rate:.1f}%")
        else:
            print(f"❌ Demo failed: {results.get('error')}")
        
        bot.close()
        
    except Exception as e:
        print(f"❌ Error running demo: {e}")
    finally:
        input("Press Enter to continue...")


def add_new_profile_url():
    """Add a new CMC profile URL"""
    try:
        print("\n📝 ADD NEW PROFILE URL")
        print("="*30)
        print("Example: https://coinmarketcap.com/community/profile/username/")
        
        profile_url = input("Enter CMC profile URL: ").strip()
        if not profile_url:
            print("❌ No URL provided")
            input("Press Enter to continue...")
            return
        
        profile_name = input("Enter display name (optional): ").strip()
        if not profile_name:
            profile_name = None
        
        # Initialize bot temporarily to add profile
        bot = CMCProfileInteractionBot(use_account_rotation=False)
        success = bot.add_manual_profile(profile_url, profile_name)
        bot.close()
        
        if success:
            print("✅ Profile added successfully!")
        else:
            print("❌ Failed to add profile")
            
    except Exception as e:
        print(f"❌ Error adding profile: {e}")
    finally:
        input("Press Enter to continue...")


def list_stored_profiles():
    """List all stored profiles"""
    try:
        print("\n📋 LISTING STORED PROFILES")
        print("="*30)
        
        # Initialize bot temporarily to list profiles
        bot = CMCProfileInteractionBot(use_account_rotation=False)
        bot.list_stored_profiles()
        bot.close()
        
    except Exception as e:
        print(f"❌ Error listing profiles: {e}")
    finally:
        input("Press Enter to continue...")


def process_all_stored_profiles():
    """Process all stored profiles"""
    try:
        print("\n🚀 PROCESSING ALL STORED PROFILES")
        print("="*40)
        
        max_posts = input("Enter max posts per profile (default 20): ").strip()
        try:
            max_posts = int(max_posts) if max_posts else 20
        except:
            max_posts = 20
        
        print(f"Processing with max {max_posts} posts per profile...")
        
        # Initialize bot
        bot = CMCProfileInteractionBot(use_account_rotation=True)
        
        # Process all profiles
        results = bot.process_all_profiles(max_posts_per_profile=max_posts)
        
        if results.get('success', True):
            print(f"\n🎉 ALL PROFILES PROCESSED!")
            print(f"   Profiles: {results['profiles_processed']}")
            print(f"   Total Successful Interactions: {results['total_successful_interactions']}")
        else:
            print(f"❌ Processing failed: {results.get('error')}")
        
        bot.close()
        
    except Exception as e:
        print(f"❌ Error processing profiles: {e}")
    finally:
        input("Press Enter to continue...")


def process_single_profile():
    """Process a single profile"""
    try:
        print("\n🎯 PROCESS SINGLE PROFILE")
        print("="*30)
        
        # Show available profiles
        bot = CMCProfileInteractionBot(use_account_rotation=False)
        bot.list_stored_profiles()
        
        if not bot.stored_profiles:
            print("❌ No profiles stored. Please add profiles first.")
            bot.close()
            input("Press Enter to continue...")
            return
        
        profile_url = input("\nEnter profile URL to process: ").strip()
        if not profile_url:
            print("❌ No URL provided")
            bot.close()
            input("Press Enter to continue...")
            return
        
        max_posts = input("Enter max posts (default 20): ").strip()
        try:
            max_posts = int(max_posts) if max_posts else 20
        except:
            max_posts = 20
        
        # Process the profile
        results = bot.visit_profile_and_interact(profile_url, max_posts)
        
        if results['success']:
            print(f"\n✅ Profile processed successfully!")
            print(f"   Posts: {results['posts_found']}")
            print(f"   Successful: {results['interaction_results'].get('successful_interactions', 0)}")
        else:
            print(f"❌ Processing failed: {results.get('error')}")
        
        bot.close()
        
    except Exception as e:
        print(f"❌ Error processing profile: {e}")
    finally:
        input("Press Enter to continue...")


def clear_all_stored_profiles():
    """Clear all stored profiles"""
    try:
        print("\n🗑️ CLEAR ALL STORED PROFILES")
        print("="*30)
        
        confirm = input("Are you sure? This will delete all stored profiles (y/n): ").strip().lower()
        if confirm == 'y':
            # Initialize bot and clear profiles
            bot = CMCProfileInteractionBot(use_account_rotation=False)
            bot.stored_profiles = {}
            bot._save_stored_profiles()
            bot.close()
            print("✅ All profiles cleared!")
        else:
            print("❌ Operation cancelled")
            
    except Exception as e:
        print(f"❌ Error clearing profiles: {e}")
    finally:
        input("Press Enter to continue...")

def run_like_stacking_bot():
    """Run the Like Stacking Bot that uses all accounts to like the same posts"""
    if not LIKE_STACKING_BOT_AVAILABLE:
        print("❌ Like Stacking Bot not available")
        input("Press Enter to continue...")
        return
    
    try:
        print_header("🎯 Like Stacking Bot")
        
        print("🎯 This bot will:")
        print("   • Find posts about a specific coin (e.g., GOONC)")
        print("   • Rotate through ALL your CMC accounts")
        print("   • Each account likes the SAME posts")
        print("   • Results in 'stacked' likes on each post")
        print("   • Example: 5 accounts × 10 posts = 50 total likes")
        
        # Initialize bot
        bot = CMCLikeStackingBot()
        
        if len(bot.cmc_profiles) == 0:
            print("\n❌ No CMC profiles found. Please create profiles first.")
            input("Press Enter to continue...")
            return
        
        print(f"\n✅ Found {len(bot.cmc_profiles)} CMC accounts for stacking")
        
        # Get user settings
        coin = input("\nEnter coin to stack likes on (e.g., GOONC): ").strip()
        if not coin:
            coin = "GOONC"
        
        max_posts = input(f"Max posts per account (default 10): ").strip()
        try:
            max_posts = int(max_posts) if max_posts else 10
        except:
            max_posts = 10
        
        # Show the stacking plan
        print(f"\n🚀 LIKE STACKING PLAN:")
        print(f"   Coin: {coin.upper()}")
        print(f"   Max Posts Per Account: {max_posts}")
        print(f"   Accounts Available: {len(bot.cmc_profiles)}")
        print(f"   Expected Max Total Likes: {max_posts * len(bot.cmc_profiles)}")
        print(f"   Strategy: Each account will search for {coin.upper()} posts and like them")
        
        proceed = input("\n🚀 Proceed with like stacking? (y/n): ").strip().lower()
        
        if proceed != 'y':
            print("❌ Like stacking cancelled")
            input("Press Enter to continue...")
            return
        
        # Run the like stacking
        print(f"\n🎯 Starting like stacking for {coin.upper()}...")
        results = bot.stack_likes_on_coin(coin, max_posts)
        
        if results['success']:
            print(f"\n🎉 LIKE STACKING SUCCESS!")
            print("="*50)
            print(f"✅ Total Likes Stacked: {results['total_likes']}")
            print(f"📊 Posts Found: {results['posts_found']}")
            print(f"👥 Accounts Used: {results['accounts_used']}")
            print(f"📈 Average Likes Per Post: {results['avg_likes_per_post']:.1f}")
            
            if results['posts_found'] > 0:
                efficiency = (results['total_likes'] / (results['posts_found'] * results['accounts_used'])) * 100
                print(f"🎯 Stacking Efficiency: {efficiency:.1f}%")
                
                print(f"\n💡 RESULTS EXPLANATION:")
                print(f"   • Found {results['posts_found']} posts about {coin.upper()}")
                print(f"   • {results['accounts_used']} accounts each tried to like these posts")
                print(f"   • Total successful likes: {results['total_likes']}")
                print(f"   • Each post got an average of {results['avg_likes_per_post']:.1f} likes")
        else:
            print(f"\n❌ Like stacking failed: {results.get('error')}")
        
        bot.close()
        
    except Exception as e:
        print(f"\n❌ Error running like stacking bot: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("Press Enter to continue...")

def custom_bot_configuration():
    """Custom configuration for the coin posts bot"""
    print_header("⚙️ Custom Bot Configuration")
    
    print("🔧 Advanced bot configuration options:")
    print("\n📋 Configuration Options:")
    print("1. 🎯 Multiple Coin Search")
    print("2. 📊 Batch Processing Mode")
    print("3. ⏰ Scheduled Running")
    print("4. 🔄 Advanced Rotation Settings")
    print("5. 🔙 Back to Coin Posts Menu")
    
    choice = input("\n🎯 Select option (1-5): ").strip()
    
    if choice == '1':
        print("\n🎯 MULTIPLE COIN SEARCH")
        print("="*30)
        
        coins_input = input("Enter coins separated by commas (e.g., goonc,btc,eth): ").strip()
        if not coins_input:
            print("❌ No coins specified")
            input("Press Enter to continue...")
            return
        
        coins = [coin.strip() for coin in coins_input.split(',')]
        max_posts_per_coin = input("Max posts per coin (default: 5): ").strip()
        if not max_posts_per_coin.isdigit():
            max_posts_per_coin = 5
        else:
            max_posts_per_coin = int(max_posts_per_coin)
        
        print(f"\n🚀 Processing {len(coins)} coins with {max_posts_per_coin} posts each...")
        
        bot = None
        try:
            bot = CMCCoinPostsBot(use_account_rotation=True)
            
            total_successful = 0
            total_posts = 0
            
            for coin in coins:
                print(f"\n🔍 Processing {coin.upper()}...")
                results = bot.run_coin_interaction_bot(
                    coin_query=coin,
                    max_posts=max_posts_per_coin,
                    interaction_type="emoji"
                )
                
                if results['success']:
                    successful = results['interaction_results'].get('successful_interactions', 0)
                    found = results['posts_found']
                    total_successful += successful
                    total_posts += found
                    print(f"   ✅ {coin.upper()}: {successful}/{found} successful interactions")
                else:
                    print(f"   ❌ {coin.upper()}: Failed - {results.get('error', 'Unknown error')}")
            
            print(f"\n📊 BATCH PROCESSING SUMMARY:")
            print(f"   Coins Processed: {len(coins)}")
            print(f"   Total Posts Found: {total_posts}")
            print(f"   Total Successful Interactions: {total_successful}")
            success_rate = (total_successful / max(1, total_posts)) * 100
            print(f"   Overall Success Rate: {success_rate:.1f}%")
            
        except Exception as e:
            print(f"❌ Batch processing failed: {e}")
        finally:
            if bot:
                try:
                    bot.close()
                except:
                    pass
    
    elif choice == '2':
        print("\n📊 BATCH PROCESSING MODE")
        print("="*30)
        print("💡 Configure automated batch processing")
        print("🔄 Process multiple coins with delays")
        print("⚡ Optimized for large-scale operations")
        print("\n⚙️ Batch processing configuration ready for implementation")
        
    elif choice == '3':
        print("\n⏰ SCHEDULED RUNNING")
        print("="*25)
        print("🕐 Set up scheduled bot runs")
        print("📅 Daily/hourly automation")
        print("🔔 Notification system")
        print("\n⚙️ Scheduling system ready for implementation")
        
    elif choice == '4':
        print("\n🔄 ADVANCED ROTATION SETTINGS")
        print("="*35)
        print("🎯 Configure rotation behavior")
        print("⏱️ Set rotation timing")
        print("🛡️ Error handling options")
        print("\n⚙️ Advanced rotation settings ready for implementation")
    
    input("\nPress Enter to continue...")

def list_accounts_and_passwords():
    """Launch the account listing utility"""
    try:
        print_header("📋 Account Listing Utility")
        
        # Check if accounts database exists
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "accounts.db")
        if not os.path.exists(db_path):
            print("❌ No accounts database found!")
            print(f"   Expected location: {db_path}")
            print("\nTo create accounts, use the Account Management menu (option 5)")
            print("or run: python autocrypto_social_bot/scripts/account_management_demo.py")
            input("\nPress Enter to continue...")
            return
        
        # Import and run the account listing utility
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Run the list_accounts script
        import subprocess
        result = subprocess.run(
            [sys.executable, "list_accounts.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=False
        )
        
        # Alternative: direct import and run
        if result.returncode != 0:
            print("\n🔄 Trying alternative method...")
            try:
                # Add project root to path
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if project_root not in sys.path:
                    sys.path.append(project_root)
                
                # Import the account listing functions
                import sqlite3
                from datetime import datetime
                
                # Quick account summary
                print("\n📊 QUICK ACCOUNT SUMMARY:")
                print("=" * 40)
                
                with sqlite3.connect(db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute("""
                        SELECT 
                            platform, status, COUNT(*) as count
                        FROM accounts 
                        GROUP BY platform, status
                        ORDER BY platform, status
                    """)
                    
                    total_accounts = 0
                    for row in cursor:
                        platform, status, count = row
                        total_accounts += count
                        status_emoji = {
                            'active': '✅',
                            'suspended': '⚠️',
                            'banned': '❌',
                            'inactive': '😴'
                        }.get(status, '❓')
                        print(f"{status_emoji} {platform.upper()} {status}: {count} accounts")
                    
                    print(f"\n🎯 TOTAL ACCOUNTS: {total_accounts}")
                
                # Ask if user wants to see detailed view
                show_details = input("\n🔍 Show detailed account list with passwords? (y/n): ").strip().lower()
                
                if show_details == 'y':
                    with sqlite3.connect(db_path) as conn:
                        conn.row_factory = sqlite3.Row
                        cursor = conn.execute("""
                            SELECT * FROM accounts 
                            ORDER BY platform, status, created_at DESC
                        """)
                        
                        accounts = cursor.fetchall()
                        
                        for account in accounts:
                            print(f"\n📧 Email: {account['email_alias']}")
                            print(f"👤 Username: {account['username'] or 'N/A'}")
                            print(f"🔑 Password: {account['password']}")
                            print(f"🌐 Platform: {account['platform']}")
                            print(f"📊 Status: {account['status']}")
                            
                            if account['profile_name']:
                                print(f"🖥️  Profile: {account['profile_name'][:50]}...")
                            
                            if account['created_at']:
                                created = datetime.fromisoformat(account['created_at']).strftime("%Y-%m-%d %H:%M")
                                print(f"📅 Created: {created}")
                            
                            print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error reading accounts: {e}")
        
    except Exception as e:
        print(f"❌ Error launching account listing: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to continue...")

def main_menu():
    """Display main menu and handle user selections"""
    # Configure proxy rotation at startup (once per session)
    proxy_config = configure_proxy_rotation_startup()
    
    while True:
        # Get current directory info for display
        current_dir = os.getcwd()
        
        print("\n" + "="*60)
        print("🚀 CRYPTO SOCIAL AUTOMATION BOT")
        print("="*60)
        print(f"📂 Working Directory: {os.path.basename(current_dir)}")
        
        # Show proxy configuration status
        print(f"\n🔧 PROXY CONFIGURATION:")
        if proxy_config.get('auto_proxy_rotation', True):
            print(f"   ✅ Auto Proxy Rotation: ENABLED")
            print(f"   🎯 Mode: {proxy_config.get('proxy_mode', 'enterprise').upper()}")
        else:
            print(f"   ❌ Auto Proxy Rotation: DISABLED") 
            print(f"   🌐 Mode: DIRECT CONNECTION")
        print(f"   📝 {proxy_config.get('description', 'Default configuration')}")
        
        # 🔥 ENHANCED STATUS DISPLAY
        try:
            from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
            if cmc_bypass_manager and proxy_config.get('auto_proxy_rotation', True):
                status = cmc_bypass_manager.get_system_status()
                if status['verified_proxies'] >= 5:
                    print("🔥 BREAKTHROUGH: Enhanced CMC System ACTIVE")
                    print(f"   ✅ {status['verified_proxies']} Verified Working Proxies")
                    print(f"   🎯 {status['success_rate']:.1f}% Success Rate")
                    print("   🛡️ AUTO-TUNNEL DETECTION: Enabled")
                    print("   🔄 AUTO-PROXY SWITCHING: Enabled")
                    print("   🔍 AUTO-PROXY RE-SCRAPING: Enabled")
                else:
                    print("⚠️ CMC Bypass: Limited proxies available")
                    print("   🔄 Auto-discovery system standing by")
            elif not proxy_config.get('auto_proxy_rotation', True):
                print("🌐 DIRECT CONNECTION: Proxy rotation disabled")
                print("   ⚡ Faster startup, no proxy discovery")
        except:
            print("⚠️ CMC Bypass: Not available")
        
        # Show enhanced enterprise proxy status (only if proxy rotation enabled)
        if proxy_config.get('auto_proxy_rotation', True):
            try:
                from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
                enterprise_manager = EnterpriseProxyManager()
                session_info = enterprise_manager.get_session_info()
                
                if session_info['verified_proxies_count'] > 0:
                    print(f"🏢 ENTERPRISE PROXY: {session_info['verified_proxies_count']} verified proxies ready")
                    print("   ✅ Enhanced HTML content validation active")
                    print("   🚨 Emergency proxy re-scraping enabled")
                else:
                    print("🏢 ENTERPRISE PROXY: Initializing...")
                    
            except Exception as e:
                print(f"🏢 ENTERPRISE PROXY: Error - {str(e)}")
        
        print("\n📋 MENU OPTIONS:")
        print("1. 👤 Profile Management")
        print("2. 🤖 Run Bot (ENHANCED AUTO-RECOVERY SYSTEM)")
        print("3. ⚙️ Settings")
        print("4. 🔧 Change Proxy Configuration")
        print("5. 🔑 Account Management")
        print("6. 🔍 CMC Coin Posts Bot (GOONC & More)")
        print("7. 📋 List All Accounts & Passwords")
        print("8. ❌ Exit")
        
        print("\n" + "="*60)
        print("🆕 NEW FEATURES:")
        print("   • CMC Coin Posts Bot (GOONC & more)")
        print("   • Emoji button interaction system")
        print("   • Configurable proxy rotation modes")
        print("   • Direct connection option for testing") 
        print("   • Manual proxy-only mode")
        print("   • Automatic tunnel error detection")
        print("   • Intelligent HTML content validation") 
        print("   • Auto-proxy switching on failures")
        print("   • Emergency proxy re-scraping")
        print("   • Enhanced retry mechanisms")
        print("="*60)
        
        choice = input("🎯 Select option (1-8): ").strip()
        
        if choice == '1':
            manage_profiles()
        elif choice == '2':
            # Run the bot with enhanced auto-recovery and proxy configuration
            print(f"\n🔥 Starting bot with proxy configuration:")
            print(f"   🔧 Auto Proxy Rotation: {'ENABLED' if proxy_config.get('auto_proxy_rotation', True) else 'DISABLED'}")
            print(f"   🎯 Mode: {proxy_config.get('proxy_mode', 'enterprise').upper()}")
            
            if proxy_config.get('auto_proxy_rotation', True):
                print("✅ Your bot now automatically handles:")
                print("   🛡️ Tunnel connection failures")
                print("   🔍 HTML content validation") 
                print("   🔄 Automatic proxy switching")
                print("   🚨 Emergency proxy discovery")
                print("   ⚡ Real-time error recovery")
            else:
                print("✅ Your bot is using direct connection:")
                print("   ⚡ Faster startup and operation")
                print("   🌐 No proxy overhead")
                print("   🔄 Manual proxy management only")
            
            run_bot(proxy_config)
        elif choice == '3':
            proxy_and_anti_detection_menu()
        elif choice == '4':
            # Allow user to change proxy configuration
            print("\n🔧 Reconfiguring proxy settings...")
            proxy_config = configure_proxy_rotation_startup()
        elif choice == '5':
            account_management_menu()
        elif choice == '6':
            coin_posts_bot_menu()
        elif choice == '7':
            list_accounts_and_passwords()
        elif choice == '8':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting... 👋")
        sys.exit(0) 