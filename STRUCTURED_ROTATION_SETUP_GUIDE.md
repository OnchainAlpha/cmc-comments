# 🔄 Structured Profile Rotation System - Setup Guide

## ✨ What's New

Your CMC automation bot now has a **structured profile rotation system** that ensures:

1. **Sequential rotation**: `cmc_profile_1` → `cmc_profile_2` → `cmc_profile_3`...
2. **Login verification**: Each profile is checked before use
3. **User confirmation**: You decide which logged-out profiles to delete
4. **No wasted time**: Only functional profiles are used

## 🚀 Quick Start

### Step 1: Test the System
```bash
python test_structured_rotation.py
```
This will verify that the structured rotation system is working correctly.

### Step 2: Verify Your Profiles (Recommended)
```bash
python test_structured_rotation.py --verify
```
This will:
- Check all your CMC profiles for login status
- Ask you which logged-out profiles to delete
- Clean up your profile collection

### Step 3: Run the Bot
```bash
python autocrypto_social_bot/main.py
```
When prompted:
- Choose **'y'** to verify all profiles before starting (recommended)
- Choose **'n'** to skip verification and start immediately

## 🔄 How It Works

### Before (Old System)
```
❌ Random profile selection
❌ No login verification
❌ Time wasted on logged-out profiles
❌ Automatic profile deletion without asking
```

### After (New System)
```
✅ Sequential profile rotation (cmc_profile_1 → cmc_profile_2 → cmc_profile_3...)
✅ Login verification before each use
✅ User confirmation before deleting profiles
✅ Clear status reporting
✅ No time wasted on broken profiles
```

## 📋 What You'll See

### During Setup
```
🔄 INITIALIZING STRUCTURED PROFILE ROTATION
============================================================
Verify all profiles for login status before starting? (y/n): y

🔍 VERIFYING LOGIN STATUS FOR ALL 5 PROFILES
======================================================================

==================================================
🔍 CHECKING PROFILE 1/5: cmc_profile_1
==================================================
📂 Loading profile: cmc_profile_1
🔍 Verifying CMC login status...
✅ VERIFIED: cmc_profile_1 is logged into CMC

==================================================
🔍 CHECKING PROFILE 2/5: cmc_profile_2
==================================================
📂 Loading profile: cmc_profile_2
🔍 Verifying CMC login status...
❌ FAILED: cmc_profile_2 is NOT logged into CMC
   Reasons: Login text found: log in, Login element found: //button[contains(text(), 'Log In')]

⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
❌ PROFILE NOT LOGGED IN: cmc_profile_2
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
📊 Login Score: 0
📊 Logout Score: 5
🔍 Reasons: Login text found: log in, Login element found: //button[contains(text(), 'Log In')]

This profile is taking up space and slowing down rotation.
It will be moved to a backup folder, not permanently deleted.

🗑️ Delete cmc_profile_2? (y/n/s=skip all): y
🗑️ DELETED: cmc_profile_2
```

### During Operation
```
🔄 STRUCTURED ROTATION #1
   📋 Profile: cmc_profile_1
   📊 Position: 1/3
   🔄 Next: cmc_profile_3

🔄 Using structured profile rotation...
✅ VERIFIED: cmc_profile_1 is logged in
✅ STRUCTURED ROTATION SUCCESS: Now using cmc_profile_1
```

## 🛠️ Advanced Usage

### Manual Profile Verification
```bash
python autocrypto_social_bot/structured_profile_rotation.py
```
Choose from:
1. Verify all profiles
2. Test rotation sequence
3. Both

### Test Rotation Sequence Only
```bash
python test_structured_rotation.py
```

### Get Help
```bash
python test_structured_rotation.py --help
```

## 🎯 Benefits

### ⚡ **Faster Operation**
- No time wasted trying to use logged-out profiles
- Quick login verification before each use
- Efficient sequential rotation

### 🎯 **Predictable Behavior**
- Always rotates in order: 1 → 2 → 3 → 1...
- Clear status reporting
- No random profile selection

### 🧹 **Automatic Cleanup**
- Detects logged-out profiles automatically
- Asks for your permission before deleting
- Keeps only functional profiles

### 👤 **User Control**
- You decide which profiles to delete
- Option to skip verification entirely
- Clear feedback on what's happening

## 🔧 Configuration

The system automatically integrates with your existing configuration:
- Uses your existing proxy settings
- Works with all existing profile management features
- Fallback to standard rotation if needed

## 🐛 Troubleshooting

### "No CMC profiles found"
Create profiles first:
```bash
python autocrypto_social_bot/menu.py
```
Go to Profile Management → Create New Profile

### "Structured rotation not available"
The system will automatically fall back to standard rotation. Check that `autocrypto_social_bot/structured_profile_rotation.py` exists.

### "All profiles failed verification"
All your profiles need to be logged into CMC:
1. Manually log into each profile
2. Or create new profiles and log in
3. Run verification again

## 📊 Status Reporting

The system provides detailed status information:
- Number of profiles found
- Login verification results
- Rotation sequence and position
- Success/failure rates
- Clear error messages

## 🎉 Ready to Go!

Your bot now has intelligent profile rotation that:
- ✅ Ensures sequential rotation order
- ✅ Verifies login status before use
- ✅ Asks permission before deleting profiles
- ✅ Saves time by avoiding broken profiles
- ✅ Provides clear status reporting

Run the test to verify everything is working:
```bash
python test_structured_rotation.py
```

Then start your bot as usual:
```bash
python autocrypto_social_bot/main.py
``` 