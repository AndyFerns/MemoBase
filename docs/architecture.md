# Architecture Documentation

MemoBase follows a strict modular architecture with three main pipelines.

## System Pipelines

### Build Pipeline

```
Filesystem Scanner → Parser → Memory Builder → Storage → Index → Graph
```

**Filesystem Scanner**
- Respects `.gitignore` patterns
- Skips binary files
- Streams files (no full load)
- Filters by extension and size

**Parser** (Tree-sitter based)
- Supports Python, JavaScript/TypeScript
- Extracts symbols, AST nodes
- Generates metadata
- Handles errors gracefully

**Memory Builder**
- Constructs `MemoryUnit` objects
- Generates embeddings (TF-IDF)
- Extracts relationships
- Assigns keywords

**Storage**
- File-based (JSONL)
- SQLite backend
- Async operations
- Compression support

**Index Builder**
- Inverted index for terms
- Symbol index for names
- File index for paths
- Incremental updates

**Graph Builder**
- Nodes: MemoryUnits
- Edges: Relationships
- Adjacency lists
- Metadata storage

### Query Pipeline

```
Input → Intent Classifier → Retriever → Formatter → Output
```

**Intent Classifier**
- Rule-based patterns
- Keyword matching
- Query type detection: SEARCH, FIND, ANALYZE, GRAPH

**Retriever**
- Index search (term-based)
- Semantic search (embeddings)
- Graph traversal
- Result ranking

**Formatter**
- Text output
- JSON output
- Table output
- Markdown output

### TUI Loop

```
Input → State Manager → Renderer (partial updates only)
```

**State Manager**
- Single source of truth
- Immutable state updates
- Event-driven changes

**Renderer**
- Virtual scrolling
- Lazy loading
- Depth-limited graph
- Async operations

## Module Responsibilities

### Core (memobase/core/)
- **models.py**: Data models with JSON schemas
- **interfaces.py**: Module contracts
- **exceptions.py**: Error handling

### Parser (memobase/parser/)
- **base.py**: Base parser interface
- **python.py**: Python parser
- **javascript.py**: JavaScript parser
- **factory.py**: Parser selection

### Memory (memobase/memory/)
- **builder.py**: Memory unit construction
- **extractor.py**: Relationship extraction
- **embedder.py**: Text embeddings

### Storage (memobase/storage/)
- **file_storage.py**: JSONL backend
- **sqlite_storage.py**: SQLite backend
- **cache.py**: LRU caching

### Index (memobase/index/)
- **builder.py**: Index construction
- **searcher.py**: Search algorithms
- **ranker.py**: Result ranking

### Graph (memobase/graph/)
- **builder.py**: Graph construction
- **traversal.py**: BFS, DFS, Dijkstra, A*
- **analyzer.py**: Centrality, clustering

### Query (memobase/query/)
- **processor.py**: Query execution
- **classifier.py**: Intent detection
- **formatter.py**: Output formatting

### Analysis (memobase/analysis/)
- **code_analyzer.py**: Security, quality, performance
- **metrics.py**: Code metrics
- **pattern_detector.py**: Design patterns, code smells

### Incremental (memobase/incremental/)
- **change_detector.py**: SHA256 change detection
- **updater.py**: Incremental updates

### CLI (memobase/cli/)
- **main.py**: Typer app
- **commands.py**: Command implementations

### TUI (memobase/tui/)
- **app.py**: Textual app
- **state.py**: Global state
- **controller.py**: Core bridge
- **event_bus.py**: Event system
- **actions.py**: Keybindings
- **widgets/**: UI components
- **views/**: Mode views

### Infrastructure (memobase/infrastructure/)
- **filesystem/**: Scanner, ignore patterns
- **logging/**: Logger with verbosity
- **config/**: Configuration loader
- **concurrency/**: Executor wrapper
- **hashing/**: SHA256 hasher
- **utils/**: Path utilities, timers

## Performance Characteristics

### Streaming
- Files processed one at a time
- No full repository loading
- Memory usage: O(1) relative to repo size

### Parallelism
- Parser: ProcessPoolExecutor
- Memory Builder: Parallel batch processing
- Configurable worker count

### Caching
- File content cache (LRU)
- Hash cache for incremental
- Index cache for queries

### Lazy Loading
- File tree: Virtual scrolling
- Graph: Depth-limited traversal
- Search: Top-k retrieval

## Data Flow

1. **Initialization**
   - Load configuration
   - Initialize storage
   - Check for existing index

2. **Build Process**
   - Scan filesystem (streaming)
   - Parse files (parallel)
   - Build memory units
   - Create index
   - Build graph
   - Store results

3. **Query Process**
   - Classify intent
   - Search index
   - Traverse graph (if needed)
   - Rank results
   - Format output

4. **Incremental Update**
   - Calculate file hashes
   - Detect changes
   - Update modified units
   - Update index incrementally
   - Update graph incrementally

## Extension Points

### Adding Language Support
1. Create parser in `memobase/parser/`
2. Register in `ParserFactory`
3. Add tests

### Adding Storage Backend
1. Implement `StorageInterface`
2. Add configuration option
3. Add tests

### Adding Analysis Type
1. Add to `AnalysisType` enum
2. Implement in `CodeAnalyzer`
3. Update CLI commands

## Versioning

All data models include `version` field for:
- Migration handling
- Backward compatibility
- Schema evolution
