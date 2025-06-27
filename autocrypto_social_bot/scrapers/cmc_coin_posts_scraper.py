#!/usr/bin/env python3
"""
CMC Coin Posts Scraper

This scraper focuses on:
1. Searching for specific coins and their posts on CoinMarketCap
2. Getting all latest posts for a specific coin
3. Interacting with posts (emoji reactions, comments)
4. Using account rotation for scalability
"""

import time
import logging
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autocrypto_social_bot.utils.helpers import random_delay
from typing import List, Dict, Optional
from datetime import datetime

class CMCCoinPostsScraper:
    def __init__(self, driver, profile_manager=None, proxy_config=None):
        self.driver = driver
        self.profile_manager = profile_manager
        self.proxy_config = proxy_config or {'auto_proxy_rotation': True, 'proxy_mode': 'enterprise'}
        
        self.logger = logging.getLogger(__name__)
        
        # CMC URLs
        self.base_url = "https://coinmarketcap.com"
        self.community_url = "https://coinmarketcap.com/community/"
        self.search_url = "https://coinmarketcap.com/community/search/latest/"
        
        print(f"🔍 CMC Coin Posts Scraper initialized")
        print(f"   Auto Proxy Rotation: {'✅ ENABLED' if self.proxy_config.get('auto_proxy_rotation', True) else '❌ DISABLED'}")
        print(f"   Mode: {self.proxy_config.get('proxy_mode', 'enterprise').upper()}")

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
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test*='post'], .post-card, [class*='post']"))
                )
            except TimeoutException:
                print("⚠️ No posts found or page didn't load properly")
                return []
            
            # Find all post elements
            posts_data = []
            post_selectors = [
                "[data-test*='post']",
                ".post-card", 
                "[class*='post-card']",
                "[data-role='post-card']",
                ".community-post",
                "[class*='community-post']"
            ]
            
            post_elements = []
            for selector in post_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        post_elements = elements
                        print(f"✅ Found {len(elements)} posts using selector: {selector}")
                        break
                except Exception as e:
                    continue
            
            if not post_elements:
                print("❌ No post elements found with any selector")
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

    def _extract_post_data(self, post_element, post_index: int) -> Optional[Dict]:
        """Extract data from a single post element"""
        try:
            post_data = {
                'index': post_index,
                'timestamp': datetime.now().isoformat(),
                'content': '',
                'author': '',
                'likes': 0,
                'comments': 0,
                'post_id': '',
                'emoji_button': None,
                'has_interactions': False
            }
            
            # Extract post content
            content_selectors = [
                "[data-test='post-content']",
                ".post-content",
                "[class*='post-content']",
                ".content",
                "[data-role='post-content']",
                "p, div[class*='text']"
            ]
            
            for selector in content_selectors:
                try:
                    content_elem = post_element.find_element(By.CSS_SELECTOR, selector)
                    if content_elem and content_elem.text.strip():
                        post_data['content'] = content_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract author
            author_selectors = [
                "[data-test='author-name']",
                ".author-name",
                "[class*='author']",
                "[data-role='author-name']",
                ".username",
                "[class*='username']"
            ]
            
            for selector in author_selectors:
                try:
                    author_elem = post_element.find_element(By.CSS_SELECTOR, selector)
                    if author_elem and author_elem.text.strip():
                        post_data['author'] = author_elem.text.strip()
                        break
                except:
                    continue
            
            # Extract metrics (likes, comments)
            try:
                like_selectors = [
                    "[data-test='like-count']",
                    ".like-count",
                    "[class*='like']",
                    ".count"
                ]
                
                for selector in like_selectors:
                    try:
                        like_elem = post_element.find_element(By.CSS_SELECTOR, selector)
                        if like_elem:
                            like_text = like_elem.text.strip()
                            if like_text.isdigit():
                                post_data['likes'] = int(like_text)
                                break
                    except:
                        continue
            except:
                pass
            
            # Find emoji button (the main target for interaction)
            emoji_button = self._find_emoji_button(post_element)
            if emoji_button:
                post_data['emoji_button'] = emoji_button
                post_data['has_interactions'] = True
            
            # Generate a unique post ID
            post_data['post_id'] = f"post_{post_index}_{int(time.time())}"
            
            return post_data if post_data['content'] else None
            
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

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
                # SVG-based selectors (for the smile icon)
                'svg[class*="eyXrOz"] use[href="#SMILE"]',
                'svg use[href="#SMILE"]',
                # Generic interaction buttons
                '.base-icon-wrapper',
                '[class*="base-icon-wrapper"]'
            ]
            
            for selector in emoji_selectors:
                try:
                    emoji_elements = post_element.find_elements(By.CSS_SELECTOR, selector)
                    for emoji_elem in emoji_elements:
                        if emoji_elem.is_displayed():
                            # Check if it's really an emoji button
                            if self._is_emoji_button(emoji_elem):
                                return {
                                    'element': emoji_elem,
                                    'selector': selector,
                                    'location': emoji_elem.location,
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
            
            # Look for emoji-related indicators
            emoji_indicators = [
                'emoji-action',
                'smile',
                'post-emoji',
                'reaction'
            ]
            
            element_text = (class_name + ' ' + data_test).lower()
            
            for indicator in emoji_indicators:
                if indicator in element_text:
                    return True
                    
            # Check for SVG with smile icon
            try:
                svg_elements = element.find_elements(By.TAG_NAME, 'svg')
                for svg in svg_elements:
                    use_elements = svg.find_elements(By.TAG_NAME, 'use')
                    for use_elem in use_elements:
                        href = use_elem.get_attribute('href') or ''
                        if 'SMILE' in href.upper():
                            return True
            except:
                pass
                
            return False
            
        except Exception as e:
            return False

    def interact_with_posts(self, posts_data: List[Dict], interaction_type: str = "emoji") -> Dict:
        """
        Interact with posts (click emoji buttons, etc.)
        
        Args:
            posts_data: List of post data from search_coin_posts
            interaction_type: Type of interaction ("emoji", "like", etc.)
            
        Returns:
            Summary of interactions performed
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
            print(f"Success Rate: {(interaction_results['successful_interactions'] / max(1, interaction_results['total_posts'])) * 100:.1f}%")
            
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
            
            # Try to click using different methods
            try:
                # Method 1: Direct click
                emoji_element.click()
                print(f"     ✅ Direct click successful")
                return True
            except ElementClickInterceptedException:
                try:
                    # Method 2: JavaScript click
                    self.driver.execute_script("arguments[0].click();", emoji_element)
                    print(f"     ✅ JavaScript click successful")
                    return True
                except Exception:
                    try:
                        # Method 3: ActionChains click
                        actions = ActionChains(self.driver)
                        actions.move_to_element(emoji_element).click().perform()
                        print(f"     ✅ ActionChains click successful")
                        return True
                    except Exception as e:
                        print(f"     ❌ All click methods failed: {str(e)}")
                        return False
            
        except Exception as e:
            print(f"     ❌ Error clicking emoji button: {str(e)}")
            return False

    def run_coin_interaction_bot(self, coin_query: str, max_posts: int = 10, interaction_type: str = "emoji") -> Dict:
        """
        Main method to run the coin interaction bot
        
        Args:
            coin_query: Coin to search for (e.g., "goonc")
            max_posts: Maximum number of posts to process
            interaction_type: Type of interaction to perform
            
        Returns:
            Complete results of the bot run
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
            
            # Step 3: Account rotation if needed
            if self.profile_manager and self.proxy_config.get('auto_proxy_rotation', True):
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
                'timestamp': datetime.now().isoformat(),
                'posts_data': posts_data  # Include full post data for analysis
            }
            
            print(f"\n🎉 BOT RUN COMPLETE!")
            print(f"   Found: {len(posts_data)} posts")
            print(f"   Successful interactions: {interaction_results.get('successful_interactions', 0)}")
            print(f"   Success rate: {(interaction_results.get('successful_interactions', 0) / max(1, len(posts_data))) * 100:.1f}%")
            
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
        Get the latest posts for a specific coin from CMC community search
        
        This is a focused method for just retrieving posts without interaction
        """
        try:
            print(f"\n📊 GETTING LATEST POSTS FOR: ${coin_symbol.upper()}")
            
            posts_data = self.search_coin_posts(coin_symbol, limit)
            
            # Sort by relevance/recency (assuming newer posts appear first)
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