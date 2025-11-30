# MarkdownChunker API

Complete API documentation for the MarkdownChunker class.

## Overview

`MarkdownChunker` is the main class for chunking markdown documents with intelligent strategy selection.

## Class: MarkdownChunker

### Import

```python
from markdown_chunker import MarkdownChunker
```

### Constructor

```python
MarkdownChunker(config: ChunkConfig = None)
```

Creates a new MarkdownChunker instance.

**Parameters:**
- `config` (ChunkConfig, optional): Configuration for chunking behavior. If None, uses default configuration.

**Example:**
```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# With default config
chunker = MarkdownChunker()

# With custom config
config = ChunkConfig(max_chunk_size=2048, enable_overlap=True)
chunker = MarkdownChunker(config)
```

### Methods

#### chunk()

```python
chunk(text: str, include_analysis: bool = False) -> ChunkingResult
```

Chunk markdown text into smaller pieces.

**Parameters:**
- `text` (str): Markdown content to chunk. Must be valid UTF-8 text.
- `include_analysis` (bool, optional): Include content analysis in result. Default: False.

**Returns:**
- `ChunkingResult`: Object containing chunks and metadata

**Example:**
```python
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

# Access chunks
for chunk in result.chunks:
    print(f"Content: {chunk.content}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Size: {chunk.size} chars")

# Access metadata
print(f"Strategy used: {result.strategy_used}")
print(f"Total chunks: {len(result.chunks)}")

# Access analysis (if include_analysis=True)
if result.analysis:
    print(f"Content type: {result.analysis.content_type}")
    print(f"Code ratio: {result.analysis.code_ratio:.2%}")
```

## ChunkingResult

Result object returned by `chunk()` method.

**Attributes:**
- `chunks` (List[Chunk]): List of generated chunks
- `strategy_used` (str): Name of strategy that was used
- `analysis` (ContentAnalysis, optional): Content analysis if requested

## Chunk

Individual chunk object.

**Attributes:**
- `content` (str): Chunk text content
- `start_line` (int): Starting line number in original document
- `end_line` (int): Ending line number in original document
- `size` (int): Size in characters
- `strategy` (str): Strategy used for this chunk
- `metadata` (dict): Additional metadata

## Usage Examples

### Basic Chunking

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk("# Title\n\nContent here")

for i, chunk in enumerate(result.chunks, 1):
    print(f"Chunk {i}: {chunk.size} chars")
```

### With Analysis

```python
result = chunker.chunk(markdown_text, include_analysis=True)

print(f"Strategy: {result.strategy_used}")
print(f"Content type: {result.analysis.content_type}")
print(f"Complexity: {result.analysis.complexity_score:.2f}")
```

### With Custom Configuration

```python
from markdown_chunker import ChunkConfig

config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100
)

chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text)
```

### Processing Files

```python
with open("README.md") as f:
    markdown = f.read()

result = chunker.chunk(markdown, include_analysis=True)
print(f"Created {len(result.chunks)} chunks")
```

## See Also

- [ChunkConfig API](config.md) - Configuration options
- [Data Types](types.md) - Type definitions
- [API Overview](README.md) - Complete API reference
