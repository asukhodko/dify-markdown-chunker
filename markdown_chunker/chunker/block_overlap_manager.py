"""Block-based overlap manager.

Replaces character-based overlap with block-based overlap to address MC-003.
Ensures overlap respects block boundaries and never crosses section headers.
"""

import logging
from typing import List, Optional

from markdown_chunker.chunker.block_packer import Block, BlockType
from markdown_chunker.chunker.types import Chunk, ChunkConfig

logger = logging.getLogger(__name__)


class BlockOverlapManager:
    """Calculate overlap using complete blocks only.

    Addresses MC-003 by ensuring:
    - Overlap contains only complete blocks (no mid-block splits)
    - Overlap doesn't include headers from different sections
    - Blocks are atomic units for overlap calculation
    """

    def __init__(self, config: ChunkConfig):
        """Initialize block overlap manager.

        Args:
            config: Chunking configuration
        """
        self.config = config

    def apply_block_overlap(
        self, chunks: List[Chunk], blocks_by_chunk: Optional[List[List[Block]]] = None
    ) -> List[Chunk]:
        """Apply block-based overlap to chunks.

        Args:
            chunks: List of chunks to add overlap to
            blocks_by_chunk: Optional list of blocks for each chunk

        Returns:
            List of chunks with overlap added
        """
        if not self.config.enable_overlap or len(chunks) < 2:
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk has no previous overlap
                overlapped_chunks.append(chunk)
                continue

            prev_chunk = chunks[i - 1]

            # Extract overlap blocks from previous chunk
            overlap_blocks = self._extract_overlap_blocks(
                prev_chunk, blocks_by_chunk[i - 1] if blocks_by_chunk else None
            )

            if not overlap_blocks:
                overlapped_chunks.append(chunk)
                continue

            # Validate overlap doesn't cross section boundaries
            if not self._validate_overlap_boundaries(overlap_blocks, chunk):
                # Skip overlap if it crosses sections
                overlapped_chunks.append(chunk)
                continue

            # Add overlap to chunk
            enhanced_chunk = self._add_overlap_to_chunk(
                chunk, overlap_blocks, prev_chunk_index=i - 1
            )
            overlapped_chunks.append(enhanced_chunk)

        return overlapped_chunks

    def _extract_overlap_blocks(  # noqa: C901
        self, chunk: Chunk, blocks: Optional[List[Block]] = None
    ) -> List[Block]:
        """Extract last N blocks from chunk for overlap.

        Args:
            chunk: Chunk to extract overlap from
            blocks: Optional pre-extracted blocks

        Returns:
            List of blocks for overlap
        """
        if blocks is None:
            # Re-extract blocks from chunk content
            from markdown_chunker.chunker.block_packer import BlockPacker

            packer = BlockPacker()
            blocks = packer.extract_blocks(chunk.content)

        if not blocks:
            return []

        # Walk backward accumulating blocks until size >= overlap_size
        overlap_size_target = self.config.overlap_size
        accumulated_size = 0
        overlap_blocks: list[Block] = []

        for block in reversed(blocks):
            # Skip headers in overlap (prevent cross-section overlap)
            if block.type == BlockType.HEADER:
                continue

            # Skip code blocks in overlap (prevent splitting code blocks - MC-002)
            # Code blocks must remain atomic and never be split
            if block.type == BlockType.CODE:
                continue

            # Skip table blocks in overlap (prevent splitting tables - MC-002)
            # Tables must remain atomic and never be split
            if block.type == BlockType.TABLE:
                continue

            # Skip blank blocks
            if block.type == BlockType.BLANK:
                continue

            overlap_blocks.insert(0, block)
            accumulated_size += block.size

            if accumulated_size >= overlap_size_target:
                break

        # Limit overlap to 50% of chunk size
        max_overlap_size = chunk.size // 2
        if accumulated_size > max_overlap_size:
            # Trim blocks from start to fit limit
            while overlap_blocks and accumulated_size > max_overlap_size:
                removed_block = overlap_blocks.pop(0)
                accumulated_size -= removed_block.size

        # STRICT ENFORCEMENT: Ensure ratio never exceeds 50%
        # Even if blocks were trimmed, verify the actual ratio
        if overlap_blocks and accumulated_size > 0:
            overlap_ratio = accumulated_size / chunk.size
            if overlap_ratio > 0.50:
                # Log warning and reduce further if needed
                logger.warning(
                    f"Overlap ratio {overlap_ratio:.1%} exceeds 50% limit, "
                    f"reducing overlap for chunk safety"
                )
                # Trim until ratio is under 50%
                while overlap_blocks and accumulated_size / chunk.size > 0.50:
                    removed_block = overlap_blocks.pop(0)
                    accumulated_size -= removed_block.size

        return overlap_blocks

    def _validate_overlap_boundaries(
        self, overlap_blocks: List[Block], next_chunk: Chunk
    ) -> bool:
        """Validate that overlap doesn't cross section boundaries.

        Args:
            overlap_blocks: Blocks to use for overlap
            next_chunk: Next chunk receiving overlap

        Returns:
            True if overlap is valid, False if it would cross sections
        """
        if not overlap_blocks:
            return True

        # Check if any overlap block is a section header
        for block in overlap_blocks:
            if block.type == BlockType.HEADER:
                return False

        # Check if overlap would include content from different section_path
        # This is handled by excluding headers from overlap

        return True

    def _add_overlap_to_chunk(
        self, chunk: Chunk, overlap_blocks: List[Block], prev_chunk_index: int
    ) -> Chunk:
        """Add overlap blocks to chunk.

        Args:
            chunk: Chunk to add overlap to
            overlap_blocks: Blocks to add as overlap
            prev_chunk_index: Index of previous chunk

        Returns:
            Enhanced chunk with overlap
        """
        if not overlap_blocks:
            return chunk

        # Calculate total overlap size
        overlap_size = sum(block.size for block in overlap_blocks)

        # Build overlap content
        overlap_content = "\n\n".join(block.content for block in overlap_blocks)

        # CRITICAL FIX: Enforce 50% overlap limit
        # Calculate what final chunk size would be
        core_size = len(chunk.content)
        separator_size = 2  # "\n\n"
        final_size = overlap_size + separator_size + core_size

        # Check if overlap exceeds 50% of final chunk
        if final_size > 0:
            overlap_ratio = overlap_size / final_size
            if overlap_ratio > 0.5:
                # Trim overlap to meet 50% constraint
                # Target: overlap / (overlap + separator + core) = 0.5
                # Solving: overlap = core + separator
                max_overlap = core_size + separator_size
                if overlap_size > max_overlap:
                    # Truncate overlap content to max_overlap size
                    # Use word boundary truncation
                    from .text_normalizer import truncate_at_word_boundary

                    overlap_content = truncate_at_word_boundary(
                        overlap_content, max_overlap, from_end=True
                    )
                    overlap_size = len(overlap_content)

        # Create new chunk with overlap prepended
        new_content = overlap_content + "\n\n" + chunk.content

        # Copy metadata and add overlap info
        new_metadata = chunk.metadata.copy()
        new_metadata["has_overlap"] = True
        new_metadata["overlap_size"] = overlap_size
        new_metadata["overlap_type"] = "block_based"
        new_metadata["overlap_block_count"] = len(overlap_blocks)
        new_metadata["previous_chunk_index"] = prev_chunk_index

        # Create enhanced chunk
        return Chunk(
            content=new_content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )
