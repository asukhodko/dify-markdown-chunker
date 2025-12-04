"""
BlockTracker - Tracks content blocks for validation of chunking completeness.

This module addresses the critical issue of content loss on chunk boundaries
(problem 3.1 `block-loss-on-boundaries` from manual testing report).

It ensures every source block appears in at least one output chunk and
detects excessive duplication of non-header blocks.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BlockInfo:
    """
    Information about a content block in the source document.

    A block is an atomic unit of markdown content that should not be
    split across chunks (paragraph, list, table, code block, header).
    """

    block_id: str
    block_type: str  # 'paragraph', 'list', 'table', 'code', 'header'
    content_hash: str
    start_offset: int
    end_offset: int
    start_line: int = 0
    end_line: int = 0
    is_header: bool = False
    header_level: Optional[int] = None
    parent_section_id: Optional[str] = None
    content_preview: str = ""  # First 50 chars for debugging

    @classmethod
    def from_content(
        cls,
        block_id: str,
        block_type: str,
        content: str,
        start_offset: int,
        end_offset: int,
        start_line: int = 0,
        end_line: int = 0,
        is_header: bool = False,
        header_level: Optional[int] = None,
        parent_section_id: Optional[str] = None,
    ) -> "BlockInfo":
        """Create BlockInfo from content string."""
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()[:16]
        content_preview = content[:50].replace("\n", " ")

        return cls(
            block_id=block_id,
            block_type=block_type,
            content_hash=content_hash,
            start_offset=start_offset,
            end_offset=end_offset,
            start_line=start_line,
            end_line=end_line,
            is_header=is_header,
            header_level=header_level,
            parent_section_id=parent_section_id,
            content_preview=content_preview,
        )


@dataclass
class ValidationResult:
    """Result of block coverage validation."""

    is_valid: bool
    coverage_percentage: float
    missing_blocks: List[str] = field(default_factory=list)
    over_duplicated_blocks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def get_summary(self) -> str:
        """Get human-readable summary."""
        status = "VALID" if self.is_valid else "INVALID"
        parts = [
            f"Status: {status}",
            f"Coverage: {self.coverage_percentage:.1f}%",
        ]
        if self.missing_blocks:
            parts.append(f"Missing blocks: {len(self.missing_blocks)}")
        if self.over_duplicated_blocks:
            parts.append(f"Over-duplicated blocks: {len(self.over_duplicated_blocks)}")
        return ", ".join(parts)


class BlockTracker:
    """
    Tracks which blocks appear in which chunks for validation.

    This component ensures:
    1. Every source block appears in at least one chunk (no data loss)
    2. Non-header blocks don't appear in more than 2 consecutive chunks
    3. Provides coverage statistics for debugging

    Usage:
        tracker = BlockTracker()

        # Register blocks from source document
        for block in parse_blocks(document):
            tracker.register_block(block)

        # Record which blocks appear in each chunk
        for i, chunk in enumerate(chunks):
            for block_id in extract_block_ids(chunk):
                tracker.record_block_in_chunk(block_id, i)

        # Validate completeness
        result = tracker.validate_completeness()
        if not result.is_valid:
            print(f"Missing blocks: {result.missing_blocks}")
    """

    def __init__(self, max_duplication: int = 2):
        """
        Initialize BlockTracker.

        Args:
            max_duplication: Maximum times a non-header block can appear
                            in consecutive chunks (default: 2)
        """
        self.blocks: Dict[str, BlockInfo] = {}
        self.block_to_chunks: Dict[str, List[int]] = {}
        self.max_duplication = max_duplication
        self._block_counter = 0

    def generate_block_id(self) -> str:
        """Generate unique block ID."""
        self._block_counter += 1
        return f"block_{self._block_counter}"

    def register_block(self, block: BlockInfo) -> None:
        """
        Register a block from the source document.

        Args:
            block: BlockInfo describing the block
        """
        self.blocks[block.block_id] = block
        if block.block_id not in self.block_to_chunks:
            self.block_to_chunks[block.block_id] = []

    def register_block_from_content(
        self,
        content: str,
        block_type: str,
        start_offset: int,
        end_offset: int,
        start_line: int = 0,
        end_line: int = 0,
        is_header: bool = False,
        header_level: Optional[int] = None,
        parent_section_id: Optional[str] = None,
    ) -> str:
        """
        Register a block from content string.

        Returns:
            Generated block_id
        """
        block_id = self.generate_block_id()
        block = BlockInfo.from_content(
            block_id=block_id,
            block_type=block_type,
            content=content,
            start_offset=start_offset,
            end_offset=end_offset,
            start_line=start_line,
            end_line=end_line,
            is_header=is_header,
            header_level=header_level,
            parent_section_id=parent_section_id,
        )
        self.register_block(block)
        return block_id

    def record_block_in_chunk(self, block_id: str, chunk_index: int) -> None:
        """
        Record that a block appears in a chunk.

        Args:
            block_id: ID of the block
            chunk_index: Index of the chunk (0-based)
        """
        if block_id not in self.block_to_chunks:
            self.block_to_chunks[block_id] = []

        # Avoid duplicate recordings for same chunk
        if chunk_index not in self.block_to_chunks[block_id]:
            self.block_to_chunks[block_id].append(chunk_index)
            self.block_to_chunks[block_id].sort()

    def get_missing_blocks(self) -> List[str]:
        """
        Get blocks that don't appear in any chunk.

        Returns:
            List of block IDs that are missing from all chunks
        """
        missing = []
        for block_id in self.blocks:
            chunks = self.block_to_chunks.get(block_id, [])
            if not chunks:
                missing.append(block_id)
        return missing

    def get_over_duplicated_blocks(self, max_count: Optional[int] = None) -> List[str]:
        """
        Get non-header blocks appearing in more than max_count consecutive chunks.

        Args:
            max_count: Maximum allowed appearances (default: self.max_duplication)

        Returns:
            List of block IDs that are over-duplicated
        """
        if max_count is None:
            max_count = self.max_duplication

        over_duplicated = []
        for block_id, chunks in self.block_to_chunks.items():
            block = self.blocks.get(block_id)

            # Headers are allowed to appear in more chunks
            if block and block.is_header:
                continue

            # Check for consecutive appearances exceeding limit
            if len(chunks) > max_count:
                # Verify they are consecutive
                consecutive_count = 1
                max_consecutive = 1
                for i in range(1, len(chunks)):
                    if chunks[i] == chunks[i - 1] + 1:
                        consecutive_count += 1
                        max_consecutive = max(max_consecutive, consecutive_count)
                    else:
                        consecutive_count = 1

                if max_consecutive > max_count:
                    over_duplicated.append(block_id)

        return over_duplicated

    def get_block_chunk_count(self, block_id: str) -> int:
        """Get number of chunks a block appears in."""
        return len(self.block_to_chunks.get(block_id, []))

    def get_chunks_for_block(self, block_id: str) -> List[int]:
        """Get list of chunk indices where block appears."""
        return self.block_to_chunks.get(block_id, []).copy()

    def validate_completeness(self) -> ValidationResult:
        """
        Validate that all blocks are covered and duplication is controlled.

        Returns:
            ValidationResult with coverage statistics and issues
        """
        missing = self.get_missing_blocks()
        over_duplicated = self.get_over_duplicated_blocks()

        total_blocks = len(self.blocks)
        covered_blocks = total_blocks - len(missing)
        coverage = (covered_blocks / total_blocks * 100) if total_blocks > 0 else 100.0

        warnings = []
        errors = []

        # Check for missing blocks (critical)
        if missing:
            block_previews = []
            for block_id in missing[:5]:  # Show first 5
                block = self.blocks.get(block_id)
                if block:
                    block_previews.append(
                        f"{block_id} ({block.block_type}): '{block.content_preview}...'"
                    )
            errors.append(
                f"Content loss detected: {len(missing)} blocks missing from output. "
                f"Examples: {'; '.join(block_previews)}"
            )

        # Check for over-duplication (warning)
        if over_duplicated:
            block_info = []
            for block_id in over_duplicated[:5]:
                chunks = self.block_to_chunks.get(block_id, [])
                block_info.append(f"{block_id} in chunks {chunks}")
            warnings.append(
                f"Excessive duplication: {len(over_duplicated)} non-header blocks "
                f"appear in >{self.max_duplication} consecutive chunks. "
                f"Examples: {'; '.join(block_info)}"
            )

        # Coverage warning
        if coverage < 95.0:
            warnings.append(f"Low coverage: {coverage:.1f}% of blocks covered")

        is_valid = len(missing) == 0 and coverage >= 95.0

        return ValidationResult(
            is_valid=is_valid,
            coverage_percentage=coverage,
            missing_blocks=missing,
            over_duplicated_blocks=over_duplicated,
            warnings=warnings,
            errors=errors,
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get tracking statistics."""
        total_blocks = len(self.blocks)
        header_blocks = sum(1 for b in self.blocks.values() if b.is_header)
        content_blocks = total_blocks - header_blocks

        covered = sum(1 for chunks in self.block_to_chunks.values() if chunks)

        return {
            "total_blocks": total_blocks,
            "header_blocks": header_blocks,
            "content_blocks": content_blocks,
            "covered_blocks": covered,
            "missing_blocks": total_blocks - covered,
            "coverage_percentage": (
                (covered / total_blocks * 100) if total_blocks > 0 else 100.0
            ),
        }

    def clear(self) -> None:
        """Clear all tracking data."""
        self.blocks.clear()
        self.block_to_chunks.clear()
        self._block_counter = 0
