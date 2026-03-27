"""
Memory unit builder implementation.
"""

from __future__ import annotations

import asyncio
import hashlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Generator, List

from memobase.core.interfaces import EmbeddingInterface, MemoryBuilderInterface
from memobase.core.models import MemoryUnit, ParsedFile, Relationship, Symbol, SymbolType, RelationType


class MemoryBuilder(MemoryBuilderInterface):
    """Memory unit builder with relationship extraction."""
    
    def __init__(self, embedder: EmbeddingInterface) -> None:
        """Initialize memory builder.
        
        Args:
            embedder: Embedding interface for text embeddings
        """
        self.embedder = embedder
    
    def build(self, parsed_file: ParsedFile) -> List[MemoryUnit]:
        """Build memory units from parsed file."""
        memory_units = []
        
        # Create memory unit for the entire file
        file_unit = self._create_file_unit(parsed_file)
        memory_units.append(file_unit)
        
        # Create memory units for each symbol
        for symbol in parsed_file.symbols:
            symbol_unit = self._create_symbol_unit(symbol, parsed_file)
            if symbol_unit:
                memory_units.append(symbol_unit)
        
        # Generate embeddings for all units
        for unit in memory_units:
            if unit.content:
                unit.embeddings = self.embedder.embed(unit.content)
        
        return memory_units
    
    def build_batch(self, parsed_files: Generator[ParsedFile, None, None]) -> Generator[MemoryUnit, None, None]:
        """Build memory units from multiple parsed files."""
        with ProcessPoolExecutor() as executor:
            for parsed_file in parsed_files:
                units = executor.submit(self.build, parsed_file).result()
                for unit in units:
                    yield unit
    
    async def build_async(self, parsed_file: ParsedFile) -> List[MemoryUnit]:
        """Async version of build."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.build, parsed_file)
    
    def extract_relationships(self, memory_units: List[MemoryUnit]) -> List[Relationship]:
        """Extract relationships between memory units."""
        relationships = []
        
        # Build lookup dictionaries
        units_by_id = {unit.id: unit for unit in memory_units}
        units_by_symbol = {}
        units_by_file = {}
        
        for unit in memory_units:
            if unit.symbol:
                units_by_symbol[unit.symbol.name] = unit
            units_by_file[str(unit.file_path)] = unit
        
        # Extract various types of relationships
        relationships.extend(self._extract_call_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_definition_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_import_relationships(memory_units, units_by_symbol))
        relationships.extend(self._extract_containment_relationships(memory_units, units_by_file))
        relationships.extend(self._extract_reference_relationships(memory_units, units_by_symbol))
        
        return relationships
    
    def _create_file_unit(self, parsed_file: ParsedFile) -> MemoryUnit:
        """Create memory unit for the entire file."""
        content = parsed_file.path.read_text(encoding='utf-8')
        
        # Generate unique ID for file unit
        unit_id = hashlib.sha256(f"file:{parsed_file.path}:{parsed_file.content_hash}".encode()).hexdigest()
        
        # Extract keywords from file
        keywords = self._extract_file_keywords(parsed_file)
        
        return MemoryUnit(
            id=unit_id,
            file_path=parsed_file.path,
            content=content,
            keywords=keywords,
            metadata={
                'type': 'file',
                'file_type': parsed_file.file_type.value,
                'size_bytes': parsed_file.size_bytes,
                'last_modified': parsed_file.last_modified.isoformat(),
                'symbols_count': len(parsed_file.symbols),
                'imports_count': len(parsed_file.imports),
                'exports_count': len(parsed_file.exports),
            }
        )
    
    def _create_symbol_unit(self, symbol: Symbol, parsed_file: ParsedFile) -> MemoryUnit:
        """Create memory unit for a symbol."""
        # Extract symbol content
        content = self._extract_symbol_content(symbol, parsed_file.path)
        
        if not content:
            return None
        
        # Create memory unit from symbol
        unit = MemoryUnit.create_from_symbol(symbol, parsed_file.path, content)
        
        # Add symbol-specific metadata
        unit.metadata.update({
            'type': 'symbol',
            'symbol_type': symbol.symbol_type.value,
            'line_start': symbol.line_start,
            'line_end': symbol.line_end,
            'column_start': symbol.column_start,
            'column_end': symbol.column_end,
            'is_async': symbol.is_async,
            'is_static': symbol.is_static,
            'is_exported': symbol.is_exported,
        })
        
        # Add additional keywords
        additional_keywords = self._extract_symbol_keywords(symbol)
        unit.keywords.extend(additional_keywords)
        
        return unit
    
    def _extract_file_keywords(self, parsed_file: ParsedFile) -> List[str]:
        """Extract keywords from parsed file."""
        keywords = []
        
        # Add file name without extension
        file_stem = parsed_file.path.stem.lower()
        keywords.append(file_stem)
        
        # Add symbol names
        for symbol in parsed_file.symbols:
            keywords.append(symbol.name.lower())
            if symbol.symbol_type == SymbolType.CLASS:
                keywords.append(f"class {symbol.name.lower()}")
            elif symbol.symbol_type == SymbolType.FUNCTION:
                keywords.append(f"function {symbol.name.lower()}")
            elif symbol.symbol_type == SymbolType.METHOD:
                keywords.append(f"method {symbol.name.lower()}")
        
        # Add import names
        for import_stmt in parsed_file.imports:
            # Extract module names from imports
            import_parts = import_stmt.split()
            if import_parts:
                keywords.append(import_parts[0].lower())
        
        # Add file type keywords
        keywords.append(parsed_file.file_type.value)
        keywords.append(f"{parsed_file.file_type.value} file")
        
        return list(set(keywords))  # Remove duplicates
    
    def _extract_symbol_keywords(self, symbol: Symbol) -> List[str]:
        """Extract keywords from symbol."""
        keywords = []
        
        # Add symbol type
        keywords.append(symbol.symbol_type.value)
        
        # Add parameter names for functions/methods
        for param in symbol.parameters:
            keywords.append(param.lower())
        
        # Add return type if available
        if symbol.return_type:
            keywords.append(symbol.return_type.lower())
        
        # Add visibility if available
        if symbol.visibility:
            keywords.append(symbol.visibility.lower())
        
        # Add async/static/exported keywords
        if symbol.is_async:
            keywords.append('async')
        if symbol.is_static:
            keywords.append('static')
        if symbol.is_exported:
            keywords.append('exported')
        
        return keywords
    
    def _extract_symbol_content(self, symbol: Symbol, file_path: Path) -> str:
        """Extract content for symbol from file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Extract lines for the symbol
            start_line = symbol.line_start - 1  # Convert to 0-based
            end_line = symbol.line_end
            
            if start_line >= 0 and end_line <= len(lines):
                symbol_lines = lines[start_line:end_line]
                return '\n'.join(symbol_lines)
            
        except Exception:
            pass
        
        return None
    
    def _extract_call_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: dict) -> List[Relationship]:
        """Extract function call relationships."""
        relationships = []
        
        for unit in memory_units:
            if not unit.content or not unit.symbol:
                continue
            
            # Find function calls in content
            if unit.symbol.symbol_type in [SymbolType.FUNCTION, SymbolType.METHOD]:
                called_symbols = self._find_called_functions(unit.content)
                
                for called_name in called_symbols:
                    target_unit = units_by_symbol.get(called_name)
                    if target_unit and target_unit.id != unit.id:
                        relationship = Relationship(
                            source_id=unit.id,
                            target_id=target_unit.id,
                            relation_type=RelationType.CALLS,
                            weight=1.0
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _extract_definition_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: dict) -> List[Relationship]:
        """Extract definition relationships (e.g., class contains methods)."""
        relationships = []
        
        for unit in memory_units:
            if not unit.symbol:
                continue
            
            # Class contains methods
            if unit.symbol.symbol_type == SymbolType.CLASS:
                # Find methods in the same file
                file_units = [u for u in memory_units if u.file_path == unit.file_path]
                for other_unit in file_units:
                    if (other_unit.symbol and 
                        other_unit.symbol.symbol_type == SymbolType.METHOD and
                        other_unit.id != unit.id):
                        relationship = Relationship(
                            source_id=unit.id,
                            target_id=other_unit.id,
                            relation_type=RelationType.CONTAINS,
                            weight=1.0
                        )
                        relationships.append(relationship)
        
        return relationships
    
    def _extract_import_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: dict) -> List[Relationship]:
        """Extract import relationships."""
        relationships = []
        
        for unit in memory_units:
            if unit.metadata.get('type') != 'file':
                continue
            
            # Find imported symbols
            imported_symbols = self._find_imported_symbols(unit.content)
            
            for imported_name in imported_symbols:
                target_unit = units_by_symbol.get(imported_name)
                if target_unit:
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.IMPORTS,
                        weight=0.8
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_containment_relationships(self, memory_units: List[MemoryUnit], units_by_file: dict) -> List[Relationship]:
        """Extract file containment relationships."""
        relationships = []
        
        for unit in memory_units:
            if unit.metadata.get('type') == 'symbol':
                file_unit = units_by_file.get(str(unit.file_path))
                if file_unit:
                    relationship = Relationship(
                        source_id=file_unit.id,
                        target_id=unit.id,
                        relation_type=RelationType.CONTAINS,
                        weight=1.0
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _extract_reference_relationships(self, memory_units: List[MemoryUnit], units_by_symbol: dict) -> List[Relationship]:
        """Extract reference relationships."""
        relationships = []
        
        for unit in memory_units:
            if not unit.content:
                continue
            
            # Find symbol references in content
            referenced_symbols = self._find_referenced_symbols(unit.content)
            
            for ref_name in referenced_symbols:
                target_unit = units_by_symbol.get(ref_name)
                if target_unit and target_unit.id != unit.id:
                    relationship = Relationship(
                        source_id=unit.id,
                        target_id=target_unit.id,
                        relation_type=RelationType.REFERENCES,
                        weight=0.6
                    )
                    relationships.append(relationship)
        
        return relationships
    
    def _find_called_functions(self, content: str) -> List[str]:
        """Find function calls in content (simplified)."""
        # This is a simplified implementation
        # In practice, you'd use proper parsing
        import re
        
        # Find function call patterns
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, content)
        
        # Filter out common keywords
        keywords = {'if', 'for', 'while', 'switch', 'return', 'print', 'len', 'range'}
        return [match for match in matches if match not in keywords]
    
    def _find_imported_symbols(self, content: str) -> List[str]:
        """Find imported symbols in content (simplified)."""
        import re
        
        imported = []
        
        # Python imports
        import_patterns = [
            r'import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
            r'from\s+[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    imported.extend(match)
                else:
                    imported.append(match)
        
        return [name.strip() for name in imported if name.strip()]
    
    def _find_referenced_symbols(self, content: str) -> List[str]:
        """Find symbol references in content (simplified)."""
        import re
        
        # Find identifier patterns
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(pattern, content)
        
        # Filter out common keywords
        keywords = {
            'if', 'else', 'elif', 'for', 'while', 'break', 'continue',
            'def', 'class', 'return', 'yield', 'import', 'from', 'as',
            'try', 'except', 'finally', 'with', 'pass', 'global', 'nonlocal',
            'and', 'or', 'not', 'in', 'is', 'lambda', 'None', 'True', 'False'
        }
        
        return [match for match in matches if match not in keywords and len(match) > 1]
