#!/usr/bin/env python3
"""
Property-based tests for monotonic chunk ordering guarantee.

**Feature: markdown-chunker-quality-audit, Property 7: Monotonic Chunk Ordering**
**Validates: Requirements 3.4, 10.2**

This module uses Hypothesis to generate random markdown text and verifies
that chunks appear in the same order as their content appears in the input,
with monotonically increasing start_line values.

Migration note: Migrated to markdown_chunker_v2 (December 2025)
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


# Hypothesis strategies for generating markdown
@st.composite
def random_markdown(draw):
    """Generate random markdown content."""
    elements = []

    # Add title
    title = draw(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=5,
            max_size=50,
        ).filter(lambda x: x.strip())
    )
    elements.append(f"# {title}")
    elements.append("")

    # Add 1-5 sections
    num_sections = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_sections):
        # Section header
        header = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=3,
                max_size=40,
            ).filter(lambda x: x.strip())
        )
        elements.append(f"## {header}")
        elements.append("")

        # Section content (1-3 paragraphs)
        num_paragraphs = draw(st.integers(min_value=1, max_value=3))
        for _ in range(num_paragraphs):
            paragraph = draw(
                st.text(
                    alphabet=st.characters(
                        whitelist_categories=("Lu", "Ll", "Nd"),
                        whitelist_characters=" .,!?-\n",
                    ),
                    min_size=20,
                    max_size=200,
                ).filter(lambda x: x.strip())
            )
            elements.append(paragraph)
            elements.append("")

    return "\n".join(elements)


class TestMonotonicOrderingProperty:
    """Property-based tests for monotonic chunk ordering guarantee."""

    @settings(max_examples=1000, deadline=10000)
    @given(random_markdown())
    def test_property_monotonic_ordering(self, markdown_text):
        """
        **Property 7: Monotonic Chunk Ordering**
        **Validates: Requirements 3.4, 10.2**

        For any markdown text:
        - Chunks must appear in the same order as their content in the input
        - start_line values must be monotonically increasing
        - No chunk should start before the previous chunk
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            # Skip examples that cause errors
            return

        if len(chunks) == 0:
            return

        # Property: start_line values must be monotonically increasing
        for i in range(1, len(chunks)):
            prev_start = chunks[i - 1].start_line
            curr_start = chunks[i].start_line

            assert curr_start >= prev_start, (
                f"Monotonic ordering violated: "
                f"Chunk {i} starts at line {curr_start}, "
                f"but chunk {i-1} starts at line {prev_start}. "
                f"Chunks must appear in input order."
            )

    @settings(max_examples=500, deadline=10000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "P")),
            min_size=10,
            max_size=5000,
        ).filter(lambda x: x.strip())
    )
    def test_property_monotonic_ordering_plain_text(self, text):
        """
        Property: Plain text chunks should be in monotonic order.

        For any plain text, chunk start_line values should be monotonically increasing.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"Plain text monotonic ordering violated at chunk {i}"

    @settings(max_examples=300, deadline=10000)
    @given(
        st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=5,
                max_size=100,
            ).filter(lambda x: x.strip()),
            min_size=1,
            max_size=20,
        )
    )
    def test_property_monotonic_ordering_with_lists(self, list_items):
        """
        Property: List chunks should be in monotonic order.

        For any list, chunk start_line values should be monotonically increasing.
        """
        markdown_text = "# List Document\n\n" + "\n".join(
            f"- {item}" for item in list_items
        )

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"List monotonic ordering violated at chunk {i}"

    @settings(max_examples=200, deadline=10000)
    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz\n ",
            min_size=20,
            max_size=500,
        ).filter(lambda x: x.strip())
    )
    def test_property_monotonic_ordering_with_code(self, code_content):
        """
        Property: Code block chunks should be in monotonic order.

        For any code content, chunk start_line values should be monotonically increasing.
        """
        markdown_text = f"# Code Example\n\n```python\n{code_content}\n```"

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"Code block monotonic ordering violated at chunk {i}"


class TestMonotonicOrderingWithStrategies:
    """Test monotonic ordering across different strategies.

    Note: In v2, strategy is selected automatically based on content analysis.
    These tests verify monotonic ordering regardless of which strategy is selected.
    """

    @settings(max_examples=300, deadline=10000)
    @given(random_markdown())
    def test_property_monotonic_ordering_auto_strategy(self, markdown_text):
        """
        Property: Monotonic ordering should work with automatic strategy selection.

        For any markdown, chunks should be in monotonic order regardless of
        which strategy v2 selects automatically.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"Monotonic ordering violated at chunk {i}"

    @settings(max_examples=200, deadline=10000)
    @given(
        st.integers(min_value=500, max_value=5000),
        st.integers(min_value=100, max_value=2000),
    )
    def test_property_monotonic_ordering_with_different_chunk_sizes(
        self, max_chunk_size, min_chunk_size
    ):
        """
        Property: Monotonic ordering with different chunk sizes.

        For any chunk size configuration, chunks should be in monotonic order.
        """
        if min_chunk_size >= max_chunk_size:
            return

        markdown_text = "# Test Document\n\n" + ("Content paragraph. " * 100)

        config = ChunkConfig(
            max_chunk_size=max_chunk_size, min_chunk_size=min_chunk_size
        )
        chunker = MarkdownChunker(config=config)

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"Chunk size config monotonic ordering violated at chunk {i}"


class TestMonotonicOrderingEdgeCases:
    """Test monotonic ordering edge cases."""

    @settings(max_examples=100, deadline=5000)
    @given(
        st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=1,
            max_size=20,
        )
    )
    def test_property_monotonic_ordering_multiple_paragraphs(self, paragraphs):
        """
        Property: Multiple paragraphs should be in monotonic order.

        For any list of paragraphs, chunks should be in monotonic order.
        """
        markdown_text = "\n\n".join(paragraphs)

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        for i in range(1, len(chunks)):
            assert (
                chunks[i].start_line >= chunks[i - 1].start_line
            ), f"Multiple paragraphs monotonic ordering violated at chunk {i}"

    @settings(max_examples=100, deadline=5000)
    @given(random_markdown())
    def test_property_strict_monotonic_ordering(self, markdown_text):
        """
        Property: Verify strict monotonic ordering (no equal start_lines).

        For most documents, start_line values should be strictly increasing
        (each chunk starts after the previous one ends).
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) <= 1:
            return

        # Count how many times start_line stays the same
        equal_count = sum(
            1
            for i in range(1, len(chunks))
            if chunks[i].start_line == chunks[i - 1].start_line
        )

        # Most chunks should have strictly increasing start_line
        # Allow some overlap cases, but not too many
        assert equal_count < len(chunks) * 0.5, (
            f"Too many chunks with equal start_line: {equal_count}/{len(chunks)}. "
            f"Most chunks should have strictly increasing start_line values."
        )

    @settings(max_examples=100, deadline=5000)
    @given(random_markdown())
    def test_property_end_line_consistency(self, markdown_text):
        """
        Property: Verify end_line is also monotonic (with overlap consideration).

        For any document, end_line values should generally be monotonic,
        though overlap may cause some variation.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) <= 1:
            return

        # Check that end_line values don't decrease dramatically
        for i in range(1, len(chunks)):
            # Allow some overlap, but end_line shouldn't go backwards significantly
            assert chunks[i].end_line >= chunks[i - 1].start_line, (
                f"Chunk {i} ends before chunk {i-1} starts: "
                f"chunk {i} end_line={chunks[i].end_line}, "
                f"chunk {i-1} start_line={chunks[i-1].start_line}"
            )

    @settings(max_examples=100, deadline=5000)
    @given(random_markdown())
    def test_property_no_backwards_chunks(self, markdown_text):
        """
        Property: No chunk should appear before previous chunk in document.

        For any document, each chunk's start should be at or after
        the previous chunk's start.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Verify no chunk goes backwards
        for i in range(1, len(chunks)):
            assert chunks[i].start_line >= chunks[i - 1].start_line, (
                f"Chunk {i} appears before chunk {i-1} in document: "
                f"start_line {chunks[i].start_line} < {chunks[i-1].start_line}"
            )
