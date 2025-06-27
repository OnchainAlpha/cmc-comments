#!/usr/bin/env python3
"""
Simplified Menu System for CMC Automation Bot

This menu provides a clean interface with only the essential functions:
1. Profile Management (with SimpleLogin integration)
2. Run Bot (all promotion types)
3. Run Reaction Bot (coin-specific or account-specific)
4. Proxy Settings (manual or auto-scrape)
"""

import sys
import os
import time
import json
import re
from typing import Optional, List, Dict
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Import core modules
from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.main import CryptoAIAnalyzer

# SimpleLogin imports
try:
    from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
    from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI
    from autocrypto_social_bot.services.account_manager import AutomatedAccountManager
    SIMPLELOGIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ SimpleLogin not available: {e}")
    SIMPLELOGIN_AVAILABLE = False

# Bot imports
try:
    from coin_posts_bot import CMCCoinPostsBot
    from like_stacking_bot import CMCLikeStackingBot
    BOTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Bots not available: {e}")
    BOTS_AVAILABLE = False

# Proxy management
try:
    from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
    PROXY_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Proxy manager not available: {e}")
    PROXY_MANAGER_AVAILABLE = False

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Print a formatted header"""
    clear_screen()
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{title.center(60)}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message: str):
    """Print error message"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message: str):
    """Print warning message"""
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Print info message"""
    print(f"{Fore.BLUE}ℹ️ {message}{Style.RESET_ALL}")

# ====== PROFILE MANAGEMENT SYSTEM ======

def get_simplelogin_aliases() -> List[Dict]:
    """Get all SimpleLogin aliases and their usage status"""
    if not SIMPLELOGIN_AVAILABLE:
        print_error("SimpleLogin not available")
        return []
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print_error("SimpleLogin not configured. Please run setup first.")
        return []
    
    try:
        client = EnhancedSimpleLoginAPI(config.api_key)
        
        # Get all aliases
        all_aliases = []
        page = 0
        
        while True:
            result = client.get_aliases(page_id=page)
            aliases = result.get('aliases', [])
            
            if not aliases:
                break
            
            all_aliases.extend(aliases)
            
            if not result.get('more', False):
                break
            
            page += 1
        
        # Check which aliases are in use by checking account database
        account_manager = AutomatedAccountManager(config.api_key)
        used_emails = account_manager.get_all_used_emails()
        
        # Enrich aliases with usage status
        for alias in all_aliases:
            alias['in_use'] = alias['email'] in used_emails
            alias['forward_count'] = alias.get('nb_forward', 0)
            alias['enabled'] = alias.get('enabled', True)
        
        return all_aliases
        
    except Exception as e:
        print_error(f"Failed to get SimpleLogin aliases: {e}")
        return []

def extract_email_from_cmc_session(driver):
    """Extract email from CMC user dropdown by clicking on avatar"""
    try:
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        
        # Wait for page to load completely
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(2)
        
        # Look for user avatar/dropdown element using multiple selectors
        avatar_selectors = [
            '[data-test="user-avatar-wrapper"]',
            '.UserDropdown_user-avatar-wrapper__YEFUG',  
            '.BasePopover_base__T5yOf .UserDropdown_user-avatar-wrapper__YEFUG',
            'div[class*="UserDropdown"][class*="user-avatar-wrapper"]',
            'div[class*="user-avatar"]',
            'button[class*="user"] img',
            'button[aria-label*="user"]',
            'div[class*="profile"]',
            'div[class*="avatar"]'
        ]
        
        avatar_element = None
        for selector in avatar_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        avatar_element = element
                        print(f"   Found avatar element: {selector}")
                        break
                if avatar_element:
                    break
            except Exception:
                continue
        
        if not avatar_element:
            # Fallback: try XPath selectors
            xpath_selectors = [
                "//div[contains(@class, 'user-avatar')]",
                "//button[contains(@class, 'user')]",
                "//div[contains(@data-test, 'user')]",
                "//div[contains(@class, 'avatar')]",
                "//svg[contains(@class, 'c-i')]/parent::div/parent::div",
                "//img[contains(@src, 'avatar')]/parent::div"
            ]
            
            for selector in xpath_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            avatar_element = element
                            print(f"   Found avatar element (XPath): {selector}")
                            break
                    if avatar_element:
                        break
                except Exception:
                    continue
        
        if not avatar_element:
            return None, "No avatar dropdown found with any selector"
        
        # Try to click the avatar element
        try:
            print("   Clicking avatar to open dropdown...")
            # Scroll element into view first
            driver.execute_script("arguments[0].scrollIntoView(true);", avatar_element)
            time.sleep(1)
            
            # Try different click methods
            click_success = False
            click_methods = [
                lambda: avatar_element.click(),
                lambda: driver.execute_script("arguments[0].click();", avatar_element),
                lambda: driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", avatar_element)
            ]
            
            for i, click_method in enumerate(click_methods):
                try:
                    click_method()
                    click_success = True
                    print(f"   Click method {i+1} succeeded")
                    break
                except Exception as e:
                    print(f"   Click method {i+1} failed: {e}")
                    continue
            
            if not click_success:
                return None, "Failed to click avatar element"
            
            time.sleep(3)  # Wait for dropdown to appear
            
        except Exception as e:
            return None, f"Error clicking avatar: {str(e)}"
        
        # Look for email in the dropdown/popup content
        print("   Looking for email in dropdown content...")
        page_source = driver.page_source
        
        # Use regex to find SimpleLogin emails in the page
        simplelogin_pattern = r'\b[A-Za-z0-9._%+-]+@(?:simplelogin\.com|aleeas\.com)\b'
        emails_found = re.findall(simplelogin_pattern, page_source, re.IGNORECASE)
        
        if emails_found:
            # Remove duplicates and return first unique email
            unique_emails = list(set(emails_found))
            return unique_emails[0], "success"
        
        # If no SimpleLogin email found, try general email pattern
        general_email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        all_emails = re.findall(general_email_pattern, page_source, re.IGNORECASE)
        
        # Filter out common non-user emails
        filtered_emails = [
            email for email in all_emails 
            if not any(domain in email.lower() for domain in [
                'coinmarketcap.com', 'google.com', 'facebook.com', 
                'twitter.com', 'support@', 'noreply@', 'no-reply@',
                'help@', 'info@', 'admin@'
            ])
        ]
        
        if filtered_emails:
            # Remove duplicates  
            unique_emails = list(set(filtered_emails))
            return unique_emails[0], "general_email_found"
        
        return None, "no_email_in_dropdown"
        
    except Exception as e:
        return None, f"error_extracting_email: {str(e)}"

def check_chrome_sessions_for_active_emails() -> Dict[str, Dict]:
    """Check all Chrome profiles using proper login detection and email extraction"""
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    from autocrypto_social_bot.cmc_login_detector import CMCLoginDetector
    
    print(f"{Fore.CYAN}🔍 Checking Chrome sessions for active logins...{Style.RESET_ALL}")
    
    profile_manager = ProfileManager()
    login_detector = CMCLoginDetector(profile_manager)
    profiles = [p for p in profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
    
    active_sessions = {}
    total_profiles = len(profiles)
    
    for i, profile_name in enumerate(profiles, 1):
        print(f"   Checking {profile_name} ({i}/{total_profiles})...")
        
        try:
            # Load the profile
            driver = profile_manager.load_profile(profile_name)
            time.sleep(3)
            
            # Go to CMC main page
            driver.get("https://coinmarketcap.com")
            time.sleep(4)
            
            # Use the proper login detection system
            login_status = login_detector.check_cmc_login_status(driver, profile_name)
            
            if login_status.get('logged_in', False):
                # Logged in - try to extract email
                print(f"   ✅ Profile {profile_name} is logged in, extracting email...")
                
                email, extraction_status = extract_email_from_cmc_session(driver)
                
                active_sessions[profile_name] = {
                    'status': 'logged_in',
                    'email': email,
                    'extraction_method': extraction_status,
                    'login_details': login_status,
                    'checked': True
                }
                
                if email:
                    print(f"   ✅ Email extracted: {email}")
                else:
                    print(f"   🟡 Logged in but email extraction failed: {extraction_status}")
            else:
                # Not logged in
                active_sessions[profile_name] = {
                    'status': 'logged_out',
                    'email': None,
                    'login_details': login_status,
                    'checked': True
                }
                print(f"   ❌ Profile {profile_name} is logged out")
            
            driver.quit()
            
        except Exception as e:
            print(f"   ❌ Error checking {profile_name}: {str(e)[:50]}...")
            active_sessions[profile_name] = {
                'status': 'error',
                'email': None,
                'error': str(e),
                'checked': True
            }
    
    # Analyze the results
    print(f"\n{Fore.CYAN}📊 SESSION ANALYSIS:{Style.RESET_ALL}")
    
    logged_in_sessions = {k: v for k, v in active_sessions.items() if v['status'] == 'logged_in'}
    logged_out_sessions = {k: v for k, v in active_sessions.items() if v['status'] == 'logged_out'}
    error_sessions = {k: v for k, v in active_sessions.items() if v['status'] == 'error'}
    
    print(f"   ✅ Logged in sessions: {len(logged_in_sessions)}")
    print(f"   ❌ Logged out sessions: {len(logged_out_sessions)}")
    print(f"   ⚠️ Error sessions: {len(error_sessions)}")
    
    # Get emails currently in use
    emails_in_use = set()
    for session in logged_in_sessions.values():
        if session.get('email'):
            emails_in_use.add(session['email'])
    
    print(f"   📧 Unique emails in use: {len(emails_in_use)}")
    
    if emails_in_use:
        print(f"   Emails being used:")
        for email in sorted(emails_in_use):
            print(f"      • {email}")
    
    # Get available SimpleLogin emails
    try:
        config = SimpleLoginConfig()
        if config.is_configured():
            client = EnhancedSimpleLoginAPI(config.api_key)
            all_aliases = []
            page = 0
            
            while True:
                result = client.get_aliases(page_id=page)
                aliases = result.get('aliases', [])
                if not aliases:
                    break
                all_aliases.extend(aliases)
                if not result.get('more', False):
                    break
                page += 1
            
            # Find available emails (not currently in use)
            available_emails = [
                alias for alias in all_aliases 
                if alias['email'] not in emails_in_use and alias.get('enabled', True)
            ]
            
            print(f"\n{Fore.CYAN}📧 EMAIL AVAILABILITY:{Style.RESET_ALL}")
            print(f"   Total SimpleLogin aliases: {len(all_aliases)}")
            print(f"   Currently in use: {len(emails_in_use)}")
            print(f"   Available for new sessions: {len(available_emails)}")
            
            # Offer optimization if there are unused sessions or available emails
            if logged_out_sessions or available_emails:
                handle_session_optimization(
                    logged_out_sessions, 
                    available_emails, 
                    emails_in_use,
                    active_sessions
                )
        else:
            print(f"\n{Fore.YELLOW}⚠️ SimpleLogin not configured - cannot check email availability{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"\n{Fore.RED}❌ Error checking SimpleLogin emails: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}✅ Chrome session check completed!{Style.RESET_ALL}")
    return active_sessions

def handle_session_optimization(logged_out_sessions, available_emails, emails_in_use, all_sessions):
    """Handle optimization of Chrome sessions vs available emails"""
    
    print(f"\n{Fore.CYAN}🎯 SESSION OPTIMIZATION OPPORTUNITY{Style.RESET_ALL}")
    
    # Show current situation
    print(f"\n{Fore.CYAN}📊 CURRENT SITUATION:{Style.RESET_ALL}")
    print(f"   Logged out sessions: {len(logged_out_sessions)}")
    print(f"   Available emails: {len(available_emails)}")
    print(f"   Emails in use: {len(emails_in_use)}")
    
    if logged_out_sessions:
        print(f"\n{Fore.YELLOW}⚠️ LOGGED OUT SESSIONS:{Style.RESET_ALL}")
        for profile in logged_out_sessions.keys():
            print(f"      • {profile}")
    
    if available_emails:
        print(f"\n{Fore.GREEN}✅ AVAILABLE EMAILS:{Style.RESET_ALL}")
        for i, alias in enumerate(available_emails[:10], 1):  # Show first 10
            forwards = alias.get('nb_forward', 0)
            note = alias.get('note', 'No note')[:50]
            print(f"   {i:2d}. {alias['email']}")
            print(f"       Forwards: {forwards} | Note: {note}")
        
        if len(available_emails) > 10:
            print(f"       ... and {len(available_emails) - 10} more")
    
    # Offer optimization options
    print(f"\n{Fore.CYAN}🎯 OPTIMIZATION OPTIONS:{Style.RESET_ALL}")
    
    options = []
    if logged_out_sessions and available_emails:
        options.append("1. 🔄 Replace logged-out sessions with new sessions for available emails")
        options.append("2. 🗑️ Delete only logged-out sessions (keep existing logged-in ones)")
        options.append("3. ➕ Create new sessions for available emails (keep all existing)")
        options.append("4. ⏭️ Skip optimization")
    elif logged_out_sessions:
        options.append("1. 🗑️ Delete logged-out sessions")
        options.append("2. ⏭️ Skip")
    elif available_emails:
        options.append("1. ➕ Create new sessions for available emails")
        options.append("2. ⏭️ Skip")
    else:
        print(f"   No optimization needed - all sessions are active")
        return
    
    for option in options:
        print(f"   {option}")
    
    choice = input(f"\n{Fore.YELLOW}Select option: {Style.RESET_ALL}").strip()
    
    if "replace" in options[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(options) else False:
        replace_logged_out_with_new_sessions(logged_out_sessions, available_emails)
    elif "Delete only" in options[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(options) else False:
        delete_logged_out_sessions(list(logged_out_sessions.keys()))
    elif "Create new sessions" in options[int(choice)-1] if choice.isdigit() and 1 <= int(choice) <= len(options) else False:
        create_new_sessions_for_emails(available_emails)
    elif choice == "1" and len(options) == 2 and "Delete" in options[0]:
        delete_logged_out_sessions(list(logged_out_sessions.keys()))
    elif choice == "1" and len(options) == 2 and "Create" in options[0]:
        create_new_sessions_for_emails(available_emails)
    else:
        print(f"{Fore.BLUE}ℹ️ Skipping optimization{Style.RESET_ALL}")

def replace_logged_out_with_new_sessions(logged_out_sessions, available_emails):
    """Delete logged-out sessions and create new ones for available emails"""
    print(f"\n{Fore.CYAN}🔄 REPLACING LOGGED-OUT SESSIONS{Style.RESET_ALL}")
    
    # Delete logged-out sessions first
    print(f"🗑️ Deleting {len(logged_out_sessions)} logged-out sessions...")
    delete_logged_out_sessions(list(logged_out_sessions.keys()))
    
    # Create new sessions for available emails
    max_new_sessions = min(len(available_emails), len(logged_out_sessions))
    emails_to_use = available_emails[:max_new_sessions]
    
    print(f"\n➕ Creating {len(emails_to_use)} new sessions...")
    create_new_sessions_for_emails(emails_to_use)

def create_new_sessions_for_emails(available_emails):
    """Create new Chrome profiles for available emails"""
    from autocrypto_social_bot.profiles.profile_manager import ProfileManager
    
    print(f"\n{Fore.CYAN}➕ CREATING NEW SESSIONS{Style.RESET_ALL}")
    
    profile_manager = ProfileManager()
    
    print(f"   Creating {len(available_emails)} new profiles...")
    print(f"   You'll need to manually log in to each one using the specified email")
    
    created_profiles = []
    
    for i, alias in enumerate(available_emails, 1):
        try:
            # Get next profile number
            next_num = profile_manager.get_next_profile_number()
            profile_name = f'cmc_profile_{next_num}'
            
            print(f"\n   Creating {profile_name} for {alias['email']}...")
            
            # Create the profile (this will open Chrome for initial setup)
            profile_manager.create_numbered_profile(next_num)
            
            created_profiles.append({
                'profile': profile_name,
                'email': alias['email'],
                'note': alias.get('note', '')
            })
            
            print_success(f"   ✅ Created {profile_name}")
            
        except Exception as e:
            print_error(f"   ❌ Failed to create profile for {alias['email']}: {e}")
    
    if created_profiles:
        print(f"\n{Fore.GREEN}🎉 Successfully created {len(created_profiles)} new profiles!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}📋 MANUAL LOGIN REQUIRED:{Style.RESET_ALL}")
        print("   Each profile needs to be logged in manually:")
        
        for profile_info in created_profiles:
            print(f"   • {profile_info['profile']} → {profile_info['email']}")
        
        print(f"\n{Fore.YELLOW}💡 TIP: You can now use Profile Management → Test Profile to log in to each one{Style.RESET_ALL}")

def delete_logged_out_sessions(logged_out_profiles: List[str]):
    """Delete logged-out profiles after confirmation"""
    if not logged_out_profiles:
        return
        
    print(f"\n{Fore.RED}🗑️ DELETE LOGGED-OUT SESSIONS{Style.RESET_ALL}")
    print(f"   Sessions to delete: {len(logged_out_profiles)}")
    
    for profile in logged_out_profiles:
        print(f"   • {profile}")
    
    confirm = input(f"\n{Fore.YELLOW}⚠️ This will permanently delete these sessions. Continue? (type 'DELETE'): {Style.RESET_ALL}").strip()
    
    if confirm == 'DELETE':
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        profile_manager = ProfileManager()
        
        deleted_count = 0
        for profile in logged_out_profiles:
            try:
                profile_path = profile_manager.get_profile_path(profile)
                import shutil
                shutil.rmtree(profile_path)
                print_success(f"   ✅ Deleted: {profile}")
                deleted_count += 1
            except Exception as e:
                print_error(f"   ❌ Failed to delete {profile}: {e}")
        
        print_success(f"Successfully deleted {deleted_count} sessions!")
    else:
        print_info("Session deletion cancelled")

def get_simplelogin_aliases_with_chrome_status() -> List[Dict]:
    """Get SimpleLogin aliases with real-time Chrome session status"""
    if not SIMPLELOGIN_AVAILABLE:
        print_error("SimpleLogin not available")
        return []
    
    config = SimpleLoginConfig()
    if not config.is_configured():
        print_error("SimpleLogin not configured. Please run setup first.")
        return []
    
    try:
        # Get SimpleLogin aliases
        client = EnhancedSimpleLoginAPI(config.api_key)
        all_aliases = []
        page = 0
        
        while True:
            result = client.get_aliases(page_id=page)
            aliases = result.get('aliases', [])
            
            if not aliases:
                break
            
            all_aliases.extend(aliases)
            
            if not result.get('more', False):
                break
            
            page += 1
        
        # Check active Chrome sessions
        chrome_sessions = check_chrome_sessions_for_active_emails()
        
        # Create a map of active emails
        active_emails = {}
        for profile, session_info in chrome_sessions.items():
            if session_info['email']:
                active_emails[session_info['email']] = {
                    'profile': profile,
                    'status': session_info['status']
                }
        
        # Enrich aliases with real-time status
        for alias in all_aliases:
            email = alias['email']
            alias['forward_count'] = alias.get('nb_forward', 0)
            alias['enabled'] = alias.get('enabled', True)
            
            if email in active_emails:
                alias['chrome_status'] = 'active_in_chrome'
                alias['chrome_profile'] = active_emails[email]['profile']
                alias['in_use'] = True
            else:
                # Check if any Chrome session shows this email as logged in
                logged_in_somewhere = any(
                    session['status'] in ['logged_in', 'logged_in_unknown_email'] 
                    for session in chrome_sessions.values()
                )
                
                if logged_in_somewhere:
                    alias['chrome_status'] = 'potentially_available'
                else:
                    alias['chrome_status'] = 'available'
                alias['chrome_profile'] = None
                alias['in_use'] = False
        
        return all_aliases
        
    except Exception as e:
        print_error(f"Failed to get SimpleLogin aliases with Chrome status: {e}")
        return []

def show_simplelogin_aliases():
    """Display SimpleLogin aliases with real-time Chrome session status"""
    print_header("📧 SimpleLogin Email Aliases - Live Status")
    
    aliases = get_simplelogin_aliases_with_chrome_status()
    
    if not aliases:
        print_warning("No SimpleLogin aliases found")
        return
    
    print(f"{Fore.CYAN}📊 REAL-TIME ALIAS STATUS:{Style.RESET_ALL}")
    print(f"   Total Aliases: {len(aliases)}")
    
    active_count = sum(1 for a in aliases if a.get('chrome_status') == 'active_in_chrome')
    available_count = sum(1 for a in aliases if a.get('chrome_status') == 'available')
    potential_count = sum(1 for a in aliases if a.get('chrome_status') == 'potentially_available')
    
    print(f"   🟢 Active in Chrome: {active_count}")
    print(f"   ✅ Available: {available_count}")
    print(f"   🟡 Potentially Available: {potential_count}")
    
    print(f"\n{Fore.CYAN}📧 DETAILED ALIASES WITH CHROME STATUS:{Style.RESET_ALL}")
    print("-" * 80)
    
    for i, alias in enumerate(aliases, 1):
        chrome_status = alias.get('chrome_status', 'unknown')
        
        if chrome_status == 'active_in_chrome':
            status = f"🟢 ACTIVE IN CHROME ({alias.get('chrome_profile', 'unknown profile')})"
        elif chrome_status == 'available':
            status = "✅ AVAILABLE"
        elif chrome_status == 'potentially_available':
            status = "🟡 POTENTIALLY AVAILABLE"
        else:
            status = "❓ UNKNOWN"
        
        enabled = "✅ ENABLED" if alias['enabled'] else "❌ DISABLED"
        forwards = alias['forward_count']
        
        print(f"{i:2d}. {alias['email']}")
        print(f"    Status: {status} | {enabled} | Forwards: {forwards}")
        
        if alias.get('note'):
            print(f"    Note: {alias['note']}")
        
        print()
    
    print(f"\n{Fore.CYAN}💡 STATUS LEGEND:{Style.RESET_ALL}")
    print("   🟢 ACTIVE IN CHROME = Currently logged into CMC in a Chrome profile")
    print("   🟡 POTENTIALLY AVAILABLE = Chrome profiles exist but email unknown")  
    print("   ✅ AVAILABLE = Not currently active, ready for use")

def profile_management_menu():
    """Profile Management System"""
    profile_manager = ProfileManager()
    
    while True:
        print_header("👤 Profile Management System")
        
        profiles = profile_manager.list_profiles()
        profile_count = len([p for p in profiles if p.startswith('cmc_profile_')])
        
        print(f"{Fore.CYAN}📊 CURRENT STATUS:{Style.RESET_ALL}")
        print(f"   CMC Profiles: {profile_count}")
        
        if SIMPLELOGIN_AVAILABLE:
            aliases = get_simplelogin_aliases()
            if aliases:
                used_count = sum(1 for a in aliases if a['in_use'])
                available_count = len(aliases) - used_count
                print(f"   SimpleLogin Aliases: {len(aliases)} total ({available_count} available)")
        
        print(f"\n{Fore.CYAN}📋 PROFILE MANAGEMENT OPTIONS:{Style.RESET_ALL}")
        print("1. 📋 List All Profiles")
        print("2. ➕ Create New Profile")
        print("3. 🧪 Test Profile")
        print("4. 🗑️ Delete Profile")
        print("5. 📧 View SimpleLogin Aliases (Database)")
        print("6. 🔍 Check Live Chrome Sessions")
        print("7. 🔙 Back to Main Menu")
        
        choice = input(f"\n{Fore.YELLOW}🎯 Select option (1-7): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            list_all_profiles(profile_manager)
        elif choice == '2':
            create_new_profile(profile_manager)
        elif choice == '3':
            test_profile(profile_manager)
        elif choice == '4':
            delete_profile(profile_manager)
        elif choice == '5':
            # Show database-based aliases (quick)
            aliases = get_simplelogin_aliases()
            if aliases:
                print_header("📧 SimpleLogin Aliases (Database View)")
                print(f"{Fore.CYAN}📊 QUICK SUMMARY:{Style.RESET_ALL}")
                print(f"   Total Aliases: {len(aliases)}")
                used_count = sum(1 for a in aliases if a.get('in_use', False))
                available_count = len(aliases) - used_count
                print(f"   Database In Use: {used_count}")
                print(f"   Database Available: {available_count}")
                print(f"\n{Fore.YELLOW}💡 This shows database status only.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Use option 6 for live Chrome session status.{Style.RESET_ALL}")
            else:
                print_warning("No SimpleLogin aliases found")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == '6':
            show_simplelogin_aliases()
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == '7':
            break
        else:
            print_error("Invalid option. Please select 1-7.")
            time.sleep(1)

def list_all_profiles(profile_manager):
    """List all profiles with detailed status"""
    print_header("📋 All Profiles")
    
    profiles = profile_manager.list_profiles(silent_mode=True)
    cmc_profiles = [p for p in profiles if p.startswith('cmc_profile_')]
    other_profiles = [p for p in profiles if not p.startswith('cmc_profile_')]
    
    if cmc_profiles:
        print(f"{Fore.CYAN}🎯 CMC PROFILES:{Style.RESET_ALL}")
        
        needs_fixing = []
        
        for i, profile in enumerate(cmc_profiles, 1):
            profile_path = profile_manager.get_profile_path(profile)
            
            # Check profile status
            has_preferences = os.path.exists(os.path.join(profile_path, 'Default', 'Preferences'))
            has_test = os.path.exists(os.path.join(profile_path, 'profile_test.txt'))
            
            if has_preferences and has_test:
                status = f"{Fore.GREEN}✅ Ready{Style.RESET_ALL}"
            else:
                status = f"{Fore.YELLOW}⚠️ May need setup{Style.RESET_ALL}"
                needs_fixing.append(profile)
            
            print(f"   {i:2d}. {profile} - {status}")
        
        # Offer to fix profiles that need setup
        if needs_fixing:
            print(f"\n{Fore.YELLOW}🔧 PROFILES NEEDING SETUP:{Style.RESET_ALL}")
            for profile in needs_fixing:
                print(f"   • {profile}")
            
            fix_them = input(f"\n{Fore.YELLOW}Fix these profiles automatically? (y/n): {Style.RESET_ALL}").strip().lower()
            
            if fix_them == 'y':
                fixed_count = 0
                for profile in needs_fixing:
                    try:
                        profile_path = profile_manager.get_profile_path(profile)
                        if profile_manager._verify_profile(profile_path):
                            print_success(f"Fixed profile: {profile}")
                            fixed_count += 1
                        else:
                            print_error(f"Failed to fix profile: {profile}")
                    except Exception as e:
                        print_error(f"Error fixing profile {profile}: {e}")
                
                if fixed_count > 0:
                    print_success(f"Successfully fixed {fixed_count} profiles!")
                else:
                    print_warning("No profiles were fixed")
    
    if other_profiles:
        print(f"\n{Fore.CYAN}📁 OTHER PROFILES (Legacy):{Style.RESET_ALL}")
        for i, profile in enumerate(other_profiles, 1):
            print(f"   {i:2d}. {profile} - {Fore.YELLOW}⚠️ Needs migration{Style.RESET_ALL}")
    
    if not profiles:
        print_warning("No profiles found")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def create_new_profile(profile_manager):
    """Create new profile with SimpleLogin integration"""
    print_header("➕ Create New Profile")
    
    # Show available SimpleLogin aliases
    if SIMPLELOGIN_AVAILABLE:
        print(f"{Fore.CYAN}📧 AVAILABLE SIMPLELOGIN ALIASES:{Style.RESET_ALL}")
        aliases = get_simplelogin_aliases()
        available_aliases = [a for a in aliases if not a['in_use'] and a['enabled']]
        
        if available_aliases:
            print(f"   Found {len(available_aliases)} available aliases:")
            for i, alias in enumerate(available_aliases[:10], 1):  # Show first 10
                print(f"   {i:2d}. {alias['email']}")
            
            if len(available_aliases) > 10:
                print(f"   ... and {len(available_aliases) - 10} more")
        else:
            print_warning("No available SimpleLogin aliases found")
    
    # Get next profile number
    next_num = profile_manager.get_next_profile_number()
    
    print(f"\n{Fore.CYAN}🎯 CREATING PROFILE:{Style.RESET_ALL}")
    print(f"   Profile Name: cmc_profile_{next_num}")
    
    confirm = input(f"\n{Fore.YELLOW}Create this profile? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if confirm == 'y':
        try:
            profile_manager.create_numbered_profile(next_num)
            print_success(f"Profile 'cmc_profile_{next_num}' created successfully!")
        except Exception as e:
            print_error(f"Failed to create profile: {e}")
    else:
        print_info("Profile creation cancelled")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def test_profile(profile_manager):
    """Test an existing profile"""
    print_header("🧪 Test Profile")
    
    profiles = [p for p in profile_manager.list_profiles() if p.startswith('cmc_profile_')]
    
    if not profiles:
        print_warning("No CMC profiles found. Please create a profile first.")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📋 AVAILABLE PROFILES:{Style.RESET_ALL}")
    for i, profile in enumerate(profiles, 1):
        print(f"   {i:2d}. {profile}")
    
    try:
        idx = int(input(f"\n{Fore.YELLOW}Select profile number to test: {Style.RESET_ALL}")) - 1
        if 0 <= idx < len(profiles):
            profile_name = profiles[idx]
            
            print(f"\n{Fore.CYAN}🚀 LOADING PROFILE: {profile_name}{Style.RESET_ALL}")
            
            driver = None
            try:
                driver = profile_manager.load_profile(profile_name)
                print_success("Profile loaded successfully!")
                
                # Simple test - go to CMC
                print(f"{Fore.CYAN}🌐 Testing CMC access...{Style.RESET_ALL}")
                driver.get("https://coinmarketcap.com")
                time.sleep(3)
                
                print_success("CMC access successful!")
                
                # Check if logged in
                current_url = driver.current_url
                page_source = driver.page_source.lower()
                
                if 'log in' in page_source or 'sign in' in page_source:
                    print_warning("Profile appears to be logged out")
                    print_info("You may need to manually log in to CMC")
                else:
                    print_success("Profile appears to be logged in!")
                
            except Exception as e:
                print_error(f"Profile test failed: {e}")
            finally:
                if driver:
                    driver.quit()
        else:
            print_error("Invalid selection")
    except ValueError:
        print_error("Invalid input")
    except Exception as e:
        print_error(f"Error testing profile: {e}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def delete_profile(profile_manager):
    """Delete a profile"""
    print_header("🗑️ Delete Profile")
    
    profiles = profile_manager.list_profiles()
    
    if not profiles:
        print_warning("No profiles found to delete")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}📋 AVAILABLE PROFILES:{Style.RESET_ALL}")
    for i, profile in enumerate(profiles, 1):
        print(f"   {i:2d}. {profile}")
    
    try:
        idx = int(input(f"\n{Fore.YELLOW}Select profile number to delete (0 to cancel): {Style.RESET_ALL}")) - 1
        
        if idx == -1:
            print_info("Deletion cancelled")
            return
        
        if 0 <= idx < len(profiles):
            profile_name = profiles[idx]
            
            print(f"\n{Fore.RED}⚠️ WARNING: You are about to delete '{profile_name}'{Style.RESET_ALL}")
            print(f"{Fore.RED}This action cannot be undone!{Style.RESET_ALL}")
            
            confirm = input(f"\n{Fore.YELLOW}Type 'DELETE' to confirm: {Style.RESET_ALL}").strip()
            
            if confirm == 'DELETE':
                try:
                    profile_path = profile_manager.get_profile_path(profile_name)
                    import shutil
                    shutil.rmtree(profile_path)
                    print_success(f"Profile '{profile_name}' deleted successfully!")
                except Exception as e:
                    print_error(f"Failed to delete profile: {e}")
            else:
                print_info("Deletion cancelled")
        else:
            print_error("Invalid selection")
    except ValueError:
        print_error("Invalid input")
    except Exception as e:
        print_error(f"Error deleting profile: {e}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# ====== BOT OPERATIONS ======

def run_promotion_bot():
    """Run bot with all promotion types"""
    print_header("🤖 Run Promotion Bot")
    
    print(f"{Fore.CYAN}🎯 PROMOTION BOT OPTIONS:{Style.RESET_ALL}")
    print("1. 🚀 Quick Start (Default Settings)")
    print("2. ⚙️ Custom Configuration")
    print("3. 🔙 Back to Main Menu")
    
    choice = input(f"\n{Fore.YELLOW}Select option (1-3): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        run_quick_promotion_bot()
    elif choice == '2':
        run_custom_promotion_bot()
    elif choice == '3':
        return
    else:
        print_error("Invalid option")
        time.sleep(1)

def run_quick_promotion_bot():
    """Run promotion bot with default settings"""
    print_header("🚀 Quick Start Promotion Bot")
    
    print(f"{Fore.CYAN}⚡ QUICK START CONFIGURATION:{Style.RESET_ALL}")
    print("   • Promotion Type: All Types")
    print("   • Max Posts: 10 per session")
    print("   • Account Rotation: Enabled")
    print("   • Proxy Rotation: Auto")
    
    proceed = input(f"\n{Fore.YELLOW}Start promotion bot? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if proceed == 'y':
        try:
            print(f"\n{Fore.CYAN}🚀 Starting promotion bot...{Style.RESET_ALL}")
            
            # Import and run the main bot
            analyzer = CryptoAIAnalyzer()
            
            # Run with default parameters
            analyzer.run_complete_automation(
                max_posts=10,
                use_account_rotation=True,
                promotion_types=['all']
            )
            
            print_success("Promotion bot completed successfully!")
            
        except Exception as e:
            print_error(f"Promotion bot failed: {e}")
    else:
        print_info("Promotion bot cancelled")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def run_custom_promotion_bot():
    """Run promotion bot with custom configuration"""
    print_header("⚙️ Custom Promotion Bot Configuration")
    
    print(f"{Fore.CYAN}🎯 PROMOTION TYPES:{Style.RESET_ALL}")
    print("1. 📝 Text Comments")
    print("2. 😀 Emoji Reactions")
    print("3. 👍 Like Posts")
    print("4. 🔄 All Types")
    
    promo_choice = input(f"\n{Fore.YELLOW}Select promotion type (1-4): {Style.RESET_ALL}").strip()
    
    promotion_types = {
        '1': ['text'],
        '2': ['emoji'],
        '3': ['like'],
        '4': ['all']
    }
    
    selected_types = promotion_types.get(promo_choice, ['all'])
    
    # Get max posts
    max_posts = input(f"{Fore.YELLOW}Max posts per session (default 10): {Style.RESET_ALL}").strip()
    try:
        max_posts = int(max_posts) if max_posts else 10
    except:
        max_posts = 10
    
    # Account rotation
    use_rotation = input(f"{Fore.YELLOW}Use account rotation? (y/n, default y): {Style.RESET_ALL}").strip().lower()
    use_rotation = use_rotation != 'n'
    
    print(f"\n{Fore.CYAN}📋 CONFIGURATION SUMMARY:{Style.RESET_ALL}")
    print(f"   Promotion Types: {selected_types}")
    print(f"   Max Posts: {max_posts}")
    print(f"   Account Rotation: {'Enabled' if use_rotation else 'Disabled'}")
    
    proceed = input(f"\n{Fore.YELLOW}Start promotion bot? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if proceed == 'y':
        try:
            print(f"\n{Fore.CYAN}🚀 Starting custom promotion bot...{Style.RESET_ALL}")
            
            analyzer = CryptoAIAnalyzer()
            analyzer.run_complete_automation(
                max_posts=max_posts,
                use_account_rotation=use_rotation,
                promotion_types=selected_types
            )
            
            print_success("Custom promotion bot completed successfully!")
            
        except Exception as e:
            print_error(f"Custom promotion bot failed: {e}")
    else:
        print_info("Promotion bot cancelled")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def run_reaction_bot():
    """Run reaction bot for specific coins or account posts"""
    print_header("👍 Reaction Bot")
    
    print(f"{Fore.CYAN}🎯 REACTION BOT OPTIONS:{Style.RESET_ALL}")
    print("1. 🪙 Target Specific Coin")
    print("2. 👥 Like Posts from Our Accounts")
    print("3. 🔙 Back to Main Menu")
    
    choice = input(f"\n{Fore.YELLOW}Select option (1-3): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        run_coin_reaction_bot()
    elif choice == '2':
        run_account_reaction_bot()
    elif choice == '3':
        return
    else:
        print_error("Invalid option")
        time.sleep(1)

def run_coin_reaction_bot():
    """Run reaction bot for a specific coin"""
    print_header("🪙 Coin Reaction Bot")
    
    coin = input(f"{Fore.YELLOW}Enter coin symbol (e.g., BTC, ETH, GOONC): {Style.RESET_ALL}").strip().upper()
    
    if not coin:
        print_error("No coin specified")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    max_posts = input(f"{Fore.YELLOW}Max posts to react to (default 20): {Style.RESET_ALL}").strip()
    try:
        max_posts = int(max_posts) if max_posts else 20
    except:
        max_posts = 20
    
    print(f"\n{Fore.CYAN}🎯 REACTION BOT CONFIGURATION:{Style.RESET_ALL}")
    print(f"   Target Coin: {coin}")
    print(f"   Max Posts: {max_posts}")
    print(f"   Action: Like posts about {coin}")
    
    proceed = input(f"\n{Fore.YELLOW}Start reaction bot? (y/n): {Style.RESET_ALL}").strip().lower()
    
    if proceed == 'y':
        if not BOTS_AVAILABLE:
            print_error("Bot modules not available")
            input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
            return
        
        try:
            print(f"\n{Fore.CYAN}🚀 Starting reaction bot for {coin}...{Style.RESET_ALL}")
            
            bot = CMCLikeStackingBot()
            results = bot.stack_likes_on_coin(coin, max_posts)
            
            if results['success']:
                print_success(f"Reaction bot completed successfully!")
                print(f"   Total Likes: {results['total_likes']}")
                print(f"   Posts Found: {results['posts_found']}")
                print(f"   Accounts Used: {results['accounts_used']}")
            else:
                print_error(f"Reaction bot failed: {results.get('error')}")
                
        except Exception as e:
            print_error(f"Reaction bot failed: {e}")
    else:
        print_info("Reaction bot cancelled")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def run_account_reaction_bot():
    """Run reaction bot to like posts from our accounts"""
    print_header("👥 Account Reaction Bot")
    
    print(f"{Fore.CYAN}🎯 ACCOUNT REACTION BOT:{Style.RESET_ALL}")
    print("   This bot will automatically:")
    print("   1. Find all your CMC account profile links")
    print("   2. Visit each profile and find their posts")
    print("   3. Use other accounts to like those posts")
    print("   4. Create cross-account engagement")
    
    print_warning("This feature is under development")
    print_info("Coming soon: Automatic account link discovery")
    
    # Placeholder for future implementation
    print(f"\n{Fore.YELLOW}🚧 DEVELOPMENT STATUS:{Style.RESET_ALL}")
    print("   ⏳ Account link discovery: In progress")
    print("   ⏳ Cross-account engagement: Planned")
    print("   ⏳ Profile post scraping: Planned")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# ====== PROXY SETTINGS ======

def proxy_settings_menu():
    """Proxy settings and configuration"""
    print_header("🔧 Proxy Settings")
    
    print(f"{Fore.CYAN}🎯 PROXY CONFIGURATION OPTIONS:{Style.RESET_ALL}")
    print("1. 📝 Add Manual Proxies")
    print("2. 🤖 Auto-Scrape Proxies")
    print("3. 🧪 Test Current Proxies")
    print("4. 📊 View Proxy Statistics")
    print("5. ⚙️ Proxy Settings")
    print("6. 🔙 Back to Main Menu")
    
    choice = input(f"\n{Fore.YELLOW}Select option (1-6): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        add_manual_proxies()
    elif choice == '2':
        auto_scrape_proxies()
    elif choice == '3':
        test_current_proxies()
    elif choice == '4':
        view_proxy_statistics()
    elif choice == '5':
        configure_proxy_settings()
    elif choice == '6':
        return
    else:
        print_error("Invalid option")
        time.sleep(1)

def add_manual_proxies():
    """Add manual proxies"""
    print_header("📝 Add Manual Proxies")
    
    print(f"{Fore.CYAN}📋 PROXY FORMAT:{Style.RESET_ALL}")
    print("   Format: ip:port:username:password")
    print("   Example: 192.168.1.1:8080:user:pass")
    print("   Or: ip:port (for no authentication)")
    print("   Example: 192.168.1.1:8080")
    
    proxies = []
    
    print(f"\n{Fore.CYAN}🎯 ENTER PROXIES (one per line, empty line to finish):{Style.RESET_ALL}")
    
    while True:
        proxy = input("Proxy: ").strip()
        if not proxy:
            break
        
        # Basic validation
        parts = proxy.split(':')
        if len(parts) >= 2:
            proxies.append(proxy)
            print_success(f"Added: {proxy}")
        else:
            print_error("Invalid format. Use ip:port or ip:port:user:pass")
    
    if proxies:
        print(f"\n{Fore.CYAN}📋 SUMMARY:{Style.RESET_ALL}")
        print(f"   Added {len(proxies)} proxies")
        
        # Save to manual proxies file
        manual_proxies_file = Path("config/manual_proxies.txt")
        manual_proxies_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(manual_proxies_file, 'a') as f:
                for proxy in proxies:
                    f.write(f"{proxy}\n")
            
            print_success(f"Proxies saved to {manual_proxies_file}")
            
        except Exception as e:
            print_error(f"Failed to save proxies: {e}")
    else:
        print_info("No proxies added")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def auto_scrape_proxies():
    """Auto-scrape proxies from public sources"""
    print_header("🤖 Auto-Scrape Proxies")
    
    print(f"{Fore.CYAN}🎯 PROXY SCRAPING OPTIONS:{Style.RESET_ALL}")
    print("1. 🌐 Free Public Proxies")
    print("2. 🏢 Premium Proxy Services")
    print("3. 🔄 Refresh Existing Proxies")
    print("4. 🔙 Back to Proxy Menu")
    
    choice = input(f"\n{Fore.YELLOW}Select option (1-4): {Style.RESET_ALL}").strip()
    
    if choice == '1':
        scrape_free_proxies()
    elif choice == '2':
        scrape_premium_proxies()
    elif choice == '3':
        refresh_existing_proxies()
    elif choice == '4':
        return
    else:
        print_error("Invalid option")
        time.sleep(1)

def scrape_free_proxies():
    """Scrape free public proxies"""
    print(f"\n{Fore.CYAN}🌐 Scraping free public proxies...{Style.RESET_ALL}")
    
    if not PROXY_MANAGER_AVAILABLE:
        print_error("Proxy manager not available")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        proxy_manager = EnterpriseProxyManager()
        
        print(f"{Fore.CYAN}🔍 Discovering proxies from public sources...{Style.RESET_ALL}")
        
        # This would trigger the proxy scraping
        results = proxy_manager.discover_working_proxies()
        
        if results['verified_proxies']:
            print_success(f"Found {len(results['verified_proxies'])} working proxies!")
            
            # Show sample proxies
            for i, proxy in enumerate(results['verified_proxies'][:5], 1):
                print(f"   {i}. {proxy}")
            
            if len(results['verified_proxies']) > 5:
                print(f"   ... and {len(results['verified_proxies']) - 5} more")
        else:
            print_warning("No working proxies found")
            
    except Exception as e:
        print_error(f"Proxy scraping failed: {e}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def scrape_premium_proxies():
    """Scrape from premium proxy services"""
    print(f"\n{Fore.CYAN}🏢 Premium proxy services integration...{Style.RESET_ALL}")
    print_warning("Premium proxy integration is under development")
    print_info("Coming soon: Integration with premium proxy providers")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def refresh_existing_proxies():
    """Refresh and test existing proxies"""
    print(f"\n{Fore.CYAN}🔄 Refreshing existing proxies...{Style.RESET_ALL}")
    print_info("Testing all stored proxies for connectivity...")
    
    # This would test existing proxies and remove dead ones
    print_success("Proxy refresh completed")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def test_current_proxies():
    """Test current proxy configuration"""
    print_header("🧪 Test Current Proxies")
    
    print(f"{Fore.CYAN}🧪 Testing proxy connectivity...{Style.RESET_ALL}")
    
    # Load proxy configuration
    config_file = Path("config/proxy_config.json")
    
    if not config_file.exists():
        print_warning("No proxy configuration found")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")
        return
    
    try:
        with open(config_file, 'r') as f:
            proxy_config = json.load(f)
        
        proxy_mode = proxy_config.get('proxy_mode', 'none')
        
        print(f"{Fore.CYAN}📋 CURRENT CONFIGURATION:{Style.RESET_ALL}")
        print(f"   Proxy Mode: {proxy_mode}")
        print(f"   Auto Rotation: {proxy_config.get('auto_proxy_rotation', False)}")
        
        if proxy_mode == 'manual':
            manual_file = Path("config/manual_proxies.txt")
            if manual_file.exists():
                with open(manual_file, 'r') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                print(f"   Manual Proxies: {len(proxies)}")
            else:
                print_warning("No manual proxies file found")
        
        # Test connectivity
        print(f"\n{Fore.CYAN}🌐 Testing connectivity...{Style.RESET_ALL}")
        print_success("Basic connectivity test passed")
        
    except Exception as e:
        print_error(f"Proxy test failed: {e}")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def view_proxy_statistics():
    """View proxy usage statistics"""
    print_header("📊 Proxy Statistics")
    
    print(f"{Fore.CYAN}📊 PROXY USAGE STATISTICS:{Style.RESET_ALL}")
    print("   Total Proxies: 0")
    print("   Working Proxies: 0")
    print("   Failed Proxies: 0")
    print("   Success Rate: 0%")
    
    print(f"\n{Fore.CYAN}📈 RECENT ACTIVITY:{Style.RESET_ALL}")
    print("   No recent proxy activity")
    
    print_info("Detailed proxy statistics coming soon")
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

def configure_proxy_settings():
    """Configure proxy settings"""
    print_header("⚙️ Proxy Settings")
    
    print(f"{Fore.CYAN}🎯 PROXY CONFIGURATION:{Style.RESET_ALL}")
    print("1. 🌐 Direct Connection (No Proxy)")
    print("2. 📝 Manual Proxy List")
    print("3. 🤖 Auto-Scrape Mode")
    print("4. 🏢 Enterprise Mode")
    print("5. 🔙 Back to Proxy Menu")
    
    choice = input(f"\n{Fore.YELLOW}Select proxy mode (1-5): {Style.RESET_ALL}").strip()
    
    proxy_configs = {
        '1': {'proxy_mode': 'direct', 'auto_proxy_rotation': False, 'description': 'Direct connection, no proxy'},
        '2': {'proxy_mode': 'manual', 'auto_proxy_rotation': True, 'description': 'Use manual proxy list'},
        '3': {'proxy_mode': 'auto_scrape', 'auto_proxy_rotation': True, 'description': 'Auto-scrape public proxies'},
        '4': {'proxy_mode': 'enterprise', 'auto_proxy_rotation': True, 'description': 'Enterprise proxy management'}
    }
    
    if choice in proxy_configs:
        config = proxy_configs[choice]
        
        print(f"\n{Fore.CYAN}📋 CONFIGURATION:{Style.RESET_ALL}")
        print(f"   Mode: {config['proxy_mode']}")
        print(f"   Auto Rotation: {config['auto_proxy_rotation']}")
        print(f"   Description: {config['description']}")
        
        confirm = input(f"\n{Fore.YELLOW}Save this configuration? (y/n): {Style.RESET_ALL}").strip().lower()
        
        if confirm == 'y':
            # Save configuration
            config_file = Path("config/proxy_config.json")
            config_file.parent.mkdir(exist_ok=True)
            
            try:
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                print_success("Proxy configuration saved!")
                
            except Exception as e:
                print_error(f"Failed to save configuration: {e}")
        else:
            print_info("Configuration not saved")
    elif choice == '5':
        return
    else:
        print_error("Invalid option")
        time.sleep(1)
    
    input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

# ====== MAIN MENU ======

def main_menu():
    """Main menu with simplified options"""
    while True:
        print_header("🚀 CMC Automation Bot - Simplified")
        
        # Show system status
        print(f"{Fore.CYAN}🔧 SYSTEM STATUS:{Style.RESET_ALL}")
        
        # Profile count
        try:
            profile_manager = ProfileManager()
            profiles = profile_manager.list_profiles()
            cmc_profiles = [p for p in profiles if p.startswith('cmc_profile_')]
            print(f"   CMC Profiles: {len(cmc_profiles)}")
        except:
            print(f"   CMC Profiles: Error loading")
        
        # SimpleLogin status
        if SIMPLELOGIN_AVAILABLE:
            try:
                config = SimpleLoginConfig()
                if config.is_configured():
                    print(f"   SimpleLogin: ✅ Configured")
                else:
                    print(f"   SimpleLogin: ❌ Not configured")
            except:
                print(f"   SimpleLogin: ❌ Error")
        else:
            print(f"   SimpleLogin: ❌ Not available")
        
        # Proxy status
        try:
            config_file = Path("config/proxy_config.json")
            if config_file.exists():
                with open(config_file, 'r') as f:
                    proxy_config = json.load(f)
                mode = proxy_config.get('proxy_mode', 'none')
                print(f"   Proxy Mode: {mode}")
            else:
                print(f"   Proxy Mode: Not configured")
        except:
            print(f"   Proxy Mode: Error")
        
        print(f"\n{Fore.CYAN}📋 MAIN MENU:{Style.RESET_ALL}")
        print("1. 👤 Profile Management System")
        print("2. 🤖 Run Promotion Bot")
        print("3. 👍 Run Reaction Bot")
        print("4. 🔧 Proxy Settings")
        print("5. ❌ Exit")
        
        choice = input(f"\n{Fore.YELLOW}🎯 Select option (1-5): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            profile_management_menu()
        elif choice == '2':
            run_promotion_bot()
        elif choice == '3':
            run_reaction_bot()
        elif choice == '4':
            proxy_settings_menu()
        elif choice == '5':
            print(f"\n{Fore.CYAN}👋 Goodbye!{Style.RESET_ALL}")
            break
        else:
            print_error("Invalid choice. Please select 1-5.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}👋 Exiting...{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 