"""
Unit tests for memory module.
"""

import pytest

from memobase.core.models import Config, ParsedFile, SymbolInfo, SymbolType
from memobase.memory.builder import MemoryBuilder
from memobase.memory.embedder import TextEmbedder, TFIDFEmbedder
from memobase.memory.extractor import RelationshipExtractor


class TestTextEmbedder:
    """Test text embedder."""
    
    def test_embedder_creation(self):
        """Test embedder initialization."""
        embedder = TextEmbedder()
        assert embedder is not None
    
    def test_hash_text(self):
        """Test text hashing."""
        embedder = TextEmbedder()
        hash1 = embedder._hash_text("test text")
        hash2 = embedder._hash_text("test text")
        
        assert hash1 == hash2
        assert isinstance(hash1, str)
    
    def test_different_texts_different_hashes(self):
        """Test that different texts produce different hashes."""
        embedder = TextEmbedder()
        hash1 = embedder._hash_text("text one")
        hash2 = embedder._hash_text("text two")
        
        assert hash1 != hash2


class TestTFIDFEmbedder:
    """Test TF-IDF embedder."""
    
    def test_tfidf_creation(self):
        """Test TF-IDF embedder initialization."""
        embedder = TFIDFEmbedder()
        assert embedder is not None
    
    def test_tokenize(self):
        """Test tokenization."""
        embedder = TFIDFEmbedder()
        tokens = embedder._tokenize("Hello world test")
        
        assert "hello" in tokens
        assert "world" in tokens
        assert "test" in tokens


class TestRelationshipExtractor:
    """Test relationship extractor."""
    
    def test_extractor_creation(self, sample_config):
        """Test extractor initialization."""
        extractor = RelationshipExtractor(sample_config)
        assert extractor is not None


class TestMemoryBuilder:
    """Test memory builder."""
    
    def test_builder_creation(self, sample_config):
        """Test builder initialization."""
        embedder = TextEmbedder()
        builder = MemoryBuilder(embedder)
        assert builder is not None
    
    def test_extract_keywords_from_symbol(self):
        """Test keyword extraction from symbol."""
        symbol = SymbolInfo(
            name="calculate_sum",
            symbol_type=SymbolType.FUNCTION,
            line_start=1,
            line_end=10,
        )
        
        keywords = MemoryBuilder.extract_keywords_from_symbol(symbol)
        
        assert "calculate" in keywords
        assert "sum" in keywords
    
    def test_extract_keywords_from_content(self):
        """Test keyword extraction from content."""
        content = "def process_data(items):\n    return [item for item in items]"
        
        keywords = MemoryBuilder.extract_keywords_from_content(content)
        
        assert "process" in keywords
        assert "data" in keywords
        assert "items" in keywords
