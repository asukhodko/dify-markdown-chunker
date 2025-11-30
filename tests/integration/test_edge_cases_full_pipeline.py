"""
Edge case tests for full chunking pipeline.

Tests handling of unusual, malformed, or extreme inputs.
"""

import pytest

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


@pytest.fixture
def chunker():
    """Create chunker with default config."""
    return MarkdownChunker()


class TestEmptyAndMinimalDocuments:
    """Tests for empty and minimal documents."""

    def test_empty_document(self, chunker):
        """Test handling of empty document."""
        result = chunker.chunk("", include_analysis=True)

        # Should handle gracefully
        assert isinstance(result.chunks, list)
        assert len(result.chunks) == 0
        assert result.processing_time >= 0

    def test_whitespace_only_document(self, chunker):
        """Test document with only whitespace."""
        result = chunker.chunk("   \n\n\t\n   ", include_analysis=True)

        # Should handle gracefully
        assert isinstance(result.chunks, list)
        # May create empty chunks or no chunks
        assert len(result.chunks) >= 0

    def test_single_character_document(self, chunker):
        """Test document with single character."""
        result = chunker.chunk("a", include_analysis=True)

        # Should create at least one chunk
        assert len(result.chunks) >= 1
        assert result.success

    def test_single_line_document(self, chunker):
        """Test document with single line."""
        result = chunker.chunk("This is a single line.", include_analysis=True)

        assert len(result.chunks) >= 1
        assert result.success
        assert result.chunks[0].content.strip() == "This is a single line."


class TestVeryLargeDocuments:
    """Tests for very large documents."""

    def test_very_large_document(self, chunker):
        """Test handling of very large document (1MB+)."""
        # Generate 1MB document
        section = "# Section\n\nThis is content. " * 100 + "\n\n"
        content = section * 200  # ~1MB

        result = chunker.chunk(content, include_analysis=True)

        # Should handle without crashing
        assert result.success
        assert len(result.chunks) > 0

        # Should complete in reasonable time
        assert (
            result.processing_time < 130.0
        ), f"Too slow: {result.processing_time:.1f}s"

    def test_very_long_single_line(self, chunker):
        """Test document with very long single line."""
        # 100KB single line
        content = "This is a very long line. " * 4000

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_many_small_sections(self, chunker):
        """Test document with many small sections."""
        # 1000 tiny sections
        sections = [f"## Section {i}\n\nContent {i}\n\n" for i in range(1000)]
        content = "# Document\n\n" + "".join(sections)

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestMalformedMarkdown:
    """Tests for malformed markdown."""

    def test_unclosed_code_block(self, chunker):
        """Test markdown with unclosed code block."""
        content = """
# Title

```python
def test():
    return True

This is text after unclosed code block.
"""

        result = chunker.chunk(content, include_analysis=True)

        # Should handle gracefully
        assert result.success
        assert len(result.chunks) > 0

    def test_mismatched_headers(self, chunker):
        """Test markdown with mismatched header levels."""
        content = """
# Level 1

#### Level 4 (skipped 2 and 3)

## Level 2 (going back)

##### Level 5
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_malformed_table(self, chunker):
        """Test markdown with malformed table."""
        content = """
# Title

| Column 1 | Column 2
|----------|
| Value 1 | Value 2 | Extra value
| Missing value |

More content.
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_malformed_list(self, chunker):
        """Test markdown with malformed list."""
        content = """
# Title

- Item 1
  - Subitem 1
    - Sub-subitem
- Item 2
    - Inconsistent indentation
  - Another subitem
- Item 3

Content after list.
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestUnicodeAndSpecialCharacters:
    """Tests for unicode and special characters."""

    def test_unicode_heavy_document(self, chunker):
        """Test document with heavy unicode usage."""
        content = """
# 文档标题 (Document Title)

## Раздел 1 (Section 1)

这是一个包含多种语言的文档。
Это документ с несколькими языками.
هذا مستند بلغات متعددة.

### Emojis

Hello 👋 World 🌍
- ✅ Task 1
- ❌ Task 2
- 🔄 Task 3

### Special Characters

Math: ∑ ∫ ∂ √ ∞
Arrows: → ← ↑ ↓ ⇒ ⇐
Symbols: © ® ™ € £ ¥
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

        # Verify unicode preserved
        all_content = "".join(c.content for c in result.chunks)
        assert "文档标题" in all_content
        assert "👋" in all_content
        assert "∑" in all_content

    def test_special_markdown_characters(self, chunker):
        """Test document with special markdown characters."""
        content = """
# Title with `code` and *emphasis*

Text with **bold** and _italic_ and ~~strikethrough~~.

Escaped characters: \\* \\_ \\` \\# \\[ \\]

Links: [text](url) and ![image](url)

Inline code: `code with backticks`

Math: $x^2 + y^2=z^2$
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestMixedLineEndings:
    """Tests for mixed line endings."""

    def test_document_with_mixed_line_endings(self, chunker):
        """Test document with mixed line endings (LF, CRLF)."""
        # Mix of \n and \r\n
        content = (
            "# Title\r\n\r\nParagraph 1\n\nParagraph 2\r\n\r\n## Section\n\nContent"
        )

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_document_with_cr_only(self, chunker):
        """Test document with CR only line endings."""
        content = "# Title\r\rParagraph 1\r\r## Section\r\rContent"

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestDocumentWithOnlyCode:
    """Tests for documents with only code."""

    def test_document_with_only_code(self, chunker):
        """Test document containing only code blocks."""
        content = """
```python
def function1():
    return 1
```

```python
def function2():
    return 2
```

```python
def function3():
    return 3
```
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

        # Should use code strategy
        assert result.strategy_used in ["code", "structural", "sentences", "mixed"]

    def test_document_with_only_inline_code(self, chunker):
        """Test document with only inline code."""
        content = "`code1` and `code2` and `code3` " * 50

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestDocumentWithOnlyText:
    """Tests for documents with only text."""

    def test_document_with_only_text(self, chunker):
        """Test document with only plain text (no markdown)."""
        content = "This is plain text. " * 100

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

        # Should use sentences strategy
        assert result.strategy_used in ["sentences", "structural"]

    def test_document_with_only_paragraphs(self, chunker):
        """Test document with only paragraphs (no headers)."""
        paragraphs = [f"This is paragraph {i}. " * 10 for i in range(20)]
        content = "\n\n".join(paragraphs)

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestDeeplyNestedStructures:
    """Tests for deeply nested structures."""

    def test_deeply_nested_headers(self, chunker):
        """Test document with deeply nested headers."""
        content = """
# Level 1

## Level 2

### Level 3

#### Level 4

##### Level 5

###### Level 6

Content at deepest level.

###### Another Level 6

More content.
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_deeply_nested_lists(self, chunker):
        """Test document with deeply nested lists."""
        content = """
# Title

- Level 1
  - Level 2
    - Level 3
      - Level 4
        - Level 5
          - Level 6
            - Level 7
              - Level 8

Content after list.
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_deeply_nested_blockquotes(self, chunker):
        """Test document with deeply nested blockquotes."""
        content = """
# Title

> Level 1
>> Level 2
>>> Level 3
>>>> Level 4
>>>>> Level 5

Content after blockquotes.
"""

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestExtremeConfigurations:
    """Tests for extreme configuration values."""

    def test_very_small_chunk_size(self):
        """Test with very small max_chunk_size."""
        config = ChunkConfig(max_chunk_size=100, min_chunk_size=10)
        chunker = MarkdownChunker(config)

        content = "# Title\n\n" + "This is content. " * 50
        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_very_large_chunk_size(self):
        """Test with very large max_chunk_size."""
        config = ChunkConfig(max_chunk_size=100000, min_chunk_size=1000)
        chunker = MarkdownChunker(config)

        content = "# Title\n\n" + "This is content. " * 1000
        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_zero_overlap(self):
        """Test with zero overlap."""
        config = ChunkConfig(enable_overlap=True, overlap_size=0)
        chunker = MarkdownChunker(config)

        content = "# Title\n\n" + "Content. " * 100
        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

    def test_100_percent_overlap(self):
        """Test with 100% overlap."""
        config = ChunkConfig(
            enable_overlap=True, overlap_percentage=1.0, max_chunk_size=1000
        )
        chunker = MarkdownChunker(config)

        content = "# Title\n\n" + "Content. " * 100
        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0


class TestErrorRecovery:
    """Tests for error recovery and fallback."""

    def test_fallback_chain_activation(self, chunker):
        """Test that fallback chain activates when needed."""
        # Create content that might trigger fallback
        content = "# Title\n\n" + "x" * 10000  # Very long paragraph

        result = chunker.chunk(content, include_analysis=True)

        assert result.success
        assert len(result.chunks) > 0

        # May or may not use fallback, but should succeed
        assert result.processing_time > 0

    def test_recovery_from_invalid_strategy(self):
        """Test recovery when invalid strategy specified."""
        chunker = MarkdownChunker()
        content = "# Title\n\nContent"

        # Invalid strategy should raise error
        with pytest.raises(Exception):
            chunker.chunk(content, strategy="invalid_strategy")

    def test_graceful_degradation(self, chunker):
        """Test graceful degradation on problematic content."""
        # Content that might cause issues
        content = (
            """
# Title

"""
            + "```python\n" * 100
            + "code\n"
            + "```\n" * 100
        )

        result = chunker.chunk(content, include_analysis=True)

        # Should handle gracefully
        assert isinstance(result.chunks, list)
        assert result.processing_time > 0
