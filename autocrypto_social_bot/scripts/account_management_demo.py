#!/usr/bin/env python3
"""
Automated Account Management Demo

This script demonstrates the automated account creation and management system
using SimpleLogin.io for email aliases and SQLite for account storage.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.services.account_manager import AutomatedAccountManager
from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig, setup_simplelogin
from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_account_info(account):
    """Print formatted account information"""
    print(f"📧 Email: {account.email_alias}")
    print(f"👤 Username: {account.username}")
    print(f"🔑 Password: {account.password}")
    print(f"🌐 Platform: {account.platform}")
    print(f"📊 Posts today: {account.posts_today}")
    print(f"📈 Total posts: {account.total_posts}")
    print(f"✅ Success rate: {account.success_rate}%")
    print(f"📝 Notes: {account.notes}")

def demo_basic_account_creation():
    """Demonstrate basic account creation"""
    print_header("DEMO 1: Basic Account Creation")
    
    try:
        # Check if SimpleLogin is configured
        config = SimpleLoginConfig()
        if not config.is_configured():
            print("⚠️  SimpleLogin API key not configured!")
            setup_result = setup_simplelogin()
            if not setup_result:
                print("❌ Setup failed. Skipping this demo.")
                return
            config = setup_result
        
        # Initialize account manager
        manager = AutomatedAccountManager(config.get_api_key())
        
        print("🚀 Creating a new CMC account...")
        account = manager.create_new_account("cmc")
        
        print("\n✅ Account created successfully!")
        print_account_info(account)
        
        return account
        
    except Exception as e:
        print(f"❌ Error in basic account creation demo: {e}")
        return None

def demo_multiple_account_creation():
    """Demonstrate creating multiple accounts"""
    print_header("DEMO 2: Multiple Account Creation")
    
    try:
        config = SimpleLoginConfig()
        if not config.is_configured():
            print("⚠️  SimpleLogin not configured. Please run setup first.")
            return
        
        manager = AutomatedAccountManager(config.get_api_key())
        
        print("🚀 Creating 3 new accounts...")
        accounts = manager.create_multiple_accounts("cmc", 3)
        
        print(f"\n✅ Created {len(accounts)} accounts successfully!")
        for i, account in enumerate(accounts, 1):
            print(f"\n--- Account {i} ---")
            print_account_info(account)
        
        return accounts
        
    except Exception as e:
        print(f"❌ Error in multiple account creation demo: {e}")
        return []

def demo_account_rotation():
    """Demonstrate account rotation functionality"""
    print_header("DEMO 3: Account Rotation")
    
    try:
        config = SimpleLoginConfig()
        if not config.is_configured():
            print("⚠️  SimpleLogin not configured. Please run setup first.")
            return
        
        manager = AutomatedAccountManager(config.get_api_key())
        
        print("🔄 Getting next available account...")
        account1 = manager.get_next_account("cmc")
        print(f"✅ Got account: {account1.username}")
        
        print("\n🔄 Simulating account usage...")
        manager.database.update_account_usage(account1.id, success=True)
        
        print("🔄 Getting fresh account (max 0 posts per day)...")
        account2 = manager.rotate_to_fresh_account("cmc", max_posts_per_day=0)
        print(f"✅ Got fresh account: {account2.username}")
        
        if account1.id != account2.id:
            print("✅ Successfully rotated to a different account!")
        else:
            print("ℹ️  Same account returned (no other fresh accounts available)")
        
        return account1, account2
        
    except Exception as e:
        print(f"❌ Error in account rotation demo: {e}")
        return None, None

def demo_enhanced_profile_manager():
    """Demonstrate the enhanced profile manager"""
    print_header("DEMO 4: Enhanced Profile Manager (Chrome Integration)")
    
    try:
        print("🚀 Initializing Enhanced Profile Manager...")
        print("⚠️  This will open Chrome browser windows!")
        
        input("Press Enter to continue or Ctrl+C to skip...")
        
        manager = EnhancedProfileManager()
        
        print("🔄 Creating fresh account with Chrome profile...")
        account, driver = manager.create_fresh_account_with_profile("cmc")
        
        print("✅ Account and Chrome profile created!")
        print_account_info(account)
        print(f"🌐 Browser URL: {driver.current_url}")
        
        print("\n⏳ Keeping browser open for 10 seconds...")
        time.sleep(10)
        
        print("🔄 Rotating to another fresh account...")
        account2, driver2 = manager.rotate_to_fresh_account("cmc")
        
        print("✅ Rotated to fresh account!")
        print_account_info(account2)
        
        print("\n⏳ Keeping browser open for 5 seconds...")
        time.sleep(5)
        
        # Cleanup
        manager.cleanup()
        print("✅ Cleaned up browser sessions")
        
    except Exception as e:
        print(f"❌ Error in enhanced profile manager demo: {e}")
        if 'manager' in locals():
            manager.cleanup()

def demo_statistics_and_monitoring():
    """Demonstrate statistics and monitoring features"""
    print_header("DEMO 5: Statistics & Monitoring")
    
    try:
        config = SimpleLoginConfig()
        if not config.is_configured():
            print("⚠️  SimpleLogin not configured. Please run setup first.")
            return
        
        manager = AutomatedAccountManager(config.get_api_key())
        
        print("📊 Getting comprehensive account statistics...")
        stats = manager.get_stats_summary()
        
        print("\n✅ Account Statistics:")
        print(json.dumps(stats, indent=2))
        
        print("\n🔧 Performing maintenance...")
        manager.perform_maintenance()
        
        print("✅ Maintenance completed!")
        
    except Exception as e:
        print(f"❌ Error in statistics demo: {e}")

def demo_account_management_operations():
    """Demonstrate account management operations"""
    print_header("DEMO 6: Account Management Operations")
    
    try:
        config = SimpleLoginConfig()
        if not config.is_configured():
            print("⚠️  SimpleLogin not configured. Please run setup first.")
            return
        
        manager = AutomatedAccountManager(config.get_api_key())
        
        # Get all accounts
        accounts = manager.database.get_accounts_by_platform("cmc", "active")
        
        if accounts:
            print(f"📋 Found {len(accounts)} active CMC accounts:")
            for account in accounts[:3]:  # Show first 3
                print(f"  - {account.username} ({account.email_alias})")
            
            # Demonstrate marking an account as compromised
            if len(accounts) > 0:
                test_account = accounts[0]
                print(f"\n⚠️  Simulating account compromise for: {test_account.username}")
                manager.mark_account_compromised(test_account.id, "Demo: Simulated detection")
                print("✅ Account marked as compromised")
                
                # Get updated stats
                stats = manager.get_stats_summary()
                print(f"📊 Updated stats: {json.dumps(stats, indent=2)}")
        else:
            print("ℹ️  No active accounts found. Create some accounts first!")
        
    except Exception as e:
        print(f"❌ Error in account management operations demo: {e}")

def interactive_menu():
    """Interactive menu for running demos"""
    while True:
        print_header("AUTOMATED ACCOUNT MANAGEMENT DEMO")
        print("1. 🆕 Basic Account Creation")
        print("2. 📝 Multiple Account Creation") 
        print("3. 🔄 Account Rotation")
        print("4. 🌐 Enhanced Profile Manager (Chrome)")
        print("5. 📊 Statistics & Monitoring")
        print("6. ⚙️  Account Management Operations")
        print("7. 🔧 Setup SimpleLogin API")
        print("8. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == "1":
            demo_basic_account_creation()
        elif choice == "2":
            demo_multiple_account_creation()
        elif choice == "3":
            demo_account_rotation()
        elif choice == "4":
            demo_enhanced_profile_manager()
        elif choice == "5":
            demo_statistics_and_monitoring()
        elif choice == "6":
            demo_account_management_operations()
        elif choice == "7":
            setup_simplelogin()
        elif choice == "8":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

def run_all_demos():
    """Run all demos in sequence"""
    print_header("RUNNING ALL DEMOS")
    print("⚠️  This will run all demos in sequence!")
    print("⚠️  Chrome browsers will open during some demos!")
    
    confirm = input("Do you want to continue? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Demos cancelled.")
        return
    
    demos = [
        demo_basic_account_creation,
        demo_multiple_account_creation, 
        demo_account_rotation,
        demo_statistics_and_monitoring,
        demo_account_management_operations,
        # Skip enhanced profile manager in batch mode
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n🚀 Running Demo {i}/{len(demos)}...")
        try:
            demo()
            print(f"✅ Demo {i} completed successfully!")
        except Exception as e:
            print(f"❌ Demo {i} failed: {e}")
        
        if i < len(demos):
            print("\n⏳ Waiting 3 seconds before next demo...")
            time.sleep(3)
    
    print_header("ALL DEMOS COMPLETED")
    print("✅ Finished running all demos!")

if __name__ == "__main__":
    print_header("AUTOMATED ACCOUNT MANAGEMENT SYSTEM")
    print("This demo showcases automated account creation using SimpleLogin.io")
    print("Features:")
    print("  ✅ Automated email alias creation")
    print("  ✅ Account database storage") 
    print("  ✅ Account rotation and management")
    print("  ✅ Chrome profile integration")
    print("  ✅ Statistics and monitoring")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_all_demos()
    else:
        interactive_menu() 