"""
Tests for Stage 2 data structures and types.

This module tests all the core data structures used in Stage 2,
including Chunk, ChunkingResult, ChunkConfig, and StrategyMetrics.
"""

import pytest

from markdown_chunker.chunker.types import (
    Chunk,
    ChunkConfig,
    ChunkingResult,
    ContentType,
    StrategyMetrics,
    StrategyType,
)


class TestChunk:
    """Test cases for Chunk data structure."""

    def test_chunk_creation_valid(self):
        """Test creating a valid chunk."""
        chunk = Chunk(
            content="# Test Header\n\nSome content here.",
            start_line=1,
            end_line=3,
            metadata={"content_type": "text", "strategy": "structural"},
        )

        assert chunk.content == "# Test Header\n\nSome content here."
        assert chunk.start_line == 1
        assert chunk.end_line == 3
        assert chunk.size == len("# Test Header\n\nSome content here.")
        assert chunk.line_count == 3
        assert chunk.content_type == "text"
        assert chunk.strategy == "structural"

    def test_chunk_creation_minimal(self):
        """Test creating chunk with minimal required fields."""
        chunk = Chunk(content="Simple content", start_line=5, end_line=5)

        assert chunk.content == "Simple content"
        assert chunk.start_line == 5
        assert chunk.end_line == 5
        assert chunk.line_count == 1
        assert chunk.content_type == "text"  # default
        assert chunk.strategy == "unknown"  # default

    def test_chunk_invalid_line_numbers(self):
        """Test chunk creation with invalid line numbers."""
        # start_line < 1
        with pytest.raises(ValueError, match="start_line must be >= 1"):
            Chunk(content="test", start_line=0, end_line=1)

        # end_line < start_line
        with pytest.raises(ValueError, match="end_line must be >= start_line"):
            Chunk(content="test", start_line=5, end_line=3)

    def test_chunk_empty_content(self):
        """Test chunk creation with empty or whitespace content."""
        # Empty content
        with pytest.raises(ValueError, match="chunk content cannot be empty"):
            Chunk(content="", start_line=1, end_line=1)

        # Whitespace-only content
        with pytest.raises(ValueError, match="chunk content cannot be empty"):
            Chunk(content="   \n\t  ", start_line=1, end_line=2)

    def test_chunk_metadata_operations(self):
        """Test chunk metadata operations."""
        chunk = Chunk(content="test", start_line=1, end_line=1)

        # Add metadata
        chunk.add_metadata("language", "python")
        chunk.add_metadata("function_name", "test_func")

        assert chunk.get_metadata("language") == "python"
        assert chunk.get_metadata("function_name") == "test_func"
        assert chunk.get_metadata("nonexistent") is None
        assert chunk.get_metadata("nonexistent", "default") == "default"

    def test_chunk_properties(self):
        """Test chunk computed properties."""
        chunk = Chunk(
            content="```python\ndef hello():\n    pass\n```",
            start_line=10,
            end_line=13,
            metadata={
                "content_type": "code",
                "language": "python",
                "allow_oversize": True,
            },
        )

        assert chunk.size == len("```python\ndef hello():\n    pass\n```")
        assert chunk.line_count == 4
        assert chunk.content_type == "code"
        assert chunk.language == "python"
        assert chunk.is_oversize is True


class TestChunkingResult:
    """Test cases for ChunkingResult data structure."""

    def test_chunking_result_creation(self):
        """Test creating a chunking result."""
        chunks = [
            Chunk("content1", 1, 2),
            Chunk("content2", 3, 4),
            Chunk("content3", 5, 6),
        ]

        result = ChunkingResult(
            chunks=chunks,
            strategy_used="code",
            processing_time=0.123,
            total_chars=100,
            total_lines=10,
            content_type="code",
            complexity_score=0.75,
        )

        assert result.chunks == chunks
        assert result.strategy_used == "code"
        assert result.processing_time == 0.123
        assert result.total_chunks == 3
        assert result.success is True
        assert result.fallback_used is False
        assert result.fallback_level == 0

    def test_chunking_result_statistics(self):
        """Test chunking result statistics calculation."""
        chunks = [
            Chunk("short", 1, 1),  # 5 chars
            Chunk("medium content", 2, 2),  # 14 chars
            Chunk("this is a longer piece of content", 3, 3),  # 33 chars (not 37)
        ]

        result = ChunkingResult(
            chunks=chunks, strategy_used="mixed", processing_time=0.05
        )

        assert result.total_chunks == 3
        assert result.min_chunk_size == 5
        assert result.max_chunk_size == 33
        assert result.average_chunk_size == (5 + 14 + 33) / 3

    def test_chunking_result_empty_chunks(self):
        """Test chunking result with no chunks."""
        result = ChunkingResult(
            chunks=[], strategy_used="sentences", processing_time=0.01
        )

        assert result.total_chunks == 0
        assert result.min_chunk_size == 0
        assert result.max_chunk_size == 0
        assert result.average_chunk_size == 0.0
        assert result.success is False  # No chunks=failure

    def test_chunking_result_error_handling(self):
        """Test chunking result error and warning handling."""
        result = ChunkingResult(
            chunks=[Chunk("test", 1, 1)],
            strategy_used="structural",
            processing_time=0.02,
        )

        result.add_error("Test error")
        result.add_warning("Test warning")

        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert "Test error" in result.errors
        assert "Test warning" in result.warnings

    def test_chunking_result_summary(self):
        """Test chunking result summary generation."""
        chunks = [Chunk("test content", 1, 1)]
        result = ChunkingResult(
            chunks=chunks,
            strategy_used="code",
            processing_time=0.1,
            fallback_used=True,
            fallback_level=2,
            total_chars=50,
            complexity_score=0.6,
        )
        result.add_error("Minor error")
        result.add_warning("Minor warning")

        summary = result.get_summary()

        assert summary["success"] is True
        assert summary["total_chunks"] == 1
        assert summary["strategy_used"] == "code"
        assert summary["fallback_used"] is True
        assert summary["fallback_level"] == 2
        assert summary["errors"] == 1
        assert summary["warnings"] == 1
        assert summary["complexity_score"] == 0.6


class TestChunkConfig:
    """Test cases for ChunkConfig configuration."""

    def test_config_default_creation(self):
        """Test creating default configuration."""
        config = ChunkConfig.default()

        assert config.max_chunk_size == 4096
        assert config.min_chunk_size == 512
        assert config.target_chunk_size == 2048
        assert config.overlap_size == 200
        assert config.enable_overlap is True
        assert (
            config.code_ratio_threshold == 0.3
        )  # Updated from 0.7 to match new defaults
        assert config.min_code_blocks == 1  # Updated from 3 to match new defaults
        assert config.allow_oversize is True

    def test_config_factory_methods(self):
        """Test configuration factory methods."""
        # Code-heavy configuration
        code_config = ChunkConfig.for_code_heavy()
        assert code_config.max_chunk_size == 6144
        assert code_config.code_ratio_threshold == 0.5
        assert code_config.min_code_blocks == 2

        # Structured docs configuration
        struct_config = ChunkConfig.for_structured_docs()
        assert struct_config.max_chunk_size == 3072
        assert struct_config.header_count_threshold == 2

        # Large documents configuration
        large_config = ChunkConfig.for_large_documents()
        assert large_config.max_chunk_size == 8192
        assert large_config.enable_streaming is True

        # Compact configuration
        compact_config = ChunkConfig.compact()
        assert compact_config.max_chunk_size == 2048
        assert compact_config.min_chunk_size == 256

    def test_config_validation(self):
        """Test configuration validation."""
        # Invalid max_chunk_size
        with pytest.raises(ValueError, match="max_chunk_size must be positive"):
            ChunkConfig(max_chunk_size=0)

        # Invalid min_chunk_size
        with pytest.raises(ValueError, match="min_chunk_size must be positive"):
            ChunkConfig(min_chunk_size=-1)

        # min >= max - now auto-adjusts instead of raising error
        config = ChunkConfig(min_chunk_size=1000, max_chunk_size=500)
        # Should auto-adjust min_chunk_size to be less than max_chunk_size
        assert config.min_chunk_size < config.max_chunk_size
        assert config.min_chunk_size == 250  # max(1, 500 // 2)

        # Invalid overlap percentage
        with pytest.raises(
            ValueError, match="overlap_percentage must be between 0.0 and 1.0"
        ):
            ChunkConfig(overlap_percentage=1.5)

        # Invalid code ratio threshold
        with pytest.raises(
            ValueError, match="code_ratio_threshold must be between 0.0 and 1.0"
        ):
            ChunkConfig(code_ratio_threshold=2.0)

    def test_config_effective_overlap_size(self):
        """Test effective overlap size calculation."""
        config = ChunkConfig(overlap_size=300, overlap_percentage=0.1)

        # Small chunk - percentage wins
        assert config.get_effective_overlap_size(1000) == 100  # 10% of 1000

        # Large chunk - fixed size wins
        assert config.get_effective_overlap_size(5000) == 300  # Fixed size

        # Very large chunk - percentage wins (10% of 800=80)
        assert config.get_effective_overlap_size(800) == 80  # 10% of 800


class TestStrategyMetrics:
    """Test cases for StrategyMetrics."""

    def test_strategy_metrics_creation(self):
        """Test creating strategy metrics."""
        metrics = StrategyMetrics(
            strategy_name="code",
            can_handle=True,
            quality_score=0.85,
            priority=1,
            final_score=0.925,
            reason="High code ratio detected",
        )

        assert metrics.strategy_name == "code"
        assert metrics.can_handle is True
        assert metrics.quality_score == 0.85
        assert metrics.priority == 1
        assert metrics.final_score == 0.925
        assert metrics.reason == "High code ratio detected"

    def test_strategy_metrics_validation(self):
        """Test strategy metrics validation."""
        # Invalid quality score
        with pytest.raises(
            ValueError, match="quality_score must be between 0.0 and 1.0"
        ):
            StrategyMetrics("test", True, 1.5, 1, 0.5)

        # Invalid priority
        with pytest.raises(ValueError, match="priority must be >= 1"):
            StrategyMetrics("test", True, 0.5, 0, 0.5)

        # Invalid final score
        with pytest.raises(ValueError, match="final_score must be between 0.0 and 1.0"):
            StrategyMetrics("test", True, 0.5, 1, 1.5)


class TestEnums:
    """Test cases for enum types."""

    def test_content_type_enum(self):
        """Test ContentType enum."""
        assert ContentType.CODE.value == "code"
        assert ContentType.TEXT.value == "text"
        assert ContentType.MIXED.value == "mixed"

        # Test all values are unique
        values = [ct.value for ct in ContentType]
        assert len(values) == len(set(values))

    def test_strategy_type_enum(self):
        """Test StrategyType enum."""
        assert StrategyType.CODE.value == "code"
        assert StrategyType.SENTENCES.value == "sentences"

        # Test all values are unique
        values = [st.value for st in StrategyType]
        assert len(values) == len(set(values))
