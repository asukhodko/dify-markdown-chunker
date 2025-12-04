"""
Base strategy class with shared utilities.

All chunking strategies inherit from BaseStrategy and implement
can_handle() and apply() methods.
"""

import re
from abc import ABC, abstractmethod
from typing import List

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis


class BaseStrategy(ABC):
    """
    Base class for all chunking strategies.

    Provides shared utilities and defines the strategy interface.
    """

    def __init__(self, config: ChunkConfig) -> None:
        """
        Initialize strategy with configuration.

        Args:
            config: ChunkConfig instance
        """
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name used for identification and logging."""
        pass

    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle this content type.

        Args:
            analysis: Content analysis from parser

        Returns:
            True if strategy should be applied, False otherwise
        """
        pass

    @abstractmethod
    def apply(self, text: str, analysis: ContentAnalysis) -> List[Chunk]:
        """
        Apply strategy to chunk the text.

        Args:
            text: Original markdown text
            analysis: Content analysis from parser

        Returns:
            List of chunks
        """
        pass

    # Shared utility methods

    def _create_chunk(
        self, content: str, start_line: int, end_line: int, **metadata
    ) -> Chunk:
        """
        Create chunk with standard metadata.

        Args:
            content: Chunk content
            start_line: Starting line number (1-based)
            end_line: Ending line number (inclusive)
            **metadata: Additional metadata fields

        Returns:
            Chunk instance
        """
        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata={"strategy": self.name, **metadata},
        )

    def _is_within_size(self, text: str) -> bool:
        """
        Check if text fits within max_chunk_size.

        Args:
            text: Text to check

        Returns:
            True if text size <= max_chunk_size
        """
        return len(text) <= self.config.max_chunk_size

    def _split_by_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs (double newline separator).

        Args:
            text: Text to split

        Returns:
            List of paragraph strings
        """
        paragraphs = []
        for para in text.split("\n\n"):
            if para.strip():
                paragraphs.append(para)
        return paragraphs

    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.

        Args:
            text: Text to split

        Returns:
            List of sentence strings
        """
        # Simple sentence splitting on punctuation + whitespace
        sentences = re.split(r"(?<=[.!?])\s+", text)
        return [s for s in sentences if s.strip()]

    def _calculate_line_numbers(
        self, text: str, content: str, base_line: int = 1
    ) -> tuple[int, int]:
        """
        Calculate line numbers for content within text.

        Args:
            text: Full text
            content: Content substring
            base_line: Base line number offset

        Returns:
            Tuple of (start_line, end_line)
        """
        # Find position of content in text
        pos = text.find(content)
        if pos == -1:
            # Content not found, return safe defaults
            return base_line, base_line

        # Count newlines before content starts
        lines_before = text[:pos].count("\n")
        # Count newlines in content
        lines_in_content = content.count("\n")

        start_line = base_line + lines_before
        end_line = start_line + lines_in_content

        return start_line, end_line

    def _group_to_target_size(
        self, items: List[str], text: str, base_line: int = 1
    ) -> List[Chunk]:
        """
        Group text items to target chunk size.

        Args:
            items: List of text items (paragraphs, sentences)
            text: Original full text for line number calculation
            base_line: Base line number

        Returns:
            List of chunks
        """
        chunks = []
        current_group = []
        current_size = 0

        for item in items:
            item_size = len(item)

            # Check if adding this item would exceed max size
            if current_size + item_size > self.config.max_chunk_size:
                # Flush current group if not empty
                if current_group:
                    combined = "\n\n".join(current_group)
                    start_line, end_line = self._calculate_line_numbers(
                        text, combined, base_line
                    )
                    chunks.append(self._create_chunk(combined, start_line, end_line))
                    current_group = []
                    current_size = 0

                # Handle oversized single item
                if item_size > self.config.max_chunk_size:
                    if self.config.allow_oversize:
                        start_line, end_line = self._calculate_line_numbers(
                            text, item, base_line
                        )
                        chunks.append(
                            self._create_chunk(
                                item,
                                start_line,
                                end_line,
                                is_atomic=True,
                                allow_oversize=True,
                            )
                        )
                    else:
                        # Split oversized item by sentences
                        sentences = self._split_by_sentences(item)
                        chunks.extend(
                            self._group_to_target_size(sentences, text, base_line)
                        )
                else:
                    # Start new group with this item
                    current_group = [item]
                    current_size = item_size
            else:
                # Add to current group
                current_group.append(item)
                current_size += item_size + 2  # +2 for "\n\n" separator

        # Flush remaining group
        if current_group:
            combined = "\n\n".join(current_group)
            start_line, end_line = self._calculate_line_numbers(
                text, combined, base_line
            )
            chunks.append(self._create_chunk(combined, start_line, end_line))

        return chunks
