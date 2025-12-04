"""
Chunking strategies for Stage 2.

This package contains all the chunking strategies that can be applied
to Markdown documents based on their content characteristics.

Available Strategies:
- BaseStrategy: Abstract base class for all strategies
- CodeStrategy: For code-heavy documents (≥70% code)
- MixedStrategy: For mixed content with balanced elements
- ListStrategy: For list-heavy documents (≥5 lists)
- TableStrategy: For table-heavy documents (≥3 tables)
- StructuralStrategy: For structured documents with headers
- SentencesStrategy: Universal fallback strategy
"""

from .base import BaseStrategy

# Strategy imports (will be uncommented as implemented)
from .code_strategy import CodeStrategy
from .list_strategy import ListStrategy
from .mixed_strategy import MixedStrategy
from .sentences_strategy import SentencesStrategy
from .structural_strategy import StructuralStrategy
from .table_strategy import TableStrategy

__all__ = [
    "BaseStrategy",
    # Strategy classes (to be uncommented as implemented)
    "CodeStrategy",
    "MixedStrategy",
    "ListStrategy",
    "TableStrategy",
    "StructuralStrategy",
    "SentencesStrategy",
]
