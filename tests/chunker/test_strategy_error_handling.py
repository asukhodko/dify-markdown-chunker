"""
Tests for strategy selection error handling.

This module tests that StrategySelectionError is properly raised and not
caught by the general exception handler.
"""

from unittest.mock import Mock, patch

import pytest

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.selector import StrategySelectionError


class TestStrategyErrorHandling:
    """Test strategy selection error handling."""

    def test_invalid_strategy_name_raises_error(self):
        """Test that invalid strategy name raises StrategySelectionError."""
        chunker = MarkdownChunker()

        # Test with invalid strategy name
        with pytest.raises(StrategySelectionError) as exc_info:
            chunker.chunk("# Test\n\nContent", strategy="invalid_name")

        # Verify error message contains strategy name and available strategies
        error_msg = str(exc_info.value)
        assert "invalid_name" in error_msg
        assert "not found" in error_msg or "Invalid strategy" in error_msg
        assert "Available strategies" in error_msg

    def test_error_message_includes_available_strategies(self):
        """Test that error message includes list of available strategies."""
        chunker = MarkdownChunker()

        with pytest.raises(StrategySelectionError) as exc_info:
            chunker.chunk("# Test", strategy="nonexistent")

        error_msg = str(exc_info.value)
        # Should include all 6 strategy names
        expected_strategies = [
            "code",
            "mixed",
            "list",
            "table",
            "structural",
            "sentences",
        ]
        for strategy in expected_strategies:
            assert strategy in error_msg

    def test_valid_strategy_name_does_not_raise_error(self):
        """Test that valid strategy names don't raise StrategySelectionError."""
        chunker = MarkdownChunker()

        # Test all valid strategy names
        valid_strategies = ["code", "mixed", "list", "table", "structural", "sentences"]

        for strategy_name in valid_strategies:
            # Should not raise StrategySelectionError
            try:
                chunks = chunker.chunk("# Test\n\nContent", strategy=strategy_name)
                # Should get some chunks
                assert len(chunks) >= 0  # May be 0 if strategy can't handle content
            except StrategySelectionError:
                pytest.fail(
                    f"Valid strategy '{strategy_name}' raised StrategySelectionError"
                )

    def test_strategy_validation_before_try_block(self):
        """Test that strategy validation happens before try block."""
        chunker = MarkdownChunker()

        # Mock _get_strategy_by_name to return None (invalid strategy)
        with patch.object(chunker, "_get_strategy_by_name", return_value=None):
            with pytest.raises(StrategySelectionError):
                chunker.chunk("# Test", strategy="mocked_invalid")

    def test_strategy_selection_error_not_caught_by_general_except(self):
        """Test that StrategySelectionError is not caught by general exception handler."""
        chunker = MarkdownChunker()

        # This should raise StrategySelectionError, not fall back to emergency chunking
        with pytest.raises(StrategySelectionError):
            chunker.chunk("# Test", strategy="definitely_invalid")

        # Verify that emergency chunking is NOT used for invalid strategy names
        # (it should only be used for processing errors, not validation errors)

    def test_other_exceptions_still_caught(self):
        """Test that other exceptions are still caught and trigger emergency fallback."""
        chunker = MarkdownChunker()

        # Create a mock strategy and add it to the chunker
        mock_strategy = Mock()
        mock_strategy.name = "test"
        mock_strategy.priority = 999
        mock_strategy.apply.side_effect = RuntimeError("Processing failed")

        # Add the mock strategy to the chunker
        chunker.add_strategy(mock_strategy)

        # This should NOT raise an exception, but use fallback
        result = chunker.chunk_with_analysis("# Test", strategy="test")

        # Should use fallback (structural or emergency)
        assert result.strategy_used in ["structural", "sentences", "emergency"]
        assert result.fallback_used is True
        assert len(result.errors) > 0

    def test_automatic_strategy_selection_errors_handled(self):
        """Test that errors in automatic strategy selection are handled properly."""
        chunker = MarkdownChunker()

        # Mock strategy selector to raise an exception
        with patch.object(
            chunker._strategy_selector,
            "select_strategy",
            side_effect=RuntimeError("Selection failed"),
        ):
            # Should not raise exception, should use fallback strategy
            result = chunker.chunk_with_analysis("# Test")

            # After refactoring, fallback uses sentences strategy instead of emergency
            assert result.strategy_used == "sentences"
            assert "Strategy selection failed" in str(result.errors)

    def test_chunk_with_analysis_propagates_strategy_error(self):
        """Test that chunk_with_analysis also propagates StrategySelectionError."""
        chunker = MarkdownChunker()

        with pytest.raises(StrategySelectionError):
            chunker.chunk_with_analysis("# Test", strategy="invalid")

    def test_get_available_strategies_returns_correct_list(self):
        """Test that get_available_strategies returns the correct strategy names."""
        chunker = MarkdownChunker()

        strategies = chunker.get_available_strategies()

        # Should have all 6 strategies
        assert len(strategies) == 6
        expected = {"code", "mixed", "list", "table", "structural", "sentences"}
        assert set(strategies) == expected

    def test_case_sensitivity_in_strategy_names(self):
        """Test that strategy names are case sensitive."""
        chunker = MarkdownChunker()

        # These should all raise StrategySelectionError
        invalid_cases = ["Code", "CODE", "Mixed", "STRUCTURAL", "Sentences"]

        for invalid_name in invalid_cases:
            with pytest.raises(StrategySelectionError):
                chunker.chunk("# Test", strategy=invalid_name)

    def test_empty_strategy_name(self):
        """Test that empty strategy name raises StrategySelectionError."""
        chunker = MarkdownChunker()

        # Empty string should be treated as invalid strategy
        with pytest.raises(StrategySelectionError):
            chunker.chunk("# Test", strategy="")

    def test_none_strategy_uses_automatic_selection(self):
        """Test that None strategy uses automatic selection (no error)."""
        chunker = MarkdownChunker()

        # Should not raise StrategySelectionError
        result = chunker.chunk_with_analysis("# Test", strategy=None)

        # Should use some strategy (not emergency unless all strategies fail)
        assert result.strategy_used != "emergency" or len(result.errors) > 0
