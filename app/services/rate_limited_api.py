import os
import requests
import time
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from threading import Lock
import logging

logger = logging.getLogger(__name__)

class RateLimitedAPI:
    """Rate-limited API client with caching and retry logic"""
    
    def __init__(self, api_key: str, base_url: str, headers: Dict[str, str]):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = headers
        
        # Rate limiting configuration
        self.max_requests_per_minute = 10  # Conservative limit
        self.max_requests_per_day = 100   # Daily limit
        self.request_timestamps = []
        self.daily_requests = 0
        self.last_reset_date = datetime.now().date()
        
        # Thread safety
        self.lock = Lock()
        
        # Cache configuration
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        
    def _is_rate_limited(self) -> bool:
        """Check if we're hitting rate limits"""
        with self.lock:
            now = datetime.now()
            
            # Reset daily counter if new day
            if now.date() > self.last_reset_date:
                self.daily_requests = 0
                self.last_reset_date = now.date()
            
            # Check daily limit
            if self.daily_requests >= self.max_requests_per_day:
                logger.warning("Daily API limit reached")
                return True
            
            # Check minute limit
            minute_ago = now - timedelta(minutes=1)
            self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]
            
            if len(self.request_timestamps) >= self.max_requests_per_minute:
                logger.warning("Minute API limit reached")
                return True
            
            return False
    
    def _wait_for_rate_limit(self) -> None:
        """Wait if rate limited"""
        if self._is_rate_limited():
            wait_time = 60  # Wait 1 minute
            logger.info(f"Rate limited, waiting {wait_time} seconds")
            time.sleep(wait_time)
    
    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key for request"""
        params_str = json.dumps(params, sort_keys=True) if params else ""
        return f"{endpoint}:{params_str}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if not expired"""
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                logger.debug(f"Cache hit for {cache_key}")
                return data
            else:
                # Remove expired cache entry
                del self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict) -> None:
        """Save data to cache"""
        self.cache[cache_key] = (data, datetime.now())
        logger.debug(f"Cached data for {cache_key}")
    
    def _make_request_with_retry(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with retry logic"""
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                # Check rate limits before request
                self._wait_for_rate_limit()
                
                logger.info(f"Making API request to {endpoint} (attempt {attempt + 1})")
                
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30,
                    allow_redirects=True
                )
                
                # Update rate limiting counters
                with self.lock:
                    self.request_timestamps.append(datetime.now())
                    self.daily_requests += 1
                
                # Handle different response codes
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"API request successful: {endpoint}")
                    return data
                
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limited (429), waiting {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 403:
                    # Forbidden - API key issue
                    logger.error(f"API key issue (403): {response.text}")
                    return None
                
                elif response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"Server error ({response.status_code}), retrying...")
                    time.sleep(self.retry_delay)
                    continue
                
                else:
                    # Other client errors
                    logger.error(f"API request failed: {response.status_code} - {response.text}")
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1})")
                time.sleep(self.retry_delay)
                continue
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception: {e}")
                time.sleep(self.retry_delay)
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        logger.error(f"All retry attempts failed for {endpoint}")
        return None
    
    def get(self, endpoint: str, params: Dict = None, use_cache: bool = True) -> Optional[Dict]:
        """Make GET request with rate limiting and caching"""
        if not self.api_key:
            logger.warning("API key not set")
            return None
        
        # Check cache first
        if use_cache:
            cache_key = self._get_cache_key(endpoint, params)
            cached_data = self._get_from_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Make request
        data = self._make_request_with_retry(endpoint, params)
        
        # Cache successful response
        if data and use_cache:
            cache_key = self._get_cache_key(endpoint, params)
            self._save_to_cache(cache_key, data)
        
        return data
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        with self.lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            recent_requests = [ts for ts in self.request_timestamps if ts > minute_ago]
            
            return {
                'requests_last_minute': len(recent_requests),
                'requests_today': self.daily_requests,
                'max_per_minute': self.max_requests_per_minute,
                'max_per_day': self.max_requests_per_day,
                'cache_size': len(self.cache),
                'is_rate_limited': self._is_rate_limited()
            }
    
    def clear_cache(self) -> None:
        """Clear the cache"""
        with self.lock:
            self.cache.clear()
            logger.info("Cache cleared")
