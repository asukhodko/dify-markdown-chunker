"""
Python Markdown Chunker - Advanced adaptive markdown chunking system.

This package provides intelligent chunking of Markdown documents with
automatic strategy selection based on content analysis.

Quick Start:
    >>> from markdown_chunker import MarkdownChunker
    >>> chunker=MarkdownChunker()
    >>> result=chunker.chunk_with_analysis("# Hello\\n\\nWorld")
    >>> print(len(result.chunks))
    1

API Modules:
    - parser: Markdown parsing and content analysis
    - chunker: Chunking with adaptive strategies
    - api: REST API adapters for integration (coming soon)
"""

__version__ = "1.0.0"

# Provider class (for Dify plugin integration)
# Import directly from provider module to avoid circular imports
import importlib.util
from pathlib import Path

from typing import Optional

# Main chunking interface
from .chunker.core import MarkdownChunker
from .chunker.types import Chunk, ChunkConfig, ChunkingResult

# Parser interface (for advanced usage) - now from core.py
from .parser.core import ParserInterface

# Preamble extraction (for advanced usage)
from .parser.preamble import (
    PreambleExtractor,
    PreambleInfo,
    PreambleType,
    extract_preamble,
)
from .parser.types import ContentAnalysis

_provider_file = Path(__file__).parent.parent / "provider" / "markdown_chunker.py"
_spec = importlib.util.spec_from_file_location("_provider_module", _provider_file)
_provider_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_provider_module)
MarkdownChunkerProvider = _provider_module.MarkdownChunkerProvider


# Convenience functions
def chunk_text(text: str, config: ChunkConfig = None) -> list:
    """
    Convenience function to chunk markdown text.

    Simple one-line interface for chunking markdown content.
    Automatically selects optimal strategy based on content analysis.

    Args:
        text: Markdown content to chunk. Must be valid UTF-8 text.
        config: Optional ChunkConfig. If None, uses default configuration.

    Returns:
        List of Chunk objects with content, line numbers, and metadata.

    Examples:
        >>> from markdown_chunker import chunk_text
        >>>
        >>> # Basic usage
        >>> chunks=chunk_text("# Hello\\n\\nWorld")
        >>> print(chunks[0].content)
        '# Hello\\n\\nWorld'
        >>> print(chunks[0].start_line)
        1
        >>>
        >>> # With custom config
        >>> from markdown_chunker import ChunkConfig
        >>> config=ChunkConfig.for_code_heavy()
        >>> chunks=chunk_text(code_document, config)
        >>> print(len(chunks))
        5
        >>>
        >>> # Access metadata
        >>> for chunk in chunks:
        ...     print(f"Strategy: {chunk.strategy}, Size: {chunk.size}")

    See Also:
        - chunk_file(): Chunk from file path
        - MarkdownChunker: Full API with analysis
        - ChunkConfig: Configuration options
    """
    chunker = MarkdownChunker(config)
    raw_result = chunker.chunk(text, include_analysis=True)
    result = raw_result  # type: ignore[assignment]
    return result.chunks


def chunk_file(file_path: str, config: Optional[ChunkConfig] = None) -> list:
    """
    Convenience function to chunk markdown file.

    Reads a markdown file and chunks its content. Handles file I/O
    and encoding automatically.

    Args:
        file_path: Path to markdown file (relative or absolute).
            File must exist and be readable.
        config: Optional ChunkConfig. If None, uses default configuration.

    Returns:
        List of Chunk objects with content, line numbers, and metadata.

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file is not valid UTF-8
        PermissionError: If file is not readable

    Examples:
        >>> from markdown_chunker import chunk_file
        >>>
        >>> # Basic usage
        >>> chunks=chunk_file("README.md")
        >>> print(f"Created {len(chunks)} chunks")
        >>>
        >>> # With custom config
        >>> from markdown_chunker import ChunkConfig
        >>> config=ChunkConfig.for_dify_rag()
        >>> chunks=chunk_file("docs/api.md", config)
        >>>
        >>> # Process all chunks
        >>> for i, chunk in enumerate(chunks, 1):
        ...     print(f"Chunk {i}: {chunk.size} chars")
        ...     print(f"Lines {chunk.start_line}-{chunk.end_line}")

    See Also:
        - chunk_text(): Chunk from string
        - MarkdownChunker: Full API with analysis
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return chunk_text(text, config)


__all__ = [
    # Main classes
    "MarkdownChunker",
    "ChunkConfig",
    "Chunk",
    "ChunkingResult",
    # Parser
    "ParserInterface",
    "ContentAnalysis",
    # Preamble extraction
    "PreambleExtractor",
    "PreambleInfo",
    "PreambleType",
    "extract_preamble",
    # Provider
    "MarkdownChunkerProvider",
    # Functions
    "chunk_text",
    "chunk_file",
    # Version
    "__version__",
]
