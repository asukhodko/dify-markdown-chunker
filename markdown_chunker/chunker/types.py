"""
Backward compatibility shim for markdown_chunker.chunker.types imports.
"""

from markdown_chunker_v2.types import Chunk, ContentAnalysis, FencedBlock, ChunkingResult
from markdown_chunker_v2.config import ChunkConfig

__all__ = ["Chunk", "ChunkConfig", "ContentAnalysis", "FencedBlock", "ChunkingResult"]
