"""
Core data structures for Stage 2 chunking system.

This module defines the fundamental data types used throughout the Stage 2
chunking system, including chunks, configuration, and result structures.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ContentType(Enum):
    """Types of content that can be found in chunks."""

    CODE = "code"
    TEXT = "text"
    LIST = "list"
    TABLE = "table"
    MIXED = "mixed"
    HEADER = "header"
    PREAMBLE = "preamble"


class StrategyType(Enum):
    """Available chunking strategies."""

    CODE = "code"
    MIXED = "mixed"
    LIST = "list"
    TABLE = "table"
    STRUCTURAL = "structural"
    SENTENCES = "sentences"


@dataclass
class Chunk:
    """
    Represents a single chunk of content with metadata.

    A chunk is a semantically meaningful fragment of a Markdown document
    that preserves context and structure while fitting within size constraints.
    """

    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate chunk data after initialization."""
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1 (1-based line numbering)")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if not self.content.strip():
            raise ValueError("chunk content cannot be empty or whitespace-only")

    @property
    def size(self) -> int:
        """
        Size of chunk content in characters.

        Returns:
            Number of characters in the chunk content (len(content)).

        Examples:
            >>> chunk=Chunk("# Hello\\nWorld", 1, 2, {})
            >>> print(chunk.size)
            13
        """
        return len(self.content)

    @property
    def line_count(self) -> int:
        """
        Number of lines in the chunk.

        Calculated as end_line - start_line + 1 (inclusive range).

        Returns:
            Number of lines spanned by this chunk.

        Examples:
            >>> chunk=Chunk("content", start_line=5, end_line=10, metadata={})
            >>> print(chunk.line_count)
            6
        """
        return self.end_line - self.start_line + 1

    @property
    def content_type(self) -> str:
        """
        Type of content in this chunk.

        Returns:
            Content type from metadata. Common values:
            - "code": Code block
            - "text": Plain text
            - "list": List items
            - "table": Table content
            - "mixed": Mixed content
            Defaults to "text" if not set.

        Examples:
            >>> chunk=Chunk("```python\\ncode\\n```", 1, 3, {"content_type": "code"})
            >>> print(chunk.content_type)
            'code'
        """
        return self.metadata.get("content_type", "text")

    @property
    def strategy(self) -> str:
        """
        Strategy used to create this chunk.

        Returns:
            Strategy name from metadata. Common values:
            - "code": Code strategy
            - "structural": Structural strategy
            - "sentences": Sentences strategy
            - "list": List strategy
            - "table": Table strategy
            - "mixed": Mixed strategy
            Defaults to "unknown" if not set.

        Examples:
            >>> chunk=Chunk("content", 1, 1, {"strategy": "code"})
            >>> print(chunk.strategy)
            'code'
        """
        return self.metadata.get("strategy", "unknown")

    @property
    def language(self) -> Optional[str]:
        """
        Programming language for code chunks.

        Returns:
            Language identifier (e.g., "python", "javascript", "rust")
            or None if not a code chunk or language not detected.

        Examples:
            >>> chunk=Chunk("```python\\ncode\\n```", 1, 3, {"language": "python"})
            >>> print(chunk.language)
            'python'
            >>>
            >>> text_chunk=Chunk("text", 1, 1, {})
            >>> print(text_chunk.language)
            None
        """
        return self.metadata.get("language")

    @property
    def is_oversize(self) -> bool:
        """
        Whether this chunk exceeds normal size limits.

        Returns:
            True if chunk was allowed to exceed max_chunk_size
            (typically for indivisible elements like code blocks or tables).
            False otherwise.

        Examples:
            >>> # Large code block that couldn't be split
            >>> chunk=Chunk(large_code, 1, 50, {"allow_oversize": True})
            >>> print(chunk.is_oversize)
            True
            >>> print(chunk.size > 4096)  # Exceeds default max
            True
        """
        return self.metadata.get("allow_oversize", False)

    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the chunk.

        Args:
            key: Metadata key (string)
            value: Metadata value (any JSON-serializable type)

        Examples:
            >>> chunk=Chunk("content", 1, 1, {})
            >>> chunk.add_metadata("custom_field", "value")
            >>> chunk.add_metadata("importance", 0.95)
            >>> print(chunk.metadata)
            {'custom_field': 'value', 'importance': 0.95}
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get metadata value with optional default.

        Args:
            key: Metadata key to retrieve
            default: Default value if key not found (default: None)

        Returns:
            Metadata value or default if key doesn't exist

        Examples:
            >>> chunk=Chunk("content", 1, 1, {"strategy": "code"})
            >>> print(chunk.get_metadata("strategy"))
            'code'
            >>> print(chunk.get_metadata("missing", "default"))
            'default'
        """
        return self.metadata.get(key, default)

    def get_section_path(self) -> List[str]:
        """
        Get hierarchical section path (Phase 2).

        Returns:
            List of header texts forming the path to this chunk's section.
            Empty list if no section path available.

        Examples:
            >>> chunk=Chunk(
            ...     "content", 1, 1,
            ...     {"section_path": ["Chapter 1", "Introduction"]}
            ... )
            >>> print(chunk.get_section_path())
            ['Chapter 1', 'Introduction']
        """
        return self.metadata.get("section_path", [])

    def get_source_range(self) -> tuple[int, int]:
        """
        Get character offset range in source document (Phase 2).

        Returns:
            Tuple of (start_offset, end_offset) in characters from document start.
            Returns (0, 0) if offsets not available.

        Examples:
            >>> chunk=Chunk("content", 1, 1, {"start_offset": 100, "end_offset": 200})
            >>> start, end = chunk.get_source_range()
            >>> print(f"Chunk spans characters {start}-{end}")
            Chunk spans characters 100-200
        """
        return (
            self.metadata.get("start_offset", 0),
            self.metadata.get("end_offset", 0),
        )

    def get_section_id(self) -> str:
        """
        Get stable section identifier (Phase 2).

        Returns:
            Section ID slug (e.g., "chapter-1-introduction") or empty string.

        Examples:
            >>> chunk=Chunk("content", 1, 1, {"section_id": "intro-section"})
            >>> print(chunk.get_section_id())
            'intro-section'
        """
        return self.metadata.get("section_id", "")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert chunk to dictionary for JSON serialization.

        Returns:
            Dictionary with all chunk data including:
            - content: Chunk text
            - start_line, end_line: Line range
            - size: Character count
            - line_count: Number of lines
            - content_type: Type of content
            - metadata: All metadata

        Examples:
            >>> chunk=Chunk("# Hello", 1, 1, {"strategy": "structural"})
            >>> data=chunk.to_dict()
            >>> print(data['content'])
            '# Hello'
            >>> print(data['size'])
            7
            >>> import json
            >>> json_str=json.dumps(data)  # Fully serializable
        """
        return {
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "size": self.size,
            "line_count": self.line_count,
            "content_type": self.content_type,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Chunk":
        """
        Create chunk from dictionary.

        Args:
            data: Dictionary with chunk data (from to_dict())

        Returns:
            New Chunk instance

        Examples:
            >>> data={
            ...     "content": "# Hello",
            ...     "start_line": 1,
            ...     "end_line": 1,
            ...     "metadata": {"strategy": "structural"}
            ... }
            >>> chunk=Chunk.from_dict(data)
            >>> print(chunk.content)
            '# Hello'
        """
        return cls(
            content=data["content"],
            start_line=data["start_line"],
            end_line=data["end_line"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class ChunkingResult:
    """
    Complete result of a chunking operation.

    Contains the generated chunks along with analysis information,
    performance metrics, and any errors encountered.
    """

    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    fallback_used: bool = False
    fallback_level: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Analysis information (populated from Stage 1)
    total_chars: int = 0
    total_lines: int = 0
    content_type: str = "unknown"
    complexity_score: float = 0.0

    @property
    def total_chunks(self) -> int:
        """
        Total number of chunks created.

        Returns:
            Count of chunks in the result.

        Examples:
            >>> result=chunker.chunk(text, include_analysis=True)
            >>> print(f"Created {result.total_chunks} chunks")
        """
        return len(self.chunks)

    @property
    def average_chunk_size(self) -> float:
        """
        Average chunk size in characters.

        Returns:
            Mean size of all chunks, or 0.0 if no chunks.

        Examples:
            >>> result=chunker.chunk(text, include_analysis=True)
            >>> print(f"Average: {result.average_chunk_size:.0f} chars")
        """
        if not self.chunks:
            return 0.0
        return sum(chunk.size for chunk in self.chunks) / len(self.chunks)

    @property
    def min_chunk_size(self) -> int:
        """
        Size of smallest chunk.

        Returns:
            Size of smallest chunk in characters, or 0 if no chunks.

        Examples:
            >>> result=chunker.chunk(text, include_analysis=True)
            >>> print(f"Range: {result.min_chunk_size}-{result.max_chunk_size}")
        """
        if not self.chunks:
            return 0
        return min(chunk.size for chunk in self.chunks)

    @property
    def max_chunk_size(self) -> int:
        """
        Size of largest chunk.

        Returns:
            Size of largest chunk in characters, or 0 if no chunks.

        Examples:
            >>> result=chunker.chunk(text, include_analysis=True)
            >>> if result.max_chunk_size > config.max_chunk_size:
            ...     print("Has oversized chunks")
        """
        if not self.chunks:
            return 0
        return max(chunk.size for chunk in self.chunks)

    @property
    def success(self) -> bool:
        """
        Whether chunking completed successfully.

        Returns:
            True if chunks were created and no critical errors occurred.
            False if no chunks or critical errors present.

        Examples:
            >>> result=chunker.chunk(text, include_analysis=True)
            >>> if result.success:
            ...     process_chunks(result.chunks)
            >>> else:
            ...     print(f"Errors: {result.errors}")
        """
        return len(self.chunks) > 0 and not any(
            "critical" in error.lower() for error in self.errors
        )

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the chunking result."""
        return {
            "success": self.success,
            "total_chunks": self.total_chunks,
            "strategy_used": self.strategy_used,
            "fallback_used": self.fallback_used,
            "fallback_level": self.fallback_level,
            "processing_time": self.processing_time,
            "average_chunk_size": self.average_chunk_size,
            "size_range": [self.min_chunk_size, self.max_chunk_size],
            "total_chars": self.total_chars,
            "content_type": self.content_type,
            "complexity_score": self.complexity_score,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        return {
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "strategy_used": self.strategy_used,
            "processing_time": self.processing_time,
            "fallback_used": self.fallback_used,
            "fallback_level": self.fallback_level,
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": {
                "total_chunks": self.total_chunks,
                "total_chars": self.total_chars,
                "total_lines": self.total_lines,
                "average_chunk_size": self.average_chunk_size,
                "min_chunk_size": self.min_chunk_size,
                "max_chunk_size": self.max_chunk_size,
                "content_type": self.content_type,
                "complexity_score": self.complexity_score,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkingResult":
        """Create result from dictionary."""
        chunks = [Chunk.from_dict(c) for c in data["chunks"]]
        stats = data.get("statistics", {})

        return cls(
            chunks=chunks,
            strategy_used=data["strategy_used"],
            processing_time=data["processing_time"],
            fallback_used=data.get("fallback_used", False),
            fallback_level=data.get("fallback_level", 0),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
            total_chars=stats.get("total_chars", 0),
            total_lines=stats.get("total_lines", 0),
            content_type=stats.get("content_type", "unknown"),
            complexity_score=stats.get("complexity_score", 0.0),
        )


@dataclass
class ChunkConfig:
    """
    Configuration for chunking behavior.

    Controls all aspects of the chunking process including size limits,
    strategy selection thresholds, overlap settings, and behavior flags.

    This dataclass provides fine-grained control over how markdown documents
    are chunked. All parameters have sensible defaults for most use cases,
    and factory methods provide pre-configured profiles for common scenarios.

    Attributes:
        max_chunk_size: Maximum size in characters per chunk (default: 4096).
            Chunks may exceed this if allow_oversize=True for indivisible elements.
        min_chunk_size: Minimum size in characters per chunk (default: 512).
            Smaller chunks may be created for structural elements.
        target_chunk_size: Target size for chunks (default: 2048).
            Chunker aims for this size when possible.
        overlap_size: Size of overlap in characters (default: 200).
            Used when enable_overlap=True.
        overlap_percentage: Percentage of chunk to overlap (default: 0.1).
            Maximum overlap is min(overlap_size, chunk_size * overlap_percentage).
        enable_overlap: Whether to create overlapping chunks (default: True).
            Useful for maintaining context in RAG applications.
        code_ratio_threshold: Threshold for code strategy selection (default: 0.7).
            Document must have ≥70% code content.
        min_code_blocks: Minimum code blocks for code strategy (default: 3).
        min_complexity: Minimum complexity for mixed strategy (default: 0.3).
        list_count_threshold: Minimum lists for list strategy (default: 5).
        list_ratio_threshold: Threshold for list strategy (default: 0.6).
        table_count_threshold: Minimum tables for table strategy (default: 3).
        table_ratio_threshold: Threshold for table strategy (default: 0.4).
        header_count_threshold: Minimum headers for structural strategy (default: 3).
        allow_oversize: Allow chunks larger than max_chunk_size (default: True).
            For indivisible elements like code blocks or tables.
        preserve_code_blocks: Keep code blocks intact (default: True).
        preserve_tables: Keep tables intact (default: True).
        preserve_list_hierarchy: Keep list items together (default: True).
        enable_fallback: Enable fallback strategies (default: True).
        fallback_strategy: Strategy to use when primary fails (default: "sentences").
        max_fallback_level: Maximum fallback depth (default: 4).
        enable_streaming: Enable streaming for large documents (default: False).
        streaming_threshold: Size threshold for streaming (default: 10MB).

    Examples:
        >>> # Default configuration
        >>> config=ChunkConfig()
        >>> print(config.max_chunk_size)
        4096

        >>> # Custom configuration
        >>> config=ChunkConfig(
        ...     max_chunk_size=2048,
        ...     enable_overlap=True,
        ...     overlap_size=100
        ... )

        >>> # Using factory methods
        >>> config=ChunkConfig.for_code_heavy()
        >>> config=ChunkConfig.for_dify_rag()
        >>> config=ChunkConfig.for_chat_context()

    See Also:
        - default(): Default configuration
        - for_code_heavy(): For code-heavy documents
        - for_dify_rag(): For RAG systems
        - for_chat_context(): For chat/LLM context
        - for_search_indexing(): For search indexing

    Notes:
        - Configuration is validated in __post_init__
        - Invalid values are auto-adjusted when possible
        - All size parameters are in characters, not bytes
        - Factory methods provide optimized presets
    """

    # Size limits (in characters)
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    target_chunk_size: int = 2048

    # Overlap settings
    overlap_size: int = 200
    overlap_percentage: float = 0.1  # 10% overlap
    enable_overlap: bool = True

    # Strategy selection thresholds
    code_ratio_threshold: float = 0.3  # Lowered from 0.7 to handle real-world docs
    min_code_blocks: int = 1  # Lowered from 3 to handle docs with few code blocks
    min_complexity: float = 0.3
    list_count_threshold: int = 5
    list_ratio_threshold: float = 0.6
    table_count_threshold: int = 3
    table_ratio_threshold: float = 0.4
    header_count_threshold: int = 3

    # Behavior flags
    allow_oversize: bool = True
    preserve_code_blocks: bool = True
    preserve_tables: bool = True
    preserve_list_hierarchy: bool = True

    # Fallback settings
    enable_fallback: bool = True
    fallback_strategy: str = "sentences"
    max_fallback_level: int = 4

    # Content validation settings (Phase 1 Fix 3)
    enable_content_validation: bool = True  # Validate no content loss

    # Performance settings
    enable_streaming: bool = False
    streaming_threshold: int = 10 * 1024 * 1024  # 10MB

    # Preamble settings
    extract_preamble: bool = True
    separate_preamble_chunk: bool = False
    preamble_min_size: int = 10

    # Phase 2: Semantic quality parameters
    section_boundary_level: int = 2  # H2 by default (1-6)
    min_content_per_chunk: int = 50  # Minimum actual content (excluding headers)
    preserve_markdown_structure: bool = True
    # Note: Oversize chunks are ALWAYS created for atomic blocks > max_chunk_size
    # This is required behavior per Phase 2 Requirements 1.5 and 5.5 (no data loss)

    def __post_init__(self) -> None:  # noqa: C901
        """Validate and auto-adjust configuration after initialization."""
        # Complexity justified: Comprehensive validation of all config parameters
        if self.max_chunk_size <= 0:
            raise ValueError("max_chunk_size must be positive")
        if self.min_chunk_size <= 0:
            raise ValueError("min_chunk_size must be positive")

        # Auto-adjust min_chunk_size if necessary
        if self.min_chunk_size >= self.max_chunk_size:
            # Allow equal values or auto-adjust
            if self.min_chunk_size > self.max_chunk_size:
                self.min_chunk_size = max(1, self.max_chunk_size // 2)

        # Auto-adjust target_chunk_size if necessary
        if self.target_chunk_size > self.max_chunk_size:
            self.target_chunk_size = self.max_chunk_size
        if self.target_chunk_size < self.min_chunk_size:
            self.target_chunk_size = self.min_chunk_size

        # Validate percentages
        if not (0.0 <= self.overlap_percentage <= 1.0):
            raise ValueError("overlap_percentage must be between 0.0 and 1.0")
        if not (0.0 <= self.code_ratio_threshold <= 1.0):
            raise ValueError("code_ratio_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.list_ratio_threshold <= 1.0):
            raise ValueError("list_ratio_threshold must be between 0.0 and 1.0")
        if not (0.0 <= self.table_ratio_threshold <= 1.0):
            raise ValueError("table_ratio_threshold must be between 0.0 and 1.0")

        # Validate preamble settings
        if self.preamble_min_size < 0:
            raise ValueError("preamble_min_size must be non-negative")

        # Validate Phase 2 parameters
        if not (1 <= self.section_boundary_level <= 6):
            raise ValueError("section_boundary_level must be between 1 and 6")
        if self.min_content_per_chunk < 0:
            raise ValueError("min_content_per_chunk must be non-negative")

        # Final invariant check
        assert (
            self.min_chunk_size <= self.target_chunk_size <= self.max_chunk_size
        ), "Size invariant violated after auto-adjustment"

    @classmethod
    def default(cls) -> "ChunkConfig":
        """
        Create default configuration.

        Returns a configuration with balanced settings suitable for
        most markdown documents. Good starting point for general use.

        Returns:
            ChunkConfig with default values:
            - max_chunk_size: 4096
            - min_chunk_size: 512
            - target_chunk_size: 2048
            - enable_overlap: True
            - overlap_size: 200

        Examples:
            >>> config=ChunkConfig.default()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(markdown_text)

        See Also:
            - ChunkConfig(): Direct instantiation (equivalent)
            - for_code_heavy(): For code-heavy documents
            - for_dify_rag(): For RAG systems
        """
        return cls()

    @classmethod
    def for_code_heavy(cls) -> "ChunkConfig":
        """
        Configuration optimized for code-heavy documents.

        Larger chunks with aggressive code detection. Ideal for
        technical documentation, API references, and tutorials
        with extensive code examples.

        Returns:
            ChunkConfig optimized for code:
            - max_chunk_size: 6144 (larger for complete code blocks)
            - target_chunk_size: 3072
            - code_ratio_threshold: 0.5 (more aggressive detection)
            - min_code_blocks: 2
            - overlap_size: 300 (larger for code context)
            - preserve_code_blocks: True

        Examples:
            >>> config=ChunkConfig.for_code_heavy()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(api_documentation)
            >>>
            >>> # Most chunks will use code strategy
            >>> print(chunks[0].metadata['strategy'])
            'code'

        See Also:
            - for_api_docs(): Alternative for API documentation
            - for_code_docs(): For pure code documentation

        Notes:
            - Preserves code blocks as single units when possible
            - Allows oversized chunks for large code blocks
            - Larger overlap maintains code context
        """
        return cls(
            max_chunk_size=6144,  # Larger chunks for code
            target_chunk_size=3072,
            code_ratio_threshold=0.5,  # More aggressive code detection
            min_code_blocks=2,
            allow_oversize=True,
            preserve_code_blocks=True,
            overlap_size=300,  # Larger overlap for code context
        )

    @classmethod
    def for_structured_docs(cls) -> "ChunkConfig":
        """
        Configuration optimized for structured documentation.

        Medium-sized chunks that respect document hierarchy.
        Ideal for well-organized documentation with clear sections,
        headers, and lists.

        Returns:
            ChunkConfig optimized for structured docs:
            - max_chunk_size: 3072
            - target_chunk_size: 1536
            - header_count_threshold: 2 (aggressive structural detection)
            - preserve_list_hierarchy: True
            - overlap_size: 150

        Examples:
            >>> config=ChunkConfig.for_structured_docs()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(user_manual)
            >>>
            >>> # Chunks respect section boundaries
            >>> for chunk in chunks:
            ...     print(f"Lines {chunk.start_line}-{chunk.end_line}")

        See Also:
            - for_api_docs(): For API documentation
            - default(): For general documents

        Notes:
            - Respects markdown hierarchy (headers, lists)
            - Smaller chunks for better section granularity
            - Preserves list structure
        """
        return cls(
            max_chunk_size=3072,
            target_chunk_size=1536,
            header_count_threshold=2,  # More aggressive structural detection
            preserve_list_hierarchy=True,
            overlap_size=150,
        )

    @classmethod
    def for_large_documents(cls) -> "ChunkConfig":
        """
        Configuration optimized for large documents.

        Large chunks with streaming enabled for memory efficiency.
        Ideal for processing books, long articles, or documentation
        sets exceeding 10MB.

        Returns:
            ChunkConfig optimized for large docs:
            - max_chunk_size: 8192 (large chunks)
            - target_chunk_size: 4096
            - enable_streaming: True
            - overlap_size: 400
            - overlap_percentage: 0.05 (smaller percentage)

        Examples:
            >>> config=ChunkConfig.for_large_documents()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(book_content)  # 50MB document
            >>>
            >>> # Fewer, larger chunks
            >>> print(f"Created {len(chunks)} chunks")
            >>> print(f"Avg size: {sum(c.size for c in chunks) / len(chunks)}")

        See Also:
            - for_fast_processing(): For maximum throughput
            - compact(): For smaller chunks

        Notes:
            - Streaming reduces memory usage for large documents
            - Larger chunks mean fewer total chunks
            - Smaller overlap percentage for efficiency
        """
        return cls(
            max_chunk_size=8192,  # Larger chunks
            target_chunk_size=4096,
            enable_streaming=True,
            overlap_size=400,
            overlap_percentage=0.05,  # Smaller percentage overlap
        )

    @classmethod
    def compact(cls) -> "ChunkConfig":
        """
        Configuration for smaller, more numerous chunks.

        Small chunks for fine-grained processing. Ideal for
        applications requiring high granularity like detailed
        search indexing or precise context extraction.

        Returns:
            ChunkConfig with compact settings:
            - max_chunk_size: 2048 (small chunks)
            - min_chunk_size: 256
            - target_chunk_size: 1024
            - overlap_size: 100

        Examples:
            >>> config=ChunkConfig.compact()
            >>> chunker=MarkdownChunker(config)
            >>> chunks=chunker.chunk(markdown_text)
            >>>
            >>> # Many small chunks
            >>> print(f"Created {len(chunks)} chunks")
            >>> print(f"Avg size: {sum(c.size for c in chunks) / len(chunks)}")
            >>> # Typically: avg size ~1000 chars

        See Also:
            - for_search_indexing(): For search applications
            - for_chat_context(): For chat/LLM context
            - for_large_documents(): Opposite approach

        Notes:
            - More chunks=more granular retrieval
            - Smaller chunks=better for precise matching
            - Good for semantic search applications
        """
        return cls(
            max_chunk_size=2048,
            min_chunk_size=256,
            target_chunk_size=1024,
            overlap_size=100,
        )

    @classmethod
    def for_api_default(cls) -> "ChunkConfig":
        """
        Default configuration for API usage.

        Balanced settings suitable for most API use cases with
        reasonable chunk sizes and overlap for context preservation.
        """
        return cls(
            max_chunk_size=4096,
            min_chunk_size=512,
            target_chunk_size=2048,
            overlap_size=200,
            enable_overlap=True,
            code_ratio_threshold=0.7,
            allow_oversize=True,
        )

    @classmethod
    def for_dify_rag(cls) -> "ChunkConfig":
        """
        Optimized configuration for Dify RAG systems.

        Settings tuned for RAG (Retrieval-Augmented Generation) with
        moderate chunk sizes for better semantic search and retrieval.
        """
        return cls(
            max_chunk_size=3072,
            min_chunk_size=256,
            target_chunk_size=1536,
            overlap_size=150,
            enable_overlap=True,
            code_ratio_threshold=0.6,
            preserve_code_blocks=True,
            preserve_list_hierarchy=True,
            allow_oversize=False,
        )

    @classmethod
    def for_fast_processing(cls) -> "ChunkConfig":
        """
        Configuration optimized for fast processing.

        Larger chunks with minimal overlap for maximum throughput.
        Suitable for batch processing or when speed is priority.
        """
        return cls(
            max_chunk_size=8192,
            min_chunk_size=1024,
            target_chunk_size=4096,
            overlap_size=100,
            enable_overlap=False,
            allow_oversize=True,
            enable_streaming=True,
        )

    @classmethod
    def for_api_docs(cls) -> "ChunkConfig":
        """
        Configuration optimized for API documentation.

        Balanced settings for API docs with code examples and structured content.
        """
        return cls(
            max_chunk_size=3072,
            min_chunk_size=256,
            overlap_size=150,
            enable_overlap=True,
            code_ratio_threshold=0.6,
            list_count_threshold=3,
            table_count_threshold=2,
            min_complexity=0.2,
        )

    @classmethod
    def for_code_docs(cls) -> "ChunkConfig":
        """
        Configuration optimized for code documentation.

        Smaller chunks with no overlap, optimized for code blocks.
        """
        return cls(
            max_chunk_size=2048,
            min_chunk_size=128,
            overlap_size=100,
            enable_overlap=False,
            code_ratio_threshold=0.8,
            preserve_code_blocks=True,
            list_count_threshold=8,
            table_count_threshold=5,
        )

    @classmethod
    def for_chat_context(cls) -> "ChunkConfig":
        """
        Configuration optimized for chat/LLM context.

        Smaller chunks suitable for chat context windows.
        """
        return cls(
            max_chunk_size=1536,
            min_chunk_size=200,
            overlap_size=200,
            enable_overlap=True,
            code_ratio_threshold=0.5,
            list_count_threshold=4,
            table_count_threshold=2,
            min_complexity=0.1,
        )

    @classmethod
    def for_search_indexing(cls) -> "ChunkConfig":
        """
        Configuration optimized for search indexing.

        Small chunks with overlap for better search granularity.
        """
        return cls(
            max_chunk_size=1024,
            min_chunk_size=100,
            overlap_size=100,
            enable_overlap=True,
            code_ratio_threshold=0.4,
            list_count_threshold=6,
            table_count_threshold=3,
            preserve_list_hierarchy=True,
        )

    def get_effective_overlap_size(self, chunk_size: int) -> int:
        """Calculate effective overlap size based on configuration."""
        percentage_based = int(chunk_size * self.overlap_percentage)
        quarter_limit = chunk_size // 4
        return min(self.overlap_size, percentage_based, quarter_limit)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for JSON serialization."""
        return {
            "max_chunk_size": self.max_chunk_size,
            "min_chunk_size": self.min_chunk_size,
            "overlap_size": self.overlap_size,
            "enable_overlap": self.enable_overlap,
            "code_ratio_threshold": self.code_ratio_threshold,
            "list_count_threshold": self.list_count_threshold,
            "table_count_threshold": self.table_count_threshold,
            "min_complexity": self.min_complexity,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkConfig":
        """Create config from dictionary with defaults."""
        return cls(
            max_chunk_size=data.get("max_chunk_size", 4096),
            min_chunk_size=data.get("min_chunk_size", 512),
            overlap_size=data.get("overlap_size", 200),
            enable_overlap=data.get("enable_overlap", True),
            code_ratio_threshold=data.get("code_ratio_threshold", 0.7),
            list_count_threshold=data.get("list_count_threshold", 5),
            table_count_threshold=data.get("table_count_threshold", 3),
            min_complexity=data.get("min_complexity", 0.3),
        )


@dataclass
class StrategyMetrics:
    """
    Metrics for strategy performance and selection.

    Used by the strategy selector to determine the best strategy
    for a given document based on content analysis.
    """

    strategy_name: str
    can_handle: bool
    quality_score: float
    priority: int
    final_score: float
    reason: str = ""

    def __post_init__(self) -> None:
        """Validate metrics after initialization."""
        if not (0.0 <= self.quality_score <= 1.0):
            raise ValueError("quality_score must be between 0.0 and 1.0")
        if self.priority < 1:
            raise ValueError("priority must be >= 1")
        if not (0.0 <= self.final_score <= 1.0):
            raise ValueError("final_score must be between 0.0 and 1.0")


# Type aliases for convenience
ChunkList = List[Chunk]
MetadataDict = Dict[str, Any]
StrategyName = str
