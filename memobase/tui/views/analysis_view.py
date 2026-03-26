"""
Analysis view for TUI.

Input: Findings[]
"""

from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Static

from memobase.core.models import Findings


class AnalysisView(Widget):
    """View for displaying code analysis results."""
    
    DEFAULT_CSS = """
    AnalysisView {
        width: 100%;
        height: 100%;
        padding: 1;
    }
    
    AnalysisView .summary {
        margin: 1 0;
        padding: 1;
        background: $surface-darken-1;
    }
    
    AnalysisView .finding {
        margin: 1 0;
        padding: 1;
        border: solid;
    }
    
    AnalysisView .finding-critical {
        border-color: $error;
        background: $error-darken-3;
    }
    
    AnalysisView .finding-high {
        border-color: $warning;
        background: $warning-darken-3;
    }
    
    AnalysisView .finding-medium {
        border-color: $primary;
        background: $primary-darken-3;
    }
    
    AnalysisView .finding-low {
        border-color: $success;
        background: $success-darken-3;
    }
    
    AnalysisView .finding-info {
        border-color: $text-disabled;
        background: $surface-darken-2;
    }
    """
    
    def __init__(self, findings: list[Findings], **kwargs) -> None:
        """Initialize analysis view.
        
        Args:
            findings: List of analysis findings
        """
        super().__init__(**kwargs)
        self.findings = findings
    
    def compose(self):
        """Compose analysis view."""
        # Summary
        yield Static(self._format_summary(), classes="summary")
        
        # Findings list
        if not self.findings:
            yield Static("No findings. Your code looks great! ✓")
        else:
            # Sort by severity
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
            sorted_findings = sorted(
                self.findings,
                key=lambda f: severity_order.get(f.severity, 5)
            )
            
            # Display findings
            for finding in sorted_findings[:100]:  # Limit to 100 findings
                severity_class = f"finding-{finding.severity}"
                yield Static(self._format_finding(finding), classes=f"finding {severity_class}")
            
            if len(sorted_findings) > 100:
                yield Static(f"... and {len(sorted_findings) - 100} more findings")
    
    def _format_summary(self) -> str:
        """Format findings summary."""
        if not self.findings:
            return "[b]Analysis Summary:[/b] No issues found"
        
        # Count by severity
        severity_counts = {}
        for finding in self.findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1
        
        lines = [f"[b]Analysis Summary:[/b] {len(self.findings)} total findings"]
        
        for severity, count in sorted(severity_counts.items()):
            color = self._severity_to_color(severity)
            lines.append(f"  [{color}]{severity.upper()}:[/{color}] {count}")
        
        return "\n".join(lines)
    
    def _format_finding(self, finding: Findings) -> str:
        """Format a single finding."""
        lines = [
            f"[b]{finding.analysis_type.upper()}[/b] - {finding.severity.upper()}",
            f"{finding.message}",
        ]
        
        if finding.file_path:
            location = str(finding.file_path)
            if finding.line_number > 0:
                location += f":{finding.line_number}"
            lines.append(f"  Location: {location}")
        
        if finding.suggestion:
            lines.append(f"  Suggestion: {finding.suggestion}")
        
        if finding.confidence > 0:
            lines.append(f"  Confidence: {finding.confidence:.0%}")
        
        if finding.code_snippet:
            snippet = finding.code_snippet[:200]  # Limit snippet length
            if len(finding.code_snippet) > 200:
                snippet += "..."
            lines.append(f"  Code:\n```\n{snippet}\n```")
        
        return "\n".join(lines)
    
    def _severity_to_color(self, severity: str) -> str:
        """Convert severity to color code."""
        colors = {
            "critical": "red",
            "high": "bright_red",
            "medium": "yellow",
            "low": "bright_yellow",
            "info": "blue",
        }
        return colors.get(severity, "white")
