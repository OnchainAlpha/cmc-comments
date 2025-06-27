#!/usr/bin/env python3
"""
CMC Like Stacking Bot - Rotates through all accounts to like the same posts
"""

import sys
import os
import time
import random
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager

try:
    from coin_posts_bot import CMCCoinPostsBot
    COIN_POSTS_BOT_AVAILABLE = True
except ImportError:
    COIN_POSTS_BOT_AVAILABLE = False

class CMCLikeStackingBot:
    def __init__(self):
        print("🎯 CMC Like Stacking Bot initialized")
        self.profile_manager = ProfileManager()
        
        # Get all available CMC profiles
        all_profiles = self.profile_manager.list_profiles(silent_mode=True)
        raw_cmc_profiles = [p for p in all_profiles if p.startswith('cmc_profile_')]
        
        # Filter out logged-out backup profiles first
        active_profiles = self._filter_active_profiles(raw_cmc_profiles)
        
        # Then filter out profiles with problematic sessions
        self.cmc_profiles = self._filter_healthy_profiles(active_profiles)
        
        print(f"   Total CMC Profiles Found: {len(raw_cmc_profiles)}")
        print(f"   Active (Non-Backup) Profiles: {len(active_profiles)}")
        print(f"   Healthy & Ready Profiles: {len(self.cmc_profiles)}")
        
        backup_count = len(raw_cmc_profiles) - len(active_profiles)
        session_issues = len(active_profiles) - len(self.cmc_profiles)
        
        if backup_count > 0:
            print(f"   🗑️ Excluded {backup_count} logged-out backup profiles")
        if session_issues > 0:
            print(f"   ⚠️ Skipped {session_issues} profiles with session issues")
        
        for i, profile in enumerate(self.cmc_profiles, 1):
            print(f"   {i}. {profile[:50]}{'...' if len(profile) > 50 else ''}")
        
        # Initial cleanup of any hanging sessions
        if self.cmc_profiles:
            self._initial_cleanup()

    def _filter_active_profiles(self, raw_profiles):
        """Filter out logged-out backup profiles and only keep active accounts"""
        active_profiles = []
        
        print("🔍 Filtering active profiles...")
        
        for profile in raw_profiles:
            try:
                # Check if profile is a backup/logged-out profile
                is_backup = self._is_backup_profile(profile)
                
                if is_backup:
                    print(f"   🗑️ Excluding backup: {profile[:40]}...")
                    continue
                
                # Profile seems active
                active_profiles.append(profile)
                print(f"   ✅ Active profile: {profile[:40]}...")
                
            except Exception as e:
                print(f"   ❌ Error checking {profile[:30]}...: {str(e)[:30]}")
                continue
        
        print(f"✅ Found {len(active_profiles)} active profiles out of {len(raw_profiles)} total")
        return active_profiles

    def _is_backup_profile(self, profile_name):
        """Check if a profile is a backup/logged-out profile that should be excluded"""
        try:
            # Common indicators of backup/logged-out profiles
            backup_indicators = [
                'logged_out_backup',
                'backup_logged_out',
                '_backup_',
                'deleted_',
                'inactive_',
                'old_'
            ]
            
            profile_lower = profile_name.lower()
            
            # Check for backup indicators
            for indicator in backup_indicators:
                if indicator in profile_lower:
                    return True
            
            # Additional check: if profile name has multiple backup timestamps
            # (indicating it's been logged out multiple times)
            backup_count = profile_lower.count('backup')
            if backup_count >= 2:  # Multiple backups = likely not active
                return True
            
            # Check for excessive length (backup profiles tend to be very long)
            if len(profile_name) > 150:  # Very long names usually indicate backups
                return True
            
            return False
            
        except Exception as e:
            print(f"   ⚠️ Error checking backup status for {profile_name[:30]}: {e}")
            # If we can't determine, err on the side of caution and exclude
            return True

    def _initial_cleanup(self):
        """Perform initial cleanup of hanging Chrome sessions"""
        try:
            print("\n🧹 Performing initial session cleanup...")
            
            # Kill any hanging Chrome processes
            self._kill_hanging_chrome_processes()
            
            # Clean up lock files from all profiles
            cleaned_count = 0
            for profile in self.cmc_profiles:
                profile_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "autocrypto_social_bot", 
                    "chrome_profiles", 
                    profile
                )
                
                if os.path.exists(profile_path):
                    lock_files = [
                        os.path.join(profile_path, "SingletonLock"),
                        os.path.join(profile_path, "lockfile")
                    ]
                    
                    for lock_file in lock_files:
                        if os.path.exists(lock_file):
                            try:
                                os.remove(lock_file)
                                cleaned_count += 1
                            except:
                                pass
            
            if cleaned_count > 0:
                print(f"   🧹 Cleaned {cleaned_count} lock files")
            
            print("   ✅ Initial cleanup complete")
            
        except Exception as e:
            print(f"   ⚠️ Initial cleanup warning: {str(e)[:50]}")

    def _filter_healthy_profiles(self, raw_profiles):
        """Filter out profiles with corrupted or hanging Chrome sessions"""
        healthy_profiles = []
        
        print("🔍 Checking profile health...")
        
        for profile in raw_profiles:
            try:
                # Quick check to see if profile can be loaded
                profile_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "autocrypto_social_bot", 
                    "chrome_profiles", 
                    profile
                )
                
                # Check if profile directory exists and isn't corrupted
                if os.path.exists(profile_path):
                    # Check for signs of hanging Chrome processes
                    lock_files = [
                        os.path.join(profile_path, "SingletonLock"),
                        os.path.join(profile_path, "lockfile")
                    ]
                    
                    # If lock files exist, the profile might be in use
                    has_locks = any(os.path.exists(lock_file) for lock_file in lock_files)
                    
                    if has_locks:
                        print(f"   ⚠️ Skipping {profile[:30]}... (has active locks)")
                        self._cleanup_profile_locks(profile_path)
                        continue
                    
                    healthy_profiles.append(profile)
                    print(f"   ✅ {profile[:30]}... (healthy)")
                else:
                    print(f"   ❌ Skipping {profile[:30]}... (missing directory)")
                    
            except Exception as e:
                print(f"   ❌ Skipping {profile[:30]}... (error: {str(e)[:30]})")
                continue
        
        return healthy_profiles

    def _cleanup_profile_locks(self, profile_path):
        """Try to clean up Chrome lock files"""
        try:
            lock_files = [
                os.path.join(profile_path, "SingletonLock"),
                os.path.join(profile_path, "lockfile")
            ]
            
            for lock_file in lock_files:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        print(f"      🧹 Cleaned lock file: {os.path.basename(lock_file)}")
                    except:
                        pass  # Might be in use, skip
        except:
            pass  # Best effort cleanup

    def _kill_hanging_chrome_processes(self):
        """Kill any hanging Chrome processes"""
        try:
            import subprocess
            import psutil
            
            # Kill Chrome processes that might be hanging
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'chrome' in proc.info['name'].lower():
                        proc.kill()
                        print(f"      🔫 Killed hanging Chrome process: {proc.info['pid']}")
                except:
                    pass
        except ImportError:
            # psutil not available, try basic approach
            try:
                subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], 
                             capture_output=True, check=False)
                subprocess.run(['taskkill', '/f', '/im', 'chromedriver.exe'], 
                             capture_output=True, check=False)
            except:
                pass

    def _cleanup_before_account(self, profile_name):
        """Cleanup before loading an account"""
        try:
            print(f"   🧹 Pre-cleanup for {profile_name[:30]}...")
            
            # Clean up any hanging Chrome processes
            self._kill_hanging_chrome_processes()
            
            # Clean up profile locks
            profile_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "autocrypto_social_bot", 
                "chrome_profiles", 
                profile_name
            )
            
            if os.path.exists(profile_path):
                self._cleanup_profile_locks(profile_path)
            
            # Small delay to let cleanup complete
            time.sleep(2)
            
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {str(e)[:50]}")

    def _cleanup_after_account(self, account_bot, profile_name):
        """Cleanup after using an account"""
        try:
            print(f"   🧹 Post-cleanup for {profile_name[:30]}...")
            
            # Close the bot properly
            if account_bot:
                try:
                    account_bot.close()
                except:
                    pass
            
            # Kill any remaining Chrome processes
            time.sleep(1)
            self._kill_hanging_chrome_processes()
            
            # Clean up profile locks again
            profile_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "autocrypto_social_bot", 
                "chrome_profiles", 
                profile_name
            )
            
            if os.path.exists(profile_path):
                self._cleanup_profile_locks(profile_path)
            
            print(f"   ✅ Cleanup complete")
            
        except Exception as e:
            print(f"   ⚠️ Cleanup warning: {str(e)[:50]}")

    def _cleanup_failed_account(self, account_bot, profile_name):
        """Cleanup when an account fails to load"""
        try:
            print(f"   🧹 Failed account cleanup for {profile_name[:30]}...")
            
            if account_bot:
                try:
                    if hasattr(account_bot, 'driver') and account_bot.driver:
                        account_bot.driver.quit()
                except:
                    pass
                
                try:
                    account_bot.close()
                except:
                    pass
            
            # Aggressive cleanup for failed accounts
            self._kill_hanging_chrome_processes()
            
            profile_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "autocrypto_social_bot", 
                "chrome_profiles", 
                profile_name
            )
            
            if os.path.exists(profile_path):
                self._cleanup_profile_locks(profile_path)
            
        except Exception as e:
            print(f"   ⚠️ Failed cleanup warning: {str(e)[:50]}")

    def stack_likes_on_coin(self, coin_query, max_posts=15):
        """Stack likes from all accounts on the same coin posts"""
        try:
            print(f"\n🎯 STACKING LIKES ON {coin_query.upper()} POSTS")
            print("="*60)
            print(f"Will use {len(self.cmc_profiles)} accounts")
            
            if not COIN_POSTS_BOT_AVAILABLE:
                print("❌ Coin Posts Bot not available")
                return {'success': False}
            
            if not self.cmc_profiles:
                print("❌ No CMC profiles available")
                return {'success': False}
            
            total_successful_likes = 0
            total_posts_found = 0
            
            # Process each account
            for account_index, profile_name in enumerate(self.cmc_profiles, 1):
                try:
                    print(f"\n{'='*60}")
                    print(f"ACCOUNT {account_index}/{len(self.cmc_profiles)}: {profile_name}")
                    print("="*60)
                    
                    # Pre-cleanup before loading account
                    self._cleanup_before_account(profile_name)
                    
                    # Create bot instance for this account
                    account_bot = None
                    try:
                        account_bot = CMCCoinPostsBot(use_account_rotation=False)
                        
                        # Try to load the profile with better error handling
                        try:
                            account_bot.driver = account_bot.profile_manager.load_profile(profile_name)
                            print(f"   ✅ Profile loaded successfully")
                        except Exception as profile_error:
                            print(f"   ❌ Failed to load profile: {str(profile_error)[:100]}")
                            # Try cleanup and skip this account
                            self._cleanup_failed_account(account_bot, profile_name)
                            continue
                        
                        # Run the coin interaction bot for this account
                        account_results = account_bot.run_coin_interaction_bot(
                            coin_query=coin_query,
                            max_posts=max_posts,
                            interaction_type="emoji"
                        )
                        
                        if account_results.get('success'):
                            successful = account_results['interaction_results'].get('successful_interactions', 0)
                            posts_found = account_results.get('posts_found', 0)
                            
                            total_successful_likes += successful
                            if account_index == 1:  # Only count posts once
                                total_posts_found = posts_found
                            
                            print(f"✅ Account {account_index}: {successful} successful likes on {posts_found} posts")
                            
                            success_rate = (successful / max(1, posts_found)) * 100
                            print(f"   Success Rate: {success_rate:.1f}%")
                        else:
                            print(f"❌ Account {account_index}: Failed - {account_results.get('error', 'Unknown error')}")
                        
                    except Exception as bot_error:
                        print(f"   ❌ Bot error: {str(bot_error)[:100]}")
                    finally:
                        # Always cleanup after each account
                        self._cleanup_after_account(account_bot, profile_name)
                    
                    # Delay between accounts (important for stacking)
                    if account_index < len(self.cmc_profiles):
                        delay = random.uniform(15, 25)  # Longer delay for safety
                        print(f"⏱️ Waiting {delay:.1f}s before next account...")
                        time.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ Error with account {profile_name}: {e}")
                    continue
            
            # Final summary
            print(f"\n🎉 LIKE STACKING COMPLETE!")
            print("="*50)
            print(f"Total Accounts Used: {len(self.cmc_profiles)}")
            print(f"Total Posts Found: {total_posts_found}")
            print(f"Total Successful Likes: {total_successful_likes}")
            
            if total_posts_found > 0:
                avg_likes_per_post = total_successful_likes / total_posts_found
                print(f"Average Likes Per Post: {avg_likes_per_post:.1f}")
                
                max_possible_likes = total_posts_found * len(self.cmc_profiles)
                overall_success_rate = (total_successful_likes / max_possible_likes) * 100
                print(f"Overall Stacking Success Rate: {overall_success_rate:.1f}%")
            
            return {
                'success': True,
                'accounts_used': len(self.cmc_profiles),
                'total_likes': total_successful_likes,
                'posts_found': total_posts_found,
                'avg_likes_per_post': total_successful_likes / max(1, total_posts_found)
            }
            
        except Exception as e:
            print(f"❌ Error in like stacking: {e}")
            return {'success': False, 'error': str(e)}

    def close(self):
        """Clean up"""
        pass


def main():
    """Demo usage"""
    try:
        print("🎯 CMC Like Stacking Bot Demo")
        print("="*40)
        
        bot = CMCLikeStackingBot()
        
        if len(bot.cmc_profiles) == 0:
            print("❌ No CMC profiles found. Please create profiles first.")
            return
        
        coin = input("\nEnter coin to stack likes on (e.g., GOONC): ").strip()
        if not coin:
            coin = "GOONC"
        
        max_posts = input(f"Max posts per account (default 10): ").strip()
        try:
            max_posts = int(max_posts) if max_posts else 10
        except:
            max_posts = 10
        
        print(f"\n🚀 LIKE STACKING PLAN:")
        print(f"   Coin: {coin.upper()}")
        print(f"   Max Posts Per Account: {max_posts}")
        print(f"   Accounts: {len(bot.cmc_profiles)}")
        print(f"   Expected Max Likes: {max_posts * len(bot.cmc_profiles)}")
        
        proceed = input("\nProceed with like stacking? (y/n): ").strip().lower()
        
        if proceed == 'y':
            results = bot.stack_likes_on_coin(coin, max_posts)
            
            if results['success']:
                print(f"\n✅ LIKE STACKING SUCCESS!")
                print(f"   Total Likes Stacked: {results['total_likes']}")
                print(f"   Posts Found: {results['posts_found']}")
                print(f"   Accounts Used: {results['accounts_used']}")
                print(f"   Avg Likes Per Post: {results['avg_likes_per_post']:.1f}")
            else:
                print(f"\n❌ Like stacking failed: {results.get('error')}")
        else:
            print("❌ Like stacking cancelled")
        
        bot.close()
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 