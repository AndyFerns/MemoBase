"""
Main panel widget for TUI.

Switches views based on current mode.
"""

from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget

from memobase.core.models import Response
from memobase.tui.controller import TUIController
from memobase.tui.state import TUIState
from memobase.tui.views.analysis_view import AnalysisView
from memobase.tui.views.graph_view import GraphView
from memobase.tui.views.memory_view import MemoryView
from memobase.tui.views.query_view import QueryView


class MainPanel(Widget):
    """Main panel that switches between views."""
    
    DEFAULT_CSS = """
    MainPanel {
        width: 100%;
        height: 100%;
        border: solid $primary;
        background: $surface;
    }
    """
    
    def __init__(self, state: TUIState, controller: TUIController, **kwargs) -> None:
        """Initialize main panel.
        
        Args:
            state: TUI state manager
            controller: TUI controller
        """
        super().__init__(**kwargs)
        self.state = state
        self.controller = controller
        
        # View instances
        self._memory_view: MemoryView | None = None
        self._graph_view: GraphView | None = None
        self._analysis_view: AnalysisView | None = None
        self._query_view: QueryView | None = None
    
    def compose(self):
        """Compose main panel with view container."""
        # Container for active view
        yield Vertical(id="view-container")
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Watch for mode changes
        self.watch(self.state, "current_mode", self._on_mode_changed)
        
        # Watch for data changes
        self.watch(self.state, "current_memory_unit", self._on_memory_changed)
        self.watch(self.state, "current_graph_subset", self._on_graph_changed)
        self.watch(self.state, "current_analysis_results", self._on_analysis_changed)
        self.watch(self.state, "current_query_response", self._on_query_changed)
        
        # Initialize with current mode
        self._render_current_view()
    
    def _on_mode_changed(self) -> None:
        """Handle mode change."""
        self._render_current_view()
    
    def _on_memory_changed(self) -> None:
        """Handle memory unit change."""
        if self.state.current_mode == "memory":
            self._render_current_view()
    
    def _on_graph_changed(self) -> None:
        """Handle graph change."""
        if self.state.current_mode == "graph":
            self._render_current_view()
    
    def _on_analysis_changed(self) -> None:
        """Handle analysis results change."""
        if self.state.current_mode == "analysis":
            self._render_current_view()
    
    def _on_query_changed(self) -> None:
        """Handle query response change."""
        if self.state.current_mode == "query":
            self._render_current_view()
    
    def _render_current_view(self) -> None:
        """Render current view based on mode."""
        mode = self.state.current_mode
        container = self.query_one("#view-container", Vertical)
        
        # Remove existing children
        container.remove_children()
        
        # Render appropriate view
        if mode == "memory":
            self._render_memory(container)
        elif mode == "graph":
            self._render_graph(container)
        elif mode == "analysis":
            self._render_analysis(container)
        elif mode == "query":
            self._render_query(container)
    
    def _render_memory(self, container: Vertical) -> None:
        """Render memory view.
        
        Args:
            container: Container to render into
        """
        from textual.widgets import Static
        
        if self.state.current_memory_unit:
            view = MemoryView(self.state.current_memory_unit)
            container.mount(view)
        else:
            container.mount(Static("No memory unit selected. Select a file from the tree."))
    
    def _render_graph(self, container: Vertical) -> None:
        """Render graph view.
        
        Args:
            container: Container to render into
        """
        from textual.widgets import Static
        
        if self.state.current_graph_subset:
            view = GraphView(
                self.state.current_graph_subset,
                self.state.graph_depth
            )
            container.mount(view)
        else:
            container.mount(Static("No graph data. Select a file and press 'g' for graph view."))
    
    def _render_analysis(self, container: Vertical) -> None:
        """Render analysis view.
        
        Args:
            container: Container to render into
        """
        view = AnalysisView(self.state.current_analysis_results)
        container.mount(view)
    
    def _render_query(self, container: Vertical) -> None:
        """Render query view.
        
        Args:
            container: Container to render into
        """
        if self.state.current_query_response:
            view = QueryView(self.state.current_query_response)
            container.mount(view)
        else:
            from textual.widgets import Static
            container.mount(Static("No query results. Press '/' to enter a query."))
    
    def show_query_results(self, response: Response) -> None:
        """Show query results.
        
        Args:
            response: Query response to display
        """
        self.state.set_query_response(response)
        self.state.set_mode("query")
        self._render_current_view()
