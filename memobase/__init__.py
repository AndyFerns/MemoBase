"""
MemoBase — Memory for Your Codebase

A production-grade, offline-first codebase memory system.
"""

__version__ = "1.0.0"
__author__ = "MemoBase Team"
__email__ = "team@memobase.dev"

from memobase.core.models import ParsedFile, MemoryUnit, Index, Graph, Findings
from memobase.core.interfaces import (
    ParserInterface,
    MemoryBuilderInterface,
    StorageInterface,
    IndexInterface,
    GraphInterface,
    QueryInterface,
)

__all__ = [
    "ParsedFile",
    "MemoryUnit", 
    "Index",
    "Graph",
    "Findings",
    "ParserInterface",
    "MemoryBuilderInterface",
    "StorageInterface",
    "IndexInterface",
    "GraphInterface",
    "QueryInterface",
]
