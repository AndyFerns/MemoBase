"""
Unit tests for parser module.
"""

import pytest

from memobase.parser.base import BaseParser
from memobase.parser.factory import ParserFactory
from memobase.parser.python import PythonParser


class TestBaseParser:
    """Test base parser functionality."""
    
    def test_base_parser_init(self):
        """Test base parser initialization."""
        parser = BaseParser()
        assert parser.language == "base"
    
    def test_parse_not_implemented(self, sample_python_file):
        """Test that parse raises NotImplementedError."""
        parser = BaseParser()
        
        with pytest.raises(NotImplementedError):
            parser.parse(sample_python_file)


class TestParserFactory:
    """Test parser factory."""
    
    def test_factory_creation(self):
        """Test factory creation."""
        factory = ParserFactory()
        assert factory is not None
    
    def test_get_parser_by_extension_python(self):
        """Test getting parser for Python files."""
        factory = ParserFactory()
        parser = factory.get_parser_by_extension(".py")
        
        assert parser is not None
        assert parser.language == "python"
    
    def test_get_parser_by_extension_javascript(self):
        """Test getting parser for JavaScript files."""
        factory = ParserFactory()
        parser = factory.get_parser_by_extension(".js")
        
        assert parser is not None
        assert parser.language == "javascript"
    
    def test_get_parser_by_extension_unknown(self):
        """Test getting parser for unknown extension."""
        factory = ParserFactory()
        parser = factory.get_parser_by_extension(".xyz")
        
        assert parser is None
    
    def test_get_parser_by_type(self):
        """Test getting parser by language type."""
        factory = ParserFactory()
        parser = factory.get_parser_by_type("python")
        
        assert parser is not None
        assert parser.language == "python"


class TestPythonParser:
    """Test Python parser."""
    
    def test_python_parser_init(self):
        """Test Python parser initialization."""
        parser = PythonParser()
        assert parser.language == "python"
    
    def test_can_parse_python_file(self, sample_python_file):
        """Test parsing Python file."""
        parser = PythonParser()
        
        # This would need actual tree-sitter setup to work fully
        # For now, just test the interface
        assert parser.can_parse(sample_python_file)
    
    def test_cannot_parse_js_file(self, sample_js_file):
        """Test that Python parser cannot parse JS files."""
        parser = PythonParser()
        
        assert not parser.can_parse(sample_js_file)
