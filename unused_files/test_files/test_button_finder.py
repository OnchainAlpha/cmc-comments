from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

def analyze_buttons():
    # Setup Chrome
    options = Options()
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Go to BTC page
        driver.get('https://coinmarketcap.com/currencies/bitcoin/')
        time.sleep(5)  # Wait for page load
        
        # Get all button info
        button_info = driver.execute_script("""
            function getElementInfo(element) {
                const rect = element.getBoundingClientRect();
                return {
                    tagName: element.tagName,
                    className: element.className,
                    id: element.id,
                    text: element.textContent.trim(),
                    attributes: Array.from(element.attributes).map(attr => ({
                        name: attr.name,
                        value: attr.value
                    })),
                    position: {
                        top: rect.top,
                        left: rect.left,
                        bottom: rect.bottom,
                        right: rect.right
                    },
                    parentInfo: element.parentElement ? {
                        tagName: element.parentElement.tagName,
                        className: element.parentElement.className,
                        id: element.parentElement.id
                    } : null,
                    html: element.outerHTML
                };
            }
            
            // Get all buttons
            const buttons = Array.from(document.getElementsByTagName('button'));
            
            // Filter and map to detailed info
            return buttons
                .filter(btn => {
                    const text = btn.textContent.toLowerCase();
                    return text.includes('?') && 
                           (text.includes('price') || text.includes('why') || text.includes('what'));
                })
                .map(getElementInfo);
        """)
        
        # Save to file
        with open('button_analysis.json', 'w') as f:
            json.dump(button_info, f, indent=2)
            
        print("\nFound buttons:")
        for btn in button_info:
            print(f"\nText: {btn['text']}")
            print(f"Class: {btn['className']}")
            print(f"Parent: {btn['parentInfo']}")
            print(f"Position: {btn['position']}")
            print(f"HTML: {btn['html']}\n")
            print("-" * 80)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    analyze_buttons() 