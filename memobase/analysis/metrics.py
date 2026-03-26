"""
Metrics calculator implementation.
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Dict, List, Set

from memobase.core.exceptions import QueryError
from memobase.core.models import MemoryUnit, SymbolType


class MetricsCalculator:
    """Calculates various code metrics and statistics."""
    
    def __init__(self) -> None:
        """Initialize metrics calculator."""
        self.metric_weights = {
            'complexity': 0.3,
            'size': 0.2,
            'coupling': 0.2,
            'cohesion': 0.15,
            'maintainability': 0.15,
        }
    
    def calculate_all_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate all available metrics."""
        try:
            metrics = {}
            
            # Basic metrics
            basic_metrics = self.calculate_basic_metrics(memory_units)
            metrics.update(basic_metrics)
            
            # Complexity metrics
            complexity_metrics = self.calculate_complexity_metrics(memory_units)
            metrics.update(complexity_metrics)
            
            # Size metrics
            size_metrics = self.calculate_size_metrics(memory_units)
            metrics.update(size_metrics)
            
            # Coupling metrics
            coupling_metrics = self.calculate_coupling_metrics(memory_units)
            metrics.update(coupling_metrics)
            
            # Cohesion metrics
            cohesion_metrics = self.calculate_cohesion_metrics(memory_units)
            metrics.update(cohesion_metrics)
            
            # Maintainability metrics
            maintainability_metrics = self.calculate_maintainability_metrics(memory_units)
            metrics.update(maintainability_metrics)
            
            # Overall quality score
            metrics['overall_quality'] = self.calculate_quality_score(metrics)
            
            return metrics
            
        except Exception as e:
            raise QueryError(f"Metrics calculation failed: {str(e)}")
    
    def calculate_basic_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate basic project metrics."""
        metrics = {}
        
        # Count metrics
        metrics['total_units'] = len(memory_units)
        metrics['total_files'] = len(set(str(unit.file_path) for unit in memory_units))
        metrics['total_symbols'] = sum(1 for unit in memory_units if unit.symbol)
        
        # Symbol type distribution
        symbol_types = Counter()
        for unit in memory_units:
            if unit.symbol:
                symbol_types[unit.symbol.symbol_type.value] += 1
        
        for symbol_type, count in symbol_types.items():
            metrics[f'{symbol_type}_count'] = count
        
        # Average symbols per file
        if metrics['total_files'] > 0:
            metrics['avg_symbols_per_file'] = metrics['total_symbols'] / metrics['total_files']
        else:
            metrics['avg_symbols_per_file'] = 0.0
        
        return metrics
    
    def calculate_complexity_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate complexity metrics."""
        metrics = {}
        
        complexities = []
        cyclomatic_complexities = []
        
        for unit in memory_units:
            if unit.content:
                # Basic complexity (control structures)
                basic_complexity = (unit.content.count('if ') + 
                                  unit.content.count('for ') + 
                                  unit.content.count('while ') + 
                                  unit.content.count('try ') * 2 +
                                  unit.content.count('elif ') +
                                  unit.content.count('except '))
                complexities.append(basic_complexity)
                
                # Cyclomatic complexity (simplified)
                cc = (unit.content.count('if ') + 
                     unit.content.count('for ') + 
                     unit.content.count('while ') + 
                     unit.content.count('and ') + 
                     unit.content.count('or ') + 1)
                cyclomatic_complexities.append(cc)
        
        if complexities:
            metrics['avg_complexity'] = sum(complexities) / len(complexities)
            metrics['max_complexity'] = max(complexities)
            metrics['min_complexity'] = min(complexities)
            metrics['total_complexity'] = sum(complexities)
        else:
            metrics['avg_complexity'] = 0.0
            metrics['max_complexity'] = 0.0
            metrics['min_complexity'] = 0.0
            metrics['total_complexity'] = 0.0
        
        if cyclomatic_complexities:
            metrics['avg_cyclomatic_complexity'] = sum(cyclomatic_complexities) / len(cyclomatic_complexities)
            metrics['max_cyclomatic_complexity'] = max(cyclomatic_complexities)
        else:
            metrics['avg_cyclomatic_complexity'] = 0.0
            metrics['max_cyclomatic_complexity'] = 0.0
        
        return metrics
    
    def calculate_size_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate size-related metrics."""
        metrics = {}
        
        sizes = []
        line_counts = []
        
        for unit in memory_units:
            if unit.content:
                content_size = len(unit.content)
                line_count = unit.content.count('\n') + 1
                
                sizes.append(content_size)
                line_counts.append(line_count)
        
        if sizes:
            metrics['avg_size_bytes'] = sum(sizes) / len(sizes)
            metrics['max_size_bytes'] = max(sizes)
            metrics['min_size_bytes'] = min(sizes)
            metrics['total_size_bytes'] = sum(sizes)
            metrics['median_size_bytes'] = self._median(sizes)
        else:
            metrics['avg_size_bytes'] = 0.0
            metrics['max_size_bytes'] = 0.0
            metrics['min_size_bytes'] = 0.0
            metrics['total_size_bytes'] = 0.0
            metrics['median_size_bytes'] = 0.0
        
        if line_counts:
            metrics['avg_lines'] = sum(line_counts) / len(line_counts)
            metrics['max_lines'] = max(line_counts)
            metrics['min_lines'] = min(line_counts)
            metrics['total_lines'] = sum(line_counts)
            metrics['median_lines'] = self._median(line_counts)
        else:
            metrics['avg_lines'] = 0.0
            metrics['max_lines'] = 0.0
            metrics['min_lines'] = 0.0
            metrics['total_lines'] = 0.0
            metrics['median_lines'] = 0.0
        
        return metrics
    
    def calculate_coupling_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate coupling metrics."""
        metrics = {}
        
        # Coupling through relationships
        coupling_counts = []
        import_counts = []
        
        for unit in memory_units:
            # Count outgoing relationships
            coupling_count = len(unit.relationships)
            coupling_counts.append(coupling_count)
            
            # Count imports (proxy for external coupling)
            import_count = len(unit.metadata.get('imports', []))
            import_counts.append(import_count)
        
        if coupling_counts:
            metrics['avg_coupling'] = sum(coupling_counts) / len(coupling_counts)
            metrics['max_coupling'] = max(coupling_counts)
            metrics['total_coupling'] = sum(coupling_counts)
        else:
            metrics['avg_coupling'] = 0.0
            metrics['max_coupling'] = 0.0
            metrics['total_coupling'] = 0.0
        
        if import_counts:
            metrics['avg_imports'] = sum(import_counts) / len(import_counts)
            metrics['max_imports'] = max(import_counts)
            metrics['total_imports'] = sum(import_counts)
        else:
            metrics['avg_imports'] = 0.0
            metrics['max_imports'] = 0.0
            metrics['total_imports'] = 0.0
        
        # Afferent and efferent coupling (simplified)
        file_units = defaultdict(list)
        for unit in memory_units:
            file_units[str(unit.file_path)].append(unit)
        
        afferent_coupling = []
        efferent_coupling = []
        
        for file_path, units in file_units.items():
            # Afferent coupling: how many other files depend on this file
            afferent = 0
            # Efferent coupling: how many other files this file depends on
            efferent = set()
            
            for unit in units:
                for relationship in unit.relationships:
                    # Find target file
                    for other_unit in memory_units:
                        if other_unit.id == relationship.target_id:
                            target_file = str(other_unit.file_path)
                            if target_file != file_path:
                                efferent.add(target_file)
                            break
            
            # Count files that depend on this file
            for other_file, other_units in file_units.items():
                if other_file != file_path:
                    for other_unit in other_units:
                        for relationship in other_unit.relationships:
                            for unit in units:
                                if relationship.target_id == unit.id:
                                    afferent += 1
                                    break
            
            afferent_coupling.append(afferent)
            efferent_coupling.append(len(efferent))
        
        if afferent_coupling:
            metrics['avg_afferent_coupling'] = sum(afferent_coupling) / len(afferent_coupling)
            metrics['max_afferent_coupling'] = max(afferent_coupling)
        else:
            metrics['avg_afferent_coupling'] = 0.0
            metrics['max_afferent_coupling'] = 0.0
        
        if efferent_coupling:
            metrics['avg_efferent_coupling'] = sum(efferent_coupling) / len(efferent_coupling)
            metrics['max_efferent_coupling'] = max(efferent_coupling)
        else:
            metrics['avg_efferent_coupling'] = 0.0
            metrics['max_efferent_coupling'] = 0.0
        
        # Instability (I = Ce / (Ca + Ce))
        total_ca = sum(afferent_coupling)
        total_ce = sum(efferent_coupling)
        if total_ca + total_ce > 0:
            metrics['instability'] = total_ce / (total_ca + total_ce)
        else:
            metrics['instability'] = 0.0
        
        return metrics
    
    def calculate_cohesion_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate cohesion metrics."""
        metrics = {}
        
        # LCOM (Lack of Cohesion of Methods) - simplified
        lcom_values = []
        
        # Group by class
        class_units = defaultdict(list)
        for unit in memory_units:
            if unit.symbol and unit.symbol.symbol_type == SymbolType.CLASS:
                class_units[unit.symbol.name].append(unit)
        
        for class_name, units in class_units.items():
            # Get all methods in the class
            methods = [unit for unit in units if unit.symbol and unit.symbol.symbol_type == SymbolType.METHOD]
            
            if len(methods) < 2:
                lcom_values.append(0.0)
                continue
            
            # Count shared instance variables (simplified)
            shared_vars = set()
            method_vars = []
            
            for method in methods:
                if method.content:
                    # Extract instance variables (simplified pattern)
                    import re
                    vars_in_method = set(re.findall(r'self\.(\w+)', method.content))
                    method_vars.append(vars_in_method)
                    shared_vars.update(vars_in_method)
            
            # Calculate LCOM: number of disjoint method variable pairs
            if not shared_vars:
                lcom_values.append(len(methods) * (len(methods) - 1) / 2)
                continue
            
            disjoint_pairs = 0
            for i in range(len(method_vars)):
                for j in range(i + 1, len(method_vars)):
                    if not method_vars[i] & method_vars[j]:  # No shared variables
                        disjoint_pairs += 1
            
            lcom = disjoint_pairs / (len(methods) * (len(methods) - 1) / 2)
            lcom_values.append(lcom)
        
        if lcom_values:
            metrics['avg_lcom'] = sum(lcom_values) / len(lcom_values)
            metrics['max_lcom'] = max(lcom_values)
            metrics['min_lcom'] = min(lcom_values)
        else:
            metrics['avg_lcom'] = 0.0
            metrics['max_lcom'] = 0.0
            metrics['min_lcom'] = 0.0
        
        # Cohesion ratio (inverse of LCOM)
        if lcom_values:
            metrics['avg_cohesion'] = 1.0 - metrics['avg_lcom']
        else:
            metrics['avg_cohesion'] = 1.0
        
        return metrics
    
    def calculate_maintainability_metrics(self, memory_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate maintainability metrics."""
        metrics = {}
        
        # Documentation coverage
        documented_units = 0
        total_documentable = 0
        
        for unit in memory_units:
            if unit.symbol and unit.symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD, SymbolType.CLASS]:
                total_documentable += 1
                if unit.symbol.documentation:
                    documented_units += 1
        
        if total_documentable > 0:
            metrics['documentation_coverage'] = documented_units / total_documentable
        else:
            metrics['documentation_coverage'] = 0.0
        
        # Comment ratio (simplified)
        comment_lines = 0
        code_lines = 0
        
        for unit in memory_units:
            if unit.content:
                lines = unit.content.split('\n')
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                        comment_lines += 1
                    elif stripped and not stripped.startswith('*'):
                        code_lines += 1
        
        if code_lines + comment_lines > 0:
            metrics['comment_ratio'] = comment_lines / (code_lines + comment_lines)
        else:
            metrics['comment_ratio'] = 0.0
        
        # Function length metrics
        function_lengths = []
        for unit in memory_units:
            if unit.symbol and unit.symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD]:
                if unit.content:
                    length = unit.content.count('\n') + 1
                    function_lengths.append(length)
        
        if function_lengths:
            metrics['avg_function_length'] = sum(function_lengths) / len(function_lengths)
            metrics['max_function_length'] = max(function_lengths)
            metrics['long_functions'] = sum(1 for length in function_lengths if length > 50)
        else:
            metrics['avg_function_length'] = 0.0
            metrics['max_function_length'] = 0.0
            metrics['long_functions'] = 0
        
        # Parameter complexity
        param_counts = []
        for unit in memory_units:
            if unit.symbol and unit.symbol.parameters:
                param_counts.append(len(unit.symbol.parameters))
        
        if param_counts:
            metrics['avg_parameters'] = sum(param_counts) / len(param_counts)
            metrics['max_parameters'] = max(param_counts)
            metrics['complex_functions'] = sum(1 for count in param_counts if count > 5)
        else:
            metrics['avg_parameters'] = 0.0
            metrics['max_parameters'] = 0.0
            metrics['complex_functions'] = 0
        
        return metrics
    
    def calculate_quality_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall quality score from metrics."""
        try:
            score = 0.0
            
            # Complexity score (lower is better)
            avg_complexity = metrics.get('avg_complexity', 0.0)
            complexity_score = max(0.0, 1.0 - (avg_complexity / 20.0))  # Normalize to 0-1
            score += complexity_score * self.metric_weights['complexity']
            
            # Size score (moderate is better)
            avg_size = metrics.get('avg_size_bytes', 0.0)
            size_score = 1.0 - abs(avg_size - 1000) / 2000  # Optimal around 1000 bytes
            size_score = max(0.0, min(1.0, size_score))
            score += size_score * self.metric_weights['size']
            
            # Coupling score (lower is better)
            avg_coupling = metrics.get('avg_coupling', 0.0)
            coupling_score = max(0.0, 1.0 - (avg_coupling / 10.0))
            score += coupling_score * self.metric_weights['coupling']
            
            # Cohesion score (higher is better)
            cohesion = metrics.get('avg_cohesion', 0.0)
            score += cohesion * self.metric_weights['cohesion']
            
            # Maintainability score
            doc_coverage = metrics.get('documentation_coverage', 0.0)
            comment_ratio = metrics.get('comment_ratio', 0.0)
            maintainability_score = (doc_coverage + comment_ratio) / 2.0
            score += maintainability_score * self.metric_weights['maintainability']
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default neutral score
    
    def calculate_file_metrics(self, file_units: List[MemoryUnit]) -> Dict[str, float]:
        """Calculate metrics for a specific file."""
        return self.calculate_all_metrics(file_units)
    
    def calculate_trend_metrics(self, historical_metrics: List[Dict[str, float]]) -> Dict[str, float]:
        """Calculate trend metrics from historical data."""
        if len(historical_metrics) < 2:
            return {}
        
        trends = {}
        
        # Get all metric names
        all_metrics = set()
        for metrics in historical_metrics:
            all_metrics.update(metrics.keys())
        
        # Calculate trends for each metric
        for metric_name in all_metrics:
            values = [m.get(metric_name, 0.0) for m in historical_metrics if metric_name in m]
            
            if len(values) >= 2:
                # Simple linear trend
                trend = (values[-1] - values[0]) / len(values)
                trends[f'{metric_name}_trend'] = trend
                
                # Percentage change
                if values[0] != 0:
                    percent_change = ((values[-1] - values[0]) / abs(values[0])) * 100
                    trends[f'{metric_name}_percent_change'] = percent_change
        
        return trends
    
    def _median(self, values: List[float]) -> float:
        """Calculate median value."""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2.0
        else:
            return sorted_values[n//2]
    
    def get_metric_summary(self, metrics: Dict[str, float]) -> Dict[str, str]:
        """Get human-readable summary of metrics."""
        summary = {}
        
        # Quality assessment
        quality = metrics.get('overall_quality', 0.0)
        if quality >= 0.8:
            summary['quality_rating'] = "Excellent"
        elif quality >= 0.6:
            summary['quality_rating'] = "Good"
        elif quality >= 0.4:
            summary['quality_rating'] = "Fair"
        else:
            summary['quality_rating'] = "Poor"
        
        # Complexity assessment
        complexity = metrics.get('avg_complexity', 0.0)
        if complexity <= 5:
            summary['complexity_rating'] = "Low"
        elif complexity <= 10:
            summary['complexity_rating'] = "Medium"
        elif complexity <= 20:
            summary['complexity_rating'] = "High"
        else:
            summary['complexity_rating'] = "Very High"
        
        # Size assessment
        avg_size = metrics.get('avg_size_bytes', 0.0)
        if avg_size <= 500:
            summary['size_rating'] = "Small"
        elif avg_size <= 2000:
            summary['size_rating'] = "Medium"
        elif avg_size <= 5000:
            summary['size_rating'] = "Large"
        else:
            summary['size_rating'] = "Very Large"
        
        # Maintainability assessment
        doc_coverage = metrics.get('documentation_coverage', 0.0)
        if doc_coverage >= 0.8:
            summary['documentation_rating'] = "Well Documented"
        elif doc_coverage >= 0.5:
            summary['documentation_rating'] = "Moderately Documented"
        else:
            summary['documentation_rating'] = "Poorly Documented"
        
        return summary
