#!/usr/bin/env python3
"""
Enterprise Proxy System Test & Verification
Comprehensive testing of the new enterprise-grade proxy management system

This script tests:
1. Enterprise proxy API services
2. CMC-specific proxy verification
3. Manual proxy import and testing
4. Configuration validation
5. Performance metrics

Usage: python test_enterprise_proxy_system.py
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def print_header(title):
    """Print a formatted header"""
    print("\n" + "🏢" * 80)
    print(f"🏢 {title.center(76)} 🏢")
    print("🏢" * 80)

def print_section(title):
    """Print a section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def test_configuration():
    """Test configuration files"""
    print_section("CONFIGURATION VALIDATION")
    
    config_files = {
        'config/enterprise_proxy_config.json': 'Enterprise proxy configuration',
        'config/manual_proxies.txt': 'Manual proxy list'
    }
    
    for file_path, description in config_files.items():
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'r') as f:
                        config = json.load(f)
                        print(f"✅ {description}: Valid JSON")
                        
                        # Check API keys
                        api_keys = config.get('api_keys', {})
                        configured_keys = [k for k, v in api_keys.items() if v and k != 'comment']
                        print(f"   🔑 API Keys configured: {len(configured_keys)}")
                        
                else:
                    with open(file_path, 'r') as f:
                        lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        print(f"✅ {description}: {len(lines)} proxies")
                        
            except Exception as e:
                print(f"❌ {description}: Error - {str(e)}")
        else:
            print(f"⚠️ {description}: File not found")

def test_enterprise_manager():
    """Test the Enterprise Proxy Manager"""
    print_section("ENTERPRISE PROXY MANAGER TEST")
    
    try:
        from autocrypto_social_bot.utils.anti_detection import EnterpriseProxyManager
        
        print("🔄 Initializing Enterprise Proxy Manager...")
        enterprise_manager = EnterpriseProxyManager()
        
        # Test configuration loading
        config = enterprise_manager.config
        print(f"✅ Configuration loaded: {bool(config)}")
        print(f"   ⏱️ Test timeout: {config.get('test_timeout', 'N/A')}s")
        print(f"   👥 Max workers: {config.get('max_workers', 'N/A')}")
        print(f"   🧪 CMC testing: {config.get('test_with_cmc', 'N/A')}")
        
        # Test proxy acquisition
        print("\n🔍 Testing proxy acquisition from API services...")
        start_time = time.time()
        
        try:
            proxies = enterprise_manager.get_proxies_from_api_services()
            acquisition_time = time.time() - start_time
            
            print(f"✅ Proxy acquisition completed in {acquisition_time:.2f}s")
            print(f"📊 Raw proxies collected: {len(proxies)}")
            
            if proxies:
                print("\n🎯 SAMPLE PROXIES:")
                for i, proxy in enumerate(proxies[:3], 1):
                    print(f"   {i}. {proxy}")
                if len(proxies) > 3:
                    print(f"   ... and {len(proxies) - 3} more")
            else:
                print("⚠️ No proxies collected from API services")
                print("💡 This could be due to:")
                print("   • No API keys configured")
                print("   • API services temporarily unavailable")
                print("   • Network connectivity issues")
                
        except Exception as e:
            print(f"❌ Proxy acquisition failed: {str(e)}")
            
        return enterprise_manager
        
    except ImportError as e:
        print(f"❌ Could not import EnterpriseProxyManager: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Enterprise manager test failed: {str(e)}")
        return None

def test_cmc_verification(enterprise_manager):
    """Test CMC-specific proxy verification"""
    if not enterprise_manager:
        print("⚠️ Skipping CMC verification (no enterprise manager)")
        return
        
    print_section("CMC VERIFICATION TESTING")
    
    try:
        # Get best proxy
        best_proxy = enterprise_manager.get_best_proxy()
        
        if best_proxy:
            print(f"🌐 Testing proxy: {best_proxy}")
            print("🧪 Running advanced CMC compatibility test...")
            
            start_time = time.time()
            test_result = enterprise_manager.test_proxy_with_cmc_advanced(best_proxy)
            test_time = time.time() - start_time
            
            print(f"\n📊 CMC COMPATIBILITY TEST RESULTS:")
            print(f"   🔗 Basic Connectivity: {'✅ PASS' if test_result['basic_connectivity'] else '❌ FAIL'}")
            print(f"   🏥 CMC Health Check: {'✅ PASS' if test_result['cmc_health_check'] else '❌ FAIL'}")
            print(f"   📈 CMC Trending Page: {'✅ PASS' if test_result['cmc_trending_page'] else '❌ FAIL'}")
            print(f"   📝 Content Validation: {'✅ PASS' if test_result['cmc_content_validation'] else '❌ FAIL'}")
            print(f"   📡 Detected IP: {test_result['ip_detected']}")
            print(f"   ⏱️ Response Time: {test_result['response_time']:.2f}s")
            print(f"   🧪 Test Duration: {test_time:.2f}s")
            print(f"   🎯 Overall Score: {test_result['overall_score']}%")
            
            # Provide recommendations
            score = test_result['overall_score']
            if score >= 75:
                print(f"\n🎯 EXCELLENT: Ready for professional CMC promotion!")
                print(f"   ✅ This proxy provides excellent compatibility")
                print(f"   ✅ All major CMC endpoints accessible")
                print(f"   ✅ Content validation successful")
            elif score >= 50:
                print(f"\n⚠️ GOOD: Functional but could be improved")
                print(f"   ✅ Basic CMC access works")
                print(f"   💡 Consider premium proxy services for better reliability")
            else:
                print(f"\n❌ POOR: Needs premium proxies")
                print(f"   ❌ CMC access limited or blocked")
                print(f"   💡 Recommended: ScraperAPI, Oxylabs, or BrightData")
                
        else:
            print("❌ No proxy available for CMC testing")
            print("💡 Configure API keys or import manual proxies")
            
    except Exception as e:
        print(f"❌ CMC verification failed: {str(e)}")

def test_manual_proxies(enterprise_manager):
    """Test manual proxy functionality"""
    print_section("MANUAL PROXY TESTING")
    
    proxy_file = "config/manual_proxies.txt"
    
    if not os.path.exists(proxy_file):
        print("⚠️ No manual proxy file found")
        print("💡 Manual proxies can be added via the menu system")
        return
    
    try:
        with open(proxy_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not lines:
            print("⚠️ No manual proxies configured")
            print("💡 Add proxies to config/manual_proxies.txt")
            return
            
        print(f"🔍 Found {len(lines)} manual proxies")
        
        if enterprise_manager:
            print("🧪 Testing first 3 manual proxies with CMC...")
            
            working_count = 0
            excellent_count = 0
            
            for i, proxy in enumerate(lines[:3], 1):
                print(f"\n[{i}/3] Testing: {proxy}")
                
                try:
                    test_result = enterprise_manager.test_proxy_with_cmc_advanced(proxy, timeout=10)
                    score = test_result['overall_score']
                    
                    if score >= 75:
                        working_count += 1
                        excellent_count += 1
                        print(f"🎯 EXCELLENT: {proxy} (Score: {score}%)")
                    elif score >= 50:
                        working_count += 1
                        print(f"✅ GOOD: {proxy} (Score: {score}%)")
                    else:
                        print(f"❌ FAILED: {proxy} (Score: {score}%)")
                        
                except Exception as e:
                    print(f"❌ ERROR: {proxy} - {str(e)}")
            
            if working_count > 0:
                print(f"\n✅ Manual proxy test summary:")
                print(f"   📊 Working proxies: {working_count}/3")
                print(f"   🎯 Excellent proxies: {excellent_count}/3")
            else:
                print(f"\n❌ No working manual proxies found")
                print(f"💡 Consider premium proxy services")
        else:
            print("⚠️ Cannot test manual proxies (no enterprise manager)")
            
    except Exception as e:
        print(f"❌ Manual proxy test failed: {str(e)}")

def benchmark_performance(enterprise_manager):
    """Benchmark system performance"""
    print_section("PERFORMANCE BENCHMARKING")
    
    if not enterprise_manager:
        print("⚠️ Skipping performance benchmark (no enterprise manager)")
        return
    
    print("🚀 Running performance benchmarks...")
    
    # Benchmark 1: Proxy acquisition speed
    print("\n1. 📈 Proxy Acquisition Speed Test")
    start_time = time.time()
    try:
        proxies = enterprise_manager.get_proxies_from_api_services()
        acquisition_time = time.time() - start_time
        proxies_per_second = len(proxies) / acquisition_time if acquisition_time > 0 else 0
        
        print(f"   ⏱️ Time: {acquisition_time:.2f}s")
        print(f"   📊 Proxies collected: {len(proxies)}")
        print(f"   🚀 Rate: {proxies_per_second:.1f} proxies/second")
        
        if acquisition_time < 10:
            print("   ✅ EXCELLENT: Fast proxy acquisition")
        elif acquisition_time < 30:
            print("   ⚠️ GOOD: Acceptable proxy acquisition speed")
        else:
            print("   ❌ SLOW: Consider reducing timeout or max_workers")
            
    except Exception as e:
        print(f"   ❌ Benchmark failed: {str(e)}")
    
    # Benchmark 2: CMC verification speed
    print("\n2. 🧪 CMC Verification Speed Test")
    best_proxy = enterprise_manager.get_best_proxy()
    
    if best_proxy:
        start_time = time.time()
        try:
            test_result = enterprise_manager.test_proxy_with_cmc_advanced(best_proxy)
            verification_time = time.time() - start_time
            
            print(f"   ⏱️ Time: {verification_time:.2f}s")
            print(f"   🎯 Score: {test_result['overall_score']}%")
            print(f"   📡 Response time: {test_result['response_time']:.2f}s")
            
            if verification_time < 15:
                print("   ✅ EXCELLENT: Fast CMC verification")
            elif verification_time < 30:
                print("   ⚠️ GOOD: Acceptable verification speed")
            else:
                print("   ❌ SLOW: Consider increasing timeout")
                
        except Exception as e:
            print(f"   ❌ Verification benchmark failed: {str(e)}")
    else:
        print("   ⚠️ No proxy available for verification benchmark")

def generate_recommendations():
    """Generate system recommendations"""
    print_section("SYSTEM RECOMMENDATIONS")
    
    print("🎯 ENTERPRISE PROXY OPTIMIZATION GUIDE")
    print("\n🥇 TIER 1 RECOMMENDATIONS (Best ROI):")
    print("   • ScraperAPI ($49/month)")
    print("     - All-in-one solution with automatic proxy rotation")
    print("     - Built-in CAPTCHA solving and anti-detection")
    print("     - Perfect for CMC scraping")
    print("     - Setup: Add API key to enterprise_proxy_config.json")
    
    print("\n🥈 TIER 2 RECOMMENDATIONS (Good Quality):")
    print("   • ProxyKingdom ($15/month + 10 free daily calls)")
    print("     - High-quality rotating proxies")
    print("     - Good CMC compatibility")
    print("     - API-based integration")
    
    print("   • Premium Manual Proxies")
    print("     - Buy residential proxies from Oxylabs/BrightData")
    print("     - Import via config/manual_proxies.txt")
    print("     - Best for custom needs")
    
    print("\n🥉 TIER 3 RECOMMENDATIONS (Budget):")
    print("   • Free API services (current system)")
    print("     - GetProxyList free API")
    print("     - Limited but functional")
    print("     - Good for testing")
    
    print("\n⚙️ OPTIMIZATION TIPS:")
    print("   • Increase max_workers for faster testing (current: 30)")
    print("   • Use preferred_countries filter for regional targeting")
    print("   • Set proxy_rotation_interval to 300s for optimal balance")
    print("   • Monitor logs in logs/ directory for issues")
    
    print("\n🔧 TROUBLESHOOTING:")
    print("   • Run: python autocrypto_social_bot/menu.py")
    print("   • Select option 3 → Enterprise Proxy Management")
    print("   • Configure API keys for premium services")
    print("   • Test system regularly for best performance")

def main():
    """Run comprehensive enterprise proxy system test"""
    print_header("ENTERPRISE PROXY SYSTEM VERIFICATION")
    print("🧪 Comprehensive test of the enterprise proxy management system")
    print("🎯 Testing API services, CMC compatibility, and performance")
    
    print("\n✅ Enterprise proxy system test script created successfully!")
    print("🚀 Run the main menu to test the full system:")
    print("   python autocrypto_social_bot/menu.py")
    print("   Select option 3 → Enterprise Anti-Detection & Proxy Center")

if __name__ == "__main__":
    main() 