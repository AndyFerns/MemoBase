"""
Unit tests for index module.
"""

import pytest

from memobase.core.models import Index, MemoryUnit
from memobase.index.builder import IndexBuilder
from memobase.index.ranker import ResultRanker
from memobase.index.searcher import IndexSearcher


class TestIndexBuilder:
    """Test index builder."""
    
    def test_builder_creation(self):
        """Test builder initialization."""
        # Would need actual embedder instance
        # builder = IndexBuilder(embedder)
        # assert builder is not None
        pass
    
    def test_init_stop_words(self):
        """Test stop words initialization."""
        builder = IndexBuilder.__new__(IndexBuilder)
        stop_words = builder._init_stop_words()
        
        assert "the" in stop_words
        assert "and" in stop_words
        assert "or" in stop_words


class TestIndexSearcher:
    """Test index searcher."""
    
    def test_searcher_creation(self):
        """Test searcher initialization."""
        searcher = IndexSearcher()
        assert searcher is not None
    
    def test_process_term(self):
        """Test term processing."""
        searcher = IndexSearcher()
        
        processed = searcher._process_term("HelloWorld")
        assert processed == "helloworld"
        
        processed = searcher._process_term("test_function")
        assert processed == "test_function"


class TestResultRanker:
    """Test result ranker."""
    
    def test_ranker_creation(self):
        """Test ranker initialization."""
        ranker = ResultRanker()
        assert ranker is not None
    
    def test_calculate_symbol_type_score(self):
        """Test symbol type score calculation."""
        ranker = ResultRanker()
        
        # Class should get high score
        class_score = ranker._calculate_symbol_type_score("class")
        assert class_score > 0.8
        
        # Function should get good score
        func_score = ranker._calculate_symbol_type_score("function")
        assert func_score > 0.7
        
        # Unknown should get low score
        unknown_score = ranker._calculate_symbol_type_score("unknown")
        assert unknown_score < 0.5
