import sys
import os
import time
from selenium.webdriver.common.by import By

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager

def debug_ai_button():
    """Debug script to find AI button on CMC pages"""
    print("\n" + "="*60)
    print("🔍 CMC AI Button Debugger")
    print("="*60)
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Load profile
    try:
        print("\nLoading Chrome profile...")
        driver = profile_manager.load_profile("cmc")
        print("✅ Chrome loaded successfully")
    except Exception as e:
        print(f"❌ Error loading profile: {str(e)}")
        return
    
    try:
        # Test URLs
        test_coins = [
            ("Bitcoin", "BTC", "https://coinmarketcap.com/currencies/bitcoin/"),
            ("Cronos", "CRO", "https://coinmarketcap.com/currencies/cronos/"),
            ("Ethereum", "ETH", "https://coinmarketcap.com/currencies/ethereum/")
        ]
        
        for coin_name, coin_symbol, url in test_coins:
            print(f"\n{'='*60}")
            print(f"🪙 Testing: {coin_name} ({coin_symbol})")
            print(f"{'='*60}")
            
            # Navigate to coin page
            print(f"Navigating to: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Wait for login if needed
            if "bitcoin" in url:  # First coin only
                print("\n⚠️  Please log in to CMC if not already logged in")
                input("Press Enter when ready to continue...")
            
            print("\n🔍 Searching for AI-related elements...")
            
            # First find CMC AI section
            print("1. Looking for CMC AI section...")
            cmc_sections = driver.find_elements(By.XPATH, "//*[contains(text(), 'CMC AI')]")
            print(f"Found {len(cmc_sections)} CMC AI sections")
            
            # Search for question elements
            print("\n2. Looking for AI questions...")
            question_elements = []
            
            # Method 1: Find all elements with question marks
            all_questions = driver.find_elements(By.XPATH, "//*[contains(text(), '?')]")
            print(f"Found {len(all_questions)} elements with question marks")
            
            # Filter for actual questions
            for q in all_questions:
                try:
                    if (q.is_displayed() and 
                        len(q.text) > 10 and 
                        q.text.count('?') == 1 and
                        any(start in q.text for start in ["Why", "What", "How", "Will", "Is", "Can"])):
                        question_elements.append(("Question text", q))
                except:
                    continue
            
            # Method 2: Look near CMC AI sections
            for cmc_section in cmc_sections:
                try:
                    parent = cmc_section.find_element(By.XPATH, "./../..")
                    nearby_questions = parent.find_elements(By.XPATH, ".//*[contains(text(), '?')]")
                    for q in nearby_questions:
                        if q not in [elem[1] for elem in question_elements]:
                            question_elements.append(("Near CMC AI", q))
                except:
                    continue
            
            print(f"\n✅ Found {len(question_elements)} potential AI questions:")
            
            # Analyze each question
            for idx, (source, elem) in enumerate(question_elements):
                try:
                    print(f"\n--- Question {idx + 1} ({source}) ---")
                    print(f"Text: '{elem.text}'")
                    print(f"Tag: {elem.tag_name}")
                    print(f"Classes: {elem.get_attribute('class')}")
                    print(f"Clickable: {elem.is_enabled()}")
                    print(f"Size: {elem.size}")
                    
                    # Check if it's near CMC AI
                    is_near_cmc = False
                    for cmc in cmc_sections:
                        try:
                            if abs(elem.location['y'] - cmc.location['y']) < 300:
                                is_near_cmc = True
                                break
                        except:
                            pass
                    print(f"Near CMC AI: {is_near_cmc}")
                    
                    # Highlight the element
                    driver.execute_script("""
                        arguments[0].style.border = '3px solid blue';
                        arguments[0].style.backgroundColor = 'lightblue';
                    """, elem)
                    
                except Exception as e:
                    print(f"Error analyzing question: {str(e)}")
            
            # Take screenshot
            screenshot_name = f"debug_{coin_symbol}_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_name)
            print(f"\n📸 Screenshot saved: {screenshot_name}")
            
            # Try different scroll positions
            print("\n🔄 Checking different scroll positions...")
            for scroll_percent in [20, 40, 60, 80]:
                driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_percent/100});")
                time.sleep(2)
                
                # Look for new AI elements
                new_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'AI') or contains(text(), 'CMC AI')]")
                visible_new = [e for e in new_elements if e.is_displayed()]
                
                if visible_new:
                    print(f"At {scroll_percent}% scroll: Found {len(visible_new)} visible AI elements")
            
            input(f"\n✋ Press Enter to continue to next coin...")
        
        print("\n" + "="*60)
        print("📊 DEBUGGING COMPLETE")
        print("="*60)
        print("\nPlease check the screenshots and element information above")
        print("to identify the correct AI button pattern for each coin.")
        
    except Exception as e:
        print(f"\n❌ Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n✋ Press Enter to close the browser...")
        driver.quit()
        print("✅ Debug complete!")

if __name__ == "__main__":
    debug_ai_button() 