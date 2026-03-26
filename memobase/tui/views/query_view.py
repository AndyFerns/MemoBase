"""
Query view for TUI.

Input: Response
"""

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from memobase.core.models import Response


class QueryView(Widget):
    """View for displaying query results."""
    
    DEFAULT_CSS = """
    QueryView {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    QueryView .header {
        margin: 1 0;
        padding: 1;
        background: $surface-darken-1;
    }
    
    QueryView .result {
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }
    
    QueryView .result-number {
        color: $primary;
        text-style: bold;
    }
    
    QueryView .result-title {
        text-style: bold;
    }
    
    QueryView .result-meta {
        color: $text-disabled;
        text-style: dim;
    }
    
    QueryView .no-results {
        text-align: center;
        color: $text-disabled;
    }
    """
    
    def __init__(self, response: Response, **kwargs) -> None:
        """Initialize query view.
        
        Args:
            response: Query response to display
        """
        super().__init__(**kwargs)
        self.response = response
    
    def compose(self):
        """Compose query view."""
        # Header with query info
        yield Static(self._format_header(), classes="header")
        
        # Results or no results message
        if not self.response.results:
            yield Static("No results found.", classes="no-results")
        else:
            # Display results
            for i, result in enumerate(self.response.results, 1):
                yield Static(self._format_result(i, result), classes="result")
            
            # Show if results were truncated
            if self.response.total_count > len(self.response.results):
                remaining = self.response.total_count - len(self.response.results)
                yield Static(f"... and {remaining} more results")
    
    def _format_header(self) -> str:
        """Format query header."""
        lines = [
            f"[b]Query Results[/b]",
            f"Found: {self.response.total_count} total",
            f"Showing: {len(self.response.results)}",
            f"Execution time: {self.response.execution_time_ms:.2f}ms",
        ]
        
        if self.response.metadata:
            lines.append(f"Query type: {self.response.metadata.get('query_type', 'unknown')}")
        
        return "\n".join(lines)
    
    def _format_result(self, index: int, result) -> str:
        """Format a single result."""
        lines = [f"[.result-number]{index}.[/.result-number] [.result-title]{self._get_result_title(result)}[/.result-title]"]
        
        # Location
        if hasattr(result, 'file_path') and result.file_path:
            location = str(result.file_path)
            if hasattr(result, 'symbol') and result.symbol and result.symbol.line_start > 0:
                location += f":{result.symbol.line_start}"
            lines.append(f"  [.result-meta]{location}[/.result-meta]")
        
        # Content preview
        if hasattr(result, 'content') and result.content:
            preview = result.content[:200]
            if len(result.content) > 200:
                preview += "..."
            lines.append(f"\n```\n{preview}\n```")
        
        # Keywords
        if hasattr(result, 'keywords') and result.keywords:
            lines.append(f"\n[.result-meta]Keywords: {', '.join(result.keywords)}[/.result-meta]")
        
        return "\n".join(lines)
    
    def _get_result_title(self, result) -> str:
        """Get title for result."""
        if hasattr(result, 'symbol') and result.symbol:
            return f"{result.symbol.name} ({result.symbol.symbol_type.value})"
        
        if hasattr(result, 'file_path') and result.file_path:
            return result.file_path.name
        
        return "Unknown"


class CompactQueryView(QueryView):
    """Compact query view for smaller displays."""
    
    DEFAULT_CSS = """
    CompactQueryView {
        width: 100%;
        height: 100%;
        padding: 0;
    }
    """
    
    def _format_result(self, index: int, result) -> str:
        """Format a single result (compact)."""
        title = self._get_result_title(result)
        
        if hasattr(result, 'file_path') and result.file_path:
            return f"{index}. {title} - {result.file_path.name}"
        
        return f"{index}. {title}"
