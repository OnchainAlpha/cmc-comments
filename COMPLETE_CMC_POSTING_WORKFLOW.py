#!/usr/bin/env python3
"""
Complete CMC Posting Workflow with Automatic Account Creation

This script demonstrates the complete end-to-end workflow of how our repository
leverages SimpleLogin to create fresh email aliases and automatically register
new CoinMarketCap accounts for every posting session.
"""

import sys
import os
import time
import random
from typing import List, Dict

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autocrypto_social_bot'))

from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager
from autocrypto_social_bot.services.account_manager import Account
from autocrypto_social_bot.scrapers.cmc_scraper import CMCScraper

class AutomatedCMCPoster:
    """
    Complete automated CMC posting system with fresh account creation
    """
    
    def __init__(self):
        self.enhanced_manager = EnhancedProfileManager()
        self.current_account = None
        self.current_driver = None
        self.posts_this_session = 0
        self.max_posts_per_account = 10  # Rotate after 10 posts
        
        print("🚀 Automated CMC Poster initialized")
    
    def start_fresh_session(self) -> bool:
        """Start a fresh posting session with a new account"""
        try:
            print("\n" + "="*60)
            print("🔄 STARTING FRESH POSTING SESSION")
            print("="*60)
            
            # Step 1: Create fresh account with SimpleLogin alias
            print("📧 Step 1: Creating SimpleLogin alias...")
            account, driver = self.enhanced_manager.create_fresh_account_with_profile("cmc")
            
            print(f"   ✅ Created alias: {account.email_alias}")
            print(f"   👤 Username: {account.username}")
            print(f"   🌐 Chrome profile: {account.profile_name}")
            
            # Step 2: Register CMC account
            print("\n📝 Step 2: Registering CMC account...")
            login_success = self.enhanced_manager.login_to_platform("cmc")
            
            if login_success:
                print("   ✅ CMC account registered and logged in!")
            else:
                print("   ⚠️ Registration pending email verification")
            
            # Step 3: Initialize CMC scraper with the driver
            print("\n🔧 Step 3: Initializing CMC scraper...")
            self.cmc_scraper = CMCScraper(driver=driver)
            
            # Store current state
            self.current_account = account
            self.current_driver = driver
            self.posts_this_session = 0
            
            print("✅ Fresh session ready for posting!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start fresh session: {e}")
            return False
    
    def post_comment(self, comment: str, coin_symbol: str = "BTC") -> bool:
        """Post a comment using the current fresh account"""
        try:
            print(f"\n💬 Posting comment as {self.current_account.username}...")
            print(f"   📝 Comment: {comment[:50]}...")
            print(f"   🎯 Target: {coin_symbol}")
            
            # Use CMC scraper to post comment
            success = self.cmc_scraper.post_community_comment(coin_symbol, comment)
            
            if success:
                self.posts_this_session += 1
                print(f"   ✅ Comment posted! (Session: {self.posts_this_session}/{self.max_posts_per_account})")
                
                # Update account usage in database
                self.enhanced_manager.account_manager.database.update_account_usage(
                    self.current_account.id, 
                    success=True
                )
                
                return True
            else:
                print("   ❌ Failed to post comment")
                return False
                
        except Exception as e:
            print(f"   ❌ Error posting comment: {e}")
            return False
    
    def should_rotate_account(self) -> bool:
        """Check if we should rotate to a fresh account"""
        if self.posts_this_session >= self.max_posts_per_account:
            print(f"🔄 Account hit post limit ({self.posts_this_session}/{self.max_posts_per_account})")
            return True
        
        # Check if account got suspended/banned
        if self.current_account and self.current_account.status != "active":
            print(f"⚠️ Account status changed to: {self.current_account.status}")
            return True
        
        return False
    
    def rotate_to_fresh_account(self) -> bool:
        """Rotate to a fresh account with new SimpleLogin alias"""
        try:
            print("\n🔄 ROTATING TO FRESH ACCOUNT")
            print("-" * 40)
            
            # Close current session
            if self.current_driver:
                self.current_driver.quit()
            
            # Get fresh account (creates new one if needed)
            account, driver = self.enhanced_manager.rotate_to_fresh_account("cmc", self.max_posts_per_account)
            
            print(f"   📧 Fresh alias: {account.email_alias}")
            print(f"   👤 Username: {account.username}")
            print(f"   📊 Posts today: {account.posts_today}")
            
            # Login to CMC with fresh account
            self.enhanced_manager.current_account = account
            self.enhanced_manager.current_driver = driver
            
            login_success = self.enhanced_manager.login_to_platform("cmc")
            if login_success:
                print("   ✅ Logged in with fresh account!")
            
            # Reinitialize scraper
            self.cmc_scraper = CMCScraper(driver=driver)
            
            # Update state
            self.current_account = account
            self.current_driver = driver
            self.posts_this_session = 0
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to rotate account: {e}")
            return False
    
    def run_posting_campaign(self, comments_list: List[Dict]) -> Dict:
        """Run a complete posting campaign with automatic account rotation"""
        
        print("🚀 STARTING AUTOMATED CMC POSTING CAMPAIGN")
        print("=" * 60)
        
        results = {
            'total_comments': len(comments_list),
            'successful_posts': 0,
            'failed_posts': 0,
            'accounts_used': 0,
            'accounts_created': 0
        }
        
        # Start with fresh session
        if not self.start_fresh_session():
            print("❌ Failed to start initial session")
            return results
        
        results['accounts_created'] += 1
        results['accounts_used'] += 1
        
        # Process each comment
        for i, comment_data in enumerate(comments_list, 1):
            print(f"\n📝 Processing comment {i}/{len(comments_list)}")
            
            # Check if we need to rotate account
            if self.should_rotate_account():
                if self.rotate_to_fresh_account():
                    results['accounts_used'] += 1
                    # Check if we created a new account vs. reused existing
                    if self.current_account.posts_today == 0:
                        results['accounts_created'] += 1
                else:
                    print("❌ Failed to rotate account, skipping comment")
                    results['failed_posts'] += 1
                    continue
            
            # Post the comment
            comment_text = comment_data.get('text', '')
            coin_symbol = comment_data.get('symbol', 'BTC')
            
            if self.post_comment(comment_text, coin_symbol):
                results['successful_posts'] += 1
            else:
                results['failed_posts'] += 1
            
            # Add delay between posts
            delay = random.uniform(30, 90)  # 30-90 seconds
            print(f"⏱️ Waiting {delay:.1f}s before next post...")
            time.sleep(delay)
        
        # Final statistics
        self.print_campaign_results(results)
        
        return results
    
    def print_campaign_results(self, results: Dict):
        """Print comprehensive campaign results"""
        print("\n" + "=" * 60)
        print("📊 CAMPAIGN RESULTS SUMMARY")
        print("=" * 60)
        
        success_rate = (results['successful_posts'] / results['total_comments']) * 100
        
        print(f"📝 Total Comments Attempted: {results['total_comments']}")
        print(f"✅ Successful Posts: {results['successful_posts']}")
        print(f"❌ Failed Posts: {results['failed_posts']}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"👥 Accounts Used: {results['accounts_used']}")
        print(f"🆕 New Accounts Created: {results['accounts_created']}")
        
        # Get account statistics
        stats = self.enhanced_manager.get_account_rotation_stats()
        print(f"\n🔍 Account Details:")
        print(f"   Current Account: {stats['current_account']['username']}")
        print(f"   Posts Today: {stats['current_account']['posts_today']}")
        print(f"   Success Rate: {stats['current_account']['success_rate']:.1f}%")
        
        print("\n✅ Campaign completed!")
    
    def cleanup(self):
        """Clean up resources"""
        if self.current_driver:
            self.current_driver.quit()
        self.enhanced_manager.cleanup()

def demo_complete_workflow():
    """Demonstrate the complete workflow"""
    
    # Sample comments to post
    comments_to_post = [
        {"text": "Bitcoin looking strong! 🚀 Great fundamentals.", "symbol": "BTC"},
        {"text": "Ethereum's development is impressive. Long-term bullish!", "symbol": "ETH"},
        {"text": "Solana ecosystem growing rapidly. Exciting times ahead.", "symbol": "SOL"},
        {"text": "DeFi innovation continues to amaze. The future is bright!", "symbol": "BTC"},
        {"text": "Crypto adoption accelerating globally. Mass adoption incoming!", "symbol": "ETH"},
        {"text": "Blockchain technology revolutionizing finance industry.", "symbol": "BTC"},
        {"text": "Smart contracts enabling new possibilities daily.", "symbol": "ETH"},
        {"text": "Decentralization is the way forward for finance.", "symbol": "BTC"},
        {"text": "Web3 infrastructure maturing nicely. Building the future!", "symbol": "SOL"},
        {"text": "Institutional adoption increasing steadily. Bullish signals everywhere!", "symbol": "BTC"},
        {"text": "Layer 2 solutions scaling effectively. Ethereum ecosystem thriving.", "symbol": "ETH"},
        {"text": "NFT utility expanding beyond collectibles. Real world use cases emerging.", "symbol": "SOL"},
        {"text": "Cross-chain interoperability improving. Seamless multi-chain future ahead.", "symbol": "BTC"},
        {"text": "Regulatory clarity increasing globally. Positive developments for crypto.", "symbol": "ETH"},
        {"text": "Developer activity at all-time highs. Innovation never stops in crypto!", "symbol": "BTC"}
    ]
    
    try:
        # Initialize poster
        poster = AutomatedCMCPoster()
        
        # Run the campaign
        results = poster.run_posting_campaign(comments_to_post)
        
        # Show final results
        print(f"\n🎯 FINAL SUMMARY:")
        print(f"   📧 Created {results['accounts_created']} fresh SimpleLogin aliases")
        print(f"   👤 Registered {results['accounts_created']} new CMC accounts")
        print(f"   💬 Posted {results['successful_posts']} comments successfully")
        print(f"   📈 Campaign success rate: {(results['successful_posts']/results['total_comments'])*100:.1f}%")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    finally:
        if 'poster' in locals():
            poster.cleanup()

if __name__ == "__main__":
    print("🎯 CMC Posting Workflow Demonstration")
    print("=" * 60)
    print()
    print("This script demonstrates how our repository:")
    print("1. 📧 Creates fresh SimpleLogin email aliases")
    print("2. 👤 Registers new CMC accounts automatically") 
    print("3. 🔄 Rotates accounts to avoid detection")
    print("4. 💬 Posts comments with fresh identities")
    print("5. 📊 Tracks performance and statistics")
    print()
    
    # Check if SimpleLogin is configured
    from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
    config = SimpleLoginConfig()
    
    if not config.is_configured():
        print("❌ SimpleLogin not configured!")
        print("   Run: python setup_simplelogin.py")
        exit(1)
    
    print("✅ SimpleLogin configured - starting demo...")
    demo_complete_workflow() 