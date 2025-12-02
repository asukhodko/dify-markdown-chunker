"""
Unit tests for overlap metadata mode implementation.

Tests the new metadata-aware overlap handling where overlap is stored
in metadata fields (overlap_prefix/overlap_suffix) instead of being merged
into chunk content.
"""

import pytest

from markdown_chunker.chunker.components import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig


class TestOverlapMetadataMode:
    """Test overlap handling in metadata mode (include_metadata=True)."""

    def test_overlap_metadata_mode_enabled(self):
        """Test overlap stored in metadata instead of content.
        
        Verify:
        - Content does NOT contain overlap
        - overlap_prefix key exists where expected (not first chunk)
        - overlap_suffix key exists where expected (not last chunk)
        - First chunk has NO overlap_prefix key
        - Last chunk has NO overlap_suffix key
        - Overlap values are non-empty strings
        - overlap_suffix matches next chunk's overlap_prefix
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)
        
        # Create 3 chunks with enough content for overlap
        chunks = [
            Chunk("# Section A\n\nFirst paragraph here.\n\nSecond paragraph.", 1, 5, {"strategy": "test"}),
            Chunk("# Section B\n\nThird paragraph here.\n\nFourth paragraph.", 6, 10, {"strategy": "test"}),
            Chunk("# Section C\n\nFifth paragraph here.", 11, 13, {"strategy": "test"}),
        ]
        
        # Apply overlap in metadata mode
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        assert len(result) == 3
        
        # First chunk should have no overlap_prefix key but should have overlap_suffix
        assert "overlap_prefix" not in result[0].metadata
        assert "overlap_suffix" in result[0].metadata
        assert result[0].metadata["overlap_suffix"]  # Non-empty
        assert isinstance(result[0].metadata["overlap_suffix"], str)
        assert result[0].content == chunks[0].content  # Content unchanged
        
        # Second chunk should have both overlap_prefix and overlap_suffix
        assert "overlap_prefix" in result[1].metadata
        assert result[1].metadata["overlap_prefix"]  # Non-empty
        assert isinstance(result[1].metadata["overlap_prefix"], str)
        assert "overlap_suffix" in result[1].metadata
        assert result[1].metadata["overlap_suffix"]  # Non-empty
        assert isinstance(result[1].metadata["overlap_suffix"], str)
        # Content should be clean - no overlap merged
        assert result[1].content == chunks[1].content
        
        # Third chunk should have overlap_prefix but no overlap_suffix
        assert "overlap_prefix" in result[2].metadata
        assert result[2].metadata["overlap_prefix"]  # Non-empty
        assert isinstance(result[2].metadata["overlap_prefix"], str)
        assert "overlap_suffix" not in result[2].metadata
        # Content should be clean - no overlap merged
        assert result[2].content == chunks[2].content
        
        # Verify overlap consistency: suffix of chunk i == prefix of chunk i+1
        assert result[0].metadata["overlap_suffix"] == result[1].metadata["overlap_prefix"]
        assert result[1].metadata["overlap_suffix"] == result[2].metadata["overlap_prefix"]

    def test_overlap_legacy_mode_disabled(self):
        """Test legacy mode where overlap is merged into content.
        
        Verify:
        - Content DOES contain overlap (current behavior)
        - overlap_prefix key is NOT present
        - overlap_suffix key is NOT present
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
        
        # First chunk unchanged
        assert result[0].content == "First chunk content here."
        assert "overlap_prefix" not in result[0].metadata
        
        # Second chunk should have overlap merged into content
        assert len(result[1].content) > len("Second chunk content here.")
        assert "overlap_prefix" not in result[1].metadata
        assert "overlap_suffix" not in result[1].metadata
        # Should have legacy metadata
        assert result[1].get_metadata("has_overlap", False) is True
        assert "overlap_size" in result[1].metadata
        
        # Third chunk should have overlap merged into content
        assert len(result[2].content) > len("Third chunk content here.")
        assert "overlap_prefix" not in result[2].metadata
        assert "overlap_suffix" not in result[2].metadata

    def test_overlap_metadata_mode_single_chunk(self):
        """Test single chunk document - no overlap keys should be present."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        chunks = [
            Chunk("Only one chunk here.", 1, 1, {"strategy": "test"}),
        ]
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        assert len(result) == 1
        # Should have no overlap keys
        assert "overlap_prefix" not in result[0].metadata
        assert "overlap_suffix" not in result[0].metadata
        # Content unchanged
        assert result[0].content == "Only one chunk here."

    def test_overlap_metadata_mode_with_code_fences(self):
        """Test that unbalanced code fences prevent overlap."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)
        
        chunks = [
            Chunk("Some text\n\n```python\ncode block", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content.", 4, 4, {"strategy": "test"}),
        ]
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # Overlap should be skipped due to unbalanced fences
        assert "overlap_prefix" not in result[1].metadata
        # Content should be clean and unchanged
        assert result[1].content == "Second chunk content."

    def test_overlap_metadata_field_presence(self):
        """Test that overlap fields are only present when overlap exists."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)
        
        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # Check key presence/absence
        assert "overlap_prefix" not in result[0].metadata
        
        if "overlap_prefix" in result[1].metadata:
            # If overlap was applied, it should be a non-empty string
            assert isinstance(result[1].metadata["overlap_prefix"], str)
            assert len(result[1].metadata["overlap_prefix"]) > 0

    def test_overlap_disabled_no_keys(self):
        """Test that overlap keys are not added when overlap is disabled."""
        config = ChunkConfig(enable_overlap=False)
        manager = OverlapManager(config)
        
        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]
        
        # Metadata mode but overlap disabled
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # No overlap keys should be present
        for chunk in result:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata


class TestOverlapModeComparison:
    """Compare behavior between metadata and legacy modes."""

    def test_content_preservation_both_modes(self):
        """Test that content is preserved correctly in both modes."""
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
        
        # In metadata mode, concatenating content should give original text
        metadata_content = "\n\n".join(c.content for c in metadata_result)
        original_content = "\n\n".join(c.content for c in original_chunks)
        assert metadata_content == original_content
        
        # Legacy mode has overlap merged, so content will be longer
        legacy_content = "\n\n".join(c.content for c in legacy_result)
        # First chunk same, others longer
        assert legacy_result[0].content == original_chunks[0].content
        if legacy_result[1].get_metadata("has_overlap"):
            assert len(legacy_result[1].content) > len(original_chunks[1].content)

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
        
        # Should behave like legacy mode
        if result[1].get_metadata("has_overlap"):
            assert len(result[1].content) > len("Second chunk.")
            assert "overlap_prefix" not in result[1].metadata
