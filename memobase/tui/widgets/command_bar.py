"""
Command bar widget for TUI.

Handles: / query input, : command mode
"""

from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static

from memobase.tui.actions import Actions
from memobase.tui.state import TUIState


class CommandBar(Widget):
    """Command bar for query and command input."""
    
    DEFAULT_CSS = """
    CommandBar {
        height: 1;
        dock: bottom;
        background: $surface-darken-1;
    }
    
    CommandBar #prompt {
        width: auto;
        color: $primary;
        text-style: bold;
    }
    
    CommandBar Input {
        width: 1fr;
        background: $surface;
    }
    
    CommandBar.hidden {
        display: none;
    }
    """
    
    def __init__(self, state: TUIState, actions: Actions, **kwargs) -> None:
        """Initialize command bar.
        
        Args:
            state: TUI state manager
            actions: Actions handler
        """
        super().__init__(**kwargs)
        self.state = state
        self.actions = actions
        self._input_mode: str | None = None
    
    def compose(self):
        """Compose command bar."""
        # Initially hidden
        yield Static(":", id="prompt")
        yield Input(placeholder="Enter command...", id="command-input")
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        # Watch for state changes
        self.watch(self.state, "command_mode", self._on_command_mode_changed)
        self.watch(self.state, "query_mode", self._on_query_mode_changed)
        
        # Hide initially
        self.add_class("hidden")
    
    def _on_command_mode_changed(self) -> None:
        """Handle command mode change."""
        if self.state.command_mode:
            self._show_command_mode()
        elif not self.state.query_mode:
            self._hide()
    
    def _on_query_mode_changed(self) -> None:
        """Handle query mode change."""
        if self.state.query_mode:
            self._show_query_mode()
        elif not self.state.command_mode:
            self._hide()
    
    def _show_command_mode(self) -> None:
        """Show command bar in command mode."""
        self._input_mode = "command"
        self.remove_class("hidden")
        
        prompt = self.query_one("#prompt", Static)
        prompt.update(":")
        
        input_widget = self.query_one("#command-input", Input)
        input_widget.placeholder = "Enter command (quit, help, etc.)..."
        input_widget.value = ""
        input_widget.focus()
    
    def _show_query_mode(self) -> None:
        """Show command bar in query mode."""
        self._input_mode = "query"
        self.remove_class("hidden")
        
        prompt = self.query_one("#prompt", Static)
        prompt.update("/")
        
        input_widget = self.query_one("#command-input", Input)
        input_widget.placeholder = "Search codebase..."
        input_widget.value = ""
        input_widget.focus()
    
    def _hide(self) -> None:
        """Hide command bar."""
        self._input_mode = None
        self.add_class("hidden")
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        value = event.value
        
        if self._input_mode == "command":
            # Execute command
            self.actions.execute_command(value)
        elif self._input_mode == "query":
            # Execute query
            import asyncio
            asyncio.create_task(self.actions.execute_query(value))
        
        # Clear and hide
        event.input.value = ""
        self._hide()
    
    def on_key(self, event) -> None:
        """Handle key events."""
        if event.key == "escape":
            # Cancel input
            self.actions.cancel()
            event.stop()
