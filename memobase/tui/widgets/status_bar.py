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
        background: $surface;
        border: solid $primary;
        padding: 0 1;
        height: 1;
    }
    
    StatusBar > Static {
        margin: 0 1;
    }
    
    #mode {
        color: $accent;
    }
    
    #verbosity {
        color: $success;
    }
    
    #message {
        color: $text;
    }
    
    #loading {
        color: $warning;
    }
    """
    
    # Reactive properties
    current_mode: reactive[str] = reactive("memory")
    verbosity: reactive[int] = reactive(1)
    status_message: reactive[str] = reactive("Ready")
    is_loading: reactive[bool] = reactive(False)
    
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
        yield Static(self.status_message, id="message")
        yield Static(self._format_loading(), id="loading")
    
    def _format_mode(self) -> str:
        """Format mode display."""
        return f"M:{self.current_mode.upper()}"
    
    def _format_verbosity(self) -> str:
        """Format verbosity display."""
        levels = ["Q", "N", "V", "D"]
        return f"V:{levels[self.verbosity]}"
    
    def _format_loading(self) -> str:
        """Format loading indicator."""
        if self.is_loading:
            return "◐"
        return ""
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Initialize from state
        self.current_mode = self.state.current_mode
        self.verbosity = self.state.verbosity
        self.status_message = self.state.status_message
        self.is_loading = self.state.is_loading
        
        # Watch our own reactive properties
        self.watch(self, "current_mode", self._update_mode)
        self.watch(self, "verbosity", self._update_verbosity)
        self.watch(self, "status_message", self._update_message)
        self.watch(self, "is_loading", self._update_loading)
        
        # Animate loading indicator
        self.set_interval(0.1, self._animate_loading)
    
    def _update_mode(self, old_value: str = None, new_value: str = None) -> None:
        """Update mode display."""
        mode_widget = self.query_one("#mode", Static)
        mode_widget.update(self._format_mode())
    
    def _update_verbosity(self, old_value: int = None, new_value: int = None) -> None:
        """Update verbosity display."""
        verbosity_widget = self.query_one("#verbosity", Static)
        verbosity_widget.update(self._format_verbosity())
    
    def _update_message(self, old_value: str = None, new_value: str = None) -> None:
        """Update message display."""
        message_widget = self.query_one("#message", Static)
        message_widget.update(self.status_message)
    
    def _update_loading(self, old_value: bool = None, new_value: bool = None) -> None:
        """Update loading indicator."""
        loading_widget = self.query_one("#loading", Static)
        loading_widget.update(self._format_loading())
    
    def _animate_loading(self) -> None:
        """Animate loading spinner."""
        if not self.is_loading:
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
