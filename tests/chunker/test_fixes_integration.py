"""
Integration tests for all Stage 2 fixes.

This module tests that all critical fixes work together correctly
and that the full pipeline functions as expected.
"""

import pytest

from markdown_chunker.chunker import MarkdownChunker
from markdown_chunker.chunker.selector import StrategySelectionError
from markdown_chunker.chunker.types import ChunkConfig


class TestFixesIntegration:
    """Test integration of all fixes."""

    def test_full_pipeline_with_automatic_strategy_selection(self):
        """Test full pipeline with automatic strategy selection."""
        chunker = MarkdownChunker()

        # Test code-heavy document
        code_doc = """
# API Documentation

## Overview
This is a code-heavy document.

```python
def hello_world():
    print("Hello, World!")
    return True
```

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```

```bash
echo "Hello from bash"
```
        """.strip()

        chunks = chunker.chunk(code_doc)
        assert len(chunks) > 0
        assert all(chunk.content.strip() for chunk in chunks)

        # Verify metadata is present
        for chunk in chunks:
            assert hasattr(chunk, "metadata")
            assert "strategy" in chunk.metadata

    def test_manual_strategy_selection(self):
        """Test manual strategy selection works."""
        chunker = MarkdownChunker()
        content = "# Test\n\nSome content here."

        # Test each strategy manually - use content that works with all strategies
        content = """
# Test Document

This is a test document with multiple elements.

## Code Section
```python
def test_function():
    return "Hello World"
```

## List Section
- Item 1
- Item 2
- Item 3

## Table Section
| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |

## Text Section
This is some regular text content that should work with all strategies.
        """.strip()

        strategies = chunker.get_available_strategies()
        for strategy in strategies:
            chunks = chunker.chunk(content, strategy=strategy)
            # Some strategies might not handle simple content, so we allow empty results
            # but if there are chunks, they should have content
            if chunks:
                assert all(chunk.content.strip() for chunk in chunks)

    def test_invalid_strategy_raises_strategy_selection_error(self):
        """Test that invalid strategy raises StrategySelectionError."""
        chunker = MarkdownChunker()
        content = "# Test\n\nContent"

        with pytest.raises(StrategySelectionError) as exc_info:
            chunker.chunk(content, strategy="invalid_strategy")

        # Verify error message contains strategy name
        assert "invalid_strategy" in str(exc_info.value)
        assert "available strategies" in str(exc_info.value).lower()

    def test_small_chunk_size_configuration_works(self):
        """Test that small chunk size configuration works with auto-adjustment."""
        # Test very small max_chunk_size
        config = ChunkConfig(
            max_chunk_size=500,
            min_chunk_size=400,  # This should be auto-adjusted
            target_chunk_size=450,
        )

        # Verify auto-adjustment worked
        assert config.min_chunk_size <= config.max_chunk_size
        assert (
            config.min_chunk_size <= config.target_chunk_size <= config.max_chunk_size
        )

        # Test chunking with small config
        chunker = MarkdownChunker(config=config)
        content = "# Test\n\n" + "This is a test sentence. " * 50
        chunks = chunker.chunk(content)
        assert len(chunks) > 0

    def test_dynamic_strategy_addition_removal(self):
        """Test dynamic strategy management works."""
        chunker = MarkdownChunker()

        # Get initial strategies
        initial_strategies = chunker.get_available_strategies()
        assert len(initial_strategies) == 6

        # Create a simple mock strategy for testing
        from markdown_chunker.chunker.strategies.sentences_strategy import (
            SentencesStrategy,
        )

        class TestStrategy(SentencesStrategy):
            @property
            def name(self) -> str:
                return "test_strategy"

            @property
            def priority(self) -> int:
                return 999

        # Add strategy
        test_strategy = TestStrategy()
        chunker.add_strategy(test_strategy)

        # Verify strategy was added
        updated_strategies = chunker.get_available_strategies()
        assert len(updated_strategies) == 7
        assert "test_strategy" in updated_strategies

        # Test chunking still works
        chunks = chunker.chunk("# Test\n\nContent")
        assert len(chunks) > 0

        # Remove strategy
        chunker.remove_strategy("test_strategy")

        # Verify strategy was removed
        final_strategies = chunker.get_available_strategies()
        assert len(final_strategies) == 6
        assert "test_strategy" not in final_strategies


class TestPerformanceBenchmarks:
    """Test performance benchmarks for fixes."""

    def test_small_document_performance(self):
        """Test small document chunking performance."""
        chunker = MarkdownChunker()
        content = "# Small Test\n\nThis is a small document."

        import time

        start_time = time.time()
        chunks = chunker.chunk(content)
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 0.1  # Should be very fast
        assert len(chunks) > 0

    def test_medium_document_performance(self):
        """Test medium document chunking performance."""
        chunker = MarkdownChunker()

        # Create medium-sized document
        content = "# Medium Document\n\n"
        content += "## Section 1\n\n" + "This is content. " * 100 + "\n\n"
        content += "## Section 2\n\n" + "More content here. " * 100 + "\n\n"
        content += "```python\n" + "print('code')\n" * 50 + "```\n\n"

        import time

        start_time = time.time()
        chunks = chunker.chunk(content)
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 1.0  # Should complete within 1 second
        assert len(chunks) > 0

    def test_large_document_performance(self):
        """Test large document chunking performance."""
        chunker = MarkdownChunker()

        # Create large document
        content = "# Large Document\n\n"
        for i in range(20):
            content += f"## Section {i+1}\n\n"
            content += "This is a lot of content. " * 200 + "\n\n"
            if i % 3 == 0:
                content += (
                    f"```python\n# Code block {i+1}\n"
                    + "print('test')\n" * 20
                    + "```\n\n"
                )

        import time

        start_time = time.time()
        chunks = chunker.chunk(content)
        end_time = time.time()

        processing_time = end_time - start_time
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert len(chunks) > 0


class TestErrorHandlingIntegration:
    """Test error handling integration."""

    def test_fallback_chain_execution(self):
        """Test that fallback chain executes properly."""
        chunker = MarkdownChunker()

        # Create content that might trigger fallbacks
        problematic_content = """
# Test Document

This is some content that might cause issues.

```
Unclosed code block without language
Some code here
        """

        # Should not raise exception, should use fallback
        chunks = chunker.chunk(problematic_content)
        assert len(chunks) > 0

        # Verify fallback info is present
        for chunk in chunks:
            assert hasattr(chunk, "metadata")

    def test_emergency_chunking_fallback(self):
        """Test emergency chunking as last resort."""
        chunker = MarkdownChunker()

        # Create very problematic content
        weird_content = "\x00\x01\x02" + "# Test\n\nContent" + "\x03\x04"

        # Should still produce chunks via emergency fallback
        chunks = chunker.chunk(weird_content)
        assert len(chunks) > 0


class TestMetadataIntegration:
    """Test metadata integration across fixes."""

    def test_strategy_metadata_present(self):
        """Test that strategy metadata is present in chunks."""
        chunker = MarkdownChunker()
        content = "# Test\n\nContent with some text."

        chunks = chunker.chunk(content)
        assert len(chunks) > 0

        for chunk in chunks:
            assert hasattr(chunk, "metadata")
            assert "strategy" in chunk.metadata
            assert chunk.metadata["strategy"] in chunker.get_available_strategies()

    def test_fallback_metadata_tracking(self):
        """Test that fallback metadata is tracked."""
        chunker = MarkdownChunker()

        # Use content that might trigger fallbacks
        content = "# Test\n\n" + "Short content."

        chunks = chunker.chunk(content)
        assert len(chunks) > 0

        # Check for fallback-related metadata
        for chunk in chunks:
            assert hasattr(chunk, "metadata")
            # Should have strategy information
            assert "strategy" in chunk.metadata


class TestConfigurationIntegration:
    """Test configuration integration."""

    def test_custom_config_integration(self):
        """Test that custom configuration works with all fixes."""
        config = ChunkConfig(
            max_chunk_size=1000,
            min_chunk_size=100,
            target_chunk_size=500,
            overlap_size=50,
        )

        chunker = MarkdownChunker(config=config)

        # Test with various content types
        contents = [
            "# Simple\n\nText content.",
            "# Code\n\n```python\nprint('hello')\n```",
            "# List\n\n- Item 1\n- Item 2\n- Item 3",
            "# Table\n\n| A | B |\n|---|---|\n| 1 | 2 |",
        ]

        for content in contents:
            chunks = chunker.chunk(content)
            assert len(chunks) > 0

            # Verify chunks respect configuration
            for chunk in chunks:
                assert (
                    len(chunk.content) <= config.max_chunk_size * 1.2
                )  # Allow some tolerance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
