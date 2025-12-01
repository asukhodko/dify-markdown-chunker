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

    def apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Apply overlap to a list of chunks.

        Args:
            chunks: List of chunks to process

        Returns:
            List of chunks with overlap applied
        """
        if not chunks or len(chunks) < 2:
            # No overlap needed for single chunk or empty list
            return chunks

        if not self.config.enable_overlap:
            # Overlap disabled
            return chunks

        overlapped_chunks = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk - no prefix overlap
                overlapped_chunks.append(chunk)
            else:
                # Add overlap from previous chunk
                previous_chunk = chunks[i - 1]

                overlap_text = self._extract_overlap(previous_chunk, is_suffix=True)

                if overlap_text:
                    # Verify overlap doesn't contain unbalanced code fences
                    if self._has_unbalanced_fences(overlap_text):
                        # Skip overlap to preserve code block integrity
                        overlapped_chunks.append(chunk)
                    else:
                        # Create new chunk with overlap prefix
                        new_chunk = self._add_overlap_prefix(chunk, overlap_text)
                        overlapped_chunks.append(new_chunk)
                else:
                    overlapped_chunks.append(chunk)

        return overlapped_chunks

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

    def _extract_overlap(self, chunk: Chunk, is_suffix: bool = True) -> str:
        """
        Extract overlap text from a chunk using block-aware extraction.

        CRITICAL FIX: Uses block-aligned extraction to prevent data loss
        and excessive duplication. Does NOT fall back to character-based
        extraction - if no blocks fit, returns empty string with warning.

        Args:
            chunk: Chunk to extract overlap from
            is_suffix: If True, extract from end; if False, from beginning

        Returns:
            Overlap text (complete blocks only), or empty string if no blocks fit
        """
        content = chunk.content

        if not content.strip():
            return ""

        # Calculate overlap size - prefer fixed size if specified,
        # otherwise use percentage
        if self.config.overlap_size > 0:
            # Fixed-size overlap takes priority
            overlap_size = self.config.overlap_size
        elif self.config.overlap_percentage > 0:
            # Percentage-based overlap as fallback
            overlap_size = int(len(content) * self.config.overlap_percentage)
        else:
            # No overlap configured
            return ""

        # CRITICAL: Ensure overlap doesn't exceed 40% of source chunk size
        # This prevents overlap from dominating the chunk content
        # The final check in _add_overlap_prefix ensures the ratio stays under 50%
        # But allow minimum of 50 chars for small chunks to enable block-aligned overlap
        max_overlap = max(50, int(len(content) * 0.40))
        overlap_size = min(overlap_size, max_overlap)

        if overlap_size <= 0:
            return ""

        # CRITICAL FIX: Use block-aligned extraction
        # This prevents partial blocks in overlap which causes data loss/duplication
        if is_suffix:
            overlap_text = self._extract_block_aligned_overlap(chunk, overlap_size)

            if overlap_text is None:
                # No blocks fit - set overlap to 0 (no char-based fallback!)
                logger.warning(
                    f"Block-aligned overlap failed: no complete blocks fit within "
                    f"{overlap_size} chars. Setting overlap to 0 for this boundary."
                )
                return ""

            return overlap_text
        else:
            # For prefix extraction, use legacy method (less common case)
            return self._extract_prefix_overlap(content, overlap_size)

    def _extract_suffix_overlap(self, content: str, target_size: int) -> str:
        """
        Extract overlap from the end of content, preserving sentence boundaries.

        Args:
            content: Content to extract from
            target_size: Target overlap size

        Returns:
            Overlap text from end
        """
        if len(content) <= target_size:
            return content

        # Find sentence boundaries
        sentences = self._split_into_sentences(content)

        if not sentences:
            # No sentences found, use word boundary extraction from end
            return truncate_at_word_boundary(content, target_size, from_end=True)

        # Collect sentences from end until we reach target size
        overlap_sentences: List[str] = []
        current_size = 0

        for sentence in reversed(sentences):
            sentence_size = len(sentence)

            # Only add first sentence unconditionally if it fits within target
            # Otherwise, stop to avoid exceeding the limit
            if current_size + sentence_size <= target_size:
                overlap_sentences.insert(0, sentence)
                current_size += sentence_size
            elif not overlap_sentences and sentence_size <= target_size * 1.5:
                # Allow first sentence with some tolerance
                overlap_sentences.insert(0, sentence)
                current_size += sentence_size
                break  # Stop after first sentence if it exceeds target
            else:
                break

        result = "".join(overlap_sentences).strip()

        # Final safety check: truncate if still too large using word boundary
        if len(result) > target_size * 1.5:
            result = truncate_at_word_boundary(result, target_size, from_end=True)

        return result

    def _extract_prefix_overlap(self, content: str, target_size: int) -> str:
        """
        Extract overlap from the beginning of content, preserving sentence boundaries.

        Args:
            content: Content to extract from
            target_size: Target overlap size

        Returns:
            Overlap text from beginning
        """
        if len(content) <= target_size:
            return content

        # Find sentence boundaries
        sentences = self._split_into_sentences(content)

        if not sentences:
            # No sentences found, use word boundary extraction
            return truncate_at_word_boundary(content, target_size, from_end=False)

        # Collect sentences from beginning until we reach target size
        overlap_sentences: List[str] = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            if current_size + sentence_size <= target_size or not overlap_sentences:
                overlap_sentences.append(sentence)
                current_size += sentence_size
            else:
                break

        return "".join(overlap_sentences).strip()

    def _truncate_preserving_sentences(self, text: str, max_size: int) -> str:
        """
        Truncate text while trying to preserve sentence boundaries.

        Args:
            text: Text to truncate
            max_size: Maximum size

        Returns:
            Truncated text, preferably ending at sentence boundary
        """
        text = text.strip()

        if len(text) <= max_size:
            return text

        # If text already ends with sentence punctuation and is close to max_size,
        # allow a tolerance to preserve the sentence boundary (up to 50% over)
        if text[-1] in ".!?" and len(text) <= max_size * 1.5:
            return text

        # Try to find a sentence boundary within the text
        # Search the entire text for sentence boundaries
        best_boundary = -1
        for i in range(len(text) - 1, -1, -1):
            if text[i] in ".!?":
                # Found a sentence boundary
                candidate_len = i + 1
                # Prefer boundaries closer to max_size but allow up to 50% over
                if candidate_len <= max_size * 1.5:
                    best_boundary = i
                    break

        if best_boundary >= 0:
            return text[: best_boundary + 1].strip()

        # No good sentence boundary found, use word boundary truncation
        # This prevents BLOCK-2 (word splitting at chunk boundaries)
        result = truncate_at_word_boundary(text, max_size, from_end=False)

        # Validate no word fragments remain
        if not validate_no_word_fragments(result):
            # If validation fails, try from the opposite end
            result = truncate_at_word_boundary(text, max_size, from_end=True)

        return result

    def _split_into_sentences(self, content: str) -> List[str]:
        """
        Split content into sentences.

        Args:
            content: Content to split

        Returns:
            List of sentences (empty list if no sentence boundaries found)
        """
        # Check if content has sentence boundaries
        if not re.search(self.SENTENCE_END_PATTERN, content):
            # No sentence boundaries found - return empty to trigger
            # character-based extraction
            return []

        # Reconstruct sentences with their punctuation
        result = []
        parts = re.split(f"({self.SENTENCE_END_PATTERN})", content)

        current_sentence = ""
        for part in parts:
            current_sentence += part
            if re.match(self.SENTENCE_END_PATTERN, part):
                result.append(current_sentence)
                current_sentence = ""

        # Add any remaining content
        if current_sentence.strip():
            result.append(current_sentence)

        return [s for s in result if s.strip()]

    def _add_overlap_prefix(self, chunk: Chunk, overlap_text: str) -> Chunk:
        """
        Add overlap prefix to a chunk.

        Args:
            chunk: Original chunk
            overlap_text: Overlap text to add

        Returns:
            New chunk with overlap prefix
        """
        chunk_content_size = len(chunk.content)

        # CRITICAL: Ensure overlap doesn't exceed 50% of the resulting chunk
        # If overlap = X and content = Y, then ratio = X / (X + Y + 2)
        # We want X / (X + Y + 2) <= 0.5
        # Solving: X <= 0.5 * (X + Y + 2) => X <= 0.5X + 0.5Y + 1
        # => 0.5X <= 0.5Y + 1 => X <= Y + 2
        # But to be safe and account for "\n\n", we use X <= 0.45 * Y
        max_overlap_for_ratio = int(chunk_content_size * 0.45)

        if len(overlap_text) > max_overlap_for_ratio:
            # Truncate but try to preserve sentence boundaries
            overlap_text = self._truncate_preserving_sentences(
                overlap_text, max_overlap_for_ratio
            )

        if not overlap_text:
            return chunk

        # CRITICAL: Strict size compliance check
        # Calculate potential size AFTER applying overlap
        potential_size = len(overlap_text) + 2 + chunk_content_size  # +2 for "\n\n"

        if potential_size > self.config.max_chunk_size:
            # Calculate how much overlap we can add without exceeding max_chunk_size
            available_space = self.config.max_chunk_size - chunk_content_size - 2

            if available_space <= 0:
                # No space for overlap - return original chunk
                return chunk

            # Truncate overlap to fit within available space
            # Also respect the 50% ratio limit
            max_allowed = min(available_space, max_overlap_for_ratio)

            # Ensure we don't exceed available space even after sentence truncation
            if max_allowed > 0:
                overlap_text = self._truncate_preserving_sentences(
                    overlap_text, max_allowed
                )

                # Final safety check - if truncated overlap still too big,
                # use word boundary truncation
                if len(overlap_text) > available_space:
                    overlap_text = truncate_at_word_boundary(
                        overlap_text, available_space, from_end=False
                    )
            else:
                overlap_text = ""

            if not overlap_text:
                # No meaningful overlap left - return original chunk
                return chunk

        # Create new content with overlap
        new_content = overlap_text + "\n\n" + chunk.content

        # CRITICAL: Check if adding overlap creates unbalanced code fences
        # This can happen when overlap contains part of a code block
        if self._has_unbalanced_fences(new_content):
            # Adding this overlap would break code block integrity
            # Return original chunk without overlap
            return chunk

        # Create new chunk with updated content and metadata
        new_metadata = chunk.metadata.copy()
        new_metadata["has_overlap"] = True
        new_metadata["overlap_size"] = len(overlap_text)
        new_metadata["overlap_type"] = "prefix"

        new_chunk = Chunk(
            content=new_content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            metadata=new_metadata,
        )

        return new_chunk

    def calculate_overlap_statistics(self, chunks: List[Chunk]) -> dict:
        """
        Calculate statistics about overlap in chunks.

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

        chunks_with_overlap = [
            c for c in chunks if c.get_metadata("has_overlap", False)
        ]

        if not chunks_with_overlap:
            return {
                "total_chunks": len(chunks),
                "chunks_with_overlap": 0,
                "avg_overlap_size": 0,
                "total_overlap_size": 0,
            }

        overlap_sizes = [c.get_metadata("overlap_size", 0) for c in chunks_with_overlap]
        total_overlap = sum(overlap_sizes)

        return {
            "total_chunks": len(chunks),
            "chunks_with_overlap": len(chunks_with_overlap),
            "avg_overlap_size": (
                total_overlap / len(chunks_with_overlap) if chunks_with_overlap else 0
            ),
            "total_overlap_size": total_overlap,
            "overlap_percentage": (len(chunks_with_overlap) / len(chunks)) * 100,
        }
