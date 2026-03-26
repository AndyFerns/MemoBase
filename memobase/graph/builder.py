"""
Graph builder implementation.
"""

from __future__ import annotations

import asyncio
import hashlib
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from typing import Dict, List, Set

from memobase.core.exceptions import GraphError
from memobase.core.interfaces import GraphInterface
from memobase.core.models import Graph, MemoryUnit, Relationship


class GraphBuilder(GraphInterface):
    """Builds and maintains relationship graphs."""
    
    def __init__(self) -> None:
        """Initialize graph builder."""
        self.node_cache = {}
        self.edge_cache = {}
    
    def build_graph(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Build relationship graph from memory units and relationships."""
        try:
            graph_id = hashlib.sha256(f"graph_{datetime.utcnow().isoformat()}".encode()).hexdigest()
            
            # Initialize graph structures
            nodes = {}
            edges = []
            adjacency_list = defaultdict(set)
            
            # Add nodes
            for unit in memory_units:
                nodes[unit.id] = unit
                adjacency_list[unit.id] = set()
            
            # Add edges
            for relationship in relationships:
                # Only add edges if both nodes exist
                if relationship.source_id in nodes and relationship.target_id in nodes:
                    edges.append(relationship)
                    adjacency_list[relationship.source_id].add(relationship.target_id)
            
            # Create Graph object
            graph = Graph(
                id=graph_id,
                nodes=nodes,
                edges=edges,
                adjacency_list=dict(adjacency_list)
            )
            
            return graph
            
        except Exception as e:
            raise GraphError(f"Failed to build graph: {str(e)}")
    
    def update_graph(self, graph: Graph, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Update existing graph with new nodes and edges."""
        try:
            # Add new nodes
            for unit in memory_units:
                if unit.id not in graph.nodes:
                    graph.nodes[unit.id] = unit
                    if unit.id not in graph.adjacency_list:
                        graph.adjacency_list[unit.id] = set()
            
            # Add new edges
            for relationship in relationships:
                # Only add edges if both nodes exist
                if relationship.source_id in graph.nodes and relationship.target_id in graph.nodes:
                    graph.edges.append(relationship)
                    graph.adjacency_list[relationship.source_id].add(relationship.target_id)
            
            # Update timestamp
            graph.updated_at = datetime.utcnow()
            
            return graph
            
        except Exception as e:
            raise GraphError(f"Failed to update graph: {str(e)}")
    
    def find_path(self, graph: Graph, source_id: str, target_id: str, max_depth: int = 5) -> List[str]:
        """Find shortest path between two nodes."""
        try:
            if source_id not in graph.nodes or target_id not in graph.nodes:
                return []
            
            # BFS to find shortest path
            from collections import deque
            
            queue = deque([(source_id, [source_id])])
            visited = {source_id}
            
            while queue and len(queue[0][1]) <= max_depth:
                current, path = queue.popleft()
                
                if current == target_id:
                    return path
                
                # Explore neighbors
                for neighbor in graph.adjacency_list.get(current, set()):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            return []
            
        except Exception as e:
            raise GraphError(f"Failed to find path: {str(e)}")
    
    def get_neighbors(self, graph: Graph, node_id: str, relation_type: str = None, max_depth: int = 1) -> Set[str]:
        """Get neighboring nodes."""
        try:
            if node_id not in graph.nodes:
                return set()
            
            neighbors = set()
            
            if max_depth == 1:
                # Direct neighbors
                if relation_type:
                    # Filter by relation type
                    for edge in graph.edges:
                        if edge.source_id == node_id and edge.relation_type.value == relation_type:
                            neighbors.add(edge.target_id)
                        elif edge.target_id == node_id and edge.relation_type.value == relation_type:
                            neighbors.add(edge.source_id)
                else:
                    # All neighbors
                    neighbors.update(graph.adjacency_list.get(node_id, set()))
                    
                    # Also check incoming edges
                    for edge in graph.edges:
                        if edge.target_id == node_id:
                            neighbors.add(edge.source_id)
            else:
                # Multi-depth neighbors
                visited = {node_id}
                frontier = {node_id}
                
                for _ in range(max_depth):
                    if not frontier:
                        break
                    
                    next_frontier = set()
                    for current in frontier:
                        current_neighbors = graph.adjacency_list.get(current, set())
                        
                        if relation_type:
                            # Filter by relation type
                            filtered_neighbors = set()
                            for neighbor in current_neighbors:
                                # Check if edge matches relation type
                                edge_matches = False
                                for edge in graph.edges:
                                    if ((edge.source_id == current and edge.target_id == neighbor) or
                                        (edge.source_id == neighbor and edge.target_id == current)):
                                        if edge.relation_type.value == relation_type:
                                            edge_matches = True
                                            break
                                if edge_matches:
                                    filtered_neighbors.add(neighbor)
                            current_neighbors = filtered_neighbors
                        
                        for neighbor in current_neighbors:
                            if neighbor not in visited:
                                visited.add(neighbor)
                                next_frontier.add(neighbor)
                                neighbors.add(neighbor)
                    
                    frontier = next_frontier
            
            return neighbors
            
        except Exception as e:
            raise GraphError(f"Failed to get neighbors: {str(e)}")
    
    def calculate_centrality(self, graph: Graph, node_id: str) -> float:
        """Calculate centrality score for a node."""
        try:
            if node_id not in graph.nodes:
                return 0.0
            
            # Calculate degree centrality (simple implementation)
            degree = len(graph.adjacency_list.get(node_id, set()))
            
            # Add incoming edges
            incoming_degree = 0
            for edge in graph.edges:
                if edge.target_id == node_id:
                    incoming_degree += 1
            
            total_degree = degree + incoming_degree
            
            # Normalize by maximum possible degree
            max_degree = len(graph.nodes) - 1
            if max_degree > 0:
                return total_degree / max_degree
            else:
                return 0.0
                
        except Exception as e:
            raise GraphError(f"Failed to calculate centrality: {str(e)}")
    
    async def build_graph_async(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Async version of build_graph."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.build_graph, memory_units, relationships)
    
    def build_weighted_graph(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Build graph with edge weights considered."""
        try:
            graph = self.build_graph(memory_units, relationships)
            
            # Calculate edge weight statistics for normalization
            if graph.edges:
                weights = [edge.weight for edge in graph.edges]
                min_weight = min(weights)
                max_weight = max(weights)
                weight_range = max_weight - min_weight if max_weight != min_weight else 1.0
                
                # Normalize weights to 0-1 range
                for edge in graph.edges:
                    if weight_range > 0:
                        edge.metadata['normalized_weight'] = (edge.weight - min_weight) / weight_range
                    else:
                        edge.metadata['normalized_weight'] = 1.0
            
            return graph
            
        except Exception as e:
            raise GraphError(f"Failed to build weighted graph: {str(e)}")
    
    def build_directed_graph(self, memory_units: List[MemoryUnit], relationships: List[Relationship]) -> Graph:
        """Build directed graph (edges have direction)."""
        try:
            graph = self.build_graph(memory_units, relationships)
            
            # Mark graph as directed in metadata
            graph.metadata['is_directed'] = True
            graph.metadata['edge_count'] = len(graph.edges)
            graph.metadata['node_count'] = len(graph.nodes)
            
            # Calculate in-degree and out-degree for each node
            in_degrees = {}
            out_degrees = {}
            
            for node_id in graph.nodes:
                in_degrees[node_id] = 0
                out_degrees[node_id] = len(graph.adjacency_list.get(node_id, set()))
            
            for edge in graph.edges:
                in_degrees[edge.target_id] = in_degrees.get(edge.target_id, 0) + 1
            
            graph.metadata['in_degrees'] = in_degrees
            graph.metadata['out_degrees'] = out_degrees
            
            return graph
            
        except Exception as e:
            raise GraphError(f"Failed to build directed graph: {str(e)}")
    
    def find_cycles(self, graph: Graph) -> List[List[str]]:
        """Find cycles in the graph."""
        try:
            cycles = []
            visited = set()
            rec_stack = set()
            path = []
            
            def dfs(node_id: str):
                if node_id in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(node_id)
                    cycle = path[cycle_start:] + [node_id]
                    cycles.append(cycle)
                    return
                
                if node_id in visited:
                    return
                
                visited.add(node_id)
                rec_stack.add(node_id)
                path.append(node_id)
                
                # Visit neighbors
                for neighbor in graph.adjacency_list.get(node_id, set()):
                    dfs(neighbor)
                
                path.pop()
                rec_stack.remove(node_id)
            
            # Run DFS from each node
            for node_id in graph.nodes:
                if node_id not in visited:
                    dfs(node_id)
            
            return cycles
            
        except Exception as e:
            raise GraphError(f"Failed to find cycles: {str(e)}")
    
    def get_connected_components(self, graph: Graph) -> List[Set[str]]:
        """Get connected components of the graph."""
        try:
            components = []
            visited = set()
            
            def bfs(start_node: str) -> Set[str]:
                component = set()
                queue = [start_node]
                visited.add(start_node)
                
                while queue:
                    current = queue.pop(0)
                    component.add(current)
                    
                    for neighbor in graph.adjacency_list.get(current, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                return component
            
            # Find all components
            for node_id in graph.nodes:
                if node_id not in visited:
                    component = bfs(node_id)
                    components.append(component)
            
            return components
            
        except Exception as e:
            raise GraphError(f"Failed to get connected components: {str(e)}")
    
    def calculate_graph_density(self, graph: Graph) -> float:
        """Calculate graph density."""
        try:
            num_nodes = len(graph.nodes)
            num_edges = len(graph.edges)
            
            if num_nodes < 2:
                return 0.0
            
            # For undirected graph: max_edges = n * (n-1) / 2
            # For directed graph: max_edges = n * (n-1)
            is_directed = graph.metadata.get('is_directed', False)
            max_edges = num_nodes * (num_nodes - 1)
            if not is_directed:
                max_edges //= 2
            
            return num_edges / max_edges if max_edges > 0 else 0.0
            
        except Exception as e:
            raise GraphError(f"Failed to calculate graph density: {str(e)}")


class IncrementalGraphBuilder(GraphBuilder):
    """Graph builder with incremental updates."""
    
    def __init__(self) -> None:
        """Initialize incremental graph builder."""
        super().__init__()
        self.node_versions = {}
        self.edge_versions = {}
    
    def update_graph_incremental(self, graph: Graph, added_nodes: List[MemoryUnit],
                               removed_node_ids: List[str], added_edges: List[Relationship],
                               removed_edge_ids: List[str]) -> Graph:
        """Update graph incrementally."""
        try:
            # Remove old nodes
            for node_id in removed_node_ids:
                self._remove_node_from_graph(graph, node_id)
            
            # Remove old edges
            for edge_id in removed_edge_ids:
                self._remove_edge_from_graph(graph, edge_id)
            
            # Add new nodes
            for node in added_nodes:
                if node.id not in graph.nodes:
                    graph.nodes[node.id] = node
                    if node.id not in graph.adjacency_list:
                        graph.adjacency_list[node.id] = set()
            
            # Add new edges
            for edge in added_edges:
                if edge.source_id in graph.nodes and edge.target_id in graph.nodes:
                    graph.edges.append(edge)
                    graph.adjacency_list[edge.source_id].add(edge.target_id)
            
            # Update timestamp
            graph.updated_at = datetime.utcnow()
            
            return graph
            
        except Exception as e:
            raise GraphError(f"Failed to update graph incrementally: {str(e)}")
    
    def _remove_node_from_graph(self, graph: Graph, node_id: str) -> None:
        """Remove node from graph."""
        if node_id in graph.nodes:
            del graph.nodes[node_id]
        
        if node_id in graph.adjacency_list:
            del graph.adjacency_list[node_id]
        
        # Remove edges connected to this node
        graph.edges = [edge for edge in graph.edges 
                      if edge.source_id != node_id and edge.target_id != node_id]
        
        # Remove from adjacency lists of other nodes
        for neighbors in graph.adjacency_list.values():
            neighbors.discard(node_id)
    
    def _remove_edge_from_graph(self, graph: Graph, edge_id: str) -> None:
        """Remove edge from graph."""
        # Find and remove edge by ID
        for i, edge in enumerate(graph.edges):
            if edge.id == edge_id:
                removed_edge = graph.edges.pop(i)
                
                # Remove from adjacency list
                if removed_edge.source_id in graph.adjacency_list:
                    graph.adjacency_list[removed_edge.source_id].discard(removed_edge.target_id)
                
                break
