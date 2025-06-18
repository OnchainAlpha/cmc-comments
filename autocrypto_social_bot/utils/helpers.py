import logging
import time
import random

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def random_delay(min_seconds=2, max_seconds=5):
    """Add a random delay between actions"""
    time.sleep(random.uniform(min_seconds, max_seconds)) 