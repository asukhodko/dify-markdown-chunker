"""
Backward compatibility shim for markdown_chunker.chunker imports.
"""

from markdown_chunker_v2 import MarkdownChunker
from markdown_chunker_v2.types import Chunk
from markdown_chunker_v2.config import ChunkConfig

__all__ = ["MarkdownChunker", "Chunk", "ChunkConfig"]
