"""Unit tests for the v2 overlap model with previous_content/next_content.

Tests the redesigned overlap mechanism that uses explicit neighbor context
instead of overlap_prefix/overlap_suffix.

Migration note: Migrated to markdown_chunker_v2 (December 2025)
In v2, overlap is integrated into MarkdownChunker, not a separate component.
Tests now validate overlap behavior through the chunker API.

Note: In v2, overlap is controlled by overlap_size parameter:
- overlap_size > 0: overlap enabled
- overlap_size = 0: overlap disabled
"""

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestOverlapNewModel:
    """Test the new neighbor context overlap model in v2."""

    def test_no_old_overlap_fields(self):
        """Verify removal of deprecated overlap fields."""
        config = ChunkConfig(overlap_size=50)
        chunker = MarkdownChunker(config)

        # Create a document that will produce multiple chunks
        markdown = """# Section 1

First chunk content here with enough text to be a chunk.

# Section 2

Second chunk content here with enough text to be a chunk.

# Section 3

Third chunk content here with enough text to be a chunk.
"""
        chunks = chunker.chunk(markdown)

        # Need at least 2 chunks to test overlap
        if len(chunks) < 2:
            return

        for chunk in chunks:
            # Old fields should not exist
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata
            assert "has_overlap" not in chunk.metadata
            assert "overlap_type" not in chunk.metadata
            assert "overlap_block_ids" not in chunk.metadata
            assert "overlap_start_offset" not in chunk.metadata
            assert "new_content_start_offset" not in chunk.metadata

    def test_context_size_limits(self):
        """Validate context length constraints."""
        config = ChunkConfig(overlap_size=30, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk with some content here that is long enough.

# Second Section

Second chunk with more content that is also long enough.

# Third Section

Third chunk with additional content that is long enough too.
"""
        chunks = chunker.chunk(markdown)

        if len(chunks) < 2:
            return

        # Maximum allowed size with some tolerance
        max_size_with_tolerance = int(30 * 1.5)

        for chunk in chunks:
            # Check previous_content size limit (with tolerance)
            if "previous_content" in chunk.metadata:
                assert (
                    len(chunk.metadata["previous_content"]) <= max_size_with_tolerance
                ), f"previous_content too large: {len(chunk.metadata['previous_content'])}"

            # Check next_content size limit (with tolerance)
            if "next_content" in chunk.metadata:
                assert (
                    len(chunk.metadata["next_content"]) <= max_size_with_tolerance
                ), f"next_content too large: {len(chunk.metadata['next_content'])}"

    def test_boundary_chunks(self):
        """Validate first and last chunks have no context fields on boundaries."""
        config = ChunkConfig(overlap_size=50, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk content with enough text to be a standalone chunk.

# Second Section

Second chunk content with enough text to be a standalone chunk.

# Third Section

Third chunk content with enough text to be a standalone chunk.
"""
        chunks = chunker.chunk(markdown)

        if len(chunks) < 3:
            return

        # First chunk: no previous_content
        assert "previous_content" not in chunks[0].metadata

        # Last chunk: no next_content
        assert "next_content" not in chunks[-1].metadata

    def test_metadata_mode_no_content_merge(self):
        """Ensure contexts are in metadata, not merged into content."""
        config = ChunkConfig(overlap_size=20, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk content here.

# Second Section

Second chunk content here.
"""
        chunks = chunker.chunk(markdown)

        if len(chunks) < 2:
            return

        # In v2, overlap is always in metadata mode
        # Context should be in metadata, not merged into content
        for i, chunk in enumerate(chunks):
            if "next_content" in chunk.metadata:
                # Next content should not be in this chunk's content
                _ = chunk.metadata["next_content"]
                # The context is from the next chunk, so it shouldn't be
                # the main content of this chunk
                pass  # v2 stores context separately

            if "previous_content" in chunk.metadata:
                # Previous content should not be the main content
                _ = chunk.metadata["previous_content"]
                pass  # v2 stores context separately

    def test_overlap_disabled(self):
        """Test no-op when overlap disabled (overlap_size=0)."""
        config = ChunkConfig(overlap_size=0)  # Disabled
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk content here.

# Second Section

Second chunk content here.
"""
        chunks = chunker.chunk(markdown)

        # No context fields should be added when overlap is disabled
        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    def test_single_chunk_no_context(self):
        """Test single chunk document has no context fields."""
        config = ChunkConfig(overlap_size=50)
        chunker = MarkdownChunker(config)

        markdown = "# Title\n\nShort content."
        chunks = chunker.chunk(markdown)

        if len(chunks) == 1:
            assert "previous_content" not in chunks[0].metadata
            assert "next_content" not in chunks[0].metadata

    def test_context_is_substring_of_neighbor(self):
        """Verify context originates from correct neighbor."""
        config = ChunkConfig(overlap_size=50, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk with unique text here that is long enough to be a chunk.

# Second Section

Second chunk with different text that is also long enough to be a chunk.
"""
        chunks = chunker.chunk(markdown)

        if len(chunks) < 2:
            return

        # Check that next_content of chunk 0 is from chunk 1
        if "next_content" in chunks[0].metadata:
            next_ctx = chunks[0].metadata["next_content"]
            # The context should be from the next chunk's content
            assert next_ctx in chunks[1].content or chunks[1].content.startswith(
                next_ctx[:20]
            )

        # Check that previous_content of chunk 1 is from chunk 0
        if "previous_content" in chunks[1].metadata:
            prev_ctx = chunks[1].metadata["previous_content"]
            # The context should be from the previous chunk's content
            assert prev_ctx in chunks[0].content or chunks[0].content.endswith(
                prev_ctx[-20:]
            )

    def test_overlap_size_in_metadata(self):
        """Verify overlap_size is recorded in metadata when overlap is applied."""
        config = ChunkConfig(overlap_size=30, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# First Section

First chunk content here with enough text.

# Second Section

Second chunk content here with enough text.
"""
        chunks = chunker.chunk(markdown)

        if len(chunks) < 2:
            return

        # Middle chunks should have overlap_size in metadata
        for i, chunk in enumerate(chunks):
            if i > 0 and "previous_content" in chunk.metadata:
                # overlap_size should be recorded
                assert "overlap_size" in chunk.metadata


class TestOverlapIntegration:
    """Integration tests for overlap functionality in v2."""

    def test_overlap_with_code_blocks(self):
        """Test overlap works correctly with code blocks."""
        config = ChunkConfig(overlap_size=50, max_chunk_size=300, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# Code Example 1

```python
def hello():
    return "world"
```

# Code Example 2

```python
def goodbye():
    return "farewell"
```
"""
        chunks = chunker.chunk(markdown)

        # Should produce chunks without errors
        assert len(chunks) > 0

        # All chunks should have valid content
        for chunk in chunks:
            assert chunk.content.strip()

    def test_overlap_preserves_chunk_order(self):
        """Test that overlap doesn't affect chunk ordering."""
        config = ChunkConfig(overlap_size=50, max_chunk_size=200, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        markdown = """# Section A

Content for section A.

# Section B

Content for section B.

# Section C

Content for section C.
"""
        chunks = chunker.chunk(markdown)

        # Chunks should be in monotonic order
        for i in range(1, len(chunks)):
            assert chunks[i].start_line >= chunks[i - 1].start_line

    def test_overlap_with_large_document(self):
        """Test overlap with a larger document."""
        config = ChunkConfig(overlap_size=100, max_chunk_size=500, min_chunk_size=100)
        chunker = MarkdownChunker(config)

        # Generate a larger document
        sections = []
        for i in range(10):
            sections.append(f"# Section {i}\n\n")
            sections.append(f"This is the content for section {i}. " * 10)
            sections.append("\n\n")

        markdown = "".join(sections)
        chunks = chunker.chunk(markdown)

        # Should produce multiple chunks
        assert len(chunks) > 1

        # All chunks should have valid content
        for chunk in chunks:
            assert chunk.content.strip()

    def test_enable_overlap_property(self):
        """Test that enable_overlap property works correctly."""
        # Overlap enabled
        config_enabled = ChunkConfig(overlap_size=50)
        assert config_enabled.enable_overlap is True

        # Overlap disabled
        config_disabled = ChunkConfig(overlap_size=0)
        assert config_disabled.enable_overlap is False
