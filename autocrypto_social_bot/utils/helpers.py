import os
import time
import random
import logging
import sys
from datetime import datetime
from typing import Optional
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def setup_logging():
    """Setup logging configuration"""
    # Force UTF-8 encoding for logging
    if sys.stdout.encoding != 'utf-8':
        if sys.platform.startswith('win'):
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Setup logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Setup file handler
    file_handler = logging.FileHandler(
        os.path.join(log_dir, 'bot.log'),
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Setup console handler with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def random_delay(min_seconds=2, max_seconds=5):
    """Add a random delay between actions"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay

def wait_for_element(driver, by: By, value: str, timeout: int = 10, condition: str = "presence") -> Optional[object]:
    """
    Wait for an element to be present/visible/clickable on the page
    
    Args:
        driver: Selenium WebDriver instance
        by: Type of selector (e.g., By.ID, By.CSS_SELECTOR)
        value: The selector value
        timeout: How long to wait before timing out
        condition: What to wait for - "presence", "visibility", or "clickable"
    
    Returns:
        The element if found, None if timed out
    """
    try:
        wait = WebDriverWait(driver, timeout)
        
        if condition == "presence":
            element = wait.until(
                EC.presence_of_element_located((by, value))
            )
        elif condition == "visibility":
            element = wait.until(
                EC.visibility_of_element_located((by, value))
            )
        elif condition == "clickable":
            element = wait.until(
                EC.element_to_be_clickable((by, value))
            )
        else:
            raise ValueError(f"Unknown wait condition: {condition}")
            
        return element
        
    except TimeoutException:
        return None