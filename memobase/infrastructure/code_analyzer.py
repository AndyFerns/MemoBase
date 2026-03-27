"""
Code analyzer module for MemoBase.

Handles code quality and security analysis.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from memobase.core.models import Config, Findings, AnalysisType, SeverityLevel
from memobase.analysis.code_analyzer import CodeAnalyzer as CoreCodeAnalyzer
from memobase.analysis.pattern_detector import PatternDetector
from memobase.analysis.metrics import MetricsCalculator
from memobase.storage.file_storage import FileStorage


class CodeAnalyzer:
    """Handles code analysis for the codebase."""
    
    def __init__(self, config: Config) -> None:
        """Initialize code analyzer.
        
        Args:
            config: Project configuration
        """
        self.config = config
        self.storage = FileStorage(config.repo_path / config.storage_path)
        self.core_analyzer = CoreCodeAnalyzer(config)
        self.pattern_detector = PatternDetector(config)
        self.metrics_calculator = MetricsCalculator(config)
    
    def analyze_repo(self, analysis_type: str = "all") -> List[Findings]:
        """Analyze the repository.
        
        Args:
            analysis_type: Type of analysis (all, security, quality, performance)
            
        Returns:
            List of findings
        """
        # Load memory units
        memory_units = self._load_memory_units()
        
        if not memory_units:
            return []
        
        all_findings = []
        
        # Run analysis based on type
        if analysis_type in ("all", "security"):
            findings = self._analyze_security(memory_units)
            all_findings.extend(findings)
        
        if analysis_type in ("all", "quality"):
            findings = self._analyze_quality(memory_units)
            all_findings.extend(findings)
        
        if analysis_type in ("all", "performance"):
            findings = self._analyze_performance(memory_units)
            all_findings.extend(findings)
        
        if analysis_type in ("all", "maintainability"):
            findings = self._analyze_maintainability(memory_units)
            all_findings.extend(findings)
        
        return all_findings
    
    def _load_memory_units(self) -> List[Any]:
        """Load memory units from storage."""
        units = []
        
        # List all memory keys
        keys = self.storage.list_keys("memory/")
        
        for key in keys:
            data = self.storage.load(key)
            if data:
                from memobase.core.models import MemoryUnit
                try:
                    units.append(MemoryUnit(**data))
                except Exception:
                    pass
        
        return units
    
    def _analyze_security(self, memory_units: List[Any]) -> List[Findings]:
        """Analyze security issues."""
        findings = []
        
        for unit in memory_units:
            unit_findings = self.core_analyzer.analyze_memory_unit(unit)
            for finding in unit_findings:
                if finding.analysis_type == AnalysisType.SECURITY:
                    findings.append(finding)
        
        return findings
    
    def _analyze_quality(self, memory_units: List[Any]) -> List[Findings]:
        """Analyze code quality issues."""
        findings = []
        
        for unit in memory_units:
            unit_findings = self.core_analyzer.analyze_memory_unit(unit)
            for finding in unit_findings:
                if finding.analysis_type == AnalysisType.QUALITY:
                    findings.append(finding)
        
        return findings
    
    def _analyze_performance(self, memory_units: List[Any]) -> List[Findings]:
        """Analyze performance issues."""
        findings = []
        
        for unit in memory_units:
            unit_findings = self.core_analyzer.analyze_memory_unit(unit)
            for finding in unit_findings:
                if finding.analysis_type == AnalysisType.PERFORMANCE:
                    findings.append(finding)
        
        return findings
    
    def _analyze_maintainability(self, memory_units: List[Any]) -> List[Findings]:
        """Analyze maintainability issues."""
        findings = []
        
        for unit in memory_units:
            unit_findings = self.core_analyzer.analyze_memory_unit(unit)
            for finding in unit_findings:
                if finding.analysis_type == AnalysisType.MAINTAINABILITY:
                    findings.append(finding)
        
        return findings
