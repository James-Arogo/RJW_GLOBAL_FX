"""
Cache Service Module
=====================
In-memory and Redis-compatible caching layer for improved performance.
"""

import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, Callable, Union
from functools import wraps
from collections import OrderedDict
import threading


class CacheEntry:
    """Represents a single cache entry with expiration."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.hits = 0
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        if self.ttl <= 0:  # TTL of 0 or less means never expires
            return False
        return time.time() - self.created_at > self.ttl
    
    def hit(self):
        """Record a cache hit."""
        self.hits += 1


class InMemoryCache:
    """
    Thread-safe in-memory cache with LRU eviction and TTL support.
    
    Features:
    - TTL (time-to-live) expiration
    - LRU (Least Recently Used) eviction
    - Thread-safe operations
    - Automatic cleanup of expired entries
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default time-to-live in seconds
        """
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.stats['misses'] += 1
                return None
            
            if entry.is_expired():
                del self.cache[key]
                self.stats['misses'] += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.hit()
            self.stats['hits'] += 1
            
            return entry.value
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if successful
        """
        with self.lock:
            ttl = ttl if ttl is not None else self.default_ttl
            
            # Evict if at capacity
            while len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[key] = CacheEntry(value, ttl)
            self.cache.move_to_end(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self.lock:
            self.cache.clear()
    
    def exists(self, key: str) -> bool:
        """Check if a key exists and is not expired."""
        return self.get(key) is not None
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if self.cache:
            self.cache.popitem(last=False)
            self.stats['evictions'] += 1
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        with self.lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = self.stats['hits'] / total_requests if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'evictions': self.stats['evictions'],
                'hit_rate': round(hit_rate * 100, 2)
            }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (simple prefix matching)
            
        Returns:
            Number of keys invalidated
        """
        with self.lock:
            matching_keys = [
                key for key in self.cache.keys()
                if key.startswith(pattern)
            ]
            
            for key in matching_keys:
                del self.cache[key]
            
            return len(matching_keys)


class CacheService:
    """
    High-level caching service with support for different cache backends.
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the cache service.
        
        Args:
            redis_url: Optional Redis URL for distributed caching
        """
        self.memory_cache = InMemoryCache(max_size=5000, default_ttl=300)
        self.redis_client = None
        
        # Try to connect to Redis if URL provided
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
            except Exception as e:
                print(f"Redis connection failed, using in-memory cache: {e}")
                self.redis_client = None
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache (tries Redis first, falls back to memory)."""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except:
                pass
        
        return self.memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set a value in cache."""
        # Always set in memory cache
        self.memory_cache.set(key, value, ttl)
        
        # Also set in Redis if available
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
            except:
                pass
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        result = self.memory_cache.delete(key)
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        return result
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern."""
        count = self.memory_cache.invalidate_pattern(pattern)
        
        if self.redis_client:
            try:
                keys = self.redis_client.keys(f"{pattern}*")
                if keys:
                    self.redis_client.delete(*keys)
                    count = len(keys)
            except:
                pass
        
        return count
    
    # ============================================
    # Specialized Cache Methods
    # ============================================
    
    def cache_prices(self, prices: Dict[str, float], ttl: int = 5) -> None:
        """Cache current market prices (short TTL for real-time data)."""
        self.set('prices:current', prices, ttl)
    
    def get_cached_prices(self) -> Optional[Dict[str, float]]:
        """Get cached market prices."""
        return self.get('prices:current')
    
    def cache_user_stats(self, user_id: int, stats: Dict, ttl: int = 60) -> None:
        """Cache user statistics."""
        self.set(f'user:stats:{user_id}', stats, ttl)
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get cached user statistics."""
        return self.get(f'user:stats:{user_id}')
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """Invalidate all cache entries for a user."""
        return self.invalidate_pattern(f'user:*:{user_id}')
    
    def cache_platform_stats(self, stats: Dict, ttl: int = 300) -> None:
        """Cache platform-wide statistics."""
        self.set('platform:stats', stats, ttl)
    
    def get_platform_stats(self) -> Optional[Dict]:
        """Get cached platform statistics."""
        return self.get('platform:stats')
    
    def get_stats(self) -> Dict:
        """Get cache service statistics."""
        return self.memory_cache.get_stats()


# ============================================
# Caching Decorator
# ============================================

def cached(
    ttl: int = 300,
    key_prefix: Optional[str] = None,
    cache_instance: Optional[CacheService] = None
):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Optional key prefix (defaults to function name)
        cache_instance: Optional cache service instance
        
    Usage:
        @cached(ttl=60, key_prefix='user_balance')
        def get_user_balance(user_id):
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            cache = cache_instance or cache_service
            prefix = key_prefix or f.__name__
            
            # Generate cache key
            key = cache._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = f(*args, **kwargs)
            cache.set(key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate
        
    Usage:
        @invalidate_cache('user:stats:*')
        def update_user_balance(user_id, amount):
            ...
    """
    def decorator(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            cache_service.invalidate_pattern(pattern)
            return result
        return wrapper
    return decorator


# Global cache service instance
cache_service = CacheService()
