#!/usr/bin/env python3
"""
Account Listing Utility

This script displays all your CMC accounts with their credentials,
organized by platform and status.
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

def get_database_path():
    """Get the path to the accounts database"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "accounts.db")

def database_exists():
    """Check if the accounts database exists"""
    return os.path.exists(get_database_path())

def get_all_accounts():
    """Retrieve all accounts from the database"""
    if not database_exists():
        return []
    
    try:
        db_path = get_database_path()
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM accounts 
                ORDER BY platform, status, created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"❌ Error reading database: {e}")
        return []

def get_account_stats():
    """Get statistics about accounts"""
    if not database_exists():
        return {}
    
    try:
        db_path = get_database_path()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    platform,
                    status,
                    COUNT(*) as count,
                    AVG(success_rate) as avg_success_rate,
                    SUM(total_posts) as total_posts,
                    MAX(last_used) as last_used
                FROM accounts
                GROUP BY platform, status
                ORDER BY platform, status
            """)
            return cursor.fetchall()
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return []

def format_account(account: Dict[str, Any], show_passwords: bool = True) -> str:
    """Format account information for display"""
    lines = []
    
    # Basic info
    lines.append(f"   📧 Email: {account['email_alias']}")
    lines.append(f"   👤 Username: {account['username'] or 'N/A'}")
    
    if show_passwords:
        lines.append(f"   🔑 Password: {account['password']}")
    else:
        lines.append(f"   🔑 Password: {'*' * len(account['password'])}")
    
    # Profile info
    if account['profile_name']:
        lines.append(f"   🌐 Profile: {account['profile_name'][:50]}...")
    
    # Stats
    lines.append(f"   📊 Posts: {account['posts_today']}/day, {account['total_posts']} total")
    lines.append(f"   ✅ Success Rate: {account['success_rate']:.1f}%")
    
    # Dates
    if account['last_used']:
        last_used = datetime.fromisoformat(account['last_used']).strftime("%Y-%m-%d %H:%M")
        lines.append(f"   🕒 Last Used: {last_used}")
    
    if account['created_at']:
        created = datetime.fromisoformat(account['created_at']).strftime("%Y-%m-%d %H:%M")
        lines.append(f"   📅 Created: {created}")
    
    # Notes
    if account['notes']:
        lines.append(f"   📝 Notes: {account['notes'][:80]}...")
    
    return "\n".join(lines)

def display_accounts_by_status(accounts: List[Dict[str, Any]], show_passwords: bool = True):
    """Display accounts organized by platform and status"""
    if not accounts:
        print("❌ No accounts found in database")
        return
    
    # Group accounts by platform and status
    grouped = {}
    for account in accounts:
        platform = account['platform']
        status = account['status']
        
        if platform not in grouped:
            grouped[platform] = {}
        if status not in grouped[platform]:
            grouped[platform][status] = []
        
        grouped[platform][status].append(account)
    
    # Display grouped accounts
    for platform, statuses in grouped.items():
        print(f"\n🚀 PLATFORM: {platform.upper()}")
        print("=" * 60)
        
        for status, status_accounts in statuses.items():
            status_emoji = {
                'active': '✅',
                'suspended': '⚠️',
                'banned': '❌',
                'inactive': '😴'
            }.get(status, '❓')
            
            print(f"\n{status_emoji} {status.upper()} ACCOUNTS ({len(status_accounts)})")
            print("-" * 40)
            
            for i, account in enumerate(status_accounts, 1):
                print(f"\n{i:2d}. ID: {account['id']}")
                print(format_account(account, show_passwords))

def display_quick_summary():
    """Display a quick summary of all accounts"""
    stats = get_account_stats()
    
    if not stats:
        print("❌ No account statistics available")
        return
    
    print("📊 ACCOUNT SUMMARY")
    print("=" * 50)
    
    total_accounts = 0
    for row in stats:
        platform, status, count, avg_success, total_posts, last_used = row
        total_accounts += count
        
        status_emoji = {
            'active': '✅',
            'suspended': '⚠️', 
            'banned': '❌',
            'inactive': '😴'
        }.get(status, '❓')
        
        print(f"{status_emoji} {platform.upper()} {status}: {count} accounts")
        if avg_success:
            print(f"   📈 Avg Success Rate: {avg_success:.1f}%")
        if total_posts:
            print(f"   📊 Total Posts: {total_posts}")
        if last_used:
            last_used_date = datetime.fromisoformat(last_used).strftime("%Y-%m-%d %H:%M")
            print(f"   🕒 Last Activity: {last_used_date}")
        print()
    
    print(f"🎯 TOTAL ACCOUNTS: {total_accounts}")

def interactive_menu():
    """Interactive menu for account viewing"""
    while True:
        print("\n" + "=" * 60)
        print("🔍 ACCOUNT LISTING UTILITY")
        print("=" * 60)
        print("1. 📊 Quick Summary")
        print("2. 👀 List All Accounts (hide passwords)")
        print("3. 🔑 List All Accounts (show passwords)")
        print("4. ✅ List Only Active Accounts")
        print("5. ⚠️  List Only Suspended/Problematic Accounts")
        print("6. 🚀 List CMC Accounts Only")
        print("0. ❌ Exit")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            display_quick_summary()
        elif choice == '2':
            accounts = get_all_accounts()
            display_accounts_by_status(accounts, show_passwords=False)
        elif choice == '3':
            accounts = get_all_accounts()
            display_accounts_by_status(accounts, show_passwords=True)
        elif choice == '4':
            accounts = [acc for acc in get_all_accounts() if acc['status'] == 'active']
            display_accounts_by_status(accounts, show_passwords=True)
        elif choice == '5':
            accounts = [acc for acc in get_all_accounts() if acc['status'] in ['suspended', 'banned', 'inactive']]
            display_accounts_by_status(accounts, show_passwords=True)
        elif choice == '6':
            accounts = [acc for acc in get_all_accounts() if acc['platform'] == 'cmc']
            display_accounts_by_status(accounts, show_passwords=True)
        else:
            print("❌ Invalid choice. Please try again.")
        
        if choice != '0':
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    if not database_exists():
        print("❌ No accounts database found!")
        print(f"   Expected location: {get_database_path()}")
        print("\nTo create accounts, use:")
        print("   python autocrypto_social_bot/scripts/account_management_demo.py")
        return
    
    print("🔍 Account Database Found!")
    print(f"   Location: {get_database_path()}")
    
    if len(sys.argv) > 1:
        # Command line usage
        arg = sys.argv[1].lower()
        if arg in ['summary', 's']:
            display_quick_summary()
        elif arg in ['active', 'a']:
            accounts = [acc for acc in get_all_accounts() if acc['status'] == 'active']
            display_accounts_by_status(accounts, show_passwords=True)
        elif arg in ['all', 'list', 'l']:
            accounts = get_all_accounts()
            display_accounts_by_status(accounts, show_passwords=True)
        elif arg in ['cmc', 'c']:
            accounts = [acc for acc in get_all_accounts() if acc['platform'] == 'cmc']
            display_accounts_by_status(accounts, show_passwords=True)
        else:
            print(f"❌ Unknown option: {arg}")
            print("Valid options: summary, active, all, cmc")
    else:
        # Interactive mode
        interactive_menu()

if __name__ == "__main__":
    main() 