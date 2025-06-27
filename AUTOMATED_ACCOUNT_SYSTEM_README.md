# 🚀 Automated Account Management System

> **Solve your visibility issues with automated fresh account creation using SimpleLogin.io**

This system automatically creates fresh social media accounts using SimpleLogin.io email aliases, stores them in a database, and rotates through them to maximize post visibility and avoid platform detection.

## 🎯 Why This Solves Your Visibility Problem

- **Fresh Accounts**: Create new accounts automatically when old ones lose effectiveness
- **Email Alias Management**: Use SimpleLogin.io to generate unique email addresses 
- **Smart Rotation**: Automatically switch between accounts based on usage limits
- **Profile Integration**: Seamlessly integrates with your existing Chrome profile system
- **Database Tracking**: SQLite database tracks account performance and usage
- **Anti-Detection**: Works with your existing proxy and anti-detection systems

## 🔧 Quick Setup (5 Minutes)

### 1. Install Dependencies

```bash
pip install requests sqlite3 selenium undetected-chromedriver python-dotenv
```

### 2. Get SimpleLogin.io API Key

1. Go to [SimpleLogin.io](https://simplelogin.io) and create an account
2. Navigate to [API Settings](https://app.simplelogin.io/dashboard/api_key)
3. Generate a new API key
4. Copy the API key

### 3. Configure the System

```bash
python setup_simplelogin.py
```

Enter your API key when prompted. The system will test it and save the configuration.

### 4. Test Account Creation

```bash
python autocrypto_social_bot/scripts/account_management_demo.py
```

## 🚀 Basic Usage

### Create Fresh Account with Chrome Profile

```python
from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager

# Initialize the manager
manager = EnhancedProfileManager()

# Create fresh account with Chrome profile
account, driver = manager.create_fresh_account_with_profile("cmc")

print(f"✅ Created: {account.username}")
print(f"📧 Email: {account.email_alias}")
print(f"🔑 Password: {account.password}")

# Use the browser for posting
driver.get("https://coinmarketcap.com")
# ... your posting logic here
```

### Rotate to Fresh Account When Needed

```python
# When current account reaches daily limit, rotate to fresh one
fresh_account, fresh_driver = manager.rotate_to_fresh_account("cmc", max_posts_per_day=10)

print(f"🔄 Switched to: {fresh_account.username}")
print(f"📊 Posts today: {fresh_account.posts_today}")
```

### Basic Account Creation (Without Chrome)

```python
from autocrypto_social_bot.services.account_manager import AutomatedAccountManager

manager = AutomatedAccountManager("your_simplelogin_api_key")

# Create single account
account = manager.create_new_account("cmc")

# Create multiple accounts
accounts = manager.create_multiple_accounts("cmc", count=5)

# Get account for posting
next_account = manager.get_next_account("cmc")
```

## 📊 Account Management Features

### View Account Statistics

```python
stats = manager.get_stats_summary()
print(f"📊 Active accounts: {stats['cmc']['active']}")
print(f"📈 Total posts: {stats['cmc']['total_posts']}")
print(f"✅ Success rate: {stats['cmc']['avg_success_rate']}%")
```

### Account Status Management

```python
# Mark account as compromised
manager.mark_account_compromised(account_id, "Detected by platform")

# Get fresh account that hasn't hit daily limits
fresh_account = manager.rotate_to_fresh_account("cmc", max_posts_per_day=5)

# Update account usage after posting
manager.database.update_account_usage(account.id, success=True)
```

### Maintenance Operations

```python
# Perform daily maintenance
manager.perform_maintenance()  # Resets daily counters, cleans up old accounts

# Clean up inactive accounts
manager.cleanup_old_accounts(days_inactive=30)
```

## 🎮 Demo Scripts

### Interactive Demo
```bash
python autocrypto_social_bot/scripts/account_management_demo.py
```

### Run All Demos
```bash
python autocrypto_social_bot/scripts/account_management_demo.py --all
```

## 🗃️ Database Schema

The system uses SQLite with these tables:

**accounts**
- `id`: Unique account ID
- `email_alias`: SimpleLogin email alias
- `password`: Generated password
- `username`: Platform username
- `platform`: Platform (cmc, twitter, etc.)
- `profile_name`: Associated Chrome profile
- `created_at`: Creation timestamp
- `last_used`: Last usage timestamp
- `status`: active, suspended, banned, inactive
- `posts_today`: Daily post count
- `total_posts`: Total lifetime posts
- `success_rate`: Success percentage
- `simplelogin_alias_id`: SimpleLogin alias ID

**account_stats**
- Daily usage statistics per account

## 🔄 Integration with Existing System

### Replace Your Current Profile Switching

**Old way:**
```python
profile_manager = ProfileManager()
driver = profile_manager.switch_to_next_profile()
```

**New way:**
```python
enhanced_manager = EnhancedProfileManager()
account, driver = enhanced_manager.rotate_to_fresh_account("cmc")
# Now you have both a fresh account AND Chrome profile
```

### Add to Your Main Script

```python
from autocrypto_social_bot.enhanced_profile_manager import EnhancedProfileManager

class YourMainBot:
    def __init__(self):
        self.account_manager = EnhancedProfileManager()
        self.current_account = None
        self.current_driver = None
    
    def get_fresh_session(self):
        """Get a fresh account and browser session"""
        if self.current_driver:
            self.current_driver.quit()
        
        # Get fresh account with Chrome profile
        self.current_account, self.current_driver = \
            self.account_manager.rotate_to_fresh_account("cmc", max_posts_per_day=10)
        
        return self.current_account, self.current_driver
    
    def post_comment(self, comment_text):
        """Post a comment using current account"""
        success = False
        try:
            # Your posting logic here
            success = self.do_actual_posting(comment_text)
        except Exception as e:
            print(f"Posting failed: {e}")
            # Maybe the account is compromised?
            if "banned" in str(e).lower() or "suspended" in str(e).lower():
                self.account_manager.mark_account_compromised(
                    self.current_account.id, 
                    str(e)
                )
        finally:
            # Update account usage stats
            self.account_manager.database.update_account_usage(
                self.current_account.id, 
                success
            )
        
        return success
```

## 📈 Advanced Features

### Custom Username Generation
```python
# Customize username patterns
manager.username_prefixes = ["myproject", "crypto2024", "trader"]
manager.username_suffixes = ["official", "pro", "alpha"]

account = manager.create_new_account("cmc", custom_username="myproject_alpha_2024")
```

### Platform-Specific Settings
```python
# Different settings per platform
if platform == "cmc":
    max_daily_posts = 15
elif platform == "twitter":
    max_daily_posts = 50

fresh_account = manager.rotate_to_fresh_account(platform, max_daily_posts)
```

### Account Pool Management
```python
# Pre-create a pool of accounts
accounts = manager.create_multiple_accounts("cmc", 10)

# Always ensure minimum pool size
active_count = len(manager.database.get_accounts_by_platform("cmc", "active"))
if active_count < 5:
    new_accounts = manager.create_multiple_accounts("cmc", 5)
```

## 🔒 Security & Privacy

- **Email Privacy**: Your real email stays hidden behind SimpleLogin aliases
- **Password Security**: Auto-generated strong passwords per account
- **Proxy Integration**: Works with your existing proxy rotation system
- **Account Isolation**: Each account has its own Chrome profile
- **Database Encryption**: Store sensitive data securely (implement as needed)

## 🐛 Troubleshooting

### Common Issues

**"SimpleLogin API key not configured"**
```bash
python setup_simplelogin.py
```

**"Failed to create SimpleLogin alias"**
- Check your SimpleLogin plan limits
- Verify API key is correct
- Check internet connection

**"Chrome profile creation failed"**
- Ensure Chrome is installed and updated
- Check Chrome profile directory permissions
- Close all Chrome instances before running

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now run your script for detailed logs
```

## 📝 Configuration Files

The system creates these config files:
- `config/simplelogin.json` - API configuration
- `config/accounts.db` - SQLite database
- Environment variable `SIMPLELOGIN_API_KEY`

## 🎯 Best Practices for Maximum Effectiveness

1. **Rotate Frequently**: Switch accounts every 5-10 posts
2. **Monitor Success Rates**: Create new accounts when success rate drops
3. **Use Realistic Limits**: Don't exceed platform posting limits
4. **Vary Timing**: Space out account creation and usage
5. **Monitor Account Health**: Watch for suspension patterns
6. **Clean Up Regularly**: Remove old inactive accounts

## 📊 Success Metrics

Track these metrics to optimize your strategy:
- Account creation success rate
- Average account lifespan
- Post success rate per account
- Detection/suspension rate
- Engagement effectiveness

## 🔮 Future Enhancements

Planned features:
- Twitter account automation
- Phone number management (when SimpleLogin adds it)
- Advanced account warming strategies
- Machine learning for optimal rotation timing
- Account marketplace integration

---

## 🆘 Need Help?

This system integrates with your existing CMC automation. If you need help customizing it for your specific use case, the code is well-documented and modular.

**Key Files:**
- `services/account_manager.py` - Core account management
- `enhanced_profile_manager.py` - Chrome integration  
- `config/simplelogin_config.py` - Configuration management
- `scripts/account_management_demo.py` - Examples and demos 