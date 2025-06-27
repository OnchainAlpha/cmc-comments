#!/usr/bin/env python3
"""
CMC Profile Interaction Bot

This bot:
1. Stores CMC profile URLs when logged in
2. Visits each stored profile page
3. Scrolls through the profile to load all posts
4. Clicks reaction buttons on all posts from that profile
5. Uses account rotation system
"""

import sys
import os
import time
import logging
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.utils.helpers import random_delay

class CMCProfileInteractionBot:
    def __init__(self, use_account_rotation=True):
        self.logger = logging.getLogger(__name__)
        
        # Initialize profile manager with account rotation
        self.profile_manager = ProfileManager()
        self.use_account_rotation = use_account_rotation
        
        # CMC URLs
        self.base_url = "https://coinmarketcap.com"
        self.community_url = "https://coinmarketcap.com/community/"
        
        # Storage for profile data
        self.profiles_storage_file = "stored_cmc_profiles.json"
        self.stored_profiles = self._load_stored_profiles()
        
        # Initialize driver
        self.driver = None
        self._load_profile()
        
        print(f"🤖 CMC Profile Interaction Bot initialized")
        print(f"   Account Rotation: {'✅ ENABLED' if use_account_rotation else '❌ DISABLED'}")
        print(f"   Stored Profiles: {len(self.stored_profiles)}")

    def _load_profile(self):
        """Load a browser profile"""
        try:
            # Get available CMC profiles
            profiles = [p for p in self.profile_manager.list_profiles(silent_mode=True) if p.startswith('cmc_profile_')]
            
            if not profiles:
                raise Exception("No CMC profiles found. Please create profiles first.")
            
            # Load first available profile
            profile_name = profiles[0]
            print(f"🔄 Loading profile: {profile_name}")
            self.driver = self.profile_manager.load_profile(profile_name)
            print(f"✅ Profile loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load profile: {e}")
            raise

    def _load_stored_profiles(self) -> Dict:
        """Load stored CMC profiles from JSON file"""
        try:
            if os.path.exists(self.profiles_storage_file):
                with open(self.profiles_storage_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            print(f"⚠️ Error loading stored profiles: {e}")
            return {}

    def _save_stored_profiles(self):
        """Save stored profiles to JSON file"""
        try:
            with open(self.profiles_storage_file, 'w') as f:
                json.dump(self.stored_profiles, f, indent=2)
            print(f"💾 Saved {len(self.stored_profiles)} stored profiles")
        except Exception as e:
            print(f"❌ Error saving profiles: {e}")

    def detect_and_store_current_profile(self) -> Optional[str]:
        """
        Detect current logged-in CMC profile and store it
        
        Returns:
            Profile URL if detected, None otherwise
        """
        try:
            print("\n🔍 DETECTING CURRENT CMC PROFILE")
            print("="*40)
            
            # Navigate to CMC community to get profile info
            print("1. Navigating to CMC community...")
            self.driver.get(self.community_url)
            time.sleep(3)
            
            # Look for profile indicators
            profile_selectors = [
                # Profile menu/dropdown selectors
                "[data-test='profile-menu']",
                ".profile-menu",
                "[class*='profile']",
                # Username/profile link selectors
                "a[href*='/community/profile/']",
                "[class*='username']",
                "[class*='user-name']",
                # Navigation profile links
                "nav a[href*='/profile/']"
            ]
            
            profile_url = None
            profile_name = None
            
            for selector in profile_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute('href') or ''
                        text = element.text.strip()
                        
                        if '/community/profile/' in href and href not in ['', '#']:
                            profile_url = href
                            profile_name = text or "Unknown"
                            print(f"✅ Found profile URL: {profile_url}")
                            print(f"✅ Profile name: {profile_name}")
                            break
                    
                    if profile_url:
                        break
                except Exception as e:
                    continue
            
            # Alternative method: try to find profile from page source
            if not profile_url:
                try:
                    page_source = self.driver.page_source
                    import re
                    
                    # Look for profile URLs in page source
                    profile_pattern = r'https://coinmarketcap\.com/community/profile/([^/"]+)/?'
                    matches = re.findall(profile_pattern, page_source)
                    
                    if matches:
                        profile_username = matches[0]
                        profile_url = f"https://coinmarketcap.com/community/profile/{profile_username}/"
                        profile_name = profile_username
                        print(f"✅ Found profile via page source: {profile_url}")
                except Exception as e:
                    print(f"⚠️ Page source search failed: {e}")
            
            # Store the profile if found
            if profile_url:
                profile_data = {
                    'url': profile_url,
                    'name': profile_name,
                    'detected_at': datetime.now().isoformat(),
                    'browser_profile': getattr(self.profile_manager, 'current_profile', 'unknown'),
                    'last_interaction': None,
                    'total_interactions': 0
                }
                
                # Use profile name or URL as key
                profile_key = profile_name if profile_name != "Unknown" else profile_url.split('/')[-2]
                self.stored_profiles[profile_key] = profile_data
                self._save_stored_profiles()
                
                print(f"💾 Stored profile: {profile_key}")
                return profile_url
            else:
                print("❌ Could not detect current profile")
                print("💡 Make sure you're logged into CMC")
                return None
                
        except Exception as e:
            print(f"❌ Error detecting profile: {e}")
            return None

    def add_manual_profile(self, profile_url: str, profile_name: str = None) -> bool:
        """
        Manually add a CMC profile URL
        
        Args:
            profile_url: CMC profile URL
            profile_name: Display name for the profile
            
        Returns:
            True if added successfully
        """
        try:
            print(f"\n📝 ADDING MANUAL PROFILE")
            print("="*30)
            
            # Validate URL format
            if not profile_url.startswith('https://coinmarketcap.com/community/profile/'):
                print("❌ Invalid profile URL format")
                print("💡 URL should be like: https://coinmarketcap.com/community/profile/username/")
                return False
            
            # Extract username from URL if no name provided
            if not profile_name:
                try:
                    profile_name = profile_url.split('/')[-2] if profile_url.endswith('/') else profile_url.split('/')[-1]
                except:
                    profile_name = "Manual Profile"
            
            # Store the profile
            profile_data = {
                'url': profile_url,
                'name': profile_name,
                'detected_at': datetime.now().isoformat(),
                'browser_profile': 'manual',
                'last_interaction': None,
                'total_interactions': 0,
                'manually_added': True
            }
            
            self.stored_profiles[profile_name] = profile_data
            self._save_stored_profiles()
            
            print(f"✅ Added profile: {profile_name}")
            print(f"🔗 URL: {profile_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding manual profile: {e}")
            return False

    def visit_profile_and_interact(self, profile_url: str, max_posts: int = 50) -> Dict:
        """
        Visit a specific CMC profile and interact with all posts
        
        Args:
            profile_url: URL of the CMC profile to visit
            max_posts: Maximum number of posts to interact with
            
        Returns:
            Dictionary with interaction results
        """
        try:
            print(f"\n🎯 VISITING PROFILE AND INTERACTING")
            print("="*50)
            print(f"URL: {profile_url}")
            print(f"Max Posts: {max_posts}")
            
            # Navigate to profile
            print("1. Navigating to profile page...")
            self.driver.get(profile_url)
            time.sleep(5)  # Wait for page load
            
            # Validate we're on a profile page
            if not self._validate_profile_page():
                return {
                    'success': False,
                    'error': 'Not a valid profile page or page failed to load'
                }
            
            # Scroll and collect posts
            print("2. Scrolling to collect posts...")
            posts_data = self._scroll_and_collect_posts(max_posts)
            
            if not posts_data:
                return {
                    'success': False,
                    'error': 'No posts found on profile page'
                }
            
            print(f"3. Found {len(posts_data)} posts, starting interactions...")
            
            # Interact with all posts
            interaction_results = self._interact_with_profile_posts(posts_data)
            
            # Update stored profile data
            profile_name = self._get_profile_name_from_url(profile_url)
            if profile_name in self.stored_profiles:
                self.stored_profiles[profile_name]['last_interaction'] = datetime.now().isoformat()
                self.stored_profiles[profile_name]['total_interactions'] += interaction_results.get('successful_interactions', 0)
                self._save_stored_profiles()
            
            return {
                'success': True,
                'profile_url': profile_url,
                'posts_found': len(posts_data),
                'interaction_results': interaction_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error visiting profile: {e}")
            return {
                'success': False,
                'error': str(e),
                'profile_url': profile_url
            }

    def _validate_profile_page(self) -> bool:
        """Validate that we're on a valid CMC profile page"""
        try:
            # Check URL
            current_url = self.driver.current_url
            if '/community/profile/' not in current_url:
                print("❌ Not on a profile page")
                return False
            
            # Look for profile page indicators
            profile_indicators = [
                "[class*='profile']",
                "[data-test*='profile']",
                ".user-profile",
                "[class*='user-info']"
            ]
            
            for selector in profile_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Profile page validated with selector: {selector}")
                        return True
                except:
                    continue
            
            # Check page title
            title = self.driver.title.lower()
            if 'profile' in title or 'community' in title:
                print("✅ Profile page validated by title")
                return True
            
            print("⚠️ Could not validate profile page, but continuing...")
            return True  # Continue anyway
            
        except Exception as e:
            print(f"⚠️ Error validating profile page: {e}")
            return True  # Continue anyway

    def _scroll_and_collect_posts(self, max_posts: int) -> List[Dict]:
        """
        Scroll through the profile page and collect all post elements
        
        Args:
            max_posts: Maximum number of posts to collect
            
        Returns:
            List of post data dictionaries
        """
        posts_data = []
        posts_found = set()  # To avoid duplicates
        scroll_attempts = 0
        max_scroll_attempts = 20  # Prevent infinite scrolling
        
        try:
            while len(posts_data) < max_posts and scroll_attempts < max_scroll_attempts:
                scroll_attempts += 1
                
                print(f"   📜 Scroll attempt {scroll_attempts}/{max_scroll_attempts}")
                
                # Find post elements
                post_selectors = [
                    "[data-test*='post']",
                    "[class*='post-card']",
                    "[data-role='post-card']",
                    ".community-post",
                    "[class*='community-post']",
                    "article",
                    "[role='article']"
                ]
                
                new_posts_found = 0
                
                for selector in post_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for i, element in enumerate(elements):
                            try:
                                # Create unique identifier for post
                                post_id = f"post_{scroll_attempts}_{i}_{element.location['y']}"
                                
                                if post_id in posts_found:
                                    continue
                                
                                # Check if element has content
                                if not element.text.strip():
                                    continue
                                
                                post_data = self._extract_post_data_from_profile(element, len(posts_data) + 1)
                                if post_data:
                                    post_data['post_id'] = post_id
                                    posts_data.append(post_data)
                                    posts_found.add(post_id)
                                    new_posts_found += 1
                                    
                                    if len(posts_data) >= max_posts:
                                        break
                            except Exception as e:
                                continue
                        
                        if len(posts_data) >= max_posts:
                            break
                            
                    except Exception as e:
                        continue
                
                print(f"      📊 Found {new_posts_found} new posts (total: {len(posts_data)})")
                
                # Scroll down to load more posts
                if len(posts_data) < max_posts:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)  # Wait for content to load
                    
                    # Check if we're at the bottom of the page
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
                    final_height = self.driver.execute_script("return document.body.scrollHeight")
                    
                    if new_height == final_height and new_posts_found == 0:
                        print("      📋 Reached end of page")
                        break
            
            print(f"✅ Collected {len(posts_data)} posts total")
            return posts_data
            
        except Exception as e:
            print(f"❌ Error during scrolling: {e}")
            return posts_data

    def _extract_post_data_from_profile(self, post_element, post_index: int) -> Optional[Dict]:
        """Extract data from a post element on a profile page"""
        try:
            post_data = {
                'index': post_index,
                'timestamp': datetime.now().isoformat(),
                'content': '',
                'author': '',
                'post_id': '',
                'emoji_button': None,
                'has_interactions': False,
                'element': post_element
            }
            
            # Extract post content
            post_data['content'] = self._extract_text_content(post_element)
            
            # Extract author (might be same as profile owner)
            post_data['author'] = self._extract_author(post_element)
            
            # Find emoji/reaction button
            emoji_button = self._find_emoji_button(post_element)
            if emoji_button:
                post_data['emoji_button'] = emoji_button
                post_data['has_interactions'] = True
            
            return post_data if post_data['content'] else None
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def _extract_text_content(self, element) -> str:
        """Extract text content from an element"""
        try:
            methods = [
                lambda: element.text,
                lambda: element.get_attribute('textContent'),
                lambda: element.get_attribute('innerText')
            ]
            
            for method in methods:
                try:
                    text = method()
                    if text and text.strip():
                        return text.strip()
                except:
                    continue
            
            return ""
        except:
            return ""

    def _extract_author(self, element) -> str:
        """Extract author information from post element"""
        author_selectors = [
            "[data-test='author-name']",
            ".author-name",
            "[class*='author']",
            "[data-role='author-name']",
            ".username",
            "[class*='username']",
            "[class*='user']"
        ]
        
        for selector in author_selectors:
            try:
                author_elem = element.find_element(By.CSS_SELECTOR, selector)
                if author_elem and author_elem.text.strip():
                    return author_elem.text.strip()
            except:
                continue
        
        return "Unknown"

    def _find_emoji_button(self, post_element) -> Optional[dict]:
        """Find the emoji/reaction button in a post element"""
        try:
            emoji_selectors = [
                # Specific selectors for CMC reaction buttons
                'div[data-test="post-emoji-action"]',
                '.post-emoji-action',
                '[class*="emoji-action"]',
                '[data-test*="emoji"]',
                # SVG-based selectors
                'svg use[href="#SMILE"]',
                'svg[class*="eyXrOz"]',
                # Generic interaction buttons
                '.base-icon-wrapper',
                '[class*="base-icon-wrapper"]',
                # Reaction buttons
                'button[class*="reaction"]',
                'div[class*="reaction"]',
                '[class*="smile"]',
                # Like buttons
                'button[class*="like"]',
                '[data-test*="like"]'
            ]
            
            for selector in emoji_selectors:
                try:
                    emoji_elements = post_element.find_elements(By.CSS_SELECTOR, selector)
                    for emoji_elem in emoji_elements:
                        if emoji_elem.is_displayed() and self._is_reaction_button(emoji_elem):
                            return {
                                'element': emoji_elem,
                                'selector': selector,
                                'clickable': emoji_elem.is_enabled()
                            }
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            return None

    def _is_reaction_button(self, element) -> bool:
        """Check if an element is actually a reaction button"""
        try:
            class_name = element.get_attribute('class') or ''
            data_test = element.get_attribute('data_test') or ''
            onclick = element.get_attribute('onclick') or ''
            tag_name = element.tag_name.lower()
            
            # Look for reaction-related indicators
            reaction_indicators = [
                'emoji-action',
                'smile',
                'post-emoji',
                'reaction',
                'base-icon-wrapper',
                'like',
                'heart'
            ]
            
            element_text = (class_name + ' ' + data_test + ' ' + onclick).lower()
            
            for indicator in reaction_indicators:
                if indicator in element_text:
                    return True
            
            # Check for clickable elements that look like buttons
            if tag_name in ['button', 'div', 'span'] and element.is_enabled():
                # Check for SVG children (reaction buttons often contain SVGs)
                try:
                    svgs = element.find_elements(By.TAG_NAME, 'svg')
                    if svgs:
                        return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            return False

    def _interact_with_profile_posts(self, posts_data: List[Dict]) -> Dict:
        """
        Interact with all posts from a profile
        
        Args:
            posts_data: List of post data dictionaries
            
        Returns:
            Interaction results summary
        """
        try:
            print(f"\n🎯 INTERACTING WITH {len(posts_data)} PROFILE POSTS")
            print("="*60)
            
            interaction_results = {
                'total_posts': len(posts_data),
                'successful_interactions': 0,
                'failed_interactions': 0,
                'posts_without_buttons': 0,
                'interactions': []
            }
            
            for i, post_data in enumerate(posts_data, 1):
                try:
                    print(f"\n🎯 Interacting with post {i}/{len(posts_data)}")
                    print(f"   📝 Content preview: {post_data['content'][:100]}...")
                    print(f"   👤 Author: {post_data['author']}")
                    
                    if not post_data.get('has_interactions'):
                        print(f"   ⚪ No reaction buttons found")
                        interaction_results['posts_without_buttons'] += 1
                        continue
                    
                    # Scroll to post to ensure it's visible
                    try:
                        post_element = post_data['element']
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", post_element)
                        time.sleep(1)
                    except:
                        pass
                    
                    # Perform the interaction
                    success = self._click_reaction_button(post_data['emoji_button'])
                    
                    interaction_record = {
                        'post_index': i,
                        'post_id': post_data['post_id'],
                        'author': post_data['author'],
                        'success': success,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    interaction_results['interactions'].append(interaction_record)
                    
                    if success:
                        print(f"   ✅ Successfully clicked reaction button")
                        interaction_results['successful_interactions'] += 1
                    else:
                        print(f"   ❌ Failed to click reaction button")
                        interaction_results['failed_interactions'] += 1
                    
                    # Add delay between interactions
                    delay = random.uniform(1, 3)
                    print(f"   ⏱️ Waiting {delay:.1f}s before next interaction...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"   ❌ Error interacting with post {i}: {str(e)}")
                    interaction_results['failed_interactions'] += 1
                    continue
            
            # Print summary
            print(f"\n📊 PROFILE INTERACTION SUMMARY")
            print("="*40)
            print(f"Total Posts: {interaction_results['total_posts']}")
            print(f"Successful: {interaction_results['successful_interactions']}")
            print(f"Failed: {interaction_results['failed_interactions']}")
            print(f"No Buttons: {interaction_results['posts_without_buttons']}")
            success_rate = (interaction_results['successful_interactions'] / max(1, interaction_results['total_posts'])) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            return interaction_results
            
        except Exception as e:
            print(f"❌ Error during profile interactions: {e}")
            return {'error': str(e)}

    def _click_reaction_button(self, reaction_button_data: Dict) -> bool:
        """Click a reaction button on a post"""
        try:
            reaction_element = reaction_button_data['element']
            
            # Try different click methods
            click_methods = [
                lambda: reaction_element.click(),
                lambda: self.driver.execute_script("arguments[0].click();", reaction_element),
                lambda: ActionChains(self.driver).move_to_element(reaction_element).click().perform()
            ]
            
            for i, method in enumerate(click_methods, 1):
                try:
                    method()
                    print(f"     ✅ Click method {i} successful")
                    return True
                except Exception as e:
                    print(f"     ⚠️ Click method {i} failed: {str(e)}")
                    continue
            
            print(f"     ❌ All click methods failed")
            return False
            
        except Exception as e:
            print(f"     ❌ Error clicking reaction button: {str(e)}")
            return False

    def process_all_stored_profiles(self, max_posts_per_profile: int = 30) -> Dict:
        """
        Process all stored profiles and interact with their posts
        
        Args:
            max_posts_per_profile: Maximum posts to interact with per profile
            
        Returns:
            Summary of all profile interactions
        """
        try:
            print(f"\n🚀 PROCESSING ALL STORED PROFILES")
            print("="*50)
            print(f"Profiles to process: {len(self.stored_profiles)}")
            print(f"Max posts per profile: {max_posts_per_profile}")
            
            if not self.stored_profiles:
                return {
                    'success': False,
                    'error': 'No stored profiles found',
                    'profiles_processed': 0
                }
            
            overall_results = {
                'profiles_processed': 0,
                'total_posts': 0,
                'total_successful_interactions': 0,
                'total_failed_interactions': 0,
                'profile_results': []
            }
            
            for profile_name, profile_data in self.stored_profiles.items():
                try:
                    print(f"\n" + "="*60)
                    print(f"📋 PROCESSING PROFILE: {profile_name}")
                    print("="*60)
                    
                    profile_url = profile_data['url']
                    
                    # Process this profile
                    results = self.visit_profile_and_interact(profile_url, max_posts_per_profile)
                    
                    if results['success']:
                        print(f"✅ Profile {profile_name} processed successfully")
                        print(f"   Posts: {results['posts_found']}")
                        print(f"   Successful: {results['interaction_results'].get('successful_interactions', 0)}")
                        
                        overall_results['total_posts'] += results['posts_found']
                        overall_results['total_successful_interactions'] += results['interaction_results'].get('successful_interactions', 0)
                        overall_results['total_failed_interactions'] += results['interaction_results'].get('failed_interactions', 0)
                    else:
                        print(f"❌ Profile {profile_name} failed: {results.get('error')}")
                    
                    overall_results['profile_results'].append({
                        'profile_name': profile_name,
                        'profile_url': profile_url,
                        'results': results
                    })
                    overall_results['profiles_processed'] += 1
                    
                    # Account rotation between profiles
                    if self.use_account_rotation and self.profile_manager:
                        try:
                            print(f"\n🔄 Rotating to next profile for next user...")
                            self.driver = self.profile_manager.switch_to_next_profile()
                            print(f"✅ Profile rotation successful")
                        except Exception as e:
                            print(f"⚠️ Profile rotation failed: {str(e)}")
                    
                    # Delay between profiles
                    delay = random.uniform(5, 10)
                    print(f"⏱️ Waiting {delay:.1f}s before next profile...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"❌ Error processing profile {profile_name}: {e}")
                    continue
            
            # Final summary
            print(f"\n🎉 ALL PROFILES PROCESSING COMPLETE!")
            print("="*50)
            print(f"Profiles Processed: {overall_results['profiles_processed']}")
            print(f"Total Posts: {overall_results['total_posts']}")
            print(f"Total Successful Interactions: {overall_results['total_successful_interactions']}")
            print(f"Total Failed Interactions: {overall_results['total_failed_interactions']}")
            
            if overall_results['total_posts'] > 0:
                success_rate = (overall_results['total_successful_interactions'] / overall_results['total_posts']) * 100
                print(f"Overall Success Rate: {success_rate:.1f}%")
            
            overall_results['success'] = True
            overall_results['timestamp'] = datetime.now().isoformat()
            
            return overall_results
            
        except Exception as e:
            print(f"❌ Error processing all profiles: {e}")
            return {
                'success': False,
                'error': str(e),
                'profiles_processed': 0
            }

    def _get_profile_name_from_url(self, url: str) -> str:
        """Extract profile name from CMC profile URL"""
        try:
            return url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        except:
            return "unknown"

    def list_stored_profiles(self):
        """Display all stored profiles"""
        print(f"\n📋 STORED CMC PROFILES ({len(self.stored_profiles)})")
        print("="*50)
        
        if not self.stored_profiles:
            print("❌ No stored profiles found")
            print("💡 Use 'detect_and_store_current_profile()' or 'add_manual_profile()' to add profiles")
            return
        
        for i, (name, data) in enumerate(self.stored_profiles.items(), 1):
            print(f"{i:2d}. {name}")
            print(f"     🔗 URL: {data['url']}")
            print(f"     📅 Added: {data['detected_at'][:10]}")
            print(f"     🎯 Total Interactions: {data.get('total_interactions', 0)}")
            last_interaction = data.get('last_interaction')
            if last_interaction:
                print(f"     ⏰ Last Interaction: {last_interaction[:10]}")
            print()

    def close(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")


def main():
    """Example usage of the CMC Profile Interaction Bot"""
    try:
        print("🤖 CMC Profile Interaction Bot")
        print("="*40)
        
        # Initialize the bot
        bot = CMCProfileInteractionBot(use_account_rotation=True)
        
        # Example workflow
        print("\n📋 EXAMPLE WORKFLOW:")
        print("1. Detect current profile")
        print("2. Add manual profiles")
        print("3. Process all profiles")
        
        choice = input("\nRun example workflow? (y/n): ").strip().lower()
        
        if choice == 'y':
            # Step 1: Try to detect current profile
            print("\n" + "="*50)
            print("STEP 1: Detecting current profile")
            current_profile = bot.detect_and_store_current_profile()
            
            # Step 2: Add example manual profile
            print("\n" + "="*50)
            print("STEP 2: Adding example manual profile")
            bot.add_manual_profile(
                "https://coinmarketcap.com/community/profile/Onchainbureaudotcom/",
                "OnchainBureau"
            )
            
            # Step 3: Show stored profiles
            bot.list_stored_profiles()
            
            # Step 4: Process all profiles
            process_all = input("\nProcess all stored profiles? (y/n): ").strip().lower()
            if process_all == 'y':
                print("\n" + "="*50)
                print("STEP 4: Processing all profiles")
                results = bot.process_all_stored_profiles(max_posts_per_profile=10)
                
                if results['success']:
                    print(f"\n🎉 All profiles processed successfully!")
                else:
                    print(f"\n❌ Processing failed: {results.get('error')}")
        
        # Show final stored profiles
        bot.list_stored_profiles()
        
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        try:
            bot.close()
        except:
            pass


if __name__ == "__main__":
    main() 