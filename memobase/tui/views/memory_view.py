"""
Memory view for TUI.

Input: MemoryUnit
Output: formatted display
"""

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from memobase.core.models import MemoryUnit


class MemoryView(Widget):
    """View for displaying memory unit information."""
    
    DEFAULT_CSS = """
    MemoryView {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    MemoryView .section {
        margin: 1 0;
        padding: 1;
        border: solid $primary-darken-2;
    }
    
    MemoryView .label {
        text-style: bold;
        color: $primary;
    }
    
    MemoryView .value {
        color: $text;
    }
    
    MemoryView .code {
        background: $surface-darken-1;
        color: $text;
        padding: 1;
    }
    """
    
    def __init__(self, memory_unit: MemoryUnit, **kwargs) -> None:
        """Initialize memory view.
        
        Args:
            memory_unit: Memory unit to display
        """
        super().__init__(**kwargs)
        self.memory_unit = memory_unit
    
    def compose(self):
        """Compose memory view."""
        # Header section
        yield Static(self._format_header(), classes="section")
        
        # Symbol information
        if self.memory_unit.symbol:
            yield Static(self._format_symbol(), classes="section")
        
        # Relationships
        if self.memory_unit.relationships:
            yield Static(self._format_relationships(), classes="section")
        
        # Content preview
        if self.memory_unit.content:
            yield Static(self._format_content(), classes="section code")
        
        # Metadata
        yield Static(self._format_metadata(), classes="section")
    
    def _format_header(self) -> str:
        """Format header section."""
        lines = [
            f"[b]File:[/b] {self.memory_unit.file_path}",
            f"[b]ID:[/b] {self.memory_unit.id}",
            f"[b]Updated:[/b] {self.memory_unit.updated_at}",
        ]
        return "\n".join(lines)
    
    def _format_symbol(self) -> str:
        """Format symbol section."""
        symbol = self.memory_unit.symbol
        
        lines = [
            f"[b]Symbol:[/b] {symbol.name}",
            f"[b]Type:[/b] {symbol.symbol_type.value}",
        ]
        
        if symbol.line_start > 0:
            lines.append(f"[b]Location:[/b] Line {symbol.line_start}")
            if symbol.line_end > symbol.line_start:
                lines.append(f"[b]Lines:[/b] {symbol.line_start}-{symbol.line_end}")
        
        if symbol.signature:
            lines.append(f"[b]Signature:[/b] {symbol.signature}")
        
        if symbol.parameters:
            lines.append(f"[b]Parameters:[/b] {', '.join(symbol.parameters)}")
        
        if symbol.return_type:
            lines.append(f"[b]Returns:[/b] {symbol.return_type}")
        
        if symbol.documentation:
            lines.append(f"[b]Documentation:[/b]\n{symbol.documentation}")
        
        return "\n".join(lines)
    
    def _format_relationships(self) -> str:
        """Format relationships section."""
        lines = ["[b]Relationships:[/b]"]
        
        for rel in self.memory_unit.relationships[:20]:  # Limit to 20
            direction = "→" if rel.source_id == self.memory_unit.id else "←"
            lines.append(f"  {direction} [{rel.relation_type.value}] {rel.target_id}")
        
        if len(self.memory_unit.relationships) > 20:
            lines.append(f"  ... and {len(self.memory_unit.relationships) - 20} more")
        
        return "\n".join(lines)
    
    def _format_content(self) -> str:
        """Format content preview."""
        content = self.memory_unit.content
        
        # Limit content length
        max_length = 2000
        if len(content) > max_length:
            content = content[:max_length] + "\n... [truncated]"
        
        return f"[b]Content:[/b]\n```\n{content}\n```"
    
    def _format_metadata(self) -> str:
        """Format metadata section."""
        lines = ["[b]Metadata:[/b]"]
        
        for key, value in self.memory_unit.metadata.items():
            lines.append(f"  {key}: {value}")
        
        if self.memory_unit.keywords:
            lines.append(f"  [b]Keywords:[/b] {', '.join(self.memory_unit.keywords)}")
        
        if self.memory_unit.embeddings:
            lines.append(f"  [b]Embeddings:[/b] {len(self.memory_unit.embeddings)} dimensions")
        
        return "\n".join(lines)
