import undetected_chromedriver as uc
import os
import time
import sys

print("Testing undetected-chromedriver initialization...\n")

# Check version
print(f"undetected-chromedriver version: {uc.__version__}")
print(f"Python version: {sys.version}")

# Test 1: Basic initialization without profile
print("\n" + "="*50)
print("Test 1: Basic initialization without profile")
print("="*50)
try:
    driver = uc.Chrome()
    print("✓ Success! Chrome opened without profile.")
    time.sleep(2)
    print(f"Browser version: {driver.capabilities.get('browserVersion', 'Unknown')}")
    print(f"Chrome driver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'Unknown')}")
    driver.quit()
    print("✓ Chrome closed successfully.")
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)}")

# Test 2: Initialize with options but no profile
print("\n" + "="*50)
print("Test 2: Initialize with options")
print("="*50)
try:
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options)
    print("✓ Success! Chrome opened with options.")
    time.sleep(2)
    driver.quit()
    print("✓ Chrome closed successfully.")
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)}")

# Test 3: Test with user profile
print("\n" + "="*50)
print("Test 3: Initialize with user profile")
print("="*50)
profile_path = os.path.expanduser("~/chrome_profiles/cmc")
if os.path.exists(profile_path):
    print(f"Profile path exists: {profile_path}")
    try:
        driver = uc.Chrome(user_data_dir=profile_path)
        print("✓ Success! Chrome opened with profile.")
        time.sleep(2)
        driver.quit()
        print("✓ Chrome closed successfully.")
    except Exception as e:
        print(f"✗ Failed: {type(e).__name__}: {str(e)}")
else:
    print(f"Profile path does not exist: {profile_path}")
    print("Please run import_profile.py first.")

# Test 4: Test with headless=False explicitly
print("\n" + "="*50)
print("Test 4: Initialize with headless=False")
print("="*50)
try:
    driver = uc.Chrome(headless=False)
    print("✓ Success! Chrome opened with headless=False.")
    time.sleep(2)
    driver.quit()
    print("✓ Chrome closed successfully.")
except Exception as e:
    print(f"✗ Failed: {type(e).__name__}: {str(e)}")

print("\n" + "="*50)
print("All tests completed.")
print("="*50) 