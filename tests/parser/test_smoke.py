"""
Smoke tests for quick functionality validation.

These tests provide fast sanity checks for core functionality without
detailed edge case testing.

Migration note: Migrated to markdown_chunker_v2 (December 2025)
V2 uses Parser.analyze() instead of extract_fenced_blocks().
"""

import pytest

from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis


class TestSmoke:
    """Quick smoke tests for basic functionality."""

    def test_basic_extraction_works(self):
        """Basic extraction works."""
        parser = Parser()
        markdown = "```python\nprint('hello')\n```"
        analysis = parser.analyze(markdown)

        assert len(analysis.code_blocks) == 1
        assert analysis.code_blocks[0].language == "python"
        assert analysis.code_blocks[0].content == "print('hello')"

    def test_line_numbering_is_1based(self):
        """Line numbering is 1-based."""
        parser = Parser()
        markdown = "Line 1\n```python\ncode\n```\nLine 5"
        analysis = parser.analyze(markdown)

        assert len(analysis.code_blocks) == 1
        assert analysis.code_blocks[0].start_line == 2  # Second line in 1-based
        assert analysis.code_blocks[0].end_line == 4  # Fourth line in 1-based

    def test_multiple_blocks_work(self):
        """Multiple blocks work correctly."""
        parser = Parser()
        markdown = """```python
print("first")
```

Some text

```javascript
console.log("second");
```"""
        analysis = parser.analyze(markdown)

        assert len(analysis.code_blocks) == 2
        assert analysis.code_blocks[0].language == "python"
        assert analysis.code_blocks[1].language == "javascript"

    def test_empty_language_handled(self):
        """Empty language is handled."""
        parser = Parser()
        markdown = "```\nsome code\n```"
        analysis = parser.analyze(markdown)

        assert len(analysis.code_blocks) == 1
        assert (
            analysis.code_blocks[0].language is None
            or analysis.code_blocks[0].language == ""
        )

    def test_language_normalization(self):
        """Language names are extracted correctly."""
        parser = Parser()
        test_cases = [
            ("```python\nprint('test')\n```", "python"),
            ("```javascript\nconsole.log('test');\n```", "javascript"),
            ("```html\n<div></div>\n```", "html"),
        ]

        for markdown, expected_language in test_cases:
            analysis = parser.analyze(markdown)
            assert (
                len(analysis.code_blocks) == 1
            ), f"Expected 1 block for {expected_language}"
            assert (
                analysis.code_blocks[0].language == expected_language
            ), f"Expected language '{expected_language}', got '{analysis.code_blocks[0].language}'"

    def test_performance_reasonable(self):
        """Performance is reasonable for typical documents."""
        import time

        parser = Parser()
        # Create a moderately complex document
        markdown = """# Header

```python
def function1():
    return "test"
```

## Subheader

Some content here.

```bash
echo "final block"
```"""

        start_time = time.time()
        analysis = parser.analyze(markdown)
        processing_time = time.time() - start_time

        # Should complete quickly
        assert processing_time < 1.0, f"Processing took {processing_time:.3f}s"

        # Should extract all blocks
        assert len(analysis.code_blocks) >= 2

    def test_error_handling_graceful(self):
        """Error handling is graceful."""
        parser = Parser()
        # Test with problematic input
        problematic_inputs = [
            "",  # Empty string
            "```",  # Just opening fence
            "```\n```",  # Empty block
        ]

        for markdown in problematic_inputs:
            try:
                analysis = parser.analyze(markdown)
                # Should not crash, may return empty list or partial results
                assert isinstance(analysis, ContentAnalysis)
            except Exception as e:
                pytest.fail(f"Should handle '{markdown}' gracefully, got: {e}")

    def test_headers_extracted(self):
        """Headers are extracted correctly."""
        parser = Parser()
        markdown = """# Main Title

## Section 1

Content here.

### Subsection 1.1

More content.

## Section 2

Final content.
"""
        analysis = parser.analyze(markdown)

        assert analysis.header_count == 4
        assert len(analysis.headers) == 4
        assert analysis.headers[0].level == 1
        assert analysis.headers[0].text == "Main Title"
        assert analysis.headers[1].level == 2
        assert analysis.headers[2].level == 3
        assert analysis.max_header_depth == 3

    def test_tables_extracted(self):
        """Tables are extracted correctly."""
        parser = Parser()
        markdown = """# Table Example

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

Some text after.
"""
        analysis = parser.analyze(markdown)

        assert analysis.table_count == 1
        assert len(analysis.tables) == 1
        assert analysis.tables[0].column_count >= 1
        assert analysis.tables[0].row_count >= 1

    def test_content_metrics(self):
        """Content metrics are calculated correctly."""
        parser = Parser()
        markdown = """# Title

Some text content.

```python
def hello():
    return "world"
```
"""
        analysis = parser.analyze(markdown)

        assert analysis.total_chars > 0
        assert analysis.total_lines > 0
        assert 0 <= analysis.code_ratio <= 1
        assert analysis.code_block_count == 1

    def test_preamble_detection(self):
        """Preamble detection works."""
        parser = Parser()

        # Document with preamble
        markdown_with_preamble = """This is preamble content.

# First Header

Content after header.
"""
        analysis = parser.analyze(markdown_with_preamble)
        assert analysis.has_preamble is True

        # Document without preamble
        markdown_no_preamble = """# First Header

Content after header.
"""
        analysis = parser.analyze(markdown_no_preamble)
        assert analysis.has_preamble is False

    def test_code_blocks_inside_headers_ignored(self):
        """Headers inside code blocks are not extracted."""
        parser = Parser()
        markdown = """# Real Header

```markdown
# This is not a header
## Neither is this
```

## Another Real Header
"""
        analysis = parser.analyze(markdown)

        # Should only find 2 real headers, not the ones inside code block
        assert analysis.header_count == 2
        assert analysis.headers[0].text == "Real Header"
        assert analysis.headers[1].text == "Another Real Header"


class TestParserLineConversion:
    """Tests for line number conversion utilities."""

    def test_get_line_at_position(self):
        """Line at position works correctly."""
        parser = Parser()
        markdown = "Line 1\nLine 2\nLine 3"

        # Position 0 is line 1
        assert parser.get_line_at_position(markdown, 0) == 1

        # Position 7 (start of "Line 2") is line 2
        assert parser.get_line_at_position(markdown, 7) == 2

    def test_get_position_at_line(self):
        """Position at line works correctly."""
        parser = Parser()
        markdown = "Line 1\nLine 2\nLine 3"

        # Line 1 starts at position 0
        assert parser.get_position_at_line(markdown, 1) == 0

        # Line 2 starts at position 7
        assert parser.get_position_at_line(markdown, 2) == 7
