# Contributing Guide

How to contribute to MemoBase.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/memobase/memobase.git
cd memobase

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Development Workflow

### 1. Create Branch

```bash
git checkout -b feature/my-feature
# or
git checkout -b fix/my-bugfix
```

### 2. Make Changes

- Follow code style guidelines
- Add tests for new features
- Update documentation

### 3. Test Changes

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=memobase

# Run linting
flake8 memobase
mypy memobase
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Tests
- `refactor:` Code refactoring
- `perf:` Performance
- `chore:` Maintenance

### 5. Push and Create PR

```bash
git push origin feature/my-feature
```

Create pull request on GitHub.

## Code Style

### Python Style

Follow PEP 8 with these specifics:

```python
# Use type hints
def process_file(file_path: Path) -> ParsedFile:
    pass

# Docstrings with Google style
def parse_file(file_path: Path) -> ParsedFile:
    """Parse a source file.
    
    Args:
        file_path: Path to file to parse
        
    Returns:
        ParsedFile with AST and metadata
        
    Raises:
        ParseError: If parsing fails
    """
    pass

# Max line length: 100
# Use double quotes for strings
```

### Import Order

```python
# 1. Standard library
import os
from pathlib import Path

# 2. Third party
import typer
from textual.app import App

# 3. Local
from memobase.core.models import Config
from memobase.parser.factory import ParserFactory
```

## Testing

### Write Tests

```python
# tests/unit/test_feature.py
def test_new_feature():
    """Test description."""
    # Arrange
    input_data = ...
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result.expected_value
```

### Test Categories

- **Unit tests**: Fast, isolated
- **Integration tests**: Full pipeline
- **Performance tests**: Benchmarks

### Run Tests

```bash
# All tests
pytest

# Specific module
pytest tests/unit/test_parser.py

# With coverage
pytest --cov=memobase --cov-report=html
```

## Documentation

### Code Documentation

- All public functions need docstrings
- Complex algorithms need comments
- Update README for major changes

### Module README

Each module should have README.md:

```markdown
# Module Name

## Purpose
Brief description

## Inputs/Outputs
What it takes and produces

## Constraints
Limitations and requirements

## Extension Points
How to extend
```

## Architecture Changes

### Adding Features

1. Update interface (if needed)
2. Implement in module
3. Add to controller/facade
4. Update CLI/TUI
5. Add tests
6. Update docs

### Breaking Changes

- Update version (major)
- Document migration path
- Deprecation warnings

## Pull Request Process

### PR Requirements

- [ ] Tests pass
- [ ] Coverage maintained
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] No lint errors

### Review Checklist

- [ ] Code follows style guide
- [ ] Tests cover new code
- [ ] Documentation is clear
- [ ] No performance regressions
- [ ] Backward compatible (or documented)

## Release Process

### Versioning

Semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Release Steps

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Tag release
6. Build and publish

## Code Review

### Review Guidelines

- Be constructive
- Ask questions
- Suggest improvements
- Approve when ready

### Review Focus

1. Correctness
2. Performance
3. Maintainability
4. Testing
5. Documentation

## Questions?

- Open an issue for bugs
- Start a discussion for features
- Join our Discord for chat

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
