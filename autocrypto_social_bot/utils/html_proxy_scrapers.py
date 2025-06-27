#!/usr/bin/env python3
"""
HTML Proxy Scrapers for various free proxy websites
Scrapes proxies directly from HTML content of proxy listing sites
"""

import requests
import re
import time
import random
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
from urllib.parse import urljoin, urlparse

class HTMLProxyScraper:
    """Base class for HTML proxy scraping"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Realistic headers to avoid detection
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(self.headers)
        
    def extract_ip_port_from_text(self, text: str) -> List[str]:
        """Extract IP:PORT combinations from any text using regex"""
        # Regex pattern for IP:PORT (IPv4:PORT)
        ip_port_pattern = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):[0-9]{1,5}\b'
        
        matches = re.findall(ip_port_pattern, text)
        
        # Validate and filter results
        valid_proxies = []
        for match in matches:
            try:
                ip, port = match.split(':')
                port_num = int(port)
                
                # Basic validation
                if 1 <= port_num <= 65535:
                    # Exclude private IP ranges
                    ip_parts = [int(x) for x in ip.split('.')]
                    if not (
                        (ip_parts[0] == 10) or  # 10.0.0.0/8
                        (ip_parts[0] == 172 and 16 <= ip_parts[1] <= 31) or  # 172.16.0.0/12
                        (ip_parts[0] == 192 and ip_parts[1] == 168) or  # 192.168.0.0/16
                        (ip_parts[0] == 127)  # 127.0.0.0/8 (localhost)
                    ):
                        valid_proxies.append(match)
                        
            except (ValueError, IndexError):
                continue
                
        return list(set(valid_proxies))  # Remove duplicates

class FreeProxyCzScraper(HTMLProxyScraper):
    """Scraper for free-proxy.cz"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "http://free-proxy.cz/en/"
        self.name = "Free-Proxy.cz"
        
    def scrape_proxies(self) -> List[str]:
        """Scrape proxies from free-proxy.cz"""
        try:
            print(f"   🕷️ Scraping {self.name}...")
            
            # Try different endpoints
            endpoints = [
                "",  # Main page
                "proxy_list",
                "proxy-list",
                "free-proxy-list"
            ]
            
            all_proxies = []
            
            for endpoint in endpoints:
                try:
                    url = urljoin(self.base_url, endpoint)
                    response = self.session.get(url, timeout=15)
                    
                    if response.status_code == 200:
                        # Parse HTML with BeautifulSoup
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Strategy 1: Look for table elements
                        tables = soup.find_all('table')
                        for table in tables:
                            table_text = table.get_text()
                            proxies = self.extract_ip_port_from_text(table_text)
                            all_proxies.extend(proxies)
                        
                        # Strategy 2: Look for div/span elements that might contain proxy lists
                        for element in soup.find_all(['div', 'span', 'pre', 'code']):
                            element_text = element.get_text()
                            proxies = self.extract_ip_port_from_text(element_text)
                            all_proxies.extend(proxies)
                        
                        # Strategy 3: Extract from entire page content
                        page_text = soup.get_text()
                        proxies = self.extract_ip_port_from_text(page_text)
                        all_proxies.extend(proxies)
                        
                        if proxies:
                            print(f"   ✅ Found {len(proxies)} proxies from {endpoint or 'main page'}")
                            break  # Stop after first successful endpoint
                            
                    time.sleep(random.uniform(1, 3))  # Be respectful
                    
                except Exception as e:
                    self.logger.debug(f"Error scraping {endpoint}: {str(e)}")
                    continue
            
            # Remove duplicates and return
            unique_proxies = list(set(all_proxies))
            print(f"   📊 {self.name}: {len(unique_proxies)} unique proxies")
            return unique_proxies
            
        except Exception as e:
            print(f"   ❌ {self.name}: {str(e)}")
            return []

class ProxyDockerScraper(HTMLProxyScraper):
    """Scraper for ProxyDocker.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.proxydocker.com/"
        self.name = "ProxyDocker"
        
    def scrape_proxies(self) -> List[str]:
        """Scrape proxies from ProxyDocker.com"""
        try:
            print(f"   🕷️ Scraping {self.name}...")
            
            # Try different search configurations
            search_configs = [
                {},  # Default search
                {'anon': 'elite'},
                {'anon': 'anonymous'},
                {'type': 'http'},
                {'type': 'https'},
                {'type': 'socks4'},
                {'type': 'socks5'},
            ]
            
            all_proxies = []
            
            for config in search_configs:
                try:
                    # Build search URL
                    params = {
                        'action': 'search',
                        'timeout': '10',
                        **config
                    }
                    
                    response = self.session.get(self.base_url, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Strategy 1: Look for the proxy table
                        table = soup.find('table')
                        if table:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                cells = row.find_all('td')
                                if len(cells) >= 1:
                                    # First cell should contain IP:PORT
                                    ip_port_text = cells[0].get_text().strip()
                                    proxies = self.extract_ip_port_from_text(ip_port_text)
                                    all_proxies.extend(proxies)
                        
                        # Strategy 2: Look for any proxy patterns in the page
                        page_text = soup.get_text()
                        proxies = self.extract_ip_port_from_text(page_text)
                        all_proxies.extend(proxies)
                        
                        # Strategy 3: Check for JSON API endpoints
                        try:
                            api_url = urljoin(self.base_url, 'api/proxy')
                            api_response = self.session.get(api_url, timeout=10)
                            if api_response.status_code == 200:
                                api_text = api_response.text
                                api_proxies = self.extract_ip_port_from_text(api_text)
                                all_proxies.extend(api_proxies)
                        except:
                            pass
                        
                    time.sleep(random.uniform(1, 3))  # Be respectful
                    
                except Exception as e:
                    self.logger.debug(f"Error with config {config}: {str(e)}")
                    continue
            
            # Try the JSON API endpoint mentioned in the HTML
            try:
                json_url = urljoin(self.base_url, '?format=json')
                json_response = self.session.get(json_url, timeout=10)
                if json_response.status_code == 200:
                    import json
                    try:
                        data = json_response.json()
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict):
                                    ip = item.get('ip', '')
                                    port = item.get('port', '')
                                    if ip and port:
                                        all_proxies.append(f"{ip}:{port}")
                    except:
                        # Fallback to text extraction
                        json_proxies = self.extract_ip_port_from_text(json_response.text)
                        all_proxies.extend(json_proxies)
            except:
                pass
            
            # Remove duplicates and return
            unique_proxies = list(set(all_proxies))
            print(f"   📊 {self.name}: {len(unique_proxies)} unique proxies")
            return unique_proxies
            
        except Exception as e:
            print(f"   ❌ {self.name}: {str(e)}")
            return []

class FreeProxyListNetScraper(HTMLProxyScraper):
    """Scraper for additional free proxy sites"""
    
    def __init__(self):
        super().__init__()
        self.sites = [
            "https://free-proxy-list.net/",
            "https://www.us-proxy.org/",
            "https://www.sslproxies.org/",
        ]
        self.name = "FreeProxyList.net"
        
    def scrape_proxies(self) -> List[str]:
        """Scrape proxies from multiple free proxy sites"""
        try:
            print(f"   🕷️ Scraping {self.name} sites...")
            
            all_proxies = []
            
            for site_url in self.sites:
                try:
                    print(f"      🌐 Checking {site_url}...")
                    response = self.session.get(site_url, timeout=15)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for tables with proxy data
                        tables = soup.find_all('table', {'class': ['table', 'proxylisttable', 'proxy-table']})
                        if not tables:
                            tables = soup.find_all('table')
                        
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                cells = row.find_all('td')
                                if len(cells) >= 2:
                                    # Usually IP in first cell, port in second
                                    ip = cells[0].get_text().strip()
                                    port = cells[1].get_text().strip()
                                    
                                    if ip and port and port.isdigit():
                                        proxy = f"{ip}:{port}"
                                        # Validate with regex
                                        if self.extract_ip_port_from_text(proxy):
                                            all_proxies.append(proxy)
                        
                        # Fallback: extract any IP:PORT patterns
                        page_text = soup.get_text()
                        fallback_proxies = self.extract_ip_port_from_text(page_text)
                        all_proxies.extend(fallback_proxies)
                        
                    time.sleep(random.uniform(2, 4))  # Be respectful
                    
                except Exception as e:
                    self.logger.debug(f"Error scraping {site_url}: {str(e)}")
                    continue
            
            # Remove duplicates and return
            unique_proxies = list(set(all_proxies))
            print(f"   📊 {self.name}: {len(unique_proxies)} unique proxies")
            return unique_proxies
            
        except Exception as e:
            print(f"   ❌ {self.name}: {str(e)}")
            return []

class HTMLProxyAggregator:
    """Aggregates proxies from all HTML scraping sources"""
    
    def __init__(self):
        self.scrapers = [
            FreeProxyCzScraper(),
            ProxyDockerScraper(),
            FreeProxyListNetScraper(),
        ]
        
    def scrape_all_sources(self) -> List[str]:
        """Scrape proxies from all HTML sources"""
        print("\n🕷️ HTML PROXY SCRAPING INITIATED")
        print("="*60)
        
        all_proxies = []
        successful_scrapers = 0
        
        for scraper in self.scrapers:
            try:
                proxies = scraper.scrape_proxies()
                if proxies:
                    all_proxies.extend(proxies)
                    successful_scrapers += 1
                    print(f"   ✅ {scraper.name}: SUCCESS")
                else:
                    print(f"   ⚠️ {scraper.name}: No proxies found")
                    
            except Exception as e:
                print(f"   ❌ {scraper.name}: FAILED - {str(e)}")
        
        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        
        print("="*60)
        print(f"🕷️ HTML SCRAPING COMPLETE")
        print(f"📊 Sources attempted: {len(self.scrapers)}")
        print(f"✅ Sources successful: {successful_scrapers}")
        print(f"🎯 Total unique proxies: {len(unique_proxies)}")
        print("="*60)
        
        return unique_proxies

# Example usage and testing
if __name__ == "__main__":
    # Test the HTML scraping system
    aggregator = HTMLProxyAggregator()
    proxies = aggregator.scrape_all_sources()
    
    print(f"\n🎯 SCRAPED PROXIES SAMPLE:")
    for i, proxy in enumerate(proxies[:10], 1):
        print(f"   {i:2d}. {proxy}")
    
    if len(proxies) > 10:
        print(f"   ... and {len(proxies) - 10} more") 