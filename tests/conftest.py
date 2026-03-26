"""
Test configuration and fixtures for MemoBase.
"""

import os
import tempfile
from pathlib import Path

import pytest

from memobase.core.models import Config


@pytest.fixture
def temp_dir():
    """Create temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config(temp_dir):
    """Create sample configuration."""
    return Config(
        repo_path=temp_dir,
        storage_path=temp_dir / ".memobase",
        max_file_size_mb=10,
        parallel_workers=2,
        index_batch_size=100,
        graph_max_depth=3,
        cache_size_mb=50,
        storage_backend="file",
        verbosity=2,
    )


@pytest.fixture
def sample_python_file(temp_dir):
    """Create sample Python file for testing."""
    file_path = temp_dir / "sample.py"
    content = '''
def hello_world():
    """Say hello."""
    return "Hello, World!"

class Calculator:
    """Simple calculator."""
    
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def subtract(self, a: int, b: int) -> int:
        return a - b
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_js_file(temp_dir):
    """Create sample JavaScript file for testing."""
    file_path = temp_dir / "sample.js"
    content = '''
function greet(name) {
    return `Hello, ${name}!`;
}

class User {
    constructor(name) {
        this.name = name;
    }
    
    sayHello() {
        console.log(greet(this.name));
    }
}

module.exports = { greet, User };
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def empty_config():
    """Create empty/minimal configuration."""
    return Config(repo_path=Path.cwd())


@pytest.fixture
def mock_storage(temp_dir):
    """Create mock storage directory."""
    storage_path = temp_dir / ".memobase"
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@pytest.fixture
def large_repo_fixture(temp_dir):
    """Create larger repository structure for testing."""
    # Create directory structure
    (temp_dir / "src" / "utils").mkdir(parents=True)
    (temp_dir / "src" / "models").mkdir(parents=True)
    (temp_dir / "tests").mkdir(parents=True)
    (temp_dir / "docs").mkdir(parents=True)
    
    # Create files
    files = [
        temp_dir / "src" / "main.py",
        temp_dir / "src" / "utils" / "helpers.py",
        temp_dir / "src" / "models" / "user.py",
        temp_dir / "tests" / "test_main.py",
        temp_dir / "README.md",
    ]
    
    for file_path in files:
        file_path.write_text(f"# {file_path.name}\n")
    
    return temp_dir
