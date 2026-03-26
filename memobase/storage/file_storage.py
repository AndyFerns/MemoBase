"""
File-based storage implementation.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List

import aiofiles
import orjson

from memobase.core.exceptions import StorageError
from memobase.core.interfaces import StorageInterface


class FileStorage(StorageInterface):
    """File-based storage using JSONL format."""
    
    def __init__(self, storage_dir: Path) -> None:
        """Initialize file storage.
        
        Args:
            storage_dir: Directory for storage files
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.data_dir = self.storage_dir / "data"
        self.index_dir = self.storage_dir / "index"
        self.graph_dir = self.storage_dir / "graph"
        self.meta_dir = self.storage_dir / "meta"
        
        for dir_path in [self.data_dir, self.index_dir, self.graph_dir, self.meta_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def store(self, data: Any, key: str) -> None:
        """Store data with given key."""
        try:
            file_path = self._get_file_path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            # Write to file
            file_path.write_text(json_data, encoding='utf-8')
            
        except Exception as e:
            raise StorageError(f"Failed to store data for key '{key}': {str(e)}")
    
    def retrieve(self, key: str) -> Any:
        """Retrieve data by key."""
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            # Read file
            json_data = file_path.read_text(encoding='utf-8')
            
            # Deserialize data
            if json_data.strip().startswith('{') or json_data.strip().startswith('['):
                return orjson.loads(json_data)
            else:
                return json_data
                
        except Exception as e:
            raise StorageError(f"Failed to retrieve data for key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """Delete data by key."""
        try:
            file_path = self._get_file_path(key)
            
            if file_path.exists():
                file_path.unlink()
                return True
            return False
            
        except Exception as e:
            raise StorageError(f"Failed to delete data for key '{key}': {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if data exists for key."""
        file_path = self._get_file_path(key)
        return file_path.exists()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with given prefix."""
        keys = []
        
        # Determine which directories to search
        search_dirs = [self.data_dir, self.index_dir, self.graph_dir, self.meta_dir]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            # Walk through directory
            for file_path in search_dir.rglob("*.json"):
                # Convert file path to key
                relative_path = file_path.relative_to(search_dir)
                key = str(relative_path.with_suffix(''))
                
                # Apply prefix filter
                if not prefix or key.startswith(prefix):
                    keys.append(key)
        
        return sorted(keys)
    
    async def store_async(self, data: Any, key: str) -> None:
        """Async version of store."""
        try:
            file_path = self._get_file_path(key)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            # Write to file asynchronously
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json_data)
                
        except Exception as e:
            raise StorageError(f"Failed to store data asynchronously for key '{key}': {str(e)}")
    
    async def retrieve_async(self, key: str) -> Any:
        """Async version of retrieve."""
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return None
            
            # Read file asynchronously
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                json_data = await f.read()
            
            # Deserialize data
            if json_data.strip().startswith('{') or json_data.strip().startswith('['):
                return orjson.loads(json_data)
            else:
                return json_data
                
        except Exception as e:
            raise StorageError(f"Failed to retrieve data asynchronously for key '{key}': {str(e)}")
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        # Determine subdirectory based on key prefix
        if key.startswith('memory_unit:'):
            return self.data_dir / f"{key.replace('memory_unit:', '')}.json"
        elif key.startswith('index:'):
            return self.index_dir / f"{key.replace('index:', '')}.json"
        elif key.startswith('graph:'):
            return self.graph_dir / f"{key.replace('graph:', '')}.json"
        elif key.startswith('meta:'):
            return self.meta_dir / f"{key.replace('meta:', '')}.json"
        else:
            # Default to data directory
            return self.data_dir / f"{key}.json"
    
    def store_batch(self, data_items: Dict[str, Any]) -> None:
        """Store multiple data items."""
        for key, data in data_items.items():
            self.store(data, key)
    
    def retrieve_batch(self, keys: List[str]) -> Dict[str, Any]:
        """Retrieve multiple data items."""
        results = {}
        for key in keys:
            results[key] = self.retrieve(key)
        return results
    
    def clear_all(self) -> None:
        """Clear all stored data."""
        try:
            for dir_path in [self.data_dir, self.index_dir, self.graph_dir, self.meta_dir]:
                if dir_path.exists():
                    for file_path in dir_path.rglob("*"):
                        if file_path.is_file():
                            file_path.unlink()
                            
        except Exception as e:
            raise StorageError(f"Failed to clear storage: {str(e)}")
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'data_files': 0,
            'index_files': 0,
            'graph_files': 0,
            'meta_files': 0,
        }
        
        dir_mapping = {
            self.data_dir: 'data_files',
            self.index_dir: 'index_files',
            self.graph_dir: 'graph_files',
            self.meta_dir: 'meta_files',
        }
        
        for dir_path, stat_key in dir_mapping.items():
            if dir_path.exists():
                for file_path in dir_path.rglob("*.json"):
                    if file_path.is_file():
                        stats['total_files'] += 1
                        stats[stat_key] += 1
                        stats['total_size_bytes'] += file_path.stat().st_size
        
        return stats
    
    def compact_storage(self) -> None:
        """Compact storage by removing duplicates and optimizing layout."""
        # This is a placeholder for storage compaction
        # In practice, you might implement:
        # - Remove duplicate data
        # - Optimize file layout
        # - Compress old data
        pass
    
    def backup_storage(self, backup_path: Path) -> None:
        """Backup storage to specified path."""
        import shutil
        
        try:
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            shutil.copytree(self.storage_dir, backup_path)
            
        except Exception as e:
            raise StorageError(f"Failed to backup storage: {str(e)}")
    
    def restore_storage(self, backup_path: Path) -> None:
        """Restore storage from backup."""
        import shutil
        
        try:
            if not backup_path.exists():
                raise StorageError(f"Backup path does not exist: {backup_path}")
            
            if self.storage_dir.exists():
                shutil.rmtree(self.storage_dir)
            
            shutil.copytree(backup_path, self.storage_dir)
            
        except Exception as e:
            raise StorageError(f"Failed to restore storage: {str(e)}")


class CompressedFileStorage(FileStorage):
    """File storage with compression."""
    
    def __init__(self, storage_dir: Path, compression_level: int = 6) -> None:
        """Initialize compressed file storage.
        
        Args:
            storage_dir: Directory for storage files
            compression_level: Compression level (1-9)
        """
        super().__init__(storage_dir)
        self.compression_level = compression_level
    
    def store(self, data: Any, key: str) -> None:
        """Store compressed data."""
        try:
            import gzip
            
            file_path = self._get_file_path(key)
            file_path = file_path.with_suffix(file_path.suffix + '.gz')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Serialize and compress data
            if hasattr(data, 'to_json'):
                json_data = data.to_json()
            else:
                json_data = orjson.dumps(data).decode()
            
            compressed_data = gzip.compress(
                json_data.encode('utf-8'),
                compresslevel=self.compression_level
            )
            
            # Write compressed data
            file_path.write_bytes(compressed_data)
            
        except Exception as e:
            raise StorageError(f"Failed to store compressed data for key '{key}': {str(e)}")
    
    def retrieve(self, key: str) -> Any:
        """Retrieve and decompress data."""
        try:
            import gzip
            
            file_path = self._get_file_path(key)
            file_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            if not file_path.exists():
                return None
            
            # Read and decompress data
            compressed_data = file_path.read_bytes()
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            
            # Deserialize data
            if json_data.strip().startswith('{') or json_data.strip().startswith('['):
                return orjson.loads(json_data)
            else:
                return json_data
                
        except Exception as e:
            raise StorageError(f"Failed to retrieve compressed data for key '{key}': {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if compressed data exists."""
        file_path = self._get_file_path(key)
        file_path = file_path.with_suffix(file_path.suffix + '.gz')
        return file_path.exists()
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with given prefix."""
        keys = []
        
        # Determine which directories to search
        search_dirs = [self.data_dir, self.index_dir, self.graph_dir, self.meta_dir]
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            # Walk through directory
            for file_path in search_dir.rglob("*.json.gz"):
                # Convert file path to key
                relative_path = file_path.relative_to(search_dir)
                key = str(relative_path.with_suffix('').with_suffix(''))
                
                # Apply prefix filter
                if not prefix or key.startswith(prefix):
                    keys.append(key)
        
        return sorted(keys)
