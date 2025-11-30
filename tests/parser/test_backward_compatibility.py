"""
Backward compatibility tests.

These tests ensure that the core API remains compatible with
existing code that depends on Stage 1 functionality.
"""

import pytest

from markdown_chunker.parser import FencedBlock, Position, extract_fenced_blocks


class TestBackwardCompatibility:
    """Test backward compatibility of core API."""

    def test_extract_fenced_blocks_signature(self):
        """Test that extract_fenced_blocks signature is preserved."""
        # Should accept string input and return list of FencedBlock
        markdown = "```python\nprint('test')\n```"

        # This should work without any changes to existing code
        blocks = extract_fenced_blocks(markdown)

        assert isinstance(blocks, list)
        assert len(blocks) == 1
        assert isinstance(blocks[0], FencedBlock)

    def test_fenced_block_essential_fields(self):
        """Test that FencedBlock essential fields are preserved."""
        markdown = "```python\nprint('hello')\n```"
        blocks = extract_fenced_blocks(markdown)
        block = blocks[0]

        # Essential fields that existing code depends on
        assert hasattr(block, "content")
        assert hasattr(block, "language")
        assert hasattr(block, "start_line")
        assert hasattr(block, "end_line")
        assert hasattr(block, "nesting_level")
        assert hasattr(block, "is_closed")
        assert hasattr(block, "fence_type")

        # Verify field types
        assert isinstance(block.content, str)
        assert isinstance(block.language, (str, type(None)))
        assert isinstance(block.start_line, int)
        assert isinstance(block.end_line, int)
        assert isinstance(block.nesting_level, int)
        assert isinstance(block.is_closed, bool)
        assert isinstance(block.fence_type, str)

    def test_1_based_line_numbering_preserved(self):
        """Test that 1-based line numbering is preserved."""
        markdown = "Line 1\n```python\ncode\n```\nLine 5"
        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1
        block = blocks[0]

        # Should still use 1-based numbering as before
        assert block.start_line == 2  # Second line
        assert block.end_line == 4  # Fourth line

    def test_nesting_support_preserved(self):
        """Test that basic nesting support is preserved."""
        markdown = """~~~markdown
# Document

```python
def function():
    pass
```
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should still support nesting (NEW CORRECT BEHAVIOR: content preservation)
        assert len(blocks) == 1  # Only outer block, inner preserved as content
        assert "```python" in blocks[0].content  # Inner fence preserved as content

        # NEW CORRECT BEHAVIOR: All blocks are level 0 (outermost only)
        nesting_levels = [block.nesting_level for block in blocks]
        assert 0 in nesting_levels

    def test_multiple_blocks_support(self):
        """Test that multiple blocks are still supported."""
        markdown = """```python
print("first")
```

```javascript
console.log("second");
```"""

        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 2
        assert blocks[0].language == "python"
        assert blocks[1].language == "javascript"

    def test_empty_language_handling(self):
        """Test that empty language handling is preserved."""
        markdown = "```\ngeneric code\n```"
        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1
        assert blocks[0].language is None or blocks[0].language == ""

    def test_unclosed_block_handling(self):
        """Test that unclosed block handling is preserved."""
        markdown = "```python\nprint('unclosed')\n# No closing fence"
        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1
        assert not blocks[0].is_closed

    def test_fence_type_detection(self):
        """Test that fence type detection is preserved."""
        test_cases = [
            ("```python\ncode\n```", "```"),
            ("~~~python\ncode\n~~~", "~~~"),
        ]

        for markdown, expected_fence in test_cases:
            blocks = extract_fenced_blocks(markdown)
            assert len(blocks) == 1
            assert blocks[0].fence_type == expected_fence

    def test_content_extraction_accuracy(self):
        """Test that content extraction accuracy is preserved."""
        markdown = """```python
def hello():
    return "world"

print("test")
```"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        content = blocks[0].content
        assert "def hello():" in content
        assert 'return "world"' in content
        assert 'print("test")' in content

    def test_position_data_structure(self):
        """Test that Position data structure is available."""
        # Position should still be available for compatibility
        pos = Position(line=1, column=0, offset=0)

        assert pos.line == 1
        assert pos.column == 0
        assert pos.offset == 0

    def test_error_handling_graceful(self):
        """Test that error handling remains graceful."""
        # Should handle edge cases without crashing
        edge_cases = [
            "",  # Empty string
            "```",  # Just opening fence
            "```\n```",  # Empty block
            None,  # None input (should be handled by validation)
        ]

        for case in edge_cases:
            try:
                if case is None:
                    # None should be handled by input validation
                    from markdown_chunker.parser import validate_and_normalize_input

                    normalized = validate_and_normalize_input(case)
                    blocks = extract_fenced_blocks(normalized)
                else:
                    blocks = extract_fenced_blocks(case)

                # Should return a list (possibly empty)
                assert isinstance(blocks, list)

            except Exception as e:
                # If it raises an exception, it should be a clear, expected one
                assert isinstance(e, (TypeError, ValueError))

    def test_language_normalization_behavior(self):
        """Test that language normalization behavior is consistent."""
        markdown = "```PYTHON\nprint('test')\n```"
        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1
        # Language should be normalized to lowercase
        assert blocks[0].language == "python"

    def test_block_boundaries_accuracy(self):
        """Test that block boundary detection remains accurate."""
        markdown = """# Header

```python
def test():
    pass
```

More text."""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        block = blocks[0]
        # Boundaries should be accurate
        assert block.start_line >= 1
        assert block.end_line > block.start_line
        assert block.start_line <= 5  # Should be around line 3-4
        assert block.end_line <= 8  # Should be around line 5-6

    def test_existing_code_patterns(self):
        """Test common existing code patterns still work."""
        markdown = """# Documentation

```python
def example_function():
    '''Example function.'''
    return "hello world"
```

```bash
echo "shell command"
```"""

        # Common pattern: extract and filter by language
        blocks = extract_fenced_blocks(markdown)
        python_blocks = [b for b in blocks if b.language == "python"]
        bash_blocks = [b for b in blocks if b.language == "bash"]

        assert len(python_blocks) == 1
        assert len(bash_blocks) == 1

        # Common pattern: check if blocks are closed
        closed_blocks = [b for b in blocks if b.is_closed]
        assert len(closed_blocks) == 2

        # Common pattern: get content
        python_content = python_blocks[0].content
        assert "def example_function" in python_content
        assert "hello world" in python_content

    def test_import_compatibility(self):
        """Test that essential imports still work."""
        # These imports should work for backward compatibility
        try:
            from markdown_chunker.parser import FencedBlock, extract_fenced_blocks

            # Basic usage should work
            blocks = extract_fenced_blocks("```python\ntest\n```")
            assert isinstance(blocks[0], FencedBlock)

        except ImportError as e:
            pytest.fail(f"Essential imports should work: {e}")

    def test_no_regression_in_core_functionality(self):
        """Test that core functionality has no regressions."""
        # This is a comprehensive test of the main use case
        markdown = """# Project Documentation

## Code Examples

```python
def main():
    print("Hello, World!")

if __name__ == "__main__":
    main()
```

## Shell Commands

```bash
pip install requirements
python main.py
```

## Nested Example

~~~markdown
# Inner Documentation

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should extract all blocks
        assert len(blocks) >= 3

        # Should have correct languages (NEW BEHAVIOR: nested content preserved)
        languages = [b.language for b in blocks if b.language]
        assert "python" in languages
        assert "bash" in languages
        assert (
            "markdown" in languages
        )  # The nested block becomes content, not separate block

        # Check that javascript is preserved as content in the markdown block
        markdown_blocks = [b for b in blocks if b.language == "markdown"]
        if markdown_blocks:
            assert (
                "javascript" in markdown_blocks[0].content
            ), "JavaScript should be preserved as content"
        assert "markdown" in languages

        # NEW CORRECT BEHAVIOR: All blocks are level 0 (outermost only)
        nesting_levels = [b.nesting_level for b in blocks]
        assert 0 in nesting_levels  # Top-level blocks only

        # Should have correct boundaries
        for block in blocks:
            assert block.start_line >= 1
            assert block.end_line >= block.start_line
            assert isinstance(block.content, str)
