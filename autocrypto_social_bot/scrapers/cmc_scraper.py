import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autocrypto_social_bot.utils.helpers import random_delay

class CMCScraper:
    def __init__(self, driver=None):
        self.base_url = "https://coinmarketcap.com"
        self.community_url = "https://coinmarketcap.com/community/"
        self.driver = driver
        self.logger = logging.getLogger(__name__)

    def post_community_comment(self, symbol: str, message: str) -> bool:
        """Post a comment in CMC community"""
        try:
            print("\n" + "="*50)
            print(f"🚀 POSTING TO CMC COMMUNITY: ${symbol}")
            print("="*50)
            
            # Navigate to community page
            print("1. Navigating to CMC community...")
            self.driver.get(self.community_url)
            random_delay(3, 4)
            
            # Find and click the editor div
            print("2. Looking for editor...")
            editor_div = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[contenteditable="true"]'))
            )
            print("✅ Found editor")
            editor_div.click()
            random_delay(2, 3)
            
            # Type the ticker symbol
            print(f"3. Typing ${symbol}...")
            editor_div.send_keys(f"${symbol}")
            random_delay(2, 3)
            
            # Press Enter to select the ticker
            print("4. Selecting ticker...")
            editor_div.send_keys(Keys.ENTER)
            random_delay(2, 3)
            
            # Replace emojis with text equivalents
            emoji_replacements = {
                "🔍": "[ANALYSIS]",
                "📊": "[STATS]",
                "🏥": "[HEALTH]",
                "⚠️": "[WARNING]",
                "🚩": "[RISK]",
                "💡": "[NOTE]",
                "•": "-"
            }
            
            # Clean up the message
            print("5. Adding analysis message...")
            for emoji, replacement in emoji_replacements.items():
                message = message.replace(emoji, replacement)
            
            # Split into lines and post
            lines = message.split('\n')
            for line in lines:
                if line.strip():
                    editor_div.send_keys(line.strip())
                    editor_div.send_keys(Keys.SHIFT + Keys.ENTER)
                    random_delay(0.3, 0.5)
            
            # Find and click post button - updated selectors
            print("6. Looking for post button...")
            try:
                # Try multiple selectors for the post button
                post_button = None
                button_selectors = [
                    'div.editor-post-button',
                    '#cmc-editor button',
                    'button.post-button',
                    'div[class*="post-button"]',
                    'div[class*="PostButton"]'
                ]
                
                for selector in button_selectors:
                    try:
                        post_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if post_button:
                            break
                    except:
                        continue
                
                if not post_button:
                    # Try JavaScript click on the button
                    self.driver.execute_script("""
                        var buttons = document.querySelectorAll('button');
                        for(var i=0; i<buttons.length; i++){
                            if(buttons[i].textContent.toLowerCase().includes('post')){
                                buttons[i].click();
                                break;
                            }
                        }
                    """)
                else:
                    print("✅ Found post button")
                    print("7. Clicking post button...")
                    try:
                        post_button.click()
                    except:
                        # Try JavaScript click if regular click fails
                        self.driver.execute_script("arguments[0].click();", post_button)
            
            except Exception as e:
                print(f"Error clicking post button: {str(e)}")
                return False
            
            # Wait for post to be published
            random_delay(5, 7)
            print(f"\n✅ Successfully posted analysis for ${symbol}")
            print("="*50 + "\n")
            
            return True

        except Exception as e:
            print(f"\n❌ Error posting to CMC community: {str(e)}")
            return False

    def get_trending_coins(self, limit=5) -> list:
        """Get trending coins from CMC community"""
        try:
            # First check community trending
            self.logger.info("Navigating to CMC community...")
            self.driver.get(self.community_url)
            random_delay(3, 5)  # Increased delay for page load

            # Try multiple possible selectors for trending section
            trending_selectors = [
                '[data-testid="trending-tokens"]',
                '.trending-tokens',
                '.trending-section',
                '//div[contains(text(), "Trending")]/../..',  # XPath for trending container
                '//div[contains(@class, "trending")]'
            ]

            trending_section = None
            for selector in trending_selectors:
                try:
                    if selector.startswith('//'):
                        # XPath selector
                        trending_section = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                    else:
                        # CSS selector
                        trending_section = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    if trending_section:
                        self.logger.info("Found trending section")
                        break
                except:
                    continue

            if not trending_section:
                # Fallback to getting trending from main page
                self.logger.info("Falling back to main page trending...")
                self.driver.get(f"{self.base_url}/trending-cryptocurrencies/")
                random_delay(3, 5)
                
                trending_table = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
                )
                
                trending_coins = []
                rows = trending_table.find_elements(By.CSS_SELECTOR, "tbody tr")
                
                for row in rows[:limit]:
                    try:
                        # Get the coin link to extract URL
                        coin_link = row.find_element(By.CSS_SELECTOR, "td:nth-child(3) a")
                        coin_url = coin_link.get_attribute('href')
                        
                        name_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(3)")
                        symbol = name_element.find_element(By.CSS_SELECTOR, "p").text
                        name = name_element.text.replace(symbol, '').strip()
                        price = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text
                        change = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)").text.strip('%')
                        
                        trending_coins.append({
                            'name': name,
                            'symbol': symbol,
                            'price': price,
                            'change_24h': change,
                            'url': coin_url
                        })
                        
                    except Exception as e:
                        self.logger.error(f"Error parsing coin row: {str(e)}")
                        continue
                        
                return trending_coins[:limit]

            # Get trending coins from community
            trending_coins = []
            coin_elements = trending_section.find_elements(
                By.CSS_SELECTOR, 
                'a[href*="/currencies/"], a[href*="/token/"]'
            )
            
            self.logger.info(f"Found {len(coin_elements)} coin elements")
            
            for coin in coin_elements[:limit]:
                try:
                    # Get the coin URL
                    coin_url = coin.get_attribute('href')
                    
                    # Try different ways to get coin info
                    try:
                        name = coin.get_attribute('title')
                        if not name:
                            name = coin.text.split('$')[0].strip()
                    except:
                        name = coin.text.split('$')[0].strip()
                    
                    try:
                        symbol = coin.text.split('$')[1].strip()
                    except:
                        symbol = coin.text.strip('$')
                    
                    # Navigate to the coin page to get price data
                    self.driver.execute_script(f"window.open('{coin_url}', '_blank');")
                    random_delay(1, 2)
                    
                    # Switch to new tab
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    random_delay(2, 3)
                    
                    # Get price data
                    try:
                        price = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((
                                By.CSS_SELECTOR, 
                                '[data-testid="price-value"], .priceValue'
                            ))
                        ).text
                    except:
                        price = "N/A"
                    
                    try:
                        change = self.driver.find_element(
                            By.CSS_SELECTOR, 
                            '[data-testid="24h-price-change"], .priceChange'
                        ).text.strip('%')
                    except:
                        change = "0"
                    
                    trending_coins.append({
                        'name': name,
                        'symbol': symbol,
                        'price': price,
                        'change_24h': change,
                        'url': coin_url
                    })
                    
                    # Close tab and switch back
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
                    random_delay(1, 2)
                    
                except Exception as e:
                    self.logger.error(f"Error getting coin data: {str(e)}")
                    # Make sure we're back on the main tab
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    continue

            self.logger.info(f"Successfully gathered {len(trending_coins)} trending coins")
            return trending_coins[:limit]

        except Exception as e:
            self.logger.error(f"Error getting trending coins: {str(e)}")
            return []

    def get_coin_discussions(self, coin_symbol):
        """Get discussions for a specific coin"""
        try:
            self.logger.info(f"Getting discussions for {coin_symbol}...")
            # First get the coin's page
            self.driver.get(f"{self.base_url}/currencies/{coin_symbol}/")
            random_delay(3, 7)

            # Wait for and click the Community tab
            try:
                # Try the new UI selector
                community_tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Community')]/parent::button"))
                )
            except:
                try:
                    # Try alternative selector
                    community_tab = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'community-tab')]"))
                    )
                except:
                    self.logger.error("Could not find Community tab")
                    return []

            community_tab.click()
            random_delay(2, 5)

            # Wait for posts to load
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-role='post-card']"))
                )
            except:
                self.logger.error("No posts found")
                return []

            discussions = []
            # Updated selector for posts
            posts = self.driver.find_elements(By.CSS_SELECTOR, "[data-role='post-card']")
            
            for post in posts[:5]:  # Get first 5 discussions
                try:
                    # Updated selectors for post elements
                    content = post.find_element(By.CSS_SELECTOR, "[data-role='post-content']").text
                    author = post.find_element(By.CSS_SELECTOR, "[data-role='author-name']").text
                    
                    # Like count might not always be present
                    try:
                        likes = post.find_element(By.CSS_SELECTOR, "[data-role='like-count']").text
                    except:
                        likes = "0"
                    
                    discussions.append({
                        'content': content,
                        'author': author,
                        'likes': likes
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error parsing discussion: {str(e)}")
                    continue

            self.logger.info(f"Found {len(discussions)} discussions for {coin_symbol}")
            return discussions

        except Exception as e:
            self.logger.error(f"Error getting discussions: {str(e)}")
            return []

    def find_ai_button(self, driver):
        """Smart AI button detection that looks for AI question prompts"""
        self.logger.info("🔍 Looking for AI question prompts...")
        
        # Strategy 1: Look for elements near the price section first
        try:
            # Find the price value element
            price_elements = driver.find_elements(By.CSS_SELECTOR, 
                '[data-testid="price-value"], .priceValue, [class*="price"]')
            
            for price_elem in price_elements:
                if not price_elem.is_displayed():
                    continue
                    
                # Look for questions in the same general area
                try:
                    # Get common ancestor and look for questions
                    ancestor = price_elem.find_element(By.XPATH, "./ancestor::div[4]")  # Go up 4 levels
                    questions = ancestor.find_elements(By.XPATH, ".//*[contains(text(), '?')]")
                    
                    for q in questions:
                        text = q.text.strip()
                        # Filter out unwanted questions and verify it's a proper AI question
                        if (q.is_displayed() and 
                            q.is_enabled() and 
                            len(text) > 10 and
                            text.count('?') == 1 and
                            not any(unwanted in text.lower() for unwanted in [
                                "do you own", "forgot", "need help", "what is", "have you seen"
                            ]) and
                            any(word in text.lower() for word in [
                                "why is", "what could", "how does", "will the"
                            ])):
                            self.logger.info(f"✅ Found AI question near price: '{text}'")
                            return q
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Price proximity search failed: {str(e)}")
        
        # Strategy 2: Look for elements with AI-specific classes
        css_selectors = [
            "[class*='ai-question']",
            "[class*='ai-prompt']",
            "[data-testid*='ai']",
            "[class*='ai-button']"
        ]
        
        for css in css_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, css)
                for elem in elements:
                    text = elem.text.strip()
                    if (elem.is_displayed() and 
                        elem.is_enabled() and 
                        "?" in text and
                        len(text) > 10 and
                        not "do you own" in text.lower()):
                        self.logger.info(f"✅ Found AI question by class: '{text}'")
                        return elem
            except:
                continue
        
        # Strategy 3: Look for questions near "CMC AI" text
        try:
            # Find CMC AI text elements
            ai_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'CMC AI')]")
            
            for ai_elem in ai_elements:
                if not ai_elem.is_displayed():
                    continue
                    
                # Look for questions in siblings and nearby elements
                try:
                    # Look in siblings first
                    parent = ai_elem.find_element(By.XPATH, "./..")
                    questions = parent.find_elements(By.XPATH, ".//*[contains(text(), '?')]")
                    
                    for q in questions:
                        text = q.text.strip()
                        if (q.is_displayed() and 
                            q.is_enabled() and 
                            len(text) > 10 and
                            text.count('?') == 1 and
                            not "do you own" in text.lower()):
                            self.logger.info(f"✅ Found question near CMC AI: '{text}'")
                            return q
                            
                    # If not found in siblings, look in nearby elements
                    ancestor = ai_elem.find_element(By.XPATH, "./ancestor::div[3]")
                    questions = ancestor.find_elements(By.XPATH, ".//*[contains(text(), '?')]")
                    
                    for q in questions:
                        text = q.text.strip()
                        if (q.is_displayed() and 
                            q.is_enabled() and 
                            len(text) > 10 and
                            text.count('?') == 1 and
                            not "do you own" in text.lower()):
                            self.logger.info(f"✅ Found question near CMC AI: '{text}'")
                            return q
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"CMC AI proximity search failed: {str(e)}")
        
        self.logger.warning("❌ No AI question prompts found")
        return None

    def find_and_click_ai_button(self, driver, max_attempts=3):
        """Enhanced method to find and click AI button with multiple strategies"""
        for attempt in range(max_attempts):
            try:
                # First try without scrolling
                ai_button = self.find_ai_button(driver)
                if ai_button:
                    try:
                        # 1. Scroll element into center view
                        driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            ai_button
                        )
                        time.sleep(1)
                        
                        # 2. Ensure element is clickable
                        driver.execute_script("""
                            arguments[0].style.position = 'relative';
                            arguments[0].style.opacity = '1';
                            arguments[0].style.zIndex = '999999';
                        """, ai_button)
                        
                        # 3. Try direct click
                        ai_button.click()
                        self.logger.info("✅ Clicked AI button successfully")
                        return True
                    except:
                        pass
                
                # If direct click failed, try different scroll positions
                scroll_positions = [0.2, 0.4, 0.6, 0.8]
                for scroll_pos in scroll_positions:
                    self.logger.info(f"Trying scroll position {int(scroll_pos * 100)}%...")
                    
                    # Scroll and wait
                    driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_pos});")
                    time.sleep(1)
                    
                    # Try to find and click button
                    ai_button = self.find_ai_button(driver)
                    if ai_button:
                        try:
                            # Try multiple click methods
                            try:
                                # Method 1: Direct click
                                ai_button.click()
                                self.logger.info("✅ Clicked using direct click")
                                return True
                            except:
                                try:
                                    # Method 2: JavaScript click
                                    driver.execute_script("arguments[0].click();", ai_button)
                                    self.logger.info("✅ Clicked using JavaScript")
                                    return True
                                except:
                                    try:
                                        # Method 3: Action chains
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        actions = ActionChains(driver)
                                        actions.move_to_element(ai_button).click().perform()
                                        self.logger.info("✅ Clicked using Action Chains")
                                        return True
                                    except:
                                        continue
                        except:
                            continue
                
                self.logger.warning(f"Attempt {attempt + 1} failed to click AI button")
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Error in click attempt {attempt + 1}: {str(e)}")
                time.sleep(2)
        
        return False

    def wait_for_ai_content(self, timeout=45):
        """Enhanced method to wait for and capture AI content"""
        start_time = time.time()
        previous_content = None
        content_stable_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Strategy 1: Look for content in right panel
                right_panel_selectors = [
                    "//div[contains(@class, 'right-panel')]",
                    "//div[contains(@class, 'ai-response')]",
                    "//div[contains(@class, 'ai-content')]",
                    "//aside",
                    "//div[@role='complementary']"
                ]
                
                for selector in right_panel_selectors:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            content = element.text.strip()
                            
                            # Check if content is substantial
                            if len(content) > 100 and ('.' in content or ',' in content):
                                # Check if content has stabilized (hasn't changed in 2 consecutive checks)
                                if content == previous_content:
                                    content_stable_count += 1
                                    if content_stable_count >= 2:
                                        self.logger.info(f"✅ Content stabilized after {int(time.time() - start_time)} seconds")
                                        return content
                                else:
                                    content_stable_count = 0
                                    previous_content = content
                
                # Strategy 2: Look for any substantial text that might be AI content
                potential_content = self.driver.find_elements(By.XPATH, 
                    "//*[string-length(text()) > 100 and (contains(text(), '.') or contains(text(), ','))]")
                
                for element in potential_content:
                    if element.is_displayed():
                        content = element.text.strip()
                        if len(content) > 100 and ('.' in content or ',' in content):
                            if content == previous_content:
                                content_stable_count += 1
                                if content_stable_count >= 2:
                                    self.logger.info(f"✅ Content stabilized after {int(time.time() - start_time)} seconds")
                                    return content
                            else:
                                content_stable_count = 0
                                previous_content = content
                
                # If we haven't found stable content yet, wait a bit
                if (time.time() - start_time) % 5 < 0.1:
                    self.logger.info(f"Still waiting for content... {int(time.time() - start_time)} seconds elapsed")
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Error while waiting for content: {str(e)}")
                time.sleep(0.5)
        
        return None

    def get_ai_token_review(self, coin_symbol: str, coin_name: str, coin_url: str = None) -> dict:
        """Get AI-generated review for a token from CMC"""
        try:
            self.logger.info(f"Getting AI review for {coin_name} (${coin_symbol})...")
            
            # Use provided URL or construct it
            if coin_url:
                target_url = coin_url
            else:
                coin_slug = coin_name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('.', '')
                target_url = f"{self.base_url}/currencies/{coin_slug}/"
            
            self.logger.info(f"Navigating to: {target_url}")
            self.driver.get(target_url)
            
            # Wait for page load
            self.logger.info("Waiting for page to fully load...")
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)  # Additional wait for dynamic content
            
            # Try to click AI button
            if not self.find_and_click_ai_button(self.driver):
                return {
                    'success': False,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'error': 'Could not click AI button'
                }
            
            # Wait for and capture AI content
            content = self.wait_for_ai_content()
            if content:
                return {
                    'success': True,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'ai_review': content,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {
                    'success': False,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'error': 'Timeout waiting for AI content'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting AI review: {str(e)}")
            return {
                'success': False,
                'coin_name': coin_name,
                'coin_symbol': coin_symbol,
                'error': str(e)
            } 