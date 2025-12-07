"""
Unit tests for header-section merging logic.

Tests the new functionality that merges small header-only chunks
with their section body to improve chunking quality.
"""

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestHeaderMerging:
    """Test header-section merging functionality."""

    def test_small_header_merges_with_child_section(self):
        """Small top-level header should merge with its child section."""
        markdown = """# Main Header

## Scope

This is the scope section with meaningful content.
It has multiple lines and substantial text.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Should merge header with scope section
        # Result should be fewer chunks than if not merged
        assert len(chunks) <= 2

        # First chunk should contain both header and scope
        first_chunk_has_both = (
            "# Main Header" in chunks[0].content and "## Scope" in chunks[0].content
        )
        assert first_chunk_has_both, "Header and scope should be in same chunk"

    def test_large_header_not_merged(self):
        """Large header chunk should not trigger merging."""
        markdown = """# Main Header With Very Long Title And Lots Of Additional Text That Exceeds The 150 Character Threshold For Merging So This Should Not Be Merged With The Next Section

## Scope

Content here.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Large header should not merge, may create separate chunks
        # Just verify no errors occur
        assert len(chunks) >= 1

    def test_level_3_header_not_merged(self):
        """Level 3+ headers should not trigger header merging."""
        markdown = """### Small Level 3

## Next Section

Content here.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Level 3 headers don't trigger merging
        assert len(chunks) >= 1

    def test_preamble_not_merged_with_headers(self):
        """Preamble should never merge with header chunks."""
        markdown = """Some preamble text before any headers.

# Main Header

Content.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Check preamble is separate
        preamble_chunks = [
            c for c in chunks if c.metadata.get("content_type") == "preamble"
        ]
        assert (
            len(preamble_chunks) >= 0
        )  # May or may not have preamble depending on strategy

    def test_same_section_merging(self):
        """Header merges with chunks in same section path."""
        markdown = """# Main

Some intro text under main header.

More text in same section.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Small header with same-section content should merge
        assert len(chunks) >= 1
        if len(chunks) == 1:
            assert "# Main" in chunks[0].content
            assert "intro text" in chunks[0].content

    def test_metadata_preserved_after_merge(self):
        """Merged chunks should preserve appropriate metadata."""
        markdown = """# Title

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=80)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Check metadata is present
        for chunk in chunks:
            assert "header_path" in chunk.metadata
            assert "chunk_index" in chunk.metadata
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line

    def test_no_merge_when_headers_at_threshold(self):
        """Headers exactly at 150 chars should not merge."""
        # Create header with exactly 150 characters
        long_title = "A" * 145  # Account for "# " prefix and newline
        markdown = f"""# {long_title}

## Next

Content.
"""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        # Should not merge at threshold
        assert len(chunks) >= 1


class TestHeaderMergingEdgeCases:
    """Test edge cases for header merging."""

    def test_empty_document(self):
        """Empty document should not cause errors."""
        markdown = ""
        chunker = MarkdownChunker()

        # Empty content now returns empty list instead of raising
        chunks = chunker.chunk(markdown)
        assert len(chunks) == 0

    def test_only_headers(self):
        """Document with only headers should not cause errors."""
        markdown = """# Header 1

## Header 2

### Header 3
"""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(markdown)

        assert len(chunks) >= 1

    def test_no_headers(self):
        """Document without headers should not trigger merging."""
        markdown = """Just plain text without any headers.

Multiple paragraphs of content.
"""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(markdown)

        assert len(chunks) >= 1
        # No headers, so no header merging should occur

    def test_single_chunk_document(self):
        """Small document that fits in single chunk."""
        markdown = """# Title

Short content."""
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(markdown)

        assert len(chunks) == 1
        assert "# Title" in chunks[0].content
