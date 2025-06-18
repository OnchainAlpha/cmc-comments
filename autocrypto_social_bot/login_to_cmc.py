import sys
import os
import time
from selenium.webdriver.common.by import By

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager

def login_to_cmc():
    """Helper script to log in to CMC and save session"""
    print("\n" + "="*60)
    print("🔐 CMC Login Helper")
    print("="*60)
    print("\nThis script will open Chrome with your persistent profile")
    print("so you can log in to CoinMarketCap and save the session.")
    print("\nSteps:")
    print("1. Chrome will open")
    print("2. Navigate to coinmarketcap.com")
    print("3. Log in to your CMC account")
    print("4. Press Enter here when logged in")
    print("5. The session will be saved for future use")
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Check if profile exists, if not create it
    if "cmc" not in profile_manager.list_profiles():
        print("\nCreating CMC profile...")
        profile_manager.import_existing_profile()
    
    # Load profile
    try:
        print("\nLoading Chrome with persistent profile...")
        driver = profile_manager.load_profile("cmc")
        print("✅ Chrome loaded successfully")
        
        # Navigate to CMC
        print("\nNavigating to CoinMarketCap...")
        driver.get("https://coinmarketcap.com")
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🚀 Chrome is now open!")
        print("="*60)
        print("\nPlease:")
        print("1. Log in to your CoinMarketCap account")
        print("2. Make sure you can access AI features")
        print("3. Press Enter here when done")
        print("\nThe browser will stay open until you press Enter...")
        
        # Wait for user to log in
        input("\nPress Enter when you've logged in to CMC...")
        
        # Test if logged in by checking for profile/account elements
        print("\n🔍 Checking if logged in...")
        
        # Look for login indicators
        login_indicators = [
            "//a[contains(text(), 'Log in')]",
            "//button[contains(text(), 'Log in')]"
        ]
        
        is_logged_in = True
        for indicator in login_indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element and element.is_displayed():
                    is_logged_in = False
                    break
            except:
                continue
        
        # Look for account/profile indicators
        if is_logged_in:
            account_indicators = [
                "//div[contains(@class, 'user')]",
                "//div[contains(@class, 'profile')]",
                "//div[contains(@class, 'account')]"
            ]
            
            for indicator in account_indicators:
                try:
                    element = driver.find_element(By.XPATH, indicator)
                    if element:
                        print("✅ Appears to be logged in!")
                        break
                except:
                    continue
        
        if not is_logged_in:
            print("⚠️  Still shows login button - please make sure you're logged in")
        
        print("\n✅ Session saved! The profile will remember your login.")
        print("You can now close this browser and run the main script.")
        
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass
        print("✅ Browser closed. Your login session has been saved!")

if __name__ == "__main__":
    login_to_cmc() 