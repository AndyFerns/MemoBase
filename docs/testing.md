# Testing Documentation

Test suite and benchmarks for MemoBase.

## Test Structure

```
tests/
├── conftest.py          # Pytest configuration
├── unit/                # Unit tests
│   ├── test_core_models.py
│   ├── test_parser.py
│   ├── test_memory.py
│   ├── test_storage.py
│   ├── test_index.py
│   └── test_graph.py
├── integration/         # Integration tests
│   └── test_pipeline.py
└── performance/         # Performance tests
    └── test_performance.py
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Performance tests
pytest tests/performance/
```

### Run with Coverage

```bash
pytest --cov=memobase --cov-report=html
```

### Run with Profiling

```bash
pytest --profile
```

## Unit Tests

### Test Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| core | 95% |
| parser | 90% |
| memory | 90% |
| storage | 90% |
| index | 85% |
| graph | 85% |
| query | 85% |
| analysis | 80% |
| incremental | 85% |
| cli | 75% |
| tui | 70% |

### Writing Unit Tests

```python
# tests/unit/test_parser.py
import pytest
from memobase.parser.python import PythonParser

class TestPythonParser:
    def test_parse_file(self, sample_python_file):
        parser = PythonParser()
        result = parser.parse(sample_python_file)
        
        assert result is not None
        assert result.language == "python"
```

### Test Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_python_file(tmp_path):
    file_path = tmp_path / "test.py"
    file_path.write_text("def hello(): pass")
    return file_path

@pytest.fixture
def sample_config(tmp_path):
    return Config(repo_path=tmp_path)
```

## Integration Tests

### Full Pipeline Test

```python
# tests/integration/test_pipeline.py
def test_full_pipeline(sample_config, sample_python_file):
    # 1. Scan
    scanner = FilesystemScanner(sample_config)
    files = list(scanner.scan(sample_config.repo_path))
    
    # 2. Parse
    parser = ParserFactory().get_parser_by_extension(".py")
    parsed = [parser.parse(f) for f in files]
    
    # 3. Build memory
    builder = MemoryBuilder(TextEmbedder())
    units = builder.build_batch(parsed)
    
    # 4. Build index
    indexer = IndexBuilder(TextEmbedder())
    index = indexer.index(units)
    
    # 5. Build graph
    graph_builder = GraphBuilder()
    graph = graph_builder.build_graph(units, [])
    
    # Assertions
    assert len(units) > 0
    assert index is not None
    assert graph is not None
```

### End-to-End Tests

```python
def test_end_to_end_query(sample_config):
    # Build
    builder = ProjectBuilder(sample_config)
    builder.build_repo()
    
    # Query
    query_engine = QueryEngine(sample_config)
    response = query_engine.ask_question("find function")
    
    # Verify
    assert response.total_count > 0
```

## Performance Tests

### Benchmarks

```python
# tests/performance/test_performance.py
class TestPerformanceMetrics:
    def test_build_small_repo(self, temp_dir):
        # Setup
        for i in range(10):
            (temp_dir / f"file_{i}.py").write_text("# test")
        
        # Time the build
        timer = Timer()
        with timer.measure():
            # ... build repo ...
            pass
        
        result = timer.get_results()[0]
        assert result.elapsed_seconds < 1.0
```

### Dataset Sizes

| Dataset | Files | LOC | Purpose |
|---------|-------|-----|---------|
| small | 10 | 1K | Fast tests |
| medium | 100 | 50K | Standard tests |
| large | 1000 | 100K | Stress tests |
| huge | 10000 | 1M | Performance tests |

### Performance Targets

```python
# tests/performance/test_targets.py
PERFORMANCE_TARGETS = {
    "small_build_time": 1.0,      # seconds
    "medium_build_time": 5.0,
    "large_build_time": 30.0,
    "small_query_latency": 0.1,   # seconds
    "medium_query_latency": 0.3,
    "large_query_latency": 1.0,
}
```

## Regression Tests

### Consistency Tests

```python
def test_consistent_hashing(temp_dir):
    hasher = FileHasher()
    
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    
    # Same file should always produce same hash
    hashes = [hasher.hash_file(test_file) for _ in range(10)]
    assert len(set(hashes)) == 1
```

### Output Stability

```python
def test_query_output_stability(sample_config):
    # Run same query multiple times
    engine = QueryEngine(sample_config)
    
    results = []
    for _ in range(5):
        response = engine.ask_question("test query")
        results.append(response.results)
    
    # Results should be identical
    for i in range(len(results) - 1):
        assert results[i] == results[i + 1]
```

## Stress Tests

### High Load Tests

```python
@pytest.mark.slow
def test_many_files(temp_dir):
    # Create 10,000 files
    for i in range(10000):
        (temp_dir / f"file_{i}.py").write_text(f"# {i}")
    
    config = Config(repo_path=temp_dir)
    scanner = FilesystemScanner(config)
    
    # Should handle without crashing
    files = list(scanner.scan(temp_dir))
    assert len(files) == 10000
```

### Memory Tests

```python
def test_memory_leak(sample_config):
    import tracemalloc
    
    tracemalloc.start()
    
    # Run operation multiple times
    for _ in range(100):
        # ... run operation ...
        pass
    
    current, peak = tracemalloc.get_traced_memory()
    
    # Memory should not grow unbounded
    assert current < 100 * 1024 * 1024  # 100 MB
```

## Test Fixtures

### Sample Data

```python
# tests/fixtures/
FIXTURES = {
    "python_file": """
def hello():
    return "world"
""",
    "javascript_file": """
function greet() {
    return "hello";
}
""",
}
```

### Mock Objects

```python
class MockParser:
    def parse(self, file_path):
        return ParsedFile(
            file_path=file_path,
            language="python",
            content="",
            symbols=[],
        )
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -e ".[dev]"
      - run: pytest --cov=memobase
      - run: pytest tests/performance/ -m slow
```

## Test Markers

### pytest Markers

```python
@pytest.mark.unit
def test_simple():
    pass

@pytest.mark.integration
def test_pipeline():
    pass

@pytest.mark.slow
def test_performance():
    pass

@pytest.mark.stress
def test_high_load():
    pass
```

### Running Marked Tests

```bash
pytest -m unit
pytest -m "not slow"
pytest -m integration
```

## Debugging Tests

### Verbose Output

```bash
pytest -v
pytest -vv
pytest -vvv
```

### Stop on First Failure

```bash
pytest -x
```

### PDB on Failure

```bash
pytest --pdb
```

### Log Output

```bash
pytest --log-cli-level=DEBUG
```

## Coverage Goals

### Overall Coverage

- Minimum: 80%
- Target: 90%
- Ideal: 95%

### Critical Path Coverage

- Parser: 95%
- Memory Builder: 95%
- Index: 90%
- Graph: 90%

### Excluded from Coverage

- TUI rendering code
- Debug utilities
- Experimental features
