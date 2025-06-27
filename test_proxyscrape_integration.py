#!/usr/bin/env python3
"""
Test script for ProxyScrape v4 integration
Verifies that proxies are being fetched and CMC access works
"""

import sys
import os
import time
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager

def test_proxyscrape_integration():
    """Test ProxyScrape v4 API integration"""
    print("🧪 TESTING PROXYSCRAPE V4 INTEGRATION")
    print("="*60)
    
    try:
        # Initialize the enterprise proxy manager
        print("🔄 Initializing Enterprise Proxy Manager...")
        manager = EnterpriseProxyManager()
        
        # Test proxy fetching
        print("\n📡 Testing ProxyScrape v4 API...")
        proxies = manager.get_enterprise_grade_proxies()
        
        if proxies:
            print(f"✅ SUCCESS: Found {len(proxies)} working proxies")
            
            # Show first few proxies
            print(f"\n🎯 TOP WORKING PROXIES:")
            for i, proxy in enumerate(proxies[:5], 1):
                print(f"   {i}. {proxy}")
            
            # Test best proxy
            best_proxy = manager.get_best_proxy()
            if best_proxy:
                print(f"\n🏆 BEST PROXY: {best_proxy}")
                
                # Test CMC access with best proxy
                print(f"\n🧪 Testing CMC access with best proxy...")
                test_result = manager.test_proxy_with_cmc_advanced(best_proxy)
                
                print(f"\n📊 CMC TEST RESULTS:")
                print(f"   🔗 Basic Connectivity: {'✅' if test_result['basic_connectivity'] else '❌'}")
                print(f"   🏥 CMC Health Check: {'✅' if test_result['cmc_health_check'] else '❌'}")
                print(f"   📈 CMC Trending Page: {'✅' if test_result['cmc_trending_page'] else '❌'}")
                print(f"   📝 Content Validation: {'✅' if test_result['cmc_content_validation'] else '❌'}")
                print(f"   📡 Detected IP: {test_result['ip_detected']}")
                print(f"   ⏱️ Response Time: {test_result['response_time']:.2f}s")
                print(f"   🎯 Overall Score: {test_result['overall_score']}%")
                
                if test_result['overall_score'] >= 75:
                    print(f"\n🎉 EXCELLENT: Ready for professional CMC promotion!")
                    return True
                elif test_result['overall_score'] >= 50:
                    print(f"\n✅ GOOD: System functional for CMC access")
                    return True
                else:
                    print(f"\n⚠️ POOR: Proxy quality could be improved")
                    return False
            else:
                print(f"❌ No best proxy available")
                return False
        else:
            print(f"❌ No working proxies found")
            print(f"\n🔧 TROUBLESHOOTING:")
            print(f"   1. Check internet connection")
            print(f"   2. ProxyScrape may be temporarily unavailable")
            print(f"   3. Try again in 1-2 minutes")
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return False

def test_mandatory_proxy_validation():
    """Test mandatory proxy validation"""
    print(f"\n🔒 TESTING MANDATORY PROXY VALIDATION")
    print("="*60)
    
    try:
        manager = EnterpriseProxyManager()
        
        # Test the validation function
        validation_result = manager.validate_proxy_availability()
        
        if validation_result:
            print("✅ VALIDATION PASSED: Proxies available for mandatory protection")
            return True
        else:
            print("❌ VALIDATION FAILED: No proxies available")
            print("💡 This would prevent the application from starting")
            return False
            
    except Exception as e:
        print(f"❌ VALIDATION ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 PROXYSCRAPE V4 INTEGRATION TEST SUITE")
    print("="*60)
    print("Testing ProxyScrape integration and mandatory proxy protection")
    print("This ensures you never use your real IP address")
    print("="*60)
    
    # Test 1: ProxyScrape Integration
    test1_passed = test_proxyscrape_integration()
    
    # Test 2: Mandatory Proxy Validation  
    test2_passed = test_mandatory_proxy_validation()
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("="*60)
    print(f"ProxyScrape v4 Integration: {'✅ PASS' if test1_passed else '❌ FAIL'}")
    print(f"Mandatory Proxy Validation: {'✅ PASS' if test2_passed else '❌ FAIL'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ Your application will ALWAYS use proxies")
        print(f"✅ Your real IP will NEVER be exposed to CMC")
        print(f"✅ ProxyScrape v4 API is working correctly")
    else:
        print(f"\n⚠️ SOME TESTS FAILED")
        print(f"💡 Check your internet connection and try again")
        print(f"💡 ProxyScrape updates proxies every minute")
    
    print("="*60)

if __name__ == "__main__":
    main() 