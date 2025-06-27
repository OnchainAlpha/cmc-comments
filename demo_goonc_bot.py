#!/usr/bin/env python3
"""
Demo script for GOONC bot

This demonstrates how to use the CMC Coin Posts Bot specifically for GOONC.
It will:
1. Search for GOONC posts on CoinMarketCap
2. Find emoji buttons on those posts
3. Click the emoji buttons
4. Use account rotation
"""

import sys
import os
import time

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from coin_posts_bot import CMCCoinPostsBot

def demo_goonc_bot():
    """Demo the GOONC bot functionality"""
    bot = None
    
    try:
        print("🚀 GOONC Bot Demo Starting...")
        print("="*60)
        
        # Initialize the bot with account rotation
        print("1. Initializing CMC Coin Posts Bot...")
        bot = CMCCoinPostsBot(use_account_rotation=True)
        
        # Demo 1: Search and interact with GOONC posts
        print("\n" + "="*60)
        print("DEMO 1: Search and interact with GOONC posts")
        print("="*60)
        
        results = bot.run_coin_interaction_bot(
            coin_query="goonc",
            max_posts=8,  # Check up to 8 posts
            interaction_type="emoji"
        )
        
        if results['success']:
            print(f"\n✅ GOONC Bot Demo Successful!")
            print(f"   Posts Found: {results['posts_found']}")
            print(f"   Successful Interactions: {results['interaction_results'].get('successful_interactions', 0)}")
            print(f"   Failed Interactions: {results['interaction_results'].get('failed_interactions', 0)}")
            print(f"   Posts Without Buttons: {results['interaction_results'].get('posts_without_buttons', 0)}")
            
            # Print interaction details
            interactions = results['interaction_results'].get('interactions', [])
            if interactions:
                print(f"\n📋 INTERACTION DETAILS:")
                for interaction in interactions:
                    status = "✅ SUCCESS" if interaction['success'] else "❌ FAILED"
                    print(f"   Post {interaction['post_index']}: {status}")
                    print(f"      Author: {interaction['author']}")
                    print(f"      Time: {interaction['timestamp']}")
            
        else:
            print(f"\n❌ GOONC Bot Demo Failed!")
            print(f"   Error: {results.get('error', 'Unknown error')}")
            return False
        
        # Demo 2: Just get latest GOONC posts (no interaction)
        print("\n" + "="*60)
        print("DEMO 2: Get latest GOONC posts (no interaction)")
        print("="*60)
        
        posts = bot.get_latest_posts_for_coin("goonc", limit=15)
        
        if posts:
            print(f"\n📊 Found {len(posts)} GOONC posts:")
            for i, post in enumerate(posts[:5], 1):  # Show first 5
                emoji_status = "🎯" if post.get('has_interactions') else "⚪"
                print(f"   {i}. {emoji_status} {post['author']}: {post['content'][:60]}...")
            
            if len(posts) > 5:
                print(f"   ... and {len(posts) - 5} more posts")
                
            # Count posts with emoji buttons
            posts_with_emojis = len([p for p in posts if p.get('has_interactions')])
            print(f"\n🎯 Posts with emoji buttons: {posts_with_emojis}/{len(posts)}")
        else:
            print("❌ No GOONC posts found")
        
        print(f"\n🎉 GOONC Bot Demo Complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error in GOONC bot demo: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if bot:
            try:
                bot.close()
            except:
                pass

def interactive_goonc_bot():
    """Interactive mode for GOONC bot"""
    bot = None
    
    try:
        print("🎮 Interactive GOONC Bot Mode")
        print("="*40)
        
        # Get user preferences  
        max_posts = input("How many GOONC posts to process? (default: 5): ").strip()
        if not max_posts.isdigit():
            max_posts = 5
        else:
            max_posts = int(max_posts)
        
        interaction_choice = input("What interaction? (emoji/view) [default: emoji]: ").strip().lower()
        if interaction_choice not in ['emoji', 'view']:
            interaction_choice = 'emoji'
        
        use_rotation = input("Use account rotation? (y/n) [default: y]: ").strip().lower()
        use_rotation = use_rotation != 'n'
        
        print(f"\n⚙️ Settings:")
        print(f"   Max Posts: {max_posts}")
        print(f"   Interaction: {interaction_choice}")
        print(f"   Account Rotation: {'✅ ON' if use_rotation else '❌ OFF'}")
        
        input("\nPress Enter to start the bot...")
        
        # Initialize bot
        bot = CMCCoinPostsBot(use_account_rotation=use_rotation)
        
        if interaction_choice == 'view':
            # Just view posts
            posts = bot.get_latest_posts_for_coin("goonc", limit=max_posts)
            print(f"\n📋 Found {len(posts)} GOONC posts")
        else:
            # Run full interaction bot
            results = bot.run_coin_interaction_bot(
                coin_query="goonc",
                max_posts=max_posts,
                interaction_type=interaction_choice
            )
            
            if results['success']:
                print(f"\n✅ Interactive GOONC bot completed successfully!")
            else:
                print(f"\n❌ Interactive GOONC bot failed: {results.get('error')}")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error in interactive mode: {e}")
    finally:
        if bot:
            try:
                bot.close()
            except:
                pass

def main():
    """Main function with options"""
    print("🤖 GOONC Bot - CMC Community Interaction")
    print("="*50)
    print("Choose an option:")
    print("1. Run Demo (automatic)")
    print("2. Interactive Mode")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1/2/3): ").strip()
    
    if choice == '1':
        print("\n🚀 Starting Demo Mode...")
        demo_goonc_bot()
    elif choice == '2':
        print("\n🎮 Starting Interactive Mode...")
        interactive_goonc_bot()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run again.")

if __name__ == "__main__":
    main() 