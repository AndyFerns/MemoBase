# MemoBase Documentation

## Overview

MemoBase is a codebase memory system that provides deep semantic understanding of your code through incremental indexing, relationship graphing, and intelligent querying.

## Table of Contents

- [Architecture](architecture.md) - System design and pipelines
- [Data Models](data_models.md) - JSON schemas and structures
- [Interfaces](interfaces.md) - Module contracts
- [CLI Usage](cli_usage.md) - Command-line interface
- [TUI Usage](tui_usage.md) - Terminal user interface
- [Performance](performance.md) - Scaling and optimization
- [Testing](testing.md) - Test suite and benchmarks
- [Contributing](contributing.md) - How to contribute

## Quick Start

### Installation

```bash
pip install memobase
```

### Initialize Repository

```bash
memobase init /path/to/repo
```

### Build Index

```bash
memobase build
```

### Ask Questions

```bash
memobase ask "How does authentication work?"
```

### Launch TUI

```bash
memobase tui
```

## System Overview

MemoBase follows a pipeline architecture:

```
Filesystem → Parser → Memory Builder → Storage → Index → Graph
                                              ↓
                                           Query Processor
```

### Key Features

- **Streaming Processing**: No full repository loading
- **Parallel Parsing**: ProcessPoolExecutor for speed
- **Incremental Updates**: SHA256-based change detection
- **Semantic Search**: TF-IDF embeddings with semantic features
- **Relationship Graphing**: Navigate code dependencies
- **Code Analysis**: Security, quality, and pattern detection

## Architecture Highlights

### TUI Module (Textual)
- Thin layer: state rendering, event dispatch, async calls to core
- ASCII splash screen on boot
- Multiple views: Memory, Graph, Analysis, Query
- Event-driven architecture with EventBus

### Infrastructure Module
- Filesystem scanner with .gitignore support
- SHA256 hasher for incremental updates
- ProcessPoolExecutor wrapper
- Configuration loader with schema validation

### Testing
- Unit tests for all modules
- Integration tests for full pipeline
- Performance tests with multiple dataset sizes
- Regression tests for consistent output

## Contributing

See [Contributing Guide](contributing.md) for details.

## License

MIT License
