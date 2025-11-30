"""
Tests for BaseStrategy abstract class and related functionality.

This module tests the base strategy interface and common functionality
that all concrete strategies inherit.
"""

from unittest.mock import Mock

import pytest

from markdown_chunker.chunker.strategies.base import (
    BaseStrategy,
    StrategyConfigError,
    StrategyContentError,
    StrategyError,
)
from markdown_chunker.chunker.types import ChunkConfig, StrategyMetrics
from markdown_chunker.parser.types import ContentAnalysis


class MockStrategy(BaseStrategy):
    """Mock strategy implementation for testing."""

    def __init__(
        self, name="mock", priority=1, can_handle_result=True, quality_score=0.8
    ):
        self._name = name
        self._priority = priority
        self._can_handle_result = can_handle_result
        self._quality_score = quality_score

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority(self) -> int:
        return self._priority

    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        return self._can_handle_result

    def calculate_quality(self, analysis: ContentAnalysis) -> float:
        return self._quality_score

    def apply(self, content: str, stage1_results, config: ChunkConfig):
        # Simple mock implementation
        return [self._create_chunk(content, 1, 1, "text")]


class TestBaseStrategy:
    """Test cases for BaseStrategy abstract class."""

    def test_abstract_methods_required(self):
        """Test that BaseStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseStrategy()

    def test_mock_strategy_creation(self):
        """Test creating a mock strategy."""
        strategy = MockStrategy("test_strategy", 2, True, 0.9)

        assert strategy.name == "test_strategy"
        assert strategy.priority == 2
        assert str(strategy) == "test_strategy (priority: 2)"
        assert "MockStrategy" in repr(strategy)

    def test_get_metrics_can_handle(self):
        """Test get_metrics when strategy can handle content."""
        strategy = MockStrategy("test", 1, True, 0.8)
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        metrics = strategy.get_metrics(analysis, config)

        assert isinstance(metrics, StrategyMetrics)
        assert metrics.strategy_name == "test"
        assert metrics.can_handle is True
        assert metrics.quality_score == 0.8
        assert metrics.priority == 1
        assert metrics.final_score > 0  # Should be calculated
        assert "can handle" in metrics.reason

    def test_get_metrics_cannot_handle(self):
        """Test get_metrics when strategy cannot handle content."""
        strategy = MockStrategy("test", 2, False, 0.8)
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        metrics = strategy.get_metrics(analysis, config)

        assert metrics.strategy_name == "test"
        assert metrics.can_handle is False
        assert metrics.quality_score == 0.0  # Should be 0 when can't handle
        assert metrics.final_score == 0.0
        assert "cannot handle" in metrics.reason

    def test_final_score_calculation(self):
        """Test final score calculation combining priority and quality."""
        # High priority (1), high quality
        strategy1 = MockStrategy("high_pri", 1, True, 0.9)
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        metrics1 = strategy1.get_metrics(analysis, config)

        # Low priority (6), high quality
        strategy2 = MockStrategy("low_pri", 6, True, 0.9)
        metrics2 = strategy2.get_metrics(analysis, config)

        # Higher priority should result in higher final score
        assert metrics1.final_score > metrics2.final_score

    def test_create_chunk_helper(self):
        """Test _create_chunk helper method."""
        strategy = MockStrategy()

        chunk = strategy._create_chunk(
            content="test content",
            start_line=5,
            end_line=7,
            content_type="code",
            language="python",
            function_name="test_func",
        )

        assert chunk.content == "test content"
        assert chunk.start_line == 5
        assert chunk.end_line == 7
        assert chunk.metadata["strategy"] == "mock"
        assert chunk.metadata["content_type"] == "code"
        assert chunk.metadata["language"] == "python"
        assert chunk.metadata["function_name"] == "test_func"
        assert chunk.metadata["size_bytes"] == len("test content")

    def test_validate_chunks_empty_content(self):
        """Test chunk validation removes empty chunks."""
        strategy = MockStrategy()
        config = ChunkConfig.default()

        # Create valid chunks first
        chunks = [
            strategy._create_chunk("valid content", 1, 1),
            strategy._create_chunk("another valid", 3, 3),
        ]

        # Manually create chunks with empty content (bypassing validation)
        whitespace_chunk = strategy._create_chunk("temp", 2, 2)
        whitespace_chunk.content = "   \n\t  "  # Make it whitespace after creation
        chunks.insert(1, whitespace_chunk)

        empty_chunk = strategy._create_chunk("temp", 4, 4)
        empty_chunk.content = ""  # Make it empty after creation
        chunks.append(empty_chunk)

        validated = strategy._validate_chunks(chunks, config)

        # Should only have 2 valid chunks
        assert len(validated) == 2
        assert validated[0].content == "valid content"
        assert validated[1].content == "another valid"

    def test_validate_chunks_oversize_warning(self):
        """Test chunk validation adds oversize warnings."""
        strategy = MockStrategy()
        config = ChunkConfig(
            max_chunk_size=100, min_chunk_size=10, allow_oversize=False
        )

        # Create oversized chunk
        large_content = "x" * 150  # Larger than max_chunk_size
        chunk = strategy._create_chunk(large_content, 1, 1)

        validated = strategy._validate_chunks([chunk], config)

        assert len(validated) == 1
        assert "size_warning" in validated[0].metadata
        assert "exceeds limit" in validated[0].metadata["size_warning"]

    def test_validate_chunks_adds_missing_metadata(self):
        """Test chunk validation adds missing required metadata."""
        strategy = MockStrategy()
        config = ChunkConfig.default()

        # Create chunk without metadata
        chunk = strategy._create_chunk("test", 1, 1)
        # Remove required metadata
        del chunk.metadata["strategy"]
        del chunk.metadata["content_type"]

        validated = strategy._validate_chunks([chunk], config)

        assert len(validated) == 1
        assert validated[0].metadata["strategy"] == "mock"
        assert validated[0].metadata["content_type"] == "text"


class TestStrategyErrors:
    """Test cases for strategy error classes."""

    def test_strategy_error_creation(self):
        """Test creating StrategyError."""
        error = StrategyError("test_strategy", "Something went wrong")

        assert error.strategy_name == "test_strategy"
        assert "test_strategy: Something went wrong" in str(error)
        assert error.original_error is None

    def test_strategy_error_with_original(self):
        """Test StrategyError with original exception."""
        original = ValueError("Original error")
        error = StrategyError("test_strategy", "Wrapper message", original)

        assert error.strategy_name == "test_strategy"
        assert error.original_error is original
        assert "test_strategy: Wrapper message" in str(error)

    def test_strategy_config_error(self):
        """Test StrategyConfigError inheritance."""
        error = StrategyConfigError("test_strategy", "Config invalid")

        assert isinstance(error, StrategyError)
        assert error.strategy_name == "test_strategy"

    def test_strategy_content_error(self):
        """Test StrategyContentError inheritance."""
        error = StrategyContentError("test_strategy", "Cannot handle content")

        assert isinstance(error, StrategyError)
        assert error.strategy_name == "test_strategy"


class TestStrategyComparison:
    """Test cases for strategy comparison and selection."""

    def test_multiple_strategies_comparison(self):
        """Test comparing multiple strategies for selection."""
        strategies = [
            MockStrategy("high_quality", 3, True, 0.9),
            MockStrategy("high_priority", 1, True, 0.6),
            MockStrategy("cannot_handle", 2, False, 0.8),
            MockStrategy("low_everything", 5, True, 0.3),
        ]

        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        # Get metrics for all strategies
        metrics = [s.get_metrics(analysis, config) for s in strategies]

        # Filter to only those that can handle
        applicable = [m for m in metrics if m.can_handle]

        # Sort by final score (descending)
        applicable.sort(key=lambda m: m.final_score, reverse=True)

        # High priority strategy should win despite lower quality
        assert applicable[0].strategy_name == "high_priority"
        assert len(applicable) == 3  # 3 can handle, 1 cannot

    def test_strategy_selection_edge_cases(self):
        """Test strategy selection edge cases."""
        analysis = Mock(spec=ContentAnalysis)
        config = ChunkConfig.default()

        # Strategy with quality score exactly 0.0
        zero_quality = MockStrategy("zero", 1, True, 0.0)
        metrics = zero_quality.get_metrics(analysis, config)
        assert metrics.quality_score == 0.0
        assert metrics.final_score > 0.0  # Still has priority weight

        # Strategy with quality score exactly 1.0
        perfect_quality = MockStrategy("perfect", 1, True, 1.0)
        metrics = perfect_quality.get_metrics(analysis, config)
        assert metrics.quality_score == 1.0
        assert metrics.final_score <= 1.0
