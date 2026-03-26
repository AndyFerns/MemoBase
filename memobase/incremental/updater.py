"""
Incremental updater implementation.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import QueryError
from memobase.core.interfaces import IncrementalInterface, ParserInterface, MemoryBuilderInterface
from memobase.core.models import Graph, Index, MemoryUnit, Relationship


class IncrementalUpdater(IncrementalInterface):
    """Handles incremental updates to index and graph."""
    
    def __init__(self, parser: ParserInterface, memory_builder: MemoryBuilderInterface) -> None:
        """Initialize incremental updater.
        
        Args:
            parser: Code parser
            memory_builder: Memory unit builder
        """
        self.parser = parser
        self.memory_builder = memory_builder
        self.update_history = []
    
    def detect_changes(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Detect file changes in repository."""
        # This would delegate to a ChangeDetector
        # For now, return empty changes
        return [], [], []
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        import hashlib
        
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def update_index(self, index: Index, changed_units: List[MemoryUnit]) -> Index:
        """Update index with changed memory units."""
        try:
            # Remove old versions of changed units
            for unit in changed_units:
                self._remove_unit_from_index(index, unit.id)
            
            # Add new versions
            for unit in changed_units:
                self._add_unit_to_index(index, unit)
            
            # Update timestamp
            from datetime import datetime
            index.updated_at = datetime.utcnow()
            
            return index
            
        except Exception as e:
            raise QueryError(f"Index update failed: {str(e)}")
    
    def update_graph(self, graph: Graph, changed_units: List[MemoryUnit], changed_relationships: List[Relationship]) -> Graph:
        """Update graph with changes."""
        try:
            # Remove old nodes and edges
            for unit in changed_units:
                self._remove_unit_from_graph(graph, unit.id)
            
            for relationship in changed_relationships:
                self._remove_relationship_from_graph(graph, relationship.id)
            
            # Add new nodes and edges
            for unit in changed_units:
                self._add_unit_to_graph(graph, unit)
            
            for relationship in changed_relationships:
                self._add_relationship_to_graph(graph, relationship)
            
            # Update timestamp
            from datetime import datetime
            graph.updated_at = datetime.utcnow()
            
            return graph
            
        except Exception as e:
            raise QueryError(f"Graph update failed: {str(e)}")
    
    async def detect_changes_async(self, repo_path: Path) -> Tuple[List[Path], List[Path], List[Path]]:
        """Async version of detect_changes."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.detect_changes, repo_path)
    
    def incremental_build(self, repo_path: Path, added_files: List[Path], 
                         modified_files: List[Path], deleted_files: List[Path]) -> Tuple[List[MemoryUnit], List[Relationship]]:
        """Perform incremental build."""
        try:
            all_memory_units = []
            all_relationships = []
            
            # Process added files
            added_units, added_relationships = self._process_files(added_files)
            all_memory_units.extend(added_units)
            all_relationships.extend(added_relationships)
            
            # Process modified files
            modified_units, modified_relationships = self._process_files(modified_files)
            all_memory_units.extend(modified_units)
            all_relationships.extend(modified_relationships)
            
            # Note: deleted files are handled by removing their units from index/graph
            
            return all_memory_units, all_relationships
            
        except Exception as e:
            raise QueryError(f"Incremental build failed: {str(e)}")
    
    def update_storage(self, storage, added_units: List[MemoryUnit], 
                      modified_units: List[MemoryUnit], deleted_unit_ids: List[str]) -> None:
        """Update storage with changes."""
        try:
            # Store added units
            for unit in added_units:
                storage.store(unit, f"memory_unit:{unit.id}")
            
            # Store modified units
            for unit in modified_units:
                storage.store(unit, f"memory_unit:{unit.id}")
            
            # Delete removed units
            for unit_id in deleted_unit_ids:
                storage.delete(f"memory_unit:{unit_id}")
                
        except Exception as e:
            raise QueryError(f"Storage update failed: {str(e)}")
    
    def get_update_statistics(self) -> Dict[str, int]:
        """Get statistics about recent updates."""
        if not self.update_history:
            return {
                'total_updates': 0,
                'avg_files_per_update': 0,
                'last_update_files': 0,
            }
        
        total_updates = len(self.update_history)
        total_files = sum(update['file_count'] for update in self.update_history)
        avg_files = total_files / total_updates
        last_update_files = self.update_history[-1]['file_count']
        
        return {
            'total_updates': total_updates,
            'avg_files_per_update': avg_files,
            'last_update_files': last_update_files,
        }
    
    def rollback_update(self, storage, update_id: str) -> bool:
        """Rollback a specific update (simplified)."""
        try:
            # This would require storing backup information
            # For now, return False indicating not implemented
            return False
            
        except Exception as e:
            raise QueryError(f"Rollback failed: {str(e)}")
    
    def _process_files(self, file_paths: List[Path]) -> Tuple[List[MemoryUnit], List[Relationship]]:
        """Process files and extract memory units and relationships."""
        all_units = []
        all_relationships = []
        
        for file_path in file_paths:
            try:
                # Parse file
                parsed_file = self.parser.parse(file_path)
                
                # Build memory units
                memory_units = self.memory_builder.build(parsed_file)
                all_units.extend(memory_units)
                
                # Extract relationships
                relationships = self.memory_builder.extract_relationships(memory_units)
                all_relationships.extend(relationships)
                
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error processing {file_path}: {e}")
                continue
        
        return all_units, all_relationships
    
    def _remove_unit_from_index(self, index: Index, unit_id: str) -> None:
        """Remove unit from all index structures."""
        # Remove from term index
        for term, unit_set in index.term_index.items():
            unit_set.discard(unit_id)
        
        # Remove from symbol index
        for symbol, unit_set in index.symbol_index.items():
            unit_set.discard(unit_id)
        
        # Remove from file index
        for file_path, unit_set in index.file_index.items():
            unit_set.discard(unit_id)
        
        # Clean up empty sets
        index.term_index = {k: v for k, v in index.term_index.items() if v}
        index.symbol_index = {k: v for k, v in index.symbol_index.items() if v}
        index.file_index = {k: v for k, v in index.file_index.items() if v}
    
    def _add_unit_to_index(self, index: Index, unit: MemoryUnit) -> None:
        """Add unit to all index structures."""
        # Add to file index
        file_key = str(unit.file_path)
        if file_key not in index.file_index:
            index.file_index[file_key] = set()
        index.file_index[file_key].add(unit.id)
        
        # Add keywords to term index
        for keyword in unit.keywords:
            if keyword not in index.term_index:
                index.term_index[keyword] = set()
            index.term_index[keyword].add(unit.id)
        
        # Add symbol information
        if unit.symbol:
            symbol_name = unit.symbol.name
            if symbol_name not in index.symbol_index:
                index.symbol_index[symbol_name] = set()
            index.symbol_index[symbol_name].add(unit.id)
            
            symbol_type = unit.symbol.symbol_type.value
            if symbol_type not in index.symbol_index:
                index.symbol_index[symbol_type] = set()
            index.symbol_index[symbol_type].add(unit.id)
    
    def _remove_unit_from_graph(self, graph: Graph, unit_id: str) -> None:
        """Remove unit from graph."""
        if unit_id in graph.nodes:
            del graph.nodes[unit_id]
        
        if unit_id in graph.adjacency_list:
            del graph.adjacency_list[unit_id]
        
        # Remove edges connected to this unit
        graph.edges = [edge for edge in graph.edges 
                      if edge.source_id != unit_id and edge.target_id != unit_id]
        
        # Remove from adjacency lists of other nodes
        for neighbors in graph.adjacency_list.values():
            neighbors.discard(unit_id)
    
    def _add_unit_to_graph(self, graph: Graph, unit: MemoryUnit) -> None:
        """Add unit to graph."""
        graph.nodes[unit.id] = unit
        if unit.id not in graph.adjacency_list:
            graph.adjacency_list[unit.id] = set()
    
    def _remove_relationship_from_graph(self, graph: Graph, relationship_id: str) -> None:
        """Remove relationship from graph."""
        # Find and remove edge by ID
        for i, edge in enumerate(graph.edges):
            if edge.id == relationship_id:
                removed_edge = graph.edges.pop(i)
                
                # Remove from adjacency list
                if removed_edge.source_id in graph.adjacency_list:
                    graph.adjacency_list[removed_edge.source_id].discard(removed_edge.target_id)
                
                break
    
    def _add_relationship_to_graph(self, graph: Graph, relationship: Relationship) -> None:
        """Add relationship to graph."""
        graph.edges.append(relationship)
        if relationship.source_id not in graph.adjacency_list:
            graph.adjacency_list[relationship.source_id] = set()
        graph.adjacency_list[relationship.source_id].add(relationship.target_id)


class BatchIncrementalUpdater(IncrementalUpdater):
    """Batch processor for large incremental updates."""
    
    def __init__(self, parser: ParserInterface, memory_builder: MemoryBuilderInterface, batch_size: int = 100) -> None:
        """Initialize batch incremental updater.
        
        Args:
            parser: Code parser
            memory_builder: Memory unit builder
            batch_size: Number of files to process in each batch
        """
        super().__init__(parser, memory_builder)
        self.batch_size = batch_size
    
    def incremental_build(self, repo_path: Path, added_files: List[Path], 
                         modified_files: List[Path], deleted_files: List[Path]) -> Tuple[List[MemoryUnit], List[Relationship]]:
        """Perform incremental build in batches."""
        try:
            all_memory_units = []
            all_relationships = []
            
            # Process files in batches
            all_files = added_files + modified_files
            
            for i in range(0, len(all_files), self.batch_size):
                batch_files = all_files[i:i + self.batch_size]
                
                batch_units, batch_relationships = self._process_files(batch_files)
                all_memory_units.extend(batch_units)
                all_relationships.extend(batch_relationships)
                
                # Yield progress (in practice, you might use a callback)
                progress = (i + len(batch_files)) / len(all_files) * 100
                print(f"Processing batch: {progress:.1f}% complete")
            
            return all_memory_units, all_relationships
            
        except Exception as e:
            raise QueryError(f"Batch incremental build failed: {str(e)}")
    
    def update_index_batch(self, index: Index, changed_units: List[MemoryUnit]) -> Index:
        """Update index with batch of changed units."""
        try:
            # Batch remove old units
            unit_ids = [unit.id for unit in changed_units]
            self._batch_remove_from_index(index, unit_ids)
            
            # Batch add new units
            self._batch_add_to_index(index, changed_units)
            
            # Update timestamp
            from datetime import datetime
            index.updated_at = datetime.utcnow()
            
            return index
            
        except Exception as e:
            raise QueryError(f"Batch index update failed: {str(e)}")
    
    def update_graph_batch(self, graph: Graph, changed_units: List[MemoryUnit], 
                          changed_relationships: List[Relationship]) -> Graph:
        """Update graph with batch of changes."""
        try:
            # Batch remove old units
            unit_ids = [unit.id for unit in changed_units]
            self._batch_remove_from_graph(graph, unit_ids)
            
            # Batch remove old relationships
            relationship_ids = [rel.id for rel in changed_relationships]
            self._batch_remove_relationships_from_graph(graph, relationship_ids)
            
            # Batch add new units
            self._batch_add_to_graph(graph, changed_units)
            
            # Batch add new relationships
            self._batch_add_relationships_to_graph(graph, changed_relationships)
            
            # Update timestamp
            from datetime import datetime
            graph.updated_at = datetime.utcnow()
            
            return graph
            
        except Exception as e:
            raise QueryError(f"Batch graph update failed: {str(e)}")
    
    def _batch_remove_from_index(self, index: Index, unit_ids: List[str]) -> None:
        """Remove multiple units from index."""
        unit_id_set = set(unit_ids)
        
        # Remove from term index
        for term, unit_set in index.term_index.items():
            unit_set -= unit_id_set
        
        # Remove from symbol index
        for symbol, unit_set in index.symbol_index.items():
            unit_set -= unit_id_set
        
        # Remove from file index
        for file_path, unit_set in index.file_index.items():
            unit_set -= unit_id_set
        
        # Clean up empty sets
        index.term_index = {k: v for k, v in index.term_index.items() if v}
        index.symbol_index = {k: v for k, v in index.symbol_index.items() if v}
        index.file_index = {k: v for k, v in index.file_index.items() if v}
    
    def _batch_add_to_index(self, index: Index, units: List[MemoryUnit]) -> None:
        """Add multiple units to index."""
        for unit in units:
            self._add_unit_to_index(index, unit)
    
    def _batch_remove_from_graph(self, graph: Graph, unit_ids: List[str]) -> None:
        """Remove multiple units from graph."""
        unit_id_set = set(unit_ids)
        
        # Remove nodes
        for unit_id in unit_id_set:
            if unit_id in graph.nodes:
                del graph.nodes[unit_id]
            if unit_id in graph.adjacency_list:
                del graph.adjacency_list[unit_id]
        
        # Remove edges
        graph.edges = [edge for edge in graph.edges 
                      if edge.source_id not in unit_id_set and edge.target_id not in unit_id_set]
        
        # Remove from adjacency lists
        for neighbors in graph.adjacency_list.values():
            neighbors -= unit_id_set
    
    def _batch_add_to_graph(self, graph: Graph, units: List[MemoryUnit]) -> None:
        """Add multiple units to graph."""
        for unit in units:
            self._add_unit_to_graph(graph, unit)
    
    def _batch_remove_relationships_from_graph(self, graph: Graph, relationship_ids: List[str]) -> None:
        """Remove multiple relationships from graph."""
        relationship_id_set = set(relationship_ids)
        
        # Remove edges
        graph.edges = [edge for edge in graph.edges if edge.id not in relationship_id_set]
        
        # Rebuild adjacency list (simplified)
        graph.adjacency_list = {}
        for edge in graph.edges:
            if edge.source_id not in graph.adjacency_list:
                graph.adjacency_list[edge.source_id] = set()
            graph.adjacency_list[edge.source_id].add(edge.target_id)
    
    def _batch_add_relationships_to_graph(self, graph: Graph, relationships: List[Relationship]) -> None:
        """Add multiple relationships to graph."""
        for relationship in relationships:
            self._add_relationship_to_graph(graph, relationship)
