"""
Graph analyzer module for MemoBase.

Handles code relationship graph analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from memobase.core.models import Config, Graph
from memobase.graph.analyzer import GraphAnalyzer as CoreGraphAnalyzer
from memobase.graph.traversal import GraphTraversal
from memobase.storage.file_storage import FileStorage


class GraphAnalyzer:
    """Handles graph analysis for the codebase."""
    
    def __init__(self, config: Config) -> None:
        """Initialize graph analyzer.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.storage = FileStorage(config.repo_path / config.storage_path)
    
    def analyze_symbol_relationships(self, symbol: str, depth: int = 3) -> Dict[str, Any]:
        """Analyze relationships for a specific symbol.
        
        Args:
            symbol: Symbol name to analyze
            depth: Graph traversal depth
            
        Returns:
            Graph analysis results
        """
        # Load graph
        graph_data = self.storage.load("graph/main")
        
        if not graph_data:
            return {
                'symbol': symbol,
                'nodes': [],
                'edges': [],
                'text_output': f"No graph data found. Run 'memobase build' first.",
                'dot_output': '',
            }
        
        graph = Graph(**graph_data)
        
        # Find symbol node
        symbol_node = None
        for node_id, node in graph.nodes.items():
            if hasattr(node, 'name') and node.name == symbol:
                symbol_node = node_id
                break
        
        if not symbol_node:
            return {
                'symbol': symbol,
                'nodes': [],
                'edges': [],
                'text_output': f"Symbol '{symbol}' not found in graph.",
                'dot_output': '',
            }
        
        # Traverse graph
        traversal = GraphTraversal(graph)
        neighbors = traversal.get_neighbors(symbol_node, max_depth=depth)
        
        # Build output
        nodes = [{'id': nid, 'name': graph.nodes.get(nid, {}).get('name', nid)} 
                 for nid in neighbors if nid in graph.nodes]
        
        edges = [e for e in graph.edges 
                 if e.source_id in neighbors and e.target_id in neighbors]
        
        text_output = self._format_graph_text(symbol, nodes, edges)
        dot_output = self._format_graph_dot(nodes, edges)
        
        return {
            'symbol': symbol,
            'nodes': nodes,
            'edges': [{'source': e.source_id, 'target': e.target_id, 'type': e.relation_type} 
                      for e in edges],
            'text_output': text_output,
            'dot_output': dot_output,
        }
    
    def analyze_overall_graph(self, depth: int = 3) -> Dict[str, Any]:
        """Analyze the overall code graph.
        
        Args:
            depth: Graph traversal depth
            
        Returns:
            Graph analysis results
        """
        # Load graph
        graph_data = self.storage.load("graph/main")
        
        if not graph_data:
            return {
                'nodes': [],
                'edges': [],
                'text_output': "No graph data found. Run 'memobase build' first.",
                'dot_output': '',
            }
        
        graph = Graph(**graph_data)
        
        # Analyze with core analyzer
        analyzer = CoreGraphAnalyzer(graph)
        properties = analyzer.analyze_graph_properties()
        
        # Build summary
        text_output = f"""Graph Analysis
==============

Nodes: {properties.get('node_count', 0)}
Edges: {properties.get('edge_count', 0)}
Density: {properties.get('density', 0):.3f}

Top Connected Nodes:
"""
        
        # Get top nodes by degree
        degrees = [(nid, len(graph.adjacency_list.get(nid, []))) 
                   for nid in graph.nodes.keys()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        
        for nid, degree in degrees[:10]:
            name = graph.nodes.get(nid, {}).get('name', nid)
            text_output += f"  {name}: {degree} connections\n"
        
        dot_output = self._format_graph_dot(
            [{'id': nid, 'name': graph.nodes.get(nid, {}).get('name', nid)} 
             for nid in list(graph.nodes.keys())[:50]],  # Limit for performance
            graph.edges[:100]
        )
        
        return {
            'nodes': list(graph.nodes.keys()),
            'edges': [{'source': e.source_id, 'target': e.target_id, 'type': e.relation_type} 
                      for e in graph.edges[:100]],
            'text_output': text_output,
            'dot_output': dot_output,
            'properties': properties,
        }
    
    def _format_graph_text(self, symbol: str, nodes: List[Dict], edges: List) -> str:
        """Format graph as text output."""
        lines = [f"Dependencies for {symbol}:", ""]
        
        for node in nodes[:20]:  # Limit for display
            lines.append(f"  → {node['name']}")
        
        if len(nodes) > 20:
            lines.append(f"  ... and {len(nodes) - 20} more")
        
        return "\n".join(lines)
    
    def _format_graph_dot(self, nodes: List[Dict], edges: List) -> str:
        """Format graph as DOT output."""
        lines = ["digraph memobase {"]
        
        for node in nodes:
            name = node.get('name', node['id']).replace('"', '\\"')
            lines.append(f'  "{node["id"]}" [label="{name}"];')
        
        for edge in edges:
            lines.append(f'  "{edge.source_id}" -> "{edge.target_id}";')
        
        lines.append("}")
        
        return "\n".join(lines)
