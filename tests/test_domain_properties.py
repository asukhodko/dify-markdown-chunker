"""
Property-based tests for domain properties PROP-1 through PROP-9.

These tests validate the core correctness properties that must be preserved
during the markdown_chunker redesign.

**Feature: architecture-redesign**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List

from markdown_chunker_v2 import MarkdownChunker, ChunkConfig


# =============================================================================
# Generators
# =============================================================================

@st.composite
def markdown_text(draw, min_size: int = 1, max_size: int = 5000):
    """Generate arbitrary markdown text."""
    text = draw(st.text(
        alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'Z'),
            blacklist_characters='\x00\r'
        ),
        min_size=min_size,
        max_size=max_size
    ))
    assume(text.strip())
    return text


@st.composite
def markdown_with_headers(draw):
    """Generate markdown with headers."""
    sections = []
    num_sections = draw(st.integers(min_value=2, max_value=5))
    
    for i in range(num_sections):
        level = draw(st.integers(min_value=1, max_value=3))
        header = "#" * level + f" Section {i+1}"
        content = draw(st.text(
            alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')),
            min_size=20,
            max_size=200
        ).filter(lambda x: x.strip() and '#' not in x))
        sections.append(f"{header}\n\n{content}")
    
    return "\n\n".join(sections)


@st.composite
def markdown_with_code(draw):
    """Generate markdown with code blocks."""
    parts = []
    num_blocks = draw(st.integers(min_value=1, max_value=3))
    
    for i in range(num_blocks):
        text = draw(st.text(min_size=10, max_size=100).filter(lambda x: '```' not in x and x.strip()))
        parts.append(text)
        
        lang = draw(st.sampled_from(['python', 'javascript', 'bash', '']))
        code = draw(st.text(min_size=5, max_size=150).filter(lambda x: '```' not in x))
        parts.append(f"```{lang}\n{code}\n```")
    
    final = draw(st.text(min_size=10, max_size=100).filter(lambda x: '```' not in x and x.strip()))
    parts.append(final)
    
    return "\n\n".join(parts)


@st.composite
def markdown_with_tables(draw):
    """Generate markdown with tables."""
    header = "# Document with Table\n\n"
    
    # Generate table
    cols = draw(st.integers(min_value=2, max_value=4))
    rows = draw(st.integers(min_value=2, max_value=5))
    
    header_row = "| " + " | ".join([f"Col{i}" for i in range(cols)]) + " |"
    sep_row = "| " + " | ".join(["---"] * cols) + " |"
    
    data_rows = []
    for r in range(rows):
        cells = [draw(st.text(min_size=1, max_size=10, alphabet='abcdefghijklmnop')) for _ in range(cols)]
        data_rows.append("| " + " | ".join(cells) + " |")
    
    table = "\n".join([header_row, sep_row] + data_rows)
    
    after = "\n\nText after table."
    
    return header + table + after


# =============================================================================
# PROP-1: No Content Loss
# =============================================================================

class TestProp1NoContentLoss:
    """
    PROP-1: No Content Loss
    
    For any markdown document, the total content in all chunks should
    preserve all non-whitespace content from the original.
    
    **Validates: Requirements 6.1**
    """
    
    @given(doc=markdown_text(min_size=50, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_content_preserved(self, doc: str):
        """
        **Feature: architecture-redesign, Property 1: No Content Loss**
        **Validates: Requirements 6.1**
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        # Reconstruct content
        reconstructed = "".join(c.content for c in chunks)
        
        # All non-whitespace chars should be present
        original_chars = set(c for c in doc if not c.isspace())
        reconstructed_chars = set(c for c in reconstructed if not c.isspace())
        
        missing = original_chars - reconstructed_chars
        assert not missing, f"Characters lost: {missing}"


# =============================================================================
# PROP-2: Size Bounds
# =============================================================================

class TestProp2SizeBounds:
    """
    PROP-2: Size Bounds
    
    For any chunk, its size should not exceed max_chunk_size unless
    allow_oversize metadata is True.
    
    **Validates: Requirements 6.2**
    """
    
    @given(doc=markdown_text(min_size=100, max_size=3000))
    @settings(max_examples=100, deadline=None)
    def test_size_bounds_respected(self, doc: str):
        """
        **Feature: architecture-redesign, Property 2: Size Bounds**
        **Validates: Requirements 6.2**
        """
        config = ChunkConfig(max_chunk_size=500)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        
        for i, chunk in enumerate(chunks):
            if len(chunk.content) > config.max_chunk_size:
                assert chunk.metadata.get("allow_oversize", False), (
                    f"Chunk {i} exceeds max_chunk_size ({len(chunk.content)}) "
                    f"without allow_oversize flag"
                )


# =============================================================================
# PROP-3: Monotonic Ordering
# =============================================================================

class TestProp3MonotonicOrdering:
    """
    PROP-3: Monotonic Ordering
    
    For any document, chunk start_lines should be monotonically non-decreasing.
    
    **Validates: Requirements 6.3**
    """
    
    @given(doc=markdown_text(min_size=100, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_monotonic_ordering(self, doc: str):
        """
        **Feature: architecture-redesign, Property 3: Monotonic Ordering**
        **Validates: Requirements 6.3**
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        for i in range(len(chunks) - 1):
            assert chunks[i].start_line <= chunks[i + 1].start_line, (
                f"Chunks out of order: chunk {i} starts at line {chunks[i].start_line}, "
                f"chunk {i+1} starts at line {chunks[i+1].start_line}"
            )


# =============================================================================
# PROP-4: No Empty Chunks
# =============================================================================

class TestProp4NoEmptyChunks:
    """
    PROP-4: No Empty Chunks
    
    For any document, no chunk should have empty or whitespace-only content.
    
    **Validates: Requirements 6.4**
    """
    
    @given(doc=markdown_text(min_size=50, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_no_empty_chunks(self, doc: str):
        """
        **Feature: architecture-redesign, Property 4: No Empty Chunks**
        **Validates: Requirements 6.4**
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), f"Chunk {i} is empty or whitespace-only"


# =============================================================================
# PROP-5: Valid Line Numbers
# =============================================================================

class TestProp5ValidLineNumbers:
    """
    PROP-5: Valid Line Numbers
    
    For any chunk, start_line >= 1 and end_line >= start_line.
    
    **Validates: Requirements 6.5**
    """
    
    @given(doc=markdown_text(min_size=50, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_valid_line_numbers(self, doc: str):
        """
        **Feature: architecture-redesign, Property 5: Valid Line Numbers**
        **Validates: Requirements 6.5**
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        total_lines = doc.count('\n') + 1
        
        for i, chunk in enumerate(chunks):
            assert chunk.start_line >= 1, (
                f"Chunk {i} has invalid start_line: {chunk.start_line}"
            )
            assert chunk.end_line >= chunk.start_line, (
                f"Chunk {i} has end_line ({chunk.end_line}) < start_line ({chunk.start_line})"
            )


# =============================================================================
# PROP-6: Code Block Integrity
# =============================================================================

class TestProp6CodeBlockIntegrity:
    """
    PROP-6: Code Block Integrity
    
    For any document with code blocks, each code block should be
    contained within exactly one chunk.
    
    **Validates: Requirements 6.6**
    """
    
    @given(doc=markdown_with_code())
    @settings(max_examples=100, deadline=None)
    def test_code_blocks_not_split(self, doc: str):
        """
        **Feature: architecture-redesign, Property 6: Code Block Integrity**
        **Validates: Requirements 6.6**
        """
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=2000))
        chunks = chunker.chunk(doc)
        
        for i, chunk in enumerate(chunks):
            fence_count = chunk.content.count('```')
            has_error = chunk.metadata.get("fence_balance_error", False)
            
            # Either balanced fences or error flag
            assert fence_count % 2 == 0 or has_error, (
                f"Chunk {i} has unbalanced fences ({fence_count}) without error flag"
            )


# =============================================================================
# PROP-7: Table Integrity
# =============================================================================

class TestProp7TableIntegrity:
    """
    PROP-7: Table Integrity
    
    For any document with tables, each table should be contained
    within exactly one chunk.
    
    **Validates: Requirements 6.7**
    """
    
    @given(doc=markdown_with_tables())
    @settings(max_examples=50, deadline=None)
    def test_tables_not_split(self, doc: str):
        """
        **Feature: architecture-redesign, Property 7: Table Integrity**
        **Validates: Requirements 6.7**
        """
        chunker = MarkdownChunker(ChunkConfig(max_chunk_size=2000))
        chunks = chunker.chunk(doc)
        
        # Find table header in chunks
        table_header = "| Col0 |"
        containing = [i for i, c in enumerate(chunks) if table_header in c.content]
        
        # Table should be in at most one chunk
        assert len(containing) <= 1, (
            f"Table found in multiple chunks: {containing}"
        )


# =============================================================================
# PROP-9: Idempotence
# =============================================================================

class TestProp9Idempotence:
    """
    PROP-9: Idempotence
    
    For any document, chunking it multiple times should produce
    identical results.
    
    **Validates: Requirements 6.8**
    """
    
    @given(doc=markdown_text(min_size=50, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_idempotence(self, doc: str):
        """
        **Feature: architecture-redesign, Property 8: Idempotence**
        **Validates: Requirements 6.8**
        """
        chunker = MarkdownChunker()
        
        chunks1 = chunker.chunk(doc)
        chunks2 = chunker.chunk(doc)
        
        assert len(chunks1) == len(chunks2), (
            f"Different chunk counts: {len(chunks1)} vs {len(chunks2)}"
        )
        
        for i, (c1, c2) in enumerate(zip(chunks1, chunks2)):
            assert c1.content == c2.content, f"Chunk {i} content differs"
            assert c1.start_line == c2.start_line, f"Chunk {i} start_line differs"
            assert c1.end_line == c2.end_line, f"Chunk {i} end_line differs"


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
