"""
Tests for extraction heuristics and edge cases.

These tests verify that the extraction logic handles various edge cases
and potential false positives correctly.
"""

from markdown_chunker.parser import extract_fenced_blocks

from .test_utils import TestUtils, assert_block_count


class TestExtractionHeuristics:
    """Test extraction heuristics and edge case handling."""

    def test_false_positive_prevention(self):
        """Test prevention of false positive block detection."""
        # Text that looks like fences but isn't
        markdown = """# Not Fences

This is just text with backticks ` and tildes ~.

Some code: `print("hello")` inline.

Not a fence: ``incomplete

Also not: ~~~incomplete

Real fence:
```python
print("real")
```"""

        blocks = extract_fenced_blocks(markdown)

        # Should only extract the real fence
        assert_block_count(blocks, 1)
        assert blocks[0].language == "python"
        assert "real" in blocks[0].content

    def test_minimum_fence_length(self):
        """Test minimum fence length requirements."""
        markdown = """# Fence Length Tests

Not a fence (too short):
``
code
``

Not a fence either:
~~
code
~~

Valid fence:
```python
print("valid")
```

Another valid fence:
~~~bash
echo "valid"
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should only extract valid fences (3+ characters)
        assert_block_count(blocks, 2)

        languages = [block.language for block in blocks]
        assert "python" in languages
        assert "bash" in languages

    def test_indented_fences(self):
        """Test handling of indented fences."""
        markdown = """# Indented Fences

Normal fence:
```python
print("normal")
```

Indented fence:
    ```javascript
    console.log("indented");
    ```

Deeply indented:
        ```bash
        echo "deep"
        ```"""

        blocks = extract_fenced_blocks(markdown)

        # Should extract all fences regardless of indentation
        assert_block_count(blocks, 3)

        TestUtils.assert_block_count_by_language(
            blocks, {"python": 1, "javascript": 1, "bash": 1}
        )

    def test_fence_with_extra_characters(self):
        """Test fences with extra characters after language."""
        markdown = """# Fences with Extra Info

```python title="example.py"
print("with title")
```

```javascript {highlight: [1,2]}
console.log("with highlight");
```

```bash copy
echo "with copy button"
```

~~~markdown filename="test.md"
# Markdown content
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should extract all blocks, ignoring extra info
        assert_block_count(blocks, 4)

        # Languages should be extracted correctly
        languages = [block.language for block in blocks if block.language]
        assert "python" in languages
        assert "javascript" in languages
        assert "bash" in languages
        assert "markdown" in languages

    def test_mixed_fence_lengths(self):
        """Test blocks with different fence lengths."""
        markdown = """# Mixed Fence Lengths

```python
print("3 backticks")
```

````python
print("4 backticks")
````

`````python
print("5 backticks")
`````

~~~python
print("3 tildes")
~~~

~~~~python
print("4 tildes")
~~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should extract all blocks
        assert_block_count(blocks, 5)

        # All should be Python
        for block in blocks:
            assert block.language == "python"

        # Check fence lengths are recorded correctly
        fence_lengths = [block.fence_length for block in blocks]
        assert 3 in fence_lengths
        assert 4 in fence_lengths
        assert 5 in fence_lengths

    def test_unclosed_block_handling(self):
        """Test handling of unclosed blocks."""
        markdown = """# Unclosed Blocks

```python
print("this block is not closed")
def function():
    return "still in block"

# Document ends without closing fence"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 1)
        assert not blocks[0].is_closed
        assert blocks[0].language == "python"
        assert "this block is not closed" in blocks[0].content
        assert "still in block" in blocks[0].content

    def test_empty_language_handling(self):
        """Test handling of blocks without language specification."""
        markdown = """# Empty Language

```
generic code block
```

~~~
another generic block
~~~

```
block with spaces after fence
```"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 3)

        # All should have None or empty language
        for block in blocks:
            assert block.language is None or block.language == ""

    def test_case_insensitive_language_detection(self):
        """Test case-insensitive language detection."""
        markdown = """# Case Variations

```Python
print("Python")
```

```JAVASCRIPT
console.log("JAVASCRIPT");
```

```c++
int main() {}
```

```HTML
<div></div>
```"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 4)

        # All languages should be normalized to lowercase
        expected_languages = ["python", "javascript", "c++", "html"]
        actual_languages = [block.language for block in blocks]

        for expected in expected_languages:
            assert expected in actual_languages

    def test_special_characters_in_content(self):
        """Test blocks with special characters in content."""
        markdown = """# Special Characters

```python
# Unicode: café, naïve, résumé
print("Special chars: àáâãäåæçèéêë")
print("Symbols: ©®™€£¥")
```

```bash
echo "Quotes: 'single' \"double\""
echo "Backticks: \\`escaped\\`"
```

```markdown
# Nested markdown with ``` and ~~~
Some text with `inline code`.
~~~
nested block
~~~
```"""

        blocks = extract_fenced_blocks(markdown)

        # Should handle special characters correctly
        assert len(blocks) >= 2  # At least python and bash blocks

        python_block = next(b for b in blocks if b.language == "python")
        assert "café" in python_block.content
        assert "©®™" in python_block.content

        bash_block = next(b for b in blocks if b.language == "bash")
        assert "escaped" in bash_block.content

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios."""
        markdown = """# Whitespace Tests

```python

print("block with leading newline")

```

```javascript
console.log("normal block");
```

```bash


echo "multiple leading newlines"


```"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 3)

        # Content should preserve internal whitespace
        python_block = next(b for b in blocks if b.language == "python")
        assert python_block.content.startswith("\n")

        bash_block = next(b for b in blocks if b.language == "bash")
        assert bash_block.content.count("\n") >= 4  # Multiple newlines preserved

    def test_boundary_detection_accuracy(self):
        """Test accuracy of block boundary detection."""
        markdown = """Line 1
Line 2
```python
def function():
    return "test"
```
Line 7
Line 8"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 1)
        block = blocks[0]

        # Should have precise boundaries
        assert block.start_line == 3  # 1-based
        assert block.end_line == 6  # 1-based
        assert block.language == "python"
        assert "def function" in block.content

    def test_consecutive_blocks_boundaries(self):
        """Test boundary detection for consecutive blocks."""
        markdown = """```python
print("block 1")
```
```javascript
console.log("block 2");
```
```bash
echo "block 3"
```"""

        blocks = extract_fenced_blocks(markdown)

        assert_block_count(blocks, 3)

        # Sort by start line
        blocks.sort(key=lambda b: b.start_line)

        # Verify boundaries don't overlap
        for i in range(len(blocks) - 1):
            current = blocks[i]
            next_block = blocks[i + 1]
            assert (
                current.end_line < next_block.start_line
            ), f"Blocks {i} and {i+1} should not overlap"

    def test_regression_phantom_block_prevention(self):
        """Regression test: ensure phantom blocks are not created."""
        markdown = """```python
print("real block 1")
```
```python
print("real block 2")
```"""

        blocks = extract_fenced_blocks(markdown)

        # Should have exactly 2 blocks, no phantom blocks
        assert_block_count(blocks, 2)

        # Verify content is correct
        contents = [block.content.strip() for block in blocks]
        assert any("real block 1" in content for content in contents)
        assert any("real block 2" in content for content in contents)

        # Verify no overlapping boundaries
        TestUtils.assert_no_overlapping_blocks(blocks)
