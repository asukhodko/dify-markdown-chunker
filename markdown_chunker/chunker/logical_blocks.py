"""
Logical block data structures for Phase 2 semantic quality improvements.

This module defines LogicalBlock and Section classes that represent
semantic units in markdown documents. These structures enable section-aware
chunking that preserves logical relationships between headers and content.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class LogicalBlock:
    """
    Represents a semantic unit that should not be split.

    A LogicalBlock is an atomic unit of content (paragraph, list item, code block,
    table, or header) that maintains semantic coherence. Blocks are the building
    blocks for section-aware chunking.

    Attributes:
        block_type: Type of block ("paragraph", "list_item", "code", "table", "header")
        content: Rendered Markdown content of this block
        ast_node: Reference to the original AST node (for re-rendering)
        start_offset: Character offset from document start
        end_offset: Character offset from document end
        start_line: Line number where block starts (1-based)
        end_line: Line number where block ends (1-based)
        is_atomic: Whether this block can be split further (default: True)
        metadata: Additional metadata (e.g., block ID, language for code)

    Examples:
        >>> block = LogicalBlock(
        ...     block_type="paragraph",
        ...     content="This is a paragraph.",
        ...     ast_node=node,
        ...     start_offset=0,
        ...     end_offset=20,
        ...     start_line=1,
        ...     end_line=1,
        ...     is_atomic=True,
        ...     metadata={"id": "block_1"}
        ... )
        >>> print(block.size)
        20
    """

    block_type: str
    content: str
    ast_node: Any
    start_offset: int
    end_offset: int
    start_line: int
    end_line: int
    is_atomic: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def size(self) -> int:
        """
        Size of block content in characters.

        Returns:
            Number of characters in the block content.
        """
        return len(self.content)

    def __post_init__(self) -> None:
        """Validate block data after initialization."""
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1 (1-based line numbering)")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if self.start_offset < 0:
            raise ValueError("start_offset must be >= 0")
        if self.end_offset < self.start_offset:
            raise ValueError("end_offset must be >= start_offset")


@dataclass
class Section(LogicalBlock):
    """
    A section with header and content blocks.

    A Section represents a hierarchical unit in a markdown document, consisting
    of an optional header and a list of content blocks (paragraphs, lists, code,
    tables, sub-headers). Sections are used for section-aware chunking that
    respects document structure.

    Attributes:
        header: Optional header block for this section (None for root section)
        header_level: Header level (0 for root, 1-6 for H1-H6)
        header_text: Text content of the header
        header_path: Hierarchical path of headers (e.g., ["Parent", "Child"])
        content_blocks: List of LogicalBlocks in this section

    Examples:
        >>> section = Section(
        ...     block_type="section",
        ...     content="",  # Will be calculated from blocks
        ...     ast_node=None,
        ...     start_offset=0,
        ...     end_offset=100,
        ...     start_line=1,
        ...     end_line=10,
        ...     header=header_block,
        ...     header_level=2,
        ...     header_text="Introduction",
        ...     header_path=["Chapter 1", "Introduction"],
        ...     content_blocks=[para1, para2, list1]
        ... )
        >>> print(section.calculate_size())
        >>> print(section.can_split())
    """

    header: Optional[LogicalBlock] = None
    header_level: int = 0
    header_text: str = ""
    header_path: List[str] = field(default_factory=list)
    content_blocks: List[LogicalBlock] = field(default_factory=list)

    def calculate_size(self) -> int:
        """
        Calculate total size of section including header and all content blocks.

        Returns:
            Total size in characters of header + all content blocks.

        Examples:
            >>> section = Section(...)
            >>> size = section.calculate_size()
            >>> print(f"Section size: {size} chars")
        """
        size = len(self.header.content) if self.header else 0
        for block in self.content_blocks:
            size += len(block.content)
        return size

    def can_split(self) -> bool:
        """
        Check if section can be split into smaller chunks.

        A section can be split if it has more than one content block.
        Single-block sections are atomic.

        Returns:
            True if section has multiple content blocks, False otherwise.

        Examples:
            >>> section = Section(...)
            >>> if section.can_split():
            ...     chunks = split_section(section)
            >>> else:
            ...     chunk = create_single_chunk(section)
        """
        return len(self.content_blocks) > 1
