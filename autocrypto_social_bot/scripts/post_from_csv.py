import sys
import os
import pandas as pd
from datetime import datetime
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager
from scrapers.cmc_scraper import CMCScraper
from utils.helpers import random_delay

def post_pending_analyses():
    """Post pending analyses from CSV to CMC"""
    profile_manager = ProfileManager()
    driver = None
    
    try:
        # Get CSV path
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'analysis_data', 'coin_analysis.csv')
        
        print(f"\nLooking for CSV file at: {csv_path}")
        
        # Load CSV
        if not os.path.exists(csv_path):
            print("❌ CSV file not found!")
            return
            
        df = pd.read_csv(csv_path)
        print(f"Found CSV with {len(df)} entries")
        
        # Get last 5 unposted analyses
        pending = df[~df['posted']].tail(5)
        
        if pending.empty:
            print("No pending analyses to post")
            return
        
        print(f"\nFound {len(pending)} analyses to post")
        
        # Debug: Print what we're about to post
        for _, row in pending.iterrows():
            print(f"\nWill post for ${row['symbol']}:")
            print(f"Message length: {len(row['message'])} characters")
            print(f"First 100 chars: {row['message'][:100]}...")
        
        # Initialize driver
        print("\nInitializing driver...")
        driver = profile_manager.load_profile("crypto")
        cmc_scraper = CMCScraper(driver)
        
        # Post each analysis
        for idx, row in pending.iterrows():
            try:
                print(f"\n{'='*40}")
                print(f"Posting analysis for {row['name']} (${row['symbol']})")
                print(f"{'='*40}")
                
                # Make sure we have valid data
                if pd.isna(row['message']) or pd.isna(row['symbol']):
                    print("❌ Invalid data in CSV row, skipping...")
                    continue
                
                # Clean the message
                message = str(row['message']).strip()
                symbol = str(row['symbol']).strip()
                
                if not message or not symbol:
                    print("❌ Empty message or symbol, skipping...")
                    continue
                
                print(f"Posting message ({len(message)} chars)")
                
                success = cmc_scraper.post_community_comment(
                    symbol,
                    message
                )
                
                if success:
                    # Mark as posted in CSV
                    df.loc[idx, 'posted'] = True
                    df.to_csv(csv_path, index=False)
                    print(f"✅ Successfully posted and updated CSV")
                
                random_delay(5, 7)
                
            except Exception as e:
                print(f"Error posting {row['symbol']}: {str(e)}")
                continue
            
    except Exception as e:
        print(f"Error in posting process: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    post_pending_analyses() 