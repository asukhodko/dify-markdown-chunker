"""
Tests for FallbackManager.

This module tests the error handling and fallback chain functionality
that ensures chunking always succeeds with a 3-level system:
- Level 0: Primary strategy
- Level 1: Structural fallback
- Level 2: Sentences fallback (final)
"""

from unittest.mock import Mock

from markdown_chunker.chunker.components.fallback_manager import (
    FallbackError,
    FallbackLevel,
    FallbackManager,
    create_fallback_manager,
    validate_fallback_chain,
)
from markdown_chunker.chunker.strategies.base import BaseStrategy, StrategyError
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import Stage1Results


class MockStrategy(BaseStrategy):
    """Mock strategy for testing fallback behavior."""

    def __init__(
        self,
        name: str,
        priority: int,
        should_fail: bool = False,
        return_empty: bool = False,
        exception_type: Exception = None,
    ):
        self._name = name
        self._priority = priority
        self.should_fail = should_fail
        self.return_empty = return_empty
        self.exception_type = exception_type or StrategyError(name, "Mock failure")

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority(self) -> int:
        return self._priority

    def can_handle(self, analysis, config) -> bool:
        return True

    def calculate_quality(self, analysis, config) -> float:
        return 0.5

    def apply(self, content: str, stage1_results, config):
        if self.should_fail:
            raise self.exception_type

        if self.return_empty:
            return []

        # Return a simple chunk
        return [self._create_chunk(content, 1, 1, "text")]


class TestFallbackManager:
    """Test cases for FallbackManager with 2-level system."""

    def test_manager_creation(self):
        """Test creating fallback manager."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        assert manager.config is config
        assert manager._fallback_strategy is not None
        assert manager._fallback_strategy.name == "sentences"

    def test_primary_strategy_success(self):
        """Test successful execution with primary strategy."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        primary_strategy = MockStrategy("primary", 1)
        stage1_results = Mock(spec=Stage1Results)
        content = "Test content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        assert result.strategy_used == "primary"
        assert result.fallback_used is False
        assert result.fallback_level == 0
        assert len(result.chunks) == 1
        assert len(result.errors) == 0

    def test_primary_strategy_failure_fallback_to_structural(self):
        """Test fallback to structural strategy when primary fails."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Primary strategy that fails
        primary_strategy = MockStrategy("primary", 1, should_fail=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nTest content with sentences. This is another sentence."

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        # Should fallback to structural first (level 1), or sentences (level 2)
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]  # Structural or Sentences
        assert len(result.chunks) >= 1
        assert len(result.errors) >= 1  # Primary strategy error
        assert "Primary strategy primary failed" in result.errors[0]

    def test_primary_strategy_returns_empty_fallback(self):
        """Test fallback when primary strategy returns empty chunks."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Primary strategy that returns empty
        primary_strategy = MockStrategy("primary", 1, return_empty=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nTest content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        # Should fallback to structural (level 1) or sentences (level 2)
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]
        assert len(result.chunks) >= 1
        assert len(result.warnings) >= 1  # Primary strategy warning

    def test_sentences_strategy_is_primary_uses_structural(self):
        """Test that when sentences is primary and fails, structural is tried."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Use sentences strategy as primary (which will fail)
        sentences_strategy = MockStrategy("sentences", 1, should_fail=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nTest content"

        result = manager.execute_with_fallback(
            content, stage1_results, sentences_strategy
        )

        # Should try structural fallback (level 1), then return empty if all fail
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]  # Structural or final failure
        assert len(result.errors) >= 1

    def test_all_strategies_fail_returns_empty(self):
        """Test that when all strategies fail, empty result is returned."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Primary strategy that fails
        primary_strategy = MockStrategy("primary", 1, should_fail=True)

        # Mock both fallback strategies to also fail
        manager._structural_strategy = MockStrategy("structural", 2, should_fail=True)
        manager._sentences_strategy = MockStrategy("sentences", 6, should_fail=True)
        manager._fallback_strategy = manager._sentences_strategy

        stage1_results = Mock(spec=Stage1Results)
        content = "Test content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        assert result.strategy_used == "none"
        assert result.fallback_used is True
        assert result.fallback_level == 2  # Final level
        assert len(result.chunks) == 0
        assert len(result.errors) >= 2  # Multiple strategies failed

    def test_validate_fallback_chain_valid(self):
        """Test validation of valid fallback chain."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        issues = manager.validate_fallback_chain()

        # Should have no issues with default config
        assert len(issues) == 0

    def test_validate_fallback_chain_disabled(self):
        """Test validation when fallback is disabled."""
        config = ChunkConfig(enable_fallback=False)
        manager = FallbackManager(config)

        issues = manager.validate_fallback_chain()

        assert len(issues) >= 1
        assert any("disabled" in issue for issue in issues)

    def test_get_fallback_statistics(self):
        """Test getting fallback statistics."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        stats = manager.get_fallback_statistics()

        assert stats["fallback_enabled"] is True
        assert stats["max_fallback_level"] == 2  # 3 levels (0, 1, 2)
        assert stats["sentences_strategy"] == "sentences"
        assert stats["structural_strategy"] == "structural"

    def test_fallback_metadata_added(self):
        """Test that fallback metadata is added to chunks."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Primary strategy that fails
        primary_strategy = MockStrategy("primary", 1, should_fail=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nTest content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        # Check that fallback metadata was added
        for chunk in result.chunks:
            assert "fallback_level" in chunk.metadata
            assert "fallback_reason" in chunk.metadata
            assert chunk.metadata["fallback_level"] in [1, 2]  # Structural or Sentences
            assert "Primary strategy failed" in chunk.metadata["fallback_reason"]

    def test_fallback_level_enum_values(self):
        """Test that FallbackLevel enum has correct values."""
        assert FallbackLevel.PRIMARY.value == 0
        assert FallbackLevel.STRUCTURAL.value == 1
        assert FallbackLevel.SENTENCES.value == 2
        assert FallbackLevel.FALLBACK.value == 1  # Backward compatibility alias

    def test_primary_returns_empty_triggers_fallback(self):
        """Test that primary returning empty chunks triggers fallback."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        primary_strategy = MockStrategy("primary", 1, return_empty=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nTest content with multiple sentences. This should work."

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]  # Structural or Sentences
        assert result.strategy_used in ["structural", "sentences"]
        assert len(result.chunks) > 0


class TestFallbackUtilities:
    """Test utility functions for fallback management."""

    def test_create_fallback_manager(self):
        """Test creating fallback manager with utility function."""
        config = ChunkConfig.default()
        manager = create_fallback_manager(config)

        assert isinstance(manager, FallbackManager)
        assert manager.config is config

    def test_test_fallback_chain(self):
        """Test the fallback chain testing utility."""
        config = ChunkConfig.default()

        strategies = [
            MockStrategy("working", 1),
            MockStrategy("failing", 2, should_fail=True),
            MockStrategy("empty", 3, return_empty=True),
        ]

        results = validate_fallback_chain("Test content", config, strategies)

        assert len(results) == 3
        assert results["working"]["success"] is True
        assert results["failing"]["fallback_used"] is True
        assert results["empty"]["fallback_used"] is True


class TestFallbackError:
    """Test FallbackError exception."""

    def test_fallback_error_creation(self):
        """Test creating FallbackError with error list."""
        errors = ["Error 1", "Error 2", "Error 3"]
        error = FallbackError("All strategies failed", errors)

        assert str(error) == "All strategies failed"
        assert error.errors == errors
        assert len(error.errors) == 3


class TestFallbackIntegration:
    """Integration tests for fallback manager."""

    def test_realistic_fallback_scenario(self):
        """Test realistic scenario with actual strategies."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Simulate a code strategy that fails
        code_strategy = MockStrategy("code", 1, should_fail=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "# Header\n\nThis is regular text content."

        result = manager.execute_with_fallback(content, stage1_results, code_strategy)

        # Should fall back to structural (level 1) or sentences (level 2)
        assert result.strategy_used in ["structural", "sentences"]
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]
        assert len(result.chunks) > 0

    def test_complete_failure_scenario(self):
        """Test scenario where all strategies fail."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        # Mock all strategies to fail
        primary_strategy = MockStrategy("primary", 1, should_fail=True)
        manager._structural_strategy = MockStrategy("structural", 2, should_fail=True)
        manager._sentences_strategy = MockStrategy("sentences", 6, should_fail=True)
        manager._fallback_strategy = manager._sentences_strategy

        stage1_results = Mock(spec=Stage1Results)
        content = "Test content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        # Should return empty result with errors
        assert result.strategy_used == "none"
        assert result.fallback_used is True
        assert result.fallback_level == 2  # Final level
        assert len(result.chunks) == 0
        assert len(result.errors) >= 2

    def test_fallback_preserves_errors_and_warnings(self):
        """Test that fallback preserves all errors and warnings."""
        config = ChunkConfig.default()
        manager = FallbackManager(config)

        primary_strategy = MockStrategy("primary", 1, should_fail=True)
        stage1_results = Mock(spec=Stage1Results)
        content = "Test content"

        result = manager.execute_with_fallback(
            content, stage1_results, primary_strategy
        )

        # Should have error from primary strategy
        assert len(result.errors) >= 1
        assert "primary failed" in result.errors[0].lower()

        # Fallback should succeed, so no additional errors
        assert result.strategy_used == "sentences"
        assert len(result.chunks) > 0
