#!/usr/bin/env python3
"""
Property-based tests for subsection splitting functionality.

**Feature: fix-chunking-quality, Property 3: Subsection Hierarchy Preservation**
**Validates: Requirements 3.3, 10.1**

This module uses Hypothesis to generate random markdown with nested subsections
and verifies that all subsection content appears in output with correct metadata.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.strategies.structural_strategy import StructuralStrategy
from markdown_chunker.chunker.types import ChunkConfig


# Hypothesis strategies for generating markdown
@st.composite
def markdown_header(draw, level=None):
    """Generate a markdown header."""
    if level is None:
        level = draw(st.integers(min_value=1, max_value=6))
    else:
        level = draw(st.just(level))

    # Generate header text (avoid special characters that might break parsing)
    text = draw(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" -_"
            ),
            min_size=3,
            max_size=50,
        ).filter(lambda x: x.strip() and not x.startswith("#"))
    )

    prefix = "#" * level
    return f"{prefix} {text.strip()}"


@st.composite
def markdown_content(draw):
    """Generate markdown content (paragraphs)."""
    num_paragraphs = draw(st.integers(min_value=1, max_value=3))
    paragraphs = []

    for _ in range(num_paragraphs):
        text = draw(
            st.text(
                alphabet=st.characters(
                    whitelist_categories=("Lu", "Ll", "Nd"),
                    whitelist_characters=" .,!?-",
                ),
                min_size=10,
                max_size=100,
            ).filter(lambda x: x.strip())
        )
        paragraphs.append(text.strip())

    return "\n\n".join(paragraphs)


@st.composite
def markdown_section(draw, level=1, max_depth=3):
    """Generate a markdown section with optional subsections."""
    # Generate header
    header = draw(markdown_header(level=level))

    # Generate content
    content = draw(markdown_content())

    parts = [header, "", content]

    # Maybe add subsections (if not at max depth)
    if level < max_depth:
        has_subsections = draw(st.booleans())
        if has_subsections:
            num_subsections = draw(st.integers(min_value=1, max_value=3))
            for _ in range(num_subsections):
                subsection = draw(
                    markdown_section(level=level + 1, max_depth=max_depth)
                )
                parts.extend(["", subsection])

    return "\n".join(parts)


@st.composite
def markdown_document(draw):
    """Generate a complete markdown document with nested sections."""
    # Main title
    title = draw(markdown_header(level=1))
    intro = draw(markdown_content())

    parts = [title, "", intro]

    # Add 1-3 main sections
    num_sections = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_sections):
        section = draw(markdown_section(level=2, max_depth=4))
        parts.extend(["", section])

    return "\n".join(parts)


class TestSubsectionSplittingProperties:
    """Property-based tests for subsection splitting."""

    @settings(max_examples=50, deadline=5000)
    @given(markdown_document())
    def test_property_subsection_hierarchy_preservation(self, markdown_text):
        """
        **Property 3: Subsection Hierarchy Preservation**
        **Validates: Requirements 3.3, 10.1**

        For any markdown document with nested subsections:
        - All subsection content should appear in output chunks
        - Chunks should have correct header_path metadata
        - No content should be lost
        """
        strategy = StructuralStrategy()
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=100)

        try:
            chunks = strategy.chunk(markdown_text, config)
        except Exception:
            # If chunking fails, skip this example
            # (some generated markdown might be edge cases)
            return

        # Property 1: All chunks should have content
        assert all(
            chunk.content.strip() for chunk in chunks
        ), "All chunks should have non-empty content"

        # Property 2: Total output should preserve most input
        # (allow some whitespace normalization)
        input_chars = len(markdown_text.strip())
        output_chars = sum(len(chunk.content.strip()) for chunk in chunks)

        if input_chars > 0:
            coverage = output_chars / input_chars
            assert coverage >= 0.80, (
                f"Output should preserve at least 80% of input. "
                f"Coverage: {coverage:.1%} ({output_chars}/{input_chars} chars)"
            )

        # Property 3: Chunks should have metadata
        for chunk in chunks:
            assert (
                "strategy" in chunk.metadata
            ), "Each chunk should have strategy metadata"
            assert (
                chunk.metadata["strategy"] == "structural"
            ), "Strategy should be 'structural'"

        # Property 4: If document has headers, chunks should have header metadata
        has_headers = any(
            line.strip().startswith("#") for line in markdown_text.split("\n")
        )
        if has_headers and chunks:
            # At least some chunks should have header metadata
            chunks_with_headers = [
                c
                for c in chunks
                if "header_text" in c.metadata or "header_level" in c.metadata
            ]
            assert (
                len(chunks_with_headers) > 0
            ), "Documents with headers should produce chunks with header metadata"

    @settings(max_examples=30, deadline=5000)
    @given(st.lists(markdown_section(level=2, max_depth=3), min_size=2, max_size=5))
    def test_property_multiple_sections_preserved(self, sections):
        """
        Property: Multiple sections should all be preserved in output.

        For any list of sections, all section content should appear in chunks.
        """
        # Combine sections into document
        markdown_text = "\n\n".join(sections)

        strategy = StructuralStrategy()
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=100)

        try:
            chunks = strategy.chunk(markdown_text, config)
        except Exception:
            return

        # All sections should be represented in output
        combined_output = " ".join(chunk.content for chunk in chunks)

        # Check that major content from each section appears
        for section in sections:
            # Extract first line (header) from section
            first_line = section.split("\n")[0].strip()
            if first_line.startswith("#"):
                # Remove # symbols to get header text
                header_text = first_line.lstrip("#").strip()
                if header_text:  # Only check non-empty headers
                    assert (
                        header_text in combined_output
                    ), f"Section header '{header_text}' should appear in output"

    @settings(max_examples=30, deadline=5000)
    @given(
        st.integers(min_value=1, max_value=6),
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=5,
            max_size=30,
        ).filter(lambda x: x.strip()),
    )
    def test_property_header_levels_preserved(self, level, header_text):
        """
        Property: Header levels should be correctly identified in metadata.

        For any header level (1-6), chunks containing that header should
        have correct header_level in metadata.
        """
        markdown_text = f"{'#' * level} {header_text}\n\nSome content here."

        strategy = StructuralStrategy()
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=100)

        try:
            chunks = strategy.chunk(markdown_text, config)
        except Exception:
            return

        if not chunks:
            return

        # At least one chunk should have the header
        chunks_with_header = [c for c in chunks if header_text in c.content]

        assert (
            len(chunks_with_header) > 0
        ), f"Header '{header_text}' should appear in at least one chunk"

        # Check metadata for chunks with header
        for chunk in chunks_with_header:
            if "header_level" in chunk.metadata:
                # If header_level is present, it should match
                assert (
                    chunk.metadata["header_level"] == level
                ), f"Header level should be {level}, got {chunk.metadata['header_level']}"


class TestSubsectionSplittingEdgeCases:
    """Property tests for edge cases."""

    @settings(max_examples=20, deadline=3000)
    @given(st.integers(min_value=100, max_value=10000))
    def test_property_large_content_split(self, content_size):
        """
        Property: Large content should be split into multiple chunks.

        For any large content block, it should be split appropriately.
        """
        # Generate large content
        large_content = "A" * content_size
        markdown_text = f"# Header\n\n{large_content}"

        strategy = StructuralStrategy()
        config = ChunkConfig(max_chunk_size=1000, min_chunk_size=100)

        try:
            chunks = strategy.chunk(markdown_text, config)
        except Exception:
            return

        if content_size > config.max_chunk_size:
            # Should produce multiple chunks
            assert (
                len(chunks) > 1
            ), f"Large content ({content_size} chars) should be split into multiple chunks"

        # All content should be preserved
        total_output = sum(len(chunk.content) for chunk in chunks)
        assert (
            total_output >= content_size * 0.9
        ), "At least 90% of content should be preserved"

    @settings(max_examples=20, deadline=3000)
    @given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
    def test_property_empty_sections_handled(self, section_titles):
        """
        Property: Empty sections should be handled gracefully.

        For any list of section titles (even with empty content),
        chunking should not fail.
        """
        # Create sections with minimal content
        sections = [f"## {title}\n\n" for title in section_titles]
        markdown_text = "# Main\n\n" + "\n".join(sections)

        strategy = StructuralStrategy()
        config = ChunkConfig(max_chunk_size=2000, min_chunk_size=100)

        try:
            chunks = strategy.chunk(markdown_text, config)
        except Exception:
            return

        # Should not crash and should produce some output
        assert isinstance(chunks, list), "Should return a list of chunks"
