"""
OverlapManager - Manages overlap between adjacent chunks for continuity.
This component creates overlapping content between chunks to maintain context
and improve readability when chunks are processed independently.
"""

import re
from typing import List

from ..text_normalizer import truncate_at_word_boundary, validate_no_word_fragments
from ..types import Chunk, ChunkConfig


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

    def _extract_overlap(self, chunk: Chunk, is_suffix: bool = True) -> str:
        """
        Extract overlap text from a chunk.

        Args:
            chunk: Chunk to extract overlap from
            is_suffix: If True, extract from end; if False, from beginning

        Returns:
            Overlap text
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
        max_overlap = int(len(content) * 0.40)
        overlap_size = min(overlap_size, max_overlap)

        if overlap_size <= 0:
            return ""

        # Extract overlap text
        if is_suffix:
            # Extract from end
            overlap_text = self._extract_suffix_overlap(content, overlap_size)
        else:
            # Extract from beginning
            overlap_text = self._extract_prefix_overlap(content, overlap_size)

        return overlap_text

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
