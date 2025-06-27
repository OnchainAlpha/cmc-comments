#!/usr/bin/env python3
"""
Demo script for CMC Like Stacking Bot
Tests the like stacking functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from like_stacking_bot import CMCLikeStackingBot
    
    def main():
        print("🎯 CMC Like Stacking Bot Demo")
        print("="*40)
        print("This bot rotates through ALL your accounts to like the same posts")
        print("Result: Multiple likes stacked on each post!")
        
        # Initialize bot
        bot = CMCLikeStackingBot()
        
        if len(bot.cmc_profiles) == 0:
            print("\n❌ No CMC profiles found. Please create profiles first.")
            return
        
        print(f"\n✅ Found {len(bot.cmc_profiles)} CMC accounts available for stacking")
        
        # Get demo settings
        coin = input("\nEnter coin to stack likes on (default: GOONC): ").strip()
        if not coin:
            coin = "GOONC"
        
        max_posts = input("Max posts per account (default: 8): ").strip()
        try:
            max_posts = int(max_posts) if max_posts else 8
        except:
            max_posts = 8
        
        # Show the plan
        print(f"\n🚀 LIKE STACKING DEMO PLAN:")
        print(f"   Target Coin: {coin.upper()}")
        print(f"   Max Posts Per Account: {max_posts}")
        print(f"   Accounts: {len(bot.cmc_profiles)}")
        print(f"   Expected Max Total Likes: {max_posts * len(bot.cmc_profiles)}")
        print(f"\n💡 How it works:")
        print(f"   1. Each account searches for {coin.upper()} posts")
        print(f"   2. Each account likes up to {max_posts} posts")
        print(f"   3. Same posts get liked by multiple accounts")
        print(f"   4. Result: Stacked engagement!")
        
        proceed = input(f"\nRun like stacking demo for {coin.upper()}? (y/n): ").strip().lower()
        
        if proceed == 'y':
            print(f"\n🎯 Starting like stacking for {coin.upper()}...")
            
            results = bot.stack_likes_on_coin(coin, max_posts)
            
            if results['success']:
                print(f"\n🎉 LIKE STACKING DEMO SUCCESS!")
                print("="*50)
                print(f"✅ Total Likes Stacked: {results['total_likes']}")
                print(f"📊 Posts Found: {results['posts_found']}")
                print(f"👥 Accounts Used: {results['accounts_used']}")
                print(f"📈 Average Likes Per Post: {results['avg_likes_per_post']:.1f}")
                
                if results['posts_found'] > 0:
                    efficiency = (results['total_likes'] / (results['posts_found'] * results['accounts_used'])) * 100
                    print(f"🎯 Stacking Efficiency: {efficiency:.1f}%")
                    
                    print(f"\n💡 What this means:")
                    if results['avg_likes_per_post'] > 1:
                        print(f"   🔥 SUCCESS: Posts got multiple likes on average!")
                        print(f"   🎯 Each post received {results['avg_likes_per_post']:.1f} likes")
                    else:
                        print(f"   ⚠️ Limited stacking: Most posts got 1 like each")
                        print(f"   💡 Try increasing max_posts or check for duplicate posts")
            else:
                print(f"\n❌ Like stacking failed: {results.get('error')}")
        else:
            print("❌ Demo cancelled")
        
        bot.close()
        print("\n✅ Demo completed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure like_stacking_bot.py exists and has the correct dependencies")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main() 