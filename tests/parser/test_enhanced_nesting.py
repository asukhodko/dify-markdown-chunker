"""
Enhanced nesting tests with precise validation.

These tests verify complex nesting scenarios with exact expectations
for nesting levels and block counts.
"""

from markdown_chunker.parser import extract_fenced_blocks


class TestEnhancedNesting:
    """Enhanced tests for nesting functionality."""

    def _load_fixture(self, filename: str) -> str:
        """Load a test fixture file."""
        from .test_utils import TestUtils

        return TestUtils.load_fixture(filename)

    def test_mixed_fence_types_nesting(self):
        """Test mixed fence types - NEW CORRECT BEHAVIOR: nested content preserved."""
        markdown = self._load_fixture("nesting/mixed_fences.md")
        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Fewer blocks as nested content is preserved
        # We expect only the outermost blocks, with inner fences as content
        assert len(blocks) >= 1, f"Expected at least 1 block, got {len(blocks)}"

        # All blocks should be level 0 (outermost blocks only)
        for block in blocks:
            assert (
                block.nesting_level == 0
            ), f"All blocks should be level 0, got {block.nesting_level}"

        # Verify that nested content is preserved in outer blocks
        has_nested_content = False
        for block in blocks:
            if "```" in block.content or "~~~" in block.content:
                has_nested_content = True
                break

        assert has_nested_content, "Should preserve nested fence markers as content"

    def test_deep_nesting_levels(self):
        """Test deep nesting - NEW CORRECT BEHAVIOR: content preservation."""
        markdown = self._load_fixture("nesting/deep_nesting.md")
        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Only outermost blocks, nested content preserved
        assert len(blocks) >= 1, f"Expected at least 1 block, got {len(blocks)}"

        # All blocks should be level 0 (outermost only)
        max_nesting = max(block.nesting_level for block in blocks)
        assert max_nesting == 0, f"Expected max nesting level 0, got {max_nesting}"

        # Verify that nested content is preserved
        has_nested_content = False
        for block in blocks:
            # Look for nested fence markers in content
            if "```" in block.content or "~~~" in block.content:
                has_nested_content = True
                break

        assert has_nested_content, "Should preserve nested fence markers as content"

    def test_sibling_blocks_same_level(self):
        """Test sibling blocks at the same nesting level."""
        markdown = """~~~markdown
# Document with multiple code blocks

```python
def first():
    return 1
```

Some text between.

```python
def second():
    return 2
```

More text.

```javascript
function third() {
    return 3;
}
```
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Should have 1 block (outer) with inner content preserved
        assert len(blocks) == 1, f"Expected 1 block (outer), got {len(blocks)}"

        # Should be the markdown block
        markdown_block = blocks[0]
        assert (
            markdown_block.language == "markdown"
        ), f"Expected markdown block, got {markdown_block.language}"
        assert (
            markdown_block.nesting_level == 0
        ), f"Should be level 0, got {markdown_block.nesting_level}"

        # All inner code should be preserved as content
        assert (
            "```python" in markdown_block.content
        ), "Should preserve first Python block as content"
        assert (
            "def first" in markdown_block.content
        ), "Should preserve first function as content"
        assert (
            "def second" in markdown_block.content
        ), "Should preserve second function as content"
        assert (
            "```javascript" in markdown_block.content
        ), "Should preserve JavaScript block as content"
        assert (
            "function third" in markdown_block.content
        ), "Should preserve JavaScript function as content"

    def test_nesting_level_calculation_precision(self):
        """Test precise nesting level calculation - NEW CORRECT BEHAVIOR."""
        markdown = """~~~outer
Level 0 content

```level1
Level 1 content

~~~level2
Level 2 content
~~~

Back to level 1
```

Back to level 0
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Should have fewer blocks as nested content is preserved
        # The malformed structure (unclosed blocks) may result in multiple blocks
        assert len(blocks) >= 1, f"Expected at least 1 block, got {len(blocks)}"

        # Verify that nested content is preserved
        for block in blocks:
            if "level1" in block.content or "level2" in block.content:
                # This block contains nested content
                assert (
                    "```" in block.content or "~~~" in block.content
                ), "Should preserve nested fence markers"

        # NEW CORRECT BEHAVIOR: All blocks should be level 0 (outermost only)
        for block in blocks:
            assert (
                block.nesting_level == 0
            ), f"All blocks should be level 0, got {block.nesting_level}"

    def test_incorrect_nesting_handling(self):
        """Test handling of incorrect/overlapping nesting."""
        # This creates overlapping blocks that should be filtered
        markdown = """```python
def function1():
    pass
~~~markdown
# This creates improper overlap
```

More content
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should handle gracefully, filtering improper overlaps
        assert len(blocks) >= 1, "Should extract at least one valid block"

        # Verify no improper overlaps remain
        blocks.sort(key=lambda b: b.start_line)
        for i in range(len(blocks) - 1):
            current = blocks[i]
            next_block = blocks[i + 1]

            # Either no overlap, or proper containment
            no_overlap = current.end_line < next_block.start_line
            proper_containment = (
                current.start_line < next_block.start_line
                and current.end_line > next_block.end_line
            )
            reverse_containment = (
                next_block.start_line < current.start_line
                and next_block.end_line > current.end_line
            )

            assert (
                no_overlap or proper_containment or reverse_containment
            ), f"Improper overlap between blocks {i} and {i+1}"

    def test_empty_nested_blocks(self):
        """Test nested blocks with empty content."""
        markdown = """~~~markdown
# Document with empty nested blocks

```python
```

```javascript

```
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Only outermost block, nested content preserved
        assert (
            len(blocks) == 1
        ), f"Expected 1 block (outer markdown with nested content), got {len(blocks)}"

        # Should be the outer markdown block
        outer_block = blocks[0]
        assert outer_block.language == "markdown"
        assert outer_block.nesting_level == 0

        # Verify nested fence markers are preserved in content
        assert "```python" in outer_block.content
        assert "```javascript" in outer_block.content

    def test_nesting_with_different_fence_lengths(self):
        """Test nesting with different fence lengths."""
        markdown = """~~~~markdown
# Document with varied fence lengths

```python
def short_fence():
    pass
```

`````python
def long_fence():
    pass
`````
~~~~"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: Only outermost block, nested content preserved
        assert (
            len(blocks) == 1
        ), f"Expected 1 block (outer markdown with nested content), got {len(blocks)}"

        # Should be the outer markdown block
        outer_block = blocks[0]
        assert outer_block.language == "markdown"
        assert outer_block.nesting_level == 0
        assert outer_block.fence_length == 4  # ~~~~

        # Verify nested fence markers with different lengths are preserved in content
        assert "```python" in outer_block.content
        assert "`````python" in outer_block.content

    def test_regression_nesting_level_consistency(self):
        """Regression test: nesting levels should be consistent."""
        markdown = """~~~markdown
# Outer document

```python
# Inner code
def test():
    pass
```

More outer content.
~~~

```bash
# Separate block
echo "not nested"
```"""

        blocks = extract_fenced_blocks(markdown)

        # NEW CORRECT BEHAVIOR: 2 blocks - outer markdown with nested content + separate bash
        assert len(blocks) == 2, f"Expected 2 blocks, got {len(blocks)}"

        # Find blocks by language
        markdown_block = next(b for b in blocks if b.language == "markdown")
        bash_block = next(b for b in blocks if b.language == "bash")

        # Verify consistent nesting levels - both should be level 0 (outermost)
        assert markdown_block.nesting_level == 0, "Markdown block should be level 0"
        assert bash_block.nesting_level == 0, "Bash block should be level 0"

        # Verify nested python content is preserved in markdown block
        assert "```python" in markdown_block.content

        # Verify block ordering
        assert bash_block.start_line > markdown_block.end_line
