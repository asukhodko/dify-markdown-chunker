"""
Code-aware chunking strategy.

This module implements the CodeAwareStrategy, which handles markdown documents
containing code blocks. It ensures code blocks are never split and maintains
the relationship between documentation and code.

Design Rationale:
- Code preservation: Code blocks never split (maintains functional integrity)
- Context awareness: Keeps related documentation with code
- Mixed content handling: Balances code and text appropriately
- Atomic blocks: Respects preserve_atomic_blocks configuration

This strategy consolidates v1.x Code and Mixed strategies into a single
unified approach that handles all code-containing documents.
"""

from typing import List, Tuple

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis, FencedBlock
from .base import BaseStrategy


class CodeAwareStrategy(BaseStrategy):
    """
    Code-aware chunking strategy.

    Handles documents containing code blocks by treating code as atomic units
    that must never be split. Maintains relationships between documentation
    and code blocks.

    Algorithm:
    1. Identify code blocks and their positions
    2. For each code block:
       - Extract preamble (documentation before code)
       - Include code block as atomic unit
       - Include postamble if fits within size
    3. Handle text-only sections between code blocks
    4. Apply intelligent merging when beneficial

    Unified approach handles both:
    - High code ratio (>30%): Primarily code documentation
    - Mixed content (<30%): Code examples within text

    Attributes:
        name: Strategy identifier "code_aware"
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize code-aware strategy.

        Args:
            config: Chunking configuration
        """
        super().__init__(config)

    @property
    def name(self) -> str:
        """Strategy name."""
        return "code_aware"

    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle content.

        CodeAwareStrategy activates when content contains code blocks.
        Uses code_threshold from config to determine if code is significant.

        Args:
            analysis: Content analysis results

        Returns:
            True if content contains code blocks
        """
        return analysis.code_block_count > 0

    def apply(self, text: str, analysis: ContentAnalysis) -> List[Chunk]:
        """
        Apply code-aware chunking strategy.

        Code blocks are treated as atomic units. Documentation is chunked
        to maintain context with related code.

        Args:
            text: Text to chunk
            analysis: Content analysis results

        Returns:
            List of chunks with code blocks preserved
        """
        if not analysis.code_blocks:
            return []

        # Sort code blocks by position
        sorted_blocks = sorted(analysis.code_blocks, key=lambda b: b.start_line)

        # Extract segments (code blocks with surrounding text)
        segments = self._extract_segments(text, sorted_blocks)

        # Process segments into chunks
        chunks = self._process_segments(segments, analysis)

        return chunks

    def _extract_segments(
        self, text: str, code_blocks: List[FencedBlock]
    ) -> List[Tuple[str, str, FencedBlock | None]]:
        """
        Extract segments from text.

        Each segment consists of:
        - Text before code block (preamble)
        - Code block (optional - can be text-only segment)
        - Text after code block (postamble)

        Args:
            text: Full text
            code_blocks: List of code blocks

        Returns:
            List of (preamble, postamble, code_block) tuples
        """
        lines = text.split("\n")
        segments: List[Tuple[str, str, FencedBlock | None]] = []

        current_line = 1

        for i, block in enumerate(code_blocks):
            # Extract preamble (text before code block)
            preamble = ""
            if current_line < block.start_line:
                preamble_lines = lines[current_line - 1 : block.start_line - 1]
                preamble = "\n".join(preamble_lines).strip()

            # Extract postamble (text after code block until next block)
            postamble = ""
            if i + 1 < len(code_blocks):
                next_block = code_blocks[i + 1]
                if block.end_line < next_block.start_line - 1:
                    postamble_lines = lines[block.end_line : next_block.start_line - 1]
                    postamble = "\n".join(postamble_lines).strip()
            else:
                # Last code block - postamble goes to end
                if block.end_line < len(lines):
                    postamble_lines = lines[block.end_line :]
                    postamble = "\n".join(postamble_lines).strip()

            segments.append((preamble, postamble, block))
            current_line = block.end_line + 1

        # Handle text before first code block
        if code_blocks and code_blocks[0].start_line > 1:
            first_block = code_blocks[0]
            prefix_lines = lines[: first_block.start_line - 1]
            prefix_text = "\n".join(prefix_lines).strip()
            if prefix_text:
                segments.insert(0, (prefix_text, "", None))

        return segments

    def _process_segments(
        self,
        segments: List[Tuple[str, str, FencedBlock | None]],
        analysis: ContentAnalysis,
    ) -> List[Chunk]:
        """
        Process segments into chunks.

        Decision logic:
        1. If segment has code block:
           - Try to include preamble + code + postamble in one chunk
           - If too large, split appropriately
        2. If segment is text-only:
           - Chunk as normal text
        3. Apply merging when beneficial

        Args:
            segments: List of (preamble, postamble, code_block) tuples
            analysis: Content analysis for strategy decisions

        Returns:
            List of chunks
        """
        chunks: List[Chunk] = []

        for preamble, postamble, code_block in segments:
            if code_block is None:
                # Text-only segment
                if preamble:
                    text_chunks = self._chunk_text(preamble, 1)
                    chunks.extend(text_chunks)
            else:
                # Segment with code block
                segment_chunks = self._process_code_segment(
                    preamble, code_block, postamble, analysis
                )
                chunks.extend(segment_chunks)

        # Apply intelligent merging
        if len(chunks) > 1:
            chunks = self._merge_small_chunks(chunks)

        return chunks

    def _process_code_segment(
        self,
        preamble: str,
        code_block: FencedBlock,
        postamble: str,
        analysis: ContentAnalysis,
    ) -> List[Chunk]:
        """
        Process a segment containing a code block.

        Strategy:
        1. Calculate combined size (preamble + code + postamble)
        2. If fits in chunk, create single chunk
        3. If too large, intelligently split

        Args:
            preamble: Text before code block
            code_block: The code block
            postamble: Text after code block
            analysis: Content analysis

        Returns:
            List of chunks for this segment
        """
        # Get code block content
        code_content = code_block.content
        code_size = len(code_content)

        # Calculate sizes
        preamble_size = len(preamble) if preamble else 0
        postamble_size = len(postamble) if postamble else 0

        # Try to create single chunk with all parts
        if self.config.extract_preamble and preamble:
            # Include preamble with code
            combined_size = preamble_size + code_size + 4  # +4 for separators

            if (
                postamble
                and combined_size + postamble_size + 2 <= self.config.max_chunk_size
            ):
                # All parts fit in one chunk
                return [self._create_combined_chunk(preamble, code_block, postamble)]
            elif combined_size <= self.config.max_chunk_size:
                # Preamble + code fit, postamble separate
                chunks = [self._create_combined_chunk(preamble, code_block, None)]
                if postamble:
                    chunks.extend(self._chunk_text(postamble, code_block.end_line + 1))
                return chunks
            else:
                # Preamble + code too large, split preamble
                chunks = []
                if preamble:
                    chunks.extend(
                        self._chunk_text(
                            preamble, code_block.start_line - preamble.count("\n") - 1
                        )
                    )
                chunks.append(self._create_code_chunk(code_block))
                if postamble:
                    chunks.extend(self._chunk_text(postamble, code_block.end_line + 1))
                return chunks
        else:
            # Don't include preamble with code
            chunks = []
            if preamble:
                chunks.extend(
                    self._chunk_text(
                        preamble, code_block.start_line - preamble.count("\n") - 1
                    )
                )

            # Add code chunk
            chunks.append(self._create_code_chunk(code_block))

            # Add postamble if present
            if postamble:
                chunks.extend(self._chunk_text(postamble, code_block.end_line + 1))

            return chunks

    def _create_code_chunk(self, code_block: FencedBlock) -> Chunk:
        """
        Create chunk containing only code block.

        Args:
            code_block: Code block to chunk

        Returns:
            Chunk containing code
        """
        return self._create_chunk(
            content=code_block.content,
            start_line=code_block.start_line,
            end_line=code_block.end_line,
            chunk_type="code",
            language=code_block.language,
            code_lines=code_block.content.count("\n") + 1,
        )

    def _create_combined_chunk(
        self, preamble: str, code_block: FencedBlock, postamble: str | None
    ) -> Chunk:
        """
        Create chunk combining preamble, code, and optionally postamble.

        Args:
            preamble: Text before code
            code_block: Code block
            postamble: Text after code (optional)

        Returns:
            Combined chunk
        """
        # Build combined content
        parts = []
        if preamble:
            parts.append(preamble)
        parts.append(code_block.content)
        if postamble:
            parts.append(postamble)

        content = "\n\n".join(parts)

        # Calculate line range
        preamble_lines = preamble.count("\n") + 1 if preamble else 0
        start_line = code_block.start_line - preamble_lines

        end_line = code_block.end_line
        if postamble:
            postamble_lines = postamble.count("\n") + 1
            end_line = code_block.end_line + postamble_lines

        return self._create_chunk(
            content=content,
            start_line=max(1, start_line),
            end_line=end_line,
            chunk_type="code_with_context",
            language=code_block.language,
            has_preamble=preamble is not None and len(preamble) > 0,
            has_postamble=postamble is not None,
        )

    def _chunk_text(self, text: str, start_line: int) -> List[Chunk]:
        """
        Chunk plain text (non-code content).

        Uses paragraph-based chunking for natural boundaries.

        Args:
            text: Text to chunk
            start_line: Starting line number

        Returns:
            List of text chunks
        """
        if not text.strip():
            return []

        paragraphs = self._split_by_paragraphs(text)
        chunks: List[Chunk] = []

        current_parts: List[str] = []
        current_size = 0
        current_line = start_line

        for paragraph in paragraphs:
            para_size = len(paragraph)
            para_lines = paragraph.count("\n") + 1

            # Check if adding paragraph would exceed size
            if (
                current_size + para_size + 2 > self.config.max_chunk_size
                and current_parts
            ):
                # Finalize current chunk
                chunk_content = "\n\n".join(current_parts)
                chunk_lines = chunk_content.count("\n") + 1

                chunk = self._create_chunk(
                    content=chunk_content,
                    start_line=current_line,
                    end_line=current_line + chunk_lines - 1,
                    chunk_type="text",
                )
                chunks.append(chunk)

                current_parts = []
                current_size = 0
                current_line += chunk_lines

            # Add paragraph
            current_parts.append(paragraph)
            current_size += para_size + 2

        # Finalize remaining
        if current_parts:
            chunk_content = "\n\n".join(current_parts)
            chunk_lines = chunk_content.count("\n") + 1

            chunk = self._create_chunk(
                content=chunk_content,
                start_line=current_line,
                end_line=current_line + chunk_lines - 1,
                chunk_type="text",
            )
            chunks.append(chunk)

        return chunks

    def _merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Merge consecutive small chunks when beneficial.

        Merges chunks that are below min_chunk_size and can be combined
        without exceeding max_chunk_size.

        Args:
            chunks: List of chunks

        Returns:
            List of chunks with small chunks merged
        """
        if not chunks:
            return chunks

        merged: List[Chunk] = []
        i = 0

        while i < len(chunks):
            current_chunk = chunks[i]
            current_size = len(current_chunk.content)

            # Check if current chunk is small
            if current_size < self.config.min_chunk_size and i + 1 < len(chunks):
                # Try to merge with next chunk
                next_chunk = chunks[i + 1]
                combined_size = current_size + len(next_chunk.content) + 2

                if combined_size <= self.config.max_chunk_size:
                    # Merge chunks
                    merged_content = current_chunk.content + "\n\n" + next_chunk.content
                    merged_chunk = self._create_chunk(
                        content=merged_content,
                        start_line=current_chunk.start_line,
                        end_line=next_chunk.end_line,
                        chunk_type="merged",
                        merged_count=2,
                    )
                    merged.append(merged_chunk)
                    i += 2  # Skip next chunk
                    continue

            # Can't merge, add as-is
            merged.append(current_chunk)
            i += 1

        return merged
