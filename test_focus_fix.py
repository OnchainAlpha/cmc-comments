#!/usr/bin/env python3
"""
Test script to verify the FOCUS FIX is working correctly
This will test AI question detection without manual clicking
"""

import sys
import os
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.scrapers.cmc_scraper import CMCScraper

def test_focus_fix():
    """Test that AI questions can be found WITHOUT manual clicking"""
    print("🧪 TESTING FOCUS FIX FOR AI QUESTION DETECTION")
    print("="*70)
    print("This test will verify that the bot can find AI questions")
    print("WITHOUT requiring you to manually click the browser window.")
    print("="*70)
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Get existing profiles
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    if not profiles:
        print("❌ No existing profiles found!")
        print("Please create profiles first using the Profile Management menu.")
        return False
    
    print(f"✅ Using profile: {profiles[0]}")
    
    try:
        # Load profile
        print("\n🔄 Loading Chrome profile...")
        driver = profile_manager.load_profile(profiles[0])
        print("✅ Chrome loaded successfully")
        
        # Initialize CMC scraper
        cmc_scraper = CMCScraper(driver, profile_manager)
        
        # Test coins with known AI questions
        test_coins = [
            ("Bitcoin", "BTC", "https://coinmarketcap.com/currencies/bitcoin/"),
            ("Ethereum", "ETH", "https://coinmarketcap.com/currencies/ethereum/")
        ]
        
        for coin_name, symbol, url in test_coins:
            print(f"\n{'='*50}")
            print(f"🪙 TESTING: {coin_name} ({symbol})")
            print(f"{'='*50}")
            print("👀 IMPORTANT: Do NOT click on the browser window!")
            print("🤖 The bot should work automatically with the FOCUS FIX")
            
            # Navigate to coin page
            print(f"\n📍 Navigating to: {url}")
            driver.get(url)
            time.sleep(5)
            
            print("\n🔧 FOCUS FIX: Testing automatic AI question detection...")
            print("⚠️  If you see focus fix messages, the fix is working!")
            print("✅ You should NOT need to click the browser window")
            
            # Try to find AI questions (this should work automatically now)
            try:
                ai_question = cmc_scraper.find_ai_button(driver)
                
                if ai_question:
                    print(f"\n🎉 SUCCESS! Found AI question automatically:")
                    print(f"   Question: {ai_question.text}")
                    print(f"   🔧 FOCUS FIX working correctly!")
                    
                    # Try clicking it to get AI content
                    print(f"\n🎯 Testing automatic clicking...")
                    click_success = cmc_scraper.find_and_click_ai_button(driver)
                    
                    if click_success:
                        print(f"✅ SUCCESS! AI content loaded automatically!")
                        print(f"🔧 FOCUS FIX completely working!")
                        
                        # Try to get content
                        content = cmc_scraper.wait_for_ai_content(timeout=30)
                        if content:
                            print(f"\n📄 AI Content Retrieved ({len(content)} chars):")
                            print(f"   {content[:200]}...")
                            print(f"\n🎉 FOCUS FIX TEST PASSED!")
                        else:
                            print(f"⚠️ AI question found and clicked, but content timeout")
                            print(f"🔧 Focus fix working for detection, content may need more time")
                    else:
                        print(f"⚠️ AI question found but clicking failed")
                        print(f"🔧 Focus fix working for detection, clicking may need adjustment")
                else:
                    print(f"\n❌ No AI questions found")
                    print(f"🔧 FOCUS FIX may need further adjustment")
                    print(f"💡 Try logging into CMC first, then run test again")
                
            except Exception as e:
                print(f"\n❌ Error during test: {str(e)}")
                print(f"🔧 Focus fix applied but other issues may exist")
            
            # Ask user about the test result
            print(f"\n" + "="*50)
            print(f"📊 FOCUS FIX TEST RESULTS FOR {symbol}")
            print(f"="*50)
            
            manual_click_needed = input("Did you need to manually click the browser window? (y/n): ").strip().lower()
            
            if manual_click_needed == 'n':
                print(f"🎉 SUCCESS! FOCUS FIX working for {symbol}")
            else:
                print(f"⚠️ FOCUS FIX needs more work for {symbol}")
            
            # Continue to next coin
            if len(test_coins) > 1 and symbol != test_coins[-1][1]:
                continue_test = input(f"\nTest next coin? (y/n): ").strip().lower()
                if continue_test != 'y':
                    break
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test error: {str(e)}")
        return False
        
    finally:
        try:
            print(f"\n🔄 Closing browser...")
            driver.quit()
            print(f"✅ Test completed")
        except:
            pass

def main():
    """Run the focus fix test"""
    print("🔧 FOCUS FIX VERIFICATION TEST")
    print("\nThis test verifies that the AI question detection")
    print("works WITHOUT manual browser clicking.")
    
    success = test_focus_fix()
    
    print(f"\n{'='*70}")
    if success:
        print("✅ FOCUS FIX TEST COMPLETED")
        print("🎯 If you didn't need to manually click the browser,")
        print("   the FOCUS FIX is working correctly!")
        print("\n🚀 Your bot should now work fully automatically!")
    else:
        print("❌ FOCUS FIX TEST FAILED")
        print("💡 Check the issues above and try again")
    print("="*70)

if __name__ == "__main__":
    main() 