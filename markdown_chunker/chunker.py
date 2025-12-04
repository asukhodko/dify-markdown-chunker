"""
Unified markdown chunker with 3-stage pipeline.

This module implements the main MarkdownChunker class, which orchestrates
the chunking process through a simplified 3-stage pipeline:

1. Stage 1: Parser - Single-pass analysis to extract content structure
2. Stage 2: Strategy Selection - Choose optimal strategy based on analysis
3. Stage 3: Post-Processing - Apply final adjustments (overlap, preamble, etc.)

Design Rationale:
- Single path: No dual mechanisms, one clear execution flow
- Strategy-driven: Automatic strategy selection based on content analysis
- Transparent: Each stage has clear inputs/outputs, easy to debug
- Extensible: New strategies can be added without changing pipeline

This consolidates v1.x's complex multi-path approach into a single,
predictable pipeline that always produces consistent results.
"""

import logging
from typing import List

from .config import ChunkConfig
from .parser import Parser
from .strategies import (
    BaseStrategy,
    CodeAwareStrategy,
    FallbackStrategy,
    StructuralStrategy,
    TableStrategy,
)
from .types import Chunk, ChunkingResult, ContentAnalysis

logger = logging.getLogger(__name__)


class MarkdownChunker:
    """
    Unified markdown chunker with 3-stage pipeline.

    Orchestrates the chunking process through three stages:
    1. Parser: Single-pass content analysis
    2. Strategy Selection: Choose optimal chunking approach
    3. Post-Processing: Apply final adjustments

    The chunker automatically selects the best strategy based on content
    characteristics, ensuring consistent and predictable results.

    Strategy Priority (first matching strategy wins):
    1. TableStrategy - When tables present (preserve integrity)
    2. CodeAwareStrategy - When code blocks present (preserve code)
    3. StructuralStrategy - When sufficient headers (semantic coherence)
    4. FallbackStrategy - Universal fallback (always succeeds)

    Attributes:
        config: Chunking configuration
        parser: Content parser
        strategies: List of available strategies (ordered by priority)

    Example:
        >>> chunker = MarkdownChunker()
        >>> result = chunker.chunk(markdown_text)
        >>> for chunk in result.chunks:
        ...     print(f"Chunk {chunk.start_line}-{chunk.end_line}: {len(chunk.content)} chars")
    """

    def __init__(self, config: ChunkConfig | None = None):
        """
        Initialize markdown chunker.

        Args:
            config: Chunking configuration. If None, uses default config.
        """
        self.config = config or ChunkConfig()
        self.parser = Parser()

        # Initialize strategies in priority order
        # Order matters: first matching strategy is used
        self.strategies: List[BaseStrategy] = [
            TableStrategy(self.config),  # Priority 1: Tables (preserve data integrity)
            CodeAwareStrategy(
                self.config
            ),  # Priority 2: Code (preserve functional blocks)
            StructuralStrategy(
                self.config
            ),  # Priority 3: Structure (semantic coherence)
            FallbackStrategy(self.config),  # Priority 4: Fallback (always succeeds)
        ]

        logger.debug(
            f"MarkdownChunker initialized with {len(self.strategies)} strategies"
        )

    def chunk(self, text: str) -> ChunkingResult:
        """
        Chunk markdown text using 3-stage pipeline.

        Stage 1: Parser - Analyze content structure
        Stage 2: Strategy Selection - Choose and apply optimal strategy
        Stage 3: Post-Processing - Apply final adjustments

        Args:
            text: Markdown text to chunk

        Returns:
            ChunkingResult containing chunks and metadata

        Raises:
            ValueError: If text is empty or invalid
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunker")
            return ChunkingResult(
                chunks=[],
                strategy_used="none",
                processing_time=0.0,
                metadata={"error": "empty_input"},
            )

        logger.debug(f"Starting chunking pipeline for {len(text)} character text")

        # Stage 1: Parser - Single-pass content analysis
        analysis = self._stage1_parse(text)

        # Stage 2: Strategy Selection - Choose and apply strategy
        chunks = self._stage2_select_and_apply(text, analysis)

        # Stage 3: Post-Processing - Apply final adjustments
        chunks = self._stage3_postprocess(chunks, text, analysis)

        # Build result
        result = ChunkingResult(
            chunks=chunks,
            strategy_used=self._get_strategy_name(analysis),
            processing_time=0.0,  # TODO: Track actual time
            metadata=self._build_metadata(analysis, chunks),
        )

        logger.info(
            f"Chunking complete: {result.chunk_count} chunks using {result.strategy_used} strategy"
        )

        return result

    def _stage1_parse(self, text: str) -> ContentAnalysis:
        """
        Stage 1: Parse content and extract structure.

        Single-pass analysis extracts all structural elements:
        - Headers (h1-h6)
        - Code blocks (fenced)
        - Tables
        - Content type and ratios

        Args:
            text: Markdown text

        Returns:
            ContentAnalysis with all structural information
        """
        logger.debug("Stage 1: Parsing content...")

        analysis = self.parser.analyze(text)

        logger.debug(
            f"Parse complete: type={analysis.content_type}, "
            f"headers={analysis.header_count}, "
            f"code_blocks={analysis.code_block_count}, "
            f"tables={analysis.table_count}"
        )

        return analysis

    def _stage2_select_and_apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Stage 2: Select optimal strategy and apply it.

        Iterates through strategies in priority order, selecting the first
        strategy that can handle the content. FallbackStrategy always
        succeeds, ensuring a result is always produced.

        Strategy Priority:
        1. TableStrategy - Preserves table integrity
        2. CodeAwareStrategy - Preserves code blocks
        3. StructuralStrategy - Maintains semantic sections
        4. FallbackStrategy - Universal fallback

        Args:
            text: Markdown text
            analysis: Content analysis from Stage 1

        Returns:
            List of chunks from selected strategy
        """
        logger.debug("Stage 2: Selecting strategy...")

        for strategy in self.strategies:
            if strategy.can_handle(analysis):
                logger.debug(f"Selected strategy: {strategy.name}")
                chunks = strategy.apply(text, analysis)
                logger.debug(f"Strategy produced {len(chunks)} chunks")
                return chunks

        # Should never reach here (FallbackStrategy always succeeds)
        logger.error("No strategy could handle content - this should not happen!")
        raise RuntimeError("Strategy selection failed - no strategy accepted content")

    def _stage3_postprocess(
        self, chunks: List[Chunk], text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Stage 3: Apply post-processing adjustments.

        Post-processing handles:
        - Validation of chunk properties
        - Filtering empty/invalid chunks
        - Final size adjustments
        - Metadata enrichment

        Note: Overlap is handled within strategies (applied during Stage 2)
        to maintain strategy-specific logic.

        Args:
            chunks: Chunks from Stage 2
            text: Original text
            analysis: Content analysis

        Returns:
            Post-processed chunks ready for output
        """
        logger.debug("Stage 3: Post-processing...")

        # Filter out invalid chunks
        valid_chunks = []
        for chunk in chunks:
            if self._is_valid_chunk(chunk):
                valid_chunks.append(chunk)
            else:
                logger.warning(
                    f"Filtered invalid chunk: lines {chunk.start_line}-{chunk.end_line}"
                )

        # Enrich metadata
        for i, chunk in enumerate(valid_chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["total_chunks"] = len(valid_chunks)

        logger.debug(f"Post-processing complete: {len(valid_chunks)} valid chunks")

        return valid_chunks

    def _is_valid_chunk(self, chunk: Chunk) -> bool:
        """
        Validate chunk meets basic requirements.

        A valid chunk must:
        - Have non-empty content
        - Have valid line numbers (start >= 1, end >= start)
        - Meet minimum size (unless atomic block with preserve_atomic_blocks=True)

        Args:
            chunk: Chunk to validate

        Returns:
            True if chunk is valid
        """
        # Check content
        if not chunk.content or not chunk.content.strip():
            return False

        # Check line numbers
        if chunk.start_line < 1 or chunk.end_line < chunk.start_line:
            return False

        # Check size (allow oversized atomic blocks)
        chunk_size = len(chunk.content)

        # Allow oversized chunks if config permits
        if chunk_size > self.config.max_chunk_size and not self.config.allow_oversize:
            # Check if it's an atomic block
            chunk_type = chunk.metadata.get("chunk_type", "")
            if chunk_type in ("code", "table") and self.config.preserve_atomic_blocks:
                # Allow oversized atomic blocks
                pass
            else:
                logger.warning(
                    f"Chunk exceeds max size: {chunk_size} > {self.config.max_chunk_size}"
                )
                return False

        return True

    def _get_strategy_name(self, analysis: ContentAnalysis) -> str:
        """
        Determine which strategy would be selected for given analysis.

        Args:
            analysis: Content analysis

        Returns:
            Name of strategy that would be selected
        """
        for strategy in self.strategies:
            if strategy.can_handle(analysis):
                return strategy.name
        return "unknown"

    def _build_metadata(self, analysis: ContentAnalysis, chunks: List[Chunk]) -> dict:
        """
        Build metadata for chunking result.

        Args:
            analysis: Content analysis
            chunks: Final chunks

        Returns:
            Metadata dictionary
        """
        return {
            "content_type": analysis.content_type,
            "code_ratio": analysis.code_ratio,
            "header_count": analysis.header_count,
            "code_block_count": analysis.code_block_count,
            "table_count": analysis.table_count,
            "avg_chunk_size": (
                sum(len(c.content) for c in chunks) // len(chunks) if chunks else 0
            ),
            "min_chunk_size": min(len(c.content) for c in chunks) if chunks else 0,
            "max_chunk_size": max(len(c.content) for c in chunks) if chunks else 0,
        }


def chunk_markdown(text: str, config: ChunkConfig | None = None) -> ChunkingResult:
    """
    Convenience function to chunk markdown text.

    This is the primary public API for simple use cases.

    Args:
        text: Markdown text to chunk
        config: Optional chunking configuration

    Returns:
        ChunkingResult containing chunks and metadata

    Example:
        >>> result = chunk_markdown("# Hello\\n\\nWorld")
        >>> print(f"Created {result.total_chunks} chunks")
    """
    chunker = MarkdownChunker(config)
    return chunker.chunk(text)
