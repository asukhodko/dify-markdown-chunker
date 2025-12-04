"""
Property-based tests for markdown_chunker_v2.

Tests for correctness properties defined in design.md.

**Feature: architecture-redesign**
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.parser import Parser


# =============================================================================
# Generators
# =============================================================================

@st.composite
def markdown_with_mixed_line_endings(draw):
    """Generate markdown with mixed line endings (\\n, \\r\\n, \\r)."""
    # Generate base content
    lines = draw(st.lists(
        st.text(min_size=1, max_size=100, alphabet=st.characters(
            blacklist_categories=('Cs',),
            blacklist_characters='\r\n'
        )),
        min_size=1,
        max_size=20
    ))
    
    # Mix line endings
    endings = ['\n', '\r\n', '\r']
    result = []
    for i, line in enumerate(lines):
        result.append(line)
        if i < len(lines) - 1:
            ending = draw(st.sampled_from(endings))
            result.append(ending)
    
    return ''.join(result)


@st.composite
def valid_markdown_document(draw):
    """Generate valid markdown documents."""
    parts = []
    
    # Optional header
    if draw(st.booleans()):
        level = draw(st.integers(min_value=1, max_value=6))
        header_text = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'Z'),
            blacklist_characters='\r\n#'
        )))
        if header_text.strip():
            parts.append('#' * level + ' ' + header_text.strip())
            parts.append('')
    
    # Some paragraphs
    num_paragraphs = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_paragraphs):
        para = draw(st.text(min_size=10, max_size=200, alphabet=st.characters(
            whitelist_categories=('L', 'N', 'P', 'Z'),
            blacklist_characters='\r\n`'
        )))
        if para.strip():
            parts.append(para.strip())
            parts.append('')
    
    result = '\n'.join(parts)
    assume(result.strip())
    return result


# =============================================================================
# Property 11: Line Ending Normalization
# =============================================================================

class TestProp11LineEndingNormalization:
    """
    Property 11: Line Ending Normalization
    
    For any markdown text with mixed line endings, the parser should
    normalize all line endings to Unix-style (\\n) before processing.
    
    **Validates: Requirements 3.1**
    """
    
    @given(md_text=markdown_with_mixed_line_endings())
    @settings(max_examples=100, deadline=None)
    def test_line_endings_normalized(self, md_text: str):
        """
        **Feature: architecture-redesign, Property 11: Line Ending Normalization**
        **Validates: Requirements 3.1**
        """
        parser = Parser()
        
        # Normalize using parser's method
        normalized = parser._normalize_line_endings(md_text)
        
        # Should not contain CR or CRLF
        assert '\r\n' not in normalized, "CRLF should be normalized to LF"
        assert '\r' not in normalized, "CR should be normalized to LF"
        
        # Content should be preserved (just line endings changed)
        original_content = md_text.replace('\r\n', '\n').replace('\r', '\n')
        assert normalized == original_content
    
    @given(md_text=markdown_with_mixed_line_endings())
    @settings(max_examples=50, deadline=None)
    def test_chunking_consistent_regardless_of_line_endings(self, md_text: str):
        """
        Chunking should produce same results regardless of line ending style.
        
        **Feature: architecture-redesign, Property 11: Line Ending Normalization**
        **Validates: Requirements 3.1**
        """
        assume(md_text.strip())
        
        chunker = MarkdownChunker()
        
        # Chunk with original (mixed) line endings
        try:
            chunks_original = chunker.chunk(md_text)
        except ValueError:
            # Empty content after normalization is OK
            return
        
        # Chunk with Unix line endings
        unix_text = md_text.replace('\r\n', '\n').replace('\r', '\n')
        try:
            chunks_unix = chunker.chunk(unix_text)
        except ValueError:
            return
        
        # Should produce same number of chunks
        assert len(chunks_original) == len(chunks_unix), \
            f"Different chunk counts: {len(chunks_original)} vs {len(chunks_unix)}"
        
        # Content should match
        for i, (c1, c2) in enumerate(zip(chunks_original, chunks_unix)):
            assert c1.content == c2.content, f"Chunk {i} content differs"


# =============================================================================
# Property 9: Fence Balance
# =============================================================================

class TestProp9FenceBalance:
    """
    Property 9: Fence Balance
    
    For any chunk, the number of code fence markers (```) should be even,
    or the chunk should be marked with fence_balance_error.
    
    **Validates: Requirements 4.5**
    """
    
    @given(md_text=valid_markdown_document())
    @settings(max_examples=100, deadline=None)
    def test_fence_balance(self, md_text: str):
        """
        **Feature: architecture-redesign, Property 9: Fence Balance**
        **Validates: Requirements 4.5**
        """
        chunker = MarkdownChunker()
        
        try:
            chunks = chunker.chunk(md_text)
        except ValueError:
            return  # Empty content is OK
        
        for i, chunk in enumerate(chunks):
            fence_count = chunk.content.count('```')
            
            # Either balanced or marked with error
            if fence_count % 2 != 0:
                assert chunk.metadata.get('fence_balance_error', False), \
                    f"Chunk {i} has unbalanced fences ({fence_count}) but no error flag"


# =============================================================================
# Property 10: Oversize Metadata Correctness
# =============================================================================

class TestProp10OversizeMetadata:
    """
    Property 10: Oversize Metadata Correctness
    
    For any chunk exceeding max_chunk_size, it must have allow_oversize=True
    and a valid oversize_reason.
    
    **Validates: Requirements 4.4**
    """
    
    def test_oversize_chunks_have_metadata(self):
        """
        **Feature: architecture-redesign, Property 10: Oversize Metadata Correctness**
        **Validates: Requirements 4.4**
        """
        # Create document with large code block
        large_code = "x = 1\n" * 500  # ~3000 chars
        md_text = f"""# Test

```python
{large_code}
```

Some text after.
"""
        
        config = ChunkConfig(max_chunk_size=1000)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)
        
        for chunk in chunks:
            if chunk.size > config.max_chunk_size:
                assert chunk.metadata.get('allow_oversize', False), \
                    f"Oversize chunk missing allow_oversize flag"
                
                reason = chunk.metadata.get('oversize_reason')
                valid_reasons = {'code_block_integrity', 'table_integrity', 'section_integrity'}
                assert reason in valid_reasons, \
                    f"Invalid oversize_reason: {reason}"


# =============================================================================
# Property 12: Strategy Selection Consistency
# =============================================================================

class TestProp12StrategySelection:
    """
    Property 12: Strategy Selection Consistency
    
    For any document, the same strategy should be selected on repeated calls.
    
    **Validates: Requirements 5.2**
    """
    
    @given(md_text=valid_markdown_document())
    @settings(max_examples=50, deadline=None)
    def test_strategy_selection_consistent(self, md_text: str):
        """
        **Feature: architecture-redesign, Property 12: Strategy Selection Consistency**
        **Validates: Requirements 5.2**
        """
        chunker = MarkdownChunker()
        
        try:
            _, strategy1, _ = chunker.chunk_with_analysis(md_text)
            _, strategy2, _ = chunker.chunk_with_analysis(md_text)
        except ValueError:
            return  # Empty content is OK
        
        assert strategy1 == strategy2, \
            f"Strategy changed between calls: {strategy1} vs {strategy2}"


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
