import sys
import os
import time
import schedule
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import CryptoAnalyzer
from scripts.post_from_csv import post_pending_analyses

# Set up logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'monitor.log')

logger = logging.getLogger('monitor')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def run_full_cycle():
    """Run both analysis and posting"""
    try:
        logger.info("Starting full cycle...")
        print(f"\n{'='*50}")
        print(f"Starting full cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        # First generate analysis
        analyzer = CryptoAnalyzer()
        logger.info("Created CryptoAnalyzer instance")
        
        try:
            analyzer.run()
            logger.info("Completed analysis run")
        except Exception as e:
            logger.error(f"Error in analyzer.run(): {str(e)}")
            raise e
        
        # Then post pending analyses
        time.sleep(10)  # Short pause between analysis and posting
        try:
            post_pending_analyses()
            logger.info("Completed posting run")
        except Exception as e:
            logger.error(f"Error in post_pending_analyses(): {str(e)}")
            raise e
        
        logger.info("Full cycle completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error in full cycle: {str(e)}")
        return False

def run_monitor():
    """Main monitoring function"""
    try:
        # Schedule full cycle every 4 hours
        schedule.every(4).hours.do(run_full_cycle)
        
        # Run first cycle immediately
        logger.info("Starting initial cycle...")
        run_full_cycle()
        
        # Main loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check schedule every minute
            except Exception as e:
                logger.error(f"Error in schedule loop: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
                continue
            
    except Exception as e:
        logger.error(f"Fatal error in monitor: {str(e)}")
        raise e

if __name__ == "__main__":
    try:
        print("\nStarting continuous monitoring...")
        print("Press Ctrl+C to stop")
        run_monitor()
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    except Exception as e:
        print(f"\nFatal error: {str(e)}") 