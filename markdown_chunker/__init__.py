"""
markdown_chunker - Production-ready markdown chunking for RAG systems.

This module re-exports the v2 implementation as the primary API.
"""

# Re-export v2 as the main implementation
from markdown_chunker_v2 import (
    MarkdownChunker,
    ChunkConfig,
    Chunk,
    ContentAnalysis,
    chunk_text,
    chunk_file,
)

# For backward compatibility with legacy imports
try:
    from markdown_chunker_v2.compat import MarkdownChunkerProvider
except ImportError:
    pass

__all__ = [
    "MarkdownChunker",
    "ChunkConfig", 
    "Chunk",
    "ContentAnalysis",
    "chunk_text",
    "chunk_file",
]

__version__ = "2.0.0"
