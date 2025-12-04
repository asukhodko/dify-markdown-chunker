"""
Nesting resolver for fenced blocks.

This module implements nesting resolution for fenced code blocks,
building parent-child relationships and calculating nesting levels.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BlockCandidate:
    """
    Represents a fenced block candidate for nesting resolution.

    Attributes:
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed)
        block_type: Type of block (e.g., 'code', 'math')
        fence_char: Fence character used ('`' or '~')
        fence_length: Length of fence (3+)
        language: Language identifier (for code blocks)
        nesting_level: Calculated nesting level (0 = top level)
        parent_block: Reference to parent block (if nested)
    """

    start_line: int
    end_line: int
    block_type: str = "code"
    fence_char: str = "`"
    fence_length: int = 3
    language: str = ""
    nesting_level: int = 0
    parent_block: Optional["BlockCandidate"] = None

    def contains(self, other: "BlockCandidate") -> bool:
        """
        Check if this block fully contains another block.

        Args:
            other: Another block to check

        Returns:
            True if this block fully contains the other block
        """
        return self.start_line < other.start_line and self.end_line > other.end_line

    def overlaps(self, other: "BlockCandidate") -> bool:
        """
        Check if this block overlaps with another block (invalid nesting).

        Args:
            other: Another block to check

        Returns:
            True if blocks overlap but don't have proper containment
        """
        # No overlap if completely separate (including adjacent blocks)
        if self.end_line <= other.start_line or self.start_line >= other.end_line:
            return False

        # Proper containment is not overlap
        if self.contains(other) or other.contains(self):
            return False

        # Any other intersection is overlap
        return True


class NestingResolver:
    """
    Resolves nesting relationships between fenced blocks.

    This class builds a tree structure of nested blocks and calculates
    nesting levels based on containment relationships.
    """

    def __init__(self):
        """Initialize the nesting resolver."""
        self.blocks: List[BlockCandidate] = []
        self.resolved: bool = False

    def add_block(self, block: BlockCandidate) -> None:
        """
        Add a block candidate for nesting resolution.

        Args:
            block: Block to add
        """
        self.blocks.append(block)
        self.resolved = False

    def resolve(self) -> List[BlockCandidate]:
        """
        Resolve nesting relationships for all blocks.

        Returns:
            List of blocks with nesting information populated

        Raises:
            ValueError: If nesting is invalid (overlapping blocks)
        """
        if not self.blocks:
            return []

        # Sort blocks by start line, then by end line (descending)
        # This ensures we process outer blocks before inner blocks
        sorted_blocks = sorted(self.blocks, key=lambda b: (b.start_line, -b.end_line))

        # Validate no overlaps
        self._validate_no_overlaps(sorted_blocks)

        # Build parent-child relationships
        self._build_relationships(sorted_blocks)

        # Calculate nesting levels
        self._calculate_nesting_levels(sorted_blocks)

        self.resolved = True
        return sorted_blocks

    def _validate_no_overlaps(self, blocks: List[BlockCandidate]) -> None:
        """
        Validate that no blocks overlap invalidly.

        Args:
            blocks: Sorted list of blocks

        Raises:
            ValueError: If overlapping blocks are found
        """
        for i, block1 in enumerate(blocks):
            for block2 in blocks[i + 1 :]:
                if block1.overlaps(block2):
                    raise ValueError(
                        f"Invalid nesting: blocks overlap at lines "
                        f"{block1.start_line}-{block1.end_line} and "
                        f"{block2.start_line}-{block2.end_line}"
                    )

    def _build_relationships(self, blocks: List[BlockCandidate]) -> None:
        """
        Build parent-child relationships between blocks.

        Args:
            blocks: Sorted list of blocks
        """
        for i, child in enumerate(blocks):
            # Find the smallest containing block (immediate parent)
            parent = None
            parent_size = float("inf")

            for potential_parent in blocks[:i]:  # Only check earlier blocks
                if potential_parent.contains(child):
                    size = potential_parent.end_line - potential_parent.start_line
                    if size < parent_size:
                        parent = potential_parent
                        parent_size = size

            child.parent_block = parent

    def _calculate_nesting_levels(self, blocks: List[BlockCandidate]) -> None:
        """
        Calculate nesting levels for all blocks.

        Args:
            blocks: List of blocks with parent relationships
        """
        for block in blocks:
            level = 0
            current = block
            while current.parent_block is not None:
                level += 1
                current = current.parent_block
            block.nesting_level = level


def resolve_nesting(blocks: List[BlockCandidate]) -> List[BlockCandidate]:
    """
    Convenience function to resolve nesting for a list of blocks.

    Args:
        blocks: List of block candidates

    Returns:
        List of blocks with nesting information populated

    Raises:
        ValueError: If nesting is invalid
    """
    if not blocks:
        return []

    resolver = NestingResolver()
    for block in blocks:
        resolver.add_block(block)

    return resolver.resolve()


def validate_block_nesting(blocks: List[BlockCandidate]) -> bool:
    """
    Validate that block nesting is consistent.

    Args:
        blocks: List of blocks to validate

    Returns:
        True if nesting is valid, False otherwise
    """
    try:
        resolve_nesting(blocks)
        return True
    except ValueError as e:
        logger.warning(f"Invalid block nesting: {e}")
        return False


def get_nesting_tree(blocks: List[BlockCandidate]) -> Dict[int, List[BlockCandidate]]:
    """
    Get blocks organized by nesting level.

    Args:
        blocks: List of resolved blocks

    Returns:
        Dictionary mapping nesting level to list of blocks at that level
    """
    tree: Dict[int, List[BlockCandidate]] = {}

    for block in blocks:
        level = block.nesting_level
        if level not in tree:
            tree[level] = []
        tree[level].append(block)

    return tree


def get_children(
    block: BlockCandidate, all_blocks: List[BlockCandidate]
) -> List[BlockCandidate]:
    """
    Get direct children of a block.

    Args:
        block: Parent block
        all_blocks: List of all blocks

    Returns:
        List of direct children
    """
    return [b for b in all_blocks if b.parent_block == block]


def get_max_nesting_depth(blocks: List[BlockCandidate]) -> int:
    """
    Get maximum nesting depth in a list of blocks.

    Args:
        blocks: List of blocks

    Returns:
        Maximum nesting level (0 if no blocks)
    """
    if not blocks:
        return 0
    return max(b.nesting_level for b in blocks)
