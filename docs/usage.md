# Usage Guide

Comprehensive guide for using Dify Markdown Chunker in different scenarios.

## 🎯 Using in Dify Workflows

### Basic Workflow Setup

1. Create or open a workflow in Dify
2. Add a "Tool" node
3. Select "Advanced Markdown Chunker"
4. Configure parameters:
   - **max_chunk_size**: 2048 (recommended for RAG)
   - **strategy**: auto (automatic selection)
   - **enable_overlap**: false

### Example Workflow

```yaml
workflow:
  - node: document_loader
    type: document_loader
    config:
      source: file_upload
  
  - node: markdown_chunker
    type: tool
    tool: advanced_markdown_chunker
    config:
      max_chunk_size: 2048
      strategy: auto
      enable_overlap: true
      overlap_size: 100
  
  - node: embedding
    type: embedding
    input: ${markdown_chunker.output}
```

## 🐍 Using as Python Library

### Basic Usage

```python
from markdown_chunker import MarkdownChunker

# Create chunker
chunker = MarkdownChunker()

# Chunk markdown
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

# Access chunks
for chunk in result.chunks:
    print(f"Chunk: {chunk.content[:50]}...")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Size: {chunk.size} chars")
```

### With Configuration

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Create custom config
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100
)

# Use config
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)
```

### Configuration Profiles

```python
from markdown_chunker import ChunkConfig

# For API documentation
config = ChunkConfig.for_api_docs()

# For code documentation
config = ChunkConfig.for_code_docs()

# For RAG systems (Dify default)
config = ChunkConfig.for_dify_rag()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

## 📚 Common Use Cases

### Use Case 1: RAG System

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Configure for RAG
config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

# Process documentation
with open("docs/api.md") as f:
    markdown = f.read()

result = chunker.chunk(markdown, include_analysis=True)

# Store chunks in vector database
for chunk in result.chunks:
    vector_db.add(
        content=chunk.content,
        metadata={
            "start_line": chunk.start_line,
            "end_line": chunk.end_line,
            "strategy": chunk.strategy
        }
    )
```

### Use Case 2: Code Documentation

```python
from markdown_chunker import ChunkConfig

# Configure for code-heavy docs
config = ChunkConfig.for_code_docs()
chunker = MarkdownChunker(config)

# Process code documentation
result = chunker.chunk(code_docs, include_analysis=True)

# Code blocks are preserved
print(f"Strategy used: {result.strategy_used}")
print(f"Code ratio: {result.analysis.code_ratio:.2%}")
```

### Use Case 3: API Reference

```python
# Configure for API docs
config = ChunkConfig.for_api_docs()
chunker = MarkdownChunker(config)

# Process API documentation
result = chunker.chunk(api_docs, include_analysis=True)

# Sections are preserved
for chunk in result.chunks:
    if chunk.metadata.get("has_header"):
        print(f"Section: {chunk.metadata['header_text']}")
```

## 🔧 Advanced Features

### Content Analysis

```python
result = chunker.chunk(markdown, include_analysis=True)

# Access analysis
analysis = result.analysis
print(f"Content type: {analysis.content_type}")
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Complexity: {analysis.complexity_score:.2f}")
print(f"Header count: {analysis.header_count}")
print(f"Code block count: {analysis.code_block_count}")
```

### Preamble Extraction

```python
from markdown_chunker import extract_preamble

markdown_with_frontmatter = """---
title: My Document
author: John Doe
---

# Content
"""

preamble = extract_preamble(markdown_with_frontmatter)
if preamble:
    print(f"Type: {preamble.type}")
    print(f"Content: {preamble.content}")
```

### Convenience Functions

```python
from markdown_chunker import chunk_text, chunk_file

# Chunk text directly
chunks = chunk_text("# Hello\n\nWorld")

# Chunk from file
chunks = chunk_file("README.md")

# With config
config = ChunkConfig.for_code_docs()
chunks = chunk_file("docs/api.md", config)
```

## 📊 Strategy Selection

The chunker automatically selects the best strategy:

- **Code Strategy**: >30% code content
- **Mixed Strategy**: Balanced code and text
- **List Strategy**: >40% list content
- **Table Strategy**: >30% table content
- **Structural Strategy**: Well-structured with headers
- **Sentences Strategy**: Simple text fallback

Force a specific strategy:

```python
config = ChunkConfig(force_strategy="code")
chunker = MarkdownChunker(config)
```

## 🆘 Troubleshooting

See [Troubleshooting Guide](guides/troubleshooting.md) for common issues and solutions.

## 📚 Next Steps

- Review [API Reference](api/README.md)
- Learn about [Chunking Strategies](architecture/strategies.md)
- Check [Configuration Options](reference/configuration.md)
