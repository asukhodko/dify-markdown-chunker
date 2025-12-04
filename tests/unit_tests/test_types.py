"""Unit tests for core data types."""

import pytest

from markdown_chunker.types import (
    Chunk,
    ChunkingResult,
    ConfigurationError,
    ContentAnalysis,
    FencedBlock,
    Header,
    Table,
    ValidationError,
)


class TestChunk:
    """Test Chunk dataclass."""

    def test_chunk_creation(self):
        """Test basic chunk creation."""
        chunk = Chunk(
            content="# Hello World",
            start_line=1,
            end_line=1,
            metadata={"test": "value"},
        )
        assert chunk.content == "# Hello World"
        assert chunk.start_line == 1
        assert chunk.end_line == 1
        assert chunk.size == 13
        assert chunk.line_count == 1

    def test_chunk_validation_empty_content(self):
        """Test that empty content raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Chunk(content="   ", start_line=1, end_line=1)

    def test_chunk_validation_invalid_start_line(self):
        """Test that start_line < 1 raises error."""
        with pytest.raises(ValueError, match="start_line must be >= 1"):
            Chunk(content="test", start_line=0, end_line=1)

    def test_chunk_validation_invalid_line_range(self):
        """Test that end_line < start_line raises error."""
        with pytest.raises(ValueError, match="end_line .* must be >="):
            Chunk(content="test", start_line=5, end_line=3)

    def test_chunk_metadata_operations(self):
        """Test metadata add/get operations."""
        chunk = Chunk(content="test", start_line=1, end_line=1)
        chunk.add_metadata("key", "value")
        assert chunk.get_metadata("key") == "value"
        assert chunk.get_metadata("missing", "default") == "default"


class TestChunkingResult:
    """Test ChunkingResult dataclass."""

    def test_chunking_result_creation(self):
        """Test basic result creation."""
        chunks = [
            Chunk(content="chunk1", start_line=1, end_line=1),
            Chunk(content="chunk2", start_line=2, end_line=2),
        ]
        result = ChunkingResult(
            chunks=chunks,
            strategy_used="test_strategy",
            processing_time=0.5,
        )
        assert result.chunk_count == 2
        assert result.total_size == 12
        assert result.average_chunk_size == 6.0

    def test_chunking_result_serialization(self):
        """Test to_dict / from_dict round-trip."""
        chunks = [
            Chunk(
                content="test",
                start_line=1,
                end_line=1,
                metadata={"key": "value"},
            )
        ]
        result = ChunkingResult(
            chunks=chunks,
            strategy_used="test",
            processing_time=1.0,
            fallback_used=True,
            fallback_level=2,
        )

        # Serialize
        data = result.to_dict()
        assert data["strategy_used"] == "test"
        assert data["fallback_used"] is True

        # Deserialize
        restored = ChunkingResult.from_dict(data)
        assert len(restored.chunks) == 1
        assert restored.chunks[0].content == "test"
        assert restored.strategy_used == "test"
        assert restored.fallback_used is True


class TestContentAnalysis:
    """Test ContentAnalysis dataclass."""

    def test_content_analysis_creation(self):
        """Test basic analysis creation."""
        analysis = ContentAnalysis(
            total_chars=1000,
            total_lines=50,
            code_ratio=0.3,
            text_ratio=0.7,
            code_block_count=5,
            header_count=3,
            max_header_depth=2,
            table_count=1,
            content_type="mixed",
            languages={"python", "javascript"},
        )
        assert analysis.total_chars == 1000
        assert analysis.content_type == "mixed"
        assert "python" in analysis.languages

    def test_content_analysis_validation_code_ratio(self):
        """Test that invalid code_ratio raises error."""
        with pytest.raises(ValueError, match="code_ratio"):
            ContentAnalysis(
                total_chars=100,
                total_lines=10,
                code_ratio=1.5,  # Invalid
                text_ratio=0.5,
                code_block_count=0,
                header_count=0,
                max_header_depth=0,
                table_count=0,
                content_type="text",
            )

    def test_content_analysis_validation_content_type(self):
        """Test that invalid content_type raises error."""
        with pytest.raises(ValueError, match="content_type"):
            ContentAnalysis(
                total_chars=100,
                total_lines=10,
                code_ratio=0.5,
                text_ratio=0.5,
                code_block_count=0,
                header_count=0,
                max_header_depth=0,
                table_count=0,
                content_type="invalid",  # Invalid
            )


class TestFencedBlock:
    """Test FencedBlock dataclass."""

    def test_fenced_block_creation(self):
        """Test basic fenced block creation."""
        block = FencedBlock(
            content='print("hello")',
            language="python",
            fence_type="```",
            start_line=5,
            end_line=7,
        )
        assert block.content == 'print("hello")'
        assert block.language == "python"


class TestHeader:
    """Test Header dataclass."""

    def test_header_creation(self):
        """Test basic header creation."""
        header = Header(level=2, text="Section Title", line_number=10)
        assert header.level == 2
        assert header.text == "Section Title"

    def test_header_validation_invalid_level(self):
        """Test that invalid header level raises error."""
        with pytest.raises(ValueError, match="Header level must be 1-6"):
            Header(level=7, text="Invalid", line_number=1)


class TestTable:
    """Test Table dataclass."""

    def test_table_creation(self):
        """Test basic table creation."""
        table = Table(
            content="| Col1 | Col2 |\n|------|------|\n| A    | B    |",
            start_line=5,
            end_line=7,
            row_count=2,
        )
        assert table.row_count == 2
        assert table.start_line == 5
