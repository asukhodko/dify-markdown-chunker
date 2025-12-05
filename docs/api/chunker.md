# MarkdownChunker API

Complete API documentation for the MarkdownChunker class (v2.0).

## Overview

`MarkdownChunker` is the main class for chunking markdown documents with intelligent strategy selection.

## Class: MarkdownChunker

### Import

```python
from markdown_chunker_v2 import MarkdownChunker
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
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

# With default config
chunker = MarkdownChunker()

# With custom config
config = ChunkConfig(max_chunk_size=2048, overlap_size=100)
chunker = MarkdownChunker(config)
```

### Methods

#### chunk()

```python
chunk(text: str) -> List[Chunk]
```

Chunk markdown text into smaller pieces.

**Parameters:**
- `text` (str): Markdown content to chunk. Must be valid UTF-8 text.

**Returns:**
- `List[Chunk]`: List of generated chunks

**Example:**
```python
chunks = chunker.chunk("# Hello\n\nWorld")

for chunk in chunks:
    print(f"Content: {chunk.content}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Size: {len(chunk.content)} chars")
    print(f"Strategy: {chunk.metadata.get('strategy')}")
```

#### chunk_with_metrics()

```python
chunk_with_metrics(text: str) -> ChunkingResult
```

Chunk markdown text and return detailed metrics.

**Parameters:**
- `text` (str): Markdown content to chunk.

**Returns:**
- `ChunkingResult`: Object containing chunks, metrics, and analysis

**Example:**
```python
result = chunker.chunk_with_metrics(markdown_text)

print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
print(f"Processing time: {result.metrics.processing_time_ms}ms")
```

## Chunk

Individual chunk object.

**Attributes:**
- `content` (str): Chunk text content
- `start_line` (int): Starting line number (1-based)
- `end_line` (int): Ending line number
- `metadata` (dict): Additional metadata

**Metadata fields:**
- `strategy` (str): Strategy used for this chunk
- `content_type` (str): Content type (text, code, table, mixed)
- `header_path` (str): Hierarchical header path
- `chunk_index` (int): Index in chunk sequence
- `previous_content` (str, optional): Overlap from previous chunk
- `next_content` (str, optional): Overlap to next chunk
- `allow_oversize` (bool): True if chunk exceeds max_chunk_size intentionally
- `oversize_reason` (str, optional): Reason for oversize

**Example:**
```python
for chunk in chunks:
    print(f"Content: {chunk.content[:50]}...")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Type: {chunk.metadata.get('content_type')}")
    print(f"Strategy: {chunk.metadata.get('strategy')}")
```

## ChunkingResult

Result object returned by `chunk_with_metrics()`.

**Attributes:**
- `chunks` (List[Chunk]): List of generated chunks
- `strategy_used` (str): Name of strategy that was used
- `metrics` (ChunkingMetrics): Processing metrics
- `analysis` (ContentAnalysis): Content analysis

## ContentAnalysis

Content analysis results.

**Attributes:**
- `code_ratio` (float): Ratio of code content (0.0-1.0)
- `header_count` (int): Number of headers
- `code_block_count` (int): Number of code blocks
- `table_count` (int): Number of tables
- `total_lines` (int): Total line count
- `total_chars` (int): Total character count

## Convenience Functions

### chunk_text()

```python
from markdown_chunker_v2 import chunk_text

chunks = chunk_text("# Hello\n\nWorld")
```

### chunk_file()

```python
from markdown_chunker_v2 import chunk_file

chunks = chunk_file("README.md")
```

## Usage Examples

### Basic Chunking

```python
from markdown_chunker_v2 import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk("# Title\n\nContent here")

for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}: {len(chunk.content)} chars")
```

### With Metrics

```python
result = chunker.chunk_with_metrics(markdown_text)

print(f"Strategy: {result.strategy_used}")
print(f"Code ratio: {result.analysis.code_ratio:.2%}")
print(f"Headers: {result.analysis.header_count}")
```

### With Custom Configuration

```python
from markdown_chunker_v2 import ChunkConfig

config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    overlap_size=100
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown_text)
```

### Processing Files

```python
from markdown_chunker_v2 import chunk_file

chunks = chunk_file("README.md")
print(f"Created {len(chunks)} chunks")
```

### Force Strategy

```python
config = ChunkConfig(strategy_override="structural")
chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown_text)
```

## See Also

- [ChunkConfig API](config.md) - Configuration options
- [Data Types](types.md) - Type definitions
- [Chunking Strategies](../architecture/strategies.md) - Strategy details
