import sqlite3
import json
import requests
import random
import string
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import os
import sys

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from autocrypto_social_bot.services.enhanced_simplelogin_client import EnhancedSimpleLoginAPI

@dataclass
class Account:
    """Represents a social media account with all its details"""
    id: Optional[int] = None
    email_alias: str = ""
    password: str = ""
    username: str = ""
    platform: str = ""  # 'cmc', 'twitter', etc.
    profile_name: str = ""  # Chrome profile name
    created_at: datetime = None
    last_used: datetime = None
    status: str = "active"  # active, suspended, banned, disabled
    posts_today: int = 0
    total_posts: int = 0
    success_rate: float = 100.0
    notes: str = ""
    simplelogin_alias_id: Optional[int] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_used is None:
            self.last_used = datetime.now()

class AccountDatabase:
    """SQLite database manager for account storage"""
    
    def __init__(self, db_path: str = "config/accounts.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_alias TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    username TEXT,
                    platform TEXT NOT NULL,
                    profile_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    posts_today INTEGER DEFAULT 0,
                    total_posts INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 100.0,
                    notes TEXT,
                    simplelogin_alias_id INTEGER
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS account_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    date TEXT,
                    posts_count INTEGER DEFAULT 0,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_platform 
                ON accounts (platform)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_accounts_status 
                ON accounts (status)
            """)
    
    def add_account(self, account: Account) -> int:
        """Add a new account to the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO accounts (
                    email_alias, password, username, platform, profile_name,
                    created_at, last_used, status, posts_today, total_posts,
                    success_rate, notes, simplelogin_alias_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                account.email_alias, account.password, account.username,
                account.platform, account.profile_name, account.created_at,
                account.last_used, account.status, account.posts_today,
                account.total_posts, account.success_rate, account.notes,
                account.simplelogin_alias_id
            ))
            return cursor.lastrowid
    
    def get_account(self, account_id: int) -> Optional[Account]:
        """Get an account by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM accounts WHERE id = ?
            """, (account_id,))
            row = cursor.fetchone()
            
            if row:
                return Account(**dict(row))
            return None
    
    def get_accounts_by_platform(self, platform: str, status: str = "active") -> List[Account]:
        """Get all accounts for a specific platform"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM accounts 
                WHERE platform = ? AND status = ?
                ORDER BY last_used ASC
            """, (platform, status))
            return [Account(**dict(row)) for row in cursor.fetchall()]
    
    def get_least_used_account(self, platform: str) -> Optional[Account]:
        """Get the least recently used account for a platform"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM accounts 
                WHERE platform = ? AND status = 'active'
                ORDER BY last_used ASC, posts_today ASC
                LIMIT 1
            """, (platform,))
            row = cursor.fetchone()
            
            if row:
                return Account(**dict(row))
            return None
    
    def update_account_usage(self, account_id: int, success: bool = True):
        """Update account usage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            # Update last_used and posts_today
            conn.execute("""
                UPDATE accounts 
                SET last_used = ?, posts_today = posts_today + 1,
                    total_posts = total_posts + 1
                WHERE id = ?
            """, (datetime.now(), account_id))
            
            # Update success rate
            if success:
                conn.execute("""
                    UPDATE accounts 
                    SET success_rate = (
                        SELECT (success_count * 100.0 / (success_count + failure_count))
                        FROM (
                            SELECT 
                                SUM(success_count) as success_count,
                                SUM(failure_count) as failure_count
                            FROM account_stats 
                            WHERE account_id = ?
                        )
                    )
                    WHERE id = ?
                """, (account_id, account_id))
    
    def reset_daily_counts(self):
        """Reset daily post counts (call this daily)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE accounts SET posts_today = 0")
    
    def mark_account_status(self, account_id: int, status: str, notes: str = ""):
        """Mark an account with a specific status"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE accounts 
                SET status = ?, notes = ?, last_used = ?
                WHERE id = ?
            """, (status, notes, datetime.now(), account_id))
    
    def update_account_profile(self, account_id: int, profile_name: str):
        """Update the Chrome profile name for an account"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE accounts 
                SET profile_name = ?, last_used = ?
                WHERE id = ?
            """, (profile_name, datetime.now(), account_id))
    
    def get_account_stats(self) -> Dict:
        """Get overall account statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    platform,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                    SUM(CASE WHEN status = 'suspended' THEN 1 ELSE 0 END) as suspended,
                    SUM(CASE WHEN status = 'banned' THEN 1 ELSE 0 END) as banned,
                    AVG(success_rate) as avg_success_rate,
                    SUM(total_posts) as total_posts
                FROM accounts
                GROUP BY platform
            """)
            
            stats = {}
            for row in cursor.fetchall():
                stats[row[0]] = {
                    'total': row[1],
                    'active': row[2],
                    'suspended': row[3],
                    'banned': row[4],
                    'avg_success_rate': round(row[5] or 0, 2),
                    'total_posts': row[6]
                }
            
            return stats

class AutomatedAccountManager:
    """Main class for automated account creation and management"""
    
    def __init__(self, simplelogin_api_key: str):
        self.simplelogin = EnhancedSimpleLoginAPI(simplelogin_api_key)
        self.database = AccountDatabase()
        self.logger = logging.getLogger(__name__)
        
        # Password generation settings
        self.password_length = 16
        self.password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
        
        # Username generation settings
        self.username_prefixes = [
            "crypto", "trader", "investor", "hodler", "finance", "digital",
            "block", "chain", "coin", "token", "defi", "web3", "tech",
            "market", "trend", "bull", "bear", "moon", "rocket", "gem"
        ]
        self.username_suffixes = [
            "2024", "2025", "pro", "expert", "master", "king", "queen",
            "boss", "alpha", "beta", "prime", "elite", "ace", "star",
            "legend", "hero", "ninja", "guru", "wizard", "genius"
        ]
    
    def generate_password(self) -> str:
        """Generate a secure random password"""
        return ''.join(random.choices(self.password_chars, k=self.password_length))
    
    def generate_username(self, platform: str = "cmc") -> str:
        """Generate a random username for the platform"""
        prefix = random.choice(self.username_prefixes)
        suffix = random.choice(self.username_suffixes)
        number = random.randint(100, 9999)
        
        # Platform-specific adjustments
        if platform == "cmc":
            return f"{prefix}_{suffix}_{number}"
        elif platform == "twitter":
            return f"{prefix}{suffix}{number}"
        else:
            return f"{prefix}_{suffix}_{number}"
    
    def create_new_account(self, platform: str = "cmc", custom_username: str = None) -> Account:
        """Create a new account with SimpleLogin alias"""
        try:
            # Generate account details
            username = custom_username or self.generate_username(platform)
            password = self.generate_password()
            
            # Create SimpleLogin alias using enhanced client
            alias_note = f"Account for {platform} - {username} - Created {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            alias_response = self.simplelogin.create_random_alias(
                hostname=f"{platform}.com", 
                note=alias_note
            )
            
            if not alias_response:
                raise Exception("Failed to create SimpleLogin alias")
            
            # Extract email from enhanced client response
            email_alias = alias_response.get('alias') if isinstance(alias_response, dict) else alias_response.email
            alias_id = alias_response.get('id') if isinstance(alias_response, dict) else alias_response.id
            
            # Create account object
            account = Account(
                email_alias=email_alias,
                password=password,
                username=username,
                platform=platform,
                simplelogin_alias_id=alias_id,
                notes=f"Auto-created with SimpleLogin alias ID: {alias_id}"
            )
            
            # Save to database
            account.id = self.database.add_account(account)
            
            self.logger.info(f"✅ Created new {platform} account: {username} ({account.email_alias})")
            return account
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create new account: {e}")
            raise
    
    def create_multiple_accounts(self, platform: str, count: int) -> List[Account]:
        """Create multiple accounts for a platform"""
        accounts = []
        
        for i in range(count):
            try:
                account = self.create_new_account(platform)
                accounts.append(account)
                
                # Add delay between creations to avoid rate limiting
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                self.logger.error(f"Failed to create account {i+1}/{count}: {e}")
                continue
        
        return accounts
    
    def get_next_account(self, platform: str, auto_create: bool = False) -> Optional[Account]:
        """Get the next account to use for posting"""
        # Try to get least used account
        account = self.database.get_least_used_account(platform)
        
        if not account:
            if auto_create:
                # Create new account if none available (only when explicitly requested)
                self.logger.info(f"No accounts available for {platform}, creating new one...")
                account = self.create_new_account(platform)
            else:
                # Don't create new accounts automatically
                self.logger.warning(f"No accounts available for {platform}. Please create accounts manually.")
                return None
        
        return account
    
    def rotate_to_fresh_account(self, platform: str, max_posts_per_day: int = 10, auto_create: bool = False) -> Optional[Account]:
        """Get a fresh account that hasn't exceeded daily post limit"""
        accounts = self.database.get_accounts_by_platform(platform, "active")
        
        # Filter accounts that haven't exceeded daily limit
        fresh_accounts = [acc for acc in accounts if acc.posts_today < max_posts_per_day]
        
        if not fresh_accounts:
            if auto_create:
                # Create new account if all are exhausted (only when explicitly requested)
                self.logger.info(f"All {platform} accounts exhausted, creating fresh account...")
                return self.create_new_account(platform)
            else:
                # Don't create new accounts automatically - use least used existing account
                self.logger.warning(f"All {platform} accounts exhausted (>{max_posts_per_day} posts). Using least used account.")
                if accounts:
                    return min(accounts, key=lambda x: (x.posts_today, x.last_used))
                else:
                    self.logger.error(f"No accounts available for {platform}. Please create accounts manually.")
                    return None
        
        # Return the least used fresh account
        return min(fresh_accounts, key=lambda x: (x.posts_today, x.last_used))
    
    def mark_account_compromised(self, account_id: int, reason: str = ""):
        """Mark an account as compromised/suspended"""
        self.database.mark_account_status(account_id, "suspended", f"Compromised: {reason}")
        self.logger.warning(f"⚠️ Account {account_id} marked as compromised: {reason}")
    
    def cleanup_old_accounts(self, days_inactive: int = 30):
        """Clean up old inactive accounts"""
        cutoff_date = datetime.now() - timedelta(days=days_inactive)
        
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.execute("""
                SELECT * FROM accounts 
                WHERE last_used < ? AND status = 'active'
            """, (cutoff_date,))
            
            old_accounts = cursor.fetchall()
            
            for account in old_accounts:
                # Disable SimpleLogin alias
                if account[13]:  # simplelogin_alias_id
                    try:
                        self.simplelogin.toggle_alias(account[13])
                    except Exception as e:
                        self.logger.error(f"Failed to disable alias for account {account[0]}: {e}")
                
                # Mark as inactive
                self.database.mark_account_status(account[0], "inactive", "Auto-cleanup due to inactivity")
            
            self.logger.info(f"🧹 Cleaned up {len(old_accounts)} inactive accounts")
    
    def get_all_used_emails(self) -> List[str]:
        """Get all email aliases currently in use by accounts"""
        with sqlite3.connect(self.database.db_path) as conn:
            cursor = conn.execute("SELECT email_alias FROM accounts WHERE status != 'inactive'")
            return [row[0] for row in cursor.fetchall()]
    
    def get_stats_summary(self) -> Dict:
        """Get comprehensive account statistics"""
        stats = self.database.get_account_stats()
        
        # Add SimpleLogin stats using enhanced client
        try:
            simplelogin_stats = self.simplelogin.get_alias_statistics()
            stats['simplelogin'] = simplelogin_stats
        except Exception as e:
            self.logger.error(f"Failed to get SimpleLogin stats: {e}")
        
        return stats
    
    def perform_maintenance(self):
        """Perform routine maintenance tasks"""
        self.logger.info("🔧 Performing account maintenance...")
        
        # Reset daily counts if it's a new day
        self.database.reset_daily_counts()
        
        # Clean up old accounts
        self.cleanup_old_accounts()
        
        # Log current stats
        stats = self.get_stats_summary()
        self.logger.info(f"📊 Current account stats: {json.dumps(stats, indent=2)}")
        
        self.logger.info("✅ Maintenance completed")

# Example usage and testing functions
def demo_account_creation():
    """Demo function showing how to use the account manager"""
    # You'll need to set your SimpleLogin API key
    API_KEY = os.getenv('SIMPLELOGIN_API_KEY', 'your_api_key_here')
    
    if API_KEY == 'your_api_key_here':
        print("❌ Please set your SIMPLELOGIN_API_KEY environment variable")
        return
    
    manager = AutomatedAccountManager(API_KEY)
    
    print("🚀 Creating new CMC account...")
    account = manager.create_new_account("cmc")
    print(f"✅ Created: {account.username} ({account.email_alias})")
    
    print("\n📊 Account statistics:")
    stats = manager.get_stats_summary()
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    demo_account_creation() 