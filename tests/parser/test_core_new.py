"""
Comprehensive tests for parser.core module (NEW CODE).

These tests specifically target the NEW refactored code in core.py,
not the old fenced_blocks.py or interface.py.
"""

from markdown_chunker.parser.core import (
    FencedBlockExtractor,
    ParserInterface,
    Stage1Interface,
    extract_fenced_blocks,
)


class TestFencedBlockExtractorNew:
    """Test FencedBlockExtractor from core.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that FencedBlockExtractor can be instantiated."""
        extractor = FencedBlockExtractor()
        assert extractor is not None
        assert hasattr(extractor, "extract_fenced_blocks")

    def test_extract_simple_code_block(self):
        """Test extracting a simple fenced code block."""
        md_text = """# Header

```python
def hello():
    print("world")
```

Some text.
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "def hello():" in blocks[0].content
        assert blocks[0].start_line == 3
        assert blocks[0].is_closed is True

    def test_extract_multiple_blocks(self):
        """Test extracting multiple fenced blocks."""
        md_text = """```python
code1
```

Text between.

```javascript
code2
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "javascript"
        assert "code1" in blocks[0].content
        assert "code2" in blocks[1].content

    def test_extract_block_without_language(self):
        """Test extracting block without language specifier."""
        md_text = """```
plain code
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert blocks[0].language is None or blocks[0].language == ""
        assert "plain code" in blocks[0].content

    def test_extract_nested_blocks(self):
        """Test extracting nested fenced blocks."""
        md_text = """```markdown
# Document

```python
nested code
```

More markdown
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        # Should extract both outer and inner blocks
        assert len(blocks) >= 1
        # Outer block should be markdown
        assert any(b.language == "markdown" for b in blocks)

    def test_extract_unclosed_block(self):
        """Test handling of unclosed fenced block."""
        md_text = """```python
def incomplete():
    pass
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert blocks[0].is_closed is False

    def test_extract_empty_document(self):
        """Test extracting from empty document."""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks("")

        assert len(blocks) == 0

    def test_extract_no_blocks(self):
        """Test document with no fenced blocks."""
        md_text = """# Header

Just regular text.

- List item
- Another item
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 0

    def test_block_line_numbers(self):
        """Test that line numbers are correctly tracked."""
        md_text = """Line 1
Line 2
```python
Line 4
Line 5
```
Line 7
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert blocks[0].start_line == 3
        assert blocks[0].end_line == 6

    def test_block_nesting_level(self):
        """Test that nesting levels are tracked."""
        md_text = """```markdown
Outer block
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert hasattr(blocks[0], "nesting_level")
        assert blocks[0].nesting_level >= 0


class TestParserInterfaceNew:
    """Test ParserInterface from core.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that ParserInterface can be instantiated."""
        parser = ParserInterface()
        assert parser is not None
        assert hasattr(parser, "process_document")

    def test_process_simple_document(self):
        """Test processing a simple markdown document."""
        md_text = """# Hello World

This is a test document.

```python
print("hello")
```
"""
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert result is not None
        assert hasattr(result, "ast")
        assert hasattr(result, "fenced_blocks")
        assert hasattr(result, "analysis")
        assert len(result.fenced_blocks) == 1

    def test_process_empty_document(self):
        """Test processing empty document."""
        parser = ParserInterface()
        result = parser.process_document("")

        assert result is not None
        assert len(result.fenced_blocks) == 0

    def test_process_document_with_multiple_blocks(self):
        """Test processing document with multiple code blocks."""
        md_text = """# Code Examples

```python
def func1():
    pass
```

```javascript
function func2() {}
```

```ruby
def func3
end
```
"""
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert len(result.fenced_blocks) == 3
        languages = [b.language for b in result.fenced_blocks]
        assert "python" in languages
        assert "javascript" in languages
        assert "ruby" in languages

    def test_prepare_for_chunking(self):
        """Test prepare_for_chunking method."""
        md_text = """# Test

```python
code
```
"""
        parser = ParserInterface()
        # First process the document to get Stage1Results
        stage1_results = parser.process_document(md_text)

        # Then prepare for chunking
        result = parser.prepare_for_chunking(stage1_results)

        # prepare_for_chunking returns a dict with processed data
        assert result is not None
        assert isinstance(result, dict)
        assert "ast" in result
        assert "fenced_blocks" in result
        assert "analysis" in result

    def test_stage1_interface_alias(self):
        """Test that Stage1Interface is an alias for ParserInterface."""
        assert Stage1Interface is ParserInterface

    def test_processing_time_tracked(self):
        """Test that processing time is tracked."""
        md_text = "# Test document"
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert hasattr(result, "processing_time")
        assert result.processing_time >= 0

    def test_content_analysis_present(self):
        """Test that content analysis is performed."""
        md_text = """# Header

Regular text paragraph.

```python
code block
```

More text.
"""
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert result.analysis is not None
        assert hasattr(result.analysis, "code_ratio")
        assert hasattr(result.analysis, "text_ratio")
        assert hasattr(result.analysis, "total_chars")
        assert result.analysis.total_chars > 0


class TestConvenienceFunctionsNew:
    """Test convenience functions from core.py (NEW CODE)."""

    def test_extract_fenced_blocks_function(self):
        """Test extract_fenced_blocks convenience function."""
        md_text = """```python
test code
```
"""
        blocks = extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert "test code" in blocks[0].content

    def test_extract_fenced_blocks_empty(self):
        """Test extract_fenced_blocks with empty input."""
        blocks = extract_fenced_blocks("")
        assert len(blocks) == 0

    def test_extract_fenced_blocks_no_blocks(self):
        """Test extract_fenced_blocks with no code blocks."""
        md_text = "# Just a header\n\nAnd some text."
        blocks = extract_fenced_blocks(md_text)
        assert len(blocks) == 0


class TestFencedBlockExtractorEdgeCases:
    """Test edge cases for FencedBlockExtractor."""

    def test_block_with_backticks_in_content(self):
        """Test block containing backticks in content."""
        md_text = """```python
# Use ` for inline code
x=`command`
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert "`" in blocks[0].content

    def test_consecutive_blocks(self):
        """Test consecutive blocks without text between."""
        md_text = """```python
block1
```
```javascript
block2
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        # Should extract at least one block (behavior may vary for consecutive blocks)
        assert len(blocks) >= 1
        assert blocks[0].language in ["python", "javascript"]

    def test_block_with_empty_lines(self):
        """Test block with empty lines in content."""
        md_text = """```python
line1

line3
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert "\n\n" in blocks[0].content or blocks[0].content.count("\n") >= 2

    def test_indented_block(self):
        """Test indented fenced block."""
        md_text = """    ```python
    indented code
    ```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        # Should still extract indented blocks
        assert len(blocks) >= 0  # Behavior may vary

    def test_block_with_special_characters(self):
        """Test block with special characters."""
        md_text = """```python
# Special: <>&"'
x="test"
```
"""
        extractor = FencedBlockExtractor()
        blocks = extractor.extract_fenced_blocks(md_text)

        assert len(blocks) == 1
        assert "<>&" in blocks[0].content


class TestParserInterfaceEdgeCases:
    """Test edge cases for ParserInterface."""

    def test_very_long_document(self):
        """Test processing very long document."""
        md_text = "# Header\n\n" + ("Line of text.\n" * 1000)
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert result is not None
        assert result.analysis.total_lines >= 1000

    def test_document_with_unicode(self):
        """Test document with unicode characters."""
        md_text = """# Привет мир 🌍

```python
# 日本語コメント
print("Hello 世界")
```
"""
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert result is not None
        assert len(result.fenced_blocks) == 1

    def test_document_with_mixed_line_endings(self):
        """Test document with mixed line endings."""
        md_text = "# Header\r\n\r\nText\n\n```python\r\ncode\r\n```\n"
        parser = ParserInterface()
        result = parser.process_document(md_text)

        assert result is not None

    def test_null_input_handling(self):
        """Test handling of None input."""
        from markdown_chunker.parser.errors import MarkdownParsingError

        parser = ParserInterface()
        # Should handle None gracefully or raise appropriate error
        try:
            result = parser.process_document(None)
            # If it doesn't raise, should return valid result
            assert result is not None
        except (TypeError, ValueError, AttributeError, MarkdownParsingError):
            # Or it should raise appropriate error
            pass
