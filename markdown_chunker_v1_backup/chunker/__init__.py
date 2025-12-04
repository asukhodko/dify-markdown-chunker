"""
Stage 2: Advanced Markdown Chunking with Adaptive Strategies

This module implements a complete chunking system with 6 adaptive strategies
that automatically select the optimal approach based on content analysis.

Main Components:
- MarkdownChunker: Main interface for chunking operations
- Strategies: 6 specialized chunking strategies (Code, Mixed, List, Table, Structural, Sentences)  # noqa: E501
- Configuration: Flexible configuration system for chunking behavior
- Support: Overlap management, metadata enrichment, error handling

Usage:
    from markdown_chunker import MarkdownChunker, ChunkConfig

    chunker=MarkdownChunker()
    chunks=chunker.chunk(markdown_text)

    # Or with custom configuration
    config=ChunkConfig.for_code_heavy()
    chunker=MarkdownChunker(config)
    result=chunker.chunk_with_analysis(markdown_text)
"""

from .core import MarkdownChunker
from .types import Chunk, ChunkConfig, ChunkingResult

# Strategy exports (will be available after implementation)
# from .strategies import (
#     BaseStrategy,
#     CodeStrategy,
#     MixedStrategy,
#     ListStrategy,
#     TableStrategy,
#     StructuralStrategy,
#     SentencesStrategy
# )

__all__ = [
    # Main interface
    "MarkdownChunker",
    # Data structures
    "Chunk",
    "ChunkingResult",
    "ChunkConfig",
    # Strategies (to be uncommented as implemented)
    # 'BaseStrategy',
    # 'CodeStrategy',
    # 'MixedStrategy',
    # 'ListStrategy',
    # 'TableStrategy',
    # 'StructuralStrategy',
    # 'SentencesStrategy',
]

__version__ = "2.0.0"
