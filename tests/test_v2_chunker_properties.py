"""
V2 Test Implementation: Chunker Properties

Implements test specifications SPEC-008 to SPEC-015 from
docs/v2-test-specification/v2-test-specification.md

Tests markdown_chunker_v2.MarkdownChunker including:
- Basic chunking behavior
- Size constraints (max/min)
- Overlap handling
- Atomic block preservation
- Metadata generation
- Strategy selection
"""

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.types import Chunk

# =============================================================================
# SPEC-008: Basic Chunking Produces Valid Chunks
# =============================================================================


class TestSPEC008BasicChunking:
    """
    SPEC-008: Basic Chunking Produces Valid Chunks

    **Feature: v2-test-implementation, Property 4: Basic chunking validity**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-008
    """

    def test_simple_text_chunking(self):
        """Test simple text produces valid chunks."""
        chunker = MarkdownChunker()
        text = "This is a simple paragraph of text."
        chunks = chunker.chunk(text)

        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.content.strip() for c in chunks)

    def test_structured_markdown_chunking(self):
        """Test structured markdown produces valid chunks."""
        chunker = MarkdownChunker()
        text = """# Header 1

Some content here.

## Header 2

More content.

```python
def hello():
    pass
```
"""
        chunks = chunker.chunk(text)

        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line >= chunk.start_line
            assert chunk.content.strip()

    @given(st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()))
    @settings(
        max_examples=50,
        deadline=5000,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
    )
    def test_non_empty_text_produces_chunks(self, text: str):
        """Property: Non-empty text produces non-empty chunks."""
        chunker = MarkdownChunker()
        chunks = chunker.chunk(text)

        # Non-empty text should produce at least one chunk
        if text.strip():
            assert len(chunks) >= 1
            # All chunks should have non-empty content
            for chunk in chunks:
                assert chunk.content.strip()

    def test_empty_text_returns_empty_list(self):
        """Empty text should return empty list."""
        chunker = MarkdownChunker()

        assert chunker.chunk("") == []
        assert chunker.chunk("   ") == []
        assert chunker.chunk("\n\n") == []


# =============================================================================
# SPEC-009: Max Chunk Size Enforcement
# =============================================================================


class TestSPEC009MaxChunkSize:
    """
    SPEC-009: Max Chunk Size Enforcement

    **Feature: v2-test-implementation, Property 5: Max chunk size enforcement**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-009
    """

    def test_chunks_respect_max_size(self):
        """Test chunks respect max_chunk_size."""
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=50)
        chunker = MarkdownChunker(config)

        # Create text larger than max_chunk_size
        text = "Word " * 200  # ~1000 chars
        chunks = chunker.chunk(text)

        for chunk in chunks:
            # Either within limit or marked as oversize
            assert chunk.size <= 500 or chunk.is_oversize

    def test_oversize_chunks_marked_correctly(self):
        """Test oversize chunks have correct metadata."""
        config = ChunkConfig(max_chunk_size=100, min_chunk_size=10, overlap_size=20)
        chunker = MarkdownChunker(config)

        # Large code block that can't be split
        text = "```python\n" + "x = 1\n" * 50 + "```"
        chunks = chunker.chunk(text)

        for chunk in chunks:
            if chunk.size > 100:
                assert chunk.is_oversize
                assert chunk.metadata.get("allow_oversize") is True

    @given(st.integers(min_value=512, max_value=8192))
    @settings(max_examples=20, deadline=5000)
    def test_various_max_sizes(self, max_size: int):
        """Property: Various max_chunk_size values are respected."""
        config = ChunkConfig(max_chunk_size=max_size, min_chunk_size=max_size // 4)
        chunker = MarkdownChunker(config)

        text = "Paragraph. " * 100
        chunks = chunker.chunk(text)

        for chunk in chunks:
            assert chunk.size <= max_size or chunk.is_oversize


# =============================================================================
# SPEC-010: Min Chunk Size Handling
# =============================================================================


class TestSPEC010MinChunkSize:
    """
    SPEC-010: Min Chunk Size Handling

    **Feature: v2-test-implementation, Property: Min chunk size handling**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-010
    """

    def test_small_chunks_may_exist(self):
        """Small chunks may exist at document boundaries."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)

        text = "Short."
        chunks = chunker.chunk(text)

        # Small content should still produce a chunk
        assert len(chunks) >= 1

    def test_chunk_merging_attempted(self):
        """Chunker attempts to merge small chunks."""
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)
        chunker = MarkdownChunker(config)

        # Multiple small sections
        text = """# A

Small.

# B

Also small.

# C

Tiny.
"""
        chunks = chunker.chunk(text)

        # Should produce chunks (merging may or may not happen)
        assert len(chunks) >= 1


# =============================================================================
# SPEC-011: Overlap Metadata Correctness
# =============================================================================


class TestSPEC011OverlapMetadata:
    """
    SPEC-011: Overlap Metadata Correctness

    **Feature: v2-test-implementation, Property 15: Overlap metadata correctness**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-011
    """

    def test_overlap_metadata_present(self):
        """Test overlap metadata is present when enabled."""
        config = ChunkConfig(max_chunk_size=200, min_chunk_size=50, overlap_size=50)
        chunker = MarkdownChunker(config)

        # Text that will produce multiple chunks
        text = "Paragraph one. " * 20 + "\n\n" + "Paragraph two. " * 20
        chunks = chunker.chunk(text)

        if len(chunks) > 1:
            # First chunk should have next_content
            if "next_content" in chunks[0].metadata:
                assert len(chunks[0].metadata["next_content"]) > 0

            # Last chunk should have previous_content
            if "previous_content" in chunks[-1].metadata:
                assert len(chunks[-1].metadata["previous_content"]) > 0

    def test_no_overlap_when_disabled(self):
        """Test no overlap metadata when overlap_size=0."""
        config = ChunkConfig(max_chunk_size=200, min_chunk_size=50, overlap_size=0)
        chunker = MarkdownChunker(config)

        text = "Paragraph. " * 50
        chunks = chunker.chunk(text)

        for chunk in chunks:
            # Should not have overlap metadata
            assert (
                "previous_content" not in chunk.metadata
                or chunk.metadata.get("previous_content") is None
            )

    @given(st.integers(min_value=10, max_value=100))
    @settings(max_examples=20, deadline=5000)
    def test_overlap_size_respected(self, overlap_size: int):
        """Property: Overlap size is approximately respected."""
        config = ChunkConfig(
            max_chunk_size=500, min_chunk_size=50, overlap_size=overlap_size
        )
        chunker = MarkdownChunker(config)

        text = "Word " * 200
        chunks = chunker.chunk(text)

        for chunk in chunks:
            if "overlap_size" in chunk.metadata:
                # Overlap should be approximately the configured size
                assert chunk.metadata["overlap_size"] <= overlap_size + 50


# =============================================================================
# SPEC-012: Atomic Block Preservation
# =============================================================================


class TestSPEC012AtomicBlockPreservation:
    """
    SPEC-012: Atomic Block Preservation

    **Feature: v2-test-implementation, Property 6: Atomic block preservation**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-012
    """

    def test_code_block_not_split(self):
        """Test code blocks are not split across chunks."""
        config = ChunkConfig(max_chunk_size=100, min_chunk_size=10, overlap_size=20)
        chunker = MarkdownChunker(config)

        text = """Before

```python
def function():
    x = 1
    y = 2
    return x + y
```

After
"""
        chunks = chunker.chunk(text)

        # Find chunk containing code block
        code_chunks = [c for c in chunks if "```" in c.content]

        for chunk in code_chunks:
            # Code block should be complete (even number of ```)
            fence_count = chunk.content.count("```")
            assert fence_count % 2 == 0, "Code block should not be split"

    def test_table_not_split(self):
        """Test tables are not split across chunks."""
        config = ChunkConfig(max_chunk_size=100, min_chunk_size=10, overlap_size=20)
        chunker = MarkdownChunker(config)

        text = """Before

| Col1 | Col2 | Col3 |
|------|------|------|
| A    | B    | C    |
| D    | E    | F    |

After
"""
        chunks = chunker.chunk(text)

        # Find table chunks
        for chunk in chunks:
            lines = [line for line in chunk.content.split("\n") if "|" in line]
            if len(lines) > 1:
                # Table format check
                assert any("---" in line for line in lines)


# =============================================================================
# SPEC-013: Chunk Metadata Completeness
# =============================================================================


class TestSPEC013ChunkMetadata:
    """
    SPEC-013: Chunk Metadata Completeness

    **Feature: v2-test-implementation, Property: Chunk metadata completeness**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-013
    """

    def test_required_metadata_present(self):
        """Test required metadata fields are present."""
        chunker = MarkdownChunker()
        text = "# Header\n\nSome content here."
        chunks = chunker.chunk(text)

        for chunk in chunks:
            assert "strategy" in chunk.metadata
            assert "chunk_index" in chunk.metadata

    def test_chunk_index_sequential(self):
        """Test chunk_index is sequential."""
        chunker = MarkdownChunker()
        text = "Para 1.\n\n" * 10
        chunks = chunker.chunk(text)

        indices = [c.metadata["chunk_index"] for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_content_type_detected(self):
        """Test content_type is detected correctly."""
        chunker = MarkdownChunker()

        # Code content
        code_text = "```python\ncode\n```"
        code_chunks = chunker.chunk(code_text)
        if code_chunks:
            assert code_chunks[0].metadata.get("content_type") in ["code", "mixed"]

        # Text content
        text_chunks = chunker.chunk("Just plain text.")
        if text_chunks:
            assert text_chunks[0].metadata.get("content_type") == "text"


# =============================================================================
# SPEC-014: Strategy Selection Determinism
# =============================================================================


class TestSPEC014StrategySelection:
    """
    SPEC-014: Strategy Selection Determinism

    **Feature: v2-test-implementation, Property 12: Strategy selection determinism**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-014
    """

    def test_same_input_same_strategy(self):
        """Test same input always selects same strategy."""
        chunker = MarkdownChunker()
        text = "# Header\n\nContent with ```code```"

        chunks1 = chunker.chunk(text)
        chunks2 = chunker.chunk(text)

        if chunks1 and chunks2:
            assert chunks1[0].metadata["strategy"] == chunks2[0].metadata["strategy"]

    @given(st.text(min_size=10, max_size=500).filter(lambda x: x.strip()))
    @settings(
        max_examples=30,
        deadline=5000,
        suppress_health_check=[HealthCheck.filter_too_much],
    )
    def test_strategy_selection_deterministic(self, text: str):
        """Property: Strategy selection is deterministic."""
        chunker = MarkdownChunker()

        chunks1 = chunker.chunk(text)
        chunks2 = chunker.chunk(text)

        if chunks1 and chunks2:
            strategies1 = [c.metadata.get("strategy") for c in chunks1]
            strategies2 = [c.metadata.get("strategy") for c in chunks2]
            assert strategies1 == strategies2


# =============================================================================
# SPEC-015: Config Validation
# =============================================================================


class TestSPEC015ConfigValidation:
    """
    SPEC-015: Config Validation

    **Feature: v2-test-implementation, Unit: Config validation**
    **Validates: Requirements 3.1, 5.1**
    **Reference**: docs/v2-test-specification/v2-test-specification.md#SPEC-015
    """

    def test_valid_config_accepted(self):
        """Valid configurations should be accepted."""
        config = ChunkConfig(max_chunk_size=1024, min_chunk_size=100, overlap_size=50)
        assert config.max_chunk_size == 1024
        assert config.min_chunk_size == 100
        assert config.overlap_size == 50

    def test_invalid_max_chunk_size_zero(self):
        """max_chunk_size=0 should raise ValueError."""
        with pytest.raises(ValueError, match="max_chunk_size must be positive"):
            ChunkConfig(max_chunk_size=0)

    def test_invalid_max_chunk_size_negative(self):
        """Negative max_chunk_size should raise ValueError."""
        with pytest.raises(ValueError, match="max_chunk_size must be positive"):
            ChunkConfig(max_chunk_size=-100)

    def test_invalid_min_chunk_size_zero(self):
        """min_chunk_size=0 should raise ValueError."""
        with pytest.raises(ValueError, match="min_chunk_size must be positive"):
            ChunkConfig(min_chunk_size=0)

    def test_min_greater_than_max_auto_adjusted(self):
        """min_chunk_size > max_chunk_size is auto-adjusted."""
        # According to config.py, this is auto-adjusted, not an error
        config = ChunkConfig(max_chunk_size=500, min_chunk_size=600, overlap_size=50)
        assert config.min_chunk_size <= config.max_chunk_size

    def test_invalid_overlap_size_negative(self):
        """Negative overlap_size should raise ValueError."""
        with pytest.raises(ValueError, match="overlap_size must be non-negative"):
            ChunkConfig(overlap_size=-10)

    def test_invalid_overlap_size_too_large(self):
        """overlap_size >= max_chunk_size should raise ValueError."""
        with pytest.raises(
            ValueError, match="overlap_size.*must be less than max_chunk_size"
        ):
            ChunkConfig(max_chunk_size=100, overlap_size=100)

    def test_invalid_code_threshold(self):
        """code_threshold outside [0,1] should raise ValueError."""
        with pytest.raises(ValueError, match="code_threshold must be between 0 and 1"):
            ChunkConfig(code_threshold=1.5)

        with pytest.raises(ValueError, match="code_threshold must be between 0 and 1"):
            ChunkConfig(code_threshold=-0.1)

    def test_invalid_structure_threshold(self):
        """structure_threshold < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="structure_threshold must be >= 1"):
            ChunkConfig(structure_threshold=0)

    def test_invalid_strategy_override(self):
        """Invalid strategy_override should raise ValueError."""
        with pytest.raises(ValueError, match="strategy_override must be one of"):
            ChunkConfig(strategy_override="invalid_strategy")

    def test_valid_strategy_overrides(self):
        """Valid strategy_override values should be accepted."""
        for strategy in ["code_aware", "structural", "fallback"]:
            config = ChunkConfig(strategy_override=strategy)
            assert config.strategy_override == strategy
