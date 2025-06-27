"""
Test script to verify the CMC AI scrolling fix
This script will test the improved scrolling logic for finding AI questions
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cmc_ai_scrolling():
    """Test the improved CMC AI scrolling functionality"""
    
    # Import our classes
    from autocrypto_social_bot.scrapers.cmc_scraper import CMCScraper
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    
    print("🧪 Testing CMC AI Scrolling Fix")
    print("=" * 50)
    
    # Setup Chrome with a basic profile
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Create CMC scraper instance
        profile_manager = ProfileManager()
        scraper = CMCScraper(driver, profile_manager)
        
        # Test coins with known AI questions
        test_coins = [
            ("Bitcoin", "BTC", "https://coinmarketcap.com/currencies/bitcoin/"),
            ("Ethereum", "ETH", "https://coinmarketcap.com/currencies/ethereum/"),
            ("Dogecoin", "DOGE", "https://coinmarketcap.com/currencies/dogecoin/")
        ]
        
        for coin_name, symbol, url in test_coins:
            print(f"\n🪙 Testing: {coin_name} ({symbol})")
            print("-" * 40)
            
            # Navigate to the coin page
            print(f"📍 Navigating to: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Try to find AI button with our improved method
            print("🔍 Searching for AI questions...")
            ai_button = scraper.find_ai_button(driver)
            
            if ai_button:
                button_text = ai_button.text.strip()
                print(f"✅ SUCCESS: Found AI button!")
                print(f"   Text: '{button_text}'")
                print(f"   Location: {ai_button.location}")
                print(f"   Size: {ai_button.size}")
                
                # Get scroll position to see where it was found
                scroll_position = driver.execute_script("return window.pageYOffset;")
                page_height = driver.execute_script("return document.body.scrollHeight;")
                print(f"   Found at scroll position: {scroll_position}px")
                print(f"   Page height: {page_height}px")
                print(f"   Position ratio: {scroll_position/page_height:.2%} down the page")
                
                # Highlight the element
                driver.execute_script("""
                    arguments[0].style.border = '3px solid green';
                    arguments[0].style.backgroundColor = 'lightgreen';
                """, ai_button)
                
            else:
                print("❌ FAILED: Could not find AI button")
                print("   This indicates the scrolling fix may need further adjustment")
            
            # Take a screenshot for debugging
            screenshot_name = f"cmc_scroll_test_{symbol}_{int(time.time())}.png"
            driver.save_screenshot(screenshot_name)
            print(f"📸 Screenshot saved: {screenshot_name}")
            
            # Wait before next test
            input("   Press Enter to continue to next coin...")
    
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Test completed")
        input("Press Enter to close browser...")
        driver.quit()

if __name__ == "__main__":
    test_cmc_ai_scrolling() 