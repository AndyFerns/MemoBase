"""
Code analyzer implementation.
"""

from __future__ import annotations

import asyncio
import re
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from typing import Dict, List, Set

from memobase.core.exceptions import QueryError
from memobase.core.interfaces import AnalysisInterface
from memobase.core.models import Findings, MemoryUnit, SymbolType


class CodeAnalyzer(AnalysisInterface):
    """Advanced code analysis with multiple detection algorithms."""
    
    def __init__(self, config=None) -> None:
        """Initialize code analyzer.
        
        Args:
            config: Optional project configuration
        """
        self.config = config
        self.analysis_patterns = self._init_analysis_patterns()
        self.severity_weights = {
            'critical': 1.0,
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4,
            'info': 0.2,
        }
    
    def analyze(self, memory_units: List[MemoryUnit]) -> List[Findings]:
        """Analyze memory units and generate findings."""
        try:
            findings = []
            
            for unit in memory_units:
                unit_findings = self._analyze_memory_unit(unit)
                findings.extend(unit_findings)
            
            return findings
            
        except Exception as e:
            raise QueryError(f"Code analysis failed: {str(e)}")
    
    def detect_patterns(self, memory_units: List[MemoryUnit]) -> Dict[str, List[MemoryUnit]]:
        """Detect common patterns in code."""
        try:
            patterns = defaultdict(list)
            
            for unit in memory_units:
                detected_patterns = self._detect_unit_patterns(unit)
                for pattern_name in detected_patterns:
                    patterns[pattern_name].append(unit)
            
            return dict(patterns)
            
        except Exception as e:
            raise QueryError(f"Pattern detection failed: {str(e)}")
    
    def calculate_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate code metrics."""
        try:
            metrics = {}
            
            # Basic metrics
            metrics['total_units'] = len(memory_units)
            metrics['files_analyzed'] = len(set(str(unit.file_path) for unit in memory_units))
            
            # Symbol distribution
            symbol_counts = Counter()
            for unit in memory_units:
                if unit.symbol:
                    symbol_counts[unit.symbol.symbol_type.value] += 1
            
            for symbol_type, count in symbol_counts.items():
                metrics[f'{symbol_type}_count'] = count
            
            # Complexity metrics
            metrics['avg_complexity'] = self._calculate_avg_complexity(memory_units)
            metrics['max_complexity'] = self._calculate_max_complexity(memory_units)
            
            # Size metrics
            metrics['avg_content_length'] = self._calculate_avg_content_length(memory_units)
            metrics['total_content_length'] = sum(len(unit.content or '') for unit in memory_units)
            
            # Relationship metrics
            metrics['avg_relationships'] = self._calculate_avg_relationships(memory_units)
            metrics['total_relationships'] = sum(len(unit.relationships) for unit in memory_units)
            
            return metrics
            
        except Exception as e:
            raise QueryError(f"Metrics calculation failed: {str(e)}")
    
    async def analyze_async(self, memory_units: List[MemoryUnit]) -> List[Findings]:
        """Async version of analyze."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.analyze, memory_units)
    
    def _analyze_memory_unit(self, unit: MemoryUnit) -> List[Findings]:
        """Analyze a single memory unit."""
        findings = []
        
        if not unit.content:
            return findings
        
        # Security analysis
        security_findings = self._security_analysis(unit)
        findings.extend(security_findings)
        
        # Code quality analysis
        quality_findings = self._quality_analysis(unit)
        findings.extend(quality_findings)
        
        # Performance analysis
        performance_findings = self._performance_analysis(unit)
        findings.extend(performance_findings)
        
        # Maintainability analysis
        maintainability_findings = self._maintainability_analysis(unit)
        findings.extend(maintainability_findings)
        
        return findings
    
    def _security_analysis(self, unit: MemoryUnit) -> List[Findings]:
        """Perform security analysis."""
        findings = []
        
        # Check for security vulnerabilities
        security_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*\%.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
            ],
            'command_injection': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'path_traversal': [
                r'open\s*\(\s*["\'].*\.\.',
                r'file\s*\(\s*["\'].*\.\.',
                r'read\s*\(\s*["\'].*\.\.',
            ],
        }
        
        for vulnerability, patterns in security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, unit.content, re.IGNORECASE)
                for match in matches:
                    line_number = self._get_line_number(unit.content, match.start())
                    
                    finding = Findings(
                        id=f"security_{vulnerability}_{unit.id}_{line_number}",
                        analysis_type="security",
                        file_path=unit.file_path,
                        line_number=line_number,
                        severity="critical",
                        message=f"Potential {vulnerability.replace('_', ' ')} vulnerability",
                        suggestion=f"Use parameterized queries or proper input validation",
                        code_snippet=self._get_code_snippet(unit.content, line_number),
                        confidence=0.8
                    )
                    findings.append(finding)
        
        return findings
    
    def _quality_analysis(self, unit: MemoryUnit) -> List[Findings]:
        """Perform code quality analysis."""
        findings = []
        
        # Check for code smells
        quality_patterns = {
            'long_function': [
                (r'def\s+\w+\s*\([^)]*\)\s*:', 50),  # Function definition
                (r'function\s+\w+\s*\([^)]*\)\s*{', 50),  # JavaScript function
            ],
            'deep_nesting': [
                (r'\s{16,}', 1),  # Deep indentation
            ],
            'large_class': [
                (r'class\s+\w+', 20),  # Many methods in class
            ],
            'duplicate_code': [
                (r'.+', 2),  # Will be checked separately
            ],
        }
        
        for smell, patterns in quality_patterns.items():
            for pattern, threshold in patterns:
                matches = list(re.finditer(pattern, unit.content))
                
                if smell == 'long_function':
                    for match in matches:
                        # Check function length
                        func_start = match.start()
                        func_end = self._find_function_end(unit.content, func_start)
                        if func_end > func_start:
                            func_lines = unit.content[func_start:func_end].count('\n')
                            if func_lines > threshold:
                                line_number = self._get_line_number(unit.content, func_start)
                                
                                finding = Findings(
                                    id=f"quality_{smell}_{unit.id}_{line_number}",
                                    analysis_type="quality",
                                    file_path=unit.file_path,
                                    line_number=line_number,
                                    severity="medium",
                                    message=f"Long function ({func_lines} lines)",
                                    suggestion="Consider breaking this function into smaller functions",
                                    code_snippet=self._get_code_snippet(unit.content, line_number),
                                    confidence=0.7
                                )
                                findings.append(finding)
                
                elif smell == 'deep_nesting':
                    deep_lines = [self._get_line_number(unit.content, m.start()) for m in matches]
                    for line_number in deep_lines:
                        finding = Findings(
                            id=f"quality_{smell}_{unit.id}_{line_number}",
                            analysis_type="quality",
                            file_path=unit.file_path,
                            line_number=line_number,
                            severity="low",
                            message="Deep nesting detected",
                            suggestion="Consider refactoring to reduce nesting level",
                            code_snippet=self._get_code_snippet(unit.content, line_number),
                            confidence=0.6
                        )
                        findings.append(finding)
        
        return findings
    
    def _performance_analysis(self, unit: MemoryUnit) -> List[Findings]:
        """Perform performance analysis."""
        findings = []
        
        # Check for performance issues
        performance_patterns = {
            'inefficient_loops': [
                r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
                r'while\s+.*\.pop\s*\(\s*0\s*\)',
            ],
            'memory_leaks': [
                r'global\s+\w+',
                r'\w+\s*\[\s*\]\s*=.*\[\s*\]',  # List comprehension in loop
            ],
            'slow_operations': [
                r'\.sort\s*\(\s*\)',  # In-place sort
                r'regex\s*=\s*re\.compile',  # Regex in loop
            ],
        }
        
        for issue, patterns in performance_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, unit.content, re.IGNORECASE)
                for match in matches:
                    line_number = self._get_line_number(unit.content, match.start())
                    
                    finding = Findings(
                        id=f"performance_{issue}_{unit.id}_{line_number}",
                        analysis_type="performance",
                        file_path=unit.file_path,
                        line_number=line_number,
                        severity="medium",
                        message=f"Potential performance issue: {issue.replace('_', ' ')}",
                        suggestion="Consider optimizing this code pattern",
                        code_snippet=self._get_code_snippet(unit.content, line_number),
                        confidence=0.6
                    )
                    findings.append(finding)
        
        return findings
    
    def _maintainability_analysis(self, unit: MemoryUnit) -> List[Findings]:
        """Perform maintainability analysis."""
        findings = []
        
        # Check for maintainability issues
        maintainability_patterns = {
            'missing_documentation': [
                (r'def\s+\w+\s*\([^)]*\)\s*:', r'def\s+\w+\s*\([^)]*\)\s*:.*""".*?"""'),
                (r'class\s+\w+\s*:', r'class\s+\w+\s*:.*""".*?"""'),
            ],
            'complex_expressions': [
                r'\w+\s*[+\-*/]\s*\w+\s*[+\-*/]\s*\w+\s*[+\-*/]\s*\w+',
            ],
            'magic_numbers': [
                r'\b(?!0|1)\d{2,}\b',  # Numbers >= 100 (excluding 0 and 1)
            ],
        }
        
        for issue, patterns in maintainability_patterns.items():
            if issue == 'missing_documentation':
                for pattern, doc_pattern in patterns:
                    func_matches = re.finditer(pattern, unit.content, re.MULTILINE)
                    for match in func_matches:
                        # Check if documentation exists
                        func_start = match.start()
                        func_end = self._find_function_end(unit.content, func_start)
                        func_content = unit.content[func_start:func_end]
                        
                        if not re.search(doc_pattern, func_content, re.DOTALL):
                            line_number = self._get_line_number(unit.content, func_start)
                            
                            finding = Findings(
                                id=f"maintainability_{issue}_{unit.id}_{line_number}",
                                analysis_type="maintainability",
                                file_path=unit.file_path,
                                line_number=line_number,
                                severity="low",
                                message="Missing documentation",
                                suggestion="Add docstring to improve code documentation",
                                code_snippet=self._get_code_snippet(unit.content, line_number),
                                confidence=0.8
                            )
                            findings.append(finding)
            
            else:
                for pattern in patterns:
                    matches = re.finditer(pattern, unit.content)
                    for match in matches:
                        line_number = self._get_line_number(unit.content, match.start())
                        
                        finding = Findings(
                            id=f"maintainability_{issue}_{unit.id}_{line_number}",
                            analysis_type="maintainability",
                            file_path=unit.file_path,
                            line_number=line_number,
                            severity="low",
                            message=f"Maintainability issue: {issue.replace('_', ' ')}",
                            suggestion="Consider refactoring for better maintainability",
                            code_snippet=self._get_code_snippet(unit.content, line_number),
                            confidence=0.5
                        )
                        findings.append(finding)
        
        return findings
    
    def _detect_unit_patterns(self, unit: MemoryUnit) -> List[str]:
        """Detect patterns in a single memory unit."""
        patterns = []
        
        if not unit.content:
            return patterns
        
        # Design patterns
        if re.search(r'class\s+\w+\s*\([^)]*\)\s*:.*def\s+__init__', unit.content, re.DOTALL):
            patterns.append('constructor_pattern')
        
        if re.search(r'class\s+\w+\s*\(.*\w+Interface.*\)\s*:', unit.content):
            patterns.append('interface_pattern')
        
        if re.search(r'class\s+\w+\s*\(.*\w+Exception.*\)\s*:', unit.content):
            patterns.append('exception_pattern')
        
        # Architectural patterns
        if re.search(r'def\s+singleton\s*\(', unit.content):
            patterns.append('singleton_pattern')
        
        if re.search(r'def\s+factory\s*\(', unit.content):
            patterns.append('factory_pattern')
        
        if re.search(r'def\s+observer\s*\(', unit.content):
            patterns.append('observer_pattern')
        
        # Code organization patterns
        if unit.symbol and unit.symbol.symbol_type == SymbolType.CLASS:
            method_count = len([r for r in unit.relationships if r.relation_type.value == 'contains'])
            if method_count > 10:
                patterns.append('large_class')
        
        # Complexity patterns
        if unit.content.count('if ') > 5:
            patterns.append('complex_conditional')
        
        if unit.content.count('for ') > 3:
            patterns.append('nested_loops')
        
        return patterns
    
    def _calculate_avg_complexity(self, memory_units: List[MemoryUnit]) -> float:
        """Calculate average complexity."""
        complexities = []
        
        for unit in memory_units:
            if unit.content:
                # Simple complexity metric based on control structures
                complexity = (unit.content.count('if ') + 
                           unit.content.count('for ') + 
                           unit.content.count('while ') + 
                           unit.content.count('try ') * 2)
                complexities.append(complexity)
        
        return sum(complexities) / len(complexities) if complexities else 0.0
    
    def _calculate_max_complexity(self, memory_units: List[MemoryUnit]) -> float:
        """Calculate maximum complexity."""
        max_complexity = 0.0
        
        for unit in memory_units:
            if unit.content:
                complexity = (unit.content.count('if ') + 
                           unit.content.count('for ') + 
                           unit.content.count('while ') + 
                           unit.content.count('try ') * 2)
                max_complexity = max(max_complexity, complexity)
        
        return max_complexity
    
    def _calculate_avg_content_length(self, memory_units: List[MemoryUnit]) -> float:
        """Calculate average content length."""
        lengths = [len(unit.content or '') for unit in memory_units]
        return sum(lengths) / len(lengths) if lengths else 0.0
    
    def _calculate_avg_relationships(self, memory_units: List[MemoryUnit]) -> float:
        """Calculate average number of relationships."""
        relationship_counts = [len(unit.relationships) for unit in memory_units]
        return sum(relationship_counts) / len(relationship_counts) if relationship_counts else 0.0
    
    def _get_line_number(self, content: str, position: int) -> int:
        """Get line number for position in content."""
        return content[:position].count('\n') + 1
    
    def _get_code_snippet(self, content: str, line_number: int, context: int = 2) -> str:
        """Get code snippet around line number."""
        lines = content.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        
        snippet_lines = lines[start:end]
        return '\n'.join(snippet_lines)
    
    def _find_function_end(self, content: str, start_pos: int) -> int:
        """Find end of function (simplified)."""
        lines = content[start_pos:].split('\n')
        
        # Simple heuristic: function ends when indentation drops back
        base_indent = len(lines[0]) - len(lines[0].lstrip())
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip() and len(line) - len(line.lstrip()) <= base_indent:
                return start_pos + sum(len(l) + 1 for l in lines[:i])
        
        return len(content)
    
    def _init_analysis_patterns(self) -> Dict[str, List[str]]:
        """Initialize analysis patterns."""
        return {
            'security': [
                r'execute\s*\(',
                r'eval\s*\(',
                r'exec\s*\(',
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
            ],
            'performance': [
                r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
                r'while\s+.*\.pop\s*\(\s*0\s*\)',
                r'\.sort\s*\(\s*\)',
            ],
            'quality': [
                r'\s{16,}',  # Deep indentation
                r'def\s+\w+\s*\([^)]*\)\s*:',
                r'class\s+\w+\s*:',
            ],
            'maintainability': [
                r'def\s+\w+\s*\([^)]*\)\s*:',
                r'class\s+\w+\s*:',
                r'\b(?!0|1)\d{2,}\b',  # Magic numbers
            ],
        }
