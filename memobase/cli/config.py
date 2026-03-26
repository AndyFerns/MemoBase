"""
CLI configuration management.
"""

from pathlib import Path
from typing import Any, Dict, Optional

# Global configuration storage
_global_config: Dict[str, Any] = {
    'verbose': False,
    'quiet': False,
    'json': False,
    'no_color': False,
    'config': None,
    'profile': False,
    'debug': False,
}


def set_global_options(options: Dict[str, Any]) -> None:
    """Set global configuration options."""
    _global_config.update(options)


def get_option(key: str, default: Any = None) -> Any:
    """Get a global configuration option."""
    return _global_config.get(key, default)


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return _global_config.get('verbose', False)


def is_quiet() -> bool:
    """Check if quiet mode is enabled."""
    return _global_config.get('quiet', False)


def is_json_output() -> bool:
    """Check if JSON output is enabled."""
    return _global_config.get('json', False)


def is_no_color() -> bool:
    """Check if color output is disabled."""
    return _global_config.get('no_color', False)


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return _global_config.get('debug', False)


def is_profile() -> bool:
    """Check if profiling is enabled."""
    return _global_config.get('profile', False)


def get_config_path() -> Optional[Path]:
    """Get configuration file path."""
    config_path = _global_config.get('config')
    return Path(config_path) if config_path else None


def load_config_file(config_path: Path) -> Dict[str, Any]:
    """Load configuration from file."""
    try:
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_path}: {e}")


def save_config_file(config_path: Path, config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    import json
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        'repo_path': '.',
        'max_file_size_mb': 10,
        'excluded_patterns': [
            '*.pyc', '*.pyo', '*.pyd', '__pycache__', '.git', '.svn', '.hg',
            'node_modules', '.vscode', '.idea', '*.log', '*.tmp'
        ],
        'included_extensions': [
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc',
            '.cxx', '.rs', '.go', '.rb', '.php', '.h', '.hpp', '.hxx'
        ],
        'parallel_workers': 4,
        'index_batch_size': 1000,
        'graph_max_depth': 5,
        'cache_size_mb': 100,
        'storage_backend': 'file',
        'storage_path': '.memobase',
    }
