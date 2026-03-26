"""
Graph analyzer implementation.
"""

from __future__ import annotations

import math
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

from memobase.core.exceptions import GraphError
from memobase.core.models import Graph, RelationType


class GraphAnalyzer:
    """Advanced graph analysis algorithms."""
    
    def __init__(self, graph: Graph) -> None:
        """Initialize graph analyzer.
        
        Args:
            graph: Graph to analyze
        """
        self.graph = graph
    
    def calculate_degree_centrality(self) -> Dict[str, float]:
        """Calculate degree centrality for all nodes."""
        try:
            centrality = {}
            num_nodes = len(self.graph.nodes)
            
            if num_nodes == 0:
                return centrality
            
            for node_id in self.graph.nodes:
                # Degree is number of connections
                degree = len(self.graph.adjacency_list.get(node_id, set()))
                
                # Normalize by maximum possible degree (n-1)
                centrality[node_id] = degree / (num_nodes - 1) if num_nodes > 1 else 0.0
            
            return centrality
            
        except Exception as e:
            raise GraphError(f"Failed to calculate degree centrality: {str(e)}")
    
    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """Calculate betweenness centrality using Brandes' algorithm."""
        try:
            centrality = {node_id: 0.0 for node_id in self.graph.nodes}
            
            for source in self.graph.nodes:
                # Single-source shortest paths
                stack = []
                paths = {node_id: [] for node_id in self.graph.nodes}
                sigma = {node_id: 0 for node_id in self.graph.nodes}
                distance = {node_id: -1 for node_id in self.graph.nodes}
                
                # BFS from source
                queue = []
                distance[source] = 0
                sigma[source] = 1
                queue.append(source)
                
                while queue:
                    current = queue.pop(0)
                    stack.append(current)
                    
                    for neighbor in self.graph.adjacency_list.get(current, set()):
                        if distance[neighbor] == -1:  # Not visited
                            distance[neighbor] = distance[current] + 1
                            queue.append(neighbor)
                            sigma[neighbor] = sigma[current]
                            paths[neighbor].append(current)
                        elif distance[neighbor] == distance[current] + 1:
                            sigma[neighbor] += sigma[current]
                            paths[neighbor].append(current)
                
                # Dependency accumulation
                delta = {node_id: 0.0 for node_id in self.graph.nodes}
                
                while stack:
                    current = stack.pop()
                    for predecessor in paths[current]:
                        delta[predecesser] += (sigma[predecessor] / sigma[current]) * (1 + delta[current])
                    
                    if current != source:
                        centrality[current] += delta[current]
            
            # Normalize
            num_nodes = len(self.graph.nodes)
            if num_nodes > 2:
                scale = 1.0 / ((num_nodes - 1) * (num_nodes - 2))
                for node_id in centrality:
                    centrality[node_id] *= scale
            
            return centrality
            
        except Exception as e:
            raise GraphError(f"Failed to calculate betweenness centrality: {str(e)}")
    
    def calculate_closeness_centrality(self) -> Dict[str, float]:
        """Calculate closeness centrality for all nodes."""
        try:
            centrality = {}
            num_nodes = len(self.graph.nodes)
            
            if num_nodes == 0:
                return centrality
            
            for node_id in self.graph.nodes:
                # Calculate shortest paths from this node
                distances = self._shortest_path_distances(node_id)
                
                # Sum of distances to all other nodes
                total_distance = sum(distances.values())
                
                # Closeness centrality (normalized)
                if total_distance > 0 and num_nodes > 1:
                    centrality[node_id] = (num_nodes - 1) / total_distance
                else:
                    centrality[node_id] = 0.0
            
            return centrality
            
        except Exception as e:
            raise GraphError(f"Failed to calculate closeness centrality: {str(e)}")
    
    def calculate_eigenvector_centrality(self, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """Calculate eigenvector centrality using power iteration."""
        try:
            num_nodes = len(self.graph.nodes)
            if num_nodes == 0:
                return {}
            
            # Initialize centrality scores
            centrality = {node_id: 1.0 for node_id in self.graph.nodes}
            
            for iteration in range(max_iterations):
                new_centrality = {}
                
                for node_id in self.graph.nodes:
                    # Sum of centrality of neighbors
                    neighbor_sum = 0.0
                    for neighbor in self.graph.adjacency_list.get(node_id, set()):
                        neighbor_sum += centrality.get(neighbor, 0.0)
                    
                    new_centrality[node_id] = neighbor_sum
                
                # Normalize
                norm = math.sqrt(sum(score ** 2 for score in new_centrality.values()))
                if norm > 0:
                    for node_id in new_centrality:
                        new_centrality[node_id] /= norm
                
                # Check convergence
                max_diff = max(abs(new_centrality[node_id] - centrality[node_id]) 
                             for node_id in self.graph.nodes)
                
                centrality = new_centrality
                
                if max_diff < tolerance:
                    break
            
            return centrality
            
        except Exception as e:
            raise GraphError(f"Failed to calculate eigenvector centrality: {str(e)}")
    
    def calculate_pagerank(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """Calculate PageRank scores."""
        try:
            num_nodes = len(self.graph.nodes)
            if num_nodes == 0:
                return {}
            
            # Initialize PageRank scores
            pagerank = {node_id: 1.0 / num_nodes for node_id in self.graph.nodes}
            
            # Build adjacency list for outgoing edges
            outgoing_links = defaultdict(list)
            for edge in self.graph.edges:
                outgoing_links[edge.source_id].append(edge.target_id)
            
            for iteration in range(max_iterations):
                new_pagerank = {}
                
                for node_id in self.graph.nodes:
                    # PageRank from incoming links
                    rank_sum = 0.0
                    
                    # Find all nodes that link to this node
                    for edge in self.graph.edges:
                        if edge.target_id == node_id:
                            source_out_degree = len(outgoing_links[edge.source_id])
                            if source_out_degree > 0:
                                rank_sum += pagerank[edge.source_id] / source_out_degree
                    
                    # Apply PageRank formula
                    new_pagerank[node_id] = (1 - damping_factor) / num_nodes + damping_factor * rank_sum
                
                # Check convergence
                max_diff = max(abs(new_pagerank[node_id] - pagerank[node_id]) 
                             for node_id in self.graph.nodes)
                
                pagerank = new_pagerank
                
                if max_diff < tolerance:
                    break
            
            return pagerank
            
        except Exception as e:
            raise GraphError(f"Failed to calculate PageRank: {str(e)}")
    
    def find_communities(self, resolution: float = 1.0) -> Dict[str, int]:
        """Find communities using Louvain algorithm (simplified)."""
        try:
            # Simplified community detection based on modularity
            communities = {node_id: i for i, node_id in enumerate(self.graph.nodes)}
            
            # Iterative improvement (simplified)
            improved = True
            iteration = 0
            
            while improved and iteration < 10:
                improved = False
                iteration += 1
                
                for node_id in self.graph.nodes:
                    current_community = communities[node_id]
                    best_community = current_community
                    best_gain = 0.0
                    
                    # Calculate gain for moving to neighboring communities
                    neighbor_communities = set()
                    for neighbor in self.graph.adjacency_list.get(node_id, set()):
                        neighbor_communities.add(communities[neighbor])
                    
                    for community in neighbor_communities:
                        if community != current_community:
                            gain = self._calculate_modularity_gain(node_id, current_community, community, communities)
                            if gain > best_gain:
                                best_gain = gain
                                best_community = community
                    
                    if best_community != current_community:
                        communities[node_id] = best_community
                        improved = True
            
            return communities
            
        except Exception as e:
            raise GraphError(f"Failed to find communities: {str(e)}")
    
    def calculate_clustering_coefficient(self) -> Dict[str, float]:
        """Calculate clustering coefficient for each node."""
        try:
            clustering = {}
            
            for node_id in self.graph.nodes:
                neighbors = self.graph.adjacency_list.get(node_id, set())
                num_neighbors = len(neighbors)
                
                if num_neighbors < 2:
                    clustering[node_id] = 0.0
                    continue
                
                # Count edges between neighbors
                neighbor_edges = 0
                for neighbor1 in neighbors:
                    for neighbor2 in neighbors:
                        if neighbor1 != neighbor2:
                            if neighbor2 in self.graph.adjacency_list.get(neighbor1, set()):
                                neighbor_edges += 1
                
                # Each edge counted twice, so divide by 2
                neighbor_edges //= 2
                
                # Clustering coefficient
                possible_edges = num_neighbors * (num_neighbors - 1) // 2
                clustering[node_id] = neighbor_edges / possible_edges if possible_edges > 0 else 0.0
            
            return clustering
            
        except Exception as e:
            raise GraphError(f"Failed to calculate clustering coefficient: {str(e)}")
    
    def detect_bridges(self) -> List[Tuple[str, str]]:
        """Detect bridge edges (edges whose removal increases connected components)."""
        try:
            bridges = []
            
            for edge in self.graph.edges:
                # Temporarily remove edge
                self.graph.adjacency_list[edge.source_id].discard(edge.target_id)
                
                # Check if graph becomes more disconnected
                components = self._count_connected_components()
                
                # Restore edge
                self.graph.adjacency_list[edge.source_id].add(edge.target_id)
                
                # If components increased, it's a bridge
                original_components = len(self.find_connected_components())
                if components > original_components:
                    bridges.append((edge.source_id, edge.target_id))
            
            return bridges
            
        except Exception as e:
            raise GraphError(f"Failed to detect bridges: {str(e)}")
    
    def find_articulation_points(self) -> Set[str]:
        """Find articulation points (nodes whose removal increases connected components)."""
        try:
            articulation_points = set()
            
            for node_id in self.graph.nodes:
                # Temporarily remove node
                original_neighbors = self.graph.adjacency_list.get(node_id, set())
                self.graph.adjacency_list[node_id] = set()
                
                # Remove edges to/from this node
                for neighbor in original_neighbors:
                    self.graph.adjacency_list[neighbor].discard(node_id)
                
                # Check if graph becomes more disconnected
                components = self._count_connected_components()
                
                # Restore node and edges
                self.graph.adjacency_list[node_id] = original_neighbors
                for neighbor in original_neighbors:
                    self.graph.adjacency_list[neighbor].add(node_id)
                
                # If components increased, it's an articulation point
                original_components = len(self.find_connected_components())
                if components > original_components:
                    articulation_points.add(node_id)
            
            return articulation_points
            
        except Exception as e:
            raise GraphError(f"Failed to find articulation points: {str(e)}")
    
    def analyze_graph_properties(self) -> Dict[str, any]:
        """Comprehensive graph analysis."""
        try:
            properties = {}
            
            # Basic properties
            properties['num_nodes'] = len(self.graph.nodes)
            properties['num_edges'] = len(self.graph.edges)
            properties['density'] = self._calculate_density()
            properties['is_directed'] = self.graph.metadata.get('is_directed', False)
            
            # Degree statistics
            degrees = [len(self.graph.adjacency_list.get(node_id, set())) for node_id in self.graph.nodes]
            if degrees:
                properties['avg_degree'] = sum(degrees) / len(degrees)
                properties['max_degree'] = max(degrees)
                properties['min_degree'] = min(degrees)
            else:
                properties['avg_degree'] = 0.0
                properties['max_degree'] = 0
                properties['min_degree'] = 0
            
            # Connected components
            components = self.find_connected_components()
            properties['num_components'] = len(components)
            properties['largest_component_size'] = max(len(comp) for comp in components) if components else 0
            
            # Centrality measures
            properties['degree_centrality'] = self.calculate_degree_centrality()
            properties['betweenness_centrality'] = self.calculate_betweenness_centrality()
            properties['closeness_centrality'] = self.calculate_closeness_centrality()
            
            # Clustering
            properties['clustering_coefficient'] = self.calculate_clustering_coefficient()
            if properties['clustering_coefficient']:
                properties['avg_clustering'] = sum(properties['clustering_coefficient'].values()) / len(properties['clustering_coefficient'])
            else:
                properties['avg_clustering'] = 0.0
            
            # Communities
            communities = self.find_communities()
            properties['num_communities'] = len(set(communities.values()))
            
            return properties
            
        except Exception as e:
            raise GraphError(f"Failed to analyze graph properties: {str(e)}")
    
    def _shortest_path_distances(self, source: str) -> Dict[str, int]:
        """Calculate shortest path distances from source using BFS."""
        distances = {source: 0}
        queue = [source]
        visited = {source}
        
        while queue:
            current = queue.pop(0)
            current_distance = distances[current]
            
            for neighbor in self.graph.adjacency_list.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    distances[neighbor] = current_distance + 1
                    queue.append(neighbor)
        
        return distances
    
    def _calculate_density(self) -> float:
        """Calculate graph density."""
        num_nodes = len(self.graph.nodes)
        num_edges = len(self.graph.edges)
        
        if num_nodes < 2:
            return 0.0
        
        is_directed = self.graph.metadata.get('is_directed', False)
        max_edges = num_nodes * (num_nodes - 1)
        if not is_directed:
            max_edges //= 2
        
        return num_edges / max_edges if max_edges > 0 else 0.0
    
    def _calculate_modularity_gain(self, node_id: str, old_community: int, new_community: int, communities: Dict[str, int]) -> float:
        """Calculate modularity gain for moving node to new community (simplified)."""
        # Simplified modularity calculation
        old_neighbors = sum(1 for neighbor in self.graph.adjacency_list.get(node_id, set()) 
                          if communities[neighbor] == old_community)
        new_neighbors = sum(1 for neighbor in self.graph.adjacency_list.get(node_id, set()) 
                          if communities[neighbor] == new_community)
        
        return (new_neighbors - old_neighbors) / len(self.graph.adjacency_list.get(node_id, set()))
    
    def _count_connected_components(self) -> int:
        """Count number of connected components."""
        visited = set()
        count = 0
        
        for node_id in self.graph.nodes:
            if node_id not in visited:
                count += 1
                queue = [node_id]
                visited.add(node_id)
                
                while queue:
                    current = queue.pop(0)
                    for neighbor in self.graph.adjacency_list.get(current, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
        
        return count
    
    def find_connected_components(self) -> List[Set[str]]:
        """Find connected components."""
        visited = set()
        components = []
        
        for node_id in self.graph.nodes:
            if node_id not in visited:
                component = set()
                queue = [node_id]
                visited.add(node_id)
                
                while queue:
                    current = queue.pop(0)
                    component.add(current)
                    
                    for neighbor in self.graph.adjacency_list.get(current, set()):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                
                components.append(component)
        
        return components
