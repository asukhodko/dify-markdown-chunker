"""
OverlapManager - Manages overlap between adjacent chunks for continuity.
This component creates overlapping content between chunks to maintain context
and improve readability when chunks are processed independently.

CRITICAL FIX (chunker-critical-fixes spec):
- Block-aware overlap: overlap boundaries align to block boundaries
- No character-based fallback: if no block fits, overlap = 0 with warning
- This preserves block integrity and prevents data loss/duplication issues
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from ..text_normalizer import truncate_at_word_boundary, validate_no_word_fragments
from ..types import Chunk, ChunkConfig

logger = logging.getLogger(__name__)


@dataclass
class ContentBlock:
    """A content block within a chunk for block-aware overlap."""

    content: str
    block_type: str  # 'paragraph', 'header', 'list', 'code', 'table'
    start_pos: int  # Position within chunk content
    end_pos: int
    is_header: bool = False

    @property
    def size(self) -> int:
        return len(self.content)


class OverlapManager:
    """
    Manages overlap between adjacent chunks.

    This component:
    - Creates sentence-based overlap between chunks
    - Supports both percentage and fixed-size overlap
    - Preserves sentence boundaries
    - Handles edge cases (short chunks, no sentences)
    - Updates chunk metadata with overlap information
    """

    # Sentence boundary patterns
    SENTENCE_END_PATTERN = r"[.!?]+\s+"

    def __init__(self, config: ChunkConfig):
        """
        Initialize OverlapManager.

        Args:
            config: Chunking configuration with overlap settings
        """
        self.config = config

    def apply_overlap(self, chunks: List[Chunk], include_metadata: bool = False) -> List[Chunk]:
        """
        Apply overlap to a list of chunks using the new neighbor context model.

        This method extracts context from neighboring chunks and either:
        - Stores it in metadata fields (metadata mode: include_metadata=True)
        - Merges it into content (legacy mode: include_metadata=False)

        Args:
            chunks: List of core chunks to process (from Phase 1)
            include_metadata: If True, store contexts in previous_content/next_content;
                            if False, merge contexts into content (legacy mode)

        Returns:
            List of chunks with neighbor context applied according to mode
        """
        if not chunks or len(chunks) < 2:
            # No overlap needed for single chunk or empty list
            return chunks

        if not self.config.enable_overlap:
            # Overlap disabled - no-op
            return chunks

        # Calculate effective overlap size
        effective_overlap = self._calculate_effective_overlap(chunks)
        
        if effective_overlap == 0:
            # No overlap - no-op
            return chunks

        # Extract contexts from all chunks (single pass over core chunks)
        result_chunks = []
        
        for i, chunk in enumerate(chunks):
            # Extract previous_content from previous chunk (if exists)
            previous_content = ""
            previous_chunk_index = None
            if i > 0:
                previous_content = self._extract_suffix_context(
                    chunks[i - 1], effective_overlap
                )
                if previous_content:
                    previous_chunk_index = i - 1
            
            # Extract next_content from next chunk (if exists)
            next_content = ""
            next_chunk_index = None
            if i < len(chunks) - 1:
                next_content = self._extract_prefix_context(
                    chunks[i + 1], effective_overlap
                )
                if next_content:
                    next_chunk_index = i + 1
            
            # Apply mode-specific logic
            if include_metadata:
                # Metadata mode: store in metadata, keep content clean
                new_chunk = self._add_context_to_metadata(
                    chunk, previous_content, next_content,
                    previous_chunk_index, next_chunk_index
                )
            else:
                # Legacy mode: merge into content
                new_chunk = self._merge_context_into_content(
                    chunk, previous_content, next_content
                )
            
            result_chunks.append(new_chunk)
        
        return result_chunks

    def _calculate_effective_overlap(self, chunks: List[Chunk]) -> int:
        """
        Calculate effective overlap size based on configuration.
        
        Args:
            chunks: List of chunks (for percentage calculation)
        
        Returns:
            Effective overlap size in characters
        """
        if self.config.overlap_size > 0:
            # Fixed-size overlap takes priority
            return self.config.overlap_size
        elif self.config.overlap_percentage > 0 and chunks:
            # Percentage-based: use average chunk size
            avg_chunk_size = sum(len(c.content) for c in chunks) // len(chunks)
            return int(avg_chunk_size * self.config.overlap_percentage)
        else:
            return 0
    
    def _extract_suffix_context(self, chunk: Chunk, target_size: int) -> str:
        """
        Extract context from the END of a core chunk for use as previous_content.
        
        Uses block-aligned extraction to preserve structural integrity.
        
        Args:
            chunk: Core chunk to extract from
            target_size: Target context size (effective_overlap)
        
        Returns:
            Context string (suffix of chunk.content), or empty string if extraction fails
        """
        content = chunk.content
        
        if not content.strip():
            return ""
        
        # Apply 40% maximum ratio relative to source chunk size
        max_overlap = max(50, int(len(content) * 0.40))
        actual_target = min(target_size, max_overlap)
        
        if actual_target <= 0:
            return ""
        
        # Use block-aligned extraction
        overlap_text = self._extract_block_aligned_overlap(chunk, actual_target)
        
        if overlap_text is None:
            # No blocks fit - return empty
            logger.debug(
                f"Block-aligned suffix context extraction failed: "
                f"no complete blocks fit within {actual_target} chars"
            )
            return ""
        
        # Verify no unbalanced code fences
        if self._has_unbalanced_fences(overlap_text):
            logger.debug("Suffix context has unbalanced code fences, skipping")
            return ""
        
        return overlap_text
    
    def _extract_prefix_context(self, chunk: Chunk, target_size: int) -> str:
        """
        Extract context from the BEGINNING of a core chunk for use as next_content.
        
        Uses block-aligned extraction to preserve structural integrity.
        
        Args:
            chunk: Core chunk to extract from
            target_size: Target context size (effective_overlap)
        
        Returns:
            Context string (prefix of chunk.content), or empty string if extraction fails
        """
        content = chunk.content
        
        if not content.strip():
            return ""
        
        # Apply 40% maximum ratio relative to source chunk size
        max_overlap = max(50, int(len(content) * 0.40))
        actual_target = min(target_size, max_overlap)
        
        if actual_target <= 0:
            return ""
        
        # Extract blocks from beginning
        blocks = self._extract_blocks_from_content(content)
        if not blocks:
            return ""
        
        # Collect blocks from beginning until we reach target size
        selected_blocks: List[ContentBlock] = []
        total_size = 0
        
        for block in blocks:
            block_size = block.size
            
            # Check if adding this block would exceed target
            if total_size == 0:
                # Allow first block with tolerance
                if block_size <= actual_target * 1.2:
                    selected_blocks.append(block)
                    total_size += block_size
                else:
                    logger.debug(
                        f"First block too large for prefix context: {block_size} > {actual_target * 1.2}"
                    )
                    break
            elif total_size + block_size + 2 <= actual_target:
                selected_blocks.append(block)
                total_size += block_size + 2
            else:
                break
        
        if not selected_blocks:
            logger.debug("No blocks fit within prefix context target size")
            return ""
        
        # Join selected blocks
        overlap_text = "\n\n".join(b.content for b in selected_blocks).strip()
        
        # Verify no unbalanced code fences
        if self._has_unbalanced_fences(overlap_text):
            logger.debug("Prefix context has unbalanced code fences, skipping")
            return ""
        
        return overlap_text
    
    def _add_context_to_metadata(
        self, 
        chunk: Chunk, 
        previous_content: str, 
        next_content: str,
        previous_chunk_index: Optional[int],
        next_chunk_index: Optional[int]
    ) -> Chunk:
        """
        Add neighbor context to chunk metadata (metadata mode).
        
        Only adds fields when context is non-empty.
        
        Args:
            chunk: Original core chunk
            previous_content: Context from previous chunk (may be empty)
            next_content: Context from next chunk (may be empty)
            previous_chunk_index: Index of previous chunk (None if no context)
            next_chunk_index: Index of next chunk (None if no context)
        
        Returns:
            New chunk with context in metadata, content unchanged
        """
        new_metadata = chunk.metadata.copy()
        
        # Only add fields when non-empty
        if previous_content:
            new_metadata["previous_content"] = previous_content
            if previous_chunk_index is not None:
                new_metadata["previous_chunk_index"] = previous_chunk_index
        
        if next_content:
            new_metadata["next_content"] = next_content
            if next_chunk_index is not None:
                new_metadata["next_chunk_index"] = next_chunk_index
        
        # Create new chunk with original content and updated metadata
        return Chunk(
            content=chunk.content,  # Unchanged - stays as content_core
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )
    
    def _merge_context_into_content(
        self, 
        chunk: Chunk, 
        previous_content: str, 
        next_content: str
    ) -> Chunk:
        """
        Merge neighbor context into chunk content (legacy mode).
        
        Creates: content = previous_content + content_core + next_content
        
        Args:
            chunk: Original core chunk
            previous_content: Context from previous chunk (may be empty)
            next_content: Context from next chunk (may be empty)
        
        Returns:
            New chunk with merged content
        """
        # Build merged content
        parts = []
        if previous_content:
            parts.append(previous_content)
        parts.append(chunk.content)  # content_core
        if next_content:
            parts.append(next_content)
        
        merged_content = "\n\n".join(parts)
        
        # Verify no unbalanced code fences in final content
        if self._has_unbalanced_fences(merged_content):
            # Skip merging to preserve code block integrity
            logger.warning(
                "Merging context would create unbalanced code fences, "
                "returning original chunk"
            )
            return chunk
        
        # Check if merged content exceeds max_chunk_size
        if len(merged_content) > self.config.max_chunk_size:
            # Truncate contexts to fit
            available_space = self.config.max_chunk_size - len(chunk.content) - 4  # -4 for separators
            
            if available_space <= 0:
                # No space for context - return original
                return chunk
            
            # Distribute space between previous and next
            prev_space = available_space // 2
            next_space = available_space - prev_space
            
            if previous_content and len(previous_content) > prev_space:
                previous_content = truncate_at_word_boundary(
                    previous_content, prev_space, from_end=True
                )
            
            if next_content and len(next_content) > next_space:
                next_content = truncate_at_word_boundary(
                    next_content, next_space, from_end=False
                )
            
            # Rebuild merged content
            parts = []
            if previous_content:
                parts.append(previous_content)
            parts.append(chunk.content)
            if next_content:
                parts.append(next_content)
            merged_content = "\n\n".join(parts)
        
        # Create new chunk with merged content
        # Note: metadata does NOT include previous_content/next_content fields in legacy mode
        return Chunk(
            content=merged_content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=chunk.metadata.copy(),  # Keep original metadata, don't add context fields
        )
    
    def _is_code_chunk(self, chunk: Chunk) -> bool:
        """
        Check if chunk contains code block content.

        Args:
            chunk: Chunk to check

        Returns:
            True if chunk contains code blocks
        """
        content_type = chunk.get_metadata("content_type", "")
        if content_type == "code":
            return True
        # Also check for fence markers
        return "```" in chunk.content

    def _has_unbalanced_fences(self, text: str) -> bool:
        """
        Check if text has unbalanced code fences.

        Args:
            text: Text to check

        Returns:
            True if fences are unbalanced
        """
        return text.count("```") % 2 != 0

    def _extract_blocks_from_content(self, content: str) -> List[ContentBlock]:
        """
        Extract content blocks from chunk content for block-aware overlap.

        Blocks are identified by:
        - Code blocks (``` ... ```)
        - Paragraphs (separated by double newlines)
        - Headers (lines starting with #)
        - Lists (lines starting with -, *, +, or numbers)

        Args:
            content: Chunk content to parse

        Returns:
            List of ContentBlock objects in document order
        """
        blocks = []

        # First, extract code blocks as atomic units
        code_block_pattern = r"```[\s\S]*?```"

        last_end = 0
        for match in re.finditer(code_block_pattern, content):
            # Process content before this code block
            if match.start() > last_end:
                pre_content = content[last_end : match.start()]
                pre_blocks = self._parse_text_blocks(pre_content, last_end)
                blocks.extend(pre_blocks)

            # Add code block
            blocks.append(
                ContentBlock(
                    content=match.group(),
                    block_type="code",
                    start_pos=match.start(),
                    end_pos=match.end(),
                    is_header=False,
                )
            )
            last_end = match.end()

        # Process remaining content after last code block
        if last_end < len(content):
            remaining = content[last_end:]
            remaining_blocks = self._parse_text_blocks(remaining, last_end)
            blocks.extend(remaining_blocks)

        return blocks

    def _parse_text_blocks(self, text: str, offset: int) -> List[ContentBlock]:
        """
        Parse non-code text into blocks (paragraphs, headers, lists, tables).

        CRITICAL: Tables are parsed as atomic units including header +
        separator + rows. This prevents table headers from being separated
        from their separators in overlap.

        Args:
            text: Text to parse
            offset: Starting offset in original content

        Returns:
            List of ContentBlock objects
        """
        blocks = []

        # Split by double newlines to get paragraphs
        parts = re.split(r"\n\s*\n", text)
        current_pos = offset

        for part in parts:
            part = part.strip()
            if not part:
                current_pos += 2  # Account for \n\n
                continue

            # Check if this is a table (must have header + separator + at least one row)
            # Tables are atomic - header, separator, and rows must stay together
            if self._is_table_block(part):
                block_type = "table"
                is_header = False
            elif part.startswith("#"):
                block_type = "header"
                is_header = True
            elif re.match(r"^[\-\*\+]\s", part) or re.match(r"^\d+\.\s", part):
                block_type = "list"
                is_header = False
            else:
                block_type = "paragraph"
                is_header = False

            # Find actual position in text
            part_start = text.find(part, current_pos - offset)
            if part_start >= 0:
                actual_start = offset + part_start
                actual_end = actual_start + len(part)
            else:
                actual_start = current_pos
                actual_end = current_pos + len(part)

            blocks.append(
                ContentBlock(
                    content=part,
                    block_type=block_type,
                    start_pos=actual_start,
                    end_pos=actual_end,
                    is_header=is_header,
                )
            )

            current_pos = actual_end + 2  # +2 for paragraph separator

        return blocks

    def _is_table_block(self, text: str) -> bool:
        """
        Check if text block is a valid markdown table.

        A valid table must have:
        1. Header row (| col1 | col2 |)
        2. Separator row (|---|---|)
        3. At least structure to be recognizable

        Args:
            text: Text block to check

        Returns:
            True if this is a valid table block
        """
        lines = text.strip().split("\n")
        if len(lines) < 2:
            return False

        # Check first line is table header (has pipes)
        first_line = lines[0].strip()
        if not (first_line.startswith("|") and first_line.endswith("|")):
            return False

        # Check second line is separator (|---|---|)
        second_line = lines[1].strip()
        if not re.match(r"^\|[\s:|-]+\|$", second_line):
            return False

        return True

    def _extract_block_aligned_overlap(
        self, chunk: Chunk, target_size: int
    ) -> Optional[str]:
        """
        Extract overlap aligned to block boundaries (no partial blocks).

        CRITICAL: This method does NOT fall back to character-based extraction.
        If no complete block fits within target_size, returns None.

        Args:
            chunk: Chunk to extract overlap from
            target_size: Target overlap size in characters

        Returns:
            Overlap text consisting of complete blocks, or None if no blocks fit
        """
        content = chunk.content
        if not content.strip():
            return None

        blocks = self._extract_blocks_from_content(content)
        if not blocks:
            return None

        # Collect blocks from end until we reach target size
        selected_blocks: List[ContentBlock] = []
        total_size = 0

        for block in reversed(blocks):
            block_size = block.size

            # Check if adding this block would exceed target
            # Allow some tolerance (1.2x) for the first block
            if total_size == 0:
                if block_size <= target_size * 1.2:
                    selected_blocks.insert(0, block)
                    total_size += block_size
                # If first block is too large, we can't include it
                # Don't fall back to character-based - return None
                else:
                    max_allowed = target_size * 1.2
                    logger.debug(
                        f"Block too large for overlap: {block_size} > {max_allowed}"
                    )
                    continue
            elif total_size + block_size + 2 <= target_size:  # +2 for separator
                selected_blocks.insert(0, block)
                total_size += block_size + 2
            else:
                break

        if not selected_blocks:
            logger.debug("No blocks fit within overlap target size")
            return None

        # Join selected blocks
        overlap_text = "\n\n".join(b.content for b in selected_blocks)
        return overlap_text.strip()

    def calculate_overlap_statistics(self, chunks: List[Chunk]) -> dict:
        """
        Calculate statistics about overlap in chunks.
        
        Note: This method is retained for backward compatibility but statistics
        are now based on presence of previous_content/next_content fields.

        Args:
            chunks: List of chunks to analyze

        Returns:
            Dictionary with overlap statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "chunks_with_overlap": 0,
                "avg_overlap_size": 0,
                "total_overlap_size": 0,
            }

        # Count chunks with context (either previous or next)
        chunks_with_context = 0
        overlap_sizes = []
        
        for chunk in chunks:
            prev = chunk.get_metadata("previous_content", "")
            next_ctx = chunk.get_metadata("next_content", "")
            
            if prev or next_ctx:
                chunks_with_context += 1
                # Sum both context sizes for this chunk
                overlap_sizes.append(len(prev) + len(next_ctx))

        if not overlap_sizes:
            return {
                "total_chunks": len(chunks),
                "chunks_with_overlap": 0,
                "avg_overlap_size": 0,
                "total_overlap_size": 0,
            }

        total_overlap = sum(overlap_sizes)

        return {
            "total_chunks": len(chunks),
            "chunks_with_overlap": chunks_with_context,
            "avg_overlap_size": (
                total_overlap / chunks_with_context if chunks_with_context else 0
            ),
            "total_overlap_size": total_overlap,
            "overlap_percentage": (chunks_with_context / len(chunks)) * 100,
        }
