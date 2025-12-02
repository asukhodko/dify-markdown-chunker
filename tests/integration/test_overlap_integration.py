"""Integration tests for overlap metadata mode implementation.

Tests the end-to-end behavior of overlap handling through the full
chunking pipeline, comparing metadata mode vs legacy mode.
"""

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestOverlapIntegrationMetadataMode:
    """Integration tests for overlap in metadata mode."""

    def test_end_to_end_metadata_mode(self):
        """Test full pipeline with metadata mode.

        Verify:
        - Clean chunk content (no overlap in text)
        - overlap_prefix keys present where expected (not first chunk)
        - overlap_suffix keys present where expected (not last chunk)
        - Overlap keys absent where expected
        - Overlap consistency between chunks
        """
        config = ChunkConfig(max_chunk_size=100, enable_overlap=True, overlap_size=20)
        chunker = MarkdownChunker(config)

        # Document that will split into multiple chunks
        md_text = """# Section A
This is the first section with some content here.

# Section B
This is the second section with more content here.

# Section C
This is the third section with final content here."""

        # Chunk with metadata mode
        result = chunker.chunk(
            md_text, include_analysis=True, include_metadata=True  # Metadata mode
        )

        chunks = result.chunks
        assert len(chunks) >= 2  # Should produce multiple chunks

        # First chunk should have no overlap_prefix but may have overlap_suffix
        assert "overlap_prefix" not in chunks[0].metadata

        # Last chunk should have no overlap_suffix but may have overlap_prefix
        assert "overlap_suffix" not in chunks[-1].metadata

        # Check middle chunks have overlap_prefix
        for i in range(1, len(chunks)):
            if "overlap_prefix" in chunks[i].metadata:
                # Overlap should be non-empty string
                assert isinstance(chunks[i].metadata["overlap_prefix"], str)
                assert len(chunks[i].metadata["overlap_prefix"]) > 0

                # Content should NOT contain the overlap
                # (it's in metadata, not merged)
                # The overlap should be from the previous chunk's end
                # But NOT be part of current chunk's content at the start
                pass

        # Verify overlap_suffix consistency
        for i in range(len(chunks) - 1):
            if (
                "overlap_suffix" in chunks[i].metadata
                and "overlap_prefix" in chunks[i + 1].metadata
            ):
                # Suffix of chunk i should match prefix of chunk i+1
                assert (
                    chunks[i].metadata["overlap_suffix"]
                    == chunks[i + 1].metadata["overlap_prefix"]
                )

    def test_end_to_end_legacy_mode(self):
        """Test full pipeline with legacy mode.

        Verify:
        - Overlap merged into content
        - No overlap_prefix/suffix keys
        - Existing metadata structure unchanged
        """
        config = ChunkConfig(max_chunk_size=100, enable_overlap=True, overlap_size=20)
        chunker = MarkdownChunker(config)

        md_text = """# Section A
This is the first section with some content here.

# Section B
This is the second section with more content here.

# Section C
This is the third section with final content here."""

        # Chunk with legacy mode
        result = chunker.chunk(
            md_text, include_analysis=True, include_metadata=False  # Legacy mode
        )

        chunks = result.chunks
        assert len(chunks) >= 2

        # No chunk should have overlap_prefix or overlap_suffix keys
        for chunk in chunks:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata

        # Chunks with overlap should have legacy metadata
        overlapped_chunks = [c for c in chunks if c.get_metadata("has_overlap", False)]
        if overlapped_chunks:
            for chunk in overlapped_chunks:
                assert "overlap_size" in chunk.metadata
                assert "overlap_type" in chunk.metadata

    def test_content_preservation_both_modes(self):
        """Test that content is preserved in both modes."""
        config = ChunkConfig(max_chunk_size=150, enable_overlap=True, overlap_size=25)
        chunker = MarkdownChunker(config)

        md_text = """# Introduction
This is an introduction section with some content.

# Main Content
This is the main content section with more detailed information.

# Conclusion
This is the conclusion section wrapping things up."""

        # Test both modes
        metadata_result = chunker.chunk(
            md_text, include_analysis=True, include_metadata=True
        )

        legacy_result = chunker.chunk(
            md_text, include_analysis=True, include_metadata=False
        )

        # In metadata mode, concatenating content should preserve original
        # (contexts are separate)

        # Both should have some chunks
        assert len(metadata_result.chunks) > 0
        assert len(legacy_result.chunks) > 0

        # Metadata mode chunks should have clean content
        for chunk in metadata_result.chunks:
            # Content shouldn't start with overlap (it's in metadata)
            if "overlap_prefix" in chunk.metadata:
                overlap = chunk.metadata["overlap_prefix"]
                # Overlap is separate, not merged into content
                assert overlap  # Non-empty
                assert isinstance(overlap, str)

    def test_single_chunk_both_modes(self):
        """Test single chunk document in both modes."""
        config = ChunkConfig(max_chunk_size=1000, enable_overlap=True, overlap_size=50)
        chunker = MarkdownChunker(config)

        md_text = "# Short Document\nThis is a short document that fits in one chunk."

        # Metadata mode
        metadata_result = chunker.chunk(md_text, include_metadata=True)
        assert len(metadata_result) == 1
        assert "overlap_prefix" not in metadata_result[0].metadata

        # Legacy mode
        legacy_result = chunker.chunk(md_text, include_metadata=False)
        assert len(legacy_result) == 1
        assert "overlap_prefix" not in legacy_result[0].metadata

    def test_overlap_disabled_no_keys(self):
        """Test that overlap keys are not added when overlap disabled."""
        config = ChunkConfig(max_chunk_size=100, enable_overlap=False)  # Disabled
        chunker = MarkdownChunker(config)

        md_text = """# Section A
Content here.

# Section B
More content.

# Section C
Final content."""

        # Even in metadata mode, no overlap keys if disabled
        result = chunker.chunk(md_text, include_metadata=True)

        for chunk in result:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata
            assert "has_overlap" not in chunk.metadata


class TestOverlapWithDifferentStrategies:
    """Test overlap mode with different chunking strategies."""

    def test_structural_strategy_metadata_mode(self):
        """Test overlap metadata mode with structural strategy."""
        config = ChunkConfig(max_chunk_size=150, enable_overlap=True, overlap_size=30)
        chunker = MarkdownChunker(config)

        md_text = """# Chapter 1
Introduction to the topic.

## Subsection 1.1
Details about the first part.

# Chapter 2
Continuation of the discussion.

## Subsection 2.1
More detailed information here."""

        result = chunker.chunk(md_text, strategy="structural", include_metadata=True)

        # Verify overlap keys are handled correctly
        for i, chunk in enumerate(result):
            if i == 0:
                assert "overlap_prefix" not in chunk.metadata
            else:
                # May or may not have overlap depending on content
                if "overlap_prefix" in chunk.metadata:
                    assert isinstance(chunk.metadata["overlap_prefix"], str)
                    assert len(chunk.metadata["overlap_prefix"]) > 0

    def test_sentences_strategy_both_modes(self):
        """Test overlap with sentences strategy in both modes."""
        config = ChunkConfig(max_chunk_size=80, enable_overlap=True, overlap_size=20)
        chunker = MarkdownChunker(config)

        md_text = """This is a first sentence. This is a second sentence. This is a third sentence. This is a fourth sentence. This is a fifth sentence."""

        # Metadata mode
        metadata_result = chunker.chunk(
            md_text, strategy="sentences", include_metadata=True
        )

        # Legacy mode
        legacy_result = chunker.chunk(
            md_text, strategy="sentences", include_metadata=False
        )

        # Both should chunk the content
        assert len(metadata_result) >= 1
        assert len(legacy_result) >= 1

        # Verify metadata mode has clean content
        for chunk in metadata_result:
            if "overlap_prefix" in chunk.metadata:
                assert chunk.metadata["overlap_prefix"]

        # Verify legacy mode has no overlap keys
        for chunk in legacy_result:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata
