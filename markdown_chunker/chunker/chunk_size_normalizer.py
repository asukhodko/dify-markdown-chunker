"""Chunk size normalizer for distribution improvement.

Implements simplified single-pass merging to reduce size variance (MC-004 fix).
"""

from typing import List

from markdown_chunker.chunker.types import Chunk, ChunkConfig


class ChunkSizeNormalizer:
    """Post-process chunks to reduce size variance through simple merging."""

    def __init__(self, config: ChunkConfig):
        """Initialize normalizer.

        Args:
            config: Chunking configuration
        """
        self.config = config
        self.min_effective_size = config.min_effective_chunk_size

    def normalize_chunk_sizes(self, chunks: List[Chunk]) -> List[Chunk]:
        """Normalize chunk sizes through linear single-pass merging.

        Args:
            chunks: List of chunks to normalize

        Returns:
            List of normalized chunks
        """
        if len(chunks) < 2:
            return chunks

        normalized = []
        i = 0

        while i < len(chunks):
            current = chunks[i]

            # Check if current chunk is undersized
            if current.size < self.min_effective_size and i + 1 < len(chunks):
                next_chunk = chunks[i + 1]

                # Check if can merge with next
                if self._can_merge(current, next_chunk):
                    merged = self._merge_chunks(current, next_chunk)
                    normalized.append(merged)
                    i += 2  # Skip both chunks
                    continue

            # Can't merge, keep as is
            normalized.append(current)
            i += 1

        return normalized

    def _can_merge(self, chunk1: Chunk, chunk2: Chunk) -> bool:
        """Check if two chunks can be merged.

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            True if chunks can be merged
        """
        # Must have same section_path
        path1 = chunk1.metadata.get("section_path", [])
        path2 = chunk2.metadata.get("section_path", [])

        if path1 != path2:
            return False

        # Combined size must not exceed max
        combined_size = chunk1.size + chunk2.size
        if combined_size > self.config.max_chunk_size:
            return False

        return True

    def _merge_chunks(self, chunk1: Chunk, chunk2: Chunk) -> Chunk:
        """Merge two adjacent chunks.

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            Merged chunk
        """
        # Combine content
        merged_content = chunk1.content + "\n\n" + chunk2.content

        # Merge metadata (prefer chunk1, add merge info)
        merged_metadata = chunk1.metadata.copy()
        merged_metadata["merged_chunks"] = True
        merged_metadata["original_chunk_count"] = 2

        # FIX #3: Check if merged chunk exceeds max size and mark oversize flag
        # This addresses size compliance when normalizer merges chunks
        merged_size = len(merged_content)
        if merged_size > self.config.max_chunk_size:
            overage_pct = (
                (merged_size - self.config.max_chunk_size) / self.config.max_chunk_size
            ) * 100

            if overage_pct <= 5.0:
                # Small overage within 5% tolerance
                merged_metadata["allow_oversize"] = True
                merged_metadata["oversize_reason"] = "block_alignment_tolerance"
                merged_metadata["oversize_pct"] = round(overage_pct, 2)
            else:
                # Larger overage - mark with merge reason
                merged_metadata["allow_oversize"] = True
                merged_metadata["oversize_reason"] = "normalizer_merge"
                merged_metadata["oversize_pct"] = round(overage_pct, 2)

        # Update line range
        return Chunk(
            content=merged_content,
            start_line=chunk1.start_line,
            end_line=chunk2.end_line,
            metadata=merged_metadata,
        )
