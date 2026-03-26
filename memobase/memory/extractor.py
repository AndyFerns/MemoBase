"""
Relationship extractor for code analysis.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set

from memobase.core.models import MemoryUnit, Relationship, RelationType, SymbolType


class RelationshipExtractor:
    """Extracts relationships between memory units."""
    
    def __init__(self) -> None:
        """Initialize relationship extractor."""
        self.call_patterns = self._init_call_patterns()
        self.import_patterns = self._init_import_patterns()
        self.reference_patterns = self._init_reference_patterns()
    
    def extract_all_relationships(self, memory_units: List[MemoryUnit]) -> List[Relationship]:
        """Extract all types of relationships."""
        relationships = []
        
        # Build lookup tables
        units_by_id = {unit.id: unit for unit in memory_units}
        units_by_symbol = self._build_symbol_lookup(memory_units)
        units_by_file = self._build_file_lookup(memory_units)
        
        # Extract different relationship types
        relationships.extend(self._extract_call_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_import_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_inheritance_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_containment_relationships(memory_units, units_by_file))
        relationships.extend(self._extract_reference_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_usage_relationships(memory_units, units_by_symbol))
        
        return relationships
    
    def _extract_call_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract function/method call relationships."""
        relationships = []
        
        for unit in memory_units:
            if not unit.content or not unit.symbol:
                continue
            
            # Only extract calls from functions/methods
            if unit.symbol.symbol_type not in [SymbolType.FUNCTION, SymbolType.METHOD]:
                continue
            
            called_symbols = self._find_function_calls(unit.content, unit.symbol.name)
            
            for called_name in called_symbols:
                target_unit = units_by_symbol.get(called_name)
                if target_unit and target_unit.id != unit.id:
                    # Calculate weight based on call frequency
                    weight = self._calculate_call_weight(unit.content, called_name)
                    
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.CALLS,
                        weight=weight,
                        metadata={
                            'call_count': self._count_calls(unit.content, called_name),
                            'caller_type': unit.symbol.symbol_type.value,
                            'callee_type': target_unit.symbol.symbol_type.value if target_unit.symbol else 'unknown'
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_import_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract import relationships."""
        relationships = []
        
        for unit in memory_units:
            if unit.metadata.get('type') != 'file':
                continue
            
            imported_symbols = self._find_imports(unit.content)
            
            for imported_name in imported_symbols:
                target_unit = units_by_symbol.get(imported_name)
                if target_unit:
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.IMPORTS,
                        weight=0.8,
                        metadata={
                            'import_type': self._detect_import_type(unit.content, imported_name),
                            'imported_from': self._find_import_source(unit.content, imported_name)
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_inheritance_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract inheritance relationships."""
        relationships = []
        
        for unit in memory_units:
            if not unit.symbol or unit.symbol.symbol_type != SymbolType.CLASS:
                continue
            
            base_classes = self._find_base_classes(unit.content)
            
            for base_class in base_classes:
                target_unit = units_by_symbol.get(base_class)
                if target_unit:
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.INHERITS,
                        weight=1.0,
                        metadata={
                            'inheritance_type': 'class_inheritance',
                            'base_class': base_class
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_containment_relationships(self, memory_units: List[MemoryUnit], units_by_file: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract containment relationships (file contains symbols, class contains methods)."""
        relationships = []
        
        # File contains symbols
        for unit in memory_units:
            if unit.metadata.get('type') == 'symbol':
                file_key = str(unit.file_path)
                file_unit = units_by_file.get(file_key)
                if file_unit:
                    relationship = Relationship(
                        source_id=file_unit.id,
                        target_id=unit.id,
                        relation_type=RelationType.CONTAINS,
                        weight=1.0,
                        metadata={
                            'containment_type': 'file_contains_symbol',
                            'symbol_type': unit.symbol.symbol_type.value if unit.symbol else 'unknown'
                        }
                    )
                    relationships.append(relationship)
        
        # Class contains methods and attributes
        for unit in memory_units:
            if not unit.symbol or unit.symbol.symbol_type != SymbolType.CLASS:
                continue
            
            # Find methods and attributes in the same file
            file_units = [u for u in memory_units if u.file_path == unit.file_path]
            
            for other_unit in file_units:
                if not other_unit.symbol or other_unit.id == unit.id:
                    continue
                
                # Check if method/attribute is defined within class scope
                if self._is_within_class_scope(other_unit, unit):
                    containment_type = 'class_contains_method' if other_unit.symbol.symbol_type == SymbolType.METHOD else 'class_contains_attribute'
                    
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=other_unit.id,
                        relation_type=RelationType.CONTAINS,
                        weight=1.0,
                        metadata={
                            'containment_type': containment_type,
                            'member_type': other_unit.symbol.symbol_type.value
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_reference_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract reference relationships."""
        relationships = []
        
        for unit in memory_units:
            if not unit.content:
                continue
            
            referenced_symbols = self._find_symbol_references(unit.content)
            
            for ref_name in referenced_symbols:
                target_unit = units_by_symbol.get(ref_name)
                if target_unit and target_unit.id != unit.id:
                    weight = self._calculate_reference_weight(unit.content, ref_name)
                    
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.REFERENCES,
                        weight=weight,
                        metadata={
                            'reference_count': self._count_references(unit.content, ref_name),
                            'reference_context': self._get_reference_context(unit.content, ref_name)
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_usage_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: Dict[str, MemoryUnit]) -> List[Relationship]:
        """Extract usage relationships (uses/depends on)."""
        relationships = []
        
        for unit in memory_units:
            if not unit.content:
                continue
            
            used_symbols = self._find_used_symbols(unit.content)
            
            for used_name in used_symbols:
                target_unit = units_by_symbol.get(used_name)
                if target_unit and target_unit.id != unit.id:
                    weight = self._calculate_usage_weight(unit.content, used_name)
                    
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.USES,
                        weight=weight,
                        metadata={
                            'usage_type': self._detect_usage_type(unit.content, used_name),
                            'usage_count': self._count_usage(unit.content, used_name)
                        }
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _build_symbol_lookup(self, memory_units: List[MemoryUnit]) -> Dict[str, MemoryUnit]:
        """Build symbol name to memory unit lookup."""
        lookup = {}
        for unit in memory_units:
            if unit.symbol:
                lookup[unit.symbol.name] = unit
        return lookup
    
    def _build_file_lookup(self, memory_units: List[MemoryUnit]) -> Dict[str, MemoryUnit]:
        """Build file path to memory unit lookup."""
        lookup = {}
        for unit in memory_units:
            if unit.metadata.get('type') == 'file':
                lookup[str(unit.file_path)] = unit
        return lookup
    
    def _find_function_calls(self, content: str, current_function: str) -> Set[str]:
        """Find function calls in content."""
        calls = set()
        
        for pattern in self.call_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    calls.update(match)
                else:
                    calls.add(match)
        
        # Remove self-references
        calls.discard(current_function)
        
        # Filter out keywords and built-ins
        keywords = {'if', 'for', 'while', 'switch', 'return', 'print', 'len', 'range', 'str', 'int', 'float', 'list', 'dict', 'set'}
        calls = {call for call in calls if call not in keywords and call.isidentifier()}
        
        return calls
    
    def _find_imports(self, content: str) -> Set[str]:
        """Find imported symbols."""
        imports = set()
        
        for pattern in self.import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    imports.update(match)
                else:
                    imports.add(match)
        
        return {imp.strip() for imp in imports if imp.strip()}
    
    def _find_base_classes(self, content: str) -> Set[str]:
        """Find base classes in class definition."""
        base_classes = set()
        
        # Python class inheritance
        pattern = r'class\s+\w+\s*\(([^)]+)\)'
        matches = re.findall(pattern, content)
        for match in matches:
            classes = [cls.strip() for cls in match.split(',')]
            base_classes.update(classes)
        
        return base_classes
    
    def _find_symbol_references(self, content: str) -> Set[str]:
        """Find symbol references in content."""
        references = set()
        
        for pattern in self.reference_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    references.update(match)
                else:
                    references.add(match)
        
        # Filter out keywords
        keywords = {
            'if', 'else', 'elif', 'for', 'while', 'break', 'continue',
            'def', 'class', 'return', 'yield', 'import', 'from', 'as',
            'try', 'except', 'finally', 'with', 'pass', 'global', 'nonlocal',
            'and', 'or', 'not', 'in', 'is', 'lambda', 'None', 'True', 'False',
            'self', 'cls'
        }
        
        return {ref for ref in references if ref not in keywords and ref.isidentifier() and len(ref) > 1}
    
    def _find_used_symbols(self, content: str) -> Set[str]:
        """Find used symbols."""
        # Similar to references but with different weighting
        return self._find_symbol_references(content)
    
    def _is_within_class_scope(self, unit: MemoryUnit, class_unit: MemoryUnit) -> bool:
        """Check if a unit is defined within class scope."""
        if not unit.symbol or not class_unit.symbol:
            return False
        
        # Simple check: same file and symbol defined after class
        if unit.file_path != class_unit.file_path:
            return False
        
        return (unit.symbol.line_start > class_unit.symbol.line_start and
                unit.symbol.line_end <= class_unit.symbol.line_end)
    
    def _calculate_call_weight(self, content: str, function_name: str) -> float:
        """Calculate weight for call relationship based on frequency."""
        count = self._count_calls(content, function_name)
        return min(1.0, 0.3 + (count * 0.1))
    
    def _calculate_reference_weight(self, content: str, symbol_name: str) -> float:
        """Calculate weight for reference relationship."""
        count = self._count_references(content, symbol_name)
        return min(1.0, 0.2 + (count * 0.05))
    
    def _calculate_usage_weight(self, content: str, symbol_name: str) -> float:
        """Calculate weight for usage relationship."""
        count = self._count_usage(content, symbol_name)
        return min(1.0, 0.4 + (count * 0.1))
    
    def _count_calls(self, content: str, function_name: str) -> int:
        """Count function calls."""
        pattern = rf'\b{re.escape(function_name)}\s*\('
        return len(re.findall(pattern, content))
    
    def _count_references(self, content: str, symbol_name: str) -> int:
        """Count symbol references."""
        pattern = rf'\b{re.escape(symbol_name)}\b'
        return len(re.findall(pattern, content))
    
    def _count_usage(self, content: str, symbol_name: str) -> int:
        """Count symbol usage."""
        return self._count_references(content, symbol_name)
    
    def _detect_import_type(self, content: str, symbol_name: str) -> str:
        """Detect import type (direct, from, etc.)."""
        if f'import {symbol_name}' in content:
            return 'direct'
        elif f'from' in content and f'import {symbol_name}' in content:
            return 'from_import'
        else:
            return 'unknown'
    
    def _find_import_source(self, content: str, symbol_name: str) -> str:
        """Find import source module."""
        # Simple implementation - could be enhanced
        lines = content.split('\n')
        for line in lines:
            if symbol_name in line and ('import' in line):
                return line.strip()
        return ''
    
    def _detect_usage_type(self, content: str, symbol_name: str) -> str:
        """Detect usage type."""
        if f'{symbol_name}(' in content:
            return 'function_call'
        elif f'({symbol_name})' in content:
            return 'type_annotation'
        else:
            return 'reference'
    
    def _get_reference_context(self, content: str, symbol_name: str) -> List[str]:
        """Get context around references."""
        contexts = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if symbol_name in line:
                # Get context lines
                start = max(0, i - 1)
                end = min(len(lines), i + 2)
                context = '\n'.join(lines[start:end])
                contexts.append(context.strip())
        return contexts[:3]  # Limit to 3 contexts
    
    def _init_call_patterns(self) -> List[str]:
        """Initialize call detection patterns."""
        return [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Function calls
            r'\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',  # Method calls
        ]
    
    def _init_import_patterns(self) -> List[str]:
        """Initialize import detection patterns."""
        return [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'from\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)',
        ]
    
    def _init_reference_patterns(self) -> List[str]:
        """Initialize reference detection patterns."""
        return [
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b',  # General identifiers
        ]
