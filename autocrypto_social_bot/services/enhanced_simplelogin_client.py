"""
Enhanced SimpleLogin API Client

Based on the official SimpleLogin repository at https://github.com/simple-login/app
This implementation incorporates best practices from their codebase while maintaining
simplicity for automation use cases.
"""

import requests
import json
import logging
import time
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import urllib.parse
from enum import Enum

class AliasActivity(Enum):
    """Alias activity types"""
    FORWARD = "forward"
    REPLY = "reply"
    BLOCK = "block"
    BOUNCED = "bounced"

class AliasStatus(Enum):
    """Alias status types"""
    ENABLED = True
    DISABLED = False

@dataclass
class Mailbox:
    """Represents a SimpleLogin mailbox"""
    id: int
    email: str
    verified: bool = True
    default: bool = False
    creation_timestamp: Optional[int] = None
    nb_alias: Optional[int] = None

@dataclass
class Contact:
    """Represents a contact for an alias"""
    id: int
    creation_date: str
    creation_timestamp: int
    last_email_sent_date: Optional[str]
    last_email_sent_timestamp: Optional[int]
    contact: str
    reverse_alias: str
    block_forward: bool = False

@dataclass
class AliasInfo:
    """Comprehensive alias information"""
    id: int
    email: str
    creation_date: str
    creation_timestamp: int
    nb_forward: int
    nb_block: int
    nb_reply: int
    enabled: bool
    note: Optional[str] = None
    name: Optional[str] = None
    pinned: bool = False
    mailbox: Optional[Mailbox] = None
    mailboxes: Optional[List[Mailbox]] = None
    latest_activity: Optional[Dict] = None
    disable_pgp: bool = False

@dataclass
class ApiResponse:
    """Standard API response wrapper"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    status_code: int = 200

class SimpleLoginAPIError(Exception):
    """Custom exception for SimpleLogin API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)

class RateLimiter:
    """Simple rate limiter to respect API limits"""
    def __init__(self, max_requests: int = 50, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        if len(self.requests) >= self.max_requests:
            # Wait until the oldest request is outside the window
            wait_time = self.time_window - (now - self.requests[0]) + 1
            if wait_time > 0:
                logging.info(f"Rate limit reached, waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
        
        self.requests.append(now)

class EnhancedSimpleLoginAPI:
    """
    Enhanced SimpleLogin API client with comprehensive functionality
    
    Based on the official SimpleLogin repository:
    https://github.com/simple-login/app
    
    Features:
    - Comprehensive alias management
    - Mailbox management  
    - Contact management
    - Rate limiting
    - Enhanced error handling
    - Activity tracking
    - Custom domains support (premium feature)
    """
    
    def __init__(self, api_key: str, base_url: str = "https://app.simplelogin.io/api"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authentication': api_key,
            'Content-Type': 'application/json',
            'User-Agent': 'Enhanced-SimpleLogin-Client/1.0'
        })
        self.logger = logging.getLogger(__name__)
        self.rate_limiter = RateLimiter()
        
        # Validate API key on initialization
        self._validate_api_key()
    
    def _validate_api_key(self):
        """Validate the API key by making a test request"""
        try:
            self.get_user_info()
            self.logger.info("✅ SimpleLogin API key validated successfully")
        except Exception as e:
            raise SimpleLoginAPIError(f"Invalid API key: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make an API request with enhanced error handling and rate limiting"""
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle different response types
            if response.headers.get('content-type', '').startswith('application/json'):
                data = response.json()
            else:
                data = response.text
            
            if response.status_code >= 400:
                error_msg = data.get('error', f'HTTP {response.status_code}') if isinstance(data, dict) else str(data)
                raise SimpleLoginAPIError(
                    error_msg, 
                    response.status_code, 
                    data if isinstance(data, dict) else {}
                )
            
            return data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise SimpleLoginAPIError(f"Request failed: {str(e)}")
    
    # USER MANAGEMENT
    def get_user_info(self) -> Dict:
        """Get user information"""
        return self._make_request('GET', '/user_info')
    
    def get_stats(self) -> Dict:
        """Get user statistics"""
        return self._make_request('GET', '/stats')
    
    # ALIAS MANAGEMENT
    def get_aliases(self, page_id: int = 0, query: str = None, sort: str = None) -> Dict:
        """
        Get aliases with pagination and filtering
        
        Args:
            page_id: Page number (0-based)
            query: Search query for alias filtering
            sort: Sort order (old_to_new, new_to_old, a_to_z, z_to_a)
        """
        params = {'page_id': page_id}
        if query:
            params['query'] = query
        if sort:
            params['sort'] = sort
            
        return self._make_request('GET', '/aliases', params=params)
    
    def create_random_alias(self, hostname: str = None, note: str = None, mailbox_ids: List[int] = None) -> AliasInfo:
        """
        Create a random alias
        
        Args:
            hostname: The hostname for the alias (used for suggestions)
            note: Note for the alias
            mailbox_ids: List of mailbox IDs to associate with the alias
        """
        data = {}
        if hostname:
            data['hostname'] = hostname
        if note:
            data['note'] = note
        if mailbox_ids:
            data['mailbox_ids'] = mailbox_ids
            
        response = self._make_request('POST', '/alias/random/new', json=data)
        # Remove extra fields that aren't in AliasInfo dataclass
        extra_fields = ['alias', 'support_pgp']
        for field in extra_fields:
            if field in response:
                response.pop(field)
        return AliasInfo(**response)
    
    def create_custom_alias(self, alias_prefix: str, signed_suffix: str = None, 
                          mailbox_ids: List[int] = None, note: str = None, 
                          name: str = None) -> AliasInfo:
        """
        Create a custom alias
        
        Args:
            alias_prefix: The prefix part of the alias
            signed_suffix: The signed suffix from get_alias_options
            mailbox_ids: List of mailbox IDs
            note: Note for the alias
            name: Display name for the alias
        """
        data = {
            'alias_prefix': alias_prefix
        }
        if signed_suffix:
            data['signed_suffix'] = signed_suffix
        if mailbox_ids:
            data['mailbox_ids'] = mailbox_ids
        if note:
            data['note'] = note
        if name:
            data['name'] = name
            
        response = self._make_request('POST', '/alias/custom', json=data)
        return AliasInfo(**response)
    
    def get_alias_options(self, hostname: str = None) -> Dict:
        """Get available options for creating custom aliases"""
        params = {}
        if hostname:
            params['hostname'] = hostname
            
        response = self._make_request('GET', '/alias/options', params=params)
        return response
    
    def get_alias(self, alias_id: int) -> AliasInfo:
        """Get detailed information about a specific alias"""
        response = self._make_request('GET', f'/aliases/{alias_id}')
        return AliasInfo(**response)
    
    def update_alias(self, alias_id: int, note: str = None, mailbox_ids: List[int] = None,
                    name: str = None, disable_pgp: bool = None) -> AliasInfo:
        """Update an alias"""
        data = {}
        if note is not None:
            data['note'] = note
        if mailbox_ids is not None:
            data['mailbox_ids'] = mailbox_ids
        if name is not None:
            data['name'] = name
        if disable_pgp is not None:
            data['disable_pgp'] = disable_pgp
            
        response = self._make_request('PATCH', f'/aliases/{alias_id}', json=data)
        return AliasInfo(**response)
    
    def toggle_alias(self, alias_id: int) -> AliasInfo:
        """Toggle alias enabled/disabled status"""
        response = self._make_request('POST', f'/aliases/{alias_id}/toggle')
        return AliasInfo(**response)
    
    def delete_alias(self, alias_id: int) -> Dict:
        """Delete an alias"""
        response = self._make_request('DELETE', f'/aliases/{alias_id}')
        return response
    
    def get_alias_activities(self, alias_id: int, page_id: int = 0) -> Dict:
        """Get activities for a specific alias"""
        params = {'page_id': page_id}
        response = self._make_request('GET', f'/aliases/{alias_id}/activities', params=params)
        return response
    
    # MAILBOX MANAGEMENT
    def get_mailboxes(self) -> List[Mailbox]:
        """Get all mailboxes"""
        response = self._make_request('GET', '/mailboxes')
        return [Mailbox(**mailbox) for mailbox in response['mailboxes']]
    
    def create_mailbox(self, email: str) -> Mailbox:
        """Create a new mailbox"""
        data = {'email': email}
        response = self._make_request('POST', '/mailboxes', json=data)
        return Mailbox(**response)
    
    def delete_mailbox(self, mailbox_id: int) -> Dict:
        """Delete a mailbox"""
        response = self._make_request('DELETE', f'/mailboxes/{mailbox_id}')
        return response
    
    def update_mailbox(self, mailbox_id: int, default: bool = None, 
                      cancel_email_change: bool = None) -> Mailbox:
        """Update mailbox settings"""
        data = {}
        if default is not None:
            data['default'] = default
        if cancel_email_change is not None:
            data['cancel_email_change'] = cancel_email_change
            
        response = self._make_request('PUT', f'/mailboxes/{mailbox_id}', json=data)
        return Mailbox(**response)
    
    # CONTACT MANAGEMENT
    def get_alias_contacts(self, alias_id: int, page_id: int = 0) -> Dict:
        """Get contacts for a specific alias"""
        params = {'page_id': page_id}
        response = self._make_request('GET', f'/aliases/{alias_id}/contacts', params=params)
        return response
    
    def create_contact(self, alias_id: int, contact: str) -> Contact:
        """Create a new contact for an alias"""
        data = {'contact': contact}
        response = self._make_request('POST', f'/aliases/{alias_id}/contacts', json=data)
        return Contact(**response)
    
    def toggle_contact(self, contact_id: int) -> Contact:
        """Toggle contact block status"""
        response = self._make_request('POST', f'/contacts/{contact_id}/toggle')
        return Contact(**response)
    
    def delete_contact(self, contact_id: int) -> Dict:
        """Delete a contact"""
        response = self._make_request('DELETE', f'/contacts/{contact_id}')
        return response
    
    # CUSTOM DOMAINS (Premium feature)
    def get_custom_domains(self) -> List[Dict]:
        """Get custom domains (premium feature)"""
        response = self._make_request('GET', '/custom_domains')
        return response.get('custom_domains', [])
    
    def create_custom_domain(self, domain: str) -> Dict:
        """Create a custom domain (premium feature)"""
        data = {'domain': domain}
        response = self._make_request('POST', '/custom_domains', json=data)
        return response
    
    # SETTINGS
    def get_settings(self) -> Dict:
        """Get user settings"""
        response = self._make_request('GET', '/setting')
        return response
    
    def update_settings(self, **kwargs) -> Dict:
        """Update user settings"""
        response = self._make_request('PATCH', '/setting', json=kwargs)
        return response
    
    # UTILITY METHODS
    def search_aliases(self, query: str, limit: int = 20) -> List[Dict]:
        """Search aliases by query"""
        all_aliases = []
        page = 0
        
        while len(all_aliases) < limit:
            result = self.get_aliases(page_id=page, query=query)
            aliases = result.get('aliases', [])
            
            if not aliases:
                break
                
            all_aliases.extend(aliases)
            page += 1
            
            if not result.get('more', False):
                break
        
        return all_aliases[:limit]
    
    def get_alias_by_email(self, email: str) -> Optional[AliasInfo]:
        """Get alias by email address"""
        aliases = self.search_aliases(email, limit=1)
        if aliases:
            return AliasInfo(**aliases[0])
        return None
    
    def bulk_create_aliases(self, count: int, hostname: str = None, 
                          note_prefix: str = "Bulk created") -> List[AliasInfo]:
        """Create multiple random aliases"""
        aliases = []
        
        for i in range(count):
            note = f"{note_prefix} {i+1}/{count}" if note_prefix else None
            try:
                alias = self.create_random_alias(hostname=hostname, note=note)
                aliases.append(alias)
                self.logger.info(f"Created alias {i+1}/{count}: {alias.email}")
                
                # Small delay to be nice to the API
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.error(f"Failed to create alias {i+1}/{count}: {e}")
                
        return aliases
    
    def get_alias_statistics(self) -> Dict:
        """Get comprehensive alias statistics"""
        stats = self.get_stats()
        user_info = self.get_user_info()
        
        return {
            'total_aliases': stats.get('nb_alias', 0),
            'enabled_aliases': stats.get('nb_enabled_alias', 0), 
            'disabled_aliases': stats.get('nb_alias', 0) - stats.get('nb_enabled_alias', 0),
            'total_forwards': stats.get('nb_forward', 0),
            'total_blocks': stats.get('nb_block', 0),
            'total_replies': stats.get('nb_reply', 0),
            'premium': user_info.get('is_premium', False),
            'alias_limit': user_info.get('max_alias_free_plan', 15) if not user_info.get('is_premium') else 'unlimited'
        }
    
    def cleanup_inactive_aliases(self, days_inactive: int = 30, dry_run: bool = True) -> List[Dict]:
        """
        Find aliases that haven't been used recently
        
        Args:
            days_inactive: Number of days to consider as inactive
            dry_run: If True, only return aliases that would be deleted
        """
        cutoff_timestamp = int(time.time()) - (days_inactive * 24 * 60 * 60)
        inactive_aliases = []
        
        page = 0
        while True:
            result = self.get_aliases(page_id=page)
            aliases = result.get('aliases', [])
            
            if not aliases:
                break
                
            for alias_data in aliases:
                alias = AliasInfo(**alias_data)
                
                # Check if alias has been inactive
                if (alias.latest_activity and 
                    alias.latest_activity.get('timestamp', 0) < cutoff_timestamp):
                    
                    inactive_aliases.append({
                        'id': alias.id,
                        'email': alias.email,
                        'last_activity': alias.latest_activity,
                        'note': alias.note
                    })
                    
                    if not dry_run:
                        try:
                            self.delete_alias(alias.id)
                            self.logger.info(f"Deleted inactive alias: {alias.email}")
                        except Exception as e:
                            self.logger.error(f"Failed to delete alias {alias.email}: {e}")
            
            if not result.get('more', False):
                break
                
            page += 1
        
        return inactive_aliases
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.session.close()

# Example usage and testing
if __name__ == "__main__":
    import os
    
    # Example usage
    api_key = os.getenv('SIMPLELOGIN_API_KEY')
    if not api_key:
        print("Please set SIMPLELOGIN_API_KEY environment variable")
        exit(1)
    
    with EnhancedSimpleLoginAPI(api_key) as client:
        # Get user info
        user_info = client.get_user_info()
        print(f"User: {user_info.get('name', 'N/A')}")
        
        # Get statistics
        stats = client.get_alias_statistics()
        print(f"Aliases: {stats['total_aliases']}")
        
        # Create a test alias
        alias = client.create_random_alias(note="Test from enhanced client")
        print(f"Created: {alias.email}")
        
        # Clean up
        client.delete_alias(alias.id)
        print("Cleaned up test alias") 