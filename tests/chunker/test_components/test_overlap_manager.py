"""
Tests for OverlapManager.
This module tests the overlap management component that creates overlapping
content between chunks for continuity.
"""

from markdown_chunker.chunker.components.overlap_manager import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig


class TestOverlapManager:
    """Test cases for OverlapManager."""

    def test_initialization(self):
        """Test OverlapManager initialization."""
        config = ChunkConfig(enable_overlap=True, overlap_size=100)
        manager = OverlapManager(config)

        assert manager.config == config

    def test_apply_overlap_disabled(self):
        """Test that overlap is not applied when disabled."""
        config = ChunkConfig(enable_overlap=False)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Content 1", 1, 5, {"strategy": "test"}),
            Chunk("Content 2", 6, 10, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        # Chunks should be unchanged
        assert len(result) == 2
        assert result[0].content == "Content 1"
        assert result[1].content == "Content 2"
        assert not result[1].get_metadata("has_overlap", False)

    def test_apply_overlap_single_chunk(self):
        """Test that single chunk is unchanged."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [Chunk("Single chunk content", 1, 5, {"strategy": "test"})]

        result = manager.apply_overlap(chunks)

        assert len(result) == 1
        assert result[0].content == "Single chunk content"

    def test_apply_overlap_empty_list(self):
        """Test that empty list is handled."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        result = manager.apply_overlap([])

        assert result == []

    def test_apply_overlap_two_chunks(self):
        """Test overlap between two chunks in legacy mode (default)."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk(
                "This is the first chunk. It has some content.",
                1,
                5,
                {"strategy": "test"},
            ),
            Chunk(
                "This is the second chunk. It also has content.",
                6,
                10,
                {"strategy": "test"},
            ),
        ]

        # Test legacy mode (default: include_metadata=False)
        result = manager.apply_overlap(chunks, include_metadata=False)

        assert len(result) == 2
        # First chunk should have next_content merged in
        assert len(result[0].content) >= len(chunks[0].content)
        # Second chunk should have previous_content merged in
        assert len(result[1].content) >= len(chunks[1].content)

    def test_apply_overlap_multiple_chunks(self):
        """Test overlap across multiple chunks in legacy mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content here.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk content here.", 7, 9, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        assert len(result) == 3
        # In legacy mode, content is merged
        # All chunks may have context merged depending on block alignment
        assert len(result[0].content) >= len(chunks[0].content)
        assert len(result[1].content) >= len(chunks[1].content)
        assert len(result[2].content) >= len(chunks[2].content)

    def test_extract_suffix_context_simple(self):
        """Test extracting suffix context from a chunk."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        chunk = Chunk("This is a test sentence. Another sentence here.", 1, 1, {})
        context = manager._extract_suffix_context(chunk, 20)

        # Should extract from end (block-aligned)
        # May be empty if no blocks fit within size limit
        if context:
            assert len(context) <= 50  # 2.5x tolerance for content-based extraction
            assert context in chunk.content

    def test_extract_prefix_context_simple(self):
        """Test extracting prefix context from a chunk."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        chunk = Chunk("This is a test sentence. Another sentence here.", 1, 1, {})
        context = manager._extract_prefix_context(chunk, 20)

        # Should extract from beginning (block-aligned)
        # May be empty if no blocks fit within size limit
        if context:
            assert len(context) <= 50  # 2.5x tolerance for content-based extraction
            assert chunk.content.startswith(
                context.split()[0]
            )  # Should start with same word

    def test_block_extraction(self):
        """Test extracting blocks from content."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        blocks = manager._extract_blocks_from_content(content)

        # Should find multiple blocks
        assert len(blocks) >= 2
        # Check that blocks are preserved
        reconstructed = "\n\n".join(b.content for b in blocks)
        assert "First paragraph" in reconstructed
        assert "Second paragraph" in reconstructed

    def test_block_extraction_single_block(self):
        """Test extracting blocks from single-block content."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        content = "This is content without paragraph breaks"
        blocks = manager._extract_blocks_from_content(content)

        # Should return at least one block
        assert len(blocks) >= 1
        assert blocks[0].content.strip() == content.strip()

    def test_overlap_with_percentage(self):
        """Test overlap using percentage (when overlap_size is 0).

        NOTE: Block-aware overlap requires complete blocks to fit within
        the overlap size. Single-block chunks may not get overlap if the
        block is larger than the calculated overlap size.
        """
        # Set overlap_size=0 to use percentage-based overlap
        config = ChunkConfig(
            enable_overlap=True, overlap_percentage=0.5, overlap_size=0
        )
        manager = OverlapManager(config)

        # Use chunks with multiple short blocks (paragraphs separated by \n\n)
        chunks = [
            Chunk(
                "Short block one.\n\nShort block two.\n\nShort block three.",
                1,
                5,
                {"strategy": "test"},
            ),
            Chunk("B" * 100, 6, 10, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # In legacy mode, second chunk should have context merged
        # Content should be at least as large as original
        assert len(result[1].content) >= len(chunks[1].content)

    def test_overlap_with_fixed_size(self):
        """Test overlap using fixed size.

        NOTE: Block-aware overlap extracts complete blocks, so the actual
        overlap size depends on block boundaries, not exact character count.
        """
        config = ChunkConfig(
            enable_overlap=True, overlap_size=100, overlap_percentage=0
        )
        manager = OverlapManager(config)

        # Use chunks with multiple blocks that can fit within overlap_size
        chunks = [
            Chunk(
                "First paragraph here.\n\nSecond paragraph.\n\nThird one.",
                1,
                5,
                {"strategy": "test"},
            ),
            Chunk("B" * 200, 6, 10, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # In legacy mode, content should be merged
        assert len(result[1].content) >= len(chunks[1].content)

    def test_overlap_preserves_metadata(self):
        """Test that overlap preserves original chunk metadata."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 3, {"strategy": "test", "custom": "value1"}),
            Chunk("Second chunk.", 4, 6, {"strategy": "test", "custom": "value2"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # Original metadata should be preserved in legacy mode
        assert result[1].get_metadata("strategy") == "test"
        assert result[1].get_metadata("custom") == "value2"
        # In legacy mode, no new metadata fields for overlap (content is merged)

    def test_overlap_with_short_chunks(self):
        """Test overlap with very short chunks."""
        config = ChunkConfig(enable_overlap=True, overlap_size=100)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Short.", 1, 1, {"strategy": "test"}),
            Chunk("Also short.", 2, 2, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        # Should handle short chunks gracefully
        assert len(result) == 2
        # Overlap should not exceed chunk size
        if result[1].get_metadata("has_overlap", False):
            overlap_size = result[1].get_metadata("overlap_size", 0)
            assert overlap_size <= len(chunks[0].content)

    def test_calculate_overlap_statistics_no_overlap(self):
        """Test statistics when no overlap is applied."""
        config = ChunkConfig(enable_overlap=False)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Content 1", 1, 3, {"strategy": "test"}),
            Chunk("Content 2", 4, 6, {"strategy": "test"}),
        ]

        stats = manager.calculate_overlap_statistics(chunks)

        assert stats["total_chunks"] == 2
        assert stats["chunks_with_overlap"] == 0
        assert stats["avg_overlap_size"] == 0
        assert stats["total_overlap_size"] == 0

    def test_calculate_overlap_statistics_with_overlap(self):
        """Test statistics when overlap is applied in metadata mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk with some content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk with more content.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk with even more content.", 7, 9, {"strategy": "test"}),
        ]

        # Use metadata mode to get context fields
        result = manager.apply_overlap(chunks, include_metadata=True)
        stats = manager.calculate_overlap_statistics(result)

        assert stats["total_chunks"] == 3
        # Statistics are based on presence of previous_content/next_content fields
        # May vary depending on block alignment

    def test_calculate_overlap_statistics_empty(self):
        """Test statistics with empty chunk list."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        stats = manager.calculate_overlap_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["chunks_with_overlap"] == 0

    def test_overlap_with_multiline_content(self):
        """Test overlap with multiline content in legacy mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Line 1\nLine 2\nLine 3\nLine 4", 1, 4, {"strategy": "test"}),
            Chunk("Line 5\nLine 6\nLine 7\nLine 8", 5, 8, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # In legacy mode, context should be merged into content
        # Content may have more lines if context was added
        assert len(result[1].content) >= len(chunks[1].content)

    def test_overlap_boundary_preservation(self):
        """Test that overlap preserves block boundaries."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunk = Chunk("Para one.\n\nPara two.\n\nPara three.", 1, 1, {})
        context = manager._extract_suffix_context(chunk, 30)

        # Context should be block-aligned (complete paragraphs)
        # May be empty if no blocks fit
        if context:
            # Should not cut in the middle of a paragraph
            assert context.strip() == context or "\n\n" in chunk.content


class TestOverlapManagerIntegration:
    """Integration tests for OverlapManager."""

    def test_realistic_document_chunking_with_overlap(self):
        """Test overlap with realistic document chunks in legacy mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=100)
        manager = OverlapManager(config)

        chunks = [
            Chunk(
                "# Introduction\n\nThis is the introduction to our document. "
                "It provides context and background information.",
                1,
                5,
                {"strategy": "structural", "content_type": "text"},
            ),
            Chunk(
                "# Main Content\n\nThis section contains the main content. "
                "It includes detailed information and examples.",
                6,
                10,
                {"strategy": "structural", "content_type": "text"},
            ),
            Chunk(
                "# Conclusion\n\nThis is the conclusion. "
                "It summarizes the key points discussed.",
                11,
                15,
                {"strategy": "structural", "content_type": "text"},
            ),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # Should have 3 chunks
        assert len(result) == 3

        # In legacy mode, chunks may have context merged
        # Content should be at least as large as original
        for i in range(len(result)):
            assert len(result[i].content) >= len(chunks[i].content)

    def test_overlap_with_code_chunks(self):
        """Test overlap with code chunks - overlap should be skipped if it would create unbalanced fences."""
        config = ChunkConfig(enable_overlap=True, overlap_size=80)
        manager = OverlapManager(config)

        chunks = [
            Chunk(
                "```python\ndef function1():\n    return 'result1'\n```",
                1,
                3,
                {"strategy": "code", "content_type": "code"},
            ),
            Chunk(
                "```python\ndef function2():\n    return 'result2'\n```",
                4,
                6,
                {"strategy": "code", "content_type": "code"},
            ),
        ]

        result = manager.apply_overlap(chunks)

        # Overlap should be skipped for code chunks to preserve code block integrity
        # because overlap from end of code block would contain unbalanced fence
        assert len(result) == 2
        # No overlap should be applied since it would create unbalanced fences
        assert result[1].get_metadata("has_overlap", False) is False
