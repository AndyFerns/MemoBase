"""
Cache manager for MemoBase storage.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional, Tuple

from memobase.core.exceptions import StorageError


class CacheManager:
    """In-memory cache manager with LRU eviction."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600) -> None:
        """Initialize cache manager.
        
        Args:
            max_size: Maximum number of cached items
            ttl_seconds: Time-to-live for cached items in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, timestamp)
        self.access_order: Dict[str, float] = {}  # key -> last access time
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            self._remove_key(key)
            self.misses += 1
            return None
        
        # Update access time
        self.access_order[key] = time.time()
        self.hits += 1
        
        return value
    
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        current_time = time.time()
        
        # Remove existing key if present
        if key in self.cache:
            self._remove_key(key)
        
        # Evict if necessary
        while len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Add new item
        self.cache[key] = (value, current_time)
        self.access_order[key] = current_time
    
    def remove(self, key: str) -> bool:
        """Remove key from cache."""
        if key in self.cache:
            self._remove_key(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.access_order.clear()
        self.hits = 0
        self.misses = 0
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds,
        }
    
    def _remove_key(self, key: str) -> None:
        """Remove key from cache and access order."""
        if key in self.cache:
            del self.cache[key]
        if key in self.access_order:
            del self.access_order[key]
    
    def _evict_lru(self) -> None:
        """Evict least recently used item."""
        if not self.access_order:
            return
        
        # Find least recently used key
        lru_key = min(self.access_order.items(), key=lambda x: x[1])[0]
        self._remove_key(lru_key)
    
    def cleanup_expired(self) -> int:
        """Clean up expired items."""
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.cache.items():
            if current_time - timestamp > self.ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            self._remove_key(key)
        
        return len(expired_keys)


class PersistentCache(CacheManager):
    """Cache with persistent storage backing."""
    
    def __init__(self, storage, max_size: int = 1000, ttl_seconds: int = 3600) -> None:
        """Initialize persistent cache.
        
        Args:
            storage: Storage backend for persistence
            max_size: Maximum number of cached items
            ttl_seconds: Time-to-live for cached items
        """
        super().__init__(max_size, ttl_seconds)
        self.storage = storage
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache or storage."""
        # Try cache first
        value = super().get(key)
        if value is not None:
            return value
        
        # Try storage
        try:
            value = self.storage.retrieve(key)
            if value is not None:
                # Cache the retrieved value
                self.put(key, value)
            return value
        except Exception:
            return None
    
    def put(self, key: str, value: Any, persist: bool = True) -> None:
        """Put value in cache and optionally persist."""
        super().put(key, value)
        
        if persist:
            try:
                self.storage.store(value, key)
            except Exception as e:
                raise StorageError(f"Failed to persist cache value: {str(e)}")
    
    def remove(self, key: str, persist: bool = True) -> bool:
        """Remove key from cache and optionally from storage."""
        cache_removed = super().remove(key)
        
        if persist:
            try:
                storage_removed = self.storage.delete(key)
                return cache_removed or storage_removed
            except Exception:
                return cache_removed
        
        return cache_removed
    
    def clear(self, persist: bool = False) -> None:
        """Clear cache and optionally storage."""
        super().clear()
        
        if persist:
            try:
                self.storage.clear_all()
            except Exception as e:
                raise StorageError(f"Failed to clear persistent storage: {str(e)}")
    
    def preload_cache(self, keys: list) -> None:
        """Preload cache with specified keys."""
        try:
            batch_data = self.storage.retrieve_batch(keys)
            for key, value in batch_data.items():
                if value is not None:
                    super().put(key, value)
        except Exception:
            pass  # Ignore preload errors


class HierarchicalCache:
    """Hierarchical cache with multiple levels."""
    
    def __init__(self, levels: list) -> None:
        """Initialize hierarchical cache.
        
        Args:
            levels: List of cache levels (L1, L2, etc.)
        """
        self.levels = levels
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache hierarchy."""
        for i, level in enumerate(self.levels):
            value = level.get(key)
            if value is not None:
                # Promote to higher levels if not already there
                for j in range(i):
                    self.levels[j].put(key, value)
                return value
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put value in all cache levels."""
        for level in self.levels:
            level.put(key, value)
    
    def remove(self, key: str) -> bool:
        """Remove key from all cache levels."""
        removed = False
        for level in self.levels:
            if level.remove(key):
                removed = True
        return removed
    
    def clear(self) -> None:
        """Clear all cache levels."""
        for level in self.levels:
            level.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all cache levels."""
        stats = {}
        for i, level in enumerate(self.levels):
            stats[f'L{i+1}'] = level.get_stats()
        return stats


class CacheKeyGenerator:
    """Utility for generating cache keys."""
    
    @staticmethod
    def generate_key(prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_parts = [prefix]
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest())
        
        return ':'.join(key_parts)
    
    @staticmethod
    def generate_file_key(file_path: str, content_hash: str = None) -> str:
        """Generate cache key for file."""
        if content_hash:
            return f"file:{file_path}:{content_hash}"
        else:
            return f"file:{file_path}"
    
    @staticmethod
    def generate_query_key(query: str, filters: dict = None) -> str:
        """Generate cache key for query."""
        if filters:
            filter_hash = hashlib.md5(str(filters).encode()).hexdigest()
            return f"query:{hashlib.md5(query.encode()).hexdigest()}:{filter_hash}"
        else:
            return f"query:{hashlib.md5(query.encode()).hexdigest()}"
    
    @staticmethod
    def generate_symbol_key(symbol_name: str, file_path: str) -> str:
        """Generate cache key for symbol."""
        return f"symbol:{symbol_name}:{file_path}"


class CacheWarmer:
    """Cache warming utility."""
    
    def __init__(self, cache: CacheManager) -> None:
        """Initialize cache warmer.
        
        Args:
            cache: Cache manager to warm
        """
        self.cache = cache
    
    def warm_cache(self, data_source, keys: list, batch_size: int = 100) -> None:
        """Warm cache with data from source."""
        try:
            # Process in batches
            for i in range(0, len(keys), batch_size):
                batch_keys = keys[i:i + batch_size]
                
                # Retrieve batch data
                if hasattr(data_source, 'retrieve_batch'):
                    batch_data = data_source.retrieve_batch(batch_keys)
                else:
                    batch_data = {}
                    for key in batch_keys:
                        value = data_source.retrieve(key)
                        if value is not None:
                            batch_data[key] = value
                
                # Cache the data
                for key, value in batch_data.items():
                    self.cache.put(key, value)
                    
        except Exception as e:
            raise StorageError(f"Failed to warm cache: {str(e)}")
    
    def warm_frequently_accessed(self, access_log: list, limit: int = 100) -> None:
        """Warm cache with frequently accessed keys."""
        # Count access frequency
        frequency = {}
        for key in access_log:
            frequency[key] = frequency.get(key, 0) + 1
        
        # Get most frequently accessed keys
        frequent_keys = sorted(frequency.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        # Warm cache with these keys
        for key, _ in frequent_keys:
            # This would need to be implemented based on your data source
            pass
