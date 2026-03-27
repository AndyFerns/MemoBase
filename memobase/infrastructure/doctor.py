"""
System doctor module for MemoBase.

Handles system health diagnostics and issue fixing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from memobase.core.models import Config
from memobase.storage.file_storage import FileStorage


class SystemDoctor:
    """Handles system diagnostics and health checks."""
    
    def __init__(self, config: Config) -> None:
        """Initialize system doctor.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.storage = FileStorage(config.repo_path / config.storage_path)
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run system diagnostics.
        
        Returns:
            Health report dictionary
        """
        issues = []
        recommendations = []
        
        # Check storage directory
        storage_path = self.config.repo_path / self.config.storage_path
        if not storage_path.exists():
            issues.append("Storage directory does not exist")
            recommendations.append("Run 'memobase init' to initialize the project")
        
        # Check index exists
        index_data = self.storage.load("index/main")
        if not index_data:
            issues.append("No index found")
            recommendations.append("Run 'memobase build' to build the memory index")
        
        # Check graph exists
        graph_data = self.storage.load("graph/main")
        if not graph_data:
            issues.append("No graph data found")
            recommendations.append("Run 'memobase build' to build the relationship graph")
        
        # Check memory units
        memory_keys = self.storage.list_keys("memory/")
        if not memory_keys:
            issues.append("No memory units found")
            recommendations.append("Run 'memobase build' to analyze your codebase")
        
        # Determine overall status
        if not issues:
            overall_status = "healthy"
        elif len(issues) <= 2:
            overall_status = "warning"
        else:
            overall_status = "critical"
        
        return {
            'overall_status': overall_status,
            'issues': issues,
            'recommendations': recommendations,
            'storage_path': str(storage_path),
            'index_exists': index_data is not None,
            'graph_exists': graph_data is not None,
            'memory_count': len(memory_keys),
        }
    
    def fix_issues(self, issues: List[str]) -> List[str]:
        """Attempt to fix detected issues.
        
        Args:
            issues: List of issues to fix
            
        Returns:
            List of fixed issues
        """
        fixed = []
        
        for issue in issues:
            if "Storage directory does not exist" in issue:
                # Create storage directory
                storage_path = self.config.repo_path / self.config.storage_path
                storage_path.mkdir(parents=True, exist_ok=True)
                (storage_path / "index").mkdir(exist_ok=True)
                (storage_path / "graph").mkdir(exist_ok=True)
                (storage_path / "memory").mkdir(exist_ok=True)
                (storage_path / "cache").mkdir(exist_ok=True)
                fixed.append(issue)
        
        return fixed
