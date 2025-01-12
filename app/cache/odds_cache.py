"""Cache module for storing and managing odds data."""
import os
import json
import time
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ..monitoring.metrics import (
    CACHE_HITS,
    CACHE_MISSES,
    CACHE_SIZE,
    CACHE_ENTRIES_CLEARED
)

class OddsCache:
    def __init__(self, cache_duration: int = 300, cache_file: str = "odds_cache.json"):
        """Initialize the odds cache.
        
        Args:
            cache_duration: How long to keep cached data in seconds
            cache_file: Path to the cache file for disk persistence
        """
        self._cache: Dict[str, Dict] = {}
        self._cache_duration = cache_duration
        self._cache_file = cache_file
        self._last_api_call: Optional[float] = None
        self._remaining_requests: int = 500  # Default daily limit
        self._used_requests: int = 0
        
        # Load cache from disk if it exists
        self._load_cache()

    def _load_cache(self) -> None:
        """Load cached data from disk."""
        if not os.path.exists(self._cache_file):
            return
            
        try:
            with open(self._cache_file, 'r') as f:
                data = json.load(f)
                self._cache = data.get("cache", {})
                self._last_api_call = data.get("last_api_call")
                self._remaining_requests = data.get("remaining_requests", 500)
                self._used_requests = data.get("used_requests", 0)
                logging.info(f"Loaded cache from {self._cache_file}")
        except Exception as e:
            logging.error(f"Error loading cache from disk: {str(e)}")

    def _save_cache(self) -> None:
        """Save current cache state to disk."""
        try:
            data = {
                "cache": self._cache,
                "last_api_call": self._last_api_call,
                "remaining_requests": self._remaining_requests,
                "used_requests": self._used_requests,
                "last_updated": time.time()
            }
            
            with open(self._cache_file, 'w') as f:
                json.dump(data, f)
            logging.info(f"Saved cache to {self._cache_file}")
        except Exception as e:
            logging.error(f"Error saving cache to disk: {str(e)}")

    def get_cached_odds(self, sport_key: str) -> Optional[List[Dict]]:
        """Get cached odds data for a sport if not expired."""
        if sport_key in self._cache:
            entry = self._cache[sport_key]
            if time.time() - entry["timestamp"] < self._cache_duration:
                CACHE_HITS.inc()
                return entry["data"]
        CACHE_MISSES.inc()
        return None

    def cache_odds(self, sport_key: str, odds_data: List[Dict]) -> None:
        """Cache odds data for a sport."""
        self._cache[sport_key] = {
            "data": odds_data,
            "timestamp": time.time()
        }
        CACHE_SIZE.set(len(self._cache))
        self._save_cache()

    def update_api_limits(self, remaining: int, used: int) -> None:
        """Update API request limits based on response headers."""
        self._remaining_requests = remaining
        self._used_requests = used
        self._last_api_call = time.time()
        self._save_cache()  # Save updated limits

    def can_make_request(self, min_interval: float = 1.0) -> bool:
        """Check if we can make a new API request based on rate limits."""
        if self._last_api_call is None:
            return True

        # Check time since last request
        time_since_last = time.time() - self._last_api_call
        if time_since_last < min_interval:
            return False

        # Check remaining requests
        return self._remaining_requests > 0

    def get_cache_stats(self) -> Dict:
        """Get current cache statistics."""
        return {
            "cached_sports": list(self._cache.keys()),
            "remaining_requests": self._remaining_requests,
            "used_requests": self._used_requests,
            "last_api_call": self._last_api_call,
            "cache_file": self._cache_file
        }

    def clear_expired(self) -> None:
        """Clear expired entries from cache."""
        now = time.time()
        expired = []
        for key in self._cache:
            if now - self._cache[key]["timestamp"] >= self._cache_duration:
                expired.append(key)
        
        for key in expired:
            del self._cache[key]
        
        CACHE_ENTRIES_CLEARED.inc(len(expired))
        CACHE_SIZE.set(len(self._cache))
        if expired:
            self._save_cache()

    def clear_all(self) -> None:
        """Clear all cached data and remove cache file."""
        self._cache = {}
        self._last_api_call = None
        self._remaining_requests = 500
        self._used_requests = 0
        
        if os.path.exists(self._cache_file):
            try:
                os.remove(self._cache_file)
                logging.info(f"Removed cache file {self._cache_file}")
            except Exception as e:
                logging.error(f"Error removing cache file: {str(e)}") 

# Create a singleton instance
odds_cache = OddsCache() 