"""
Integration tests for MemoBase.

Test full pipeline: scan → parse → memory → index → graph → query
"""

import pytest

from memobase.core.models import Config, Query, QueryType
from memobase.infrastructure.filesystem.scanner import FilesystemScanner


class TestFullPipeline:
    """Test complete MemoBase pipeline."""
    
    def test_scan_repository(self, sample_config, sample_python_file, sample_js_file):
        """Test scanning repository."""
        scanner = FilesystemScanner(sample_config)
        
        files = list(scanner.scan(sample_config.repo_path))
        
        # Should find both sample files
        assert len(files) >= 2
    
    def test_config_loading(self, temp_dir):
        """Test configuration loading and saving."""
        from memobase.infrastructure.config.loader import ConfigLoader
        
        loader = ConfigLoader(temp_dir)
        config = loader.create_default_config()
        
        assert config.repo_path == temp_dir
        assert config.storage_backend == "file"
    
    def test_parser_factory(self, sample_python_file):
        """Test parser factory."""
        from memobase.parser.factory import ParserFactory
        
        factory = ParserFactory()
        parser = factory.get_parser_by_extension(".py")
        
        assert parser is not None
    
    def test_file_hashing(self, sample_python_file):
        """Test file hashing."""
        from memobase.infrastructure.hashing.hasher import FileHasher
        
        hasher = FileHasher()
        hash1 = hasher.hash_file(sample_python_file)
        hash2 = hasher.hash_file(sample_python_file)
        
        # Same file should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_build_and_query(self, sample_config, sample_python_file):
        """Test building memory and querying."""
        # This would test the full pipeline
        # 1. Scan files
        # 2. Parse files
        # 3. Build memory units
        # 4. Build index
        # 5. Build graph
        # 6. Query
        
        # Placeholder for full integration test
        pass
    
    def test_incremental_update(self, sample_config, sample_python_file):
        """Test incremental update."""
        # This would test:
        # 1. Initial build
        # 2. File change detection
        # 3. Incremental update
        
        # Placeholder for incremental test
        pass
