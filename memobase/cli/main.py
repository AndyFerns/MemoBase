"""
Main CLI application for MemoBase.
"""

import typer
from pathlib import Path
from typing import Optional

from memobase.cli.commands import (
    init_command,
    build_command,
    ask_command,
    query_command,
    graph_command,
    analyze_command,
    update_command,
    tui_command,
    doctor_command,
    help_command,
)
from memobase.core.exceptions import MemoBaseError


class AppContext:
    """Global application context for CLI options."""
    
    def __init__(self):
        self.verbose: int = 0
        self.debug: bool = False
        self.json: bool = False
        self.quiet: bool = False
        self.no_color: bool = False
        self.config: Optional[Path] = None
        self.profile: bool = False


app = typer.Typer(
    name="memobase",
    help="MemoBase — Memory for your codebase",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)

# Global options with proper callback
@app.callback()
def main(
    ctx: typer.Context,
    verbose: int = typer.Option(0, "--verbose", "-v", help="Enable verbose output", count=True),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output"),
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    profile: bool = typer.Option(False, "--profile", help="Enable performance profiling"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
) -> None:
    """MemoBase — Memory for your codebase."""
    # Create and set context object
    ctx.obj = AppContext()
    ctx.obj.verbose = verbose
    ctx.obj.debug = debug or verbose >= 3
    ctx.obj.json = json
    ctx.obj.quiet = quiet
    ctx.obj.no_color = no_color
    ctx.obj.config = config
    ctx.obj.profile = profile

# Register commands
app.command(name="init")(init_command)
app.command(name="build")(build_command)
app.command(name="ask")(ask_command)
app.command(name="query")(query_command)
app.command(name="graph")(graph_command)
app.command(name="analyze")(analyze_command)
app.command(name="update")(update_command)
app.command(name="tui")(tui_command)
app.command(name="doctor")(doctor_command)
app.command(name="help")(help_command)

# Error handler
def handle_error(error: Exception, ctx) -> None:
    """Handle CLI errors."""
    # Check if we have debug info
    debug_enabled = False
    if ctx and hasattr(ctx, 'obj') and ctx.obj:
        debug_enabled = ctx.obj.debug
    
    if debug_enabled:
        # Show full traceback in debug mode
        import traceback
        typer.echo(f"Debug: {traceback.format_exc()}", err=True)
    
    if isinstance(error, MemoBaseError):
        typer.echo(f"Error: {error}", err=True)
    else:
        typer.echo(f"Unexpected error: {error}", err=True)
    
    raise typer.Exit(1)

# Main entry point
def cli_entry_point() -> None:
    """Entry point for CLI application."""
    try:
        app()
    except Exception as e:
        # Try to get context from exception if available
        ctx = getattr(e, 'ctx', None)
        if ctx is None:
            # Fallback - create a minimal context for error handling
            ctx = type('Context', (), {'debug': False})()
        handle_error(e, ctx)

if __name__ == "__main__":
    cli_entry_point()
