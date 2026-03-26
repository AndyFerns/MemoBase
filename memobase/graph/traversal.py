"""
Graph traversal implementation.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import GraphError
from memobase.core.models import Graph, Relationship, RelationType


class GraphTraversal:
    """Advanced graph traversal algorithms."""
    
    def __init__(self, graph: Graph) -> None:
        """Initialize graph traversal.
        
        Args:
            graph: Graph to traverse
        """
        self.graph = graph
    
    def bfs(self, start_node: str, max_depth: int = None, relation_filter: Set[RelationType] = None) -> Dict[str, int]:
        """Breadth-first search traversal.
        
        Args:
            start_node: Starting node ID
            max_depth: Maximum traversal depth
            relation_filter: Optional filter for relation types
            
        Returns:
            Dictionary mapping node_id -> distance from start
        """
        try:
            if start_node not in self.graph.nodes:
                return {}
            
            distances = {start_node: 0}
            queue = deque([start_node])
            visited = {start_node}
            
            while queue:
                current = queue.popleft()
                current_distance = distances[current]
                
                # Check depth limit
                if max_depth is not None and current_distance >= max_depth:
                    continue
                
                # Get neighbors
                neighbors = self._get_filtered_neighbors(current, relation_filter)
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        distances[neighbor] = current_distance + 1
                        queue.append(neighbor)
            
            return distances
            
        except Exception as e:
            raise GraphError(f"BFS traversal failed: {str(e)}")
    
    def dfs(self, start_node: str, max_depth: int = None, relation_filter: Set[RelationType] = None) -> List[str]:
        """Depth-first search traversal.
        
        Args:
            start_node: Starting node ID
            max_depth: Maximum traversal depth
            relation_filter: Optional filter for relation types
            
        Returns:
            List of visited nodes in DFS order
        """
        try:
            if start_node not in self.graph.nodes:
                return []
            
            visited = []
            stack = [(start_node, 0)]
            visited_set = {start_node}
            
            while stack:
                current, depth = stack.pop()
                visited.append(current)
                
                # Check depth limit
                if max_depth is not None and depth >= max_depth:
                    continue
                
                # Get neighbors
                neighbors = self._get_filtered_neighbors(current, relation_filter)
                
                # Add neighbors to stack (reverse order for consistent traversal)
                for neighbor in reversed(list(neighbors)):
                    if neighbor not in visited_set:
                        visited_set.add(neighbor)
                        stack.append((neighbor, depth + 1))
            
            return visited
            
        except Exception as e:
            raise GraphError(f"DFS traversal failed: {str(e)}")
    
    def dijkstra(self, start_node: str, end_node: str = None) -> Dict[str, float]:
        """Dijkstra's shortest path algorithm.
        
        Args:
            start_node: Starting node ID
            end_node: Optional target node (if provided, returns path to this node)
            
        Returns:
            Dictionary mapping node_id -> shortest distance from start
        """
        try:
            if start_node not in self.graph.nodes:
                return {}
            
            import heapq
            
            distances = {start_node: 0.0}
            previous = {}
            heap = [(0.0, start_node)]
            visited = set()
            
            while heap:
                current_distance, current = heapq.heappop(heap)
                
                if current in visited:
                    continue
                
                visited.add(current)
                
                # Early exit if we reached the target
                if end_node is not None and current == end_node:
                    break
                
                # Get neighbors with edge weights
                neighbors = self._get_weighted_neighbors(current)
                
                for neighbor, weight in neighbors.items():
                    if neighbor in visited:
                        continue
                    
                    distance = current_distance + (1.0 - weight)  # Convert weight to distance
                    
                    if neighbor not in distances or distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
                        heapq.heappush(heap, (distance, neighbor))
            
            return distances
            
        except Exception as e:
            raise GraphError(f"Dijkstra traversal failed: {str(e)}")
    
    def a_star(self, start_node: str, end_node: str, heuristic_func) -> List[str]:
        """A* pathfinding algorithm.
        
        Args:
            start_node: Starting node ID
            end_node: Target node ID
            heuristic_func: Function to estimate distance between nodes
            
        Returns:
            List of node IDs forming the shortest path
        """
        try:
            if start_node not in self.graph.nodes or end_node not in self.graph.nodes:
                return []
            
            import heapq
            
            open_set = [(0.0, start_node)]
            came_from = {}
            g_score = {start_node: 0.0}
            f_score = {start_node: heuristic_func(start_node, end_node)}
            
            while open_set:
                current_f, current = heapq.heappop(open_set)
                
                if current == end_node:
                    # Reconstruct path
                    path = []
                    while current in came_from:
                        path.append(current)
                        current = came_from[current]
                    path.append(start_node)
                    return list(reversed(path))
                
                # Get neighbors with edge weights
                neighbors = self._get_weighted_neighbors(current)
                
                for neighbor, weight in neighbors.items():
                    tentative_g = g_score[current] + (1.0 - weight)
                    
                    if neighbor not in g_score or tentative_g < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + heuristic_func(neighbor, end_node)
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
            
            return []
            
        except Exception as e:
            raise GraphError(f"A* traversal failed: {str(e)}")
    
    def find_all_paths(self, start_node: str, end_node: str, max_depth: int = 5) -> List[List[str]]:
        """Find all paths between two nodes.
        
        Args:
            start_node: Starting node ID
            end_node: Target node ID
            max_depth: Maximum path length
            
        Returns:
            List of all paths (each path is a list of node IDs)
        """
        try:
            if start_node not in self.graph.nodes or end_node not in self.graph.nodes:
                return []
            
            all_paths = []
            
            def dfs(current: str, path: List[str], visited: Set[str]):
                if len(path) > max_depth:
                    return
                
                if current == end_node:
                    all_paths.append(path.copy())
                    return
                
                neighbors = self.graph.adjacency_list.get(current, set())
                
                for neighbor in neighbors:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        path.append(neighbor)
                        dfs(neighbor, path, visited)
                        path.pop()
                        visited.remove(neighbor)
            
            dfs(start_node, [start_node], {start_node})
            
            return all_paths
            
        except Exception as e:
            raise GraphError(f"Failed to find all paths: {str(e)}")
    
    def find_shortest_paths(self, start_node: str, max_distance: float = float('inf')) -> Dict[str, List[str]]:
        """Find shortest paths from start node to all reachable nodes.
        
        Args:
            start_node: Starting node ID
            max_distance: Maximum path distance
            
        Returns:
            Dictionary mapping target_node -> path list
        """
        try:
            if start_node not in self.graph.nodes:
                return {}
            
            # Use Dijkstra to find shortest distances
            distances = self.dijkstra(start_node)
            
            # Filter by max_distance
            filtered_distances = {node: dist for node, dist in distances.items() 
                                if dist <= max_distance}
            
            # Reconstruct paths
            paths = {}
            for target in filtered_distances:
                path = self._reconstruct_path(start_node, target)
                if path:
                    paths[target] = path
            
            return paths
            
        except Exception as e:
            raise GraphError(f"Failed to find shortest paths: {str(e)}")
    
    def find_weakly_connected_components(self) -> List[Set[str]]:
        """Find weakly connected components (for directed graphs)."""
        try:
            visited = set()
            components = []
            
            # Treat graph as undirected for connectivity
            undirected_adj = {}
            for node_id in self.graph.nodes:
                undirected_adj[node_id] = set()
            
            for edge in self.graph.edges:
                undirected_adj[edge.source_id].add(edge.target_id)
                undirected_adj[edge.target_id].add(edge.source_id)
            
            for node_id in self.graph.nodes:
                if node_id not in visited:
                    component = set()
                    queue = [node_id]
                    visited.add(node_id)
                    
                    while queue:
                        current = queue.pop(0)
                        component.add(current)
                        
                        for neighbor in undirected_adj[current]:
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append(neighbor)
                    
                    components.append(component)
            
            return components
            
        except Exception as e:
            raise GraphError(f"Failed to find weakly connected components: {str(e)}")
    
    def find_strongly_connected_components(self) -> List[Set[str]]:
        """Find strongly connected components (for directed graphs)."""
        try:
            # Kosaraju's algorithm
            visited = set()
            order = []
            
            # First pass: DFS to get finishing order
            def dfs_first(node: str):
                visited.add(node)
                for neighbor in self.graph.adjacency_list.get(node, set()):
                    if neighbor not in visited:
                        dfs_first(neighbor)
                order.append(node)
            
            for node_id in self.graph.nodes:
                if node_id not in visited:
                    dfs_first(node_id)
            
            # Build reverse graph
            reverse_adj = {}
            for node_id in self.graph.nodes:
                reverse_adj[node_id] = set()
            
            for edge in self.graph.edges:
                reverse_adj[edge.target_id].add(edge.source_id)
            
            # Second pass: DFS on reverse graph in reverse order
            visited.clear()
            components = []
            
            def dfs_second(node: str, component: Set[str]):
                visited.add(node)
                component.add(node)
                for neighbor in reverse_adj.get(node, set()):
                    if neighbor not in visited:
                        dfs_second(neighbor, component)
            
            for node_id in reversed(order):
                if node_id not in visited:
                    component = set()
                    dfs_second(node_id, component)
                    components.append(component)
            
            return components
            
        except Exception as e:
            raise GraphError(f"Failed to find strongly connected components: {str(e)}")
    
    def topological_sort(self) -> List[str]:
        """Topological sort for directed acyclic graphs."""
        try:
            # Kahn's algorithm
            in_degree = {node_id: 0 for node_id in self.graph.nodes}
            
            # Calculate in-degrees
            for edge in self.graph.edges:
                in_degree[edge.target_id] += 1
            
            # Queue of nodes with no incoming edges
            queue = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
            result = []
            
            while queue:
                current = queue.popleft()
                result.append(current)
                
                # Remove outgoing edges
                for neighbor in self.graph.adjacency_list.get(current, set()):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            
            # Check if graph has cycles
            if len(result) != len(self.graph.nodes):
                raise GraphError("Graph has cycles, topological sort not possible")
            
            return result
            
        except Exception as e:
            raise GraphError(f"Topological sort failed: {str(e)}")
    
    def _get_filtered_neighbors(self, node_id: str, relation_filter: Set[RelationType] = None) -> Set[str]:
        """Get neighbors filtered by relation type."""
        if relation_filter is None:
            return self.graph.adjacency_list.get(node_id, set())
        
        filtered_neighbors = set()
        
        for edge in self.graph.edges:
            if edge.source_id == node_id and edge.relation_type in relation_filter:
                filtered_neighbors.add(edge.target_id)
        
        return filtered_neighbors
    
    def _get_weighted_neighbors(self, node_id: str) -> Dict[str, float]:
        """Get neighbors with edge weights."""
        weighted_neighbors = {}
        
        for edge in self.graph.edges:
            if edge.source_id == node_id:
                weighted_neighbors[edge.target_id] = edge.weight
        
        return weighted_neighbors
    
    def _reconstruct_path(self, start_node: str, end_node: str) -> List[str]:
        """Reconstruct path from Dijkstra results."""
        # This is a simplified implementation
        # In practice, you'd store the previous nodes during Dijkstra
        path = []
        current = end_node
        
        while current != start_node:
            path.append(current)
            # Find predecessor (simplified)
            found = False
            for edge in self.graph.edges:
                if edge.target_id == current:
                    current = edge.source_id
                    found = True
                    break
            if not found:
                return []
        
        path.append(start_node)
        return list(reversed(path))


class BidirectionalTraversal(GraphTraversal):
    """Bidirectional graph traversal for performance optimization."""
    
    def bidirectional_bfs(self, start_node: str, end_node: str, max_depth: int = None) -> List[str]:
        """Bidirectional BFS to find shortest path."""
        try:
            if start_node not in self.graph.nodes or end_node not in self.graph.nodes:
                return []
            
            if start_node == end_node:
                return [start_node]
            
            # Forward search
            forward_distances = {start_node: 0}
            forward_queue = deque([start_node])
            forward_visited = {start_node}
            forward_parent = {}
            
            # Backward search
            backward_distances = {end_node: 0}
            backward_queue = deque([end_node])
            backward_visited = {end_node}
            backward_parent = {}
            
            meeting_node = None
            
            while forward_queue and backward_queue:
                # Forward step
                if forward_queue:
                    current = forward_queue.popleft()
                    current_distance = forward_distances[current]
                    
                    if max_depth is not None and current_distance >= max_depth:
                        continue
                    
                    neighbors = self.graph.adjacency_list.get(current, set())
                    
                    for neighbor in neighbors:
                        if neighbor not in forward_visited:
                            forward_visited.add(neighbor)
                            forward_distances[neighbor] = current_distance + 1
                            forward_parent[neighbor] = current
                            forward_queue.append(neighbor)
                            
                            # Check if backward search has visited this node
                            if neighbor in backward_visited:
                                meeting_node = neighbor
                                break
                
                if meeting_node:
                    break
                
                # Backward step
                if backward_queue:
                    current = backward_queue.popleft()
                    current_distance = backward_distances[current]
                    
                    if max_depth is not None and current_distance >= max_depth:
                        continue
                    
                    # Find incoming edges
                    incoming_neighbors = set()
                    for edge in self.graph.edges:
                        if edge.target_id == current:
                            incoming_neighbors.add(edge.source_id)
                    
                    for neighbor in incoming_neighbors:
                        if neighbor not in backward_visited:
                            backward_visited.add(neighbor)
                            backward_distances[neighbor] = current_distance + 1
                            backward_parent[neighbor] = current
                            backward_queue.append(neighbor)
                            
                            # Check if forward search has visited this node
                            if neighbor in forward_visited:
                                meeting_node = neighbor
                                break
                
                if meeting_node:
                    break
            
            if not meeting_node:
                return []
            
            # Reconstruct path
            path = []
            
            # Forward path
            current = meeting_node
            while current != start_node:
                path.append(current)
                current = forward_parent[current]
            path.append(start_node)
            path.reverse()
            
            # Backward path (excluding meeting node)
            current = meeting_node
            while current != end_node:
                current = backward_parent[current]
                path.append(current)
            
            return path
            
        except Exception as e:
            raise GraphError(f"Bidirectional BFS failed: {str(e)}")
