#!/usr/bin/env python3
"""
Simple launcher for the CMC Automation Bot simplified menu
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Add the autocrypto_social_bot directory to the path as well
autocrypto_path = project_root / "autocrypto_social_bot"
if autocrypto_path.exists():
    sys.path.insert(0, str(autocrypto_path))

def main():
    """Main launcher function"""
    try:
        # Try multiple import approaches
        try:
            from autocrypto_social_bot.simplified_menu import main_menu
        except ImportError:
            # Fallback import method
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "simplified_menu", 
                project_root / "autocrypto_social_bot" / "simplified_menu.py"
            )
            simplified_menu = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(simplified_menu)
            main_menu = simplified_menu.main_menu
        
        print("🚀 Starting CMC Automation Bot - Simplified Menu")
        print("=" * 50)
        main_menu()
        
    except ImportError as e:
        print(f"❌ Error importing simplified menu: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all dependencies are installed:")
        print("   pip install colorama selenium undetected-chromedriver")
        print("2. Make sure you're running from the project root directory")
        print("3. Check that autocrypto_social_bot/simplified_menu.py exists")
        
        # Debug info
        print(f"\nDebug Info:")
        print(f"Current directory: {os.getcwd()}")
        print(f"Project root: {project_root}")
        print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
        
        simplified_menu_path = project_root / "autocrypto_social_bot" / "simplified_menu.py"
        print(f"Simplified menu exists: {simplified_menu_path.exists()}")
        
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting simplified menu: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 