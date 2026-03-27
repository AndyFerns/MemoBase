# MemoBase — Memory for Your Codebase

```plaintext
▄▄▄      ▄▄▄                      ▄▄▄▄▄▄▄
████▄  ▄████                      ███▀▀███▄
███▀████▀███ ▄█▀█▄ ███▄███▄ ▄███▄ ███▄▄███▀  ▀▀█▄ ▄█▀▀▀ ▄█▀█▄
███  ▀▀  ███ ██▄█▀ ██ ██ ██ ██ ██ ███  ███▄ ▄█▀██ ▀███▄ ██▄█▀
███      ███ ▀█▄▄▄ ██ ██ ██ ▀███▀ ████████▀ ▀█▄██ ▄▄▄█▀ ▀█▄▄▄
```
MemoBase — Memory for your codebase

## Overview

MemoBase is a production-grade, offline-first codebase memory system that provides intelligent code analysis, search, and visualization capabilities. Built with performance and modularity in mind.

## Features

- **Streaming Processing**: No full repository loading
- **Parallel Parsing**: Multi-core file processing
- **Intelligent Indexing**: Fast semantic search
- **Graph Visualization**: Code relationship mapping
- **CLI & TUI**: Flexible interface options
- **Incremental Updates**: Efficient change detection
- **Offline-First**: No external dependencies

## Installation

```bash
pip install memobase
```

## Quick Start

```bash
# Initialize in your project
memobase init

# Build the memory index
memobase build

# Search your codebase
memobase ask "How does authentication work?"

# Launch TUI
memobase tui
```

## Architecture

MemoBase follows a strict modular architecture:

```
BUILD PIPELINE:
Filesystem Scanner → Parser → Memory Builder → Storage → Index → Graph

QUERY PIPELINE:
Input → Intent Classifier → Retriever (Index + Graph) → Formatter → Output

TUI LOOP:
Input → State Manager → Renderer (partial updates only)
```

## Modules

- **parser/**: Tree-sitter based code parsing
- **memory/**: Memory unit construction
- **storage/**: Persistent data storage
- **index/**: Search indexing
- **graph/**: Relationship graph building
- **query/**: Query processing and retrieval
- **analysis/**: Code analysis tools
- **incremental/**: Change detection and updates
- **cli/**: Command-line interface
- **tui/**: Terminal user interface
- **infrastructure/**: Core utilities
- **tests/**: Comprehensive test suite
- **docs/**: Documentation

## Performance

- <2s query latency on large codebases
- Streaming processing with constant memory usage
- Parallel parsing with ProcessPoolExecutor
- Lazy loading throughout the system

## Documentation

See the `docs/` directory for detailed documentation:

- [Architecture](docs/architecture.md)
- [Interfaces](docs/interfaces.md)
- [Data Models](docs/data_models.md)
- [Query Language](docs/query_language.md)
- [CLI Usage](docs/cli_usage.md)
- [TUI Usage](docs/tui_usage.md)
- [Performance](docs/performance.md)
- [Testing](docs/testing.md)

## License

MIT License - see LICENSE file for details.
