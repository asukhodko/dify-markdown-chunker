"""Tests for fenced block extractor."""

from markdown_chunker.parser import FencedBlockExtractor, extract_fenced_blocks

from .test_data import (
    CODE_BLOCKS,
    EDGE_CASES,
    NESTED_BLOCKS,
    SIMPLE_MARKDOWN,
)


class TestFencedBlockExtractor:
    """Test fenced block extraction."""

    def test_simple_extraction(self):
        """Test extracting simple fenced blocks."""
        blocks = extract_fenced_blocks(SIMPLE_MARKDOWN)

        assert len(blocks) == 1
        block = blocks[0]

        assert block.language == "python"
        assert "def hello():" in block.content
        assert block.fence_type == "```"
        assert block.is_closed
        assert block.nesting_level == 0

    def test_nested_blocks(self):
        """Test extracting fenced blocks from document with nested structure."""
        blocks = extract_fenced_blocks(NESTED_BLOCKS)

        # Should find blocks (nested block parsing is complex, not required for Stage 1)
        assert len(blocks) >= 2

        # All blocks should be at level 0 (nested parsing not yet implemented)
        nesting_levels = [block.nesting_level for block in blocks]
        assert 0 in nesting_levels  # Outer blocks found
        # Note: Nested block detection is a Stage 2 feature

    def test_multiple_languages(self):
        """Test extracting blocks with different languages."""
        blocks = extract_fenced_blocks(CODE_BLOCKS)

        languages = {block.language for block in blocks if block.language}
        expected_languages = {"python", "javascript", "go", "bash"}

        assert expected_languages.issubset(languages)

    def test_unclosed_block(self):
        """Test handling unclosed blocks."""
        blocks = extract_fenced_blocks(EDGE_CASES["unclosed_block"])

        assert len(blocks) == 1
        block = blocks[0]

        assert not block.is_closed
        assert block.language == "python"
        assert "def unclosed():" in block.content

    def test_mixed_fence_types(self):
        """Test handling mixed fence types."""
        blocks = extract_fenced_blocks(EDGE_CASES["mixed_fences"])

        assert len(blocks) == 2

        fence_types = {block.fence_type for block in blocks}
        assert "```" in fence_types
        assert "~~~" in fence_types

    def test_empty_input(self):
        """Test handling empty input."""
        blocks = extract_fenced_blocks(EDGE_CASES["empty"])
        assert len(blocks) == 0

    def test_whitespace_only(self):
        """Test handling whitespace-only input."""
        blocks = extract_fenced_blocks(EDGE_CASES["whitespace_only"])
        assert len(blocks) == 0

    def test_position_calculation(self):
        """Test position calculation."""
        markdown = """Line 1
Line 2
```python
code here
```
Line 6"""

        blocks = extract_fenced_blocks(markdown)
        assert len(blocks) == 1

        block = blocks[0]
        assert block.start_line == 3  # 1-based indexing: ``` starts on line 3
        assert block.end_line == 5  # 1-based indexing: ``` ends on line 5
        assert block.start_offset > 0
        assert block.end_offset > block.start_offset


class TestFencedBlockExtractorClass:
    """Test FencedBlockExtractor class directly."""

    def test_extractor_initialization(self):
        """Test extractor initialization."""
        extractor = FencedBlockExtractor()

        assert "backtick" in extractor.fence_patterns
        assert "tilde" in extractor.fence_patterns
        assert "backtick" in extractor.closing_patterns
        assert "tilde" in extractor.closing_patterns

    def test_calculate_offset(self):
        """Test offset calculation."""
        extractor = FencedBlockExtractor()
        lines = ["Line 1", "Line 2", "Line 3"]

        assert extractor._calculate_offset(lines, 0) == 0
        assert extractor._calculate_offset(lines, 1) == 7  # "Line 1" + newline
        assert extractor._calculate_offset(lines, 2) == 14  # "Line 1\nLine 2" + newline
