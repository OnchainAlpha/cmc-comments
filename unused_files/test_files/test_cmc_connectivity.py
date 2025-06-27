#!/usr/bin/env python3
"""
CMC Connectivity Test Script
Tests CoinMarketCap accessibility with current proxy configuration
"""

import sys
import os
import time
import requests
import json
from pathlib import Path

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_connection():
    """Test direct connection to CMC without proxy"""
    print("\n🧪 TESTING DIRECT CONNECTION TO CMC")
    print("="*50)
    
    try:
        # Test health endpoint
        print("Testing CMC health endpoint...")
        health_response = requests.get('https://coinmarketcap.com/api/health-check/', timeout=10)
        if health_response.status_code == 200:
            print("✅ Health endpoint: OK")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
            return False
        
        # Test main page
        print("Testing CMC main page...")
        main_response = requests.get('https://coinmarketcap.com/', timeout=15)
        if main_response.status_code == 200 and 'coinmarketcap' in main_response.text.lower():
            print("✅ Main page: Accessible")
        else:
            print(f"❌ Main page failed: {main_response.status_code}")
            return False
        
        # Test trending page
        print("Testing CMC trending page...")
        trending_response = requests.get('https://coinmarketcap.com/trending-cryptocurrencies/', timeout=15)
        if trending_response.status_code == 200:
            print("✅ Trending page: Accessible")
            
            # Check content
            page_content = trending_response.text.lower()
            expected_content = ['trending', 'cryptocurrency', 'bitcoin']
            found_content = sum(1 for content in expected_content if content in page_content)
            print(f"✅ Content verification: {found_content}/{len(expected_content)} indicators found")
            
            return True
        else:
            print(f"❌ Trending page failed: {trending_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Direct connection failed: {str(e)}")
        return False

def test_proxy_connection(proxy):
    """Test connection to CMC through a specific proxy"""
    print(f"\n🧪 TESTING PROXY: {proxy}")
    print("="*50)
    
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Test basic connectivity
        print("Testing basic proxy connectivity...")
        ip_response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if ip_response.status_code == 200:
            ip_data = ip_response.json()
            proxy_ip = ip_data.get('origin', 'Unknown')
            print(f"✅ Proxy IP: {proxy_ip}")
        else:
            print(f"❌ Basic connectivity failed: {ip_response.status_code}")
            return False
        
        # Test CMC health endpoint
        print("Testing CMC health endpoint through proxy...")
        health_response = requests.get('https://coinmarketcap.com/api/health-check/', 
                                     proxies=proxies, headers=headers, timeout=15)
        if health_response.status_code == 200:
            print("✅ CMC health endpoint: OK")
        else:
            print(f"❌ CMC health endpoint failed: {health_response.status_code}")
            return False
        
        # Test CMC main page
        print("Testing CMC main page through proxy...")
        main_response = requests.get('https://coinmarketcap.com/', 
                                   proxies=proxies, headers=headers, timeout=15)
        if main_response.status_code == 200 and 'coinmarketcap' in main_response.text.lower():
            print("✅ CMC main page: Accessible")
        else:
            print(f"❌ CMC main page failed: {main_response.status_code}")
            return False
        
        # Test trending page
        print("Testing CMC trending page through proxy...")
        trending_response = requests.get('https://coinmarketcap.com/trending-cryptocurrencies/', 
                                       proxies=proxies, headers=headers, timeout=15)
        if trending_response.status_code == 200:
            print("✅ CMC trending page: Accessible")
            
            # Check content
            page_content = trending_response.text.lower()
            expected_content = ['trending', 'cryptocurrency', 'bitcoin']
            found_content = sum(1 for content in expected_content if content in page_content)
            print(f"✅ Content verification: {found_content}/{len(expected_content)} indicators found")
            
            if found_content >= 2:
                print("🎯 PROXY IS CMC-COMPATIBLE!")
                return True
            else:
                print("⚠️ Proxy works but content may be filtered")
                return False
        else:
            print(f"❌ CMC trending page failed: {trending_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Proxy test failed: {str(e)}")
        return False

def load_manual_proxies():
    """Load manual proxies from config file"""
    manual_proxy_file = "config/manual_proxies.txt"
    if not os.path.exists(manual_proxy_file):
        return []
    
    with open(manual_proxy_file, 'r') as f:
        proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    return proxies

def main():
    """Main test function"""
    print("🚀 CMC CONNECTIVITY TEST SUITE")
    print("="*60)
    print("This script tests CoinMarketCap accessibility for proxy configuration")
    print("="*60)
    
    # Test 1: Direct connection
    print("\n📡 PHASE 1: DIRECT CONNECTION TEST")
    direct_works = test_direct_connection()
    
    if direct_works:
        print("\n✅ Direct connection to CMC works!")
        print("If your automation is still failing, the issue might be with proxy configuration.")
    else:
        print("\n❌ Direct connection to CMC failed!")
        print("This could indicate network issues or CMC being blocked in your region.")
    
    # Test 2: Manual proxies
    manual_proxies = load_manual_proxies()
    if manual_proxies:
        print(f"\n📡 PHASE 2: MANUAL PROXY TESTING ({len(manual_proxies)} proxies)")
        working_proxies = []
        
        for i, proxy in enumerate(manual_proxies, 1):
            print(f"\n[{i}/{len(manual_proxies)}]", end=" ")
            if test_proxy_connection(proxy):
                working_proxies.append(proxy)
                print(f"🎯 ADDED TO WORKING LIST")
            else:
                print(f"❌ PROXY FAILED CMC TEST")
            
            # Add delay between tests
            if i < len(manual_proxies):
                time.sleep(2)
        
        print(f"\n📊 MANUAL PROXY RESULTS:")
        print(f"✅ Working with CMC: {len(working_proxies)}/{len(manual_proxies)}")
        
        if working_proxies:
            print(f"\n🎯 CMC-COMPATIBLE PROXIES:")
            for proxy in working_proxies:
                print(f"   ✅ {proxy}")
        else:
            print(f"\n❌ No manual proxies work with CMC")
    else:
        print(f"\n⚠️ PHASE 2 SKIPPED: No manual proxies configured")
        print(f"To add manual proxies: Run menu.py > Option 3 > Option 2")
    
    # Summary and recommendations
    print(f"\n" + "="*60)
    print("📋 TEST SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    if not direct_works and not (manual_proxies and any(manual_proxies)):
        print("❌ CRITICAL: Neither direct connection nor proxies work")
        print("🔧 RECOMMENDATIONS:")
        print("   1. Check your internet connection")
        print("   2. Try using a VPN")
        print("   3. Import working paid proxies")
        print("   4. Contact your ISP about CMC access")
    elif direct_works:
        print("✅ Direct connection works - you may not need proxies")
        print("🔧 RECOMMENDATIONS:")
        print("   1. Try running automation without proxies first")
        print("   2. If automation fails, import working proxies")
    elif manual_proxies and len(working_proxies) > 0:
        print(f"✅ {len(working_proxies)} manual proxies work with CMC")
        print("🔧 RECOMMENDATIONS:")
        print("   1. Your manual proxies should work with automation")
        print("   2. If automation still fails, try different proxies")
    else:
        print("⚠️ Mixed results - manual intervention needed")
        print("🔧 RECOMMENDATIONS:")
        print("   1. Try running automation and see what happens")
        print("   2. Import higher quality proxies if needed")
    
    print("\n🚀 Ready to test? Run: python autocrypto_social_bot/menu.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user. Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test script error: {str(e)}")
        sys.exit(1) 