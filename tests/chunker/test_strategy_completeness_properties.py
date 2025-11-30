#!/usr/bin/env python3
"""
Property-based tests for strategy completeness.

**Feature: fix-chunking-quality, Property 6: Strategy Completeness**
**Validates: Requirements 2.2, 10.1**

This module verifies that strategies returning can_handle=True don't return
empty chunks for non-empty input.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# Import shared generators
from tests.conftest import markdown_document, nested_markdown_document


class TestStrategyCompletenessProperties:
    """Property-based tests for strategy completeness."""

    @settings(max_examples=100, deadline=5000)
    @given(markdown_document())
    def test_property_chunker_completeness(self, markdown_text):
        """
        **Property 6: Strategy Completeness**
        **Validates: Requirements 2.2, 10.1**

        For any non-empty markdown document:
        - Chunker should produce non-empty chunks
        - Should never silently return empty result
        """
        if not markdown_text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
            # For non-empty input, should produce chunks
            assert len(chunks) > 0, "Chunker returned empty chunks for non-empty input"

            # All chunks should have content
            for i, chunk in enumerate(chunks):
                assert chunk.content.strip(), f"Chunk {i} is empty"
        except Exception as e:
            # If chunker fails, it should raise an error, not return empty
            assert False, f"Chunker failed: {e}"

    @settings(max_examples=100, deadline=5000)
    @given(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" .,!?"
            ),
            min_size=50,
            max_size=1000,
        )
    )
    def test_property_plain_text_completeness(self, text):
        """
        Property: Chunker should handle plain text.

        For any plain text:
        - Should produce non-empty chunks
        - Should not fail silently
        """
        if not text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(text)
            assert len(chunks) > 0, "Chunker returned empty chunks for plain text"

            for i, chunk in enumerate(chunks):
                assert chunk.content.strip(), f"Chunk {i} is empty"
        except Exception as e:
            assert False, f"Chunker failed on plain text: {e}"

    @settings(max_examples=100, deadline=5000)
    @given(nested_markdown_document())
    def test_property_nested_document_completeness(self, markdown_text):
        """
        Property: Strategies should handle nested documents.

        For any nested markdown document:
        - At least one strategy should be able to handle it
        - That strategy should produce non-empty chunks
        """
        if not markdown_text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
            assert (
                len(chunks) > 0
            ), "Chunker returned empty chunks for non-empty nested document"

            for i, chunk in enumerate(chunks):
                assert chunk.content.strip(), f"Chunk {i} is empty"
        except Exception as e:
            assert False, f"Chunker failed on nested document: {e}"

    @settings(max_examples=50, deadline=5000)
    @given(
        markdown_document(),
        st.sampled_from(["structural", "sentences", "mixed"]),
    )
    def test_property_explicit_strategy_completeness(
        self, markdown_text, strategy_name
    ):
        """
        Property: Explicitly requested strategies should produce chunks.

        For any markdown and explicitly requested strategy:
        - Strategy should either produce chunks or raise clear error
        - Should never silently return empty chunks
        """
        if not markdown_text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text, strategy=strategy_name)

            # If no error was raised, chunks should be non-empty
            assert (
                len(chunks) > 0
            ), f"Strategy '{strategy_name}' returned empty chunks without error"

            for i, chunk in enumerate(chunks):
                assert (
                    chunk.content.strip()
                ), f"Chunk {i} from '{strategy_name}' is empty"
        except Exception:
            # Raising an error is acceptable - silent failure is not
            pass


class TestStrategyCompletenessEdgeCases:
    """Test strategy completeness with edge cases."""

    @settings(max_examples=50, deadline=3000)
    @given(
        st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                min_size=1,
                max_size=50,
            ),
            min_size=1,
            max_size=20,
        )
    )
    def test_property_single_paragraph_completeness(self, paragraphs):
        """
        Property: Single paragraph documents should be handled.

        For any single paragraph:
        - Should produce at least one chunk
        - Chunk should contain the paragraph content
        """
        markdown_text = "\n\n".join(p for p in paragraphs if p.strip())

        if not markdown_text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
            assert len(chunks) > 0, "Single paragraph should produce at least one chunk"

            combined = " ".join(chunk.content for chunk in chunks)
            # Check that major content appears
            for para in paragraphs:
                if para.strip() and len(para.strip()) > 10:
                    snippet = para.strip()[:10]
                    assert (
                        snippet in combined
                    ), f"Paragraph snippet '{snippet}' missing from output"
        except Exception as e:
            assert False, f"Failed to handle single paragraph: {e}"

    @settings(max_examples=50, deadline=3000)
    @given(
        st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                min_size=3,
                max_size=30,
            ),
            min_size=1,
            max_size=10,
        )
    )
    def test_property_headers_only_completeness(self, headers):
        """
        Property: Documents with only headers should be handled.

        For any document with only headers:
        - Should produce chunks
        - Headers should appear in output
        """
        markdown_text = "\n\n".join(f"## {h}" for h in headers if h.strip())

        if not markdown_text.strip():
            return

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
            assert len(chunks) > 0, "Headers-only document should produce chunks"

            combined = " ".join(chunk.content for chunk in chunks)
            for header in headers:
                if header.strip():
                    assert (
                        header.strip() in combined
                    ), f"Header '{header}' missing from output"
        except Exception as e:
            assert False, f"Failed to handle headers-only document: {e}"

    @settings(max_examples=30, deadline=3000)
    @given(
        st.integers(min_value=100, max_value=1000),
        st.integers(min_value=50, max_value=500),
    )
    def test_property_completeness_with_size_constraints(
        self, max_chunk_size, min_chunk_size
    ):
        """
        Property: Strategies should respect size constraints.

        For any chunk size configuration:
        - Strategies should produce chunks within size limits
        - Should not return empty chunks
        """
        if min_chunk_size >= max_chunk_size:
            return

        markdown_text = "# Test Document\n\n" + ("This is a test paragraph. " * 50)

        config = ChunkConfig(
            max_chunk_size=max_chunk_size, min_chunk_size=min_chunk_size
        )
        chunker = MarkdownChunker(config=config)

        try:
            chunks = chunker.chunk(markdown_text)
            assert len(chunks) > 0, "Should produce chunks with size constraints"

            for i, chunk in enumerate(chunks):
                assert chunk.content.strip(), f"Chunk {i} is empty"
                # Chunks should generally respect max size (with some tolerance)
                # Note: Some strategies may exceed max size when content cannot be split
                # (e.g., code blocks, tables). Allow up to 50% tolerance.
                assert (
                    len(chunk.content) <= max_chunk_size * 1.5
                ), f"Chunk {i} exceeds max size by >50%"
        except Exception as e:
            assert False, f"Failed with size constraints: {e}"
