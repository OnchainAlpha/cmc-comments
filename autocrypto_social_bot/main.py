import sys
import os
import time
import random
from selenium.common.exceptions import WebDriverException
from typing import Optional
from datetime import datetime
import pandas as pd
import logging
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager
from scrapers.cmc_scraper import CMCScraper
from utils.helpers import setup_logging, random_delay

class CryptoAIAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize profile manager
        self.profile_manager = ProfileManager()
        
        # Check if profile exists, if not create it
        if "cmc" not in self.profile_manager.list_profiles():
            print("\nNo CMC profile found. Let's create one...")
            self.profile_manager.import_existing_profile()
        
        # Load profile
        try:
            self.driver = self.profile_manager.load_profile("cmc")
        except Exception as e:
            print(f"\nError loading profile: {str(e)}")
            print("\nPlease run the script again after importing a profile.")
            sys.exit(1)
        
        # Initialize CMC scraper with the driver
        self.cmc_scraper = CMCScraper(self.driver)

    def run(self):
        """Main analysis loop"""
        try:
            # Wait for user to confirm login
            print("\n" + "="*60)
            print("🔐 LOGIN CHECK")
            print("="*60)
            print("\nPlease make sure you are logged in to CoinMarketCap")
            print("The browser window should be open now.")
            print("\nSteps:")
            print("1. Log in to your CMC account if not already")
            print("2. Verify you can see your profile/account")
            print("3. Press Enter here when ready")
            
            # Navigate to CMC first
            self.driver.get("https://coinmarketcap.com")
            time.sleep(3)
            
            input("\n✋ Press Enter when you're logged in and ready to continue...")
            print("\n✅ Starting AI review generation...\n")
            
            # Get trending coins
            self.logger.info("Getting trending coins...")
            trending_coins = self.cmc_scraper.get_trending_coins(limit=10)
            
            if not trending_coins:
                self.logger.error("Could not get trending coins")
                return
            
            print(f"\n{'='*60}")
            print(f"📊 Found {len(trending_coins)} trending coins")
            print(f"{'='*60}\n")
            
            # Track results
            successful_reviews = []
            failed_reviews = []
            
            # Process each coin with retries
            for i, coin in enumerate(trending_coins, 1):
                try:
                    print(f"\n{'='*60}")
                    print(f"[{i}/{len(trending_coins)}] Processing {coin['name']} (${coin['symbol']})")
                    print(f"{'='*60}")
                    print(f"💰 Current price: {coin['price']}")
                    print(f"📈 24h change: {coin['change_24h']}%")
                    
                    # Refresh page between coins to avoid state issues
                    if i > 1:
                        print("🔄 Refreshing browser state...")
                        self.driver.get("https://coinmarketcap.com")
                        time.sleep(2)
                    
                    # Try to get AI review with retry
                    ai_review = None
                    max_attempts = 2
                    
                    for attempt in range(max_attempts):
                        if attempt > 0:
                            print(f"\n🔄 Retry attempt {attempt + 1}...")
                            time.sleep(5)
                        
                        ai_review = self.cmc_scraper.get_ai_token_review(
                            coin['symbol'], 
                            coin['name'],
                            coin.get('url')
                        )
                        
                        if ai_review['success']:
                            break
                        else:
                            print(f"❌ Attempt {attempt + 1} failed: {ai_review.get('error', 'Unknown error')}")
                    
                    if ai_review and ai_review['success']:
                        self.process_ai_review(ai_review)
                        successful_reviews.append(coin['symbol'])
                        print(f"✅ Successfully processed {coin['symbol']}")
                    else:
                        failed_reviews.append({
                            'symbol': coin['symbol'],
                            'error': ai_review.get('error', 'Unknown error') if ai_review else 'No response'
                        })
                        print(f"❌ Failed to process {coin['symbol']}")
                    
                    # Delay between coins
                    if i < len(trending_coins):
                        delay = random.randint(10, 20)
                        print(f"\n⏳ Waiting {delay} seconds before next coin...")
                        for countdown in range(delay, 0, -1):
                            print(f"\r⏳ Next coin in {countdown} seconds...", end='', flush=True)
                            time.sleep(1)
                        print()  # New line after countdown
                        
                except Exception as e:
                    self.logger.error(f"Error processing coin: {str(e)}")
                    failed_reviews.append({
                        'symbol': coin['symbol'],
                        'error': str(e)
                    })
                    continue
            
            # Summary report
            print(f"\n{'='*60}")
            print("📊 ANALYSIS SUMMARY")
            print(f"{'='*60}")
            print(f"✅ Successful: {len(successful_reviews)} coins")
            if successful_reviews:
                print(f"   Coins: {', '.join(successful_reviews)}")
            print(f"❌ Failed: {len(failed_reviews)} coins")
            if failed_reviews:
                for fail in failed_reviews:
                    print(f"   - {fail['symbol']}: {fail['error']}")
            print(f"{'='*60}\n")
                    
        except Exception as e:
            self.logger.error(f"Error in analysis run: {str(e)}")
            print(f"\n❌ Fatal error: {str(e)}")
        finally:
            if self.driver:
                print("\n🔄 Closing browser...")
                self.driver.quit()

    def process_ai_review(self, ai_review: dict):
        """Process and save AI review"""
        try:
            print(f"\n{'='*60}")
            print(f"✅ AI REVIEW FOR {ai_review['coin_name']} (${ai_review['coin_symbol']})")
            print(f"{'='*60}")
            
            # Display question asked and TLDR
            if 'question_asked' in ai_review:
                print(f"\n📌 Question: {ai_review['question_asked']}")
            
            print(f"\n📝 TLDR SUMMARY:")
            print(f"{'-'*50}")
            print(ai_review['ai_review'])
            print(f"{'='*60}\n")
            
            # Create ai_reviews directory if it doesn't exist
            reviews_dir = os.path.join(os.path.dirname(__file__), 'ai_reviews')
            os.makedirs(reviews_dir, exist_ok=True)
            
            # Save to file with TLDR formatting preserved
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(reviews_dir, f"{ai_review['coin_symbol']}_{timestamp}.txt")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Coin: {ai_review['coin_name']} ({ai_review['coin_symbol']})\n")
                f.write(f"Timestamp: {ai_review['timestamp']}\n")
                f.write(f"Question Asked: {ai_review.get('question_asked', 'N/A')}\n")
                f.write(f"{'='*50}\n\n")
                f.write("AI TLDR SUMMARY:\n")
                f.write(f"{'='*50}\n")
                f.write(ai_review['ai_review'])
                f.write(f"\n{'='*50}\n")
            
            print(f"💾 TLDR saved to: {filename}")
            
            # Also save to CSV for tracking
            self._save_to_csv(ai_review)
            
        except Exception as e:
            self.logger.error(f"Error processing AI review: {str(e)}")

    def _save_to_csv(self, ai_review: dict):
        """Save AI review data to CSV for tracking"""
        try:
            # Create data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'analysis_data')
            os.makedirs(data_dir, exist_ok=True)
            csv_path = os.path.join(data_dir, 'ai_reviews.csv')
            
            # Extract first sentence for brief summary
            ai_text = ai_review['ai_review']
            brief_summary = ai_text.split('.')[0] + '.' if '.' in ai_text else ai_text[:100]
            
            # Prepare data for CSV
            review_data = {
                'timestamp': ai_review['timestamp'],
                'coin_name': ai_review['coin_name'],
                'coin_symbol': ai_review['coin_symbol'],
                'question_asked': ai_review.get('question_asked', 'N/A'),
                'brief_summary': brief_summary,
                'full_tldr': ai_review['ai_review'],
                'tldr_length': len(ai_review['ai_review'])
            }
            
            # Load existing CSV or create new one
            try:
                df = pd.read_csv(csv_path)
            except FileNotFoundError:
                df = pd.DataFrame(columns=review_data.keys())
            
            # Append new review
            df = pd.concat([df, pd.DataFrame([review_data])], ignore_index=True)
            
            # Save to CSV
            df.to_csv(csv_path, index=False)
            self.logger.info(f"Saved AI review data to CSV")
            
        except Exception as e:
            self.logger.error(f"Error saving to CSV: {str(e)}")

if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    print("\n" + "="*60)
    print("🤖 CMC AI Token Review Analyzer")
    print("="*60)
    print("\nThis bot will:")
    print("1. Find trending tokens on CoinMarketCap")
    print("2. Generate AI reviews for each token")
    print("3. Save the reviews for your analysis")
    print("\nStarting...\n")
    
    analyzer = CryptoAIAnalyzer()
    analyzer.run()
    
    print("\n✅ Analysis complete!")
    print("Check the 'ai_reviews' folder for generated reviews.") 