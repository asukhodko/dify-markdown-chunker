"""
Python Markdown Chunker - Advanced adaptive markdown chunking system.

This package provides intelligent chunking of Markdown documents with
automatic strategy selection based on content analysis.

Version 2.0 - Redesigned architecture with simplified API.

Quick Start:
    >>> from markdown_chunker import MarkdownChunker, ChunkConfig
    >>> chunker = MarkdownChunker()
    >>> chunks = chunker.chunk("# Hello\\n\\nWorld")
    >>> print(len(chunks))
    1
"""

__version__ = "2.0.0"

# Import everything from v2
from markdown_chunker_v2 import (
    MarkdownChunker,
    ChunkConfig,
    Chunk,
    ChunkingResult,
    ContentAnalysis,
    FencedBlock,
    Validator,
    ValidationResult,
    validate_chunks,
    chunk_text,
    chunk_file,
)

# Backward compatibility aliases
from markdown_chunker_v2.types import Header, TableBlock

# Provider class (for Dify plugin integration)
import importlib.util
from pathlib import Path

_provider_file = Path(__file__).parent.parent / "provider" / "markdown_chunker.py"
if _provider_file.exists():
    _spec = importlib.util.spec_from_file_location("_provider_module", _provider_file)
    _provider_module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_provider_module)
    MarkdownChunkerProvider = _provider_module.MarkdownChunkerProvider
else:
    MarkdownChunkerProvider = None


__all__ = [
    # Main classes
    "MarkdownChunker",
    "ChunkConfig",
    "Chunk",
    "ChunkingResult",
    # Analysis
    "ContentAnalysis",
    "FencedBlock",
    "Header",
    "TableBlock",
    # Validation
    "Validator",
    "ValidationResult",
    "validate_chunks",
    # Provider
    "MarkdownChunkerProvider",
    # Functions
    "chunk_text",
    "chunk_file",
    # Version
    "__version__",
]
