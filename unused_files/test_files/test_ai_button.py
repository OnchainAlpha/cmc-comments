from autocrypto_social_bot.scrapers.cmc_scraper import CMCScraper
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def test_ai_button():
    # Setup Chrome options
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-notifications')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Create driver
    driver = webdriver.Chrome(options=options)
    
    try:
        # Create scraper
        scraper = CMCScraper(driver)
        
        # Test with different coins
        coins = [
            ('BTC', 'Bitcoin', 'https://coinmarketcap.com/currencies/bitcoin/'),
            ('ETH', 'Ethereum', 'https://coinmarketcap.com/currencies/ethereum/'),
            ('BNB', 'BNB', 'https://coinmarketcap.com/currencies/bnb/')
        ]
        
        for symbol, name, url in coins:
            print(f"\nTesting with {name} ({symbol})...")
            result = scraper.get_ai_token_review(symbol, name, url)
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    test_ai_button() 