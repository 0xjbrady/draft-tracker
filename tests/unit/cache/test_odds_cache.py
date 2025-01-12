"""Unit tests for odds cache."""
import os
import json
import time
import pytest
from app.cache.odds_cache import OddsCache

@pytest.fixture
def cache_file():
    """Temporary cache file for testing."""
    file_path = "test_cache.json"
    yield file_path
    # Cleanup after tests
    if os.path.exists(file_path):
        os.remove(file_path)

@pytest.fixture
def cache(cache_file):
    """Create a cache instance with a short duration for testing."""
    return OddsCache(cache_duration=2, cache_file=cache_file)  # 2 seconds cache duration

def test_cache_and_retrieve(cache):
    """Test basic caching and retrieval of odds data."""
    sport_key = "test_sport"
    test_data = [{"test": "data"}]
    
    # Cache data
    cache.cache_odds(sport_key, test_data)
    
    # Retrieve data
    cached = cache.get_cached_odds(sport_key)
    assert cached == test_data

def test_cache_expiration(cache):
    """Test that cached data expires after the specified duration."""
    sport_key = "test_sport"
    test_data = [{"test": "data"}]
    
    # Cache data
    cache.cache_odds(sport_key, test_data)
    
    # Verify data is cached
    assert cache.get_cached_odds(sport_key) == test_data
    
    # Wait for cache to expire
    time.sleep(3)
    
    # Verify data is expired
    assert cache.get_cached_odds(sport_key) is None

def test_api_limits(cache):
    """Test tracking of API request limits."""
    # Update limits
    cache.update_api_limits(remaining=100, used=400)
    
    # Verify limits are tracked
    stats = cache.get_cache_stats()
    assert stats["remaining_requests"] == 100
    assert stats["used_requests"] == 400
    assert stats["last_api_call"] is not None

def test_request_rate_limiting(cache):
    """Test rate limiting of API requests."""
    # Make initial request
    assert cache.can_make_request() is True
    
    # Update last API call time
    cache.update_api_limits(remaining=100, used=400)
    
    # Immediate request should be blocked
    assert cache.can_make_request(min_interval=1.0) is False
    
    # Wait and try again
    time.sleep(1.1)
    assert cache.can_make_request(min_interval=1.0) is True

def test_clear_expired(cache):
    """Test clearing of expired cache entries."""
    # Add multiple entries
    cache.cache_odds("sport1", [{"test": "data1"}])
    cache.cache_odds("sport2", [{"test": "data2"}])
    
    # Wait for entries to expire
    time.sleep(3)
    
    # Clear expired entries
    cleared = cache.clear_expired()
    assert cleared == 2
    
    # Verify cache is empty
    assert cache.get_cache_stats()["cached_sports"] == []

def test_cache_stats(cache):
    """Test retrieval of cache statistics."""
    # Add some data
    cache.cache_odds("sport1", [{"test": "data1"}])
    cache.update_api_limits(remaining=100, used=400)
    
    # Get stats
    stats = cache.get_cache_stats()
    
    # Verify stats structure
    assert "cached_sports" in stats
    assert "remaining_requests" in stats
    assert "used_requests" in stats
    assert "last_api_call" in stats
    assert "cache_file" in stats
    
    # Verify stats values
    assert "sport1" in stats["cached_sports"]
    assert stats["remaining_requests"] == 100
    assert stats["used_requests"] == 400

def test_disk_persistence(cache, cache_file):
    """Test that cache data persists to disk."""
    # Add data to cache
    sport_key = "test_sport"
    test_data = [{"test": "data"}]
    cache.cache_odds(sport_key, test_data)
    
    # Verify file exists
    assert os.path.exists(cache_file)
    
    # Read file contents
    with open(cache_file, 'r') as f:
        data = json.load(f)
    
    # Verify data structure
    assert "cache" in data
    assert "last_api_call" in data
    assert "remaining_requests" in data
    assert "used_requests" in data
    assert "last_updated" in data
    
    # Verify cached data
    assert sport_key in data["cache"]
    assert data["cache"][sport_key]["data"] == test_data

def test_load_from_disk(cache_file):
    """Test loading cache from disk on initialization."""
    # Create first cache instance and add data
    cache1 = OddsCache(cache_duration=2, cache_file=cache_file)
    cache1.cache_odds("test_sport", [{"test": "data"}])
    cache1.update_api_limits(remaining=100, used=400)
    
    # Create new cache instance that should load from disk
    cache2 = OddsCache(cache_duration=2, cache_file=cache_file)
    
    # Verify data was loaded
    stats = cache2.get_cache_stats()
    assert "test_sport" in stats["cached_sports"]
    assert stats["remaining_requests"] == 100
    assert stats["used_requests"] == 400

def test_clear_all(cache):
    """Test clearing all cache data and removing cache file."""
    # Add data to cache
    cache.cache_odds("test_sport", [{"test": "data"}])
    
    # Clear all data
    cache.clear_all()
    
    # Verify cache is empty
    stats = cache.get_cache_stats()
    assert stats["cached_sports"] == []
    assert stats["remaining_requests"] == 500
    assert stats["used_requests"] == 0
    assert stats["last_api_call"] is None
    
    # Verify cache file is removed
    assert not os.path.exists(cache.get_cache_stats()["cache_file"]) 