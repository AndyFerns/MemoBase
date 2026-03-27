"""
Project builder module for MemoBase.

Handles building the memory index for a repository.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from memobase.core.models import Config
from memobase.infrastructure.filesystem.scanner import FilesystemScanner
from memobase.infrastructure.concurrency.executor import Executor
from memobase.parser.factory import ParserFactory
from memobase.memory.builder import MemoryBuilder
from memobase.memory.embedder import TextEmbedder
from memobase.index.builder import IndexBuilder
from memobase.graph.builder import GraphBuilder
from memobase.storage.file_storage import FileStorage


class ProjectBuilder:
    """Handles building the complete memory index for a project."""
    
    def __init__(self, config: Config) -> None:
        """Initialize project builder.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.repo_path = config.repo_path
        self.storage = FileStorage(config.repo_path / config.storage_path)
        self.parser_factory = ParserFactory()
        self.embedder = TextEmbedder()
        self.memory_builder = MemoryBuilder(self.embedder)
        self.index_builder = IndexBuilder(self.embedder)
        self.graph_builder = GraphBuilder()
    
    def build_repo(self, force: bool = False) -> Dict[str, Any]:
        """Build the complete memory index.
        
        Args:
            force: Force rebuild (ignore existing)
            
        Returns:
            Build statistics
        """
        start_time = time.time()
        
        # Scan files
        scanner = FilesystemScanner(self.config)
        files = list(scanner.scan(self.repo_path))
        
        if not files:
            return {
                'files_processed': 0,
                'memory_units': 0,
                'relationships': 0,
                'build_time': 0.0,
            }
        
        # Parse files
        parsed_files = self._parse_files(files)
        
        # Build memory units
        memory_units = self._build_memory_units(parsed_files)
        
        # Extract relationships
        relationships = self.memory_builder.extract_relationships(memory_units)
        
        # Build index
        index = self.index_builder.index(memory_units)
        
        # Build graph
        graph = self.graph_builder.build_graph(memory_units, relationships)
        
        # Store results
        self._store_results(memory_units, relationships, index, graph)
        
        build_time = time.time() - start_time
        
        return {
            'files_processed': len(files),
            'memory_units': len(memory_units),
            'relationships': len(relationships),
            'build_time': build_time,
        }
    
    def _parse_files(self, files: List[Path]) -> List[Any]:
        """Parse all source files."""
        parsed = []
        
        with Executor(max_workers=self.config.parallel_workers, use_processes=True) as executor:
            for file_path in files:
                parser = self.parser_factory.get_parser_by_extension(file_path.suffix)
                
                if parser:
                    try:
                        result = parser.parse(file_path)
                        if result:
                            parsed.append(result)
                    except Exception as e:
                        pass  # Skip files that fail to parse
        
        return parsed
    
    def _build_memory_units(self, parsed_files: List[Any]) -> List[Any]:
        """Build memory units from parsed files."""
        units = []
        
        for parsed in parsed_files:
            file_units = self.memory_builder.build(parsed)
            units.extend(file_units)
            # DEBUG: print("[DEBUG] Parsed file:", parsed.path)
            # DEBUG: print("[DEBUG] Symbols:", parsed.symbols)
        
        return units
    
    def safe_id(id: str) -> str:
        return id.replace("/", "_").replace("\\", "_").replace(":", "_")
    
    def _store_results(self, memory_units, relationships, index, graph) -> None:
        """Store build results to storage."""
        # Store memory units
        for unit in memory_units:
            self.storage.store(unit.to_dict(), f"memory_unit:{self.safe_id(unit.id)}")
        
        # Store index
        self.storage.store(index.to_dict(), "index:main")

        # Store graph
        self.storage.store(graph.to_dict(), "graph:main")
