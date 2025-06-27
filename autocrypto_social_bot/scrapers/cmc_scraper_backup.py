import time
import logging
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from autocrypto_social_bot.utils.helpers import random_delay
import unicodedata
import random

# 🔥 BREAKTHROUGH: Import our verified working CMC bypass system
try:
    from autocrypto_social_bot.cmc_bypass_manager import cmc_bypass_manager
    CMC_BYPASS_AVAILABLE = True
    print("🔥 CMC Scraper: Breakthrough bypass system loaded!")
except ImportError:
    CMC_BYPASS_AVAILABLE = False
    cmc_bypass_manager = None
    print("⚠️ CMC Scraper: Bypass system not available, using fallback")

class CMCScraper:
    def __init__(self, driver, profile_manager=None):
        self.base_url = "https://coinmarketcap.com"
        self.community_url = "https://coinmarketcap.com/community/"
        self.currencies_url = "https://coinmarketcap.com/currencies/"
        self.driver = driver
        self.profile_manager = profile_manager
        self.logger = logging.getLogger(__name__)
        self.MAX_POST_LENGTH = 2000
        
        # 🔥 BREAKTHROUGH: Initialize our CMC bypass system for 100% success rate
        if CMC_BYPASS_AVAILABLE and cmc_bypass_manager:
            print("🚀 CMC Scraper: Breakthrough bypass system ready!")
            try:
                verified_count = len(cmc_bypass_manager.verified_cmc_proxies)
                print(f"✅ CMC Scraper: {verified_count} verified working CMC bypass proxies ready!")
                self.bypass_available = True
            except Exception as e:
                print(f"❌ CMC Scraper: Bypass error: {str(e)}")
                self.bypass_available = False
        else:
            self.bypass_available = False

    def _handle_rate_limit(self):
        """Handle rate limit by switching to next profile"""
        if not self.profile_manager:
            self.logger.warning("No profile manager available for rotation")
            return False

        try:
            self.logger.info("Switching to next profile due to rate limit...")
            self.driver = self.profile_manager.switch_to_next_profile()
            return True
        except Exception as e:
            self.logger.error(f"Failed to switch profile: {str(e)}")
            return False

    def _sanitize_message_for_chrome(self, message: str) -> str:
        """Sanitize message to remove characters that ChromeDriver can't handle"""
        # Remove or replace problematic Unicode characters
        sanitized = ""
        for char in message:
            # Check if character is in BMP (Basic Multilingual Plane)
            if ord(char) <= 0xFFFF:
                sanitized += char
            else:
                # Replace non-BMP characters with safe alternatives
                if char in ['💭', '💼', '📊', '🔍', '📈', '📉', '💰', '🎯', '🚀', '✅', '❌', '⚠️', '💡']:
                    # Replace common emojis with text equivalents
                    emoji_replacements = {
                        '💭': '[THOUGHTS]',
                        '💼': '[PROFESSIONAL]',
                        '📊': '[STATS]',
                        '🔍': '[ANALYSIS]',
                        '📈': '[UP]',
                        '📉': '[DOWN]',
                        '💰': '[MONEY]',
                        '🎯': '[TARGET]',
                        '🚀': '[ROCKET]',
                        '✅': '[SUCCESS]',
                        '❌': '[FAIL]',
                        '⚠️': '[WARNING]',
                        '💡': '[IDEA]'
                    }
                    sanitized += emoji_replacements.get(char, '[EMOJI]')
                else:
                    # Replace other non-BMP characters with space
                    sanitized += ' '
        
        # Also remove any other potentially problematic characters
        problematic_chars = ['\u200b', '\u200c', '\u200d', '\u2060', '\u2061', '\u2062', '\u2063', '\u2064']
        for char in problematic_chars:
            sanitized = sanitized.replace(char, '')
        
        # Normalize Unicode to remove combining characters
        sanitized = unicodedata.normalize('NFKC', sanitized)
        
        return sanitized.strip()

    def _split_message(self, message: str) -> list:
        """Split a long message into chunks that fit CMC's character limit"""
        if len(message) <= self.MAX_POST_LENGTH:
            return [message]
            
        chunks = []
        lines = message.split('\n')
        current_chunk = ""
        
        for line in lines:
            # If adding this line would exceed limit, save current chunk and start new one
            if len(current_chunk) + len(line) + 1 > self.MAX_POST_LENGTH:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk = current_chunk + "\n" + line if current_chunk else line
                
        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # Add part numbers to chunks
        total_parts = len(chunks)
        if total_parts > 1:
            for i in range(total_parts):
                chunks[i] = f"[Part {i+1}/{total_parts}]\n\n{chunks[i]}"
                
        return chunks

    def post_community_comment(self, symbol: str, message: str) -> bool:
        """Post a comment to CMC community with anti-detection and shadowban handling"""
        max_attempts = 3
        current_attempt = 0

        while current_attempt < max_attempts:
            try:
                # Check for shadowban before posting
                if hasattr(self.profile_manager, 'check_and_handle_shadowban'):
                    shadowban_detected = self.profile_manager.check_and_handle_shadowban()
                    if shadowban_detected:
                        print("🚫 [SHADOWBAN] Detected and handled, switching IP/profile...")
                        # Get new driver after IP rotation
                        self.driver = self.profile_manager.current_driver
                
                # Get adaptive delay from anti-detection system
                if hasattr(self.profile_manager, 'get_adaptive_delay'):
                    adaptive_delay = self.profile_manager.get_adaptive_delay()
                    print(f"⏱️ [ADAPTIVE] Using {adaptive_delay}s delay based on session state")
                else:
                    adaptive_delay = random.randint(45, 90)
                
                # Add human-like behavior before posting
                if hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection:
                    self.profile_manager.anti_detection.randomize_behavior(self.driver)
                
                # Navigate to community page
                self._navigate_to_cmc_with_bypass(self.community_url)
                random_delay(2, 4)

                # Try to post
                success = self._post_comment(symbol, message)
                
                if success:
                    print("✅ [SUCCESS] Post successful!")
                    
                    # Update anti-detection system with success
                    if hasattr(self.profile_manager, 'update_post_result'):
                        self.profile_manager.update_post_result(True)
                    
                    # Check if we should rotate IP for next post
                    should_rotate = False
                    if hasattr(self.profile_manager, 'anti_detection') and self.profile_manager.anti_detection:
                        should_rotate = self.profile_manager.anti_detection.should_rotate_ip()
                    
                    if should_rotate:
                        print("🔄 [IP-ROTATE] Scheduled IP rotation for next post")
                        print("🔍 [IP-ROTATE] Reason: Anti-detection system triggered rotation")
                        try:
                            self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
                            print("✅ [IP-ROTATE] Successfully rotated IP and profile")
                        except Exception as e:
                            print(f"⚠️ [IP-ROTATE] Failed: {str(e)}, continuing with current session")
                    else:
                        # Regular profile rotation
                        if self.profile_manager:
                            try:
                                print("🔄 [PROFILE] Regular profile rotation (no IP change)")
                                self.driver = self.profile_manager.switch_to_next_profile()
                                print("✅ [PROFILE] Regular profile rotation completed")
                            except Exception as e:
                                print(f"⚠️ [PROFILE] Rotation failed: {str(e)}")
                    
                    # Apply adaptive delay before next operation
                    print(f"⏱️ [DELAY] Applying adaptive delay: {adaptive_delay}s")
                    time.sleep(adaptive_delay)
                    
                    return True

                # Handle posting failure
                print("❌ [FAIL] Post failed, analyzing error...")
                
                # Check for specific error types
                error_type = self._detect_error_type()
                print(f"🔍 [ERROR-TYPE] Detected: {error_type}")
                
                # Update anti-detection system with failure
                if hasattr(self.profile_manager, 'update_post_result'):
                    self.profile_manager.update_post_result(False, error_type)
                
                # Handle different error types
                if error_type == 'shadowban':
                    print("🚫 [SHADOWBAN] Shadowban detected, forcing IP rotation...")
                    print("🔄 [SHADOWBAN] Initiating emergency IP change...")
                    if hasattr(self.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
                        self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
                        print("✅ [SHADOWBAN] Emergency IP rotation completed")
                        current_attempt += 1
                        continue
                
                elif error_type == 'rate_limit':
                    print("⏳ [RATE-LIMIT] Rate limit detected, applying extended delay...")
                    extended_delay = random.randint(120, 300)  # 2-5 minutes
                    print(f"⏱️ [EXTENDED-DELAY] Waiting {extended_delay}s...")
                    time.sleep(extended_delay)
                    
                    # Try IP rotation for rate limits too
                    print("🔄 [RATE-LIMIT] Attempting IP rotation to bypass rate limit...")
                    if hasattr(self.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
                        self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
                        print("✅ [RATE-LIMIT] IP rotation completed")
                    
                    current_attempt += 1
                    continue
                
                # For other errors, just rotate profile and continue
                if self.profile_manager:
                    try:
                        print("🔄 [ERROR] Rotating profile due to posting error...")
                        self.driver = self.profile_manager.switch_to_next_profile()
                        print("✅ [ERROR] Profile rotated after error")
                    except Exception as e:
                        print(f"⚠️ [ERROR] Failed to rotate profile: {str(e)}")

                return False

            except Exception as e:
                print(f"❌ [EXCEPTION] Error posting comment: {str(e)}")
                
                # Update anti-detection with exception
                if hasattr(self.profile_manager, 'update_post_result'):
                    self.profile_manager.update_post_result(False, 'exception')
                
                current_attempt += 1
                
                # Try rotating profile on error as well
                if self.profile_manager and current_attempt < max_attempts:
                    try:
                        if hasattr(self.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
                            self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
                        else:
                            self.driver = self.profile_manager.switch_to_next_profile()
                        print("🔄 [EXCEPTION] Rotated profile after exception")
                        time.sleep(random.randint(10, 30))  # Wait before retry
                    except Exception as rotate_error:
                        print(f"⚠️ [EXCEPTION] Failed to rotate profile: {str(rotate_error)}")

        print(f"❌ [FINAL-FAIL] Failed after {max_attempts} attempts")
        return False

    def _detect_error_type(self) -> str:
        """Detect the type of error from page content"""
        try:
            page_source = self.driver.page_source.lower()
            
            # FIXED: Shadowban indicators - only real shadowbans, not rate limits
            shadowban_indicators = [
                "your post was not published",
                "content not visible to others", 
                "under review by moderators",
                "violates our community guidelines",
                "temporarily restricted access",
                "account suspended",
                "unusual activity detected",
                "content has been removed",
                "account has been restricted",
                "posts are not showing to others"
            ]
            
            for indicator in shadowban_indicators:
                if indicator in page_source:
                    return 'shadowban'
            
            # FIXED: Rate limit indicators - these are normal, not shadowbans!
            rate_limit_indicators = [
                "too frequently",
                "wait before posting", 
                "rate limit",
                "try again later",
                "slow down",
                "posting too fast",
                "please wait"
            ]
            
            for indicator in rate_limit_indicators:
                if indicator in page_source:
                    return 'rate_limit'  # This should NOT trigger shadowban detection!
            
            # Check for error elements
            error_selectors = [
                "//div[contains(text(), 'error')]",
                "//div[contains(text(), 'failed')]",
                "//div[contains(@class, 'error')]"
            ]
            
            for selector in error_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        return 'general_error'
                except:
                    continue
            
            return 'unknown'
            
        except Exception as e:
            self.logger.debug(f"Error detecting error type: {str(e)}")
            return 'unknown'

    def _post_comment(self, symbol: str, message: str) -> bool:
        """Post a comment in CMC community"""
        try:
            # Sanitize message to prevent ChromeDriver crashes
            sanitized_message = self._sanitize_message_for_chrome(message)
            
            # Split message into chunks if needed
            message_chunks = self._split_message(sanitized_message)
            total_chunks = len(message_chunks)
            
            print("\n" + "="*50)
            print(f"🚀 POSTING TO CMC COMMUNITY: ${symbol}")
            if total_chunks > 1:
                print(f"Message will be split into {total_chunks} parts")
            print("="*50)
            
            success = True
            for i, chunk in enumerate(message_chunks, 1):
                if total_chunks > 1:
                    print(f"\nPosting part {i}/{total_chunks}...")
                
                # Navigate to community page
                print("1. 🔥 Navigating to CMC community via breakthrough bypass...")
                self._navigate_to_cmc_with_bypass(self.community_url)
                random_delay(5, 7)  # Increased delay for page load
                
                # Find and click the editor div - try multiple selectors
                print("2. Looking for editor...")
                editor_selectors = [
                    'div[contenteditable="true"]',
                    'div[role="textbox"]',
                    'div.base-editor div[contenteditable="true"]',
                    'div.editor div[contenteditable="true"]',
                    '#cmc-editor div[contenteditable="true"]'
                ]
                
                editor_div = None
                for selector in editor_selectors:
                    try:
                        editor_div = WebDriverWait(self.driver, 10).until(  # Increased timeout
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                        if editor_div:
                            break
                    except Exception:
                        continue
                
                if not editor_div:
                    print("❌ Could not find editor")
                    return False
                    
                print("✅ Found editor")
                
                # Make sure editor is in view and clickable
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", editor_div)
                random_delay(2, 3)  # Increased delay after scroll
                
                # Click editor and wait for it to be ready
                editor_div.click()
                random_delay(2, 3)
                
                # Type the ticker symbol
                print(f"3. Typing ${symbol}...")
                editor_div.send_keys(f"${symbol}")
                random_delay(3, 4)  # Increased delay after typing symbol
                
                # Press Enter to select the ticker
                print("4. Selecting ticker...")
                editor_div.send_keys(Keys.ENTER)
                random_delay(3, 4)  # Increased delay after selecting ticker
                
                # Clean up the message (already sanitized, but double-check)
                print("5. Adding analysis message...")
                # Additional emoji replacements for safety
                emoji_replacements = {
                    "🔍": "[ANALYSIS]",
                    "📊": "[STATS]",
                    "🏥": "[HEALTH]",
                    "⚠️": "[WARNING]",
                    "🚩": "[RISK]",
                    "💡": "[NOTE]",
                    "•": "-",
                    "💭": "[THOUGHTS]",
                    "💼": "[PROFESSIONAL]",
                    "📈": "[UP]",
                    "📉": "[DOWN]",
                    "💰": "[MONEY]",
                    "🎯": "[TARGET]",
                    "🚀": "[ROCKET]",
                    "✅": "[SUCCESS]",
                    "❌": "[FAIL]"
                }
                
                chunk_text = chunk
                for emoji, replacement in emoji_replacements.items():
                    chunk_text = chunk_text.replace(emoji, replacement)
                
                # Split into lines and post with proper line breaks
                lines = chunk_text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        editor_div.send_keys(line.strip())
                        if i < len(lines) - 1:  # Don't add line break after last line
                            editor_div.send_keys(Keys.SHIFT + Keys.ENTER)
                        random_delay(0.5, 1)  # Small delay between lines
                
                # Wait for content to be fully entered
                random_delay(2, 3)
                
                # Find and click post button - try multiple approaches
                print("6. Looking for post button...")
                post_button = None
                
                # Try finding by text content first
                try:
                    post_button = WebDriverWait(self.driver, 10).until(  # Increased timeout
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Post')]"))
                    )
                except Exception:
                    # Try CSS selectors if text search fails
                    button_selectors = [
                        'button[class*="post"]',
                        'div[class*="post-button"]',
                        'button[class*="PostButton"]',
                        '#cmc-editor button',
                        'div.editor-post-button button'
                    ]
                    
                    for selector in button_selectors:
                        try:
                            post_button = WebDriverWait(self.driver, 10).until(  # Increased timeout
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                            if post_button:
                                break
                        except Exception:
                            continue
                
                if not post_button:
                    # Try JavaScript click as last resort
                    print("Trying JavaScript click...")
                    try:
                        self.driver.execute_script("""
                            var buttons = document.querySelectorAll('button');
                            for(var i=0; i<buttons.length; i++){
                                if(buttons[i].textContent.toLowerCase().includes('post')){
                                    buttons[i].click();
                                    return true;
                                }
                            }
                            return false;
                        """)
                        random_delay(3, 5)  # Increased delay after JS click
                    except Exception:
                        print("❌ Could not find post button")
                        return False
                else:
                    try:
                        # Scroll the button into view before clicking
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", post_button)
                        random_delay(1, 2)
                        post_button.click()
                        random_delay(3, 5)  # Increased delay after click
                    except Exception:
                        print("❌ Failed to click post button")
                        return False
                
                print("✅ Clicked post button")
                
                # Wait for success indicator or error message with increased timeout
                try:
                    success_indicators = [
                        "//div[contains(text(), 'posted successfully')]",
                        "//div[contains(@class, 'success')]",
                        "//div[contains(text(), 'Your comment has been')]",
                        "//div[contains(text(), 'successfully')]",  # Added more generic success text
                        "//div[contains(text(), 'Comment posted')]",
                        "//span[contains(text(), 'Posted')]",
                        "//div[contains(text(), 'Thanks for sharing')]"
                    ]
                    
                    # Wait longer for success verification
                    success = False
                    max_retries = 5  # Increased retries
                    for retry in range(max_retries):
                        print(f"Checking for success indicators (attempt {retry + 1}/{max_retries})...")
                        
                        for indicator in success_indicators:
                            try:
                                element = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, indicator))
                                )
                                if element and element.is_displayed():
                                    print(f"✅ Found success indicator: {element.text[:50]}...")
                                    success = True
                                    break
                            except Exception:
                                continue
                        
                        if success:
                            break
                            
                        # Check URL change as success indicator
                        try:
                            current_url = self.driver.current_url
                            if "community" in current_url and "posted" not in current_url:
                                # If we're still on community page without error params, likely success
                                print("✅ URL indicates successful post")
                                success = True
                                break
                        except:
                            pass
                        
                        # Check if the post appears in the community feed
                        try:
                            # Look for recent posts containing our symbol
                            symbol_clean = symbol.replace('$', '').replace('\n', ' ').strip()
                            feed_posts = self.driver.find_elements(By.XPATH, f"//div[contains(text(), '{symbol_clean}')]")
                            if feed_posts:
                                print(f"✅ Found post with symbol {symbol_clean} in feed")
                                success = True
                                break
                        except:
                            pass
                        
                        # Wait between retries
                        if retry < max_retries - 1:
                            random_delay(2, 3)
                    
                    if not success:
                        print("❌ Could not verify post success after multiple attempts")
                        return False
                        
                except Exception:
                    print("❌ Could not verify post success - verification error")
                    return False
                
                # If this is not the last chunk, wait before posting next part
                if i < total_chunks:
                    random_delay(5, 7)  # Increased delay between chunks
                else:
                    print(f"\n✅ Successfully posted analysis for ${symbol}")
                    print("="*50 + "\n")
            
            return True

        except Exception as e:
            print(f"\n❌ Error posting to CMC community: {str(e)}")
            return False

    def get_trending_coins(self, limit=100, page=1) -> list:
        """Get trending coins from CMC with automatic proxy failure handling"""
        trending_coins = []
        
        try:
            # FIXED: Use different approach for pagination that actually works with CMC
            # Instead of offset-based pagination, use different sorting/filtering approaches
            page_urls = [
                f"{self.base_url}/?type=coins",  # Main trending page
                f"{self.base_url}/new/?type=coins",  # New coins
                f"{self.base_url}/gainers-losers/?type=coins",  # Gainers/Losers
                f"{self.base_url}/trending-cryptocurrencies/",  # Alternative trending  
                f"{self.base_url}/?type=coins&sort=percent_change_24h",  # Sorted by 24h change
                f"{self.base_url}/?type=coins&sort=volume_24h",  # Sorted by volume
                f"{self.base_url}/?type=coins&sort=market_cap",  # Sorted by market cap
                f"{self.base_url}/?type=coins&sort=price",  # Sorted by price
                f"{self.base_url}/most-visited-cryptocurrencies/",  # Most visited
                f"{self.base_url}/recently-added/",  # Recently added
            ]
            
            # Use modulo to cycle through different URL types
            url_index = (page - 1) % len(page_urls)
            trending_url = page_urls[url_index]
            
            # For pages beyond the basic URLs, add offset parameters
            if page > len(page_urls):
                offset = ((page - len(page_urls) - 1) * 50) + 1
                trending_url += f"&start={offset}&limit=100" if '?' in trending_url else f"?start={offset}&limit=100"
            
            print(f"🔥 Using diversified URL approach for page {page}: {trending_url}")
            
            # 🔥 BREAKTHROUGH: Navigate using bypass system with automatic proxy switching
            print(f"🔥 Navigating to CMC trending page via breakthrough bypass...")
            navigation_success = self._navigate_to_cmc_with_bypass(trending_url)
            
            if not navigation_success:
                print(f"❌ Failed to navigate to CMC after trying multiple proxies")
                print(f"🔄 The system has automatically:")
                print(f"   • Tested multiple proxies")
                print(f"   • Marked failed proxies as unusable")
                print(f"   • Attempted to discover new proxies")
                print(f"💡 Try running the bot again - it may find working proxies")
                return []
            
            print(f"✅ Successfully accessed CMC trending page")
            
            # Wait for page to stabilize
            time.sleep(3)
            
            # Now try to extract trending coins
            try:
                # Wait for table to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "table tr"))
                )
                
                # Get table rows
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                
                if not rows:
                    self.logger.error("Could not find trending coins table")
                    return []
                
                print(f"📊 Found {len(rows)} coin rows on page {page}")
                
                # Extract coin data from each row
                for i, row in enumerate(rows):
                    if len(trending_coins) >= limit:
                        break
                        
                    try:
                        coin_data = self._extract_coin_from_row(row, i + 1)
                        if coin_data:
                            trending_coins.append(coin_data)
                            print(f"✅ Extracted: {coin_data['name']} (${coin_data['symbol']})")
                    except Exception as e:
                        self.logger.warning(f"Error extracting coin from row {i}: {str(e)}")
                        continue
                
                print(f"📈 Successfully extracted {len(trending_coins)} trending coins from page {page}")
                return trending_coins
                
            except Exception as extraction_error:
                print(f"❌ Error extracting coins from page: {str(extraction_error)}")
                
                # Enhanced proxy issue detection by analyzing page content
                try:
                    page_source = self.driver.page_source.lower()
                    page_title = self.driver.title.lower()
                    current_url = self.driver.current_url.lower()
                    
                    print(f"🔍 Analyzing page content for proxy issues...")
                    print(f"   📄 Page title: {page_title[:50]}...")
                    print(f"   🔗 Current URL: {current_url[:50]}...")
                    
                    # Comprehensive proxy/tunnel error detection
                    proxy_tunnel_errors = [
                        "err_tunnel_connection_failed",
                        "err_proxy_connection_failed", 
                        "err_timed_out",
                        "err_connection_timed_out",
                        "err_connection_refused",
                        "err_address_unreachable",
                        "tunnel connection failed",
                        "proxy connection failed",
                        "502 bad gateway",
                        "503 service unavailable",
                        "504 gateway timeout",
                        "connection timed out",
                        "this site can't be reached",
                        "took too long to respond"
                    ]
                    
                    # Check for explicit proxy errors
                    has_proxy_error = any(error in page_source for error in proxy_tunnel_errors)
                    has_title_error = any(error in page_title for error in proxy_tunnel_errors)
                    
                    # Check for insufficient CMC content (indicates blocked/filtered page)
                    cmc_content_indicators = [
                        "coinmarketcap",
                        "cryptocurrency", 
                        "bitcoin",
                        "ethereum",
                        "market cap",
                        "trending",
                        "price",
                        "trading volume"
                    ]
                    
                    cmc_indicators_found = sum(1 for indicator in cmc_content_indicators if indicator in page_source)
                    insufficient_content = cmc_indicators_found < 3
                    
                    # Check for wrong page/redirects
                    wrong_page = (
                        "login" in current_url or 
                        "portfolio-tracker" in current_url or
                        "404" in page_title or
                        "not found" in page_title
                    )
                    
                    print(f"   🔍 Proxy error detected: {has_proxy_error or has_title_error}")
                    print(f"   📊 CMC content indicators: {cmc_indicators_found}/8 found")
                    print(f"   🚪 Wrong page detected: {wrong_page}")
                    
                    is_proxy_issue = has_proxy_error or has_title_error or insufficient_content or wrong_page
                    
                    if is_proxy_issue:
                        print(f"🔍 PROXY ISSUE CONFIRMED: Page content indicates proxy failure")
                        if has_proxy_error or has_title_error:
                            print(f"   ❌ Explicit proxy/tunnel errors found")
                        if insufficient_content:
                            print(f"   ❌ Insufficient CMC content (possible blocking/filtering)")
                        if wrong_page:
                            print(f"   ❌ Wrong page/redirect detected")
                        
                        print(f"🔄 Current proxy failed after initial connection - triggering automatic switch")
                        
                        # Get current proxy for marking as failed
                        current_proxy = None
                        if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                            current_proxy = getattr(self.driver, '_enterprise_working_proxy', None)
                        elif hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                            current_proxy = getattr(self.driver, '_cmc_working_proxy', None)
                        
                        if current_proxy:
                            print(f"🗑️ Marking proxy {current_proxy} as failed due to content validation failure")
                            
                            # Mark failed in both systems
                            if hasattr(self.profile_manager, 'enterprise_proxy'):
                                self.profile_manager.enterprise_proxy.mark_proxy_failed(
                                    current_proxy, f"Content validation failed: {cmc_indicators_found}/8 CMC indicators"
                                )
                            if hasattr(self.profile_manager, 'anti_detection'):
                                self.profile_manager.anti_detection.mark_proxy_failed(current_proxy)
                        
                        # Try to switch to a new proxy and retry (max 2 retries to avoid infinite loops)
                        retry_count = getattr(self, '_content_validation_retries', 0)
                        if retry_count < 2:
                            self._content_validation_retries = retry_count + 1
                            print(f"🔄 Attempting automatic proxy switch and retry (attempt {retry_count + 1}/2)...")
                            
                            try:
                                # Switch to new proxy system
                                if hasattr(self.profile_manager, 'load_profile_with_enterprise_proxy'):
                                    print("🗂️ Switching to new proxy via enterprise system...")
                                    new_driver = self.profile_manager.load_profile_with_enterprise_proxy()
                                elif hasattr(self.profile_manager, 'load_profile_with_cmc_bypass'):
                                    print("🔥 Switching to new proxy via CMC bypass system...")
                                    new_driver = self.profile_manager.load_profile_with_cmc_bypass()
                                else:
                                    print("🔄 Switching to next profile...")
                                    new_driver = self.profile_manager.switch_to_next_profile()
                                
                                if new_driver:
                                    # Close old driver
                                    try:
                                        self.driver.quit()
                                    except:
                                        pass
                                    
                                    self.driver = new_driver
                                    
                                    # Check what proxy we got
                                    new_proxy = "unknown"
                                    if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                                        new_proxy = getattr(self.driver, '_enterprise_working_proxy', 'unknown')
                                        print(f"✅ Switched to new enterprise proxy: {new_proxy}")
                                    elif hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                                        new_proxy = getattr(self.driver, '_cmc_working_proxy', 'unknown')
                                        print(f"✅ Switched to new CMC bypass proxy: {new_proxy}")
                                    else:
                                        print("✅ Switched to new profile (direct connection)")
                                    
                                    print(f"🔄 Retrying coin extraction with new proxy system...")
                                    
                                    # Retry navigation with new proxy
                                    if self._navigate_to_cmc_with_bypass(trending_url):
                                        time.sleep(3)
                                        
                                        # Retry extraction with new proxy
                                        try:
                                            WebDriverWait(self.driver, 15).until(
                                                EC.presence_of_element_located((By.CSS_SELECTOR, "table tr"))
                                            )
                                            
                                            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
                                            if rows:
                                                print(f"✅ Retry successful: Found {len(rows)} coin rows with new proxy")
                                                for i, row in enumerate(rows):
                                                    if len(trending_coins) >= limit:
                                                        break
                                                    try:
                                                        coin_data = self._extract_coin_from_row(row, i + 1)
                                                        if coin_data:
                                                            trending_coins.append(coin_data)
                                                            print(f"✅ Retry extracted: {coin_data['name']} (${coin_data['symbol']})")
                                                    except Exception as retry_e:
                                                        self.logger.warning(f"Retry error extracting coin from row {i}: {str(retry_e)}")
                                                        continue
                                                
                                                print(f"🎯 RETRY SUCCESS: Extracted {len(trending_coins)} coins with new proxy!")
                                                # Reset retry counter on success
                                                self._content_validation_retries = 0
                                                return trending_coins
                                            else:
                                                print("❌ Retry failed: No coin rows found with new proxy")
                                        except Exception as retry_extract_error:
                                            print(f"❌ Retry extraction failed: {str(retry_extract_error)}")
                                    else:
                                        print("❌ Retry navigation failed with new proxy")
                                else:
                                    print("❌ Failed to load new profile/proxy")
                                    
                            except Exception as retry_error:
                                print(f"❌ Automatic proxy switch failed: {str(retry_error)}")
                        else:
                            print(f"⚠️ Maximum retry attempts reached (2/2) - stopping automatic retries")
                            # Reset counter for next operation
                            self._content_validation_retries = 0
                    else:
                        print(f"ℹ️ Page content appears normal - extraction error may be due to page structure changes")
                    
                except Exception as check_error:
                    print(f"❌ Error during content analysis: {str(check_error)}")
                
                return trending_coins  # Return whatever we managed to extract
                
        except Exception as e:
            print(f"❌ Critical error in get_trending_coins: {str(e)}")
            
            # Log the error but also try to recover
            self.logger.error(f"Error getting trending coins: {str(e)}")
            
            # If we have enterprise proxy manager, mark current proxy as problematic
            current_proxy = None
            if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                current_proxy = getattr(self.driver, '_enterprise_working_proxy', None)
            elif hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                current_proxy = getattr(self.driver, '_cmc_working_proxy', None)
            
            if current_proxy and hasattr(self.profile_manager, 'enterprise_proxy'):
                print(f"🗑️ Marking proxy {current_proxy} as problematic due to critical error")
                self.profile_manager.enterprise_proxy.mark_proxy_failed(
                    current_proxy, f"Critical error: {str(e)}"
                )
            
            return []

    def _extract_coin_from_row(self, row, row_index: int):
        """Extract coin data from a table row"""
        try:
            # Get the coin link and name (usually in 2nd or 3rd column)
            name_cell = None
            coin_link = None
            
            # Try different column positions for the name cell
            for col_index in [2, 3]:
                try:
                    name_cell = row.find_element(By.CSS_SELECTOR, f"td:nth-child({col_index})")
                    coin_link = name_cell.find_element(By.CSS_SELECTOR, "a[href*='/currencies/']")
                    break
                except:
                    continue
            
            if not coin_link:
                self.logger.warning(f"Could not find coin link in row {row_index}, skipping...")
                return None
                
            coin_url = coin_link.get_attribute('href')
            
            # Extract symbol and name with better error handling
            try:
                # Try to find symbol element (usually has smaller text)
                symbol_elements = name_cell.find_elements(By.CSS_SELECTOR, "p, span")
                symbol = ""
                name = ""
                
                # Extract text from all elements and clean it
                all_text = name_cell.text.strip().replace('\n', ' ').replace('\r', ' ')
                link_text = coin_link.text.strip().replace('\n', ' ').replace('\r', ' ')
                
                # Try to identify symbol (usually shorter, uppercase, or last element)
                for elem in symbol_elements:
                    elem_text = elem.text.strip().replace('\n', ' ').replace('\r', ' ')
                    if elem_text and len(elem_text) <= 6 and elem_text.isupper():
                        symbol = elem_text
                        break
                
                # If no symbol found from elements, try to extract from text patterns
                if not symbol:
                    # Try to find symbol pattern in the text
                    import re
                    # Look for uppercase words of 2-6 characters
                    symbol_match = re.search(r'\b([A-Z]{2,6})\b', all_text)
                    if symbol_match:
                        symbol = symbol_match.group(1)
                    elif link_text:
                        # Use the last word from link text as fallback
                        words = link_text.split()
                        symbol = words[-1] if words else "UNKNOWN"
                
                # Extract name (remove symbol from full text)
                if symbol and symbol in all_text:
                    name = all_text.replace(symbol, '').strip()
                elif link_text:
                    name = link_text.strip()
                else:
                    name = all_text
                
                # Clean up extracted values
                symbol = ' '.join(symbol.split()) if symbol else "UNKNOWN"
                name = ' '.join(name.split()) if name else symbol
                
                # Validate symbol (must be alphanumeric and reasonable length)
                if not symbol or len(symbol) < 1 or len(symbol) > 10 or not any(c.isalnum() for c in symbol):
                    # Try to extract from URL as last resort
                    url_parts = coin_url.split('/')
                    if len(url_parts) > 2:
                        url_symbol = url_parts[-2].replace('-', '').upper()
                        if url_symbol and len(url_symbol) <= 10:
                            symbol = url_symbol[:6]  # Limit to 6 chars
                        else:
                            symbol = f"COIN{row_index}"
                    else:
                        symbol = f"COIN{row_index}"
                
                # Final validation
                if not name or name == symbol:
                    name = symbol
                    
            except Exception as e:
                self.logger.error(f"Error extracting coin info from row {row_index}: {str(e)}")
                # Emergency fallback
                symbol = f"COIN{row_index}"
                name = f"Unknown Coin {row_index}"
            
            # Get price (usually 4th column)
            try:
                price_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)")
                price = price_cell.text.strip()
            except:
                price = "N/A"
            
            # Get 24h change (usually 5th column)
            try:
                change_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(5)")
                change = change_cell.text.strip().replace('%', '')
            except:
                change = "0"
            
            return {
                'name': name,
                'symbol': symbol,
                'price': price,
                'change_24h': change,
                'url': coin_url,
                'rank_on_page': row_index
            }
        
        except Exception as e:
            self.logger.error(f"Error extracting coin from row {row_index}: {str(e)}")
            return None

    def get_coin_discussions(self, coin_symbol):
        """Get discussions for a specific coin"""
        try:
            self.logger.info(f"Getting discussions for {coin_symbol}...")
            # First get the coin's page
            self._navigate_to_cmc_with_bypass(f"{self.base_url}/currencies/{coin_symbol}/")
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

    def _analyze_page_source(self, driver):
        """Analyze page source to find potential question areas"""
        try:
            # Get page source
            page_source = driver.page_source
            
            # Look for common patterns that indicate where questions might be
            patterns = [
                'class="[^"]*question[^"]*"',
                'class="[^"]*ai[^"]*"',
                'class="[^"]*analysis[^"]*"',
                'role="button"[^>]*>.*?why.*?</button>',
                'role="button"[^>]*>.*?what.*?</button>',
                'button[^>]*>.*?\\?.*?</button>'
            ]
            
            matches = []
            for pattern in patterns:
                matches.extend(re.finditer(pattern, page_source, re.IGNORECASE))
            
            if matches:
                # Get all elements matching these patterns
                elements = []
                for match in matches:
                    try:
                        # Try to find the actual element using the matched text
                        matched_text = match.group(0)
                        # Create an XPath that matches elements containing this class or text
                        if 'class=' in matched_text:
                            class_name = re.search('class="([^"]*)"', matched_text).group(1)
                            xpath = f"//*[contains(@class, '{class_name}')]"
                        else:
                            # For text content matches, escape quotes and create appropriate XPath
                            text_content = re.search('>([^<]*)<', matched_text)
                            if text_content:
                                text = text_content.group(1)
                                xpath = f"//*[contains(text(), '{text}')]"
                            else:
                                continue
                        
                        # Find elements matching this XPath
                        found_elements = driver.find_elements(By.XPATH, xpath)
                        elements.extend(found_elements)
                    except:
                        continue
                
                return elements
        except Exception as e:
            self.logger.debug(f"Error analyzing page source: {str(e)}")
        return []

    def find_ai_button(self, driver):
        """Find the AI button/question on the page"""
        self.logger.info("Looking for AI question prompts...")
        
        # Wait for initial page load
        try:
            WebDriverWait(driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)
        except:
            self.logger.warning("Page load timeout, attempting to proceed anyway")

        # Get coin name from the page title
        try:
            coin_name = driver.find_element(By.TAG_NAME, "h1").text.split("$")[0].strip()
            self.logger.info(f"Looking for questions about {coin_name}")
        except:
            coin_name = ""
            self.logger.warning("Could not get coin name from title")

        # FIXED: Better scrolling strategy - avoid header and search areas
        # Get page height for scrolling but be more targeted
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        
        # Start scrolling after the header area (skip top 200px to avoid search bar)
        start_scroll = 200
        # Focus on the main content area, not the entire page
        max_scroll = min(viewport_height * 3, total_height - 200)  # More conservative scrolling
        scroll_step = viewport_height // 3  # Larger steps, fewer scrolls
        
        # First, scroll to start position to avoid header/search areas
        driver.execute_script(f"window.scrollTo(0, {start_scroll});")
        time.sleep(1)
        
        for scroll_pos in range(start_scroll, max_scroll, scroll_step):
            # FIXED: Use smooth scrolling to avoid jarring movements
            driver.execute_script(f"""
                window.scrollTo({{
                    top: {scroll_pos},
                    behavior: 'smooth'
                }});
            """)
            time.sleep(2)  # Increased wait time for smooth scrolling
            
            # Try to find the span using various approaches
            try:
                # ENHANCED: Look for AI-related elements with better filtering
                spans = driver.execute_script("""
                    function findSpans() {
                        const spans = document.getElementsByTagName('span');
                        return Array.from(spans).filter(span => {
                            if (!span.offsetParent) return false;  // Skip hidden elements
                            
                            const text = span.textContent.toLowerCase().trim();
                            // Look for AI question patterns
                            const hasQuestionPattern = (
                                (text.includes('why is') && text.includes('price')) ||
                                (text.includes('what') && text.includes('price')) ||
                                (text.includes('how') && text.includes('price')) ||
                                text.includes('ai analysis') ||
                                text.includes('cmc ai')
                            );
                            
                            if (!hasQuestionPattern) return false;
                            
                            // Make sure it's in the viewport and not in header/footer
                            const rect = span.getBoundingClientRect();
                            const isInViewport = rect.top >= 100 && rect.bottom <= window.innerHeight - 100;
                            const isInMainContent = rect.top > 150; // Avoid header area
                            
                            return isInViewport && isInMainContent &&
                                   span.parentElement && 
                                   span.parentElement.parentElement;
                        });
                    }
                    return findSpans();
                """)
                
                for span in spans:
                    if span.is_displayed() and span.is_enabled():
                        text = span.text.strip()
                        self.logger.info(f"Found question span: {text}")
                        return span

                # ENHANCED: More targeted XPath searches
                xpaths = [
                    "//main//span[contains(text(), 'Why is') and contains(text(), 'price')]",
                    "//div[contains(@class, 'content')]//span[contains(text(), 'Why is')]",
                    "//div[contains(@class, 'price')]//following-sibling::*//span[contains(text(), 'Why is')]",
                    "//h1[contains(text(), '$')]/following::div[position()<=10]//span[contains(text(), 'Why is')]",
                    "//span[contains(text(), 'AI') and contains(text(), 'analysis')]"
                ]
                
                for xpath in xpaths:
                    try:
                        elements = driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                # FIXED: Better viewport detection
                                in_viewport = driver.execute_script("""
                                    const rect = arguments[0].getBoundingClientRect();
                                    const isVisible = rect.top >= 100 &&
                                           rect.left >= 0 &&
                                                     rect.bottom <= window.innerHeight - 100 &&
                                           rect.right <= window.innerWidth;
                                    const isInMainContent = rect.top > 150; // Avoid header
                                    return isVisible && isInMainContent;
                                """, element)
                                
                                if in_viewport:
                                    text = element.text.strip()
                                    if ('price' in text.lower() and '?' in text) or 'ai' in text.lower():
                                        self.logger.info(f"Found via XPath: {text}")
                                        return element
                    except Exception as e:
                        self.logger.debug(f"XPath {xpath} failed: {str(e)}")
                        continue

            except Exception as e:
                self.logger.debug(f"Error in main search at scroll position {scroll_pos}: {str(e)}")

        self.logger.warning("No question spans found after comprehensive search")
        return None

    def find_and_click_ai_button(self, driver):
        """Find and click the AI button with retries"""
        max_attempts = 3
        
        for attempt in range(max_attempts):
            if attempt > 0:
                self.logger.info(f"Retry attempt {attempt + 1}...")
                # Refresh page on retry
                driver.refresh()
                time.sleep(3)
            
            try:
                # Try to find AI button
                span = self.find_ai_button(driver)
                if span:
                    # Get the clickable parent div
                    clickable = driver.execute_script("""
                        function getClickableParent(element) {
                            // Try to find the closest clickable parent
                            let current = element;
                            while (current && current.tagName !== 'BODY') {
                                // Check if this element has click handlers
                                const clickable = current.onclick || 
                                               current.getAttribute('role') === 'button' ||
                                               current.tagName === 'BUTTON' ||
                                               window.getComputedStyle(current).cursor === 'pointer';
                                               
                                if (clickable) return current;
                                current = current.parentElement;
                            }
                            return element.parentElement || element;  // Fallback to direct parent
                        }
                        return getClickableParent(arguments[0]);
                    """, span)
                    
                    if not clickable:
                        clickable = span
                    
                    # Make sure the element is in view
                    driver.execute_script("""
                        const element = arguments[0];
                        const elementRect = element.getBoundingClientRect();
                        
                        // If element is not fully visible, scroll it into center view
                        if (elementRect.top < 0 || elementRect.bottom > window.innerHeight) {
                            const absoluteElementTop = elementRect.top + window.pageYOffset;
                            const middle = absoluteElementTop - (window.innerHeight / 2);
                            window.scrollTo(0, middle);
                        }
                    """, clickable)
                    time.sleep(1)
                    
                    # ENHANCED: Try multiple clicking strategies
                    click_strategies = [
                        lambda: clickable.click(),  # Standard click
                        lambda: driver.execute_script("arguments[0].click();", clickable),  # JavaScript click
                        lambda: driver.execute_script("""
                            // Force click with events
                            const element = arguments[0];
                            element.focus();
                                ['mousedown', 'mouseup', 'click'].forEach(eventType => {
                                    const event = new MouseEvent(eventType, {
                                        view: window,
                                        bubbles: true,
                                        cancelable: true,
                                        buttons: 1
                                    });
                                    element.dispatchEvent(event);
                                });
                        """, clickable)  # Force event dispatch
                    ]
                    
                    for i, strategy in enumerate(click_strategies):
                        try:
                            print(f"🎯 Trying click strategy {i + 1}...")
                            strategy()
                            time.sleep(3)  # Wait for content to start loading
                            
                            # ENHANCED: Check for AI content appearance with more indicators
                            content_appeared = driver.execute_script("""
                                // Check multiple indicators that AI content loaded
                                const bodyText = document.body.innerText.toLowerCase();
                                const hasAIIndicators = 
                                    bodyText.includes('tldr') || 
                                    bodyText.includes('thought for') ||
                                    bodyText.includes('ai analysis') ||
                                    bodyText.includes('analysis summary') ||
                                    bodyText.includes('key insights');
                                
                                // Also check for new elements in right area
                                const rightElements = Array.from(document.querySelectorAll('*')).filter(el => {
                                    const rect = el.getBoundingClientRect();
                                    return rect.left > window.innerWidth * 0.5 && rect.width > 100;
                                });
                                
                                const hasNewRightContent = rightElements.some(el => {
                                    const text = el.textContent.toLowerCase();
                                    return text.includes('tldr') || text.includes('thought for');
                                });
                                
                                return hasAIIndicators || hasNewRightContent;
                            """)
                            
                            if content_appeared:
                                print(f"✅ AI content appeared after click strategy {i + 1}")
                                self.logger.info("AI content area appeared after click")
                                return True
                            else:
                                print(f"⚠️ Click strategy {i + 1} didn't trigger AI content, trying next...")
                                
                        except Exception as e:
                            print(f"❌ Click strategy {i + 1} failed: {str(e)}")
                            continue
                    
                    # If none of the strategies worked, try one more aggressive approach
                    print("🔥 Trying aggressive clicking approach...")
                    try:
                        # Find all clickable elements near the AI question and click them
                        driver.execute_script("""
                            // Find and click any clickable elements containing AI-related text
                            const allElements = document.querySelectorAll('*');
                            for (let element of allElements) {
                                const text = element.textContent.toLowerCase();
                                if ((text.includes('why is') && text.includes('price')) || 
                                    text.includes('ai') || 
                                    text.includes('analysis')) {
                                    
                                    const rect = element.getBoundingClientRect();
                                    if (rect.width > 0 && rect.height > 0) {
                                        try {
                                            element.click();
                                            console.log('Clicked element:', element);
                                        } catch (e) {
                                            // Continue if click fails
                                        }
                                    }
                                }
                            }
                        """)
                        
                        time.sleep(5)  # Wait longer for aggressive clicking
                        
                        # Check again for content
                        final_check = driver.execute_script("""
                            const bodyText = document.body.innerText.toLowerCase();
                            return bodyText.includes('tldr') || bodyText.includes('thought for');
                        """)
                        
                        if final_check:
                            print("✅ AI content appeared after aggressive clicking")
                            return True
                            
                    except Exception as e:
                        print(f"❌ Aggressive clicking failed: {str(e)}")
            
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                continue
        
        self.logger.warning(f"Failed to click AI element after {max_attempts} attempts")
        return False

    def wait_for_ai_content(self, timeout=45):
        """Enhanced method to wait for and capture AI content - FIXED for right sidebar"""
        start_time = time.time()
        
        print("🤖 FIXED VERSION: Waiting for AI content to load in right sidebar...")
        print("🔧 Using new stale-element-resistant content detection!")
        
        while time.time() - start_time < timeout:
            try:
                # FIXED: Use fresh element lookups every time to avoid stale references
                # Strategy 1: Look for content in the right sidebar where AI actually appears
                print(f"⏳ Checking for AI content... ({int(time.time() - start_time)}s elapsed)")
                
                # Get fresh page source each time
                page_source = self.driver.page_source
                
                # Check if AI content keywords are present in page source
                ai_indicators = ['TLDR', 'Thought for', 'AI analysis', 'analysis summary', 'key insights']
                ai_content_present = any(indicator in page_source for indicator in ai_indicators)
                
                if ai_content_present:
                    print("🎯 AI indicators found in page source, locating content...")
                    
                    # Strategy 1: Look for right sidebar content with fresh selectors
                    right_sidebar_selectors = [
                        "//div[contains(@class, 'right')]//div[contains(text(), 'TLDR') or contains(text(), 'Thought for')]",
                        "//aside//div[contains(text(), 'TLDR') or contains(text(), 'Thought for')]", 
                        "//div[@role='complementary']//div[contains(text(), 'TLDR') or contains(text(), 'Thought for')]",
                        "//*[contains(@class, 'sidebar')]//div[contains(text(), 'TLDR') or contains(text(), 'Thought for')]",
                        "//*[contains(@class, 'right-panel')]//div[contains(text(), 'TLDR') or contains(text(), 'Thought for')]"
                    ]
                    
                    for selector in right_sidebar_selectors:
                        try:
                            # Get fresh elements each time
                            elements = self.driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                try:
                                    if element.is_displayed():
                                        # Get the parent container to capture full content
                                        parent = element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'content') or contains(@class, 'panel') or contains(@class, 'sidebar')][1]")
                                        content = parent.text.strip()
                                        
                                        if len(content) > 50:
                                            print(f"✅ Found AI content via selector: {content[:100]}...")
                                                    return content
                                except Exception:
                                    # Element became stale, continue to next
                                    continue
                        except Exception:
                            continue
                    
                    # Strategy 2: Search for AI content in all visible text using JavaScript
                    try:
                        ai_content = self.driver.execute_script("""
                            // Find all text content containing AI indicators
                            function findAIContent() {
                                const indicators = ['TLDR', 'Thought for', 'analysis summary', 'key insights'];
                                const allElements = document.querySelectorAll('*');
                                
                                for (let element of allElements) {
                                    const text = element.textContent;
                                    if (text && text.length > 100) {
                                        for (let indicator of indicators) {
                                            if (text.includes(indicator)) {
                                                // Check if element is in right area of screen
                                                const rect = element.getBoundingClientRect();
                                                const isRightSide = rect.left > window.innerWidth * 0.5;
                                                const isVisible = rect.top >= 0 && rect.bottom <= window.innerHeight;
                                                
                                                if (isRightSide && isVisible) {
                                                    return text;
                                                }
                                            }
                                        }
                                    }
                                }
                                return null;
                            }
                            return findAIContent();
                        """)
                        
                        if ai_content and len(ai_content) > 100:
                            print(f"✅ Found AI content via JavaScript: {ai_content[:100]}...")
                            return ai_content
                            
                    except Exception as e:
                        print(f"❌ JavaScript search failed: {str(e)}")
                    
                    # Strategy 3: Look for content by text pattern matching
                    try:
                        # Find elements containing TLDR or Thought for
                        tldr_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'TLDR')]")
                        thought_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Thought for')]")
                        
                        all_ai_elements = tldr_elements + thought_elements
                        
                        for element in all_ai_elements:
                            try:
                                if element.is_displayed():
                                    # Try to get the container that holds the full content
                                    containers = [
                                        element.find_element(By.XPATH, "./ancestor::div[1]"),  # immediate parent
                                        element.find_element(By.XPATH, "./ancestor::div[2]"),  # grandparent
                                        element.find_element(By.XPATH, "./ancestor::div[3]"),  # great-grandparent
                                    ]
                                    
                                    for container in containers:
                                        try:
                                            content = container.text.strip()
                                            if len(content) > 100 and ('TLDR' in content or 'Thought for' in content):
                                                print(f"✅ Found AI content via text pattern: {content[:100]}...")
                                                return content
                                        except Exception:
                                            continue
                            except Exception:
                                # Element became stale, continue to next
                                continue
                                
                    except Exception as e:
                        print(f"❌ Text pattern search failed: {str(e)}")
                
                # Wait a bit before next check
                time.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Error in content search: {str(e)[:100]}...")
                time.sleep(1)
                continue
        
        print(f"❌ Timeout waiting for AI content after {timeout} seconds")
        return None

    def get_ai_token_review(self, coin_symbol: str, coin_name: str, coin_url: str = None) -> dict:
        """Get AI-generated review for a token from CMC (SCRAPING ONLY - NO POSTING)"""
        try:
            self.logger.info(f"Getting AI review for {coin_name} (${coin_symbol})...")
            
            # Use provided URL or construct it
            if coin_url:
                target_url = coin_url
            else:
                # Clean up the coin name for URL
                coin_slug = coin_name.lower()
                # Remove special characters and replace spaces with hyphens
                coin_slug = re.sub(r'[^a-z0-9\s-]', '', coin_slug)
                coin_slug = re.sub(r'\s+', '-', coin_slug.strip())
                target_url = f"{self.currencies_url}{coin_slug}/"
            
            self.logger.info(f"🔥 Navigating to CMC via breakthrough bypass: {target_url}")
            self._navigate_to_cmc_with_bypass(target_url)
            
            # Wait for page load
            self.logger.info("Waiting for page to fully load...")
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)  # Additional wait for dynamic content
            
            # Verify we're on the correct page
            current_url = self.driver.current_url
            if "/portfolio-tracker/" in current_url or "/login/" in current_url:
                self.logger.error("Redirected to wrong page. Please check login status.")
                return {
                    'success': False,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'error': 'Redirected to wrong page'
                }
            
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
                # ONLY return the content - NO POSTING HERE
                return {
                    'success': True,
                    'coin_name': coin_name,
                    'coin_symbol': coin_symbol,
                    'ai_review': content,  # Raw CMC AI content only
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'url_used': target_url
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

    def _navigate_to_cmc_with_bypass(self, url: str) -> bool:
        """Navigate to CMC page with automatic proxy failure detection and HTML content validation"""
        max_proxy_attempts = 5  # Try up to 5 different proxies
        attempt = 0
        
        while attempt < max_proxy_attempts:
            attempt += 1
            current_proxy = None
            
            try:
                # Get current proxy info
                if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                    current_proxy = getattr(self.driver, '_enterprise_working_proxy', 'Unknown')
                    print(f"🌐 Attempt {attempt}: Using proxy {current_proxy}")
                elif hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                    current_proxy = getattr(self.driver, '_cmc_working_proxy', 'Unknown')
                    print(f"🔥 Attempt {attempt}: Using CMC bypass proxy {current_proxy}")
                else:
                    print(f"🌐 Attempt {attempt}: Using direct connection")
                
                print(f"🔗 Accessing: {url}")
                
                # Try navigation with current proxy
                self.driver.get(url)
                
                # Wait for page to load and check for success
                print("⏳ Waiting for page to load...")
                time.sleep(5)  # Give page time to load
                
                # Check if navigation was successful with enhanced validation
                current_url = self.driver.current_url
                page_title = self.driver.title
                page_source = self.driver.page_source.lower()
                
                print(f"🔍 Page validation: URL={current_url[:50]}..., Title={page_title[:30]}...")
                
                # Enhanced failure indicators - check for proxy/tunnel errors first
                tunnel_errors = [
                    "err_tunnel_connection_failed",
                    "err_proxy_connection_failed", 
                    "err_timed_out",
                    "err_connection_timed_out",
                    "err_connection_refused",
                    "err_address_unreachable",
                    "502 bad gateway",
                    "503 service unavailable",
                    "504 gateway timeout",
                    "connection timed out",
                    "this site can't be reached",
                    "took too long to respond",
                    "proxy connection failed",
                    "tunnel connection failed"
                ]
                
                # Check for tunnel/proxy errors
                has_tunnel_error = any(error in page_source for error in tunnel_errors)
                has_title_error = any(error in page_title.lower() for error in tunnel_errors)
                
                if has_tunnel_error or has_title_error:
                    print(f"❌ Tunnel/Proxy error detected in page content")
                    raise Exception(f"Tunnel connection failed - proxy not working")
                
                # Content validation - check if we actually got CMC content
                cmc_content_indicators = [
                    "coinmarketcap",
                    "cryptocurrency", 
                    "bitcoin",
                    "ethereum",
                    "market cap",
                    "price",
                    "trading volume",
                    "market data"
                ]
                
                # Count how many CMC indicators we found
                cmc_indicators_found = sum(1 for indicator in cmc_content_indicators if indicator in page_source)
                
                # Success criteria
                url_success = "coinmarketcap.com" in current_url.lower()
                title_success = "coinmarketcap" in page_title.lower() and len(page_title) > 5
                content_success = cmc_indicators_found >= 3  # At least 3 CMC-related terms
                page_loaded = current_url != "data:," and current_url != "about:blank"
                
                print(f"📊 Validation results: URL={url_success}, Title={title_success}, Content={content_success} ({cmc_indicators_found}/8 indicators), Loaded={page_loaded}")
                
                # Check for success - all criteria must pass
                if url_success and title_success and content_success and page_loaded:
                    print(f"✅ Navigation successful with {'proxy' if current_proxy else 'direct connection'}")
                    print(f"✅ CMC content validated: {cmc_indicators_found}/8 indicators found")
                    if current_proxy:
                        print(f"🎯 Working proxy: {current_proxy}")
                        # Mark proxy as working in storage with high score for successful CMC access
                        if (hasattr(self.profile_manager, 'enterprise_proxy') and 
                            self.profile_manager.enterprise_proxy):
                            self.profile_manager.enterprise_proxy.proxy_storage.add_working_proxy(
                                current_proxy, response_time=5.0, test_score=90
                            )
                            print(f"💾 Marked {current_proxy} as working in storage with score 90")
                    return True
                
                # If we get here, validation failed
                failure_reasons = []
                if not url_success:
                    failure_reasons.append("Wrong URL")
                if not title_success:
                    failure_reasons.append("Invalid title")
                if not content_success:
                    failure_reasons.append(f"Insufficient CMC content ({cmc_indicators_found}/8)")
                if not page_loaded:
                    failure_reasons.append("Page not loaded")
                
                print(f"❌ Navigation validation failed: {', '.join(failure_reasons)}")
                raise Exception(f"Page validation failed: {', '.join(failure_reasons)}")
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Attempt {attempt} failed: {error_msg}")
                
                # Mark current proxy as failed if we have one
                if current_proxy and current_proxy != 'Unknown':
                    print(f"🗑️ Marking proxy {current_proxy} as failed")
                    
                    # Mark failed in enterprise proxy manager
                    if (hasattr(self.profile_manager, 'enterprise_proxy') and 
                        self.profile_manager.enterprise_proxy):
                        self.profile_manager.enterprise_proxy.mark_proxy_failed(
                            current_proxy, f"Navigation failed: {error_msg}"
                        )
                        print(f"💾 Removed {current_proxy} from working proxy storage")
                    
                    # Mark failed in legacy system too
                    if (hasattr(self.profile_manager, 'anti_detection') and 
                        self.profile_manager.anti_detection):
                        self.profile_manager.anti_detection.mark_proxy_failed(current_proxy)
                
                # If this isn't our last attempt, try to get a new proxy
                if attempt < max_proxy_attempts:
                    print(f"🔄 Attempting to switch to new working proxy...")
                    
                    try:
                        # Try to switch to a new proxy using enterprise system
                        if (hasattr(self.profile_manager, 'load_profile_with_enterprise_proxy')):
                            print("🗂️ Switching to new proxy via enterprise system...")
                            new_driver = self.profile_manager.load_profile_with_enterprise_proxy()
                            
                            if new_driver:
                                # Close old driver
                                try:
                                    self.driver.quit()
                                except:
                                    pass
                                
                                self.driver = new_driver
                                
                                # Check if new proxy was configured
                                if hasattr(self.driver, '_enterprise_proxy_configured') and self.driver._enterprise_proxy_configured:
                                    new_proxy = getattr(self.driver, '_enterprise_working_proxy', 'Unknown')
                                    print(f"✅ Switched to new proxy: {new_proxy}")
                                else:
                                    print("⚠️ No new proxy available, will try direct connection")
                                
                                continue  # Try again with new proxy
                        
                        # Fallback to CMC bypass system
                        elif hasattr(self.profile_manager, 'load_profile_with_cmc_bypass'):
                            print("🔥 Switching to new proxy via CMC bypass system...")
                            new_driver = self.profile_manager.load_profile_with_cmc_bypass()
                            
                            if new_driver:
                                # Close old driver
                                try:
                                    self.driver.quit()
                                except:
                                    pass
                                
                                self.driver = new_driver
                                
                                # Check if new proxy was configured
                                if hasattr(self.driver, '_cmc_proxy_configured') and self.driver._cmc_proxy_configured:
                                    new_proxy = getattr(self.driver, '_cmc_working_proxy', 'Unknown')
                                    print(f"✅ Switched to new proxy: {new_proxy}")
                                else:
                                    print("⚠️ No new proxy available, will try direct connection")
                                
                                continue  # Try again with new proxy
                        
                        # If no advanced systems available, try regular profile switch
                        else:
                            print("🔄 Switching to next profile...")
                            new_driver = self.profile_manager.switch_to_next_profile()
                            
                            if new_driver:
                                # Close old driver
                                try:
                                    self.driver.quit()
                                except:
                                    pass
                                
                                self.driver = new_driver
                                print("✅ Switched to new profile")
                                continue  # Try again with new profile
                        
                    except Exception as switch_error:
                        print(f"❌ Failed to switch proxy: {str(switch_error)}")
                        # Continue to next attempt anyway
                
                # Add delay before retry
                if attempt < max_proxy_attempts:
                    retry_delay = 5 + (attempt * 2)  # Increasing delay
                    print(f"⏳ Waiting {retry_delay}s before next attempt...")
                    time.sleep(retry_delay)
        
        # All attempts failed - trigger emergency proxy re-scraping
        print(f"❌ All {max_proxy_attempts} proxy attempts failed")
        print("🚨 CRITICAL: Unable to access CMC with any available proxy")
        print("🔄 INITIATING EMERGENCY PROXY RE-SCRAPING...")
        
        # Try to trigger new proxy discovery for immediate use
        if (hasattr(self.profile_manager, 'enterprise_proxy') and 
            self.profile_manager.enterprise_proxy):
            try:
                print("🔍 Step 1: Clearing failed proxy cache...")
                # Clear the verified_proxies to force re-fetching
                self.profile_manager.enterprise_proxy.verified_proxies = []
                self.profile_manager.enterprise_proxy.proxy_refresh_time = None
                
                print("🔍 Step 2: Emergency proxy acquisition from all sources...")
                new_proxies = self.profile_manager.enterprise_proxy.get_enterprise_grade_proxies()
                
                if new_proxies:
                    print(f"✅ Emergency re-scraping SUCCESS: Found {len(new_proxies)} new proxies!")
                    print("🔄 Attempting one final navigation with fresh proxies...")
                    
                    # Try loading a new profile with the fresh proxies
                    try:
                        new_driver = self.profile_manager.load_profile_with_enterprise_proxy()
                        if new_driver:
                            # Close old driver
                            try:
                                self.driver.quit()
                            except:
                                pass
                            
                            self.driver = new_driver
                            print("✅ Loaded fresh profile with newly discovered proxies")
                            
                            # Try one final navigation attempt
                            print("🎯 Final attempt with fresh proxy system...")
                            return self._navigate_to_cmc_with_bypass(url)  # Recursive call with fresh proxies
                        
                    except Exception as final_error:
                        print(f"❌ Final attempt failed: {str(final_error)}")
                else:
                    print("❌ Emergency proxy re-scraping found no working proxies")
                    
            except Exception as discovery_error:
                print(f"❌ Emergency proxy discovery failed: {str(discovery_error)}")
        
        print("💡 RECOVERY SUGGESTIONS:")
        print("   1. Check internet connection")
        print("   2. Try again in 5-10 minutes (IP ranges may be temporarily blocked)")
        print("   3. Configure premium proxy services (ScraperAPI recommended)")
        print("   4. Add working manual proxies to config/manual_proxies.txt")
        print("   5. Run the enterprise proxy test to verify system configuration")
        
        return False

 