#!/usr/bin/env python3
"""
Enhanced Multi-Tab CMC Account Registration System

This module handles the creation of multiple CMC accounts simultaneously using:
- SimpleLogin email aliases
- Multiple Chrome tabs
- Captcha solving integration
- Account rotation system integration
"""

import sys
import os
import time
from typing import List, Dict
from dataclasses import dataclass
import random
import logging

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
    from autocrypto_social_bot.services.account_manager import AutomatedAccountManager, Account
    from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
    from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager
except ImportError as e:
    print(f"Import error: {e}")

@dataclass
class RegistrationTab:
    """Represents a registration tab with all its details"""
    tab_id: int
    driver: webdriver.Chrome
    email_alias: str
    username: str
    password: str
    status: str = "initializing"
    account_id: int = None
    error_message: str = ""
    profile_name: str = ""

class MultiTabCMCRegistrationManager:
    """Manages multiple CMC account registrations simultaneously"""
    
    def __init__(self, simplelogin_api_key: str):
        self.simplelogin_client = EnhancedSimpleLoginAPI(simplelogin_api_key)
        self.account_manager = AutomatedAccountManager(simplelogin_api_key)
        self.profile_manager = EnhancedProfileManager()
        self.logger = logging.getLogger(__name__)
        
        # Registration tracking
        self.registration_tabs: List[RegistrationTab] = []
        self.completed_accounts: List[Account] = []
        
    def create_multiple_cmc_accounts_with_tabs(self, count: int = 10) -> Dict:
        """Create multiple CMC accounts using multiple browser tabs"""
        if count < 1 or count > 10:
            raise ValueError("Count must be between 1 and 10")
        
        print(f"\n🚀 MULTI-TAB CMC ACCOUNT REGISTRATION")
        print("=" * 60)
        print(f"📊 Creating {count} fresh CMC accounts simultaneously")
        print(f"📧 Using SimpleLogin for unique email aliases")
        print(f"🌐 Opening {count} browser tabs for parallel registration")
        print("=" * 60)
        
        try:
            # Create email aliases
            print(f"\n1️⃣ Creating {count} SimpleLogin email aliases...")
            email_aliases = self._create_email_aliases(count)
            print(f"✅ Created {len(email_aliases)} email aliases")
            
            # Initialize browser tabs
            print(f"\n2️⃣ Initializing {count} browser tabs...")
            self._initialize_registration_tabs(email_aliases)
            print(f"✅ Opened {len(self.registration_tabs)} browser tabs")
            
            # Navigate to signup
            print(f"\n3️⃣ Navigating all tabs to CMC signup page...")
            self._navigate_all_tabs_to_signup()
            
            # Fill forms
            print(f"\n4️⃣ Filling registration forms in all tabs...")
            self._fill_all_registration_forms()
            
            # Wait for captcha solving
            print(f"\n5️⃣ Waiting for captcha solving...")
            print("🔐 MANUAL CAPTCHA SOLVING REQUIRED")
            print("=" * 50)
            print("📋 INSTRUCTIONS:")
            print("1. Switch between browser tabs to solve captchas")
            print("2. Complete the registration for each account")
            print("3. Press Enter here when all captchas are solved")
            print("=" * 50)
            
            self._show_tab_summary()
            input("\n⏸️ Press Enter when you've solved all captchas...")
            
            # Verify and save
            print(f"\n6️⃣ Verifying registrations and saving accounts...")
            self._verify_and_save_accounts()
            
            # Cleanup
            print(f"\n7️⃣ Cleaning up browser tabs...")
            self._cleanup_tabs()
            
            # Results
            results = self._generate_results_summary()
            
            print(f"\n🎉 REGISTRATION COMPLETE!")
            print("=" * 50)
            print(f"✅ Successfully registered: {results['successful_accounts']}")
            print(f"❌ Failed registrations: {results['failed_accounts']}")
            print(f"📊 Success rate: {results['success_rate']:.1f}%")
            print("=" * 50)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Multi-tab registration failed: {e}")
            self._cleanup_tabs()
            raise
    
    def _create_email_aliases(self, count: int) -> List[str]:
        """Create or reuse SimpleLogin email aliases"""
        print("🔍 Checking existing SimpleLogin aliases...")
        
        # First, get existing aliases and show them
        existing_aliases = self._get_existing_aliases()
        self._show_existing_aliases(existing_aliases)
        
        # Check if we can reuse existing aliases
        available_aliases = self._filter_available_aliases(existing_aliases)
        
        aliases = []
        
        # Reuse existing aliases first
        reused_count = min(count, len(available_aliases))
        if reused_count > 0:
            print(f"♻️ Reusing {reused_count} existing aliases...")
            for i in range(reused_count):
                aliases.append(available_aliases[i]['email'])
                print(f"   ✅ Reusing: {available_aliases[i]['email']}")
        
        # Create new aliases if needed
        remaining_needed = count - len(aliases)
        if remaining_needed > 0:
            print(f"📧 Creating {remaining_needed} new aliases...")
            
            # Check if we're at the limit
            user_info = self.simplelogin_client.get_user_info()
            is_premium = user_info.get('is_premium', False)
            max_aliases = user_info.get('max_alias_free_plan', 15) if not is_premium else float('inf')
            current_count = len(existing_aliases)
            
            if not is_premium and (current_count + remaining_needed) > max_aliases:
                print(f"⚠️ WARNING: Would exceed free plan limit ({max_aliases} aliases)")
                print(f"   Current: {current_count}, Needed: {remaining_needed}, Limit: {max_aliases}")
                
                # Offer to proceed with available aliases only
                proceed = input("Continue with available aliases only? (y/n): ").strip().lower()
                if proceed != 'y':
                    raise Exception("User cancelled due to alias limit")
                
                remaining_needed = 0  # Don't create new ones
            
            for i in range(remaining_needed):
                try:
                    alias_info = self.simplelogin_client.create_random_alias(
                        hostname="coinmarketcap.com",
                        note=f"CMC account {len(aliases)+1} - Multi-tab {time.strftime('%Y-%m-%d %H:%M')}"
                    )
                    aliases.append(alias_info.email)
                    print(f"   ✅ Created: {alias_info.email}")
                    time.sleep(1)
                except Exception as e:
                    print(f"   ❌ Failed to create alias {i+1}: {e}")
                    if "limitation of a free account" in str(e):
                        print(f"   💡 Reached free account limit. Proceeding with {len(aliases)} aliases.")
                        break
        
        if not aliases:
            raise Exception("No aliases available - please upgrade to premium or delete unused aliases")
        
        print(f"✅ Ready with {len(aliases)} aliases ({reused_count} reused, {len(aliases)-reused_count} new)")
        return aliases
    
    def _get_existing_aliases(self) -> List[Dict]:
        """Get all existing SimpleLogin aliases"""
        try:
            all_aliases = []
            page = 0
            
            while True:
                result = self.simplelogin_client.get_aliases(page_id=page)
                aliases = result.get('aliases', [])
                
                if not aliases:
                    break
                
                all_aliases.extend(aliases)
                page += 1
                
                if not result.get('more', False):
                    break
            
            return all_aliases
            
        except Exception as e:
            print(f"⚠️ Could not fetch existing aliases: {e}")
            return []
    
    def _show_existing_aliases(self, aliases: List[Dict]):
        """Show existing aliases to the user"""
        if not aliases:
            print("📧 No existing aliases found")
            return
        
        stats = self.simplelogin_client.get_alias_statistics()
        is_premium = stats.get('premium', False)
        
        print(f"\n📊 EXISTING SIMPLELOGIN ALIASES ({len(aliases)} total)")
        print("="*70)
        print(f"Account Type: {'Premium' if is_premium else 'Free'}")
        if not is_premium:
            limit = stats.get('alias_limit', 15)
            print(f"Limit: {len(aliases)}/{limit} aliases used")
        print()
        
        # Group by status
        enabled_aliases = [a for a in aliases if a.get('enabled', True)]
        disabled_aliases = [a for a in aliases if not a.get('enabled', True)]
        
        print(f"✅ ENABLED ALIASES ({len(enabled_aliases)}):")
        for alias in enabled_aliases[:10]:  # Show first 10
            note = alias.get('note', 'No note')
            created = alias.get('creation_date', 'Unknown')[:10]  # Just date part
            forwards = alias.get('nb_forward', 0)
            print(f"   📧 {alias['email']}")
            print(f"      📝 {note}")
            print(f"      📅 Created: {created} | 📨 Forwards: {forwards}")
        
        if len(enabled_aliases) > 10:
            print(f"   ... and {len(enabled_aliases) - 10} more enabled aliases")
        
        if disabled_aliases:
            print(f"\n❌ DISABLED ALIASES ({len(disabled_aliases)}):")
            for alias in disabled_aliases[:5]:  # Show first 5
                note = alias.get('note', 'No note')
                print(f"   📧 {alias['email']} (disabled)")
                print(f"      📝 {note}")
        
            if len(disabled_aliases) > 5:
                print(f"   ... and {len(disabled_aliases) - 5} more disabled aliases")
        
        print("="*70)
    
    def _filter_available_aliases(self, aliases: List[Dict]) -> List[Dict]:
        """Filter aliases that can be reused for CMC registration"""
        available = []
        used_aliases = set()
        
        # Get list of already used aliases from database
        try:
            used_aliases = self._get_used_aliases_from_database()
        except Exception as e:
            print(f"⚠️ Could not check database for used aliases: {e}")
        
        print(f"\n🔍 Filtering available aliases...")
        print(f"   Total aliases: {len(aliases)}")
        
        for alias in aliases:
            alias_email = alias['email']
            
            # Only use enabled aliases
            if not alias.get('enabled', True):
                print(f"   ❌ Skipping disabled: {alias_email}")
                continue
            
            # Check if already in database
            if alias_email in used_aliases:
                print(f"   ❌ Already in database: {alias_email}")
                continue
            
            # Check if it's already used for CMC (check note or usage)
            note = alias.get('note', '').lower()
            
            # Skip if clearly marked as used for CMC already
            if any(keyword in note for keyword in ['cmc', 'coinmarketcap', 'registered', 'used']):
                print(f"   ❌ Marked as used in note: {alias_email}")
                continue
            
            # Check if it has recent activity (may be in use elsewhere)
            forwards = alias.get('nb_forward', 0)
            if forwards > 10:  # Arbitrary threshold
                print(f"   ⚠️ High activity ({forwards} forwards): {alias_email}")
                # Still add it but warn
            
            available.append(alias)
            print(f"   ✅ Available: {alias_email}")
        
        print(f"   Result: {len(available)} aliases available for reuse")
        return available
    
    def _get_used_aliases_from_database(self) -> set:
        """Get set of email aliases already used in the account database"""
        try:
            from autocrypto_social_bot.services.account_manager import AutomatedAccountManager
            manager = AutomatedAccountManager(self.simplelogin_client.api_key)
            
            # Get all accounts from database
            accounts = manager.database.get_all_accounts()
            used_emails = {account.email_alias for account in accounts if account.email_alias}
            
            return used_emails
        except Exception as e:
            # If database check fails, return empty set
            return set()
    
    def _initialize_registration_tabs(self, email_aliases: List[str]):
        """Initialize browser tabs with pre-selected email aliases"""
        for i, email in enumerate(email_aliases):
            try:
                print(f"   🌐 Creating tab {i+1} with alias: {email}")
                
                # Create Chrome profile without trying to create new SimpleLogin alias
                profile_name = f"cmc_profile_{int(time.time())}_{i+1}"
                driver = self._create_chrome_profile(profile_name)
                
                # Create the registration tab with the pre-selected email
                tab = RegistrationTab(
                    tab_id=i+1,
                    driver=driver,
                    email_alias=email,
                    username=self._generate_username(),
                    password=self._generate_password(),
                    status="tab_created",
                    profile_name=profile_name
                )
                self.registration_tabs.append(tab)
                print(f"   ✅ Tab {i+1} created with profile: {profile_name}")
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Failed to create tab {i+1}: {e}")
    
    def _create_chrome_profile(self, profile_name: str):
        """Create a new Chrome browser session with unique profile"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        import os
        
        # Create unique profile directory
        profile_dir = os.path.join(os.getcwd(), "autocrypto_social_bot", "chrome_profiles", profile_name)
        os.makedirs(profile_dir, exist_ok=True)
        
        # Chrome options for unique session
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir={profile_dir}")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-extensions-except")
        chrome_options.add_argument("--disable-plugins-discovery")
        chrome_options.add_argument("--start-maximized")
        
        # Anti-detection measures
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            
            # Anti-detection script
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            return driver
            
        except Exception as e:
            print(f"   ❌ Failed to create Chrome profile {profile_name}: {e}")
            raise
    
    def _navigate_all_tabs_to_signup(self):
        """Navigate all tabs to CMC signup popup modal"""
        for tab in self.registration_tabs:
            try:
                print(f"   🌐 Tab {tab.tab_id}: Opening CMC signup popup...")
                
                # Step 1: Go to CMC homepage
                print(f"      🌐 Loading CoinMarketCap homepage...")
                tab.driver.get("https://coinmarketcap.com")
                
                # Wait for page to fully load
                try:
                    WebDriverWait(tab.driver, 15).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    print(f"      ✅ Page loaded successfully")
                except:
                    print(f"      ⚠️ Page load timeout, continuing anyway...")
                
                time.sleep(3)
                
                # Step 2: Find and click the login/account button (opens popup)
                login_button = None
                login_selectors = [
                    # Exact XPath provided by user - this should open the popup
                    "/html/body/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[2]/div[4]/button",
                    # Alternative selectors for the account/login button
                    "//button[contains(@class, 'login') or contains(@class, 'account') or contains(@class, 'auth')]",
                    "//div[contains(@class, 'header')]//button[last()]",
                    "//nav//button[contains(@class, 'btn')]",
                    "//header//button",
                    "//button[contains(text(), 'Log In') or contains(text(), 'Login') or contains(text(), 'Account')]",
                    "//a[contains(text(), 'Log In') or contains(text(), 'Login') or contains(text(), 'Account')]"
                ]
                
                for i, selector in enumerate(login_selectors):
                    try:
                        print(f"      🔍 Trying login button selector {i+1}: {selector[:60]}...")
                        
                        if selector.startswith("//") or selector.startswith("/html"):
                            login_button = WebDriverWait(tab.driver, 8).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            login_button = WebDriverWait(tab.driver, 8).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        
                        if login_button:
                            print(f"      ✅ Found login button with selector {i+1}")
                            break
                            
                    except Exception as e:
                        print(f"      ❌ Selector {i+1} failed: {str(e)[:50]}")
                        continue
                
                if not login_button:
                    print(f"   ❌ Tab {tab.tab_id}: Could not find login button")
                    tab.status = "failed"
                    tab.error_message = "Login button not found"
                    continue
                
                # Step 3: Click the login button to open popup
                print(f"   🎯 Tab {tab.tab_id}: Clicking login button to open popup...")
                try:
                    # Scroll to button and click
                    tab.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                    time.sleep(1)
                    login_button.click()
                    print(f"      ✅ Login button clicked, popup should be opening...")
                    time.sleep(3)
                except Exception as click_error:
                    print(f"      ❌ Failed to click login button: {click_error}")
                    tab.status = "failed"
                    tab.error_message = f"Failed to click login button: {click_error}"
                    continue
                
                # Step 4: Look for "Sign Up" option in the popup
                print(f"      🔍 Looking for Sign Up option in popup...")
                signup_button = None
                signup_selectors = [
                    # Look for signup options in popup/modal
                    "//div[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dropdown')]//a[contains(text(), 'Sign Up')]",
                    "//div[contains(@class, 'modal') or contains(@class, 'popup') or contains(@class, 'dropdown')]//button[contains(text(), 'Sign Up')]",
                    "//a[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]",
                    "//button[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]",
                    "//span[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]/parent::*",
                    "//div[contains(text(), 'Sign Up') or contains(text(), 'Sign up')]",
                    # Look for any clickable element with signup text
                    "//*[contains(text(), 'Sign Up') or contains(text(), 'Sign up') or contains(text(), 'Create Account') or contains(text(), 'Register')]",
                    # Look in any visible popup/overlay
                    "//div[contains(@style, 'display') and not(contains(@style, 'none'))]//a[contains(text(), 'Sign')]",
                    "//div[contains(@style, 'display') and not(contains(@style, 'none'))]//button[contains(text(), 'Sign')]"
                ]
                
                for i, selector in enumerate(signup_selectors):
                    try:
                        print(f"      🔍 Trying signup selector {i+1}: {selector[:60]}...")
                        
                        signup_button = WebDriverWait(tab.driver, 6).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        
                        if signup_button and signup_button.is_displayed():
                            print(f"      ✅ Found signup option with selector {i+1}")
                            break
                        else:
                            signup_button = None
                            
                    except Exception as e:
                        print(f"      ❌ Signup selector {i+1} failed: {str(e)[:50]}")
                        continue
                
                # Step 5: Click Sign Up to show signup form
                if signup_button:
                    print(f"   🎯 Tab {tab.tab_id}: Clicking Sign Up to show signup form...")
                    try:
                        tab.driver.execute_script("arguments[0].scrollIntoView(true);", signup_button)
                        time.sleep(1)
                        signup_button.click()
                        print(f"      ✅ Sign Up clicked, signup form should be visible")
                        time.sleep(3)
                    except Exception as signup_error:
                        print(f"      ❌ Failed to click Sign Up: {signup_error}")
                        # Continue anyway, maybe the form is already visible
                
                # Step 6: Wait for signup form to appear (in popup or on page)
                print(f"      🔍 Waiting for signup form to appear...")
                try:
                    form_element = WebDriverWait(tab.driver, 10).until(
                        EC.any_of(
                            EC.presence_of_element_located((By.NAME, "email")),
                            EC.presence_of_element_located((By.ID, "email")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='email' i]")),
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Email' i]"))
                        )
                    )
                    print(f"      ✅ Signup form found and ready")
                    tab.status = "navigated"
                    
                except Exception as form_error:
                    print(f"      ⚠️ Signup form not found, but continuing: {form_error}")
                    # Check what's actually on the page
                    current_url = tab.driver.current_url
                    page_title = tab.driver.title
                    print(f"      📋 Current URL: {current_url}")
                    print(f"      📋 Page title: {page_title}")
                    
                    # Look for any input fields
                    all_inputs = tab.driver.find_elements(By.CSS_SELECTOR, "input")
                    print(f"      📋 Found {len(all_inputs)} input fields on page")
                    
                    tab.status = "navigated"  # Continue anyway, form filling will handle it
                    
            except Exception as e:
                print(f"   ❌ Tab {tab.tab_id}: Navigation failed - {e}")
                tab.status = "failed"
                tab.error_message = f"Navigation failed: {e}"
    
    def _fill_all_registration_forms(self):
        """Fill registration forms"""
        for tab in self.registration_tabs:
            if tab.status == "navigated":
                try:
                    self._fill_registration_form(tab)
                except Exception as e:
                    tab.status = "failed"
                    tab.error_message = f"Form filling failed: {e}"
    
    def _fill_registration_form(self, tab: RegistrationTab):
        """Fill CMC registration form with generated credentials"""
        driver = tab.driver
        
        print(f"   📝 Tab {tab.tab_id}: Filling registration form...")
        print(f"       📧 Email: {tab.email_alias}")
        print(f"       👤 Username: {tab.username}")
        print(f"       🔐 Password: testcmc123!")
        
        try:
            # Find email field with multiple selectors
            email_field = None
            email_selectors = [
                (By.NAME, "email"),
                (By.ID, "email"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='email' i]"),
                (By.CSS_SELECTOR, "input[placeholder*='Email' i]"),
                (By.XPATH, "//input[@type='email']"),
                (By.XPATH, "//input[contains(@placeholder, 'email')]")
            ]
            
            for selector_type, selector in email_selectors:
                try:
                    email_field = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((selector_type, selector))
                    )
                    break
                except:
                    continue
            
            if email_field:
                email_field.clear()
                email_field.send_keys(tab.email_alias)
                print(f"   ✅ Tab {tab.tab_id}: Email filled")
                time.sleep(1)
            else:
                print(f"   ❌ Tab {tab.tab_id}: Could not find email field")
                tab.status = "failed"
                tab.error_message = "Email field not found"
                return
            
            # Find username field
            username_field = None
            username_selectors = [
                (By.NAME, "username"),
                (By.ID, "username"),
                (By.CSS_SELECTOR, "input[name='username']"),
                (By.CSS_SELECTOR, "input[placeholder*='username' i]"),
                (By.CSS_SELECTOR, "input[placeholder*='Username' i]"),
                (By.XPATH, "//input[@name='username']"),
                (By.XPATH, "//input[contains(@placeholder, 'username')]")
            ]
            
            for selector_type, selector in username_selectors:
                try:
                    username_field = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
            
            if username_field:
                username_field.clear()
                username_field.send_keys(tab.username)
                print(f"   ✅ Tab {tab.tab_id}: Username filled")
                time.sleep(1)
            else:
                print(f"   ⚠️ Tab {tab.tab_id}: Username field not found (may not be required)")
            
            # Find password field
            password_field = None
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.XPATH, "//input[@type='password']"),
                (By.XPATH, "//input[@name='password']")
            ]
            
            for selector_type, selector in password_selectors:
                try:
                    password_field = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
            
            if password_field:
                password_field.clear()
                password_field.send_keys("testcmc123!")
                print(f"   ✅ Tab {tab.tab_id}: Password filled")
                time.sleep(1)
            else:
                print(f"   ❌ Tab {tab.tab_id}: Could not find password field")
                tab.status = "failed"
                tab.error_message = "Password field not found"
                return
            
            # Find confirm password field (may not exist)
            confirm_field = None
            confirm_selectors = [
                (By.NAME, "confirmPassword"),
                (By.NAME, "confirm_password"),
                (By.NAME, "passwordConfirmation"),
                (By.ID, "confirmPassword"),
                (By.ID, "confirm_password"),
                (By.CSS_SELECTOR, "input[name*='confirm']"),
                (By.XPATH, "//input[contains(@name, 'confirm')]")
            ]
            
            for selector_type, selector in confirm_selectors:
                try:
                    confirm_field = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
            
            if confirm_field:
                confirm_field.clear()
                confirm_field.send_keys("testcmc123!")
                print(f"   ✅ Tab {tab.tab_id}: Confirm password filled")
                time.sleep(1)
            else:
                print(f"   ⚠️ Tab {tab.tab_id}: Confirm password field not found (may not be required)")
            
            # Check terms and conditions checkbox
            try:
                terms_selectors = [
                    (By.CSS_SELECTOR, "input[type='checkbox']"),
                    (By.XPATH, "//input[@type='checkbox']"),
                    (By.CSS_SELECTOR, "input[name*='terms']"),
                    (By.CSS_SELECTOR, "input[name*='agree']"),
                    (By.XPATH, "//input[contains(@name, 'terms')]"),
                    (By.XPATH, "//input[contains(@name, 'agree')]")
                ]
                
                terms_checkbox = None
                for selector_type, selector in terms_selectors:
                    try:
                        terms_checkbox = driver.find_element(selector_type, selector)
                        break
                    except:
                        continue
                
                if terms_checkbox and not terms_checkbox.is_selected():
                    terms_checkbox.click()
                    print(f"   ✅ Tab {tab.tab_id}: Terms checkbox checked")
                    time.sleep(1)
                elif terms_checkbox:
                    print(f"   ✅ Tab {tab.tab_id}: Terms already checked")
                else:
                    print(f"   ⚠️ Tab {tab.tab_id}: Terms checkbox not found")
                    
            except Exception as e:
                print(f"   ⚠️ Tab {tab.tab_id}: Error with terms checkbox: {e}")
            
            # Look for submit/register button but don't click it yet (wait for captcha)
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.CSS_SELECTOR, "input[type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Sign Up')]"),
                (By.XPATH, "//button[contains(text(), 'Register')]"),
                (By.XPATH, "//button[contains(text(), 'Create Account')]"),
                (By.XPATH, "//input[@value='Sign Up']"),
                (By.CSS_SELECTOR, "button[class*='submit']"),
                (By.CSS_SELECTOR, "button[class*='register']")
            ]
            
            submit_button = None
            for selector_type, selector in submit_selectors:
                try:
                    submit_button = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
            
            if submit_button:
                print(f"   ✅ Tab {tab.tab_id}: Form ready for submission (captcha required)")
                print(f"       🔐 SOLVE CAPTCHA MANUALLY then click Submit!")
            else:
                print(f"   ⚠️ Tab {tab.tab_id}: Submit button not found")
            
            tab.status = "form_filled"
            print(f"   ✅ Tab {tab.tab_id}: All form fields completed")
            
        except Exception as e:
            print(f"   ❌ Tab {tab.tab_id}: Form filling error - {e}")
            tab.status = "failed"
            tab.error_message = f"Form filling failed: {e}"
    
    def _show_tab_summary(self):
        """Show detailed tab summary with credentials"""
        print(f"\n{'='*80}")
        print(f"🔍 CMC REGISTRATION TAB SUMMARY")
        print(f"{'='*80}")
        
        for tab in self.registration_tabs:
            status_emoji = {
                "pending": "⏳",
                "navigated": "🌐",
                "form_filled": "📝",
                "submitted": "🚀",
                "completed": "✅",
                "failed": "❌"
            }.get(tab.status, "❓")
            
            print(f"{status_emoji} Tab {tab.tab_id}: {tab.status.upper()}")
            print(f"   📧 Email: {tab.email_alias}")
            print(f"   👤 Username: {tab.username}")
            print(f"   🔐 Password: testcmc123!")
            
            # Show what's been done and what's next
            if tab.status == "navigated":
                print(f"   📋 Status: On CMC signup page, ready for form filling")
            elif tab.status == "form_filled":
                print(f"   📋 Status: Form completed - SOLVE CAPTCHA and click Submit!")
                print(f"   🎯 Action: Switch to this tab, solve captcha, click Submit button")
            elif tab.status == "completed":
                print(f"   📋 Status: Account successfully registered!")
            elif tab.status == "failed":
                print(f"   🚨 Error: {tab.error_message}")
            
            print()
        
        # Show overall statistics
        total = len(self.registration_tabs)
        completed = len([t for t in self.registration_tabs if t.status == "completed"])
        form_filled = len([t for t in self.registration_tabs if t.status == "form_filled"])
        failed = len([t for t in self.registration_tabs if t.status == "failed"])
        
        print(f"📊 PROGRESS: {completed}/{total} completed | {form_filled} awaiting captcha | {failed} failed")
        
        if form_filled > 0:
            print(f"\n{'='*50}")
            print(f"💡 CAPTCHA SOLVING INSTRUCTIONS:")
            print(f"{'='*50}")
            print(f"1. 🔄 Switch between browser tabs ({form_filled} tabs need attention)")
            print(f"2. 🔐 Solve the captcha in each tab")
            print(f"3. ✅ Click the Submit/Sign Up button")
            print(f"4. ⏸️ Return here and press Enter when all done")
            print(f"{'='*50}")
        
        print()
    
    def _verify_and_save_accounts(self):
        """Verify and save accounts"""
        for tab in self.registration_tabs:
            if tab.status == "failed":
                continue
            try:
                print(f"🔍 Verifying tab {tab.tab_id} ({tab.email_alias})...")
                
                if self._verify_registration_success(tab):
                    print(f"   ✅ Tab {tab.tab_id}: Registration successful!")
                    
                    # Create account object with the correct profile name
                    account = Account(
                        email_alias=tab.email_alias,
                        password="testcmc123!",
                        username=tab.username,
                        platform="cmc",
                        profile_name=tab.profile_name,  # Use the actual profile name created
                        status="active",
                        notes=f"Multi-tab registration - Tab {tab.tab_id} - {time.strftime('%Y-%m-%d %H:%M')}"
                    )
                    
                    # Save to database
                    account.id = self._save_account_to_database(account)
                    if account.id:
                        self.completed_accounts.append(account)
                        tab.status = "completed"
                        tab.account_id = account.id
                        print(f"   💾 Tab {tab.tab_id}: Saved to database (ID: {account.id})")
                    else:
                        tab.status = "failed"
                        tab.error_message = "Failed to save to database"
                else:
                    tab.status = "failed"
                    tab.error_message = "Registration verification failed"
                    print(f"   ❌ Tab {tab.tab_id}: Verification failed")
                    
            except Exception as e:
                tab.status = "failed"
                tab.error_message = f"Verification error: {e}"
                print(f"   ❌ Tab {tab.tab_id}: Error during verification: {e}")
    
    def _save_account_to_database(self, account: Account) -> int:
        """Save account to database without creating new SimpleLogin alias"""
        try:
            # Use the existing account manager database directly
            account_id = self.account_manager.database.add_account(account)
            return account_id
        except Exception as e:
            print(f"   ❌ Database save error: {e}")
            return None
    
    def _verify_registration_success(self, tab: RegistrationTab) -> bool:
        """Verify registration success by checking browser and email forwards"""
        try:
            # Check browser indicators
            current_url = tab.driver.current_url.lower()
            success_indicators = ["/dashboard", "/profile", "/account", "welcome", "verify"]
            browser_success = any(indicator in current_url for indicator in success_indicators)
            
            # Also check if we're no longer on signup page
            if "signup" not in current_url and "register" not in current_url:
                browser_success = True
            
            # Check for email forwards (indicates CMC sent verification email)
            email_success = self._check_email_forwards(tab.email_alias)
            
            print(f"   🔍 Tab {tab.tab_id} verification:")
            print(f"      🌐 Browser: {'✅ Success' if browser_success else '❌ Still on signup'}")
            print(f"      📧 Email: {'✅ Got forwards' if email_success else '⚠️ No forwards yet'}")
            
            # Success if either browser shows success OR we got email forwards
            return browser_success or email_success
            
        except Exception as e:
            print(f"   ❌ Tab {tab.tab_id} verification error: {e}")
            return False
    
    def _check_email_forwards(self, email_alias: str) -> bool:
        """Check if an email alias has received any forwards (indicates successful registration)"""
        try:
            # Get the alias by email to check forward count
            alias_info = self.simplelogin_client.get_alias_by_email(email_alias)
            if alias_info:
                forwards = alias_info.nb_forward
                print(f"      📨 {email_alias}: {forwards} forwards")
                return forwards > 0
            return False
        except Exception as e:
            print(f"      ⚠️ Could not check forwards for {email_alias}: {e}")
            return False
    
    def _cleanup_tabs(self):
        """Clean up browser tabs"""
        for tab in self.registration_tabs:
            try:
                tab.driver.quit()
            except:
                pass
        self.registration_tabs.clear()
    
    def _generate_results_summary(self) -> Dict:
        """Generate results summary"""
        successful = len(self.completed_accounts)
        total = len(self.registration_tabs)
        
        return {
            "successful_accounts": successful,
            "failed_accounts": total - successful,
            "total_attempts": total,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "completed_accounts": self.completed_accounts
        }
    
    def _generate_username(self) -> str:
        """Generate username"""
        prefixes = ["crypto", "trader", "hodler", "bull", "bear"]
        suffixes = ["master", "lord", "king", "guru", "pro"]
        return f"{random.choice(prefixes)}_{random.choice(suffixes)}_{random.randint(100, 9999)}"
    
    def _generate_password(self) -> str:
        """Generate consistent password"""
        return "testcmc123!"

def run_multi_tab_cmc_registration(count: int = 10) -> Dict:
    """Main function for menu integration"""
    config = SimpleLoginConfig()
    if not config.is_configured():
        raise Exception("SimpleLogin not configured!")
    
    manager = MultiTabCMCRegistrationManager(config.get_api_key())
    return manager.create_multiple_cmc_accounts_with_tabs(count)

if __name__ == "__main__":
    # Test the multi-tab registration system
    try:
        results = run_multi_tab_cmc_registration(3)  # Test with 3 accounts
        print(f"\n🎉 Test completed!")
        print(f"✅ Created {results['successful_accounts']} accounts")
    except Exception as e:
        print(f"❌ Test failed: {e}") 