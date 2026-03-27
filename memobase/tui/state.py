"""
Global state manager for TUI.

SINGLE SOURCE OF TRUTH - NO direct mutation outside state manager.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from memobase.core.models import Findings, Graph, Index, MemoryUnit, Response


@dataclass
class TUIState:
    """Global state for TUI - SINGLE SOURCE OF TRUTH."""
    
    # Context for reactive system
    _context: Optional[Any] = field(default=None, init=False)
    
    # Navigation state
    current_file: Optional[str] = None
    current_mode: str = "memory"  # memory, graph, analysis, query
    selected_node: Optional[str] = None
    
    # Data cache
    file_tree_data: List[Dict[str, Any]] = field(default_factory=list)
    current_memory_unit: Optional[MemoryUnit] = None
    current_graph_subset: Optional[Graph] = None
    current_analysis_results: List[Findings] = field(default_factory=list)
    current_query_response: Optional[Response] = None
    
    # Query state
    query_history: List[str] = field(default_factory=list)
    current_query: str = ""
    
    # Graph context
    graph_context: Dict[str, Any] = field(default_factory=dict)
    graph_depth: int = 3
    graph_center: Optional[str] = None
    
    # UI state
    verbosity: int = 1  # 0=quiet, 1=normal, 2=verbose, 3=debug
    status_message: str = "Ready"
    is_loading: bool = False
    command_mode: bool = False
    query_mode: bool = False
    
    # View state
    file_tree_expanded: set = field(default_factory=set)
    scroll_position: int = 0
    
    def set_file(self, file_path: str) -> None:
        """Set current file - controlled mutation."""
        self.current_file = file_path
    
    def set_mode(self, mode: str) -> None:
        """Set current mode - controlled mutation."""
        valid_modes = ["memory", "graph", "analysis", "query"]
        if mode in valid_modes:
            self.current_mode = mode
    
    def add_to_query_history(self, query: str) -> None:
        """Add query to history."""
        self.query_history.append(query)
        # Keep only last 100 queries
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
    
    def set_verbosity(self, level: int) -> None:
        """Set verbosity level (0-3)."""
        self.verbosity = max(0, min(3, level))
    
    def set_status(self, message: str) -> None:
        """Set status message."""
        self.status_message = message
    
    def set_loading(self, loading: bool) -> None:
        """Set loading state."""
        self.is_loading = loading
    
    def enter_command_mode(self) -> None:
        """Enter command mode."""
        self.command_mode = True
        self.query_mode = False
    
    def enter_query_mode(self) -> None:
        """Enter query mode."""
        self.query_mode = True
        self.command_mode = False
    
    def exit_input_mode(self) -> None:
        """Exit input mode."""
        self.command_mode = False
        self.query_mode = False
    
    def toggle_file_tree_node(self, node_id: str) -> None:
        """Toggle file tree node expansion."""
        if node_id in self.file_tree_expanded:
            self.file_tree_expanded.remove(node_id)
        else:
            self.file_tree_expanded.add(node_id)
    
    def set_memory_unit(self, unit: Optional[MemoryUnit]) -> None:
        """Set current memory unit."""
        self.current_memory_unit = unit
    
    def set_graph_subset(self, graph: Optional[Graph]) -> None:
        """Set current graph subset."""
        self.current_graph_subset = graph
    
    def set_analysis_results(self, findings: List[Findings]) -> None:
        """Set analysis results."""
        self.current_analysis_results = findings
    
    def set_query_response(self, response: Optional[Response]) -> None:
        """Set query response."""
        self.current_query_response = response
    
    def set_graph_context(self, **kwargs) -> None:
        """Update graph context."""
        self.graph_context.update(kwargs)
    
    def clear_graph_context(self) -> None:
        """Clear graph context."""
        self.graph_context.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "current_file": self.current_file,
            "current_mode": self.current_mode,
            "verbosity": self.verbosity,
            "status_message": self.status_message,
            "is_loading": self.is_loading,
            "query_count": len(self.query_history),
            "has_memory_unit": self.current_memory_unit is not None,
            "has_graph": self.current_graph_subset is not None,
            "has_analysis": len(self.current_analysis_results) > 0,
            "has_query_response": self.current_query_response is not None,
        }
