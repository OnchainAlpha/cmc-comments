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
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ProfileManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.profiles_dir = os.path.join(self.base_dir, 'chrome_profiles')
        os.makedirs(self.profiles_dir, exist_ok=True)

    def list_profiles(self):
        """List available Chrome profiles"""
        return ['default']  # We'll just use a default profile

    def get_profile_path(self, profile_name):
        """Get full path for a profile"""
        return os.path.join(self.profiles_dir, profile_name)

    def import_existing_profile(self, source_dir=None):
        """Simplified profile creation - no manual import needed"""
        self.logger.info("Using automated profile creation")
        return 'default'

    def load_profile(self, profile_name):
        """Load Chrome with undetected-chromedriver - basic version"""
        try:
            self.logger.info("Initializing Chrome...")
            
            # Initialize Chrome directly
            driver = uc.Chrome()
            
            # Set reasonable window size
            driver.set_window_size(1366, 768)
            
            self.logger.info("✅ Chrome initialized successfully!")
            return driver
            
        except Exception as e:
            self.logger.error(f"Failed to load Chrome: {str(e)}")
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