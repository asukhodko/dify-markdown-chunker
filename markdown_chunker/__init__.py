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

# Provider for Dify plugin system
from markdown_chunker.provider import MarkdownChunkerProvider

__all__ = [
    "MarkdownChunker",
    "ChunkConfig", 
    "Chunk",
    "ContentAnalysis",
    "chunk_text",
    "chunk_file",
    "MarkdownChunkerProvider",
]

__version__ = "2.0.0"
