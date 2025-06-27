#!/usr/bin/env python3
"""
Chrome Session Cleanup Utility

This utility cleans up hanging Chrome sessions and lock files
that can prevent the like stacking bot from working properly.
"""

import os
import sys
import subprocess
import glob

def kill_chrome_processes():
    """Kill hanging Chrome processes"""
    try:
        print("🔫 Killing Chrome processes...")
        
        # Try psutil first (more reliable)
        try:
            import psutil
            killed_count = 0
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.kill()
                        killed_count += 1
                        print(f"   Killed Chrome process: {proc.info['pid']}")
                except:
                    pass
            
            if killed_count > 0:
                print(f"   ✅ Killed {killed_count} Chrome processes")
            else:
                print("   ✅ No Chrome processes found")
                
        except ImportError:
            # Fallback to basic approach
            print("   Using basic process killing...")
            try:
                subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                             capture_output=True, check=False)
                subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                             capture_output=True, check=False)
                print("   ✅ Chrome processes killed")
            except:
                print("   ⚠️ Could not kill Chrome processes")
        
    except Exception as e:
        print(f"   ❌ Error killing processes: {e}")

def clean_profile_locks():
    """Clean up Chrome profile lock files"""
    try:
        print("\n🧹 Cleaning profile lock files...")
        
        # Find Chrome profiles directory
        profiles_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "autocrypto_social_bot",
            "chrome_profiles"
        )
        
        if not os.path.exists(profiles_dir):
            print("   ❌ Chrome profiles directory not found")
            return
        
        cleaned_count = 0
        
        # Look for all profile directories
        for profile_dir in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, profile_dir)
            
            if os.path.isdir(profile_path):
                # Clean lock files in this profile
                lock_files = [
                    os.path.join(profile_path, "SingletonLock"),
                    os.path.join(profile_path, "lockfile"),
                    os.path.join(profile_path, "Lockfile")
                ]
                
                for lock_file in lock_files:
                    if os.path.exists(lock_file):
                        try:
                            os.remove(lock_file)
                            cleaned_count += 1
                            print(f"   🧹 Cleaned: {os.path.basename(lock_file)} from {profile_dir[:30]}")
                        except Exception as e:
                            print(f"   ⚠️ Could not remove {os.path.basename(lock_file)}: {e}")
        
        if cleaned_count > 0:
            print(f"   ✅ Cleaned {cleaned_count} lock files total")
        else:
            print("   ✅ No lock files found to clean")
        
    except Exception as e:
        print(f"   ❌ Error cleaning locks: {e}")

def clean_backup_profiles():
    """Remove backup/logged-out profile directories entirely"""
    try:
        print("\n🗑️ Cleaning backup profiles...")
        
        # Find Chrome profiles directory
        profiles_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "autocrypto_social_bot",
            "chrome_profiles"
        )
        
        if not os.path.exists(profiles_dir):
            print("   ❌ Chrome profiles directory not found")
            return
        
        removed_count = 0
        backup_indicators = [
            'logged_out_backup',
            'backup_logged_out',
            '_backup_'
        ]
        
        # Look for backup profile directories
        for profile_dir in os.listdir(profiles_dir):
            profile_path = os.path.join(profiles_dir, profile_dir)
            
            if os.path.isdir(profile_path):
                # Check if this is a backup profile
                is_backup = False
                profile_lower = profile_dir.lower()
                
                for indicator in backup_indicators:
                    if indicator in profile_lower:
                        is_backup = True
                        break
                
                # Additional check for multiple backups or excessive length
                backup_count = profile_lower.count('backup')
                if backup_count >= 2 or len(profile_dir) > 150:
                    is_backup = True
                
                if is_backup:
                    try:
                        import shutil
                        shutil.rmtree(profile_path)
                        removed_count += 1
                        print(f"   🗑️ Removed backup profile: {profile_dir[:50]}...")
                    except Exception as e:
                        print(f"   ⚠️ Could not remove {profile_dir[:30]}: {e}")
        
        if removed_count > 0:
            print(f"   ✅ Removed {removed_count} backup profiles")
        else:
            print("   ✅ No backup profiles found to remove")
        
    except Exception as e:
        print(f"   ❌ Error cleaning backup profiles: {e}")

def clean_temp_files():
    """Clean up temporary Chrome files"""
    try:
        print("\n🗑️ Cleaning temporary files...")
        
        # Common Chrome temp locations
        temp_patterns = [
            os.path.expanduser("~/AppData/Local/Temp/scoped_dir*"),
            os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Crash Reports/*"),
            "C:/Windows/Temp/scoped_dir*"
        ]
        
        cleaned_count = 0
        
        for pattern in temp_patterns:
            try:
                for temp_file in glob.glob(pattern):
                    try:
                        if os.path.isfile(temp_file):
                            os.remove(temp_file)
                            cleaned_count += 1
                        elif os.path.isdir(temp_file):
                            import shutil
                            shutil.rmtree(temp_file)
                            cleaned_count += 1
                    except:
                        pass  # File might be in use
            except:
                pass
        
        if cleaned_count > 0:
            print(f"   ✅ Cleaned {cleaned_count} temporary files")
        else:
            print("   ✅ No temporary files found")
        
    except Exception as e:
        print(f"   ❌ Error cleaning temp files: {e}")

def main():
    """Main cleanup function"""
    print("🧹 Chrome Session Cleanup Utility")
    print("="*40)
    print("This will clean up hanging Chrome sessions and lock files")
    print("Run this if the like stacking bot has session issues")
    
    print("\n📋 Cleanup Options:")
    print("1. Full cleanup (recommended)")
    print("2. Basic cleanup (no backup profile removal)")
    print("3. Only remove backup profiles")
    
    choice = input("\nSelect cleanup type (1-3): ").strip()
    
    if choice not in ['1', '2', '3']:
        print("❌ Invalid choice. Using basic cleanup.")
        choice = '2'
    
    print(f"\n🚀 Starting cleanup (option {choice})...")
    
    if choice in ['1', '2']:
        # Step 1: Kill Chrome processes
        kill_chrome_processes()
        
        # Step 2: Clean profile locks
        clean_profile_locks()
        
        # Step 3: Clean temp files
        clean_temp_files()
    
    if choice in ['1', '3']:
        # Step 4: Remove backup profiles
        print("\n⚠️  WARNING: This will permanently delete backup profile directories!")
        confirm = input("Continue with backup profile removal? (y/n): ").strip().lower()
        
        if confirm == 'y':
            clean_backup_profiles()
        else:
            print("   ⏭️ Skipped backup profile removal")
    
    print("\n🎉 CLEANUP COMPLETE!")
    print("✅ Chrome sessions should now be clean")
    print("✅ You can now run the like stacking bot")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 