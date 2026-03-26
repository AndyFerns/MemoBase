"""
Graph view for TUI.

Input: Graph subset
Constraint: depth-limited rendering ONLY
"""

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from memobase.core.models import Graph


class GraphView(Widget):
    """View for displaying graph visualization."""
    
    DEFAULT_CSS = """
    GraphView {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    GraphView .node {
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }
    
    GraphView .edge {
        margin: 0 2;
        color: $text-disabled;
    }
    
    GraphView .highlight {
        background: $primary-darken-2;
    }
    """
    
    def __init__(self, graph: Graph, depth: int = 3, **kwargs) -> None:
        """Initialize graph view.
        
        Args:
            graph: Graph subset to display
            depth: Graph traversal depth limit
        """
        super().__init__(**kwargs)
        self.graph = graph
        self.depth = depth
    
    def compose(self):
        """Compose graph view."""
        # Graph info header
        yield Static(self._format_header(), classes="header")
        
        # Graph nodes (depth-limited)
        nodes_to_display = self._get_nodes_at_depth()
        
        for node_id in nodes_to_display[:50]:  # Limit to 50 nodes for performance
            yield Static(self._format_node(node_id), classes="node")
        
        if len(nodes_to_display) > 50:
            yield Static(f"... and {len(nodes_to_display) - 50} more nodes (max depth: {self.depth})")
    
    def _format_header(self) -> str:
        """Format graph header."""
        return f"[b]Graph View[/b] - {len(self.graph.nodes)} nodes, {len(self.graph.edges)} edges (depth: {self.depth})"
    
    def _get_nodes_at_depth(self) -> list:
        """Get nodes within depth limit."""
        # Start from center node or first node
        if self.graph.nodes:
            center = list(self.graph.nodes.keys())[0]
        else:
            return []
        
        # BFS to get nodes at each depth
        from collections import deque
        
        visited = {center: 0}
        queue = deque([center])
        nodes_at_depth = [center]
        
        while queue:
            current = queue.popleft()
            current_depth = visited[current]
            
            if current_depth >= self.depth:
                continue
            
            # Get neighbors
            neighbors = self.graph.adjacency_list.get(current, set())
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited[neighbor] = current_depth + 1
                    queue.append(neighbor)
                    nodes_at_depth.append(neighbor)
        
        return nodes_at_depth
    
    def _format_node(self, node_id: str) -> str:
        """Format a graph node."""
        node = self.graph.nodes.get(node_id)
        
        if not node:
            return f"[b]{node_id}[/b]"
        
        lines = [f"[b]{node_id}[/b]"]
        
        if node.symbol:
            lines.append(f"  Symbol: {node.symbol.name} ({node.symbol.symbol_type.value})")
        
        # Get outgoing edges
        outgoing = self.graph.adjacency_list.get(node_id, set())
        if outgoing:
            lines.append(f"  → {len(outgoing)} connections")
            
            # Show first few connections
            for target_id in list(outgoing)[:3]:
                lines.append(f"    → {target_id}")
            
            if len(outgoing) > 3:
                lines.append(f"    ... and {len(outgoing) - 3} more")
        
        return "\n".join(lines)


class CompactGraphView(GraphView):
    """Compact graph view for smaller displays."""
    
    DEFAULT_CSS = """
    CompactGraphView {
        width: 100%;
        height: 100%;
        padding: 0;
    }
    """
    
    def _format_node(self, node_id: str) -> str:
        """Format a graph node (compact)."""
        node = self.graph.nodes.get(node_id)
        
        if not node:
            return f"• {node_id}"
        
        if node.symbol:
            return f"• {node.symbol.name} ({node.symbol.symbol_type.value})"
        
        return f"• {node_id}"
