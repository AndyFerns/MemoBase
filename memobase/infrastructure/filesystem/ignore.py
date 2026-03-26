"""
Gitignore parser for MemoBase.

Parses .gitignore files and determines if paths should be ignored.
"""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import List, Optional, Set


class GitignoreParser:
    """Parser for .gitignore files."""
    
    def __init__(self, repo_path: Path) -> None:
        """Initialize gitignore parser.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.patterns: List[tuple] = []  # (pattern, is_negation, is_directory)
        self._load_gitignore()
    
    def _load_gitignore(self) -> None:
        """Load .gitignore file from repository."""
        gitignore_path = self.repo_path / ".gitignore"
        
        if not gitignore_path.exists():
            return
        
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    self._add_pattern(line.strip())
        except IOError:
            pass
    
    def _add_pattern(self, pattern: str) -> None:
        """Add a pattern from .gitignore line.
        
        Args:
            pattern: Pattern string
        """
        # Skip empty lines and comments
        if not pattern or pattern.startswith('#'):
            return
        
        # Check for negation
        is_negation = pattern.startswith('!')
        if is_negation:
            pattern = pattern[1:]
        
        # Check for directory-only pattern
        is_directory = pattern.endswith('/')
        if is_directory:
            pattern = pattern[:-1]
        
        # Remove leading slash (relative to gitignore location)
        if pattern.startswith('/'):
            pattern = pattern[1:]
        
        self.patterns.append((pattern, is_negation, is_directory))
    
    def is_ignored(self, path: Path) -> bool:
        """Check if path should be ignored.
        
        Args:
            path: Path to check (relative to repo root)
            
        Returns:
            True if path should be ignored
        """
        path_str = str(path).replace(os.sep, '/')
        path_parts = path_str.split('/')
        is_directory = path_str.endswith('/')
        
        ignored = False
        
        for pattern, is_negation, is_dir_pattern in self.patterns:
            # Check if pattern matches
            if self._matches(path_str, path_parts, pattern, is_dir_pattern, is_directory):
                if is_negation:
                    ignored = False
                else:
                    ignored = True
        
        return ignored
    
    def _matches(self, path_str: str, path_parts: List[str], pattern: str, 
                 is_dir_pattern: bool, is_directory: bool) -> bool:
        """Check if pattern matches path.
        
        Args:
            path_str: Full path string
            path_parts: Path components
            pattern: Pattern to match
            is_dir_pattern: Whether pattern is directory-only
            is_directory: Whether path is a directory
            
        Returns:
            True if matches
        """
        # Directory-only patterns only match directories
        if is_dir_pattern and not is_directory:
            return False
        
        # Check for exact match
        if fnmatch.fnmatch(path_str, pattern):
            return True
        
        # Check for match against any path component
        for part in path_parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        
        # Check for match with ** (match across directories)
        if '**' in pattern:
            # Convert ** to a regex-like match
            simple_pattern = pattern.replace('**/', '*')
            if fnmatch.fnmatch(path_str, simple_pattern):
                return True
        
        return False
    
    def get_patterns(self) -> List[str]:
        """Get all patterns.
        
        Returns:
            List of pattern strings
        """
        return [p[0] for p in self.patterns]


class GlobalIgnoreParser:
    """Global ignore patterns for common files."""
    
    GLOBAL_PATTERNS = [
        # Version control
        '.git/', '.svn/', '.hg/',
        # Python
        '__pycache__/', '*.pyc', '*.pyo', '*.pyd',
        '.venv/', 'venv/', 'env/',
        '*.egg-info/', '.eggs/',
        # Node.js
        'node_modules/',
        # IDE
        '.idea/', '.vscode/',
        '.DS_Store', 'Thumbs.db',
        # Build
        'build/', 'dist/', 'target/',
        '*.log', '*.tmp',
    ]
    
    def __init__(self) -> None:
        """Initialize global ignore parser."""
        self.patterns = self.GLOBAL_PATTERNS
    
    def is_ignored(self, path: Path) -> bool:
        """Check if path matches global ignore patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if should be ignored
        """
        path_str = str(path).replace(os.sep, '/')
        
        for pattern in self.patterns:
            if pattern.endswith('/'):
                # Directory pattern
                dir_pattern = pattern[:-1]
                if dir_pattern in path_str:
                    return True
            else:
                # File pattern
                if fnmatch.fnmatch(path_str, pattern):
                    return True
        
        return False
