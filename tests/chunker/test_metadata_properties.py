"""
Property-based tests for MetadataEnricher behavior.

Tests verify that metadata is complete and correct:
- All documented metadata fields are present
- Metadata values are correct
- Metadata is consistent across chunks

**Feature: markdown-chunker-quality-audit, Property 4: Metadata Completeness**
**Validates: Requirements 3.5, 10.4**
"""

import pytest
from hypothesis import given, strategies as st, settings

from markdown_chunker.chunker.components.metadata_enricher import MetadataEnricher
from markdown_chunker.chunker.types import Chunk, ChunkConfig


# Test data generators
@st.composite
def chunk_with_strategy(draw, strategy="structural"):
    """Generate a chunk with specific strategy."""
    content = draw(st.text(min_size=10, max_size=200))
    
    start_line = draw(st.integers(min_value=1, max_value=100))
    line_count = draw(st.integers(min_value=1, max_value=50))
    end_line = start_line + line_count
    
    chunk = Chunk(
        content=content,
        start_line=start_line,
        end_line=end_line,
        metadata={"strategy": strategy, "content_type": "text"}
    )
    return chunk


# Property Tests

@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_property_metadata_has_required_fields(chunks):
    """
    Property: All chunks have required metadata fields.
    
    **Feature: markdown-chunker-quality-audit, Property 4a: Required Fields**
    **Validates: Requirements 3.5, 10.4**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    required_fields = ["chunk_index", "total_chunks", "is_first_chunk", "is_last_chunk"]
    
    for chunk in enriched:
        for field in required_fields:
            assert field in chunk.metadata, f"Missing required field: {field}"


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=2, max_size=5),
)
@settings(max_examples=30)
def test_property_chunk_indices_correct(chunks):
    """
    Property: Chunk indices are correct and sequential.
    
    **Feature: markdown-chunker-quality-audit, Property 4b: Index Correctness**
    **Validates: Requirements 3.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    for i, chunk in enumerate(enriched):
        assert chunk.metadata["chunk_index"] == i, \
            f"Incorrect chunk_index: expected {i}, got {chunk.metadata['chunk_index']}"


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_property_total_chunks_consistent(chunks):
    """
    Property: total_chunks is consistent across all chunks.
    
    **Feature: markdown-chunker-quality-audit, Property 4c: Total Chunks Consistency**
    **Validates: Requirements 3.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    expected_total = len(enriched)
    
    for chunk in enriched:
        assert chunk.metadata["total_chunks"] == expected_total, \
            f"Inconsistent total_chunks: expected {expected_total}, got {chunk.metadata['total_chunks']}"


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_property_first_last_flags_correct(chunks):
    """
    Property: is_first_chunk and is_last_chunk flags are correct.
    
    **Feature: markdown-chunker-quality-audit, Property 4d: First/Last Flags**
    **Validates: Requirements 3.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    if len(enriched) > 0:
        # First chunk
        assert enriched[0].metadata["is_first_chunk"] is True
        assert enriched[0].metadata["is_last_chunk"] == (len(enriched) == 1)
        
        # Last chunk
        assert enriched[-1].metadata["is_last_chunk"] is True
        assert enriched[-1].metadata["is_first_chunk"] == (len(enriched) == 1)
        
        # Middle chunks
        for chunk in enriched[1:-1]:
            assert chunk.metadata["is_first_chunk"] is False
            assert chunk.metadata["is_last_chunk"] is False


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_property_content_statistics_present(chunks):
    """
    Property: Content statistics are present and valid.
    
    **Feature: markdown-chunker-quality-audit, Property 4e: Statistics Present**
    **Validates: Requirements 3.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    stat_fields = ["line_count", "word_count", "char_count"]
    
    for chunk in enriched:
        for field in stat_fields:
            assert field in chunk.metadata, f"Missing statistic: {field}"
            assert chunk.metadata[field] >= 0, f"{field} should be non-negative"


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
    document_id=st.text(min_size=1, max_size=20),
)
@settings(max_examples=30)
def test_property_document_id_propagated(chunks, document_id):
    """
    Property: Document ID is propagated to all chunks.
    
    **Feature: markdown-chunker-quality-audit, Property 4f: Document ID**
    **Validates: Requirements 3.5**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks, document_id=document_id)
    
    for chunk in enriched:
        assert "document_id" in chunk.metadata
        assert chunk.metadata["document_id"] == document_id


@given(
    chunks=st.lists(chunk_with_strategy(), min_size=1, max_size=5),
)
@settings(max_examples=30)
def test_property_validation_passes(chunks):
    """
    Property: Enriched chunks pass validation.
    
    **Feature: markdown-chunker-quality-audit, Property 4g: Validation**
    **Validates: Requirements 3.5, 10.4**
    """
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    enriched = enricher.enrich_chunks(chunks)
    
    validation = enricher.validate_metadata(enriched)
    
    assert validation["valid"] is True, \
        f"Validation failed: {validation.get('issues', [])}"


# Unit tests for specific enrichment

def test_code_metadata_enrichment():
    """Test code-specific metadata enrichment."""
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    chunk = Chunk(
        content="```python\nimport os\n# Comment\n```",
        start_line=1,
        end_line=4,
        metadata={"strategy": "code", "content_type": "code"}
    )
    
    enriched = enricher.enrich_chunks([chunk])
    
    assert enriched[0].metadata["code_block_count"] == 1
    assert enriched[0].metadata["has_imports"] is True
    assert enriched[0].metadata["has_comments"] is True


def test_list_metadata_enrichment():
    """Test list-specific metadata enrichment."""
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    chunk = Chunk(
        content="1. First\n2. Second\n- Bullet\n  - Nested",
        start_line=1,
        end_line=4,
        metadata={"strategy": "list", "content_type": "list"}
    )
    
    enriched = enricher.enrich_chunks([chunk])
    
    assert enriched[0].metadata["ordered_item_count"] == 2
    assert enriched[0].metadata["unordered_item_count"] == 2
    assert enriched[0].metadata["has_nested_lists"] is True


def test_table_metadata_enrichment():
    """Test table-specific metadata enrichment."""
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    chunk = Chunk(
        content="| A | B |\n|---|---|\n| 1 | 2 |",
        start_line=1,
        end_line=3,
        metadata={"strategy": "table", "content_type": "table"}
    )
    
    enriched = enricher.enrich_chunks([chunk])
    
    assert enriched[0].metadata["table_row_count"] == 3
    assert enriched[0].metadata["table_count"] == 1


def test_searchability_metadata():
    """Test searchability metadata."""
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    chunk = Chunk(
        content="Visit https://example.com or email test@example.com\n**Bold** and *italic*",
        start_line=1,
        end_line=2,
        metadata={"strategy": "structural", "content_type": "text"}
    )
    
    enriched = enricher.enrich_chunks([chunk])
    
    assert enriched[0].metadata["has_urls"] is True
    assert enriched[0].metadata["has_emails"] is True
    assert enriched[0].metadata["has_bold"] is True
    assert enriched[0].metadata["has_italic"] is True
    assert "preview" in enriched[0].metadata


def test_metadata_summary():
    """Test metadata summary generation."""
    config = ChunkConfig(max_chunk_size=2000)
    enricher = MetadataEnricher(config)
    
    chunks = [
        Chunk(content="Test 1", start_line=1, end_line=2, 
              metadata={"strategy": "structural", "content_type": "text"}),
        Chunk(content="Test 2", start_line=2, end_line=3, 
              metadata={"strategy": "code", "content_type": "code"}),
    ]
    
    enriched = enricher.enrich_chunks(chunks)
    summary = enricher.get_metadata_summary(enriched)
    
    assert summary["total_chunks"] == 2
    assert "strategies" in summary
    assert "content_types" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
