"""
markdown_chunker v2.0 - Simplified markdown chunking library.

This is the redesigned version with:
- Consolidated types in single types.py
- Simplified configuration (8 parameters instead of 32)
- 3 strategies instead of 6
- Linear pipeline without duplication
"""

from .types import Chunk, ContentAnalysis, FencedBlock, ChunkingResult, ChunkingMetrics
from .config import ChunkConfig
from .chunker import MarkdownChunker
from .validator import Validator, ValidationResult, validate_chunks

__version__ = "2.0.0"

__all__ = [
    "MarkdownChunker",
    "ChunkConfig",
    "Chunk",
    "ContentAnalysis",
    "FencedBlock",
    "ChunkingResult",
    "ChunkingMetrics",
    "Validator",
    "ValidationResult",
    "validate_chunks",
]


def chunk_text(text: str, config: ChunkConfig = None) -> list:
    """Convenience function to chunk text."""
    return MarkdownChunker(config).chunk(text)


def chunk_file(path: str, config: ChunkConfig = None) -> list:
    """Convenience function to chunk a file."""
    with open(path, encoding='utf-8') as f:
        return chunk_text(f.read(), config)
