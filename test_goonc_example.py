#!/usr/bin/env python3
"""
Simple example of using the CMC Coin Posts Bot for GOONC
"""

from coin_posts_bot import CMCCoinPostsBot

def example_goonc_search():
    """Example: Search for GOONC posts and click emoji buttons"""
    
    # Initialize the bot
    print("🚀 Initializing GOONC bot...")
    bot = CMCCoinPostsBot(use_account_rotation=True)
    
    try:
        # Method 1: Full interaction (search + click emojis)
        print("\n📍 Method 1: Search and interact with GOONC posts")
        results = bot.run_coin_interaction_bot(
            coin_query="goonc",
            max_posts=5,
            interaction_type="emoji"
        )
        
        if results['success']:
            print(f"✅ Success! Clicked emojis on {results['interaction_results']['successful_interactions']} posts")
        else:
            print(f"❌ Failed: {results['error']}")
        
        # Method 2: Just get posts (no interaction)
        print("\n📍 Method 2: Just get latest GOONC posts")
        posts = bot.get_latest_posts_for_coin("goonc", limit=10)
        print(f"📊 Found {len(posts)} GOONC posts")
        
        # Show posts with emoji buttons available
        emoji_posts = [p for p in posts if p.get('has_interactions')]
        print(f"🎯 Posts with emoji buttons: {len(emoji_posts)}")
        
    finally:
        # Always clean up
        bot.close()

if __name__ == "__main__":
    example_goonc_search() 