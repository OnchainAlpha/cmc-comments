import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from autocrypto_social_bot.main import CryptoAIAnalyzer
from autocrypto_social_bot.config.settings import DEEPSEEK_API_KEY
from autocrypto_social_bot.services.message_formatter import MessageFormatter
from autocrypto_social_bot.services.viral_hooks import ViralHooks
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set the API key in environment
os.environ['DEEPSEEK_API_KEY'] = DEEPSEEK_API_KEY

class TestAnalyzer(CryptoAIAnalyzer):
    """Test version of CryptoAIAnalyzer that bypasses interactive prompts"""
    def _get_promotion_config(self):
        """Override to skip interactive prompts"""
        return self.promotion_config
    
    def __init__(self):
        """Override to skip browser initialization"""
        self.logger = logging.getLogger(__name__)
        
        # Initialize DeepSeek client
        self.deepseek = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        # Initialize services
        self.message_formatter = MessageFormatter()
        self.viral_hooks = ViralHooks()
        
        # Initialize empty attributes
        self.promotion_config = None
        self.profile_manager = None
        self.driver = None
        self.cmc_scraper = None

def test_enhanced_content():
    """Test the enhanced content generation with different promotion types"""
    
    # Sample CMC AI review for testing
    sample_review = """
    Bitcoin (BTC) shows strong fundamentals with increasing network activity and growing institutional adoption. 
    Technical indicators suggest a bullish trend forming, with the 50-day moving average crossing above the 200-day MA. 
    Recent developments in Lightning Network scaling and institutional products have strengthened Bitcoin's position as a digital store of value.
    """
    
    # Test cases for different promotion types
    test_cases = [
        {
            'type': 'market_making',
            'params': {
                'firm_name': 'Wintermute Trading'
            }
        },
        {
            'type': 'token_launch',
            'params': {
                'platform': 'Binance Launchpad',
                'launch_date': 'July 1st, 2025'
            }
        },
        {
            'type': 'trading_group',
            'params': {
                'group_name': 'Alpha Signals',
                'join_link': 't.me/alphasignals'
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing {case['type']} promotion")
        print('='*60)
        
        # Create analyzer with pre-configured promotion type
        analyzer = TestAnalyzer()
        analyzer.promotion_config = case
        
        try:
            # Generate enhanced content
            result = analyzer._enhance_ai_review(sample_review, "BTC")
            
            if result['messages']:
                print("\nGenerated variations:")
                for i, msg in enumerate(result['messages'], 1):
                    print(f"\nVariation {i}:")
                    print(msg)
            else:
                print("\nError: No content generated")
        except Exception as e:
            print(f"\nError: {str(e)}")
        
        print("\nPress Enter to continue to next test case...")
        input()

if __name__ == "__main__":
    test_enhanced_content() 