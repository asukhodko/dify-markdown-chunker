"""Unit tests for parser module."""

import pytest

from markdown_chunker.parser import Parser
from markdown_chunker.types import ParsingError


class TestParser:
    """Test Parser class."""

    def test_parse_empty_document(self):
        """Parser handles empty document."""
        parser = Parser()
        analysis = parser.analyze("")

        assert analysis.total_chars == 0
        assert analysis.total_lines == 0
        assert analysis.code_ratio == 0.0
        assert analysis.content_type == "text"

    def test_parse_simple_text(self):
        """Parser handles simple text document."""
        parser = Parser()
        markdown = "This is a simple paragraph.\n\nAnother paragraph here."
        analysis = parser.analyze(markdown)

        assert analysis.total_chars == len(markdown)
        assert analysis.total_lines == 3
        assert analysis.code_ratio == 0.0
        assert analysis.content_type == "text"
        assert analysis.code_block_count == 0
        assert analysis.header_count == 0

    def test_parse_code_heavy_document(self):
        """Parser correctly identifies code-heavy document."""
        parser = Parser()
        markdown = """
# Code Example

```python
def hello():
    print("world")
    return True
```

Some text here.

```javascript
console.log("test");
```
"""
        analysis = parser.analyze(markdown)

        assert analysis.code_block_count == 2
        assert analysis.code_ratio > 0.3
        assert analysis.content_type == "code"
        assert "python" in analysis.languages
        assert "javascript" in analysis.languages

    def test_parse_structured_document(self):
        """Parser extracts header hierarchy."""
        parser = Parser()
        markdown = """
# Main Title

## Section 1

### Subsection 1.1

## Section 2
"""
        analysis = parser.analyze(markdown)

        assert analysis.header_count == 4
        assert analysis.max_header_depth == 3
        assert analysis.code_ratio < 0.1
        assert analysis.content_type == "text"

    def test_parse_mixed_content(self):
        """Parser identifies mixed content."""
        parser = Parser()
        # Create document with ~15% code content
        markdown = """
# Documentation

Some explanatory text here to provide context.
We need more text to balance the code ratio.

```python
def hello():
    return True
```

Additional explanatory text follows the code.
This helps maintain the mixed content ratio.
"""
        analysis = parser.analyze(markdown)

        assert analysis.code_block_count == 1
        assert 0.1 <= analysis.code_ratio < 0.3
        assert analysis.content_type == "mixed"

    def test_parse_tables(self):
        """Parser extracts tables."""
        parser = Parser()
        markdown = """
# Data

| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

Some text after table.
"""
        analysis = parser.analyze(markdown)

        assert analysis.table_count == 1
        assert analysis.header_count == 1

    def test_parse_code_without_language(self):
        """Parser handles code blocks without language."""
        parser = Parser()
        markdown = """
```
plain code
```
"""
        analysis = parser.analyze(markdown)

        assert analysis.code_block_count == 1
        assert len(analysis.languages) == 0

    def test_content_type_thresholds(self):
        """Test content type determination thresholds."""
        parser = Parser()

        # Code type (>= 30% code)
        code_doc = "```python\n" + ("x = 1\n" * 100) + "```\ntext"
        analysis = parser.analyze(code_doc)
        assert analysis.content_type == "code"

        # Text type (< 10% code)
        text_doc = ("text paragraph\n" * 100) + "```python\nx=1\n```"
        analysis = parser.analyze(text_doc)
        assert analysis.content_type == "text"
