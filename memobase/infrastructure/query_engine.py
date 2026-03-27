"""
Query engine module for MemoBase.

Handles query execution and response generation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from memobase.core.models import Config, Query, QueryType, Response
from memobase.index.searcher import IndexSearcher
from memobase.graph.traversal import GraphTraversal
from memobase.query.processor import QueryProcessor
from memobase.query.classifier import IntentClassifier
from memobase.storage.file_storage import FileStorage


class QueryEngine:
    """Handles query execution against the memory index."""
    
    def __init__(self, config: Config) -> None:
        """Initialize query engine.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.storage = FileStorage(config.repo_path / config.storage_path)
        self.classifier = IntentClassifier()
        self.processor = QueryProcessor(config)
        self.searcher = IndexSearcher()
    
    def ask_question(self, question: str, limit: int = 10) -> Response:
        """Ask a natural language question about the codebase.
        
        Args:
            question: The question to ask
            limit: Maximum number of results
            
        Returns:
            Query response
        """
        # Classify intent
        intent = self.classifier.classify(question)
        
        # Create query
        query = Query(
            id=f"ask_{hash(question) & 0xFFFFFFFF}",
            text=question,
            query_type=QueryType.SEARCH,
            filters={},
            limit=limit,
            offset=0,
        )
        
        # Load index and graph
        index_data = self.storage.load("index/main")
        graph_data = self.storage.load("graph/main")
        
        if not index_data:
            return Response(
                query_id=query.id,
                results=[],
                total_count=0,
                execution_time_ms=0.0,
                metadata={'error': 'No index found. Run "memobase build" first.'},
            )
        
        # Execute query
        from memobase.core.models import Index, Graph
        index = Index(**index_data)
        graph = Graph(**graph_data) if graph_data else None
        
        response = self.processor.query(query, index, graph)
        
        return response
    
    def execute_query(self, query_text: str, filters: Dict[str, str], limit: int, offset: int) -> Response:
        """Execute a structured search query.
        
        Args:
            query_text: Query string
            filters: Query filters
            limit: Maximum results
            offset: Result offset
            
        Returns:
            Query response
        """
        # Create query
        query = Query(
            id=f"query_{hash(query_text) & 0xFFFFFFFF}",
            text=query_text,
            query_type=QueryType.SEARCH,
            filters=filters,
            limit=limit,
            offset=offset,
        )
        
        # Load index
        index_data = self.storage.load("index/main")
        
        if not index_data:
            return Response(
                query_id=query.id,
                results=[],
                total_count=0,
                execution_time_ms=0.0,
                metadata={'error': 'No index found. Run "memobase build" first.'},
            )
        
        from memobase.core.models import Index
        index = Index(**index_data)
        
        # Search index
        results = self.searcher.search(index, query_text, limit=limit)
        
        # Load memory units
        memory_units = []
        for unit_id in results:
            unit_data = self.storage.load(f"memory/{unit_id}")
            if unit_data:
                from memobase.core.models import MemoryUnit
                memory_units.append(MemoryUnit(**unit_data))
        
        return Response(
            query_id=query.id,
            results=memory_units,
            total_count=len(memory_units),
            execution_time_ms=0.0,
            metadata={'query_type': 'search'},
        )
