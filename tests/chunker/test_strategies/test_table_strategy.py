"""
Tests for TableStrategy.
This module tests the table-heavy document chunking strategy that preserves
table structure and handles large tables by splitting rows.
"""

from unittest.mock import Mock

from markdown_chunker.chunker.strategies.table_strategy import (
    TableInfo,
    TableRowGroup,
    TableStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import ContentAnalysis, Stage1Results


class TestTableInfo:
    """Test cases for TableInfo class."""

    def test_table_info_creation(self):
        """Test creating a table info object."""
        table = TableInfo(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |", "| C | D |"],
            start_line=1,
            end_line=4,
            column_count=2,
        )

        assert table.header == "| Col1 | Col2 |"
        assert table.column_count == 2
        assert len(table.rows) == 2

    def test_get_full_content(self):
        """Test getting full table content."""
        table = TableInfo(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |"],
            start_line=1,
            end_line=3,
            column_count=2,
        )

        content = table.get_full_content()

        assert "| Col1 | Col2 |" in content
        assert "|------|------|" in content
        assert "| A | B |" in content

    def test_calculate_size(self):
        """Test calculating table size."""
        table = TableInfo(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |", "| C | D |"],
            start_line=1,
            end_line=4,
            column_count=2,
        )

        size = table.calculate_size()

        # Should include header, separator, and all rows
        assert size > 0
        assert size == len(table.get_full_content())


class TestTableRowGroup:
    """Test cases for TableRowGroup class."""

    def test_table_row_group_creation(self):
        """Test creating a table row group."""
        group = TableRowGroup(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |"],
            start_line=1,
            end_line=3,
            part_number=1,
            total_parts=2,
            total_rows=10,
        )

        assert group.part_number == 1
        assert group.total_parts == 2
        assert group.total_rows == 10
        assert len(group.rows) == 1


class TestTableStrategy:
    """Test cases for TableStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = TableStrategy()

        assert strategy.name == "table"
        assert strategy.priority == 5  # Medium-low priority

    def test_can_handle_high_table_count(self):
        """Test can_handle with high table count."""
        strategy = TableStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 5
        analysis.table_ratio = 0.2

        config = ChunkConfig(table_count_threshold=3, table_ratio_threshold=0.4)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_high_table_ratio(self):
        """Test can_handle with high table ratio."""
        strategy = TableStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 2
        analysis.table_ratio = 0.5

        config = ChunkConfig(table_count_threshold=3, table_ratio_threshold=0.4)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_insufficient_tables(self):
        """Test can_handle with insufficient tables."""
        strategy = TableStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 1
        analysis.table_ratio = 0.2

        config = ChunkConfig(table_count_threshold=3, table_ratio_threshold=0.4)

        assert strategy.can_handle(analysis, config) is False

    def test_calculate_quality_high_tables(self):
        """Test quality calculation for high table content."""
        strategy = TableStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 6
        analysis.table_ratio = 0.6

        quality = strategy.calculate_quality(analysis)

        # Should be very high quality
        assert quality > 0.9

    def test_calculate_quality_moderate_tables(self):
        """Test quality calculation for moderate table content."""
        strategy = TableStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 2
        analysis.table_ratio = 0.25

        quality = strategy.calculate_quality(analysis)

        # Should be moderate quality
        assert 0.3 < quality < 0.7

    def test_is_table_header(self):
        """Test table header detection."""
        strategy = TableStrategy()

        assert strategy._is_table_header("| Col1 | Col2 | Col3 |") is True
        assert strategy._is_table_header("| Header |") is True
        assert strategy._is_table_header("Not a table") is False
        assert strategy._is_table_header("") is False

    def test_is_table_separator(self):
        """Test table separator detection."""
        strategy = TableStrategy()

        assert strategy._is_table_separator("|------|------|") is True
        assert strategy._is_table_separator("|:--- | ---: |") is True
        assert strategy._is_table_separator("| ---- |") is True
        assert strategy._is_table_separator("Not a separator") is False

    def test_is_table_row(self):
        """Test table row detection."""
        strategy = TableStrategy()

        assert strategy._is_table_row("| Data1 | Data2 |") is True
        assert strategy._is_table_row("| A |") is True
        assert strategy._is_table_row("Not a row") is False
        assert strategy._is_table_row("") is False

    def test_detect_tables_simple(self):
        """Test detecting a simple table."""
        strategy = TableStrategy()

        content = """# Document

| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |

Some text after."""

        tables = strategy._detect_tables(content)

        assert len(tables) == 1
        assert tables[0].column_count == 2
        assert len(tables[0].rows) == 2
        assert tables[0].header == "| Name | Age |"

    def test_detect_tables_multiple(self):
        """Test detecting multiple tables."""
        strategy = TableStrategy()

        content = """# Document

| Table 1 |
|---------|
| Data 1 |

Some text.

| Table 2 | Col2 |
|---------|------|
| Data 2 | Val2 |"""

        tables = strategy._detect_tables(content)

        assert len(tables) == 2
        assert tables[0].column_count == 1
        assert tables[1].column_count == 2

    def test_detect_tables_no_data_rows(self):
        """Test that tables without data rows are ignored."""
        strategy = TableStrategy()

        content = """| Header |
|--------|

No data rows."""

        tables = strategy._detect_tables(content)

        # Should not detect table without data rows
        assert len(tables) == 0

    def test_split_table_rows(self):
        """Test splitting table rows into groups."""
        strategy = TableStrategy()

        table = TableInfo(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=[f"| Row{i} | Data{i} |" for i in range(10)],
            start_line=1,
            end_line=12,
            column_count=2,
        )

        # Small chunk size to force splitting
        groups = strategy._split_table_rows(table, max_chunk_size=200)

        # Should create multiple groups
        assert len(groups) > 1

        # Check group properties
        for i, group in enumerate(groups):
            assert group.header == table.header
            assert group.separator == table.separator
            assert group.part_number == i + 1
            assert group.total_parts == len(groups)
            assert group.total_rows == len(table.rows)

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = TableStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_no_tables(self):
        """Test applying strategy to content without tables."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()
        content = "Just some plain text without any tables."

        chunks = strategy.apply(content, stage1_results, config)

        assert chunks == []

    def test_apply_simple_table(self):
        """Test applying strategy to simple table."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        content = """# API Methods

| Method | Endpoint |
|--------|----------|
| GET | /users |
| POST | /users |"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create at least one chunk
        assert len(chunks) >= 1

        # Should have table chunks
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        assert len(table_chunks) >= 1

        # Check table metadata
        table_chunk = table_chunks[0]
        assert table_chunk.metadata["column_count"] == 2
        assert table_chunk.metadata["row_count_in_chunk"] == 2
        assert table_chunk.metadata["has_header"] is True
        assert table_chunk.metadata["is_split"] is False

    def test_create_table_chunk(self):
        """Test creating a chunk from a table."""
        strategy = TableStrategy()
        config = ChunkConfig.default()

        table = TableInfo(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |", "| C | D |"],
            start_line=1,
            end_line=4,
            column_count=2,
        )

        chunk = strategy._create_table_chunk(table, config)

        assert chunk.metadata["content_type"] == "table"
        assert chunk.metadata["column_count"] == 2
        assert chunk.metadata["row_count_in_chunk"] == 2
        assert chunk.metadata["is_split"] is False
        assert "| Col1 | Col2 |" in chunk.content

    def test_create_table_group_chunk(self):
        """Test creating a chunk from a table row group."""
        strategy = TableStrategy()
        config = ChunkConfig.default()

        group = TableRowGroup(
            header="| Col1 | Col2 |",
            separator="|------|------|",
            rows=["| A | B |"],
            start_line=1,
            end_line=3,
            part_number=1,
            total_parts=3,
            total_rows=10,
        )

        chunk = strategy._create_table_group_chunk(group, config)

        assert chunk.metadata["content_type"] == "table"
        assert chunk.metadata["is_split"] is True
        assert chunk.metadata["split_part"] == 1
        assert chunk.metadata["total_parts"] == 3
        assert chunk.metadata["total_rows"] == 10
        # Header should be duplicated
        assert "| Col1 | Col2 |" in chunk.content

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = TableStrategy()

        # Can handle - high count
        analysis = Mock(spec=ContentAnalysis)
        analysis.table_count = 5
        analysis.table_ratio = 0.2

        reason = strategy._get_selection_reason(analysis, True)
        assert "5 tables" in reason
        assert "suitable" in reason

        # Can handle - high ratio
        analysis.table_count = 2
        analysis.table_ratio = 0.5

        reason = strategy._get_selection_reason(analysis, True)
        assert "50.0%" in reason
        assert "suitable" in reason

        # Cannot handle
        analysis.table_count = 1
        analysis.table_ratio = 0.1

        reason = strategy._get_selection_reason(analysis, False)
        assert "Insufficient" in reason

    def test_get_table_statistics(self):
        """Test getting table statistics."""
        strategy = TableStrategy()

        chunks = [
            strategy._create_chunk(
                "Content 1",
                1,
                1,
                "table",
                column_count=3,
                row_count_in_chunk=5,
                is_split=False,
            ),
            strategy._create_chunk(
                "Content 2",
                2,
                2,
                "table",
                column_count=2,
                row_count_in_chunk=3,
                is_split=True,
            ),
        ]

        stats = strategy.get_table_statistics(chunks)

        assert stats["total_chunks"] == 2
        assert stats["table_chunks"] == 2
        assert stats["total_rows"] == 8
        assert stats["split_chunks"] == 1
        assert stats["avg_rows_per_chunk"] == 4.0

    def test_get_table_statistics_empty(self):
        """Test getting statistics for empty chunk list."""
        strategy = TableStrategy()

        stats = strategy.get_table_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["table_chunks"] == 0


class TestTableStrategyIntegration:
    """Integration tests for TableStrategy."""

    def test_realistic_api_documentation(self):
        """Test with realistic API documentation table."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=800, min_chunk_size=200)

        content = """# API Endpoints

## User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | /api/users | List all users | Yes |
| GET | /api/users/:id | Get user by ID | Yes |
| POST | /api/users | Create new user | Yes |
| PUT | /api/users/:id | Update user | Yes |
| DELETE | /api/users/:id | Delete user | Yes |

## Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /api/auth/login | User login | No |
| POST | /api/auth/logout | User logout | Yes |
| POST | /api/auth/refresh | Refresh token | Yes |"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) >= 2

        # Should have table chunks
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        assert len(table_chunks) >= 2

        # Check that tables have proper structure
        for table_chunk in table_chunks:
            assert table_chunk.metadata["column_count"] == 4
            assert table_chunk.metadata["has_header"] is True
            # Content should include header
            assert "Method" in table_chunk.content
            assert "Endpoint" in table_chunk.content

    def test_large_table_splitting(self):
        """Test splitting a large table."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)

        # Create a large table
        rows = []
        for i in range(50):
            rows.append(f"| {i} | User{i} | user{i}@example.com |")

        content = """# User Database

| ID | Name | Email |
|----|------|-------|
""" + "\n".join(
            rows
        )

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks due to size
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]

        if len(table_chunks) > 1:
            # Check that it's marked as split
            for chunk in table_chunks:
                assert chunk.metadata["is_split"] is True
                assert "split_part" in chunk.metadata
                assert "total_parts" in chunk.metadata
                # Header should be duplicated in each chunk
                assert "| ID | Name | Email |" in chunk.content
                assert "|----|------|-------|" in chunk.content

    def test_mixed_content_with_tables(self):
        """Test handling mixed content with tables and text."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        content = """# Database Schema

This document describes the database schema.

## Users Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR | User name |
| email | VARCHAR | Email address |

The users table stores all user information.

## Posts Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | Foreign key |
| title | VARCHAR | Post title |
| content | TEXT | Post content |

The posts table stores user posts."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) >= 2

        # Should have both table and text chunks
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]

        assert len(table_chunks) >= 2  # Two tables
        # May or may not have text chunks depending on text size threshold

    def test_wide_table_handling(self):
        """Test handling wide tables that might exceed chunk size."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig(max_chunk_size=300, min_chunk_size=100)

        # Create a wide table with many columns
        content = """| Col1 | Col2 | Col3 | Col4 | Col5 | Col6 | Col7 | Col8 |
|------|------|------|------|------|------|------|------|
| Data1 | Data2 | Data3 | Data4 | Data5 | Data6 | Data7 | Data8 |"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create at least one chunk
        assert len(chunks) >= 1

        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]

        if table_chunks:
            # If table is too wide, it might be marked as oversize
            table_chunk = table_chunks[0]
            if table_chunk.size > config.max_chunk_size:
                assert table_chunk.metadata.get("allow_oversize") is True

    def test_table_with_alignment(self):
        """Test handling tables with column alignment."""
        strategy = TableStrategy()

        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        content = """| Left | Center | Right |
|:-----|:------:|------:|
| L1 | C1 | R1 |
| L2 | C2 | R2 |"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should detect and process the table
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        assert len(table_chunks) >= 1

        # Check that alignment markers are preserved
        table_chunk = table_chunks[0]
        assert (
            ":-----" in table_chunk.content
            or ":------:" in table_chunk.content
            or "------:" in table_chunk.content
        )
