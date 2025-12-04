"""
Core data structures for markdown chunker v2.0.

This module consolidates all data types used throughout the system,
eliminating the duplication between chunker/types.py and parser/types.py
from v1.x.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class Chunk:
    """
    Single chunk of markdown content with validation.

    Attributes:
        content: Chunk content text
        start_line: Starting line number (1-based indexing)
        end_line: Ending line number (inclusive)
        metadata: Extensible metadata dictionary
    """

    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate chunk data on initialization."""
        if self.start_line < 1:
            raise ValueError(
                f"start_line must be >= 1 (1-based indexing), " f"got {self.start_line}"
            )
        if self.end_line < self.start_line:
            raise ValueError(
                f"end_line ({self.end_line}) must be >= "
                f"start_line ({self.start_line})"
            )
        if not self.content.strip():
            raise ValueError("chunk content cannot be empty or whitespace-only")

    @property
    def size(self) -> int:
        """Size in characters."""
        return len(self.content)

    @property
    def line_count(self) -> int:
        """Number of lines in chunk."""
        return self.end_line - self.start_line + 1

    def add_metadata(self, key: str, value: Any) -> None:
        """Add or update a metadata field."""
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value with optional default."""
        return self.metadata.get(key, default)


@dataclass
class ChunkingResult:
    """
    Result of chunking operation.

    Attributes:
        chunks: All generated chunks
        strategy_used: Name of applied strategy
        processing_time: Execution time in seconds
        fallback_used: Whether fallback was triggered
        fallback_level: How many strategies failed before success
        metadata: Result-level metadata
    """

    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    fallback_used: bool = False
    fallback_level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON/storage."""
        return {
            "chunks": [
                {
                    "content": chunk.content,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "metadata": chunk.metadata,
                }
                for chunk in self.chunks
            ],
            "strategy_used": self.strategy_used,
            "processing_time": self.processing_time,
            "fallback_used": self.fallback_used,
            "fallback_level": self.fallback_level,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkingResult":
        """Deserialize from dictionary."""
        chunks = [
            Chunk(
                content=chunk_data["content"],
                start_line=chunk_data["start_line"],
                end_line=chunk_data["end_line"],
                metadata=chunk_data.get("metadata", {}),
            )
            for chunk_data in data["chunks"]
        ]

        return cls(
            chunks=chunks,
            strategy_used=data["strategy_used"],
            processing_time=data["processing_time"],
            fallback_used=data.get("fallback_used", False),
            fallback_level=data.get("fallback_level", 0),
            metadata=data.get("metadata", {}),
        )

    @property
    def chunk_count(self) -> int:
        """Total number of chunks."""
        return len(self.chunks)

    @property
    def total_size(self) -> int:
        """Total size of all chunks in characters."""
        return sum(chunk.size for chunk in self.chunks)

    @property
    def average_chunk_size(self) -> float:
        """Average chunk size in characters."""
        return self.total_size / self.chunk_count if self.chunk_count > 0 else 0.0


@dataclass
class ContentAnalysis:
    """
    Stage 1 analysis result containing document metrics.

    This is produced by the Parser and used for strategy selection.

    Attributes:
        total_chars: Total character count
        total_lines: Total line count
        code_ratio: Proportion of code content (0.0-1.0)
        text_ratio: Proportion of text content (0.0-1.0)
        code_block_count: Number of fenced code blocks
        header_count: Total header count
        max_header_depth: Maximum header level (1-6)
        table_count: Number of tables
        content_type: "code", "text", or "mixed"
        languages: Programming languages detected
        code_blocks: List of extracted code blocks
        headers: List of extracted headers
        tables: List of extracted tables
    """

    total_chars: int
    total_lines: int
    code_ratio: float
    text_ratio: float
    code_block_count: int
    header_count: int
    max_header_depth: int
    table_count: int
    content_type: str
    languages: Set[str] = field(default_factory=set)
    code_blocks: List["FencedBlock"] = field(default_factory=list)
    headers: List["Header"] = field(default_factory=list)
    tables: List["Table"] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate analysis data."""
        if not 0.0 <= self.code_ratio <= 1.0:
            raise ValueError(f"code_ratio must be in [0.0, 1.0], got {self.code_ratio}")
        if not 0.0 <= self.text_ratio <= 1.0:
            raise ValueError(f"text_ratio must be in [0.0, 1.0], got {self.text_ratio}")
        if self.content_type not in ("code", "text", "mixed"):
            raise ValueError(
                f"content_type must be 'code', 'text', or 'mixed', "
                f"got {self.content_type}"
            )

    @property
    def table_ratio(self) -> float:
        """Estimated proportion of table content."""
        return min(self.table_count * 0.1, 1.0)


@dataclass
class FencedBlock:
    """
    Extracted fenced code block.

    Attributes:
        content: Code content (without fences)
        language: Programming language identifier
        fence_type: "```" or "~~~"
        start_line: Starting line number
        end_line: Ending line number
    """

    content: str
    language: str
    fence_type: str
    start_line: int
    end_line: int


@dataclass
class Header:
    """
    Markdown header.

    Attributes:
        level: Header level (1-6)
        text: Header text content
        line_number: Line number where header appears
    """

    level: int
    text: str
    line_number: int

    def __post_init__(self) -> None:
        """Validate header data."""
        if not 1 <= self.level <= 6:
            raise ValueError(f"Header level must be 1-6, got {self.level}")


@dataclass
class Table:
    """
    Markdown table.

    Attributes:
        content: Complete table content
        start_line: Starting line number
        end_line: Ending line number
        row_count: Number of rows (including header)
    """

    content: str
    start_line: int
    end_line: int
    row_count: int


# Error types (4 total, reduced from 15+ in v1.x)


class ValidationError(Exception):
    """Raised when input validation fails or domain properties are violated."""

    pass


class ParsingError(Exception):
    """Raised when parser cannot process markdown document."""

    pass


class StrategyError(Exception):
    """Raised when a strategy fails to execute."""

    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid."""

    pass
