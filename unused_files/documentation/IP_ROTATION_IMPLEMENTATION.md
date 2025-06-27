# IP Rotation Implementation

## Overview
This implementation ensures that **EVERY new session automatically changes the IP address**, regardless of promotion type, with comprehensive terminal logging for all IP changes.

## Key Features

### ✅ Mandatory IP Rotation on Session Start
- **EVERY** new session automatically triggers IP rotation
- Works for **ALL** promotion types (`market_making`, `token_shilling`, `trading_group`, etc.)
- Forced IP change happens during `CryptoAIAnalyzer.__init__()`
- Cannot be skipped or disabled

### ✅ Comprehensive Terminal Logging
- **Session Initialization**: Clear logging when new session starts with IP rotation
- **IP Changes**: Before/after IP addresses logged when possible
- **Proxy Changes**: Old/new proxy information displayed
- **Rotation Reasons**: Why IP rotation was triggered (new session, failure, anti-detection, etc.)
- **Session Status**: Current anti-detection mode, available proxies, recent failures

### ✅ Enhanced Anti-Detection Integration
- Uses existing `AntiDetectionSystem` for intelligent IP rotation
- Adaptive delays based on session health
- Automatic proxy validation and refresh
- Behavioral randomization after IP changes
- Shadowban detection and emergency IP rotation

## Implementation Details

### 1. Session Initialization (`main.py`)
```python
# MANDATORY IP ROTATION FOR EVERY NEW SESSION
print("\n🔄 MANDATORY IP ROTATION FOR NEW SESSION")
print("Initiating IP change for session security...")

# Force IP rotation on session start regardless of promotion type
if hasattr(self.profile_manager, 'switch_to_next_profile_with_ip_rotation'):
    print("🔄 Performing IP rotation with anti-detection...")
    self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
    
    # Get current IP information for logging
    current_ip = self._get_current_ip()
    if current_ip:
        print(f"✅ NEW SESSION IP: {current_ip}")
```

### 2. Enhanced Profile Manager (`profiles/profile_manager.py`)
```python
def switch_to_next_profile_with_ip_rotation(self):
    """Switch to next profile with IP rotation via anti-detection system"""
    print("\n🌐 PROFILE + IP ROTATION INITIATED")
    
    # Get current state for logging
    old_profile = self.current_profile
    old_proxy = self.anti_detection.session_state.get('current_proxy')
    
    # Log rotation details
    print(f"🔄 Switching: {old_profile} → {next_profile}")
    print(f"🌐 Proxy: {old_proxy} → {new_proxy}")
    print(f"📡 IP: {old_ip} → {new_ip}")
```

### 3. Anti-Detection System (`utils/anti_detection.py`)
```python
def create_anti_detection_options(self, use_proxy: bool = True):
    """Create Chrome options with anti-detection measures"""
    # Terminal logging for IP changes
    print(f"\n🔄 IP ROTATION INITIATED")
    print(f"🌐 Old Proxy: {old_proxy or 'None'}")
    print(f"🌐 New Proxy: {proxy}")
    print(f"📡 Previous IP: {old_ip}")
    print(f"📡 Current IP: {new_ip}")
    print(f"✅ IP ROTATION COMPLETE")
```

### 4. CMC Scraper Integration (`scrapers/cmc_scraper.py`)
```python
# Check if we should rotate IP for next post
if should_rotate:
    print("🔄 [IP-ROTATE] Anti-detection triggered IP rotation")
    print("🔍 [IP-ROTATE] Reason: Anti-detection system triggered rotation")
    self.driver = self.profile_manager.switch_to_next_profile_with_ip_rotation()
    print("✅ [IP-ROTATE] Successfully rotated IP and profile")
```

## Terminal Logging Examples

### Session Start Logging
```
🆔 NEW SESSION INITIALIZATION
================================================================================
Session ID: 20250123_143052
Session Start: 2025-01-23 14:30:52

🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
🌐 MANDATORY IP ROTATION FOR NEW SESSION
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
Initiating IP change for session security...
🔄 Performing IP rotation with anti-detection...

🔄 IP ROTATION INITIATED
🌐 Old Proxy: None
🌐 New Proxy: 185.199.229.156:7492
📡 Previous IP: Could not detect
📡 Current IP: 185.199.229.156
✅ IP ROTATION COMPLETE

✅ NEW SESSION IP: 185.199.229.156
📊 Session State: NORMAL_OPERATION
🌐 Proxy: 185.199.229.156:7492
🔧 Working Proxies: 8

🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
✅ SESSION IP ROTATION COMPLETE
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

📋 SESSION INITIALIZATION COMPLETE
================================================================================
Session ID: 20250123_143052
Promotion Type: MARKET_MAKING
IP Rotation: ✅ COMPLETED
Anti-Detection: ✅ ACTIVE
================================================================================
```

### During Operation Logging
```
🔄 [IP-ROTATE] Anti-detection triggered IP rotation
🔍 [IP-ROTATE] Reason: Anti-detection system triggered rotation

🌐 PROFILE + IP ROTATION INITIATED
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
📋 Current Profile: cmc_profile_1
🌐 Current Proxy: 185.199.229.156:7492
📡 Current IP: 185.199.229.156
🔄 Previous session closed
🔄 Switching: cmc_profile_1 → cmc_profile_2
🛡️ Creating anti-detection options with IP rotation...
📊 Anti-Detection Mode: NORMAL_OPERATION
🔧 Available Proxies: 7
🔄 Loading profile with new IP configuration...
🎭 Applying behavioral randomization...

✅ PROFILE + IP ROTATION COMPLETE
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
📋 Profile: cmc_profile_1 → cmc_profile_2
🌐 Proxy: 185.199.229.156:7492 → 194.5.207.114:8080
📡 IP: 185.199.229.156 → 194.5.207.114
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

✅ [IP-ROTATE] Successfully rotated IP and profile
```

## Session Tracking Enhancement

### Enhanced Session Info (`analysis_data/sessions/*/session_info.json`)
```json
{
  "session_id": "20250123_143052",
  "start_time": "2025-01-23 14:30:52",
  "promotion_config": {
    "type": "market_making",
    "params": {
      "firm_name": "onchain bureau"
    }
  },
  "processed_tokens": ["BTC", "ETH"],
  "failed_tokens": {},
  "ip_tracking": {
    "current_ip": "194.5.207.114",
    "current_proxy": "194.5.207.114:8080",
    "ip_rotation_forced_on_start": true,
    "estimated_ip_rotations": 2,
    "anti_detection_active": true
  }
}
```

## Promotion Type Support

### ✅ Market Making
- IP rotation on session start: **ENABLED**
- Adaptive IP rotation during operation: **ENABLED**
- Terminal logging: **COMPREHENSIVE**

### ✅ Token Shilling
- IP rotation on session start: **ENABLED**
- Adaptive IP rotation during operation: **ENABLED**
- Terminal logging: **COMPREHENSIVE**

### ✅ Trading Group
- IP rotation on session start: **ENABLED**
- Adaptive IP rotation during operation: **ENABLED**
- Terminal logging: **COMPREHENSIVE**

### ✅ All Other Types
- IP rotation on session start: **ENABLED**
- Adaptive IP rotation during operation: **ENABLED**
- Terminal logging: **COMPREHENSIVE**

## Testing

### Test Script (`test_ip_rotation.py`)
Run the test script to verify IP rotation functionality:

```bash
python test_ip_rotation.py
```

The test will:
1. ✅ Test IP rotation for all promotion types
2. ✅ Verify terminal logging is working
3. ✅ Check session tracking includes IP information
4. ✅ Validate anti-detection integration

## Configuration

### Proxy Setup (`config/proxies.txt`)
```
ip:port
# or with authentication
ip:port:username:password
```

### Anti-Detection Settings
- **Proxy refresh**: Every 1 hour
- **IP rotation triggers**: 
  - New session start (mandatory)
  - Every 10 successful posts
  - After 2 consecutive failures
  - Shadowban detection
  - Rate limit detection
- **Working proxy pool**: Maintained automatically

## Benefits

1. **🛡️ Enhanced Security**: Every session starts with a fresh IP
2. **🔄 Automatic Rotation**: No manual intervention required
3. **📊 Full Visibility**: Comprehensive logging of all IP changes
4. **🎯 Universal Support**: Works with ALL promotion types
5. **🧠 Intelligent**: Anti-detection system adapts based on session health
6. **📝 Session Tracking**: Complete audit trail of IP changes

## Usage

Simply run any promotion type - IP rotation is now **AUTOMATIC**:

```bash
# Market Making - IP rotation happens automatically
python -m autocrypto_social_bot.menu

# Token Shilling - IP rotation happens automatically  
python -m autocrypto_social_bot.menu

# Trading Group - IP rotation happens automatically
python -m autocrypto_social_bot.menu
```

**Every new session will automatically change the IP and log it clearly in the terminal!** 