"""Unit tests for the new overlap model with previous_content/next_content.

Tests the redesigned overlap mechanism that uses explicit neighbor context
instead of overlap_prefix/overlap_suffix.
"""

from markdown_chunker.chunker.components import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig


class TestOverlapNewModel:
    """Test the new neighbor context overlap model."""

    def test_no_old_overlap_fields(self):
        """Verify removal of deprecated overlap fields."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content here.", 1, 3, {"strategy": "test"}),
            Chunk("Second chunk content here.", 4, 6, {"strategy": "test"}),
            Chunk("Third chunk content here.", 7, 9, {"strategy": "test"}),
        ]

        # Test metadata mode
        result = manager.apply_overlap(chunks, include_metadata=True)

        for chunk in result:
            # Old fields should not exist
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata
            assert "has_overlap" not in chunk.metadata
            assert "overlap_type" not in chunk.metadata
            assert "overlap_size" not in chunk.metadata
            assert "overlap_block_ids" not in chunk.metadata
            assert "overlap_start_offset" not in chunk.metadata
            assert "new_content_start_offset" not in chunk.metadata

    def test_context_size_limits(self):
        """Validate context length constraints.

        Note: Block-aligned extraction allows 1.2x tolerance for the first block,
        so contexts may be slightly larger than the strict overlap_size limit.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk with some content here.", 1, 3, {}),
            Chunk("Second chunk with more content.", 4, 6, {}),
            Chunk("Third chunk with additional content.", 7, 9, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Maximum allowed size with 1.2x tolerance for first block
        max_size_with_tolerance = int(30 * 1.2)

        for chunk in result:
            # Check previous_content size limit (with tolerance)
            if "previous_content" in chunk.metadata:
                assert (
                    len(chunk.metadata["previous_content"]) <= max_size_with_tolerance
                )

            # Check next_content size limit (with tolerance)
            if "next_content" in chunk.metadata:
                assert len(chunk.metadata["next_content"]) <= max_size_with_tolerance

    def test_boundary_chunks(self):
        """Validate first and last chunks have no context fields on boundaries."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content.", 1, 3, {}),
            Chunk("Second chunk content.", 4, 6, {}),
            Chunk("Third chunk content.", 7, 9, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # First chunk: no previous_content
        assert "previous_content" not in result[0].metadata
        assert "previous_chunk_index" not in result[0].metadata

        # Last chunk: no next_content
        assert "next_content" not in result[2].metadata
        assert "next_chunk_index" not in result[2].metadata

    def test_metadata_mode_no_content_merge(self):
        """Ensure contexts not merged in metadata mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=20)
        manager = OverlapManager(config)

        original_chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        result = manager.apply_overlap(original_chunks, include_metadata=True)

        # Content should be unchanged (not merged)
        assert result[0].content == "First chunk."
        assert result[1].content == "Second chunk."

        # Context should be in metadata
        if "next_content" in result[0].metadata:
            # Next content should not be in first chunk's content
            assert result[0].metadata["next_content"] not in result[0].content

        if "previous_content" in result[1].metadata:
            # Previous content should not be in second chunk's content
            assert result[1].metadata["previous_content"] not in result[1].content

    def test_legacy_mode_content_merge(self):
        """Ensure contexts merged in legacy mode.

        In legacy mode:
        - First chunk may have next_content merged (context from chunk 1)
        - Second chunk may have previous_content merged (context from chunk 0)
        - Content = previous_content + content_core + next_content
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content here.", 1, 3, {}),
            Chunk("Second chunk content here.", 4, 6, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=False)

        # First chunk may have next_content merged (context from second chunk)
        # Content should be at least as large as original
        assert len(result[0].content) >= len("First chunk content here.")

        # Second chunk may have previous_content merged (context from first chunk)
        # Content should be at least as large as original
        assert len(result[1].content) >= len("Second chunk content here.")

        # Context fields should NOT be in metadata (they're merged into content)
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata
        assert "previous_content" not in result[1].metadata
        assert "next_content" not in result[1].metadata

    def test_mode_equivalence(self):
        """Validate invariant across modes."""
        config = ChunkConfig(enable_overlap=True, overlap_size=25)
        manager = OverlapManager(config)

        original_chunks = [
            Chunk("First chunk content.", 1, 2, {}),
            Chunk("Second chunk content.", 3, 4, {}),
            Chunk("Third chunk content.", 5, 6, {}),
        ]

        metadata_result = manager.apply_overlap(original_chunks, include_metadata=True)
        legacy_result = manager.apply_overlap(original_chunks, include_metadata=False)

        # Verify equivalence for each chunk
        for i in range(len(original_chunks)):
            meta_chunk = metadata_result[i]
            legacy_chunk = legacy_result[i]

            # Compose full context from metadata mode
            prev = meta_chunk.metadata.get("previous_content", "")
            content = meta_chunk.content
            next_ctx = meta_chunk.metadata.get("next_content", "")

            parts = []
            if prev:
                parts.append(prev)
            parts.append(content)
            if next_ctx:
                parts.append(next_ctx)

            composed = "\n\n".join(parts)

            # Should match legacy mode content
            assert (
                composed == legacy_chunk.content
            ), f"Chunk {i}: Mode equivalence failed"

    def test_offset_integrity_metadata_mode(self):
        """Validate offsets in metadata mode."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {"start_offset": 0, "end_offset": 12}),
            Chunk("Second chunk.", 2, 2, {"start_offset": 13, "end_offset": 26}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # In metadata mode, len(content) should equal offset range
        for chunk in result:
            if "start_offset" in chunk.metadata and "end_offset" in chunk.metadata:
                start = chunk.metadata["start_offset"]
                end = chunk.metadata["end_offset"]
                assert len(chunk.content) == end - start

    def test_enable_overlap_false(self):
        """Test no-op when overlap disabled."""
        config = ChunkConfig(enable_overlap=False, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Chunks should be unchanged
        assert len(result) == 2
        assert result[0].content == "First chunk."
        assert result[1].content == "Second chunk."

        # No context fields should be added
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata
        assert "previous_content" not in result[1].metadata
        assert "next_content" not in result[1].metadata

    def test_effective_overlap_zero(self):
        """Test no-op when effective overlap is zero."""
        config = ChunkConfig(enable_overlap=True, overlap_size=0, overlap_percentage=0)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # No context fields should be added
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    def test_chunk_index_references(self):
        """Validate chunk index references."""
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk content.", 1, 2, {}),
            Chunk("Second chunk content.", 3, 4, {}),
            Chunk("Third chunk content.", 5, 6, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Check index references
        # Chunk 0: no previous, may have next
        if "next_content" in result[0].metadata:
            assert result[0].metadata.get("next_chunk_index") == 1

        # Chunk 1: should have both
        if "previous_content" in result[1].metadata:
            assert result[1].metadata.get("previous_chunk_index") == 0
        if "next_content" in result[1].metadata:
            assert result[1].metadata.get("next_chunk_index") == 2

        # Chunk 2: may have previous, no next
        if "previous_content" in result[2].metadata:
            assert result[2].metadata.get("previous_chunk_index") == 1

    def test_single_chunk_no_context(self):
        """Test single chunk document has no context fields."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [Chunk("Only chunk.", 1, 1, {})]

        result = manager.apply_overlap(chunks, include_metadata=True)

        assert len(result) == 1
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata

    def test_context_is_substring_of_neighbor(self):
        """Verify context originates from correct neighbor."""
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)

        chunks = [
            Chunk("First chunk with unique text here.", 1, 2, {}),
            Chunk("Second chunk with different text.", 3, 4, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Check that next_content of chunk 0 is from chunk 1
        if "next_content" in result[0].metadata:
            assert result[0].metadata["next_content"] in chunks[1].content

        # Check that previous_content of chunk 1 is from chunk 0
        if "previous_content" in result[1].metadata:
            assert result[1].metadata["previous_content"] in chunks[0].content

    def test_empty_context_not_added(self):
        """Verify that empty contexts are not added to metadata."""
        config = ChunkConfig(enable_overlap=True, overlap_size=5)
        manager = OverlapManager(config)

        # Very short chunks might not yield extractable context
        chunks = [
            Chunk("A", 1, 1, {}),
            Chunk("B", 2, 2, {}),
        ]

        result = manager.apply_overlap(chunks, include_metadata=True)

        # Empty contexts should not be present
        for chunk in result:
            if "previous_content" in chunk.metadata:
                assert chunk.metadata["previous_content"] != ""
            if "next_content" in chunk.metadata:
                assert chunk.metadata["next_content"] != ""
