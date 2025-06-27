# CMC AI Token Review Bot

## Overview

This bot automatically generates AI-powered reviews for trending cryptocurrency tokens using CoinMarketCap's AI analysis feature and enhances them using DeepSeek AI.

## Features

- 🔍 Automatically finds trending tokens on CoinMarketCap
- 🤖 Uses CMC's AI to generate comprehensive token reviews
- 🧠 Enhances reviews using DeepSeek AI
- 💾 Saves reviews as individual text files
- 📊 Tracks all reviews in a CSV file for easy analysis

## How It Works

1. **Finds Trending Tokens**: The bot navigates to CoinMarketCap and identifies the top trending cryptocurrencies
2. **Generates AI Reviews**: For each token, it uses CMC's AI feature to generate a detailed analysis
3. **Enhances Reviews**: Uses DeepSeek AI to enhance and personalize the reviews
4. **Saves Reviews**: Each review is saved as:
   - Individual text file in `ai_reviews/` folder
   - Entry in `analysis_data/ai_reviews.csv` for tracking

## Setup

1. **Import Chrome Profile** (if not already done):
   ```bash
   python autocrypto_social_bot/import_profile.py
   ```

2. **Set up DeepSeek API Key**:
   - Get your API key from https://platform.deepseek.com/api-keys
   - Add it to `config/config.json` or set as environment variable `DEEPSEEK_API_KEY`

3. **Run the AI Review Bot**:
   ```bash
   python autocrypto_social_bot/main.py
   ```

## Testing

To test the AI review feature with a single coin:
```bash
python autocrypto_social_bot/test_ai_review.py
```

## Output Structure

### Text Files
- Location: `autocrypto_social_bot/ai_reviews/`
- Format: `{SYMBOL}_{TIMESTAMP}.txt`
- Example: `BTC_20240215_143052.txt`

### CSV Tracking
- Location: `autocrypto_social_bot/analysis_data/ai_reviews.csv`
- Columns:
  - `timestamp`: When the review was generated
  - `coin_name`: Full name of the token
  - `coin_symbol`: Token symbol
  - `ai_review`: Preview of the review (first 500 chars)
  - `full_review_length`: Total length of the review

## Configuration

You can modify these settings in `main.py`:
- `limit=10`: Number of trending coins to analyze (default: 10)
- `random_delay(5, 10)`: Delay between coins in seconds

## Troubleshooting

### "AI analysis button not found"
- CMC may have changed their interface
- The AI feature might not be available for all tokens
- Try running the test script with a major coin like Bitcoin

### Chrome initialization issues
- Make sure Chrome is fully closed before running
- Check that undetected-chromedriver is properly installed
- Try running `pip install --upgrade undetected-chromedriver`

### DeepSeek API issues
- Verify your API key is correctly set in config.json or environment
- Check your API usage limits
- Ensure you have a valid subscription

## Notes

- The bot uses undetected-chromedriver to avoid detection
- Be respectful of CMC's servers - don't run too frequently
- AI reviews may take a few seconds to generate
- Some tokens might not have AI analysis available 