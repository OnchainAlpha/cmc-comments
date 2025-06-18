import undetected_chromedriver as uc

print("Testing Chrome initialization...")

try:
    # Test 1: Basic initialization without any options
    print("\nTest 1: Basic initialization")
    driver = uc.Chrome()
    print("Success! Chrome opened.")
    driver.quit()
except Exception as e:
    print(f"Test 1 failed: {e}")

try:
    # Test 2: With options but no profile
    print("\nTest 2: With options")
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    driver = uc.Chrome(options=options)
    print("Success! Chrome opened with options.")
    driver.quit()
except Exception as e:
    print(f"Test 2 failed: {e}")

try:
    # Test 3: With headless=False explicitly
    print("\nTest 3: With headless=False")
    driver = uc.Chrome(headless=False)
    print("Success! Chrome opened with headless=False.")
    driver.quit()
except Exception as e:
    print(f"Test 3 failed: {e}")

print("\nDone with tests.") 