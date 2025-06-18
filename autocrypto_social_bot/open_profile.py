import os
import sys
import subprocess
from pathlib import Path

def open_chrome_profile():
    # Get the user's home directory
    home_dir = str(Path.home())
    
    # Path to the CMC profile
    profile_path = os.path.join(home_dir, 'chrome_profiles', 'cmc')
    
    # Check if profile exists
    if not os.path.exists(profile_path):
        print(f"Error: Profile not found at {profile_path}")
        print("Please run setup_profile.py first to create the profile.")
        return
    
    # Chrome executable path for Windows
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print("Error: Chrome not found in default locations.")
        print("Please make sure Chrome is installed.")
        return
    
    # Command to open Chrome with the profile
    cmd = f'"{chrome_path}" --user-data-dir="{profile_path}"'
    
    print("\nOpening Chrome with CMC profile...")
    print(f"Profile path: {profile_path}")
    print("\nYou can now use Chrome normally. The profile will be saved for future use.")
    
    # Open Chrome
    subprocess.Popen(cmd, shell=True)

if __name__ == "__main__":
    open_chrome_profile() 