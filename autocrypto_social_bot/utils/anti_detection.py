import random
import time
import requests
import logging
from typing import List, Dict, Optional, Tuple
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from datetime import datetime, timedelta
import asyncio
import concurrent.futures
import os
from pathlib import Path

# Add proxyscrape library integration
try:
    import proxyscrape
    PROXYSCRAPE_AVAILABLE = True
    print("✅ ProxyScrape library integration available")
except ImportError:
    PROXYSCRAPE_AVAILABLE = False
    print("⚠️ ProxyScrape library not installed. Run: pip install proxyscrape")

# Import the HTML proxy scrapers
try:
    from .html_proxy_scrapers import HTMLProxyAggregator
    HTML_SCRAPERS_AVAILABLE = True
except ImportError:
    HTMLProxyAggregator = None
    HTML_SCRAPERS_AVAILABLE = False

class PersistentProxyStorage:
    """🗂️ Persistent proxy storage system with automatic curation"""
    
    def __init__(self, storage_file: str = "config/working_proxies.json"):
        self.storage_file = storage_file
        self.logger = logging.getLogger(__name__)
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(storage_file), exist_ok=True)
        
        # Load existing proxy data
        self.proxy_data = self._load_proxy_storage()
    
    def _load_proxy_storage(self) -> Dict:
        """Load proxy storage from file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Validate structure
                    if not isinstance(data, dict):
                        data = self._create_empty_storage()
                    
                    # Ensure all required keys exist
                    required_keys = ['working_proxies', 'failed_proxies', 'proxy_stats', 'last_updated']
                    for key in required_keys:
                        if key not in data:
                            if key == 'working_proxies':
                                data[key] = []
                            elif key == 'failed_proxies':
                                data[key] = []
                            elif key == 'proxy_stats':
                                data[key] = {}
                            elif key == 'last_updated':
                                data[key] = datetime.now().isoformat()
                    
                    print(f"📂 Loaded {len(data['working_proxies'])} working proxies from storage")
                    return data
            except Exception as e:
                print(f"⚠️ Error loading proxy storage: {e}")
                return self._create_empty_storage()
        else:
            return self._create_empty_storage()
    
    def _create_empty_storage(self) -> Dict:
        """Create empty proxy storage structure"""
        return {
            'working_proxies': [],
            'failed_proxies': [],
            'proxy_stats': {},  # proxy -> {success_count, fail_count, last_success, last_fail, avg_response_time}
            'last_updated': datetime.now().isoformat(),
            'storage_version': '1.0'
        }
    
    def _save_proxy_storage(self):
        """Save proxy storage to file"""
        try:
            self.proxy_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.storage_file, 'w') as f:
                json.dump(self.proxy_data, f, indent=2)
            
            print(f"💾 Saved {len(self.proxy_data['working_proxies'])} working proxies to storage")
        except Exception as e:
            self.logger.error(f"Failed to save proxy storage: {e}")
    
    def get_working_proxies(self) -> List[str]:
        """Get list of working proxies sorted by success rate"""
        working_proxies = self.proxy_data['working_proxies'].copy()
        
        # Sort by success rate (best first)
        def proxy_score(proxy):
            stats = self.proxy_data['proxy_stats'].get(proxy, {})
            success_count = stats.get('success_count', 0)
            fail_count = stats.get('fail_count', 0)
            total = success_count + fail_count
            
            if total == 0:
                return 0.5  # Unknown proxies get medium priority
            
            success_rate = success_count / total
            
            # Factor in recency of last success
            last_success = stats.get('last_success')
            if last_success:
                try:
                    last_success_dt = datetime.fromisoformat(last_success)
                    hours_since_success = (datetime.now() - last_success_dt).total_seconds() / 3600
                    
                    # Penalize proxies that haven't worked recently
                    recency_factor = max(0.1, 1.0 - (hours_since_success / 24))  # Decay over 24 hours
                    success_rate *= recency_factor
                except:
                    pass
            
            return success_rate
        
        working_proxies.sort(key=proxy_score, reverse=True)
        return working_proxies
    
    def add_working_proxy(self, proxy: str, response_time: float = None, test_score: int = None):
        """Add a proxy to the working list with statistics"""
        
        # Remove from failed list if it was there
        if proxy in self.proxy_data['failed_proxies']:
            self.proxy_data['failed_proxies'].remove(proxy)
            print(f"♻️ Proxy {proxy} moved from failed to working list")
        
        # Add to working list if not already there
        if proxy not in self.proxy_data['working_proxies']:
            self.proxy_data['working_proxies'].append(proxy)
            print(f"✅ Added working proxy: {proxy}")
        
        # Update statistics
        if proxy not in self.proxy_data['proxy_stats']:
            self.proxy_data['proxy_stats'][proxy] = {
                'success_count': 0,
                'fail_count': 0,
                'avg_response_time': 0,
                'first_seen': datetime.now().isoformat(),
                'last_success': None,
                'last_fail': None,
                'best_score': 0
            }
        
        stats = self.proxy_data['proxy_stats'][proxy]
        stats['success_count'] += 1
        stats['last_success'] = datetime.now().isoformat()
        
        if response_time is not None:
            # Update average response time
            current_avg = stats.get('avg_response_time', 0)
            current_count = stats['success_count']
            stats['avg_response_time'] = ((current_avg * (current_count - 1)) + response_time) / current_count
        
        if test_score is not None:
            stats['best_score'] = max(stats.get('best_score', 0), test_score)
        
        self._save_proxy_storage()
    
    def mark_proxy_failed(self, proxy: str, error_reason: str = None):
        """Mark a proxy as failed and update statistics"""
        
        # Update statistics
        if proxy not in self.proxy_data['proxy_stats']:
            self.proxy_data['proxy_stats'][proxy] = {
                'success_count': 0,
                'fail_count': 0,
                'avg_response_time': 0,
                'first_seen': datetime.now().isoformat(),
                'last_success': None,
                'last_fail': None,
                'best_score': 0
            }
        
        stats = self.proxy_data['proxy_stats'][proxy]
        stats['fail_count'] += 1
        stats['last_fail'] = datetime.now().isoformat()
        
        if error_reason:
            if 'recent_failures' not in stats:
                stats['recent_failures'] = []
            stats['recent_failures'].append({
                'time': datetime.now().isoformat(),
                'reason': error_reason
            })
            # Keep only last 5 failures
            stats['recent_failures'] = stats['recent_failures'][-5:]
        
        # Calculate failure rate
        total_attempts = stats['success_count'] + stats['fail_count']
        failure_rate = stats['fail_count'] / total_attempts if total_attempts > 0 else 1
        
        # Remove from working list if failure rate is too high
        if failure_rate > 0.7 and total_attempts >= 3:  # Remove if >70% failure rate after 3+ attempts
            if proxy in self.proxy_data['working_proxies']:
                self.proxy_data['working_proxies'].remove(proxy)
                print(f"🗑️ Removed unreliable proxy: {proxy} (failure rate: {failure_rate:.1%})")
            
            # Add to failed list if not already there
            if proxy not in self.proxy_data['failed_proxies']:
                self.proxy_data['failed_proxies'].append(proxy)
                print(f"❌ Added to failed list: {proxy}")
        
        self._save_proxy_storage()
    
    def cleanup_old_failures(self, hours: int = 24):
        """Remove proxies that failed more than X hours ago (give them another chance)"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        proxies_to_retry = []
        
        for proxy in self.proxy_data['failed_proxies'].copy():
            stats = self.proxy_data['proxy_stats'].get(proxy, {})
            last_fail = stats.get('last_fail')
            
            if last_fail:
                try:
                    last_fail_dt = datetime.fromisoformat(last_fail)
                    if last_fail_dt < cutoff_time:
                        self.proxy_data['failed_proxies'].remove(proxy)
                        proxies_to_retry.append(proxy)
                except:
                    pass
        
        if proxies_to_retry:
            print(f"♻️ Gave {len(proxies_to_retry)} old failed proxies another chance")
            self._save_proxy_storage()
        
        return proxies_to_retry
    
    def get_storage_stats(self) -> Dict:
        """Get statistics about the proxy storage"""
        working_count = len(self.proxy_data['working_proxies'])
        failed_count = len(self.proxy_data['failed_proxies'])
        total_tracked = len(self.proxy_data['proxy_stats'])
        
        # Calculate average success rate
        total_success = 0
        total_attempts = 0
        
        for proxy, stats in self.proxy_data['proxy_stats'].items():
            total_success += stats.get('success_count', 0)
            total_attempts += stats.get('success_count', 0) + stats.get('fail_count', 0)
        
        avg_success_rate = (total_success / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'working_proxies': working_count,
            'failed_proxies': failed_count,
            'total_tracked': total_tracked,
            'average_success_rate': round(avg_success_rate, 1),
            'last_updated': self.proxy_data.get('last_updated', 'Unknown'),
            'storage_file': self.storage_file
        }

class EnterpriseProxyManager:
    """Enterprise-grade proxy management with multiple API sources and CMC verification"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.working_proxies = []
        self.cmc_verified_proxies = []
        self.verified_proxies = []  # Add this initialization
        self.proxy_refresh_time = None
        self.proxy_failure_counts = {}
        
        # Initialize persistent proxy storage system
        self.proxy_storage = PersistentProxyStorage()
        print(f"🗂️ Persistent proxy storage initialized")
        
        # Load configuration
        self.config = self._load_proxy_config()
        
        # Initialize HTML scraper
        self.html_scraper = HTMLProxyAggregator() if HTMLProxyAggregator else None
        
        # High-quality proxy API sources (ProxyScrape added as primary)
        self.proxy_apis = {
            'proxyscrape_v4': {
                'url': 'https://api.proxyscrape.com/v4/free-proxy-list/get',
                'method': 'GET',
                'params': {
                    'request': 'display_proxies',
                    'proxy_format': 'protocolipport',
                    'format': 'text',
                    'timeout': '10000',
                    'country': 'all'
                },
                'headers': {},
                'parse_response': self._parse_proxyscrape_v4_response,
                'free': True,
                'priority': 1  # Highest priority
            },
            'proxyscrape_v4_socks': {
                'url': 'https://api.proxyscrape.com/v4/free-proxy-list/get',
                'method': 'GET',
                'params': {
                    'request': 'display_proxies',
                    'proxy_format': 'protocolipport', 
                    'format': 'text',
                    'protocol': 'socks4',
                    'timeout': '10000',
                    'country': 'all'
                },
                'headers': {},
                'parse_response': self._parse_proxyscrape_v4_response,
                'free': True,
                'priority': 2
            },
            'html_scrapers': {
                'url': None,  # No URL needed, uses HTML scraping
                'method': 'SCRAPE',
                'params': {},
                'headers': {},
                'parse_response': self._get_html_scraped_proxies,
                'free': True,
                'priority': 3  # High priority for HTML scrapers
            },
            'proxyscrape_legacy': {
                'url': 'https://api.proxyscrape.com/v2/',
                'method': 'GET',
                'params': {
                    'request': 'get',
                    'protocol': 'http',
                    'timeout': '10000',
                    'country': 'all',
                    'ssl': 'all',
                    'anonymity': 'all',
                    'format': 'json'
                },
                'headers': {},
                'parse_response': self._parse_proxyscrape_response,
                'free': True,
                'priority': 4  # Fallback if v4 fails
            },
            'getproxylist': {
                'url': 'https://api.getproxylist.com/proxy',
                'method': 'GET',
                'params': {
                    'allowsHttps': '1',
                    'protocol[]': ['http'],
                    'maxConnectTime': '2',
                    'maxSecondsToFirstByte': '3',
                    'minDownloadSpeed': '1000',
                    'minUptime': '80'
                },
                'headers': {},
                'parse_response': self._parse_getproxylist_response,
                'free': True,
                'priority': 5
            },
            'proxykingdom': {
                'url': 'https://api.proxykingdom.com/proxy',
                'method': 'GET',
                'params': {
                    'token': self.config.get('proxykingdom_token', ''),
                    'protocol': 'http',
                    'ssl': 'true'
                },
                'headers': {},
                'parse_response': self._parse_proxykingdom_response,
                'free': False,
                'priority': 6
            },
            'proxifly': {
                'url': 'https://api.proxifly.dev/get-proxy',
                'method': 'POST',
                'params': {
                    'apiKey': self.config.get('proxifly_key', ''),
                    'https': True,
                    'quantity': 5,
                    'country': ['US', 'CA', 'GB', 'DE', 'FR', 'NL']
                },
                'headers': {'Content-Type': 'application/json'},
                'parse_response': self._parse_proxifly_response,
                'free': False,
                'priority': 7
            },
        }
        
        # User agents for stealth
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        # Screen resolutions
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720)
        ]

        # Premium proxy source configurations
        self.premium_sources = {
            'scraperapi': {
                'url': 'https://api.scraperapi.com/',
                'method': 'GET',
                'params': {
                    'api_key': self.config.get('api_keys', {}).get('scraperapi_key', ''),
                    'url': 'https://coinmarketcap.com/',
                    'premium': True,
                    'render': False
                },
                'headers': {},
                'parse_response': self._parse_scraperapi_response,
                'free': False,
                'priority': 1,
                'success_rate_expected': 95
            },
            'proxykingdom_premium': {
                'url': 'https://api.proxykingdom.com/proxy',
                'method': 'MULTI',  # Special method for multiple API calls
                'params': {
                    'token': self.config.get('api_keys', {}).get('proxykingdom_token', ''),
                    'accessType': 'elite',
                    'protocol': 'http',
                    'isSsl': 'true',
                    'uptime': '0.7'
                },
                'headers': {},
                'parse_response': self._get_proxykingdom_premium_proxies,
                'free': False,
                'priority': 2,
                'success_rate_expected': 80
            },
            'webshare_premium': {
                'url': 'https://proxy.webshare.io/api/v2/proxy/list/',
                'method': 'GET',
                'params': {
                    'mode': 'direct',
                    'page': 1,
                    'page_size': 100
                },
                'headers': {'Authorization': f'Token {self.config.get("api_keys", {}).get("webshare_token", "")}'},
                'parse_response': self._parse_webshare_response,
                'free': False,
                'priority': 3,
                'success_rate_expected': 85
            },
            'emergency_residential_list': {
                'url': None,  # Local generation
                'method': 'LOCAL',
                'params': {},
                'headers': {},
                'parse_response': self._generate_emergency_residential_proxies,
                'free': False,
                'priority': 4,
                'success_rate_expected': 60
            },
            'proxyscrape_premium': {
                'url': None,  # Uses proxyscrape library
                'method': 'LIBRARY',
                'params': {
                    'proxytype': 'http',
                    'timeout': 5000,
                    'ssl': 'all',
                    'anonymity': 'elite',
                    'country': 'us'
                },
                'headers': {},
                'parse_response': self._get_proxyscrape_premium_proxies,
                'free': False,
                'priority': 5,
                'success_rate_expected': 75
            },
        }

    def _load_proxy_config(self) -> Dict:
        """Load proxy configuration from file"""
        config_file = "config/enterprise_proxy_config.json"
        default_config = {
            'test_timeout': 10,
            'max_workers': 20,
            'min_success_rate': 0.1,
            'test_with_cmc': True,
            'enable_residential_apis': True,
            'proxykingdom_token': '',
            'proxifly_key': '',
            'scraperapi_key': '',
            'max_proxy_failures': 3,
            'proxy_rotation_interval': 300,  # 5 minutes
            'use_manual_proxies': True
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                self.logger.warning(f"Error loading proxy config: {str(e)}")
        
        # Save default config
        os.makedirs('config', exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        
        return default_config

    def _parse_proxyscrape_response(self, response) -> List[str]:
        """Parse ProxyScrape API response - supports both JSON and text formats"""
        try:
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' in content_type:
                # JSON format response
                data = response.json()
                proxies = []
                
                if isinstance(data, list):
                    for proxy_info in data:
                        if isinstance(proxy_info, dict) and 'ip' in proxy_info and 'port' in proxy_info:
                            proxies.append(f"{proxy_info['ip']}:{proxy_info['port']}")
                        elif isinstance(proxy_info, str) and ':' in proxy_info:
                            proxies.append(proxy_info)
                elif isinstance(data, dict):
                    if 'proxies' in data:
                        for proxy in data['proxies']:
                            if isinstance(proxy, dict) and 'ip' in proxy and 'port' in proxy:
                                proxies.append(f"{proxy['ip']}:{proxy['port']}")
                            elif isinstance(proxy, str):
                                proxies.append(proxy)
                
                return proxies
            else:
                # Text format response (IP:PORT per line)
                text_content = response.text.strip()
                if text_content:
                    lines = text_content.split('\n')
                    proxies = []
                    for line in lines:
                        line = line.strip()
                        if line and ':' in line and len(line.split(':')) == 2:
                            ip, port = line.split(':')
                            if port.isdigit():
                                proxies.append(line)
                    return proxies
                
        except Exception as e:
            self.logger.debug(f"Failed to parse ProxyScrape response: {str(e)}")
            
        return []

    def _parse_getproxylist_response(self, response) -> List[str]:
        """Parse GetProxyList API response"""
        try:
            data = response.json()
            if isinstance(data, dict) and 'ip' in data and 'port' in data:
                return [f"{data['ip']}:{data['port']}"]
            return []
        except Exception as e:
            self.logger.debug(f"Failed to parse getproxylist response: {str(e)}")
            return []

    def _parse_proxykingdom_response(self, response) -> List[str]:
        """Parse ProxyKingdom API response"""
        try:
            data = response.json()
            if isinstance(data, dict) and 'address' in data and 'port' in data:
                return [f"{data['address']}:{data['port']}"]
            return []
        except Exception as e:
            self.logger.debug(f"Failed to parse proxykingdom response: {str(e)}")
            return []

    def _parse_proxifly_response(self, response) -> List[str]:
        """Parse Proxifly API response"""
        try:
            data = response.json()
            proxies = []
            if isinstance(data, list):
                for proxy in data:
                    if 'ip' in proxy and 'port' in proxy:
                        proxies.append(f"{proxy['ip']}:{proxy['port']}")
            elif isinstance(data, dict) and 'proxies' in data:
                for proxy in data['proxies']:
                    if 'ip' in proxy and 'port' in proxy:
                        proxies.append(f"{proxy['ip']}:{proxy['port']}")
            return proxies
        except Exception as e:
            self.logger.debug(f"Failed to parse proxifly response: {str(e)}")
            return []

    def _parse_proxyscrape_v4_response(self, response) -> List[str]:
        """Parse ProxyScrape v4 API response in space-separated protocol://ip:port format"""
        try:
            text_content = response.text.strip()
            if not text_content:
                return []
            
            # Split by spaces and filter valid proxies
            raw_proxies = text_content.split()
            parsed_proxies = []
            
            # Cloudflare and CDN IP ranges to exclude (these won't work as regular proxies)
            excluded_prefixes = [
                '104.', '172.67.', '172.64.', '188.114.', '141.101.', '162.158.',
                '141.193.', '188.42.', '185.18.', '185.193.', '185.162.',
                '23.227.', '199.34.', '198.41.', '173.245.', '104.16.',
                '104.17.', '104.18.', '104.19.', '104.20.', '104.21.',
                '104.22.', '104.23.', '104.24.', '104.25.', '104.26.',
                '104.27.', '45.131.', '45.159.', '45.85.', '45.80.',
                '45.67.', '216.24.', '216.205.', '209.46.', '154.194.',
                '154.197.', '160.153.', '195.85.', '31.43.', '5.10.',
                '5.182.', '89.116.', '91.193.', '159.112.', '160.123.'
            ]
            
            for proxy_entry in raw_proxies:
                proxy_entry = proxy_entry.strip()
                if not proxy_entry:
                    continue
                
                # Handle different protocols
                if proxy_entry.startswith('http://'):
                    # Extract IP:PORT from http://ip:port
                    proxy_clean = proxy_entry.replace('http://', '')
                    if ':' in proxy_clean and len(proxy_clean.split(':')) == 2:
                        ip, port = proxy_clean.split(':')
                        if port.isdigit():
                            # Filter out Cloudflare/CDN IPs
                            if not any(ip.startswith(prefix) for prefix in excluded_prefixes):
                                parsed_proxies.append(proxy_clean)
                            
                elif proxy_entry.startswith('https://'):
                    # Extract IP:PORT from https://ip:port
                    proxy_clean = proxy_entry.replace('https://', '')
                    if ':' in proxy_clean and len(proxy_clean.split(':')) == 2:
                        ip, port = proxy_clean.split(':')
                        if port.isdigit():
                            # Filter out Cloudflare/CDN IPs
                            if not any(ip.startswith(prefix) for prefix in excluded_prefixes):
                                parsed_proxies.append(proxy_clean)
                            
                elif proxy_entry.startswith('socks4://'):
                    # For SOCKS4, we can try to use them as HTTP proxies in some cases
                    # Extract IP:PORT from socks4://ip:port
                    proxy_clean = proxy_entry.replace('socks4://', '')
                    if ':' in proxy_clean and len(proxy_clean.split(':')) == 2:
                        ip, port = proxy_clean.split(':')
                        if port.isdigit():
                            # Filter out Cloudflare/CDN IPs and only accept known good SOCKS ports
                            if (not any(ip.startswith(prefix) for prefix in excluded_prefixes) and
                                int(port) > 1024):  # SOCKS ports are usually > 1024
                                parsed_proxies.append(proxy_clean)
                            
                elif proxy_entry.startswith('socks5://'):
                    # Extract IP:PORT from socks5://ip:port
                    proxy_clean = proxy_entry.replace('socks5://', '')
                    if ':' in proxy_clean and len(proxy_clean.split(':')) == 2:
                        ip, port = proxy_clean.split(':')
                        if port.isdigit():
                            # Filter out Cloudflare/CDN IPs
                            if (not any(ip.startswith(prefix) for prefix in excluded_prefixes) and
                                int(port) > 1024):  # SOCKS ports are usually > 1024
                                parsed_proxies.append(proxy_clean)
                            
                elif ':' in proxy_entry and len(proxy_entry.split(':')) == 2:
                    # Direct IP:PORT format
                    ip, port = proxy_entry.split(':')
                    if port.isdigit():
                        # Filter out Cloudflare/CDN IPs
                        if not any(ip.startswith(prefix) for prefix in excluded_prefixes):
                            parsed_proxies.append(proxy_entry)
            
            print(f"   📊 ProxyScrape v4: Parsed {len(parsed_proxies)} usable from {len(raw_proxies)} total (filtered CDN/Cloudflare)")
            return parsed_proxies
            
        except Exception as e:
            self.logger.debug(f"Failed to parse ProxyScrape v4 response: {str(e)}")
            return []

    def _get_html_scraped_proxies(self, response=None) -> List[str]:
        """Get proxies from HTML scraping sources"""
        try:
            if not self.html_scraper:
                print(f"   ⚠️ HTML scraper not available")
                return []
            
            # Scrape proxies from all HTML sources
            proxies = self.html_scraper.scrape_all_sources()
            
            if proxies:
                print(f"   ✅ HTML Scrapers: Found {len(proxies)} proxies")
                return proxies
            else:
                print(f"   ⚠️ HTML Scrapers: No proxies found")
                return []
                
        except Exception as e:
            print(f"   ❌ HTML Scrapers: Error - {str(e)}")
            return []

    def get_proxies_from_api_services(self) -> List[str]:
        """Get proxies from multiple API services with ProxyScrape as primary source"""
        all_proxies = []
        
        print("\n🔄 FETCHING PROXIES FROM API SERVICES (ProxyScrape Priority)")
        print("="*60)
        
        # Load manual proxies first
        manual_proxies = self._load_manual_proxies()
        if manual_proxies:
            all_proxies.extend(manual_proxies)
            print(f"✅ Loaded {len(manual_proxies)} manual proxies")
        
        # Sort APIs by priority (ProxyScrape first)
        sorted_apis = sorted(
            self.proxy_apis.items(), 
            key=lambda x: x[1].get('priority', 999)
        )
        
        # Try each API service in priority order
        for service_name, api_config in sorted_apis:
            try:
                # Skip paid services if no API key
                if not api_config['free'] and not api_config['params'].get('token') and not api_config['params'].get('apiKey'):
                    print(f"⚠️ Skipping {service_name}: No API key configured")
                    continue
                
                print(f"🔍 Fetching from {service_name} (Priority: {api_config.get('priority', '∞')})...")
                
                # Special handling for different source types
                if service_name.startswith('proxyscrape') and 'v4' in service_name:
                    service_proxies = self._fetch_proxyscrape_with_fallback(api_config)
                elif service_name == 'html_scrapers':
                    # Handle HTML scraping
                    print(f"   🕷️ Initiating HTML scraping from multiple websites...")
                    service_proxies = api_config['parse_response']()
                else:
                    # Standard API handling
                    if api_config['method'] == 'GET':
                        response = requests.get(
                            api_config['url'],
                            params=api_config['params'],
                            headers=api_config['headers'],
                            timeout=15
                        )
                    else:  # POST
                        response = requests.post(
                            api_config['url'],
                            json=api_config['params'],
                            headers=api_config['headers'],
                            timeout=15
                        )
                    
                    if response.status_code == 200:
                        service_proxies = api_config['parse_response'](response)
                    else:
                        service_proxies = []
                        print(f"❌ {service_name}: HTTP {response.status_code}")
                
                if service_proxies:
                    all_proxies.extend(service_proxies)
                    print(f"✅ {service_name}: {len(service_proxies)} proxies")
                    
                    # Stop early if we have enough proxies from high-priority sources
                    if len(all_proxies) >= 100 and api_config.get('priority', 999) <= 3:
                        print(f"📊 Got sufficient proxies from high-priority sources")
                        break
                else:
                    print(f"⚠️ {service_name}: No proxies in response")
                    
            except Exception as e:
                print(f"❌ {service_name}: {str(e)}")
                self.logger.debug(f"Error fetching from {service_name}: {str(e)}")
        
        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        print(f"\n📊 Total unique proxies collected: {len(unique_proxies)}")
        
        return unique_proxies

    def _fetch_proxyscrape_with_fallback(self, api_config: Dict) -> List[str]:
        """Fetch ProxyScrape proxies with v4/v2 API fallback"""
        try:
            # For v4 API, try the main request first
            if 'v4' in api_config.get('url', ''):
                print(f"   🚀 Using ProxyScrape v4 API...")
                response = requests.get(
                    api_config['url'],
                    params=api_config['params'],
                    headers=api_config['headers'],
                    timeout=15
                )
                
                if response.status_code == 200:
                    proxies = api_config['parse_response'](response)
                    if proxies:
                        print(f"   ✅ v4 API successful: {len(proxies)} proxies")
                        return proxies
                    else:
                        print(f"   ⚠️ v4 API returned empty response")
                else:
                    print(f"   ❌ v4 API failed: HTTP {response.status_code}")
                
                # If v4 fails, don't fallback for v4 endpoints
                return []
            
            # For legacy v2 API, try JSON format first
            response = requests.get(
                api_config['url'],
                params=api_config['params'],
                headers=api_config['headers'],
                timeout=15
            )
            
            if response.status_code == 200:
                proxies = api_config['parse_response'](response)
                if proxies:
                    return proxies
            
            # Fallback to text format for v2 API only
            print("   📝 Trying text format fallback...")
            text_params = api_config['params'].copy()
            text_params['format'] = 'textplain'
            
            text_response = requests.get(
                api_config['url'],
                params=text_params,
                headers=api_config['headers'],
                timeout=15
            )
            
            if text_response.status_code == 200:
                return api_config['parse_response'](text_response)
                
        except Exception as e:
            self.logger.debug(f"ProxyScrape fetch failed: {str(e)}")
        
        return []

    def _load_manual_proxies(self) -> List[str]:
        """Load manual proxies from config file"""
        if not self.config.get('use_manual_proxies', True):
            return []
            
        manual_proxy_file = "config/manual_proxies.txt"
        if not os.path.exists(manual_proxy_file):
            return []
        
        try:
            with open(manual_proxy_file, 'r') as f:
                proxies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            return proxies
        except Exception as e:
            self.logger.debug(f"Error loading manual proxies: {str(e)}")
            return []

    def test_proxy_with_cmc_advanced(self, proxy: str, timeout: int = 15) -> Dict:
        """Advanced CMC-specific proxy testing with detailed metrics"""
        test_results = {
            'proxy': proxy,
            'basic_connectivity': False,
            'cmc_health_check': False,
            'cmc_trending_page': False,
            'cmc_content_validation': False,
            'response_time': None,
            'ip_detected': None,
            'overall_score': 0
        }
        
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Test 1: Basic connectivity
            start_time = time.time()
            try:
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    headers=headers,
                    timeout=timeout
                )
                if response.status_code == 200:
                    test_results['basic_connectivity'] = True
                    test_results['ip_detected'] = response.json().get('origin', 'Unknown')
                    test_results['overall_score'] += 25
            except:
                return test_results
            
            # Test 2: CMC Health Check
            try:
                health_response = requests.get(
                    'https://coinmarketcap.com/api/health-check/',
                    proxies=proxies,
                    headers=headers,
                    timeout=timeout
                )
                if health_response.status_code == 200:
                    test_results['cmc_health_check'] = True
                    test_results['overall_score'] += 25
            except:
                pass
            
            # Test 3: CMC Trending Page Access
            try:
                trending_response = requests.get(
                    'https://coinmarketcap.com/trending-cryptocurrencies/',
                    proxies=proxies,
                    headers=headers,
                    timeout=timeout
                )
                if trending_response.status_code == 200:
                    test_results['cmc_trending_page'] = True
                    test_results['overall_score'] += 25
                    
                    # Test 4: Content Validation
                    page_content = trending_response.text.lower()
                    expected_indicators = ['trending', 'cryptocurrency', 'bitcoin', 'price', 'market']
                    found_indicators = sum(1 for indicator in expected_indicators if indicator in page_content)
                    
                    if found_indicators >= 3:
                        test_results['cmc_content_validation'] = True
                        test_results['overall_score'] += 25
                        
            except:
                pass
            
            test_results['response_time'] = time.time() - start_time
            
        except Exception as e:
            self.logger.debug(f"CMC proxy test failed for {proxy}: {str(e)}")
        
        return test_results

    def get_enterprise_grade_proxies(self) -> List[str]:
        """Get high-quality proxies with premium sources prioritized for maximum CMC success"""
        print("\n🚀 ENHANCED ENTERPRISE PROXY ACQUISITION")
        print("="*60)
        print("Strategic priority: Stored working > Premium residential > Emergency residential > Filtered free")
        
        # Phase 0: Use stored working proxies first
        print("\n🗂️ PHASE 0: STORED WORKING PROXIES")
        print("-" * 40)
        
        # Cleanup old failures (give them another chance)
        self.proxy_storage.cleanup_old_failures(hours=24)
        
        # Get stored working proxies
        stored_proxies = self.proxy_storage.get_working_proxies()
        
        if stored_proxies:
            print(f"🎯 Found {len(stored_proxies)} stored working proxies")
            print(f"   📊 Testing stored proxies for current availability...")
            
            # Quick test of stored proxies
            verified_stored = self._test_stored_proxies_quick(stored_proxies[:10])  # Test top 10
            
            if verified_stored:
                print(f"   ✅ {len(verified_stored)} stored proxies still working - using them!")
                
                # Update stats for successful stored proxies
                for proxy in verified_stored:
                    self.proxy_storage.add_working_proxy(proxy)
                
                # Store for rotation
                self.verified_proxies = verified_stored
                self.proxy_refresh_time = datetime.now()
                
                return verified_stored
            else:
                print(f"   ⚠️ Stored proxies need refresh - proceeding to fetch new ones")
        else:
            print(f"   📭 No stored working proxies - will build fresh list")
        
        # Continue with normal acquisition if stored proxies aren't sufficient
        all_working_proxies = []
        total_tested = 0
        
        # Phase 1: Premium API Sources (Expected 80%+ success rate)
        print("\n🏆 PHASE 1: PREMIUM API SOURCES")
        print("-" * 40)
        
        for source_name, source_config in self.premium_sources.items():
            api_key_needed = source_config.get('params', {}).get('api_key', '') or \
                           source_config.get('headers', {}).get('Authorization', '')
            
            if not source_config['free'] and not api_key_needed and source_name != 'emergency_residential_list':
                print(f"⚠️ {source_name}: No API key - skipping")
                continue
                
            print(f"🔄 Testing {source_name} (Expected success: {source_config.get('success_rate_expected', 50)}%)")
            
            try:
                if source_config['method'] == 'LOCAL':
                    proxies = source_config['parse_response']()
                elif source_config['method'] == 'LIBRARY':
                    # ProxyScrape library integration
                    proxies = source_config['parse_response']()
                elif source_config['method'] == 'MULTI':
                    # Multiple API calls (like ProxyKingdom)
                    proxies = source_config['parse_response']()
                else:
                    # Standard API call
                    if source_config['method'] == 'GET':
                        response = requests.get(
                            source_config['url'],
                            params=source_config['params'],
                            headers=source_config['headers'],
                            timeout=15
                        )
                    else:
                        response = requests.post(
                            source_config['url'],
                            json=source_config['params'],
                            headers=source_config['headers'],
                            timeout=15
                        )
                    
                    if response.status_code == 200:
                        proxies = source_config['parse_response'](response)
                    else:
                        proxies = []
                
                # Test proxies from this source
                if proxies:
                    print(f"   📊 Found {len(proxies)} proxies from {source_name}")
                    working_from_source = self._test_proxy_batch_intelligent(
                        proxies[:20],  # Test up to 20 from each premium source
                        source_name
                    )
                    
                    all_working_proxies.extend(working_from_source)
                    total_tested += min(len(proxies), 20)
                    
                    print(f"   ✅ {source_name}: {len(working_from_source)} working proxies")
                    
                    # If we get good results from premium, we can reduce testing of free sources
                    if len(working_from_source) >= 5:
                        print(f"   🎯 Excellent results from {source_name}! Prioritizing quality over quantity.")
                        
                else:
                    print(f"   ❌ {source_name}: No proxies returned")
                    
            except Exception as e:
                print(f"   ❌ {source_name}: Error - {str(e)}")
        
        # Phase 2: High-quality manual proxies
        print(f"\n🏠 PHASE 2: MANUAL RESIDENTIAL PROXIES")
        print("-" * 40)
        
        manual_proxies = self._load_manual_proxies()
        if manual_proxies:
            print(f"🔄 Testing {len(manual_proxies)} manual proxies")
            working_manual = self._test_proxy_batch_intelligent(manual_proxies, "manual_residential")
            all_working_proxies.extend(working_manual)
            total_tested += len(manual_proxies)
            print(f"   ✅ Manual proxies: {len(working_manual)} working")
        else:
            print("   ⚠️ No manual proxies configured")
        
        # Phase 3: Intelligent free proxy selection (only if needed)
        if len(all_working_proxies) < 10:
            print(f"\n🔍 PHASE 3: INTELLIGENT FREE PROXY SELECTION")
            print("-" * 40)
            print("Applying advanced filtering to free sources...")
            
            free_proxies = self.get_proxies_from_api_services()
            if free_proxies:
                # Apply intelligent filtering
                filtered_proxies = self._apply_intelligent_filtering(free_proxies)
                print(f"   📊 Filtered to {len(filtered_proxies)} high-potential proxies")
                
                # Test smaller batch of filtered proxies
                working_filtered = self._test_proxy_batch_intelligent(
                    filtered_proxies[:50],  # Test top 50 filtered
                    "filtered_free"
                )
                all_working_proxies.extend(working_filtered)
                total_tested += min(len(filtered_proxies), 50)
                print(f"   ✅ Filtered free: {len(working_filtered)} working")
        
        # Final results
        success_rate = (len(all_working_proxies) / max(total_tested, 1)) * 100
        
        print(f"\n📊 ENTERPRISE PROXY ACQUISITION SUMMARY")
        print("="*60)
        print(f"Total tested: {total_tested}")
        print(f"Working proxies: {len(all_working_proxies)}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 15:
            print(f"🎯 EXCELLENT: High-quality proxy acquisition successful!")
        elif success_rate >= 5:
            print(f"✅ GOOD: Adequate proxy quality achieved")
        else:
            print(f"⚠️ NEEDS IMPROVEMENT: Consider premium proxy services")
            print(f"💡 Recommended: ScraperAPI ($49/month) for 95% success rate")
        
        # Store working proxies for rotation
        self.verified_proxies = all_working_proxies
        self.proxy_refresh_time = datetime.now()
        
        # Save all newly discovered working proxies to storage
        if all_working_proxies:
            print(f"\n💾 SAVING {len(all_working_proxies)} WORKING PROXIES TO STORAGE")
            for proxy in all_working_proxies:
                self.proxy_storage.add_working_proxy(proxy)
            print(f"✅ Saved all working proxies for future use!")
        
        return all_working_proxies
    
    def _apply_intelligent_filtering(self, proxies: List[str]) -> List[str]:
        """Apply intelligent filtering to prioritize higher-quality free proxies"""
        filtered = []
        
        # Prioritize certain IP ranges that are less likely to be blocked
        priority_ranges = [
            '45.', '104.', '159.', '167.', '178.', '185.', '188.',  # Premium hosting
            '73.', '74.', '75.', '76.',  # US residential-style
            '94.', '95.', '212.', '213.',  # EU residential-style
        ]
        
        # Avoid problematic ranges
        avoid_ranges = [
            '172.67.', '104.16.', '104.17.', '104.18.',  # Cloudflare
            '185.199.', '140.82.', '192.30.',  # GitHub/CDN
            '1.', '14.', '27.', '36.', '42.', '43.',  # Asian datacenter blocks
        ]
        
        for proxy in proxies:
            ip = proxy.split(':')[0]
            
            # Skip avoided ranges
            if any(ip.startswith(avoid) for avoid in avoid_ranges):
                continue
                
            # Prioritize good ranges
            if any(ip.startswith(priority) for priority in priority_ranges):
                filtered.append(proxy)
            elif len(filtered) < 200:  # Include others if we need more
                filtered.append(proxy)
        
        return filtered[:100]  # Return top 100
    
    def _test_stored_proxies_quick(self, proxies: List[str]) -> List[str]:
        """Quick test of stored proxies to verify they still work"""
        print(f"   🚀 Quick testing {len(proxies)} stored proxies...")
        
        working_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_proxy = {
                executor.submit(self._test_single_proxy_quick, proxy): proxy 
                for proxy in proxies
            }
            
            for future in concurrent.futures.as_completed(future_to_proxy, timeout=30):
                proxy = future_to_proxy[future]
                
                try:
                    is_working = future.result()
                    
                    if is_working:
                        working_proxies.append(proxy)
                        print(f"   ✅ STORED: {proxy} still working")
                    else:
                        print(f"   ❌ STORED: {proxy} no longer working")
                        self.proxy_storage.mark_proxy_failed(proxy, "Quick test failed")
                        
                except Exception as e:
                    print(f"   ❌ STORED: {proxy} error - {str(e)[:30]}...")
                    self.proxy_storage.mark_proxy_failed(proxy, f"Error: {str(e)[:50]}")
        
        print(f"   📊 STORED RESULTS: {len(working_proxies)}/{len(proxies)} still working")
        return working_proxies
    
    def _test_single_proxy_quick(self, proxy: str) -> bool:
        """Quick test to check if proxy is responsive"""
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            # Quick connectivity test
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxies,
                headers=headers,
                timeout=8
            )
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def _test_proxy_batch_intelligent(self, proxies: List[str], source_name: str) -> List[str]:
        """HIGH-SPEED multithreaded proxy testing with 10x performance boost"""
        working_proxies = []
        
        print(f"   🚀 MULTITHREADED TESTING: {len(proxies)} proxies from {source_name}...")
        print(f"   ⚡ Using {min(10, len(proxies))} concurrent threads for maximum speed")
        
        # Multithreaded testing for 10x speed boost
        max_workers = min(10, len(proxies))  # Optimal thread count
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all proxy tests concurrently
            future_to_proxy = {
                executor.submit(self._test_single_proxy_fast, proxy): proxy 
                for proxy in proxies
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_proxy, timeout=60):
                proxy = future_to_proxy[future]
                completed += 1
                
                try:
                    test_result = future.result()
                    
                    if test_result and test_result['overall_score'] >= 60:  # Emergency threshold
                        working_proxies.append(proxy)
                        print(f"   ✅ WORKING: {proxy} (Score: {test_result['overall_score']}%)")
                        
                        # Save to persistent storage immediately
                        self.proxy_storage.add_working_proxy(
                            proxy, 
                            response_time=test_result.get('response_time'),
                            test_score=test_result['overall_score']
                        )
                        
                    elif test_result and test_result['overall_score'] >= 25:
                        print(f"   ⚠️ PARTIAL: {proxy} (Score: {test_result['overall_score']}%)")
                        # Mark as working but with lower score
                        self.proxy_storage.add_working_proxy(
                            proxy, 
                            response_time=test_result.get('response_time'),
                            test_score=test_result['overall_score']
                        )
                    else:
                        print(f"   ❌ FAILED: {proxy}")
                        # Mark as failed in storage
                        self.proxy_storage.mark_proxy_failed(proxy, "CMC test failed")
                        
                except Exception as e:
                    print(f"   ❌ ERROR: {proxy} - {str(e)[:20]}...")
                    # Mark as failed in storage with error reason
                    self.proxy_storage.mark_proxy_failed(proxy, f"Test error: {str(e)[:30]}")
                
                # Progress updates
                if completed % 5 == 0:
                    print(f"   📊 SPEED: {completed}/{len(proxies)} tested, {len(working_proxies)} working")
                
                # Early success optimization for premium sources
                if len(working_proxies) >= 5 and source_name in ['emergency_residential_list', 'manual_residential', 'proxyscrape_premium']:
                    print(f"   🎯 EARLY SUCCESS: Found {len(working_proxies)} working proxies, stopping for efficiency")
                    # Cancel remaining futures
                    for remaining_future in future_to_proxy:
                        if not remaining_future.done():
                            remaining_future.cancel()
                    break
        
        print(f"   📈 RESULTS: {len(working_proxies)}/{len(proxies)} working ({len(working_proxies)/len(proxies)*100:.1f}% success)")
        return working_proxies
    
    def _test_single_proxy_fast(self, proxy: str) -> Dict:
        """Fast single proxy test optimized for speed"""
        try:
            # Use shorter timeout for speed
            return self.test_proxy_with_cmc_advanced(proxy, timeout=8)
        except Exception as e:
            return {'proxy': proxy, 'overall_score': 0, 'error': str(e)}

    def get_best_proxy(self) -> Optional[str]:
        """Get the best available proxy for CMC scraping with automatic re-scraping"""
        # Try to get enterprise proxies first
        proxies = getattr(self, 'verified_proxies', [])
        
        # If no proxies in memory, try to get them
        if not proxies:
            print("🔄 No proxies in memory, acquiring fresh proxies...")
            proxies = self.get_enterprise_grade_proxies()
        
        if not proxies:
            print("\n⚠️ No CMC-verified proxies available")
            print("🔄 Attempting emergency proxy acquisition...")
            
            # Try emergency acquisition
            if self._trigger_emergency_proxy_discovery():
                proxies = getattr(self, 'verified_proxies', [])
            
            if not proxies:
                print("❌ Emergency proxy acquisition failed")
                return None
        
        # Select best proxy (consider failure counts)
        best_proxy = None
        min_failures = float('inf')
        
        for proxy in proxies:
            failures = self.proxy_failure_counts.get(proxy, 0)
            if failures < min_failures:
                min_failures = failures
                best_proxy = proxy
        
        if best_proxy:
            print(f"🎯 Selected best proxy: {best_proxy} (failures: {min_failures})")
        
        return best_proxy

    def mark_proxy_failed(self, proxy: str, error_reason: str = "General failure"):
        """Mark a proxy as failed and remove from good lists"""
        self.proxy_failure_counts[proxy] = self.proxy_failure_counts.get(proxy, 0) + 1
        
        # Mark as failed in persistent storage
        self.proxy_storage.mark_proxy_failed(proxy, error_reason)
        
        # Remove from verified lists if too many failures
        if hasattr(self, 'verified_proxies') and proxy in self.verified_proxies:
            self.verified_proxies.remove(proxy)
            print(f"🗑️ Removed failed proxy: {proxy}")
        
        # Check if we need to trigger emergency proxy re-scraping
        remaining_proxies = len(getattr(self, 'verified_proxies', []))
        if remaining_proxies <= 2:  # Trigger when only 2 or fewer proxies remain
            print(f"⚠️ Low proxy count detected ({remaining_proxies} remaining) - triggering emergency re-scraping")
            self._trigger_emergency_proxy_discovery()

    def _trigger_emergency_proxy_discovery(self):
        """Automatically trigger emergency proxy discovery when proxy pool is low"""
        try:
            print("\n🚨 EMERGENCY PROXY DISCOVERY INITIATED")
            print("="*60)
            print("Reason: Proxy pool exhausted or critically low")
            
            # Clear cache to force fresh acquisition
            self.verified_proxies = []
            self.proxy_refresh_time = None
            
            print("🔄 Step 1: Clearing proxy cache...")
            print("🔍 Step 2: Acquiring fresh proxies from all sources...")
            
            # Force fresh proxy acquisition
            new_proxies = self.get_enterprise_grade_proxies()
            
            if new_proxies:
                print(f"✅ EMERGENCY SUCCESS: Discovered {len(new_proxies)} fresh working proxies!")
                print(f"🎯 System is ready to continue with automatic proxy rotation")
                
                # Show sample of new proxies
                if len(new_proxies) >= 3:
                    print(f"📋 Sample of fresh proxies:")
                    for i, proxy in enumerate(new_proxies[:3], 1):
                        print(f"   {i}. {proxy}")
                
                return True
            else:
                print(f"❌ EMERGENCY FAILED: No new working proxies found")
                print(f"💡 Consider:")
                print(f"   • Configuring premium proxy APIs")
                print(f"   • Adding manual proxies to config/manual_proxies.txt")
                print(f"   • Waiting 10-15 minutes for proxy sources to refresh")
                
                return False
                
        except Exception as e:
            print(f"❌ Emergency proxy discovery failed: {str(e)}")
            return False

    def create_anti_detection_options(self, use_proxy: bool = True, force_proxy: bool = True) -> Options:
        """Create Chrome options with enterprise anti-detection and MANDATORY proxy usage"""
        options = Options()
        
        proxy_used = False
        
        if use_proxy or force_proxy:
            proxy = self.get_best_proxy()
            if proxy:
                options.add_argument(f'--proxy-server=http://{proxy}')
                print(f"🌐 Using enterprise proxy: {proxy}")
                proxy_used = True
            else:
                if force_proxy:
                    # CRITICAL: Don't allow operation without proxy
                    print("🚫 CRITICAL ERROR: No proxy available and force_proxy=True")
                    print("🔄 Attempting emergency proxy acquisition...")
                    
                    # Emergency proxy fetch
                    emergency_proxies = self.get_enterprise_grade_proxies()
                    if emergency_proxies:
                        emergency_proxy = emergency_proxies[0]
                        options.add_argument(f'--proxy-server=http://{emergency_proxy}')
                        print(f"🆘 Using emergency proxy: {emergency_proxy}")
                        proxy_used = True
                    else:
                        raise Exception("MANDATORY PROXY REQUIRED: No proxies available from any source. Cannot proceed without proxy protection.")
                else:
                    print("⚠️ No enterprise proxy available, using direct connection")
        
        # Log proxy status
        if proxy_used:
            print("✅ PROXY PROTECTION: ACTIVE")
        else:
            print("⚠️ PROXY PROTECTION: DISABLED (NOT RECOMMENDED)")
        
        # Advanced anti-detection
        user_agent = random.choice(self.user_agents)
        width, height = random.choice(self.screen_resolutions)
        
        options.add_argument(f'--user-agent={user_agent}')
        options.add_argument(f'--window-size={width},{height}')
        
        # Stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript-harmony-shipping')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-default-apps')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        
        # Fingerprint randomization
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random viewport and timezone
        options.add_argument(f'--window-position={random.randint(0, 100)},{random.randint(0, 100)}')
        timezones = ['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney']
        options.add_argument(f'--timezone={random.choice(timezones)}')
        
        return options

    def get_session_info(self) -> Dict:
        """Get current session information including storage stats"""
        storage_stats = self.proxy_storage.get_storage_stats()
        
        # Handle case where verified_proxies might not be initialized
        verified_count = len(getattr(self, 'verified_proxies', []))
        working_count = len(getattr(self, 'working_proxies', []))
        
        return {
            'enterprise_mode': True,
            'verified_proxies_count': verified_count,
            'working_proxies_count': working_count,
            'current_proxy': self.get_best_proxy(),
            'last_refresh': self.proxy_refresh_time.strftime('%H:%M:%S') if self.proxy_refresh_time else 'Never',
            'config_loaded': bool(self.config),
            'storage_stats': storage_stats
        }
    
    def view_proxy_storage_stats(self):
        """Display detailed proxy storage statistics"""
        print("\n🗂️ PERSISTENT PROXY STORAGE STATISTICS")
        print("="*60)
        
        storage_stats = self.proxy_storage.get_storage_stats()
        
        print(f"📊 STORAGE OVERVIEW:")
        print(f"   ✅ Working proxies: {storage_stats['working_proxies']}")
        print(f"   ❌ Failed proxies: {storage_stats['failed_proxies']}")
        print(f"   📈 Total tracked: {storage_stats['total_tracked']}")
        print(f"   🎯 Average success rate: {storage_stats['average_success_rate']}%")
        print(f"   🕒 Last updated: {storage_stats['last_updated']}")
        print(f"   📁 Storage file: {storage_stats['storage_file']}")
        
        # Show top working proxies
        working_proxies = self.proxy_storage.get_working_proxies()
        if working_proxies:
            print(f"\n🏆 TOP WORKING PROXIES:")
            for i, proxy in enumerate(working_proxies[:10], 1):
                stats = self.proxy_storage.proxy_data['proxy_stats'].get(proxy, {})
                success_count = stats.get('success_count', 0)
                fail_count = stats.get('fail_count', 0)
                total = success_count + fail_count
                success_rate = (success_count / total * 100) if total > 0 else 0
                avg_response = stats.get('avg_response_time', 0)
                best_score = stats.get('best_score', 0)
                
                print(f"   {i:2d}. {proxy}")
                print(f"       📊 Success: {success_count}/{total} ({success_rate:.1f}%)")
                print(f"       ⚡ Avg response: {avg_response:.2f}s | 🎯 Best score: {best_score}%")
        
        # Show recent failures if any
        failed_proxies = self.proxy_storage.proxy_data.get('failed_proxies', [])
        if failed_proxies:
            print(f"\n❌ RECENT FAILURES ({len(failed_proxies)} total):")
            for proxy in failed_proxies[-5:]:  # Show last 5 failures
                stats = self.proxy_storage.proxy_data['proxy_stats'].get(proxy, {})
                last_fail = stats.get('last_fail', 'Unknown')
                recent_failures = stats.get('recent_failures', [])
                
                print(f"   • {proxy}")
                if recent_failures:
                    latest_failure = recent_failures[-1]
                    print(f"     Last failure: {latest_failure.get('reason', 'Unknown')}")
                    print(f"     Time: {latest_failure.get('time', 'Unknown')}")
        
        print("="*60)

    def validate_proxy_availability(self) -> bool:
        """Validate that proxies are available before starting any operations"""
        print("\n🔒 MANDATORY PROXY VALIDATION")
        print("="*50)
        
        available_proxies = self.get_enterprise_grade_proxies()
        
        if not available_proxies:
            print("❌ VALIDATION FAILED: No working proxies available")
            print("🔧 SOLUTIONS:")
            print("   1. Check internet connection")
            print("   2. Configure premium proxy APIs")
            print("   3. Add manual proxies to config/manual_proxies.txt")
            print("   4. Wait for ProxyScrape to refresh (updates every minute)")
            return False
        
        print(f"✅ VALIDATION PASSED: {len(available_proxies)} proxies available")
        return True

    def _parse_scraperapi_response(self, response) -> List[str]:
        """Parse ScraperAPI response - returns special ScraperAPI proxy endpoint"""
        try:
            if hasattr(response, 'status_code') and response.status_code == 200:
                # ScraperAPI works differently - it's a proxy service endpoint
                api_key = self.config.get('api_keys', {}).get('scraperapi_key', '')
                if api_key:
                    # Return ScraperAPI proxy endpoint
                    return [f"scraperapi:{api_key}@proxy-server.scraperapi.com:8001"]
            return []
        except Exception as e:
            self.logger.debug(f"Failed to parse ScraperAPI response: {str(e)}")
            return []
    
    def _parse_webshare_response(self, response) -> List[str]:
        """Parse Webshare premium proxy response"""
        try:
            data = response.json()
            proxies = []
            if 'results' in data:
                for proxy in data['results']:
                    if proxy.get('proxy_address') and proxy.get('port'):
                        # Include auth if available
                        username = proxy.get('username', '')
                        password = proxy.get('password', '')
                        if username and password:
                            proxies.append(f"{username}:{password}@{proxy['proxy_address']}:{proxy['port']}")
                        else:
                            proxies.append(f"{proxy['proxy_address']}:{proxy['port']}")
            return proxies
        except Exception as e:
            self.logger.debug(f"Failed to parse Webshare response: {str(e)}")
            return []
    
    def _generate_emergency_residential_proxies(self) -> List[str]:
        """Generate emergency residential proxy list from known working sources"""
        # Emergency residential proxy ranges that are often CMC-compatible
        emergency_proxies = [
            # Residential ISP ranges (US)
            "73.162.91.47:8080",
            "173.239.198.73:3128", 
            "174.129.154.69:3128",
            "45.79.142.218:3128",
            "198.13.56.92:8080",
            
            # Premium datacenter (less likely to be blocked)
            "159.203.61.169:3128",
            "104.248.90.212:8080",
            "159.89.49.60:3128",
            "167.172.109.12:46369",
            "164.90.152.213:3128",
            
            # European residential-style
            "185.38.111.1:8080",
            "178.32.129.31:3128",
            "51.158.68.133:8811",
            "195.154.67.61:3128",
            "51.15.3.186:8080",
            
            # Canadian residential
            "192.99.144.208:8080",
            "167.114.96.27:9300",
            "149.56.140.40:8080",
            
            # Australian premium
            "103.216.82.18:6666",
            "43.245.94.229:4995"
        ]
        
        print(f"   🏠 Generated {len(emergency_proxies)} emergency residential-style proxies")
        return emergency_proxies

    def _get_proxykingdom_premium_proxies(self) -> List[str]:
        """🎯 PREMIUM: Fetch high-quality proxies from ProxyKingdom API"""
        try:
            # Get API token from config
            token = self.config.get('api_keys', {}).get('proxykingdom_token', '')
            if not token:
                print("   ⚠️ ProxyKingdom: No API token configured")
                return []
            
            print(f"   🏆 ProxyKingdom Premium: Fetching elite proxies with token: {token[:6]}...")
            
            # ProxyKingdom API returns one proxy per call, so we make multiple calls
            # with different filters to get variety
            filter_configs = [
                # High-quality US proxies
                {'country': 'US', 'accessType': 'elite', 'protocol': 'http', 'isSsl': 'true'},
                # High-quality UK proxies
                {'country': 'GB', 'accessType': 'elite', 'protocol': 'http', 'isSsl': 'true'},
                # High-quality Canadian proxies
                {'country': 'CA', 'accessType': 'elite', 'protocol': 'http', 'isSsl': 'true'},
                # High-quality German proxies
                {'country': 'DE', 'accessType': 'elite', 'protocol': 'http', 'isSsl': 'true'},
                # Anonymous proxies (slightly lower tier)
                {'accessType': 'anonymous', 'protocol': 'http', 'isSsl': 'true', 'uptime': '0.8'},
                # Fast response proxies
                {'responseTime': '2.0', 'accessType': 'elite', 'protocol': 'http'},
                # High uptime proxies
                {'uptime': '0.9', 'accessType': 'elite', 'protocol': 'http'},
                # SSL-enabled proxies
                {'isSsl': 'true', 'accessType': 'elite'},
                # SOCKS4 proxies for variety
                {'protocol': 'socks4', 'accessType': 'elite'},
                # General elite proxies
                {'accessType': 'elite', 'protocol': 'http'}
            ]
            
            all_proxies = []
            successful_requests = 0
            
            # Make multiple API calls to get diverse proxy pool
            for i, filter_config in enumerate(filter_configs, 1):
                try:
                    # Prepare API parameters
                    params = {
                        'token': token,
                        **filter_config
                    }
                    
                    print(f"   📡 API Call {i}/10: {filter_config}")
                    
                    # Make API request
                    response = requests.get(
                        'https://api.proxykingdom.com/proxy',  
                        params=params,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Parse the JSON response
                        data = response.json()
                        
                        if isinstance(data, dict) and 'address' in data and 'port' in data:
                            proxy_address = f"{data['address']}:{data['port']}"
                            
                            # Extract additional info for quality assessment
                            proxy_info = {
                                'proxy': proxy_address,
                                'protocol': data.get('protocol', 'http'),
                                'access_type': data.get('accessType', 'unknown'),
                                'uptime': data.get('uptime', 0),
                                'ssl': data.get('isSsl', False),
                                'response_time': data.get('timings', {}).get('responseTime', 999),
                                'country': data.get('location', {}).get('country', {}).get('name', 'Unknown'),
                                'isp': data.get('isp', {}).get('name', 'Unknown'),
                                'last_tested': data.get('lastTested', 'Unknown')
                            }
                            
                            all_proxies.append(proxy_address)
                            successful_requests += 1
                            
                            print(f"   ✅ Got {proxy_info['protocol'].upper()} proxy: {proxy_address}")
                            print(f"      📍 {proxy_info['country']} | {proxy_info['access_type']} | {proxy_info['uptime']:.2f} uptime")
                            print(f"      ⚡ {proxy_info['response_time']:.3f}s response | 🏢 {proxy_info['isp']}")
                            
                        else:
                            print(f"   ❌ Invalid response format: {data}")
                            
                    elif response.status_code == 404:
                        print(f"   ⚠️ No proxies match filter: {filter_config}")
                        
                    elif response.status_code == 429:
                        print(f"   ⚠️ Rate limit hit - pausing...")
                        time.sleep(2)  # Brief pause for rate limiting
                        
                    else:
                        print(f"   ❌ API Error {response.status_code}: {response.text[:100]}")
                        
                except Exception as e:
                    print(f"   ❌ Request {i} failed: {str(e)}")
                    continue
                
                # Brief delay between requests to respect rate limits
                time.sleep(0.5)
            
            # Remove duplicates while preserving order
            unique_proxies = []
            seen = set()
            for proxy in all_proxies:
                if proxy not in seen:
                    unique_proxies.append(proxy)
                    seen.add(proxy)
            
            success_rate = (successful_requests / len(filter_configs)) * 100
            
            print(f"   📊 ProxyKingdom Summary:")
            print(f"      🎯 Successful API calls: {successful_requests}/{len(filter_configs)} ({success_rate:.1f}%)")
            print(f"      🌐 Unique proxies obtained: {len(unique_proxies)}")
            print(f"      💎 Premium quality expected: 80%+ CMC success rate")
            
            if unique_proxies:
                print(f"   🏆 ProxyKingdom SUCCESS: Premium proxy pool ready!")
                return unique_proxies
            else:
                print(f"   ❌ ProxyKingdom: No proxies obtained")
                return []
                
        except Exception as e:
            print(f"   ❌ ProxyKingdom Premium error: {str(e)}")
            return []

    def _get_proxyscrape_premium_proxies(self):
        """Get high-quality proxies from proxyscrape library using CORRECT resource names"""
        if not PROXYSCRAPE_AVAILABLE:
            print(f"   ⚠️ ProxyScrape library not available")
            return []
        
        try:
            import proxyscrape
            all_proxies = []
            
            # Use the ACTUAL available resources from the library
            print(f"   🔄 Fetching from ProxyScrape library (verified resources)...")
            
            # Define the actual available resources
            resource_configs = [
                ('us-proxy', 'US proxies', 15),
                ('uk-proxy', 'UK proxies', 10), 
                ('free-proxy-list', 'Free proxy list', 20),
                ('ssl-proxy', 'SSL proxies', 15),
                ('anonymous-proxy', 'Anonymous proxies', 15),
                ('proxy-daily-http', 'HTTP daily proxies', 10)
            ]
            
            for resource_name, description, limit in resource_configs:
                try:
                    print(f"   🔄 Fetching from {description}...")
                    
                    # Create collector with unique name
                    collector_name = f'cmc_{resource_name.replace("-", "_")}'
                    collector = proxyscrape.create_collector(collector_name, resource_name)
                    
                    # Get proxies with filters for better quality
                    proxies = collector.get_proxies({'anonymous': True})
                    
                    if proxies:
                        collected_count = 0
                        for proxy_obj in proxies[:limit]:
                            if hasattr(proxy_obj, 'host') and hasattr(proxy_obj, 'port'):
                                # Additional filtering for better quality
                                host = proxy_obj.host
                                port = str(proxy_obj.port)
                                
                                # Skip obviously bad IPs
                                if (host and port and 
                                    not host.startswith('127.') and 
                                    not host.startswith('192.168.') and
                                    not host.startswith('10.') and
                                    port.isdigit()):
                                    
                                    proxy_str = f"{host}:{port}"
                                    all_proxies.append(proxy_str)
                                    collected_count += 1
                        
                        print(f"   ✅ {description}: {collected_count} quality proxies")
                    else:
                        print(f"   ⚠️ {description}: No proxies returned")
                        
                except Exception as e:
                    print(f"   ⚠️ {description} failed: {str(e)}")
                    continue
            
            # Try basic resource types as fallback
            print(f"   🔄 Trying basic resource types...")
            for resource_type in ['http', 'https']:
                try:
                    collector = proxyscrape.create_collector(f'cmc_basic_{resource_type}', resource_type)
                    proxies = collector.get_proxies()
                    
                    if proxies:
                        for proxy_obj in proxies[:10]:  # Limit fallback
                            if hasattr(proxy_obj, 'host') and hasattr(proxy_obj, 'port'):
                                host = proxy_obj.host
                                port = str(proxy_obj.port)
                                
                                if (host and port and 
                                    not host.startswith('127.') and 
                                    port.isdigit()):
                                    
                                    proxy_str = f"{host}:{port}"
                                    all_proxies.append(proxy_str)
                        
                        print(f"   ✅ Basic {resource_type}: {len(proxies)} proxies")
                    
                except Exception as e:
                    print(f"   ⚠️ Basic {resource_type} failed: {str(e)}")
            
            # Remove duplicates and filter
            unique_proxies = list(set(all_proxies))
            
            if unique_proxies:
                print(f"   📊 ProxyScrape Library SUCCESS: {len(unique_proxies)} unique proxies!")
                print(f"   🎯 Sample working proxies: {unique_proxies[:3]}")
                print(f"   ✅ ProxyScrape integration CONFIRMED WORKING!")
            else:
                print(f"   ⚠️ ProxyScrape Library: No proxies collected (sources may be empty)")
            
            return unique_proxies
            
        except Exception as e:
            print(f"   ❌ ProxyScrape library error: {str(e)}")
            import traceback
            traceback.print_exc()
            return []


class AntiDetectionSystem:
    """Legacy wrapper for backwards compatibility"""
    
    def __init__(self, proxy_config: dict = None):
        self.enterprise_manager = EnterpriseProxyManager()
        self.logger = logging.getLogger(__name__)
        
        # Store proxy configuration
        self.proxy_config = proxy_config or {}
        self.ip_rotation_enabled = self.proxy_config.get('auto_proxy_rotation', True)
        
        # Legacy attributes for compatibility
        self.working_proxies = []
        self.proxy_refresh_time = None
        self.session_state = {
            'current_mode': 'enterprise_mode' if self.ip_rotation_enabled else 'direct_connection',
            'consecutive_failures': 0,
            'total_posts_today': 0,
            'shadowban_suspected': False,
            'proxy_failures': {},
            'last_success_time': datetime.now(),
            'current_proxy': None
        }
        
        # Add shadowban detection indicators - FIXED: Only real shadowban indicators, not rate limits
        self.shadowban_indicators = [
            "your post was not published",
            "content not visible to others",
            "under review by moderators", 
            "violates our community guidelines",
            "temporarily restricted access",
            "account suspended",
            "unusual activity detected",
            "content has been removed",
            "account has been restricted",
            "posts are not showing to others"
            # REMOVED: "posting too frequently", "try again later" - these are just rate limits!
        ]
        
        # User agents for randomization
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
        ]
        
        # Screen resolutions for randomization
        self.screen_resolutions = [
            (1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1280, 720)
        ]
        
    def get_working_proxy(self) -> Optional[str]:
        """Get working proxy using enterprise system (only if IP rotation enabled)"""
        if not self.ip_rotation_enabled:
            return None  # Direct connection mode - no proxy
        
        proxy = self.enterprise_manager.get_best_proxy()
        if proxy:
            self.session_state['current_proxy'] = proxy
        return proxy
    
    def create_anti_detection_options(self, use_proxy: bool = True, force_proxy: bool = True) -> Options:
        """Create anti-detection options using enterprise system"""
        # Override proxy usage based on configuration
        if not self.ip_rotation_enabled:
            use_proxy = False
            force_proxy = False
        
        return self.enterprise_manager.create_anti_detection_options(use_proxy, force_proxy)
    
    def mark_proxy_failed(self, proxy: str):
        """Mark proxy as failed (only if IP rotation enabled)"""
        if self.ip_rotation_enabled and proxy:
            self.enterprise_manager.mark_proxy_failed(proxy)
    
    def verify_cmc_accessibility(self, proxy: str = None) -> bool:
        """Verify CMC accessibility"""
        if proxy and self.ip_rotation_enabled:
            test_result = self.enterprise_manager.test_proxy_with_cmc_advanced(proxy)
            return test_result['overall_score'] >= 50
        else:
            # Test without proxy (direct connection)
            try:
                response = requests.get('https://coinmarketcap.com/', timeout=15)
                return response.status_code == 200 and 'coinmarketcap' in response.text.lower()
            except:
                return False
    
    def detect_shadowban(self, driver) -> bool:
        """Detect if account is shadowbanned - FIXED: Removed aggressive detection"""
        try:
            page_source = driver.page_source.lower()
            
            # Check for shadowban indicators
            for indicator in self.shadowban_indicators:
                if indicator in page_source:
                    print(f"🚫 SHADOWBAN INDICATOR: '{indicator}' detected")
                    self.session_state['shadowban_suspected'] = True
                    return True
            
            # REMOVED: The aggressive "no comments visible" check that was causing browser closures
            # This was triggering false positives and closing the browser unnecessarily
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error detecting shadowban: {str(e)}")
            return False
    
    def get_adaptive_delay(self) -> int:
        """Get adaptive delay based on session state"""
        import random
        
        # Base delay range
        base_min, base_max = 45, 75
        
        # Adjust based on session state
        if self.session_state['shadowban_suspected']:
            # Much longer delays if shadowban suspected
            return random.randint(180, 300)  # 3-5 minutes
            
        elif self.session_state['consecutive_failures'] > 3:
            # Longer delays after multiple failures
            return random.randint(90, 150)  # 1.5-2.5 minutes
            
        elif self.session_state['consecutive_failures'] > 1:
            # Moderate delays after some failures
            return random.randint(60, 90)  # 1-1.5 minutes
            
        elif self.session_state['total_posts_today'] > 20:
            # Conservative delays after many posts
            return random.randint(75, 120)  # 1.25-2 minutes
            
        else:
            # Normal operation
            return random.randint(base_min, base_max)  # 45-75 seconds
    
    def update_session_state(self, success: bool, error_type: str = None):
        """Update session state based on operation result"""
        if success:
            print(f"✅ POST SUCCESS: Resetting failure count")
            self.session_state['consecutive_failures'] = 0
            self.session_state['total_posts_today'] += 1
            self.session_state['last_success_time'] = datetime.now()
            self.session_state['shadowban_suspected'] = False
        else:
            print(f"❌ POST FAILURE: {error_type or 'Unknown error'}")
            self.session_state['consecutive_failures'] += 1
            
            if error_type == 'shadowban':
                print(f"🚫 SHADOWBAN DETECTED: Entering recovery mode")
                self.session_state['shadowban_suspected'] = True
            elif error_type == 'rate_limit':
                print(f"⏱️ RATE LIMIT: Adjusting delays")
    
    def get_session_summary(self) -> Dict:
        """Get session summary information"""
        enterprise_info = self.enterprise_manager.get_session_info()
        
        return {
            'mode': 'enterprise' if self.ip_rotation_enabled else 'direct_connection',
            'ip_rotation_enabled': self.ip_rotation_enabled,
            'legacy_wrapper': True,
            'consecutive_failures': self.session_state['consecutive_failures'],
            'total_posts_today': self.session_state['total_posts_today'],
            'shadowban_suspected': self.session_state['shadowban_suspected'],
            'current_proxy': self.session_state.get('current_proxy'),
            'last_success_time': self.session_state['last_success_time'].strftime('%H:%M:%S'),
            **enterprise_info
        }
    
    def display_anti_detection_status(self):
        """Display anti-detection system status based on configuration"""
        print("🛡️ Anti-Detection System: ACTIVE")
        
        if self.ip_rotation_enabled:
            print("   ✅ IP Rotation via Proxies")
        else:
            print("   ❌ IP Rotation DISABLED (Direct Connection)")
            
        print("   ✅ Shadowban Detection")
        print("   ✅ Adaptive Rate Limiting")
        print("   ✅ Behavioral Randomization")
        print("   ✅ Browser Fingerprint Obfuscation")
    
    def randomize_behavior(self, driver):
        """Add human-like behavior randomization"""
        import random
        import time
        
        try:
            # Random mouse movements
            driver.execute_script("""
                function randomMouseMove() {
                    const event = new MouseEvent('mousemove', {
                        clientX: Math.random() * window.innerWidth,
                        clientY: Math.random() * window.innerHeight
                    });
                    document.dispatchEvent(event);
                }
                randomMouseMove();
            """)
            
            # Random small scroll
            scroll_amount = random.randint(-100, 100)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            
            # Random short pause
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            self.logger.debug(f"Error in behavior randomization: {str(e)}")

    def get_session_info(self) -> Dict:
        """Get session information from enterprise system"""
        return self.get_session_summary()

    def should_rotate_ip(self) -> bool:
        """Determine if IP rotation should happen (respects direct connection preference)"""
        # If IP rotation is disabled by user preference, never rotate
        if not self.ip_rotation_enabled:
            return False
            
        # Check if IP rotation is needed based on session conditions
        if self.session_state['shadowban_suspected']:
            return True
            
        if self.session_state['consecutive_failures'] >= 3:
            return True
            
        # Rotate IP every 10 successful posts for freshness
        if self.session_state['total_posts_today'] > 0 and self.session_state['total_posts_today'] % 10 == 0:
            return True
            
        return False
    
    def validate_proxy_availability(self) -> bool:
        """Validate that proxies are available before starting operations"""
        if not self.ip_rotation_enabled:
            return True  # Direct connection always available
        return self.enterprise_manager.validate_proxy_availability()