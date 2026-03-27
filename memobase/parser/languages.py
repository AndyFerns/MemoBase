"""
Tree-sitter language loading and caching module.

This module provides a centralized way to load and cache Tree-sitter languages
from compiled shared libraries or Python extensions, ensuring efficient language initialization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import tree_sitter
from tree_sitter import Language


class LanguageCache:
    """Singleton cache for Tree-sitter languages."""
    
    _instance: Optional[LanguageCache] = None
    _languages: Dict[str, Language] = {}
    
    def __new__(cls) -> LanguageCache:
        """Create singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_language(self, name: str) -> Language:
        """Get language from cache or load it.
        
        Args:
            name: Language name (e.g., 'python')
            
        Returns:
            Tree-sitter Language instance
            
        Raises:
            ImportError: If language cannot be loaded
        """
        if name not in self._languages:
            self._languages[name] = self._load_language(name)
        return self._languages[name]
    
    def _load_language(self, name: str) -> Language:
        """Load language from compiled shared library or Python extension.
        
        Args:
            name: Language name
            
        Returns:
            Tree-sitter Language instance
            
        Raises:
            ImportError: If language library cannot be found or loaded
        """
        # First try to load from shared library
        build_dir = Path(__file__).parent / "build"
        library_path = build_dir / f"{name}.so"
        
        if library_path.exists():
            try:
                return Language(str(library_path), name)
            except Exception as e:
                print(f"Warning: Failed to load shared library {library_path}: {e}")
        
        # Fallback: try to load from Python extension
        vendor_dir = Path(__file__).parent / "vendor" / f"tree-sitter-{name}"
        extension_dir = vendor_dir / "bindings" / "python" / f"tree_sitter_{name}"
        
        if extension_dir.exists():
            try:
                # Import the Python extension and get the language
                import sys
                sys.path.insert(0, str(vendor_dir / "bindings" / "python"))
                
                # Import the module
                module = __import__(f"tree_sitter_{name}")
                
                # Try to get language from the module
                if hasattr(module, 'language'):
                    # The language() function returns a PyCapsule, need to wrap it
                    language_capsule = module.language()
                    return Language(language_capsule)
                else:
                    raise ImportError(f"No language interface found in tree_sitter_{name}")
                    
            except Exception as e:
                raise ImportError(
                    f"Failed to load Tree-sitter language '{name}' from Python extension: {e}\n"
                    f"Please run: python -m memobase.parser.build_languages"
                )
        
        raise ImportError(
            f"Tree-sitter language library not found for '{name}'\n"
            f"Expected: {library_path} or {extension_dir}\n"
            f"Please run: python -m memobase.parser.build_languages"
        )


# Global language cache instance
_language_cache = LanguageCache()


def get_language(name: str) -> Language:
    """Get Tree-sitter language by name.
    
    Args:
        name: Language name (e.g., 'python')
        
    Returns:
        Tree-sitter Language instance
        
    Raises:
        ImportError: If language cannot be loaded
        
    Example:
        >>> python_lang = get_language("python")
        >>> parser = tree_sitter.Parser()
        >>> parser.set_language(python_lang)
    """
    return _language_cache.get_language(name)
