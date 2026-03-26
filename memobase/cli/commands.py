"""
CLI command implementations.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from memobase.cli.config import (
    get_config_path, 
    get_default_config, 
    is_debug, 
    is_json_output, 
    is_no_color, 
    is_profile, 
    is_quiet, 
    is_verbose,
    load_config_file,
    save_config_file,
)
from memobase.core.exceptions import MemoBaseError
from memobase.core.models import Config

# Initialize console
console = Console(no_color=is_no_color(), stderr=True)


def init_command(
    repo_path: Path = typer.Argument(".", help="Path to repository to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Force initialization even if directory exists"),
) -> None:
    """Initialize MemoBase in a repository."""
    try:
        from memobase.infrastructure.setup import ProjectSetup
        
        if not is_quiet():
            console.print(f"[bold blue]Initializing MemoBase in[/bold blue] [green]{repo_path}[/green]")
        
        # Load or create config
        config_path = get_config_path()
        if config_path and config_path.exists():
            config = load_config_file(config_path)
        else:
            config = get_default_config()
        
        config['repo_path'] = str(repo_path.absolute())
        
        # Setup project
        setup = ProjectSetup(config)
        setup.initialize_repo(force)
        
        # Save config
        if config_path:
            save_config_file(config_path, config)
        
        if not is_quiet():
            console.print("[bold green]✓[/bold green] MemoBase initialized successfully")
            console.print(f"Storage directory: {setup.storage_path}")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def build_command(
    repo_path: Path = typer.Argument(".", help="Path to repository"),
    parallel: Optional[int] = typer.Option(None, "--parallel", "-p", help="Number of parallel workers"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild"),
) -> None:
    """Build the memory index for a repository."""
    try:
        from memobase.infrastructure.builder import ProjectBuilder
        
        if not is_quiet():
            console.print(f"[bold blue]Building memory index for[/bold blue] [green]{repo_path}[/green]")
        
        # Load config
        config = load_project_config(repo_path)
        if parallel:
            config.parallel_workers = parallel
        
        # Build project
        builder = ProjectBuilder(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Building memory...", total=None)
            
            stats = builder.build_repo(force)
            
            progress.update(task, description="Build complete")
        
        if not is_quiet():
            console.print("[bold green]✓[/bold green] Build completed successfully")
            console.print(f"Files processed: {stats['files_processed']}")
            console.print(f"Memory units: {stats['memory_units']}")
            console.print(f"Relationships: {stats['relationships']}")
            console.print(f"Build time: {stats['build_time']:.2f}s")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def ask_command(
    question: str = typer.Argument(..., help="Question to ask about your codebase"),
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Ask a question about your codebase."""
    try:
        from memobase.infrastructure.query_engine import QueryEngine
        from memobase.query.formatter import ResponseFormatter
        
        # Load config
        config = load_project_config(repo_path)
        
        # Initialize query engine
        engine = QueryEngine(config)
        
        if not is_quiet():
            console.print(f"[bold blue]Query:[/bold blue] {question}")
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            
            response = engine.ask_question(question, limit)
            
            progress.update(task, description="Search complete")
        
        # Format and display results
        formatter = ResponseFormatter()
        output_format = 'json' if json_output or is_json_output() else 'text'
        formatted_response = formatter.format_response(response, output_format)
        
        console.print(formatted_response)
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def query_command(
    query_text: str = typer.Argument(..., help="Query string"),
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
    offset: int = typer.Option(0, "--offset", "-o", help="Result offset"),
    filters: Optional[str] = typer.Option(None, "--filter", "-f", help="Query filters"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Execute a search query."""
    try:
        from memobase.infrastructure.query_engine import QueryEngine
        from memobase.query.formatter import ResponseFormatter
        
        # Load config
        config = load_project_config(repo_path)
        
        # Parse filters
        query_filters = {}
        if filters:
            for filter_pair in filters.split(','):
                if ':' in filter_pair:
                    key, value = filter_pair.split(':', 1)
                    query_filters[key.strip()] = value.strip()
        
        # Initialize query engine
        engine = QueryEngine(config)
        
        if not is_quiet():
            console.print(f"[bold blue]Query:[/bold blue] {query_text}")
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            
            response = engine.execute_query(query_text, query_filters, limit, offset)
            
            progress.update(task, description="Search complete")
        
        # Format and display results
        formatter = ResponseFormatter()
        output_format = 'json' if json_output or is_json_output() else 'text'
        formatted_response = formatter.format_response(response, output_format)
        
        console.print(formatted_response)
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def graph_command(
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s", help="Symbol to analyze"),
    depth: int = typer.Option(3, "--depth", "-d", help="Graph traversal depth"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for graph"),
    format_type: str = typer.Option("text", "--format", "-f", help="Output format (text, dot, json)"),
) -> None:
    """Analyze code relationships."""
    try:
        from memobase.infrastructure.graph_analyzer import GraphAnalyzer
        
        # Load config
        config = load_project_config(repo_path)
        
        # Initialize graph analyzer
        analyzer = GraphAnalyzer(config)
        
        if not is_quiet():
            console.print("[bold blue]Analyzing code relationships...[/bold blue]")
        
        # Analyze graph
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Analyzing graph...", total=None)
            
            if symbol:
                graph_data = analyzer.analyze_symbol_relationships(symbol, depth)
            else:
                graph_data = analyzer.analyze_overall_graph(depth)
            
            progress.update(task, description="Analysis complete")
        
        # Output results
        if output:
            with open(output, 'w') as f:
                if format_type == 'json':
                    import json
                    json.dump(graph_data, f, indent=2)
                elif format_type == 'dot':
                    f.write(graph_data['dot_output'])
                else:
                    f.write(graph_data['text_output'])
            
            if not is_quiet():
                console.print(f"[bold green]✓[/bold green] Graph analysis saved to {output}")
        else:
            if format_type == 'json':
                import json
                console.print(json.dumps(graph_data, indent=2))
            else:
                console.print(graph_data['text_output'])
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def analyze_command(
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    analysis_type: str = typer.Option("all", "--type", "-t", help="Analysis type (all, security, quality, performance)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for analysis"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Analyze code quality and security."""
    try:
        from memobase.infrastructure.code_analyzer import CodeAnalyzer
        
        # Load config
        config = load_project_config(repo_path)
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(config)
        
        if not is_quiet():
            console.print(f"[bold blue]Running {analysis_type} analysis...[/bold blue]")
        
        # Run analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Analyzing code...", total=None)
            
            findings = analyzer.analyze_repo(analysis_type)
            
            progress.update(task, description="Analysis complete")
        
        # Output results
        if json_output or is_json_output():
            import json
            output_text = json.dumps(findings, indent=2, default=str)
        else:
            output_text = format_findings_text(findings)
        
        if output:
            with open(output, 'w') as f:
                f.write(output_text)
            
            if not is_quiet():
                console.print(f"[bold green]✓[/bold green] Analysis saved to {output}")
        else:
            console.print(output_text)
        
        # Summary
        if not is_quiet():
            console.print(f"\n[bold]Summary:[/bold]")
            console.print(f"Total findings: {len(findings)}")
            severity_counts = {}
            for finding in findings:
                severity = finding.severity
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity, count in severity_counts.items():
                color = get_severity_color(severity)
                console.print(f"{severity}: {color}{count}[/{color}]")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def update_command(
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    force: bool = typer.Option(False, "--force", "-f", help="Force full rebuild"),
) -> None:
    """Update memory index with changes."""
    try:
        from memobase.infrastructure.updater import ProjectUpdater
        
        # Load config
        config = load_project_config(repo_path)
        
        # Initialize updater
        updater = ProjectUpdater(config)
        
        if not is_quiet():
            console.print(f"[bold blue]Updating memory index for[/bold blue] [green]{repo_path}[/green]")
        
        # Update
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Detecting changes...", total=None)
            
            stats = updater.update_repo(force)
            
            progress.update(task, description="Update complete")
        
        if not is_quiet():
            console.print("[bold green]✓[/bold green] Update completed successfully")
            console.print(f"Files added: {stats['files_added']}")
            console.print(f"Files modified: {stats['files_modified']}")
            console.print(f"Files deleted: {stats['files_deleted']}")
            console.print(f"Update time: {stats['update_time']:.2f}s")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def tui_command(
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
) -> None:
    """Launch the Terminal User Interface."""
    try:
        from memobase.tui.app import MemoBaseTUI
        
        # Load config
        config = load_project_config(repo_path)
        
        # Launch TUI
        tui_app = MemoBaseTUI(config)
        tui_app.run()
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def doctor_command(
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to fix issues"),
) -> None:
    """Check system health and diagnose issues."""
    try:
        from memobase.infrastructure.doctor import SystemDoctor
        
        # Load config
        config = load_project_config(repo_path)
        
        # Initialize doctor
        doctor = SystemDoctor(config)
        
        if not is_quiet():
            console.print("[bold blue]Running system diagnostics...[/bold blue]")
        
        # Run diagnostics
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(),
        ) as progress:
            task = progress.add_task("Diagnosing...", total=None)
            
            health_report = doctor.run_diagnostics()
            
            progress.update(task, description="Diagnostics complete")
        
        # Display results
        display_health_report(health_report)
        
        # Fix issues if requested
        if fix and health_report['issues']:
            if not is_quiet():
                console.print("\n[bold yellow]Attempting to fix issues...[/bold yellow]")
            
            fixed_issues = doctor.fix_issues(health_report['issues'])
            
            if not is_quiet():
                console.print(f"[bold green]✓[/bold green] Fixed {len(fixed_issues)} issues")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug():
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def help_command(
    command: Optional[str] = typer.Argument(None, help="Command to get help for"),
) -> None:
    """Get help for MemoBase commands."""
    if command:
        # Show help for specific command
        typer.echo(f"Help for '{command}' command:")
        # Implementation would show detailed help for specific command
    else:
        # Show general help
        typer.echo("""
[bold blue]MemoBase — Memory for your codebase[/bold blue]

[bold]Common commands:[/bold]
  init        Initialize MemoBase in a repository
  build       Build the memory index
  ask         Ask a question about your codebase
  query       Execute a search query
  tui         Launch the Terminal User Interface
  analyze     Analyze code quality and security
  update      Update memory index with changes
  doctor      Check system health

[bold]Examples:[/bold]
  memobase init ./my-project
  memobase build
  memobase ask "How does authentication work?"
  memobase query "function login" --limit 5
  memobase tui

[bold]For more help:[/bold]
  memobase <command> --help
  memobase --help
        """)


# Helper functions
def load_project_config(repo_path: Path) -> Config:
    """Load project configuration."""
    from memobase.core.models import Config
    
    # Load base config
    config_path = get_config_path()
    if config_path and config_path.exists():
        config_data = load_config_file(config_path)
    else:
        config_data = get_default_config()
    
    # Override repo path
    config_data['repo_path'] = str(repo_path.absolute())
    
    return Config(**config_data)


def format_findings_text(findings) -> str:
    """Format findings as text."""
    lines = []
    
    for finding in findings:
        severity_color = get_severity_color(finding.severity)
        lines.append(f"{severity_color}[{finding.severity.upper()}][/{severity_color}] {finding.message}")
        lines.append(f"  File: {finding.file_path}:{finding.line_number}")
        if finding.suggestion:
            lines.append(f"  Suggestion: {finding.suggestion}")
        lines.append("")
    
    return "\n".join(lines)


def get_severity_color(severity: str) -> str:
    """Get color for severity level."""
    colors = {
        'critical': 'red',
        'high': 'bright_red',
        'medium': 'yellow',
        'low': 'bright_yellow',
        'info': 'blue',
    }
    return colors.get(severity, 'white')


def display_health_report(report: dict) -> None:
    """Display health report."""
    console.print("\n[bold]System Health Report[/bold]")
    
    # Overall status
    status = report['overall_status']
    status_color = 'green' if status == 'healthy' else 'yellow' if status == 'warning' else 'red'
    console.print(f"Overall Status: {status_color}{status.upper()}[/{status_color}]")
    
    # Issues
    if report['issues']:
        console.print(f"\n[bold red]Issues Found ({len(report['issues'])}):[/bold red]")
        for issue in report['issues']:
            console.print(f"  • {issue}")
    else:
        console.print("\n[bold green]✓ No issues found[/bold green]")
    
    # Recommendations
    if report['recommendations']:
        console.print(f"\n[bold blue]Recommendations:[/bold blue]")
        for rec in report['recommendations']:
            console.print(f"  • {rec}")
