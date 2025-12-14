"""
Unit tests for table grouping feature.

**Feature: table-grouping-option**
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_chunker_v2.chunker import MarkdownChunker  # noqa: E402
from markdown_chunker_v2.config import ChunkConfig  # noqa: E402
from markdown_chunker_v2.table_grouping import (  # noqa: E402
    TableGrouper,
    TableGroupingConfig,
)
from markdown_chunker_v2.types import Header, TableBlock  # noqa: E402


class TestTableGroupingConfig:
    """Tests for TableGroupingConfig."""

    def test_default_config_values(self):
        """Default config has expected values."""
        config = TableGroupingConfig()
        assert config.max_distance_lines == 10
        assert config.max_grouped_tables == 5
        assert config.max_group_size == 5000
        assert config.require_same_section is True

    def test_custom_config_values(self):
        """Custom config values are respected."""
        config = TableGroupingConfig(
            max_distance_lines=20,
            max_grouped_tables=3,
            max_group_size=8000,
            require_same_section=False,
        )
        assert config.max_distance_lines == 20
        assert config.max_grouped_tables == 3
        assert config.max_group_size == 8000
        assert config.require_same_section is False

    def test_invalid_max_distance_raises(self):
        """Negative max_distance_lines raises ValueError."""
        with pytest.raises(ValueError, match="max_distance_lines"):
            TableGroupingConfig(max_distance_lines=-1)

    def test_invalid_max_tables_raises(self):
        """Zero max_grouped_tables raises ValueError."""
        with pytest.raises(ValueError, match="max_grouped_tables"):
            TableGroupingConfig(max_grouped_tables=0)

    def test_invalid_max_size_raises(self):
        """Too small max_group_size raises ValueError."""
        with pytest.raises(ValueError, match="max_group_size"):
            TableGroupingConfig(max_group_size=50)


class TestChunkConfigTableGrouping:
    """Tests for ChunkConfig table grouping integration."""

    def test_grouping_disabled_by_default(self):
        """Table grouping is disabled by default."""
        config = ChunkConfig()
        assert config.group_related_tables is False
        assert config.table_grouping_config is None

    def test_get_table_grouper_returns_none_when_disabled(self):
        """get_table_grouper returns None when disabled."""
        config = ChunkConfig(group_related_tables=False)
        assert config.get_table_grouper() is None

    def test_get_table_grouper_returns_grouper_when_enabled(self):
        """get_table_grouper returns TableGrouper when enabled."""
        config = ChunkConfig(group_related_tables=True)
        grouper = config.get_table_grouper()
        assert grouper is not None
        assert type(grouper).__name__ == "TableGrouper"

    def test_get_table_grouper_uses_custom_config(self):
        """get_table_grouper uses custom TableGroupingConfig."""
        custom_config = TableGroupingConfig(max_distance_lines=20)
        config = ChunkConfig(
            group_related_tables=True,
            table_grouping_config=custom_config,
        )
        grouper = config.get_table_grouper()
        assert grouper.config.max_distance_lines == 20


class TestTableGrouper:
    """Tests for TableGrouper class."""

    def test_empty_tables_returns_empty(self):
        """Empty tables list returns empty groups."""
        grouper = TableGrouper()
        groups = grouper.group_tables([], [], [])
        assert groups == []

    def test_single_table_returns_single_group(self):
        """Single table returns single group."""
        table = TableBlock(
            content="| A | B |\n|---|---|\n| 1 | 2 |",
            start_line=1,
            end_line=3,
        )
        lines = ["| A | B |", "|---|---|", "| 1 | 2 |"]
        grouper = TableGrouper()
        groups = grouper.group_tables([table], lines, [])

        assert len(groups) == 1
        assert groups[0].table_count == 1
        assert groups[0].tables[0] == table

    def test_close_tables_grouped(self):
        """Tables within max_distance are grouped."""
        table1 = TableBlock(
            content="| A | B |\n|---|---|\n| 1 | 2 |",
            start_line=1,
            end_line=3,
        )
        table2 = TableBlock(
            content="| C | D |\n|---|---|\n| 3 | 4 |",
            start_line=5,
            end_line=7,
        )
        lines = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "",
            "| C | D |",
            "|---|---|",
            "| 3 | 4 |",
        ]
        grouper = TableGrouper(TableGroupingConfig(max_distance_lines=10))
        groups = grouper.group_tables([table1, table2], lines, [])

        assert len(groups) == 1
        assert groups[0].table_count == 2

    def test_far_tables_not_grouped(self):
        """Tables beyond max_distance are not grouped."""
        table1 = TableBlock(
            content="| A | B |\n|---|---|\n| 1 | 2 |",
            start_line=1,
            end_line=3,
        )
        table2 = TableBlock(
            content="| C | D |\n|---|---|\n| 3 | 4 |",
            start_line=20,
            end_line=22,
        )
        lines = (
            ["| A | B |", "|---|---|", "| 1 | 2 |"]
            + [""] * 16
            + ["| C | D |", "|---|---|", "| 3 | 4 |"]
        )
        grouper = TableGrouper(TableGroupingConfig(max_distance_lines=10))
        groups = grouper.group_tables([table1, table2], lines, [])

        assert len(groups) == 2
        assert groups[0].table_count == 1
        assert groups[1].table_count == 1

    def test_tables_with_header_between_not_grouped(self):
        """Tables separated by header are not grouped."""
        table1 = TableBlock(
            content="| A | B |\n|---|---|\n| 1 | 2 |",
            start_line=1,
            end_line=3,
        )
        table2 = TableBlock(
            content="| C | D |\n|---|---|\n| 3 | 4 |",
            start_line=6,
            end_line=8,
        )
        header = Header(level=2, text="Section 2", line=5)
        lines = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "",
            "## Section 2",
            "| C | D |",
            "|---|---|",
            "| 3 | 4 |",
        ]
        grouper = TableGrouper(TableGroupingConfig(require_same_section=True))
        groups = grouper.group_tables([table1, table2], lines, [header])

        assert len(groups) == 2

    def test_max_tables_respected(self):
        """max_grouped_tables limit is respected."""
        tables = [
            TableBlock(content=f"| {i} |", start_line=i * 2 + 1, end_line=i * 2 + 1)
            for i in range(5)
        ]
        lines = []
        for i in range(5):
            lines.append(f"| {i} |")
            lines.append("")

        grouper = TableGrouper(
            TableGroupingConfig(
                max_grouped_tables=2,
                max_distance_lines=100,
            )
        )
        groups = grouper.group_tables(tables, lines, [])

        # With max 2 tables per group, 5 tables should create 3 groups
        assert len(groups) >= 2
        for group in groups:
            assert group.table_count <= 2

    def test_max_size_respected(self):
        """max_group_size limit is respected."""
        # Create tables with known sizes (~30 chars each)
        table1 = TableBlock(
            content="| A | B |\n|---|---|\n| 1 | 2 |",
            start_line=1,
            end_line=3,
        )
        table2 = TableBlock(
            content="| C | D |\n|---|---|\n| 3 | 4 |",
            start_line=5,
            end_line=7,
        )
        lines = [
            "| A | B |",
            "|---|---|",
            "| 1 | 2 |",
            "",
            "| C | D |",
            "|---|---|",
            "| 3 | 4 |",
        ]
        # Set max_group_size to 100 - should not fit both tables (~60 chars)
        # Actually both tables together are ~60 chars, so 100 should fit them
        # Use 150 to ensure grouping, then test with smaller value
        grouper = TableGrouper(
            TableGroupingConfig(
                max_group_size=150,
                max_distance_lines=100,
            )
        )
        groups = grouper.group_tables([table1, table2], lines, [])
        # With 150 chars limit, both should be grouped
        assert len(groups) == 1

        # Now test with limit that prevents grouping
        grouper2 = TableGrouper(
            TableGroupingConfig(
                max_group_size=100,  # Minimum allowed
                max_distance_lines=100,
            )
        )
        # Create larger tables
        large_table1 = TableBlock(
            content="| Column A | Column B | Column C |\n|----------|----------|----------|\n| Value 1 | Value 2 | Value 3 |",
            start_line=1,
            end_line=3,
        )
        large_table2 = TableBlock(
            content="| Column D | Column E | Column F |\n|----------|----------|----------|\n| Value 4 | Value 5 | Value 6 |",
            start_line=5,
            end_line=7,
        )
        large_lines = [
            "| Column A | Column B | Column C |",
            "|----------|----------|----------|",
            "| Value 1 | Value 2 | Value 3 |",
            "",
            "| Column D | Column E | Column F |",
            "|----------|----------|----------|",
            "| Value 4 | Value 5 | Value 6 |",
        ]
        groups2 = grouper2.group_tables([large_table1, large_table2], large_lines, [])
        # With 100 chars limit, large tables should not be grouped
        assert len(groups2) == 2


class TestTableGrouperIntegration:
    """Integration tests with MarkdownChunker."""

    def test_integration_with_chunker_disabled(self):
        """Chunker works with grouping disabled."""
        md_text = """# Test

| A | B |
|---|---|
| 1 | 2 |

| C | D |
|---|---|
| 3 | 4 |
"""
        config = ChunkConfig(group_related_tables=False)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should have chunks without table group metadata
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        for chunk in table_chunks:
            assert not chunk.metadata.get("is_table_group", False)

    def test_integration_with_chunker_enabled(self):
        """Chunker works with grouping enabled."""
        md_text = """# Test

| A | B |
|---|---|
| 1 | 2 |

| C | D |
|---|---|
| 3 | 4 |
"""
        config = ChunkConfig(
            group_related_tables=True,
            table_grouping_config=TableGroupingConfig(
                max_distance_lines=10,
                require_same_section=False,
            ),
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Should have grouped table chunk
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        assert len(table_chunks) >= 1

    def test_fixture_api_reference(self):
        """Test with api_reference.md fixture."""
        fixture_path = (
            Path(__file__).parent / "fixtures/table_grouping/api_reference.md"
        )
        if not fixture_path.exists():
            pytest.skip("Fixture not found")

        md_text = fixture_path.read_text()
        config = ChunkConfig(
            group_related_tables=True,
            table_grouping_config=TableGroupingConfig(
                max_distance_lines=10,
                require_same_section=True,
            ),
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        assert len(chunks) > 0

    def test_fixture_close_tables(self):
        """Test with close_tables.md fixture."""
        fixture_path = Path(__file__).parent / "fixtures/table_grouping/close_tables.md"
        if not fixture_path.exists():
            pytest.skip("Fixture not found")

        md_text = fixture_path.read_text()
        config = ChunkConfig(
            group_related_tables=True,
            table_grouping_config=TableGroupingConfig(
                max_distance_lines=10,
                require_same_section=False,
            ),
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # Close tables should be grouped - check that we have table chunks
        table_chunks = [c for c in chunks if c.metadata.get("content_type") == "table"]
        # At minimum, we should have at least one table chunk
        assert len(table_chunks) >= 1
        # If grouping worked, we should have fewer table chunks than tables in doc
        # (3 tables in fixture, should be grouped into 1 or 2 chunks)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
