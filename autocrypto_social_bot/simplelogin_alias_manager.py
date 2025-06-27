#!/usr/bin/env python3

"""
SimpleLogin Alias Management Utility
====================================

Helps manage SimpleLogin aliases when hitting the free account limit.
Provides functions to list, clean up, and optimize alias usage.
"""

import os
import sys
from typing import List, Dict, Set
from datetime import datetime, timedelta

# Add autocrypto_social_bot to path
sys.path.append(os.path.dirname(__file__))

from services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
from services.account_manager import AutomatedAccountManager
from config.simplelogin_config import SimpleLoginConfig

class SimpleLoginAliasManager:
    """Manages SimpleLogin aliases and helps with free account limits"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = EnhancedSimpleLoginAPI(api_key)
        self.account_manager = None
        
        try:
            self.account_manager = AutomatedAccountManager(api_key)
        except Exception as e:
            print(f"⚠️ Could not initialize account manager: {e}")
    
    def show_comprehensive_alias_report(self):
        """Show comprehensive report of all aliases"""
        print("\n📊 COMPREHENSIVE SIMPLELOGIN ALIAS REPORT")
        print("="*80)
        
        # Get user info and stats
        user_info = self.client.get_user_info()
        stats = self.client.get_alias_statistics()
        
        print(f"👤 Account: {user_info.get('email', 'Unknown')}")
        print(f"🏷️ Plan: {'Premium' if stats['premium'] else 'Free'}")
        
        if not stats['premium']:
            limit = stats['alias_limit']
            current = stats['total_aliases']
            remaining = limit - current
            print(f"📊 Usage: {current}/{limit} aliases ({remaining} remaining)")
            
            if remaining <= 0:
                print("🚨 LIMIT REACHED! Consider upgrading or cleaning up unused aliases.")
        
        print(f"📈 Activity: {stats['total_forwards']} forwards, {stats['total_replies']} replies, {stats['total_blocks']} blocks")
        print()
        
        # Get all aliases
        aliases = self._get_all_aliases()
        
        if not aliases:
            print("📧 No aliases found")
            return
        
        # Categorize aliases
        categorized = self._categorize_aliases(aliases)
        
        # Show categories
        print("📂 ALIAS CATEGORIES:")
        print("-"*50)
        
        print(f"✅ Active & In Use: {len(categorized['active_used'])}")
        print(f"♻️ Available for Reuse: {len(categorized['available'])}")
        print(f"💤 Inactive/Unused: {len(categorized['inactive'])}")
        print(f"❌ Disabled: {len(categorized['disabled'])}")
        print(f"🔒 High Activity (External): {len(categorized['high_activity'])}")
        print()
        
        # Show details for each category
        self._show_category_details("✅ ACTIVE & IN USE", categorized['active_used'])
        self._show_category_details("♻️ AVAILABLE FOR REUSE", categorized['available'])
        self._show_category_details("💤 INACTIVE/UNUSED", categorized['inactive'])
        self._show_category_details("❌ DISABLED", categorized['disabled'])
        self._show_category_details("🔒 HIGH ACTIVITY (EXTERNAL)", categorized['high_activity'])
        
        return categorized
    
    def _get_all_aliases(self) -> List[Dict]:
        """Get all aliases from SimpleLogin"""
        try:
            all_aliases = []
            page = 0
            
            while True:
                result = self.client.get_aliases(page_id=page)
                aliases = result.get('aliases', [])
                
                if not aliases:
                    break
                
                all_aliases.extend(aliases)
                page += 1
                
                if not result.get('more', False):
                    break
            
            return all_aliases
        except Exception as e:
            print(f"❌ Error fetching aliases: {e}")
            return []
    
    def _categorize_aliases(self, aliases: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize aliases based on usage and status"""
        categories = {
            'active_used': [],      # In database and being used
            'available': [],        # Not in database, enabled, low activity
            'inactive': [],         # Not in database, enabled, no recent activity
            'disabled': [],         # Disabled aliases
            'high_activity': []     # High activity but not in our database
        }
        
        # Get used aliases from database
        used_aliases = self._get_used_aliases_from_database()
        
        for alias in aliases:
            email = alias['email']
            enabled = alias.get('enabled', True)
            forwards = alias.get('nb_forward', 0)
            note = alias.get('note', '').lower()
            
            if not enabled:
                categories['disabled'].append(alias)
            elif email in used_aliases:
                categories['active_used'].append(alias)
            elif forwards > 10:  # High activity threshold
                categories['high_activity'].append(alias)
            elif forwards == 0:  # Never used
                categories['inactive'].append(alias)
            else:
                categories['available'].append(alias)
        
        return categories
    
    def _get_used_aliases_from_database(self) -> Set[str]:
        """Get aliases that are in our account database"""
        if not self.account_manager:
            return set()
        
        try:
            accounts = self.account_manager.database.get_all_accounts()
            return {account.email_alias for account in accounts if account.email_alias}
        except Exception:
            return set()
    
    def _show_category_details(self, title: str, aliases: List[Dict], max_show: int = 5):
        """Show details for a category of aliases"""
        if not aliases:
            return
        
        print(f"\n{title} ({len(aliases)}):")
        print("-" * (len(title) + 10))
        
        for i, alias in enumerate(aliases[:max_show]):
            email = alias['email']
            note = alias.get('note', 'No note')
            created = alias.get('creation_date', 'Unknown')[:10]
            forwards = alias.get('nb_forward', 0)
            
            print(f"   {i+1}. {email}")
            print(f"      📝 {note}")
            print(f"      📅 {created} | 📨 {forwards} forwards")
        
        if len(aliases) > max_show:
            print(f"   ... and {len(aliases) - max_show} more")
        print()
    
    def suggest_cleanup_actions(self, categorized: Dict[str, List[Dict]]):
        """Suggest cleanup actions to free up alias slots"""
        print("\n💡 CLEANUP SUGGESTIONS:")
        print("="*50)
        
        total_can_free = len(categorized['disabled']) + len(categorized['inactive'])
        
        if total_can_free == 0:
            print("✅ No cleanup needed - all aliases appear to be in use")
            return
        
        print(f"🧹 You can potentially free up {total_can_free} alias slots:")
        
        if categorized['disabled']:
            print(f"   • Delete {len(categorized['disabled'])} disabled aliases")
        
        if categorized['inactive']:
            print(f"   • Delete {len(categorized['inactive'])} unused aliases")
        
        print(f"\n⚠️ CAUTION:")
        print(f"   • High activity aliases might be used elsewhere")
        print(f"   • Always verify before deleting")
        
        return total_can_free
    
    def interactive_cleanup(self):
        """Interactive cleanup process"""
        print("\n🧹 INTERACTIVE ALIAS CLEANUP")
        print("="*40)
        
        categorized = self.show_comprehensive_alias_report()
        
        if not categorized:
            return
        
        total_can_free = self.suggest_cleanup_actions(categorized)
        
        if total_can_free == 0:
            print("Nothing to clean up!")
            return
        
        print(f"\n🤔 What would you like to do?")
        print(f"1. Delete all disabled aliases ({len(categorized['disabled'])})")
        print(f"2. Delete inactive/unused aliases ({len(categorized['inactive'])})")
        print(f"3. Delete both disabled and inactive ({total_can_free} total)")
        print(f"4. Manual selection")
        print(f"5. Cancel")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            self._delete_aliases(categorized['disabled'], "disabled")
        elif choice == '2':
            self._delete_aliases(categorized['inactive'], "inactive/unused")
        elif choice == '3':
            all_to_delete = categorized['disabled'] + categorized['inactive']
            self._delete_aliases(all_to_delete, "disabled and inactive")
        elif choice == '4':
            self._manual_selection_cleanup(categorized)
        elif choice == '5':
            print("❌ Cleanup cancelled")
        else:
            print("❌ Invalid choice")
    
    def _delete_aliases(self, aliases: List[Dict], category_name: str):
        """Delete a list of aliases"""
        if not aliases:
            print(f"No {category_name} aliases to delete")
            return
        
        print(f"\n⚠️ About to delete {len(aliases)} {category_name} aliases:")
        for alias in aliases[:5]:  # Show first 5
            print(f"   • {alias['email']}")
        
        if len(aliases) > 5:
            print(f"   ... and {len(aliases) - 5} more")
        
        confirm = input(f"\n❓ Confirm deletion of {len(aliases)} aliases? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Deletion cancelled")
            return
        
        deleted_count = 0
        for alias in aliases:
            try:
                self.client.delete_alias(alias['id'])
                print(f"   ✅ Deleted: {alias['email']}")
                deleted_count += 1
            except Exception as e:
                print(f"   ❌ Failed to delete {alias['email']}: {e}")
        
        print(f"\n🎉 Cleanup complete! Deleted {deleted_count}/{len(aliases)} aliases")
        print(f"💡 You now have {deleted_count} more alias slots available")
    
    def _manual_selection_cleanup(self, categorized: Dict[str, List[Dict]]):
        """Manual selection of aliases to delete"""
        print("\n🔧 MANUAL SELECTION MODE")
        print("="*30)
        
        # Combine cleanable aliases
        cleanable = categorized['disabled'] + categorized['inactive']
        
        if not cleanable:
            print("No aliases available for cleanup")
            return
        
        print("Select aliases to delete (enter numbers separated by commas):")
        print("Example: 1,3,5-8,10")
        print()
        
        for i, alias in enumerate(cleanable, 1):
            email = alias['email']
            note = alias.get('note', 'No note')
            status = "disabled" if not alias.get('enabled') else "inactive"
            forwards = alias.get('nb_forward', 0)
            
            print(f"   {i:2d}. {email} ({status}, {forwards} forwards)")
            print(f"       {note}")
        
        selection = input(f"\nEnter selection (1-{len(cleanable)}): ").strip()
        
        if not selection:
            print("❌ No selection made")
            return
        
        # Parse selection
        selected_indices = self._parse_selection(selection, len(cleanable))
        
        if not selected_indices:
            print("❌ Invalid selection")
            return
        
        selected_aliases = [cleanable[i-1] for i in selected_indices]
        self._delete_aliases(selected_aliases, "selected")
    
    def _parse_selection(self, selection: str, max_index: int) -> List[int]:
        """Parse user selection string like '1,3,5-8,10'"""
        indices = []
        
        try:
            parts = selection.split(',')
            for part in parts:
                part = part.strip()
                if '-' in part:
                    # Range like 5-8
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                else:
                    # Single number
                    indices.append(int(part))
            
            # Filter valid indices
            indices = [i for i in indices if 1 <= i <= max_index]
            return sorted(set(indices))  # Remove duplicates and sort
            
        except ValueError:
            return []

def main():
    """Main function for standalone usage"""
    config = SimpleLoginConfig()
    
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        print("Please configure SimpleLogin first")
        return
    
    manager = SimpleLoginAliasManager(config.get_api_key())
    
    print("🔧 SIMPLELOGIN ALIAS MANAGER")
    print("="*40)
    print("1. Show Alias Report")
    print("2. Interactive Cleanup")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == '1':
        manager.show_comprehensive_alias_report()
    elif choice == '2':
        manager.interactive_cleanup()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 