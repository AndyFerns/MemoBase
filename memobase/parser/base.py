"""
Base parser implementation using tree-sitter.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Generator, List, Optional

import tree_sitter
from tree_sitter import Language, Parser

from memobase.core.exceptions import ParseError
from memobase.core.interfaces import ParserInterface
from memobase.core.models import FileType, ParsedFile, Symbol, SymbolType


class BaseParser(ParserInterface):
    """Base parser implementation using tree-sitter."""
    
    def __init__(self, language: Language, file_type: FileType) -> None:
        """Initialize parser with language and file type.
        
        Args:
            language: Tree-sitter Language object
            file_type: FileType enum value
        """
        self.language = language
        self.file_type = file_type
        self.parser = Parser()
        self.parser.set_language(language)
    
    def parse(self, file_path: Path) -> ParsedFile:
        """Parse a file and return ParsedFile."""
        try:
            parsed_file = ParsedFile.create_from_path(file_path)
            
            if parsed_file.file_type != self.file_type:
                raise ParseError(f"File type mismatch: expected {self.file_type}, got {parsed_file.file_type}")
            
            content = file_path.read_text(encoding='utf-8')
            tree = self.parser.parse(bytes(content, 'utf-8'))
            
            parsed_file.symbols = self._extract_symbols(tree, content)
            parsed_file.imports = self._extract_imports(tree)
            parsed_file.exports = self._extract_exports(tree)
            
            return parsed_file
            
        except Exception as e:
            raise ParseError(f"Failed to parse {file_path}: {str(e)}")
    
    def parse_batch(self, file_paths: List[Path]) -> Generator[ParsedFile, None, None]:
        """Parse multiple files in batch."""
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(self.parse, path) for path in file_paths]
            for future in futures:
                try:
                    yield future.result()
                except Exception as e:
                    raise ParseError(f"Batch parsing failed: {str(e)}")
    
    async def parse_async(self, file_path: Path) -> ParsedFile:
        """Async version of parse."""
        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.parse, file_path)
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return self._get_extensions_for_type(self.file_type)
    
    def _extract_symbols(self, tree: tree_sitter.Tree, content: str) -> List[Symbol]:
        """Extract symbols from parse tree. Override in subclasses."""
        return []
    
    def _extract_imports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract imports from parse tree. Override in subclasses."""
        return []
    
    def _extract_exports(self, tree: tree_sitter.Tree) -> List[str]:
        """Extract exports from parse tree. Override in subclasses."""
        return []
    
    def _get_symbol_type(self, node_type: str) -> SymbolType:
        """Convert tree-sitter node type to SymbolType. Override in subclasses."""
        return SymbolType.UNKNOWN
    
    def _get_node_text(self, node: tree_sitter.Node, content: str) -> str:
        """Get text content of a node."""
        return content[node.start_byte:node.end_byte]
    
    def _get_location(self, node: tree_sitter.Node) -> tuple[int, int, int, int]:
        """Get location tuple from node."""
        return (
            node.start_point[0] + 1,  # Convert to 1-based line numbers
            node.end_point[0] + 1,
            node.start_point[1] + 1,
            node.end_point[1] + 1
        )
    
    @staticmethod
    def _get_extensions_for_type(file_type: FileType) -> List[str]:
        """Get file extensions for a file type."""
        extension_map = {
            FileType.PYTHON: [".py", ".pyi"],
            FileType.JAVASCRIPT: [".js", ".jsx"],
            FileType.TYPESCRIPT: [".ts", ".tsx"],
            FileType.JAVA: [".java"],
            FileType.C: [".c", ".h"],
            FileType.CPP: [".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
            FileType.RUST: [".rs"],
            FileType.GO: [".go"],
            FileType.RUBY: [".rb"],
            FileType.PHP: [".php"],
        }
        return extension_map.get(file_type, [])
    
    def _traverse_tree(self, node: tree_sitter.Node, content: str):
        """Traverse tree and yield nodes with their text."""
        stack = [node]
        while stack:
            current = stack.pop()
            text = self._get_node_text(current, content)
            yield current, text
            stack.extend(reversed(current.children))
    
    def _find_nodes_by_type(self, node: tree_sitter.Node, node_types: List[str]) -> List[tree_sitter.Node]:
        """Find all nodes of specified types."""
        results = []
        stack = [node]
        
        while stack:
            current = stack.pop()
            if current.type in node_types:
                results.append(current)
            stack.extend(reversed(current.children))
        
        return results
    
    def _extract_function_info(self, node: tree_sitter.Node, content: str) -> dict:
        """Extract function information from node. Override in subclasses."""
        return {
            'name': '',
            'parameters': [],
            'return_type': None,
            'documentation': None,
            'signature': None,
            'is_async': False,
            'is_static': False,
            'is_exported': False,
        }
    
    def _extract_class_info(self, node: tree_sitter.Node, content: str) -> dict:
        """Extract class information from node. Override in subclasses."""
        return {
            'name': '',
            'base_classes': [],
            'methods': [],
            'attributes': [],
            'documentation': None,
            'is_exported': False,
        }
    
    def _extract_variable_info(self, node: tree_sitter.Node, content: str) -> dict:
        """Extract variable information from node. Override in subclasses."""
        return {
            'name': '',
            'type': None,
            'value': None,
            'is_constant': False,
            'is_static': False,
            'is_exported': False,
        }
