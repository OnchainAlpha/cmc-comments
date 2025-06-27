import logging
from pathlib import Path
from openai import OpenAI

from autocrypto_social_bot.config.settings import DEEPSEEK_API_KEY
from autocrypto_social_bot.services.message_formatter import MessageFormatter
from autocrypto_social_bot.services.viral_hooks import ViralHooks
from autocrypto_social_bot.utils.helpers import setup_logging

def test_deepseek_connection():
    """Test DeepSeek API connection and basic completion"""
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        prompt = "Write a brief, engaging crypto market update about Bitcoin's recent performance"
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional crypto market analyst."},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        
        print("\n=== DeepSeek API Test ===")
        print("Response:", response.choices[0].message.content)
        return True
    except Exception as e:
        print(f"DeepSeek API Error: {str(e)}")
        return False

def test_message_formatting():
    """Test message formatting with viral hooks"""
    formatter = MessageFormatter()
    hooks_gen = ViralHooks()
    
    # Test market making promotion
    promotion_type = "market_making"
    ai_analysis = "TestCoin has surged 25% to $1,500 in the past 24 hours, showing strong momentum with increasing volume. The token's recent partnership with major exchanges and growing institutional interest suggest a potential long-term uptrend."
    
    params = {
        "token": "TestCoin",
        "firm_name": "AlphaTrade Capital",
        "market_sentiment": "bull",
        "time_of_day": "morning",
        "region": "global"
    }
    
    print("\n=== Message Formatting Test ===")
    
    # Generate hooks and pick one
    hooks = hooks_gen.generate_hooks(
        token=params["token"],
        analysis=ai_analysis,
        market_sentiment=params["market_sentiment"]
    )
    hook = hooks["question"]  # Use the question hook for testing
    print("Generated Hook:", hook)
    
    # Get promotion prompt and format message
    prompt = formatter.get_promotion_prompt(promotion_type, ai_analysis, params)
    message = formatter.format_final_message(prompt, params["token"])
    print("\nFormatted Message:", message)
    
    return bool(hook and message)

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("Starting Integration Tests...")
    
    # Test DeepSeek API
    if test_deepseek_connection():
        logger.info("✅ DeepSeek API test passed")
    else:
        logger.error("❌ DeepSeek API test failed")
    
    # Test Message Formatting
    if test_message_formatting():
        logger.info("✅ Message formatting test passed")
    else:
        logger.error("❌ Message formatting test failed")

if __name__ == "__main__":
    main() 