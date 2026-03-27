"""
Build script for Tree-sitter language libraries.

This script builds Tree-sitter languages from grammar sources and compiles
them into shared libraries that can be loaded by the languages module.
"""

from __future__ import annotations

import sys
from pathlib import Path

from tree_sitter import Language


def build_languages() -> None:
    """Build all supported Tree-sitter languages."""
    print("Building Tree-sitter language libraries...")
    
    # Build directory
    build_dir = Path(__file__).parent / "build"
    build_dir.mkdir(exist_ok=True)
    
    # Supported languages and their grammar directories
    languages = {
        "python": "vendor/tree-sitter-python",
    }
    
    # Build each language
    for language_name, grammar_dir in languages.items():
        grammar_path = Path(__file__).parent / grammar_dir
        
        if not grammar_path.exists():
            print(f"⚠️  Grammar directory not found: {grammar_path}")
            print(f"   Please clone the grammar repository:")
            print(f"   git clone https://github.com/tree-sitter/tree-sitter-python.git")
            print(f"   mv tree-sitter-python {grammar_path}")
            continue
        
        print(f"Building {language_name}...")
        
        try:
            # Build the language library
            library_path = build_dir / f"{language_name}.so"
            Language.build_library(
                str(library_path),
                [str(grammar_path)]
            )
            
            if library_path.exists():
                print(f"✅ Built {language_name}: {library_path}")
            else:
                print(f"❌ Failed to build {language_name}")
                
        except Exception as e:
            print(f"❌ Error building {language_name}: {e}")
    
    print("\nBuild complete!")
    
    # List built libraries
    built_libs = list(build_dir.glob("*.so"))
    if built_libs:
        print(f"Built libraries: {[lib.name for lib in built_libs]}")
    else:
        print("No libraries built. Check grammar directories.")


def main() -> None:
    """Main entry point."""
    try:
        build_languages()
    except KeyboardInterrupt:
        print("\nBuild interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
