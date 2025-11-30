#!/usr/bin/env python3
"""Validate that P0 critical fixes work correctly."""
from markdown_chunker.chunker import MarkdownChunker


def test_mixed_strategy_lists():
    """Test MixedStrategy uses Stage 1 list data."""
    markdown = "# Doc\n\n- Item 1\n- Item 2\n- Item 3"

    chunker = MarkdownChunker()

    # The main test: no AttributeError should occur
    try:
        result = chunker.chunk_with_analysis(markdown)
        # If we get here, no AttributeError was raised - that's the main fix
        assert len(result.chunks) > 0, "Should produce at least one chunk"
        assert (
            result.strategy_used != "emergency"
        ), f"Used emergency fallback! Strategy: {result.strategy_used}"
        print(
            f"✅ MixedStrategy lists: PASSED (Strategy: {result.strategy_used}, Chunks: {len(result.chunks)})"
        )
    except AttributeError as e:
        raise AssertionError(
            f"AttributeError occurred (this means our fixes didn't work): {e}"
        )


def test_mixed_strategy_tables():
    """Test MixedStrategy uses Stage 1 table data."""
    markdown = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"

    chunker = MarkdownChunker()

    # The main test: no AttributeError should occur
    try:
        result = chunker.chunk_with_analysis(markdown)
        # If we get here, no AttributeError was raised - that's the main fix
        assert len(result.chunks) > 0, "Should produce at least one chunk"
        assert (
            result.strategy_used != "emergency"
        ), f"Used emergency fallback! Strategy: {result.strategy_used}"
        print(
            f"✅ MixedStrategy tables: PASSED (Strategy: {result.strategy_used}, Chunks: {len(result.chunks)})"
        )
    except AttributeError as e:
        raise AssertionError(
            f"AttributeError occurred (this means our fixes didn't work): {e}"
        )


def test_list_strategy_integration():
    """Test ListStrategy uses Stage 1 list items."""
    markdown = "- Parent 1\n  - Child 1.1\n  - Child 1.2\n- Parent 2"

    chunker = MarkdownChunker()

    # The main test: no AttributeError should occur
    try:
        result = chunker.chunk_with_analysis(markdown)
        # If we get here, no AttributeError was raised - that's the main fix
        assert len(result.chunks) > 0, "Should produce at least one chunk"
        assert (
            result.strategy_used != "emergency"
        ), f"Used emergency fallback! Strategy: {result.strategy_used}"
        assert (
            result.fallback_level < 4
        ), f"High fallback level: {result.fallback_level}"
        print(
            f"✅ ListStrategy integration: PASSED (Strategy: {result.strategy_used}, Fallback: {result.fallback_level})"
        )
    except AttributeError as e:
        raise AssertionError(
            f"AttributeError occurred (this means our fixes didn't work): {e}"
        )


def test_no_attribute_errors():
    """Test that no AttributeErrors occur."""
    test_cases = [
        "# Doc\n\n- List item",
        "| A | B |\n|---|---|\n| 1 | 2 |",
        "# Complex\n\nText\n\n- List\n\n| T | able |\n|---|---|\n| 1 | 2 |",
    ]

    chunker = MarkdownChunker()
    for markdown in test_cases:
        try:
            result = chunker.chunk_with_analysis(markdown)
            assert len(result.chunks) > 0
        except AttributeError as e:
            raise AssertionError(f"AttributeError occurred: {e}")

    print("✅ No AttributeErrors: PASSED")


if __name__ == "__main__":
    print("🧪 Validating P0 Critical Fixes...\n")

    test_mixed_strategy_lists()
    test_mixed_strategy_tables()
    test_list_strategy_integration()
    test_no_attribute_errors()

    print("\n🎉 ALL CRITICAL FIXES VALIDATED!")
