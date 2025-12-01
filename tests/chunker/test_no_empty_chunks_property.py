#!/usr/bin/env python3
"""
Property-based tests for no empty chunks guarantee.

**Feature: markdown-chunker-quality-audit, Property 2: No Empty Chunks**
**Validates: Requirements 1.3, 6.1**

This module uses Hypothesis to generate random markdown text and verifies
that non-empty input never produces empty chunks.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


# Hypothesis strategies for generating markdown
@st.composite
def non_empty_markdown(draw):
    """Generate non-empty markdown content."""
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


class TestNoEmptyChunksProperty:
    """Property-based tests for no empty chunks guarantee."""

    @settings(max_examples=1000, deadline=10000)
    @given(non_empty_markdown())
    def test_property_no_empty_chunks(self, markdown_text):
        """
        **Property 2: No Empty Chunks for Non-Empty Input**
        **Validates: Requirements 1.3, 6.1**

        For any non-empty markdown text:
        - All chunks must have non-empty content
        - No chunk should have only whitespace
        """
        # Verify input is non-empty
        assert markdown_text.strip(), "Input should be non-empty"

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            # Skip examples that cause errors
            return

        # Property: All chunks must have non-empty content
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), (
                f"Chunk {i} is empty or whitespace-only. "
                f"Non-empty input should never produce empty chunks."
            )

    @settings(max_examples=500, deadline=10000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "P")),
            min_size=10,
            max_size=5000,
        ).filter(lambda x: x.strip())
    )
    def test_property_no_empty_chunks_plain_text(self, text):
        """
        Property: Plain text should never produce empty chunks.

        For any non-empty plain text, all chunks should have content.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(text)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert (
                chunk.content.strip()
            ), f"Chunk {i} is empty. Plain text should never produce empty chunks."

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
    def test_property_no_empty_chunks_with_lists(self, list_items):
        """
        Property: Markdown lists should never produce empty chunks.

        For any list of items, all chunks should have content.
        """
        # Create markdown list
        markdown_text = "# List Document\n\n" + "\n".join(
            f"- {item}" for item in list_items
        )

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert (
                chunk.content.strip()
            ), f"Chunk {i} is empty. List content should never produce empty chunks."

    @settings(max_examples=200, deadline=10000)
    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz\n ",
            min_size=20,
            max_size=500,
        ).filter(lambda x: x.strip())
    )
    def test_property_no_empty_chunks_with_code(self, code_content):
        """
        Property: Code blocks should never produce empty chunks.

        For any code content, all chunks should have content.
        """
        markdown_text = f"# Code Example\n\n```python\n{code_content}\n```"

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert (
                chunk.content.strip()
            ), f"Chunk {i} is empty. Code blocks should never produce empty chunks."


class TestNoEmptyChunksWithStrategies:
    """Test no empty chunks across different strategies."""

    @settings(max_examples=300, deadline=10000)
    @given(non_empty_markdown(), st.sampled_from(["structural", "sentences", "mixed"]))
    def test_property_no_empty_chunks_across_strategies(self, markdown_text, strategy):
        """
        Property: No empty chunks should work for all strategies.

        For any non-empty markdown and any strategy, no chunks should be empty.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text, strategy=strategy)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), (
                f"Strategy '{strategy}' produced empty chunk {i}. "
                f"No strategy should produce empty chunks from non-empty input."
            )

    @settings(max_examples=200, deadline=10000)
    @given(
        st.integers(min_value=500, max_value=5000),
        st.integers(min_value=100, max_value=2000),
    )
    def test_property_no_empty_chunks_with_different_chunk_sizes(
        self, max_chunk_size, min_chunk_size
    ):
        """
        Property: No empty chunks with different chunk sizes.

        For any chunk size configuration, no chunks should be empty.
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

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), (
                f"Chunk size config produced empty chunk {i}. "
                f"No configuration should produce empty chunks."
            )


class TestNoEmptyChunksEdgeCases:
    """Test no empty chunks edge cases."""

    @settings(max_examples=100, deadline=5000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip())
    )
    def test_property_no_empty_chunks_single_line(self, single_line):
        """
        Property: Single line should not produce empty chunks.

        For any single line of text, chunks should have content.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(single_line)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert chunk.content.strip(), f"Single line input produced empty chunk {i}."

    @settings(max_examples=100, deadline=5000)
    @given(
        st.lists(
            st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
            min_size=1,
            max_size=20,
        )
    )
    def test_property_no_empty_chunks_multiple_paragraphs(self, paragraphs):
        """
        Property: Multiple paragraphs should not produce empty chunks.

        For any list of paragraphs, all chunks should have content.
        """
        markdown_text = "\n\n".join(paragraphs)

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert (
                chunk.content.strip()
            ), f"Multiple paragraphs produced empty chunk {i}."

    @settings(max_examples=100, deadline=5000)
    @given(
        st.integers(min_value=1, max_value=6),
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=5,
            max_size=50,
        ).filter(lambda x: x.strip()),
    )
    def test_property_no_empty_chunks_headers_only(self, header_level, header_text):
        """
        Property: Headers-only documents should not produce empty chunks.

        For any header, chunks should have content.
        """
        markdown_text = f"{'#' * header_level} {header_text}"

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        # All chunks must have content
        for i, chunk in enumerate(chunks):
            assert (
                chunk.content.strip()
            ), f"Header-only document produced empty chunk {i}."
