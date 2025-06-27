#!/usr/bin/env python3
"""
Complete Integration Test for Automated Account Management System
"""

import sys
import os
import time
import logging
from datetime import datetime

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_system():
    """Test the complete system"""
    print("🧪 Testing Automated Account Management System...")
    
    try:
        from autocrypto_social_bot.config.simplelogin_config import SimpleLoginConfig
        config = SimpleLoginConfig()
        
        if not config.is_configured():
            print("❌ SimpleLogin not configured. Please run setup_simplelogin.py first.")
            return False
        
        print("✅ Configuration loaded")
        
        from autocrypto_social_bot.services.account_manager import AutomatedAccountManager
        manager = AutomatedAccountManager(config.get_api_key())
        
        print("✅ Account manager initialized")
        
        # Test account creation
        test_account = manager.create_new_account("test")
        print(f"✅ Created account: {test_account.username}")
        
        # Test statistics
        stats = manager.get_stats_summary()
        print(f"✅ Statistics: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_system() 