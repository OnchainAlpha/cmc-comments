import sys
import os
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager
from scrapers.cmc_scraper import CMCScraper
from utils.helpers import setup_logging

def test_ai_review():
    """Test the AI review functionality"""
    print("\n" + "="*60)
    print("🧪 Testing CMC AI Review Feature")
    print("="*60)
    
    # Setup logging
    setup_logging()
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Check if profile exists
    if "cmc" not in profile_manager.list_profiles():
        print("\nNo CMC profile found. Please run import_profile.py first.")
        return
    
    # Load profile
    try:
        print("\nLoading Chrome profile...")
        driver = profile_manager.load_profile("cmc")
        print("✅ Chrome loaded successfully")
    except Exception as e:
        print(f"❌ Error loading profile: {str(e)}")
        return
    
    try:
        # Navigate to CMC and wait for login
        print("\nNavigating to CoinMarketCap...")
        driver.get("https://coinmarketcap.com")
        time.sleep(3)
        
        print("\n" + "="*60)
        print("🔐 LOGIN CHECK")
        print("="*60)
        print("\nPlease make sure you are logged in to CoinMarketCap")
        print("\nSteps:")
        print("1. Log in to your CMC account if not already")
        print("2. Verify you can see your profile/account")
        print("3. Press Enter here when ready")
        
        input("\n✋ Press Enter when you're logged in and ready to test...")
        print("\n✅ Starting test...\n")
        
        # Initialize CMC scraper
        cmc_scraper = CMCScraper(driver)
        
        # Test with Cronos (the example the user mentioned)
        print(f"\n{'='*60}")
        print("Test 1: Cronos (CRO)")
        print(f"{'='*60}")
        ai_review = cmc_scraper.get_ai_token_review(
            "CRO", 
            "Cronos", 
            "https://coinmarketcap.com/currencies/cronos/"
        )
        
        if ai_review['success']:
            print(f"\n✅ Successfully got AI review!")
            print(f"URL used: {ai_review.get('url_used', 'N/A')}")
            print(f"\nReview content ({len(ai_review['ai_review'])} chars):")
            print("-" * 60)
            print(ai_review['ai_review'][:500] + "..." if len(ai_review['ai_review']) > 500 else ai_review['ai_review'])
            print("-" * 60)
        else:
            print(f"\n❌ Failed to get AI review: {ai_review.get('error', 'Unknown error')}")
        
        # Delay between tests
        print("\n⏳ Waiting 15 seconds before next test...")
        time.sleep(15)
        
        # Also test without URL to see fallback behavior
        print(f"\n{'='*60}")
        print("Test 2: Bitcoin (BTC)")
        print(f"{'='*60}")
        ai_review_2 = cmc_scraper.get_ai_token_review("BTC", "Bitcoin")
        
        if ai_review_2['success']:
            print(f"\n✅ Successfully got AI review for Bitcoin!")
            print(f"URL used: {ai_review_2.get('url_used', 'N/A')}")
            print(f"\nReview preview ({len(ai_review_2['ai_review'])} chars):")
            print("-" * 60)
            print(ai_review_2['ai_review'][:500] + "...")
            print("-" * 60)
        else:
            print(f"\n❌ Failed to get AI review for Bitcoin: {ai_review_2.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🔄 Closing browser...")
        driver.quit()
        print("✅ Test complete!")

if __name__ == "__main__":
    test_ai_review() 