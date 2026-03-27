"""
Main Textual app for MemoBase TUI.

Boots Textual app, renders ASCII splash, initializes layout.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget

from memobase.core.models import Config
from memobase.tui.actions import Actions
from memobase.tui.controller import TUIController
from memobase.tui.event_bus import EventBus
from memobase.tui.layouts.main_layout import MainLayout
from memobase.tui.state import TUIState
from memobase.tui.widgets.command_bar import CommandBar
from memobase.tui.widgets.file_tree import FileTree
from memobase.tui.widgets.header import Header
from memobase.tui.widgets.main_panel import MainPanel
from memobase.tui.widgets.status_bar import StatusBar


class MemoBaseTUI(App):
    """Main Textual application for MemoBase."""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 1;
        grid-rows: auto 1fr auto;
    }
    
    #header {
        height: 3;
        dock: top;
    }
    
    #main-container {
        layout: grid;
        grid-size: 2;
        grid-columns: 25% 1fr;
    }
    
    #file-tree {
        width: 100%;
        height: 100%;
    }
    
    #main-panel {
        width: 100%;
        height: 100%;
    }
    
    #status-bar {
        height: 1;
        dock: bottom;
    }
    
    #command-bar {
        height: 1;
        dock: bottom;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("h", "show_help", "Help"),
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
        Binding("g", "show_graph", "Graph"),
        Binding("m", "show_memory", "Memory"),
        Binding("a", "show_analysis", "Analysis"),
        Binding("slash", "enter_query", "Query"),
        Binding("colon", "enter_command", "Command"),
        Binding("escape", "cancel", "Cancel"),
        Binding("v", "toggle_verbose", "Verbose"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, config: Optional[Config] = None) -> None:
        """Initialize MemoBase TUI.
        
        Args:
            config: MemoBase configuration
        """
        super().__init__()
        self.config = config or Config(repo_path=Path.cwd())
        
        # Initialize core components
        self.state = TUIState()
        self.event_bus = EventBus()
        self.controller = TUIController(self.config, self.state, self.event_bus)
        self.actions = Actions(self.state, self.controller, self.event_bus)
        
        # Track async tasks
        self._tasks: set[asyncio.Task] = set()
    
    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        # Show ASCII splash on startup
        self._show_splash()
        
        # Header
        yield Header(self.state)
        
        # Main container with file tree and main panel
        with Horizontal(id="main-container"):
            yield FileTree(self.state, self.controller, id="file-tree")
            yield MainPanel(self.state, self.controller, id="main-panel")
        
        # Command bar (hidden by default)
        yield CommandBar(self.state, self.actions, id="command-bar")
        
        # Status bar
        yield StatusBar(self.state, id="status-bar")
    
    async def on_mount(self) -> None:
        """Called when app is mounted."""
        # Initialize state
        self.state.current_mode = "memory"
        self.state.verbosity = 1
        
        # Start async initialization
        task = asyncio.create_task(self._async_init())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        
        # Subscribe to events
        self.event_bus.subscribe("state_changed", self._on_state_changed)
        self.event_bus.subscribe("error", self._on_error)
        self.event_bus.subscribe("query_result", self._on_query_result)
    
    async def on_unmount(self) -> None:
        """Called when app is unmounted."""
        # Cancel all pending tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
    
    def _show_splash(self) -> None:
        """Render ASCII splash screen."""
        splash = """
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   ███╗   ███╗ ███████╗ ███╗   ███╗  ██████╗  ██████╗   ██╗  ║
║   ████╗ ████║ ██╔════╝ ████╗ ████║ ██╔═══██╗ ██╔══██╗  ██║  ║
║   ██╔████╔██║ █████╗   ██╔████╔██║ ██║   ██║ ██████╔╝  ██║  ║
║   ██║╚██╔╝██║ ██╔══╝   ██║╚██╔╝██║ ██║   ██║ ██╔══██╗  ██║  ║
║   ██║ ╚═╝ ██║ ███████╗ ██║ ╚═╝ ██║ ╚██████╔╝ ██████╔╝  ██║  ║
║   ╚═╝     ╚═╝ ╚══════╝ ╚═╝     ╚═╝  ╚═════╝  ╚═════╝   ╚═╝  ║
║                                                            ║
║              Memory for Your Codebase                       ║
║                                                            ║
║     [M]emory  [G]raph  [A]nalysis  [/]Query  [?]Help       ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """
        # In a real implementation, this would be shown as an overlay
        # For now, we just log it
        self.log(splash)
    
    async def _async_init(self) -> None:
        """Async initialization."""
        try:
            # Initialize controller
            await self.controller.initialize()
            
            # Update status
            self.state.status_message = "Ready"
            self.event_bus.emit("state_changed", {"status": "initialized"})
            
        except Exception as e:
            self.event_bus.emit("error", {"message": str(e)})
    
    def _on_state_changed(self, event: dict) -> None:
        """Handle state change events."""
        # Trigger re-render
        self.refresh()
    
    def _on_error(self, event: dict) -> None:
        """Handle error events."""
        message = event.get("message", "Unknown error")
        self.state.status_message = f"Error: {message}"
        self.notify(message, severity="error")
    
    def _on_query_result(self, event: dict) -> None:
        """Handle query result events."""
        # Update main panel with results
        main_panel = self.query_one("#main-panel", MainPanel)
        main_panel.show_query_results(event.get("response"))
    
    # Action handlers
    def action_show_help(self) -> None:
        """Show help."""
        self.actions.show_help()
    
    def action_move_down(self) -> None:
        """Move selection down."""
        self.actions.move_down()
    
    def action_move_up(self) -> None:
        """Move selection up."""
        self.actions.move_up()
    
    def action_show_graph(self) -> None:
        """Show graph view."""
        self.actions.show_graph()
    
    def action_show_memory(self) -> None:
        """Show memory view."""
        self.actions.show_memory()
    
    def action_show_analysis(self) -> None:
        """Show analysis view."""
        self.actions.show_analysis()
    
    def action_enter_query(self) -> None:
        """Enter query mode."""
        self.actions.enter_query_mode()
    
    def action_enter_command(self) -> None:
        """Enter command mode."""
        self.actions.enter_command_mode()
    
    def action_cancel(self) -> None:
        """Cancel current operation."""
        self.actions.cancel()
    
    def action_toggle_verbose(self) -> None:
        """Toggle verbose mode."""
        self.actions.toggle_verbose()
    
    def action_refresh(self) -> None:
        """Refresh data."""
        asyncio.create_task(self.actions.refresh())
    
    def run(self) -> None:
        """Run the TUI application."""
        super().run()


def launch_tui(config: Optional[Config] = None) -> None:
    """Launch the MemoBase TUI.
    
    Args:
        config: MemoBase configuration
    """
    app = MemoBaseTUI(config)
    app.run()
