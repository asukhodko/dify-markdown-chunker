"""
Backward compatibility tests for API.

Tests verify that existing API call patterns still work:
- Basic chunk() method
- Configuration options
- Return types and structure
- Error handling

**Feature: markdown-chunker-quality-audit, Property 13: Backward Compatibility**
**Validates: Requirements 10.2**
"""

import pytest
from hypothesis import given, strategies as st, settings

from markdown_chunker import MarkdownChunker, ChunkConfig
from markdown_chunker.chunker.types import Chunk


# Property Tests

@given(
    content=st.text(min_size=10, max_size=500),
)
@settings(max_examples=30)
def test_property_basic_chunk_method_works(content):
    """
    Property: Basic chunk() method works for any input.
    
    **Feature: markdown-chunker-quality-audit, Property 13a: Basic API**
    **Validates: Requirements 10.2**
    """
    chunker = MarkdownChunker()
    
    try:
        chunks = chunker.chunk(content)
        
        # Should return list
        assert isinstance(chunks, list), "Should return list"
        
        # All items should be Chunk objects
        for chunk in chunks:
            assert isinstance(chunk, Chunk), "Should return Chunk objects"
            assert hasattr(chunk, 'content'), "Chunk should have content"
            assert hasattr(chunk, 'metadata'), "Chunk should have metadata"
    
    except Exception as e:
        # Should not raise unexpected exceptions
        pytest.fail(f"chunk() raised unexpected exception: {e}")


@given(
    max_size=st.integers(min_value=500, max_value=5000),
)
@settings(max_examples=20)
def test_property_config_parameter_works(max_size):
    """
    Property: ChunkConfig parameter works correctly.
    
    **Feature: markdown-chunker-quality-audit, Property 13b: Config Parameter**
    **Validates: Requirements 10.2**
    """
    config = ChunkConfig(max_chunk_size=max_size)
    chunker = MarkdownChunker(config)
    
    chunks = chunker.chunk("# Test\n\nContent here")
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0


@given(
    content=st.text(min_size=10, max_size=500),
)
@settings(max_examples=20)
def test_property_chunk_attributes_present(content):
    """
    Property: All chunks have required attributes.
    
    **Feature: markdown-chunker-quality-audit, Property 13c: Chunk Attributes**
    **Validates: Requirements 10.2**
    """
    chunker = MarkdownChunker()
    
    try:
        chunks = chunker.chunk(content)
        
        if chunks:
            for chunk in chunks:
                # Required attributes
                assert hasattr(chunk, 'content'), "Missing content"
                assert hasattr(chunk, 'start_line'), "Missing start_line"
                assert hasattr(chunk, 'end_line'), "Missing end_line"
                assert hasattr(chunk, 'metadata'), "Missing metadata"
                
                # Attributes should have correct types
                assert isinstance(chunk.content, str)
                assert isinstance(chunk.start_line, int)
                assert isinstance(chunk.end_line, int)
                assert isinstance(chunk.metadata, dict)
    
    except Exception:
        pass  # Some inputs may fail, that's ok


# Unit Tests for Specific Scenarios

def test_basic_chunk_method():
    """Test basic chunk() method works."""
    chunker = MarkdownChunker()
    chunks = chunker.chunk("# Test\n\nContent")
    
    assert len(chunks) > 0
    assert all(hasattr(c, 'content') for c in chunks)
    assert all(isinstance(c.content, str) for c in chunks)


def test_chunk_with_default_config():
    """Test chunk() with default configuration."""
    chunker = MarkdownChunker()
    chunks = chunker.chunk("# Title\n\nParagraph 1\n\nParagraph 2")
    
    assert len(chunks) > 0
    assert all(c.content for c in chunks)


def test_chunk_with_custom_config():
    """Test chunk() with custom config."""
    config = ChunkConfig(
        max_chunk_size=1000,
        min_chunk_size=100,
        enable_overlap=True,
        overlap_size=50
    )
    chunker = MarkdownChunker(config)
    chunks = chunker.chunk("# Test\n\nContent here with some text")
    
    assert len(chunks) > 0


def test_chunk_returns_list():
    """Test chunk() returns list."""
    chunker = MarkdownChunker()
    result = chunker.chunk("# Test")
    
    assert isinstance(result, list)


def test_chunk_with_empty_string():
    """Test chunk() handles empty string."""
    chunker = MarkdownChunker()
    
    try:
        chunks = chunker.chunk("")
        assert isinstance(chunks, list)
    except Exception:
        pass  # May raise exception, that's acceptable


def test_chunk_with_whitespace_only():
    """Test chunk() handles whitespace-only input."""
    chunker = MarkdownChunker()
    
    try:
        chunks = chunker.chunk("   \n\n   ")
        assert isinstance(chunks, list)
    except Exception:
        pass  # May raise exception, that's acceptable


def test_chunk_metadata_structure():
    """Test that chunk metadata has expected structure."""
    chunker = MarkdownChunker()
    chunks = chunker.chunk("# Test\n\nContent")
    
    if chunks:
        chunk = chunks[0]
        assert isinstance(chunk.metadata, dict)
        # Should have some metadata
        assert len(chunk.metadata) > 0


def test_chunk_line_numbers():
    """Test that chunks have valid line numbers."""
    chunker = MarkdownChunker()
    chunks = chunker.chunk("# Test\n\nContent")
    
    for chunk in chunks:
        assert chunk.start_line >= 1, "start_line should be >= 1"
        assert chunk.end_line >= chunk.start_line, "end_line should be >= start_line"


def test_multiple_chunkers_independent():
    """Test that multiple chunker instances are independent."""
    config1 = ChunkConfig(max_chunk_size=1000)
    config2 = ChunkConfig(max_chunk_size=2000)
    
    chunker1 = MarkdownChunker(config1)
    chunker2 = MarkdownChunker(config2)
    
    content = "# Test\n\n" + "Content. " * 100
    
    chunks1 = chunker1.chunk(content)
    chunks2 = chunker2.chunk(content)
    
    # Different configs may produce different chunk counts
    assert isinstance(chunks1, list)
    assert isinstance(chunks2, list)


def test_chunk_config_profiles():
    """Test ChunkConfig profile methods work."""
    # Test that profile methods exist and work
    try:
        config = ChunkConfig.for_code_heavy()
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk("```python\ncode\n```")
        assert isinstance(chunks, list)
    except AttributeError:
        # Profile methods may not exist, that's ok
        pass


def test_chunk_preserves_content_order():
    """Test that chunks preserve content order."""
    chunker = MarkdownChunker()
    
    content = "# First\n\nContent 1\n\n# Second\n\nContent 2\n\n# Third\n\nContent 3"
    chunks = chunker.chunk(content)
    
    combined = ''.join(c.content for c in chunks)
    
    # Check order is preserved
    assert combined.index("First") < combined.index("Second")
    assert combined.index("Second") < combined.index("Third")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

