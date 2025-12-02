"""
Property-based tests for the redesigned overlap model.

Uses Hypothesis for property-based testing to validate invariants
that should hold across all possible inputs.
"""

import pytest
from hypothesis import given, settings, strategies as st

from markdown_chunker.chunker.components import OverlapManager
from markdown_chunker.chunker.types import Chunk, ChunkConfig


# Strategy for generating valid chunks
@st.composite
def chunk_strategy(draw):
    """Generate a valid Chunk for testing."""
    content = draw(st.text(min_size=10, max_size=200))
    start_line = draw(st.integers(min_value=1, max_value=100))
    end_line = draw(st.integers(min_value=start_line, max_value=start_line + 20))
    metadata = {}
    return Chunk(content, start_line, end_line, metadata)


@st.composite
def chunk_list_strategy(draw, min_chunks=2, max_chunks=5):
    """Generate a list of valid chunks."""
    n = draw(st.integers(min_value=min_chunks, max_value=max_chunks))
    chunks = []
    current_line = 1
    for _ in range(n):
        content = draw(st.text(min_size=20, max_size=150))
        start_line = current_line
        end_line = current_line + draw(st.integers(min_value=1, max_value=10))
        chunks.append(Chunk(content, start_line, end_line, {}))
        current_line = end_line + 1
    return chunks


class TestOverlapPropertiesRedesign:
    """Property-based tests for overlap redesign."""

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_context_size_constraint(self, chunks):
        """
        Property: Context sizes respect effective_overlap limit.
        
        For all chunks where context fields are present:
        len(previous_content) <= effective_overlap
        len(next_content) <= effective_overlap
        """
        overlap_size = 40
        config = ChunkConfig(enable_overlap=True, overlap_size=overlap_size)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for chunk in result:
            if "previous_content" in chunk.metadata:
                assert len(chunk.metadata["previous_content"]) <= overlap_size
            
            if "next_content" in chunk.metadata:
                assert len(chunk.metadata["next_content"]) <= overlap_size

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_context_source_correctness_metadata(self, chunks):
        """
        Property: In metadata mode, contexts are substrings of neighbors.
        
        previous_content[i] is a suffix of chunks[i-1].content
        next_content[i] is a prefix of chunks[i+1].content
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for i in range(len(result)):
            chunk = result[i]
            
            # Check previous_content
            if "previous_content" in chunk.metadata and i > 0:
                prev_content = chunk.metadata["previous_content"]
                prev_chunk = chunks[i - 1]
                # Should be substring of previous chunk
                assert prev_content in prev_chunk.content
            
            # Check next_content
            if "next_content" in chunk.metadata and i < len(result) - 1:
                next_content = chunk.metadata["next_content"]
                next_chunk = chunks[i + 1]
                # Should be substring of next chunk
                assert next_content in next_chunk.content

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_context_source_independence(self, chunks):
        """
        Property: Contexts are independent extractions.
        
        No requirement that next_content[i] == previous_content[i+1]
        They are independently extracted and may differ.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # This property just documents that we don't enforce equality
        # We verify they CAN be different
        for i in range(len(result) - 1):
            # Both might exist
            if "next_content" in result[i].metadata and \
               "previous_content" in result[i + 1].metadata:
                # They may or may not be equal - both are valid
                # Just verify both are non-empty
                assert result[i].metadata["next_content"]
                assert result[i + 1].metadata["previous_content"]

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_mode_equivalence(self, chunks):
        """
        Property: Mode equivalence holds.
        
        For same input:
        chunk_no_meta[i].content == 
        chunk_meta[i].previous_content + chunk_meta[i].content + chunk_meta[i].next_content
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        meta_result = manager.apply_overlap(chunks, include_metadata=True)
        legacy_result = manager.apply_overlap(chunks, include_metadata=False)
        
        assert len(meta_result) == len(legacy_result)
        
        for i in range(len(meta_result)):
            meta = meta_result[i]
            legacy = legacy_result[i]
            
            # Compose from metadata mode
            prev = meta.metadata.get("previous_content", "")
            content = meta.content
            next_ctx = meta.metadata.get("next_content", "")
            
            parts = []
            if prev:
                parts.append(prev)
            parts.append(content)
            if next_ctx:
                parts.append(next_ctx)
            
            composed = "\n\n".join(parts)
            
            # Should match legacy
            assert composed == legacy.content

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_index_consistency(self, chunks):
        """
        Property: Chunk index references are consistent.
        
        When present, previous_chunk_index and next_chunk_index
        correctly reference neighbor indices.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for i in range(len(result)):
            chunk = result[i]
            
            # Check previous_chunk_index
            if "previous_chunk_index" in chunk.metadata:
                assert chunk.metadata["previous_chunk_index"] == i - 1
                # Must have previous_content too
                assert "previous_content" in chunk.metadata
            
            # Check next_chunk_index
            if "next_chunk_index" in chunk.metadata:
                assert chunk.metadata["next_chunk_index"] == i + 1
                # Must have next_content too
                assert "next_content" in chunk.metadata

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_overlap_disabled_behavior(self, chunks):
        """
        Property: When enable_overlap=false, no context fields added.
        """
        config = ChunkConfig(enable_overlap=False, overlap_size=50)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata
            assert "previous_chunk_index" not in chunk.metadata
            assert "next_chunk_index" not in chunk.metadata

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_no_legacy_fields(self, chunks):
        """
        Property: No legacy overlap fields in output.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        # Test both modes
        for include_metadata in [True, False]:
            result = manager.apply_overlap(chunks, include_metadata=include_metadata)
            
            for chunk in result:
                assert "overlap_prefix" not in chunk.metadata
                assert "overlap_suffix" not in chunk.metadata
                assert "has_overlap" not in chunk.metadata
                assert "overlap_type" not in chunk.metadata
                assert "overlap_size" not in chunk.metadata

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_boundary_chunks_no_context(self, chunks):
        """
        Property: First chunk has no previous_content, last has no next_content.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # First chunk
        assert "previous_content" not in result[0].metadata
        
        # Last chunk
        assert "next_content" not in result[-1].metadata

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_content_unchanged_in_metadata_mode(self, chunks):
        """
        Property: In metadata mode, chunk content is unchanged.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        # Content should match original
        for i in range(len(result)):
            assert result[i].content == chunks[i].content

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_offsets_unchanged(self, chunks):
        """
        Property: Offsets remain unchanged by overlap processing.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for i in range(len(result)):
            # Line numbers should be unchanged
            assert result[i].start_line == chunks[i].start_line
            assert result[i].end_line == chunks[i].end_line

    @given(st.integers(min_value=0, max_value=100))
    @settings(max_examples=30, deadline=None)
    def test_property_effective_overlap_zero(self, overlap_size):
        """
        Property: When effective_overlap=0, no context fields added.
        """
        # Force effective overlap to 0
        config = ChunkConfig(
            enable_overlap=True if overlap_size > 0 else False,
            overlap_size=0,
            overlap_percentage=0
        )
        manager = OverlapManager(config)
        
        chunks = [
            Chunk("First chunk.", 1, 1, {}),
            Chunk("Second chunk.", 2, 2, {}),
        ]
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    @given(chunks=chunk_list_strategy(min_chunks=1, max_chunks=1))
    @settings(max_examples=30, deadline=None)
    def test_property_single_chunk_no_context(self, chunks):
        """
        Property: Single chunk has no context fields.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=50)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        assert len(result) == 1
        assert "previous_content" not in result[0].metadata
        assert "next_content" not in result[0].metadata

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_context_non_empty_when_present(self, chunks):
        """
        Property: When context fields are present, they are non-empty.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=True)
        
        for chunk in result:
            if "previous_content" in chunk.metadata:
                assert chunk.metadata["previous_content"] != ""
                assert len(chunk.metadata["previous_content"]) > 0
            
            if "next_content" in chunk.metadata:
                assert chunk.metadata["next_content"] != ""
                assert len(chunk.metadata["next_content"]) > 0

    @given(chunks=chunk_list_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_metadata_mode_no_context_in_legacy(self, chunks):
        """
        Property: Legacy mode has no context fields in metadata.
        """
        config = ChunkConfig(enable_overlap=True, overlap_size=30)
        manager = OverlapManager(config)
        
        result = manager.apply_overlap(chunks, include_metadata=False)
        
        for chunk in result:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata
            assert "previous_chunk_index" not in chunk.metadata
            assert "next_chunk_index" not in chunk.metadata
