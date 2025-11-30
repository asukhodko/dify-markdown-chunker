"""
MixedStrategy - Strategy for documents with mixed content types.

This strategy handles complex documents with multiple element types (code, lists,
tables, text) in significant proportions, preserving semantic relationships.

Algorithm Documentation:
    - Mixed Strategy: docs/markdown-extractor/03-strategies/mixed-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from markdown_chunker.parser.types import (
    ContentAnalysis,
    MarkdownList,
    Stage1Results,
    Table,
)

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy

# Set up logger for this module
logger = logging.getLogger(__name__)


@dataclass
class ContentElement:
    """Represents a content element with type and position."""

    element_type: str  # "header", "code", "list", "table", "text"
    content: str
    start_line: int
    end_line: int
    is_indivisible: bool = False
    metadata: Optional[Dict[Any, Any]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LogicalSection:
    """A logical section grouping related elements."""

    header: Optional[ContentElement]
    elements: List[ContentElement]
    start_line: int
    end_line: int

    def calculate_size(self) -> int:
        """Calculate total size of section."""
        size = 0
        if self.header:
            size += len(self.header.content)
        for element in self.elements:
            size += len(element.content)
        return size

    def get_element_types(self) -> Set[str]:
        """Get set of element types in section."""
        types = set()
        if self.header:
            types.add(self.header.element_type)
        for element in self.elements:
            types.add(element.element_type)
        return types


class MixedStrategy(BaseStrategy):
    """
    Strategy for mixed content documents.

    This strategy:
    - Handles documents with multiple content types
    - Groups related elements logically
    - Preserves semantic relationships
    - Splits around indivisible elements (code, tables)
    - Balances chunk sizes adaptively

    Priority: 2 (high)
    """

    @property
    def name(self) -> str:
        """Strategy name."""
        return "mixed"

    @property
    def priority(self) -> int:
        """High priority."""
        return 2

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if strategy can handle the content.

        Suitable for documents with:
        - Mixed content (multiple element types in significant proportions)
        - Sufficient complexity
        - No single dominant type
        """
        # Check for mixed content
        has_mixed = (
            0.1 < analysis.code_ratio < 0.7
            and (analysis.list_ratio > 0.1 or analysis.table_ratio > 0.1)
            and analysis.text_ratio > 0.2
        )

        # Check complexity
        complexity = getattr(analysis, "complexity_score", 0.5)

        return has_mixed and complexity >= config.min_complexity

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for mixed strategy.

        Higher quality for:
        - Truly mixed content (no dominant type)
        - Multiple element types
        - Balanced proportions
        """
        score = 0.0

        # Anti-pattern: one type dominates
        if (
            analysis.code_ratio > 0.7
            or analysis.list_ratio > 0.7
            or analysis.table_ratio > 0.6
        ):
            return 0.2  # Low score for specialized documents

        # Bonus for truly mixed content
        has_mixed = (
            0.1 < analysis.code_ratio < 0.7
            and (analysis.list_ratio > 0.1 or analysis.table_ratio > 0.1)
            and analysis.text_ratio > 0.2
        )

        if has_mixed:
            score += 0.7

        # Bonus for balanced code
        if 0.3 <= analysis.code_ratio <= 0.7:
            score += 0.3
        elif 0.1 < analysis.code_ratio < 0.3:
            score += 0.2

        # Bonus for element diversity
        element_count = sum(
            [
                analysis.code_ratio > 0.1,
                analysis.list_ratio > 0.1,
                analysis.table_ratio > 0.1,
                analysis.text_ratio > 0.3,
            ]
        )

        if element_count >= 3:
            score += 0.2
        elif element_count >= 2:
            score += 0.1

        return min(score, 1.0)

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply mixed strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by mixed-content splitting
        """
        if not content.strip():
            return []

        # Detect all elements
        elements = self._detect_all_elements(content, stage1_results)

        if not elements:
            return []

        # Group into logical sections
        sections = self._group_into_logical_sections(elements)

        # Process sections into chunks
        chunks = self._process_sections(sections, config)

        return self._validate_chunks(chunks, config)

    def _detect_all_elements(  # noqa: C901
        self, content: str, stage1_results: Stage1Results
    ) -> List[ContentElement]:
        """
        Detect all content elements.

        Complexity justified: This method coordinates detection of multiple
        element types (headers, code blocks, lists, tables) with proper
        ordering and overlap handling.

        Args:
            content: Content to analyze
            stage1_results: Stage 1 results

        Returns:
            List of content elements sorted by position
        """
        elements = []
        lines = content.split("\n")

        # Detect headers
        for i, line in enumerate(lines, 1):
            if re.match(r"^#{1,6}\s+", line):
                elements.append(
                    ContentElement(
                        element_type="header",
                        content=line,
                        start_line=i,
                        end_line=i,
                        is_indivisible=False,
                    )
                )

        # Detect code blocks from Stage 1
        if hasattr(stage1_results, "fenced_blocks") and stage1_results.fenced_blocks:
            for block in stage1_results.fenced_blocks:
                elements.append(
                    ContentElement(
                        element_type="code",
                        content=getattr(
                            block, "raw_content", getattr(block, "content", str(block))
                        ),
                        start_line=block.start_line,
                        end_line=block.end_line,
                        is_indivisible=True,
                        metadata={
                            "language": block.language,
                            "fence_type": block.fence_type,
                        },
                    )
                )

        # CRITICAL FIX: Add lists from Stage 1 (if available)
        if (
            hasattr(stage1_results, "elements")
            and stage1_results.elements
            and stage1_results.elements.lists
        ):
            try:
                for markdown_list in stage1_results.elements.lists:
                    try:
                        # Reconstruct content from items
                        list_content = self._reconstruct_list_content(markdown_list)

                        elements.append(
                            ContentElement(
                                element_type="list",
                                content=list_content,
                                start_line=markdown_list.start_line,
                                end_line=markdown_list.end_line,
                                is_indivisible=True,  # Don't split lists
                                metadata={
                                    "list_type": markdown_list.type,  # FIXED: .type instead of .list_type  # noqa: E501
                                    "item_count": markdown_list.get_item_count(),
                                    "max_nesting": markdown_list.max_nesting_level,
                                    "source": "stage1_analysis",
                                },
                            )
                        )
                    except AttributeError as e:
                        logger.warning(
                            f"AttributeError accessing MarkdownList fields: {e}. "
                            f"Object type: {type(markdown_list)}. "
                            f"Falling back to regex."
                        )
                        # Continue processing other lists, fallback will handle missing ones  # noqa: E501
                        continue
            except Exception as e:
                logger.error(
                    f"Error processing Stage 1 lists: {e}. "
                    f"Falling back to regex detection."
                )
                # Clear any partial results and use fallback
                elements = [e for e in elements if e.element_type != "list"]
                elements.extend(self._detect_lists_regex(lines))
        else:
            # Fallback to regex detection if Stage 1 data unavailable
            logger.debug("Stage 1 list data unavailable, using regex fallback")
            elements.extend(self._detect_lists_regex(lines))

        # CRITICAL FIX: Add tables from Stage 1 (if available)
        if (
            hasattr(stage1_results, "elements")
            and stage1_results.elements
            and stage1_results.elements.tables
        ):
            try:
                for table in stage1_results.elements.tables:
                    try:
                        # Reconstruct table content
                        table_content = self._reconstruct_table_content(table)

                        elements.append(
                            ContentElement(
                                element_type="table",
                                content=table_content,
                                start_line=table.start_line,
                                end_line=table.end_line,
                                is_indivisible=True,  # Don't split tables
                                metadata={
                                    "columns": table.column_count,
                                    "rows": table.get_row_count(),  # FIXED: method instead of field  # noqa: E501
                                    "has_header": bool(
                                        table.headers
                                    ),  # FIXED: check headers list
                                    "alignment": table.alignment,
                                    "source": "stage1_analysis",
                                },
                            )
                        )
                    except AttributeError as e:
                        logger.warning(
                            f"AttributeError accessing Table fields: {e}. "
                            f"Object type: {type(table)}. Falling back to regex."
                        )
                        # Continue processing other tables, fallback will handle missing ones  # noqa: E501
                        continue
            except Exception as e:
                logger.error(
                    f"Error processing Stage 1 tables: {e}. "
                    f"Falling back to regex detection."
                )
                # Clear any partial results and use fallback
                elements = [e for e in elements if e.element_type != "table"]
                elements.extend(self._detect_tables_regex(lines))
        else:
            # Fallback to regex detection if Stage 1 data unavailable
            logger.debug("Stage 1 table data unavailable, using regex fallback")
            elements.extend(self._detect_tables_regex(lines))

        # Sort by position
        elements.sort(key=lambda e: e.start_line)

        # Insert text paragraphs between elements
        elements = self._insert_text_paragraphs(content, elements)

        return elements

    def _reconstruct_list_content(self, markdown_list: MarkdownList) -> str:
        """Reconstruct list content from Stage 1 MarkdownList."""
        lines = []
        for item in markdown_list.items:
            indent = "  " * item.level

            if item.is_task:
                # For task lists, use - marker and add checkbox
                checkbox = "[x]" if item.is_checked else "[ ]"
                lines.append(f"{indent}- {checkbox} {item.content}")
            else:
                # For regular lists, use the original marker
                lines.append(f"{indent}{item.marker} {item.content}")

        return "\n".join(lines)

    def _reconstruct_table_content(self, table: Table) -> str:
        """Reconstruct table content from Stage 1 Table."""
        lines = []

        # Header row
        header_row = "| " + " | ".join(table.headers) + " |"
        lines.append(header_row)

        # Separator row
        separators = []
        for align in table.alignment:
            if align == "center":
                separators.append(":---:")
            elif align == "right":
                separators.append("---:")
            else:
                separators.append("---")
        sep_row = "| " + " | ".join(separators) + " |"
        lines.append(sep_row)

        # Data rows
        for row in table.rows:
            data_row = "| " + " | ".join(row) + " |"
            lines.append(data_row)

        return "\n".join(lines)

    def _insert_text_paragraphs(
        self, content: str, elements: List[ContentElement]
    ) -> List[ContentElement]:
        """
        Insert text paragraph elements between other elements.

        Args:
            content: Original content
            elements: Existing elements

        Returns:
            Elements with text paragraphs inserted
        """
        if not elements:
            # All content is text
            return [
                ContentElement(
                    element_type="text",
                    content=content,
                    start_line=1,
                    end_line=len(content.split("\n")),
                    is_indivisible=False,
                )
            ]

        result = []
        lines = content.split("\n")
        current_line = 1

        for element in elements:
            # Add text before this element
            if element.start_line > current_line:
                text_content = "\n".join(
                    lines[current_line - 1 : element.start_line - 1]
                ).strip()
                if text_content:
                    result.append(
                        ContentElement(
                            element_type="text",
                            content=text_content,
                            start_line=current_line,
                            end_line=element.start_line - 1,
                            is_indivisible=False,
                        )
                    )

            result.append(element)
            current_line = element.end_line + 1

        # Add text after last element
        if current_line <= len(lines):
            text_content = "\n".join(lines[current_line - 1 :]).strip()
            if text_content:
                result.append(
                    ContentElement(
                        element_type="text",
                        content=text_content,
                        start_line=current_line,
                        end_line=len(lines),
                        is_indivisible=False,
                    )
                )

        return result

    def _group_into_logical_sections(
        self, elements: List[ContentElement]
    ) -> List[LogicalSection]:
        """
        Group elements into logical sections.

        Args:
            elements: List of content elements

        Returns:
            List of logical sections
        """
        sections = []
        current_section = None

        for element in elements:
            if element.element_type == "header":
                # Header starts new section
                if current_section:
                    sections.append(current_section)

                current_section = LogicalSection(
                    header=element,
                    elements=[],
                    start_line=element.start_line,
                    end_line=element.end_line,
                )
            else:
                # Add to current section
                if not current_section:
                    # Create section without header
                    current_section = LogicalSection(
                        header=None,
                        elements=[],
                        start_line=element.start_line,
                        end_line=element.end_line,
                    )

                current_section.elements.append(element)
                current_section.end_line = element.end_line

        if current_section:
            sections.append(current_section)

        return sections

    def _process_sections(
        self, sections: List[LogicalSection], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Process sections into chunks.

        Args:
            sections: Logical sections
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []

        for section in sections:
            section_size = section.calculate_size()

            if section_size <= config.max_chunk_size:
                # Section fits in one chunk
                chunk = self._create_section_chunk(section, config)
                chunks.append(chunk)
            else:
                # Section too large - split
                if self._has_indivisible_elements(section):
                    # Split around indivisible elements
                    parts = self._split_around_indivisible(section, config)
                    for part in parts:
                        chunk = self._create_part_chunk(part, config)
                        chunks.append(chunk)
                else:
                    # Regular text splitting
                    parts = self._split_by_size(section, config)
                    for part in parts:
                        chunk = self._create_part_chunk(part, config)
                        chunks.append(chunk)

        return chunks

    def _has_indivisible_elements(self, section: LogicalSection) -> bool:
        """Check if section has indivisible elements."""
        return any(e.is_indivisible for e in section.elements)

    def _split_around_indivisible(
        self, section: LogicalSection, config: ChunkConfig
    ) -> List[List[ContentElement]]:
        """
        Split section around indivisible elements.

        Args:
            section: Section to split
            config: Chunking configuration

        Returns:
            List of element groups
        """
        parts = []
        current_part = []
        current_size = 0

        # Include header in first part if exists
        if section.header:
            current_part.append(section.header)
            current_size = len(section.header.content)

        for element in section.elements:
            if element.is_indivisible:
                # Save current part
                if current_part:
                    parts.append(current_part)
                    current_part = []
                    current_size = 0

                # Indivisible element as separate part
                parts.append([element])
            else:
                # Add to current part
                if current_size + len(element.content) <= config.max_chunk_size:
                    current_part.append(element)
                    current_size += len(element.content)
                else:
                    # Current part full
                    if current_part:
                        parts.append(current_part)
                    current_part = [element]
                    current_size = len(element.content)

        if current_part:
            parts.append(current_part)

        return parts

    def _split_by_size(
        self, section: LogicalSection, config: ChunkConfig
    ) -> List[List[ContentElement]]:
        """
        Split section by size.

        Args:
            section: Section to split
            config: Chunking configuration

        Returns:
            List of element groups
        """
        parts = []
        current_part = []
        current_size = 0

        # Include header in first part
        if section.header:
            current_part.append(section.header)
            current_size = len(section.header.content)

        for element in section.elements:
            if current_size + len(element.content) <= config.max_chunk_size:
                current_part.append(element)
                current_size += len(element.content)
            else:
                if current_part:
                    parts.append(current_part)
                current_part = [element]
                current_size = len(element.content)

        if current_part:
            parts.append(current_part)

        return parts

    def _create_section_chunk(
        self, section: LogicalSection, config: ChunkConfig
    ) -> Chunk:
        """Create chunk from complete section."""
        content_parts = []
        if section.header:
            content_parts.append(section.header.content)
        for element in section.elements:
            content_parts.append(element.content)

        content = "\n\n".join(content_parts)
        element_types = section.get_element_types()

        metadata = {
            "element_types": ",".join(sorted(element_types)),
            "element_count": len(section.elements) + (1 if section.header else 0),
            "has_code": "code" in element_types,
            "has_list": "list" in element_types,
            "has_table": "table" in element_types,
        }

        return self._create_chunk(
            content=content,
            start_line=section.start_line,
            end_line=section.end_line,
            content_type="mixed",
            **metadata,
        )

    def _create_part_chunk(
        self, elements: List[ContentElement], config: ChunkConfig
    ) -> Chunk:
        """Create chunk from element group."""
        if not elements:
            return None

        content = "\n\n".join(e.content for e in elements)
        element_types = set(e.element_type for e in elements)

        metadata = {
            "element_types": ",".join(sorted(element_types)),
            "element_count": len(elements),
            "has_code": "code" in element_types,
            "has_list": "list" in element_types,
            "has_table": "table" in element_types,
        }

        # Check for oversize
        if len(content) > config.max_chunk_size:
            metadata["allow_oversize"] = True
            metadata["oversize_reason"] = "indivisible_element"

        return self._create_chunk(
            content=content,
            start_line=elements[0].start_line,
            end_line=elements[-1].end_line,
            content_type="mixed",
            **metadata,
        )

    def _detect_lists_regex(self, lines: List[str]) -> List[ContentElement]:
        """Fallback regex-based list detection."""
        elements = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detect list items (unordered: -, *, +; ordered: 1., 2., etc.)
            if re.match(r"^\s*[-*+]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
                # Found start of list
                start_line = i + 1
                list_lines = [line]
                i += 1

                # Collect consecutive list items
                while i < len(lines):
                    next_line = lines[i]
                    if (
                        re.match(r"^\s*[-*+]\s+", next_line)
                        or re.match(r"^\s*\d+\.\s+", next_line)
                        or (next_line.strip() and next_line.startswith("  "))
                    ):  # Continuation
                        list_lines.append(next_line)
                        i += 1
                    elif not next_line.strip():  # Empty line
                        list_lines.append(next_line)
                        i += 1
                    else:
                        break

                if list_lines:
                    content = "\n".join(list_lines)
                    list_type = (
                        "ordered"
                        if re.match(r"^\s*\d+\.", list_lines[0])
                        else "unordered"
                    )
                    item_count = sum(
                        1
                        for line in list_lines
                        if re.match(r"^\s*[-*+]\s+", line)
                        or re.match(r"^\s*\d+\.\s+", line)
                    )

                    elements.append(
                        ContentElement(
                            element_type="list",
                            content=content,
                            start_line=start_line,
                            end_line=start_line + len(list_lines) - 1,
                            is_indivisible=True,
                            metadata={
                                "list_type": list_type,
                                "item_count": item_count,
                                "source": "regex_fallback",
                            },
                        )
                    )
            else:
                i += 1

        return elements

    def _detect_tables_regex(self, lines: List[str]) -> List[ContentElement]:
        """Fallback regex-based table detection."""
        elements = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Detect table rows (contains |)
            if (
                "|" in line
                and line.strip().startswith("|")
                and line.strip().endswith("|")
            ):
                # Found potential table start
                start_line = i + 1
                table_lines = [line]
                i += 1

                # Collect consecutive table rows
                while i < len(lines):
                    next_line = lines[i]
                    if "|" in next_line and (
                        next_line.strip().startswith("|")
                        or re.match(r"^\s*\|?[-:|\s]+\|?\s*$", next_line)
                    ):  # Header separator or row
                        table_lines.append(next_line)
                        i += 1
                    elif not next_line.strip():  # Empty line
                        i += 1
                        break
                    else:
                        break

                if len(table_lines) >= 2:  # At least header + separator or 2 rows
                    content = "\n".join(table_lines)
                    # Count columns from first row
                    columns = len(
                        [cell for cell in table_lines[0].split("|") if cell.strip()]
                    )
                    has_header = len(table_lines) > 1 and bool(
                        re.match(r"^\s*\|?[-:|\s]+\|?\s*$", table_lines[1])
                    )

                    elements.append(
                        ContentElement(
                            element_type="table",
                            content=content,
                            start_line=start_line,
                            end_line=start_line + len(table_lines) - 1,
                            is_indivisible=True,
                            metadata={
                                "columns": columns,
                                "rows": len(table_lines) - (1 if has_header else 0),
                                "has_header": has_header,
                                "source": "regex_fallback",
                            },
                        )
                    )
            else:
                i += 1

        return elements

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            return (
                f"Mixed content (code={analysis.code_ratio:.1%}, "
                f"lists={analysis.list_ratio:.1%}, "
                f"text={analysis.text_ratio:.1%}) - suitable for mixed strategy"
            )
        else:
            if analysis.code_ratio >= 0.7:
                return (
                    f"Code dominates ({analysis.code_ratio:.1%}) - "
                    f"not suitable for mixed strategy"
                )
            elif analysis.text_ratio < 0.2:
                return (
                    f"Insufficient text ({analysis.text_ratio:.1%}) - "
                    f"not suitable for mixed strategy"
                )
            else:
                return "Content not sufficiently mixed for mixed strategy"
