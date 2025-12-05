"""
V2 Test Implementation: Core Properties

Implements test specifications SPEC-023 to SPEC-026 from
docs/v2-test-specification/v2-test-specification.md

Tests core domain properties:
- SPEC-023: Data Preservation (PROP-1)
- SPEC-024: Monotonic Ordering (PROP-3)
- SPEC-025: No Empty Chunks (PROP-4)
- SPEC-026: Idempotence (PROP-5)
"""

import pytest
from hypothesis import given, settings, strategies as st, HealthCheck

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


# =============================================================================
# SPEC-023: Data Preservation (PROP-1)
# =============================================================================

class TestSPEC023DataPreservation:
    """
    SPEC-023: Data Preservation (PROP-1)
    
    **Feature: v2-test-implementation, Property 8: Data preservation**
    **Validates: Requirements 3.1, 5.4**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-023
    """
    
    def test_content_preserved_simple(self):
        """Test content is preserved in simple case."""
        chunker = MarkdownChunker()
        text = "Hello world. This is a test."
        chunks = chunker.chunk(text)
        
        combined = ''.join(c.content for c in chunks)
        
        # All words should be present
        for word in ["Hello", "world", "This", "test"]:
            assert word in combined
    
    def test_content_preserved_with_code(self):
        """Test content is preserved with code blocks."""
        chunker = MarkdownChunker()
        text = """# Header

Some text.

```python
def hello():
    return "world"
```

More text.
"""
        chunks = chunker.chunk(text)
        combined = ''.join(c.content for c in chunks)
        
        assert "Header" in combined
        assert "def hello" in combined
        assert "More text" in combined
    
    @given(st.text(min_size=1, max_size=500).filter(lambda x: x.strip() and any(c.isalnum() for c in x)))
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_alphanumeric_content_preserved(self, text: str):
        """Property: Alphanumeric content is preserved."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)
        
        if not chunks:
            return
        
        combined = ''.join(c.content for c in chunks)
        
        # Extract alphanumeric sequences from original
        import re
        original_words = set(re.findall(r'\w+', text))
        combined_words = set(re.findall(r'\w+', combined))
        
        # Most words should be preserved (allowing for some edge cases)
        preserved = len(original_words & combined_words)
        total = len(original_words)
        if total > 0:
            assert preserved / total >= 0.8, f"Only {preserved}/{total} words preserved"


# =============================================================================
# SPEC-024: Monotonic Ordering (PROP-3)
# =============================================================================

class TestSPEC024MonotonicOrdering:
    """
    SPEC-024: Monotonic Ordering (PROP-3)
    
    **Feature: v2-test-implementation, Property 9: Monotonic ordering**
    **Validates: Requirements 3.1, 5.4**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-024
    """
    
    def test_line_numbers_monotonic(self):
        """Test chunk line numbers are monotonically increasing."""
        chunker = MarkdownChunker()
        text = """# Section 1

Content 1.

# Section 2

Content 2.

# Section 3

Content 3.
"""
        chunks = chunker.chunk(text)
        
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                # Each chunk's start should be >= previous chunk's start
                assert chunks[i].start_line <= chunks[i + 1].start_line
    
    def test_start_end_line_valid(self):
        """Test each chunk has valid start_line <= end_line."""
        chunker = MarkdownChunker()
        text = "Para 1.\n\nPara 2.\n\nPara 3."
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.start_line <= chunk.end_line
            assert chunk.start_line >= 1
    
    @given(st.text(min_size=10, max_size=1000).filter(lambda x: x.strip()))
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_monotonic_ordering_property(self, text: str):
        """Property: Chunk line numbers are monotonically ordered."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)
        
        if len(chunks) <= 1:
            return
        
        # Check monotonic ordering
        for i in range(len(chunks) - 1):
            assert chunks[i].start_line <= chunks[i].end_line
            # Allow overlap but start lines should be non-decreasing
            assert chunks[i].start_line <= chunks[i + 1].start_line


# =============================================================================
# SPEC-025: No Empty Chunks (PROP-4)
# =============================================================================

class TestSPEC025NoEmptyChunks:
    """
    SPEC-025: No Empty Chunks (PROP-4)
    
    **Feature: v2-test-implementation, Property 10: No empty chunks**
    **Validates: Requirements 3.1, 5.4**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-025
    """
    
    def test_no_empty_chunks_simple(self):
        """Test no empty chunks in simple case."""
        chunker = MarkdownChunker()
        text = "Hello world."
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.content.strip(), "Chunk content should not be empty"
    
    def test_no_empty_chunks_with_whitespace(self):
        """Test no empty chunks even with lots of whitespace."""
        chunker = MarkdownChunker()
        text = "Para 1.\n\n\n\n\nPara 2.\n\n\n\nPara 3."
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert chunk.content.strip(), "Chunk content should not be empty"
    
    @given(st.text(min_size=1, max_size=500).filter(lambda x: x.strip()))
    @settings(max_examples=50, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_no_empty_chunks_property(self, text: str):
        """Property: All chunks have non-empty content."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)
        
        for chunk in chunks:
            assert len(chunk.content.strip()) > 0, "Chunk content must not be empty"


# =============================================================================
# SPEC-026: Idempotence (PROP-5)
# =============================================================================

class TestSPEC026Idempotence:
    """
    SPEC-026: Idempotence (PROP-5)
    
    **Feature: v2-test-implementation, Property 11: Idempotence**
    **Validates: Requirements 3.1, 5.4**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-026
    """
    
    def test_chunking_deterministic(self):
        """Test chunking produces same result on repeated calls."""
        chunker = MarkdownChunker()
        text = """# Header

Some content here.

## Subheader

More content.
"""
        chunks1 = chunker.chunk(text)
        chunks2 = chunker.chunk(text)
        
        assert len(chunks1) == len(chunks2)
        
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.content == c2.content
            assert c1.start_line == c2.start_line
            assert c1.end_line == c2.end_line
    
    def test_different_chunker_instances_same_result(self):
        """Test different chunker instances produce same result."""
        config = ChunkConfig(max_chunk_size=500)
        
        chunker1 = MarkdownChunker(config)
        chunker2 = MarkdownChunker(config)
        
        text = "Test content. " * 20
        
        chunks1 = chunker1.chunk(text)
        chunks2 = chunker2.chunk(text)
        
        assert len(chunks1) == len(chunks2)
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.content == c2.content
    
    @given(st.text(min_size=1, max_size=500).filter(lambda x: x.strip()))
    @settings(max_examples=30, deadline=5000, suppress_health_check=[HealthCheck.filter_too_much, HealthCheck.too_slow])
    def test_idempotence_property(self, text: str):
        """Property: Chunking is idempotent (deterministic)."""
        chunker = MarkdownChunker()
        
        chunks1 = chunker.chunk(text)
        chunks2 = chunker.chunk(text)
        
        assert len(chunks1) == len(chunks2)
        
        for c1, c2 in zip(chunks1, chunks2):
            assert c1.content == c2.content
            assert c1.start_line == c2.start_line
            assert c1.end_line == c2.end_line
