import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager

def setup_cmc_profile():
    print("\n=== CoinMarketCap Profile Setup ===")
    print("This script will help you set up a Chrome profile for CoinMarketCap automation.")
    
    # Initialize profile manager
    profile_manager = ProfileManager()
    
    # Check if profile already exists
    existing_profiles = profile_manager.list_profiles()
    if "cmc" in existing_profiles:
        print("\nA CMC profile already exists. Would you like to:")
        print("1. Use existing profile")
        print("2. Create new profile")
        choice = input("Enter your choice (1/2): ")
        
        if choice == "1":
            print("\nUsing existing CMC profile...")
            return "cmc"
    
    # Import profile
    print("\nLet's import your Chrome profile:")
    print("1. Close all Chrome windows")
    print("2. Select your Chrome profile that's already logged into CoinMarketCap")
    input("\nPress Enter when ready...")
    
    profile_name = profile_manager.import_existing_profile()
    if not profile_name:
        print("\nProfile import cancelled.")
        return None
    
    # Rename to cmc if not already named that
    if profile_name != "cmc":
        old_path = os.path.join(profile_manager.profiles_dir, profile_name)
        new_path = os.path.join(profile_manager.profiles_dir, "cmc")
        
        if os.path.exists(new_path):
            overwrite = input("\nA 'cmc' profile already exists. Overwrite? (y/n): ")
            if overwrite.lower() != 'y':
                return None
            import shutil
            shutil.rmtree(new_path)
        
        os.rename(old_path, new_path)
        print("\nProfile renamed to 'cmc'")
    
    return "cmc"

if __name__ == "__main__":
    profile_name = setup_cmc_profile()
    if profile_name:
        print(f"\nProfile setup complete! You can now use the '{profile_name}' profile for automation.")
    else:
        print("\nProfile setup cancelled.") 