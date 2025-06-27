#!/usr/bin/env python3
"""
SimpleLogin.io Setup Script

This script helps you configure SimpleLogin.io API for automated account creation.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.config.simplelogin_config import setup_simplelogin

def main():
    print("🔧 SimpleLogin.io Configuration Setup")
    print("=" * 60)
    print()
    print("This script will help you configure SimpleLogin.io for automated")
    print("account creation with fresh email aliases.")
    print()
    print("Benefits of using SimpleLogin.io:")
    print("  ✅ Create unlimited email aliases")
    print("  ✅ Keep your real email private")
    print("  ✅ Perfect for account rotation")
    print("  ✅ Professional email forwarding")
    print("  ✅ API-based automation")
    print()
    
    # Check if already configured
    from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
    config = SimpleLoginConfig()
    
    if config.is_configured():
        print("✅ SimpleLogin is already configured!")
        print(f"Current API key: {config.api_key[:10]}...")
        print()
        choice = input("Do you want to reconfigure? (y/n): ").lower()
        if choice != 'y':
            print("Configuration unchanged.")
            return
    
    # Run setup
    result = setup_simplelogin()
    
    if result:
        print()
        print("🎉 SUCCESS!")
        print("=" * 60)
        print("SimpleLogin.io has been configured successfully!")
        print()
        print("Next steps:")
        print("1. Run the demo script to test account creation:")
        print("   python autocrypto_social_bot/scripts/account_management_demo.py")
        print()
        print("2. Or integrate with your existing automation:")
        print("   from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager")
        print("   manager = EnhancedProfileManager()")
        print("   account, driver = manager.create_fresh_account_with_profile('cmc')")
        print()
        print("3. View account statistics anytime:")
        print("   python -c \"from autocrypto_social_bot.services.account_manager import *; print(AutomatedAccountManager(os.getenv('SIMPLELOGIN_API_KEY')).get_stats_summary())\"")
    else:
        print()
        print("❌ Setup failed!")
        print("Please check your API key and try again.")

if __name__ == "__main__":
    main() 