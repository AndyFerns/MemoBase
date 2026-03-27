"""
Python parser implementation using tree-sitter.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import tree_sitter
from tree_sitter import Language

from memobase.core.models import FileType, ParsedFile, Symbol, SymbolType
from memobase.parser.base import BaseParser


class PythonParser(BaseParser):
    """Python language parser."""
    
    def __init__(self) -> None:
        """Initialize Python parser."""
        try:
            from memobase.parser.languages import get_language
            python_language = get_language("python")
            super().__init__(python_language, FileType.PYTHON)
        except ImportError as e:
            raise ImportError(f"Failed to load Python tree-sitter language: {e}")
    
    def _extract_symbols(self, tree: tree_sitter.Tree, content: str) -> List[Symbol]:
        """Extract symbols from Python parse tree."""
        symbols = []
        
        # Find function definitions
        function_nodes = self._find_nodes_by_type(tree.root_node, ['function_definition'])
        for node in function_nodes:
            symbol = self._extract_function_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        # Find class definitions
        class_nodes = self._find_nodes_by_type(tree.root_node, ['class_definition'])
        for node in class_nodes:
            symbol = self._extract_class_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        # Find variable assignments at module level
        assignment_nodes = self._find_nodes_by_type(tree.root_node, ['assignment'])
        for node in assignment_nodes:
            symbols.extend(self._extract_variable_symbols(node, content))
        
        # Find import statements
        import_nodes = self._find_nodes_by_type(tree.root_node, ['import_statement', 'import_from_statement'])
        for node in import_nodes:
            symbol = self._extract_import_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        return symbols
    
    def _extract_imports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract import statements."""
        imports = []
        
        import_nodes = self._find_nodes_by_type(tree.root_node, ['import_statement', 'import_from_statement'])
        for node in import_nodes:
            import_text = self._get_node_text(node, '').strip()
            imports.append(import_text)
        
        return imports
    
    def _extract_exports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract exports (Python uses __all__)."""
        exports = []
        
        # Look for __all__ assignments
        assignment_nodes = self._find_nodes_by_type(tree.root_node, ['assignment'])
        for node in assignment_nodes:
            text = self._get_node_text(node, '')
            if '__all__' in text:
                # Parse the list of exported names
                exports.extend(self._parse_all_assignment(text))
        
        return exports
    
    def _extract_function_symbol(self, node: tree_sitter.Node, content: str) -> Symbol:
        """Extract function symbol."""
        info = self._extract_function_info(node, content)
        location = self._get_location(node)
        
        return Symbol(
            name=info['name'],
            symbol_type=SymbolType.FUNCTION,
            line_start=location[0],
            line_end=location[1],
            column_start=location[2],
            column_end=location[3],
            documentation=info['documentation'],
            signature=info['signature'],
            parameters=info['parameters'],
            return_type=info['return_type'],
            is_async=info['is_async'],
            is_static=info['is_static'],
            is_exported=info['is_exported']
        )
    
    def _extract_class_symbol(self, node: tree_sitter.Node, content: str) -> Symbol:
        """Extract class symbol."""
        info = self._extract_class_info(node, content)
        location = self._get_location(node)
        
        return Symbol(
            name=info['name'],
            symbol_type=SymbolType.CLASS,
            line_start=location[0],
            line_end=location[1],
            column_start=location[2],
            column_end=location[3],
            documentation=info['documentation'],
            is_exported=info['is_exported']
        )
    
    def _extract_variable_symbols(self, node: tree_sitter.Node, content: str) -> List[Symbol]:
        """Extract variable symbols from assignment."""
        symbols = []
        info = self._extract_variable_info(node, content)
        location = self._get_location(node)
        
        if info['name']:
            symbol_type = SymbolType.CONSTANT if info['is_constant'] else SymbolType.VARIABLE
            
            symbol = Symbol(
                name=info['name'],
                symbol_type=symbol_type,
                line_start=location[0],
                line_end=location[1],
                column_start=location[2],
                column_end=location[3],
                is_static=info['is_static'],
                is_exported=info['is_exported']
            )
            symbols.append(symbol)
        
        return symbols
    
    def _extract_import_symbol(self, node: tree_sitter.Node, content: str) -> Symbol:
        """Extract import symbol."""
        location = self._get_location(node)
        import_text = self._get_node_text(node, '').strip()
        
        return Symbol(
            name=import_text,
            symbol_type=SymbolType.IMPORT,
            line_start=location[0],
            line_end=location[1],
            column_start=location[2],
            column_end=location[3]
        )
    
    def _extract_function_info(self, node: tree_sitter.Tree, content: str) -> dict:
        """Extract function information."""
        info = {
            'name': '',
            'parameters': [],
            'return_type': None,
            'documentation': None,
            'signature': None,
            'is_async': False,
            'is_static': False,
            'is_exported': False,
        }
        
        # Check if async
        for child in node.children:
            if child.type == 'async':
                info['is_async'] = True
        
        # Get function name
        for child in node.children:
            if child.type == 'identifier':
                info['name'] = self._get_node_text(child, content)
                break
        
        # Get parameters
        for child in node.children:
            if child.type == 'parameters':
                info['parameters'] = self._extract_parameters(child, content)
                break
        
        # Get return type annotation
        for child in node.children:
            if child.type == 'type' and child.child_count > 0:
                info['return_type'] = self._get_node_text(child, content)
                break
        
        # Get docstring
        info['documentation'] = self._extract_docstring(node, content)
        
        # Get signature
        info['signature'] = self._get_node_text(node, content).split(':')[0].strip()
        
        return info
    
    def _extract_class_info(self, node: tree_sitter.Tree, content: str) -> dict:
        """Extract class information."""
        info = {
            'name': '',
            'base_classes': [],
            'methods': [],
            'attributes': [],
            'documentation': None,
            'is_exported': False,
        }
        
        # Get class name
        for child in node.children:
            if child.type == 'identifier':
                info['name'] = self._get_node_text(child, content)
                break
        
        # Get base classes
        for child in node.children:
            if child.type == 'argument_list':
                info['base_classes'] = self._extract_argument_list(child, content)
                break
        
        # Get docstring
        info['documentation'] = self._extract_docstring(node, content)
        
        return info
    
    def _extract_variable_info(self, node: tree_sitter.Tree, content: str) -> dict:
        """Extract variable information."""
        info = {
            'name': '',
            'type': None,
            'value': None,
            'is_constant': False,
            'is_static': False,
            'is_exported': False,
        }
        
        # Get variable name from left side
        for child in node.children:
            if child.type == 'pattern_list':
                # Handle multiple assignment: a, b = 1, 2
                identifiers = self._find_nodes_by_type(child, ['identifier'])
                if identifiers:
                    info['name'] = self._get_node_text(identifiers[0], content)
            elif child.type == 'identifier':
                # Handle single assignment: a = 1
                info['name'] = self._get_node_text(child, content)
                break
        
        # Check if constant (uppercase)
        if info['name'] and info['name'].isupper():
            info['is_constant'] = True
        
        return info
    
    def _extract_parameters(self, params_node: tree_sitter.Node, content: str) -> List[str]:
        """Extract parameter names from parameter list."""
        parameters = []
        
        for child in params_node.children:
            if child.type == 'identifier':
                parameters.append(self._get_node_text(child, content))
            elif child.type == 'typed_parameter':
                # Handle typed parameters: name: type
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(self._get_node_text(subchild, content))
                        break
            elif child.type == 'default_parameter':
                # Handle default parameters: name = value
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(self._get_node_text(subchild, content))
                        break
                    elif subchild.type == 'typed_parameter':
                        for subsubchild in subchild.children:
                            if subsubchild.type == 'identifier':
                                parameters.append(self._get_node_text(subsubchild, content))
                                break
        
        return parameters
    
    def _extract_argument_list(self, arg_list_node: tree_sitter.Node, content: str) -> List[str]:
        """Extract argument names from argument list."""
        arguments = []
        
        for child in arg_list_node.children:
            if child.type == 'identifier':
                arguments.append(self._get_node_text(child, content))
        
        return arguments
    
    def _extract_docstring(self, node: tree_sitter.Node, content: str) -> str:
        """Extract docstring from node."""
        # Look for expression statement with string as first child
        for child in node.children:
            if child.type == 'block':
                for grandchild in child.children:
                    if grandchild.type == 'expression_statement':
                        for ggchild in grandchild.children:
                            if ggchild.type in ['string', 'interpolated_string']:
                                return self._get_node_text(ggchild, content).strip('\'"')
        
        return None
    
    def _parse_all_assignment(self, text: str) -> List[str]:
        """Parse __all__ assignment to extract exported names."""
        exports = []
        
        # Simple parsing for __all__ = ['name1', 'name2']
        if '__all__' in text and '=' in text:
            after_equals = text.split('=', 1)[1].strip()
            if after_equals.startswith('[') and after_equals.endswith(']'):
                content = after_equals[1:-1].strip()
                # Split by commas and clean up quotes
                parts = content.split(',')
                for part in parts:
                    name = part.strip().strip('\'"')
                    if name:
                        exports.append(name)
        
        return exports
