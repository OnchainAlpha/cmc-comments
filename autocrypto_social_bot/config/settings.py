import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Chrome Profile Settings
CHROME_PROFILES_DIR = os.path.join(os.path.expanduser('~'), 'chrome_profiles')

# URLs
CMC_BASE_URL = "https://coinmarketcap.com"
TWITTER_BASE_URL = "https://twitter.com"

# Delays (in seconds)
MIN_DELAY = 2
MAX_DELAY = 5

# Blacklist words for content filtering
BLACKLIST_WORDS = [
    "scam",
    "fraud",
    "fake",
    # Add more as needed
] 