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

app = typer.Typer(
    name="memobase",
    help="MemoBase — Memory for your codebase",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

# Global options
@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-error output"),
    json: bool = typer.Option(False, "--json", help="Output in JSON format"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colored output"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Configuration file path"),
    profile: bool = typer.Option(False, "--profile", help="Enable performance profiling"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
) -> None:
    """MemoBase — Memory for your codebase."""
    # Set global configuration based on options
    import memobase.cli.config as cli_config
    cli_config.set_global_options({
        'verbose': verbose,
        'quiet': quiet,
        'json': json,
        'no_color': no_color,
        'config': config,
        'profile': profile,
        'debug': debug,
    })

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
def handle_error(error: Exception) -> None:
    """Handle CLI errors."""
    import memobase.cli.config as cli_config
    
    if cli_config.get_option('debug'):
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
    """Entry point for the CLI application."""
    try:
        app()
    except Exception as e:
        handle_error(e)

if __name__ == "__main__":
    cli_entry_point()
