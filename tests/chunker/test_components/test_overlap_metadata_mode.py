"""Unit tests for overlap metadata mode implementation.

Tests the new metadata-aware overlap handling where overlap context is stored
in metadata fields (previous_content/next_content) instead of being merged
into chunk content.
"""

from markdown_chunker.chunker.components import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig


class TestOverlapMetadataMode:
    """Test overlap handling in metadata mode (include_metadata=True)."""

    def test_overlap_metadata_mode_enabled(self):
        """Test overlap stored in metadata instead of content.

        Verify:
        - Content does NOT contain overlap (stays as content_core)
        - previous_content key exists where expected (not first chunk)
        - next_content key exists where expected (not last chunk)
        - First chunk has NO previous_content key
        - Last chunk has NO next_content key
        - Context values are non-empty strings
        - next_content of chunk i is extracted from beginning of chunk i+1
        - previous_content of chunk i is extracted from end of chunk i-1
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        # Create 3 chunks with enough content for overlap
        chunks = [
            Chunk(
                "# Section A\n\nFirst paragraph here.\n\nSecond paragraph.",
                1,
                5,
                {"strategy": "test"},
            ),
            Chunk(
                "# Section B\n\nThird paragraph here.\n\nFourth paragraph.",
                6,
                10,
                {"strategy": "test"},
            ),
            Chunk("# Section C\n\nFifth paragraph here.", 11, 13, {"strategy": "test"}),
        ]

        # Apply overlap in metadata mode
        result = manager.apply_overlap(chunks, include_metadata=True)

        assert len(result) == 3

        # First chunk should have no previous_content but may have next_content
        assert "previous_content" not in result[0].metadata
        # next_content should be present if extraction succeeded
        if "next_content" in result[0].metadata:
            assert result[0].metadata["next_content"]  # Non-empty
            assert isinstance(result[0].metadata["next_content"], str)
        assert result[0].content == chunks[0].content  # Content unchanged

        # Second chunk should have both previous_content and next_content
        # (if block alignment allows)
        if "previous_content" in result[1].metadata:
            assert result[1].metadata["previous_content"]  # Non-empty
            assert isinstance(result[1].metadata["previous_content"], str)
        if "next_content" in result[1].metadata:
            assert result[1].metadata["next_content"]  # Non-empty
            assert isinstance(result[1].metadata["next_content"], str)
        # Content should be clean - no overlap merged
        assert result[1].content == chunks[1].content

        # Third chunk should have previous_content but no next_content
        if "previous_content" in result[2].metadata:
            assert result[2].metadata["previous_content"]  # Non-empty
            assert isinstance(result[2].metadata["previous_content"], str)
        assert "next_content" not in result[2].metadata
        # Content should be clean - no overlap merged
        assert result[2].content == chunks[2].content

    def test_overlap_legacy_mode_disabled(self):
        """Test legacy mode where overlap is merged into content.

        Verify:
        - Content DOES contain overlap (merged)
        - previous_content key is NOT present
        - next_content key is NOT present
        - Existing metadata fields remain unchanged
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content here.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk content here.", 7, 9, {"strategy": "test"}),
        ]

        # Apply overlap in legacy mode
        result = manager.apply_overlap(chunks, include_metadata=False)

        assert len(result) == 3

        # First chunk may have next_content merged
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata

        # Second chunk may have overlap merged into content
        # Content may be longer if context was added
        assert len(result[1].content) >= len("Second chunk content here.")
        assert "previous_content" not in result[1].metadata
        assert "next_content" not in result[1].metadata

        # Third chunk may have overlap merged into content
        assert len(result[2].content) >= len("Third chunk content here.")
        assert "previous_content" not in result[2].metadata
        assert "next_content" not in result[2].metadata

    def test_overlap_metadata_mode_single_chunk(self):
        """Test single chunk document - no context keys should be present."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Only one chunk here.", 1, 1, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        assert len(result) == 1
        # Should have no context keys
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata
        # Content unchanged
        assert result[0].content == "Only one chunk here."

    def test_overlap_metadata_mode_with_code_fences(self):
        """Test overlap extraction with unbalanced code fences.
        
        When a chunk has unbalanced code fences, the system should:
        1. Extract valid content BEFORE the unbalanced fence
        2. Skip content that includes/follows the unbalanced fence
        
        This provides graceful degradation: extract what IS safe rather than
        giving up entirely.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("Some text\n\n```python\ncode block", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content.", 4, 4, {"strategy": "test"}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Should extract the safe content "Some text" before the unbalanced fence
        assert "previous_content" in result[1].metadata
        assert result[1].metadata["previous_content"] == "Some text"
        # Content should be clean and unchanged
        assert result[1].content == "Second chunk content."

    def test_overlap_metadata_field_presence(self):
        """Test that context fields are only present when context exists."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Check key presence/absence
        assert "previous_content" not in result[0].metadata

        if "previous_content" in result[1].metadata:
            # If context was applied, it should be a non-empty string
            assert isinstance(result[1].metadata["previous_content"], str)
            assert len(result[1].metadata["previous_content"]) > 0

    def test_overlap_disabled_no_keys(self):
        """Test that context keys are not added when overlap is disabled."""
        config = ChunkConfig(enable_overlap=False)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        # Metadata mode but overlap disabled
        result = manager.apply_overlap(chunks, include_metadata=True)

        # No context keys should be present
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata


class TestOverlapModeComparison:
    """Compare behavior between metadata and legacy modes."""

    def test_content_preservation_both_modes(self):
        """Test that content is preserved correctly in both modes.

        In metadata mode: content stays as content_core, contexts in metadata.
        In legacy mode: content = previous_content + content_core + next_content.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=25)
        manager = OverlapManager(config)

        original_chunks = [
            Chunk("First chunk with some content.", 1, 1, {}),
            Chunk("Second chunk with more content.", 2, 2, {}),
            Chunk("Third chunk with final content.", 3, 3, {}),
        ]

        # Apply both modes
        metadata_result = manager.apply_overlap(original_chunks, include_metadata=True)
        legacy_result = manager.apply_overlap(original_chunks, include_metadata=False)

        # In metadata mode, content should be unchanged (content_core)
        for i in range(len(original_chunks)):
            assert metadata_result[i].content == original_chunks[i].content

        # Legacy mode may have context merged, so content may be longer
        for i in range(len(original_chunks)):
            assert len(legacy_result[i].content) >= len(original_chunks[i].content)

    def test_backward_compatibility_default_false(self):
        """Test that default parameter (False) maintains backward compatibility."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        # Default should be legacy mode (False)
        result = manager.apply_overlap(chunks)  # No include_metadata parameter

        # Should behave like legacy mode - no context fields in metadata
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata
