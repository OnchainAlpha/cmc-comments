from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from utils.helpers import random_delay
import logging
import time

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
        
        # Strategy 1: Look for CMC AI section first, then find questions
        try:
            # Find CMC AI section
            cmc_ai_section = None
            section_patterns = [
                "//*[contains(text(), 'CMC AI')]",
                "//div[contains(., 'CMC AI') and not(contains(@class, 'button'))]",
                "//span[contains(text(), 'CMC AI')]",
                "//h2[contains(text(), 'CMC AI')]",
                "//h3[contains(text(), 'CMC AI')]"
            ]
            
            for pattern in section_patterns:
                try:
                    elements = driver.find_elements(By.XPATH, pattern)
                    for elem in elements:
                        if elem.is_displayed() and elem.text.strip() == "CMC AI":
                            cmc_ai_section = elem
                            self.logger.info("✅ Found CMC AI section")
                            break
                    if cmc_ai_section:
                        break
                except:
                    continue
            
            # If we found CMC AI section, look for questions nearby
            if cmc_ai_section:
                # Look for question elements in the parent/sibling elements
                parent = cmc_ai_section.find_element(By.XPATH, "./..")
                
                # Search for clickable questions
                question_selectors = [
                    ".//div[contains(@class, 'question')]",
                    ".//button[contains(., '?')]",
                    ".//div[contains(., '?') and @role='button']",
                    ".//div[contains(., 'Why')]",
                    ".//div[contains(., 'What')]",
                    ".//div[contains(., 'price')]",
                    ".//div[contains(., 'affect')]",
                    ".//span[contains(., '?')]",
                    ".//*[contains(text(), '?')]"
                ]
                
                for selector in question_selectors:
                    try:
                        questions = parent.find_elements(By.XPATH, selector)
                        for q in questions:
                            # Check if it's a question (contains ?)
                            if "?" in q.text and q.is_displayed() and q.is_enabled():
                                self.logger.info(f"✅ Found AI question: '{q.text}'")
                                return q
                    except:
                        continue
        except Exception as e:
            self.logger.debug(f"CMC AI section search failed: {str(e)}")
        
        # Strategy 2: Direct search for question patterns
        question_patterns = [
            "Why is",
            "What could affect",
            "What are people saying",
            "How does",
            "What is the",
            "Will the price"
        ]
        
        for pattern in question_patterns:
            try:
                # Search for elements containing these question starts
                elements = driver.find_elements(By.XPATH, 
                    f"//*[contains(text(), '{pattern}') and contains(text(), '?')]")
                
                for element in elements:
                    # Verify it's clickable
                    if element.is_displayed() and element.is_enabled():
                        # Check if it's near CMC AI text
                        try:
                            # Check if CMC AI is within 500 pixels
                            cmc_nearby = driver.find_elements(By.XPATH, 
                                "//*[contains(text(), 'CMC AI')]")
                            for cmc in cmc_nearby:
                                if cmc.is_displayed():
                                    distance = abs(element.location['y'] - cmc.location['y'])
                                    if distance < 500:  # Within reasonable distance
                                        self.logger.info(f"✅ Found AI question prompt: '{element.text}'")
                                        return element
                        except:
                            # If we can't check distance, still return if it looks like a question
                            if len(element.text) > 10 and element.text.endswith("?"):
                                self.logger.info(f"✅ Found potential AI question: '{element.text}'")
                                return element
            except Exception as e:
                self.logger.debug(f"Question pattern '{pattern}' search failed: {str(e)}")
        
        # Strategy 3: Look for any clickable element with a question mark near CMC AI
        try:
            # Find all elements with question marks
            question_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '?')]")
            
            for elem in question_elements:
                try:
                    # Check if it's displayed and has reasonable length (not just "?")
                    if (elem.is_displayed() and 
                        elem.is_enabled() and 
                        len(elem.text) > 15 and 
                        elem.text.count('?') == 1):  # Exactly one question mark
                        
                        # Check tag type - prefer divs, buttons, spans
                        tag = elem.tag_name.lower()
                        if tag in ['div', 'button', 'span', 'a']:
                            self.logger.info(f"✅ Found clickable question: '{elem.text}'")
                            return elem
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"General question search failed: {str(e)}")
        
        # Strategy 4: Look for elements with specific CSS that might indicate AI questions
        css_selectors = [
            "[class*='ai-question']",
            "[class*='ai-prompt']",
            "[class*='question']",
            "[data-testid*='question']",
            "[role='button'][class*='ai']"
        ]
        
        for css in css_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, css)
                for elem in elements:
                    if elem.is_displayed() and "?" in elem.text:
                        self.logger.info(f"✅ Found AI question by CSS: '{elem.text}'")
                        return elem
            except:
                continue
        
        self.logger.warning("❌ No AI question prompts found")
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
            
            # Navigate with retry logic
            max_retries = 3
            for retry in range(max_retries):
                try:
                    self.driver.get(target_url)
                    
                    # Smart wait for page to fully load
                    self.logger.info("Waiting for page to fully load...")
                    WebDriverWait(self.driver, 30).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    
                    # Wait for specific CMC elements to ensure page is ready
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-role='coin-name'], h1, .coin-name"))
                    )
                    
                    # Additional wait to ensure all dynamic content loads
                    time.sleep(3)
                    
                    # Verify we're on the right page
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if coin_symbol.upper() in page_text.upper():
                        self.logger.info(f"✅ Confirmed on {coin_symbol} page")
                        break
                    else:
                        self.logger.warning(f"Page doesn't contain {coin_symbol}, retrying...")
                        if retry < max_retries - 1:
                            time.sleep(2)
                            continue
                except Exception as e:
                    self.logger.error(f"Navigation attempt {retry+1} failed: {str(e)}")
                    if retry < max_retries - 1:
                        time.sleep(2)
                        continue
                    raise
            
            # Try different scroll positions to find the AI button
            scroll_positions = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
            ai_button = None
            
            for scroll_pos in scroll_positions:
                self.logger.info(f"Scrolling to {int(scroll_pos * 100)}% of page...")
                self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {scroll_pos});")
                time.sleep(2)
                
                # Try to find AI button using smart detection
                ai_button = self.find_ai_button(self.driver)
                if ai_button:
                    break
            
            if not ai_button:
                # Last attempt - check if there's an XPath in the provided parameter
                if coin_url and "xpath:" in coin_url:
                    # Extract XPath from URL parameter if provided
                    custom_xpath = coin_url.split("xpath:")[1]
                    try:
                        ai_button = self.driver.find_element(By.XPATH, custom_xpath)
                        self.logger.info(f"Found AI button with custom XPath")
                    except:
                        pass
            
            if not ai_button:
                # Save screenshot for debugging
                screenshot_path = f"debug_{coin_symbol}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.error(f"AI button not found. Screenshot saved: {screenshot_path}")
                
                return {
                    'success': False,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'error': 'AI button not found after exhaustive search',
                    'screenshot': screenshot_path
                }
            
            try:
                self.logger.info("✅ Found AI analysis button!")
                
                # Scroll button into view
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", ai_button)
                time.sleep(2)
                
                # Highlight the button for visual confirmation (debugging)
                self.driver.execute_script("""
                    arguments[0].style.border = '3px solid red';
                    arguments[0].style.backgroundColor = 'yellow';
                """, ai_button)
                time.sleep(1)
                
                # Try multiple click methods
                click_success = False
                for method in range(3):
                    try:
                        if method == 0:
                            # Method 1: Regular click
                            ai_button.click()
                            self.logger.info("Clicked using regular click")
                        elif method == 1:
                            # Method 2: JavaScript click
                            self.driver.execute_script("arguments[0].click();", ai_button)
                            self.logger.info("Clicked using JavaScript")
                        else:
                            # Method 3: Action chains
                            from selenium.webdriver.common.action_chains import ActionChains
                            ActionChains(self.driver).move_to_element(ai_button).click().perform()
                            self.logger.info("Clicked using Action Chains")
                        
                        click_success = True
                        break
                    except Exception as e:
                        self.logger.warning(f"Click method {method+1} failed: {str(e)}")
                        time.sleep(1)
                
                if not click_success:
                    raise Exception("Could not click AI button with any method")
                
                # Wait for AI content to generate with visual feedback
                self.logger.info("⏳ Waiting for AI to generate content...")
                self.logger.info("This may take 15-30 seconds...")
                
                # Store the question text to verify it changes
                clicked_question = ai_button.text
                self.logger.info(f"Clicked on question: '{clicked_question}'")
                
                content_changed = False
                ai_response_text = ""
                
                for wait_time in range(30):  # Wait up to 30 seconds
                    time.sleep(1)
                    try:
                        # Look for TLDR section on the right side of the screen
                        tldr_selectors = [
                            "//h2[text()='TLDR' or text()='TL;DR']",
                            "//div[contains(text(), 'TLDR')]",
                            "//span[contains(text(), 'TLDR')]",
                            "//*[contains(@class, 'tldr')]",
                            "//h3[text()='TLDR' or text()='TL;DR']"
                        ]
                        
                        tldr_element = None
                        for selector in tldr_selectors:
                            try:
                                elements = self.driver.find_elements(By.XPATH, selector)
                                for elem in elements:
                                    if elem.is_displayed():
                                        tldr_element = elem
                                        self.logger.info("✅ Found TLDR section!")
                                        break
                                if tldr_element:
                                    break
                            except:
                                continue
                        
                        if tldr_element:
                            # Get the TLDR content - look for the parent container
                            tldr_container = tldr_element.find_element(By.XPATH, "./..")
                            
                            # Get all text content after TLDR
                            full_text = tldr_container.text
                            
                            # Extract just the TLDR content
                            if "TLDR" in full_text:
                                # Split by TLDR and take everything after it
                                parts = full_text.split("TLDR")
                                if len(parts) > 1:
                                    tldr_content = parts[1].strip()
                                    
                                    # If there's another section after TLDR, cut it off
                                    # Common sections that might follow: "Analysis", "Details", "Read more"
                                    for end_marker in ["Analysis", "Details", "Read more", "Full report", "Thought for"]:
                                        if end_marker in tldr_content:
                                            tldr_content = tldr_content.split(end_marker)[0].strip()
                                    
                                    # Clean up the content
                                    tldr_content = tldr_content.strip()
                                    
                                    if len(tldr_content) > 50:  # Make sure we have substantial content
                                        content_changed = True
                                        ai_response_text = tldr_content
                                        self.logger.info(f"✅ Extracted TLDR content! Length: {len(ai_response_text)} chars")
                                        self.logger.info(f"TLDR Preview: {ai_response_text[:100]}...")
                                        break
                        
                        # Alternative: Look for right-side panel with AI response
                        if not content_changed:
                            right_panel_selectors = [
                                "//div[contains(@class, 'right')]//div[contains(text(), 'rose') or contains(text(), 'fell') or contains(text(), 'gained')]",
                                "//aside//div[contains(text(), 'ETF') or contains(text(), 'Technical') or contains(text(), 'Sector')]",
                                "//div[@role='complementary']//div[contains(text(), '%')]"
                            ]
                            
                            for selector in right_panel_selectors:
                                try:
                                    response_elem = self.driver.find_element(By.XPATH, selector)
                                    if response_elem.is_displayed() and len(response_elem.text) > 100:
                                        # Try to find the containing section
                                        container = response_elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'container') or contains(@class, 'section') or contains(@class, 'panel')]")
                                        if container:
                                            ai_response_text = container.text
                                            # Extract TLDR if present
                                            if "TLDR" in ai_response_text:
                                                parts = ai_response_text.split("TLDR")
                                                if len(parts) > 1:
                                                    ai_response_text = parts[1].split("Thought for")[0].strip()
                                            
                                            content_changed = True
                                            self.logger.info(f"✅ Found AI response in right panel! Length: {len(ai_response_text)} chars")
                                            break
                                except:
                                    continue
                        
                        if content_changed:
                            break
                        
                        if wait_time % 5 == 0:
                            self.logger.info(f"Still waiting for TLDR content... {wait_time} seconds elapsed")
                            
                    except Exception as e:
                        self.logger.debug(f"Check failed at {wait_time}s: {str(e)}")
                
                if content_changed and ai_response_text:
                    return {
                        'success': True,
                        'coin_name': coin_name,
                        'coin_symbol': coin_symbol,
                        'ai_review': ai_response_text,
                        'question_asked': clicked_question,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'url_used': target_url
                    }
                else:
                    self.logger.error("AI content did not appear after 30 seconds")
                    # Take screenshot for debugging
                    screenshot_path = f"no_response_{coin_symbol}_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    self.driver.save_screenshot(screenshot_path)
                    
                    return {
                        'success': False,
                        'coin_name': coin_name,
                        'coin_symbol': coin_symbol,
                        'error': 'AI content generation timeout - no response appeared',
                        'screenshot': screenshot_path
                    }
                
            except Exception as e:
                self.logger.error(f"AI button interaction failed: {str(e)}")
                
                # Check if we need to log in
                if "log in" in self.driver.page_source.lower() or "sign up" in self.driver.page_source.lower():
                    return {
                        'success': False,
                        'coin_name': coin_name,
                        'coin_symbol': coin_symbol,
                        'error': 'Not logged in to CMC - please log in manually first'
                    }
                
                return {
                    'success': False,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'error': f'AI button interaction failed: {str(e)}'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting AI review: {str(e)}")
            return {
                'success': False,
                'coin_name': coin_name,
                'coin_symbol': coin_symbol,
                'error': str(e)
            } 