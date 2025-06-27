#!/usr/bin/env python3
"""
CMC Coin Posts Bot

This bot searches for specific coins on CoinMarketCap community and interacts with posts.
Features:
1. Search for posts about specific coins (e.g., "goonc")
2. Get all latest posts for a coin
3. Click emoji buttons on posts
4. Use account rotation system
"""

import sys
import os
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from typing import List, Dict, Optional
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autocrypto_social_bot.profiles.profile_manager import ProfileManager
from autocrypto_social_bot.utils.helpers import random_delay

class CMCCoinPostsBot:
    def __init__(self, use_account_rotation=True):
        self.logger = logging.getLogger(__name__)
        
        # Initialize profile manager with account rotation
        self.profile_manager = ProfileManager()
        self.use_account_rotation = use_account_rotation
        
        # CMC URLs
        self.base_url = "https://coinmarketcap.com"
        self.community_url = "https://coinmarketcap.com/community/"
        self.search_url = "https://coinmarketcap.com/community/search/latest/"
        
        # Initialize driver
        self.driver = None
        self._load_profile()
        
        print(f"🤖 CMC Coin Posts Bot initialized")
        print(f"   Account Rotation: {'✅ ENABLED' if use_account_rotation else '❌ DISABLED'}")

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

    def search_coin_posts(self, coin_query: str, max_posts: int = 20) -> List[Dict]:
        """
        Search for posts about a specific coin on CMC community
        
        Args:
            coin_query: The coin symbol or name to search for (e.g., "goonc", "BTC")
            max_posts: Maximum number of posts to retrieve
            
        Returns:
            List of post dictionaries with details
        """
        try:
            print(f"\n🔍 SEARCHING FOR POSTS ABOUT: {coin_query.upper()}")
            print("="*60)
            
            # Navigate to search page
            search_url = f"{self.search_url}?q={coin_query}"
            print(f"1. Navigating to search: {search_url}")
            self.driver.get(search_url)
            random_delay(3, 5)
            
            # Wait for search results to load
            print("2. Waiting for search results...")
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div, article, section"))
                )
                time.sleep(3)  # Additional wait for dynamic content
            except TimeoutException:
                print("⚠️ Page didn't load properly, trying to continue...")
            
            # Find post elements using multiple strategies
            posts_data = []
            post_elements = self._find_post_elements()
            
            if not post_elements:
                print("❌ No post elements found")
                return []
            
            # Limit posts to max_posts
            posts_to_process = post_elements[:max_posts]
            print(f"3. Processing {len(posts_to_process)} posts...")
            
            for i, post_element in enumerate(posts_to_process, 1):
                try:
                    print(f"\n   📝 Processing post {i}/{len(posts_to_process)}")
                    post_data = self._extract_post_data(post_element, i)
                    if post_data:
                        posts_data.append(post_data)
                        print(f"   ✅ Extracted post data successfully")
                    else:
                        print(f"   ⚠️ Could not extract post data")
                        
                except Exception as e:
                    print(f"   ❌ Error processing post {i}: {str(e)}")
                    continue
            
            print(f"\n✅ SEARCH COMPLETE: Found {len(posts_data)} posts about {coin_query.upper()}")
            print("="*60)
            
            return posts_data
            
        except Exception as e:
            self.logger.error(f"Error searching for coin posts: {str(e)}")
            return []

    def _find_post_elements(self) -> List:
        """Find post elements using multiple strategies"""
        post_selectors = [
            # Common post selectors
            "[data-test*='post']",
            "[class*='post-card']",
            "[data-role='post-card']",
            ".community-post",
            "[class*='community-post']",
            # Generic content selectors
            "article",
            "[role='article']",
            "div[class*='content']",
            # Fallback selectors
            "div[class*='card']",
            "div[class*='item']"
        ]
        
        post_elements = []
        for selector in post_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Filter out obviously non-post elements
                    filtered_elements = []
                    for elem in elements:
                        try:
                            if elem.is_displayed() and elem.text.strip():
                                filtered_elements.append(elem)
                        except:
                            continue
                    
                    if filtered_elements:
                        post_elements = filtered_elements
                        print(f"✅ Found {len(filtered_elements)} posts using selector: {selector}")
                        break
            except Exception as e:
                continue
        
        return post_elements

    def _extract_post_data(self, post_element, post_index: int) -> Optional[Dict]:
        """Extract data from a single post element"""
        try:
            post_data = {
                'index': post_index,
                'timestamp': datetime.now().isoformat(),
                'content': '',
                'author': '',
                'likes': 0,
                'post_id': f"post_{post_index}_{int(time.time())}",
                'emoji_button': None,
                'has_interactions': False,
                'element': post_element  # Keep reference to the element
            }
            
            # Extract post content
            post_data['content'] = self._extract_text_content(post_element)
            
            # Extract author
            post_data['author'] = self._extract_author(post_element)
            
            # Find emoji button (the main target for interaction)
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
            # Try different text extraction methods
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
        """Find the emoji/smile button in a post element"""
        try:
            # Based on the user's provided HTML structure
            emoji_selectors = [
                # Exact selector from user's HTML
                'div[data-test="post-emoji-action"]',
                # Generic emoji selectors
                '.post-emoji-action',
                '[class*="emoji-action"]',
                '[data-test*="emoji"]',
                # SVG-based selectors (for the smile icon)
                'svg use[href="#SMILE"]',
                'svg[class*="eyXrOz"]',
                # Generic interaction buttons
                '.base-icon-wrapper',
                '[class*="base-icon-wrapper"]',
                # Broader selectors
                'button[class*="emoji"]',
                'div[class*="reaction"]',
                '[class*="smile"]'
            ]
            
            for selector in emoji_selectors:
                try:
                    emoji_elements = post_element.find_elements(By.CSS_SELECTOR, selector)
                    for emoji_elem in emoji_elements:
                        if emoji_elem.is_displayed() and self._is_emoji_button(emoji_elem):
                            return {
                                'element': emoji_elem,
                                'selector': selector,
                                'clickable': emoji_elem.is_enabled()
                            }
                except Exception as e:
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error finding emoji button: {str(e)}")
            return None

    def _is_emoji_button(self, element) -> bool:
        """Check if an element is actually an emoji button"""
        try:
            # Check for specific attributes or text content
            class_name = element.get_attribute('class') or ''
            data_test = element.get_attribute('data-test') or ''
            onclick = element.get_attribute('onclick') or ''
            
            # Look for emoji-related indicators
            emoji_indicators = [
                'emoji-action',
                'smile',
                'post-emoji',
                'reaction',
                'base-icon-wrapper'
            ]
            
            element_text = (class_name + ' ' + data_test + ' ' + onclick).lower()
            
            for indicator in emoji_indicators:
                if indicator in element_text:
                    return True
                    
            # Check for SVG with smile icon
            try:
                svg_elements = element.find_elements(By.TAG_NAME, 'svg')
                for svg in svg_elements:
                    svg_html = svg.get_attribute('outerHTML') or ''
                    if 'SMILE' in svg_html.upper() or 'emoji' in svg_html.lower():
                        return True
            except:
                pass
                
            return False
            
        except Exception as e:
            return False

    def interact_with_posts(self, posts_data: List[Dict], interaction_type: str = "emoji") -> Dict:
        """
        Interact with posts (click emoji buttons, etc.)
        """
        try:
            print(f"\n🎯 INTERACTING WITH {len(posts_data)} POSTS")
            print("="*50)
            
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
                        print(f"   ⚠️ No interaction buttons found")
                        interaction_results['posts_without_buttons'] += 1
                        continue
                    
                    # Perform the interaction
                    success = self._perform_interaction(post_data, interaction_type)
                    
                    interaction_record = {
                        'post_index': i,
                        'post_id': post_data['post_id'],
                        'author': post_data['author'],
                        'interaction_type': interaction_type,
                        'success': success,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    interaction_results['interactions'].append(interaction_record)
                    
                    if success:
                        print(f"   ✅ Successfully performed {interaction_type} interaction")
                        interaction_results['successful_interactions'] += 1
                    else:
                        print(f"   ❌ Failed to perform {interaction_type} interaction")
                        interaction_results['failed_interactions'] += 1
                    
                    # Add delay between interactions to avoid rate limiting
                    delay = random.uniform(2, 5)
                    print(f"   ⏱️ Waiting {delay:.1f}s before next interaction...")
                    time.sleep(delay)
                    
                except Exception as e:
                    print(f"   ❌ Error interacting with post {i}: {str(e)}")
                    interaction_results['failed_interactions'] += 1
                    continue
            
            # Print summary
            print(f"\n📊 INTERACTION SUMMARY")
            print("="*30)
            print(f"Total Posts: {interaction_results['total_posts']}")
            print(f"Successful: {interaction_results['successful_interactions']}")
            print(f"Failed: {interaction_results['failed_interactions']}")
            print(f"No Buttons: {interaction_results['posts_without_buttons']}")
            success_rate = (interaction_results['successful_interactions'] / max(1, interaction_results['total_posts'])) * 100
            print(f"Success Rate: {success_rate:.1f}%")
            
            return interaction_results
            
        except Exception as e:
            self.logger.error(f"Error interacting with posts: {str(e)}")
            return {'error': str(e)}

    def _perform_interaction(self, post_data: Dict, interaction_type: str) -> bool:
        """Perform a specific interaction with a post"""
        try:
            if interaction_type == "emoji" and post_data.get('emoji_button'):
                return self._click_emoji_button(post_data['emoji_button'])
            else:
                print(f"   ⚠️ Interaction type '{interaction_type}' not supported yet")
                return False
                
        except Exception as e:
            print(f"   ❌ Error performing interaction: {str(e)}")
            return False

    def _click_emoji_button(self, emoji_button_data: Dict) -> bool:
        """Click the emoji button on a post"""
        try:
            emoji_element = emoji_button_data['element']
            
            # Scroll to the element
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", emoji_element)
            time.sleep(1)
            
            # Try different click methods
            click_methods = [
                lambda: emoji_element.click(),
                lambda: self.driver.execute_script("arguments[0].click();", emoji_element),
                lambda: ActionChains(self.driver).move_to_element(emoji_element).click().perform()
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
            print(f"     ❌ Error clicking emoji button: {str(e)}")
            return False

    def run_coin_interaction_bot(self, coin_query: str, max_posts: int = 10, interaction_type: str = "emoji") -> Dict:
        """
        Main method to run the coin interaction bot
        """
        try:
            print(f"\n🤖 STARTING COIN INTERACTION BOT")
            print("="*50)
            print(f"Target Coin: {coin_query.upper()}")
            print(f"Max Posts: {max_posts}")
            print(f"Interaction: {interaction_type}")
            print("="*50)
            
            # Step 1: Search for posts
            posts_data = self.search_coin_posts(coin_query, max_posts)
            
            if not posts_data:
                return {
                    'success': False,
                    'error': 'No posts found for the specified coin',
                    'coin_query': coin_query
                }
            
            # Step 2: Interact with posts
            interaction_results = self.interact_with_posts(posts_data, interaction_type)
            
            # Step 3: Account rotation if enabled
            if self.use_account_rotation and self.profile_manager:
                try:
                    print(f"\n🔄 Rotating to next profile for future operations...")
                    self.driver = self.profile_manager.switch_to_next_profile()
                    print(f"✅ Profile rotation successful")
                except Exception as e:
                    print(f"⚠️ Profile rotation failed: {str(e)}")
            
            # Complete results
            results = {
                'success': True,
                'coin_query': coin_query,
                'posts_found': len(posts_data),
                'interaction_type': interaction_type,
                'interaction_results': interaction_results,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"\n🎉 BOT RUN COMPLETE!")
            print(f"   Found: {len(posts_data)} posts")
            print(f"   Successful interactions: {interaction_results.get('successful_interactions', 0)}")
            success_rate = (interaction_results.get('successful_interactions', 0) / max(1, len(posts_data))) * 100
            print(f"   Success rate: {success_rate:.1f}%")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error running coin interaction bot: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'coin_query': coin_query
            }

    def get_latest_posts_for_coin(self, coin_symbol: str, limit: int = 50) -> List[Dict]:
        """
        Get the latest posts for a specific coin (without interaction)
        """
        try:
            print(f"\n📊 GETTING LATEST POSTS FOR: ${coin_symbol.upper()}")
            
            posts_data = self.search_coin_posts(coin_symbol, limit)
            
            if posts_data:
                print(f"✅ Retrieved {len(posts_data)} latest posts for ${coin_symbol.upper()}")
                
                # Print a summary
                print(f"\n📋 LATEST POSTS SUMMARY:")
                for i, post in enumerate(posts_data[:5], 1):  # Show first 5
                    print(f"   {i}. {post['author']}: {post['content'][:80]}...")
                    
                if len(posts_data) > 5:
                    print(f"   ... and {len(posts_data) - 5} more posts")
            
            return posts_data
            
        except Exception as e:
            self.logger.error(f"Error getting latest posts: {str(e)}")
            return []

    def close(self):
        """Clean up resources"""
        try:
            if self.driver:
                self.driver.quit()
                print("✅ Browser closed successfully")
        except Exception as e:
            print(f"⚠️ Error closing browser: {e}")


def main():
    """Example usage of the CMC Coin Posts Bot"""
    try:
        # Initialize the bot
        bot = CMCCoinPostsBot(use_account_rotation=True)
        
        # Example 1: Search and interact with GOONC posts
        print("\n" + "="*80)
        print("EXAMPLE 1: Search and interact with GOONC posts")
        print("="*80)
        
        results = bot.run_coin_interaction_bot(
            coin_query="goonc",
            max_posts=5,
            interaction_type="emoji"
        )
        
        if results['success']:
            print(f"✅ Bot run successful for GOONC!")
        else:
            print(f"❌ Bot run failed: {results.get('error', 'Unknown error')}")
        
        # Example 2: Just get latest posts for BTC (no interaction)
        print("\n" + "="*80)
        print("EXAMPLE 2: Get latest BTC posts (no interaction)")
        print("="*80)
        
        btc_posts = bot.get_latest_posts_for_coin("BTC", limit=10)
        print(f"Found {len(btc_posts)} BTC posts")
        
    except Exception as e:
        print(f"❌ Error running bot: {e}")
    finally:
        # Clean up
        try:
            bot.close()
        except:
            pass


if __name__ == "__main__":
    main() 