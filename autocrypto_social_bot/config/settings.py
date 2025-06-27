import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def save_config(api_key: str) -> None:
    """Save API key to config file"""
    config_dir = Path(__file__).parent
    config_dir.mkdir(exist_ok=True)
    
    config = {'deepseek_api_key': api_key}
    
    with open(config_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)

# Load config from JSON if exists
config_path = Path(__file__).parent / 'config.json'
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
else:
    config = {}

# DeepSeek Configuration
DEEPSEEK_API_KEY = config.get('deepseek_api_key', '')  # Get from config.json first

# If not in config.json, try environment variable
if not DEEPSEEK_API_KEY:
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

# If still not found, use the hardcoded key
if not DEEPSEEK_API_KEY:
    DEEPSEEK_API_KEY = "sk-cc68436dda774415b838060830cbb2ee"

# Save the key to config.json
if DEEPSEEK_API_KEY and not config.get('deepseek_api_key'):
    save_config(DEEPSEEK_API_KEY)

# CMC Configuration
CMC_BASE_URL = "https://coinmarketcap.com"
CMC_COMMUNITY_URL = "https://coinmarketcap.com/community/"

# Browser Configuration
BROWSER_WINDOW_SIZE = (1366, 768)
DEFAULT_TIMEOUT = 10
RANDOM_DELAY_MIN = 2
RANDOM_DELAY_MAX = 5

# Profile Configuration
DEFAULT_PROFILE_NAME = "cmc_profile"
CHROME_PROFILES_DIR = "chrome_profiles"

# Analysis Configuration
MAX_TRENDING_COINS = 10
MAX_RETRIES = 2
SAVE_REVIEWS = True

# URLs
TWITTER_BASE_URL = "https://twitter.com"

# Blacklist words for content filtering
BLACKLIST_WORDS = [
    "scam",
    "fraud",
    "fake",
    # Add more as needed
] 