"""
Tests for fallback manager initialization in MarkdownChunker.

This module tests that the fallback manager is properly initialized
with the 3-level fallback system:
- Level 0: Primary strategy
- Level 1: Structural fallback
- Level 2: Sentences fallback (final)
"""

from unittest.mock import Mock, patch

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.strategies.sentences_strategy import SentencesStrategy
from markdown_chunker.chunker.strategies.structural_strategy import StructuralStrategy
from markdown_chunker.chunker.types import ChunkConfig


class TestStructuralStrategyInitialization:
    """Test fallback manager initialization with 3-level system."""

    def test_fallback_strategy_is_set_in_init(self):
        """Test that fallback strategies are set in FallbackManager during initialization."""
        chunker = MarkdownChunker()

        # Verify that both fallback strategies are set
        assert chunker._fallback_manager._fallback_strategy is not None
        assert chunker._fallback_manager._sentences_strategy is not None
        assert chunker._fallback_manager._structural_strategy is not None

    def test_fallback_strategy_types_are_correct(self):
        """Test that the fallback strategies are of correct types."""
        chunker = MarkdownChunker()

        assert isinstance(
            chunker._fallback_manager._sentences_strategy, SentencesStrategy
        )
        assert isinstance(
            chunker._fallback_manager._structural_strategy, StructuralStrategy
        )

    def test_fallback_manager_has_3_level_chain(self):
        """Test that FallbackManager has 3-level fallback chain."""
        chunker = MarkdownChunker()
        fallback_manager = chunker._fallback_manager

        # Verify both fallback strategies are available
        assert fallback_manager._structural_strategy is not None
        assert fallback_manager._sentences_strategy is not None

        # Verify statistics reflect 3-level system
        stats = fallback_manager.get_fallback_statistics()
        assert (
            stats["max_fallback_level"] == 2
        )  # 0 (primary), 1 (structural), 2 (sentences)

    def test_fallback_chain_execution_through_levels(self):
        """Test that fallback chain can execute through all levels."""
        chunker = MarkdownChunker()

        # Test fallback directly through fallback manager
        failing_strategy = Mock()
        failing_strategy.name = "code"
        failing_strategy.apply.side_effect = Exception("Primary failed")

        # Execute with fallback
        result = chunker._fallback_manager.execute_with_fallback(
            "# Test\n\nContent with sentences.",
            Mock(analysis=Mock()),
            failing_strategy,
        )

        # Verify fallback was used (structural or sentences)
        assert result.strategy_used in ["structural", "sentences"]
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]
        assert len(result.chunks) > 0

    def test_fallback_strategy_used_in_fallback(self):
        """Test that fallback strategy is actually used in fallback chain."""
        chunker = MarkdownChunker()

        # Create a primary strategy that will fail
        failing_strategy = Mock()
        failing_strategy.name = "failing"
        failing_strategy.apply.side_effect = Exception("Primary failed")

        # Execute with fallback
        result = chunker._fallback_manager.execute_with_fallback(
            "# Test\n\nContent with sentences.",
            Mock(analysis=Mock()),
            failing_strategy,
        )

        # Verify fallback strategy was used
        assert result.strategy_used in ["structural", "sentences"]
        assert result.fallback_used is True
        assert result.fallback_level in [1, 2]
        assert len(result.chunks) > 0

    def test_initialization_with_custom_config(self):
        """Test that fallback manager initialization works with custom config."""
        custom_config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(custom_config)

        # Verify fallback strategies are still set
        assert chunker._fallback_manager._sentences_strategy is not None
        assert chunker._fallback_manager._structural_strategy is not None

        # Verify config is passed correctly
        assert chunker.config.max_chunk_size == 1000

    def test_structural_strategy_is_available(self):
        """Test that structural strategy is available in fallback chain."""
        chunker = MarkdownChunker()

        # Verify that fallback manager has structural strategy
        assert hasattr(chunker._fallback_manager, "_structural_strategy")
        assert chunker._fallback_manager._structural_strategy.name == "structural"

    def test_sentences_strategy_is_final_fallback(self):
        """Test that sentences strategy is the final fallback."""
        chunker = MarkdownChunker()

        fallback = chunker._fallback_manager._sentences_strategy

        assert fallback is not None
        assert fallback.name == "sentences"
        assert isinstance(fallback, SentencesStrategy)

    def test_fallback_manager_config_consistency(self):
        """Test that FallbackManager uses the same config as chunker."""
        config = ChunkConfig(max_chunk_size=2000)
        chunker = MarkdownChunker(config)

        # Verify config consistency
        assert chunker._fallback_manager.config == config
        assert chunker._fallback_manager.config.max_chunk_size == 2000

    def test_all_strategies_fail_returns_empty(self):
        """Test that when all strategies fail, empty result is returned."""
        chunker = MarkdownChunker()

        # Mock all strategies to fail
        failing_primary = Mock()
        failing_primary.name = "primary"
        failing_primary.apply.side_effect = Exception("Primary failed")

        # Mock both fallbacks to also fail
        with patch.object(
            chunker._fallback_manager._structural_strategy,
            "apply",
            side_effect=Exception("Structural failed"),
        ):
            with patch.object(
                chunker._fallback_manager._sentences_strategy,
                "apply",
                side_effect=Exception("Sentences failed"),
            ):
                result = chunker._fallback_manager.execute_with_fallback(
                    "# Test",
                    Mock(analysis=Mock()),
                    failing_primary,
                )

                # Should return empty result with errors
                assert result.strategy_used == "none"
                assert result.fallback_used is True
                assert result.fallback_level == 2  # Final level
                assert len(result.chunks) == 0
                assert len(result.errors) >= 2
