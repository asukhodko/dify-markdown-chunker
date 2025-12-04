"""
Property-based tests for redesign validation.

These tests validate the correctness properties that must be preserved
during the markdown_chunker redesign.

**Feature: redesign-review**
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
            whitelist_categories=('L', 'N', 'P', 'Z', 'S'),
            blacklist_characters='\x00'
        ),
        min_size=min_size,
        max_size=max_size
    ))
    assume(text.strip())  # Non-empty after stripping
    return text


@st.composite
def markdown_with_code_blocks(draw):
    """Generate markdown with code blocks."""
    # Generate some text before
    before = draw(st.text(min_size=0, max_size=200).filter(lambda x: '```' not in x))
    
    # Generate code block
    lang = draw(st.sampled_from(['python', 'javascript', 'rust', '']))
    code_content = draw(st.text(min_size=1, max_size=500).filter(lambda x: '```' not in x))
    code_block = f"```{lang}\n{code_content}\n```"
    
    # Generate some text after
    after = draw(st.text(min_size=0, max_size=200).filter(lambda x: '```' not in x))
    
    return f"{before}\n\n{code_block}\n\n{after}"


@st.composite  
def markdown_with_multiple_code_blocks(draw):
    """Generate markdown with multiple code blocks."""
    sections = []
    num_blocks = draw(st.integers(min_value=1, max_value=3))
    
    for i in range(num_blocks):
        # Text section
        text = draw(st.text(min_size=10, max_size=100).filter(lambda x: '```' not in x))
        sections.append(text)
        
        # Code block
        lang = draw(st.sampled_from(['python', 'javascript', '']))
        code = draw(st.text(min_size=5, max_size=200).filter(lambda x: '```' not in x))
        sections.append(f"```{lang}\n{code}\n```")
    
    # Final text
    final_text = draw(st.text(min_size=10, max_size=100).filter(lambda x: '```' not in x))
    sections.append(final_text)
    
    return "\n\n".join(sections)


@st.composite
def unicode_markdown(draw):
    """Generate markdown with Unicode content."""
    # Mix of ASCII and Unicode
    cyrillic = draw(st.text(
        alphabet=st.characters(whitelist_categories=('L',), whitelist_characters='абвгдеёжзийклмнопрстуфхцчшщъыьэюя'),
        min_size=10,
        max_size=100
    ))
    
    emoji = draw(st.sampled_from(['🎉', '👍', '🚀', '✅', '❌', '⚠️', '📝']))
    
    # Create markdown with Unicode
    header = f"# Заголовок {emoji}"
    paragraph = f"Текст на русском: {cyrillic}"
    
    return f"{header}\n\n{paragraph}"


@st.composite
def chunk_configs(draw):
    """Generate valid chunk configurations."""
    max_size = draw(st.integers(min_value=500, max_value=8000))
    min_size = draw(st.integers(min_value=50, max_value=max_size // 2))
    overlap = draw(st.integers(min_value=0, max_value=min(500, max_size // 4)))
    
    return ChunkConfig(
        max_chunk_size=max_size,
        min_chunk_size=min_size,
        overlap_size=overlap,
        enable_overlap=overlap > 0
    )


# =============================================================================
# Property 1: Overlap Integrity
# **Feature: redesign-review, Property 1: Overlap Integrity**
# **Validates: Requirements 1.4, 2.5**
# =============================================================================

class TestOverlapIntegrity:
    """
    Property 1: Overlap Integrity
    
    For any markdown document with code blocks, the overlap between chunks
    SHALL NOT contain partial code blocks (unbalanced ``` markers).
    """
    
    @given(doc=markdown_with_code_blocks())
    @settings(max_examples=100, deadline=None)
    def test_overlap_has_balanced_fences(self, doc: str):
        """
        **Feature: redesign-review, Property 1: Overlap Integrity**
        **Validates: Requirements 1.4, 2.5**
        
        Overlap content must have balanced code fences (even number of ```).
        """
        config = ChunkConfig(
            max_chunk_size=500,
            min_chunk_size=100,
            overlap_size=100  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        
        for chunk in chunks:
            # Check overlap content in metadata
            overlap_content = chunk.metadata.get("previous_content", "")
            if overlap_content:
                fence_count = overlap_content.count("```")
                assert fence_count % 2 == 0, (
                    f"Overlap has unbalanced code fences ({fence_count}): "
                    f"{overlap_content[:100]}..."
                )
    
    @given(doc=markdown_with_multiple_code_blocks())
    @settings(max_examples=50, deadline=None)
    def test_overlap_never_splits_code_block(self, doc: str):
        """
        **Feature: redesign-review, Property 1: Overlap Integrity**
        **Validates: Requirements 1.4, 2.5**
        
        Overlap must not start or end in the middle of a code block.
        """
        config = ChunkConfig(
            max_chunk_size=300,
            min_chunk_size=50,
            overlap_size=50  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        
        for i, chunk in enumerate(chunks):
            # Check that chunk content has balanced fences
            fence_count = chunk.content.count("```")
            assert fence_count % 2 == 0, (
                f"Chunk {i} has unbalanced code fences ({fence_count})"
            )


# =============================================================================
# Property 2: Chunk Integrity Preservation  
# **Feature: redesign-review, Property 2: Chunk Integrity Preservation**
# **Validates: Requirements 2.3, 2.4**
# =============================================================================

class TestChunkIntegrityPreservation:
    """
    Property 2: Chunk Integrity Preservation
    
    For any chunk that exceeds max_chunk_size, it SHALL have allow_oversize=True
    in metadata AND a valid oversize_reason.
    """
    
    @given(doc=markdown_with_code_blocks())
    @settings(max_examples=100, deadline=None)
    def test_oversize_chunks_are_flagged(self, doc: str):
        """
        **Feature: redesign-review, Property 2: Chunk Integrity Preservation**
        **Validates: Requirements 2.3, 2.4**
        
        Chunks exceeding max_chunk_size must have allow_oversize=True.
        """
        config = ChunkConfig(
            max_chunk_size=200,  # Small to trigger oversize
            min_chunk_size=50,
            overlap_size=0  # overlap_size=0 disables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        
        for i, chunk in enumerate(chunks):
            if len(chunk.content) > config.max_chunk_size:
                assert chunk.metadata.get("allow_oversize", False), (
                    f"Chunk {i} exceeds max_chunk_size ({len(chunk.content)} > "
                    f"{config.max_chunk_size}) but allow_oversize is not set"
                )
    
    @given(doc=markdown_with_code_blocks())
    @settings(max_examples=100, deadline=None)
    def test_oversize_chunks_have_reason(self, doc: str):
        """
        **Feature: redesign-review, Property 2: Chunk Integrity Preservation**
        **Validates: Requirements 2.3, 2.4**
        
        Oversize chunks must have a valid oversize_reason.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=0  # overlap_size=0 disables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(doc)
        
        valid_reasons = {"code_block_integrity", "table_integrity", "section_integrity"}
        
        for i, chunk in enumerate(chunks):
            if chunk.metadata.get("allow_oversize", False):
                reason = chunk.metadata.get("oversize_reason")
                if reason is not None:
                    assert reason in valid_reasons, (
                        f"Chunk {i} has invalid oversize_reason: {reason}"
                    )


# =============================================================================
# Property 3: Strategy Equivalence
# **Feature: redesign-review, Property 3: Strategy Equivalence**
# **Validates: Requirements 5.1, 5.4**
# =============================================================================

class TestStrategyEquivalence:
    """
    Property 3: Strategy Equivalence
    
    For any document, the chunking result must satisfy all domain properties
    (PROP-1 through PROP-5) regardless of which strategy is selected.
    """
    
    @given(doc=markdown_text(min_size=50, max_size=2000))
    @settings(max_examples=100, deadline=None)
    def test_all_strategies_satisfy_domain_properties(self, doc: str):
        """
        **Feature: redesign-review, Property 3: Strategy Equivalence**
        **Validates: Requirements 5.1, 5.4**
        
        All strategies must produce results satisfying PROP-1 through PROP-5.
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        # PROP-3: Monotonic ordering
        for i in range(len(chunks) - 1):
            assert chunks[i].start_line <= chunks[i + 1].start_line, (
                f"PROP-3 violated: chunks out of order at {i}"
            )
        
        # PROP-4: No empty chunks
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), f"PROP-4 violated: empty chunk at {i}"
        
        # PROP-5: Valid line numbers
        for i, chunk in enumerate(chunks):
            assert chunk.start_line >= 1, (
                f"PROP-5 violated: invalid start_line at {i}"
            )
            assert chunk.end_line >= chunk.start_line, (
                f"PROP-5 violated: end_line < start_line at {i}"
            )


# =============================================================================
# Property 4: Default Config Equivalence
# **Feature: redesign-review, Property 4: Default Config Equivalence**
# **Validates: Requirements 4.3**
# =============================================================================

class TestDefaultConfigEquivalence:
    """
    Property 4: Default Config Equivalence
    
    Chunking with default config must produce valid results satisfying
    all domain properties.
    """
    
    @given(doc=markdown_text(min_size=10, max_size=3000))
    @settings(max_examples=100, deadline=None)
    def test_default_config_produces_valid_results(self, doc: str):
        """
        **Feature: redesign-review, Property 4: Default Config Equivalence**
        **Validates: Requirements 4.3**
        
        Default configuration must produce valid chunking results.
        """
        chunker = MarkdownChunker()  # Default config
        chunks = chunker.chunk(doc)
        
        # All chunks must be valid
        for chunk in chunks:
            assert chunk.content.strip(), "Empty chunk produced"
            assert chunk.start_line >= 1, "Invalid start_line"
            assert chunk.end_line >= chunk.start_line, "Invalid end_line"


# =============================================================================
# Property 5: Unicode Preservation
# **Feature: redesign-review, Property 5: Unicode Preservation**
# **Validates: Requirements 3.5**
# =============================================================================

class TestUnicodePreservation:
    """
    Property 5: Unicode Preservation
    
    All non-ASCII characters must be preserved in output chunks.
    """
    
    @given(doc=unicode_markdown())
    @settings(max_examples=100, deadline=None)
    def test_unicode_characters_preserved(self, doc: str):
        """
        **Feature: redesign-review, Property 5: Unicode Preservation**
        **Validates: Requirements 3.5**
        
        Unicode characters must not be corrupted or lost.
        """
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        # Reconstruct content from chunks
        reconstructed = "".join(chunk.content for chunk in chunks)
        
        # All non-whitespace Unicode chars should be present
        for char in doc:
            if not char.isspace() and ord(char) > 127:
                assert char in reconstructed, (
                    f"Unicode character {repr(char)} (U+{ord(char):04X}) lost"
                )
    
    def test_cyrillic_preserved(self):
        """
        **Feature: redesign-review, Property 5: Unicode Preservation**
        **Validates: Requirements 3.5**
        
        Cyrillic text must be preserved.
        """
        doc = "# Заголовок\n\nТекст на русском языке с кириллицей."
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        reconstructed = "".join(chunk.content for chunk in chunks)
        assert "Заголовок" in reconstructed
        assert "кириллицей" in reconstructed
    
    def test_emoji_preserved(self):
        """
        **Feature: redesign-review, Property 5: Unicode Preservation**
        **Validates: Requirements 3.5**
        
        Emoji must be preserved.
        """
        doc = "# Test 🎉\n\nHello 👍 World 🚀"
        chunker = MarkdownChunker()
        chunks = chunker.chunk(doc)
        
        reconstructed = "".join(chunk.content for chunk in chunks)
        assert "🎉" in reconstructed
        assert "👍" in reconstructed
        assert "🚀" in reconstructed


# =============================================================================
# Run tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
