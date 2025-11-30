"""
Tests for unified chunk() API.

This module tests the new unified chunk() method that replaces
chunk_with_analysis() and chunk_simple() with a single consistent interface.
"""

import warnings

import pytest

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import Chunk, ChunkingResult


class TestUnifiedAPIBasic:
    """Test basic unified API functionality."""

    def test_chunk_default_returns_list(self):
        """Test that chunk() with defaults returns List[Chunk]."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test\n\nContent here")

        assert isinstance(result, list)
        assert all(isinstance(c, Chunk) for c in result)
        assert len(result) > 0

    def test_chunk_with_analysis_returns_result(self):
        """Test that chunk(include_analysis=True) returns ChunkingResult."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test\n\nContent here", include_analysis=True)

        assert isinstance(result, ChunkingResult)
        assert hasattr(result, "chunks")
        assert hasattr(result, "strategy_used")
        assert hasattr(result, "processing_time")

    def test_chunk_dict_format_returns_dict(self):
        """Test that chunk(return_format='dict') returns dict."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test\n\nContent here", return_format="dict")

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "metadata" in result
        assert isinstance(result["chunks"], list)

    def test_chunk_dict_with_analysis_returns_full_dict(self):
        """Test that chunk(include_analysis=True, return_format='dict') returns full dict."""
        chunker = MarkdownChunker()
        result = chunker.chunk(
            "# Test\n\nContent here", include_analysis=True, return_format="dict"
        )

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "strategy_used" in result
        assert "processing_time" in result
        assert "statistics" in result


class TestUnifiedAPIParameters:
    """Test parameter validation and combinations."""

    def test_strategy_parameter_works(self):
        """Test that strategy parameter is respected."""
        chunker = MarkdownChunker()
        result = chunker.chunk(
            "# Test\n\n```python\ncode\n```", strategy="code", include_analysis=True
        )

        assert result.strategy_used == "code"

    def test_invalid_strategy_raises_error(self):
        """Test that invalid strategy raises StrategySelectionError."""
        from markdown_chunker.chunker.selector import StrategySelectionError

        chunker = MarkdownChunker()

        with pytest.raises(StrategySelectionError, match="Invalid strategy"):
            chunker.chunk("# Test", strategy="invalid_strategy")

    def test_empty_strategy_raises_error(self):
        """Test that empty strategy raises StrategySelectionError."""
        from markdown_chunker.chunker.selector import StrategySelectionError

        chunker = MarkdownChunker()

        with pytest.raises(StrategySelectionError, match="strategy cannot be empty"):
            chunker.chunk("# Test", strategy="")

    def test_empty_text_returns_empty_result(self):
        """Test that empty text returns empty result (backward compatibility)."""
        chunker = MarkdownChunker()

        # Empty text should return empty chunks (not raise error)
        result = chunker.chunk("")
        assert isinstance(result, list)
        assert len(result) == 0

        # Whitespace-only should also return empty
        result = chunker.chunk("   \n\n  ")
        assert isinstance(result, list)
        # May return empty or minimal chunks depending on strategy

    def test_invalid_return_format_raises_error(self):
        """Test that invalid return_format raises ValueError."""
        chunker = MarkdownChunker()

        with pytest.raises(ValueError, match="Invalid return_format"):
            chunker.chunk("# Test", return_format="json")

    def test_invalid_include_analysis_type_raises_error(self):
        """Test that non-boolean include_analysis raises TypeError."""
        chunker = MarkdownChunker()

        with pytest.raises(TypeError, match="must be a boolean"):
            chunker.chunk("# Test", include_analysis="true")

    def test_invalid_md_text_type_raises_error(self):
        """Test that non-string md_text raises TypeError."""
        chunker = MarkdownChunker()

        with pytest.raises(TypeError, match="must be a string"):
            chunker.chunk(123)


class TestUnifiedAPIBackwardCompatibility:
    """Test backward compatibility with old API."""

    def test_default_behavior_matches_old_chunk(self):
        """Test that chunk() default behavior matches old chunk()."""
        chunker = MarkdownChunker()
        markdown = "# Test\n\nContent here\n\n## Section\n\nMore content"

        # New API (default)
        new_result = chunker.chunk(markdown)

        # Should return List[Chunk]
        assert isinstance(new_result, list)
        assert all(isinstance(c, Chunk) for c in new_result)

    def test_include_analysis_matches_old_chunk_with_analysis(self):
        """Test that chunk(include_analysis=True) matches old chunk_with_analysis()."""
        chunker = MarkdownChunker()
        markdown = "# Test\n\nContent here"

        # New API
        new_result = chunker.chunk(markdown, include_analysis=True)

        # Old API (with deprecation warning)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_result = chunker.chunk_with_analysis(markdown)

            # Should have deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "chunk_with_analysis() is deprecated" in str(w[0].message)

        # Results should be equivalent
        assert isinstance(new_result, ChunkingResult)
        assert isinstance(old_result, ChunkingResult)
        assert len(new_result.chunks) == len(old_result.chunks)
        assert new_result.strategy_used == old_result.strategy_used

    def test_dict_format_matches_old_chunk_simple(self):
        """Test that chunk(return_format='dict') matches old chunk_simple()."""
        chunker = MarkdownChunker()
        markdown = "# Test\n\nContent here"

        # New API
        new_result = chunker.chunk(markdown, return_format="dict")

        # Old API (with deprecation warning)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            old_result = chunker.chunk_simple(markdown)

            # Should have deprecation warning
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "chunk_simple() is deprecated" in str(w[0].message)

        # Results should have same structure
        assert isinstance(new_result, dict)
        assert isinstance(old_result, dict)
        assert "chunks" in new_result
        assert "chunks" in old_result
        assert len(new_result["chunks"]) == len(old_result["chunks"])


class TestUnifiedAPIOutputFormats:
    """Test different output format combinations."""

    def test_objects_format_without_analysis(self):
        """Test objects format without analysis returns List[Chunk]."""
        chunker = MarkdownChunker()
        result = chunker.chunk(
            "# Test", include_analysis=False, return_format="objects"
        )

        assert isinstance(result, list)
        assert all(isinstance(c, Chunk) for c in result)

    def test_objects_format_with_analysis(self):
        """Test objects format with analysis returns ChunkingResult."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test", include_analysis=True, return_format="objects")

        assert isinstance(result, ChunkingResult)
        assert hasattr(result, "chunks")

    def test_dict_format_without_analysis(self):
        """Test dict format without analysis returns simplified dict."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test", include_analysis=False, return_format="dict")

        assert isinstance(result, dict)
        assert "success" in result
        assert "chunks" in result
        assert "metadata" in result
        assert "errors" in result
        assert "warnings" in result

    def test_dict_format_with_analysis(self):
        """Test dict format with analysis returns full dict."""
        chunker = MarkdownChunker()
        result = chunker.chunk("# Test", include_analysis=True, return_format="dict")

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "strategy_used" in result
        assert "processing_time" in result
        assert "statistics" in result


class TestUnifiedAPIIntegration:
    """Test unified API with real-world scenarios."""

    def test_code_heavy_document(self):
        """Test unified API with code-heavy document."""
        markdown = """# API Reference

```python
def hello():
    return "world"
```

```python
def goodbye():
    return "farewell"
```
"""
        chunker = MarkdownChunker()
        result = chunker.chunk(markdown, include_analysis=True)

        assert isinstance(result, ChunkingResult)
        # Strategy can be any valid strategy depending on content analysis
        assert result.strategy_used in ["code", "mixed", "structural", "sentences"]
        assert len(result.chunks) > 0

    def test_list_heavy_document(self):
        """Test unified API with list-heavy document."""
        markdown = """# Tasks

- Task 1
  - Subtask 1.1
  - Subtask 1.2
- Task 2
  - Subtask 2.1
- Task 3
"""
        chunker = MarkdownChunker()
        result = chunker.chunk(markdown, strategy="list", include_analysis=True)

        assert result.strategy_used == "list"
        assert len(result.chunks) > 0

    def test_table_document(self):
        """Test unified API with table document."""
        markdown = """# Data

| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
"""
        chunker = MarkdownChunker()
        result = chunker.chunk(markdown, include_analysis=True)

        assert len(result.chunks) > 0

    def test_mixed_content_document(self):
        """Test unified API with mixed content."""
        markdown = """# Tutorial

Introduction text here.

```python
code_example()
```

## Steps

1. First step
2. Second step

| Feature | Status |
|---------|--------|
| A | Done |
"""
        chunker = MarkdownChunker()

        # Test all output formats
        chunks_list = chunker.chunk(markdown)
        assert isinstance(chunks_list, list)

        result_obj = chunker.chunk(markdown, include_analysis=True)
        assert isinstance(result_obj, ChunkingResult)

        result_dict = chunker.chunk(markdown, return_format="dict")
        assert isinstance(result_dict, dict)


class TestUnifiedAPIEdgeCases:
    """Test edge cases and error conditions."""

    def test_very_small_document(self):
        """Test with very small document."""
        chunker = MarkdownChunker()
        result = chunker.chunk("Hi", include_analysis=True)

        assert isinstance(result, ChunkingResult)
        assert len(result.chunks) >= 1

    def test_document_with_only_whitespace_between_content(self):
        """Test document with lots of whitespace."""
        markdown = "# Test\n\n\n\n\n\nContent"
        chunker = MarkdownChunker()
        result = chunker.chunk(markdown)

        assert isinstance(result, list)
        assert len(result) > 0

    def test_unicode_content(self):
        """Test with unicode content."""
        markdown = "# Тест\n\n日本語\n\n🎉 Emoji"
        chunker = MarkdownChunker()
        result = chunker.chunk(markdown, include_analysis=True)

        assert isinstance(result, ChunkingResult)
        assert len(result.chunks) > 0

    def test_all_parameters_combined(self):
        """Test with all parameters specified."""
        chunker = MarkdownChunker()
        result = chunker.chunk(
            "# Test\n\nContent",
            strategy="structural",
            include_analysis=True,
            return_format="dict",
        )

        assert isinstance(result, dict)
        assert result["strategy_used"] == "structural"
        assert "chunks" in result


class TestDeprecatedMethods:
    """Test that deprecated methods still work but emit warnings."""

    def test_chunk_with_analysis_emits_warning(self):
        """Test that chunk_with_analysis() emits deprecation warning."""
        chunker = MarkdownChunker()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = chunker.chunk_with_analysis("# Test")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "2.0.0" in str(w[0].message)

        assert isinstance(result, ChunkingResult)

    def test_chunk_simple_emits_warning(self):
        """Test that chunk_simple() emits deprecation warning."""
        chunker = MarkdownChunker()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = chunker.chunk_simple("# Test")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "deprecated" in str(w[0].message).lower()
            assert "2.0.0" in str(w[0].message)

        assert isinstance(result, dict)

    def test_deprecated_methods_still_functional(self):
        """Test that deprecated methods still produce correct results."""
        chunker = MarkdownChunker()
        markdown = "# Test\n\nContent"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            result1 = chunker.chunk_with_analysis(markdown)
            result2 = chunker.chunk_simple(markdown)

        assert isinstance(result1, ChunkingResult)
        assert isinstance(result2, dict)
        assert len(result1.chunks) > 0
        assert len(result2["chunks"]) > 0
