"""
Base strategy class for all chunking strategies.

This module defines the abstract interface that all chunking strategies
must implement, ensuring consistent behavior across different approaches.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from markdown_chunker.parser.types import ContentAnalysis, Stage1Results

from ..types import Chunk, ChunkConfig, StrategyMetrics


class BaseStrategy(ABC):
    """
    Abstract base class for all chunking strategies.

    Each strategy implements a specific approach to chunking Markdown content
    based on the document's characteristics (code-heavy, list-heavy, etc.).

    All strategies must implement:
    - can_handle(): Check if strategy is applicable to the content
    - apply(): Apply the strategy to create chunks
    - calculate_quality(): Calculate quality score for strategy selection
    - priority: Strategy priority (1=highest, 6=lowest)
    - name: Human-readable strategy name
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the strategy."""

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Strategy priority for selection (1=highest, 6=lowest).

        Lower numbers indicate higher priority. When multiple strategies
        can handle content, the one with the lowest priority number is preferred.
        """

    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if this strategy can handle the given content.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            True if strategy can handle the content, False otherwise
        """

    @abstractmethod
    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for this strategy given the content.

        Quality score indicates how well-suited this strategy is for
        the content, independent of whether it can handle it.

        Args:
            analysis: Content analysis from Stage 1

        Returns:
            Quality score between 0.0 and 1.0 (higher is better)
        """

    @abstractmethod
    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply the strategy to create chunks from the content.

        This is the main method that implements the chunking logic
        specific to this strategy.

        Args:
            content: Original Markdown content
            stage1_results: Complete results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by this strategy

        Raises:
            StrategyError: If strategy cannot process the content
        """

    def get_metrics(
        self, analysis: ContentAnalysis, config: ChunkConfig
    ) -> StrategyMetrics:
        """
        Get comprehensive metrics for this strategy.

        Args:
            analysis: Content analysis from Stage 1
            config: Chunking configuration

        Returns:
            StrategyMetrics with all relevant information
        """
        can_handle = self.can_handle(analysis, config)
        quality_score = self.calculate_quality(analysis) if can_handle else 0.0

        # Calculate final score combining priority and quality
        priority_weight = 1.0 / self.priority  # Higher priority=higher weight
        final_score = (
            (priority_weight * 0.5) + (quality_score * 0.5) if can_handle else 0.0
        )

        reason = self._get_selection_reason(analysis, can_handle)

        return StrategyMetrics(
            strategy_name=self.name,
            can_handle=can_handle,
            quality_score=quality_score,
            priority=self.priority,
            final_score=final_score,
            reason=reason,
        )

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """
        Get human-readable reason for strategy selection decision.

        Args:
            analysis: Content analysis from Stage 1
            can_handle: Whether strategy can handle the content

        Returns:
            Explanation of why strategy was/wasn't selected
        """
        if can_handle:
            return f"{self.name} can handle this content type"
        else:
            return f"{self.name} cannot handle this content type"

    def _create_chunk(
        self,
        content: str,
        start_line: int,
        end_line: int,
        content_type: str = "text",
        **metadata,
    ) -> Chunk:
        """
        Helper method to create a chunk with standard metadata.

        Args:
            content: Chunk content
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based)
            content_type: Type of content (code, text, list, etc.)
            **metadata: Additional metadata fields

        Returns:
            Chunk with standard and custom metadata
        """
        chunk_metadata = {
            "strategy": self.name,
            "content_type": content_type,
            "size_bytes": len(content),
            **metadata,
        }

        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata=chunk_metadata,
        )

    def _validate_chunks(self, chunks: List[Chunk], config: ChunkConfig) -> List[Chunk]:
        """
        Validate and potentially fix chunks created by the strategy.

        Args:
            chunks: List of chunks to validate
            config: Chunking configuration

        Returns:
            Validated (and potentially corrected) chunks
        """
        validated_chunks = []

        for chunk in chunks:
            # Skip empty chunks
            if not chunk.content.strip():
                continue

            # Handle oversized chunks
            if chunk.size > config.max_chunk_size:
                if config.allow_oversize:
                    # Mark as oversize but allow
                    chunk.add_metadata("allow_oversize", True)
                    chunk.add_metadata(
                        "size_warning",
                        f"Chunk size {chunk.size} exceeds "
                        f"limit {config.max_chunk_size}",
                    )
                    validated_chunks.append(chunk)
                else:
                    # Try to split the chunk if it contains atomic elements
                    if self._contains_atomic_element(chunk.content):
                        # Mark as oversize because it contains atomic element
                        chunk.add_metadata("allow_oversize", True)
                        chunk.add_metadata(
                            "size_warning",
                            f"Chunk contains atomic element, "
                            f"size {chunk.size} exceeds limit "
                            f"{config.max_chunk_size}",
                        )
                        validated_chunks.append(chunk)
                    else:
                        # Non-atomic oversized chunk - enforce split (CRIT-1 fix)
                        from ..size_enforcer import split_oversized_chunk

                        split_chunks = split_oversized_chunk(chunk, config)
                        validated_chunks.extend(split_chunks)
            else:
                validated_chunks.append(chunk)

        # Ensure required metadata is present
        for chunk in validated_chunks:
            if "strategy" not in chunk.metadata:
                chunk.add_metadata("strategy", self.name)
            if "content_type" not in chunk.metadata:
                chunk.add_metadata("content_type", "text")

        # CRITICAL FIX: Validate code fence balance (Phase 1.1)
        # Prevent atomic code blocks from being split across chunks
        validated_chunks = self._validate_code_fence_balance(validated_chunks, config)

        return validated_chunks

    def _contains_atomic_element(self, content: str) -> bool:
        """
        Check if content contains atomic elements (code blocks, tables).

        Args:
            content: Content to check

        Returns:
            True if content contains atomic elements
        """
        # Check for code blocks
        if "```" in content:
            return True
        # Check for tables (simple heuristic)
        if "|" in content and "---" in content:
            return True
        return False

    def _validate_code_fence_balance(self, chunks: List[Chunk], config) -> List[Chunk]:
        """
        Validate that no chunk has unbalanced code fences.

        This is a critical validation to prevent code blocks from being
        split across chunk boundaries, which would corrupt the content.

        Args:
            chunks: List of chunks to validate
            config: Chunk configuration

        Returns:
            List of validated chunks (same as input if all valid)
        """
        for i, chunk in enumerate(chunks):
            fence_count = chunk.content.count("```")

            # Unbalanced fences indicate a split code block
            if fence_count % 2 != 0:
                # Log the error for debugging
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Chunk {i} has unbalanced code fences ({fence_count}). "
                    f"Code blocks should never be split. "
                    f"Strategy: {self.name}, Size: {chunk.size}"
                )

                # Mark chunk as having fence balance issue
                chunk.add_metadata("fence_balance_error", True)
                chunk.add_metadata("fence_count", fence_count)

        return chunks

    # ========================================================================
    # Semantic Boundary Splitting Utilities (Requirements 4.1, 4.2, 4.3)
    # ========================================================================

    def _split_at_boundary(self, content: str, max_size: int) -> List[str]:
        """
        Split content at semantic boundaries (paragraph > sentence > word).

        IMPORTANT: Strategies MUST NOT pass content slices to this method that
        cut through atomic elements; splitting at semantic boundaries applies
        only within non-atomic blocks.

        Args:
            content: Content to split
            max_size: Maximum size for each part

        Returns:
            List of content parts split at semantic boundaries
        """
        if len(content) <= max_size:
            return [content]

        parts = []
        remaining = content

        while remaining:
            if len(remaining) <= max_size:
                parts.append(remaining)
                break

            # Try to find paragraph boundary
            split_pos = self._find_paragraph_boundary(remaining, max_size)

            # Fall back to sentence boundary
            if split_pos <= 0:
                split_pos = self._find_sentence_boundary(remaining, max_size)

            # Fall back to word boundary
            if split_pos <= 0:
                split_pos = self._find_word_boundary(remaining, max_size)

            # Last resort: hard split (should never happen)
            if split_pos <= 0:
                split_pos = max_size

            parts.append(remaining[:split_pos].rstrip())
            remaining = remaining[split_pos:].lstrip()

        return parts

    def _find_paragraph_boundary(self, content: str, max_pos: int) -> int:
        """
        Find last paragraph boundary before max_pos.

        Args:
            content: Content to search
            max_pos: Maximum position to search up to

        Returns:
            Position of paragraph boundary, or -1 if not found
        """
        # Look for double newline
        pos = content.rfind("\n\n", 0, max_pos)
        return pos + 2 if pos > 0 else -1

    def _find_sentence_boundary(self, content: str, max_pos: int) -> int:
        """
        Find last sentence boundary before max_pos.

        Args:
            content: Content to search
            max_pos: Maximum position to search up to

        Returns:
            Position of sentence boundary, or -1 if not found
        """
        # Look for sentence-ending punctuation followed by space
        import re

        matches = list(re.finditer(r"[.!?]+\s+", content[:max_pos]))
        if matches:
            return matches[-1].end()
        return -1

    def _find_word_boundary(self, content: str, max_pos: int) -> int:
        """
        Find last word boundary before max_pos.

        Args:
            content: Content to search
            max_pos: Maximum position to search up to

        Returns:
            Position of word boundary, or -1 if not found
        """
        # Look for whitespace
        pos = content.rfind(" ", 0, max_pos)
        return pos + 1 if pos > 0 else -1

    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.name} (priority: {self.priority})"

    def __repr__(self) -> str:
        """Detailed string representation of the strategy."""
        return (
            f"{self.__class__.__name__}(name='{self.name}', priority={self.priority})"
        )


class StrategyError(Exception):
    """Exception raised when a strategy cannot process content."""

    def __init__(
        self,
        strategy_name: str,
        message: str,
        original_error: Optional[Exception] = None,
    ):
        self.strategy_name = strategy_name
        self.original_error = original_error
        super().__init__(f"{strategy_name}: {message}")


class StrategyConfigError(StrategyError):
    """Exception raised when strategy configuration is invalid."""


class StrategyContentError(StrategyError):
    """Exception raised when strategy cannot handle the content structure."""
