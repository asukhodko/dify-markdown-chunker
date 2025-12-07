"""
Base strategy class for markdown_chunker v2.
"""

from abc import ABC, abstractmethod
from typing import List

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis


class BaseStrategy(ABC):
    """
    Abstract base class for chunking strategies.

    All strategies must implement:
    - name: Strategy identifier
    - priority: Selection priority (1 = highest)
    - can_handle: Whether strategy can handle the document
    - apply: Apply strategy to produce chunks
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name identifier."""
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """Selection priority (1 = highest)."""
        pass

    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if this strategy can handle the document.

        Args:
            analysis: Document analysis results
            config: Chunking configuration

        Returns:
            True if strategy can handle the document
        """
        pass

    @abstractmethod
    def apply(
        self, md_text: str, analysis: ContentAnalysis, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply strategy to produce chunks.

        Args:
            md_text: Normalized markdown text
            analysis: Document analysis results
            config: Chunking configuration

        Returns:
            List of chunks
        """
        pass

    def _create_chunk(
        self, content: str, start_line: int, end_line: int, **metadata
    ) -> Chunk:
        """
        Create a chunk with strategy metadata.

        Args:
            content: Chunk content
            start_line: Starting line (1-indexed)
            end_line: Ending line (1-indexed)
            **metadata: Additional metadata

        Returns:
            Chunk instance
        """
        meta = {"strategy": self.name, **metadata}
        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata=meta,
        )

    def _set_oversize_metadata(
        self, chunk: Chunk, reason: str, config: ChunkConfig
    ) -> None:
        """
        Set metadata for oversize chunks.

        Called by strategy when creating a chunk that exceeds
        max_chunk_size for a valid reason (preserving atomic blocks).

        Args:
            chunk: Chunk to mark
            reason: Reason for oversize (code_block_integrity,
                table_integrity, section_integrity)
            config: Configuration for size check
        """
        VALID_REASONS = {"code_block_integrity", "table_integrity", "section_integrity"}

        if reason not in VALID_REASONS:
            raise ValueError(
                f"Invalid oversize_reason: {reason}. Must be one of {VALID_REASONS}"
            )

        if chunk.size > config.max_chunk_size:
            chunk.metadata["allow_oversize"] = True
            chunk.metadata["oversize_reason"] = reason

    def _ensure_fence_balance(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Ensure all chunks have balanced code fences.

        If a chunk has unbalanced fences, try to merge with adjacent chunk.
        If merge fails, mark with fence_balance_error.

        Args:
            chunks: List of chunks to check

        Returns:
            List of chunks with balanced fences (or error flags)
        """
        result = []
        i = 0

        while i < len(chunks):
            chunk = chunks[i]
            fence_count = chunk.content.count("```")

            if fence_count % 2 == 0:
                # Balanced - keep as is
                result.append(chunk)
                i += 1
            else:
                # Unbalanced - try to merge with next chunk
                if i + 1 < len(chunks):
                    merged_content = chunk.content + "\n" + chunks[i + 1].content
                    merged_fence_count = merged_content.count("```")

                    if merged_fence_count % 2 == 0:
                        # Merge restored balance
                        merged_chunk = self._create_chunk(
                            content=merged_content,
                            start_line=chunk.start_line,
                            end_line=chunks[i + 1].end_line,
                            merged_for_fence_balance=True,
                        )
                        result.append(merged_chunk)
                        i += 2
                        continue

                # Merge didn't help - mark error
                chunk.metadata["fence_balance_error"] = True
                chunk.metadata["fence_count"] = fence_count
                result.append(chunk)
                i += 1

        return result

    def _split_text_to_size(
        self, text: str, start_line: int, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Split text into chunks respecting size limits.

        Splits at paragraph boundaries when possible.

        Args:
            text: Text to split
            start_line: Starting line number
            config: Configuration

        Returns:
            List of chunks
        """
        if len(text) <= config.max_chunk_size:
            if text.strip():
                end_line = start_line + text.count("\n")
                return [self._create_chunk(text, start_line, end_line)]
            return []

        chunks = []
        paragraphs = text.split("\n\n")

        current_content = ""
        current_start = start_line
        current_line = start_line

        for para in paragraphs:
            para_with_sep = para + "\n\n" if para != paragraphs[-1] else para

            if len(current_content) + len(para_with_sep) <= config.max_chunk_size:
                current_content += para_with_sep
                current_line += para_with_sep.count("\n")
            else:
                # Save current chunk
                if current_content.strip():
                    chunks.append(
                        self._create_chunk(
                            current_content.rstrip(),
                            current_start,
                            current_line,
                        )
                    )

                # Start new chunk
                current_content = para_with_sep
                current_start = current_line + 1
                current_line = current_start + para_with_sep.count("\n")

        # Save last chunk
        if current_content.strip():
            chunks.append(
                self._create_chunk(
                    current_content.rstrip(),
                    current_start,
                    current_line,
                )
            )

        return chunks
