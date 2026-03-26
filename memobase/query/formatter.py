"""
Response formatter implementation.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from memobase.core.exceptions import QueryError
from memobase.core.models import MemoryUnit, Query, Response, QueryType


class ResponseFormatter:
    """Formats query responses for different output formats."""
    
    def __init__(self) -> None:
        """Initialize response formatter."""
        self.output_formats = ['text', 'json', 'table', 'markdown']
    
    def format_response(self, response: Response, output_format: str = 'text', 
                       query: Query = None, include_metadata: bool = True) -> str:
        """Format response in specified format.
        
        Args:
            response: Response to format
            output_format: Output format ('text', 'json', 'table', 'markdown')
            query: Original query (for context)
            include_metadata: Whether to include metadata
            
        Returns:
            Formatted response string
        """
        try:
            if output_format not in self.output_formats:
                raise QueryError(f"Unsupported output format: {output_format}")
            
            formatter_method = getattr(self, f'_format_{output_format}')
            return formatter_method(response, query, include_metadata)
            
        except Exception as e:
            raise QueryError(f"Response formatting failed: {str(e)}")
    
    def format_memory_unit(self, unit: MemoryUnit, output_format: str = 'text') -> str:
        """Format a single memory unit.
        
        Args:
            unit: Memory unit to format
            output_format: Output format
            
        Returns:
            Formatted memory unit string
        """
        try:
            if output_format not in self.output_formats:
                raise QueryError(f"Unsupported output format: {output_format}")
            
            formatter_method = getattr(self, f'_format_unit_{output_format}')
            return formatter_method(unit)
            
        except Exception as e:
            raise QueryError(f"Memory unit formatting failed: {str(e)}")
    
    def format_error(self, error_message: str, output_format: str = 'text') -> str:
        """Format error message.
        
        Args:
            error_message: Error message to format
            output_format: Output format
            
        Returns:
            Formatted error string
        """
        try:
            if output_format == 'json':
                return json.dumps({
                    'error': True,
                    'message': error_message,
                    'timestamp': datetime.utcnow().isoformat()
                }, indent=2)
            elif output_format == 'markdown':
                return f"## Error\n\n{error_message}"
            else:
                return f"Error: {error_message}"
                
        except Exception as e:
            return f"Formatting error: {str(e)}"
    
    def _format_text(self, response: Response, query: Query = None, include_metadata: bool = True) -> str:
        """Format response as plain text."""
        lines = []
        
        # Header
        if query:
            lines.append(f"Query: {query.text}")
            lines.append(f"Type: {query.query_type.value}")
            lines.append("")
        
        # Results summary
        lines.append(f"Found {response.total_count} results")
        if response.total_count != len(response.results):
            lines.append(f"Showing {len(response.results)} results")
        lines.append("")
        
        # Results
        for i, result in enumerate(response.results, 1):
            lines.append(f"{i}. {self._format_unit_summary(result)}")
            lines.append("")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append("Metadata:")
            for key, value in response.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        # Performance
        lines.append(f"Execution time: {response.execution_time_ms:.2f}ms")
        
        return "\n".join(lines)
    
    def _format_json(self, response: Response, query: Query = None, include_metadata: bool = True) -> str:
        """Format response as JSON."""
        data = {
            'query_id': response.query_id,
            'total_count': response.total_count,
            'execution_time_ms': response.execution_time_ms,
            'results': [self._unit_to_dict(result) for result in response.results],
        }
        
        if query:
            data['query'] = {
                'text': query.text,
                'type': query.query_type.value,
                'filters': query.filters,
                'limit': query.limit,
                'offset': query.offset,
            }
        
        if include_metadata:
            data['metadata'] = response.metadata
        
        return json.dumps(data, indent=2, default=str)
    
    def _format_table(self, response: Response, query: Query = None, include_metadata: bool = True) -> str:
        """Format response as table."""
        lines = []
        
        # Header
        if query:
            lines.append(f"Query: {query.text}")
            lines.append(f"Results: {response.total_count} found, {len(response.results)} shown")
            lines.append("")
        
        # Table header
        lines.append(f"{'#':<4} {'Name':<30} {'Type':<12} {'File':<40} {'Line':<6}")
        lines.append("-" * 92)
        
        # Table rows
        for i, result in enumerate(response.results, 1):
            name = result.symbol.name if result.symbol else "N/A"
            symbol_type = result.symbol.symbol_type.value if result.symbol else "N/A"
            file_name = result.file_path.name if result.file_path else "N/A"
            line_num = str(result.symbol.line_start) if result.symbol else "N/A"
            
            # Truncate if too long
            name = name[:27] + "..." if len(name) > 30 else name
            file_name = file_name[:37] + "..." if len(file_name) > 40 else file_name
            
            lines.append(f"{i:<4} {name:<30} {symbol_type:<12} {file_name:<40} {line_num:<6}")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append("")
            lines.append("Metadata:")
            for key, value in response.metadata.items():
                lines.append(f"  {key}: {value}")
        
        return "\n".join(lines)
    
    def _format_markdown(self, response: Response, query: Query = None, include_metadata: bool = True) -> str:
        """Format response as Markdown."""
        lines = []
        
        # Header
        if query:
            lines.append(f"# Query Results")
            lines.append("")
            lines.append(f"**Query:** `{query.text}`")
            lines.append(f"**Type:** {query.query_type.value}")
            lines.append("")
        
        # Results summary
        lines.append(f"**Found {response.total_count} results**")
        if response.total_count != len(response.results):
            lines.append(f"Showing {len(response.results)} results")
        lines.append("")
        
        # Results
        for i, result in enumerate(response.results, 1):
            lines.append(f"## {i}. {self._format_unit_title(result)}")
            lines.append("")
            
            # Unit details
            if result.symbol:
                lines.append(f"- **Type:** {result.symbol.symbol_type.value}")
                lines.append(f"- **Location:** Line {result.symbol.line_start}")
                if result.symbol.documentation:
                    lines.append(f"- **Description:** {result.symbol.documentation}")
            
            lines.append(f"- **File:** `{result.file_path}`")
            
            # Content preview
            if result.content:
                preview = result.content[:200] + "..." if len(result.content) > 200 else result.content
                lines.append("")
                lines.append("```")
                lines.append(preview)
                lines.append("```")
            
            lines.append("")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append("## Metadata")
            lines.append("")
            for key, value in response.metadata.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")
        
        # Performance
        lines.append(f"*Execution time: {response.execution_time_ms:.2f}ms*")
        
        return "\n".join(lines)
    
    def _format_unit_text(self, unit: MemoryUnit) -> str:
        """Format memory unit as text."""
        lines = []
        
        if unit.symbol:
            lines.append(f"{unit.symbol.name} ({unit.symbol.symbol_type.value})")
            lines.append(f"Location: {unit.file_path}:{unit.symbol.line_start}")
            if unit.symbol.documentation:
                lines.append(f"Description: {unit.symbol.documentation}")
        else:
            lines.append(f"File: {unit.file_path}")
        
        if unit.content:
            preview = unit.content[:300] + "..." if len(unit.content) > 300 else unit.content
            lines.append("")
            lines.append("Content:")
            lines.append(preview)
        
        return "\n".join(lines)
    
    def _format_unit_json(self, unit: MemoryUnit) -> str:
        """Format memory unit as JSON."""
        return json.dumps(self._unit_to_dict(unit), indent=2, default=str)
    
    def _format_unit_table(self, unit: MemoryUnit) -> str:
        """Format memory unit as table row."""
        name = unit.symbol.name if unit.symbol else "N/A"
        symbol_type = unit.symbol.symbol_type.value if unit.symbol else "N/A"
        file_name = unit.file_path.name if unit.file_path else "N/A"
        line_num = str(unit.symbol.line_start) if unit.symbol else "N/A"
        
        return f"{name:<30} {symbol_type:<12} {file_name:<40} {line_num:<6}"
    
    def _format_unit_markdown(self, unit: MemoryUnit) -> str:
        """Format memory unit as Markdown."""
        lines = []
        
        if unit.symbol:
            lines.append(f"## {unit.symbol.name}")
            lines.append("")
            lines.append(f"- **Type:** {unit.symbol.symbol_type.value}")
            lines.append(f"- **Location:** {unit.file_path}:{unit.symbol.line_start}")
            if unit.symbol.documentation:
                lines.append(f"- **Description:** {unit.symbol.documentation}")
        else:
            lines.append(f"## {unit.file_path.name}")
            lines.append("")
            lines.append(f"- **File:** `{unit.file_path}`")
        
        if unit.content:
            preview = unit.content[:200] + "..." if len(unit.content) > 200 else unit.content
            lines.append("")
            lines.append("```")
            lines.append(preview)
            lines.append("```")
        
        return "\n".join(lines)
    
    def _format_unit_summary(self, unit: MemoryUnit) -> str:
        """Format memory unit summary."""
        if unit.symbol:
            name = unit.symbol.name
            symbol_type = unit.symbol.symbol_type.value
            location = f"{unit.file_path.name}:{unit.symbol.line_start}"
            return f"{name} ({symbol_type}) at {location}"
        else:
            return f"File: {unit.file_path}"
    
    def _format_unit_title(self, unit: MemoryUnit) -> str:
        """Format memory unit title."""
        if unit.symbol:
            return f"{unit.symbol.name} ({unit.symbol.symbol_type.value})"
        else:
            return unit.file_path.name
    
    def _unit_to_dict(self, unit: MemoryUnit) -> Dict:
        """Convert memory unit to dictionary."""
        data = {
            'id': unit.id,
            'file_path': str(unit.file_path),
            'keywords': unit.keywords,
            'metadata': unit.metadata,
            'created_at': unit.created_at.isoformat(),
            'updated_at': unit.updated_at.isoformat(),
        }
        
        if unit.symbol:
            data['symbol'] = {
                'name': unit.symbol.name,
                'type': unit.symbol.symbol_type.value,
                'line_start': unit.symbol.line_start,
                'line_end': unit.symbol.line_end,
                'documentation': unit.symbol.documentation,
                'signature': unit.symbol.signature,
                'parameters': unit.symbol.parameters,
                'return_type': unit.symbol.return_type,
            }
        
        if unit.content:
            # Include content preview
            data['content_preview'] = unit.content[:500] + "..." if len(unit.content) > 500 else unit.content
        
        return data


class InteractiveFormatter(ResponseFormatter):
    """Interactive formatter with color and formatting."""
    
    def __init__(self, use_colors: bool = True) -> None:
        """Initialize interactive formatter."""
        super().__init__()
        self.use_colors = use_colors
        self.colors = self._init_colors() if use_colors else {}
    
    def format_response(self, response: Response, output_format: str = 'text', 
                       query: Query = None, include_metadata: bool = True) -> str:
        """Format response with interactive features."""
        if output_format == 'text' and self.use_colors:
            return self._format_colored_text(response, query, include_metadata)
        else:
            return super().format_response(response, output_format, query, include_metadata)
    
    def _format_colored_text(self, response: Response, query: Query = None, include_metadata: bool = True) -> str:
        """Format response with colors."""
        lines = []
        
        # Query header
        if query:
            lines.append(f"{self.colors['cyan']}Query:{self.colors['reset']} {query.text}")
            lines.append(f"{self.colors['cyan']}Type:{self.colors['reset']} {query.query_type.value}")
            lines.append("")
        
        # Results summary
        count_color = self.colors['green'] if response.total_count > 0 else self.colors['red']
        lines.append(f"{count_color}Found {response.total_count} results{self.colors['reset']}")
        if response.total_count != len(response.results):
            lines.append(f"Showing {len(response.results)} results")
        lines.append("")
        
        # Results
        for i, result in enumerate(response.results, 1):
            lines.append(f"{self.colors['yellow']}{i}.{self.colors['reset']} {self._format_unit_colored(result)}")
            lines.append("")
        
        # Metadata
        if include_metadata and response.metadata:
            lines.append(f"{self.colors['cyan']}Metadata:{self.colors['reset']}")
            for key, value in response.metadata.items():
                lines.append(f"  {self.colors['white']}{key}:{self.colors['reset']} {value}")
            lines.append("")
        
        # Performance
        perf_color = self.colors['green'] if response.execution_time_ms < 100 else self.colors['yellow']
        lines.append(f"{perf_color}Execution time: {response.execution_time_ms:.2f}ms{self.colors['reset']}")
        
        return "\n".join(lines)
    
    def _format_unit_colored(self, unit: MemoryUnit) -> str:
        """Format memory unit with colors."""
        parts = []
        
        if unit.symbol:
            # Symbol name and type
            name_color = self.colors['blue']
            type_color = self.colors['magenta']
            parts.append(f"{name_color}{unit.symbol.name}{self.colors['reset']} ({type_color}{unit.symbol.symbol_type.value}{self.colors['reset']})")
            
            # Location
            location_color = self.colors['cyan']
            parts.append(f"at {location_color}{unit.file_path.name}:{unit.symbol.line_start}{self.colors['reset']}")
            
            # Documentation
            if unit.symbol.documentation:
                doc_color = self.colors['white']
                doc_preview = unit.symbol.documentation[:100] + "..." if len(unit.symbol.documentation) > 100 else unit.symbol.documentation
                parts.append(f"{doc_color}{doc_preview}{self.colors['reset']}")
        else:
            # File
            file_color = self.colors['cyan']
            parts.append(f"{file_color}File:{self.colors['reset']} {unit.file_path}")
        
        return " | ".join(parts)
    
    def _init_colors(self) -> Dict[str, str]:
        """Initialize ANSI color codes."""
        return {
            'reset': '\033[0m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
        }
