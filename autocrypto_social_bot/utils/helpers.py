import os
import time
import random
import logging
from datetime import datetime

def setup_logging(level=logging.INFO):
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'bot_{timestamp}.log')
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def random_delay(min_seconds=1, max_seconds=3):
    """Add a random delay between actions"""
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)
    return delay 