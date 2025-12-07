"""
Test for parser ListBlock.end_line correctness with continuation lines.

This test verifies the fix for the critical bug where ListBlock.end_line
was set to the last item's line_number instead of the actual end index
that includes continuation lines.
"""

from markdown_chunker_v2.parser import Parser


def test_list_block_end_line_includes_continuations():
    """
    Test that ListBlock.end_line includes continuation lines.

    This was the root cause of the bug:
    - items[-1].line_number only gives the marker line
    - end_idx tracks the actual last line including continuations
    - ListBlock.end_line must use end_idx, not items[-1].line_number
    """
    md_text = """- Item 1
  continuation of item 1
  more continuation
- Item 2
  continuation of item 2"""

    parser = Parser()
    analysis = parser.analyze(md_text)

    assert analysis.list_count == 1
    block = analysis.list_blocks[0]

    # Line 1: - Item 1
    # Line 2:   continuation of item 1
    # Line 3:   more continuation
    # Line 4: - Item 2
    # Line 5:   continuation of item 2

    assert block.start_line == 1, f"Expected start_line=1, got {block.start_line}"
    assert block.end_line == 5, f"Expected end_line=5, got {block.end_line}"

    # Verify items
    assert len(block.items) == 2
    assert block.items[0].line_number == 1  # First item marker
    assert block.items[1].line_number == 4  # Second item marker

    # The bug was: end_line = items[-1].line_number = 4
    # The fix: end_line = end_idx + 1 = 5
    assert (
        block.end_line > block.items[-1].line_number
    ), "ListBlock.end_line must include continuation lines after last marker"


def test_list_block_end_line_no_continuation():
    """Test that end_line is correct even without continuation lines."""
    md_text = """- Item 1
- Item 2
- Item 3"""

    parser = Parser()
    analysis = parser.analyze(md_text)

    assert analysis.list_count == 1
    block = analysis.list_blocks[0]

    assert block.start_line == 1
    assert block.end_line == 3
    assert len(block.items) == 3


def test_list_block_end_line_with_trailing_content():
    """Test list block boundaries when followed by other content."""
    md_text = """Some intro text

- Item 1
  continuation
- Item 2

After list paragraph"""

    parser = Parser()
    analysis = parser.analyze(md_text)

    assert analysis.list_count == 1
    block = analysis.list_blocks[0]

    # Line 3: - Item 1
    # Line 4:   continuation
    # Line 5: - Item 2
    # Line 6: (empty)
    # Line 7: After list paragraph

    assert block.start_line == 3
    assert block.end_line == 5, f"Expected end_line=5, got {block.end_line}"


def test_multiple_list_blocks_with_continuations():
    """Test multiple list blocks each with continuation lines."""
    md_text = """- List 1 Item 1
  continuation

Text between

- List 2 Item 1
  continuation
- List 2 Item 2
  more continuation"""

    parser = Parser()
    analysis = parser.analyze(md_text)

    assert analysis.list_count == 2

    block1 = analysis.list_blocks[0]
    assert block1.start_line == 1
    assert block1.end_line == 2, f"Block 1: Expected end_line=2, got {block1.end_line}"

    block2 = analysis.list_blocks[1]
    assert block2.start_line == 6
    assert block2.end_line == 9, f"Block 2: Expected end_line=9, got {block2.end_line}"


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v"])
