"""
ListStrategy - Strategy for list-heavy documents.

This strategy preserves list hierarchy and handles nested structures,
ensuring parent-child relationships remain intact.

Algorithm Documentation:
    - List Strategy: docs/markdown-extractor/03-strategies/list-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import logging
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from markdown_chunker.parser.types import ContentAnalysis, ListItem, Stage1Results

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy

# Set up logger for this module
logger = logging.getLogger(__name__)


@dataclass
class ListItemInfo:
    """Information about a list item with hierarchy."""

    content: str
    level: int
    list_type: str  # "ordered", "unordered", "task"
    marker: str
    number: Optional[int] = None
    is_checked: Optional[bool] = None
    start_line: int = 1
    end_line: int = 1
    children: Optional[List["ListItemInfo"]] = None
    parent: Optional["ListItemInfo"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


@dataclass
class ListGroup:
    """A group of list items that fit within size constraints."""

    items: List[ListItemInfo]
    size: int
    start_line: int
    end_line: int
    is_continuation: bool = False
    parent_context: str = ""


class ListStrategy(BaseStrategy):
    """
    Strategy for list-heavy documents (≥5 lists or ≥60% list content).

    This strategy:
    - Preserves list hierarchy and nesting
    - Groups related list items together
    - Duplicates parent items when splitting large lists
    - Maintains numbering for ordered lists
    - Handles mixed list types (ordered, unordered, task lists)

    Priority: 3 (medium-high)
    """

    # List detection patterns
    LIST_PATTERNS = {
        "ordered": r"^(\s*)(\d+)\.\s+(.+)$",
        "unordered": r"^(\s*)([-*+])\s+(.+)$",
        "task": r"^(\s*)([-*+])\s+\[([ xX])\]\s+(.+)$",
    }

    @property
    def name(self) -> str:
        """Strategy name."""
        return "list"

    @property
    def priority(self) -> int:
        """Medium-high priority."""
        return 3

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if strategy can handle the content.

        Suitable for documents with:
        - High list count (≥5 lists by default)
        - High list ratio (≥60% by default)
        """
        return (
            analysis.list_count >= config.list_count_threshold
            or analysis.list_ratio >= config.list_ratio_threshold
        )

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for list strategy.

        Higher quality for:
        - More lists
        - Higher list ratio
        - Nested list structures
        """
        score = 0.0

        # List count contribution
        if analysis.list_count >= 10:
            score += 0.8
        elif analysis.list_count >= 5:
            score += 0.6
        elif analysis.list_count >= 3:
            score += 0.4

        # List ratio contribution
        if analysis.list_ratio >= 0.7:
            score += 0.3
        elif analysis.list_ratio >= 0.5:
            score += 0.2
        elif analysis.list_ratio >= 0.3:
            score += 0.1

        # Nested lists bonus
        if hasattr(analysis, "has_nested_lists") and analysis.has_nested_lists:
            score += 0.2

        return min(score, 1.0)

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply list strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by list-aware splitting
        """
        if not content.strip():
            return []

        # Extract list information from Stage 1 or parse manually
        list_items = self._extract_list_items(content, stage1_results)

        if not list_items:
            # No lists found - cannot use list strategy
            return []

        # Build list hierarchy
        list_hierarchy = self._build_list_hierarchy(list_items)

        # Group lists into chunks
        chunks = self._create_chunks_from_lists(list_hierarchy, content, config)

        # FIX: Sort chunks by document position (Requirements 2.1, 9.3)
        if chunks:
            chunks = sorted(chunks, key=lambda c: (c.start_line, c.end_line))

        return self._validate_chunks(chunks, config)

    def _extract_list_items(
        self, content: str, stage1_results: Stage1Results
    ) -> List[ListItemInfo]:
        """
        Extract list items from content.

        Args:
            content: Original content
            stage1_results: Stage 1 results (may contain list info)

        Returns:
            List of ListItemInfo objects
        """
        # Try to use Stage 1 results first
        # FIXED: correct path to data
        if hasattr(stage1_results, "elements") and stage1_results.elements.lists:
            try:
                # Collect all items from all lists
                all_items = []
                for markdown_list in stage1_results.elements.lists:
                    try:
                        all_items.extend(markdown_list.items)
                    except AttributeError as e:
                        logger.warning(
                            f"AttributeError accessing MarkdownList.items: {e}. "
                            f"Object type: {type(markdown_list)}. Skipping this list."
                        )
                        continue

                if all_items:
                    return self._convert_stage1_lists(all_items)
                else:
                    logger.debug(
                        "No valid Stage 1 list items found, "
                        "falling back to manual parsing"
                    )

            except Exception as e:
                logger.error(
                    f"Error processing Stage 1 list data: {e}. "
                    f"Falling back to manual parsing."
                )
        else:
            logger.debug("Stage 1 list data unavailable, using manual parsing")

        # Fallback to manual parsing
        return self._parse_lists_manually(content)

    def _convert_stage1_lists(self, stage1_items: List[ListItem]) -> List[ListItemInfo]:
        """
        Convert Stage 1 list items to ListItemInfo.

        Args:
            stage1_items: List items from Stage 1

        Returns:
            List of ListItemInfo objects
        """
        list_items = []

        for item in stage1_items:
            try:
                list_type = self._determine_list_type(item.marker, item.content)

                # Extract number for ordered lists
                number = None
                if list_type == "ordered":
                    match = re.match(r"^(\d+)\.", item.marker)
                    if match:
                        number = int(match.group(1))

                # Ensure line numbers are >= 1 (Stage 1 may return 0-based)
                line_num = max(1, item.line + 1) if item.line == 0 else item.line

                list_item = ListItemInfo(
                    content=item.content,
                    level=item.level,
                    list_type=list_type,
                    marker=item.marker,
                    number=number,
                    is_checked=item.is_checked,
                    start_line=line_num,  # FIXED: .line instead of .start_line, ensure >= 1  # noqa: E501
                    end_line=line_num,  # FIXED: ListItem is single line
                )

                list_items.append(list_item)

            except AttributeError as e:
                logger.warning(
                    f"AttributeError accessing ListItem fields: {e}. "
                    f"Object type: {type(item)}. Skipping this item."
                )
                continue
            except Exception as e:
                logger.error(f"Error converting ListItem: {e}. Skipping this item.")
                continue

        return list_items

    def _parse_lists_manually(self, content: str) -> List[ListItemInfo]:
        """
        Parse list items manually from content.

        Args:
            content: Content to parse

        Returns:
            List of ListItemInfo objects
        """
        list_items = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            list_item = self._parse_list_line(line, line_num)
            if list_item:
                list_items.append(list_item)

        return list_items

    def _parse_list_line(self, line: str, line_num: int) -> Optional[ListItemInfo]:
        """
        Parse a single line for list item.

        Args:
            line: Line to parse
            line_num: Line number

        Returns:
            ListItemInfo if line is a list item, None otherwise
        """
        # Try task list first (most specific)
        task_match = re.match(self.LIST_PATTERNS["task"], line)
        if task_match:
            indent, marker, check, content = task_match.groups()
            level = len(indent) // 2 + 1  # Assume 2 spaces per level
            is_checked = check.lower() == "x"

            return ListItemInfo(
                content=content,
                level=level,
                list_type="task",
                marker=marker,
                is_checked=is_checked,
                start_line=line_num,
                end_line=line_num,
            )

        # Try ordered list
        ordered_match = re.match(self.LIST_PATTERNS["ordered"], line)
        if ordered_match:
            indent, number, content = ordered_match.groups()
            level = len(indent) // 2 + 1

            return ListItemInfo(
                content=content,
                level=level,
                list_type="ordered",
                marker=f"{number}.",
                number=int(number),
                start_line=line_num,
                end_line=line_num,
            )

        # Try unordered list
        unordered_match = re.match(self.LIST_PATTERNS["unordered"], line)
        if unordered_match:
            indent, marker, content = unordered_match.groups()
            level = len(indent) // 2 + 1

            return ListItemInfo(
                content=content,
                level=level,
                list_type="unordered",
                marker=marker,
                start_line=line_num,
                end_line=line_num,
            )

        return None

    def _determine_list_type(self, marker: str, content: str) -> str:
        """
        Determine list type from marker and content.

        Args:
            marker: List marker
            content: List content

        Returns:
            List type: 'ordered', 'unordered', or 'task'
        """
        # Check for task list - look for checkbox pattern in content
        if re.match(r"^\[([ xX])\]", content.strip()):
            return "task"

        # Check for ordered list
        if re.match(r"^\d+\.", marker):
            return "ordered"

        # Default to unordered
        return "unordered"

    def _build_list_hierarchy(
        self, list_items: List[ListItemInfo]
    ) -> List[ListItemInfo]:
        """
        Build hierarchical structure from flat list items.

        Args:
            list_items: Flat list of list items

        Returns:
            List of root list items with children
        """
        if not list_items:
            return []

        root_items = []
        stack = []  # Stack to track parent items

        for item in list_items:
            # Find appropriate parent based on level
            while stack and stack[-1].level >= item.level:
                stack.pop()

            if stack:
                # Add as child to current parent
                parent = stack[-1]
                parent.children.append(item)
                item.parent = parent
            else:
                # This is a root item
                root_items.append(item)

            stack.append(item)

        return root_items

    def _create_chunks_from_lists(
        self, list_hierarchy: List[ListItemInfo], content: str, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Create chunks from list hierarchy.

        FIX: Groups multiple root items together to avoid single-item chunks
        (Requirement 9.4)

        Args:
            list_hierarchy: Root list items with children
            content: Original content
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []

        # FIX: Group multiple root items together when they fit
        current_items = []
        current_size = 0

        for root_item in list_hierarchy:
            item_size = self._calculate_item_size(root_item)

            # Check if we can add this item to current group
            if current_size + item_size <= config.max_chunk_size:
                current_items.append(root_item)
                current_size += item_size
            else:
                # Current group is full, create chunk(s) from it
                if current_items:
                    chunks.extend(self._create_chunks_from_items(current_items, config))

                # Start new group with current item
                current_items = [root_item]
                current_size = item_size

        # Process remaining items
        if current_items:
            chunks.extend(self._create_chunks_from_items(current_items, config))

        return chunks

    def _create_chunks_from_items(
        self, items: List[ListItemInfo], config: ChunkConfig
    ) -> List[Chunk]:
        """
        Create chunks from a group of list items.

        Args:
            items: List items to chunk
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []

        # If all items fit together, create single chunk
        total_size = sum(self._calculate_item_size(item) for item in items)

        if total_size <= config.max_chunk_size:
            # Create single chunk with all items
            chunk = self._create_multi_item_chunk(items, config)
            chunks.append(chunk)
        else:
            # Need to process items individually with potential splitting
            for root_item in items:
                item_size = self._calculate_item_size(root_item)

                if item_size <= config.max_chunk_size:
                    chunk = self._create_list_chunk(
                        root_item, config, is_continuation=False
                    )
                    chunks.append(chunk)
                else:
                    # Need to split this large item
                    groups = self._group_list_items(root_item, config.max_chunk_size)

                    for i, group in enumerate(groups):
                        group.is_continuation = i > 0
                        if group.is_continuation:
                            group.parent_context = self._generate_parent_context(
                                root_item
                            )

                        chunk = self._create_group_chunk(group, config)
                        chunks.append(chunk)

        return chunks

    def _calculate_item_size(self, item: ListItemInfo) -> int:
        """
        Calculate total size of list item including all children.

        Args:
            item: List item to measure

        Returns:
            Total size in characters
        """
        size = len(item.content) + len(item.marker) + 10  # Base size with formatting

        # Add size of all children recursively
        for child in item.children:
            size += self._calculate_item_size(child)

        return size

    def _group_list_items(
        self, root_item: ListItemInfo, max_chunk_size: int
    ) -> List[ListGroup]:
        """
        Group list items into chunks that fit within size constraints.

        FIX: Groups multiple items together to avoid single-item micro-chunks
        (Requirement 9.4)

        Args:
            root_item: Root list item to group
            max_chunk_size: Maximum size per chunk

        Returns:
            List of ListGroup objects
        """
        groups = []

        # For now, implement simple grouping by direct children
        # More sophisticated grouping can be added later
        current_group = ListGroup(
            items=[],
            size=0,
            start_line=root_item.start_line,
            end_line=root_item.start_line,
        )

        # Add root item header if it has content
        if root_item.content.strip():
            root_size = len(root_item.content) + len(root_item.marker) + 10
            current_group.items.append(root_item)
            current_group.size = root_size

        # Group children - try to include multiple items per chunk
        min_items_per_chunk = 2  # Avoid single-item chunks when possible

        for i, child in enumerate(root_item.children):
            child_size = self._calculate_item_size(child)

            # Check if we can add this child to current group
            can_add = current_group.size + child_size <= max_chunk_size

            # If this is the last child and current group has only 1 item,
            # try to add it even if slightly over size (to avoid single-item chunk)
            is_last = i == len(root_item.children) - 1
            has_few_items = len(current_group.items) < min_items_per_chunk

            if can_add or (is_last and has_few_items and child_size < max_chunk_size):
                # Add to current group
                current_group.items.append(child)
                current_group.size += child_size
                current_group.end_line = child.end_line
            else:
                # Current group is full
                if current_group.items:
                    groups.append(current_group)

                # Start new group
                current_group = ListGroup(
                    items=[child],
                    size=child_size,
                    start_line=child.start_line,
                    end_line=child.end_line,
                )

        # Add final group
        if current_group.items:
            groups.append(current_group)

        return groups

    def _generate_parent_context(self, root_item: ListItemInfo) -> str:
        """
        Generate parent context for continuation chunks.

        Args:
            root_item: Root item to use as context

        Returns:
            Formatted parent context string
        """
        if not root_item.content.strip():
            return ""

        indent = "  " * (root_item.level - 1)
        return f"{indent}{root_item.marker} {root_item.content}\n"

    def _create_list_chunk(
        self, item: ListItemInfo, config: ChunkConfig, is_continuation: bool = False
    ) -> Chunk:
        """
        Create a chunk from a single list item and its children.

        Args:
            item: List item to create chunk from
            config: Chunking configuration
            is_continuation: Whether this is a continuation chunk

        Returns:
            Chunk with list content
        """
        content = self._format_list_item(item)

        metadata = {
            "list_type": item.list_type,
            "item_count": self._count_items(item),
            "max_nesting": self._calculate_max_nesting(item),
            "has_nested_items": len(item.children) > 0,
            "is_continuation": is_continuation,
        }

        # Add specific metadata based on list type
        if item.list_type == "ordered" and item.number is not None:
            metadata["start_number"] = item.number
        elif item.list_type == "task" and item.is_checked is not None:
            metadata["is_checked"] = item.is_checked

        return self._create_chunk(
            content=content,
            start_line=item.start_line,
            end_line=item.end_line,
            content_type="list",
            **metadata,
        )

    def _create_multi_item_chunk(
        self, items: List[ListItemInfo], config: ChunkConfig
    ) -> Chunk:
        """
        Create a chunk from multiple list items.

        FIX: Groups multiple items to avoid single-item chunks (Requirement 9.4)

        Args:
            items: List items to include in chunk
            config: Chunking configuration

        Returns:
            Chunk with multiple list items
        """
        # Format all items
        content_parts = []
        for item in items:
            content_parts.append(self._format_list_item(item))

        content = "\n".join(content_parts)

        # Calculate metadata
        total_items = sum(self._count_items(item) for item in items)
        max_nesting = max(
            (self._calculate_max_nesting(item) for item in items), default=0
        )

        start_line = min(item.start_line for item in items)
        end_line = max(item.end_line for item in items)

        metadata = {
            "list_type": items[0].list_type if items else "unordered",
            "item_count": total_items,
            "max_nesting": max_nesting,
            "has_nested_items": any(len(item.children) > 0 for item in items),
            "is_continuation": False,
            "grouped_items": len(items),  # Track that this is a grouped chunk
        }

        return self._create_chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            content_type="list",
            **metadata,
        )

    def _create_group_chunk(self, group: ListGroup, config: ChunkConfig) -> Chunk:
        """
        Create a chunk from a list group.

        Args:
            group: List group to create chunk from
            config: Chunking configuration

        Returns:
            Chunk with grouped list content
        """
        content = group.parent_context

        for item in group.items:
            content += self._format_list_item(item)

        # Calculate metadata from all items in group
        list_types = set(item.list_type for item in group.items)
        main_list_type = list(list_types)[0] if len(list_types) == 1 else "mixed"

        metadata = {
            "list_type": main_list_type,
            "item_count": len(group.items),
            "max_nesting": max(
                self._calculate_max_nesting(item) for item in group.items
            ),
            "has_nested_items": any(len(item.children) > 0 for item in group.items),
            "is_continuation": group.is_continuation,
        }

        if group.is_continuation:
            metadata["has_parent_context"] = bool(group.parent_context.strip())

        return self._create_chunk(
            content=content.strip(),
            start_line=group.start_line,
            end_line=group.end_line,
            content_type="list",
            **metadata,
        )

    def _format_list_item(self, item: ListItemInfo, level_offset: int = 0) -> str:
        """
        Format a list item and its children as markdown.

        Args:
            item: List item to format
            level_offset: Additional indentation offset

        Returns:
            Formatted markdown string
        """
        indent = "  " * (item.level - 1 + level_offset)

        # Format marker based on type
        if item.list_type == "task":
            check_mark = "x" if item.is_checked else " "
            marker = f"- [{check_mark}]"
        elif item.list_type == "ordered":
            marker = f"{item.number}." if item.number else "1."
        else:
            # For unordered lists, use the original marker
            marker = item.marker

        content = f"{indent}{marker} {item.content}\n"

        # Add children recursively
        for child in item.children:
            content += self._format_list_item(child, level_offset)

        return content

    def _count_items(self, item: ListItemInfo) -> int:
        """
        Count total number of items including children.

        Args:
            item: Root item to count from

        Returns:
            Total item count
        """
        count = 1  # Count this item

        for child in item.children:
            count += self._count_items(child)

        return count

    def _calculate_max_nesting(self, item: ListItemInfo) -> int:
        """
        Calculate maximum nesting level in item tree.

        Args:
            item: Root item to analyze

        Returns:
            Maximum nesting level
        """
        if not item.children:
            return item.level

        max_child_level = max(
            self._calculate_max_nesting(child) for child in item.children
        )
        return max(item.level, max_child_level)

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            if analysis.list_count >= 5:
                return (
                    f"High list count ({analysis.list_count} lists) - "
                    f"suitable for list strategy"
                )
            else:
                return (
                    f"High list ratio ({analysis.list_ratio:.1%}) - "
                    f"suitable for list strategy"
                )
        else:
            return (
                f"Insufficient lists ({analysis.list_count} lists, "
                f"{analysis.list_ratio:.1%} ratio) for list strategy"
            )

    def get_list_statistics(self, chunks: List[Chunk]) -> Dict:
        """
        Get statistics about list-based chunks.

        Args:
            chunks: List of chunks created by this strategy

        Returns:
            Dictionary with list statistics
        """
        if not chunks:
            return {"total_chunks": 0, "list_types": {}}

        list_types = {}
        total_items = 0
        continuation_chunks = 0
        nested_chunks = 0

        for chunk in chunks:
            list_type = chunk.get_metadata("list_type", "unknown")
            list_types[list_type] = list_types.get(list_type, 0) + 1

            total_items += chunk.get_metadata("item_count", 0)

            if chunk.get_metadata("is_continuation", False):
                continuation_chunks += 1

            if chunk.get_metadata("has_nested_items", False):
                nested_chunks += 1

        return {
            "total_chunks": len(chunks),
            "list_types": list_types,
            "total_items": total_items,
            "continuation_chunks": continuation_chunks,
            "nested_chunks": nested_chunks,
            "avg_items_per_chunk": total_items / len(chunks) if chunks else 0,
        }
