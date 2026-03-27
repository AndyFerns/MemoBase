"""
Project setup module for MemoBase.

Handles initialization of MemoBase in a repository.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from memobase.core.exceptions import ConfigurationError
from memobase.infrastructure.config.loader import ConfigLoader


class ProjectSetup:
    """Handles project initialization and setup."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize project setup.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.repo_path = Path(config.get('repo_path', '.')).absolute()
        self.storage_path = self.repo_path / config.get('storage_path', '.memobase')
    
    def initialize_repo(self, force: bool = False) -> None:
        """Initialize MemoBase in repository.
        
        Args:
            force: Force initialization even if already exists
            
        Raises:
            ConfigurationError: If initialization fails
        """
        # Check if already initialized
        if self.storage_path.exists() and not force:
            raise ConfigurationError(
                f"MemoBase already initialized at {self.storage_path}. "
                "Use --force to reinitialize."
            )
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.storage_path / 'index').mkdir(exist_ok=True)
        (self.storage_path / 'graph').mkdir(exist_ok=True)
        (self.storage_path / 'memory').mkdir(exist_ok=True)
        (self.storage_path / 'cache').mkdir(exist_ok=True)
        
        # Create default config file
        config_loader = ConfigLoader(self.repo_path)
        from memobase.core.models import Config
        cfg = Config(**self.config)
        config_loader.save(cfg)
        
        # Create .gitignore if it doesn't exist
        self._create_gitignore()
    
    def _create_gitignore(self) -> None:
        """Create .gitobase ignore entries in .gitignore."""
        gitignore_path = self.repo_path / '.gitignore'
        
        memobase_entries = [
            '# MemoBase',
            '.memobase/',
            '*.memobase',
            ''
        ]
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            if '.memobase/' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n' + '\n'.join(memobase_entries))
        else:
            gitignore_path.write_text('\n'.join(memobase_entries))
