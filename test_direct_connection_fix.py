#!/usr/bin/env python3
"""
Test Direct Connection Fix - Comprehensive Anti-Detection System Test
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
import json

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_anti_detection_system_configuration():
    """Test that anti-detection system respects proxy configuration"""
    print("🧪 Testing Anti-Detection System Configuration...")
    
    try:
        from autocrypto_social_bot.utils.anti_detection import AntiDetectionSystem
        
        # Test 1: Direct connection mode (IP rotation disabled)
        print("\n1️⃣ Testing Direct Connection Mode...")
        direct_config = {'auto_proxy_rotation': False}
        direct_anti_detection = AntiDetectionSystem(proxy_config=direct_config)
        
        assert not direct_anti_detection.ip_rotation_enabled, "IP rotation should be disabled in direct connection mode"
        assert direct_anti_detection.session_state['current_mode'] == 'direct_connection', "Mode should be direct_connection"
        
        # Test get_working_proxy returns None for direct connection
        proxy = direct_anti_detection.get_working_proxy()
        assert proxy is None, "Should return None for direct connection mode"
        
        print("   ✅ Direct connection mode configured correctly")
        
        # Test 2: Enterprise mode (IP rotation enabled)
        print("\n2️⃣ Testing Enterprise Mode...")
        enterprise_config = {'auto_proxy_rotation': True}
        enterprise_anti_detection = AntiDetectionSystem(proxy_config=enterprise_config)
        
        assert enterprise_anti_detection.ip_rotation_enabled, "IP rotation should be enabled in enterprise mode"
        assert enterprise_anti_detection.session_state['current_mode'] == 'enterprise_mode', "Mode should be enterprise_mode"
        
        print("   ✅ Enterprise mode configured correctly")
        
        # Test 3: Default configuration (should default to enterprise)
        print("\n3️⃣ Testing Default Configuration...")
        default_anti_detection = AntiDetectionSystem()
        
        assert default_anti_detection.ip_rotation_enabled, "Should default to IP rotation enabled"
        assert default_anti_detection.session_state['current_mode'] == 'enterprise_mode', "Should default to enterprise_mode"
        
        print("   ✅ Default configuration works correctly")
        
        print("\n✅ All anti-detection system configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Anti-detection system configuration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_profile_manager_proxy_config_passing():
    """Test that ProfileManager properly passes proxy config to anti-detection system"""
    print("\n🧪 Testing ProfileManager Proxy Configuration Passing...")
    
    try:
        from autocrypto_social_bot.profiles.profile_manager import ProfileManager
        
        # Test 1: Direct connection configuration
        print("\n1️⃣ Testing ProfileManager with Direct Connection...")
        direct_config = {'auto_proxy_rotation': False}
        
        with patch('autocrypto_social_bot.profiles.profile_manager.AntiDetectionSystem') as mock_anti_detection:
            mock_instance = Mock()
            mock_instance.display_anti_detection_status = Mock()
            mock_anti_detection.return_value = mock_instance
            
            profile_manager = ProfileManager(proxy_config=direct_config)
            
            # Verify AntiDetectionSystem was called with proxy_config
            mock_anti_detection.assert_called_with(proxy_config=direct_config)
            print("   ✅ ProfileManager passes proxy config to AntiDetectionSystem")
            
            # Verify display_anti_detection_status was called
            mock_instance.display_anti_detection_status.assert_called_once()
            print("   ✅ Anti-detection status display was called")
        
        # Test 2: Enterprise configuration
        print("\n2️⃣ Testing ProfileManager with Enterprise Configuration...")
        enterprise_config = {'auto_proxy_rotation': True}
        
        with patch('autocrypto_social_bot.profiles.profile_manager.AntiDetectionSystem') as mock_anti_detection:
            mock_instance = Mock()
            mock_instance.display_anti_detection_status = Mock()
            mock_anti_detection.return_value = mock_instance
            
            profile_manager = ProfileManager(proxy_config=enterprise_config)
            
            mock_anti_detection.assert_called_with(proxy_config=enterprise_config)
            print("   ✅ Enterprise configuration passed correctly")
        
        print("\n✅ All ProfileManager proxy configuration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ ProfileManager proxy configuration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_anti_detection_status_display():
    """Test that anti-detection status display shows correct IP rotation status"""
    print("\n🧪 Testing Anti-Detection Status Display...")
    
    try:
        from autocrypto_social_bot.utils.anti_detection import AntiDetectionSystem
        
        # Test 1: Direct connection status display
        print("\n1️⃣ Testing Direct Connection Status Display...")
        direct_config = {'auto_proxy_rotation': False}
        direct_anti_detection = AntiDetectionSystem(proxy_config=direct_config)
        
        # Capture print output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            direct_anti_detection.display_anti_detection_status()
        output = f.getvalue()
        
        assert "IP Rotation DISABLED (Direct Connection)" in output, "Should show IP rotation disabled"
        assert "Anti-Detection System: ACTIVE" in output, "Should show system is active"
        print("   ✅ Direct connection status display correct")
        
        # Test 2: Enterprise mode status display
        print("\n2️⃣ Testing Enterprise Mode Status Display...")
        enterprise_config = {'auto_proxy_rotation': True}
        enterprise_anti_detection = AntiDetectionSystem(proxy_config=enterprise_config)
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            enterprise_anti_detection.display_anti_detection_status()
        output = f.getvalue()
        
        assert "IP Rotation via Proxies" in output, "Should show IP rotation enabled"
        assert "IP Rotation DISABLED" not in output, "Should not show disabled message"
        print("   ✅ Enterprise mode status display correct")
        
        print("\n✅ All anti-detection status display tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Anti-detection status display test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_crypto_ai_analyzer_integration():
    """Test that CryptoAIAnalyzer properly integrates with the updated system"""
    print("\n🧪 Testing CryptoAIAnalyzer Integration...")
    
    try:
        # Mock the config file and dependencies
        with patch('os.path.exists') as mock_exists, \
             patch('builtins.open', create=True) as mock_open, \
             patch('json.load') as mock_json_load, \
             patch('autocrypto_social_bot.main.ChromeDriverManager'), \
             patch('autocrypto_social_bot.main.webdriver'), \
             patch('autocrypto_social_bot.main.ProfileManager') as mock_profile_manager, \
             patch('autocrypto_social_bot.main.CMCScraper'), \
             patch('autocrypto_social_bot.main.OpenAI'):
            
            # Setup mocks
            mock_exists.return_value = True
            mock_json_load.return_value = {'auto_proxy_rotation': False}
            mock_profile_instance = Mock()
            mock_profile_instance.anti_detection = Mock()
            mock_profile_instance.anti_detection.display_anti_detection_status = Mock()
            mock_profile_manager.return_value = mock_profile_instance
            
            from autocrypto_social_bot.main import CryptoAIAnalyzer
            
            # Test direct connection configuration
            direct_config = {'auto_proxy_rotation': False}
            analyzer = CryptoAIAnalyzer(proxy_config=direct_config)
            
            # Verify ProfileManager was called with proxy_config
            mock_profile_manager.assert_called_with(proxy_config=direct_config)
            print("   ✅ CryptoAIAnalyzer passes proxy config to ProfileManager")
            
        print("\n✅ All CryptoAIAnalyzer integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ CryptoAIAnalyzer integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_anti_detection_tests():
    """Run all anti-detection system tests"""
    print("🔬 COMPREHENSIVE ANTI-DETECTION SYSTEM TESTS")
    print("="*60)
    
    tests = [
        test_anti_detection_system_configuration,
        test_profile_manager_proxy_config_passing,
        test_anti_detection_status_display,
        test_crypto_ai_analyzer_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL ANTI-DETECTION TESTS PASSED!")
        print("🎯 Anti-detection system properly respects direct connection preference")
        print("✅ IP rotation is correctly disabled when direct connection is chosen")
        print("🛡️ Other anti-detection features remain active (shadowban detection, etc.)")
    else:
        print(f"\n⚠️ {failed} tests failed - check configuration")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_anti_detection_tests()
    exit(0 if success else 1) 