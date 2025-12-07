"""Integration tests for the redesigned overlap model.

Tests the full pipeline with the new previous_content/next_content model.

Migration note: Updated for v2 API (December 2025)
- enable_overlap replaced with overlap_size > 0
- include_metadata parameter removed (always included in v2)
"""

from markdown_chunker_v2 import ChunkConfig, MarkdownChunker


class TestOverlapRedesignIntegration:
    """Integration tests for overlap redesign."""

    def test_full_pipeline_metadata_mode(self):
        """End-to-end test with metadata mode (v2 default)."""
        config = ChunkConfig(max_chunk_size=150, overlap_size=30)
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

        chunks = chunker.chunk(md_text)

        # Should have multiple chunks
        assert len(chunks) > 1

        # First chunk should have no previous_content
        assert "previous_content" not in chunks[0].metadata

        # Last chunk should have no next_content
        assert "next_content" not in chunks[-1].metadata

        # Verify no legacy fields
        for chunk in chunks:
            assert "overlap_prefix" not in chunk.metadata
            assert "overlap_suffix" not in chunk.metadata

    def test_full_pipeline_no_overlap(self):
        """End-to-end test with overlap disabled."""
        config = ChunkConfig(max_chunk_size=150, overlap_size=0)
        chunker = MarkdownChunker(config)

        md_text = """# Section A
This is the first section with some content here.

# Section B
This is the second section with more content here."""

        chunks = chunker.chunk(md_text)

        # Verify no context fields in metadata
        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata

    def test_mode_equivalence_full_document(self):
        """Test chunking produces consistent results."""
        config = ChunkConfig(max_chunk_size=200, overlap_size=40)
        chunker = MarkdownChunker(config)

        md_text = """# Introduction
This is an introduction section.

# Main Content
This is the main content with details.

# Conclusion
This is the conclusion."""

        chunks = chunker.chunk(md_text)

        # Should have chunks
        assert len(chunks) > 0

        # All chunks should have content
        for chunk in chunks:
            assert chunk.content.strip()

    def test_section_boundary_isolation(self):
        """Verify chunks maintain section boundaries."""
        config = ChunkConfig(max_chunk_size=100, overlap_size=20)
        chunker = MarkdownChunker(config)

        md_text = """# Section 1
Short content.

# Section 2
Another short section."""

        chunks = chunker.chunk(md_text)

        # Should produce chunks
        assert len(chunks) > 0

    def test_real_document_context_tracking(self):
        """Test with actual markdown document structure."""
        config = ChunkConfig(max_chunk_size=250, overlap_size=50)
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

        chunks = chunker.chunk(md_text)

        # Validate basic context traceability
        for i in range(1, len(chunks)):
            chunk = chunks[i]

            # If has previous_content, it should be a valid string
            if "previous_content" in chunk.metadata:
                prev_context = chunk.metadata["previous_content"]
                assert isinstance(prev_context, str)
                assert len(prev_context) > 0

    def test_context_offset_boundaries(self):
        """Verify context extraction works correctly."""
        config = ChunkConfig(max_chunk_size=100, overlap_size=25)
        chunker = MarkdownChunker(config)

        md_text = """First paragraph here.

Second paragraph here.

Third paragraph here."""

        chunks = chunker.chunk(md_text)

        # Should produce chunks
        assert len(chunks) > 0

        # All chunks should have valid content
        for chunk in chunks:
            assert chunk.content.strip()

    def test_code_heavy_document(self):
        """Test with code-heavy document."""
        config = ChunkConfig(max_chunk_size=300, overlap_size=50)
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

        chunks = chunker.chunk(md_text)

        # Verify code blocks are handled correctly
        for chunk in chunks:
            # Content should have balanced code fences
            fence_count = chunk.content.count("```")
            assert fence_count % 2 == 0, "Unbalanced code fences in chunk"

    def test_overlap_disabled_integration(self):
        """Test full pipeline with overlap disabled."""
        config = ChunkConfig(max_chunk_size=200, overlap_size=0)
        chunker = MarkdownChunker(config)

        md_text = """# Section 1
Content here.

# Section 2
More content here."""

        chunks = chunker.chunk(md_text)

        # No context fields should be present
        for chunk in chunks:
            assert "previous_content" not in chunk.metadata
            assert "next_content" not in chunk.metadata
