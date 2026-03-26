"""
File hasher for MemoBase.

hash_file(path) → sha256

Used in incremental engine.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Optional


class FileHasher:
    """SHA256 file hasher for change detection."""
    
    def __init__(self, chunk_size: int = 4096) -> None:
        """Initialize file hasher.
        
        Args:
            chunk_size: Size of chunks to read (default 4KB)
        """
        self.chunk_size = chunk_size
        self._cache: Dict[Path, str] = {}
    
    def hash_file(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of hash
        """
        hasher = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(self.chunk_size), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def hash_file_cached(self, file_path: Path) -> str:
        """Calculate hash with caching.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of hash
        """
        # Check cache
        if file_path in self._cache:
            return self._cache[file_path]
        
        # Calculate hash
        file_hash = self.hash_file(file_path)
        
        # Cache result
        self._cache[file_path] = file_hash
        
        return file_hash
    
    def hash_bytes(self, data: bytes) -> str:
        """Hash byte data.
        
        Args:
            data: Bytes to hash
            
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(data).hexdigest()
    
    def hash_string(self, text: str) -> str:
        """Hash string data.
        
        Args:
            text: String to hash
            
        Returns:
            Hex digest of hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def clear_cache(self) -> None:
        """Clear hash cache."""
        self._cache.clear()
    
    def get_cached_hash(self, file_path: Path) -> Optional[str]:
        """Get cached hash for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Cached hash or None
        """
        return self._cache.get(file_path)
    
    def invalidate_cache(self, file_path: Path) -> None:
        """Invalidate cache entry for file.
        
        Args:
            file_path: Path to file
        """
        self._cache.pop(file_path, None)
    
    def compare_hashes(self, hash1: str, hash2: str) -> bool:
        """Compare two hashes for equality.
        
        Args:
            hash1: First hash
            hash2: Second hash
            
        Returns:
            True if hashes match
        """
        return hash1 == hash2


class IncrementalHasher:
    """Hasher optimized for incremental updates."""
    
    def __init__(self, chunk_size: int = 4096) -> None:
        """Initialize incremental hasher.
        
        Args:
            chunk_size: Size of chunks to read
        """
        self.chunk_size = chunk_size
        self.hasher = FileHasher(chunk_size)
        self.stored_hashes: Dict[Path, str] = {}
    
    def check_for_changes(self, file_path: Path) -> tuple[bool, Optional[str]]:
        """Check if file has changed since last hash.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (changed, old_hash)
        """
        # Get current hash
        current_hash = self.hasher.hash_file(file_path)
        
        # Get stored hash
        stored_hash = self.stored_hashes.get(file_path)
        
        # Compare
        changed = stored_hash is None or current_hash != stored_hash
        
        # Update stored hash
        self.stored_hashes[file_path] = current_hash
        
        return changed, stored_hash
    
    def get_all_hashes(self) -> Dict[Path, str]:
        """Get all stored hashes.
        
        Returns:
            Dictionary of path -> hash
        """
        return self.stored_hashes.copy()
    
    def set_hashes(self, hashes: Dict[Path, str]) -> None:
        """Set stored hashes.
        
        Args:
            hashes: Dictionary of path -> hash
        """
        self.stored_hashes = hashes.copy()
    
    def remove_file(self, file_path: Path) -> None:
        """Remove file from stored hashes.
        
        Args:
            file_path: Path to file
        """
        self.stored_hashes.pop(file_path, None)
