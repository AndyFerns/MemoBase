"""
Config schema for MemoBase.

Defines validation rules for configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class ConfigSchema:
    """Schema for validating MemoBase configuration."""
    
    def __init__(self) -> None:
        """Initialize config schema."""
        self.validators = {
            'repo_path': self._validate_path,
            'storage_path': self._validate_path,
            'max_file_size_mb': self._validate_positive_int,
            'parallel_workers': self._validate_positive_int,
            'index_batch_size': self._validate_positive_int,
            'graph_max_depth': self._validate_positive_int,
            'cache_size_mb': self._validate_positive_int,
            'storage_backend': self._validate_storage_backend,
            'verbosity': self._validate_verbosity,
            'included_extensions': self._validate_string_list,
            'excluded_patterns': self._validate_string_list,
        }
    
    def validate(self, config_data: Dict[str, Any]) -> List[str]:
        """Validate configuration data.
        
        Args:
            config_data: Configuration dictionary to validate
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        for key, value in config_data.items():
            if key in self.validators:
                validator = self.validators[key]
                error = validator(value)
                if error:
                    errors.append(f"{key}: {error}")
        
        # Check required fields
        required_fields = ['repo_path', 'storage_path']
        for field in required_fields:
            if field not in config_data:
                errors.append(f"Missing required field: {field}")
        
        return errors
    
    def _validate_path(self, value: Any) -> Optional[str]:
        """Validate path field.
        
        Args:
            value: Value to validate
            
        Returns:
            Error message or None if valid
        """
        if not isinstance(value, (str, Path)):
            return "Must be a string or Path"
        return None
    
    def _validate_positive_int(self, value: Any) -> Optional[str]:
        """Validate positive integer field.
        
        Args:
            value: Value to validate
            
        Returns:
            Error message or None if valid
        """
        if not isinstance(value, int):
            return "Must be an integer"
        if value <= 0:
            return "Must be positive"
        return None
    
    def _validate_storage_backend(self, value: Any) -> Optional[str]:
        """Validate storage backend field.
        
        Args:
            value: Value to validate
            
        Returns:
            Error message or None if valid
        """
        valid_backends = ['file', 'sqlite', 'memory']
        if value not in valid_backends:
            return f"Must be one of: {', '.join(valid_backends)}"
        return None
    
    def _validate_verbosity(self, value: Any) -> Optional[str]:
        """Validate verbosity field.
        
        Args:
            value: Value to validate
            
        Returns:
            Error message or None if valid
        """
        if not isinstance(value, int):
            return "Must be an integer"
        if value < 0 or value > 3:
            return "Must be between 0 and 3"
        return None
    
    def _validate_string_list(self, value: Any) -> Optional[str]:
        """Validate string list field.
        
        Args:
            value: Value to validate
            
        Returns:
            Error message or None if valid
        """
        if not isinstance(value, list):
            return "Must be a list"
        for item in value:
            if not isinstance(item, str):
                return "All items must be strings"
        return None
    
    def get_schema(self) -> Dict[str, Dict[str, Any]]:
        """Get schema definition as dictionary.
        
        Returns:
            Schema definition
        """
        return {
            'repo_path': {
                'type': 'string',
                'required': True,
                'description': 'Path to repository root',
            },
            'storage_path': {
                'type': 'string',
                'required': True,
                'default': '.memobase',
                'description': 'Path to storage directory',
            },
            'max_file_size_mb': {
                'type': 'integer',
                'required': False,
                'default': 10,
                'description': 'Maximum file size in MB',
            },
            'parallel_workers': {
                'type': 'integer',
                'required': False,
                'default': 4,
                'description': 'Number of parallel workers',
            },
            'index_batch_size': {
                'type': 'integer',
                'required': False,
                'default': 1000,
                'description': 'Batch size for indexing',
            },
            'graph_max_depth': {
                'type': 'integer',
                'required': False,
                'default': 5,
                'description': 'Maximum graph traversal depth',
            },
            'cache_size_mb': {
                'type': 'integer',
                'required': False,
                'default': 100,
                'description': 'Cache size in MB',
            },
            'storage_backend': {
                'type': 'string',
                'required': False,
                'default': 'file',
                'enum': ['file', 'sqlite', 'memory'],
                'description': 'Storage backend type',
            },
            'verbosity': {
                'type': 'integer',
                'required': False,
                'default': 1,
                'minimum': 0,
                'maximum': 3,
                'description': 'Verbosity level (0-3)',
            },
            'included_extensions': {
                'type': 'array',
                'required': False,
                'items': {'type': 'string'},
                'description': 'File extensions to include',
            },
            'excluded_patterns': {
                'type': 'array',
                'required': False,
                'items': {'type': 'string'},
                'description': 'Patterns to exclude',
            },
        }
