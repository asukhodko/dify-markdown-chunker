"""
SentencesStrategy - Universal fallback chunking strategy.

This strategy provides a reliable fallback for any type of content by
splitting text into sentences and grouping them into appropriately sized chunks.

Algorithm Documentation:
    - Sentences Strategy: docs/markdown-extractor/03-strategies/sentences-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import re
from typing import List

from markdown_chunker.parser.types import ContentAnalysis, Stage1Results

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy


class SentencesStrategy(BaseStrategy):
    """
    Universal fallback strategy that splits content by sentences.

    This strategy:
    - Always can handle any content (universal fallback)
    - Splits text into sentences using regex patterns
    - Groups sentences into chunks respecting size limits
    - Preserves paragraph boundaries when possible
    - Provides reliable, predictable chunking for any content type

    Priority: 6 (lowest - fallback strategy)
    """

    # Sentence boundary patterns
    SENTENCE_PATTERNS = [
        # Standard sentence endings with space/newline after
        r"([.!?]+)\s+(?=[A-ZА-Я])",
        # Sentence endings at end of line
        r"([.!?]+)$",
        # Sentence endings before quotes
        r'([.!?]+)(?=\s*["\'])',
    ]

    # Compiled regex for performance
    _sentence_regex = None

    @property
    def name(self) -> str:
        """Strategy name."""
        return "sentences"

    @property
    def priority(self) -> int:
        """Lowest priority (fallback strategy)."""
        return 6

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Always can handle any content (universal fallback).

        Args:
            analysis: Content analysis (not used)
            config: Configuration (not used)

        Returns:
            Always True - this strategy can handle any content

        Examples:
            >>> strategy=SentencesStrategy()
            >>> print(strategy.can_handle(any_analysis, any_config))
            True
        """
        return True

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for sentences strategy.

        Quality is lower for structured content that would benefit
        from specialized strategies, higher for simple text.

        Scoring:
        - Base: 0.3 (universal applicability)
        - Penalties: code (-0.1), headers (-0.1), lists (-0.05), tables (-0.05)
        - Bonuses: high text ratio (+0.2), low complexity (+0.1)

        Args:
            analysis: Content analysis from Stage 1

        Returns:
            Quality score between 0.0 and 1.0

        Examples:
            >>> # Simple text document
            >>> analysis=ContentAnalysis(
            ...     text_ratio=0.9,
            ...     complexity_score=0.1,
            ...     code_ratio=0.0,
            ...     header_count=0,
            ...     ...
            ... )
            >>> strategy=SentencesStrategy()
            >>> score=strategy.calculate_quality(analysis)
            >>> print(f"{score:.2f}")  # 0.3 + 0.2 + 0.1=0.6
            0.60
        """
        score = 0.3  # Base score for universal applicability

        # Lower quality for structured content
        if analysis.code_ratio > 0.1:
            score -= 0.1
        if analysis.get_total_header_count() > 3:
            score -= 0.1
        if analysis.list_count > 2:
            score -= 0.05
        if analysis.table_count > 0:
            score -= 0.05

        # Higher quality for simple text
        if analysis.text_ratio > 0.8:
            score += 0.2
        if analysis.complexity_score < 0.2:
            score += 0.1

        return max(0.0, min(1.0, score))

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply sentences strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by sentence-based splitting
        """
        if not content.strip():
            return []

        # Split content into paragraphs first
        paragraphs = self._split_into_paragraphs(content)

        chunks = []
        current_chunk_content = ""
        current_start_line = 1
        current_line = 1

        for paragraph in paragraphs:
            if not paragraph.strip():
                current_line += 1
                continue

            # FIX: Check if this is structured content (header, list, table)
            is_structured = self._is_structured_content(paragraph)

            if is_structured:
                # Keep structured content intact, don't split into sentences
                # Check if adding this paragraph would exceed chunk size
                potential_content = current_chunk_content
                if potential_content:
                    potential_content += "\n\n" + paragraph
                else:
                    potential_content = paragraph

                if (
                    len(potential_content) > config.max_chunk_size
                    and current_chunk_content
                ):
                    # Create chunk with current content
                    chunk = self._create_chunk(
                        content=current_chunk_content,
                        start_line=current_start_line,
                        end_line=current_line - 1,
                        content_type="text",
                        sentence_based=True,
                        sentences_per_chunk=len(
                            self._split_into_sentences(current_chunk_content)
                        ),
                    )
                    chunks.append(chunk)

                    # Start new chunk with this paragraph
                    current_chunk_content = paragraph
                    current_start_line = current_line
                else:
                    # Add paragraph to current chunk
                    if current_chunk_content:
                        current_chunk_content += "\n\n" + paragraph
                    else:
                        current_chunk_content = paragraph
                        current_start_line = current_line

                # Update line counter
                current_line += paragraph.count("\n") + 1
            else:
                # Regular text - split into sentences
                sentences = self._split_into_sentences(paragraph)

                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue

                    # Check if adding this sentence would exceed chunk size
                    potential_content = current_chunk_content
                    if potential_content:
                        potential_content += " " + sentence
                    else:
                        potential_content = sentence

                    if (
                        len(potential_content) > config.max_chunk_size
                        and current_chunk_content
                    ):
                        # Create chunk with current content
                        chunk = self._create_chunk(
                            content=current_chunk_content,
                            start_line=current_start_line,
                            end_line=current_line - 1,
                            content_type="text",
                            sentence_based=True,
                            sentences_per_chunk=len(
                                self._split_into_sentences(current_chunk_content)
                            ),
                        )
                        chunks.append(chunk)

                        # Start new chunk
                        current_chunk_content = sentence
                        current_start_line = current_line
                    else:
                        # Add sentence to current chunk
                        if current_chunk_content:
                            current_chunk_content += " " + sentence
                        else:
                            current_chunk_content = sentence
                            current_start_line = current_line

                    # Estimate line increment (rough approximation)
                    current_line += sentence.count("\n") + 1

        # Add final chunk if there's remaining content
        if current_chunk_content.strip():
            chunk = self._create_chunk(
                content=current_chunk_content,
                start_line=current_start_line,
                end_line=current_line,
                content_type="text",
                sentence_based=True,
                sentences_per_chunk=len(
                    self._split_into_sentences(current_chunk_content)
                ),
            )
            chunks.append(chunk)

        return self._validate_chunks(chunks, config)

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """
        Split content into paragraphs.

        FIX: Preserves markdown structure (headers, lists, tables)
        instead of merging everything into sentences.

        Args:
            content: Text content to split

        Returns:
            List of paragraph strings (preserving markdown structure)
        """
        # FIX: Split by lines and group related content together
        lines = content.split("\n")
        paragraphs = []
        current_para = []
        in_list = False
        in_table = False

        for line in lines:
            stripped = line.strip()

            # Check if this is a header
            is_header = bool(re.match(r"^#{1,6}\s+", stripped))

            # Check if this is a list item
            is_list = bool(re.match(r"^(\s*)([-*+]|\d+\.)\s+", stripped))

            # Check if this is a table row
            is_table = bool(re.match(r"^\|.*\|$", stripped))

            # Empty line - might be paragraph boundary
            if not stripped:
                if current_para and not in_list and not in_table:
                    # End current paragraph
                    paragraphs.append("\n".join(current_para))
                    current_para = []
                elif current_para:
                    # Keep empty line in structured content
                    current_para.append(line)
                continue

            # Header - always starts new paragraph
            if is_header:
                if current_para:
                    paragraphs.append("\n".join(current_para))
                    current_para = []
                current_para.append(line)
                in_list = False
                in_table = False
                # Headers are standalone paragraphs
                paragraphs.append("\n".join(current_para))
                current_para = []
                continue

            # List item
            if is_list:
                if not in_list and current_para:
                    # Starting new list, end previous paragraph
                    paragraphs.append("\n".join(current_para))
                    current_para = []
                current_para.append(line)
                in_list = True
                in_table = False
                continue

            # Table row
            if is_table:
                if not in_table and current_para:
                    # Starting new table, end previous paragraph
                    paragraphs.append("\n".join(current_para))
                    current_para = []
                current_para.append(line)
                in_table = True
                in_list = False
                continue

            # Regular text
            if in_list or in_table:
                # End structured content
                if current_para:
                    paragraphs.append("\n".join(current_para))
                    current_para = []
                in_list = False
                in_table = False

            current_para.append(line)

        # Add final paragraph
        if current_para:
            paragraphs.append("\n".join(current_para))

        return [p.strip() for p in paragraphs if p.strip()]

    def _is_structured_content(self, text: str) -> bool:
        """
        Check if text is structured content (header, list, table).

        FIX: Helps preserve markdown structure instead of breaking it.

        Args:
            text: Text to check

        Returns:
            True if text contains structured markdown elements
        """
        lines = text.split("\n")

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Check for headers
            if re.match(r"^#{1,6}\s+", stripped):
                return True

            # Check for list items
            if re.match(r"^(\s*)([-*+]|\d+\.)\s+", stripped):
                return True

            # Check for tables
            if re.match(r"^\|.*\|$", stripped):
                return True

        return False

    def _split_into_sentences(self, text: str) -> List[str]:  # noqa: C901
        """
        Split text into sentences using regex patterns.

        Complexity justified: Handles multiple sentence boundary patterns
        and edge cases for proper sentence splitting.

        Args:
            text: Text to split into sentences

        Returns:
            List of sentence strings
        """
        if not text.strip():
            return []

        # Initialize regex if not already done
        if SentencesStrategy._sentence_regex is None:
            pattern = "|".join(self.SENTENCE_PATTERNS)
            SentencesStrategy._sentence_regex = re.compile(pattern, re.MULTILINE)

        # Split by sentence boundaries
        parts = SentencesStrategy._sentence_regex.split(text)

        sentences = []
        current_sentence = ""

        for i, part in enumerate(parts):
            if not part:
                continue

            # Check if this part is a sentence ending punctuation
            if re.match(r"^[.!?]+$", part):
                current_sentence += part
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""
            else:
                current_sentence += part

        # Add any remaining content as a sentence
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        # Fallback: if no sentences found, split by periods
        if not sentences and text.strip():
            simple_sentences = text.split(".")
            sentences = [s.strip() + "." for s in simple_sentences[:-1] if s.strip()]
            if simple_sentences[-1].strip():
                sentences.append(simple_sentences[-1].strip())

        # Final fallback: return original text as single sentence
        if not sentences and text.strip():
            sentences = [text.strip()]

        return sentences

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            if analysis.text_ratio > 0.8:
                return "High text ratio - sentences strategy is well-suited"
            elif analysis.complexity_score < 0.2:
                return "Low complexity content - sentences strategy is appropriate"
            else:
                return "Universal fallback strategy - can handle any content"
        else:
            # This should never happen for sentences strategy
            return "Sentences strategy should always be able to handle content"

    def get_chunk_statistics(self, chunks: List[Chunk]) -> dict:
        """
        Get statistics about chunks created by this strategy.

        Args:
            chunks: List of chunks created by this strategy

        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "total_sentences": 0,
                "avg_sentences_per_chunk": 0,
                "sentence_based": True,
            }

        total_sentences = sum(
            chunk.get_metadata("sentences_per_chunk", 1) for chunk in chunks
        )

        return {
            "total_chunks": len(chunks),
            "total_sentences": total_sentences,
            "avg_sentences_per_chunk": total_sentences / len(chunks),
            "sentence_based": True,
            "avg_chunk_size": sum(chunk.size for chunk in chunks) / len(chunks),
            "size_range": [
                min(chunk.size for chunk in chunks),
                max(chunk.size for chunk in chunks),
            ],
        }


# Utility functions for sentence processing
def count_sentences(text: str) -> int:
    """
    Count sentences in text.

    Args:
        text: Text to count sentences in

    Returns:
        Number of sentences
    """
    strategy = SentencesStrategy()
    sentences = strategy._split_into_sentences(text)
    return len(sentences)


def preview_sentence_splitting(text: str, max_sentences: int = 5) -> List[str]:
    """
    Preview how text would be split into sentences.

    Args:
        text: Text to preview
        max_sentences: Maximum number of sentences to return

    Returns:
        List of first few sentences
    """
    strategy = SentencesStrategy()
    sentences = strategy._split_into_sentences(text)
    return sentences[:max_sentences]
