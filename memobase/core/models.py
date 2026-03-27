"""
Core data models for MemoBase.

Strict JSON schema implementation with versioning.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import orjson


class VersionedModel:
    """Base class for all versioned models."""
    
    VERSION: str = "1.0.0"
    
    def __init__(self, **kwargs) -> None:
        self.version = self.VERSION
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, (list, dict, str, int, float, bool, type(None))):
                result[key] = value
            elif isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, Enum):
                result[key] = value.value
            else:
                result[key] = str(value)
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return orjson.dumps(self.to_dict()).decode()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VersionedModel":
        """Create instance from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "VersionedModel":
        """Create instance from JSON string."""
        data = orjson.loads(json_str)
        return cls.from_dict(data)


class FileType(Enum):
    """Supported file types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    RUST = "rust"
    GO = "go"
    RUBY = "ruby"
    PHP = "php"
    UNKNOWN = "unknown"


class SymbolType(Enum):
    """Symbol types in code."""
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    INTERFACE = "interface"
    VARIABLE = "variable"
    CONSTANT = "constant"
    IMPORT = "import"
    EXPORT = "export"
    TYPE = "type"
    ENUM = "enum"
    NAMESPACE = "namespace"
    MODULE = "module"
    UNKNOWN = "unknown"


class RelationType(Enum):
    """Relationship types between symbols."""
    CALLS = "calls"
    DEFINES = "defines"
    USES = "uses"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    IMPORTS = "imports"
    EXPORTS = "exports"
    CONTAINS = "contains"
    REFERENCES = "references"
    ANNOTATES = "annotates"


class QueryType(Enum):
    """Query types."""
    SEARCH = "search"
    FIND = "find"
    ANALYZE = "analyze"
    GRAPH = "graph"
    HELP = "help"


class AnalysisType(Enum):
    """Analysis types."""
    SECURITY = "security"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    COMPLEXITY = "complexity"


class SeverityLevel(Enum):
    """Severity levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ParsedFile(VersionedModel):
    """Represents a parsed source file."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        path: Path,
        file_type: FileType,
        content_hash: str,
        size_bytes: int,
        last_modified: datetime,
        symbols: Optional[List[Symbol]] = None,
        imports: Optional[List[str]] = None,
        exports: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.path = path
        self.file_type = file_type
        self.content_hash = content_hash
        self.size_bytes = size_bytes
        self.last_modified = last_modified
        self.symbols = symbols or []
        self.imports = imports or []
        self.exports = exports or []
        self.metadata = metadata or {}
    
    @classmethod
    def create_from_path(cls, path: Path) -> "ParsedFile":
        """Create ParsedFile from file path."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        stat = path.stat()
        content = path.read_bytes()
        content_hash = hashlib.sha256(content).hexdigest()
        
        file_type = cls._detect_file_type(path)
        
        return cls(
            path=path,
            file_type=file_type,
            content_hash=content_hash,
            size_bytes=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime)
        )
    
    @staticmethod
    def _detect_file_type(path: Path) -> FileType:
        """Detect file type from extension."""
        extension_map = {
            ".py": FileType.PYTHON,
            ".js": FileType.JAVASCRIPT,
            ".jsx": FileType.JAVASCRIPT,
            ".ts": FileType.TYPESCRIPT,
            ".tsx": FileType.TYPESCRIPT,
            ".java": FileType.JAVA,
            ".c": FileType.C,
            ".cpp": FileType.CPP,
            ".cc": FileType.CPP,
            ".cxx": FileType.CPP,
            ".rs": FileType.RUST,
            ".go": FileType.GO,
            ".rb": FileType.RUBY,
            ".php": FileType.PHP,
        }
        return extension_map.get(path.suffix.lower(), FileType.UNKNOWN)


class Symbol(VersionedModel):
    """Represents a code symbol."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        name: str,
        symbol_type: SymbolType,
        line_start: int,
        line_end: int,
        column_start: int,
        column_end: int,
        documentation: Optional[str] = None,
        signature: Optional[str] = None,
        parameters: Optional[List[str]] = None,
        return_type: Optional[str] = None,
        visibility: Optional[str] = None,
        is_async: bool = False,
        is_static: bool = False,
        is_exported: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.name = name
        self.symbol_type = symbol_type
        self.line_start = line_start
        self.line_end = line_end
        self.column_start = column_start
        self.column_end = column_end
        self.documentation = documentation
        self.signature = signature
        self.parameters = parameters or []
        self.return_type = return_type
        self.visibility = visibility
        self.is_async = is_async
        self.is_static = is_static
        self.is_exported = is_exported
        self.metadata = metadata or {}
    
    @property
    def location(self) -> Tuple[int, int, int, int]:
        """Get location as tuple."""
        return (self.line_start, self.line_end, self.column_start, self.column_end)


class MemoryUnit(VersionedModel):
    """Represents a unit of memory in the system."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        id: str,
        file_path: Path,
        symbol: Optional[Symbol] = None,
        content: Optional[str] = None,
        embeddings: Optional[List[float]] = None,
        keywords: Optional[List[str]] = None,
        relationships: Optional[List[Relationship]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id = id
        self.file_path = file_path
        self.symbol = symbol
        self.content = content
        self.embeddings = embeddings or []
        self.keywords = keywords or []
        self.relationships = relationships or []
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def create_from_symbol(cls, symbol: Symbol, file_path: Path, content: str) -> "MemoryUnit":
        """Create MemoryUnit from symbol."""
        unit_id = hashlib.sha256(f"{file_path}:{symbol.name}:{symbol.symbol_type.value}".encode()).hexdigest()
        return cls(
            id=unit_id,
            file_path=file_path,
            symbol=symbol,
            content=content,
            keywords=[symbol.name.lower()]
        )


class Relationship(VersionedModel):
    """Represents a relationship between memory units."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        source_id: str,
        target_id: str,
        relation_type: RelationType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.source_id = source_id
        self.target_id = target_id
        self.relation_type = relation_type
        self.weight = weight
        self.metadata = metadata or {}


class Index(VersionedModel):
    """Represents the search index."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        id: str,
        term_index: Optional[Dict[str, Set[str]]] = None,
        symbol_index: Optional[Dict[str, Set[str]]] = None,
        file_index: Optional[Dict[str, Set[str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id = id
        # Convert lists to sets if needed (JSON deserialization)
        self.term_index = self._convert_to_sets(term_index) if term_index else {}
        self.symbol_index = self._convert_to_sets(symbol_index) if symbol_index else {}
        self.file_index = self._convert_to_sets(file_index) if file_index else {}
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @staticmethod
    def _convert_to_sets(index_dict: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Convert dict values from lists to sets (for JSON deserialization)."""
        result = {}
        for key, value in index_dict.items():
            if isinstance(value, list):
                result[key] = set(value)
            elif isinstance(value, set):
                result[key] = value
            else:
                # Handle single values
                result[key] = {str(value)}
        return result
    
    def add_term(self, term: str, unit_id: str) -> None:
        """Add term to index."""
        if term not in self.term_index:
            self.term_index[term] = set()
        self.term_index[term].add(unit_id)
        self.updated_at = datetime.utcnow()
    
    def add_symbol(self, symbol: str, unit_id: str) -> None:
        """Add symbol to index."""
        if symbol not in self.symbol_index:
            self.symbol_index[symbol] = set()
        self.symbol_index[symbol].add(unit_id)
        self.updated_at = datetime.utcnow()
    
    def add_file(self, file_path: str, unit_id: str) -> None:
        """Add file to index."""
        if file_path not in self.file_index:
            self.file_index[file_path] = set()
        self.file_index[file_path].add(unit_id)
        self.updated_at = datetime.utcnow()


class Graph(VersionedModel):
    """Represents the relationship graph."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        id: str,
        nodes: Optional[Dict[str, MemoryUnit]] = None,
        edges: Optional[List[Relationship]] = None,
        adjacency_list: Optional[Dict[str, Set[str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id = id
        self.nodes = nodes or {}
        self.edges = edges or []
        self.adjacency_list = adjacency_list or {}
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_node(self, unit: MemoryUnit) -> None:
        """Add node to graph."""
        self.nodes[unit.id] = unit
        if unit.id not in self.adjacency_list:
            self.adjacency_list[unit.id] = set()
        self.updated_at = datetime.utcnow()
    
    def add_edge(self, relationship: Relationship) -> None:
        """Add edge to graph."""
        self.edges.append(relationship)
        if relationship.source_id not in self.adjacency_list:
            self.adjacency_list[relationship.source_id] = set()
        self.adjacency_list[relationship.source_id].add(relationship.target_id)
        self.updated_at = datetime.utcnow()
    
    def get_neighbors(self, node_id: str, max_depth: int = 1) -> Set[str]:
        """Get neighbors within specified depth."""
        visited = set()
        frontier = {node_id}
        
        for _ in range(max_depth):
            if not frontier:
                break
            next_frontier = set()
            for current in frontier:
                if current in self.adjacency_list:
                    for neighbor in self.adjacency_list[current]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            next_frontier.add(neighbor)
            frontier = next_frontier
        
        return visited


class Findings(VersionedModel):
    """Represents analysis findings."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        id: str,
        analysis_type: str,
        file_path: Path,
        line_number: int,
        severity: str,
        message: str,
        suggestion: Optional[str] = None,
        code_snippet: Optional[str] = None,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id = id
        self.analysis_type = analysis_type
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.message = message
        self.suggestion = suggestion
        self.code_snippet = code_snippet
        self.confidence = confidence
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()


class Query(VersionedModel):
    """Represents a user query."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        id: str,
        query_type: QueryType,
        text: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.id = id
        self.query_type = query_type
        self.text = text
        self.filters = filters or {}
        self.limit = limit
        self.offset = offset
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()


class Response(VersionedModel):
    """Represents a query response."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        query_id: str,
        results: List[MemoryUnit],
        total_count: int,
        execution_time_ms: float,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.query_id = query_id
        self.results = results
        self.total_count = total_count
        self.execution_time_ms = execution_time_ms
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()


class Config(VersionedModel):
    """System configuration."""
    
    VERSION: str = "1.0.0"
    
    def __init__(
        self,
        repo_path: Path,
        max_file_size_mb: int = 10,
        excluded_patterns: Optional[List[str]] = None,
        included_extensions: Optional[List[str]] = None,
        parallel_workers: int = 4,
        index_batch_size: int = 1000,
        graph_max_depth: int = 5,
        embedding_model: str = "default",
        cache_size_mb: int = 100,
        storage_path: str = ".memobase",
        verbosity: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.repo_path = Path(repo_path) if isinstance(repo_path, str) else repo_path
        self.max_file_size_mb = max_file_size_mb
        self.excluded_patterns = excluded_patterns or [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__",
            ".git",
            ".svn",
            ".hg",
            "node_modules",
            ".vscode",
            ".idea",
            "*.log",
            "*.tmp",
        ]
        self.included_extensions = included_extensions or [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".cc", ".cxx",
            ".rs", ".go", ".rb", ".php", ".h", ".hpp", ".hxx"
        ]
        self.parallel_workers = parallel_workers
        self.index_batch_size = index_batch_size
        self.graph_max_depth = graph_max_depth
        self.embedding_model = embedding_model
        self.cache_size_mb = cache_size_mb
        self.storage_path = storage_path
        self.verbosity = verbosity
        self.metadata = metadata or {}
