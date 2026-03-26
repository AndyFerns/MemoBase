"""
Bridge layer between TUI and core modules.

TUI → Controller → Core Modules
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from memobase.core.models import Config, Findings, Graph, MemoryUnit, Query, QueryType, Response
from memobase.tui.state import TUIState
from memobase.tui.event_bus import EventBus


class TUIController:
    """Bridge between TUI and core modules."""
    
    def __init__(self, config: Config, state: TUIState, event_bus: EventBus) -> None:
        """Initialize TUI controller.
        
        Args:
            config: MemoBase configuration
            state: TUI state manager
            event_bus: Event bus for decoupled communication
        """
        self.config = config
        self.state = state
        self.event_bus = event_bus
        
        # Core modules (initialized lazily)
        self._parser = None
        self._memory_builder = None
        self._index = None
        self._graph = None
        self._query_processor = None
        self._analyzer = None
    
    async def initialize(self) -> None:
        """Initialize controller and load core modules."""
        self.state.set_status("Initializing...")
        
        # Initialize core modules
        await self._initialize_core_modules()
        
        # Load file tree
        await self._load_file_tree()
        
        self.state.set_status("Ready")
    
    async def _initialize_core_modules(self) -> None:
        """Initialize core modules asynchronously."""
        # Import core modules
        from memobase.parser.factory import ParserFactory
        from memobase.memory.builder import MemoryBuilder
        from memobase.memory.embedder import TextEmbedder
        from memobase.index.builder import IndexBuilder
        from memobase.graph.builder import GraphBuilder
        from memobase.query.processor import QueryProcessor
        from memobase.analysis.code_analyzer import CodeAnalyzer
        from memobase.storage.file_storage import FileStorage
        
        # Initialize storage
        storage = FileStorage(self.config.storage_path)
        
        # Initialize embedder
        embedder = TextEmbedder()
        
        # Initialize modules
        self._parser = ParserFactory()
        self._memory_builder = MemoryBuilder(embedder)
        self._index_builder = IndexBuilder(embedder)
        self._graph_builder = GraphBuilder()
        self._query_processor = QueryProcessor()
        self._analyzer = CodeAnalyzer()
        
        # Try to load existing index and graph
        try:
            # Load from storage if available
            pass  # Implementation depends on storage backend
        except Exception:
            # No existing data, will build fresh
            pass
    
    async def _load_file_tree(self) -> None:
        """Load file tree data."""
        from memobase.infrastructure.filesystem.scanner import FilesystemScanner
        
        scanner = FilesystemScanner(self.config)
        
        file_tree = []
        async for file_path in scanner.scan_async(self.config.repo_path):
            file_tree.append({
                "path": str(file_path),
                "name": file_path.name,
                "type": "file",
            })
        
        self.state.file_tree_data = file_tree
    
    async def get_file_memory(self, file_path: str) -> Optional[MemoryUnit]:
        """Get memory unit for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            MemoryUnit if found, None otherwise
        """
        self.state.set_loading(True)
        
        try:
            # Query index for file
            from memobase.index.searcher import IndexSearcher
            
            searcher = IndexSearcher()
            unit_ids = searcher.search(self._index, file_path, limit=1)
            
            if unit_ids:
                # Load memory unit from storage
                # Placeholder: would load from storage
                pass
            
            return None
            
        finally:
            self.state.set_loading(False)
    
    async def get_dependencies(self, file_path: str, depth: int = 3) -> Optional[Graph]:
        """Get dependency graph for file.
        
        Args:
            file_path: Path to file
            depth: Graph traversal depth
            
        Returns:
            Graph subset if found, None otherwise
        """
        self.state.set_loading(True)
        
        try:
            # Get file's memory unit
            memory_unit = await self.get_file_memory(file_path)
            
            if not memory_unit:
                return None
            
            # Traverse graph from this node
            from memobase.graph.traversal import GraphTraversal
            
            traversal = GraphTraversal(self._graph)
            neighbors = traversal.get_neighbors(
                self._graph, 
                memory_unit.id, 
                max_depth=depth
            )
            
            # Build subgraph
            # Placeholder: would build actual subgraph
            return None
            
        finally:
            self.state.set_loading(False)
    
    async def run_query(self, query_text: str, query_type: QueryType = QueryType.SEARCH) -> Response:
        """Run a query against the codebase.
        
        Args:
            query_text: Query string
            query_type: Type of query
            
        Returns:
            Query response
        """
        self.state.set_loading(True)
        self.state.set_status(f"Querying: {query_text}...")
        
        try:
            # Create query object
            query = Query(
                id=f"tui_query_{len(self.state.query_history)}",
                text=query_text,
                query_type=query_type,
                filters={},
                limit=50,
                offset=0,
            )
            
            # Execute query
            response = self._query_processor.query(
                query, self._index, self._graph
            )
            
            # Update state
            self.state.add_to_query_history(query_text)
            self.state.set_query_response(response)
            
            # Emit event
            self.event_bus.emit("query_result", {"response": response})
            
            return response
            
        finally:
            self.state.set_loading(False)
            self.state.set_status("Ready")
    
    async def run_analysis(self, analysis_type: str = "all") -> List[Findings]:
        """Run code analysis.
        
        Args:
            analysis_type: Type of analysis to run
            
        Returns:
            List of findings
        """
        self.state.set_loading(True)
        self.state.set_status("Running analysis...")
        
        try:
            # Run analysis
            findings = self._analyzer.analyze([])  # Would pass actual memory units
            
            # Update state
            self.state.set_analysis_results(findings)
            
            return findings
            
        finally:
            self.state.set_loading(False)
            self.state.set_status("Ready")
    
    async def refresh_data(self) -> None:
        """Refresh all data."""
        self.state.set_loading(True)
        self.state.set_status("Refreshing...")
        
        try:
            # Reload file tree
            await self._load_file_tree()
            
            # Reload index and graph
            await self._initialize_core_modules()
            
            # Emit refresh event
            self.event_bus.emit("state_changed", {"refreshed": True})
            
        finally:
            self.state.set_loading(False)
            self.state.set_status("Ready")
    
    def get_file_tree(self) -> List[Dict[str, Any]]:
        """Get file tree data."""
        return self.state.file_tree_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get repository stats."""
        return {
            "total_files": len(self.state.file_tree_data),
            "current_mode": self.state.current_mode,
            "query_count": len(self.state.query_history),
            "verbosity": self.state.verbosity,
        }
