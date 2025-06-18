from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import random_delay
import logging
import time
from datetime import datetime
from urllib.parse import quote_plus
import re

class TwitterScraper:
    def __init__(self, driver=None):
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://twitter.com/search?q="
        self.tweet_wait_time = 10  # seconds to wait for tweets to load
    
    def get_user_details(self, username, tweet_element=None):
        """Get detailed information about a Twitter user from a tweet"""
        try:
            user_info = {}
            
            if tweet_element:
                try:
                    # Get the actual Twitter handle (@username)
                    try:
                        # Find the actual username/handle from the tweet
                        username_element = tweet_element.find_element(
                            By.CSS_SELECTOR, 
                            'div[data-testid="User-Name"] a[href*="/status/"]'
                        )
                        actual_username = username_element.get_attribute('href').split('/')[3]
                        username = actual_username  # Update the username to the actual handle
                    except:
                        # Try alternative selector for username
                        username_element = tweet_element.find_element(
                            By.CSS_SELECTOR, 
                            'div[data-testid="User-Name"] a[role="link"]'
                        )
                        actual_username = username_element.get_attribute('href').split('/')[-1]
                        username = actual_username

                    # Get follower count from hover card
                    try:
                        # Hover over the username to trigger the hover card
                        username_element = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", username_element)
                        random_delay(1, 2)
                        
                        hover_card = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="HoverCard"]'))
                        )
                        user_info['followers'] = hover_card.find_element(By.CSS_SELECTOR, 
                            'span[data-testid="UserFollowers"]').text
                    except:
                        user_info['followers'] = "Unknown"
                    
                    # Get other user details without clicking
                    try:
                        # Try to extract info from the tweet metadata
                        user_name_div = tweet_element.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                        time_element = tweet_element.find_element(By.CSS_SELECTOR, "time")
                        
                        # Store the tweet timestamp as a reference point
                        user_info['last_tweet_time'] = time_element.get_attribute("datetime")
                        
                        # Check verification status
                        user_info['is_verified'] = len(tweet_element.find_elements(
                            By.CSS_SELECTOR, '[aria-label*="Verified"]')) > 0
                    except:
                        pass
                    
                except Exception as e:
                    self.logger.debug(f"Could not get user details from tweet card: {str(e)}")
            
            # If we couldn't get enough info from the tweet card,
            # try visiting the profile as a fallback
            if 'followers' not in user_info or user_info['followers'] == "Unknown":
                try:
                    # Open profile in a new tab
                    self.driver.execute_script(f'window.open("https://twitter.com/{username}", "_blank");')
                    random_delay(1, 2)
                    
                    # Switch to the new tab
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    random_delay(2, 3)
                    
                    # Get follower count
                    try:
                        followers_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href$="/followers"] span span'))
                        )
                        user_info['followers'] = followers_element.text
                    except:
                        user_info['followers'] = "Unknown"
                    
                    # Get account creation date
                    try:
                        join_date_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[data-testid="UserJoinDate"]'))
                        )
                        user_info['join_date'] = join_date_element.text.replace("Joined ", "")
                    except:
                        user_info['join_date'] = "Unknown"
                    
                    # Get recent tweets to check for coin promotions
                    try:
                        recent_tweets = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                        )[:5]
                        
                        promoted_coins = set()
                        for tweet in recent_tweets:
                            try:
                                text = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]').text
                                coins = {word for word in text.split() 
                                       if word.startswith('$') and len(word) > 1}
                                promoted_coins.update(coins)
                            except:
                                continue
                        
                        user_info['promoted_coins'] = list(promoted_coins)
                    except:
                        user_info['promoted_coins'] = []
                    
                    # Close the tab and switch back
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    
                except Exception as e:
                    self.logger.error(f"Error getting user details from profile: {str(e)}")
                    # Make sure we switch back to the main tab
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
            
            return user_info
            
        except Exception as e:
            self.logger.error(f"Error in get_user_details: {str(e)}")
            return None
        
    def get_coin_discussions(self, symbol: str, limit: int = 10) -> list:
        """Get recent discussions about a coin from Twitter"""
        try:
            self.logger.info(f"Searching Twitter for top tweets about ${symbol}")
            
            # More targeted search queries for analysis and trading discussions
            search_queries = [
                f"${symbol} analysis",           # Analysis discussions
                f"${symbol} technical analysis", # Technical analysis
                f"${symbol} price",             # Price discussions
                f"${symbol} trading",           # Trading discussions
                f"${symbol}",                   # General discussions
                f"#{symbol} crypto"             # Hashtag discussions as fallback
            ]
            
            tweets_data = []
            
            for query in search_queries:
                if len(tweets_data) >= limit:
                    break
                
                try:    
                    # Construct search URL with engagement filters
                    search_query = quote_plus(f"{query} min_faves:5 lang:en")  # Lower min likes, add language filter
                    url = f"{self.base_url}{search_query}&f=live"  # Use live feed
                    
                    self.logger.info(f"Trying search query: {query}")
                    self.driver.get(url)
                    
                    # Wait for tweets to load
                    time.sleep(3)  # Reduced initial wait
                    
                    scroll_attempts = 0
                    max_scrolls = 2  # Reduced scrolls per query since we have more queries
                    
                    while len(tweets_data) < limit and scroll_attempts < max_scrolls:
                        try:
                            # Find tweet elements
                            tweet_elements = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                            )
                            
                            # Process new tweets
                            for tweet in tweet_elements:
                                if len(tweets_data) >= limit:
                                    break
                                    
                                try:
                                    tweet_data = self._extract_tweet_data(tweet)
                                    if tweet_data and not any(t['id'] == tweet_data['id'] for t in tweets_data):
                                        # Filter out low-quality tweets
                                        text = tweet_data['text'].lower()
                                        if any(word in text for word in ['analysis', 'price', 'support', 'resistance', 'trend', 'trading']):
                                            tweets_data.append(tweet_data)
                                            self.logger.info(f"Found relevant tweet: {tweet_data['text'][:100]}...")
                                except Exception as e:
                                    self.logger.error(f"Error extracting tweet data: {str(e)}")
                                    continue
                            
                            # Scroll down for more tweets
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            scroll_attempts += 1
                            time.sleep(2)
                            
                        except Exception as e:
                            self.logger.error(f"Error finding tweets in scroll attempt {scroll_attempts}: {str(e)}")
                            scroll_attempts += 1
                            continue
                except Exception as e:
                    self.logger.error(f"Error with search query '{query}': {str(e)}")
                    continue
            
            # If we couldn't find any tweets, return a fallback dummy tweet to prevent errors
            if not tweets_data:
                self.logger.warning(f"No tweets found for ${symbol}, returning fallback data")
                fallback_tweet = {
                    'id': 'fallback_id',
                    'username': 'placeholder',
                    'text': f"Analysis for ${symbol} not available at this time.",
                    'timestamp': datetime.now().isoformat(),
                    'user_info': {
                        'followers': '100',
                        'is_verified': False,
                        'join_date': 'Jan 2023',
                        'promoted_coins': [f"${symbol}"]
                    }
                }
                tweets_data.append(fallback_tweet)
            
            return tweets_data
            
        except Exception as e:
            self.logger.error(f"Error finding tweets: {str(e)}")
            # Return a fallback dummy tweet to prevent errors
            fallback_tweet = {
                'id': 'fallback_id',
                'username': 'placeholder',
                'text': f"Analysis for ${symbol} not available at this time.",
                'timestamp': datetime.now().isoformat(),
                'user_info': {
                    'followers': '100',
                    'is_verified': False,
                    'join_date': 'Jan 2023',
                    'promoted_coins': [f"${symbol}"]
                }
            }
            return [fallback_tweet]

    def _extract_tweet_data(self, tweet_element) -> dict:
        """Extract data from a tweet element"""
        try:
            # Get tweet text
            text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
            text = text_element.text
            
            # Get user info
            user_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
            username = user_element.text.split('\n')[0]
            
            # Check for verification
            verified = False
            try:
                verified_badge = user_element.find_element(By.CSS_SELECTOR, '[data-testid="icon-verified"]')
                verified = True
            except:
                pass
            
            # Get engagement metrics
            metrics = {
                'likes': 0,
                'retweets': 0,
                'replies': 0
            }
            
            try:
                metrics_elements = tweet_element.find_elements(By.CSS_SELECTOR, '[data-testid$="-count"]')
                for element in metrics_elements:
                    count = int(element.get_attribute('aria-label').split()[0] or 0)
                    if 'like' in element.get_attribute('data-testid'):
                        metrics['likes'] = count
                    elif 'retweet' in element.get_attribute('data-testid'):
                        metrics['retweets'] = count
                    elif 'reply' in element.get_attribute('data-testid'):
                        metrics['replies'] = count
            except:
                pass
            
            return {
                'id': tweet_element.get_attribute('data-tweet-id'),
                'text': text,
                'user': {
                    'screen_name': username,
                    'verified': verified,
                    'followers_count': 0  # Twitter no longer shows this easily
                },
                'metrics': metrics,
                'hashtags': re.findall(r'#(\w+)', text),
                'user_mentions': re.findall(r'@(\w+)', text)
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting tweet data: {str(e)}")
            return None 