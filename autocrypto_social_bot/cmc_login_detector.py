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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        IMPROVED: Click test approach - try clicking login button to see if popup appears
        """
        try:
            print(f"🔍 CHECKING CMC LOGIN STATUS{f' for {profile_name}' if profile_name else ''}...")
            
            # Navigate to CMC main page for accurate detection
            print("📍 Navigating to CMC main page to check login status...")
            driver.get("https://coinmarketcap.com/")
            
            # Wait for page to load
            time.sleep(5)
            
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"🔍 Current URL: {current_url}")
            print(f"🔍 Page Title: {page_title}")
            
            # CLICK TEST APPROACH: Try to find and click login button
            print("🎯 CLICK TEST: Looking for 'Log In' button to click...")
            
            # EXACT CMC login button selectors based on actual HTML structure
            login_button_selectors = [
                # PRIMARY: Exact match for CMC login button with data attributes
                "//button[@data-btnname='Log In']",
                "//button[@data-forcetrack='Log In']",
                "//button[@data-test='Log In']",
                
                # SECONDARY: Class-based selectors for CMC button structure
                "//button[contains(@class, 'BaseButton_base') and contains(@class, 'BaseButton_v-primary')]//div[contains(text(), 'Log In')]/..",
                "//button[contains(@class, 'BaseButton_base') and .//div[text()='Log In']]",
                "//button[contains(@class, 'eQBACe') and contains(@class, 'BaseButton_base') and .//div[text()='Log In']]",
                
                # TERTIARY: XPath based on the exact structure you provided
                "//button[contains(@class, 'BaseButton_base') and contains(@class, 'BaseButton_v-primary')]//div[@data-role='btn-content-item' and text()='Log In']/../..",
                "//button//div[@data-role='btn-content-item' and text()='Log In']/../..",
                "//div[@data-role='btn-content-item' and text()='Log In']/ancestor::button",
                
                # QUATERNARY: Full XPath pattern match
                "/html/body/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div[4]/button",
                "/html/body/div[2]/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div[4]/button/div[1]/..",
                
                # FALLBACK: General patterns (kept for compatibility)
                "//button[contains(text(), 'Log In')]",
                "//button[text()='Log In']",
                "//button//div[text()='Log In']/ancestor::button",
                
                # Additional CMC-specific patterns
                "//button[contains(@class, 'BaseButton') and contains(., 'Log In')]",
                "//button[@data-page='HomePage' and contains(., 'Log In')]",
                
                # Generic fallbacks
                "//*[contains(text(), 'Log In') and self::button]",
                "//a[contains(text(), 'Log In')]"
            ]
            
            login_button_element = None
            login_button_details = []
            
            # Try to find the login button
            for selector in login_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            button_text = element.text.strip()
                            button_tag = element.tag_name
                            button_class = element.get_attribute('class') or ''
                            
                            print(f"🔍 FOUND LOGIN BUTTON: '{button_text}' ({button_tag}, class: {button_class[:50]})")
                            login_button_element = element
                            login_button_details.append(f"{button_tag}[{button_class[:30]}]: '{button_text}'")
                            break
                    if login_button_element:
                        break
                except Exception as e:
                    continue
            
            # PERFORM CLICK TEST
            if login_button_element:
                print("🖱️ CLICK TEST: Attempting to click login button...")
                
                try:
                    # Get current window handles before clicking
                    windows_before = driver.window_handles
                    
                    # Try to click the login button
                    driver.execute_script("arguments[0].click();", login_button_element)
                    time.sleep(3)  # Wait for potential popup/modal
                    
                    # Check for new windows/tabs
                    windows_after = driver.window_handles
                    new_window_opened = len(windows_after) > len(windows_before)
                    
                    # Check for modal/popup on same page
                    modal_selectors = [
                        "//div[contains(@class, 'modal')]",
                        "//div[contains(@class, 'popup')]",
                        "//div[contains(@class, 'dialog')]",
                        "//div[contains(@class, 'overlay')]",
                        "//form[contains(@class, 'login')]",
                        "//div[contains(@class, 'login-form')]",
                        "//div[contains(@class, 'signin')]",
                        "//input[@type='email' or @type='password']"
                    ]
                    
                    modal_found = False
                    for selector in modal_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed():
                                    print(f"📝 FOUND LOGIN FORM: {element.tag_name} with class '{element.get_attribute('class')}'")
                                    modal_found = True
                                    break
                            if modal_found:
                                break
                        except:
                            continue
                    
                    # Determine result based on click test
                    if new_window_opened or modal_found:
                        print("❌ CLICK TEST RESULT: NOT LOGGED IN")
                        print("   Reason: Login button opened popup/modal/new window")
                        is_logged_in = False
                        primary_reason = "Login button functional - opened login form"
                        
                        # Close any new windows that opened
                        if new_window_opened:
                            for handle in windows_after:
                                if handle not in windows_before:
                                    driver.switch_to.window(handle)
                                    driver.close()
                            driver.switch_to.window(windows_before[0])
                        
                        # Try to close modal if it exists
                        if modal_found:
                            try:
                                # Look for close button
                                close_selectors = [
                                    "//button[contains(@class, 'close')]",
                                    "//button[contains(text(), 'Close')]",
                                    "//button[contains(text(), '×')]",
                                    "//*[contains(@class, 'close')]"
                                ]
                                for close_selector in close_selectors:
                                    try:
                                        close_btn = driver.find_element(By.XPATH, close_selector)
                                        if close_btn.is_displayed():
                                            close_btn.click()
                                            break
                                    except:
                                        continue
                                # Fallback: press Escape key
                                from selenium.webdriver.common.keys import Keys
                                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                            except:
                                pass
                    else:
                        print("✅ CLICK TEST RESULT: LOGGED IN")
                        print("   Reason: Login button didn't open popup (likely user menu)")
                        is_logged_in = True
                        primary_reason = "Login button non-functional - likely already logged in"
                    
                except Exception as click_error:
                    print(f"❌ CLICK TEST FAILED: {str(click_error)}")
                    print("   Assuming NOT LOGGED IN due to click test failure")
                    is_logged_in = False
                    primary_reason = f"Click test failed: {str(click_error)}"
            
            else:
                # NO LOGIN BUTTON FOUND
                print("🔍 NO LOGIN BUTTON FOUND - Checking for logged-in indicators...")
                
                # Look for clear logged-in indicators
                logged_in_selectors = [
                    # User profile/avatar indicators
                    "//button[contains(@class, 'user') or contains(@class, 'profile')]//img",
                    "//div[contains(@class, 'user-menu')]",
                    "//div[contains(@class, 'profile-menu')]",
                    
                    # Logout option (clear indicator of being logged in)
                    "//button[contains(text(), 'Logout') or contains(text(), 'Sign Out')]",
                    "//a[contains(text(), 'Logout') or contains(text(), 'Sign Out')]",
                    "//a[contains(@href, 'logout')]",
                    
                    # Portfolio/watchlist (logged-in features)
                    "//a[contains(@href, '/portfolio/')]",
                    "//a[contains(@href, '/watchlist/')]",
                    "//a[contains(text(), 'Portfolio')]",
                    "//a[contains(text(), 'Watchlist')]",
                    
                    # Account settings
                    "//a[contains(@href, '/account/')]",
                    "//a[contains(text(), 'Account')]"
                ]
                
                logged_in_found = False
                logged_in_details = []
                
                for selector in logged_in_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed():
                                element_text = element.text.strip()
                                element_tag = element.tag_name
                                element_class = element.get_attribute('class') or ''
                                element_href = element.get_attribute('href') or ''
                                
                                print(f"✅ FOUND LOGGED-IN INDICATOR: '{element_text}' ({element_tag}, href: {element_href[:50]})")
                                logged_in_found = True
                                logged_in_details.append(f"{element_tag}: '{element_text}' ({element_href[:30]})")
                                break
                        if logged_in_found:
                            break
                    except Exception as e:
                        continue
                
                if logged_in_found:
                    print("✅ NO LOGIN BUTTON + LOGGED-IN INDICATORS = LOGGED IN")
                    is_logged_in = True
                    primary_reason = "No login button found, logged-in indicators present"
                else:
                    print("❓ NO LOGIN BUTTON + NO CLEAR INDICATORS = UNCLEAR")
                    print("   Performing additional verification...")
                    
                    # Additional check: try to access a logged-in only page
                    try:
                        print("🔍 Testing access to portfolio page...")
                        original_url = driver.current_url
                        driver.get("https://coinmarketcap.com/portfolio/")
                        time.sleep(3)
                        
                        current_url_after = driver.current_url
                        if '/portfolio/' in current_url_after and 'login' not in current_url_after.lower():
                            print("✅ Portfolio page accessible - LOGGED IN")
                            is_logged_in = True
                            primary_reason = "Portfolio page accessible"
                        else:
                            print("❌ Portfolio page redirected to login - NOT LOGGED IN")
                            is_logged_in = False
                            primary_reason = "Portfolio page inaccessible"
                        
                        # Go back to main page
                        driver.get("https://coinmarketcap.com/")
                        time.sleep(2)
                        
                    except Exception as portfolio_error:
                        print(f"❌ Portfolio test failed: {str(portfolio_error)}")
                        is_logged_in = False
                        primary_reason = f"Portfolio test failed: {str(portfolio_error)}"
            
            # Compile results
            status = {
                'logged_in': is_logged_in,
                'primary_reason': primary_reason,
                'login_button_found': bool(login_button_element),
                'login_button_details': login_button_details,
                'click_test_performed': bool(login_button_element),
                'url': current_url,
                'title': page_title,
                'profile_name': profile_name
            }
            
            # Clear summary
            print(f"\n{'='*60}")
            if is_logged_in:
                print(f"✅ FINAL RESULT: LOGGED IN")
                print(f"   Profile: {profile_name}")
                print(f"   Reason: {primary_reason}")
            else:
                print(f"❌ FINAL RESULT: NOT LOGGED IN")
                print(f"   Profile: {profile_name}")
                print(f"   Reason: {primary_reason}")
            print(f"{'='*60}")
            
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
        IMPROVED: Simple click test - try clicking login button
        """
        try:
            # EXACT CMC login button selectors (same as full detection)
            login_button_selectors = [
                # PRIMARY: Exact match for CMC login button with data attributes
                "//button[@data-btnname='Log In']",
                "//button[@data-forcetrack='Log In']",
                "//button[@data-test='Log In']",
                
                # SECONDARY: Class-based selectors for CMC button structure
                "//button[contains(@class, 'BaseButton_base') and .//div[text()='Log In']]",
                "//div[@data-role='btn-content-item' and text()='Log In']/ancestor::button",
                
                # FALLBACK: General patterns
                "//button[contains(text(), 'Log In')]",
                "//button[text()='Log In']"
            ]
            
            # Try to find login button
            login_button = None
            for selector in login_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            login_button = element
                            break
                    if login_button:
                        break
                except:
                    continue
            
            if login_button:
                # Found login button - try quick click test
                try:
                    # Get window count before click
                    windows_before = len(driver.window_handles)
                    
                    # Click the button
                    driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(2)  # Brief wait
                    
                    # Check for new windows or modals
                    windows_after = len(driver.window_handles)
                    
                    # Look for login form quickly
                    modal_found = False
                    try:
                        modal_elements = driver.find_elements(By.XPATH, "//input[@type='email' or @type='password']")
                        modal_found = any(elem.is_displayed() for elem in modal_elements)
                    except:
                        pass
                    
                    # Clean up if modal/window opened
                    if windows_after > windows_before:
                        # Close new window
                        driver.switch_to.window(driver.window_handles[-1])
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    elif modal_found:
                        # Try to close modal
                        try:
                            from selenium.webdriver.common.keys import Keys
                            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        except:
                            pass
                    
                    # Return result
                    return not (windows_after > windows_before or modal_found)
                    
                except:
                    return False  # Click failed, assume not logged in
            else:
                # No login button found - likely logged in
                return True
            
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