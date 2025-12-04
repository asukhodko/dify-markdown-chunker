"""
Fallback chunking strategy.

This module implements the FallbackStrategy, which serves as the universal fallback
when other specialized strategies cannot handle the content. It uses sentence-based
chunking with paragraph boundaries for natural break points.

Design Rationale:
- Universal applicability: Always succeeds, handles any content type
- Sentence-aware: Breaks on sentence boundaries for readability
- Paragraph-aware: Respects paragraph boundaries when possible
- Size-adaptive: Handles both small and large content gracefully

This strategy consolidates v1.x Simple and Paragraph strategies into a single
robust fallback mechanism.
"""

from typing import List

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis
from .base import BaseStrategy


class FallbackStrategy(BaseStrategy):
    """
    Universal fallback chunking strategy.

    Uses sentence-based chunking with paragraph boundaries as natural break points.
    Always succeeds, making it suitable as the final fallback in the strategy chain.

    Algorithm:
    1. Split text into paragraphs
    2. For each paragraph:
       - If paragraph fits in chunk size, add as-is
       - If too large, split by sentences
       - If sentence too large, split by character (with word boundaries)
    3. Apply overlap between chunks

    Attributes:
        name: Strategy identifier "fallback"
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize fallback strategy.

        Args:
            config: Chunking configuration
        """
        super().__init__(config)

    @property
    def name(self) -> str:
        """Strategy name."""
        return "fallback"

    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle content.

        FallbackStrategy always returns True as it's the universal fallback.

        Args:
            analysis: Content analysis results

        Returns:
            Always True
        """
        return True

    def apply(self, text: str, analysis: ContentAnalysis) -> List[Chunk]:
        """
        Apply fallback chunking strategy.

        Uses sentence-based chunking with paragraph boundaries. Handles edge cases
        like oversized sentences gracefully.

        Args:
            text: Text to chunk
            analysis: Content analysis results

        Returns:
            List of chunks with overlap applied
        """
        if not text.strip():
            return []

        # Split into paragraphs first (respects natural boundaries)
        paragraphs = self._split_by_paragraphs(text)

        chunks: List[Chunk] = []
        current_chunk_parts: List[str] = []
        current_size = 0

        for paragraph in paragraphs:
            paragraph_size = len(paragraph)

            # If paragraph fits within target size
            if paragraph_size <= self.config.max_chunk_size:
                # Check if adding to current chunk would exceed size
                if (
                    current_size + paragraph_size + 2 > self.config.max_chunk_size
                    and current_chunk_parts
                ):
                    # Finalize current chunk
                    chunk_text = "\n\n".join(current_chunk_parts)
                    chunks.append(self._create_chunk_from_text(chunk_text, text))
                    current_chunk_parts = []
                    current_size = 0

                # Add paragraph to current chunk
                current_chunk_parts.append(paragraph)
                current_size += paragraph_size + 2  # +2 for \n\n separator

            else:
                # Paragraph too large, need to split further
                # First, finalize any current chunk
                if current_chunk_parts:
                    chunk_text = "\n\n".join(current_chunk_parts)
                    chunks.append(self._create_chunk_from_text(chunk_text, text))
                    current_chunk_parts = []
                    current_size = 0

                # Split large paragraph by sentences
                sentence_chunks = self._split_large_text(paragraph)
                chunks.extend(sentence_chunks)

        # Finalize remaining chunk
        if current_chunk_parts:
            chunk_text = "\n\n".join(current_chunk_parts)
            chunks.append(self._create_chunk_from_text(chunk_text, text))

        # Apply overlap between chunks
        chunks = self._apply_overlap(chunks, text)

        return chunks

    def _split_large_text(self, text: str) -> List[Chunk]:
        """
        Split large text that exceeds max_chunk_size.

        Uses sentence boundaries when possible, falls back to character-based
        splitting for very long sentences.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        sentences = self._split_by_sentences(text)
        chunks: List[Chunk] = []
        current_parts: List[str] = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # Handle oversized single sentence
            if sentence_size > self.config.max_chunk_size:
                # Finalize current chunk first
                if current_parts:
                    chunk_text = " ".join(current_parts)
                    chunks.append(self._create_chunk_from_text(chunk_text, text))
                    current_parts = []
                    current_size = 0

                # Split oversized sentence by words/characters
                if self.config.allow_oversize:
                    # Allow as single oversized chunk
                    chunks.append(self._create_chunk_from_text(sentence, text))
                else:
                    # Force split at character boundaries (word-aware)
                    word_chunks = self._split_by_words(sentence)
                    chunks.extend(word_chunks)

                continue

            # Check if adding sentence would exceed size
            if (
                current_size + sentence_size + 1 > self.config.max_chunk_size
                and current_parts
            ):
                # Finalize current chunk
                chunk_text = " ".join(current_parts)
                chunks.append(self._create_chunk_from_text(chunk_text, text))
                current_parts = []
                current_size = 0

            # Add sentence to current chunk
            current_parts.append(sentence)
            current_size += sentence_size + 1  # +1 for space separator

        # Finalize remaining chunk
        if current_parts:
            chunk_text = " ".join(current_parts)
            chunks.append(self._create_chunk_from_text(chunk_text, text))

        return chunks

    def _split_by_words(self, text: str) -> List[Chunk]:
        """
        Split text by words when sentence is too large.

        This is the last resort for extremely long sentences without punctuation.

        Args:
            text: Text to split

        Returns:
            List of chunks
        """
        words = text.split()
        chunks: List[Chunk] = []
        current_words: List[str] = []
        current_size = 0

        for word in words:
            word_size = len(word)

            # Check if adding word would exceed size
            if (
                current_size + word_size + 1 > self.config.max_chunk_size
                and current_words
            ):
                # Finalize current chunk
                chunk_text = " ".join(current_words)
                chunks.append(self._create_chunk_from_text(chunk_text, text))
                current_words = []
                current_size = 0

            # Add word to current chunk
            current_words.append(word)
            current_size += word_size + 1  # +1 for space

        # Finalize remaining chunk
        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append(self._create_chunk_from_text(chunk_text, text))

        return chunks

    def _create_chunk_from_text(self, chunk_text: str, original_text: str) -> Chunk:
        """
        Create chunk with calculated line numbers.

        Args:
            chunk_text: Chunk content
            original_text: Original full text

        Returns:
            Chunk with line numbers
        """
        start_line, end_line = self._calculate_line_numbers(chunk_text, original_text)
        return self._create_chunk(
            content=chunk_text,
            start_line=start_line,
            end_line=end_line,
            chunk_type="text",
        )

    def _apply_overlap(self, chunks: List[Chunk], original_text: str) -> List[Chunk]:
        """
        Apply overlap between consecutive chunks.

        Takes last N characters from previous chunk and prepends to next chunk.

        Args:
            chunks: List of chunks
            original_text: Original full text

        Returns:
            Chunks with overlap applied
        """
        if len(chunks) <= 1 or self.config.overlap_size == 0:
            return chunks

        overlapped_chunks: List[Chunk] = []

        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk - no overlap needed
                overlapped_chunks.append(chunk)
            else:
                # Get overlap from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = prev_chunk.content[-self.config.overlap_size :]

                # Prepend overlap to current chunk
                new_content = overlap_text + "\n" + chunk.content
                start_line, end_line = self._calculate_line_numbers(
                    new_content, original_text
                )

                overlapped_chunk = self._create_chunk(
                    content=new_content,
                    start_line=start_line,
                    end_line=end_line,
                    chunk_type=chunk.metadata.get("chunk_type", "text"),
                    has_overlap=True,
                )
                overlapped_chunks.append(overlapped_chunk)

        return overlapped_chunks
