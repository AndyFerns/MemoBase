"""
Core interface contracts for MemoBase.

Strict interface definitions that must be followed exactly.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Set, Tuple

from memobase.core.models import (
    Config,
    Findings,
    Graph,
    Index,
    MemoryUnit,
    ParsedFile,
    Query,
    Relationship,
    Response,
)


class ParserInterface(ABC):
    """Interface for code parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> ParsedFile:
        """Parse a file and return ParsedFile.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            ParsedFile with extracted symbols and metadata
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ParseError: If parsing fails
        """
        pass
    
    @abstractmethod
    def parse_batch(self, file_paths: List[Path]) -> Generator[ParsedFile, None, None]:
        """Parse multiple files in batch.
        
        Args:
            file_paths: List of file paths to parse
            
        Yields:
            ParsedFile objects as they are processed
        """
        pass
    
    @abstractmethod
    async def parse_async(self, file_path: Path) -> ParsedFile:
        """Async version of parse.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            ParsedFile with extracted symbols and metadata
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions (including leading dot)
        """
        pass


class MemoryBuilderInterface(ABC):
    """Interface for memory unit builders."""
    
    @abstractmethod
    def build(self, parsed_file: ParsedFile) -> List[MemoryUnit]:
        """Build memory units from parsed file.
        
        Args:
            parsed_file: The parsed file to process
            
        Returns:
            List of MemoryUnit objects
        """
        pass
    
    @abstractmethod
    def build_batch(self, parsed_files: Generator[ParsedFile, None, None]) -> Generator[MemoryUnit, None, None]:
        """Build memory units from multiple parsed files.
        
        Args:
            parsed_files: Generator of ParsedFile objects
            
        Yields:
            MemoryUnit objects as they are created
        """
        pass
    
    @abstractmethod
    async def build_async(self, parsed_file: ParsedFile) -> List[MemoryUnit]:
        """Async version of build.
        
        Args:
            parsed_file: The parsed file to process
            
        Returns:
            List of MemoryUnit objects
        """
        pass
    
    @abstractmethod
    def extract_relationships(self, memory_units: List[MemoryUnit]) -> List[Relationship]:
        """Extract relationships between memory units.
        
        Args:
            memory_units: List of MemoryUnit objects
            
        Returns:
            List of Relationship objects
        """
        pass


class StorageInterface(ABC):
    """Interface for persistent storage."""
    
    @abstractmethod
    def store(self, data: Any, key: str) -> None:
        """Store data with given key.
        
        Args:
            data: Data to store (must be serializable)
            key: Unique key for the data
        """
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Any:
        """Retrieve data by key.
        
        Args:
            key: Key of the data to retrieve
            
        Returns:
            Stored data or None if not found
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete data by key.
        
        Args:
            key: Key of the data to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if data exists for key.
        
        Args:
            key: Key to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_keys(self, prefix: str = "") -> List[str]:
        """List all keys with given prefix.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            List of matching keys
        """
        pass
    
    @abstractmethod
    async def store_async(self, data: Any, key: str) -> None:
        """Async version of store.
        
        Args:
            data: Data to store
            key: Unique key for the data
        """
        pass
    
    @abstractmethod
    async def retrieve_async(self, key: str) -> Any:
        """Async version of retrieve.
        
        Args:
            key: Key of the data to retrieve
            
        Returns:
            Stored data or None if not found
        """
        pass


class IndexInterface(ABC):
    """Interface for search indexing."""
    
    @abstractmethod
    def index(self, memory_units: List[MemoryUnit]) -> Index:
        """Create index from memory units.
        
        Args:
            memory_units: List of MemoryUnit objects to index
            
        Returns:
            Index object
        """
        pass
    
    @abstractmethod
    def update_index(self, index: Index, memory_units: List[MemoryUnit]) -> Index:
        """Update existing index with new memory units.
        
        Args:
            index: Existing index to update
            memory_units: New MemoryUnit objects to add
            
        Returns:
            Updated Index object
        """
        pass
    
    @abstractmethod
    def search(self, index: Index, query: str, limit: int = 10) -> List[str]:
        """Search index for matching memory unit IDs.
        
        Args:
            index: Index to search
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching MemoryUnit IDs
        """
        pass
    
    @abstractmethod
    def get_term_frequency(self, index: Index, term: str) -> Dict[str, int]:
        """Get term frequency across all documents.
        
        Args:
            index: Index to analyze
            term: Term to analyze
            
        Returns:
            Dictionary mapping unit_id to frequency
        """
        pass
    
    @abstractmethod
    async def index_async(self, memory_units: List[MemoryUnit]) -> Index:
        """Async version of index.
        
        Args:
            memory_units: List of MemoryUnit objects to index
            
        Returns:
            Index object
        """
        pass


class GraphInterface(ABC):
    """Interface for relationship graph."""
    
    @abstractmethod
    def build_graph(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Build relationship graph from memory units and relationships.
        
        Args:
            memory_units: List of MemoryUnit objects
            relationships: List of Relationship objects
            
        Returns:
            Graph object
        """
        pass
    
    @abstractmethod
    def update_graph(self, graph: Graph, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Update existing graph with new nodes and edges.
        
        Args:
            graph: Existing graph to update
            memory_units: New MemoryUnit objects to add
            relationships: New Relationship objects to add
            
        Returns:
            Updated Graph object
        """
        pass
    
    @abstractmethod
    def find_path(self, graph: Graph, source_id: str, target_id: str, max_depth: int = 5) -> Optional[List[str]]:
        """Find shortest path between two nodes.
        
        Args:
            graph: Graph to search
            source_id: Starting node ID
            target_id: Target node ID
            max_depth: Maximum search depth
            
        Returns:
            List of node IDs forming the path, or None if no path
        """
        pass
    
    @abstractmethod
    def get_neighbors(self, graph: Graph, node_id: str, relation_type: Optional[str] = None, max_depth: int = 1) -> Set[str]:
        """Get neighboring nodes.
        
        Args:
            graph: Graph to search
            node_id: Central node ID
            relation_type: Optional relation type filter
            max_depth: Search depth
            
        Returns:
            Set of neighboring node IDs
        """
        pass
    
    @abstractmethod
    def calculate_centrality(self, graph: Graph, node_id: str) -> float:
        """Calculate centrality score for a node.
        
        Args:
            graph: Graph to analyze
            node_id: Node ID to analyze
            
        Returns:
            Centrality score (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    async def build_graph_async(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Async version of build_graph.
        
        Args:
            memory_units: List of MemoryUnit objects
            relationships: List of Relationship objects
            
        Returns:
            Graph object
        """
        pass


class QueryInterface(ABC):
    """Interface for query processing."""
    
    @abstractmethod
    def query(self, query: Query, index: Index, graph: Graph) -> Response:
        """Execute query against index and graph.
        
        Args:
            query: Query object
            index: Search index
            graph: Relationship graph
            
        Returns:
            Response object with results
        """
        pass
    
    @abstractmethod
    def classify_intent(self, query_text: str) -> str:
        """Classify query intent.
        
        Args:
            query_text: Raw query text
            
        Returns:
            Intent classification string
        """
        pass
    
    @abstractmethod
    def extract_filters(self, query_text: str) -> Dict[str, Any]:
        """Extract filters from query text.
        
        Args:
            query_text: Raw query text
            
        Returns:
            Dictionary of filters
        """
        pass
    
    @abstractmethod
    def rank_results(self, results: List[MemoryUnit], query: Query) -> List[MemoryUnit]:
        """Rank results by relevance.
        
        Args:
            results: List of MemoryUnit results
            query: Original query
            
        Returns:
            Ranked list of MemoryUnit objects
        """
        pass
    
    @abstractmethod
    async def query_async(self, query: Query, index: Index, graph: Graph) -> Response:
        """Async version of query.
        
        Args:
            query: Query object
            index: Search index
            graph: Relationship graph
            
        Returns:
            Response object with results
        """
        pass


class AnalysisInterface(ABC):
    """Interface for code analysis."""
    
    @abstractmethod
    def analyze(self, memory_units: List[MemoryUnit]) -> List[Findings]:
        """Analyze memory units and generate findings.
        
        Args:
            memory_units: List of MemoryUnit objects to analyze
            
        Returns:
            List of Findings objects
        """
        pass
    
    @abstractmethod
    def detect_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect common patterns in code.
        
        Args:
            memory_units: List of MemoryUnit objects
            
        Returns:
            Dictionary mapping pattern names to matching units
        """
        pass
    
    @abstractmethod
    def calculate_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate code metrics.
        
        Args:
            memory_units: List of MemoryUnit objects
            
        Returns:
            Dictionary of metric names to values
        """
        pass
    
    @abstractmethod
    async def analyze_async(self, memory_units: List[MemoryUnit]) -> List[Findings]:
        """Async version of analyze.
        
        Args:
            memory_units: List of MemoryUnit objects to analyze
            
        Returns:
            List of Findings objects
        """
        pass


class IncrementalInterface(ABC):
    """Interface for incremental updates."""
    
    @abstractmethod
    def detect_changes(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect file changes in repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Tuple of (added_files, modified_files, deleted_files)
        """
        pass
    
    @abstractmethod
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            SHA256 hash string
        """
        pass
    
    @abstractmethod
    def update_index(self, index: Index, changed_units: List[MemoryUnit]) -> Index:
        """Update index with changed memory units.
        
        Args:
            index: Existing index
            changed_units: List of changed MemoryUnit objects
            
        Returns:
            Updated Index object
        """
        pass
    
    @abstractmethod
    def update_graph(self, graph: Graph, changed_units: List[MemoryUnit], changed_relationships: List[Relationship]) -> Graph:
        """Update graph with changes.
        
        Args:
            graph: Existing graph
            changed_units: List of changed MemoryUnit objects
            changed_relationships: List of changed Relationship objects
            
        Returns:
            Updated Graph object
        """
        pass
    
    @abstractmethod
    async def detect_changes_async(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Async version of detect_changes.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Tuple of (added_files, modified_files, deleted_files)
        """
        pass


class ScannerInterface(ABC):
    """Interface for filesystem scanning."""
    
    @abstractmethod
    def scan(self, repo_path: Path, config: Config) -> Generator[Path, None, None]:
        """Scan repository for files to process.
        
        Args:
            repo_path: Path to repository
            config: Configuration object
            
        Yields:
            Path objects for files to process
        """
        pass
    
    @abstractmethod
    def should_exclude(self, file_path: Path, config: Config) -> bool:
        """Check if file should be excluded.
        
        Args:
            file_path: Path to check
            config: Configuration object
            
        Returns:
            True if file should be excluded
        """
        pass
    
    @abstractmethod
    async def scan_async(self, repo_path: Path, config: Config) -> AsyncGenerator[Path, None]:
        """Async version of scan.
        
        Args:
            repo_path: Path to repository
            config: Configuration object
            
        Yields:
            Path objects for files to process
        """
        pass


class EmbeddingInterface(ABC):
    """Interface for text embeddings."""
    
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass
    
    @abstractmethod
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        pass
    
    @abstractmethod
    async def embed_async(self, text: str) -> List[float]:
        """Async version of embed.
        
        Args:
            text: Text to embed
            
        Returns:
            List of float values representing the embedding
        """
        pass
