"""
Test for list continuation line bug.

Bug: When list items have continuation lines, the ListBlock.end_line
is incorrectly set to the last item's line_number instead of including
the continuation lines, causing chunks to have inverted line numbers.
"""

import pytest

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


def test_list_with_continuation_lines_chunk_line_numbers():
    """Test that chunks from lists with continuation lines have valid line numbers."""
    md_text = """# Document

Some intro text.

- First item
  continues here
  and here
- Second item
  also continues
- Third item
"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=4096,
            list_ratio_threshold=0.3,  # Lower to activate ListAware
        )
    )

    chunks = chunker.chunk(md_text)

    # Verify all chunks have valid line numbers
    for i, chunk in enumerate(chunks):
        assert (
            chunk.start_line >= 1
        ), f"Chunk {i}: start_line must be >= 1, got {chunk.start_line}"
        assert (
            chunk.end_line >= chunk.start_line
        ), f"Chunk {i}: end_line ({chunk.end_line}) must be >= start_line ({chunk.start_line})"


def test_list_block_end_line_includes_continuation():
    """Test that ListBlock.end_line includes continuation lines."""
    md_text = """- Item 1
  continuation of item 1
  more continuation
- Item 2
  continuation
- Item 3"""

    from markdown_chunker_v2.parser import Parser

    parser = Parser()
    analysis = parser.analyze(md_text)

    # Should have 1 list block
    assert analysis.list_count == 1

    block = analysis.list_blocks[0]

    # Block should start at line 1 (first item)
    assert block.start_line == 1

    # Block should end at line 6 (last line of last item)
    # Not at line 5 (where "- Item 3" marker is)
    assert (
        block.end_line == 6
    ), f"Expected end_line=6 to include all continuation lines, got {block.end_line}"


def test_list_strategy_with_multiline_items():
    """Test ListAware strategy with multi-line list items."""
    md_text = """# Features

Our new features include:

- Authentication system
  with OAuth2 support
  and JWT tokens
- Database layer
  with connection pooling
  and query optimization
- API endpoints
  following REST principles
"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=4096,
            list_ratio_threshold=0.3,
        )
    )

    chunks = chunker.chunk(md_text)

    # All chunks should have valid line numbers
    for chunk in chunks:
        assert (
            chunk.end_line >= chunk.start_line
        ), f"Invalid line range: start={chunk.start_line}, end={chunk.end_line}"


def test_nested_list_with_continuation_lines():
    """Test nested lists where items have continuation lines."""
    md_text = """- Top level item
  continues here
  - Nested item 1
    with continuation
  - Nested item 2
    also continues
- Another top level
  with more text"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=4096,
            list_ratio_threshold=0.2,
        )
    )

    chunks = chunker.chunk(md_text)

    for chunk in chunks:
        assert chunk.start_line >= 1
        assert (
            chunk.end_line >= chunk.start_line
        ), f"Chunk line numbers inverted: start={chunk.start_line}, end={chunk.end_line}"


def test_list_item_group_reconstruction():
    """Test that list item groups are reconstructed with correct line numbers."""
    md_text = """- Item 1 with a very long text that continues on the next line
  and keeps going here
- Item 2 also long
  continues
- Item 3"""

    from markdown_chunker_v2.parser import Parser
    from markdown_chunker_v2.strategies.list_aware import ListAwareStrategy

    parser = Parser()
    analysis = parser.analyze(md_text)

    assert analysis.list_count == 1
    block = analysis.list_blocks[0]

    strategy = ListAwareStrategy()

    lines = md_text.split("\n")

    # Test reconstruction of item group
    items = block.items[:2]  # First two items
    group_text, actual_end_line = strategy._reconstruct_item_group(items, lines, block)

    # Verify the reconstruction includes continuation lines
    assert "continues on the next line" in group_text
    assert "and keeps going here" in group_text
    assert "continues" in group_text

    # Verify actual_end_line is correct
    assert (
        actual_end_line > items[-1].line_number
    ), "End line should include continuation lines"


def test_inverted_line_numbers_bug():
    """Reproduce the exact bug: chunks with inverted line numbers."""
    # Create a document where list items appear in reverse order
    # or where continuation lines cause line number issues
    padding = "\n" * 300
    md_text = f"""# Large Document
{padding}
# Section Near End

- Item at line ~305
  continuation line
  more continuation
- Another item
"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=500,  # Small to force splitting
            list_ratio_threshold=0.1,
        )
    )

    # This should not raise ValueError
    chunks = chunker.chunk(md_text)

    # Verify all chunks have valid line numbers
    for chunk in chunks:
        assert (
            chunk.start_line <= chunk.end_line
        ), f"Inverted line numbers: start={chunk.start_line}, end={chunk.end_line}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
