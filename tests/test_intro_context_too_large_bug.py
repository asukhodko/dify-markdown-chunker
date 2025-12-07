"""
Test for the intro_context too large bug.

Bug: When text_before has an intro_context pattern BUT the combined
(intro + list) is too large, the text_before was NOT processed,
causing current_line to not be updated, leading to inverted line numbers
when the next list block is processed.

The error was: "end_line (298) must be >= start_line (305)"
"""

import pytest

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


def test_intro_context_too_large_skips_text():
    """
    Test that when intro_context exists but combined is too large,
    the text_before is still processed and current_line is updated.

    This reproduces the exact bug from Dify:
    - Text at line ~298 has "following:" pattern (intro_context)
    - List starts at line ~305
    - Combined is too large
    - text_before was never chunked, so current_line stayed at 1
    - When list block is processed with start_line=305, end_line=298
    - Result: inverted line numbers!
    """
    # Create padding to push list to line ~305
    padding_lines = "\n".join([f"Padding line {i}" for i in range(1, 295)])

    md_text = f"""{padding_lines}

# Section Header

This section includes the following:

- First item in the list
  with continuation lines
  and more content
- Second item
  also with continuation
- Third item
  final continuation"""

    # Use small max_chunk_size to force the combined to be too large
    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=500,  # Too small for combined intro + list
            list_ratio_threshold=0.1,
        )
    )

    # Before the fix, this would raise:
    # ValueError: end_line (298) must be >= start_line (305)
    chunks = chunker.chunk(md_text)

    # Verify all chunks have valid line numbers
    for i, chunk in enumerate(chunks):
        assert (
            chunk.start_line >= 1
        ), f"Chunk {i}: start_line must be >= 1, got {chunk.start_line}"
        assert chunk.end_line >= chunk.start_line, (
            f"Chunk {i}: inverted line numbers - "
            f"start={chunk.start_line}, end={chunk.end_line}"
        )

    # Verify that the intro text was processed
    intro_found = any("following:" in chunk.content.lower() for chunk in chunks)
    assert intro_found, "Introduction text should be in some chunk"

    # Verify that the list was processed
    list_found = any("First item" in chunk.content for chunk in chunks)
    assert list_found, "List content should be in some chunk"


def test_no_intro_context_text_before_processed():
    """
    Test that when text_before has NO intro_context,
    it's still processed and current_line is updated.
    """
    padding_lines = "\n".join([f"Line {i}" for i in range(1, 100)])

    md_text = f"""{padding_lines}

Some regular text without intro pattern.

More text here.

- List item 1
  continuation
- List item 2"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=500,
            list_ratio_threshold=0.1,
        )
    )

    chunks = chunker.chunk(md_text)

    # Verify all chunks have valid line numbers
    for i, chunk in enumerate(chunks):
        assert chunk.end_line >= chunk.start_line, f"Chunk {i}: inverted line numbers"

    # Verify regular text was processed
    text_found = any("regular text" in chunk.content.lower() for chunk in chunks)
    assert text_found, "Regular text should be in some chunk"


def test_multiple_lists_with_intro_context():
    """
    Test multiple list blocks where some have intro_context.
    """
    md_text = """# Document

Padding text here to increase size.

## Section 1

This section includes the following:

- Item A
  continuation A
- Item B

## Section 2

Another section with items such as:

- Item C
  continuation C
- Item D

## Section 3

Final items:

- Item E
- Item F"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=300,  # Small to force splitting
            list_ratio_threshold=0.1,
        )
    )

    chunks = chunker.chunk(md_text)

    # Verify all chunks have valid line numbers
    for i, chunk in enumerate(chunks):
        assert chunk.end_line >= chunk.start_line, f"Chunk {i}: inverted line numbers"

    # The main goal is no inverted line numbers
    assert len(chunks) >= 1, "Document should produce at least one chunk"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
