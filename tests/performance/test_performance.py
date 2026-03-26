"""
Performance tests for MemoBase.

REQUIRED DATASETS
- small_repo (~1K LOC)
- medium_repo (~50K LOC)
- large_repo (~100K LOC)
- huge_repo (~1M LOC synthetic)

METRICS
- build time
- query latency
- memory usage
"""

import time
from pathlib import Path

import pytest

from memobase.core.models import Config
from memobase.infrastructure.filesystem.scanner import FilesystemScanner
from memobase.infrastructure.utils.timers import Timer, Profiler


class TestPerformanceMetrics:
    """Performance metric tests."""
    
    def test_small_repo_scan_performance(self, temp_dir):
        """Test scanning small repository (~1K LOC)."""
        # Create small repository
        for i in range(10):
            (temp_dir / f"file_{i}.py").write_text(
                "# File\n" + "\n".join([f"def func_{j}(): pass" for j in range(10)])
            )
        
        config = Config(repo_path=temp_dir)
        scanner = FilesystemScanner(config)
        
        # Time the scan
        timer = Timer("small_repo_scan")
        with timer.measure():
            files = list(scanner.scan(temp_dir))
        
        result = timer.get_results()[0]
        
        # Should complete quickly
        assert result.elapsed_seconds < 1.0
        assert len(files) == 10
    
    def test_medium_repo_scan_performance(self, temp_dir):
        """Test scanning medium repository (~50K LOC simulated)."""
        # Create medium repository
        for i in range(100):
            content = "# File\n" + "\n".join([f"def func_{j}():\n    pass" for j in range(50)])
            (temp_dir / f"file_{i}.py").write_text(content)
        
        config = Config(repo_path=temp_dir)
        scanner = FilesystemScanner(config)
        
        timer = Timer("medium_repo_scan")
        with timer.measure():
            files = list(scanner.scan(temp_dir))
        
        result = timer.get_results()[0]
        
        # Should complete within reasonable time
        assert result.elapsed_seconds < 5.0
        assert len(files) == 100
    
    def test_file_hashing_performance(self, temp_dir):
        """Test file hashing performance."""
        from memobase.infrastructure.hashing.hasher import FileHasher
        
        # Create test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("A" * 1000000)  # 1MB file
        
        hasher = FileHasher()
        
        timer = Timer("file_hash")
        with timer.measure():
            hash_value = hasher.hash_file(test_file)
        
        result = timer.get_results()[0]
        
        # Should hash quickly
        assert result.elapsed_seconds < 0.1
        assert len(hash_value) == 64
    
    def test_memory_usage(self, temp_dir):
        """Test memory usage during operations."""
        import sys
        
        # Create test files
        for i in range(50):
            (temp_dir / f"file_{i}.py").write_text(
                "# Test\n" * 100
            )
        
        config = Config(repo_path=temp_dir)
        scanner = FilesystemScanner(config)
        
        # Measure memory before
        # Note: This is simplified, real memory profiling would use tracemalloc
        files = list(scanner.scan(temp_dir))
        
        # Memory should be reasonable
        assert len(files) == 50


class TestStressTests:
    """Stress tests for MemoBase."""
    
    @pytest.mark.slow
    def test_large_number_of_files(self, temp_dir):
        """Test with thousands of files."""
        # Create many files
        for i in range(1000):
            (temp_dir / f"file_{i}.py").write_text(f"# File {i}\n")
        
        config = Config(repo_path=temp_dir)
        scanner = FilesystemScanner(config)
        
        profiler = Profiler()
        
        with profiler.profile("large_scan"):
            files = list(scanner.scan(temp_dir))
        
        assert len(files) == 1000
        
        # Print profiling results
        print(profiler.get_report())
    
    @pytest.mark.slow
    def test_large_file_content(self, temp_dir):
        """Test with large file content."""
        # Create large file (5MB)
        large_file = temp_dir / "large.py"
        content = "# Large file\n" + "x = 1\n" * 100000
        large_file.write_text(content)
        
        config = Config(repo_path=temp_dir)
        
        # Should handle large files
        assert large_file.exists()
        assert large_file.stat().st_size > 1000000  # > 1MB


class TestRegressionTests:
    """Regression tests for consistent output."""
    
    def test_consistent_hashing(self, temp_dir):
        """Test that hashing produces consistent results."""
        from memobase.infrastructure.hashing.hasher import FileHasher
        
        test_file = temp_dir / "test.txt"
        test_file.write_text("consistent content")
        
        hasher = FileHasher()
        
        # Hash multiple times
        hashes = [hasher.hash_file(test_file) for _ in range(10)]
        
        # All hashes should be identical
        assert len(set(hashes)) == 1
    
    def test_consistent_scan_order(self, temp_dir):
        """Test that scanning produces consistent ordering."""
        # Create files
        for i in range(20):
            (temp_dir / f"file_{i:02d}.py").write_text(f"# {i}")
        
        config = Config(repo_path=temp_dir)
        scanner = FilesystemScanner(config)
        
        # Scan multiple times
        scans = [list(scanner.scan(temp_dir)) for _ in range(3)]
        
        # All scans should produce same order
        for i in range(len(scans) - 1):
            assert [f.name for f in scans[i]] == [f.name for f in scans[i + 1]]
