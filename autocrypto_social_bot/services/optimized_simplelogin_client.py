"""
Optimized SimpleLogin Client - Enhanced Performance Implementation

This module extends our existing SimpleLogin client with targeted optimizations
without requiring the entire SimpleLogin repository.
"""

import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass

from .enhanced_simplelogin_client import (
    EnhancedSimpleLoginAPI, SimpleLoginAPIError, AliasInfo
)

class TokenBucketRateLimiter:
    """
    Enhanced rate limiter using token bucket algorithm
    Provides smoother request distribution and better burst handling
    """
    def __init__(self, capacity: int = 50, refill_rate: float = 50/60):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.logger = logging.getLogger(__name__)
    
    def acquire(self, tokens_needed: int = 1) -> bool:
        """Acquire tokens from the bucket"""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        
        if self.tokens >= tokens_needed:
            self.tokens -= tokens_needed
            return True
        return False
    
    def wait_for_tokens(self, tokens_needed: int = 1):
        """Wait until tokens are available"""
        while not self.acquire(tokens_needed):
            wait_time = tokens_needed / self.refill_rate
            self.logger.info(f"Rate limit: waiting {wait_time:.1f}s for {tokens_needed} tokens")
            time.sleep(min(wait_time, 1.0))

class PerformanceMetrics:
    """Performance monitoring and analytics"""
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.start_time = time.time()
    
    def record_response_time(self, endpoint: str, response_time: float):
        """Record API response time"""
        self.metrics[f'{endpoint}_response_times'].append(response_time)
        self.counters[f'{endpoint}_requests'] += 1
    
    def record_error(self, endpoint: str, error_type: str):
        """Record API error"""
        self.counters[f'{endpoint}_errors'] += 1
        self.counters[f'error_{error_type}'] += 1
    
    def record_rate_limit_hit(self, endpoint: str):
        """Record rate limit encounter"""
        self.counters[f'{endpoint}_rate_limits'] += 1
        self.counters['total_rate_limits'] += 1
    
    def get_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        total_requests = sum(v for k, v in self.counters.items() if k.endswith('_requests'))
        total_errors = sum(v for k, v in self.counters.items() if k.endswith('_errors'))
        
        if total_requests == 0:
            return {'status': 'no_data'}
        
        # Calculate average response times
        avg_response_times = {}
        for key, times in self.metrics.items():
            if key.endswith('_response_times') and times:
                endpoint = key.replace('_response_times', '')
                avg_response_times[endpoint] = sum(times) / len(times)
        
        success_rate = ((total_requests - total_errors) / total_requests) * 100
        
        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'success_rate': success_rate,
            'avg_response_times': avg_response_times,
            'rate_limit_hits': self.counters.get('total_rate_limits', 0),
            'uptime_hours': (time.time() - self.start_time) / 3600,
            'requests_per_hour': total_requests / max((time.time() - self.start_time) / 3600, 0.1),
            'health_score': min(100, success_rate * 0.7 + 
                               (100 - min(10, self.counters.get('total_rate_limits', 0))) * 0.3)
        }

class OptimizedSimpleLoginClient(EnhancedSimpleLoginAPI):
    """
    Optimized SimpleLogin client with enhanced performance features
    """
    
    def __init__(self, api_key: str, base_url: str = "https://app.simplelogin.io/api"):
        super().__init__(api_key, base_url)
        
        # Replace basic rate limiter with token bucket
        self.rate_limiter = TokenBucketRateLimiter()
        self.metrics = PerformanceMetrics()
        
        self.logger.info("🚀 Optimized SimpleLogin client initialized")
    
    def _make_request_optimized(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Enhanced request method with performance monitoring"""
        # Wait for rate limit token
        self.rate_limiter.wait_for_tokens()
        
        start_time = time.time()
        endpoint_name = endpoint.strip('/').replace('/', '_')
        
        try:
            response = super()._make_request(method, endpoint, **kwargs)
            
            # Record successful request
            response_time = time.time() - start_time
            self.metrics.record_response_time(endpoint_name, response_time)
            
            return response
            
        except SimpleLoginAPIError as e:
            # Record error
            if e.status_code == 429:
                self.metrics.record_rate_limit_hit(endpoint_name)
                error_type = 'rate_limit'
            elif e.status_code >= 500:
                error_type = 'server_error'
            else:
                error_type = 'client_error'
            
            self.metrics.record_error(endpoint_name, error_type)
            raise
    
    # Override parent's _make_request to use optimized version
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        return self._make_request_optimized(method, endpoint, **kwargs)
    
    def bulk_create_aliases_optimized(self, count: int, batch_size: int = 8,
                                    hostname: str = None, note_prefix: str = "Auto-created") -> List[AliasInfo]:
        """
        Optimized bulk alias creation with intelligent batching
        """
        self.logger.info(f"🚀 Starting optimized bulk creation: {count} aliases")
        
        # Pre-validate capacity
        user_info = self.get_user_info()
        if not user_info.get('is_premium'):
            current_aliases = self.get_stats()['nb_alias']
            available = user_info.get('max_alias_free_plan', 15) - current_aliases
            if available < count:
                raise ValueError(f"Insufficient alias capacity: need {count}, have {available}")
        
        aliases = []
        failed_count = 0
        
        # Create in optimized batches
        for batch_start in range(0, count, batch_size):
            batch_end = min(batch_start + batch_size, count)
            batch_aliases = []
            
            self.logger.info(f"📦 Processing batch {batch_start//batch_size + 1}: {batch_start+1}-{batch_end}")
            
            for i in range(batch_start, batch_end):
                try:
                    note = f"{note_prefix} {i+1}/{count}" if note_prefix else None
                    alias = self.create_random_alias(hostname=hostname, note=note)
                    batch_aliases.append(alias)
                    
                    # Micro-delay for sustainability
                    time.sleep(0.1)
                    
                except SimpleLoginAPIError as e:
                    failed_count += 1
                    self.logger.warning(f"⚠️ Failed to create alias {i+1}: {e}")
                    
                    if e.status_code == 429:
                        # Rate limit hit - wait longer
                        self.logger.info("⏳ Rate limit encountered, extending delay...")
                        time.sleep(5)
                    
                    continue
            
            aliases.extend(batch_aliases)
            
            # Inter-batch delay for rate limit management
            if batch_end < count:
                delay = 2 + (failed_count * 0.5)  # Adaptive delay based on failures
                self.logger.info(f"⏱️ Inter-batch delay: {delay}s")
                time.sleep(delay)
        
        success_rate = ((count - failed_count) / count) * 100
        self.logger.info(f"✅ Bulk creation complete: {len(aliases)}/{count} aliases ({success_rate:.1f}% success)")
        
        return aliases
    
    def smart_account_creation_pipeline(self, platform: str, count: int = 5,
                                      username_prefix: str = None) -> List[Dict]:
        """
        Intelligent account creation pipeline with pre-planning
        """
        self.logger.info(f"🎯 Smart pipeline: Creating {count} {platform} accounts")
        
        # Phase 1: Validate SimpleLogin capacity
        user_info = self.get_user_info()
        stats = self.get_stats()
        
        if not user_info.get('is_premium'):
            available_slots = user_info.get('max_alias_free_plan', 15) - stats['nb_alias']
            if available_slots < count:
                raise ValueError(f"Insufficient SimpleLogin capacity: {available_slots}/{count}")
        
        # Phase 2: Create aliases in optimized batches
        aliases = self.bulk_create_aliases_optimized(
            count=count,
            hostname=f"{platform}.com",
            note_prefix=f"{platform.upper()} automation"
        )
        
        # Phase 3: Prepare account data
        accounts = []
        for i, alias in enumerate(aliases):
            account_data = {
                'email_alias': alias.email,
                'alias_id': alias.id,
                'platform': platform,
                'username': f"{username_prefix or platform}_{i+1:03d}",
                'password': self._generate_secure_password(),
                'created_at': time.time(),
                'status': 'created',
                'note': f"Auto-created for {platform} automation"
            }
            accounts.append(account_data)
        
        self.logger.info(f"✅ Pipeline complete: {len(accounts)} accounts ready")
        return accounts
    
    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate secure random password"""
        import random
        import string
        
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        report = self.metrics.get_performance_report()
        
        # Add SimpleLogin-specific metrics
        try:
            stats = self.get_alias_statistics()
            report['simplelogin_stats'] = stats
        except Exception as e:
            self.logger.warning(f"Could not fetch SimpleLogin stats: {e}")
        
        return report
    
    def health_check(self) -> Dict:
        """Comprehensive health check"""
        health = {
            'status': 'healthy',
            'timestamp': time.time(),
            'issues': []
        }
        
        try:
            # Test API connectivity
            start_time = time.time()
            user_info = self.get_user_info()
            api_response_time = time.time() - start_time
            
            health['api_response_time'] = api_response_time
            health['api_status'] = 'connected'
            
            if api_response_time > 5.0:
                health['issues'].append('Slow API response time')
                health['status'] = 'degraded'
            
            # Check rate limiting status
            metrics = self.get_performance_metrics()
            if metrics.get('rate_limit_hits', 0) > 10:
                health['issues'].append('Frequent rate limiting')
                health['status'] = 'degraded'
            
            # Check success rate
            success_rate = metrics.get('success_rate', 100)
            if success_rate < 90:
                health['issues'].append(f'Low success rate: {success_rate:.1f}%')
                health['status'] = 'unhealthy' if success_rate < 75 else 'degraded'
            
        except Exception as e:
            health['status'] = 'unhealthy'
            health['issues'].append(f'API connectivity failed: {str(e)}')
        
        return health

# Example usage and demonstration
if __name__ == "__main__":
    import os
    
    api_key = os.getenv('SIMPLELOGIN_API_KEY')
    if not api_key:
        print("Please set SIMPLELOGIN_API_KEY environment variable")
        exit(1)
    
    # Initialize optimized client
    client = OptimizedSimpleLoginClient(api_key)
    
    # Health check
    health = client.health_check()
    print(f"Health Status: {health['status']}")
    if health['issues']:
        print(f"Issues: {', '.join(health['issues'])}")
    
    # Performance demonstration
    print("\n🚀 Performance Test: Creating 3 test aliases...")
    try:
        aliases = client.bulk_create_aliases_optimized(3, note_prefix="Performance test")
        print(f"✅ Created {len(aliases)} aliases successfully")
        
        # Clean up test aliases
        for alias in aliases:
            client.delete_alias(alias.id)
        print("🧹 Cleaned up test aliases")
        
        # Show performance metrics
        metrics = client.get_performance_metrics()
        print(f"\n📊 Performance Metrics:")
        print(f"   Success Rate: {metrics.get('success_rate', 0):.1f}%")
        print(f"   Health Score: {metrics.get('health_score', 0):.1f}/100")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
    
    print("\n✅ Optimized client demonstration complete!") 