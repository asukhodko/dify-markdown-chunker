"""
Tests for preamble chunking integration in MarkdownChunker.

Tests the full integration of preamble extraction and processing
in the chunking pipeline.
"""

from markdown_chunker.chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestPreambleChunking:
    """Test preamble chunking in MarkdownChunker."""

    def test_preamble_added_to_first_chunk_metadata(self):
        """Test that preamble is added to first chunk metadata by default."""
        text = """Author: John Doe
Date: 2025-11-16
Version: 1.0

# Introduction

This is the main content of the document.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert chunks[0].get_metadata("has_preamble") is True
        assert "preamble" in chunks[0].metadata
        assert chunks[0].get_metadata("preamble_type") == "metadata"

    def test_separate_preamble_chunk(self):
        """Test creating separate chunk for preamble."""
        text = """Summary: This document explains the API.
Author: Development Team

# API Documentation

## Overview

Content here.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 2
        # First chunk should be preamble
        assert chunks[0].get_metadata("is_preamble_chunk") is True
        assert chunks[0].get_metadata("content_type") == "preamble"
        assert "Summary:" in chunks[0].content or "Author:" in chunks[0].content

    def test_no_preamble_no_metadata(self):
        """Test that documents without preamble don't get preamble metadata."""
        text = """# Title

Content starts immediately with header.

More content here.
"""

        config = ChunkConfig(extract_preamble=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert chunks[0].get_metadata("has_preamble") is None

    def test_preamble_extraction_disabled(self):
        """Test that preamble extraction can be disabled."""
        text = """Author: John Doe
Date: 2025-11-16

# Title

Content.
"""

        config = ChunkConfig(extract_preamble=False)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        assert chunks[0].get_metadata("has_preamble") is None
        assert "preamble" not in chunks[0].metadata

    def test_preamble_with_metadata_fields(self):
        """Test that metadata fields are extracted correctly."""
        text = """Title: Test Document
Author: John Doe
Date: 2025-11-16
Version: 1.0.0
Status: Draft

# Main Content

Document body.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0
        preamble_data = chunks[0].get_metadata("preamble")
        assert preamble_data is not None
        assert "metadata_fields" in preamble_data
        assert "author" in preamble_data["metadata_fields"]
        assert preamble_data["metadata_fields"]["author"] == "John Doe"

    def test_preamble_type_in_chunk_metadata(self):
        """Test that preamble type is correctly identified."""
        # Test introduction type
        text1 = """This is an introduction to the document.
It provides context and overview.

# Chapter 1

Content.
"""

        config = ChunkConfig(extract_preamble=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text1)

        assert len(chunks) > 0
        assert chunks[0].get_metadata("preamble_type") == "introduction"

    def test_preamble_chunk_type(self):
        """Test that separate preamble chunk has correct content_type."""
        text = """Author: Test
Date: 2025

# Title

Content.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 2
        assert chunks[0].content_type == "preamble"

    def test_preamble_line_numbers(self):
        """Test that preamble chunk has correct line numbers."""
        text = """Author: John Doe
Date: 2025-11-16
Version: 1.0

# Title

Content starts here.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        assert len(chunks) >= 2
        # Preamble should start at line 1
        assert chunks[0].start_line == 1
        # Preamble should end before the header
        assert chunks[0].end_line < 5

    def test_preamble_integration_with_strategies(self):
        """Test that preamble works with different strategies."""
        text = """Summary: Code-heavy document

# Code Examples

```python
def hello():
    print("Hello")
```

```python
def world():
    print("World")
```

```python
def test():
    pass
```
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)
        result = chunker.chunk(text, include_analysis=True)

        # Strategy is auto-selected based on content
        assert result.strategy_used in ["code", "structural", "sentences"]
        # First chunk should have preamble metadata
        assert result.chunks[0].get_metadata("has_preamble") is True

    def test_preamble_edge_cases(self):
        """Test preamble with edge cases."""
        # Very short preamble (should be ignored)
        text1 = """Hi

# Title

Content.
"""

        config = ChunkConfig(extract_preamble=True)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text1)

        # Short preamble should be ignored
        assert chunks[0].get_metadata("has_preamble") is None

    def test_preamble_with_full_analysis(self):
        """Test preamble with full analysis result."""
        text = """Author: Test Author
Summary: Test document

# Title

Content here.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=True)
        chunker = MarkdownChunker(config)
        result = chunker.chunk(text, include_analysis=True)

        assert result.success
        assert len(result.chunks) >= 2
        assert result.chunks[0].get_metadata("is_preamble_chunk") is True

    def test_preamble_with_dict_format(self):
        """Test preamble with dictionary return format."""
        text = """Author: John
Date: 2025

# Title

Content.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)
        result = chunker.chunk(text, return_format="dict")

        assert "chunks" in result
        assert len(result["chunks"]) > 0
        assert result["chunks"][0]["metadata"].get("has_preamble") is True

    def test_preamble_preserved_in_overlap(self):
        """Test that preamble metadata is preserved when overlap is enabled."""
        text = """Author: Test

# Section 1

Content for section 1.

# Section 2

Content for section 2.
"""

        config = ChunkConfig(
            extract_preamble=True,
            separate_preamble_chunk=False,
            enable_overlap=True,
            max_chunk_size=100,
        )
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text)

        # First chunk should have preamble
        assert chunks[0].get_metadata("has_preamble") is True

    def test_preamble_with_manual_strategy(self):
        """Test preamble with manually specified strategy."""
        text = """Summary: Structural document

# Section 1

Content.

# Section 2

More content.
"""

        config = ChunkConfig(extract_preamble=True, separate_preamble_chunk=False)
        chunker = MarkdownChunker(config)
        chunks = chunker.chunk(text, strategy="structural")

        assert len(chunks) > 0
        assert chunks[0].get_metadata("has_preamble") is True
        assert chunks[0].get_metadata("strategy") == "structural"
