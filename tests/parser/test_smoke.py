"""
Smoke tests for quick functionality validation.

These tests provide fast sanity checks for core functionality without
detailed edge case testing.
"""

import pytest

from markdown_chunker.parser import (
    LineNumberConverter,
    extract_fenced_blocks,
    validate_block_sequence,
)


class TestSmoke:
    """Quick smoke tests for basic functionality."""

    def test_basic_extraction_works(self):
        """Basic extraction works."""
        markdown = "```python\nprint('hello')\n```"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert blocks[0].content == "print('hello')"

    def test_line_numbering_is_1based(self):
        """Line numbering is 1-based."""
        markdown = "Line 1\n```python\ncode\n```\nLine 5"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].start_line == 2  # Second line in 1-based
        assert blocks[0].end_line == 4  # Fourth line in 1-based

    def test_line_converter_works(self):
        """Line converter works correctly."""
        # 0-based to 1-based
        assert LineNumberConverter.to_api_line_number(0) == 1
        assert LineNumberConverter.to_api_line_number(5) == 6

        # 1-based to 0-based
        assert LineNumberConverter.from_api_line_number(1) == 0
        assert LineNumberConverter.from_api_line_number(6) == 5

    def test_simple_nesting_works(self):
        """Simple nesting works."""
        markdown = """~~~markdown
# Header

```python
def hello():
    return "world"
```
~~~"""
        blocks = extract_fenced_blocks(markdown)
        # NEW CORRECT BEHAVIOR: Only outer block, nested content preserved
        assert len(blocks) == 1

        # Should be level 0 (outermost only)
        assert blocks[0].nesting_level == 0
        # Verify nested content is preserved
        assert "```python" in blocks[0].content

    def test_multiple_blocks_work(self):
        """Multiple blocks work correctly."""
        markdown = """```python
print("first")
```

Some text

```javascript
console.log("second");
```"""
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "javascript"

    def test_unclosed_blocks_handled(self):
        """Unclosed blocks are handled gracefully."""
        markdown = """```python
print("unclosed")
# No closing fence"""
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1
        assert not blocks[0].is_closed

    def test_empty_language_handled(self):
        """Empty language is handled."""
        markdown = "```\nsome code\n```"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].language is None or blocks[0].language == ""

    def test_tilde_fences_work(self):
        """Tilde fences work."""
        markdown = "~~~python\nprint('tilde')\n~~~"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1
        assert blocks[0].language == "python"
        assert blocks[0].fence_type == "~~~"

    def test_phantom_block_prevention_works(self):
        """Phantom block prevention works."""
        # This should not create phantom blocks
        markdown = """```python
print("real block")
```
```python
print("another real block")
```"""
        blocks = extract_fenced_blocks(markdown)

        # Validate no phantom blocks detected
        warnings = validate_block_sequence(blocks)
        # Should have minimal or no warnings for legitimate blocks
        assert len(warnings) <= 1  # Allow for minor warnings

    def test_language_normalization(self):
        """Language names are normalized to lowercase."""
        test_cases = [
            ("```PYTHON\nprint('test')\n```", "python"),
            ("```JavaScript\nconsole.log('test');\n```", "javascript"),
            ("```C++\nint main() {}\n```", "c++"),
            ("```HTML\n<div></div>\n```", "html"),
        ]

        for markdown, expected_language in test_cases:
            blocks = extract_fenced_blocks(markdown)
            assert len(blocks) == 1, f"Expected 1 block for {expected_language}"
            assert (
                blocks[0].language == expected_language
            ), f"Expected language '{expected_language}', got '{blocks[0].language}'"

    def test_performance_reasonable(self):
        """Performance is reasonable for typical documents."""
        import time

        # Create a moderately complex document
        markdown = """# Header

```python
def function1():
    return "test"
```

## Subheader

~~~markdown
# Inner doc

```javascript
console.log("nested");
```

More content.
~~~

```bash
echo "final block"
```"""

        start_time = time.time()
        blocks = extract_fenced_blocks(markdown)
        processing_time = time.time() - start_time

        # Should complete quickly
        assert processing_time < 1.0, f"Processing took {processing_time:.3f}s"

        # Should extract all blocks
        assert len(blocks) >= 3

        # NEW CORRECT BEHAVIOR: All blocks are level 0 (outermost only)
        nesting_levels = [block.nesting_level for block in blocks]
        assert max(nesting_levels) == 0  # All blocks should be level 0

    def test_error_handling_graceful(self):
        """Error handling is graceful."""
        # Test with problematic input
        problematic_inputs = [
            "",  # Empty string
            "```",  # Just opening fence
            "```\n```",  # Empty block
            "~~~\n```\n~~~",  # Mixed unclosed
        ]

        for markdown in problematic_inputs:
            try:
                blocks = extract_fenced_blocks(markdown)
                # Should not crash, may return empty list or partial results
                assert isinstance(blocks, list)
            except Exception as e:
                pytest.fail(f"Should handle '{markdown}' gracefully, got: {e}")
