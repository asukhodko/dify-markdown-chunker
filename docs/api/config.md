# ChunkConfig API

Complete API documentation for the ChunkConfig class.

## Overview

`ChunkConfig` controls chunking behavior and strategy selection.

## Class: ChunkConfig

### Import

```python
from markdown_chunker import ChunkConfig
```

### Constructor

```python
ChunkConfig(
    max_chunk_size: int = 2048,
    min_chunk_size: int = 256,
    enable_overlap: bool = False,
    overlap_size: int = 100,
    force_strategy: Optional[str] = None
)
```

**Parameters:**
- `max_chunk_size` (int): Maximum chunk size in characters. Default: 2048
- `min_chunk_size` (int): Minimum chunk size in characters. Default: 256
- `enable_overlap` (bool): Enable chunk overlap. Default: False
- `overlap_size` (int): Overlap size in characters. Default: 100
- `force_strategy` (str, optional): Force specific strategy. Options: "code", "mixed", "list", "table", "structural", "sentences", or None for auto

**Example:**
```python
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100
)
```

## Configuration Profiles

Pre-configured profiles for common use cases.

### for_api_docs()

```python
ChunkConfig.for_api_docs() -> ChunkConfig
```

Optimized for API documentation.

**Settings:**
- max_chunk_size: 1500
- Preserves code blocks
- Maintains section structure

**Example:**
```python
config = ChunkConfig.for_api_docs()
chunker = MarkdownChunker(config)
```

### for_code_docs()

```python
ChunkConfig.for_code_docs() -> ChunkConfig
```

Optimized for code-heavy documentation.

**Settings:**
- max_chunk_size: 2000
- Preserves code blocks
- Handles mixed content

**Example:**
```python
config = ChunkConfig.for_code_docs()
```

### for_dify_rag()

```python
ChunkConfig.for_dify_rag() -> ChunkConfig
```

Optimized for RAG systems (Dify default).

**Settings:**
- max_chunk_size: 2048
- Balanced chunking
- Overlap enabled

**Example:**
```python
config = ChunkConfig.for_dify_rag()
```

### for_search_indexing()

```python
ChunkConfig.for_search_indexing() -> ChunkConfig
```

Optimized for search indexing.

**Settings:**
- max_chunk_size: 1200
- Smaller chunks
- No overlap

**Example:**
```python
config = ChunkConfig.for_search_indexing()
```

## Usage Examples

### Basic Configuration

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2048)
chunker = MarkdownChunker(config)
```

### With Overlap

```python
config = ChunkConfig(
    max_chunk_size=2048,
    enable_overlap=True,
    overlap_size=100
)
```

### Force Strategy

```python
# Force code strategy
config = ChunkConfig(force_strategy="code")

# Force structural strategy
config = ChunkConfig(force_strategy="structural")
```

### Using Profiles

```python
# For API documentation
config = ChunkConfig.for_api_docs()

# For code documentation
config = ChunkConfig.for_code_docs()

# For RAG systems
config = ChunkConfig.for_dify_rag()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

## Configuration Parameters

### max_chunk_size

Maximum size of generated chunks in characters.

- **Type**: int
- **Default**: 2048
- **Range**: 100-10000 recommended
- **Impact**: Larger chunks = fewer chunks, more context per chunk

### min_chunk_size

Minimum size of generated chunks in characters.

- **Type**: int
- **Default**: 256
- **Range**: 50-1000 recommended
- **Impact**: Prevents very small chunks

### enable_overlap

Enable overlapping content between chunks.

- **Type**: bool
- **Default**: False
- **Impact**: Improves context continuity, increases total size

### overlap_size

Size of overlap between chunks in characters.

- **Type**: int
- **Default**: 100
- **Range**: 50-500 recommended
- **Impact**: Only used if enable_overlap=True

### force_strategy

Force a specific chunking strategy.

- **Type**: str or None
- **Default**: None (automatic selection)
- **Options**: "code", "mixed", "list", "table", "structural", "sentences"
- **Impact**: Overrides automatic strategy selection

## See Also

- [MarkdownChunker API](chunker.md) - Main chunking class
- [Chunking Strategies](../architecture/strategies.md) - Strategy details
- [API Overview](README.md) - Complete API reference
