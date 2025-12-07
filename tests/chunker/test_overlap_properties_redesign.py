"""Property-based tests for the v2 overlap implementation.

Uses Hypothesis for property-based testing to validate invariants
that should hold across all possible inputs.

Note: In v2, overlap logic is integrated into MarkdownChunker._apply_overlap()
rather than a separate OverlapManager class.
In v2, overlap is enabled when overlap_size > 0 (no enable_overlap parameter).
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


# Strategy for generating valid markdown text
@st.composite
def markdown_text_strategy(draw, min_size=50, max_size=500):
    """Generate valid markdown text for chunking."""
    # Generate multiple paragraphs
    num_paragraphs = draw(st.integers(min_value=2, max_value=5))
    paragraphs = []

    for _ in range(num_paragraphs):
        text = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
                min_size=20,
                max_size=150,
            ).filter(lambda x: x.strip())
        )
        paragraphs.append(text)

    return "\n\n".join(paragraphs)


@st.composite
def markdown_with_headers_strategy(draw):
    """Generate markdown with headers for structural chunking."""
    sections = []
    num_sections = draw(st.integers(min_value=2, max_value=4))

    for i in range(num_sections):
        level = draw(st.integers(min_value=1, max_value=3))
        header = "#" * level + f" Section {i+1}"
        content = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("L", "N", "P", "Z")),
                min_size=30,
                max_size=200,
            ).filter(lambda x: x.strip() and "#" not in x)
        )
        sections.append(f"{header}\n\n{content}")

    return "\n\n".join(sections)


class TestOverlapPropertiesV2:
    """Property-based tests for v2 overlap implementation."""

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_previous_content_is_suffix(self, md_text: str):
        """
        Property: previous_content is a suffix of the previous chunk's content.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=40,  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        if len(chunks) < 2:
            return  # Need at least 2 chunks to test overlap

        for i in range(1, len(chunks)):
            chunk = chunks[i]
            prev_chunk = chunks[i - 1]

            if "previous_content" in chunk.metadata:
                prev_content = chunk.metadata["previous_content"]
                # previous_content should be in the previous chunk
                assert (
                    prev_content in prev_chunk.content
                ), f"Chunk {i}: previous_content not found in chunk {i-1}"

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_first_chunk_no_previous(self, md_text: str):
        """
        Property: First chunk has no previous_content.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=40,  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        if chunks:
            assert (
                "previous_content" not in chunks[0].metadata
            ), "First chunk should not have previous_content"

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_overlap_size_constraint(self, md_text: str):
        """
        Property: Overlap size respects configuration with tolerance.
        """
        overlap_size = 40
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=overlap_size,  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        max_size_with_tolerance = int(overlap_size * 1.5)

        for i, chunk in enumerate(chunks):
            if "previous_content" in chunk.metadata:
                prev_len = len(chunk.metadata["previous_content"])
                assert (
                    prev_len <= max_size_with_tolerance
                ), f"Chunk {i}: previous_content too large: {prev_len} > {max_size_with_tolerance}"

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_overlap_disabled_no_metadata(self, md_text: str):
        """
        Property: When overlap_size=0, no overlap metadata is added.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=0,  # overlap_size=0 disables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_content_unchanged_with_overlap(self, md_text: str):
        """
        Property: Chunk content is unchanged by overlap processing.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=40,  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)

        # Chunk with overlap
        chunks_with_overlap = chunker.chunk(md_text)

        # Chunk without overlap
        config_no_overlap = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=0,  # overlap_size=0 disables overlap
        )
        chunker_no_overlap = MarkdownChunker(config_no_overlap)
        chunks_no_overlap = chunker_no_overlap.chunk(md_text)

        # Content should be the same
        assert len(chunks_with_overlap) == len(chunks_no_overlap)
        for i in range(len(chunks_with_overlap)):
            assert chunks_with_overlap[i].content == chunks_no_overlap[i].content

    @given(md_text=markdown_text_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_line_numbers_unchanged(self, md_text: str):
        """
        Property: Line numbers are unchanged by overlap processing.
        """
        config = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=40,  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)

        # Chunk with overlap
        chunks_with_overlap = chunker.chunk(md_text)

        # Chunk without overlap
        config_no_overlap = ChunkConfig(
            max_chunk_size=200,
            min_chunk_size=50,
            overlap_size=0,  # overlap_size=0 disables overlap
        )
        chunker_no_overlap = MarkdownChunker(config_no_overlap)
        chunks_no_overlap = chunker_no_overlap.chunk(md_text)

        # Line numbers should be the same
        assert len(chunks_with_overlap) == len(chunks_no_overlap)
        for i in range(len(chunks_with_overlap)):
            assert chunks_with_overlap[i].start_line == chunks_no_overlap[i].start_line
            assert chunks_with_overlap[i].end_line == chunks_no_overlap[i].end_line

    @given(md_text=markdown_with_headers_strategy())
    @settings(max_examples=50, deadline=None)
    def test_property_overlap_with_structural_chunks(self, md_text: str):
        """
        Property: Overlap works correctly with structural (header-based) chunks.
        """
        config = ChunkConfig(
            max_chunk_size=500,
            min_chunk_size=50,
            overlap_size=50,  # overlap_size > 0 enables overlap
            structure_threshold=2,
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        # All chunks except first should have previous_content if overlap enabled
        for i in range(1, len(chunks)):
            if len(chunks) > 1:
                # previous_content should exist for non-first chunks
                assert (
                    "previous_content" in chunks[i].metadata
                ), f"Chunk {i} missing previous_content"

    def test_single_chunk_no_overlap(self):
        """
        Property: Single chunk has no overlap metadata.
        """
        md_text = "Short text."
        config = ChunkConfig(
            max_chunk_size=1000, overlap_size=50  # overlap_size > 0 enables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        if len(chunks) == 1:
            assert "previous_content" not in chunks[0].metadata
            assert "next_content" not in chunks[0].metadata

    def test_overlap_size_zero_no_metadata(self):
        """
        Property: When overlap_size=0, no overlap metadata is added.
        """
        md_text = "# Header\n\nParagraph one.\n\n# Header 2\n\nParagraph two."
        config = ChunkConfig(
            max_chunk_size=100, overlap_size=0  # overlap_size=0 disables overlap
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(md_text)

        for chunk in chunks:
            # With overlap_size=0, previous_content should not be present
            assert "previous_content" not in chunk.metadata
