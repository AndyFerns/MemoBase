"""
Path utilities for MemoBase.

Path normalization and manipulation utilities.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Union


class PathUtils:
    """Utility class for path operations."""
    
    @staticmethod
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize path (resolve, absolute).
        
        Args:
            path: Path to normalize
            
        Returns:
            Normalized Path
        """
        return Path(path).resolve().absolute()
    
    @staticmethod
    def make_relative(path: Path, base: Path) -> Path:
        """Make path relative to base.
        
        Args:
            path: Path to make relative
            base: Base path
            
        Returns:
            Relative path
        """
        try:
            return path.relative_to(base)
        except ValueError:
            return path
    
    @staticmethod
    def get_extension(path: Union[str, Path]) -> str:
        """Get file extension (lowercase).
        
        Args:
            path: File path
            
        Returns:
            File extension with dot
        """
        return Path(path).suffix.lower()
    
    @staticmethod
    def remove_extension(path: Union[str, Path]) -> str:
        """Remove file extension.
        
        Args:
            path: File path
            
        Returns:
            Path without extension
        """
        p = Path(path)
        return str(p.with_suffix(''))
    
    @staticmethod
    def ensure_dir(path: Union[str, Path]) -> Path:
        """Ensure directory exists (create if needed).
        
        Args:
            path: Directory path
            
        Returns:
            Path to directory
        """
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    @staticmethod
    def is_subpath(path: Path, potential_parent: Path) -> bool:
        """Check if path is a subpath of potential_parent.
        
        Args:
            path: Path to check
            potential_parent: Potential parent path
            
        Returns:
            True if path is subpath
        """
        try:
            path.relative_to(potential_parent)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def join_paths(*paths: Union[str, Path]) -> Path:
        """Join multiple path components.
        
        Args:
            *paths: Path components
            
        Returns:
            Joined path
        """
        result = Path(paths[0])
        for path in paths[1:]:
            result = result / path
        return result
    
    @staticmethod
    def get_common_base(paths: List[Path]) -> Optional[Path]:
        """Get common base path for multiple paths.
        
        Args:
            paths: List of paths
            
        Returns:
            Common base path or None
        """
        if not paths:
            return None
        
        # Start with first path
        base = paths[0].parent
        
        # Narrow down
        for path in paths[1:]:
            while base and not PathUtils.is_subpath(path, base):
                base = base.parent
        
        return base
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe usage.
        
        Args:
            filename: Filename to sanitize
            
        Returns:
            Safe filename
        """
        # Remove or replace unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        safe = filename
        for char in unsafe_chars:
            safe = safe.replace(char, '_')
        
        # Limit length
        max_length = 255
        if len(safe) > max_length:
            name_part = Path(safe).stem
            ext_part = Path(safe).suffix
            safe = name_part[:max_length - len(ext_part)] + ext_part
        
        return safe
    
    @staticmethod
    def get_file_size(path: Path) -> int:
        """Get file size in bytes.
        
        Args:
            path: File path
            
        Returns:
            File size in bytes (0 if not found)
        """
        try:
            return path.stat().st_size
        except (OSError, IOError):
            return 0
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format size in human readable form.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human readable string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    @staticmethod
    def find_files_by_extension(directory: Path, extension: str) -> List[Path]:
        """Find all files with given extension.
        
        Args:
            directory: Directory to search
            extension: File extension (with or without dot)
            
        Returns:
            List of file paths
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        
        return list(directory.rglob(f"*{extension}"))
    
    @staticmethod
    def touch_file(path: Path) -> None:
        """Create empty file or update timestamp.
        
        Args:
            path: File path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
