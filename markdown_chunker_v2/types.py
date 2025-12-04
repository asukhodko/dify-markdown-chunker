"""
Consolidated type definitions for markdown_chunker v2.

All types in one file - no duplication between parser and chunker.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FencedBlock:
    """
    Represents a fenced code block in markdown.
    
    Attributes:
        language: Programming language (e.g., 'python', 'javascript')
        content: The code content inside the fences
        start_line: Line number where block starts (1-indexed)
        end_line: Line number where block ends (1-indexed)
        start_pos: Character position in document
        end_pos: Character position in document
    """
    language: Optional[str]
    content: str
    start_line: int
    end_line: int
    start_pos: int = 0
    end_pos: int = 0


@dataclass
class TableBlock:
    """
    Represents a markdown table.
    
    Attributes:
        content: Full table content including header and rows
        start_line: Line number where table starts
        end_line: Line number where table ends
        column_count: Number of columns
        row_count: Number of data rows (excluding header)
    """
    content: str
    start_line: int
    end_line: int
    column_count: int = 0
    row_count: int = 0


@dataclass
class Header:
    """
    Represents a markdown header.
    
    Attributes:
        level: Header level (1-6)
        text: Header text content
        line: Line number (1-indexed)
        pos: Character position in document
    """
    level: int
    text: str
    line: int
    pos: int = 0


@dataclass
class ContentAnalysis:
    """
    Result of analyzing a markdown document.
    
    Contains metrics and extracted elements for strategy selection.
    """
    # Basic metrics
    total_chars: int
    total_lines: int
    
    # Content ratios
    code_ratio: float  # code_chars / total_chars
    
    # Element counts
    code_block_count: int
    header_count: int
    max_header_depth: int
    table_count: int
    list_count: int = 0
    
    # Extracted elements
    code_blocks: List[FencedBlock] = field(default_factory=list)
    headers: List[Header] = field(default_factory=list)
    tables: List[TableBlock] = field(default_factory=list)
    
    # Additional metrics
    has_preamble: bool = False
    preamble_end_line: int = 0


@dataclass
class Chunk:
    """
    A chunk of markdown content.
    
    Attributes:
        content: The text content of the chunk
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        metadata: Additional information about the chunk
    """
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate chunk on creation."""
        if self.start_line < 1:
            raise ValueError(f"start_line must be >= 1, got {self.start_line}")
        if self.end_line < self.start_line:
            raise ValueError(f"end_line ({self.end_line}) must be >= start_line ({self.start_line})")
        if not self.content.strip():
            raise ValueError("Chunk content cannot be empty or whitespace-only")
    
    @property
    def size(self) -> int:
        """Size of chunk in characters."""
        return len(self.content)
    
    @property
    def line_count(self) -> int:
        """Number of lines in chunk."""
        return self.content.count('\n') + 1
    
    @property
    def is_oversize(self) -> bool:
        """Whether chunk is marked as intentionally oversize."""
        return self.metadata.get("allow_oversize", False)
    
    @property
    def strategy(self) -> str:
        """Strategy that created this chunk."""
        return self.metadata.get("strategy", "unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "size": self.size,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """Create from dictionary."""
        return cls(
            content=data["content"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChunkingResult:
    """
    Result of chunking a document.
    
    Contains chunks and metadata about the chunking process.
    """
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float = 0.0
    total_chars: int = 0
    total_lines: int = 0
    
    @property
    def chunk_count(self) -> int:
        """Number of chunks produced."""
        return len(self.chunks)
    
    @property
    def total_output_size(self) -> int:
        """Total size of all chunks."""
        return sum(c.size for c in self.chunks)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "chunks": [c.to_dict() for c in self.chunks],
            "strategy_used": self.strategy_used,
            "processing_time": self.processing_time,
            "total_chars": self.total_chars,
            "total_lines": self.total_lines,
            "chunk_count": self.chunk_count,
        }
