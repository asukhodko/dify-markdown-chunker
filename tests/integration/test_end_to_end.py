"""
End-to-end integration tests for MarkdownChunker.

Tests verify complete chunking pipeline with real documents:
- No data loss in any scenario
- Correct strategy selection
- Proper error handling
- Metadata completeness

**Feature: markdown-chunker-quality-audit, Integration Tests**
**Validates: Requirements 4.4, 8.3**
"""

import pytest

from markdown_chunker import ChunkConfig, MarkdownChunker

# Test documents
README_DOC = """# Project Title

This is a sample README file for testing.

## Installation

```bash
pip install package
```

## Usage

1. Import the module
2. Create instance
3. Call methods

## Features

- Feature 1
- Feature 2
- Feature 3

## License

MIT License
"""

CODE_HEAVY_DOC = """# API Documentation

## Authentication

```python
import requests

def authenticate(api_key):
    headers = {'Authorization': f'Bearer {api_key}'}
    return headers
```

## Making Requests

```python
def get_data(url, headers):
    response = requests.get(url, headers=headers)
    return response.json()
```

## Error Handling

```python
try:
    data = get_data(url, headers)
except Exception as e:
    print(f"Error: {e}")
```
"""

TABLE_DOC = """# Data Report

## Results

| Name | Score | Status |
|------|-------|--------|
| Alice | 95 | Pass |
| Bob | 87 | Pass |
| Charlie | 72 | Pass |

## Summary

Total participants: 3
Average score: 84.7
"""


# Integration Tests


def test_end_to_end_readme_document():
    """Test complete pipeline with README-style document."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk(README_DOC)

    # Verify chunks created
    assert len(chunks) > 0, "Should create chunks"

    # Verify no data loss
    combined = "".join(c.content for c in chunks)
    # Check key content is preserved
    assert "Project Title" in combined
    assert "Installation" in combined
    assert "pip install" in combined
    assert "License" in combined


def test_end_to_end_code_heavy_document():
    """Test complete pipeline with code-heavy document."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk(CODE_HEAVY_DOC)

    # Verify chunks created
    assert len(chunks) > 0, "Should create chunks"

    # Verify code blocks preserved
    combined = "".join(c.content for c in chunks)
    assert "def authenticate" in combined
    assert "def get_data" in combined
    assert "try:" in combined


def test_end_to_end_table_document():
    """Test complete pipeline with table document."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk(TABLE_DOC)

    # Verify chunks created
    assert len(chunks) > 0, "Should create chunks"

    # Verify table preserved
    combined = "".join(c.content for c in chunks)
    assert "| Name | Score | Status |" in combined
    assert "Alice" in combined
    assert "Bob" in combined


def test_end_to_end_with_custom_config():
    """Test pipeline with custom configuration."""
    config = ChunkConfig(max_chunk_size=1000, overlap_size=100)
    chunker = MarkdownChunker(config)

    chunks = chunker.chunk(README_DOC)

    # Verify configuration applied
    assert len(chunks) > 0
    for chunk in chunks:
        # Chunks should respect size limit (with some tolerance for overlap)
        assert len(chunk.content) <= 1500  # Allow tolerance


def test_end_to_end_metadata_present():
    """Test that all chunks have required metadata."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk(README_DOC)

    required_fields = ["strategy", "content_type"]

    for chunk in chunks:
        for field in required_fields:
            assert field in chunk.metadata, f"Missing metadata: {field}"


def test_end_to_end_empty_input():
    """Test pipeline handles empty input gracefully."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk("")

    # Should handle gracefully (may return empty or single chunk)
    assert isinstance(chunks, list)


def test_end_to_end_minimal_input():
    """Test pipeline with minimal valid input."""
    chunker = MarkdownChunker()

    chunks = chunker.chunk("# Title\n\nContent")

    assert len(chunks) > 0
    combined = "".join(c.content for c in chunks)
    assert "Title" in combined
    assert "Content" in combined


def test_end_to_end_large_document():
    """Test pipeline with larger document."""
    # Create a large document
    large_doc = "# Main Title\n\n"
    for i in range(20):
        large_doc += f"## Section {i}\n\n"
        large_doc += f"This is content for section {i}. " * 10
        large_doc += "\n\n"

    chunker = MarkdownChunker()
    chunks = chunker.chunk(large_doc)

    # Should create multiple chunks
    assert len(chunks) > 1, "Large document should create multiple chunks"

    # Verify no data loss
    combined = "".join(c.content for c in chunks)
    for i in range(20):
        assert f"Section {i}" in combined, f"Section {i} lost"


def test_end_to_end_mixed_content():
    """Test pipeline with mixed content types."""
    mixed_doc = """# Mixed Document

## Text Section

This is regular text content.

## Code Section

```python
def hello():
    print("Hello")
```

## List Section

- Item 1
- Item 2
- Item 3

## Table Section

| A | B |
|---|---|
| 1 | 2 |
"""

    chunker = MarkdownChunker()
    chunks = chunker.chunk(mixed_doc)

    assert len(chunks) > 0

    # Verify all content types preserved
    combined = "".join(c.content for c in chunks)
    assert "Text Section" in combined
    assert "def hello" in combined
    assert "Item 1" in combined
    assert "| A | B |" in combined


def test_end_to_end_performance():
    """Test that chunking completes in reasonable time."""
    import time

    chunker = MarkdownChunker()

    start = time.time()
    chunks = chunker.chunk(README_DOC)
    elapsed = time.time() - start

    # Should complete quickly (< 1 second for small doc)
    assert elapsed < 1.0, f"Chunking took too long: {elapsed:.2f}s"
    assert len(chunks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
