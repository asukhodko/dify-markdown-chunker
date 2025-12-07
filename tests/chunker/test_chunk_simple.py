"""Tests for chunk_simple() method.

Migration note: Updated for v2 API (December 2025)
v2 chunk_simple returns: chunks, errors, warnings, total_chunks, strategy_used
"""

from markdown_chunker_v2 import MarkdownChunker


class TestChunkSimple:
    """Test simplified chunking interface."""

    def test_chunk_simple_basic(self):
        """Test basic chunk_simple usage."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent here.")

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "errors" in result
        assert "warnings" in result
        assert "total_chunks" in result
        assert "strategy_used" in result
        assert len(result["chunks"]) > 0

    def test_chunk_simple_returns_dict_chunks(self):
        """Test that chunks are dictionaries."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent")

        assert isinstance(result["chunks"], list)
        assert len(result["chunks"]) > 0

        chunk = result["chunks"][0]
        assert isinstance(chunk, dict)
        assert "content" in chunk
        assert "start_line" in chunk
        assert "end_line" in chunk
        assert "metadata" in chunk

    def test_chunk_simple_with_config_dict(self):
        """Test chunk_simple with config dictionary."""
        chunker = MarkdownChunker()
        config_dict = {"max_chunk_size": 2048, "min_chunk_size": 100}

        result = chunker.chunk_simple("# Test\n\nContent", config=config_dict)

        assert len(result["errors"]) == 0
        assert len(result["chunks"]) > 0

    def test_chunk_simple_with_strategy(self):
        """Test chunk_simple with strategy parameter (ignored in v2)."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent", strategy="sentences")

        # v2 auto-selects strategy, so strategy param is ignored
        assert len(result["errors"]) == 0
        assert "strategy_used" in result

    def test_chunk_simple_metadata_structure(self):
        """Test metadata structure in chunk dicts."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent")

        assert len(result["chunks"]) > 0
        chunk = result["chunks"][0]

        # v2 metadata is in each chunk
        assert "metadata" in chunk
        assert isinstance(chunk["metadata"], dict)

    def test_chunk_simple_preserves_original_config(self):
        """Test that chunk_simple doesn't permanently change config."""
        chunker = MarkdownChunker()
        original_max = chunker.config.max_chunk_size

        # Call with different config
        chunker.chunk_simple("# Test", config={"max_chunk_size": 2048})

        # Original config should be preserved
        assert chunker.config.max_chunk_size == original_max

    def test_chunk_simple_with_empty_content(self):
        """Test chunk_simple with empty content."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("")

        assert isinstance(result, dict)
        assert "chunks" in result
        assert "errors" in result
        assert result["total_chunks"] == 0

    def test_chunk_simple_json_serializable(self):
        """Test that result is JSON serializable."""
        import json

        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent")

        # Should not raise exception
        json_str = json.dumps(result)
        assert isinstance(json_str, str)

        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed["total_chunks"] == result["total_chunks"]

    def test_chunk_simple_with_code_content(self):
        """Test chunk_simple with code-heavy content."""
        chunker = MarkdownChunker()
        content = """# Code Example

```python
def hello():
    print("world")
```

Some text here.
"""
        result = chunker.chunk_simple(content)

        assert len(result["errors"]) == 0
        assert len(result["chunks"]) > 0

    def test_chunk_simple_errors_list(self):
        """Test that errors list is present."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test")

        assert "errors" in result
        assert isinstance(result["errors"], list)

    def test_chunk_simple_warnings_list(self):
        """Test that warnings list is present."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test")

        assert "warnings" in result
        assert isinstance(result["warnings"], list)


class TestChunkSimpleIntegration:
    """Integration tests for chunk_simple."""

    def test_chunk_simple_complete_workflow(self):
        """Test complete workflow with chunk_simple."""
        chunker = MarkdownChunker()

        content = """# Introduction

This is a test document with multiple sections.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

        result = chunker.chunk_simple(
            content, config={"max_chunk_size": 4096}, strategy="structural"
        )

        assert len(result["errors"]) == 0
        assert len(result["chunks"]) > 0
        assert "strategy_used" in result

        # Verify chunk structure
        for chunk in result["chunks"]:
            assert "content" in chunk
            assert "start_line" in chunk
            assert "end_line" in chunk
            assert isinstance(chunk["content"], str)
            assert isinstance(chunk["start_line"], int)
            assert isinstance(chunk["end_line"], int)

    def test_chunk_simple_vs_chunk_with_analysis(self):
        """Test that chunk_simple produces same results as chunk_with_analysis."""
        chunker = MarkdownChunker()
        content = "# Test\n\nContent here."

        # Get result from both methods
        simple_result = chunker.chunk_simple(content)
        chunks, strategy_used, analysis = chunker.chunk_with_analysis(content)

        # Should have same number of chunks
        assert len(simple_result["chunks"]) == len(chunks)

        # Should use same strategy
        assert simple_result["strategy_used"] == strategy_used

        # First chunk content should match
        if len(simple_result["chunks"]) > 0:
            assert simple_result["chunks"][0]["content"] == chunks[0].content
