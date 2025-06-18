import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from profiles.profile_manager import ProfileManager
import time

def main():
    profile_manager = ProfileManager()
    
    while True:
        print("\nProfile Manager")
        print("1. List imported profiles")
        print("2. Import existing Chrome profile")
        print("3. Test profile")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            profiles = profile_manager.list_profiles()
            if profiles:
                print("\nAvailable profiles:")
                for profile in profiles:
                    print(f"- {profile}")
            else:
                print("\nNo profiles found")
                
        elif choice == "2":
            profile_manager.import_existing_profile()
            
        elif choice == "3":
            profiles = profile_manager.list_profiles()
            if not profiles:
                print("\nNo profiles available. Please import a profile first.")
                continue
                
            print("\nAvailable profiles:")
            for i, profile in enumerate(profiles):
                print(f"{i+1}. {profile}")
                
            try:
                idx = int(input("\nSelect profile number to test: ")) - 1
                if 0 <= idx < len(profiles):
                    profile_name = profiles[idx]
                    driver = None
                    try:
                        print(f"\nLoading profile: {profile_name}")
                        driver = profile_manager.load_profile(profile_name)
                        
                        while True:
                            print("\nTest Menu:")
                            print("1. Go to Twitter")
                            print("2. Go to CoinMarketCap")
                            print("3. Go to custom URL")
                            print("4. Close browser")
                            
                            test_choice = input("\nEnter your choice (1-4): ")
                            
                            if test_choice == "1":
                                driver.get("https://twitter.com")
                            elif test_choice == "2":
                                driver.get("https://coinmarketcap.com")
                            elif test_choice == "3":
                                url = input("Enter URL (include https://): ")
                                driver.get(url)
                            elif test_choice == "4":
                                break
                            
                            time.sleep(2)
                            
                    finally:
                        if driver:
                            driver.quit()
                else:
                    print("Invalid profile number")
            except ValueError:
                print("Invalid input")
                
        elif choice == "4":
            print("\nExiting Profile Manager...")
            sys.exit(0)
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 