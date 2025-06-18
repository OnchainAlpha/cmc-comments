import sys
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager
from utils.helpers import random_delay

def test_cmc_post():
    """Test posting a comment to CMC community"""
    profile_manager = ProfileManager()
    driver = None
    
    try:
        # Load the crypto profile
        print("\nLoading crypto profile...")
        driver = profile_manager.load_profile("crypto")
        
        # Navigate to CMC community
        print("\nNavigating to CMC community...")
        driver.get("https://coinmarketcap.com/community/")
        random_delay(3, 4)
        
        # Find and click the editor div
        print("\nLooking for editor...")
        editor_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                '#cmc-editor > div.sc-4c05d6ef-0.sc-702d4300-5.dlQYLv.dnXJWG.editor.inputs.communityHomepage > div.sc-83b82cd7-0.bmLonJ.base-editor > div'
            ))
        )
        print("✅ Found editor")
        editor_div.click()
        random_delay(2, 3)
        
        # Type the coin ticker
        symbol = "BTC"  # Test with Bitcoin
        print(f"\nTyping ${symbol}...")
        editor_div.send_keys(f"${symbol}")
        random_delay(2, 3)
        
        # Press Enter to select the ticker
        print("Selecting ticker...")
        editor_div.send_keys(Keys.ENTER)
        random_delay(1, 2)
        
        # Add message
        test_message = " - Test message from automated analysis bot. This is a test post."
        print("Adding message...")
        editor_div.send_keys(test_message)
        random_delay(2, 3)
        
        # Find and click post button
        print("\nLooking for post button...")
        post_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                '#cmc-editor > div.sc-702d4300-7.eIqxIO.editor-post-button'
            ))
        )
        print("✅ Found post button")
        
        print("Clicking post button...")
        post_button.click()
        
        # Wait to confirm post
        random_delay(5, 7)
        print("\n✅ Test complete!")
        
        # Keep browser open for manual inspection
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    test_cmc_post() 