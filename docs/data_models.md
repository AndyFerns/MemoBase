# Data Models Documentation

JSON schemas and data structures for MemoBase.

## Core Models

### Config

Configuration object for MemoBase.

```json
{
  "version": "1.0",
  "repo_path": "/path/to/repo",
  "storage_path": ".memobase",
  "max_file_size_mb": 10,
  "parallel_workers": 4,
  "index_batch_size": 1000,
  "graph_max_depth": 5,
  "cache_size_mb": 100,
  "storage_backend": "file",
  "verbosity": 1,
  "included_extensions": [".py", ".js"],
  "excluded_patterns": ["*.pyc", "__pycache__"]
}
```

**Fields:**
- `repo_path`: Repository root path
- `storage_path`: Storage directory path
- `max_file_size_mb`: Maximum file size to process
- `parallel_workers`: Number of parallel workers
- `index_batch_size`: Batch size for indexing
- `graph_max_depth`: Maximum graph traversal depth
- `cache_size_mb`: Cache size in MB
- `storage_backend`: Storage backend type
- `verbosity`: Verbosity level (0-3)
- `included_extensions`: File extensions to include
- `excluded_patterns`: Patterns to exclude

### ParsedFile

Result of parsing a source file.

```json
{
  "version": "1.0",
  "id": "sha256_hash",
  "file_path": "/path/to/file.py",
  "language": "python",
  "content": "file content string",
  "symbols": [...],
  "ast": {...},
  "metadata": {
    "file_size": 1024,
    "line_count": 50,
    "hash": "sha256"
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### SymbolInfo

Information about a code symbol.

```json
{
  "name": "function_name",
  "symbol_type": "function",
  "line_start": 10,
  "line_end": 25,
  "column_start": 0,
  "column_end": 80,
  "documentation": "docstring content",
  "signature": "def function_name(arg: int) -> str",
  "parameters": ["arg1", "arg2"],
  "return_type": "str",
  "decorators": ["@decorator"],
  "modifiers": [],
  "scope": "global"
}
```

**Symbol Types:**
- `function`: Function definition
- `method`: Method within a class
- `class`: Class definition
- `variable`: Variable declaration
- `constant`: Constant value
- `import`: Import statement
- `export`: Export statement
- `interface`: Interface definition
- `type`: Type alias
- `enum`: Enumeration
- `namespace`: Namespace/module
- `unknown`: Unknown symbol type

### MemoryUnit

Core memory unit representing code knowledge.

```json
{
  "version": "1.0",
  "id": "unique_id",
  "file_path": "/path/to/file.py",
  "content": "code content",
  "keywords": ["keyword1", "keyword2"],
  "symbol": {...},
  "embeddings": [0.1, 0.2, 0.3],
  "relationships": [...],
  "metadata": {
    "language": "python",
    "file_type": "python",
    "parser_version": "1.0"
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Relationship

Relationship between memory units.

```json
{
  "id": "relationship_id",
  "source_id": "source_memory_unit_id",
  "target_id": "target_memory_unit_id",
  "relation_type": "calls",
  "weight": 0.8,
  "metadata": {},
  "created_at": "2024-01-01T00:00:00"
}
```

**Relation Types:**
- `calls`: Function/method call
- `imports`: Import dependency
- `inherits`: Inheritance relationship
- `contains`: Containment (class contains method)
- `references`: General reference
- `uses`: Usage relationship
- `implements`: Interface implementation
- `extends`: Class extension

### Index

Search index for memory units.

```json
{
  "version": "1.0",
  "id": "index_id",
  "term_index": {
    "keyword": ["unit_id1", "unit_id2"]
  },
  "symbol_index": {
    "symbol_name": ["unit_id1"]
  },
  "file_index": {
    "/path/to/file": ["unit_id1"]
  },
  "metadata": {},
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Graph

Relationship graph.

```json
{
  "version": "1.0",
  "id": "graph_id",
  "nodes": {
    "unit_id": {...}
  },
  "edges": [...],
  "adjacency_list": {
    "unit_id": ["neighbor_id1", "neighbor_id2"]
  },
  "metadata": {
    "is_directed": true,
    "node_count": 100,
    "edge_count": 250
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Query

Query object for searching.

```json
{
  "id": "query_id",
  "text": "search query",
  "query_type": "search",
  "filters": {
    "file_type": "python",
    "symbol_type": "function"
  },
  "limit": 10,
  "offset": 0,
  "created_at": "2024-01-01T00:00:00"
}
```

**Query Types:**
- `search`: General search
- `find`: Exact match search
- `analyze`: Analysis query
- `graph`: Graph traversal query
- `help`: Help request

### Response

Query response.

```json
{
  "query_id": "query_id",
  "results": [...],
  "total_count": 100,
  "execution_time_ms": 150.5,
  "metadata": {
    "query_type": "search",
    "filters_applied": true
  }
}
```

### Findings

Code analysis findings.

```json
{
  "id": "finding_id",
  "analysis_type": "security",
  "file_path": "/path/to/file.py",
  "line_number": 42,
  "severity": "high",
  "message": "Description of issue",
  "suggestion": "How to fix",
  "code_snippet": "relevant code",
  "confidence": 0.85,
  "created_at": "2024-01-01T00:00:00"
}
```

**Severity Levels:**
- `critical`: Critical security issue
- `high`: Important issue
- `medium`: Moderate issue
- `low`: Minor issue
- `info`: Informational

**Analysis Types:**
- `security`: Security vulnerability
- `quality`: Code quality issue
- `performance`: Performance issue
- `maintainability`: Maintainability issue

## Enumerations

### SymbolType

- `function`: Function
- `method`: Method
- `class`: Class
- `variable`: Variable
- `constant`: Constant
- `import`: Import
- `export`: Export
- `interface`: Interface
- `type`: Type
- `enum`: Enum
- `namespace`: Namespace
- `module`: Module
- `unknown`: Unknown

### RelationType

- `calls`: Calls
- `imports`: Imports
- `inherits`: Inherits
- `contains`: Contains
- `references`: References
- `uses`: Uses
- `implements`: Implements
- `extends`: Extends

### QueryType

- `search`: Search
- `find`: Find
- `analyze`: Analyze
- `graph`: Graph
- `help`: Help

### AnalysisType

- `security`: Security
- `quality`: Quality
- `performance`: Performance
- `maintainability`: Maintainability

## Versioning

All models include a `version` field:

- **1.0.0**: Initial version
- Changes tracked via version field
- Migration support for schema evolution

## Validation

Models use Python dataclasses with type hints:
- Runtime validation via dacite
- JSON serialization via orjson
- Schema evolution support
