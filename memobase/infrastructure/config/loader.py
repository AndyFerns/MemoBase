"""
Config loader for MemoBase.

Loads .memobase/config.json

Must:
- validate schema
- provide defaults
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from memobase.core.exceptions import ConfigurationError
from memobase.core.models import Config
from memobase.infrastructure.config.schema import ConfigSchema


class ConfigLoader:
    """Configuration loader with validation."""
    
    DEFAULT_CONFIG_PATH = ".memobase/config.json"
    
    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """Initialize config loader.
        
        Args:
            repo_path: Repository path (uses cwd if None)
        """
        self.repo_path = repo_path or Path.cwd()
        self.schema = ConfigSchema()
    
    def load(self, config_path: Optional[Path] = None) -> Config:
        """Load configuration from file.
        
        Args:
            config_path: Path to config file (uses default if None)
            
        Returns:
            Config instance
        """
        if config_path is None:
            config_path = self.repo_path / self.DEFAULT_CONFIG_PATH
        
        # Load config data
        config_data = self._load_config_file(config_path)
        
        # Merge with defaults
        config_data = self._merge_with_defaults(config_data)
        
        # Validate
        errors = self.schema.validate(config_data)
        if errors:
            raise ConfigurationError(f"Config validation failed: {'; '.join(errors)}")
        
        # Create Config instance
        return Config(**config_data)
    
    def _load_config_file(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in config file: {e}")
        except IOError as e:
            raise ConfigurationError(f"Cannot read config file: {e}")
    
    def _merge_with_defaults(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge config with default values.
        
        Args:
            config_data: Loaded config data
            
        Returns:
            Merged config data
        """
        defaults = self._get_defaults()
        
        # Merge (user values override defaults)
        merged = defaults.copy()
        merged.update(config_data)
        
        # Ensure repo_path is set
        if 'repo_path' not in merged:
            merged['repo_path'] = str(self.repo_path)
        
        return merged
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get default configuration values.
        
        Returns:
            Default configuration dictionary
        """
        return {
            'repo_path': str(self.repo_path),
            'storage_path': '.memobase',
            'max_file_size_mb': 10,
            'parallel_workers': 4,
            'index_batch_size': 1000,
            'graph_max_depth': 5,
            'cache_size_mb': 100,
            'storage_backend': 'file',
            'verbosity': 1,
            'included_extensions': [
                '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc',
                '.cxx', '.rs', '.go', '.rb', '.php', '.h', '.hpp', '.hxx',
            ],
            'excluded_patterns': [
                '*.pyc', '*.pyo', '*.pyd', '__pycache__', '.git', '.svn', '.hg',
                'node_modules', '.vscode', '.idea', '*.log', '*.tmp', '.venv',
                'venv', 'env', 'dist', 'build', 'target',
            ],
        }
    
    def save(self, config: Config, config_path: Optional[Path] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Config instance to save
            config_path: Path to config file (uses default if None)
        """
        if config_path is None:
            config_path = self.repo_path / self.DEFAULT_CONFIG_PATH
        
        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert config to dictionary
        config_data = {
            'repo_path': str(config.repo_path),
            'storage_path': str(config.storage_path),
            'max_file_size_mb': config.max_file_size_mb,
            'parallel_workers': config.parallel_workers,
            'index_batch_size': config.index_batch_size,
            'graph_max_depth': config.graph_max_depth,
            'cache_size_mb': config.cache_size_mb,
            'storage_backend': config.storage_backend,
            'verbosity': config.verbosity,
            'included_extensions': config.included_extensions,
            'excluded_patterns': config.excluded_patterns,
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
        except IOError as e:
            raise ConfigurationError(f"Cannot write config file: {e}")
    
    def create_default_config(self) -> Config:
        """Create default configuration.
        
        Returns:
            Config instance with default values
        """
        defaults = self._get_defaults()
        return Config(**defaults)
