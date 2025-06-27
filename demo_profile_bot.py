#!/usr/bin/env python3
"""
Demo script for CMC Profile Interaction Bot
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from profile_bot import CMCProfileInteractionBot
    
    def main():
        print("🤖 CMC Profile Interaction Bot Demo")
        print("="*40)
        
        # Initialize bot
        bot = CMCProfileInteractionBot(use_account_rotation=True)
        
        # Add the OnchainBureau profile
        print("\n📝 Adding OnchainBureau profile...")
        success = bot.add_manual_profile(
            "https://coinmarketcap.com/community/profile/Onchainbureaudotcom/",
            "OnchainBureau"
        )
        
        if not success:
            print("❌ Failed to add profile")
            return
        
        # Show stored profiles
        bot.list_stored_profiles()
        
        # Ask if user wants to process profiles
        choice = input("\nProcess the OnchainBureau profile? (y/n): ").strip().lower()
        
        if choice == 'y':
            print("\n🚀 Processing OnchainBureau profile...")
            results = bot.visit_profile_and_interact(
                "https://coinmarketcap.com/community/profile/Onchainbureaudotcom/",
                max_posts=15
            )
            
            if results['success']:
                print(f"\n🎉 SUCCESS!")
                print(f"   Posts Found: {results['posts_found']}")
                print(f"   Successful Interactions: {results['interaction_results'].get('successful_interactions', 0)}")
                print(f"   Failed Interactions: {results['interaction_results'].get('failed_interactions', 0)}")
                print(f"   Posts Without Buttons: {results['interaction_results'].get('posts_without_buttons', 0)}")
                
                if results['posts_found'] > 0:
                    success_rate = (results['interaction_results'].get('successful_interactions', 0) / results['posts_found']) * 100
                    print(f"   Success Rate: {success_rate:.1f}%")
            else:
                print(f"❌ Failed: {results.get('error')}")
        
        # Clean up
        bot.close()
        print("\n✅ Demo completed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure profile_bot.py exists and has the correct dependencies")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    main() 