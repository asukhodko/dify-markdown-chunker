"""
TableStrategy - Strategy for table-heavy documents.

This strategy preserves table structure and handles large tables by splitting
rows while duplicating headers for readability.

Algorithm Documentation:
    - Table Strategy: docs/markdown-extractor/03-strategies/table-strategy.md
    - Strategy Selection: docs/markdown-extractor/02-algorithm-core/strategy-selection.md  # noqa: E501
"""

import re
from dataclasses import dataclass
from typing import Dict, List

from markdown_chunker.parser.types import ContentAnalysis, Stage1Results

from ..types import Chunk, ChunkConfig
from .base import BaseStrategy


@dataclass
class TableInfo:
    """Information about a markdown table."""

    header: str
    separator: str
    rows: List[str]
    start_line: int
    end_line: int
    column_count: int

    def get_full_content(self) -> str:
        """Get full table content."""
        return f"{self.header}\n{self.separator}\n" + "\n".join(self.rows)

    def calculate_size(self) -> int:
        """Calculate total size of table."""
        return len(self.get_full_content())


@dataclass
class TableRowGroup:
    """A group of table rows that fit within size constraints."""

    header: str
    separator: str
    rows: List[str]
    start_line: int
    end_line: int
    part_number: int
    total_parts: int
    total_rows: int


class TableStrategy(BaseStrategy):
    """
    Strategy for table-heavy documents (≥3 tables or ≥40% table content).

    This strategy:
    - Preserves tables intact when possible
    - Splits large tables by rows
    - Duplicates headers in each chunk for readability
    - Maintains table structure and formatting
    - Handles wide tables with oversize allowance

    Priority: 4 (medium)
    """

    # Table detection patterns
    TABLE_HEADER_PATTERN = r"^\|.+\|$"
    TABLE_SEPARATOR_PATTERN = r"^\|[\s:|-]+\|$"
    TABLE_ROW_PATTERN = r"^\|.+\|$"

    @property
    def name(self) -> str:
        """Strategy name."""
        return "table"

    @property
    def priority(self) -> int:
        """Medium-low priority."""
        return 5

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Check if strategy can handle the content.

        Suitable for documents with:
        - High table count (≥3 tables by default)
        - High table ratio (≥40% by default)
        """
        return (
            analysis.table_count >= config.table_count_threshold
            or analysis.table_ratio >= config.table_ratio_threshold
        )

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        """
        Calculate quality score for table strategy.

        Higher quality for:
        - More tables
        - Higher table ratio
        - Well-structured tables
        """
        score = 0.0

        # Table count contribution
        if analysis.table_count >= 5:
            score += 0.8
        elif analysis.table_count >= 3:
            score += 0.6
        elif analysis.table_count >= 2:
            score += 0.4

        # Table ratio contribution
        if analysis.table_ratio >= 0.5:
            score += 0.3
        elif analysis.table_ratio >= 0.3:
            score += 0.2
        elif analysis.table_ratio >= 0.2:
            score += 0.1

        return min(score, 1.0)

    def apply(
        self, content: str, stage1_results: Stage1Results, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply table strategy to create chunks.

        Args:
            content: Original markdown content
            stage1_results: Results from Stage 1 processing
            config: Chunking configuration

        Returns:
            List of chunks created by table-aware splitting
        """
        if not content.strip():
            return []

        # Detect tables in content
        tables = self._detect_tables(content)

        if not tables:
            # No tables found - cannot use table strategy
            return []

        # Create chunks from tables
        chunks = self._create_chunks_from_tables(tables, content, config)

        return self._validate_chunks(chunks, config)

    def _detect_tables(self, content: str) -> List[TableInfo]:
        """
        Detect markdown tables in content.

        Args:
            content: Content to analyze

        Returns:
            List of TableInfo objects
        """
        tables = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            # Look for table header
            if (
                i + 1 < len(lines)
                and self._is_table_header(lines[i])
                and self._is_table_separator(lines[i + 1])
            ):
                # Found a table
                header = lines[i]
                separator = lines[i + 1]
                start_line = i + 1  # 1-based

                # Count columns
                column_count = header.count("|") - 1

                # Collect table rows
                rows = []
                j = i + 2
                while j < len(lines) and self._is_table_row(lines[j]):
                    rows.append(lines[j])
                    j += 1

                end_line = j  # 1-based

                # Only consider valid tables (with at least one data row)
                if rows:
                    table = TableInfo(
                        header=header,
                        separator=separator,
                        rows=rows,
                        start_line=start_line,
                        end_line=end_line,
                        column_count=column_count,
                    )
                    tables.append(table)

                i = j
            else:
                i += 1

        return tables

    def _is_table_header(self, line: str) -> bool:
        """Check if line is a table header."""
        return bool(re.match(self.TABLE_HEADER_PATTERN, line.strip()))

    def _is_table_separator(self, line: str) -> bool:
        """Check if line is a table separator."""
        return bool(re.match(self.TABLE_SEPARATOR_PATTERN, line.strip()))

    def _is_table_row(self, line: str) -> bool:
        """Check if line is a table row."""
        stripped = line.strip()
        if not stripped:
            return False
        return bool(re.match(self.TABLE_ROW_PATTERN, stripped))

    def _create_chunks_from_tables(
        self, tables: List[TableInfo], content: str, config: ChunkConfig
    ) -> List[Chunk]:
        """
        Create chunks from detected tables.

        Args:
            tables: List of detected tables
            content: Original content
            config: Chunking configuration

        Returns:
            List of chunks
        """
        chunks = []
        content_lines = content.split("\n")
        last_position = 0

        for table in tables:
            # Add text before table as a chunk if significant
            if table.start_line - 1 >= last_position:
                text_before = "\n".join(
                    content_lines[last_position : table.start_line - 1]
                ).strip()
                if (
                    text_before and len(text_before) > 10
                ):  # Minimum text size (lowered to preserve headers)
                    text_chunk = self._create_chunk(
                        content=text_before,
                        start_line=last_position + 1,
                        end_line=table.start_line - 1,
                        content_type="text",
                    )
                    chunks.append(text_chunk)

            # Process table
            table_size = table.calculate_size()

            if table_size <= config.max_chunk_size:
                # Table fits in one chunk
                chunk = self._create_table_chunk(table, config)
                chunks.append(chunk)
            else:
                # Need to split table by rows
                row_groups = self._split_table_rows(table, config.max_chunk_size)

                for group in row_groups:
                    chunk = self._create_table_group_chunk(group, config)
                    chunks.append(chunk)

            last_position = table.end_line

        # Add remaining text after last table
        if last_position < len(content_lines):
            text_after = "\n".join(content_lines[last_position:]).strip()
            if text_after and len(text_after) > 50:
                text_chunk = self._create_chunk(
                    content=text_after,
                    start_line=last_position + 1,
                    end_line=len(content_lines),
                    content_type="text",
                )
                chunks.append(text_chunk)

        return chunks

    def _split_table_rows(
        self, table: TableInfo, max_chunk_size: int
    ) -> List[TableRowGroup]:
        """
        Split table rows into groups that fit within size constraints.

        Args:
            table: Table to split
            max_chunk_size: Maximum chunk size

        Returns:
            List of TableRowGroup objects
        """
        # Calculate header size (header + separator)
        header_size = len(table.header) + len(table.separator) + 2  # +2 for newlines

        # Calculate average row size
        if table.rows:
            avg_row_size = (
                sum(len(row) for row in table.rows) / len(table.rows) + 1
            )  # +1 for newline
        else:
            avg_row_size = 50  # Default estimate

        # Calculate how many rows fit per chunk
        available_size = max_chunk_size - header_size
        rows_per_chunk = max(1, int(available_size / avg_row_size))

        # Split rows into groups
        groups = []
        total_parts = (
            len(table.rows) + rows_per_chunk - 1
        ) // rows_per_chunk  # Ceiling division

        for i in range(0, len(table.rows), rows_per_chunk):
            group_rows = table.rows[i : i + rows_per_chunk]
            part_number = i // rows_per_chunk + 1

            group = TableRowGroup(
                header=table.header,
                separator=table.separator,
                rows=group_rows,
                start_line=table.start_line + i,
                end_line=table.start_line + i + len(group_rows),
                part_number=part_number,
                total_parts=total_parts,
                total_rows=len(table.rows),
            )
            groups.append(group)

        return groups

    def _create_table_chunk(self, table: TableInfo, config: ChunkConfig) -> Chunk:
        """
        Create a chunk from a complete table.

        Args:
            table: Table to create chunk from
            config: Chunking configuration

        Returns:
            Chunk with table content
        """
        content = table.get_full_content()

        metadata: dict = {
            "column_count": table.column_count,
            "row_count_in_chunk": len(table.rows),
            "total_rows": len(table.rows),
            "has_header": True,
            "is_split": False,
        }

        # Check if table is oversized
        if len(content) > config.max_chunk_size:
            metadata["allow_oversize"] = True
            metadata["oversize_reason"] = "wide_table_row"

        return self._create_chunk(
            content=content,
            start_line=table.start_line,
            end_line=table.end_line,
            content_type="table",
            **metadata,
        )

    def _create_table_group_chunk(
        self, group: TableRowGroup, config: ChunkConfig
    ) -> Chunk:
        """
        Create a chunk from a table row group.

        Args:
            group: Table row group
            config: Chunking configuration

        Returns:
            Chunk with table group content
        """
        # Build content with header duplication
        content = f"{group.header}\n{group.separator}\n" + "\n".join(group.rows)

        metadata = {
            "column_count": group.header.count("|") - 1,
            "row_count_in_chunk": len(group.rows),
            "total_rows": group.total_rows,
            "has_header": True,
            "is_split": True,
            "split_part": group.part_number,
            "total_parts": group.total_parts,
        }

        return self._create_chunk(
            content=content,
            start_line=group.start_line,
            end_line=group.end_line,
            content_type="table",
            **metadata,
        )

    def _get_selection_reason(self, analysis: ContentAnalysis, can_handle: bool) -> str:
        """Get reason for strategy selection."""
        if can_handle:
            if analysis.table_count >= 3:
                return (
                    f"High table count ({analysis.table_count} tables) - "
                    f"suitable for table strategy"
                )
            else:
                return (
                    f"High table ratio ({analysis.table_ratio:.1%}) - "
                    f"suitable for table strategy"
                )
        else:
            return (
                f"Insufficient tables ({analysis.table_count} tables, "
                f"{analysis.table_ratio:.1%} ratio) for table strategy"
            )

    def get_table_statistics(self, chunks: List[Chunk]) -> Dict:
        """
        Get statistics about table-based chunks.

        Args:
            chunks: List of chunks created by this strategy

        Returns:
            Dictionary with table statistics
        """
        if not chunks:
            return {"total_chunks": 0, "table_chunks": 0}

        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]

        if not table_chunks:
            return {"total_chunks": len(chunks), "table_chunks": 0}

        total_rows = sum(c.get_metadata("row_count_in_chunk", 0) for c in table_chunks)
        split_chunks = sum(1 for c in table_chunks if c.get_metadata("is_split", False))

        column_counts = [c.get_metadata("column_count", 0) for c in table_chunks]

        return {
            "total_chunks": len(chunks),
            "table_chunks": len(table_chunks),
            "total_rows": total_rows,
            "split_chunks": split_chunks,
            "avg_rows_per_chunk": total_rows / len(table_chunks) if table_chunks else 0,
            "avg_columns": (
                sum(column_counts) / len(column_counts) if column_counts else 0
            ),
            "max_columns": max(column_counts) if column_counts else 0,
        }
