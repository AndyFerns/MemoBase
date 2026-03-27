"""
Parser factory for creating language-specific parsers.
"""

from pathlib import Path
from typing import Dict, List, Optional, Type

from memobase.core.exceptions import ParseError
from memobase.core.interfaces import ParserInterface
from memobase.core.models import FileType
from memobase.parser.base import BaseParser
from memobase.parser.python import PythonParser
from memobase.parser.javascript import JavaScriptParser


class ParserFactory:
    """Factory for creating language-specific parsers."""
    
    _parsers: Dict[FileType, Type[ParserInterface]] = {
        FileType.PYTHON: PythonParser,
        FileType.JAVASCRIPT: JavaScriptParser,
        # Add more parsers as they are implemented
        # FileType.TYPESCRIPT: TypeScriptParser,
        # FileType.JAVA: JavaParser,
        # FileType.C: CParser,
        # FileType.CPP: CppParser,
        # FileType.RUST: RustParser,
        # FileType.GO: GoParser,
        # FileType.RUBY: RubyParser,
        # FileType.PHP: PhpParser,
    }
    
    @classmethod
    def create_parser(cls, file_path: Path) -> ParserInterface:
        """Create appropriate parser for file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            ParserInterface instance
            
        Raises:
            ParseError: If no parser available for file type
        """
        if not file_path.exists():
            raise ParseError(f"File not found: {file_path}")
        
        # Detect file type
        file_type = cls._detect_file_type(file_path)
        
        # Get parser class
        parser_class = cls._parsers.get(file_type)
        if not parser_class:
            raise ParseError(f"No parser available for file type: {file_type}")
        
        print("FACTORY LOADED FROM:", __file__)
        print("PARSERS AT LOAD:", ParserFactory._parsers)
        
        # Create and return parser instance
        try:
            return parser_class()
        except Exception as e:
            raise ParseError(f"Failed to create parser for {file_type}: {str(e)}")
    
    @classmethod
    def create_parser_by_type(cls, file_type: FileType) -> ParserInterface:
        """Create parser by file type.
        
        Args:
            file_type: FileType enum value
            
        Returns:
            ParserInterface instance
            
        Raises:
            ParseError: If no parser available for file type
        """
        parser_class = cls._parsers.get(file_type)
        if not parser_class:
            raise ParseError(f"No parser available for file type: {file_type}")
        
        try:
            return parser_class()
        except Exception as e:
            raise ParseError(f"Failed to create parser for {file_type}: {str(e)}")
    
    @classmethod
    def get_supported_types(cls) -> List[FileType]:
        """Get list of supported file types.
        
        Returns:
            List of FileType enum values
        """
        return list(cls._parsers.keys())
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of all supported file extensions.
        
        Returns:
            List of file extensions (including leading dot)
        """
        extensions = []
        for file_type in cls._parsers.keys():
            parser = cls.create_parser_by_type(file_type)
            extensions.extend(parser.get_supported_extensions())
        return extensions
    
    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        """Check if file is supported.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file type is supported
        """
        try:
            file_type = cls._detect_file_type(file_path)
            return file_type in cls._parsers
        except ParseError:
            return False
    
    @classmethod
    def register_parser(cls, file_type: FileType, parser_class: Type[ParserInterface]) -> None:
        """Register a new parser for a file type.
        
        Args:
            file_type: FileType enum value
            parser_class: Parser class to register
        """
        cls._parsers[file_type] = parser_class
    
    @classmethod
    def get_parser_by_extension(cls, extension: str) -> Optional[ParserInterface]:
        """Get parser by file extension.
        
        Args:
            extension: File extension (e.g., '.py', '.js')
            
        Returns:
            ParserInterface instance or None if not supported
        """
        print("ID BEFORE:", id(ParserFactory._parsers))
        # Normalize extension
        ext = extension.lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        
        # Detect file type from extension
        file_type = cls._detect_file_type_from_ext(ext)
        
        if file_type == FileType.UNKNOWN:
            return None
        
        parser_class = cls._parsers.get(file_type)
        if not parser_class:
            return None
        
        print("ID OF PARSERS:", id(cls._parsers))
        print("PARSERS CONTENT:", cls._parsers)
        
        print("\nDETECTED FILE TYPE:", file_type, id(file_type))
        print("FACTORY KEYS:", [(k, id(k)) for k in cls._parsers.keys()])
        
        try:
            return parser_class()
        except Exception as e:
            # Stupid a*s tree sitter throws errors when it can't find the right parser
            # Hours of debugging for this sh*t
            # Hours wasted: 3h
            print("PARSER INIT ERROR:", e)
            return None
    
    @staticmethod
    def _detect_file_type_from_ext(ext: str) -> FileType:
        """Detect file type from extension string."""
        extension_map = {
            ".py": FileType.PYTHON,
            ".pyi": FileType.PYTHON,
            ".js": FileType.JAVASCRIPT,
            ".jsx": FileType.JAVASCRIPT,
            ".ts": FileType.TYPESCRIPT,
            ".tsx": FileType.TYPESCRIPT,
            ".java": FileType.JAVA,
            ".c": FileType.C,
            ".cpp": FileType.CPP,
            ".cc": FileType.CPP,
            ".cxx": FileType.CPP,
            ".rs": FileType.RUST,
            ".go": FileType.GO,
            ".rb": FileType.RUBY,
            ".php": FileType.PHP,
        }
        return extension_map.get(ext, FileType.UNKNOWN)
    
    @staticmethod
    def _detect_file_type(file_path: Path) -> FileType:
        """Detect file type from extension."""
        extension_map = {
            ".py": FileType.PYTHON,
            ".pyi": FileType.PYTHON,
            ".js": FileType.JAVASCRIPT,
            ".jsx": FileType.JAVASCRIPT,
            ".ts": FileType.TYPESCRIPT,
            ".tsx": FileType.TYPESCRIPT,
            ".java": FileType.JAVA,
            ".c": FileType.C,
            ".cpp": FileType.CPP,
            ".cc": FileType.CPP,
            ".cxx": FileType.CPP,
            ".rs": FileType.RUST,
            ".go": FileType.GO,
            ".rb": FileType.RUBY,
            ".php": FileType.PHP,
        }
        
        extension = file_path.suffix.lower()
        return extension_map.get(extension, FileType.UNKNOWN)
