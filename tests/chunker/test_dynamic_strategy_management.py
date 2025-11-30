"""
Tests for dynamic strategy management in MarkdownChunker.

This module tests that strategies can be added and removed dynamically
without breaking the strategy selector.
"""

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.strategies.base import BaseStrategy
from markdown_chunker.chunker.types import Chunk


class MockStrategy(BaseStrategy):
    """Mock strategy for testing."""

    def __init__(self, strategy_name: str, strategy_priority: int = 10):
        self._name = strategy_name
        self._priority = strategy_priority

    @property
    def name(self) -> str:
        return self._name

    @property
    def priority(self) -> int:
        return self._priority

    def can_handle(self, analysis, config):
        return True

    def apply(self, md_text, stage1_results, config):
        return [Chunk(f"Mock {self.name} chunk", 1, 1, {})]

    def calculate_quality(self, analysis):
        return 0.5


class TestDynamicStrategyManagement:
    """Test dynamic strategy management."""

    def test_add_strategy_recreates_selector(self):
        """Test that add_strategy recreates the strategy selector."""
        chunker = MarkdownChunker()

        # Get initial selector
        initial_selector = chunker._strategy_selector
        initial_strategies_count = len(chunker._strategies)

        # Add a new strategy
        mock_strategy = MockStrategy("test_strategy")
        chunker.add_strategy(mock_strategy)

        # Verify strategy was added
        assert len(chunker._strategies) == initial_strategies_count + 1
        assert mock_strategy in chunker._strategies

        # Verify selector was recreated (not None)
        assert chunker._strategy_selector is not None
        assert chunker._strategy_selector != initial_selector

        # Verify selector works
        available_strategies = chunker.get_available_strategies()
        assert "test_strategy" in available_strategies

    def test_strategy_selection_works_after_addition(self):
        """Test that strategy selection works after adding a strategy."""
        chunker = MarkdownChunker()

        # Add a mock strategy
        mock_strategy = MockStrategy("custom_strategy", 1)  # High priority
        chunker.add_strategy(mock_strategy)

        # Test that chunking still works
        chunks = chunker.chunk("# Test\n\nContent")
        assert len(chunks) > 0

        # Test that the new strategy can be selected manually
        chunks = chunker.chunk("# Test", strategy="custom_strategy")
        assert len(chunks) == 1
        assert "Mock custom_strategy chunk" in chunks[0].content

    def test_remove_strategy_works(self):
        """Test that remove_strategy removes the strategy and recreates selector."""
        chunker = MarkdownChunker()

        # Add a strategy first
        mock_strategy = MockStrategy("removable_strategy")
        chunker.add_strategy(mock_strategy)

        # Verify it was added
        assert "removable_strategy" in chunker.get_available_strategies()

        # Remove the strategy
        chunker.remove_strategy("removable_strategy")

        # Verify it was removed
        assert "removable_strategy" not in chunker.get_available_strategies()
        assert mock_strategy not in chunker._strategies

        # Verify selector still works
        assert chunker._strategy_selector is not None
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0

    def test_remove_nonexistent_strategy_safe(self):
        """Test that removing non-existent strategy doesn't break anything."""
        chunker = MarkdownChunker()

        initial_count = len(chunker._strategies)

        # Remove non-existent strategy
        chunker.remove_strategy("nonexistent")

        # Should not change anything
        assert len(chunker._strategies) == initial_count
        assert chunker._strategy_selector is not None

        # Should still work
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0

    def test_selector_mode_preserved_on_add(self):
        """Test that selector mode is preserved when adding strategies."""
        chunker = MarkdownChunker()

        # Change selector mode (if possible)
        # Note: This test assumes StrategySelector has a _mode attribute
        if hasattr(chunker._strategy_selector, "_mode"):
            original_mode = chunker._strategy_selector._mode

            # Add strategy
            mock_strategy = MockStrategy("mode_test")
            chunker.add_strategy(mock_strategy)

            # Verify mode is preserved
            assert chunker._strategy_selector._mode == original_mode

    def test_selector_mode_preserved_on_remove(self):
        """Test that selector mode is preserved when removing strategies."""
        chunker = MarkdownChunker()

        # Add and then remove strategy
        mock_strategy = MockStrategy("temp_strategy")
        chunker.add_strategy(mock_strategy)

        if hasattr(chunker._strategy_selector, "_mode"):
            mode_after_add = chunker._strategy_selector._mode

            chunker.remove_strategy("temp_strategy")

            # Verify mode is preserved
            assert chunker._strategy_selector._mode == mode_after_add

    def test_multiple_strategy_operations(self):
        """Test multiple add/remove operations in sequence."""
        chunker = MarkdownChunker()

        initial_count = len(chunker._strategies)

        # Add multiple strategies
        strategy1 = MockStrategy("strategy1")
        strategy2 = MockStrategy("strategy2")
        strategy3 = MockStrategy("strategy3")

        chunker.add_strategy(strategy1)
        chunker.add_strategy(strategy2)
        chunker.add_strategy(strategy3)

        assert len(chunker._strategies) == initial_count + 3

        # Remove some strategies
        chunker.remove_strategy("strategy2")
        assert len(chunker._strategies) == initial_count + 2
        assert "strategy2" not in chunker.get_available_strategies()

        # Verify remaining strategies still work
        chunks = chunker.chunk("# Test", strategy="strategy1")
        assert len(chunks) == 1

        chunks = chunker.chunk("# Test", strategy="strategy3")
        assert len(chunks) == 1

    def test_add_duplicate_strategy_name(self):
        """Test adding strategy with duplicate name."""
        chunker = MarkdownChunker()

        # Add strategy with existing name
        duplicate_strategy = MockStrategy("sentences")  # Already exists
        initial_count = len(chunker._strategies)

        chunker.add_strategy(duplicate_strategy)

        # Should add it (allowing duplicates for now)
        assert len(chunker._strategies) == initial_count + 1

        # Both strategies should be available
        sentences_strategies = [s for s in chunker._strategies if s.name == "sentences"]
        assert len(sentences_strategies) == 2

    def test_selector_not_none_after_operations(self):
        """Test that selector is never None after any operation."""
        chunker = MarkdownChunker()

        # Initial state
        assert chunker._strategy_selector is not None

        # After adding strategy
        mock_strategy = MockStrategy("test")
        chunker.add_strategy(mock_strategy)
        assert chunker._strategy_selector is not None

        # After removing strategy
        chunker.remove_strategy("test")
        assert chunker._strategy_selector is not None

        # After removing non-existent strategy
        chunker.remove_strategy("nonexistent")
        assert chunker._strategy_selector is not None

    def test_chunking_works_after_all_operations(self):
        """Test that chunking continues to work after all operations."""
        chunker = MarkdownChunker()

        # Test initial chunking
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0

        # Add strategy and test
        mock_strategy = MockStrategy("test")
        chunker.add_strategy(mock_strategy)
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0

        # Remove strategy and test
        chunker.remove_strategy("test")
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0

        # Remove built-in strategy and test (but not sentences, as it's the fallback)
        chunker.remove_strategy("code")  # Remove code strategy instead
        chunks = chunker.chunk("# Test")
        assert len(chunks) > 0  # Should still work with remaining strategies

    def test_get_available_strategies_updated(self):
        """Test that get_available_strategies reflects changes."""
        chunker = MarkdownChunker()

        initial_strategies = set(chunker.get_available_strategies())

        # Add strategy
        mock_strategy = MockStrategy("dynamic")
        chunker.add_strategy(mock_strategy)

        after_add = set(chunker.get_available_strategies())
        assert "dynamic" in after_add
        assert after_add == initial_strategies | {"dynamic"}

        # Remove strategy
        chunker.remove_strategy("dynamic")

        after_remove = set(chunker.get_available_strategies())
        assert "dynamic" not in after_remove
        assert after_remove == initial_strategies
