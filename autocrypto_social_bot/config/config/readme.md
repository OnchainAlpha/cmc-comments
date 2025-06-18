# Auto Crypto Social Bot

An automated system for cryptocurrency social media engagement and content generation.

## Project Overview

This bot automates several tasks:
- Creates and manages multiple Chrome profiles with optional proxy support
- Scrapes trending cryptocurrencies from CoinMarketCap
- Gathers relevant Twitter discussions
- Generates content using ChatGPT API
- Manages social media engagement

## Prerequisites

1. Python 3.8 or higher
2. Google Chrome browser installed
3. Twitter accounts (manual login required)
4. CoinMarketCap accounts (manual login required)
5. OpenAI API key for ChatGPT
6. (Optional) Proxy list

## Initial Setup

1. **Create Virtual Environment**
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate


2. **Install Dependencies**
bash
pip install -r requirements.txt


3. **Configuration Setup**
- Copy `.env.example` to `.env` and add your OpenAI API key:
OPENAI_API_KEY=your_api_key_here
- Add your accounts to `config/accounts.csv`:

csv
profile_name,twitter_username,coinmarketcap_username,profile_directory_name
Account1,twitter_user1,cmc_user1,profile1

- (Optional) Add proxies to `config/proxies.txt`:
ip:port
ip:port:username:password

## Manual Steps Required

### Chrome Profile Setup (One-time process per account)

1. Run the profile creator:
bash
python -m profiles.profile_manager


2. Choose option 2 (Create single profile)

3. For each profile:
   - The script will open Chrome with a new profile
   - A Twitter login page will open
   - **Manually log in to Twitter**
   - Press Enter in the terminal
   - A CoinMarketCap login page will open
   - **Manually log in to CoinMarketCap**
   - Press Enter in the terminal
   - The profile will be saved with login sessions

⚠️ **Important**: This manual login process is necessary to bypass anti-bot measures and create persistent login sessions. The saved Chrome profiles will maintain these sessions for future automated use.

## Running the Bot

### 1. Trend Analysis and Content Generation

python main.py
This will:
- Scrape trending coins from CoinMarketCap
- Gather Twitter discussions  form those coins
- Generate content using ChatGPT of those discussion 
- Save generated content for review
- post it on CMC community

### 2. Engagement Bot (Separate Script)

python -m engagement.like_comments
This will:
- Load saved Chrome profiles
- Visit target profiles
- Perform engagement actions (likes, etc.)
- Use random delays between actions

## Project Structure
utocrypto_social_bot/
├── config/ # Configuration files
│ ├── settings.py # Global settings
│ ├── accounts.csv # Account information
│ ├── proxies.txt # Proxy list
│ └── tokens.txt # Cryptocurrency tokens to track
├── profiles/ # Chrome profile management
│ └── profile_manager.py # Profile creation and management
├── scrapers/ # Web scraping modules
│ ├── cmc_scraper.py # CoinMarketCap scraper
│ └── twitter_scraper.py # Twitter scraper
├── content_generation/ # Content generation using ChatGPT
│ └── content_generator.py
├── engagement/ # Social media engagement
│ └── like_comments.py # Comment liking automation
├── utils/ # Utility functions
│ └── helpers.py # Helper functions
└── main.py # Main script


## Safety Measures

1. **Rate Limiting**
   - Random delays between actions
   - Configurable minimum and maximum delays
   - Proxy rotation (if configured)

2. **Error Handling**
   - Graceful error recovery
   - Session maintenance
   - Activity logging

3. **Anti-Detection**
   - Random delays between actions
   - Proxy support
   - Separate Chrome profiles
   - Human-like behavior patterns

## Maintenance

- Regularly check if login sessions are still valid
- Monitor proxy health if using proxies
- Update Chrome profiles if needed
- Check for any platform changes (Twitter/CMC) that might affect the bot

## Troubleshooting

1. **Invalid Login Sessions**
   - Delete the affected Chrome profile
   - Recreate the profile with manual login

2. **Proxy Issues**
   - Check proxy validity
   - Remove or replace non-working proxies
   - Consider using paid proxy services for better reliability

3. **Rate Limiting**
   - Increase delay times in settings.py
   - Add more proxies
   - Reduce concurrent actions

## Best Practices

1. Start with longer delays and gradually adjust based on performance
2. Regularly backup Chrome profiles
3. Monitor engagement patterns for any anomalies
4. Keep proxy list updated and verified
5. Regularly update the blacklist words in settings.py

## Legal Disclaimer

This tool is for educational purposes only. Users are responsible for:
- Complying with all relevant platform Terms of Service
- Ensuring appropriate use of proxies
- Managing API usage within allowed limits
- Following social media platform guidelines

## Contributing

Feel free to submit issues and enhancement requests!

## License

[Your chosen license]
