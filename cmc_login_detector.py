#!/usr/bin/env python3
"""
CMC Login Detection & Profile Cleanup System

This system detects whether a Chrome profile is logged into CMC
and automatically removes profiles that have lost their login sessions.
"""

import os
import sys
import time
import shutil
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class CMCLoginDetector:
    """Detects CMC login status and manages profile cleanup"""
    
    def __init__(self, profile_manager=None):
        self.profile_manager = profile_manager
        self.logger = logging.getLogger(__name__)
        
        # Define login/logout indicators
        self.login_indicators = {
            'logged_out_urls': [
                '/account/login/',
                '/account/signup/',
                '/account/register/',
                'login',
                'signup',
                'register'
            ],
            'logged_out_elements': [
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Sign Up')]", 
                "//a[contains(text(), 'Log In')]",
                "//a[contains(text(), 'Sign Up')]",
                "//input[@placeholder*='email' or @placeholder*='Email']",
                "//input[@type='password']",
                "//div[contains(@class, 'login')]",
                "//div[contains(@class, 'signin')]",
                "//form[contains(@class, 'login')]"
            ],
            'logged_out_text': [
                'log in',
                'sign up', 
                'login',
                'signin',
                'continue with google',
                'continue with apple',
                'continue with email',
                'email address',
                'password',
                'create account'
            ],
            'logged_in_indicators': [
                '/portfolio/',
                '/watchlist/',
                '/account/settings/',
                'logout',
                'profile',
                'dashboard'
            ]
        }
    
    def check_cmc_login_status(self, driver, profile_name: str = None) -> dict:
        """
        Check if the current driver session is logged into CMC
        Returns detailed status information
        """
        try:
            print(f"🔍 CHECKING CMC LOGIN STATUS{f' for {profile_name}' if profile_name else ''}...")
            
            # Navigate to CMC community to test login status
            print("📍 Navigating to CMC community to check login status...")
            driver.get("https://coinmarketcap.com/community/")
            
            # Wait for page to load
            time.sleep(5)
            
            current_url = driver.current_url
            page_title = driver.title
            page_source = driver.page_source.lower()
            
            print(f"🔍 Current URL: {current_url}")
            print(f"🔍 Page Title: {page_title}")
            
            # Check for logged out indicators
            logout_score = 0
            logout_reasons = []
            
            # 1. Check URL for login/logout patterns
            for logout_url in self.login_indicators['logged_out_urls']:
                if logout_url in current_url.lower():
                    logout_score += 3
                    logout_reasons.append(f"Logout URL pattern: {logout_url}")
            
            # 2. Check for login dialog/form elements
            login_elements_found = 0
            for xpath in self.login_indicators['logged_out_elements']:
                try:
                    elements = driver.find_elements(By.XPATH, xpath)
                    if elements:
                        visible_elements = [e for e in elements if e.is_displayed()]
                        if visible_elements:
                            login_elements_found += len(visible_elements)
                            logout_score += 2
                            logout_reasons.append(f"Login element found: {xpath}")
                except:
                    continue
            
            # 3. Check page source for login text
            login_text_found = 0
            for text in self.login_indicators['logged_out_text']:
                if text in page_source:
                    login_text_found += 1
                    logout_score += 1
                    logout_reasons.append(f"Login text found: {text}")
            
            # 4. Check for logged-in indicators (negative score)
            login_score = 0
            login_reasons = []
            for indicator in self.login_indicators['logged_in_indicators']:
                if indicator in current_url.lower() or indicator in page_source:
                    login_score += 2
                    login_reasons.append(f"Logged-in indicator: {indicator}")
            
            # 5. Special check for login dialog popup (like in the screenshot)
            try:
                login_dialog = driver.find_elements(By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'dialog')]//input[@type='password' or @placeholder*='email']")
                if login_dialog:
                    logout_score += 5
                    logout_reasons.append("Login dialog/modal detected")
            except:
                pass
            
            # Calculate final status
            final_score = logout_score - login_score
            is_logged_in = final_score < 3  # Threshold for being logged in
            
            status = {
                'logged_in': is_logged_in,
                'logout_score': logout_score,
                'login_score': login_score,
                'final_score': final_score,
                'logout_reasons': logout_reasons,
                'login_reasons': login_reasons,
                'url': current_url,
                'title': page_title,
                'profile_name': profile_name,
                'login_elements_count': login_elements_found,
                'login_text_count': login_text_found
            }
            
            if is_logged_in:
                print(f"✅ LOGGED IN - Profile appears to be logged into CMC")
                print(f"   Login Score: {login_score}, Logout Score: {logout_score}")
            else:
                print(f"❌ NOT LOGGED IN - Profile session has expired or not logged in")
                print(f"   Login Score: {login_score}, Logout Score: {logout_score}")
                print(f"   Reasons: {', '.join(logout_reasons[:3])}")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error checking CMC login status: {str(e)}")
            return {
                'logged_in': False,
                'error': str(e),
                'profile_name': profile_name
            }
    
    def cleanup_logged_out_profile(self, profile_name: str) -> bool:
        """
        Remove a profile that is not logged into CMC
        """
        try:
            if not self.profile_manager:
                print("❌ No profile manager available for cleanup")
                return False
            
            profile_path = self.profile_manager.get_profile_path(profile_name)
            
            if not os.path.exists(profile_path):
                print(f"⚠️ Profile {profile_name} doesn't exist at {profile_path}")
                return False
            
            print(f"🗑️ REMOVING LOGGED-OUT PROFILE: {profile_name}")
            print(f"   Path: {profile_path}")
            
            # Create backup before deletion (optional)
            backup_path = f"{profile_path}_logged_out_backup_{int(time.time())}"
            try:
                shutil.move(profile_path, backup_path)
                print(f"✅ Profile moved to backup: {backup_path}")
                print(f"💡 You can restore it manually if needed")
            except Exception as e:
                print(f"❌ Failed to backup profile: {str(e)}")
                # Try direct deletion
                try:
                    shutil.rmtree(profile_path)
                    print(f"✅ Profile deleted directly: {profile_path}")
                except Exception as e2:
                    print(f"❌ Failed to delete profile: {str(e2)}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error during profile cleanup: {str(e)}")
            return False
    
    def scan_and_cleanup_all_profiles(self) -> dict:
        """
        Scan all CMC profiles and remove those that aren't logged in
        """
        if not self.profile_manager:
            return {'error': 'No profile manager available'}
        
        print("\n" + "="*70)
        print("🧹 CMC PROFILE LOGIN SCAN & CLEANUP")
        print("="*70)
        
        # Get all CMC profiles
        all_profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not all_profiles:
            print("❌ No CMC profiles found")
            return {'profiles_scanned': 0, 'profiles_removed': 0, 'profiles_kept': 0}
        
        print(f"🔍 Found {len(all_profiles)} CMC profiles to scan")
        
        results = {
            'profiles_scanned': 0,
            'profiles_removed': 0,
            'profiles_kept': 0,
            'logged_in_profiles': [],
            'removed_profiles': [],
            'errors': []
        }
        
        for profile_name in all_profiles:
            try:
                print(f"\n{'='*50}")
                print(f"🔍 SCANNING: {profile_name}")
                print(f"{'='*50}")
                
                # Load profile and check login status
                try:
                    driver = self.profile_manager.load_profile(profile_name)
                    time.sleep(3)  # Let profile load
                    
                    # Check login status
                    status = self.check_cmc_login_status(driver, profile_name)
                    results['profiles_scanned'] += 1
                    
                    if status.get('logged_in', False):
                        print(f"✅ KEEPING: {profile_name} - Logged into CMC")
                        results['profiles_kept'] += 1
                        results['logged_in_profiles'].append(profile_name)
                    else:
                        print(f"❌ REMOVING: {profile_name} - Not logged into CMC")
                        
                        # Close driver before cleanup
                        try:
                            driver.quit()
                        except:
                            pass
                        
                        # Remove the profile
                        if self.cleanup_logged_out_profile(profile_name):
                            results['profiles_removed'] += 1
                            results['removed_profiles'].append(profile_name)
                        else:
                            results['errors'].append(f"Failed to remove {profile_name}")
                    
                    # Close driver
                    try:
                        driver.quit()
                    except:
                        pass
                    
                except Exception as profile_error:
                    print(f"❌ Error loading profile {profile_name}: {str(profile_error)}")
                    results['errors'].append(f"Error loading {profile_name}: {str(profile_error)}")
                    continue
                
                # Brief delay between profiles
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error scanning profile {profile_name}: {str(e)}")
                results['errors'].append(f"Error scanning {profile_name}: {str(e)}")
                continue
        
        # Summary
        print(f"\n" + "="*70)
        print(f"📊 CMC PROFILE CLEANUP SUMMARY")
        print(f"="*70)
        print(f"🔍 Profiles Scanned: {results['profiles_scanned']}")
        print(f"✅ Profiles Kept (Logged In): {results['profiles_kept']}")
        print(f"🗑️ Profiles Removed (Logged Out): {results['profiles_removed']}")
        print(f"❌ Errors: {len(results['errors'])}")
        
        if results['logged_in_profiles']:
            print(f"\n✅ KEPT PROFILES:")
            for profile in results['logged_in_profiles']:
                print(f"   • {profile}")
        
        if results['removed_profiles']:
            print(f"\n🗑️ REMOVED PROFILES:")
            for profile in results['removed_profiles']:
                print(f"   • {profile}")
        
        if results['errors']:
            print(f"\n❌ ERRORS:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        print(f"="*70)
        
        return results
    
    def quick_login_check(self, driver) -> bool:
        """
        Quick check if current driver session is logged into CMC
        Used during bot operation to detect logout
        """
        try:
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            
            # Quick checks for logout indicators
            logout_indicators = [
                'log in' in page_source,
                'sign up' in page_source,
                'login' in current_url.lower(),
                'email address' in page_source,
                len(driver.find_elements(By.XPATH, "//input[@type='password']")) > 0
            ]
            
            # If 2 or more logout indicators, consider logged out
            logout_score = sum(logout_indicators)
            
            return logout_score < 2  # Logged in if less than 2 logout indicators
            
        except Exception as e:
            self.logger.debug(f"Quick login check error: {str(e)}")
            return False  # Assume logged out on error


# Standalone functions for easy integration
def scan_and_cleanup_profiles():
    """Standalone function to scan and cleanup profiles"""
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    
    profile_manager = ProfileManager()
    detector = CMCLoginDetector(profile_manager)
    
    return detector.scan_and_cleanup_all_profiles()


def check_single_profile_login(profile_name: str):
    """Check login status of a single profile"""
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    
    profile_manager = ProfileManager()
    detector = CMCLoginDetector(profile_manager)
    
    try:
        driver = profile_manager.load_profile(profile_name)
        status = detector.check_cmc_login_status(driver, profile_name)
        driver.quit()
        return status
    except Exception as e:
        return {'logged_in': False, 'error': str(e), 'profile_name': profile_name}


if __name__ == "__main__":
    """Run profile scan and cleanup"""
    print("🧹 CMC Profile Login Scanner & Cleanup Tool")
    print("This will scan all your CMC profiles and remove those that aren't logged in.")
    
    confirm = input("\nProceed with scan and cleanup? (y/n): ").strip().lower()
    if confirm == 'y':
        results = scan_and_cleanup_profiles()
        
        if results['profiles_removed'] > 0:
            print(f"\n🎯 Removed {results['profiles_removed']} logged-out profiles")
            print(f"✅ Your bot will now only use the {results['profiles_kept']} logged-in profiles")
        else:
            print(f"\n✅ All profiles are logged in - no cleanup needed")
    else:
        print("Operation cancelled.") 