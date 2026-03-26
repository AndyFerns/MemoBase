"""
Filesystem scanner for MemoBase.

scan_repo(path) → generator[file_path]

Rules:
- respect .gitignore
- skip binaries
- streaming only
"""

from __future__ import annotations

import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import AsyncGenerator, Generator, List, Optional

from memobase.core.exceptions import ConfigurationError
from memobase.core.models import Config
from memobase.infrastructure.filesystem.ignore import GitignoreParser


class FilesystemScanner:
    """Filesystem scanner with .gitignore support."""
    
    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.bin',
        '.obj', '.o', '.a', '.lib', '.class',
        '.jar', '.war', '.ear', '.zip', '.tar',
        '.gz', '.bz2', '.xz', '.7z', '.rar',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp',
        '.ico', '.svg', '.pdf', '.doc', '.docx',
        '.xls', '.xlsx', '.ppt', '.pptx',
        '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        '.db', '.sqlite', '.sqlite3',
    }
    
    def __init__(self, config: Config) -> None:
        """Initialize filesystem scanner.
        
        Args:
            config: MemoBase configuration
        """
        self.config = config
        self.ignore_parser = GitignoreParser(config.repo_path)
    
    def scan(self, repo_path: Path) -> Generator[Path, None, None]:
        """Scan repository for files.
        
        Args:
            repo_path: Path to repository root
            
        Yields:
            File paths
        """
        try:
            for root, dirs, files in os.walk(repo_path):
                root_path = Path(root)
                
                # Filter directories to skip
                dirs[:] = [
                    d for d in dirs
                    if self._should_process_directory(root_path / d)
                ]
                
                # Yield files
                for file_name in files:
                    file_path = root_path / file_name
                    
                    if self._should_process_file(file_path):
                        yield file_path
                        
        except Exception as e:
            raise ConfigurationError(f"Failed to scan repository: {e}")
    
    async def scan_async(self, repo_path: Path) -> AsyncGenerator[Path, None]:
        """Async scan repository for files.
        
        Args:
            repo_path: Path to repository root
            
        Yields:
            File paths
        """
        loop = asyncio.get_event_loop()
        
        with ProcessPoolExecutor() as executor:
            # Run scan in executor
            future = loop.run_in_executor(executor, self._scan_sync_list, repo_path)
            file_list = await future
            
            # Yield files
            for file_path in file_list:
                yield file_path
    
    def _scan_sync_list(self, repo_path: Path) -> List[Path]:
        """Synchronous scan returning list.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            List of file paths
        """
        return list(self.scan(repo_path))
    
    def _should_process_directory(self, dir_path: Path) -> bool:
        """Check if directory should be processed.
        
        Args:
            dir_path: Directory path
            
        Returns:
            True if directory should be processed
        """
        dir_name = dir_path.name
        
        # Skip hidden directories
        if dir_name.startswith('.'):
            return False
        
        # Skip common non-source directories
        skip_dirs = {
            'node_modules', 'vendor', 'dist', 'build', 'target',
            '__pycache__', '.git', '.svn', '.hg', '.venv', 'venv',
            'env', 'site-packages', 'eggs', '.eggs',
        }
        
        if dir_name in skip_dirs:
            return False
        
        # Check .gitignore
        try:
            relative_path = dir_path.relative_to(self.config.repo_path)
            if self.ignore_parser.is_ignored(relative_path):
                return False
        except ValueError:
            pass
        
        return True
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed.
        
        Args:
            file_path: File path
            
        Returns:
            True if file should be processed
        """
        # Check extension
        file_ext = file_path.suffix.lower()
        
        # Skip binary files
        if file_ext in self.BINARY_EXTENSIONS:
            return False
        
        # Check if in included extensions
        if self.config.included_extensions:
            if file_ext not in self.config.included_extensions:
                return False
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            max_size = self.config.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                return False
        except OSError:
            return False
        
        # Check .gitignore
        try:
            relative_path = file_path.relative_to(self.config.repo_path)
            if self.ignore_parser.is_ignored(relative_path):
                return False
        except ValueError:
            pass
        
        # Check excluded patterns
        file_name = file_path.name
        for pattern in self.config.excluded_patterns:
            if self._matches_pattern(file_name, pattern):
                return False
        
        return True
    
    def _matches_pattern(self, file_name: str, pattern: str) -> bool:
        """Check if filename matches pattern.
        
        Args:
            file_name: File name to check
            pattern: Pattern to match
            
        Returns:
            True if matches
        """
        import fnmatch
        return fnmatch.fnmatch(file_name, pattern)
    
    def get_file_count(self, repo_path: Path) -> int:
        """Get total file count.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Number of files
        """
        return sum(1 for _ in self.scan(repo_path))
    
    def get_total_size(self, repo_path: Path) -> int:
        """Get total size of all files.
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        for file_path in self.scan(repo_path):
            try:
                total_size += file_path.stat().st_size
            except OSError:
                pass
        return total_size
