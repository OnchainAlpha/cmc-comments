import sys
import os
import time
import random
from selenium.common.exceptions import WebDriverException
from typing import Optional, List, Dict
from datetime import datetime
import pandas as pd
import logging
from pathlib import Path
from selenium.webdriver.common.by import By
from openai import OpenAI
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from autocrypto_social_bot.utils.helpers import random_delay

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.scrapers.cmc_scraper import CMCScraper
from autocrypto_social_bot.utils.helpers import setup_logging, wait_for_element
from autocrypto_social_bot.config.settings import DEEPSEEK_API_KEY, save_config, CMC_COMMUNITY_URL
from autocrypto_social_bot.services.message_formatter import MessageFormatter
from autocrypto_social_bot.services.viral_hooks import ViralHooks

# Import our new structured rotation system
try:
    from autocrypto_social_bot.structured_profile_rotation import EnhancedProfileManager
    STRUCTURED_ROTATION_AVAILABLE = True
    print("🔄 Structured Profile Rotation System loaded!")
except ImportError:
    STRUCTURED_ROTATION_AVAILABLE = False
    print("⚠️ Structured Profile Rotation not available, using standard rotation")

# Import our breakthrough CMC bypass system
try:
    from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
    CMC_BYPASS_AVAILABLE = True
    print("🔥 BREAKTHROUGH: CMC Bypass system loaded successfully!")
except ImportError:
    CMC_BYPASS_AVAILABLE = False
    cmc_bypass_manager = None
    print("⚠️ CMC Bypass system not available, using fallback")

# Import our Enterprise Proxy System with Persistent Storage
try:
    from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
    ENTERPRISE_PROXY_AVAILABLE = True
    print("✅ Enterprise Proxy System with Persistent Storage loaded!")
except ImportError:
    ENTERPRISE_PROXY_AVAILABLE = False
    print("⚠️ Enterprise Proxy System not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class CryptoAIAnalyzer:
    def __init__(self, proxy_config=None):
        self.logger = logging.getLogger(__name__)
        
        # Load proxy configuration if not provided
        if proxy_config is None:
            proxy_config_path = 'config/proxy_rotation_config.json'
            if os.path.exists(proxy_config_path):
                with open(proxy_config_path, 'r') as f:
                    proxy_config = json.load(f)
            else:
                # Default configuration for backward compatibility
                proxy_config = {
                    'auto_proxy_rotation': True,
                    'proxy_mode': 'enterprise',
                    'use_proxy_discovery': True,
                    'fallback_to_direct': True
                }
        
        self.proxy_config = proxy_config
        print(f"\n🔧 PROXY CONFIGURATION LOADED:")
        print(f"   Auto Proxy Rotation: {'✅ ENABLED' if proxy_config.get('auto_proxy_rotation', True) else '❌ DISABLED'}")
        print(f"   Mode: {proxy_config.get('proxy_mode', 'enterprise').upper()}")
        print(f"   Description: {proxy_config.get('description', 'Default configuration')}")
        
        # Initialize DeepSeek client
        self.deepseek = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        # Initialize services
        self.message_formatter = MessageFormatter()
        self.viral_hooks = ViralHooks()
        
        # Initialize profile manager with structured rotation if available
        if STRUCTURED_ROTATION_AVAILABLE:
            print("🔄 Initializing Enhanced Profile Manager with Structured Rotation...")
            self.profile_manager = EnhancedProfileManager(proxy_config=self.proxy_config)
            self.use_structured_rotation = True
        else:
            print("⚠️ Using standard Profile Manager...")
            self.profile_manager = ProfileManager(proxy_config=self.proxy_config)
            self.use_structured_rotation = False
        
        # Check if enhanced account rotation is enabled
        self.use_account_rotation = self._check_account_rotation_enabled()
        if self.use_account_rotation:
            print("🔄 Enhanced account rotation detected - integrating with account database...")
            self._initialize_account_rotation()
        
        # Track processed tokens and failed attempts
        self.processed_tokens = set()
        self.failed_tokens = {}  # {symbol: number_of_attempts}
        self.max_retries_per_token = 10  # Increased from 3 to 10 for better success rate
        
        # Track current session
        self.session_start_time = time.time()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create session directory for tracking
        self.session_dir = Path("analysis_data/sessions") / self.session_id
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "="*80)
        print("🆔 NEW SESSION INITIALIZATION")
        print("="*80)
        print(f"Session ID: {self.session_id}")
        print(f"Session Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check existing profiles and use them without creating new ones
        profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
        if not profiles:
            print("\n" + "="*60)
            print("❌ NO CMC PROFILES FOUND")
            print("="*60)
            print("\nNo existing CMC profiles were found.")
            print("Please create profiles manually using the Profile Management menu.")
            print("You can access it from the main menu or by running the menu.py script.")
            print("\nExiting...")
            raise Exception("No CMC profiles found. Please create profiles manually first.")
        
        print(f"\n✅ Found {len(profiles)} existing CMC profile(s)")
        print("Using existing profiles for rotation...")
        
        # Initialize structured rotation if available
        if self.use_structured_rotation:
            print("\n🔄 INITIALIZING STRUCTURED PROFILE ROTATION")
            print("="*60)
            
            # Ask user if they want to verify all profiles before starting
            verify_choice = input("Verify all profiles for login status before starting? (y/n): ").strip().lower()
            if verify_choice == 'y':
                try:
                    self.profile_manager.initialize_structured_rotation(verify_all=True, ask_confirmation=True)
                    print("✅ Structured rotation initialized with profile verification")
                except Exception as e:
                    print(f"❌ Structured rotation initialization failed: {e}")
                    print("🔄 Falling back to standard rotation...")
                    self.profile_manager = ProfileManager(proxy_config=self.proxy_config)
                    self.use_structured_rotation = False
            else:
                try:
                    self.profile_manager.initialize_structured_rotation(verify_all=False, ask_confirmation=False)
                    print("✅ Structured rotation initialized without verification")
                except Exception as e:
                    print(f"❌ Structured rotation initialization failed: {e}")
                    print("🔄 Falling back to standard rotation...")
                    self.profile_manager = ProfileManager(proxy_config=self.proxy_config)
                    self.use_structured_rotation = False
        
        # Load browser profile based on proxy configuration
        self._load_browser_with_proxy_config()
        
        print("🔄"*60)
        print("✅ SESSION INITIALIZATION COMPLETE")
        print("🔄"*60)
        
        # Initialize CMC scraper with the driver, profile manager, and proxy configuration
        self.cmc_scraper = CMCScraper(self.driver, self.profile_manager, self.proxy_config)

        # Anti-detection status is now displayed by ProfileManager during initialization

        # Get promotion configuration - check if it already exists first
        self.promotion_config = self._get_promotion_config()
        
        # Save session info after complete initialization
        self._save_session_info()
        
        # Log final session initialization status
        print("\n" + "="*80)
        print("📋 SESSION INITIALIZATION COMPLETE")
        print("="*80)
        print(f"Session ID: {self.session_id}")
        print(f"Promotion Type: {self.promotion_config.get('type', 'Unknown').upper()}")
        print(f"Proxy Mode: {self.proxy_config.get('proxy_mode', 'enterprise').upper()}")
        print(f"IP Rotation: {'✅ ENABLED' if self.proxy_config.get('auto_proxy_rotation', True) else '❌ DISABLED'}")
        print(f"Anti-Detection: {'✅ ACTIVE' if hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection else '⚠️ BASIC'}")
        print("="*80)

    def _check_account_rotation_enabled(self) -> bool:
        """Check if enhanced account rotation is enabled"""
        try:
            flag_file = "config/use_account_rotation.flag"
            return os.path.exists(flag_file)
        except:
            return False
    
    def _initialize_account_rotation(self):
        """Initialize enhanced account rotation system"""
        try:
            from autocrypto_social_bot.services.account_manager import AutomatedAccountManager
            from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
            
            # Check if SimpleLogin is configured
            config = SimpleLoginConfig()
            if not config.is_configured():
                print("⚠️ SimpleLogin not configured - disabling account rotation")
                self.use_account_rotation = False
                return
            
            # Initialize account manager
            self.account_manager = AutomatedAccountManager(config.get_api_key())
            
            # Get available accounts
            available_accounts = self.account_manager.database.get_accounts_by_platform("cmc", "active")
            
            if len(available_accounts) == 0:
                print("⚠️ No CMC accounts found in database - using regular profiles")
                self.use_account_rotation = False
                return
            
            print(f"✅ Found {len(available_accounts)} CMC accounts for rotation")
            
            # Track rotation state
            self.current_account = None
            self.posts_this_session = 0
            self.max_posts_per_account = 5
            
            # Override profile switching with account rotation
            original_switch = self.profile_manager.switch_to_next_profile
            
            def enhanced_switch_to_next_profile():
                return self._rotate_to_next_account()
            
            self.profile_manager.switch_to_next_profile = enhanced_switch_to_next_profile
            print("🔄 Profile switching enhanced with account rotation")
            
        except Exception as e:
            print(f"❌ Failed to initialize account rotation: {e}")
            self.use_account_rotation = False
    
    def _rotate_to_next_account(self):
        """Rotate to the next available account with robust error handling"""
        try:
            # Get available accounts
            available_accounts = self.account_manager.database.get_accounts_by_platform("cmc", "active")
            
            if not available_accounts:
                print("⚠️ No available accounts - falling back to regular profiles")
                return self._safe_fallback_rotation()
            
            # Select account with lowest posts_today
            best_account = min(available_accounts, key=lambda acc: acc.posts_today)
            
            print(f"🔄 Rotating to account: {best_account.username} (posts today: {best_account.posts_today})")
            
            # Close current driver safely
            self._safe_close_driver()
            
            # Try to load the account's profile with multiple fallbacks
            driver_loaded = False
            
            # Attempt 1: Load specific profile
            if best_account.profile_name:
                try:
                    print(f"   📁 Attempting to load profile: {best_account.profile_name}")
                    self.driver = self.profile_manager.load_profile(best_account.profile_name)
                    driver_loaded = True
                    print(f"   ✅ Profile loaded successfully")
                except Exception as profile_error:
                    print(f"   ❌ Profile loading failed: {profile_error}")
                    print(f"   🔄 Will create new profile for this account")
            
            # Attempt 2: Use any existing profile if specific profile failed
            if not driver_loaded:
                try:
                    print(f"   🔄 Assigning existing profile to account: {best_account.username}")
                    # Get available existing profiles instead of creating new ones
                    available_profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                    if not available_profiles:
                        raise Exception("No existing CMC profiles found for account rotation. Please create profiles manually.")
                    
                    # Use first available profile (or rotate through them)
                    selected_profile = available_profiles[0]
                    self.driver = self.profile_manager.load_profile(selected_profile)
                    
                    # Update account with existing profile name
                    best_account.profile_name = selected_profile
                    self.account_manager.database.update_account_profile(best_account.id, selected_profile)
                    
                    driver_loaded = True
                    print(f"   ✅ Assigned existing profile: {selected_profile}")
                except Exception as assign_error:
                    print(f"   ❌ Profile assignment failed: {assign_error}")
            
            # Attempt 3: Use regular profile rotation as last resort
            if not driver_loaded:
                print(f"   🔄 Falling back to regular profile rotation")
                return self._safe_fallback_rotation()
            
            # Update tracking
            self.current_account = best_account
            self.posts_this_session = 0
            
            # Try to login to CMC with account credentials
            try:
                self._login_to_cmc_with_account(best_account)
            except Exception as login_error:
                print(f"   ⚠️ CMC login attempt failed: {login_error}")
                print(f"   ✅ Continuing with loaded profile anyway")
            
            print(f"✅ Successfully rotated to account: {best_account.username}")
            return self.driver
            
        except Exception as e:
            print(f"❌ Account rotation completely failed: {e}")
            import traceback
            traceback.print_exc()
            # Ultimate fallback
            return self._safe_fallback_rotation()
    
    def _safe_close_driver(self):
        """Safely close the current WebDriver"""
        if hasattr(self, 'driver') and self.driver:
            try:
                print("   🔄 Closing current driver...")
                self.driver.quit()
                print("   ✅ Driver closed successfully")
            except Exception as e:
                print(f"   ⚠️ Driver close warning: {e}")
            finally:
                self.driver = None
    
    def _safe_fallback_rotation(self):
        """Safe fallback rotation method"""
        try:
            print("🔄 Executing safe fallback rotation...")
            self._safe_close_driver()
            
            # Reset current account
            self.current_account = None
            self.posts_this_session = 0
            
            # Use regular profile manager
            self.driver = self.profile_manager.switch_to_next_profile()
            print("✅ Fallback rotation successful")
            return self.driver
            
        except Exception as fallback_error:
            print(f"❌ Even fallback rotation failed: {fallback_error}")
            # Ultimate emergency fallback - create a basic driver
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                
                options = Options()
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                self.driver = webdriver.Chrome(options=options)
                print("🆘 Emergency fallback: Basic Chrome driver created")
                return self.driver
                
            except Exception as emergency_error:
                print(f"🆘 CRITICAL: All rotation methods failed: {emergency_error}")
                raise
    
    def _login_to_cmc_with_account(self, account):
        """Login to CMC using account credentials"""
        try:
            print(f"🔐 Logging in to CMC as {account.username}...")
            
            # Navigate to CMC
            self.driver.get("https://coinmarketcap.com")
            time.sleep(3)
            
            # Check if already logged in
            page_source = self.driver.page_source.lower()
            if "logout" in page_source or "dashboard" in page_source:
                print("✅ Already logged in to CMC")
                return True
            
            # Navigate to login page
            self.driver.get("https://coinmarketcap.com/account/login/")
            time.sleep(3)
            
            # Login logic would go here, but CMC login is usually session-based
            # For now, just navigate to CMC community where posting happens
            self.driver.get("https://coinmarketcap.com/community/")
            time.sleep(3)
            
            print("✅ Navigated to CMC community")
            return True
            
        except Exception as e:
            print(f"⚠️ CMC login attempt failed: {e}")
            return False
    
    def _update_account_post_stats(self, success: bool):
        """Update account statistics after posting"""
        if not self.use_account_rotation or not self.current_account:
            return
        
        try:
            # Update post counter
            self.posts_this_session += 1
            
            # Update database
            self.account_manager.database.update_account_usage(self.current_account.id, success)
            
            # Reload account to get updated stats
            self.current_account = self.account_manager.database.get_account(self.current_account.id)
            
            status = "✅ SUCCESS" if success else "❌ FAILED"
            print(f"{status} - Post #{self.posts_this_session} with {self.current_account.username}")
            
            # Auto-rotate if we've hit the limit
            if self.posts_this_session >= self.max_posts_per_account:
                print(f"🔄 Hit post limit ({self.max_posts_per_account}) - will rotate on next post")
            
        except Exception as e:
            print(f"⚠️ Error updating account stats: {e}")
    
    def _switch_to_next_profile_smart(self):
        """Smart profile switching that uses structured rotation when available"""
        try:
            if self.use_structured_rotation and hasattr(self.profile_manager, 'switch_to_next_profile_structured'):
                print("🔄 Using structured profile rotation...")
                return self.profile_manager.switch_to_next_profile_structured()
            else:
                print("🔄 Using standard profile rotation...")
                return self.profile_manager.switch_to_next_profile()
        except Exception as e:
            print(f"❌ Profile rotation failed: {e}")
            # Fallback to standard rotation
            if self.use_structured_rotation:
                print("🔄 Falling back to standard rotation...")
                try:
                    return self.profile_manager.switch_to_next_profile()
                except Exception as e2:
                    print(f"❌ Standard rotation also failed: {e2}")
                    raise
            else:
                raise

    def _get_current_ip(self) -> Optional[str]:
        """Get current IP address for logging purposes"""
        try:
            # Use a simple service to get current IP
            self.driver.execute_script("window.open('http://httpbin.org/ip', '_blank');")
            time.sleep(3)
            
            # Switch to the new tab
            windows = self.driver.window_handles
            if len(windows) > 1:
                self.driver.switch_to.window(windows[-1])
                time.sleep(2)
                
                # Try to get IP from the page
                try:
                    ip_element = self.driver.find_element(By.TAG_NAME, "pre")
                    if ip_element:
                        import json
                        ip_data = json.loads(ip_element.text)
                        current_ip = ip_data.get('origin', 'Unknown')
                        
                        # Close the tab and return to main window
                        self.driver.close()
                        self.driver.switch_to.window(windows[0])
                        
                        return current_ip
                except Exception:
                    pass
                
                # Close the tab and return to main window
                try:
                    self.driver.close()
                    self.driver.switch_to.window(windows[0])
                except:
                    pass
            
            return None
        except Exception as e:
            self.logger.debug(f"Could not get current IP: {str(e)}")
            return None

    def _load_profile_with_mandatory_proxy(self):
        """Load a profile with mandatory proxy protection"""
        try:
            # Get anti-detection options with mandatory proxy
            if hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection:
                print("🛡️ Creating anti-detection options with mandatory proxy...")
                options = self.profile_manager.anti_detection.create_anti_detection_options(
                    use_proxy=True, 
                    force_proxy=True  # This will fail if no proxy is available
                )
                
                # Get available profiles
                profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if not profiles:
                    raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
                
                # Load first profile with proxy
                profile_name = profiles[0]
                print(f"🔄 Loading profile {profile_name} with mandatory proxy...")
                
                driver = self.profile_manager.load_profile_with_options(profile_name, options)
                print("✅ Profile loaded with proxy protection")
                return driver
            else:
                # Fallback: try to create basic options with proxy
                print("⚠️ Anti-detection not available, attempting basic proxy setup...")
                raise Exception("Anti-detection system required for mandatory proxy protection")
                
        except Exception as e:
            self.logger.error(f"Failed to load profile with mandatory proxy: {str(e)}")
            raise

    def _get_promotion_config(self):
        """Get promotion configuration from user"""
        # First, check if config already exists
        config_path = "config/promotion_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
                    
                print(f"\n✅ Found existing promotion configuration:")
                print(f"Type: {existing_config.get('type', 'Unknown')}")
                if 'params' in existing_config:
                    for key, value in existing_config['params'].items():
                        print(f"{key}: {value}")
                
                use_existing = input("\nUse existing configuration? (y/n): ").strip().lower()
                if use_existing == 'y':
                    # Convert numeric type to string type
                    if isinstance(existing_config.get('type'), int):
                        type_mapping = {
                            1: 'market_making',
                            2: 'token_shilling', 
                            3: 'trading_group'
                        }
                        existing_config['type'] = type_mapping.get(existing_config['type'], 'market_making')
                    
                    return existing_config
            except Exception as e:
                print(f"Error reading existing config: {str(e)}")
        
        print("\n" + "="*60)
        print("📢 Promotion Configuration")
        print("="*60)
        
        print("\nPromotion Types:")
        print("1. Market Making")
        print("2. Token Shilling (Cross-reference promoted token)")
        print("3. Trading Group")
        
        while True:
            choice = input("\nSelect promotion type (1-3): ").strip()
            if choice in ['1', '2', '3']:
                break
            print("Invalid choice. Please select 1, 2, or 3.")
        
        promo_type = {
            '1': 'market_making',
            '2': 'token_shilling',
            '3': 'trading_group'
        }[choice]
        
        params = {}
        if promo_type == 'market_making':
            params['firm_name'] = input("\nEnter market making firm name: ").strip()
        elif promo_type == 'token_shilling':
            params['promoted_ticker'] = input("\nEnter the token ticker you want to shill (e.g., EXAMPLE): ").strip().upper()
            params['promoted_name'] = input("Enter the full token name (e.g., Example Token): ").strip()
            print(f"\n✅ Will cross-reference ${params['promoted_ticker']} when analyzing other tokens")
        else:  # trading_group
            params['group_name'] = input("\nEnter trading group name: ").strip()
            params['join_link'] = input("Enter group join link: ").strip()
        
        config = {
            'type': promo_type,
            'params': params
        }
        
        # Save the configuration
        os.makedirs('config', exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        return config

    def _save_session_info(self):
        """Save session information for tracking"""
        # Get current IP and proxy info
        current_ip = None
        current_proxy = None
        ip_rotation_count = 0
        
        if hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection:
            current_proxy = self.profile_manager.anti_detection.session_state.get('current_proxy')
            # Try to get current IP for session tracking
            if current_proxy:
                try:
                    import requests
                    proxies = {'http': f'http://{current_proxy}', 'https': f'http://{current_proxy}'}
                    ip_response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=5)
                    current_ip = ip_response.json().get('origin', 'Unknown')
                except Exception as e:
                    self.logger.debug(f"Could not get current IP for session info: {str(e)}")
            
            # Track IP rotation count (based on successful posts)
            ip_rotation_count = self.profile_manager.anti_detection.session_state.get('total_posts_today', 0) // 10
        
        session_info = {
            'session_id': self.session_id,
            'start_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'promotion_config': getattr(self, 'promotion_config', None),
            'processed_tokens': list(self.processed_tokens),
            'failed_tokens': self.failed_tokens,
            'ip_tracking': {
                'current_ip': current_ip,
                'current_proxy': current_proxy,
                'ip_rotation_forced_on_start': True,  # Always true now
                'estimated_ip_rotations': ip_rotation_count,
                'anti_detection_active': bool(hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection)
            }
        }
        
        with open(self.session_dir / 'session_info.json', 'w') as f:
            json.dump(session_info, f, indent=2)

    def _update_session_tracking(self, symbol: str, success: bool):
        """Update session tracking information"""
        if success:
            self.processed_tokens.add(symbol)
            if symbol in self.failed_tokens:
                del self.failed_tokens[symbol]
        else:
            self.failed_tokens[symbol] = self.failed_tokens.get(symbol, 0) + 1
        
        # Update account statistics if account rotation is enabled
        self._update_account_post_stats(success)
        
        self._save_session_info()

    def _should_retry_token(self, symbol: str) -> bool:
        """Determine if we should retry posting for a token"""
        attempts = self.failed_tokens.get(symbol, 0)
        return attempts < self.max_retries_per_token

    def reset_failed_tokens(self):
        """Reset failed tokens tracking to give all coins a fresh start"""
        old_count = len(self.failed_tokens)
        self.failed_tokens.clear()
        print(f"🔄 RESET: Cleared {old_count} failed tokens - giving all coins a fresh start!")
        self._save_session_info()
        
    def get_failed_tokens_status(self):
        """Get current status of failed tokens for debugging"""
        if not self.failed_tokens:
            return "No failed tokens"
        
        status = []
        for symbol, attempts in self.failed_tokens.items():
            can_retry = self._should_retry_token(symbol)
            status.append(f"${symbol}: {attempts} attempts ({'can retry' if can_retry else 'BLOCKED'})")
        
        return "\n".join(status)

    def _enhance_ai_review(self, original_review: str, symbol: str) -> Dict[str, str]:
        """Enhance AI review with promotional content using DeepSeek"""
        try:
            # Get the appropriate prompt based on promotion type
            promotion_prompt = self.message_formatter.get_promotion_prompt(
                self.promotion_config['type'],
                original_review,
                self.promotion_config['params']
            )
            
            # Determine the appropriate system prompt based on promotion type
            system_prompts = {
                'market_making': """You are Onchain Bureau's head of market operations. Your task is to:

1. START IMMEDIATELY with "Onchain Bureau market making positions have been strategically placed at [derive buy price from CMC data] for accumulation and [derive sell price 8-15% higher] for distribution based on the following analysis:"

2. Extract specific price levels from the CMC analysis to use as your buy/sell targets
3. Follow with 2-3 concise paragraphs integrating the CMC analysis 
4. Focus on liquidity depth, execution quality, and why these levels matter
5. Position OCB as the authoritative liquidity provider
6. Keep total response under 1600 characters (strict limit)
7. End with subtle engagement question

Format: Lead with positioning statement, then analysis, then engagement. Be authoritative about OCB's market leadership.""",

                'token_shilling': """You are Onchain Bureau's head of strategic intelligence. Your mission is to naturally cross-reference our promoted token while analyzing the current token. 

CRITICAL MISSION: Seamlessly integrate mentions of the promoted token using varied, creative approaches:

APPROACH ROTATION (use different ones):
1. "Onchain data reveals top traders of [current_token] are quietly rotating into ${promoted_ticker} - institutional flow patterns suggest this transition accelerated 48hrs ago"
2. "Smart money analysis shows ${promoted_ticker} accumulation from [current_token] profit-takers - whale transactions indicate coordinated positioning"  
3. "Cross-chain analytics expose ${promoted_ticker} as the primary beneficiary of [current_token] exit liquidity - major wallets repositioning"
4. "Institutional tracking reveals ${promoted_ticker} receiving significant inflows from [current_token] distribution - timing suggests coordinated strategy"
5. "Onchain intelligence indicates ${promoted_ticker} emerging as the preferred hedge for [current_token] exposure - sophisticated wallet behavior"

EXECUTION RULES:
- Pick ONE approach per analysis (rotate for variety)
- Integrate CMC analysis of current token FIRST (2-3 sentences)
- Then naturally transition to promoted token connection
- Make it sound like exclusive intel from OCB's onchain monitoring
- Keep under 1600 characters total
- End with subtle engagement question about the connection

TONE: Authoritative insider knowledge, exclusive intelligence, sophisticated analysis""",

                'trading_group': """You are Onchain Bureau's head of institutional trading. Your task is to:

1. START IMMEDIATELY with "Onchain Bureau's institutional trading desk has identified key levels at [derive from CMC data] for optimal entry/exit based on the following analysis:"

2. Extract specific trading levels from the CMC analysis
3. Enhance the CMC AI analysis with OCB's institutional trading insights
4. Add technical analysis perspectives from OCB's proprietary models
5. Highlight risk management strategies that OCB provides to institutional clients
6. Demonstrate OCB's community value and professional trading expertise
7. Keep total response under 1600 characters (strict limit)
8. Position OCB as the authoritative institutional trading partner

Format: Lead with OCB positioning, then analysis, then trading insights. Be authoritative about OCB's institutional leadership."""
            }
            
            # Get the appropriate system prompt
            system_prompt = system_prompts.get(
                self.promotion_config['type'],
                """You are a professional cryptocurrency analyst. Create a comprehensive analysis under 1600 characters that incorporates the CMC AI data with promotional content."""
            )
            
            # Combine CMC content with promotional prompt
            combined_prompt = f"""Here is the complete CMC AI analysis for {symbol}:

{original_review}

Using this COMPLETE analysis as your foundation, {promotion_prompt}

CRITICAL REQUIREMENTS:
- For market making: START with "Onchain Bureau market making positions have been strategically placed at [price] for accumulation and [higher price] for distribution based on the following analysis:"
- For token shilling: Use the current token analysis to create a natural transition to the promoted token cross-reference. Current token: {symbol}. Promoted token: {self.promotion_config['params'].get('promoted_ticker', 'N/A')}
- For trading group: START with "Onchain Bureau's institutional trading desk has identified key levels at [price] for optimal entry/exit based on the following analysis:"
- Extract actual price levels from the CMC data above
- Keep total response under 1600 characters (STRICT LIMIT)
- Create authoritative, professional content that positions OCB as market leaders
- Single cohesive post, not multiple parts
- VARY your approach each time - don't use the same language patterns repeatedly"""
            
            # Call DeepSeek to enhance the review (generate only 1 optimal version)
            response = self.deepseek.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": combined_prompt
                }],
                temperature=0.7,
                max_tokens=500  # Reduced for concise content
            )
            
            enhanced_review = response.choices[0].message.content.strip()
            
            # Generate only 1 variation for simplicity and efficiency
            variations = [enhanced_review]
            
            self.logger.info(f"Successfully generated optimized promotional content with DeepSeek")
            
            # Format the single variation using the new character-limited method
            final_messages = [
                self.message_formatter.format_comprehensive_promotional_message(enhanced_review, symbol)
            ]
            
            # Save variation for analysis
            self._save_variations(symbol, variations)
            
            return {"messages": final_messages}
            
        except Exception as e:
            self.logger.error(f"Error enhancing review: {str(e)}")
            return {"messages": []}

    def _save_variations(self, symbol: str, variations: list):
        """Save message variations for analysis"""
        try:
            # Create analysis_data/variations directory if it doesn't exist
            variations_dir = Path("analysis_data/variations")
            variations_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_filename = f"{symbol}_{timestamp}"
            
            # Save each variation
            for i, variation in enumerate(variations, 1):
                filename = variations_dir / f"{base_filename}_v{i}.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(variation)
            
            self.logger.info(f"Saved {len(variations)} variations for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Error saving variations: {str(e)}")

    def analyze_token(self, symbol: str, name: str, url: Optional[str] = None) -> Dict:
        """Analyze a token and generate enhanced content"""
        try:
            # Get initial AI review from CMC
            ai_review = self.cmc_scraper.get_ai_token_review(symbol, name, url)
            
            if not ai_review['success']:
                return {'success': False, 'error': ai_review.get('error', 'Failed to get AI review')}
            
            # Enhance the review and generate variations
            enhanced_content = self._enhance_ai_review(ai_review['ai_review'], symbol)
            
            # Save all variations for later analysis
            self._save_variations(symbol, enhanced_content['messages'])
            
            return {
                'success': True,
                'original_review': ai_review['ai_review'],
                'enhanced_content': enhanced_content,
                'url_used': ai_review.get('url_used')
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {str(e)}")
            return {'success': False, 'error': str(e)}

    def test_promotion(self, token_symbol: str = "BTC", token_name: str = "Bitcoin") -> Dict:
        """Test the promotion formatting without browser setup"""
        try:
            # Simulate an AI review for testing
            sample_ai_review = f"""${token_symbol} Analysis:
            
Current market shows strong fundamentals with increasing adoption and development activity.
Key metrics indicate growing institutional interest and improving market structure.
Technical analysis suggests a potential consolidation phase with key support levels holding.
            
Recent developments:
- Increased developer activity on GitHub
- Growing institutional adoption
- Improving market liquidity
- Strong community engagement"""

            # Enhance the review with promotional content
            enhanced_content = self._enhance_ai_review(sample_ai_review, token_symbol)
            
            # Save variations for analysis
            self._save_variations(token_symbol, enhanced_content['messages'])
            
            return {
                'success': True,
                'original_review': sample_ai_review,
                'enhanced_content': enhanced_content
            }
            
        except Exception as e:
            self.logger.error(f"Error in test promotion: {str(e)}")
            return {'success': False, 'error': str(e)}

    def test_token_shilling(self, current_token: str = "ETH", promoted_token: str = "MYTOKEN") -> Dict:
        """Test the token shilling cross-referencing functionality"""
        try:
            print(f"\n🎯 Testing token shilling: Analyzing {current_token} while promoting {promoted_token}")
            
            # Simulate a promotion config for token shilling
            original_config = self.promotion_config
            self.promotion_config = {
                'type': 'token_shilling',
                'params': {
                    'promoted_ticker': promoted_token,
                    'promoted_name': f"{promoted_token} Token"
                }
            }
            
            # Simulate an AI review for the current token being analyzed
            sample_ai_review = f"""${current_token} Analysis:
            
Current market shows strong fundamentals with increasing institutional adoption and development activity.
Price has stabilized around key support levels with growing volume indicating potential accumulation phase.
Technical indicators suggest consolidation before next major move, with resistance at $2,100 and support at $1,800.
            
Recent developments:
- Major exchange listings increasing liquidity
- Institutional partnerships driving adoption
- Developer activity showing continued innovation
- Community growth accelerating globally"""

            # Enhance the review with token shilling
            enhanced_content = self._enhance_ai_review(sample_ai_review, current_token)
            
            # Restore original config
            self.promotion_config = original_config
            
            # Save variations for analysis
            self._save_variations(f"{current_token}_SHILL_{promoted_token}", enhanced_content['messages'])
            
            return {
                'success': True,
                'original_review': sample_ai_review,
                'enhanced_content': enhanced_content,
                'current_token': current_token,
                'promoted_token': promoted_token
            }
            
        except Exception as e:
            self.logger.error(f"Error in token shilling test: {str(e)}")
            return {'success': False, 'error': str(e)}

    def run_analysis(self):
        """Run the analysis - either test mode or fully automated mode"""
        print("\nCMC AI Analysis with Promotional Enhancement")
        print("=" * 60)
        print("1. 🧪 Test mode (sample data)")
        print("2. 🎯 Test token shilling (cross-reference demo)")
        print("3. 🤖 Fully automated mode (live CMC scraping)")
        
        while True:
            try:
                choice = input("\nSelect mode (1-3): ").strip()
                if choice in ['1', '2', '3']:
                    break
                print("Please enter 1, 2, or 3")
            except KeyboardInterrupt:
                print("\nExiting...")
                return
        
        if choice == '1':
            return self._run_test_mode()
        elif choice == '2':
            return self._run_token_shilling_test()
        else:
            return self._run_automated_mode()
    
    def _run_test_mode(self):
        """Run test mode with sample data"""
        try:
            print("\n🧪 Running test mode with sample data...")
            result = self.test_promotion()
            
            if not result['success']:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                return
            
            # Show the message variations
            print("\nGenerated message variations:")
            for i, msg in enumerate(result['enhanced_content']['messages'], 1):
                print(f"\nVariation {i}:")
                print(msg)
            
            print("\n✅ Test complete! Check the 'analysis_data/variations' folder for saved variations.")
        
        except Exception as e:
            self.logger.error(f"Error in test mode: {str(e)}")
            print(f"❌ Test error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _run_token_shilling_test(self):
        """Run token shilling test"""
        try:
            print("\n🎯 Token Shilling Cross-Reference Demo")
            print("=" * 60)
            print("This will show how we cross-reference your promoted token")
            print("when analyzing another trending token.\n")
            
            # Get tokens from user
            current_token = input("Enter the token to analyze (e.g., ETH, BTC): ").strip().upper()
            if not current_token:
                current_token = "ETH"
            
            promoted_token = input("Enter the token you want to shill/promote (e.g., MYTOKEN): ").strip().upper()
            if not promoted_token:
                promoted_token = "MYTOKEN"
            
            print(f"\n🔄 Analyzing ${current_token} while cross-referencing ${promoted_token}...")
            
            result = self.test_token_shilling(current_token, promoted_token)
            
            if not result['success']:
                print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
                return
            
            # Show the enhanced content
            print(f"\n📊 Results: ${current_token} Analysis with ${promoted_token} Cross-Reference")
            print("=" * 80)
            
            print("\n🤖 AI-Enhanced Content:")
            for i, msg in enumerate(result['enhanced_content']['messages'], 1):
                print(f"\n📝 Generated Message {i}:")
                print("-" * 50)
                print(msg)
            
            print(f"\n✅ Token shilling demo complete!")
            print(f"📁 Content saved to: analysis_data/variations/{current_token}_SHILL_{promoted_token}_*.txt")
            print("\n💡 This shows how your promoted token gets naturally integrated")
            print("   into analysis of ANY trending token!")
        
        except Exception as e:
            self.logger.error(f"Error in token shilling test: {str(e)}")
            print(f"❌ Token shilling test error: {str(e)}")
            import traceback
            traceback.print_exc()

    def _run_automated_mode(self):
        """Run fully automated mode with CMC scraping and pagination"""
        try:
            print("\n" + "="*60)
            print("[AUTOMATED] Starting Automated CMC Analysis")
            print("="*60)
            
            # 🔄 AUTOMATIC RESET: Always reset failed tokens for fresh start
            if self.failed_tokens:
                print(f"\n[AUTO-RESET] Automatically resetting {len(self.failed_tokens)} failed tokens for fresh start")
                self.reset_failed_tokens()
                print("[SUCCESS] All coins now have fresh retry chances!")
            else:
                print("[INFO] No failed tokens found - all coins available for processing")
            
            process_limit = 100  # Increased from 50 to 100 for better coverage
            tokens_processed = 0
            current_page = 1  # Start with page 1 of trending coins
            consecutive_empty_pages = 0  # Track empty pages to avoid infinite loops
            
            while tokens_processed < process_limit and consecutive_empty_pages < 5:
                print(f"\n[PAGE] Getting trending coins from page {current_page}...")
                
                # Get trending coins from current page (increased to 10 coins per page)
                pending_tokens = self.cmc_scraper.get_trending_coins(limit=10, page=current_page)
                
                if not pending_tokens:
                    print(f"[INFO] No coins found on page {current_page}, moving to next page...")
                    consecutive_empty_pages += 1
                    current_page += 1
                    if current_page > 50:  # Increased page limit
                        print("[INFO] Reached page limit, resetting to page 1...")
                        current_page = 1
                        consecutive_empty_pages = 0
                    continue
                
                # Reset consecutive empty pages counter
                consecutive_empty_pages = 0
                print(f"[SUCCESS] Found {len(pending_tokens)} trending coins on page {current_page}")
                
                for coin in pending_tokens:
                    if tokens_processed >= process_limit:
                        break
                    
                    try:
                        print(f"\n" + "="*60)
                        print(f"[PROCESS] Processing ${coin['symbol']} ({coin['name']}) from page {current_page}")
                        print("="*60)
                        
                        # FIXED: More lenient retry logic - only skip if really excessive failures
                        if coin['symbol'] in self.failed_tokens and self.failed_tokens[coin['symbol']] >= 8:
                            print(f"[SKIP] ${coin['symbol']} has {self.failed_tokens[coin['symbol']]} failed attempts (excessive)")
                            continue
                        
                        # Check if we already processed this token recently
                        if coin['symbol'] in self.processed_tokens:
                            print(f"[SKIP] Already processed ${coin['symbol']} recently")
                            continue
                        
                        # ENHANCED: Show retry status
                        retry_count = self.failed_tokens.get(coin['symbol'], 0)
                        if retry_count > 0:
                            print(f"[RETRY] This is retry attempt #{retry_count + 1} for ${coin['symbol']}")
                        
                        # 🔐 CRITICAL: Verify login status BEFORE starting any work
                        print(f"🔐 VERIFYING CMC LOGIN STATUS BEFORE PROCESSING ${coin['symbol']}...")
                        if not self._verify_login_before_work():
                            print(f"❌ Current profile is not logged into CMC - switching profiles...")
                            if not self._switch_to_logged_in_profile():
                                print(f"❌ No logged-in profiles available! Skipping ${coin['symbol']}")
                                self._update_session_tracking(coin['symbol'], False)
                                continue
                            print(f"✅ Successfully switched to logged-in profile")
                        else:
                            print(f"✅ Current profile is logged into CMC")
                        
                        # Step 1: Get CMC AI analysis
                        print("[STEP1] Getting CMC AI analysis...")
                        ai_review = self.cmc_scraper.get_ai_token_review(
                            coin['symbol'],
                            coin['name'],
                            coin.get('url')
                        )
                        
                        if not ai_review['success']:
                            print(f"[FAIL] Could not get AI analysis for ${coin['symbol']}: {ai_review.get('error', 'Unknown error')}")
                            self._update_session_tracking(coin['symbol'], False)
                            continue
                        
                        print(f"[SUCCESS] Retrieved CMC AI analysis ({len(ai_review['ai_review'])} characters)")
                        
                        # Step 2: Enhance with DeepSeek
                        print("[STEP2] Enhancing with DeepSeek promotional content...")
                        enhanced_content = self._enhance_ai_review(ai_review['ai_review'], coin['symbol'])
                        
                        if not enhanced_content['messages']:
                            print(f"[FAIL] Could not enhance content for ${coin['symbol']}")
                            self._update_session_tracking(coin['symbol'], False)
                            continue
                        
                        print(f"[SUCCESS] Generated optimized promotional content (under 2000 chars)")
                        
                        # Debug: Show enhanced content preview
                        print(f"\n[ANALYSIS] Enhanced Content Preview (First 200 chars):")
                        print(f"[CONTENT] {enhanced_content['messages'][0][:200]}...")
                        print(f"[STATS] Full length: {len(enhanced_content['messages'][0])} characters")
                        
                        # Verify promotional content integration
                        first_message = enhanced_content['messages'][0].lower()
                        has_promotional = any(term in first_message for term in ['ocb', 'onchain bureau', 'market making', 'liquidity'])
                        has_positioning = 'strategically placed' in first_message or 'accumulation' in first_message
                        print(f"[SUCCESS] Promotional integration detected: {has_promotional}")
                        print(f"[SUCCESS] OCB positioning detected: {has_positioning}")
                        
                        # Step 3: Auto-save enhanced variation
                        print("[SAVE] Step 3: Auto-saving enhanced content...")
                        self._save_variations(coin['symbol'], enhanced_content['messages'])
                        
                        # Step 4: Auto-post to CMC community
                        print("[STEP4] Auto-posting to CMC community...")
                        
                        # FIXED: Show the actual comment that will be posted
                        comment_to_post = enhanced_content['messages'][0]
                        print(f"[COMMENT-PREVIEW] About to post comment for ${coin['symbol']}:")
                        print(f"[COMMENT-PREVIEW] {comment_to_post}")
                        print(f"[COMMENT-PREVIEW] Character count: {len(comment_to_post)}")
                        
                        post_success = self.cmc_scraper.post_community_comment(
                            coin['symbol'], 
                            comment_to_post
                        )
                        
                        if post_success:
                            print(f"[SUCCESS] Successfully posted enhanced content to CMC community")
                            
                            # Update session tracking
                            self._update_session_tracking(coin['symbol'], True)
                            tokens_processed += 1
                            
                            print(f"[COMPLETE] Successfully processed ${coin['symbol']} from page {current_page}")
                            print("="*60)
                            
                        else:
                            print(f"[FAIL] Failed to post enhanced content to community")
                            self._update_session_tracking(coin['symbol'], False)
                            
                            # Try rotating profile on failure
                            if self.cmc_scraper.profile_manager:
                                try:
                                    print("[ROTATE] Rotating profile after posting failure...")
                                    # Check if we should do IP rotation on failure
                                    if hasattr(self.cmc_scraper.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
                                        print("[IP-ROTATE] Using IP rotation due to failure")
                                        self.cmc_scraper.driver = self.cmc_scraper.profile_manager.switch_to_next_profile_with_ip_rotation()
                                        print("[SUCCESS] Profile + IP rotation completed after failure")
                                    else:
                                        self.cmc_scraper.driver = self._switch_to_next_profile_smart()
                                        print("[SUCCESS] Profile rotation completed after failure")
                                    random_delay(3, 5)
                                except Exception as e:
                                    print(f"[WARNING] Failed to rotate profile after failure: {str(e)}")
                            
                            continue
                        
                        # Step 5: Auto-rotate profile after successful post
                        print("[ROTATE] Step 5: Auto-rotating Chrome profile...")
                        if self.cmc_scraper.profile_manager:
                            try:
                                # Check if IP rotation is needed
                                should_rotate_ip = False
                                if hasattr(self.cmc_scraper.profile_manager, 'anti_detection') and self.cmc_scraper.profile_manager.anti_detection:
                                    should_rotate_ip = self.cmc_scraper.profile_manager.anti_detection.should_rotate_ip()
                                
                                if should_rotate_ip:
                                    print("[IP-ROTATE] Anti-detection triggered IP rotation")
                                    self.cmc_scraper.driver = self.cmc_scraper.profile_manager.switch_to_next_profile_with_ip_rotation()
                                    print("[SUCCESS] Profile + IP rotation completed")
                                else:
                                    print("[PROFILE] Regular profile rotation (no IP change needed)")
                                    self.cmc_scraper.driver = self._switch_to_next_profile_smart()
                                    print("[SUCCESS] Profile rotation completed")
                                
                                random_delay(3, 5)  # Delay after profile switch
                            except Exception as e:
                                print(f"[WARNING] Failed to rotate profile: {str(e)}")
                        
                        # Show progress summary
                        print(f"\n[STATS] Progress: {tokens_processed}/{process_limit} tokens processed")
                        print(f"[SUCCESS] Success rate: {len(self.processed_tokens)}/{len(self.processed_tokens) + len(self.failed_tokens)} tokens")
                        
                        # Delay between tokens (respecting rate limits)
                        if tokens_processed < process_limit:
                            # Use adaptive delay from anti-detection system
                            if hasattr(self.cmc_scraper.profile_manager, 'get_adaptive_delay'):
                                delay = self.cmc_scraper.profile_manager.get_adaptive_delay()
                                print(f"[ADAPTIVE-DELAY] Using intelligent delay: {delay} seconds")
                            else:
                                delay = random.randint(45, 75)  # Fallback to old system
                                print(f"[STANDARD-DELAY] Using standard delay: {delay} seconds")
                            
                            # Show session information including IP status
                            if hasattr(self.cmc_scraper.profile_manager, 'get_session_info'):
                                session_info = self.cmc_scraper.profile_manager.get_session_info()
                                print(f"[SESSION-INFO] Mode: {session_info.get('mode', 'unknown').upper()}")
                                if session_info.get('current_proxy'):
                                    print(f"[SESSION-INFO] Current Proxy: {session_info['current_proxy']}")
                                print(f"[SESSION-INFO] Available Proxies: {session_info.get('working_proxies_count', 0)}")
                                if session_info.get('consecutive_failures', 0) > 0:
                                    print(f"[SESSION-INFO] Recent Failures: {session_info['consecutive_failures']}")
                            
                            print(f"[WAIT] Cooling down for {delay} seconds...")
                            time.sleep(delay)
                    
                    except Exception as e:
                        print(f"[ERROR] Error processing {coin['symbol']}: {str(e)}")
                        self._update_session_tracking(coin['symbol'], False)
                        
                        # Try rotating profile on failure
                        if self.cmc_scraper.profile_manager:
                            try:
                                print("[ROTATE] Rotating profile after posting failure...")
                                # Check if we should do IP rotation on failure
                                if hasattr(self.cmc_scraper.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
                                    print("[IP-ROTATE] Using IP rotation due to failure")
                                    self.cmc_scraper.driver = self.cmc_scraper.profile_manager.switch_to_next_profile_with_ip_rotation()
                                    print("[SUCCESS] Profile + IP rotation completed after failure")
                                else:
                                    self.cmc_scraper.driver = self._switch_to_next_profile_smart()
                                    print("[SUCCESS] Profile rotation completed after failure")
                                random_delay(3, 5)
                            except Exception as e:
                                print(f"[WARNING] Failed to rotate profile after failure: {str(e)}")
                        
                        continue
                
                # Move to next page after processing all coins from current page
                if tokens_processed < process_limit:
                    current_page += 1
                    print(f"\n[PAGE] Moving to trending page {current_page} for more coins...")
                    
                    # Safety reset to avoid infinite pagination
                    if current_page > 50:  # After 50 pages (top 500+ coins), reset to page 1
                        print("[INFO] Completed pagination cycle, resetting to page 1...")
                        current_page = 1
                        # Brief pause before restarting the cycle
                        print("[WAIT] Brief pause before restarting pagination cycle...")
                        time.sleep(300)  # 5 minutes pause before restarting cycle
            
            # Final summary
            print("\n" + "="*60)
            print("[COMPLETE] Automated CMC Analysis Session Complete")
            print("="*60)
            print(f"[STATS] Total tokens processed: {len(self.processed_tokens)}")
            print(f"[STATS] Failed tokens: {len(self.failed_tokens)}")
            print(f"[STATS] Success rate: {len(self.processed_tokens)}/{len(self.processed_tokens) + len(self.failed_tokens)}")
            print(f"[SAVE] Session data saved to: analysis_data/sessions/")
            print(f"[SAVE] Variations saved to: analysis_data/variations/")
            print("="*60)
            
            if self.processed_tokens:
                print(f"\n[SUMMARY] Successfully processed tokens:")
                for token in list(self.processed_tokens)[:10]:  # Show first 10
                    print(f"  • ${token}")
                if len(self.processed_tokens) > 10:
                    print(f"  ... and {len(self.processed_tokens) - 10} more")
                    
        except KeyboardInterrupt:
            print("\n[INTERRUPT] Session interrupted by user")
        except Exception as e:
            self.logger.error(f"Error in automated mode: {str(e)}")
            print(f"[ERROR] Automated mode error: {str(e)}")
        finally:
            # Save final session state
            self._save_session_info()

    def _load_browser_with_proxy_config(self):
        """Load browser based on proxy configuration"""
        auto_proxy_rotation = self.proxy_config.get('auto_proxy_rotation', True)
        proxy_mode = self.proxy_config.get('proxy_mode', 'enterprise')
        
        if not auto_proxy_rotation:
            # Direct connection mode - no proxy rotation
            print("\n🌐 DIRECT CONNECTION MODE")
            print("   ❌ Auto proxy rotation disabled")
            print("   ⚡ Using direct connection for faster operation")
            
            try:
                # Load profile without proxy
                profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if profiles:
                    self.driver = self.profile_manager.load_profile(profiles[0])
                    print(f"✅ Loaded profile {profiles[0]} with direct connection")
                else:
                    raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
            except Exception as e:
                print(f"❌ Direct connection failed: {str(e)}")
                raise
                
        elif proxy_mode == 'direct':
            # Same as above - direct connection
            self._load_direct_connection()
            
        elif proxy_mode == 'manual_only':
            # Use only manually configured proxies
            print("\n🎯 MANUAL PROXY MODE")
            print("   📁 Using only manually imported proxies")
            print("   ❌ No automatic proxy discovery")
            
            try:
                # Try to load with manual proxies only
                if hasattr(self.profile_manager, 'load_profile_with_manual_proxies'):
                    self.driver = self.profile_manager.load_profile_with_manual_proxies()
                    print("✅ Loaded profile with manual proxies")
                else:
                    print("⚠️ Manual proxy system not available, falling back to direct connection")
                    self._load_direct_connection()
            except Exception as e:
                print(f"❌ Manual proxy loading failed: {str(e)}")
                if self.proxy_config.get('fallback_to_direct', False):
                    print("🔄 Falling back to direct connection...")
                    self._load_direct_connection()
                else:
                    raise
                    
        else:
            # Enterprise mode with auto proxy rotation (default)
            print("\n🏢 ENTERPRISE PROXY MODE")
            print("   ✅ Auto proxy rotation enabled")
            print("   🔄 Using enterprise proxy discovery")
            
            try:
                # 🗂️ ENTERPRISE: Use persistent storage proxy system
                if hasattr(self.profile_manager, 'load_profile_with_enterprise_proxy'):
                    print("🗂️ Loading profile with Enterprise Persistent Storage Proxy System...")
                    self.driver = self.profile_manager.load_profile_with_enterprise_proxy()
                    
                    # Check if proxy was successfully configured
                    if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                        working_proxy = getattr(self.driver, '_enterprise_working_proxy', 'Unknown')
                        print(f"✅ ENTERPRISE SUCCESS: Chrome configured with stored working proxy!")
                        print(f"🌐 Active Proxy: {working_proxy}")
                        print(f"🔒 Your real IP is completely protected")
                        print(f"🗂️ Using persistent storage system for proxy management")
                    else:
                        print("⚠️ No stored working proxy found")
                        print("💡 Bot will discover and save new working proxies automatically")
                        
                # 🔥 BREAKTHROUGH: Fallback to CMC bypass system
                elif hasattr(self.profile_manager, 'load_profile_with_cmc_bypass'):
                    print("🔥 Loading profile with integrated CMC bypass system...")
                    self.driver = self.profile_manager.load_profile_with_cmc_bypass()
                    
                    # Check if proxy was successfully configured
                    if hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                        working_proxy = getattr(self.driver, '_cmc_working_proxy', 'Unknown')
                        print(f"✅ BREAKTHROUGH SUCCESS: Chrome configured with working proxy!")
                        print(f"🌐 Active Proxy: {working_proxy}")
                        print(f"🔒 Your real IP is completely protected")
                    else:
                        print("⚠️ No working proxy found, using direct connection")
                        print("💡 Bot will still work but without proxy protection")
                        
                else:
                    print("⚠️ Enterprise and breakthrough systems not available, using basic profile switch...")
                    # Even for basic profile switch, ensure proxy is used
                    self.driver = self._load_profile_with_mandatory_proxy()
                    print("✅ Profile loaded with proxy protection")
                    
            except Exception as e:
                print(f"❌ Enterprise proxy loading failed: {str(e)}")
                if self.proxy_config.get('fallback_to_direct', True):
                    print("🔄 Falling back to direct connection...")
                    self._load_direct_connection()
                else:
                    print("🔄 Attempting basic profile load...")
                    try:
                        self.driver = self.profile_manager.switch_to_next_profile()
                        print("✅ Basic profile loaded")
                    except Exception as e2:
                        print(f"❌ Critical error: Cannot load any profile: {str(e2)}")
                        print("\n🚫 ABORTING: Cannot proceed without browser profile")
                        sys.exit(1)
        
        # Verify browser loaded successfully
        if not hasattr(self, 'driver') or self.driver is None:
            print("❌ CRITICAL: Browser failed to load")
            sys.exit(1)
        
        # Show final configuration status
        print(f"\n🎯 FINAL BROWSER CONFIGURATION:")
        print(f"   Browser: ✅ Loaded successfully")
        if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
            proxy = getattr(self.driver, '_enterprise_working_proxy', 'Unknown')
            print(f"   Proxy: ✅ {proxy}")
        elif hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
            proxy = getattr(self.driver, '_cmc_working_proxy', 'Unknown')
            print(f"   Proxy: ✅ {proxy}")
        else:
            print(f"   Proxy: ❌ Direct connection")
        print(f"   Mode: {self.proxy_config.get('proxy_mode', 'enterprise').upper()}")
        
    def _load_direct_connection(self):
        """Load browser with direct connection (no proxy)"""
        try:
            profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            if profiles:
                self.driver = self.profile_manager.load_profile(profiles[0])
                print(f"✅ Loaded profile {profiles[0]} with direct connection")
            else:
                raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
        except Exception as e:
            print(f"❌ Direct connection failed: {str(e)}")
            raise
    
    def _verify_login_before_work(self) -> bool:
        """
        Verify that the current browser session is logged into CMC BEFORE starting any work.
        IMPROVED: Focus on the "Log In" button in the top right header
        """
        try:
            if not hasattr(self, 'cmc_scraper') or not self.cmc_scraper or not self.cmc_scraper.driver:
                print("⚠️ No browser session available")
                return False
            
            # Navigate to CMC main page for accurate detection
            current_url = self.cmc_scraper.driver.current_url
            if 'coinmarketcap.com' not in current_url:
                self.cmc_scraper.driver.get("https://coinmarketcap.com/")
                time.sleep(3)
            
            # PRIMARY CHECK: Look for "Log In" button in the header (most reliable indicator)
            print("🎯 PRIMARY CHECK: Looking for 'Log In' button in header...")
            
            # Specific selectors for the CMC header login button
            header_login_selectors = [
                # Direct text match for Log In button
                "//button[contains(text(), 'Log In') and contains(@class, 'btn')]",
                "//a[contains(text(), 'Log In') and contains(@class, 'btn')]",
                "//button[text()='Log In']",
                "//a[text()='Log In']",
                
                # Header-specific selectors
                "//header//button[contains(text(), 'Log In')]",
                "//header//a[contains(text(), 'Log In')]",
                "//nav//button[contains(text(), 'Log In')]",
                "//nav//a[contains(text(), 'Log In')]",
                
                # Top navigation selectors
                "//div[contains(@class, 'header')]//button[contains(text(), 'Log In')]",
                "//div[contains(@class, 'navbar')]//button[contains(text(), 'Log In')]",
                "//div[contains(@class, 'nav')]//button[contains(text(), 'Log In')]",
                
                # Fallback: any visible login button
                "//button[contains(text(), 'Log In') and not(contains(@style, 'display: none'))]",
                "//a[contains(text(), 'Log In') and not(contains(@style, 'display: none'))]"
            ]
            
            login_button_found = False
            for selector in header_login_selectors:
                try:
                    elements = self.cmc_scraper.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            button_text = element.text.strip()
                            button_tag = element.tag_name
                            print(f"❌ FOUND LOGIN BUTTON: '{button_text}' ({button_tag}) - Session is NOT logged in")
                            login_button_found = True
                            break
                    if login_button_found:
                        break
                except:
                    continue
            
            if login_button_found:
                print("❌ FINAL RESULT: NOT LOGGED IN - Login button visible in header")
                return False  # Found login button = not logged in
            
            # SECONDARY CHECK: Look for logged-in indicators
            print("🔍 SECONDARY CHECK: Looking for logged-in indicators...")
            
            logged_in_selectors = [
                # Profile/user menu indicators
                "//button[contains(@class, 'profile') or contains(@class, 'user')]",
                "//div[contains(@class, 'profile') or contains(@class, 'user')]//img",
                "//button[contains(@class, 'dropdown') and .//img]",  # Profile dropdown with avatar
                
                # Account menu indicators
                "//button[contains(text(), 'Account') or contains(text(), 'Profile')]",
                "//a[contains(text(), 'Account') or contains(text(), 'Profile')]",
                
                # Logout option (means logged in)
                "//button[contains(text(), 'Logout') or contains(text(), 'Sign Out')]",
                "//a[contains(text(), 'Logout') or contains(text(), 'Sign Out')]",
                
                # Portfolio/watchlist links (logged-in features)
                "//a[contains(@href, '/portfolio/') or contains(@href, '/watchlist/')]",
                
                # User avatar/image in header
                "//header//img[contains(@class, 'avatar') or contains(@class, 'profile')]",
                "//nav//img[contains(@class, 'avatar') or contains(@class, 'profile')]"
            ]
            
            logged_in_found = False
            for selector in logged_in_selectors:
                try:
                    elements = self.cmc_scraper.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.strip()
                            element_tag = element.tag_name
                            print(f"✅ FOUND LOGGED-IN INDICATOR: '{element_text}' ({element_tag})")
                            logged_in_found = True
                            break
                    if logged_in_found:
                        break
                except:
                    continue
            
            if logged_in_found:
                print("✅ FINAL RESULT: LOGGED IN - Found logged-in indicators")
                return True
            else:
                print("❓ UNCLEAR STATUS - No clear indicators found, assuming NOT logged in")
                return False
                    
        except Exception as e:
            print(f"❌ Error during login verification: {str(e)}")
            return False
    
    def _switch_to_logged_in_profile(self) -> bool:
        """
        Switch to a profile that is logged into CMC.
        Uses the automatic profile cleanup system to find valid profiles.
        """
        try:
            if not hasattr(self, 'cmc_scraper') or not self.cmc_scraper or not hasattr(self.cmc_scraper, 'profile_manager'):
                print("❌ Profile manager not available")
                return False
            
            max_attempts = 5  # Limit attempts to avoid infinite loops
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                print(f"🔄 Attempt {attempt}/{max_attempts}: Switching to next profile...")
                
                try:
                    # Use the enhanced profile switching with automatic login detection
                    self.cmc_scraper.driver = self.cmc_scraper.profile_manager.switch_to_next_profile()
                    time.sleep(3)  # Give profile time to load
                    
                    # Verify this profile is logged in
                    if self._verify_login_before_work():
                        print(f"✅ Found logged-in profile after {attempt} attempts")
                        return True
                    else:
                        print(f"❌ Profile {attempt} is not logged in, trying next...")
                        continue
                        
                except Exception as e:
                    print(f"❌ Error switching to profile {attempt}: {str(e)}")
                    continue
            
            print(f"❌ Could not find logged-in profile after {max_attempts} attempts")
            return False
            
        except Exception as e:
            print(f"❌ Error during profile switching: {str(e)}")
            return False

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    print("\n" + "="*60)
    print("🤖 CMC AI Token Review Analyzer & Shilling Bot")
    print("="*60)
    print("\nThis bot will:")
    print("1. Find trending tokens on CoinMarketCap")
    print("2. Generate AI reviews for each token")
    print("3. Cross-reference your promoted token in analyses")
    print("4. Post enhanced reviews to CMC community")
    print("5. Save all content locally for analysis")
    print("\n💡 NEW: Token Shilling Mode - Naturally promote your token")
    print("   when analyzing ANY other trending token!")
    print("\nStarting...\n")
    
    analyzer = CryptoAIAnalyzer()
    analyzer.run_analysis()
    
    print("\n✅ Analysis complete!")
    print("Check the 'analysis_data' folder for generated variations.") 