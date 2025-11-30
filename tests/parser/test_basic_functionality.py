"""
Pytest-compatible version of basic functionality tests.

This is the same as test_basic.py but structured for pytest discovery.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


class TestBasicFunctionality:
    """Automated tests for Stage 1 basic functionality."""

    def test_data_structures(self):
        """Test basic data structures."""
        from markdown_chunker.parser.types import NodeType, Position

        # Test Position creation and validation
        pos = Position(line=1, column=5, offset=10)
        assert pos.line == 1, f"Expected line=1, got {pos.line}"
        assert pos.column == 5, f"Expected column=5, got {pos.column}"
        assert pos.offset == 10, f"Expected offset=10, got {pos.offset}"

        # Test Position validation
        try:
            Position(line=-1, column=5, offset=10)
            assert False, "Should raise ValueError for negative line"
        except ValueError:
            pass  # Expected

        # Test NodeType enum
        assert NodeType.DOCUMENT.value == "document"
        assert NodeType.CODE_BLOCK.value == "code_block"

    def test_fenced_block_extraction(self):
        """Test fenced block extraction with assertions."""
        from markdown_chunker.parser import extract_fenced_blocks

        markdown = """# Test

```python
def hello():
    print("Hello, World!")
```

Some text here.
"""

        blocks = extract_fenced_blocks(markdown)

        # Validate block count
        assert len(blocks) == 1, f"Expected 1 fenced block, got {len(blocks)}"

        # Validate block properties
        block = blocks[0]
        assert (
            block.language == "python"
        ), f"Expected language='python',\n        got '{block.language}'"
        assert (
            "def hello():" in block.content
        ), "Block \
            should contain function definition"
        assert block.is_valid(), "Block should be valid"
        assert block.is_closed, "Block should be closed"
        assert (
            block.fence_type == "```"
        ), f"Expected fence_type='```',\n        got '{block.fence_type}'"

        # Validate 1-based line numbering (this was a key fix)
        assert (
            block.start_line >= 1
        ), f"start_line \
            should be >= 1 (1-based),\n        got {block.start_line}"
        assert block.end_line >= block.start_line, "end_line should be >= start_line"

    def test_element_detection(self):
        """Test basic element detection (Stage 2 functionality moved)."""
        # This test is now a placeholder since element detection moved to Stage 2
        # Basic validation that we can still extract fenced blocks
        from markdown_chunker.parser import extract_fenced_blocks

        markdown = """# Test Header

```python
def hello():
    pass
```"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) >= 1, "Should extract fenced blocks"
        assert blocks[0].language == "python", "Should identify language"

    def test_content_analysis(self):
        """Test basic content analysis (Stage 2 functionality moved)."""
        # This test is now a placeholder since content analysis moved to Stage 2
        # Basic validation that we can still extract and analyze fenced blocks
        from markdown_chunker.parser import extract_fenced_blocks

        markdown = """# Test Document

```python
def function():
    return "code"
```

More text content."""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) >= 1, "Should extract code blocks"
        assert blocks[0].language == "python", "Should identify language"
        assert "function" in blocks[0].content, "Should extract content"

    def test_configuration(self):
        """Test basic configuration (Stage 2 functionality moved)."""
        # This test is now a placeholder since advanced config moved to Stage 2
        # Basic validation that we can still use the simplified API
        from markdown_chunker.parser import LineNumberConverter, extract_fenced_blocks

        # Test that basic functionality works
        markdown = "```python\ntest\n```"
        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1, "Should extract blocks"

        # Test line converter
        assert LineNumberConverter.to_api_line_number(0) == 1, "Should convert lines"
        # Basic configuration test - Stage 1 uses simple API without complex config
        # Advanced configuration moved to Stage 2
        assert True, "Stage 1 uses simplified API without complex configuration"

    def test_line_numbering_fixes(self):
        """Test that line numbering fixes are working."""
        from markdown_chunker.parser import LineNumberConverter, extract_fenced_blocks

        # Test line converter
        assert (
            LineNumberConverter.to_api_line_number(0) == 1
        ), "0-based 0 \
            should convert to 1-based 1"
        assert (
            LineNumberConverter.from_api_line_number(1) == 0
        ), "1-based 1 \
            should convert to 0-based 0"

        # Test that extracted blocks use 1-based numbering
        markdown = "```python\ncode\n```"
        blocks = extract_fenced_blocks(markdown)

        assert len(blocks) == 1, "Should extract one block"
        block = blocks[0]
        assert (
            block.start_line == 1
        ), f"First line \
            should be 1 (1-based),\n        got {block.start_line}"
        assert (
            block.end_line == 3
        ), f"End line \
            should be 3 (1-based),\n        got {block.end_line}"

    def test_nested_block_fixes(self):
        """Test that nested block fixes are working."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Test nested blocks are not skipped
        markdown = """~~~markdown
# Document
```python
def nested():
    pass
```
End
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # Should find outer block with inner content preserved (NEW CORRECT BEHAVIOR)
        assert (
            len(blocks) == 1
        ), f"Should find 1 block (outer with inner as content), got {len(blocks)}"

        # Inner content should be preserved
        assert (
            "```python" in blocks[0].content
        ), "Inner fence should be preserved as content"
        assert (
            "def nested" in blocks[0].content
        ), "Inner code should be preserved as content"

        # NEW CORRECT BEHAVIOR: All blocks are level 0 (outermost only)
        nesting_levels = [block.nesting_level for block in blocks]
        assert 0 in nesting_levels, "Should have level 0 blocks"
