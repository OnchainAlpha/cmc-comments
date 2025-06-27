import sys
import os
import json
import time
import psutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import tempfile
import shutil
import logging
from pathlib import Path
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the anti-detection system with persistent storage
try:
    from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager, AntiDetectionSystem
    ENTERPRISE_PROXY_AVAILABLE = True
except ImportError:
    EnterpriseProxyManager = None
    AntiDetectionSystem = None
    ENTERPRISE_PROXY_AVAILABLE = False

# 🔥 BREAKTHROUGH: Import our verified working CMC bypass system
try:
    from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
    CMC_BYPASS_AVAILABLE = True
    print("🔥 Profile Manager: Breakthrough CMC bypass system loaded!")
except ImportError:
    CMC_BYPASS_AVAILABLE = False
    cmc_bypass_manager = None
    print("⚠️ Profile Manager: CMC bypass system not available")

class ProfileManager:
    def __init__(self, proxy_config: dict = None):
        self.logger = logging.getLogger(__name__)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.profiles_dir = os.path.join(self.base_dir, 'chrome_profiles')
        os.makedirs(self.profiles_dir, exist_ok=True)
        self.current_profile = None
        self.current_driver = None
        
        # Store proxy configuration
        self.proxy_config = proxy_config or {}
        
        # Initialize enterprise proxy system with persistent storage
        if ENTERPRISE_PROXY_AVAILABLE:
            self.enterprise_proxy = EnterpriseProxyManager()
            # Initialize anti-detection system with proxy configuration
            self.anti_detection = AntiDetectionSystem(proxy_config=self.proxy_config) if AntiDetectionSystem else None
            print("✅ Enterprise Proxy System with Persistent Storage initialized")
            print("🗂️ Stored working proxies will be used automatically")
        else:
            self.enterprise_proxy = None
            # Initialize anti-detection system with proxy configuration
            self.anti_detection = AntiDetectionSystem(proxy_config=self.proxy_config) if AntiDetectionSystem else None
            
        if self.anti_detection:
            self.logger.info("✅ Anti-detection system initialized")
            # Display the configured anti-detection status
            self.anti_detection.display_anti_detection_status()
        else:
            self.logger.warning("⚠️ Anti-detection system not available")

    def list_profiles(self, silent_mode=False):
        """List available Chrome profiles"""
        profiles = []
        
        if not silent_mode:
            print("\nAvailable Chrome Profiles:")
            print("="*60)
        
        # First, list numbered profiles
        numbered_profiles = []
        other_profiles = []
        
        for item in os.listdir(self.profiles_dir):
            profile_path = os.path.join(self.profiles_dir, item)
            if os.path.isdir(profile_path):
                if item.startswith('cmc_profile_'):
                    numbered_profiles.append(item)
                else:
                    other_profiles.append(item)
        
        # Sort numbered profiles
        numbered_profiles.sort(key=lambda x: int(x.split('_')[-1]))
        
        # Print numbered profiles first
        for item in numbered_profiles:
            profile_path = os.path.join(self.profiles_dir, item)
            has_preferences = os.path.exists(os.path.join(profile_path, 'Default', 'Preferences'))
            has_test = os.path.exists(os.path.join(profile_path, 'profile_test.txt'))
            
            status = "✅ Ready" if has_preferences and has_test else "⚠️ May need setup"
            
            try:
                created = time.ctime(os.path.getctime(profile_path))
            except:
                created = "Unknown"
            
            if not silent_mode:
                print(f"\nProfile: {item}")
                print(f"Status: {status}")
                print(f"Created: {created}")
                print(f"Path: {profile_path}")
            
            profiles.append(item)
        
        # Print other profiles
        if other_profiles:
            if not silent_mode:
                print("\nLegacy Profiles (need migration):")
            for item in other_profiles:
                profile_path = os.path.join(self.profiles_dir, item)
                try:
                    created = time.ctime(os.path.getctime(profile_path))
                except:
                    created = "Unknown"
                
                if not silent_mode:
                    print(f"\nProfile: {item}")
                    print(f"Status: ⚠️ Needs migration")
                    print(f"Created: {created}")
                    print(f"Path: {profile_path}")
                
                profiles.append(item)
        
        if not profiles and not silent_mode:
            print("\nNo profiles found.")
            print("Use option 2 to create a new profile.")
        elif not silent_mode:
            print("\nℹ️ Legacy profiles should be migrated to the new format.")
            print("Use option 5 to migrate profiles.")
        
        if not silent_mode:
            print("\n" + "="*60)
        return profiles

    def get_profile_path(self, profile_name):
        """Get full path for a profile"""
        return os.path.join(self.profiles_dir, profile_name)

    def _kill_chrome_processes(self):
        """Kill any existing Chrome processes"""
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() in ['chrome.exe', 'chromedriver.exe']:
                    try:
                        proc.kill()
                    except:
                        pass
            time.sleep(2)  # Wait for processes to close
        except:
            pass

    def _cleanup_profile(self, profile_path):
        """Clean up problematic files in Chrome profile"""
        try:
            problem_files = ['Singleton*', 'lockfile', 'DevToolsActivePort']
            for item in problem_files:
                for file in Path(profile_path).glob(item):
                    try:
                        file.unlink()
                    except:
                        pass
        except:
            pass

    def _verify_profile(self, profile_path):
        """Verify that a profile is properly set up"""
        try:
            # Create Default directory if it doesn't exist
            default_dir = os.path.join(profile_path, 'Default')
            os.makedirs(default_dir, exist_ok=True)
            
            # Create necessary files if they don't exist
            preferences_file = os.path.join(default_dir, 'Preferences')
            if not os.path.exists(preferences_file):
                with open(preferences_file, 'w') as f:
                    json.dump({
                        "profile": {
                            "name": os.path.basename(profile_path),
                            "avatar_icon": ""
                        },
                        "session": {
                            "restore_on_startup": 4
                        }
                    }, f)
            
            # Create test file
            test_file = os.path.join(profile_path, 'profile_test.txt')
            if not os.path.exists(test_file):
                with open(test_file, 'w') as f:
                    f.write('Profile test file')
            
            return True
        except Exception as e:
            self.logger.error(f"Error verifying profile: {str(e)}")
            return False

    def import_existing_profile(self, source_dir=None):
        """Create a new Chrome profile for CMC"""
        try:
            # Get next available profile number
            profiles = [p for p in self.list_profiles() if p.startswith('cmc_profile_')]
            next_num = len(profiles) + 1
            profile_name = f'cmc_profile_{next_num}'
            profile_path = self.get_profile_path(profile_name)
            
            # Create profile directory if it doesn't exist
            os.makedirs(profile_path, exist_ok=True)
            
            print("\n" + "="*60)
            print(f"🔐 CREATING CMC PROFILE #{next_num}")
            print("="*60)
            print("\nThis will create a new Chrome profile for CoinMarketCap.")
            print("You'll need to log in to your CMC account ONCE.")
            print("The profile will be saved and reused in future runs.")
            
            # Kill existing Chrome processes
            self._kill_chrome_processes()
            
            # Clean up profile
            self._cleanup_profile(profile_path)
            
            # Verify profile structure
            self._verify_profile(profile_path)
            
            # Use regular selenium for initial profile setup with additional options
            options = Options()
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--window-size=1366,768')
            # Add options to help with SSL/connection issues
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-blink-features=AutomationControlled')
            # Disable GPU and sandboxing
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            # Disable logging
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Initialize Chrome with selenium-manager
            service = Service()
            service.creation_flags = 0x08000000  # No console window
            driver = webdriver.Chrome(service=service, options=options)
            
            # Navigate to CMC
            print("\n1. Opening CoinMarketCap...")
            driver.get("https://coinmarketcap.com")
            time.sleep(3)
            
            print("\n2. Please log in to your CMC account.")
            print("3. After logging in, verify you can see your profile.")
            input("\n✋ Press Enter once you're logged in and ready...")
            
            # Save cookies and preferences
            cookies = driver.get_cookies()
            preferences_file = os.path.join(profile_path, 'Default', 'Preferences')
            with open(preferences_file, 'w') as f:
                json.dump({
                    "profile": {
                        "name": profile_name,
                        "avatar_icon": ""
                    },
                    "session": {
                        "restore_on_startup": 4
                    },
                    "cookies": cookies
                }, f)
            
            print("\n✅ Profile created successfully!")
            print(f"Profile saved at: {profile_path}")
            
            driver.quit()
            return profile_name
            
        except Exception as e:
            self.logger.error(f"Failed to create profile: {str(e)}")
            if 'driver' in locals():
                try:
                    driver.quit()
                except:
                    pass
            raise

    def load_profile(self, profile_name='cmc_profile'):
        """Load Chrome with the saved profile"""
        try:
            self.logger.info("Loading Chrome profile...")
            profile_path = self.get_profile_path(profile_name)
            
            # Verify profile exists
            if not os.path.exists(profile_path):
                self.logger.warning(f"Profile '{profile_name}' not found. Selecting from existing profiles...")
                # Instead of creating new profile, use existing one
                existing_profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if existing_profiles:
                    profile_name = existing_profiles[0]  # Use first available profile
                    profile_path = self.get_profile_path(profile_name)
                    self.logger.info(f"Using existing profile: {profile_name}")
                else:
                    raise Exception("No existing CMC profiles found. Please create profiles manually.")
            
            # Kill existing Chrome processes
            self._kill_chrome_processes()
            
            # Clean up profile
            self._cleanup_profile(profile_path)
            
            # Try regular selenium first since it's more stable
            try:
                self.logger.info("Initializing Chrome with regular selenium...")
                options = Options()
                options.add_argument(f'--user-data-dir={profile_path}')
                options.add_argument('--no-first-run')
                options.add_argument('--no-default-browser-check')
                options.add_argument('--window-size=1366,768')
                # Add options to help with SSL/connection issues
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--disable-web-security')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                options.add_argument('--disable-blink-features=AutomationControlled')
                # Disable GPU and sandboxing
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                # Disable logging
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                
                service = Service()
                service.creation_flags = 0x08000000  # No console window
                driver = webdriver.Chrome(service=service, options=options)
                
            except Exception as e:
                self.logger.warning(f"Failed to initialize with regular selenium: {str(e)}")
                self.logger.info("Trying undetected-chromedriver as fallback...")
                
                # Fallback to undetected-chromedriver
                options = uc.ChromeOptions()
                options.add_argument(f'--user-data-dir={profile_path}')
                options.add_argument('--no-first-run')
                options.add_argument('--no-default-browser-check')
                options.add_argument('--window-size=1366,768')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                driver = uc.Chrome(options=options, suppress_welcome=True)
            
            self.logger.info("✅ Chrome profile loaded successfully!")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to load Chrome profile: {str(e)}")
            raise

    def get_chrome_version(self):
        """Get installed Chrome version"""
        try:
            # Try to detect Chrome version
            driver = uc.Chrome(version_main=136, use_subprocess=True)
            version = driver.capabilities.get('browserVersion', 'Unknown')
            driver.quit()
            return version
        except:
            # Fallback to checking common installation paths
            if os.name == 'nt':  # Windows
                paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
                for path in paths:
                    if os.path.exists(path):
                        return "latest"  # Let webdriver-manager handle version
            return None 

    def create_numbered_profile(self, number: int):
        """Create a new numbered CMC profile"""
        profile_name = f'cmc_profile_{number}'
        print(f"\nCreating profile: {profile_name}")
        return self.import_existing_profile(profile_name)

    def get_next_profile_number(self):
        """Get the next available profile number"""
        profiles = self.list_profiles(silent_mode=True)
        numbers = []
        for profile in profiles:
            if profile.startswith('cmc_profile_'):
                try:
                    num = int(profile.split('_')[-1])
                    numbers.append(num)
                except ValueError:
                    continue
        return max(numbers, default=0) + 1 if numbers else 1

    def switch_to_next_profile(self):
        """Switch to the next available profile with login validation"""
        try:
            # Close current driver if exists
            if self.current_driver:
                try:
                    self.current_driver.quit()
                except:
                    pass
                self.current_driver = None

            # Get all profiles
            profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            
            if not profiles:
                # Don't create profiles automatically - raise error instead
                raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")

            # Find next profile
            if not self.current_profile:
                next_profile = profiles[0]
            else:
                try:
                    current_idx = profiles.index(self.current_profile)
                    next_profile = profiles[(current_idx + 1) % len(profiles)]
                except ValueError:
                    next_profile = profiles[0]

            # Load next profile
            print(f"🔄 Switching to profile: {next_profile}")
            self.current_driver = self.load_profile(next_profile)
            self.current_profile = next_profile
            
            # ENHANCED: Quick check if the profile is logged into CMC
            print("🔍 Quick login check for profile...")
            try:
                # Use quick check first for speed
                is_logged_in = self.quick_login_check(self.current_driver)
                
                if not is_logged_in:
                    print(f"❌ Profile {next_profile} is not logged into CMC!")
                    
                    # Close the current driver
                    try:
                        self.current_driver.quit()
                    except:
                        pass
                    self.current_driver = None
                    
                    # Remove the logged-out profile
                    print(f"🗑️ Automatically removing logged-out profile: {next_profile}")
                    if self.cleanup_logged_out_profile(next_profile):
                        print(f"✅ Profile {next_profile} removed successfully")
                        
                        # Recursively try the next profile
                        print("🔄 Attempting to switch to next available profile...")
                        return self.switch_to_next_profile()
                    else:
                        print(f"❌ Failed to remove profile {next_profile}")
                        # Continue with the logged-out profile as fallback
                        self.current_driver = self.load_profile(next_profile)
                        self.current_profile = next_profile
                        print("⚠️ Continuing with logged-out profile - manual login may be required")
                else:
                    print(f"✅ Profile {next_profile} is logged into CMC")
                    
            except Exception as login_check_error:
                print(f"⚠️ Could not verify login status: {str(login_check_error)}")
                print("🔄 Continuing with profile switch...")
            
            self.logger.info(f"Successfully switched to profile: {next_profile}")
            return self.current_driver

        except Exception as e:
            self.logger.error(f"Error switching profiles: {str(e)}")
            # Don't create new profiles automatically - just raise the error
            raise 

    def migrate_profile(self, old_name):
        """Migrate an old profile to the new numbered format"""
        try:
            # Get next available profile number
            profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            next_num = len(profiles) + 1
            new_name = f'cmc_profile_{next_num}'
            
            old_path = self.get_profile_path(old_name)
            new_path = self.get_profile_path(new_name)
            
            # Move the profile
            shutil.move(old_path, new_path)
            
            # Verify and fix the profile structure
            self._verify_profile(new_path)
            
            print(f"\n✅ Migrated profile '{old_name}' to '{new_name}'")
            return new_name
        except Exception as e:
            self.logger.error(f"Failed to migrate profile: {str(e)}")
            return None 

    def load_profile_with_options(self, profile_name: str, custom_options: Options = None):
        """Load Chrome profile with custom options (including proxy)"""
        try:
            self.logger.info(f"Loading profile {profile_name} with custom options...")
            profile_path = self.get_profile_path(profile_name)
            
            # Verify profile exists
            if not os.path.exists(profile_path):
                self.logger.warning(f"Profile '{profile_name}' not found. Selecting from existing profiles...")
                # Instead of creating new profile, use existing one
                existing_profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if existing_profiles:
                    profile_name = existing_profiles[0]  # Use first available profile
                    profile_path = self.get_profile_path(profile_name)
                    self.logger.info(f"Using existing profile: {profile_name}")
                else:
                    raise Exception("No existing CMC profiles found. Please create profiles manually.")
            
            # Kill existing Chrome processes
            self._kill_chrome_processes()
            
            # Clean up profile
            self._cleanup_profile(profile_path)
            
            # Use custom options or create new ones
            if custom_options is None:
                options = Options()
            else:
                options = custom_options
            
            # Add profile-specific arguments
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            
            # Additional stability options
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--disable-web-security')
            options.add_argument('--allow-running-insecure-content')
            options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Try regular selenium first
            try:
                service = Service()
                service.creation_flags = 0x08000000  # No console window
                driver = webdriver.Chrome(service=service, options=options)
                
            except Exception as e:
                self.logger.warning(f"Failed with regular selenium: {str(e)}")
                # Fallback to undetected-chromedriver
                uc_options = uc.ChromeOptions()
                
                # Transfer arguments from regular options to uc options
                for arg in options.arguments:
                    uc_options.add_argument(arg)
                
                # Transfer experimental options
                for key, value in options.experimental_options.items():
                    uc_options.add_experimental_option(key, value)
                
                driver = uc.Chrome(options=uc_options, suppress_welcome=True)
            
            self.current_driver = driver
            self.current_profile = profile_name
            self.logger.info("✅ Profile loaded successfully with custom options!")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to load profile with options: {str(e)}")
            raise

    def load_profile_with_enterprise_proxy(self, profile_name: str = None):
        """🗂️ Load profile with persistent storage proxy system (automatic proxy discovery and curation)"""
        try:
            if not self.enterprise_proxy:
                print("⚠️ Enterprise proxy system not available, using fallback")
                return self.load_profile_with_cmc_bypass(profile_name)
            
            print("🗂️ LOADING PROFILE WITH PERSISTENT STORAGE PROXY SYSTEM")
            print("="*60)
            print("✅ Automatically uses stored working proxies")
            print("✅ Discovers new proxies if needed")
            print("✅ Saves working proxies for future use")
            print("✅ Removes failed proxies automatically")
            
            # Get options with enterprise proxy (uses stored proxies first)
            print("\n🔄 Creating Chrome options with enterprise proxy...")
            options = self.enterprise_proxy.create_anti_detection_options(
                use_proxy=True, 
                force_proxy=False  # Allow operation without proxy if none available
            )
            
            # If no specific profile requested, get next available
            if not profile_name:
                profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                if not profiles:
                    raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
                profile_name = profiles[0]
            
            print(f"👤 Loading profile: {profile_name}")
            
            # Load profile with enterprise proxy options
            driver = self.load_profile_with_options(profile_name, options)
            
            # Get current proxy info
            best_proxy = self.enterprise_proxy.get_best_proxy()
            if best_proxy:
                print(f"✅ Profile loaded with stored working proxy: {best_proxy}")
                driver._enterprise_proxy_configured = True
                driver._enterprise_working_proxy = best_proxy
            else:
                print("⚠️ No proxy available - using direct connection")
                driver._enterprise_proxy_configured = False
                driver._enterprise_working_proxy = None
            
            # Show storage stats
            storage_stats = self.enterprise_proxy.proxy_storage.get_storage_stats()
            print(f"\n📊 PROXY STORAGE STATUS:")
            print(f"   ✅ Working proxies available: {storage_stats['working_proxies']}")
            print(f"   ❌ Failed proxies tracked: {storage_stats['failed_proxies']}")
            print(f"   📈 Average success rate: {storage_stats['average_success_rate']}%")
            
            self.current_driver = driver
            self.current_profile = profile_name
            print("="*60)
            return driver
                
        except Exception as e:
            print(f"❌ Error loading profile with enterprise proxy: {str(e)}")
            print("🔄 Falling back to CMC bypass system...")
            return self.load_profile_with_cmc_bypass(profile_name)

    def switch_to_next_profile_with_ip_rotation(self):
        """Switch to next profile with IP rotation via anti-detection system"""
        # Check if IP rotation is disabled by user preference
        if hasattr(self, 'proxy_config') and not self.proxy_config.get('auto_proxy_rotation', True):
            print("⚠️ [PROFILE-SWITCH] IP rotation disabled by user preference - using regular profile switch")
            return self.switch_to_next_profile()
            
        try:
            print("\n" + "🔄"*60)
            print("🌐 PROFILE + IP ROTATION INITIATED")
            print("🔄"*60)
            
            # Get current state for logging
            old_profile = self.current_profile
            old_proxy = None
            old_ip = None
            
            if self.anti_detection and hasattr(self.anti_detection, 'session_state'):
                old_proxy = self.anti_detection.session_state.get('current_proxy')
                print(f"📋 Current Profile: {old_profile or 'None'}")
                print(f"🌐 Current Proxy: {old_proxy or 'None'}")
                
                # Try to get current IP
                if old_proxy:
                    try:
                        import requests
                        old_proxies = {'http': f'http://{old_proxy}', 'https': f'http://{old_proxy}'}
                        old_ip_response = requests.get('http://httpbin.org/ip', proxies=old_proxies, timeout=5)
                        old_ip = old_ip_response.json().get('origin', 'Unknown')
                        print(f"📡 Current IP: {old_ip}")
                    except Exception as e:
                        print(f"📡 Current IP: Could not detect")
                        self.logger.debug(f"Could not get current IP: {str(e)}")
            
            # Close current driver if exists
            if self.current_driver:
                try:
                    self.current_driver.quit()
                except:
                    pass
                self.current_driver = None
                time.sleep(2)  # Wait for cleanup
                print("🔄 Previous session closed")

            # Get all profiles
            profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            
            if not profiles:
                # Don't create profiles automatically - raise error instead
                raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")

            # Find next profile
            if not self.current_profile:
                next_profile = profiles[0]
            else:
                try:
                    current_idx = profiles.index(self.current_profile)
                    next_profile = profiles[(current_idx + 1) % len(profiles)]
                except ValueError:
                    next_profile = profiles[0]

            print(f"🔄 Switching: {old_profile or 'None'} → {next_profile}")

            # Get anti-detection options with proxy
            if self.anti_detection:
                print("🛡️ Creating anti-detection options with IP rotation...")
                options = self.anti_detection.create_anti_detection_options(use_proxy=True)
                
                # Log session summary
                summary = self.anti_detection.get_session_summary()
                print(f"📊 Anti-Detection Mode: {summary.get('mode', 'unknown').upper()}")
                print(f"🔧 Available Proxies: {summary.get('working_proxies_count', 0)}")
                
                if summary.get('consecutive_failures', 0) > 0:
                    print(f"⚠️ Previous Failures: {summary['consecutive_failures']}")
                
            else:
                print("⚠️ Anti-detection not available, using basic options")
                options = Options()

            # Load next profile with anti-detection options
            print(f"🔄 Loading profile with new IP configuration...")
            self.current_driver = self.load_profile_with_options(next_profile, options)
            self.current_profile = next_profile
            
            # Get new proxy and IP info for logging
            new_proxy = None
            new_ip = None
            
            if self.anti_detection and hasattr(self.anti_detection, 'session_state'):
                new_proxy = self.anti_detection.session_state.get('current_proxy')
                
                if new_proxy and new_proxy != old_proxy:
                    try:
                        import requests
                        new_proxies = {'http': f'http://{new_proxy}', 'https': f'http://{new_proxy}'}
                        new_ip_response = requests.get('http://httpbin.org/ip', proxies=new_proxies, timeout=5)
                        new_ip = new_ip_response.json().get('origin', 'Unknown')
                    except Exception as e:
                        self.logger.debug(f"Could not get new IP: {str(e)}")
            
            # Add behavioral randomization
            if self.anti_detection and self.current_driver:
                print("🎭 Applying behavioral randomization...")
                self.anti_detection.randomize_behavior(self.current_driver)
            
            # Final logging
            print("🔄"*60)
            print("✅ PROFILE + IP ROTATION COMPLETE")
            print("🔄"*60)
            print(f"📋 Profile: {old_profile or 'None'} → {next_profile}")
            print(f"🌐 Proxy: {old_proxy or 'None'} → {new_proxy or 'None'}")
            if old_ip or new_ip:
                print(f"📡 IP: {old_ip or 'Unknown'} → {new_ip or 'Unknown'}")
            print("🔄"*60)
            
            self.logger.info(f"Successfully switched to profile: {next_profile} with IP rotation")
            return self.current_driver
            
        except Exception as e:
            print(f"❌ PROFILE + IP ROTATION FAILED: {str(e)}")
            print("🔄"*60)
            self.logger.error(f"Failed to switch profile with IP rotation: {str(e)}")
            # Fallback to regular profile switching
            try:
                print("🔄 Attempting fallback to basic profile switch...")
                return self.switch_to_next_profile()
            except Exception as e2:
                print(f"❌ Fallback also failed: {str(e2)}")
                raise

    def check_and_handle_shadowban(self):
        """Check for shadowban but DON'T close browser - FIXED: Removed aggressive browser closing"""
        if not self.anti_detection or not self.current_driver:
            return False
            
        try:
            # Check for shadowban
            is_shadowbanned = self.anti_detection.detect_shadowban(self.current_driver)
            
            if is_shadowbanned:
                self.logger.warning("🚫 SHADOWBAN DETECTED!")
                self.anti_detection.update_session_state(False, 'shadowban')
                
                # REMOVED: Automatic browser closing and IP rotation
                # This was causing more problems than it solved
                print("⚠️ SHADOWBAN: Detected but continuing without closing browser")
                print("💡 TIP: Manual intervention may be needed if posts aren't appearing")
                return True  # Return True to indicate shadowban detected, but don't close browser
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking shadowban: {str(e)}")
            return False

    def get_adaptive_delay(self) -> int:
        """Get adaptive delay from anti-detection system"""
        if self.anti_detection:
            return self.anti_detection.get_adaptive_delay()
        else:
            # Fallback to random delay
            import random
            return random.randint(45, 90)

    def update_post_result(self, success: bool, error_type: str = None):
        """Update anti-detection system with post result"""
        if self.anti_detection:
            self.anti_detection.update_session_state(success, error_type)

    def get_session_info(self) -> dict:
        """Get current session information"""
        if self.anti_detection:
            return self.anti_detection.get_session_summary()
        else:
            return {
                'mode': 'basic',
                'current_profile': self.current_profile,
                'anti_detection': False
            } 

    def load_profile_with_cmc_bypass(self, profile_name: str = None):
        """🔥 BREAKTHROUGH: Load profile with currently working CMC bypass proxy"""
        try:
            if not CMC_BYPASS_AVAILABLE or not cmc_bypass_manager:
                print("⚠️ CMC bypass not available, loading profile normally")
                if profile_name:
                    return self.load_profile(profile_name)
                else:
                    return self.switch_to_next_profile()
            
            print("🔥 BREAKTHROUGH: Loading profile with CMC bypass proxy integration...")
            
            # Get selenium options with currently working proxy
            proxy_options, working_proxy = cmc_bypass_manager.create_selenium_proxy_options()
            
            if working_proxy:
                print(f"✅ Using working CMC bypass proxy: {working_proxy}")
                
                # If no specific profile requested, get next available
                if not profile_name:
                    profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
                    if not profiles:
                        raise Exception("No existing CMC profiles found. Please create profiles manually using the Profile Management menu.")
                    profile_name = profiles[0]
                
                # Load profile with proxy options
                driver = self.load_profile_with_options(profile_name, proxy_options)
                
                # Mark as proxy configured
                driver._cmc_proxy_configured = True
                driver._cmc_working_proxy = working_proxy
                
                print(f"🎉 BREAKTHROUGH: Profile loaded with working CMC bypass proxy!")
                print(f"🌐 Proxy: {working_proxy}")
                print(f"👤 Profile: {profile_name}")
                
                self.current_driver = driver
                self.current_profile = profile_name
                return driver
                
            else:
                print("❌ No working CMC bypass proxy found, loading profile normally")
                if profile_name:
                    return self.load_profile(profile_name)
                else:
                    return self.switch_to_next_profile()
                    
        except Exception as e:
            print(f"❌ Error loading profile with CMC bypass: {str(e)}")
            print("🔄 Falling back to normal profile loading...")
            if profile_name:
                return self.load_profile(profile_name)
            else:
                return self.switch_to_next_profile()
    
    def check_cmc_login_status(self, driver, profile_name: str = None) -> dict:
        """
        Check if the current driver session is logged into CMC
        SIMPLE TEST: If you can see "Log In" button in top right, you're NOT logged in.
        """
        try:
            print(f"🔍 CHECKING CMC LOGIN STATUS{f' for {profile_name}' if profile_name else ''}...")
            
            # Navigate to CMC main page for accurate detection
            print("📍 Navigating to CMC main page to check login status...")
            driver.get("https://coinmarketcap.com/")
            time.sleep(3)
            
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"🔍 Current URL: {current_url}")
            print(f"🔍 Page Title: {page_title}")
            
            # CRITICAL FIX: Look for Login button (means NOT logged in)
            print("🔍 Looking for 'Log In' button in top navigation...")
            
            login_button_selectors = [
                "//button[contains(text(), 'Log In')]",
                "//a[contains(text(), 'Log In')]", 
                "//div[contains(text(), 'Log In')]",
                "//span[contains(text(), 'Log In')]"
            ]
            
            login_button_found = False
            logout_reasons = []
            
            for selector in login_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            print(f"❌ FOUND LOGIN BUTTON: '{element.text}' - Profile is NOT logged in")
                            login_button_found = True
                            logout_reasons.append(f"Login button found: {element.text}")
                            break
                    if login_button_found:
                        break
                except:
                    continue
            
            if login_button_found:
                # Definitely not logged in
                status = {
                    'logged_in': False,
                    'logout_score': 10,
                    'login_score': 0,
                    'final_score': 10,
                    'logout_reasons': logout_reasons,
                    'login_reasons': [],
                    'url': current_url,
                    'title': page_title,
                    'profile_name': profile_name
                }
                
                print(f"❌ NOT LOGGED IN - Login button found in navigation")
                return status
            
            # Check for logged-in indicators
            print("🔍 Looking for logged-in indicators (profile menu, etc.)...")
            
            logged_in_selectors = [
                "//button[contains(text(), 'Profile')]",
                "//a[contains(text(), 'Profile')]",
                "//button[contains(text(), 'Logout')]", 
                "//a[contains(text(), 'Logout')]",
                "//div[contains(@class, 'profile')]//img",  # Profile avatar
                "//div[contains(@class, 'user')]//img",     # User avatar
                "//button[contains(@class, 'profile')]"
            ]
            
            logged_in_found = False
            login_reasons = []
            
            for selector in logged_in_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            print(f"✅ FOUND LOGGED-IN INDICATOR: {selector}")
                            logged_in_found = True
                            login_reasons.append(f"Logged-in indicator: {selector}")
                            break
                    if logged_in_found:
                        break
                except:
                    continue
            
            if logged_in_found:
                status = {
                    'logged_in': True,
                    'logout_score': 0,
                    'login_score': 10,
                    'final_score': -10,
                    'logout_reasons': [],
                    'login_reasons': login_reasons,
                    'url': current_url,
                    'title': page_title,
                    'profile_name': profile_name
                }
                
                print(f"✅ LOGGED IN - Profile has valid login session")
                return status
            else:
                # Ambiguous - no clear login button, but no clear logged-in indicators either
                status = {
                    'logged_in': False,
                    'logout_score': 5,
                    'login_score': 0,
                    'final_score': 5,
                    'logout_reasons': ['No clear logged-in indicators found'],
                    'login_reasons': [],
                    'url': current_url,
                    'title': page_title,
                    'profile_name': profile_name
                }
                
                print(f"❌ AMBIGUOUS - No clear login indicators found, assuming logged out")
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
            profile_path = self.get_profile_path(profile_name)
            
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
        print("\n" + "="*70)
        print("🧹 CMC PROFILE LOGIN SCAN & CLEANUP")
        print("="*70)
        
        # Get all CMC profiles
        all_profiles = [p for p in self.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
        
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
                    driver = self.load_profile(profile_name)
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
        SIMPLE TEST: If you can see "Log In" button in top right, you're NOT logged in.
        """
        try:
            # Navigate to main page if not already there
            current_url = driver.current_url
            if 'coinmarketcap.com' not in current_url or 'community' in current_url:
                driver.get("https://coinmarketcap.com/")
                time.sleep(2)
            
            # Look for Login button (means NOT logged in)
            login_button_selectors = [
                "//button[contains(text(), 'Log In')]",
                "//a[contains(text(), 'Log In')]", 
                "//div[contains(text(), 'Log In')]",
                "//span[contains(text(), 'Log In')]"
            ]
            
            # If we find a login button, we're NOT logged in
            for selector in login_button_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            return False  # Found login button = not logged in
                except:
                    continue
            
            # Look for logged-in indicators
            logged_in_selectors = [
                "//button[contains(text(), 'Profile')]",
                "//a[contains(text(), 'Profile')]",
                "//button[contains(text(), 'Logout')]", 
                "//a[contains(text(), 'Logout')]",
                "//div[contains(@class, 'profile')]//img",  # Profile avatar
                "//div[contains(@class, 'user')]//img"      # User avatar
            ]
            
            # If we find logged-in indicators, we're logged in
            for selector in logged_in_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            return True  # Found logged-in indicator = logged in
                except:
                    continue
            
            # If no clear indicators either way, assume logged out for safety
            return False
            
        except Exception as e:
            self.logger.debug(f"Quick login check error: {str(e)}")
            return False  # Assume logged out on error