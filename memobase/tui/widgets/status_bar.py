"""
Status bar widget for TUI.

Displays: mode, verbosity, status messages
"""

from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from memobase.tui.state import TUIState


class StatusBar(Widget):
    """Status bar displaying mode, verbosity, and messages."""
    
    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        dock: bottom;
        background: $primary-darken-2;
        color: $text;
    }
    
    StatusBar #mode {
        width: auto;
        text-style: bold;
    }
    
    StatusBar #verbosity {
        width: auto;
        text-style: dim;
    }
    
    StatusBar #message {
        width: 1fr;
        text-align: center;
    }
    
    StatusBar #loading {
        width: auto;
        color: $warning;
    }
    """
    
    def __init__(self, state: TUIState, **kwargs) -> None:
        """Initialize status bar.
        
        Args:
            state: TUI state manager
        """
        super().__init__(**kwargs)
        self.state = state
    
    def compose(self):
        """Compose status bar."""
        yield Static(self._format_mode(), id="mode")
        yield Static(self._format_verbosity(), id="verbosity")
        yield Static(self.state.status_message, id="message")
        yield Static("", id="loading")
    
    def _format_mode(self) -> str:
        """Format mode string."""
        return f"[{self.state.current_mode.upper()}]"
    
    def _format_verbosity(self) -> str:
        """Format verbosity string."""
        levels = ["Q", "N", "V", "D"]
        return f"V:{levels[self.state.verbosity]}"
    
    def _format_loading(self) -> str:
        """Format loading indicator."""
        if self.state.is_loading:
            return "◐"
        return ""
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Watch for state changes
        self.watch(self.state, "current_mode", self._update_mode)
        self.watch(self.state, "verbosity", self._update_verbosity)
        self.watch(self.state, "status_message", self._update_message)
        self.watch(self.state, "is_loading", self._update_loading)
        
        # Animate loading indicator
        self.set_interval(0.1, self._animate_loading)
    
    def _update_mode(self) -> None:
        """Update mode display."""
        mode_widget = self.query_one("#mode", Static)
        mode_widget.update(self._format_mode())
    
    def _update_verbosity(self) -> None:
        """Update verbosity display."""
        verbosity_widget = self.query_one("#verbosity", Static)
        verbosity_widget.update(self._format_verbosity())
    
    def _update_message(self) -> None:
        """Update message display."""
        message_widget = self.query_one("#message", Static)
        message_widget.update(self.state.status_message)
    
    def _update_loading(self) -> None:
        """Update loading indicator."""
        loading_widget = self.query_one("#loading", Static)
        loading_widget.update(self._format_loading())
    
    def _animate_loading(self) -> None:
        """Animate loading spinner."""
        if not self.state.is_loading:
            return
        
        loading_widget = self.query_one("#loading", Static)
        current = loading_widget.renderable
        
        # Rotate spinner
        spinners = ["◐", "◓", "◑", "◒"]
        try:
            idx = spinners.index(current)
            next_spinner = spinners[(idx + 1) % len(spinners)]
        except ValueError:
            next_spinner = spinners[0]
        
        loading_widget.update(next_spinner)
