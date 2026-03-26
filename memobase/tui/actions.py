"""
Command and keybinding actions for TUI.

Maps keybindings → actions
"""

from __future__ import annotations

import asyncio
from typing import Optional

from memobase.core.models import QueryType
from memobase.tui.state import TUIState
from memobase.tui.controller import TUIController
from memobase.tui.event_bus import EventBus, TypedEventBus


class Actions:
    """Maps keybindings and commands to actions."""
    
    def __init__(
        self,
        state: TUIState,
        controller: TUIController,
        event_bus: EventBus
    ) -> None:
        """Initialize actions.
        
        Args:
            state: TUI state manager
            controller: TUI controller
            event_bus: Event bus for communication
        """
        self.state = state
        self.controller = controller
        self.event_bus = event_bus
    
    # Navigation actions
    def move_down(self) -> None:
        """Move selection down."""
        self.state.scroll_position += 1
        self.event_bus.emit("state_changed", {"scroll": self.state.scroll_position})
    
    def move_up(self) -> None:
        """Move selection up."""
        if self.state.scroll_position > 0:
            self.state.scroll_position -= 1
            self.event_bus.emit("state_changed", {"scroll": self.state.scroll_position})
    
    def move_to_top(self) -> None:
        """Move to top of list."""
        self.state.scroll_position = 0
        self.event_bus.emit("state_changed", {"scroll": self.state.scroll_position})
    
    def move_to_bottom(self) -> None:
        """Move to bottom of list."""
        # Implementation depends on content length
        self.event_bus.emit("state_changed", {"scroll": "bottom"})
    
    # View switching actions
    def show_memory(self) -> None:
        """Show memory view."""
        self.state.set_mode("memory")
        self.event_bus.emit("mode_changed", {"mode": "memory"})
    
    def show_graph(self) -> None:
        """Show graph view."""
        self.state.set_mode("graph")
        self.event_bus.emit("mode_changed", {"mode": "graph"})
    
    def show_analysis(self) -> None:
        """Show analysis view."""
        self.state.set_mode("analysis")
        self.event_bus.emit("mode_changed", {"mode": "analysis"})
    
    def show_query(self) -> None:
        """Show query view."""
        self.state.set_mode("query")
        self.event_bus.emit("mode_changed", {"mode": "query"})
    
    # Input mode actions
    def enter_query_mode(self) -> None:
        """Enter query input mode."""
        self.state.enter_query_mode()
        self.event_bus.emit("state_changed", {"input_mode": "query"})
    
    def enter_command_mode(self) -> None:
        """Enter command input mode."""
        self.state.enter_command_mode()
        self.event_bus.emit("state_changed", {"input_mode": "command"})
    
    def cancel(self) -> None:
        """Cancel current operation."""
        self.state.exit_input_mode()
        self.state.set_status("Cancelled")
        self.event_bus.emit("state_changed", {"input_mode": None})
    
    # Query actions
    async def execute_query(self, query_text: str) -> None:
        """Execute a query.
        
        Args:
            query_text: Query string to execute
        """
        self.state.exit_input_mode()
        
        response = await self.controller.run_query(query_text, QueryType.SEARCH)
        
        # Switch to query view to show results
        self.show_query()
    
    def execute_command(self, command: str) -> None:
        """Execute a command.
        
        Args:
            command: Command string to execute
        """
        self.state.exit_input_mode()
        
        # Parse and execute command
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        # Execute command
        if cmd == "quit" or cmd == "q":
            self.quit()
        elif cmd == "memory" or cmd == "m":
            self.show_memory()
        elif cmd == "graph" or cmd == "g":
            self.show_graph()
        elif cmd == "analysis" or cmd == "a":
            self.show_analysis()
        elif cmd == "verbose" or cmd == "v":
            if args:
                try:
                    level = int(args[0])
                    self.set_verbosity(level)
                except ValueError:
                    self.state.set_status(f"Invalid verbosity level: {args[0]}")
            else:
                self.toggle_verbose()
        elif cmd == "depth" or cmd == "d":
            if args:
                try:
                    depth = int(args[0])
                    self.set_graph_depth(depth)
                except ValueError:
                    self.state.set_status(f"Invalid depth: {args[0]}")
        elif cmd == "refresh" or cmd == "r":
            asyncio.create_task(self.refresh())
        elif cmd == "help" or cmd == "h":
            self.show_help()
        else:
            self.state.set_status(f"Unknown command: {cmd}")
    
    # File actions
    def select_file(self, file_path: str) -> None:
        """Select a file.
        
        Args:
            file_path: Path to selected file
        """
        self.state.set_file(file_path)
        self.event_bus.emit("file_selected", {"file_path": file_path})
    
    async def show_file_memory(self, file_path: str) -> None:
        """Show memory view for file.
        
        Args:
            file_path: Path to file
        """
        self.select_file(file_path)
        
        memory_unit = await self.controller.get_file_memory(file_path)
        
        if memory_unit:
            self.state.set_memory_unit(memory_unit)
            self.show_memory()
        else:
            self.state.set_status(f"No memory data for: {file_path}")
    
    async def show_file_graph(self, file_path: str, depth: int = 3) -> None:
        """Show graph view for file.
        
        Args:
            file_path: Path to file
            depth: Graph traversal depth
        """
        self.select_file(file_path)
        
        graph = await self.controller.get_dependencies(file_path, depth)
        
        if graph:
            self.state.set_graph_subset(graph)
            self.show_graph()
        else:
            self.state.set_status(f"No graph data for: {file_path}")
    
    # Verbosity actions
    def toggle_verbose(self) -> None:
        """Toggle verbose mode."""
        current = self.state.verbosity
        new_level = (current + 1) % 4  # Cycle through 0-3
        self.set_verbosity(new_level)
    
    def set_verbosity(self, level: int) -> None:
        """Set verbosity level.
        
        Args:
            level: Verbosity level (0-3)
        """
        self.state.set_verbosity(level)
        
        level_names = ["Quiet", "Normal", "Verbose", "Debug"]
        self.state.set_status(f"Verbosity: {level_names[level]} ({level})")
        self.event_bus.emit("state_changed", {"verbosity": level})
    
    # Graph actions
    def set_graph_depth(self, depth: int) -> None:
        """Set graph traversal depth.
        
        Args:
            depth: Graph depth limit
        """
        self.state.graph_depth = max(1, min(10, depth))
        self.state.set_status(f"Graph depth: {self.state.graph_depth}")
        self.event_bus.emit("state_changed", {"graph_depth": self.state.graph_depth})
    
    def expand_graph(self) -> None:
        """Expand graph depth."""
        self.set_graph_depth(self.state.graph_depth + 1)
    
    def collapse_graph(self) -> None:
        """Collapse graph depth."""
        self.set_graph_depth(self.state.graph_depth - 1)
    
    # Data actions
    async def refresh(self) -> None:
        """Refresh all data."""
        await self.controller.refresh_data()
        self.state.set_status("Data refreshed")
    
    async def run_analysis(self, analysis_type: str = "all") -> None:
        """Run code analysis.
        
        Args:
            analysis_type: Type of analysis to run
        """
        findings = await self.controller.run_analysis(analysis_type)
        
        if findings:
            self.show_analysis()
            self.state.set_status(f"Analysis complete: {len(findings)} findings")
        else:
            self.state.set_status("No analysis findings")
    
    # Help actions
    def show_help(self) -> None:
        """Show help."""
        help_text = """
MemoBase TUI Help

Navigation:
  j/k       Move up/down
  g         Go to top
  G         Go to bottom

Views:
  m         Memory view
  g         Graph view
  a         Analysis view
  /         Query mode

Graph:
  +         Expand depth
  -         Collapse depth
  d N       Set depth to N

Commands (:command):
  :quit, :q       Quit
  :memory, :m     Switch to memory
  :graph, :g      Switch to graph
  :analysis, :a   Switch to analysis
  :verbose N      Set verbosity (0-3)
  :refresh, :r    Refresh data
  :help, :h       Show this help

Other:
  v         Toggle verbose
  r         Refresh data
  Esc       Cancel/Exit mode
  ?         Show help
        """
        self.state.set_status("Help displayed")
        # In a real implementation, this would show a help overlay
    
    def quit(self) -> None:
        """Quit the application."""
        self.event_bus.emit("quit", {})


class CommandParser:
    """Parse command strings into actions."""
    
    def __init__(self, actions: Actions) -> None:
        """Initialize command parser.
        
        Args:
            actions: Actions instance to execute commands
        """
        self.actions = actions
    
    def parse(self, command: str) -> None:
        """Parse and execute command.
        
        Args:
            command: Command string to parse
        """
        # Trim whitespace
        command = command.strip()
        
        if not command:
            return
        
        # Handle query (starts with /)
        if command.startswith("/"):
            query = command[1:].strip()
            asyncio.create_task(self.actions.execute_query(query))
            return
        
        # Handle command (starts with :)
        if command.startswith(":"):
            cmd = command[1:].strip()
            self.actions.execute_command(cmd)
            return
        
        # Default: treat as search query
        asyncio.create_task(self.actions.execute_query(command))
