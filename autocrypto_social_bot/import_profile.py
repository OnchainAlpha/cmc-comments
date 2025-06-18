from profiles.profile_manager import ProfileManager

def main():
    print("Starting profile import process...")
    manager = ProfileManager()
    
    # Import the profile
    manager.import_existing_profile()
    
    # List available profiles to confirm
    profiles = manager.list_profiles()
    if profiles:
        print("\nSuccessfully imported profiles:")
        for profile in profiles:
            print(f"- {profile}")
    else:
        print("\nNo profiles were imported. Please check if Chrome is installed and has at least one profile.")

if __name__ == "__main__":
    main() 