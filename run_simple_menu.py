#!/usr/bin/env python3
"""
Simple launcher for the CMC Automation Bot simplified menu
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from autocrypto_social_bot.simplified_menu import main_menu
    
    if __name__ == "__main__":
        print("🚀 Starting CMC Automation Bot - Simplified Menu")
        print("=" * 50)
        main_menu()
        
except ImportError as e:
    print(f"❌ Error importing simplified menu: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install colorama selenium undetected-chromedriver")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting simplified menu: {e}")
    sys.exit(1) 