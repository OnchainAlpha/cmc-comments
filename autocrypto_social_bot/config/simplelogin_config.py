import os
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleLoginConfig:
    """Configuration manager for SimpleLogin.io API"""
    
    def __init__(self):
        self.config_file = Path(__file__).parent / "simplelogin.json"
        self.api_key = None
        self.load_config()
    
    def load_config(self):
        """Load SimpleLogin configuration from file or environment"""
        # Try to load from environment first
        self.api_key = os.getenv('SIMPLELOGIN_API_KEY')
        
        # Try to load from config file if not in environment
        if not self.api_key and self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('api_key')
            except Exception as e:
                print(f"Error loading SimpleLogin config: {e}")
        
        return self.api_key is not None
    
    def save_config(self, api_key: str):
        """Save SimpleLogin API key to config file"""
        config = {
            'api_key': api_key,
            'created_at': str(datetime.now()),
            'notes': 'SimpleLogin.io API configuration for automated account creation'
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.api_key = api_key
            print(f"✅ SimpleLogin API key saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving SimpleLogin config: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if SimpleLogin is properly configured"""
        return self.api_key is not None and self.api_key != ""
    
    def get_api_key(self) -> str:
        """Get the SimpleLogin API key"""
        if not self.is_configured():
            raise ValueError("SimpleLogin API key not configured!")
        return self.api_key

def setup_simplelogin():
    """Interactive setup for SimpleLogin.io API"""
    print("🔧 SimpleLogin.io Setup")
    print("=" * 60)
    print("To use automated account creation, you need a SimpleLogin.io API key.")
    print()
    print("Steps to get your API key:")
    print("1. Go to https://app.simplelogin.io/dashboard/api_key")
    print("2. Log in to your SimpleLogin account")
    print("3. Generate a new API key")
    print("4. Copy the API key")
    print()
    
    config = SimpleLoginConfig()
    
    if config.is_configured():
        print(f"✅ SimpleLogin is already configured!")
        print(f"Current API key: {config.api_key[:10]}...")
        overwrite = input("Do you want to update the API key? (y/n): ").lower()
        if overwrite != 'y':
            return config
    
    api_key = input("Enter your SimpleLogin API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return None
    
    # Test the API key
    print("🔍 Testing API key...")
    try:
        from autocrypto_social_bot.services.account_manager import SimpleLoginAPI
        test_api = SimpleLoginAPI(api_key)
        aliases = test_api.get_aliases()
        print(f"✅ API key is valid! Found {len(aliases)} existing aliases.")
        
        # Save the config
        if config.save_config(api_key):
            print("✅ SimpleLogin configuration saved successfully!")
            return config
        else:
            print("❌ Failed to save configuration!")
            return None
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        print("Please check your API key and try again.")
        return None

if __name__ == "__main__":
    setup_simplelogin() 