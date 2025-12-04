"""
Table-preserving chunking strategy.

This module implements the TableStrategy, which ensures tables are never split
across chunk boundaries. Tables are treated as atomic units that must be preserved
in their entirety.

Design Rationale:
- Atomic preservation: Tables never split (maintains data integrity)
- Preamble awareness: Captures text before tables for context
- Postamble handling: Includes text after tables when possible
- Oversize handling: Allows tables to exceed max_chunk_size when necessary

This strategy consolidates v1.x table handling logic into a single focused strategy.
"""

from typing import List, Tuple

from ..config import ChunkConfig
from ..types import Chunk, ContentAnalysis, Table
from .base import BaseStrategy


class TableStrategy(BaseStrategy):
    """
    Table-preserving chunking strategy.

    Ensures tables are never split across chunk boundaries. Each table becomes
    an atomic unit, potentially with surrounding context text.

    Algorithm:
    1. Extract all tables with their positions
    2. For each table:
       - Extract preamble (text before table)
       - Include table as atomic block
       - Include postamble if fits within size
    3. Handle text between tables as separate chunks

    Attributes:
        name: Strategy identifier "table"
    """

    def __init__(self, config: ChunkConfig):
        """
        Initialize table strategy.

        Args:
            config: Chunking configuration
        """
        super().__init__(config)

    @property
    def name(self) -> str:
        """Strategy name."""
        return "table"

    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle content.

        TableStrategy activates when content contains at least one table.

        Args:
            analysis: Content analysis results

        Returns:
            True if content contains tables
        """
        return analysis.table_count > 0

    def apply(self, text: str, analysis: ContentAnalysis) -> List[Chunk]:
        """
        Apply table-preserving chunking strategy.

        Tables are treated as atomic blocks that never split. Surrounding text
        is chunked normally but respects table boundaries.

        Args:
            text: Text to chunk
            analysis: Content analysis results

        Returns:
            List of chunks with tables preserved
        """
        if not analysis.tables:
            return []

        chunks: List[Chunk] = []
        lines = text.split("\n")

        # Sort tables by start line
        sorted_tables = sorted(analysis.tables, key=lambda t: t.start_line)

        # Track current position in text
        current_line = 1

        for table in sorted_tables:
            # Process text before table (preamble)
            if current_line < table.start_line:
                preamble_lines = lines[current_line - 1 : table.start_line - 1]
                preamble_text = "\n".join(preamble_lines).strip()

                if preamble_text:
                    # Check if we should include preamble with table
                    if self.config.extract_preamble:
                        # Create table chunk with preamble
                        table_chunk = self._create_table_chunk_with_context(
                            table, lines, preamble_text, None
                        )
                        chunks.append(table_chunk)
                    else:
                        # Create separate preamble chunks
                        preamble_chunks = self._chunk_text_section(
                            preamble_text, current_line, table.start_line - 1
                        )
                        chunks.extend(preamble_chunks)

                        # Create table chunk without preamble
                        table_chunk = self._create_table_chunk(table, lines)
                        chunks.append(table_chunk)
                else:
                    # No preamble, just table
                    table_chunk = self._create_table_chunk(table, lines)
                    chunks.append(table_chunk)
            else:
                # No preamble, just table
                table_chunk = self._create_table_chunk(table, lines)
                chunks.append(table_chunk)

            # Update current position
            current_line = table.end_line + 1

        # Process remaining text after last table
        if current_line <= len(lines):
            remaining_lines = lines[current_line - 1 :]
            remaining_text = "\n".join(remaining_lines).strip()

            if remaining_text:
                remaining_chunks = self._chunk_text_section(
                    remaining_text, current_line, len(lines)
                )
                chunks.extend(remaining_chunks)

        return chunks

    def _create_table_chunk(self, table: Table, lines: List[str]) -> Chunk:
        """
        Create chunk containing only the table.

        Args:
            table: Table element to chunk
            lines: All lines of original text

        Returns:
            Chunk containing table
        """
        table_lines = lines[table.start_line - 1 : table.end_line]
        table_content = "\n".join(table_lines)

        return self._create_chunk(
            content=table_content,
            start_line=table.start_line,
            end_line=table.end_line,
            chunk_type="table",
            table_rows=table.row_count,
        )

    def _create_table_chunk_with_context(
        self, table: Table, lines: List[str], preamble: str, postamble: str | None
    ) -> Chunk:
        """
        Create chunk containing table with surrounding context.

        Args:
            table: Table element to chunk
            lines: All lines of original text
            preamble: Text before table
            postamble: Text after table (optional)

        Returns:
            Chunk containing table with context
        """
        # Get table content
        table_lines = lines[table.start_line - 1 : table.end_line]
        table_content = "\n".join(table_lines)

        # Combine preamble, table, and postamble
        parts = [preamble, table_content]
        if postamble:
            parts.append(postamble)

        full_content = "\n\n".join(parts)

        # Calculate line range
        # Preamble line count (only if non-empty)
        preamble_line_count = preamble.count("\n") + 1 if preamble else 0
        start_line = (
            table.start_line - preamble_line_count
            if preamble_line_count > 0
            else table.start_line
        )

        # End line calculation
        end_line = table.end_line
        if postamble:
            postamble_line_count = postamble.count("\n") + 1
            end_line = table.end_line + postamble_line_count

        # Ensure valid line range
        start_line = max(1, start_line)
        end_line = max(start_line, end_line)

        return self._create_chunk(
            content=full_content,
            start_line=start_line,
            end_line=end_line,
            chunk_type="table_with_context",
            table_rows=table.row_count,
            has_preamble=True,
            has_postamble=postamble is not None,
        )

    def _chunk_text_section(
        self, text: str, start_line: int, end_line: int
    ) -> List[Chunk]:
        """
        Chunk a section of text (non-table content).

        Uses paragraph-based chunking similar to fallback strategy.

        Args:
            text: Text to chunk
            start_line: Starting line number
            end_line: Ending line number

        Returns:
            List of chunks
        """
        if not text.strip():
            return []

        # Split by paragraphs
        paragraphs = self._split_by_paragraphs(text)

        chunks: List[Chunk] = []
        current_parts: List[str] = []
        current_size = 0
        current_start_line = start_line

        for paragraph in paragraphs:
            para_size = len(paragraph)
            para_lines = paragraph.count("\n") + 1

            # Check if adding paragraph would exceed size
            if (
                current_size + para_size + 2 > self.config.max_chunk_size
                and current_parts
            ):
                # Finalize current chunk
                chunk_text = "\n\n".join(current_parts)
                chunk_lines = chunk_text.count("\n") + 1

                chunks.append(
                    self._create_chunk(
                        content=chunk_text,
                        start_line=current_start_line,
                        end_line=current_start_line + chunk_lines - 1,
                        chunk_type="text",
                    )
                )

                current_parts = []
                current_size = 0
                current_start_line = current_start_line + chunk_lines

            # Add paragraph to current chunk
            current_parts.append(paragraph)
            current_size += para_size + 2

        # Finalize remaining chunk
        if current_parts:
            chunk_text = "\n\n".join(current_parts)
            chunk_lines = chunk_text.count("\n") + 1

            chunks.append(
                self._create_chunk(
                    content=chunk_text,
                    start_line=current_start_line,
                    end_line=min(current_start_line + chunk_lines - 1, end_line),
                    chunk_type="text",
                )
            )

        return chunks
