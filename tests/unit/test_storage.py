"""
Unit tests for storage module.
"""

import pytest

from memobase.core.models import Config, MemoryUnit
from memobase.storage.cache import CacheManager
from memobase.storage.file_storage import FileStorage


class TestCacheManager:
    """Test cache manager."""
    
    def test_cache_creation(self):
        """Test cache initialization."""
        cache = CacheManager(max_size=100)
        assert cache is not None
        assert cache.max_size == 100
    
    def test_cache_get_set(self):
        """Test cache get and set operations."""
        cache = CacheManager()
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
    
    def test_cache_miss(self):
        """Test cache miss."""
        cache = CacheManager()
        
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_eviction(self):
        """Test cache eviction when full."""
        cache = CacheManager(max_size=2)
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1
        
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"


class TestFileStorage:
    """Test file storage backend."""
    
    def test_storage_creation(self, temp_dir):
        """Test storage initialization."""
        storage = FileStorage(temp_dir)
        assert storage is not None
        assert storage.base_path == temp_dir
    
    def test_store_and_load(self, temp_dir):
        """Test storing and loading data."""
        storage = FileStorage(temp_dir)
        
        data = {"test": "data", "number": 42}
        storage.store(data, "test_key")
        
        loaded = storage.load("test_key")
        assert loaded["test"] == "data"
        assert loaded["number"] == 42
    
    def test_exists(self, temp_dir):
        """Test checking if key exists."""
        storage = FileStorage(temp_dir)
        
        data = {"test": "data"}
        storage.store(data, "test_key")
        
        assert storage.exists("test_key")
        assert not storage.exists("nonexistent")
    
    def test_delete(self, temp_dir):
        """Test deleting data."""
        storage = FileStorage(temp_dir)
        
        data = {"test": "data"}
        storage.store(data, "test_key")
        assert storage.exists("test_key")
        
        storage.delete("test_key")
        assert not storage.exists("test_key")
    
    def test_list_keys(self, temp_dir):
        """Test listing keys."""
        storage = FileStorage(temp_dir)
        
        storage.store({"a": 1}, "key1")
        storage.store({"b": 2}, "key2")
        
        keys = storage.list_keys()
        assert "key1" in keys
        assert "key2" in keys
