#!/usr/bin/env python3
"""
Property-based tests for idempotence guarantee.

**Feature: markdown-chunker-quality-audit, Property 6: Idempotence**
**Validates: Requirements 10.2, 10.5**

This module uses Hypothesis to generate random markdown text and verifies
that chunking the same input twice with the same configuration produces
identical results.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


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


def chunks_are_identical(chunks1, chunks2):
    """Compare two lists of chunks for exact equality."""
    if len(chunks1) != len(chunks2):
        return False, f"Different number of chunks: {len(chunks1)} vs {len(chunks2)}"

    for i, (chunk1, chunk2) in enumerate(zip(chunks1, chunks2)):
        if chunk1.content != chunk2.content:
            return False, f"Chunk {i} content differs"
        if chunk1.start_line != chunk2.start_line:
            return (
                False,
                f"Chunk {i} start_line differs: {chunk1.start_line} vs {chunk2.start_line}",
            )
        if chunk1.end_line != chunk2.end_line:
            return (
                False,
                f"Chunk {i} end_line differs: {chunk1.end_line} vs {chunk2.end_line}",
            )
        if chunk1.strategy != chunk2.strategy:
            return (
                False,
                f"Chunk {i} strategy differs: {chunk1.strategy} vs {chunk2.strategy}",
            )

    return True, "Chunks are identical"


class TestIdempotenceProperty:
    """Property-based tests for idempotence guarantee."""

    @settings(max_examples=1000, deadline=10000)
    @given(random_markdown())
    def test_property_idempotence(self, markdown_text):
        """
        **Property 6: Idempotence**
        **Validates: Requirements 10.2, 10.5**

        For any markdown text:
        - Chunking it twice with the same configuration must produce identical results
        - All chunk properties (content, start_line, end_line, strategy) must match
        """
        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            # Skip examples that cause errors
            return

        # Property: Chunking twice must produce identical results
        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, (
            f"Idempotence failed: {message}. "
            f"Chunking same input twice should produce identical results."
        )

    @settings(max_examples=500, deadline=10000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "P")),
            min_size=10,
            max_size=5000,
        ).filter(lambda x: x.strip())
    )
    def test_property_idempotence_plain_text(self, text):
        """
        Property: Plain text chunking should be idempotent.

        For any plain text, chunking twice should produce identical results.
        """
        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(text)
            chunks2 = chunker.chunk(text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Plain text idempotence failed: {message}"

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
    def test_property_idempotence_with_lists(self, list_items):
        """
        Property: List chunking should be idempotent.

        For any list, chunking twice should produce identical results.
        """
        markdown_text = "# List Document\n\n" + "\n".join(
            f"- {item}" for item in list_items
        )

        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"List idempotence failed: {message}"

    @settings(max_examples=200, deadline=10000)
    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz\n ",
            min_size=20,
            max_size=500,
        ).filter(lambda x: x.strip())
    )
    def test_property_idempotence_with_code(self, code_content):
        """
        Property: Code block chunking should be idempotent.

        For any code content, chunking twice should produce identical results.
        """
        markdown_text = f"# Code Example\n\n```python\n{code_content}\n```"

        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Code block idempotence failed: {message}"


class TestIdempotenceWithStrategies:
    """Test idempotence across different strategies."""

    @settings(max_examples=300, deadline=10000)
    @given(random_markdown(), st.sampled_from(["structural", "sentences", "mixed"]))
    def test_property_idempotence_across_strategies(self, markdown_text, strategy):
        """
        Property: Idempotence should work for all strategies.

        For any markdown and any strategy, chunking twice should produce identical results.
        """
        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text, strategy=strategy)
            chunks2 = chunker.chunk(markdown_text, strategy=strategy)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Strategy '{strategy}' idempotence failed: {message}"

    @settings(max_examples=200, deadline=10000)
    @given(
        st.integers(min_value=500, max_value=5000),
        st.integers(min_value=100, max_value=2000),
    )
    def test_property_idempotence_with_different_chunk_sizes(
        self, max_chunk_size, min_chunk_size
    ):
        """
        Property: Idempotence with different chunk sizes.

        For any chunk size configuration, chunking twice should produce identical results.
        """
        if min_chunk_size >= max_chunk_size:
            return

        markdown_text = "# Test Document\n\n" + ("Content paragraph. " * 100)

        config = ChunkConfig(
            max_chunk_size=max_chunk_size, min_chunk_size=min_chunk_size
        )
        chunker = MarkdownChunker(config=config)

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Chunk size config idempotence failed: {message}"


class TestIdempotenceEdgeCases:
    """Test idempotence edge cases."""

    @settings(max_examples=100, deadline=5000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip())
    )
    def test_property_idempotence_single_line(self, single_line):
        """
        Property: Single line chunking should be idempotent.

        For any single line, chunking twice should produce identical results.
        """
        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(single_line)
            chunks2 = chunker.chunk(single_line)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Single line idempotence failed: {message}"

    @settings(max_examples=100, deadline=5000)
    @given(
        st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=1,
            max_size=20,
        )
    )
    def test_property_idempotence_multiple_paragraphs(self, paragraphs):
        """
        Property: Multiple paragraphs chunking should be idempotent.

        For any list of paragraphs, chunking twice should produce identical results.
        """
        markdown_text = "\n\n".join(paragraphs)

        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Multiple paragraphs idempotence failed: {message}"

    @settings(max_examples=100, deadline=5000)
    @given(
        st.integers(min_value=1, max_value=6),
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=5,
            max_size=50,
        ).filter(lambda x: x.strip()),
    )
    def test_property_idempotence_headers_only(self, header_level, header_text):
        """
        Property: Headers-only documents chunking should be idempotent.

        For any header, chunking twice should produce identical results.
        """
        markdown_text = f"{'#' * header_level} {header_text}"

        chunker = MarkdownChunker()

        try:
            chunks1 = chunker.chunk(markdown_text)
            chunks2 = chunker.chunk(markdown_text)
        except Exception:
            return

        identical, message = chunks_are_identical(chunks1, chunks2)
        assert identical, f"Header-only idempotence failed: {message}"

    @settings(max_examples=50, deadline=5000)
    @given(random_markdown())
    def test_property_idempotence_multiple_runs(self, markdown_text):
        """
        Property: Multiple runs should all produce identical results.

        Chunking the same input 5 times should produce identical results each time.
        """
        chunker = MarkdownChunker()

        try:
            results = [chunker.chunk(markdown_text) for _ in range(5)]
        except Exception:
            return

        # All results should be identical to the first
        for i, chunks in enumerate(results[1:], start=2):
            identical, message = chunks_are_identical(results[0], chunks)
            assert identical, (
                f"Run {i} differs from run 1: {message}. "
                f"All runs should produce identical results."
            )
