# CMC Coin Posts Bot

A specialized bot for searching and interacting with specific coin posts on CoinMarketCap community.

## Features

🔍 **Search Functionality**
- Search for posts about specific coins (e.g., "goonc", "BTC", "ETH")
- Navigate to CMC community search pages
- Extract post data including content, author, and interaction buttons

🎯 **Interaction Capabilities**
- Find and click emoji buttons on posts (the smile button you mentioned)
- Support for multiple interaction types
- Robust clicking with fallback methods

🔄 **Account Rotation**
- Integrates with your existing account rotation system
- Automatically switches profiles to avoid rate limiting
- Works with all your existing CMC profiles

## Files Created

1. **`coin_posts_bot.py`** - Main bot class with all functionality
2. **`demo_goonc_bot.py`** - Demo script specifically for GOONC

## How to Use

### Quick Start - GOONC Demo

```bash
python demo_goonc_bot.py
```

This will show you a menu with options:
1. **Run Demo** - Automatically searches for GOONC posts and clicks emoji buttons
2. **Interactive Mode** - Let you customize settings
3. **Exit**

### Using the Bot Programmatically

```python
from coin_posts_bot import CMCCoinPostsBot

# Initialize the bot
bot = CMCCoinPostsBot(use_account_rotation=True)

# Search and interact with posts
results = bot.run_coin_interaction_bot(
    coin_query="goonc",
    max_posts=10,
    interaction_type="emoji"
)

# Just get posts without interaction
posts = bot.get_latest_posts_for_coin("goonc", limit=20)

# Clean up
bot.close()
```

## Emoji Button Detection

The bot specifically looks for the emoji button you mentioned:
- `<div data-test="post-emoji-action">` - Your exact HTML structure
- SVG elements with `href="#SMILE"` - The smile icon
- Generic emoji and reaction buttons

## Account Rotation Integration

The bot uses your existing account rotation system:
- Automatically loads CMC profiles (profiles starting with `cmc_profile_`)
- Switches profiles after interactions to avoid rate limiting
- Maintains session state across rotations

## Example Output

```
🤖 STARTING COIN INTERACTION BOT
==================================================
Target Coin: GOONC
Max Posts: 5
Interaction: emoji
==================================================

🔍 SEARCHING FOR POSTS ABOUT: GOONC
============================================================
1. Navigating to search: https://coinmarketcap.com/community/search/latest/?q=goonc
2. Waiting for search results...
✅ Found 8 posts using selector: [data-test*='post']
3. Processing 5 posts...

   📝 Processing post 1/5
   ✅ Extracted post data successfully

🎯 INTERACTING WITH 5 POSTS
==================================================

🎯 Interacting with post 1/5
   📝 Content preview: This is a post about GOONC...
   👤 Author: CryptoTrader123
     ✅ Click method 1 successful
   ✅ Successfully performed emoji interaction

📊 INTERACTION SUMMARY
==============================
Total Posts: 5
Successful: 4
Failed: 1
No Buttons: 0
Success Rate: 80.0%

🎉 BOT RUN COMPLETE!
   Found: 5 posts
   Successful interactions: 4
   Success rate: 80.0%
```

## Requirements

- Your existing CMC profiles must be set up
- The bot will automatically use your account rotation system
- Requires the same dependencies as your existing bot

## Troubleshooting

**No posts found?**
- Check if the coin symbol is correct
- Verify CMC community search is working
- Try with a more common coin like "BTC" first

**Emoji buttons not found?**
- The bot tries multiple selectors to find emoji buttons
- Some posts may not have interaction buttons
- Check the browser console for any JavaScript errors

**Account rotation not working?**
- Ensure you have CMC profiles created (names starting with `cmc_profile_`)
- Check that your existing account rotation system is functional

## Customization

You can easily modify the bot for different interactions:

```python
# Add new interaction types
def _perform_interaction(self, post_data: Dict, interaction_type: str) -> bool:
    if interaction_type == "emoji":
        return self._click_emoji_button(post_data['emoji_button'])
    elif interaction_type == "comment":
        return self._add_comment(post_data)  # Your custom method
    # Add more interaction types...
```

The bot is designed to be extensible for different coins and interaction types while maintaining the robust account rotation you already have in place. 