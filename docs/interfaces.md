# Interfaces Documentation

Exact function contracts for all MemoBase modules.

## Core Interfaces

### ParserInterface

```python
class ParserInterface:
    def parse(self, file_path: Path) -> ParsedFile:
        """Parse a single file.
        
        Args:
            file_path: Path to file to parse
            
        Returns:
            ParsedFile with AST and metadata
            
        Raises:
            ParseError: If parsing fails
        """
        pass
    
    def parse_batch(self, file_paths: List[Path]) -> List[ParsedFile]:
        """Parse multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of ParsedFile objects
        """
        pass
    
    def parse_async(self, file_path: Path) -> asyncio.Future[ParsedFile]:
        """Parse file asynchronously.
        
        Args:
            file_path: Path to file
            
        Returns:
            Future resolving to ParsedFile
        """
        pass
```

### MemoryBuilderInterface

```python
class MemoryBuilderInterface:
    def build(self, parsed_file: ParsedFile) -> List[MemoryUnit]:
        """Build memory units from parsed file.
        
        Args:
            parsed_file: Parsed file data
            
        Returns:
            List of MemoryUnit objects
        """
        pass
    
    def build_batch(self, parsed_files: List[ParsedFile]) -> List[MemoryUnit]:
        """Build memory units from multiple files.
        
        Args:
            parsed_files: List of parsed files
            
        Returns:
            List of MemoryUnit objects
        """
        pass
    
    def build_async(self, parsed_file: ParsedFile) -> asyncio.Future[List[MemoryUnit]]:
        """Build memory units asynchronously.
        
        Args:
            parsed_file: Parsed file data
            
        Returns:
            Future resolving to list of MemoryUnits
        """
        pass
    
    def extract_relationships(self, memory_units: List[MemoryUnit]) -> List[Relationship]:
        """Extract relationships between memory units.
        
        Args:
            memory_units: List of memory units
            
        Returns:
            List of Relationship objects
        """
        pass
```

### StorageInterface

```python
class StorageInterface:
    def store(self, data: Any, key: str) -> None:
        """Store data with key.
        
        Args:
            data: Data to store
            key: Storage key
        """
        pass
    
    def load(self, key: str) -> Any:
        """Load data by key.
        
        Args:
            key: Storage key
            
        Returns:
            Stored data or None
        """
        pass
    
    def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Storage key
            
        Returns:
            True if key exists
        """
        pass
    
    def delete(self, key: str) -> None:
        """Delete data by key.
        
        Args:
            key: Storage key
        """
        pass
    
    def list_keys(self, prefix: str = "") -> List[str]:
        """List keys with optional prefix.
        
        Args:
            prefix: Key prefix filter
            
        Returns:
            List of keys
        """
        pass
```

### IndexInterface

```python
class IndexInterface:
    def index(self, memory_units: List[MemoryUnit]) -> Index:
        """Create index from memory units.
        
        Args:
            memory_units: List of memory units
            
        Returns:
            Index object
        """
        pass
    
    def update_index(self, index: Index, memory_units: List[MemoryUnit]) -> Index:
        """Update existing index.
        
        Args:
            index: Existing index
            memory_units: New memory units
            
        Returns:
            Updated index
        """
        pass
    
    def search(self, index: Index, query: str, limit: int = 10) -> List[str]:
        """Search index for matching unit IDs.
        
        Args:
            index: Index to search
            query: Search query
            limit: Maximum results
            
        Returns:
            List of MemoryUnit IDs
        """
        pass
    
    def get_term_frequency(self, index: Index, term: str) -> Dict[str, int]:
        """Get term frequency across documents.
        
        Args:
            index: Index to query
            term: Term to check
            
        Returns:
            Dictionary mapping unit_id to frequency
        """
        pass
```

### GraphInterface

```python
class GraphInterface:
    def build_graph(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Build relationship graph.
        
        Args:
            memory_units: List of memory units
            relationships: List of relationships
            
        Returns:
            Graph object
        """
        pass
    
    def update_graph(self, graph: Graph, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Update existing graph.
        
        Args:
            graph: Existing graph
            memory_units: New memory units
            relationships: New relationships
            
        Returns:
            Updated graph
        """
        pass
    
    def find_path(self, graph: Graph, source_id: str, target_id: str, max_depth: int = 5) -> List[str]:
        """Find shortest path between two nodes.
        
        Args:
            graph: Graph to search
            source_id: Starting node ID
            target_id: Target node ID
            max_depth: Maximum traversal depth
            
        Returns:
            List of node IDs forming path
        """
        pass
    
    def get_neighbors(self, graph: Graph, node_id: str, relation_type: str = None, max_depth: int = 1) -> Set[str]:
        """Get neighboring nodes.
        
        Args:
            graph: Graph to search
            node_id: Center node ID
            relation_type: Optional relation filter
            max_depth: Traversal depth
            
        Returns:
            Set of neighbor node IDs
        """
        pass
    
    def calculate_centrality(self, graph: Graph, node_id: str) -> float:
        """Calculate centrality score for node.
        
        Args:
            graph: Graph to analyze
            node_id: Node to analyze
            
        Returns:
            Centrality score (0-1)
        """
        pass
```

### QueryInterface

```python
class QueryInterface:
    def query(self, query: Query, index: Index, graph: Graph) -> Response:
        """Execute query against index and graph.
        
        Args:
            query: Query object
            index: Search index
            graph: Relationship graph
            
        Returns:
            Query response
        """
        pass
    
    def classify_intent(self, query_text: str) -> str:
        """Classify query intent.
        
        Args:
            query_text: Raw query text
            
        Returns:
            Intent type (search, find, analyze, graph)
        """
        pass
    
    def extract_filters(self, query_text: str) -> Dict[str, Any]:
        """Extract filters from query.
        
        Args:
            query_text: Raw query text
            
        Returns:
            Dictionary of filters
        """
        pass
    
    def rank_results(self, results: List[MemoryUnit], query: Query) -> List[MemoryUnit]:
        """Rank results by relevance.
        
        Args:
            results: Search results
            query: Original query
            
        Returns:
            Ranked results
        """
        pass
```

### AnalysisInterface

```python
class AnalysisInterface:
    def analyze(self, memory_units: List[MemoryUnit]) -> List[Findings]:
        """Analyze memory units.
        
        Args:
            memory_units: List of memory units
            
        Returns:
            List of findings
        """
        pass
    
    def detect_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect code patterns.
        
        Args:
            memory_units: List of memory units
            
        Returns:
            Dictionary mapping pattern to units
        """
        pass
    
    def calculate_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate code metrics.
        
        Args:
            memory_units: List of memory units
            
        Returns:
            Dictionary of metrics
        """
        pass
```

### IncrementalInterface

```python
class IncrementalInterface:
    def detect_changes(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect file changes.
        
        Args:
            repo_path: Repository path
            
        Returns:
            Tuple of (added, modified, deleted) files
        """
        pass
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.
        
        Args:
            file_path: File to hash
            
        Returns:
            Hex digest of hash
        """
        pass
    
    def update_index(self, index: Index, changed_units: List[MemoryUnit]) -> Index:
        """Update index incrementally.
        
        Args:
            index: Existing index
            changed_units: Changed memory units
            
        Returns:
            Updated index
        """
        pass
    
    def update_graph(self, graph: Graph, changed_units: List[MemoryUnit], changed_relationships: List[Relationship]) -> Graph:
        """Update graph incrementally.
        
        Args:
            graph: Existing graph
            changed_units: Changed memory units
            changed_relationships: Changed relationships
            
        Returns:
            Updated graph
        """
        pass
```

### ScannerInterface

```python
class ScannerInterface:
    def scan(self, repo_path: Path, config: Config) -> Generator[Path, None, None]:
        """Scan repository for files.
        
        Args:
            repo_path: Repository path
            config: Scan configuration
            
        Yields:
            File paths
        """
        pass
    
    def should_scan(self, file_path: Path, config: Config) -> bool:
        """Check if file should be scanned.
        
        Args:
            file_path: File to check
            config: Scan configuration
            
        Returns:
            True if should scan
        """
        pass
```

### EmbeddingInterface

```python
class EmbeddingInterface:
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between embeddings.
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        pass
```

## Versioning

All interfaces are versioned. Changes to interfaces:

- **Patch**: Bug fixes, backward compatible
- **Minor**: New methods, backward compatible
- **Major**: Breaking changes

Current version: **1.0.0**
