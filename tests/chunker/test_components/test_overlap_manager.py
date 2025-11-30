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
        """Test overlap between two chunks."""
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

        result = manager.apply_overlap(chunks)

        assert len(result) == 2
        # First chunk unchanged
        assert result[0].content == chunks[0].content
        # Second chunk should have overlap
        assert result[1].get_metadata("has_overlap", False) is True
        assert result[1].get_metadata("overlap_type") == "prefix"
        assert len(result[1].content) > len(chunks[1].content)

    def test_apply_overlap_multiple_chunks(self):
        """Test overlap across multiple chunks."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content here.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk content here.", 7, 9, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        assert len(result) == 3
        # First chunk unchanged
        assert not result[0].get_metadata("has_overlap", False)
        # Second and third chunks should have overlap
        assert result[1].get_metadata("has_overlap", False) is True
        assert result[2].get_metadata("has_overlap", False) is True

    def test_extract_suffix_overlap_simple(self):
        """Test extracting suffix overlap."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        content = "This is a test sentence. Another sentence here."
        overlap = manager._extract_suffix_overlap(content, 20)

        # Should extract from end
        assert len(overlap) > 0
        assert len(overlap) <= 30  # Should be close to target
        assert overlap in content

    def test_extract_prefix_overlap_simple(self):
        """Test extracting prefix overlap."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        content = "This is a test sentence. Another sentence here."
        overlap = manager._extract_prefix_overlap(content, 20)

        # Should extract from beginning
        assert len(overlap) > 0
        assert len(overlap) <= 30  # Should be close to target
        assert content.startswith(overlap.split()[0])  # Should start with same word

    def test_split_into_sentences(self):
        """Test splitting content into sentences."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        content = "First sentence. Second sentence! Third sentence? Fourth."
        sentences = manager._split_into_sentences(content)

        assert len(sentences) >= 3  # Should find multiple sentences
        # Check that sentences are preserved
        reconstructed = "".join(sentences)
        assert reconstructed.strip() == content.strip()

    def test_split_into_sentences_no_punctuation(self):
        """Test splitting content without sentence punctuation."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        content = "This is content without proper sentence endings"
        sentences = manager._split_into_sentences(content)

        # Should return empty list when no sentence boundaries found
        # This triggers character-based extraction in the overlap methods
        assert len(sentences) == 0

    def test_overlap_with_percentage(self):
        """Test overlap using percentage (when overlap_size is 0)."""
        # Set overlap_size=0 to use percentage-based overlap
        config = ChunkConfig(enable_overlap=True, overlap_percentage=0.2, overlap_size=0)
        manager = OverlapManager(config)

        chunks = [
            Chunk("A" * 100, 1, 5, {"strategy": "test"}),
            Chunk("B" * 100, 6, 10, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        # Second chunk should have overlap
        assert result[1].get_metadata("has_overlap", False) is True
        overlap_size = result[1].get_metadata("overlap_size", 0)
        # Overlap should be approximately 20% of first chunk
        assert 15 <= overlap_size <= 25  # Allow some variance for sentence boundaries

    def test_overlap_with_fixed_size(self):
        """Test overlap using fixed size."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50, overlap_percentage=0)
        manager = OverlapManager(config)

        chunks = [
            Chunk("A" * 200, 1, 5, {"strategy": "test"}),
            Chunk("B" * 200, 6, 10, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        # Second chunk should have overlap
        assert result[1].get_metadata("has_overlap", False) is True
        overlap_size = result[1].get_metadata("overlap_size", 0)
        # Overlap should be close to 50
        assert 40 <= overlap_size <= 60  # Allow some variance

    def test_overlap_preserves_metadata(self):
        """Test that overlap preserves original chunk metadata."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 3, {"strategy": "test", "custom": "value1"}),
            Chunk("Second chunk.", 4, 6, {"strategy": "test", "custom": "value2"}),
        ]

        result = manager.apply_overlap(chunks)

        # Original metadata should be preserved
        assert result[1].get_metadata("strategy") == "test"
        assert result[1].get_metadata("custom") == "value2"
        # Overlap metadata should be added
        assert result[1].get_metadata("has_overlap") is True

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
        """Test statistics when overlap is applied."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk with some content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk with more content.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk with even more content.", 7, 9, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)
        stats = manager.calculate_overlap_statistics(result)

        assert stats["total_chunks"] == 3
        assert stats["chunks_with_overlap"] == 2  # All except first
        assert stats["avg_overlap_size"] > 0
        assert stats["total_overlap_size"] > 0
        assert stats["overlap_percentage"] > 0

    def test_calculate_overlap_statistics_empty(self):
        """Test statistics with empty chunk list."""
        config = ChunkConfig(enable_overlap=True)
        manager = OverlapManager(config)

        stats = manager.calculate_overlap_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["chunks_with_overlap"] == 0

    def test_overlap_with_multiline_content(self):
        """Test overlap with multiline content."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Line 1\nLine 2\nLine 3\nLine 4", 1, 4, {"strategy": "test"}),
            Chunk("Line 5\nLine 6\nLine 7\nLine 8", 5, 8, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks)

        # Second chunk should have overlap
        assert result[1].get_metadata("has_overlap", False) is True
        # Overlap should preserve line structure
        assert "\n" in result[1].content or result[1].content.count("\n") > chunks[
            1
        ].content.count("\n")

    def test_overlap_boundary_preservation(self):
        """Test that overlap preserves sentence boundaries."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        content = "This is sentence one. This is sentence two. This is sentence three."
        overlap = manager._extract_suffix_overlap(content, 30)

        # Overlap should end at a sentence boundary or be a complete sentence
        # It should not cut in the middle of a word
        assert (
            not overlap
            or overlap[-1] in [".", "!", "?", " "]
            or overlap.endswith("three.")
        )


class TestOverlapManagerIntegration:
    """Integration tests for OverlapManager."""

    def test_realistic_document_chunking_with_overlap(self):
        """Test overlap with realistic document chunks."""
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

        result = manager.apply_overlap(chunks)

        # Should have 3 chunks
        assert len(result) == 3

        # First chunk unchanged
        assert result[0].content == chunks[0].content

        # Second and third chunks should have overlap
        for i in range(1, 3):
            assert result[i].get_metadata("has_overlap") is True
            assert len(result[i].content) > len(chunks[i].content)
            # Should contain some content from previous chunk
            # (This is a heuristic check - actual overlap content may vary)

        # Statistics should be reasonable
        stats = manager.calculate_overlap_statistics(result)
        assert stats["chunks_with_overlap"] == 2
        assert stats["overlap_percentage"] > 60  # 2 out of 3 chunks

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
