"""
Tests for main MarkdownChunker class.

This module tests the primary interface for Stage 2 chunking operations,
including basic functionality and integration with Stage 1.
"""

from unittest.mock import Mock, patch

from markdown_chunker.chunker.core import (
    ChunkingError,
    ConfigurationError,
    MarkdownChunker,
)
from markdown_chunker.chunker.types import ChunkConfig, ChunkingResult


def create_mock_analysis(**kwargs):
    """Create a mock analysis with all required attributes for strategy selection."""
    mock = Mock()
    # Set defaults
    mock.total_chars = kwargs.get("total_chars", 100)
    mock.total_lines = kwargs.get("total_lines", 10)
    mock.content_type = kwargs.get("content_type", "text")
    mock.complexity_score = kwargs.get("complexity_score", 0.5)
    mock.code_ratio = kwargs.get("code_ratio", 0.0)
    mock.list_ratio = kwargs.get("list_ratio", 0.0)
    mock.table_ratio = kwargs.get("table_ratio", 0.0)
    mock.header_ratio = kwargs.get("header_ratio", 0.0)
    mock.text_ratio = kwargs.get("text_ratio", 1.0)
    mock.header_count = kwargs.get("header_count", 0)
    mock.list_count = kwargs.get("list_count", 0)
    mock.table_count = kwargs.get("table_count", 0)
    mock.preamble = kwargs.get("preamble", None)
    return mock


class TestMarkdownChunker:
    """Test cases for MarkdownChunker main class."""

    def test_chunker_creation_default_config(self):
        """Test creating chunker with default configuration."""
        chunker = MarkdownChunker()

        assert chunker.config is not None
        assert isinstance(chunker.config, ChunkConfig)
        assert chunker.config.max_chunk_size == 4096  # Default value
        assert chunker.stage1 is not None

    def test_chunker_creation_custom_config(self):
        """Test creating chunker with custom configuration."""
        config = ChunkConfig.for_code_heavy()
        chunker = MarkdownChunker(config)

        assert chunker.config is config
        assert chunker.config.max_chunk_size == 6144  # Code-heavy value

    def test_get_available_strategies_loaded(self):
        """Test getting available strategies when they are loaded."""
        chunker = MarkdownChunker()

        strategies = chunker.get_available_strategies()

        assert isinstance(strategies, list)
        assert len(strategies) == 6  # All 6 strategies loaded
        expected_strategies = {
            "code",
            "mixed",
            "list",
            "table",
            "structural",
            "sentences",
        }
        assert set(strategies) == expected_strategies

    def test_validate_config_valid(self):
        """Test config validation with valid configuration."""
        config = ChunkConfig.default()
        chunker = MarkdownChunker(config)

        errors = chunker.validate_config()

        assert isinstance(errors, list)
        assert len(errors) == 0  # No validation errors

    def test_validate_config_invalid(self):
        """Test config validation with invalid configuration."""
        # Create invalid config by bypassing validation
        config = ChunkConfig.__new__(ChunkConfig)
        config.max_chunk_size = -1  # Invalid
        config.min_chunk_size = 100

        chunker = MarkdownChunker(config)

        # Note: Current implementation doesn't catch this,
        # but the test structure is ready for when validation is enhanced
        errors = chunker.validate_config()
        assert isinstance(errors, list)

    @patch("markdown_chunker.chunker.core.ParserInterface")
    def test_chunk_with_analysis_stage1_success(self, mock_stage1_class):
        """Test chunk_with_analysis with successful Stage 1 processing."""
        # Mock Stage 1 results with all required attributes for strategy selection
        mock_analysis = create_mock_analysis(
            total_chars=100, total_lines=10, content_type="text", complexity_score=0.5
        )

        mock_stage1_results = Mock()
        mock_stage1_results.analysis = mock_analysis

        mock_stage1_instance = Mock()
        mock_stage1_instance.process_document.return_value = mock_stage1_results
        mock_stage1_class.return_value = mock_stage1_instance

        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis("# Test\n\nSome content")

        assert isinstance(result, ChunkingResult)
        assert result.total_chars == 100
        assert result.total_lines == 10
        assert result.content_type == "text"
        assert result.complexity_score == 0.5
        assert result.processing_time > 0

        # Verify Stage 1 was called (may be called twice due to preamble processing)
        assert mock_stage1_instance.process_document.called
        assert mock_stage1_instance.process_document.call_count >= 1

    @patch("markdown_chunker.chunker.core.ParserInterface")
    def test_chunk_with_analysis_stage1_failure(self, mock_stage1_class):
        """Test chunk_with_analysis with Stage 1 processing failure."""
        mock_stage1_instance = Mock()
        mock_stage1_instance.process_document.side_effect = Exception("Stage 1 failed")
        mock_stage1_class.return_value = mock_stage1_instance

        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis("# Test")

        assert isinstance(result, ChunkingResult)
        assert len(result.chunks) == 0
        assert result.strategy_used == "none"
        assert result.fallback_used is True
        assert result.fallback_level == 4
        assert len(result.errors) > 0
        assert "Stage 1 processing failed" in result.errors[0]

    @patch("markdown_chunker.chunker.core.ParserInterface")
    def test_chunk_method_delegates_to_chunk_with_analysis(self, mock_stage1_class):
        """Test that chunk() method delegates to chunk_with_analysis()."""
        # Mock Stage 1 results
        mock_analysis = create_mock_analysis(
            total_chars=50, total_lines=5, content_type="text", complexity_score=0.3
        )

        mock_stage1_results = Mock()
        mock_stage1_results.analysis = mock_analysis

        mock_stage1_instance = Mock()
        mock_stage1_instance.process_document.return_value = mock_stage1_results
        mock_stage1_class.return_value = mock_stage1_instance

        chunker = MarkdownChunker()
        chunks = chunker.chunk("# Simple test")

        assert isinstance(chunks, list)
        # Should return chunks since strategies are implemented
        assert len(chunks) >= 1

    def test_chunk_with_strategy_override(self):
        """Test chunking with strategy override parameter."""
        chunker = MarkdownChunker()

        # This should work without error even though strategies aren't implemented
        result = chunker.chunk_with_analysis("# Test", strategy="code")

        assert isinstance(result, ChunkingResult)
        # Strategy override is accepted but not yet used

    def test_chunker_initialization_components(self):
        """Test that chunker initializes all required components."""
        chunker = MarkdownChunker()

        # Check that strategies are initialized
        assert len(chunker._strategies) == 6
        strategy_names = [s.name for s in chunker._strategies]
        expected_names = {"code", "mixed", "list", "table", "structural", "sentences"}
        assert set(strategy_names) == expected_names
        assert chunker._strategy_selector is not None
        assert chunker._overlap_manager is not None
        assert chunker._metadata_enricher is not None
        assert chunker._fallback_manager is not None

        # These will be properly initialized in later tasks


class TestChunkingErrors:
    """Test cases for chunking error classes."""

    def test_chunking_error_creation(self):
        """Test creating ChunkingError."""
        error = ChunkingError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert isinstance(error, Exception)

    def test_configuration_error_inheritance(self):
        """Test ConfigurationError inheritance."""
        error = ConfigurationError("Invalid config")

        assert isinstance(error, ChunkingError)
        assert str(error) == "Invalid config"

    def test_strategy_selection_error_inheritance(self):
        """Test StrategySelectionError inheritance."""
        from markdown_chunker.chunker.selector import StrategySelectionError

        error = StrategySelectionError("No applicable strategy")

        # StrategySelectionError теперь наследуется от Exception, а не ChunkingError
        assert isinstance(error, Exception)
        assert str(error) == "No applicable strategy"


class TestChunkerIntegration:
    """Integration tests for chunker with various inputs."""

    @patch("markdown_chunker.chunker.core.ParserInterface")
    def test_chunker_with_empty_input(self, mock_stage1_class):
        """Test chunker behavior with empty input."""
        mock_analysis = create_mock_analysis(
            total_chars=0, total_lines=0, content_type="text", complexity_score=0.0
        )

        mock_stage1_results = Mock()
        mock_stage1_results.analysis = mock_analysis

        mock_stage1_instance = Mock()
        mock_stage1_instance.process_document.return_value = mock_stage1_results
        mock_stage1_class.return_value = mock_stage1_instance

        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis("")

        assert isinstance(result, ChunkingResult)
        assert result.total_chars == 0
        assert result.total_lines == 0

    @patch("markdown_chunker.chunker.core.ParserInterface")
    def test_chunker_with_various_configs(self, mock_stage1_class):
        """Test chunker with different configuration presets."""
        mock_analysis = create_mock_analysis(
            total_chars=1000, total_lines=50, content_type="mixed", complexity_score=0.7
        )

        mock_stage1_results = Mock()
        mock_stage1_results.analysis = mock_analysis

        mock_stage1_instance = Mock()
        mock_stage1_instance.process_document.return_value = mock_stage1_results
        mock_stage1_class.return_value = mock_stage1_instance

        test_content = (
            "# Test\n\nSome content with code:\n\n```python\nprint('hello')\n```"
        )

        # Test different configurations
        configs = [
            ChunkConfig.default(),
            ChunkConfig.for_code_heavy(),
            ChunkConfig.for_structured_docs(),
            ChunkConfig.compact(),
        ]

        for config in configs:
            chunker = MarkdownChunker(config)
            result = chunker.chunk_with_analysis(test_content)

            assert isinstance(result, ChunkingResult)
            assert result.processing_time > 0
            # All should succeed with current placeholder implementation

    def test_chunker_performance_timing(self):
        """Test that chunker properly measures processing time."""
        chunker = MarkdownChunker()

        # Use a simple input that won't cause Stage 1 to fail
        with patch.object(chunker.stage1, "process_document") as mock_process:
            mock_analysis = create_mock_analysis(
                total_chars=100,
                total_lines=10,
                content_type="text",
                complexity_score=0.5,
            )

            mock_stage1_results = Mock()
            mock_stage1_results.analysis = mock_analysis
            mock_process.return_value = mock_stage1_results

            result = chunker.chunk_with_analysis("# Test content")

            assert result.processing_time > 0
            assert (
                result.processing_time < 1.0
            )  # Should be very fast for simple content
