"""
Tests for precise block boundaries using fixtures.

These tests verify exact start_line and end_line values for extracted blocks
to prevent regressions in boundary calculation.
"""

from markdown_chunker.parser import extract_fenced_blocks


class TestPreciseBoundaries:
    """Test precise block boundaries with fixtures."""

    def _load_fixture(self, filename: str) -> str:
        """Load a test fixture file."""
        from .test_utils import TestUtils

        return TestUtils.load_fixture(filename)

    def test_sequential_blocks_precise_boundaries(self):
        """Test sequential blocks have precise boundaries."""
        markdown = self._load_fixture("sequential_blocks.md")
        blocks = extract_fenced_blocks(markdown)

        # Should extract exactly 2 blocks
        assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"

        # Sort blocks by start line for predictable testing
        blocks.sort(key=lambda b: b.start_line)

        # First block (Python)
        python_block = blocks[0]
        assert python_block.language == "python"
        assert (
            python_block.start_line == 5
        ), f"Python block should start at line 5, got {python_block.start_line}"
        assert (
            python_block.end_line == 8
        ), f"Python block should end at line 8, got {python_block.end_line}"
        assert (
            python_block.content.strip() == 'def first_function():\n    return "first"'
        )

        # Second block (JavaScript)
        js_block = blocks[1]
        assert js_block.language == "javascript"
        assert (
            js_block.start_line == 14
        ), f"JS block should start at line 14, got {js_block.start_line}"
        assert (
            js_block.end_line == 18
        ), f"JS block should end at line 18, got {js_block.end_line}"
        assert "function secondFunction()" in js_block.content

    def test_nested_blocks_precise_boundaries(self):
        """Test nested blocks have precise boundaries."""
        markdown = self._load_fixture("nested_complex.md")
        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Only outermost blocks, nested content preserved
        assert len(blocks) >= 1, f"Expected at least 1 block, got {len(blocks)}"

        # All blocks should be level 0 (outermost only)
        for block in blocks:
            assert (
                block.nesting_level == 0
            ), f"All blocks should be level 0, got {block.nesting_level}"

        # Find outer markdown block
        outer_blocks = [b for b in blocks if b.language == "markdown"]
        if outer_blocks:
            outer_block = outer_blocks[0]
            assert outer_block.start_line >= 1
            assert outer_block.end_line >= outer_block.start_line
            # Verify nested content is preserved
            assert "~~~" in outer_block.content or "```" in outer_block.content

    def test_phantom_prevention_boundaries(self):
        """Test phantom prevention doesn't affect legitimate boundaries."""
        markdown = self._load_fixture("phantom_prevention.md")
        blocks = extract_fenced_blocks(markdown)

        # Should extract all legitimate blocks
        assert len(blocks) >= 4, f"Expected at least 4 blocks, got {len(blocks)}"

        # Sort by start line
        blocks.sort(key=lambda b: b.start_line)

        # Check first two Python blocks (adjacent but legitimate)
        python_blocks = [b for b in blocks if b.language == "python"]
        assert (
            len(python_blocks) == 2
        ), f"Expected 2 Python blocks, got {len(python_blocks)}"

        first_python = python_blocks[0]
        second_python = python_blocks[1]

        # Verify they are sequential but not overlapping
        assert first_python.end_line < second_python.start_line, (
            "Python blocks should not overlap: "
            f"{first_python.end_line} >= {second_python.start_line}"
        )

        # Verify content is correct
        assert "legitimate block 1" in first_python.content
        assert "legitimate block 2" in second_python.content

    def test_mixed_fence_types_boundaries(self):
        """Test mixed fence types have correct boundaries."""
        markdown = """# Mixed Fences

~~~markdown
# Outer document

```python
def nested():
    return "nested"
```

More content.
~~~

```bash
echo "separate block"
```"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: 2 blocks - outer markdown with nested content + separate bash
        assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"

        # Find blocks by type
        markdown_blocks = [b for b in blocks if b.language == "markdown"]
        bash_blocks = [b for b in blocks if b.language == "bash"]

        assert len(markdown_blocks) == 1
        assert len(bash_blocks) == 1

        markdown_block = markdown_blocks[0]
        bash_block = bash_blocks[0]

        # Verify nesting - both should be level 0 (outermost)
        assert markdown_block.nesting_level == 0
        assert bash_block.nesting_level == 0

        # Verify boundaries
        assert markdown_block.fence_type == "~~~"
        assert bash_block.fence_type == "```"

        # Verify nested python content is preserved in markdown block
        assert "```python" in markdown_block.content

        # Bash should be after markdown
        assert bash_block.start_line > markdown_block.end_line

    def test_unclosed_block_boundaries(self):
        """Test unclosed blocks have correct boundaries."""
        markdown = """# Unclosed Block Test

```python
def unclosed_function():
    return "no closing fence"
# Document ends without closing fence"""

        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1, f"Expected 1 unclosed block, got {len(blocks)}"

        block = blocks[0]
        assert not block.is_closed, "Block should be marked as unclosed"
        assert block.language == "python"
        assert (
            block.start_line == 3
        ), f"Unclosed block should start at line 3, got {block.start_line}"
        # End line should be the last line of the document
        lines = markdown.split("\n")
        expected_end_line = len(lines)
        assert block.end_line == expected_end_line, (
            f"Unclosed block should end at line {expected_end_line}, "
            f"got {block.end_line}"
        )

    def test_empty_blocks_boundaries(self):
        """Test empty blocks have correct boundaries."""
        markdown = """# Empty Blocks

```python
```

```javascript

```

```bash


```"""

        blocks = extract_fenced_blocks(markdown)

        # Should extract all blocks even if empty
        assert len(blocks) == 3, f"Expected 3 empty blocks, got {len(blocks)}"

        # Sort by start line
        blocks.sort(key=lambda b: b.start_line)

        # Check each block
        python_block = blocks[0]
        assert python_block.language == "python"
        assert python_block.start_line == 3
        assert python_block.end_line == 4
        assert python_block.content == ""

        js_block = blocks[1]
        assert js_block.language == "javascript"
        assert js_block.start_line == 6
        assert js_block.end_line == 8
        assert js_block.content.strip() == ""

        bash_block = blocks[2]
        assert bash_block.language == "bash"
        assert bash_block.start_line == 10
        assert bash_block.end_line == 13
        assert bash_block.content.strip() == ""

    def test_single_line_blocks_boundaries(self):
        """Test single-line blocks have correct boundaries."""
        markdown = """# Single Line Blocks

```python
print("one line")
```

```bash
echo "another line"
```"""

        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 2, f"Expected 2 single-line blocks, got {len(blocks)}"

        blocks.sort(key=lambda b: b.start_line)

        python_block = blocks[0]
        assert python_block.start_line == 3
        assert python_block.end_line == 5
        assert python_block.content == 'print("one line")'

        bash_block = blocks[1]
        assert bash_block.start_line == 7
        assert bash_block.end_line == 9
        assert bash_block.content == 'echo "another line"'

    def test_regression_no_phantom_blocks_in_sequence(self):
        """Regression test: sequential blocks should not create phantom blocks."""
        markdown = """```python
print("block 1")
```
```python
print("block 2")
```
```python
print("block 3")
```"""

        blocks = extract_fenced_blocks(markdown)

        # Should have exactly 3 blocks, no phantom blocks
        assert len(blocks) == 3, f"Expected exactly 3 blocks, got {len(blocks)}"

        # Verify each block has correct content
        expected_contents = ["block 1", "block 2", "block 3"]
        actual_contents = [block.content.strip() for block in blocks]

        for expected in expected_contents:
            assert any(
                expected in content for content in actual_contents
            ), f"Missing expected content: {expected}"

        # Verify no overlapping boundaries
        blocks.sort(key=lambda b: b.start_line)
        for i in range(len(blocks) - 1):
            current = blocks[i]
            next_block = blocks[i + 1]
            assert current.end_line < next_block.start_line, (
                f"Blocks {i} and {i+1} should not overlap: "
                f"{current.end_line} >= {next_block.start_line}"
            )
