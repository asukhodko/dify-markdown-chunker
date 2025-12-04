"""
Strategy module exports.

This module provides the 4 chunking strategies:
- BaseStrategy: Abstract base class with shared utilities
- CodeAwareStrategy: Code + mixed content (merged from Code and Mixed)
- StructuralStrategy: Header-based chunking (simplified)
- TableStrategy: Table preservation
- FallbackStrategy: Universal fallback (renamed from Sentences)
"""

from .base import BaseStrategy
from .code_aware import CodeAwareStrategy
from .fallback import FallbackStrategy
from .structural import StructuralStrategy
from .table import TableStrategy

__all__ = [
    "BaseStrategy",
    "CodeAwareStrategy",
    "StructuralStrategy",
    "TableStrategy",
    "FallbackStrategy",
]
