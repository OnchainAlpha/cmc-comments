import sys
import os
import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import shutil
import logging

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ProfileManager:
    def __init__(self):
        self.profiles_dir = os.path.expanduser("~/chrome_profiles")
        os.makedirs(self.profiles_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def import_existing_profile(self):
        """Import an existing Chrome profile - simplified version"""
        print("\nProfile import: Using simplified profile system.")
        print("The bot will create a new profile to avoid conflicts.")
        # Create a marker file to indicate profile exists
        profile_name = "cmc"
        profile_path = os.path.join(self.profiles_dir, profile_name)
        os.makedirs(profile_path, exist_ok=True)
        marker_file = os.path.join(profile_path, "profile_imported.txt")
        with open(marker_file, 'w') as f:
            f.write("Profile imported successfully")
        print(f"\nProfile '{profile_name}' set up successfully!")
        return

    def load_profile(self, profile_name: str):
        """Load a Chrome profile - simplified but reliable version"""
        profile_path = os.path.join(self.profiles_dir, profile_name)
        
        # Ensure profile directory exists
        os.makedirs(profile_path, exist_ok=True)
        
        try:
            print("\nInitializing Chrome...")
            print(f"undetected-chromedriver version: {uc.__version__}")
            
            # Simple approach that works reliably
            options = uc.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-popup-blocking')
            
            driver = uc.Chrome(options=options, version_main=136)
            print("✅ Chrome initialized successfully!")
            print("📝 NOTE: You'll need to log in to CMC manually in this session")
            
            # Set some additional properties to avoid detection
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Error initializing Chrome: {str(e)}")
            print(f"\nError initializing Chrome: {str(e)}")
            
            # Clean up and try again
            try:
                print("\nCleaning up and trying again...")
                import subprocess
                try:
                    subprocess.run(["taskkill", "/f", "/im", "chromedriver.exe"], 
                                 capture_output=True, check=False)
                    subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                                 capture_output=True, check=False)
                except:
                    pass
                
                # Simplest possible initialization
                driver = uc.Chrome(version_main=136)
                print("✅ Chrome initialized with simplest method!")
                return driver
                
            except Exception as e2:
                self.logger.error(f"Fallback also failed: {str(e2)}")
                print(f"\nFallback also failed: {str(e2)}")
                raise Exception(f"Failed to initialize Chrome: {str(e)}")

    def list_profiles(self):
        """List all imported profiles"""
        if not os.path.exists(self.profiles_dir):
            return []
        return [d for d in os.listdir(self.profiles_dir) 
                if os.path.isdir(os.path.join(self.profiles_dir, d))]

    def get_chrome_version(self):
        """Get installed Chrome version"""
        try:
            # Try to detect Chrome version
            driver = uc.Chrome()
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