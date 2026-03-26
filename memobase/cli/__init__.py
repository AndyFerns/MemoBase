"""
CLI module for MemoBase.

Command-line interface implementation.
"""

from memobase.cli.main import app
from memobase.cli.commands import *

__all__ = [
    "app",
]
