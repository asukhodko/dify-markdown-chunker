"""Regression tests to prevent return to 0-based line numbering."""

from markdown_chunker.parser import extract_fenced_blocks


class TestLineNumberingRegression:
    """Regression tests for 1-based line numbering."""

    def test_prevent_zero_based_line_numbers(self):
        """Ensure line numbers are never 0-based (regression test)."""
        markdown = """```python
print("hello")
```"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        block = blocks[0]

        # Line numbers must be >= 1 (1-based)
        assert block.start_line >= 1, f"start_line must be >= 1, got {block.start_line}"
        assert block.end_line >= 1, f"end_line must be >= 1, got {block.end_line}"

        # For this specific case, should be lines 1-3
        assert block.start_line == 1, f"Expected start_line=1, got {block.start_line}"
        assert block.end_line == 3, f"Expected end_line=3, got {block.end_line}"

    def test_multiple_blocks_never_zero_based(self):
        """Ensure multiple blocks never use 0-based numbering."""
        markdown = """First line
```python
code1
```
Middle line
```javascript
code2
```
Last line"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 2

        for i, block in enumerate(blocks):
            assert (
                block.start_line >= 1
            ), f"Block {i} start_line \
            must be >= 1,\n        got {block.start_line}"
            assert (
                block.end_line >= 1
            ), f"Block {i} end_line \
            must be >= 1,\n        got {block.end_line}"
            assert (
                block.end_line >= block.start_line
            ), f"Block {i} end_line \
            must be >= start_line"

    def test_line_number_consistency(self):
        """Test that line numbers are consistent across different scenarios."""
        test_cases = [
            # (markdown, blocks_count, first_start, first_end)
            ("```\ncode\n```", 1, 1, 3),
            ("line1\n```\ncode\n```", 1, 2, 4),
            ("line1\nline2\n```\ncode\n```\nline6", 1, 3, 5),
        ]

        for markdown, expected_count, expected_start, expected_end in test_cases:
            blocks = extract_fenced_blocks(markdown)
            assert (
                len(blocks) == expected_count
            ), f"Expected {expected_count} blocks for: {repr(markdown)}"

            if blocks:
                block = blocks[0]
                assert block.start_line == expected_start, (
                    f"Expected start_line={expected_start}, "
                    f"got {block.start_line} for: {repr(markdown)}"
                )
                assert block.end_line == expected_end, (
                    f"Expected end_line={expected_end}, "
                    f"got {block.end_line} for: {repr(markdown)}"
                )

    def test_unclosed_block_line_numbers(self):
        """Test that unclosed blocks also use 1-based numbering."""
        markdown = """Line 1
Line 2
```python
unclosed code
more code"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        block = blocks[0]
        assert not block.is_closed, "Block should be unclosed"
        assert block.start_line == 3, f"Expected start_line=3, got {block.start_line}"
        assert (
            block.end_line >= 3
        ), f"end_line \
            must be >= start_line,\n        got {block.end_line}"
        # For unclosed block, end_line should be the last line (1-based)
        assert (
            block.end_line == 5
        ), f"Expected end_line=5 for unclosed block,\n        got {block.end_line}"

    def test_nested_blocks_line_numbers(self):
        """Test that nested blocks use 1-based numbering."""
        markdown = """# Header
~~~markdown
# Inner header
```python
nested_code()
```
More inner content
~~~
# Outer header"""

        blocks = extract_fenced_blocks(markdown)
        # Should find at least the outer block
        assert len(blocks) >= 1

        for block in blocks:
            assert (
                block.start_line >= 1
            ), f"Block start_line \
            must be >= 1,\n        got {block.start_line}"
            assert (
                block.end_line >= 1
            ), f"Block end_line \
            must be >= 1,\n        got {block.end_line}"
            assert block.end_line >= block.start_line, "end_line must be >= start_line"

    def test_api_compliance_validation(self):
        """Test that all returned blocks comply with 1-based API specification."""
        markdown = """```python
def func1():
    pass
```

Some text

```javascript
function func2() {}
```

```go
func main() {}
```"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 3, f"Expected 3 blocks, got {len(blocks)}"

        # Validate each block follows 1-based API
        for i, block in enumerate(blocks):
            # All line numbers must be positive (1-based)
            assert (
                block.start_line > 0
            ), f"Block {i} start_line \
            must be > 0,\n        got {block.start_line}"
            assert (
                block.end_line > 0
            ), f"Block {i} end_line \
            must be > 0,\n        got {block.end_line}"

            # End must be >= start
            assert (
                block.end_line >= block.start_line
            ), f"Block {i} end_line \
            must be >= start_line"

            # Blocks should be in order
            if i > 0:
                prev_block = blocks[i - 1]
                assert (
                    block.start_line > prev_block.end_line
                ), f"Block {i} \
            should start after previous block ends"

    def test_line_number_validation_methods(self):
        """Test that line number validation methods work correctly."""
        from markdown_chunker.parser import LineNumberConverter

        markdown = "```\ntest\n```"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        block = blocks[0]

        # Should not raise exceptions for valid 1-based line numbers
        assert LineNumberConverter.validate_api_line_number(block.start_line)
        assert LineNumberConverter.validate_api_line_number(block.end_line)
        assert LineNumberConverter.validate_line_range(block.start_line, block.end_line)
