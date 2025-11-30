"""
Basic usage examples for Python Markdown Chunker.

This script demonstrates the most common use cases for the chunker.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_chunker import MarkdownChunker, ChunkConfig, chunk_text, chunk_file


def example_1_simple_chunking():
    """Example 1: Simple chunking with default configuration."""
    print("=" * 60)
    print("Example 1: Simple Chunking")
    print("=" * 60)

    markdown="""# My Document

This is an introduction paragraph with some text content.

## Section 1

Here's some content in section 1.

```python
def hello():
    return "world"
```

## Section 2

More content in section 2.
"""

    chunker=MarkdownChunker()
    chunks=chunker.chunk(markdown)

    print(f"\nGenerated {len(chunks)} chunks:\n")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}:")
        print(f"  Lines: {chunk.start_line}-{chunk.end_line}")
        print(f"  Size: {chunk.size} chars")
        print(f"  Preview: {chunk.content[:50]}...")
        print()


def example_2_with_analysis():
    """Example 2: Chunking with detailed analysis."""
    print("=" * 60)
    print("Example 2: Chunking with Analysis")
    print("=" * 60)

    markdown="""# Code Tutorial

Learn Python basics.

```python
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
```

```python
class Person:
    def __init__(self, name):
        self.name=name
```
"""

    chunker=MarkdownChunker()
    result=chunker.chunk_with_analysis(markdown)

    print(f"\nStrategy used: {result.strategy_used}")
    print(f"Content type: {result.content_type}")
    print(f"Processing time: {result.processing_time:.3f}s")
    print(f"Complexity score: {result.complexity_score:.2f}")
    print(f"Total chunks: {len(result.chunks)}")

    if result.fallback_used:
        print(f"⚠️  Fallback used at level {result.fallback_level}")

    print("\nChunks:")
    for i, chunk in enumerate(result.chunks):
        print(f"\nChunk {i}:")
        print(f"  Content: {chunk.content[:80]}...")
        print(f"  Metadata: {chunk.metadata}")


def example_3_custom_configuration():
    """Example 3: Custom configuration."""
    print("=" * 60)
    print("Example 3: Custom Configuration")
    print("=" * 60)

    markdown="""# Documentation

This is a long document that needs to be chunked with specific settings.

## Section 1

Content for section 1 with multiple paragraphs.

This is another paragraph in section 1.

## Section 2

Content for section 2.
"""

    # Custom configuration
    config=ChunkConfig(
        max_chunk_size=200,      # Smaller chunks
        min_chunk_size=50,
        enable_overlap=True,     # Enable overlap
        overlap_size=30
    )

    chunker=MarkdownChunker(config)
    result=chunker.chunk_with_analysis(markdown)

    print(f"\nConfiguration:")
    print(f"  Max chunk size: {config.max_chunk_size}")
    print(f"  Min chunk size: {config.min_chunk_size}")
    print(f"  Overlap enabled: {config.enable_overlap}")
    print(f"  Overlap size: {config.overlap_size}")

    print(f"\nGenerated {len(result.chunks)} chunks:")
    for i, chunk in enumerate(result.chunks):
        has_overlap=chunk.metadata.get('has_overlap', False)
        overlap_marker=" [OVERLAP]" if has_overlap else ""
        print(f"  Chunk {i}: {chunk.size} chars{overlap_marker}")


def example_4_strategy_override():
    """Example 4: Manual strategy override."""
    print("=" * 60)
    print("Example 4: Strategy Override")
    print("=" * 60)

    markdown="""# Mixed Content

Some text here.

```python
def test():
    pass
```

- List item 1
- List item 2
"""

    chunker=MarkdownChunker()

    # Try different strategies
    strategies=["structural", "code", "list"]

    for strategy in strategies:
        chunks=chunker.chunk(markdown, strategy=strategy)
        print(f"\nUsing {strategy} strategy: {len(chunks)} chunks")


def example_5_code_heavy_document():
    """Example 5: Code-heavy document with configuration profile."""
    print("=" * 60)
    print("Example 5: Code-Heavy Document")
    print("=" * 60)

    markdown="""# API Reference

```python
class UserAPI:
    def get_user(self, user_id):
        return self.db.query(user_id)

    def create_user(self, data):
        return self.db.insert(data)

    def update_user(self, user_id, data):
        return self.db.update(user_id, data)
```

```python
class OrderAPI:
    def get_order(self, order_id):
        return self.db.query(order_id)

    def create_order(self, data):
        return self.db.insert(data)
```

```javascript
function processOrder(order) {
    return api.post('/orders', order);
}
```
"""

    # Use code documentation profile
    config=ChunkConfig.for_code_docs()
    chunker=MarkdownChunker(config)

    result=chunker.chunk_with_analysis(markdown)

    print(f"\nStrategy: {result.strategy_used}")
    print(f"Chunks: {len(result.chunks)}")

    print("\nCode blocks found:")
    for i, chunk in enumerate(result.chunks):
        if 'language' in chunk.metadata:
            lang=chunk.metadata['language']
            print(f"  - {lang} code block in chunk {i}")


def example_6_list_heavy_document():
    """Example 6: List-heavy document."""
    print("=" * 60)
    print("Example 6: List-Heavy Document")
    print("=" * 60)

    markdown="""# Project Tasks

## Development Phase
- Set up environment
  - Install Python
  - Create virtualenv
  - Install dependencies
- Write code
  - Implement features
  - Add tests
  - Write documentation
- Review and test
  - Code review
  - Integration tests
  - User acceptance testing

## Deployment Phase
- Prepare deployment
  - Build artifacts
  - Configure servers
  - Set up monitoring
- Deploy to production
  - Deploy application
  - Verify deployment
  - Monitor metrics
"""

    chunker=MarkdownChunker()
    result=chunker.chunk_with_analysis(markdown)

    print(f"\nStrategy: {result.strategy_used}")
    print(f"Chunks: {len(result.chunks)}")

    print("\nList information:")
    for i, chunk in enumerate(result.chunks):
        if 'list_type' in chunk.metadata:
            list_type=chunk.metadata['list_type']
            item_count=chunk.metadata.get('list_item_count', 0)
            print(f"  Chunk {i}: {list_type} list with {item_count} items")


def example_7_table_document():
    """Example 7: Table-heavy document."""
    print("=" * 60)
    print("Example 7: Table Document")
    print("=" * 60)

    markdown="""# Data Report

## User Statistics

| Name | Age | City | Status |
|------|-----|------|--------|
| Alice | 30 | NYC | Active |
| Bob | 25 | LA | Active |
| Carol | 35 | Chicago | Inactive |
| Dave | 28 | Boston | Active |
| Eve | 32 | Seattle | Active |

## Sales Data

| Product | Q1 | Q2 | Q3 | Q4 |
|---------|----|----|----|----|
| Widget A | 100 | 120 | 150 | 180 |
| Widget B | 80 | 90 | 100 | 110 |
| Widget C | 60 | 70 | 80 | 90 |
"""

    chunker=MarkdownChunker()
    result=chunker.chunk_with_analysis(markdown)

    print(f"\nStrategy: {result.strategy_used}")
    print(f"Chunks: {len(result.chunks)}")

    print("\nTable information:")
    for i, chunk in enumerate(result.chunks):
        if 'column_count' in chunk.metadata:
            cols=chunk.metadata['column_count']
            rows=chunk.metadata.get('row_count', 0)
            print(f"  Chunk {i}: {cols} columns × {rows} rows")


def example_8_convenience_functions():
    """Example 8: Using convenience functions."""
    print("=" * 60)
    print("Example 8: Convenience Functions")
    print("=" * 60)

    markdown="""# Quick Example

This is a quick example using convenience functions.

## Section 1

Content here.
"""

    # Use convenience function
    chunks=chunk_text(markdown)

    print(f"\nUsing chunk_text():")
    print(f"  Generated {len(chunks)} chunks")

    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {chunk.size} chars")

    # With custom config
    config=ChunkConfig(max_chunk_size=200)
    chunks=chunk_text(markdown, config)

    print(f"\nWith custom config:")
    print(f"  Generated {len(chunks)} chunks")


def main():
    """Run all examples."""
    examples=[
        example_1_simple_chunking,
        example_2_with_analysis,
        example_3_custom_configuration,
        example_4_strategy_override,
        example_5_code_heavy_document,
        example_6_list_heavy_document,
        example_7_table_document,
        example_8_convenience_functions,
    ]

    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()


if __name__ == "__main__":
    main()
