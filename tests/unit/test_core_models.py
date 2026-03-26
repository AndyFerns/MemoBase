"""
Unit tests for core models.
"""

from pathlib import Path

import pytest

from memobase.core.models import (
    Config,
    Index,
    MemoryUnit,
    ParsedFile,
    Query,
    QueryType,
    RelationType,
    Response,
    SymbolInfo,
    SymbolType,
)


class TestConfig:
    """Test configuration model."""
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config(repo_path=Path("/test"))
        
        assert config.repo_path == Path("/test")
        assert config.storage_path == Path(".memobase")
        assert config.max_file_size_mb == 10
        assert config.parallel_workers == 4
        assert config.index_batch_size == 1000
        assert config.graph_max_depth == 5
        assert config.cache_size_mb == 100
        assert config.storage_backend == "file"
        assert config.verbosity == 1
    
    def test_config_custom_values(self):
        """Test custom configuration values."""
        config = Config(
            repo_path=Path("/custom"),
            storage_path=Path("custom_storage"),
            max_file_size_mb=50,
            parallel_workers=8,
        )
        
        assert config.repo_path == Path("/custom")
        assert config.storage_path == Path("custom_storage")
        assert config.max_file_size_mb == 50
        assert config.parallel_workers == 8


class TestSymbolInfo:
    """Test symbol information model."""
    
    def test_symbol_info_creation(self):
        """Test creating symbol info."""
        symbol = SymbolInfo(
            name="test_function",
            symbol_type=SymbolType.FUNCTION,
            line_start=10,
            line_end=20,
            documentation="Test documentation",
            signature="def test_function()",
            parameters=["arg1", "arg2"],
            return_type="int",
        )
        
        assert symbol.name == "test_function"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.line_start == 10
        assert symbol.line_end == 20
        assert symbol.documentation == "Test documentation"


class TestMemoryUnit:
    """Test memory unit model."""
    
    def test_memory_unit_creation(self, sample_config):
        """Test creating memory unit."""
        unit = MemoryUnit(
            file_path=Path("/test.py"),
            keywords=["test", "function"],
            symbol=None,
            config=sample_config,
        )
        
        assert unit.file_path == Path("/test.py")
        assert "test" in unit.keywords
        assert unit.id is not None
        assert unit.version == "1.0"


class TestParsedFile:
    """Test parsed file model."""
    
    def test_parsed_file_creation(self):
        """Test creating parsed file."""
        parsed = ParsedFile(
            file_path=Path("/test.py"),
            language="python",
            content="def test(): pass",
            symbols=[],
        )
        
        assert parsed.file_path == Path("/test.py")
        assert parsed.language == "python"
        assert parsed.content == "def test(): pass"


class TestQuery:
    """Test query model."""
    
    def test_query_creation(self):
        """Test creating query."""
        query = Query(
            id="test_query",
            text="find function",
            query_type=QueryType.SEARCH,
            filters={"file_type": "python"},
            limit=10,
            offset=0,
        )
        
        assert query.id == "test_query"
        assert query.text == "find function"
        assert query.query_type == QueryType.SEARCH
        assert query.filters == {"file_type": "python"}
        assert query.limit == 10


class TestResponse:
    """Test response model."""
    
    def test_response_creation(self):
        """Test creating response."""
        response = Response(
            query_id="test_query",
            results=[],
            total_count=0,
            execution_time_ms=100.0,
            metadata={"test": "data"},
        )
        
        assert response.query_id == "test_query"
        assert response.total_count == 0
        assert response.execution_time_ms == 100.0


class TestIndex:
    """Test index model."""
    
    def test_index_creation(self):
        """Test creating index."""
        index = Index(
            id="test_index",
            term_index={},
            symbol_index={},
            file_index={},
        )
        
        assert index.id == "test_index"
        assert index.term_index == {}
        assert index.symbol_index == {}
        assert index.file_index == {}


class TestEnums:
    """Test enumeration types."""
    
    def test_symbol_type_values(self):
        """Test symbol type enum values."""
        assert SymbolType.FUNCTION.value == "function"
        assert SymbolType.CLASS.value == "class"
        assert SymbolType.METHOD.value == "method"
    
    def test_query_type_values(self):
        """Test query type enum values."""
        assert QueryType.SEARCH.value == "search"
        assert QueryType.FIND.value == "find"
        assert QueryType.ANALYZE.value == "analyze"
    
    def test_relation_type_values(self):
        """Test relation type enum values."""
        assert RelationType.CALLS.value == "calls"
        assert RelationType.IMPORTS.value == "imports"
        assert RelationType.INHERITS.value == "inherits"
