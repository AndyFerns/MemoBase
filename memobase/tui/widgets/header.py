"""
Header widget for TUI.

Displays: project name, stats (file count, etc.)
"""

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from memobase.tui.state import TUIState


class Header(Widget):
    """Header widget displaying project info and stats."""
    
    DEFAULT_CSS = """
    Header {
        background: $primary-darken-2;
        color: $text;
        height: 3;
        dock: top;
        content-align: center middle;
    }
    
    Header #project-name {
        width: auto;
        text-style: bold;
    }
    
    Header #stats {
        width: auto;
        text-style: dim;
    }
    """
    
    def __init__(self, state: TUIState) -> None:
        """Initialize header.
        
        Args:
            state: TUI state manager
        """
        super().__init__()
        self.state = state
    
    def compose(self):
        """Compose header content."""
        from textual.widgets import Static
        from textual.containers import Horizontal
        
        # Project name
        yield Static("MemoBase", id="project-name")
        
        # Stats
        stats_text = self._format_stats()
        yield Static(stats_text, id="stats")
    
    def _format_stats(self) -> str:
        """Format stats string."""
        stats = []
        
        # File count
        file_count = len(self.state.file_tree_data)
        stats.append(f"Files: {file_count}")
        
        # Current mode
        stats.append(f"Mode: {self.state.current_mode.upper()}")
        
        # Query count
        if self.state.query_history:
            stats.append(f"Queries: {len(self.state.query_history)}")
        
        return " | ".join(stats)
    
    def refresh_stats(self) -> None:
        """Refresh stats display."""
        stats_widget = self.query_one("#stats", Static)
        if stats_widget:
            stats_widget.update(self._format_stats())
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.set_interval(1.0, self.refresh_stats)
