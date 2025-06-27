import sys
import os
import logging
from typing import Optional, Dict, List
import time
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.services.account_manager import AutomatedAccountManager, Account
from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EnhancedProfileManager:
    """
    Enhanced profile manager that combines Chrome profiles with automated account creation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize SimpleLogin configuration
        self.simplelogin_config = SimpleLoginConfig()
        if not self.simplelogin_config.is_configured():
            raise ValueError("SimpleLogin API key not configured! Run setup_simplelogin.py first.")
        
        # Initialize components
        self.profile_manager = ProfileManager()
        self.account_manager = AutomatedAccountManager(self.simplelogin_config.get_api_key())
        
        # Track current account and profile
        self.current_account = None
        self.current_driver = None
        
        self.logger.info("✅ Enhanced Profile Manager initialized")
    
    def create_fresh_account_with_profile(self, platform: str = "cmc", force_create: bool = False) -> tuple[Account, webdriver.Chrome]:
        """
        Get a fresh account with corresponding Chrome profile (only creates new if forced)
        """
        try:
            self.logger.info(f"🚀 Getting fresh {platform} account with Chrome profile...")
            
            # Try to get existing account first, only create new if forced
            if force_create:
                # Create new account with SimpleLogin alias (only when explicitly requested)
                account = self.account_manager.create_new_account(platform)
            else:
                # Use existing account
                account = self.account_manager.get_next_account(platform, auto_create=False)
                if not account:
                    raise ValueError(f"No existing accounts available for {platform}. Please create accounts manually or use force_create=True.")
            
            # Use existing profile instead of creating new one
            profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            if not profiles:
                raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
            
            # Use first available profile
            profile_name = profiles[0]
            
            # Update account with profile name
            account.profile_name = profile_name
            self.account_manager.database.mark_account_status(
                account.id, 
                "active", 
                f"Associated with Chrome profile: {profile_name}"
            )
            
            # Load existing Chrome profile
            driver = self.profile_manager.load_profile_with_enterprise_proxy(profile_name)
            
            # Store current state
            self.current_account = account
            self.current_driver = driver
            
            self.logger.info(f"✅ Using account {account.username} with profile {profile_name}")
            return account, driver
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get fresh account with profile: {e}")
            raise
    
    def rotate_to_fresh_account(self, platform: str = "cmc", max_daily_posts: int = 10, allow_exhausted: bool = True) -> tuple[Account, webdriver.Chrome]:
        """
        Rotate to a fresh account that hasn't exceeded daily post limits
        """
        try:
            self.logger.info(f"🔄 Rotating to fresh {platform} account...")
            
            # Close current driver if exists
            if self.current_driver:
                try:
                    self.current_driver.quit()
                except:
                    pass
                self.current_driver = None
            
            # Get fresh account (only use existing accounts)
            account = self.account_manager.rotate_to_fresh_account(platform, max_daily_posts, auto_create=False)
            
            if not account:
                if allow_exhausted:
                    # If no fresh accounts, use any existing account
                    account = self.account_manager.get_next_account(platform, auto_create=False)
                    if account:
                        self.logger.warning(f"⚠️ All accounts exhausted. Using account with {account.posts_today} posts today.")
                
                if not account:
                    raise ValueError(f"No accounts available for {platform}. Please create accounts manually.")
            
            # Load appropriate Chrome profile
            if account.profile_name:
                # Use existing profile
                driver = self.profile_manager.load_profile_with_enterprise_proxy(account.profile_name)
            else:
                # Use existing profile instead of creating new one
                profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if not profiles:
                    raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
                
                # Use first available profile
                profile_name = profiles[0]
                
                # Update account with profile name
                account.profile_name = profile_name
                self.account_manager.database.mark_account_status(
                    account.id, 
                    "active", 
                    f"Associated with Chrome profile: {profile_name}"
                )
                
                driver = self.profile_manager.load_profile_with_enterprise_proxy(profile_name)
            
            # Store current state
            self.current_account = account
            self.current_driver = driver
            
            self.logger.info(f"✅ Rotated to account {account.username} (posts today: {account.posts_today})")
            return account, driver
            
        except Exception as e:
            self.logger.error(f"❌ Failed to rotate to fresh account: {e}")
            raise
    
    def login_to_platform(self, platform: str = "cmc", max_retries: int = 3) -> bool:
        """
        Automatically log in to the platform using current account credentials
        """
        if not self.current_account or not self.current_driver:
            raise ValueError("No active account or driver!")
        
        try:
            if platform == "cmc":
                return self._login_to_cmc(max_retries)
            elif platform == "twitter":
                return self._login_to_twitter(max_retries)
            else:
                self.logger.error(f"Unsupported platform: {platform}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Failed to login to {platform}: {e}")
            return False
    
    def _login_to_cmc(self, max_retries: int) -> bool:
        """Login to CoinMarketCap"""
        for attempt in range(max_retries):
            try:
                self.logger.info(f"🔐 Logging into CMC (attempt {attempt + 1}/{max_retries})...")
                
                # Navigate to CMC login page
                self.current_driver.get("https://coinmarketcap.com/account/login/")
                time.sleep(3)
                
                # Wait for login form
                wait = WebDriverWait(self.current_driver, 20)
                
                # Find and fill email
                email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
                email_input.clear()
                email_input.send_keys(self.current_account.email_alias)
                
                # Find and fill password
                password_input = self.current_driver.find_element(By.NAME, "password")
                password_input.clear()
                password_input.send_keys(self.current_account.password)
                
                # Click login button
                login_button = self.current_driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_button.click()
                
                # Wait for login to complete or error to appear
                time.sleep(5)
                
                # Check if login was successful
                if "dashboard" in self.current_driver.current_url.lower() or "profile" in self.current_driver.current_url.lower():
                    self.logger.info("✅ Successfully logged into CMC!")
                    return True
                elif "login" in self.current_driver.current_url.lower():
                    # Check for error messages
                    error_elements = self.current_driver.find_elements(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
                    if error_elements:
                        error_text = error_elements[0].text
                        self.logger.warning(f"⚠️ Login failed: {error_text}")
                        
                        # If account doesn't exist, we need to register
                        if "not found" in error_text.lower() or "invalid" in error_text.lower():
                            self.logger.info("📝 Account doesn't exist, attempting to register...")
                            return self._register_cmc_account()
                    else:
                        self.logger.warning("⚠️ Login failed for unknown reason")
                
            except Exception as e:
                self.logger.error(f"❌ Login attempt {attempt + 1} failed: {e}")
                time.sleep(2)
        
        return False
    
    def _register_cmc_account(self) -> bool:
        """Register a new CMC account"""
        try:
            self.logger.info("📝 Registering new CMC account...")
            
            # Navigate to registration page
            self.current_driver.get("https://coinmarketcap.com/account/signup/")
            time.sleep(3)
            
            wait = WebDriverWait(self.current_driver, 20)
            
            # Fill registration form
            username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            username_input.clear()
            username_input.send_keys(self.current_account.username)
            
            email_input = self.current_driver.find_element(By.NAME, "email")
            email_input.clear()
            email_input.send_keys(self.current_account.email_alias)
            
            password_input = self.current_driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(self.current_account.password)
            
            # Confirm password if field exists
            try:
                confirm_password = self.current_driver.find_element(By.NAME, "confirmPassword")
                confirm_password.clear()
                confirm_password.send_keys(self.current_account.password)
            except:
                pass
            
            # Accept terms if checkbox exists
            try:
                terms_checkbox = self.current_driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                if not terms_checkbox.is_selected():
                    terms_checkbox.click()
            except:
                pass
            
            # Submit registration
            submit_button = self.current_driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            submit_button.click()
            
            time.sleep(5)
            
            # Check if registration was successful
            if "verify" in self.current_driver.current_url.lower() or "welcome" in self.current_driver.current_url.lower():
                self.logger.info("✅ Account registration submitted! Check email for verification.")
                self.account_manager.database.mark_account_status(
                    self.current_account.id,
                    "pending_verification",
                    "Account registered, awaiting email verification"
                )
                return True
            else:
                self.logger.error("❌ Registration failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Registration failed: {e}")
            return False
    
    def post_comment(self, comment_text: str, target_url: str = None) -> bool:
        """
        Post a comment using the current account with login detection
        """
        if not self.current_account or not self.current_driver:
            raise ValueError("No active account or driver!")
        
        try:
            self.logger.info(f"💬 Posting comment with account {self.current_account.username}...")
            
            # ENHANCED: Check if logged into CMC before attempting to post
            try:
                if hasattr(self.profile_manager, 'quick_login_check'):
                    print("🔍 Verifying CMC login status before posting...")
                    is_logged_in = self.profile_manager.quick_login_check(self.current_driver)
                    
                    if not is_logged_in:
                        print("❌ Current session is not logged into CMC!")
                        print("💡 TIP: Consider account rotation to use a logged-in profile")
                        # Don't abort - let the posting attempt continue and handle the failure
                        self.logger.warning("Session appears to be logged out - posting may fail")
                    else:
                        print("✅ Session appears to be logged into CMC")
                        
            except Exception as login_check_error:
                self.logger.debug(f"Could not verify login status: {str(login_check_error)}")
                print("⚠️ Could not verify login status - continuing with post attempt...")
            
            # Navigate to target URL if provided
            if target_url:
                self.current_driver.get(target_url)
                time.sleep(3)
            
            # Implementation depends on the specific platform
            # This is a basic structure that would need to be customized
            success = self._post_comment_to_current_page(comment_text)
            
            # Update account usage
            self.account_manager.database.update_account_usage(self.current_account.id, success)
            
            if success:
                self.logger.info("✅ Comment posted successfully!")
            else:
                self.logger.error("❌ Failed to post comment")
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to post comment: {e}")
            return False
    
    def _post_comment_to_current_page(self, comment_text: str) -> bool:
        """
        Post comment to the current page (platform-specific implementation needed)
        """
        # This would need to be implemented based on the specific platform's UI
        # For now, return True as placeholder
        return True
    
    def get_account_rotation_stats(self) -> Dict:
        """Get statistics about account rotation and usage"""
        return {
            'current_account': {
                'username': self.current_account.username if self.current_account else None,
                'posts_today': self.current_account.posts_today if self.current_account else 0,
                'total_posts': self.current_account.total_posts if self.current_account else 0,
                'success_rate': self.current_account.success_rate if self.current_account else 0
            },
            'overall_stats': self.account_manager.get_stats_summary()
        }
    
    def perform_maintenance(self):
        """Perform maintenance on both profile and account systems"""
        self.logger.info("🔧 Performing enhanced profile manager maintenance...")
        
        # Perform account maintenance
        self.account_manager.perform_maintenance()
        
        self.logger.info("✅ Enhanced profile manager maintenance completed")
    
    def cleanup(self):
        """Clean up resources"""
        if self.current_driver:
            try:
                self.current_driver.quit()
            except:
                pass
            self.current_driver = None

# Example usage
if __name__ == "__main__":
    try:
        # Initialize enhanced profile manager
        manager = EnhancedProfileManager()
        
        # Create fresh account with profile
        account, driver = manager.create_fresh_account_with_profile("cmc")
        print(f"✅ Created account: {account.username} ({account.email_alias})")
        
        # Attempt to login
        if manager.login_to_platform("cmc"):
            print("✅ Successfully logged in!")
        else:
            print("❌ Login failed")
        
        # Get stats
        stats = manager.get_account_rotation_stats()
        print(f"📊 Stats: {stats}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'manager' in locals():
            manager.cleanup() 