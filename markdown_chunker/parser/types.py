"""
Basic data structures for Stage 1 of Python Markdown Chunker.

This module defines the core data structures used throughout the system,
based on the technical specification from
docs/markdown-extractor/TECHNICAL-SPECIFICATION.md.
"""

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .enhanced_ast_builder import SourceRange


@dataclass
class Position:
    """Position information for elements in the source text."""

    line: int
    column: int
    offset: int  # Position in characters from the beginning of the document

    def __post_init__(self):
        """Validate position values."""
        if self.line < 0:
            raise ValueError(f"Line number must be non-negative, got {self.line}")
        if self.column < 0:
            raise ValueError(f"Column number must be non-negative, got {self.column}")
        if self.offset < 0:
            raise ValueError(f"Offset must be non-negative, got {self.offset}")


class NodeType(Enum):
    """Types of nodes in the Markdown AST."""

    DOCUMENT = "document"
    HEADER = "header"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    LIST = "list"
    LIST_ITEM = "list_item"
    TABLE = "table"
    TABLE_ROW = "table_row"
    TABLE_CELL = "table_cell"
    BLOCKQUOTE = "blockquote"
    TEXT = "text"
    EMPHASIS = "emphasis"
    STRONG = "strong"
    LINK = "link"
    IMAGE = "image"
    HORIZONTAL_RULE = "horizontal_rule"
    LINE_BREAK = "line_break"


@dataclass
class MarkdownNode:
    """Node in the Markdown AST with enhanced child support."""

    type: NodeType
    content: str
    start_pos: Position
    end_pos: Position
    children: List["MarkdownNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def find_children(self, node_type: NodeType) -> List["MarkdownNode"]:
        """Find all child nodes of a specific type."""
        result = []
        for child in self.children:
            if child.type == node_type:
                result.append(child)
            result.extend(child.find_children(node_type))
        return result

    def find_children_by_type(self, node_type: NodeType) -> List["MarkdownNode"]:
        """Find direct child nodes of a specific type (non-recursive)."""
        return [child for child in self.children if child.type == node_type]

    def get_text_content(self) -> str:
        """Get the textual content of the node and all its children."""
        if not self.children:
            return self.content

        text_parts = []

        # Add node's own content if it exists
        if self.content:
            text_parts.append(self.content)

        # Add children's content
        for child in self.children:
            child_content = child.get_text_content()
            if child_content:
                text_parts.append(child_content)

        return "".join(text_parts)

    def get_line_range(self) -> tuple[int, int]:
        """Get the line range of the node."""
        return (self.start_pos.line, self.end_pos.line)

    def get_size(self) -> int:
        """Get the size of the node in characters."""
        return len(self.get_text_content())

    def is_leaf(self) -> bool:
        """Check if the node is a leaf (has no children)."""
        return len(self.children) == 0

    def get_source_range(self) -> "SourceRange":
        """Get the source range of this node."""
        from .enhanced_ast_builder import SourceRange

        return SourceRange(start=self.start_pos, end=self.end_pos)

    def contains_position(self, position: Position) -> bool:
        """Check if this node contains the given position."""
        return (
            position.line > self.start_pos.line
            or (
                position.line == self.start_pos.line
                and position.column >= self.start_pos.column
            )
        ) and (
            position.line < self.end_pos.line
            or (
                position.line == self.end_pos.line
                and position.column <= self.end_pos.column
            )
        )

    def find_node_at_position(self, position: Position) -> Optional["MarkdownNode"]:
        """Find the deepest node that contains the given position."""
        if not self.contains_position(position):
            return None

        # Check children first (deepest match)
        for child in self.children:
            child_match = child.find_node_at_position(position)
            if child_match:
                return child_match

        # If no child contains the position, this node is the match
        return self

    def get_inline_elements(self) -> List["MarkdownNode"]:
        """Get all inline elements (links, emphasis, code, etc.) in this node."""
        inline_types = {
            NodeType.LINK,
            NodeType.EMPHASIS,
            NodeType.STRONG,
            NodeType.TEXT,
        }
        inline_elements = []

        for child in self.children:
            if child.type in inline_types:
                inline_elements.append(child)
            # Recursively get inline elements from children
            inline_elements.extend(child.get_inline_elements())

        return inline_elements

    def has_inline_elements(self) -> bool:
        """Check if this node has any inline elements."""
        return len(self.get_inline_elements()) > 0

    def get_depth(self) -> int:
        """Get the depth of this node in the tree."""
        if not self.children:
            return 0
        return 1 + max(child.get_depth() for child in self.children)

    def count_nodes(self) -> int:
        """Count total number of nodes in this subtree."""
        count = 1  # Count this node
        for child in self.children:
            count += child.count_nodes()
        return count

    def validate_structure(self) -> List[str]:
        """Validate the structure of this node and return any issues."""
        issues = []

        # Check position validity
        if self.start_pos.line < 0 or self.start_pos.column < 0:
            issues.append(f"Invalid start position: {self.start_pos}")

        if self.end_pos.line < self.start_pos.line:
            issues.append("End position before start position")

        if (
            self.end_pos.line == self.start_pos.line
            and self.end_pos.column < self.start_pos.column
        ):
            issues.append("End column before start column")

        # Check children are within bounds
        for i, child in enumerate(self.children):
            if (
                child.start_pos.offset < self.start_pos.offset
                or child.end_pos.offset > self.end_pos.offset
            ):
                issues.append(f"Child {i} ({child.type}) outside parent bounds")

            # Recursively validate children
            child_issues = child.validate_structure()
            issues.extend([f"Child {i}: {issue}" for issue in child_issues])

        return issues


@dataclass
class FencedBlock:
    """Represents a fenced code block extracted from Markdown."""

    content: str
    language: Optional[str]
    fence_type: str  # "```" or "~~~"
    fence_length: int  # Length of the fence (3, 4, 5+ characters)
    start_line: int
    end_line: int
    start_offset: int  # Position in characters from the beginning of the document
    end_offset: int
    nesting_level: int
    is_closed: bool
    raw_content: str  # Content with fences included

    def __post_init__(self):
        """Normalize language to lowercase."""
        if self.language:
            self.language = self.language.lower()

    def get_size(self) -> int:
        """Get the size of the block in characters."""
        return len(self.content)

    def is_valid(self) -> bool:
        """Check if the block is valid."""
        return self.is_closed and self.start_line < self.end_line

    def get_hash(self) -> str:
        """Get a hash of the block content for deduplication."""
        content_hash = hashlib.md5(self.content.encode("utf-8")).hexdigest()
        return f"{self.language or 'unknown'}_{content_hash[:8]}"


class ElementType(Enum):
    """Types of structural elements in Markdown."""

    HEADER = "header"
    LIST = "list"
    TABLE = "table"
    BLOCKQUOTE = "blockquote"


@dataclass
class Header:
    """Represents a header element."""

    level: int  # 1-6
    text: str
    line: int
    offset: int
    anchor: Optional[str] = None

    def get_hierarchy_path(self, all_headers: List["Header"]) -> List[str]:
        """Get the hierarchy path of this header."""
        path = []
        current_level = self.level

        # Find parent headers
        for header in reversed(all_headers[: all_headers.index(self)]):
            if header.level < current_level:
                path.insert(0, header.text)
                current_level = header.level
                if current_level == 1:
                    break

        path.append(self.text)
        return path


@dataclass
class ListItem:
    """Represents a list item."""

    content: str
    level: int  # Nesting level (0-based)
    marker: str  # -, *, +, 1., 2., etc.
    line: int
    offset: int
    is_task: bool = False
    is_checked: Optional[bool] = None
    children: List["ListItem"] = field(default_factory=list)


@dataclass
class MarkdownList:
    """Represents a list structure."""

    type: str  # "ordered", "unordered", "task"
    items: List[ListItem]
    start_line: int
    end_line: int
    max_nesting_level: int

    def get_item_count(self) -> int:
        """Get the total number of items in the list."""
        return len(self.items)

    def get_total_size(self) -> int:
        """Get the total size of the list in characters."""
        return sum(len(item.content) for item in self.items)


@dataclass
class Table:
    """Represents a table structure."""

    headers: List[str]
    rows: List[List[str]]
    start_line: int
    end_line: int
    column_count: int
    alignment: List[str] = field(default_factory=list)  # "left", "center", "right"

    def get_row_count(self) -> int:
        """Get the number of data rows (excluding header)."""
        return len(self.rows)

    def get_total_size(self) -> int:
        """Get the total size of the table in characters."""
        size = sum(len(header) for header in self.headers)
        for row in self.rows:
            size += sum(len(cell) for cell in row)
        return size


@dataclass
class ElementCollection:
    """Collection of all detected structural elements."""

    headers: List[Header] = field(default_factory=list)
    lists: List[MarkdownList] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)

    def get_element_count(self) -> Dict[str, int]:
        """Get count of elements by type."""
        return {
            "headers": len(self.headers),
            "lists": len(self.lists),
            "tables": len(self.tables),
            "list_items": sum(lst.get_item_count() for lst in self.lists),
        }

    def get_total_size(self) -> int:
        """Get the total size of all elements."""
        size = 0
        size += sum(len(h.text) for h in self.headers)
        size += sum(lst.get_total_size() for lst in self.lists)
        size += sum(table.get_total_size() for table in self.tables)
        return size


@dataclass
class PreambleInfo:
    """
    Information about document preamble (content before first header).

    The preamble is the content that appears before the first header in a
    markdown document. It often contains introductory text, metadata, or
    document summaries.

    Attributes:
        content: The actual preamble text
        type: Classification of preamble type:
            - "introduction": Introductory text
            - "summary": Document summary or abstract
            - "metadata": Structured metadata (author, date, etc.)
            - "general": General content that doesn't fit other categories
        line_count: Number of lines in the preamble
        char_count: Number of characters in the preamble
        has_metadata: Whether preamble contains structured metadata
        metadata_fields: Dictionary of extracted metadata fields

    Examples:
        >>> preamble=PreambleInfo(
        ...     content="This is an introduction to the document.",
        ...     type="introduction",
        ...     line_count=1,
        ...     char_count=42,
        ...     has_metadata=False,
        ...     metadata_fields={}
        ... )
        >>> print(preamble.type)
        'introduction'
    """

    content: str
    type: str  # "introduction", "summary", "metadata", "general"
    line_count: int
    char_count: int
    has_metadata: bool
    metadata_fields: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate preamble data."""
        if self.line_count < 0:
            raise ValueError(f"line_count must be non-negative, got {self.line_count}")
        if self.char_count < 0:
            raise ValueError(f"char_count must be non-negative, got {self.char_count}")
        if self.type not in ("introduction", "summary", "metadata", "general"):
            raise ValueError(
                "type must be one of: introduction, summary, metadata, general. "
                f"Got: {self.type}"
            )
        if self.has_metadata and not self.metadata_fields:
            raise ValueError("has_metadata is True but metadata_fields is empty")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "content": self.content,
            "type": self.type,
            "line_count": self.line_count,
            "char_count": self.char_count,
            "has_metadata": self.has_metadata,
            "metadata_fields": self.metadata_fields,
        }


@dataclass
class ContentAnalysis:
    """Synchronized analysis of document content and metrics for Stage 1."""

    # Required basic metrics
    total_chars: int
    total_lines: int
    total_words: int

    # Required content type ratios (always defined, sum to 1.0)
    code_ratio: float
    text_ratio: float

    # Required element counts (always defined)
    code_block_count: int

    # Required content classification (must come before fields with defaults)
    content_type: str  # "code_heavy", "mixed", "text_heavy"

    # P1-005: Change header_count from int to Dict[int, int] for granularity
    header_count: Dict[int, int] = field(default_factory=dict)

    # P1-006: Change languages from Set[str] to Dict[str, int] for occurrence counts
    languages: Dict[str, int] = field(default_factory=dict)

    # Additional element counts with defaults
    list_count: int = 0
    table_count: int = 0
    link_count: int = 0
    image_count: int = 0

    # Additional ratios with defaults
    list_ratio: float = 0.0
    table_ratio: float = 0.0

    # Complexity metrics
    complexity_score: float = 0.0
    max_header_depth: int = 0
    has_mixed_content: bool = False

    # P1-003: Add nested list depth tracking
    nested_list_depth: int = 0

    # P1-007: Add boolean convenience flags
    has_tables: bool = False
    has_nested_lists: bool = False

    # P1-002: Add inline code count
    inline_code_count: int = 0

    # P1-001: Add ContentMetrics fields
    average_line_length: float = 0.0
    max_line_length: int = 0
    empty_lines: int = 0
    indented_lines: int = 0
    punctuation_ratio: float = 0.0
    special_chars: Dict[str, int] = field(default_factory=dict)

    # P1-004: Add unified block elements list
    block_elements: List[Any] = field(default_factory=list)

    # Preamble information (content before first header)
    preamble: Optional[PreambleInfo] = None

    def get_total_header_count(self) -> int:
        """Get total number of headers across all levels."""
        if isinstance(self.header_count, dict):
            return sum(self.header_count.values())
        return self.header_count if isinstance(self.header_count, int) else 0

    def __post_init__(self):
        """Validate and normalize after creation."""
        self._validate_required_fields()
        self._normalize_ratios()
        self._calculate_derived_metrics()

    def _validate_required_fields(self):
        """Validate required fields."""
        if self.total_chars < 0:
            raise ValueError("total_chars must be >= 0")
        if self.total_lines < 0:
            raise ValueError("total_lines must be >= 0")
        if self.total_words < 0:
            raise ValueError("total_words must be >= 0")
        if self.code_block_count < 0:
            raise ValueError("code_block_count must be >= 0")
        # P1-005: header_count is now Dict[int, int], validate values
        if isinstance(self.header_count, dict):
            for level, count in self.header_count.items():
                if count < 0:
                    raise ValueError(f"header_count[{level}] must be >= 0")
        # P1-006: languages is now Dict[str, int], validate values
        if isinstance(self.languages, dict):
            for lang, count in self.languages.items():
                if count < 0:
                    raise ValueError(f"languages[{lang}] must be >= 0")

    def _normalize_ratios(self):
        """Normalize ratios to ensure they sum to 1.0."""
        total_ratio = self.code_ratio + self.text_ratio
        if total_ratio > 1.0:
            # Normalize to sum to 1.0
            self.code_ratio /= total_ratio
            self.text_ratio /= total_ratio
        elif total_ratio < 1.0 and total_ratio > 0:
            # Fill remaining with text ratio
            remaining = 1.0 - total_ratio
            self.text_ratio += remaining

        # Ensure ratios are in valid range
        self.code_ratio = max(0.0, min(1.0, self.code_ratio))
        self.text_ratio = max(0.0, min(1.0, self.text_ratio))
        self.list_ratio = max(0.0, min(1.0, self.list_ratio))
        self.table_ratio = max(0.0, min(1.0, self.table_ratio))

    def _calculate_derived_metrics(self):
        """Calculate derived metrics."""
        # Calculate complexity score
        self.complexity_score = self._calculate_complexity()

        # Determine if content is mixed
        self.has_mixed_content = (
            self.code_block_count > 0
            and self.get_total_header_count() > 0
            and (self.list_count > 0 or self.table_count > 0)
        )

        # P1-007: Calculate boolean flags
        self.has_tables = self.table_count > 0
        self.has_nested_lists = self.nested_list_depth > 1

        # Ensure content type is valid
        if self.content_type not in ["code_heavy", "mixed", "text_heavy"]:
            self.content_type = self._determine_content_type()

    def _calculate_complexity(self) -> float:
        """Calculate content complexity score."""
        complexity = 0.0

        # Factor in different element types
        if self.code_block_count > 0:
            complexity += 0.3
        # P1-005: header_count is now Dict, sum all counts
        total_headers = (
            sum(self.header_count.values())
            if isinstance(self.header_count, dict)
            else self.header_count
        )
        if total_headers > 3:
            complexity += 0.2
        if self.list_count > 0:
            complexity += 0.1
        if self.table_count > 0:
            complexity += 0.2
        # P1-006: languages is now Dict, check number of unique languages
        if len(self.languages) > 1:
            complexity += 0.2

        return min(1.0, complexity)

    def _determine_content_type(self) -> str:
        """Determine content type based on ratios."""
        if self.code_ratio >= 0.7:
            return "code_heavy"
        elif self.code_ratio >= 0.3:
            return "mixed"
        else:
            return "text_heavy"

    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the analysis."""
        return {
            "content_type": self.content_type,
            "complexity_score": self.complexity_score,
            "ratios": {
                "code": self.code_ratio,
                "text": self.text_ratio,
                "list": self.list_ratio,
                "table": self.table_ratio,
            },
            "elements": {
                "code_blocks": self.code_block_count,
                "headers": self.header_count,
                "lists": self.list_count,
                "tables": self.table_count,
                "links": self.link_count,
                "images": self.image_count,
            },
            "metrics": {
                "total_chars": self.total_chars,
                "total_lines": self.total_lines,
                "total_words": self.total_words,
                "max_header_depth": self.max_header_depth,
                "has_mixed_content": self.has_mixed_content,
                "complexity_score": self.complexity_score,
            },
            "languages": list(self.languages),
            "preamble": self.preamble.to_dict() if self.preamble else None,
        }

    def recommend_strategy(self) -> str:
        """Recommend a chunking strategy based on the analysis."""
        if self.code_ratio >= 0.7 and self.code_block_count >= 3:
            return "code"
        elif self.has_mixed_content and self.complexity_score >= 0.3:
            return "mixed"
        elif self.list_count >= 5 or self.list_ratio > 0.6:
            return "list"
        elif self.table_count >= 3 or self.table_ratio > 0.4:
            return "table"
        elif self.get_total_header_count() >= 3 and self.max_header_depth > 1:
            return "structural"
        else:
            return "sentences"

    def get_element_counts(self) -> Dict[str, int]:
        """Get all element counts as a dictionary."""
        return {
            "code_blocks": self.code_block_count,
            "headers": self.header_count,
            "lists": self.list_count,
            "tables": self.table_count,
            "links": self.link_count,
            "images": self.image_count,
        }

    def validate_consistency(self) -> List[str]:
        """Validate internal consistency and return any issues."""
        issues = []

        # Check ratio consistency
        total_ratio = self.code_ratio + self.text_ratio
        if abs(total_ratio - 1.0) > 0.1:
            issues.append(f"Ratios don't sum to 1.0: {total_ratio}")

        # Check element count consistency
        if self.code_block_count == 0 and self.code_ratio > 0.5:
            issues.append("High code ratio but no code blocks")

        if self.get_total_header_count() == 0 and self.max_header_depth > 0:
            issues.append("Header depth > 0 but no headers")

        # Additional consistency checks
        if self.list_count == 0 and self.list_ratio > 0.3:
            issues.append("High list ratio but no lists")

        if self.table_count == 0 and self.table_ratio > 0.3:
            issues.append("High table ratio but no tables")

        # Check content type consistency
        if self.content_type == "code_heavy" and self.code_ratio < 0.5:
            issues.append("Content type 'code_heavy' but low code ratio")

        if self.content_type == "text_heavy" and self.code_ratio > 0.5:
            issues.append("Content type 'text_heavy' but high code ratio")

        return issues

    def validate_structure_integrity(self) -> List[str]:
        """Validate structural integrity of the analysis data."""
        issues = []

        self._validate_basic_counts(issues)
        self._validate_element_counts(issues)
        self._validate_ratios(issues)
        self._validate_content_type(issues)
        self._validate_complexity_score(issues)

        return issues

    def _validate_basic_counts(self, issues: List[str]) -> None:
        """Validate basic count fields."""
        if self.total_chars < 0:
            issues.append("Negative total_chars")
        if self.total_lines < 0:
            issues.append("Negative total_lines")
        if self.total_words < 0:
            issues.append("Negative total_words")

    def _validate_element_counts(self, issues: List[str]) -> None:
        """Validate element count fields."""
        if self.code_block_count < 0:
            issues.append("Negative code_block_count")
        # P1-005: header_count is now Dict, check all values
        if isinstance(self.header_count, dict):
            for level, count in self.header_count.items():
                if count < 0:
                    issues.append(f"Negative header_count[{level}]")
        elif isinstance(self.header_count, int) and self.header_count < 0:
            issues.append("Negative header_count")
        if self.list_count < 0:
            issues.append("Negative list_count")
        if self.table_count < 0:
            issues.append("Negative table_count")

    def _validate_ratios(self, issues: List[str]) -> None:
        """Validate ratio fields are within bounds."""
        if not (0.0 <= self.code_ratio <= 1.0):
            issues.append(f"Code ratio out of bounds: {self.code_ratio}")
        if not (0.0 <= self.text_ratio <= 1.0):
            issues.append(f"Text ratio out of bounds: {self.text_ratio}")
        if not (0.0 <= self.list_ratio <= 1.0):
            issues.append(f"List ratio out of bounds: {self.list_ratio}")
        if not (0.0 <= self.table_ratio <= 1.0):
            issues.append(f"Table ratio out of bounds: {self.table_ratio}")

    def _validate_content_type(self, issues: List[str]) -> None:
        """Validate content type field."""
        valid_types = ["code_heavy", "mixed", "text_heavy"]
        if self.content_type not in valid_types:
            issues.append(f"Invalid content_type: {self.content_type}")

    def _validate_complexity_score(self, issues: List[str]) -> None:
        """Validate complexity score field."""
        if not (0.0 <= self.complexity_score <= 1.0):
            issues.append(f"Complexity score out of bounds: {self.complexity_score}")

    def validate_cross_component_consistency(
        self, other_components: Dict[str, Any]
    ) -> List[str]:
        """Validate consistency with other Stage 1 components."""
        issues = []

        self._validate_ast_consistency(other_components, issues)
        self._validate_fenced_blocks_consistency(other_components, issues)
        self._validate_elements_consistency(other_components, issues)

        return issues

    def _validate_ast_consistency(
        self, other_components: Dict[str, Any], issues: List[str]
    ) -> None:
        """Validate consistency with AST component."""
        if "ast" in other_components:
            ast = other_components["ast"]
            if hasattr(ast, "count_nodes"):
                ast_node_count = ast.count_nodes()
                # Basic sanity check - should have some relationship
                if ast_node_count == 0 and (
                    self.get_total_header_count() > 0 or self.code_block_count > 0
                ):
                    issues.append("Empty AST but analysis shows content")

    def _validate_fenced_blocks_consistency(
        self, other_components: Dict[str, Any], issues: List[str]
    ) -> None:
        """Validate consistency with fenced blocks component."""
        if "fenced_blocks" in other_components:
            blocks = other_components["fenced_blocks"]
            actual_block_count = len(blocks) if blocks else 0
            if actual_block_count != self.code_block_count:
                issues.append(
                    f"Code block count mismatch: analysis={self.code_block_count}, "
                    f"actual={actual_block_count}"
                )

    def _validate_elements_consistency(
        self, other_components: Dict[str, Any], issues: List[str]
    ) -> None:
        """Validate consistency with elements component."""
        if "elements" in other_components:
            elements = other_components["elements"]
            if hasattr(elements, "get_element_count"):
                element_counts = elements.get_element_count()

                # Check header count consistency
                # P1-005: header_count is now Dict[int, int], compare total
                if "headers" in element_counts:
                    if element_counts["headers"] != self.get_total_header_count():
                        total = self.get_total_header_count()
                        issues.append(
                            f"Header count mismatch: analysis={total}, "
                            f"elements={element_counts['headers']}"
                        )

                # Check list count consistency
                if "lists" in element_counts:
                    if element_counts["lists"] != self.list_count:
                        issues.append(
                            f"List count mismatch: analysis={self.list_count}, "
                            f"elements={element_counts['lists']}"
                        )

    def validate_serialization_compatibility(self) -> List[str]:
        """Validate that the analysis can be properly serialized/deserialized."""
        issues = []

        try:
            # Test basic serialization compatibility
            import json

            # Create a serializable version
            serializable_data = {
                "total_chars": self.total_chars,
                "total_lines": self.total_lines,
                "total_words": self.total_words,
                "code_ratio": self.code_ratio,
                "text_ratio": self.text_ratio,
                "code_block_count": self.code_block_count,
                "header_count": self.header_count,
                "content_type": self.content_type,
                # P1-006: Now Dict[str, int], already serializable
                "languages": self.languages,
                "list_count": self.list_count,
                "table_count": self.table_count,
                "complexity_score": self.complexity_score,
            }

            # Test JSON serialization
            json_str = json.dumps(serializable_data)
            json.loads(json_str)  # Test deserialization

        except (TypeError, ValueError) as e:
            issues.append(f"Serialization failed: {e}")
        except Exception as e:
            issues.append(f"Unexpected serialization error: {e}")

        # Check for non-serializable types
        if not isinstance(self.languages, (set, list, tuple)):
            issues.append("Languages field is not a serializable collection")

        return issues

    def full_validation(
        self, other_components: Dict[str, Any] = None
    ) -> Dict[str, List[str]]:
        """Perform full validation and return categorized issues."""
        validation_results = {
            "consistency": self.validate_consistency(),
            "structure": self.validate_structure_integrity(),
            "serialization": self.validate_serialization_compatibility(),
        }

        if other_components:
            validation_results["cross_component"] = (
                self.validate_cross_component_consistency(other_components)
            )

        return validation_results

    def is_valid(self, other_components: Dict[str, Any] = None) -> bool:
        """Check if the analysis passes all validation checks."""
        validation_results = self.full_validation(other_components)

        # Check if any validation category has issues
        for category, issues in validation_results.items():
            if issues:
                return False

        return True


@dataclass
class Stage1Results:
    """Results of Stage 1 processing with validation support."""

    ast: MarkdownNode
    fenced_blocks: List[FencedBlock]
    elements: ElementCollection
    analysis: ContentAnalysis
    parser_name: str
    processing_time: float  # in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)  # For validation info

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the results."""
        return {
            "ast_nodes": self._count_ast_nodes(self.ast),
            "fenced_blocks": len(self.fenced_blocks),
            "elements": self.elements.get_element_count(),
            "analysis": self.analysis.get_summary(),
            "parser_used": self.parser_name,
            "processing_time": self.processing_time,
            "validation_status": self.metadata.get("validation_errors") is None,
        }

    def _count_ast_nodes(self, node: MarkdownNode) -> int:
        """Count nodes in the AST."""
        count = 1
        for child in node.children:
            count += self._count_ast_nodes(child)
        return count

    def has_validation_errors(self) -> bool:
        """Check if there are validation errors."""
        return (
            "validation_errors" in self.metadata and self.metadata["validation_errors"]
        )

    def get_validation_errors(self) -> List[str]:
        """Get validation errors if any."""
        return self.metadata.get("validation_errors", [])

    def get_validation_warnings(self) -> List[str]:
        """Get validation warnings if any."""
        return self.metadata.get("validation_warnings", [])
