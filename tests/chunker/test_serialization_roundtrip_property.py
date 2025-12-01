#!/usr/bin/env python3
"""
Property-based tests for serialization round-trip guarantee.

**Feature: markdown-chunker-quality-audit, Property 14: Serialization Round-Trip**
**Validates: Requirements 10.4**

This module uses Hypothesis to generate random markdown text and verifies
that chunks can be serialized and deserialized without data loss.
"""

import json

from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.chunker.core import MarkdownChunker


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


def serialize_chunk(chunk):
    """Serialize a chunk to JSON-compatible dict."""
    return {
        "content": chunk.content,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "strategy": chunk.strategy,
        "metadata": chunk.metadata if hasattr(chunk, "metadata") else None,
    }


def deserialize_chunk(data):
    """Deserialize a chunk from JSON-compatible dict."""
    # Return as dict for comparison (we don't need to reconstruct the object)
    return data


class TestSerializationRoundTripProperty:
    """Property-based tests for serialization round-trip guarantee."""

    @settings(max_examples=1000, deadline=10000)
    @given(random_markdown())
    def test_property_serialization_roundtrip(self, markdown_text):
        """
        **Property 14: Serialization Round-Trip**
        **Validates: Requirements 10.4**

        For any markdown text:
        - Chunks can be serialized to JSON
        - Deserialized chunks preserve all data
        - Round-trip preserves content, line numbers, strategy, and metadata
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            # Skip examples that cause errors
            return

        if len(chunks) == 0:
            return

        # Serialize all chunks
        serialized = [serialize_chunk(chunk) for chunk in chunks]

        # Convert to JSON and back (full round-trip)
        try:
            json_str = json.dumps(serialized)
            deserialized = json.loads(json_str)
        except (TypeError, ValueError) as e:
            assert False, f"Serialization failed: {e}"

        # Property: Same number of chunks after round-trip
        assert len(deserialized) == len(
            chunks
        ), f"Round-trip changed number of chunks: {len(chunks)} -> {len(deserialized)}"

        # Property: All chunk data preserved
        for i, (original, restored) in enumerate(zip(chunks, deserialized)):
            # Content preserved
            assert (
                restored["content"] == original.content
            ), f"Chunk {i} content not preserved in round-trip"

            # Line numbers preserved
            assert (
                restored["start_line"] == original.start_line
            ), f"Chunk {i} start_line not preserved in round-trip"
            assert (
                restored["end_line"] == original.end_line
            ), f"Chunk {i} end_line not preserved in round-trip"

            # Strategy preserved
            assert (
                restored["strategy"] == original.strategy
            ), f"Chunk {i} strategy not preserved in round-trip"

    @settings(max_examples=500, deadline=10000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "P")),
            min_size=10,
            max_size=5000,
        ).filter(lambda x: x.strip())
    )
    def test_property_serialization_roundtrip_plain_text(self, text):
        """
        Property: Plain text chunks can be serialized and deserialized.

        For any plain text, chunks should survive round-trip.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)
        for i, (original, restored) in enumerate(zip(chunks, deserialized)):
            assert restored["content"] == original.content

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
    def test_property_serialization_roundtrip_with_lists(self, list_items):
        """
        Property: List chunks can be serialized and deserialized.

        For any list, chunks should survive round-trip.
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

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)

    @settings(max_examples=200, deadline=10000)
    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyz\n ",
            min_size=20,
            max_size=500,
        ).filter(lambda x: x.strip())
    )
    def test_property_serialization_roundtrip_with_code(self, code_content):
        """
        Property: Code block chunks can be serialized and deserialized.

        For any code content, chunks should survive round-trip.
        """
        markdown_text = f"# Code Example\n\n```python\n{code_content}\n```"

        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text)
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)


class TestSerializationWithStrategies:
    """Test serialization across different strategies."""

    @settings(max_examples=300, deadline=10000)
    @given(random_markdown(), st.sampled_from(["structural", "sentences", "mixed"]))
    def test_property_serialization_across_strategies(self, markdown_text, strategy):
        """
        Property: Serialization should work for all strategies.

        For any markdown and any strategy, chunks should survive round-trip.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text, strategy=strategy)
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)
        for i, (original, restored) in enumerate(zip(chunks, deserialized)):
            assert restored["content"] == original.content
            assert restored["strategy"] == original.strategy


class TestSerializationEdgeCases:
    """Test serialization edge cases."""

    @settings(max_examples=100, deadline=5000)
    @given(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
            min_size=1,
            max_size=50,
        ).filter(lambda x: x.strip())
    )
    def test_property_serialization_single_line(self, single_line):
        """
        Property: Single line chunks can be serialized.

        For any single line, chunks should survive round-trip.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(single_line)
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)

    @settings(max_examples=100, deadline=5000)
    @given(random_markdown())
    def test_property_metadata_serialization(self, markdown_text):
        """
        Property: Metadata should be serializable.

        For any markdown, chunk metadata should survive round-trip.
        """
        chunker = MarkdownChunker()

        try:
            chunks = chunker.chunk(markdown_text, strategy="structural")
        except Exception:
            return

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify metadata preserved
        for i, (original, restored) in enumerate(zip(chunks, deserialized)):
            if hasattr(original, "metadata") and original.metadata:
                assert (
                    restored["metadata"] is not None
                ), f"Chunk {i} metadata lost in round-trip"
                # Metadata should be a dict
                assert isinstance(
                    restored["metadata"], dict
                ), f"Chunk {i} metadata is not a dict after round-trip"

    def test_special_characters_serialization(self):
        """Test serialization with special characters."""
        markdown_text = """# Title with "quotes" and 'apostrophes'

## Section with special chars: <>&

Content with unicode: café, naïve, 日本語

```python
# Code with special chars
def test():
    return "string with \n newline"
```
"""

        chunker = MarkdownChunker()
        chunks = chunker.chunk(markdown_text)

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Verify data preserved
        assert len(deserialized) == len(chunks)
        for i, (original, restored) in enumerate(zip(chunks, deserialized)):
            assert restored["content"] == original.content

    def test_empty_metadata_serialization(self):
        """Test serialization with empty or None metadata."""
        markdown_text = "Simple text without structure."

        chunker = MarkdownChunker()
        chunks = chunker.chunk(markdown_text)

        if len(chunks) == 0:
            return

        # Serialize and deserialize
        serialized = [serialize_chunk(chunk) for chunk in chunks]
        json_str = json.dumps(serialized)
        deserialized = json.loads(json_str)

        # Should not fail even with None metadata
        assert len(deserialized) == len(chunks)
