#!/usr/bin/env python3
"""
Structured Profile Rotation System

This system ensures:
1. Sequential profile rotation (cmc_profile_1 -> cmc_profile_2 -> cmc_profile_3...)
2. Login verification before each use
3. User confirmation before deleting logged-out profiles
4. No time wasted on non-functional profiles
"""

import os
import sys
import time
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector

class StructuredProfileRotation:
    """Manages structured sequential profile rotation with login verification"""
    
    def __init__(self, profile_manager: ProfileManager = None):
        self.profile_manager = profile_manager or ProfileManager()
        self.login_detector = CMCLoginDetector(self.profile_manager)
        self.logger = logging.getLogger(__name__)
        
        # Rotation state
        self.current_profile_index = 0
        self.available_profiles = []
        self.verified_profiles = []  # Profiles confirmed to be logged in
        self.failed_profiles = []    # Profiles that failed login check
        
        # Session tracking
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.rotation_count = 0
        
        print(f"🔄 Structured Profile Rotation System Initialized")
        print(f"📅 Session ID: {self.session_id}")
        
        # Initialize profile list
        self._refresh_profile_list()
    
    def _refresh_profile_list(self) -> List[str]:
        """Get all CMC profiles in numerical order"""
        all_profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        # Sort profiles numerically (cmc_profile_1, cmc_profile_2, etc.)
        def extract_number(profile_name):
            try:
                # Extract number from profile name (e.g., "cmc_profile_1" -> 1)
                parts = profile_name.split('_')
                if len(parts) >= 3 and parts[-1].isdigit():
                    return int(parts[-1])
                else:
                    # Handle profiles like "cmc_profile_1750867065_1"
                    for part in reversed(parts):
                        if part.isdigit() and len(part) <= 3:  # Reasonable profile number
                            return int(part)
                    return 999  # Put at end if no number found
            except:
                return 999
        
        sorted_profiles = sorted(all_profiles, key=extract_number)
        self.available_profiles = sorted_profiles
        
        print(f"📋 Found {len(sorted_profiles)} CMC profiles:")
        for i, profile in enumerate(sorted_profiles, 1):
            print(f"   {i}. {profile}")
        
        return sorted_profiles
    
    def verify_all_profiles_login_status(self, ask_user_confirmation: bool = True) -> Dict:
        """
        Check login status of all profiles and handle logged-out ones
        
        Args:
            ask_user_confirmation: If True, ask user before deleting profiles
        
        Returns:
            Dict with verification results
        """
        if not self.available_profiles:
            self._refresh_profile_list()
        
        if not self.available_profiles:
            return {
                'total_profiles': 0,
                'verified_profiles': [],
                'failed_profiles': [],
                'deleted_profiles': [],
                'error': 'No CMC profiles found'
            }
        
        print(f"\n" + "="*70)
        print(f"🔍 VERIFYING LOGIN STATUS FOR ALL {len(self.available_profiles)} PROFILES")
        print(f"="*70)
        
        verified = []
        failed = []
        deleted = []
        
        for i, profile_name in enumerate(self.available_profiles, 1):
            print(f"\n{'='*50}")
            print(f"🔍 CHECKING PROFILE {i}/{len(self.available_profiles)}: {profile_name}")
            print(f"{'='*50}")
            
            try:
                # Load profile
                print(f"📂 Loading profile: {profile_name}")
                driver = self.profile_manager.load_profile(profile_name)
                time.sleep(3)  # Allow profile to fully load
                
                # Quick login verification using improved detection
                print(f"🔍 Verifying login status...")
                status = self.login_detector.check_cmc_login_status(driver, profile_name)
                is_logged_in = status.get('logged_in', False)
                
                # Close driver
                try:
                    driver.quit()
                except:
                    pass
                
                if is_logged_in:
                    print(f"✅ VERIFIED: {profile_name} is logged into CMC")
                    verified.append(profile_name)
                else:
                    print(f"❌ FAILED: {profile_name} is NOT logged into CMC")
                    print(f"   Reasons: {', '.join(status.get('logout_reasons', ['Unknown'])[:3])}")
                    failed.append(profile_name)
                    
                    # Ask user what to do with this profile
                    if ask_user_confirmation:
                        should_delete = self._ask_user_delete_confirmation(profile_name, status)
                        if should_delete:
                            if self.login_detector.cleanup_logged_out_profile(profile_name):
                                print(f"🗑️ DELETED: {profile_name}")
                                deleted.append(profile_name)
                            else:
                                print(f"❌ FAILED TO DELETE: {profile_name}")
                        else:
                            print(f"⚠️ KEEPING: {profile_name} (user choice)")
                    else:
                        # Auto-delete if no user confirmation required
                        if self.login_detector.cleanup_logged_out_profile(profile_name):
                            print(f"🗑️ AUTO-DELETED: {profile_name}")
                            deleted.append(profile_name)
                
                # Brief delay between profiles
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ ERROR checking {profile_name}: {str(e)}")
                failed.append(profile_name)
                
                if ask_user_confirmation:
                    should_delete = self._ask_user_delete_confirmation(profile_name, {'error': str(e)})
                    if should_delete:
                        if self.login_detector.cleanup_logged_out_profile(profile_name):
                            deleted.append(profile_name)
        
        # Update internal state
        self.verified_profiles = verified
        self.failed_profiles = [p for p in failed if p not in deleted]
        
        # Refresh profile list after deletions
        self._refresh_profile_list()
        
        # Summary
        print(f"\n" + "="*70)
        print(f"📊 PROFILE VERIFICATION SUMMARY")
        print(f"="*70)
        print(f"🔍 Total Profiles Checked: {len(self.available_profiles) + len(deleted)}")
        print(f"✅ Verified (Logged In): {len(verified)}")
        print(f"❌ Failed (Not Logged In): {len(failed)}")
        print(f"🗑️ Deleted: {len(deleted)}")
        print(f"📋 Remaining Profiles: {len(self.available_profiles)}")
        
        if verified:
            print(f"\n✅ VERIFIED PROFILES:")
            for profile in verified:
                print(f"   • {profile}")
        
        if deleted:
            print(f"\n🗑️ DELETED PROFILES:")
            for profile in deleted:
                print(f"   • {profile}")
        
        if self.failed_profiles:
            print(f"\n⚠️ FAILED PROFILES (KEPT):")
            for profile in self.failed_profiles:
                print(f"   • {profile}")
        
        print(f"="*70)
        
        return {
            'total_profiles': len(self.available_profiles) + len(deleted),
            'verified_profiles': verified,
            'failed_profiles': self.failed_profiles,
            'deleted_profiles': deleted,
            'remaining_profiles': self.available_profiles
        }
    
    def _ask_user_delete_confirmation(self, profile_name: str, status: Dict) -> bool:
        """Ask user if they want to delete a logged-out profile"""
        print(f"\n" + "⚠️"*30)
        print(f"❌ PROFILE NOT LOGGED IN: {profile_name}")
        print(f"⚠️"*30)
        
        if 'error' in status:
            print(f"💥 Error: {status['error']}")
        else:
            print(f"📊 Login Score: {status.get('login_score', 0)}")
            print(f"📊 Logout Score: {status.get('logout_score', 0)}")
            if status.get('logout_reasons'):
                print(f"🔍 Reasons: {', '.join(status['logout_reasons'][:3])}")
        
        print(f"\nThis profile is taking up space and slowing down rotation.")
        print(f"It will be moved to a backup folder, not permanently deleted.")
        
        while True:
            choice = input(f"\n🗑️ Delete {profile_name}? (y/n/s=skip all): ").strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            elif choice in ['s', 'skip']:
                # Skip all remaining confirmations
                print("⏭️ Skipping all remaining confirmations...")
                return False
            else:
                print("❌ Please enter 'y' (yes), 'n' (no), or 's' (skip all)")
    
    def get_next_profile(self) -> Optional[str]:
        """
        Get the next profile in the rotation sequence
        Ensures sequential rotation: cmc_profile_1 -> cmc_profile_2 -> cmc_profile_3...
        """
        if not self.available_profiles:
            self._refresh_profile_list()
            
        if not self.available_profiles:
            raise Exception("No CMC profiles available for rotation")
        
        # Get current profile
        if self.current_profile_index >= len(self.available_profiles):
            self.current_profile_index = 0  # Loop back to start
        
        next_profile = self.available_profiles[self.current_profile_index]
        
        # Increment for next rotation
        self.current_profile_index = (self.current_profile_index + 1) % len(self.available_profiles)
        self.rotation_count += 1
        
        print(f"🔄 STRUCTURED ROTATION #{self.rotation_count}")
        print(f"   📋 Profile: {next_profile}")
        print(f"   📊 Position: {self.current_profile_index}/{len(self.available_profiles)}")
        print(f"   🔄 Next: {self.available_profiles[self.current_profile_index] if self.available_profiles else 'N/A'}")
        
        return next_profile
    
    def rotate_to_next_profile_with_verification(self) -> Tuple[Optional[object], str]:
        """
        Rotate to next profile with login verification
        
        Returns:
            Tuple of (driver, profile_name) or (None, '') if failed
        """
        max_attempts = len(self.available_profiles) if self.available_profiles else 1
        attempts = 0
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                # Get next profile
                profile_name = self.get_next_profile()
                
                print(f"\n🔄 LOADING PROFILE: {profile_name} (Attempt {attempts}/{max_attempts})")
                
                # Load profile
                driver = self.profile_manager.load_profile(profile_name)
                time.sleep(3)  # Allow profile to load
                
                # Quick login verification using improved detection
                print(f"🔍 Verifying login status...")
                status = self.login_detector.check_cmc_login_status(driver, profile_name)
                is_logged_in = status.get('logged_in', False)
                
                if is_logged_in:
                    print(f"✅ VERIFIED: {profile_name} is logged in")
                    return driver, profile_name
                else:
                    print(f"❌ FAILED: {profile_name} is not logged in")
                    
                    # Close driver
                    try:
                        driver.quit()
                    except:
                        pass
                    
                    # Ask user if they want to delete this profile
                    print(f"⚠️ Profile {profile_name} lost its login session during operation")
                    should_delete = input(f"🗑️ Delete {profile_name}? (y/n): ").strip().lower() == 'y'
                    
                    if should_delete:
                        if self.login_detector.cleanup_logged_out_profile(profile_name):
                            print(f"🗑️ DELETED: {profile_name}")
                            # Remove from available profiles
                            if profile_name in self.available_profiles:
                                self.available_profiles.remove(profile_name)
                            # Adjust index if needed
                            if self.current_profile_index > 0:
                                self.current_profile_index -= 1
                        else:
                            print(f"❌ Failed to delete {profile_name}")
                    
                    # Continue to next profile
                    continue
                    
            except Exception as e:
                print(f"❌ Error loading profile: {str(e)}")
                continue
        
        # If we get here, all profiles failed
        print(f"❌ All available profiles failed login verification")
        return None, ''
    
    def get_rotation_stats(self) -> Dict:
        """Get current rotation statistics"""
        return {
            'session_id': self.session_id,
            'rotation_count': self.rotation_count,
            'total_profiles': len(self.available_profiles),
            'current_index': self.current_profile_index,
            'verified_profiles': len(self.verified_profiles),
            'failed_profiles': len(self.failed_profiles),
            'available_profiles': self.available_profiles,
            'current_profile': self.available_profiles[self.current_profile_index - 1] if self.available_profiles and self.current_profile_index > 0 else None
        }
    
    def print_rotation_status(self):
        """Print current rotation status"""
        stats = self.get_rotation_stats()
        
        print(f"\n📊 ROTATION STATUS")
        print(f"="*40)
        print(f"🔄 Rotations: {stats['rotation_count']}")
        print(f"📋 Available Profiles: {stats['total_profiles']}")
        print(f"📍 Current Index: {stats['current_index']}")
        print(f"✅ Verified: {stats['verified_profiles']}")
        print(f"❌ Failed: {stats['failed_profiles']}")
        
        if stats['current_profile']:
            print(f"👤 Current: {stats['current_profile']}")
        
        if stats['available_profiles']:
            print(f"🔄 Sequence: {' → '.join(stats['available_profiles'][:5])}")
            if len(stats['available_profiles']) > 5:
                print(f"           ... and {len(stats['available_profiles']) - 5} more")
        
        print(f"="*40)


# Integration with existing ProfileManager
class EnhancedProfileManager(ProfileManager):
    """Enhanced ProfileManager with structured rotation"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.structured_rotation = StructuredProfileRotation(self)
        self._rotation_initialized = False
    
    def initialize_structured_rotation(self, verify_all: bool = True, ask_confirmation: bool = True):
        """Initialize structured rotation with profile verification"""
        if self._rotation_initialized:
            return
        
        print(f"\n🚀 INITIALIZING STRUCTURED PROFILE ROTATION")
        print(f"="*60)
        
        if verify_all:
            results = self.structured_rotation.verify_all_profiles_login_status(ask_confirmation)
            
            if results['verified_profiles']:
                print(f"✅ Structured rotation ready with {len(results['verified_profiles'])} verified profiles")
            else:
                print(f"❌ No verified profiles available!")
                raise Exception("No logged-in profiles available for rotation")
        
        self._rotation_initialized = True
        print(f"="*60)
    
    def switch_to_next_profile_structured(self):
        """Switch to next profile using structured rotation"""
        if not self._rotation_initialized:
            self.initialize_structured_rotation()
        
        # Close current driver
        if self.current_driver:
            try:
                self.current_driver.quit()
            except:
                pass
            self.current_driver = None
        
        # Get next profile with verification
        driver, profile_name = self.structured_rotation.rotate_to_next_profile_with_verification()
        
        if driver and profile_name:
            self.current_driver = driver
            self.current_profile = profile_name
            print(f"✅ STRUCTURED ROTATION SUCCESS: Now using {profile_name}")
            return driver
        else:
            raise Exception("Structured rotation failed - no available profiles")
    
    def get_structured_rotation_stats(self):
        """Get structured rotation statistics"""
        if not self._rotation_initialized:
            return {'error': 'Structured rotation not initialized'}
        
        return self.structured_rotation.get_rotation_stats()


# Standalone functions for easy use
def verify_all_profiles(ask_confirmation: bool = True):
    """Standalone function to verify all profiles"""
    rotation = StructuredProfileRotation()
    return rotation.verify_all_profiles_login_status(ask_confirmation)

def test_structured_rotation():
    """Test the structured rotation system"""
    print("🧪 TESTING STRUCTURED ROTATION SYSTEM")
    print("="*50)
    
    rotation = StructuredProfileRotation()
    
    # Show current profiles
    rotation.print_rotation_status()
    
    # Test getting next few profiles (without actually loading them)
    print(f"\n🔄 TESTING ROTATION SEQUENCE:")
    for i in range(min(5, len(rotation.available_profiles))):
        next_profile = rotation.get_next_profile()
        print(f"   Rotation {i+1}: {next_profile}")
    
    print(f"\n✅ Structured rotation test complete")
    return True


if __name__ == "__main__":
    """Run profile verification and setup structured rotation"""
    print("🔄 Structured Profile Rotation Setup")
    print("="*50)
    
    choice = input("Choose action:\n1. Verify all profiles\n2. Test rotation\n3. Both\nEnter choice (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        print("\n🔍 VERIFYING ALL PROFILES...")
        results = verify_all_profiles(ask_confirmation=True)
        
        if results['verified_profiles']:
            print(f"\n✅ {len(results['verified_profiles'])} profiles are ready for structured rotation")
        else:
            print(f"\n❌ No verified profiles - please create and login to CMC profiles first")
    
    if choice in ['2', '3']:
        print("\n🧪 TESTING ROTATION...")
        test_structured_rotation()
    
    print(f"\n🎯 Setup complete! Your bot will now use structured profile rotation.")