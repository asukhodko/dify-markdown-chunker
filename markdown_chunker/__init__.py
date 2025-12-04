"""
Markdown Chunker v2.0 - Simplified architecture.

This is a complete redesign reducing complexity from:
- 55 files to 12 files
- 32 config parameters to 8 parameters
- 1,853 tests to 50 property-based tests

Public API exports (7 total):
    - MarkdownChunker: Main chunking engine
    - chunk_markdown: Convenience function for text chunking
    - ChunkConfig: Configuration dataclass
    - Chunk: Chunk data structure
    - ChunkingResult: Result data structure
    - ContentAnalysis: Analysis data structure
"""

__version__ = "2.0.0"

# Main API
from .chunker import MarkdownChunker, chunk_markdown

# Configuration
from .config import ChunkConfig

# Core types
from .types import (
    Chunk,
    ChunkingResult,
    ConfigurationError,
    ContentAnalysis,
    ParsingError,
    StrategyError,
    ValidationError,
)

__all__ = [
    # Main class and function
    "MarkdownChunker",
    "chunk_markdown",
    # Configuration
    "ChunkConfig",
    # Data types
    "Chunk",
    "ChunkingResult",
    "ContentAnalysis",
    # Errors
    "ValidationError",
    "ParsingError",
    "StrategyError",
    "ConfigurationError",
]
