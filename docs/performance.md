# Performance Documentation

Scaling strategy and memory constraints for MemoBase.

## Performance Characteristics

### Streaming Processing

MemoBase processes files one at a time:
- No full repository loading
- Memory usage: O(1) relative to repo size
- Processing: O(n) where n = number of files

### Parallelism

ProcessPoolExecutor for CPU-bound tasks:
- Parsing: Parallel by file
- Memory building: Parallel batches
- Configurable worker count (default: 4)

### Caching

Multi-level caching strategy:
1. **File content cache** (LRU)
2. **Hash cache** (incremental updates)
3. **Index cache** (query acceleration)
4. **Graph cache** (traversal results)

## Scaling Metrics

### Small Repository (~1K LOC)

**Metrics:**
- Build time: < 1 second
- Memory usage: < 50 MB
- Query latency: < 100 ms
- File count: ~10-50

**Configuration:**
```json
{
  "parallel_workers": 2,
  "cache_size_mb": 50,
  "index_batch_size": 100
}
```

### Medium Repository (~50K LOC)

**Metrics:**
- Build time: 2-5 seconds
- Memory usage: 100-200 MB
- Query latency: 100-300 ms
- File count: ~500-1000

**Configuration:**
```json
{
  "parallel_workers": 4,
  "cache_size_mb": 100,
  "index_batch_size": 1000
}
```

### Large Repository (~100K LOC)

**Metrics:**
- Build time: 5-15 seconds
- Memory usage: 200-500 MB
- Query latency: 200-500 ms
- File count: ~2000-5000

**Configuration:**
```json
{
  "parallel_workers": 8,
  "cache_size_mb": 200,
  "index_batch_size": 2000,
  "graph_max_depth": 3
}
```

### Huge Repository (~1M LOC)

**Metrics:**
- Build time: 30-120 seconds
- Memory usage: 1-2 GB
- Query latency: 500-1000 ms
- File count: ~10,000+

**Configuration:**
```json
{
  "parallel_workers": 16,
  "cache_size_mb": 500,
  "index_batch_size": 5000,
  "graph_max_depth": 2
}
```

## Memory Constraints

### Peak Memory Usage

Peak memory occurs during:
1. **Parallel parsing** (worker processes)
2. **Index building** (inverted index)
3. **Graph building** (adjacency lists)

### Memory Optimization

**Strategies:**
- Streaming processing
- Batch operations
- Lazy loading
- LRU eviction
- Compression

### Memory Limits

| Repository Size | Recommended RAM |
|-----------------|-----------------|
| < 10K LOC | 2 GB |
| 10-50K LOC | 4 GB |
| 50-100K LOC | 8 GB |
| 100K-1M LOC | 16 GB |
| > 1M LOC | 32 GB |

## Build Performance

### Initial Build

Phases:
1. **Scan** (sequential): O(n)
2. **Parse** (parallel): O(n/p) where p = workers
3. **Memory build** (parallel): O(n/p)
4. **Index** (sequential): O(n log n)
5. **Graph** (sequential): O(n + e)

Total: O(n log n) with parallelism

### Incremental Update

Change detection: O(n) with SHA256 caching
Update: O(k) where k = changed files

### Benchmarks

```
Repository Size | Initial Build | Incremental
----------------|---------------|-------------
1K LOC          | 0.5s          | 0.1s
10K LOC         | 2s            | 0.3s
100K LOC        | 10s           | 1s
1M LOC          | 60s           | 5s
```

## Query Performance

### Search Query

**Complexity:**
- Term search: O(1) hash lookup
- Result ranking: O(k log k) where k = results
- Total: O(k log k)

### Graph Query

**Complexity:**
- BFS traversal: O(v + e) where v = vertices, e = edges
- Depth-limited: O(b^d) where b = branching, d = depth

### Query Caching

Cache hit: O(1)
Cache miss: Full query execution

### Latency Targets

| Query Type | Target Latency |
|------------|----------------|
| Simple search | < 100 ms |
| Complex search | < 500 ms |
| Graph traversal | < 1000 ms |
| Analysis | < 5000 ms |

## Storage Performance

### File Storage

**Write:**
- Sequential append: O(1) per record
- Batch writes: O(n) for n records

**Read:**
- Sequential scan: O(n)
- Indexed lookup: O(1)

### SQLite Storage

**Write:**
- Single insert: O(log n)
- Batch insert: O(n log n)
- WAL mode for concurrency

**Read:**
- Indexed query: O(log n)
- Full scan: O(n)

### Storage Size

| Repository | Index Size | Graph Size | Total |
|------------|------------|------------|-------|
| 10K LOC | 1 MB | 2 MB | 5 MB |
| 100K LOC | 10 MB | 20 MB | 50 MB |
| 1M LOC | 100 MB | 200 MB | 500 MB |

## TUI Performance

### Rendering

**Requirements:**
- 60 FPS for interactions
- Lazy loading for large lists
- Virtual scrolling for file tree
- Depth-limited graph rendering

### Async Operations

All core operations are async:
- File loading: Background
- Query execution: Background
- Analysis: Background

### Memory Usage

TUI memory: ~50 MB base
Additional: ~1 MB per 1000 visible items

## Optimization Guidelines

### For Small Repositories

- Reduce workers: 2
- Smaller cache: 50 MB
- Lower batch size: 100

### For Large Repositories

- Increase workers: 8-16
- Larger cache: 200-500 MB
- Higher batch size: 5000
- Reduce graph depth: 2-3
- Use compression

### For CI/CD

- Use `--quiet` mode
- Reduce verbosity: 0
- Disable TUI
- Use JSON output

## Profiling

### Enable Profiling

```bash
memobase build --profile
memobase ask "query" --profile
```

### Profiling Output

```
Profiling Report
========================================
scan_repo:
  Total: 2.34s
  Count: 1
  Average: 2.34s

parse_files:
  Total: 5.67s
  Count: 150
  Average: 37.8ms

build_index:
  Total: 1.23s
  Count: 1
  Average: 1.23s
```

### Memory Profiling

```python
import tracemalloc

tracemalloc.start()
# ... run operation ...
current, peak = tracemalloc.get_traced_memory()
print(f"Peak memory: {peak / 1024 / 1024:.1f} MB")
```

## Bottlenecks

### Common Bottlenecks

1. **Large files** (> 10 MB)
   - Skip or truncate
   - Config: `max_file_size_mb`

2. **Deep graphs** (> depth 5)
   - Limit traversal depth
   - Config: `graph_max_depth`

3. **Many relationships** (> 1000 per unit)
   - Prune weak relationships
   - Config: `relationship_threshold`

4. **Binary files**
   - Auto-detected and skipped
   - Config: `binary_extensions`

## Best Practices

### Repository Structure

- Organize code in directories
- Avoid single huge files
- Use .gitignore for generated files

### Configuration

- Tune for your repo size
- Monitor memory usage
- Adjust workers to CPU count

### Workflow

- Use incremental updates
- Cache aggressively
- Profile regularly
