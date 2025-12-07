"""
Integration test for the critical bug fix in list handling.

This test simulates the real Dify plugin scenario that was failing
with the error: "end_line (298) must be >= start_line (305)"
"""

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


def test_dify_scenario_large_document_with_lists():
    """
    Reproduce the exact scenario from Dify plugin usage.

    The bug occurred when:
    1. Large document (300+ lines)
    2. Lists with continuation lines near the end
    3. ListAware strategy activated
    4. Parser incorrectly set ListBlock.end_line
    """
    # Create document similar to Dify usage pattern
    # 300 lines of content, then lists with continuations
    padding = "\n".join([f"Line {i}" for i in range(1, 296)])

    md_text = f"""{padding}

# Section at line 297

Introduction text here.

- Item 1 at line ~301
  This is a continuation line
  And another continuation
- Item 2
  With its own continuation
- Item 3
  Final continuation line"""

    # This configuration mimics Dify plugin settings
    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=2000,
            min_chunk_size=200,
            overlap_size=100,
            list_ratio_threshold=0.3,
        )
    )

    # This used to raise:
    # ValueError: end_line (298) must be >= start_line (305)
    chunks = chunker.chunk(md_text)

    # Verify all chunks are valid
    assert len(chunks) > 0, "Should produce chunks"

    for i, chunk in enumerate(chunks):
        assert (
            chunk.start_line >= 1
        ), f"Chunk {i}: start_line must be >= 1, got {chunk.start_line}"
        assert (
            chunk.end_line >= chunk.start_line
        ), f"Chunk {i}: end_line ({chunk.end_line}) must be >= start_line ({chunk.start_line})"
        assert chunk.content.strip(), f"Chunk {i}: content cannot be empty"

    print(f"✓ Successfully created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(
            f"  Chunk {i}: lines {chunk.start_line}-{chunk.end_line} ({chunk.size} chars)"
        )


def test_list_aware_strategy_activation_with_continuation():
    """
    Test that ListAware strategy correctly handles lists with continuations.
    """
    md_text = """# Documentation

The following features are available:

- Authentication
  OAuth 2.0 support
  SAML integration
  MFA options
- Authorization
  Role-based access
  Permission groups
- Monitoring
  Real-time metrics
  Alerting system"""

    chunker = MarkdownChunker(
        ChunkConfig(
            max_chunk_size=500,
            list_ratio_threshold=0.3,
        )
    )

    chunks, strategy_name, analysis = chunker.chunk_with_analysis(md_text)

    # Should activate ListAware strategy
    assert strategy_name == "list_aware", f"Expected list_aware, got {strategy_name}"

    # Verify all chunks have valid line numbers
    for chunk in chunks:
        assert (
            chunk.start_line <= chunk.end_line
        ), f"Invalid chunk: start={chunk.start_line}, end={chunk.end_line}"

    print(f"✓ Strategy: {strategy_name}")
    print(f"✓ List count: {analysis.list_count}")
    print(f"✓ List ratio: {analysis.list_ratio:.2%}")


def test_multiple_lists_with_mixed_continuations():
    """
    Test multiple list blocks with varying continuation patterns.
    """
    md_text = """# Project Tasks

## Phase 1

- Setup repository
  Initialize Git
  Configure CI/CD

- Documentation
  Write README
  API docs

## Phase 2

- Implementation
  Core features
  Tests

- Deployment
  Staging
  Production"""

    chunker = MarkdownChunker(ChunkConfig(max_chunk_size=300))
    chunks = chunker.chunk(md_text)

    # All chunks must have valid line ranges
    for i, chunk in enumerate(chunks):
        assert (
            chunk.end_line >= chunk.start_line
        ), f"Chunk {i}: end_line ({chunk.end_line}) < start_line ({chunk.start_line})"

    print(f"✓ Processed {len(chunks)} chunks successfully")


def test_edge_case_list_at_document_end():
    """
    Test list with continuations at the very end of document.
    """
    md_text = """Start of document

Some content here

- Final list item
  with continuation
  and more continuation"""

    chunker = MarkdownChunker(ChunkConfig())
    chunks = chunker.chunk(md_text)

    assert len(chunks) > 0

    # Last chunk should include the continuation lines
    last_chunk = chunks[-1]
    assert "continuation" in last_chunk.content.lower()
    assert last_chunk.start_line <= last_chunk.end_line


if __name__ == "__main__":
    import pytest

    pytest.main([__file__, "-v", "-s"])
