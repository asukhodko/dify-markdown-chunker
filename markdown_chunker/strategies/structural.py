"""
Structural (header-based) chunking strategy.

This module implements the StructuralStrategy, which uses markdown headers as
natural chunk boundaries. This approach maintains semantic coherence by keeping
related sections together.

Design Rationale:
- Semantic preservation: Sections stay together (related content grouped)
- Header hierarchy: Respects document structure (h1 > h2 > h3...)
- Size awareness: Merges small sections, splits large sections
- Simplified Phase 2: No complex tree building, just linear processing

This strategy consolidates v1.x Structural strategy, removing unnecessary Phase 2
complexity while maintaining semantic chunking benefits.
"""

from typing import List, Tuple

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis, Header
from .base import BaseStrategy


class StructuralStrategy(BaseStrategy):
    """
    Header-based structural chunking strategy.

    Uses markdown headers as natural boundaries for chunks. Maintains document
    structure by keeping sections together when possible.

    Algorithm:
    1. Extract all headers with their content
    2. For each section:
       - If section fits in chunk size, keep as-is
       - If section too small, merge with next section
       - If section too large, split by sub-headers or paragraphs
    3. Respect header hierarchy when merging/splitting

    Simplified from v1.x: No tree building, no complex hierarchy traversal,
    just linear processing with hierarchy awareness.

    Attributes:
        name: Strategy identifier "structural"
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize structural strategy.

        Args:
            config: Chunking configuration
        """
        super().__init__(config)

    @property
    def name(self) -> str:
        """Strategy name."""
        return "structural"

    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle content.

        StructuralStrategy activates when content has sufficient header structure.
        Uses structure_threshold from config (default: 3 headers).

        Args:
            analysis: Content analysis results

        Returns:
            True if content has enough headers
        """
        return analysis.header_count >= self.config.structure_threshold

    def apply(self, text: str, analysis: ContentAnalysis) -> List[Chunk]:
        """
        Apply structural chunking strategy.

        Uses headers as boundaries, maintaining semantic coherence while
        respecting size constraints.

        Args:
            text: Text to chunk
            analysis: Content analysis results

        Returns:
            List of chunks based on document structure
        """
        if not analysis.headers:
            return []

        # Extract sections based on headers
        sections = self._extract_sections(text, analysis.headers)

        # Process sections into chunks
        chunks = self._process_sections(sections)

        return chunks

    def _extract_sections(
        self, text: str, headers: List[Header]
    ) -> List[Tuple[Header, str]]:
        """
        Extract sections from text based on headers.

        Each section includes the header and all content until the next header
        of equal or higher level.

        Args:
            text: Full text
            headers: List of headers

        Returns:
            List of (header, content) tuples
        """
        lines = text.split("\n")
        sections: List[Tuple[Header, str]] = []

        # Sort headers by line number
        sorted_headers = sorted(headers, key=lambda h: h.line_number)

        for i, header in enumerate(sorted_headers):
            # Determine section end
            if i + 1 < len(sorted_headers):
                # Section ends at next header of equal or higher level
                next_header = sorted_headers[i + 1]

                # Find next header of equal or higher level (lower number = higher level)
                section_end = next_header.line_number - 1
                for j in range(i + 1, len(sorted_headers)):
                    if sorted_headers[j].level <= header.level:
                        section_end = sorted_headers[j].line_number - 1
                        break
                    if j == len(sorted_headers) - 1:
                        section_end = len(lines)
            else:
                # Last header - section goes to end of document
                section_end = len(lines)

            # Extract section content
            section_lines = lines[header.line_number - 1 : section_end]
            section_content = "\n".join(section_lines)

            sections.append((header, section_content))

        return sections

    def _process_sections(self, sections: List[Tuple[Header, str]]) -> List[Chunk]:
        """
        Process sections into chunks.

        Handles three cases:
        1. Section fits in chunk - keep as-is
        2. Section too small - merge with next section
        3. Section too large - split into sub-chunks

        Args:
            sections: List of (header, content) tuples

        Returns:
            List of chunks
        """
        chunks: List[Chunk] = []
        i = 0

        while i < len(sections):
            header, content = sections[i]
            section_size = len(content)

            # Case 1: Section fits nicely in chunk size
            if self._is_within_size(content):
                chunk = self._create_section_chunk(header, content)
                chunks.append(chunk)
                i += 1

            # Case 2: Section too small - try to merge with next
            elif section_size < self.config.min_chunk_size and i + 1 < len(sections):
                merged_content = content
                merged_end_line = header.line_number + content.count("\n")
                j = i + 1

                # Merge consecutive small sections
                while j < len(sections):
                    next_header, next_content = sections[j]
                    combined_size = len(merged_content) + len(next_content) + 2

                    if combined_size <= self.config.max_chunk_size:
                        merged_content = merged_content + "\n\n" + next_content
                        merged_end_line = next_header.line_number + next_content.count(
                            "\n"
                        )
                        j += 1
                    else:
                        break

                # Create merged chunk
                chunk = self._create_chunk(
                    content=merged_content,
                    start_line=header.line_number,
                    end_line=merged_end_line,
                    chunk_type="structural",
                    header_level=header.level,
                    header_text=header.text,
                    merged_sections=j - i,
                )
                chunks.append(chunk)
                i = j

            # Case 3: Section too large - split it
            else:
                section_chunks = self._split_large_section(header, content)
                chunks.extend(section_chunks)
                i += 1

        return chunks

    def _create_section_chunk(self, header: Header, content: str) -> Chunk:
        """
        Create chunk from a single section.

        Args:
            header: Section header
            content: Section content

        Returns:
            Chunk representing the section
        """
        end_line = header.line_number + content.count("\n")

        return self._create_chunk(
            content=content,
            start_line=header.line_number,
            end_line=end_line,
            chunk_type="structural",
            header_level=header.level,
            header_text=header.text,
        )

    def _split_large_section(self, header: Header, content: str) -> List[Chunk]:
        """
        Split large section into multiple chunks.

        Strategy:
        1. Try to split by sub-headers (if present)
        2. Fall back to paragraph-based splitting

        Args:
            header: Section header
            content: Section content

        Returns:
            List of chunks from split section
        """
        # Check if section has sub-headers
        lines = content.split("\n")
        sub_headers = []

        for i, line in enumerate(lines):
            if line.startswith("#"):
                # Count header level
                level = len(line) - len(line.lstrip("#"))
                if level > header.level:
                    sub_headers.append((i, level, line))

        # If has sub-headers, split by them
        if sub_headers and self.config.preserve_atomic_blocks:
            return self._split_by_subheaders(header, content, sub_headers)

        # Otherwise, split by paragraphs
        return self._split_by_paragraphs_with_header(header, content)

    def _split_by_subheaders(
        self, header: Header, content: str, sub_headers: List[Tuple[int, int, str]]
    ) -> List[Chunk]:
        """
        Split section by sub-headers.

        Args:
            header: Main section header
            content: Section content
            sub_headers: List of (line_index, level, text) for sub-headers

        Returns:
            List of chunks split by sub-headers
        """
        lines = content.split("\n")
        chunks: List[Chunk] = []

        # Include content before first sub-header with main header
        if sub_headers[0][0] > 1:
            preamble_lines = lines[: sub_headers[0][0]]
            preamble_content = "\n".join(preamble_lines)

            if preamble_content.strip():
                chunk = self._create_chunk(
                    content=preamble_content,
                    start_line=header.line_number,
                    end_line=header.line_number + len(preamble_lines) - 1,
                    chunk_type="structural",
                    header_level=header.level,
                    header_text=header.text,
                )
                chunks.append(chunk)

        # Process each sub-section
        for i, (line_idx, level, text) in enumerate(sub_headers):
            # Determine sub-section end
            if i + 1 < len(sub_headers):
                end_idx = sub_headers[i + 1][0]
            else:
                end_idx = len(lines)

            # Extract sub-section content
            subsection_lines = lines[line_idx:end_idx]
            subsection_content = "\n".join(subsection_lines)

            # Check if subsection still too large
            if len(subsection_content) > self.config.max_chunk_size:
                # Recursively split
                subsection_header = Header(
                    level=level,
                    text=text.lstrip("#").strip(),
                    line_number=header.line_number + line_idx,
                )
                sub_chunks = self._split_large_section(
                    subsection_header, subsection_content
                )
                chunks.extend(sub_chunks)
            else:
                # Create chunk for subsection
                chunk = self._create_chunk(
                    content=subsection_content,
                    start_line=header.line_number + line_idx,
                    end_line=header.line_number + end_idx - 1,
                    chunk_type="structural",
                    header_level=level,
                    header_text=text.lstrip("#").strip(),
                )
                chunks.append(chunk)

        return chunks

    def _split_by_paragraphs_with_header(
        self, header: Header, content: str
    ) -> List[Chunk]:
        """
        Split section by paragraphs when no sub-headers available.

        Args:
            header: Section header
            content: Section content

        Returns:
            List of chunks split by paragraphs
        """
        paragraphs = self._split_by_paragraphs(content)
        chunks: List[Chunk] = []

        current_parts: List[str] = []
        current_size = 0
        current_line = header.line_number

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
                    chunk_type="structural",
                    header_level=header.level,
                    header_text=header.text,
                )
                chunks.append(chunk)

                current_parts = []
                current_size = 0
                current_line += chunk_lines

            # Add paragraph to current chunk
            current_parts.append(paragraph)
            current_size += para_size + 2

        # Finalize remaining chunk
        if current_parts:
            chunk_content = "\n\n".join(current_parts)
            chunk_lines = chunk_content.count("\n") + 1

            chunk = self._create_chunk(
                content=chunk_content,
                start_line=current_line,
                end_line=current_line + chunk_lines - 1,
                chunk_type="structural",
                header_level=header.level,
                header_text=header.text,
            )
            chunks.append(chunk)

        return chunks
