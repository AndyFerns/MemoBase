"""
CLI command implementations.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from memobase.core.exceptions import MemoBaseError
from memobase.core.models import Config

# Initialize console
console = Console(stderr=True)


def get_console(ctx: typer.Context) -> Console:
    """Get console instance with proper color settings."""
    no_color = ctx.obj.no_color if ctx and ctx.obj else False
    return Console(no_color=no_color, stderr=True)


def is_debug(ctx: typer.Context) -> bool:
    """Check if debug mode is enabled."""
    return ctx.obj.debug if ctx and ctx.obj else False


def is_verbose(ctx: typer.Context) -> bool:
    """Check if verbose mode is enabled."""
    return ctx.obj.verbose > 0 if ctx and ctx.obj else False


def get_verbosity_level(ctx: typer.Context) -> int:
    """Get verbosity level."""
    return ctx.obj.verbose if ctx and ctx.obj else 0


def is_json_output(ctx: typer.Context) -> bool:
    """Check if JSON output is enabled."""
    return ctx.obj.json if ctx and ctx.obj else False


def is_quiet(ctx: typer.Context) -> bool:
    """Check if quiet mode is enabled."""
    return ctx.obj.quiet if ctx and ctx.obj else False


def is_profile(ctx: typer.Context) -> bool:
    """Check if profiling is enabled."""
    return ctx.obj.profile if ctx and ctx.obj else False


def get_config_path(ctx: typer.Context) -> Optional[Path]:
    """Get configuration file path."""
    return ctx.obj.config if ctx and ctx.obj else None


def init_command(
    ctx: typer.Context,
    repo_path: Path = typer.Argument(".", help="Path to repository to initialize"),
    force: bool = typer.Option(False, "--force", "-f", help="Force initialization even if directory exists"),
) -> None:
    """Initialize MemoBase in a repository."""
    try:
        from memobase.infrastructure.setup import ProjectSetup
        
        console = get_console(ctx)
        
        if is_verbose(ctx):
            console.print(f"[dim]Initializing MemoBase in {repo_path}[/dim]")
        
        setup = ProjectSetup(repo_path)
        setup.init_repo(force=force)
        
        console.print(f"✅ MemoBase initialized successfully")
        console.print(f"Storage directory: {setup.storage_dir}")
        
        if get_verbosity_level(ctx) >= 2:
            console.print(f"[dim]Config file: {setup.config_path}[/dim]")
            
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def build_command(
    ctx: typer.Context,
    repo_path: Path = typer.Argument(".", help="Path to repository"),
    parallel: Optional[int] = typer.Option(None, "--parallel", "-p", help="Number of parallel workers"),
    force: bool = typer.Option(False, "--force", "-f", help="Force rebuild"),
) -> None:
    """Build the memory index for a repository."""
    try:
        from memobase.infrastructure.builder import ProjectBuilder
        
        console = get_console(ctx)
        
        if not is_quiet(ctx):
            console.print(f"[bold blue]Building memory index for[/bold blue] [green]{repo_path}[/green]")
        
        # Load config
        config = load_project_config(ctx, repo_path)
        if parallel:
            config.parallel_workers = parallel
        
        # Build project
        builder = ProjectBuilder(config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
        ) as progress:
            task = progress.add_task("Building memory...", total=None)
            
            stats = builder.build_repo(force)
            
            progress.update(task, description="Build complete")
        
        if not is_quiet(ctx):
            console.print("[bold green]✓[/bold green] Build completed successfully")
            console.print(f"Files processed: {stats['files_processed']}")
            console.print(f"Memory units: {stats['memory_units']}")
            console.print(f"Relationships: {stats['relationships']}")
            console.print(f"Build time: {stats['build_time']:.2f}s")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def ask_command(
    ctx: typer.Context,
    question: str = typer.Argument(..., help="Question to ask about your codebase"),
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Ask a question about your codebase."""
    try:
        from memobase.infrastructure.query_engine import QueryEngine
        from memobase.query.formatter import ResponseFormatter
        
        console = get_console(ctx)
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Initialize query engine
        engine = QueryEngine(config)
        
        if not is_quiet(ctx):
            console.print(f"[bold blue]Query:[/bold blue] {question}")
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            
            response = engine.ask_question(question, limit)
            
            progress.update(task, description="Search complete")
        
        # Format and display results
        formatter = ResponseFormatter()
        output_format = 'json' if json_output or is_json_output(ctx) else 'text'
        formatted_response = formatter.format_response(response, output_format)
        
        console.print(formatted_response)
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def query_command(
    ctx: typer.Context,
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
        
        console = get_console(ctx)
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Parse filters
        query_filters = {}
        if filters:
            for filter_pair in filters.split(','):
                if ':' in filter_pair:
                    key, value = filter_pair.split(':', 1)
                    query_filters[key.strip()] = value.strip()
        
        # Initialize query engine
        engine = QueryEngine(config)
        
        if not is_quiet(ctx):
            console.print(f"[bold blue]Query:[/bold blue] {query_text}")
        
        # Execute query
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
        ) as progress:
            task = progress.add_task("Searching...", total=None)
            
            response = engine.execute_query(query_text, query_filters, limit, offset)
            
            progress.update(task, description="Search complete")
        
        # Format and display results
        formatter = ResponseFormatter()
        output_format = 'json' if json_output or is_json_output(ctx) else 'text'
        formatted_response = formatter.format_response(response, output_format)
        
        console.print(formatted_response)
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def graph_command(
    ctx: typer.Context,
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
        config = load_project_config(ctx, repo_path)
        
        # Initialize graph analyzer
        analyzer = GraphAnalyzer(config)
        
        if not is_quiet(ctx):
            console.print("[bold blue]Analyzing code relationships...[/bold blue]")
        
        # Analyze graph
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
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
            
            if not is_quiet(ctx):
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
    ctx: typer.Context,
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    analysis_type: str = typer.Option("all", "--type", "-t", help="Analysis type (all, security, quality, performance)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for analysis"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format"),
) -> None:
    """Analyze code quality and security."""
    try:
        from memobase.infrastructure.code_analyzer import CodeAnalyzer
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(config)
        
        if not is_quiet(ctx):
            console.print(f"[bold blue]Running {analysis_type} analysis...[/bold blue]")
        
        # Run analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
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
            
            if not is_quiet(ctx):
                console.print(f"[bold green]✓[/bold green] Analysis saved to {output}")
        else:
            console.print(output_text)
        
        # Summary
        if not is_quiet(ctx):
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
    ctx: typer.Context,
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    force: bool = typer.Option(False, "--force", "-f", help="Force full rebuild"),
) -> None:
    """Update memory index with changes."""
    try:
        from memobase.infrastructure.updater import ProjectUpdater
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Initialize updater
        updater = ProjectUpdater(config)
        
        if not is_quiet(ctx):
            console.print(f"[bold blue]Updating memory index for[/bold blue] [green]{repo_path}[/green]")
        
        # Update
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
        ) as progress:
            task = progress.add_task("Detecting changes...", total=None)
            
            stats = updater.update_repo(force)
            
            progress.update(task, description="Update complete")
        
        if not is_quiet(ctx):
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
    ctx: typer.Context,
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
) -> None:
    """Launch the Terminal User Interface."""
    try:
        from memobase.tui.app import MemoBaseTUI
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Launch TUI
        tui_app = MemoBaseTUI(config)
        tui_app.run()
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
            console.print_exception()
        else:
            console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


def doctor_command(
    ctx: typer.Context,
    repo_path: Path = typer.Option(".", "--repo", "-r", help="Repository path"),
    fix: bool = typer.Option(False, "--fix", "-f", help="Attempt to fix issues"),
) -> None:
    """Check system health and diagnose issues."""
    try:
        from memobase.infrastructure.doctor import SystemDoctor
        
        console = get_console(ctx)
        
        # Load config
        config = load_project_config(ctx, repo_path)
        
        # Initialize doctor
        doctor = SystemDoctor(config)
        
        if not is_quiet(ctx):
            console.print("[bold blue]Running system diagnostics...[/bold blue]")
        
        # Run diagnostics
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=is_quiet(ctx),
        ) as progress:
            task = progress.add_task("Diagnosing...", total=None)
            
            health_report = doctor.run_diagnostics()
            
            progress.update(task, description="Diagnostics complete")
        
        # Display results
        display_health_report(health_report)
        
        # Fix issues if requested
        if fix and health_report['issues']:
            if not is_quiet(ctx):
                console.print("\n[bold yellow]Attempting to fix issues...[/bold yellow]")
            
            fixed_issues = doctor.fix_issues(health_report['issues'])
            
            if not is_quiet(ctx):
                console.print(f"[bold green]✓[/bold green] Fixed {len(fixed_issues)} issues")
        
    except MemoBaseError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        if is_debug(ctx):
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


def get_default_config() -> dict:
    """Get default configuration."""
    return {
        'repo_path': '.',
        'max_file_size_mb': 10,
        'excluded_patterns': [
            '*.pyc', '*.pyo', '*.pyd', '__pycache__', '.git', '.svn', '.hg',
            'node_modules', '.vscode', '.idea', '*.log', '*.tmp'
        ],
        'included_extensions': [
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc',
            '.cxx', '.rs', '.go', '.rb', '.php', '.h', '.hpp', '.hxx'
        ],
        'parallel_workers': 4,
        'index_batch_size': 1000,
        'graph_max_depth': 5,
        'cache_size_mb': 100,
        'storage_backend': 'file',
        'storage_path': '.memobase',
    }


def load_config_file(config_path: Path) -> dict:
    """Load configuration from file."""
    try:
        import json
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_path}: {e}")


# Helper functions
def load_project_config(ctx: typer.Context, repo_path: Path) -> Config:
    """Load project configuration."""
    from memobase.core.models import Config
    
    # Load base config
    config_path = get_config_path(ctx)
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
    console.print(f"Overall Status: [{status_color}]{status.upper()}[/{status_color}]")
    
    # Issues
    if report['issues']:
        console.print(f"\n[bold red]Issues Found ({len(report['issues'])}):[/bold red]")
        for issue in report['issues']:
            # Escape any brackets in the issue text
            safe_issue = issue.replace("[", "\\[").replace("]", "\\]")
            console.print(f"  • {safe_issue}")
    else:
        console.print("\n[bold green]✓ No issues found[/bold green]")
    
    # Recommendations
    if report['recommendations']:
        console.print(f"\n[bold blue]Recommendations:[/bold blue]")
        for rec in report['recommendations']:
            # Escape any brackets in the recommendation text
            safe_rec = rec.replace("[", "\\[").replace("]", "\\]")
            console.print(f"  • {safe_rec}")
