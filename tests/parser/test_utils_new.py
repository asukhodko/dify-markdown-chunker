"""
Comprehensive tests for parser.utils module (NEW CODE).

These tests specifically target the NEW refactored code in utils.py.
"""

import pytest

from markdown_chunker.parser.utils import (
    LineNumberConverter,
    PhantomBlockPreventer,
    TextRecoveryUtils,
    convert_from_api_lines,
    convert_to_api_lines,
    create_text_recovery_utils,
    filter_phantom_blocks,
    validate_block_sequence,
)


class TestLineNumberConverterNew:
    """Test LineNumberConverter from utils.py (NEW CODE)."""

    def test_to_api_line_number(self):
        """Test converting 0-based to 1-based."""
        assert LineNumberConverter.to_api_line_number(0) == 1
        assert LineNumberConverter.to_api_line_number(1) == 2
        assert LineNumberConverter.to_api_line_number(99) == 100

    def test_to_api_line_number_negative(self):
        """Test that negative internal line raises ValueError."""
        with pytest.raises(ValueError):
            LineNumberConverter.to_api_line_number(-1)

    def test_from_api_line_number(self):
        """Test converting 1-based to 0-based."""
        assert LineNumberConverter.from_api_line_number(1) == 0
        assert LineNumberConverter.from_api_line_number(2) == 1
        assert LineNumberConverter.from_api_line_number(100) == 99

    def test_from_api_line_number_invalid(self):
        """Test that API line < 1 raises ValueError."""
        with pytest.raises(ValueError):
            LineNumberConverter.from_api_line_number(0)

        with pytest.raises(ValueError):
            LineNumberConverter.from_api_line_number(-1)

    def test_validate_api_line_number_valid(self):
        """Test validating valid API line numbers."""
        assert LineNumberConverter.validate_api_line_number(1) is True
        assert LineNumberConverter.validate_api_line_number(100) is True

    def test_validate_api_line_number_invalid(self):
        """Test validating invalid API line numbers."""
        with pytest.raises(ValueError):
            LineNumberConverter.validate_api_line_number(0)

        with pytest.raises(ValueError):
            LineNumberConverter.validate_api_line_number(-1)

    def test_validate_line_range_valid(self):
        """Test validating valid line ranges."""
        assert LineNumberConverter.validate_line_range(1, 10) is True
        assert LineNumberConverter.validate_line_range(5, 5) is True

    def test_validate_line_range_invalid_order(self):
        """Test that end < start raises ValueError."""
        with pytest.raises(ValueError):
            LineNumberConverter.validate_line_range(10, 5)

    def test_validate_line_range_invalid_values(self):
        """Test that invalid line numbers raise ValueError."""
        with pytest.raises(ValueError):
            LineNumberConverter.validate_line_range(0, 10)

        with pytest.raises(ValueError):
            LineNumberConverter.validate_line_range(1, 0)

    def test_round_trip_conversion(self):
        """Test that conversion is reversible."""
        internal = 42
        api = LineNumberConverter.to_api_line_number(internal)
        back_to_internal = LineNumberConverter.from_api_line_number(api)

        assert back_to_internal == internal

    def test_convert_to_api_lines_function(self):
        """Test convert_to_api_lines convenience function."""
        start_api, end_api = convert_to_api_lines(0, 9)

        assert start_api == 1
        assert end_api == 10

    def test_convert_from_api_lines_function(self):
        """Test convert_from_api_lines convenience function."""
        start_internal, end_internal = convert_from_api_lines(1, 10)

        assert start_internal == 0
        assert end_internal == 9

    def test_convert_to_api_lines_invalid(self):
        """Test convert_to_api_lines with invalid input."""
        with pytest.raises(ValueError):
            convert_to_api_lines(-1, 5)

    def test_convert_from_api_lines_invalid(self):
        """Test convert_from_api_lines with invalid input."""
        with pytest.raises(ValueError):
            convert_from_api_lines(0, 10)

        with pytest.raises(ValueError):
            convert_from_api_lines(10, 5)


class TestLineNumberConverterEdgeCases:
    """Test edge cases for LineNumberConverter."""

    def test_zero_to_one(self):
        """Test converting line 0 to line 1."""
        assert LineNumberConverter.to_api_line_number(0) == 1

    def test_large_numbers(self):
        """Test with large line numbers."""
        large_num = 1000000
        api = LineNumberConverter.to_api_line_number(large_num)
        assert api == large_num + 1

        back = LineNumberConverter.from_api_line_number(api)
        assert back == large_num

    def test_single_line_range(self):
        """Test range with same start and end."""
        assert LineNumberConverter.validate_line_range(5, 5) is True

        start, end = convert_to_api_lines(4, 4)
        assert start == 5
        assert end == 5


class TestTextRecoveryUtilsNew:
    """Test TextRecoveryUtils from utils.py (NEW CODE)."""

    def create_mock_block(self, start_line, end_line, content="", **kwargs):
        """Helper to create mock blocks."""

        class MockBlock:
            def __init__(self, start_line, end_line, content="", **kwargs):
                self.start_line = start_line
                self.end_line = end_line
                self.content = content
                for key, value in kwargs.items():
                    setattr(self, key, value)

        return MockBlock(start_line, end_line, content, **kwargs)

    def test_initialization(self):
        """Test TextRecoveryUtils initialization."""
        source = "line 1\nline 2\nline 3"
        utils = TextRecoveryUtils(source)

        assert utils.source_text == source
        assert len(utils.lines) == 3

    def test_get_block_text_with_fences(self):
        """Test recovering block text with fences."""
        source = "# Header\n```python\ncode here\n```\ntext"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(2, 4, "code here")
        result = utils.get_block_text(block, include_fences=True)

        assert "```python" in result
        assert "code here" in result
        assert "```" in result

    def test_get_block_text_without_fences(self):
        """Test recovering block content only."""
        source = "# Header\n```python\ncode here\n```\ntext"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(2, 4, "code here")
        result = utils.get_block_text(block, include_fences=False)

        assert result == "code here"

    def test_get_block_text_invalid_range(self):
        """Test handling invalid line range."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(1, 10, "content")
        result = utils.get_block_text(block, include_fences=True)

        # Should fallback to content
        assert result == "content"

    def test_get_block_context(self):
        """Test getting block with context."""
        source = "line 1\nline 2\n```\ncode\n```\nline 6\nline 7"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(3, 5, "code")
        result = utils.get_block_context(block, context_lines=1)

        assert ">>>" in result  # Block lines marked
        assert "    " in result  # Context lines marked
        assert "line 2" in result  # Context before
        assert "line 6" in result  # Context after

    def test_get_line_text_valid(self):
        """Test getting text of a specific line."""
        source = "line 1\nline 2\nline 3"
        utils = TextRecoveryUtils(source)

        assert utils.get_line_text(1) == "line 1"
        assert utils.get_line_text(2) == "line 2"
        assert utils.get_line_text(3) == "line 3"

    def test_get_line_text_invalid(self):
        """Test getting text of invalid line."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        assert utils.get_line_text(0) == ""
        assert utils.get_line_text(10) == ""
        assert utils.get_line_text(-1) == ""

    def test_get_text_range(self):
        """Test getting text range."""
        source = "line 1\nline 2\nline 3\nline 4"
        utils = TextRecoveryUtils(source)

        result = utils.get_text_range(2, 3)
        assert result == "line 2\nline 3"

    def test_get_text_range_single_line(self):
        """Test getting single line range."""
        source = "line 1\nline 2\nline 3"
        utils = TextRecoveryUtils(source)

        result = utils.get_text_range(2, 2)
        assert result == "line 2"

    def test_get_text_range_invalid(self):
        """Test getting invalid text range."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        assert utils.get_text_range(0, 1) == ""
        assert utils.get_text_range(1, 10) == ""
        assert utils.get_text_range(3, 2) == ""

    def test_find_text_at_position(self):
        """Test finding text at specific position."""
        source = "line 1\nline 2 with content\nline 3"
        utils = TextRecoveryUtils(source)

        # Line 2 is "line 2 with content"
        # Position 6 (1-based) = index 5 (0-based) = '2'
        # Extract 4 characters starting from position 6
        result = utils.find_text_at_position(2, 6, 4)
        assert result == "2 wi"

    def test_find_text_at_position_invalid_line(self):
        """Test finding text at invalid line."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        result = utils.find_text_at_position(10, 1, 5)
        assert result == ""

    def test_find_text_at_position_boundary(self):
        """Test finding text at line boundary."""
        source = "short"
        utils = TextRecoveryUtils(source)

        result = utils.find_text_at_position(1, 1, 100)
        assert result == "short"

    def test_validate_block_recovery_valid(self):
        """Test validating valid block."""
        source = "line 1\n```\ncode\n```\nline 5"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(2, 4, "code")
        issues = utils.validate_block_recovery(block)

        assert len(issues) == 0

    def test_validate_block_recovery_invalid_range(self):
        """Test validating block with invalid range."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(3, 2, "content")
        issues = utils.validate_block_recovery(block)

        assert len(issues) > 0
        assert any("Invalid line range" in issue for issue in issues)

    def test_validate_block_recovery_out_of_bounds(self):
        """Test validating block exceeding document bounds."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(1, 10, "content")
        issues = utils.validate_block_recovery(block)

        assert len(issues) > 0
        assert any("exceeds document length" in issue for issue in issues)

    def test_convenience_function_create_text_recovery_utils(self):
        """Test create_text_recovery_utils convenience function."""
        source = "line 1\nline 2"
        utils = create_text_recovery_utils(source)

        assert isinstance(utils, TextRecoveryUtils)
        assert utils.source_text == source


class TestTextRecoveryUtilsEdgeCases:
    """Test edge cases for TextRecoveryUtils."""

    def create_mock_block(self, start_line, end_line, content="", **kwargs):
        """Helper to create mock blocks."""

        class MockBlock:
            def __init__(self, start_line, end_line, content="", **kwargs):
                self.start_line = start_line
                self.end_line = end_line
                self.content = content
                for key, value in kwargs.items():
                    setattr(self, key, value)

        return MockBlock(start_line, end_line, content, **kwargs)

    def test_empty_source_text(self):
        """Test with empty source text."""
        utils = TextRecoveryUtils("")

        assert utils.source_text == ""
        assert len(utils.lines) == 1  # Empty string splits to ['']

    def test_single_line_source(self):
        """Test with single line source."""
        utils = TextRecoveryUtils("only line")

        assert len(utils.lines) == 1
        assert utils.get_line_text(1) == "only line"

    def test_block_with_raw_content_fallback(self):
        """Test block with raw_content attribute."""
        source = "line 1\nline 2"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(1, 10, "content", raw_content="raw content")
        result = utils.get_block_text(block, include_fences=True)

        assert result == "raw content"

    def test_get_block_context_at_document_start(self):
        """Test getting context at document start."""
        source = "```\ncode\n```\nline 4"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(1, 3, "code")
        result = utils.get_block_context(block, context_lines=2)

        assert ">>>" in result
        assert "line 4" in result

    def test_get_block_context_at_document_end(self):
        """Test getting context at document end."""
        source = "line 1\n```\ncode\n```"
        utils = TextRecoveryUtils(source)

        block = self.create_mock_block(2, 4, "code")
        result = utils.get_block_context(block, context_lines=2)

        assert ">>>" in result
        assert "line 1" in result

    def test_unicode_content(self):
        """Test with unicode content."""
        source = "line 1\n日本語\némoji 😀\nline 4"
        utils = TextRecoveryUtils(source)

        assert utils.get_line_text(2) == "日本語"
        assert utils.get_line_text(3) == "émoji 😀"

    def test_very_long_lines(self):
        """Test with very long lines."""
        long_line = "x" * 10000
        source = f"line 1\n{long_line}\nline 3"
        utils = TextRecoveryUtils(source)

        result = utils.get_line_text(2)
        assert len(result) == 10000

    def test_mixed_line_endings(self):
        """Test with mixed line endings (already normalized)."""
        source = "line 1\nline 2\nline 3"
        utils = TextRecoveryUtils(source)

        assert len(utils.lines) == 3


class TestPhantomBlockPreventerNew:
    """Test PhantomBlockPreventer from utils.py (NEW CODE)."""

    def create_mock_block(self, start_line, end_line, content="", fence_type="```"):
        """Helper to create mock blocks."""

        class MockBlock:
            def __init__(self, start_line, end_line, content="", fence_type="```"):
                self.start_line = start_line
                self.end_line = end_line
                self.content = content
                self.fence_type = fence_type

        return MockBlock(start_line, end_line, content, fence_type)

    def test_validate_block_sequence_empty(self):
        """Test validating empty block sequence."""
        preventer = PhantomBlockPreventer()
        warnings = preventer.validate_block_sequence([])

        assert warnings == []

    def test_validate_block_sequence_single_block(self):
        """Test validating single block."""
        preventer = PhantomBlockPreventer()
        block = self.create_mock_block(1, 3, "content")
        warnings = preventer.validate_block_sequence([block])

        assert warnings == []

    def test_validate_block_sequence_valid_blocks(self):
        """Test validating valid non-overlapping blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "content1"),
            self.create_mock_block(5, 7, "content2"),
            self.create_mock_block(10, 12, "content3"),
        ]
        warnings = preventer.validate_block_sequence(blocks)

        assert warnings == []

    def test_validate_block_sequence_overlapping(self):
        """Test detecting overlapping blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 5, "content1"),
            self.create_mock_block(4, 8, "content2"),  # Overlaps with first
        ]
        warnings = preventer.validate_block_sequence(blocks)

        assert len(warnings) > 0
        assert "overlap" in warnings[0].lower()

    def test_validate_block_sequence_proper_nesting(self):
        """Test proper nesting doesn't trigger warnings."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 10, "outer content"),
            self.create_mock_block(3, 7, "inner content"),  # Properly nested
        ]
        warnings = preventer.validate_block_sequence(blocks)

        # Proper nesting should not trigger warnings
        assert warnings == []

    def test_validate_block_sequence_adjacent_suspicious(self):
        """Test detecting suspicious adjacent blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "short", "```"),
            self.create_mock_block(
                4, 6, "tiny", "```"
            ),  # Adjacent, same fence type, short
        ]
        warnings = preventer.validate_block_sequence(blocks)

        assert len(warnings) > 0
        assert "adjacent" in warnings[0].lower()

    def test_filter_phantom_blocks_empty(self):
        """Test filtering empty list."""
        preventer = PhantomBlockPreventer()
        result = preventer.filter_phantom_blocks([])

        assert result == []

    def test_filter_phantom_blocks_single(self):
        """Test filtering single block."""
        preventer = PhantomBlockPreventer()
        block = self.create_mock_block(1, 3, "content")
        result = preventer.filter_phantom_blocks([block])

        assert len(result) == 1
        assert result[0] == block

    def test_filter_phantom_blocks_valid_blocks(self):
        """Test filtering valid blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "content1"),
            self.create_mock_block(5, 7, "content2"),
            self.create_mock_block(10, 12, "content3"),
        ]
        result = preventer.filter_phantom_blocks(blocks)

        assert len(result) == 3

    def test_filter_phantom_blocks_removes_suspicious(self):
        """Test filtering removes suspicious phantom blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "longer content here", "```"),
            self.create_mock_block(4, 6, "short", "```"),  # Suspicious phantom
        ]
        result = preventer.filter_phantom_blocks(blocks)

        # Should keep the longer block
        assert len(result) == 1
        assert "longer" in result[0].content

    def test_filter_phantom_blocks_keeps_longer(self):
        """Test filtering keeps longer block when both suspicious."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "short", "```"),
            self.create_mock_block(4, 6, "much longer content here", "```"),
        ]
        result = preventer.filter_phantom_blocks(blocks)

        # Should keep the longer block
        assert len(result) == 1
        assert "much longer" in result[0].content

    def test_is_proper_nesting(self):
        """Test proper nesting detection."""
        preventer = PhantomBlockPreventer()

        outer = self.create_mock_block(1, 10, "outer")
        inner = self.create_mock_block(3, 7, "inner")

        assert preventer._is_proper_nesting(outer, inner) is True

    def test_is_not_proper_nesting(self):
        """Test improper nesting detection."""
        preventer = PhantomBlockPreventer()

        block1 = self.create_mock_block(1, 5, "content1")
        block2 = self.create_mock_block(4, 8, "content2")  # Overlaps

        assert preventer._is_proper_nesting(block1, block2) is False

    def test_looks_like_phantom_block_same_fence_short(self):
        """Test phantom detection with same fence type and short content."""
        preventer = PhantomBlockPreventer()

        block1 = self.create_mock_block(1, 3, "short", "```")
        block2 = self.create_mock_block(4, 6, "tiny", "```")

        assert preventer._looks_like_phantom_block(block1, block2) is True

    def test_looks_like_phantom_block_different_fence(self):
        """Test phantom detection with different fence types."""
        preventer = PhantomBlockPreventer()

        block1 = self.create_mock_block(1, 3, "short", "```")
        block2 = self.create_mock_block(4, 6, "tiny", "~~~")

        assert preventer._looks_like_phantom_block(block1, block2) is False

    def test_looks_like_phantom_block_long_content(self):
        """Test phantom detection with long content."""
        preventer = PhantomBlockPreventer()

        block1 = self.create_mock_block(1, 3, "this is longer content", "```")
        block2 = self.create_mock_block(4, 6, "this is also longer", "```")

        assert preventer._looks_like_phantom_block(block1, block2) is False

    def test_convenience_function_validate_block_sequence(self):
        """Test validate_block_sequence convenience function."""
        blocks = [
            self.create_mock_block(1, 3, "content1"),
            self.create_mock_block(5, 7, "content2"),
        ]
        warnings = validate_block_sequence(blocks)

        assert isinstance(warnings, list)

    def test_convenience_function_filter_phantom_blocks(self):
        """Test filter_phantom_blocks convenience function."""
        blocks = [
            self.create_mock_block(1, 3, "content1"),
            self.create_mock_block(5, 7, "content2"),
        ]
        result = filter_phantom_blocks(blocks)

        assert isinstance(result, list)
        assert len(result) == 2


class TestPhantomBlockPreventerEdgeCases:
    """Test edge cases for PhantomBlockPreventer."""

    def create_mock_block(self, start_line, end_line, content="", fence_type="```"):
        """Helper to create mock blocks."""

        class MockBlock:
            def __init__(self, start_line, end_line, content="", fence_type="```"):
                self.start_line = start_line
                self.end_line = end_line
                self.content = content
                self.fence_type = fence_type

        return MockBlock(start_line, end_line, content, fence_type)

    def test_unsorted_blocks(self):
        """Test that blocks are sorted before processing."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(10, 12, "content3"),
            self.create_mock_block(1, 3, "content1"),
            self.create_mock_block(5, 7, "content2"),
        ]
        result = preventer.filter_phantom_blocks(blocks)

        # Should handle unsorted input
        assert len(result) == 3

    def test_multiple_adjacent_blocks(self):
        """Test multiple adjacent suspicious blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "short1", "```"),
            self.create_mock_block(4, 6, "short2", "```"),
            self.create_mock_block(7, 9, "short3", "```"),
        ]
        result = preventer.filter_phantom_blocks(blocks)

        # Should filter out some suspicious blocks
        assert len(result) < 3

    def test_nested_within_nested(self):
        """Test deeply nested blocks."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 20, "outer"),
            self.create_mock_block(3, 15, "middle"),
            self.create_mock_block(5, 10, "inner"),
        ]
        warnings = preventer.validate_block_sequence(blocks)

        # Proper nesting should not trigger warnings
        assert warnings == []

    def test_empty_content_blocks(self):
        """Test blocks with empty content."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "", "```"),
            self.create_mock_block(4, 6, "", "```"),
        ]
        warnings = preventer.validate_block_sequence(blocks)

        # Empty content is suspicious
        assert len(warnings) > 0

    def test_whitespace_only_content(self):
        """Test blocks with whitespace-only content."""
        preventer = PhantomBlockPreventer()
        blocks = [
            self.create_mock_block(1, 3, "   ", "```"),
            self.create_mock_block(4, 6, "  \n  ", "```"),
        ]
        result = preventer.filter_phantom_blocks(blocks)

        # Should filter suspicious blocks
        assert len(result) <= 1
