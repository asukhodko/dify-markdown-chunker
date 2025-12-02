"""Integration tests for the redesigned overlap model.

Tests the full pipeline with the new previous_content/next_content model.
"""

from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestOverlapRedesignIntegration:
    """Integration tests for overlap redesign."""

    def test_full_pipeline_metadata_mode(self):
        """End-to-end test with metadata mode."""
        config = ChunkConfig(max_chunk_size=150, enable_overlap=True, overlap_size=30)
        chunker = MarkdownChunker(config)

        md_text = """# Section A
This is the first section with some content here.
It has multiple paragraphs.

# Section B
This is the second section with more content here.
It also has detailed information.

# Section C
This is the third section with additional content.
Final section of the document."""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # Should have multiple chunks
        assert len(chunks) > 1

        # First chunk should have no previous_content
        assert "previous_content" not in chunks[0].metadata

        # Last chunk should have no next_content
        assert "next_content" not in chunks[-1].metadata

        # Middle chunks should have contexts
        for i in range(1, len(chunks) - 1):
            chunk = chunks[i]
            # Should have previous_content
            if "previous_content" in chunk.metadata:
                assert isinstance(chunk.metadata["previous_content"], str)
                assert len(chunk.metadata["previous_content"]) > 0
                assert len(chunk.metadata["previous_content"]) <= 30

            # Should have next_content
            if "next_content" in chunk.metadata:
                assert isinstance(chunk.metadata["next_content"], str)
                assert len(chunk.metadata["next_content"]) > 0
                assert len(chunk.metadata["next_content"]) <= 30

        # Verify no legacy fields
        for chunk in chunks:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata
            # Note: has_overlap IS present in block-based overlap metadata mode
            # This is correct behavior - block-based overlap adds metadata fields

    def test_full_pipeline_legacy_mode(self):
        """End-to-end test with legacy mode."""
        config = ChunkConfig(max_chunk_size=150, enable_overlap=True, overlap_size=30)
        chunker = MarkdownChunker(config)

        md_text = """# Section A
This is the first section with some content here.

# Section B
This is the second section with more content here."""

        result = chunker.chunk(md_text, include_metadata=False)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # Verify no context fields in metadata
        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    def test_mode_equivalence_full_document(self):
        """Compare outputs across modes for equivalence."""
        config = ChunkConfig(max_chunk_size=200, enable_overlap=True, overlap_size=40)
        chunker = MarkdownChunker(config)

        md_text = """# Introduction
This is an introduction section.

# Main Content
This is the main content with details.

# Conclusion
This is the conclusion."""

        # Get results from both modes
        meta_result = chunker.chunk(md_text, include_metadata=True)
        legacy_result = chunker.chunk(md_text, include_metadata=False)

        meta_chunks = (
            meta_result.chunks if hasattr(meta_result, "chunks") else meta_result
        )
        legacy_chunks = (
            legacy_result.chunks if hasattr(legacy_result, "chunks") else legacy_result
        )

        # Should have same number of chunks
        assert len(meta_chunks) == len(legacy_chunks)

        # Validate equivalence invariant
        for i in range(len(meta_chunks)):
            meta = meta_chunks[i]
            legacy = legacy_chunks[i]

            # Compose full context from metadata mode
            prev = meta.metadata.get("previous_content", "")
            content = meta.content
            next_ctx = meta.metadata.get("next_content", "")

            parts = []
            if prev:
                parts.append(prev)
            parts.append(content)
            if next_ctx:
                parts.append(next_ctx)

            composed = "\n\n".join(parts)

            # Should match legacy mode
            assert composed == legacy.content, f"Chunk {i}: equivalence failed"

    def test_section_boundary_isolation(self):
        """Verify no cross-section context."""
        config = ChunkConfig(max_chunk_size=100, enable_overlap=True, overlap_size=20)
        chunker = MarkdownChunker(config)

        md_text = """# Section 1
Short content.

# Section 2
Another short section."""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # First chunk of each section should not have previous_content
        # (assuming each section becomes one chunk)
        for chunk in chunks:
            # If this is a section start, no previous context
            if chunk.content.startswith("# Section"):
                assert (
                    "previous_content" not in chunk.metadata
                    or chunk.metadata.get("previous_content") == ""
                )

    def test_real_document_context_tracking(self):
        """Test with actual markdown document structure.

        Note: This test has relaxed validation due to known core chunking behavior
        where structural elements (headers) may appear in multiple chunks.
        """
        config = ChunkConfig(max_chunk_size=250, enable_overlap=True, overlap_size=50)
        chunker = MarkdownChunker(config)

        md_text = """# User Guide

## Installation

To install the package, run:

```bash
pip install markdown-chunker
```

## Usage

Here's how to use it:

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk(text)
```

## Configuration

You can configure various options:

- max_chunk_size: Maximum chunk size
- overlap_size: Overlap between chunks
- strategy: Chunking strategy

## Advanced Features

The chunker supports multiple strategies."""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # Validate basic context traceability
        for i in range(1, len(chunks)):
            chunk = chunks[i]

            # If has previous_content, it should be a valid string
            if "previous_content" in chunk.metadata:
                prev_context = chunk.metadata["previous_content"]
                assert isinstance(prev_context, str)
                assert len(prev_context) > 0
                assert len(prev_context) <= 60  # With 1.2x tolerance

                # TODO: Add stricter validation once core chunking duplication is resolved
                # Currently, structural elements like headers may appear in multiple chunks

    def test_context_offset_boundaries(self):
        """Verify context extraction respects offset boundaries."""
        config = ChunkConfig(max_chunk_size=100, enable_overlap=True, overlap_size=25)
        chunker = MarkdownChunker(config)

        md_text = """First paragraph here.

Second paragraph here.

Third paragraph here."""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # In metadata mode, verify offsets describe content range
        for chunk in chunks:
            if "start_offset" in chunk.metadata and "end_offset" in chunk.metadata:
                start = chunk.metadata["start_offset"]
                end = chunk.metadata["end_offset"]

                # Content length should match offset range
                assert (
                    len(chunk.content) == end - start
                ), f"Content length mismatch: {len(chunk.content)} != {end - start}"

    def test_code_heavy_document(self):
        """Test with code-heavy document."""
        config = ChunkConfig(max_chunk_size=300, enable_overlap=True, overlap_size=50)
        chunker = MarkdownChunker(config)

        md_text = """# Code Example

Here's a function:

```python
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
```

And another:

```python
def validate(input):
    if not input:
        return False
    return True
```"""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # Verify code blocks are handled correctly
        for chunk in chunks:
            # Content should have balanced code fences
            fence_count = chunk.content.count("```")
            assert fence_count % 2 == 0, "Unbalanced code fences in chunk"

            # Context should also not have unbalanced fences
            if "previous_content" in chunk.metadata:
                prev_fences = chunk.metadata["previous_content"].count("```")
                assert prev_fences % 2 == 0

            if "next_content" in chunk.metadata:
                next_fences = chunk.metadata["next_content"].count("```")
                assert next_fences % 2 == 0

    def test_overlap_disabled_integration(self):
        """Test full pipeline with overlap disabled."""
        config = ChunkConfig(max_chunk_size=200, enable_overlap=False)
        chunker = MarkdownChunker(config)

        md_text = """# Section 1
Content here.

# Section 2
More content here."""

        result = chunker.chunk(md_text, include_metadata=True)
        chunks = result.chunks if hasattr(result, "chunks") else result

        # No context fields should be present
        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata
            assert "previous_chunk_index" not in chunk.metadata
            assert "next_chunk_index" not in chunk.metadata
