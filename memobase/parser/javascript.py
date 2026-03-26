"""
JavaScript parser implementation using tree-sitter.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import tree_sitter
from tree_sitter import Language

from memobase.core.models import FileType, ParsedFile, Symbol, SymbolType
from memobase.parser.base import BaseParser


class JavaScriptParser(BaseParser):
    """JavaScript language parser."""
    
    def __init__(self) -> None:
        """Initialize JavaScript parser."""
        try:
            js_language = Language(tree_sitter.language_pointer(), 'javascript')
            super().__init__(js_language, FileType.JAVASCRIPT)
        except Exception as e:
            raise ImportError(f"Failed to load JavaScript tree-sitter language: {e}")
    
    def _extract_symbols(self, tree: tree_sitter.Tree, content: str) -> List[Symbol]:
        """Extract symbols from JavaScript parse tree."""
        symbols = []
        
        # Find function declarations
        function_nodes = self._find_nodes_by_type(tree.root_node, ['function_declaration', 'function_expression'])
        for node in function_nodes:
            symbol = self._extract_function_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        # Find class declarations
        class_nodes = self._find_nodes_by_type(tree.root_node, ['class_declaration'])
        for node in class_nodes:
            symbol = self._extract_class_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        # Find variable declarations
        var_nodes = self._find_nodes_by_type(tree.root_node, ['variable_declaration'])
        for node in var_nodes:
            symbols.extend(self._extract_variable_symbols(node, content))
        
        # Find import statements
        import_nodes = self._find_nodes_by_type(tree.root_node, ['import_statement'])
        for node in import_nodes:
            symbol = self._extract_import_symbol(node, content)
            if symbol:
                symbols.append(symbol)
        
        # Find export statements
        export_nodes = self._find_nodes_by_type(tree.root_node, ['export_statement'])
        for node in export_nodes:
            symbols.extend(self._extract_export_symbols(node, content))
        
        return symbols
    
    def _extract_imports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract import statements."""
        imports = []
        
        import_nodes = self._find_nodes_by_type(tree.root_node, ['import_statement'])
        for node in import_nodes:
            import_text = self._get_node_text(node, '').strip()
            imports.append(import_text)
        
        return imports
    
    def _extract_exports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract export statements."""
        exports = []
        
        export_nodes = self._find_nodes_by_type(tree.root_node, ['export_statement'])
        for node in export_nodes:
            export_text = self._get_node_text(node, '').strip()
            exports.append(export_text)
        
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
        """Extract variable symbols from declaration."""
        symbols = []
        
        for child in node.children:
            if child.type == 'variable_declarator':
                info = self._extract_variable_info(child, content)
                location = self._get_location(child)
                
                if info['name']:
                    symbol_type = SymbolType.CONSTANT if info['is_constant'] else SymbolType.VARIABLE
                    
                    symbol = Symbol(
                        name=info['name'],
                        symbol_type=symbol_type,
                        line_start=location[0],
                        line_end=location[1],
                        column_start=location[2],
                        column_end=location[3],
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
    
    def _extract_export_symbols(self, node: tree_sitter.Node, content: str) -> List[Symbol]:
        """Extract export symbols."""
        symbols = []
        location = self._get_location(node)
        export_text = self._get_node_text(node, '').strip()
        
        # Create export symbol
        export_symbol = Symbol(
            name=export_text,
            symbol_type=SymbolType.EXPORT,
            line_start=location[0],
            line_end=location[1],
            column_start=location[2],
            column_end=location[3]
        )
        symbols.append(export_symbol)
        
        # Also extract the actual exported symbols
        for child in node.children:
            if child.type == 'identifier':
                symbol = Symbol(
                    name=self._get_node_text(child, content),
                    symbol_type=SymbolType.EXPORT,
                    line_start=location[0],
                    line_end=location[1],
                    column_start=location[2],
                    column_end=location[3],
                    is_exported=True
                )
                symbols.append(symbol)
        
        return symbols
    
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
            if child.type == 'formal_parameters':
                info['parameters'] = self._extract_parameters(child, content)
                break
        
        # Get docstring (JSDoc comment before function)
        info['documentation'] = self._extract_jsdoc(node, content)
        
        # Get signature
        info['signature'] = self._get_node_text(node, content).split('{')[0].strip()
        
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
        
        # Check for extends
        for child in node.children:
            if child.type == 'class_heritage':
                info['base_classes'] = self._extract_class_heritage(child, content)
                break
        
        # Get docstring (JSDoc comment before class)
        info['documentation'] = self._extract_jsdoc(node, content)
        
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
        
        # Get variable name
        for child in node.children:
            if child.type == 'identifier':
                info['name'] = self._get_node_text(child, content)
                break
        
        # Check if constant (const keyword)
        parent = node.parent
        if parent and parent.type == 'variable_declaration':
            for child in parent.children:
                if child.type == 'const':
                    info['is_constant'] = True
                    break
        
        return info
    
    def _extract_parameters(self, params_node: tree_sitter.Node, content: str) -> List[str]:
        """Extract parameter names from parameter list."""
        parameters = []
        
        for child in params_node.children:
            if child.type == 'identifier':
                parameters.append(self._get_node_text(child, content))
            elif child.type == 'assignment_pattern':
                # Default parameter: name = value
                for subchild in child.children:
                    if subchild.type == 'identifier':
                        parameters.append(self._get_node_text(subchild, content))
                        break
        
        return parameters
    
    def _extract_class_heritage(self, heritage_node: tree_sitter.Node, content: str) -> List[str]:
        """Extract base classes from class heritage."""
        base_classes = []
        
        for child in heritage_node.children:
            if child.type == 'identifier':
                base_classes.append(self._get_node_text(child, content))
        
        return base_classes
    
    def _extract_jsdoc(self, node: tree_sitter.Node, content: str) -> str:
        """Extract JSDoc comment for a node."""
        # This is a simplified implementation
        # In practice, you'd need to look at the previous sibling or parent's comments
        return None
