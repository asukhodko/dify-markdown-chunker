# Streaming API Reference

## Overview

The Streaming API enables memory-efficient processing of large Markdown files (>10MB) through buffer-based chunking. This API maintains chunk quality while keeping memory usage below configured limits, making it suitable for resource-constrained environments and large documentation processing.

**Key Benefits:**
- Process files >10MB with <50MB RAM usage
- Configurable buffer management (100KB default window)
- Progress tracking for long-running operations
- Maintains quality through smart window boundary detection

---

## StreamingConfig

Configuration for streaming chunking operations.

### Definition

```python
from dataclasses import dataclass

@dataclass
class StreamingConfig:
    buffer_size: int = 100_000
    overlap_lines: int = 20
    max_memory_mb: int = 100
    safe_split_threshold: float = 0.8
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `buffer_size` | int | 100,000 | Size of buffer window in characters (100KB) |
| `overlap_lines` | int | 20 | Context lines preserved between buffer windows |
| `max_memory_mb` | int | 100 | Maximum memory usage ceiling in megabytes |
| `safe_split_threshold` | float | 0.8 | Where to look for split points (80% of buffer) |

### Usage Example

```python
from markdown_chunker import StreamingConfig

# Default configuration
config = StreamingConfig()

# Memory-constrained environment
config = StreamingConfig(
    buffer_size=50_000,   # 50KB windows
    max_memory_mb=50      # Strict 50MB limit
)

# Large file optimized
config = StreamingConfig(
    buffer_size=200_000,  # 200KB windows for fewer window transitions
    overlap_lines=30      # More context between windows
)
```

---

## chunk_file_streaming()

Stream chunks from a file with memory-efficient processing.

### Signature

```python
def chunk_file_streaming(
    self,
    file_path: str,
    streaming_config: Optional[StreamingConfig] = None
) -> Iterator[Chunk]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | str | required | Path to Markdown file to process |
| `streaming_config` | StreamingConfig | None | Streaming configuration (uses defaults if None) |

### Returns

`Iterator[Chunk]` — Generator yielding chunks one at a time.

### Chunk Metadata

Streaming chunks include standard metadata plus:

| Field | Type | Description |
|-------|------|-------------|
| `stream_window_index` | int | Which buffer window produced this chunk |
| `stream_chunk_index` | int | Global chunk index across all windows |
| `is_cross_window` | bool | Whether chunk spans buffer boundaries |

Standard metadata fields preserved:
- `content_type`, `header_path`, `strategy`, `start_line`, `end_line`
- `previous_content`, `next_content` (overlap context)
- All strategy-specific metadata

### Usage Example

```python
from markdown_chunker import MarkdownChunker, StreamingConfig

chunker = MarkdownChunker()

# Basic usage
for chunk in chunker.chunk_file_streaming("large_docs.md"):
    process_chunk(chunk)

# With configuration
config = StreamingConfig(buffer_size=100_000, max_memory_mb=50)
for chunk in chunker.chunk_file_streaming("large_docs.md", config):
    vector_db.insert(chunk.content, chunk.metadata)
```

### Memory Usage

Memory consumption is bounded by:
```
Peak Memory ≈ buffer_size + overlap_size + processing_overhead
            ≈ 100KB + (20 lines × avg_line_length) + 50KB
            ≈ 150KB-200KB per window
```

**Guaranteed ceiling:** `max_memory_mb` parameter enforces strict upper bound.

---

## chunk_stream()

Stream chunks from a generic text stream (file-like object).

### Signature

```python
def chunk_stream(
    self,
    stream: io.TextIOBase,
    streaming_config: Optional[StreamingConfig] = None
) -> Iterator[Chunk]
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `stream` | io.TextIOBase | required | Text stream to process (file, StringIO, etc.) |
| `streaming_config` | StreamingConfig | None | Streaming configuration (uses defaults if None) |

### Returns

`Iterator[Chunk]` — Generator yielding chunks one at a time.

### Usage Example

```python
from markdown_chunker import MarkdownChunker
from io import StringIO

chunker = MarkdownChunker()

# From StringIO
markdown_text = "# Large Document\n\n" * 10000
stream = StringIO(markdown_text)

for chunk in chunker.chunk_stream(stream):
    print(f"Chunk {chunk.metadata['stream_chunk_index']}: {len(chunk.content)} chars")

# From file object
with open("large_docs.md", "r", encoding="utf-8") as f:
    for chunk in chunker.chunk_stream(f):
        process_chunk(chunk)
```

---

## Performance Characteristics

### Processing Speed

| File Size | Processing Time | Throughput |
|-----------|----------------|------------|
| 1MB | ~50ms | ~20MB/sec |
| 10MB | ~500ms | ~20MB/sec |
| 100MB | ~5s | ~20MB/sec |

*Benchmarked on standard hardware (Intel i5, 8GB RAM)*

### Memory Usage

| File Size | Memory Usage | Peak Memory |
|-----------|-------------|-------------|
| 1MB | ~10MB | ~15MB |
| 10MB | ~10MB | ~15MB |
| 100MB | ~10MB | ~15MB |
| 1GB+ | ~10MB | ~15MB |

**Scaling:** Memory usage remains constant regardless of file size.

### Overhead

- Streaming adds ~10-15% overhead vs. batch processing
- Trade-off: Slightly slower processing for guaranteed memory bounds
- Recommended for files >10MB or memory-constrained environments

---

## Safe Split Detection

Streaming maintains chunk quality through intelligent window boundary detection.

### Split Priority Order

1. **Header boundary** — Line before `#` header (highest priority)
2. **Paragraph break** — Double newline `\n\n`
3. **Newline outside fence** — Single newline (fence-aware)
4. **Fallback** — Hard split at `safe_split_threshold` (80% of buffer)

### Fence Tracking

Code blocks and tables are never split mid-block:

```python
# Buffer boundary detection
if inside_code_block:
    extend_buffer()  # Avoid splitting code
elif at_paragraph_break:
    split_here()     # Clean boundary
```

**Guaranteed:** No code fences, tables, or LaTeX blocks split between windows.

---

## Progress Tracking

Monitor processing of large files:

```python
import os
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
file_path = "large_documentation.md"
file_size = os.path.getsize(file_path)

processed_bytes = 0
for chunk in chunker.chunk_file_streaming(file_path):
    processed_bytes += len(chunk.content)
    progress = (processed_bytes / file_size) * 100
    print(f"\rProgress: {progress:.1f}%", end="")

print("\nComplete!")
```

---

## Error Handling

### Common Issues

**Out of Memory Despite Streaming:**
```python
# Solution: Reduce buffer size
config = StreamingConfig(buffer_size=50_000, max_memory_mb=50)
chunker.chunk_file_streaming(file_path, config)
```

**File Not Found:**
```python
from pathlib import Path

file_path = "docs.md"
if not Path(file_path).exists():
    raise FileNotFoundError(f"File not found: {file_path}")

chunks = chunker.chunk_file_streaming(file_path)
```

**Encoding Issues:**
```python
# Explicitly specify encoding
with open(file_path, "r", encoding="utf-8") as f:
    for chunk in chunker.chunk_stream(f):
        process_chunk(chunk)
```

---

## Comparison: Batch vs. Streaming

### When to Use Batch (`chunk()`)

- ✅ Files <10MB
- ✅ Memory available (>100MB RAM)
- ✅ Need fastest processing speed
- ✅ Full-document features (semantic boundaries)

### When to Use Streaming (`chunk_file_streaming()`)

- ✅ Files >10MB
- ✅ Memory-constrained (<100MB RAM)
- ✅ Need progress tracking
- ✅ Processing very large documentation (100MB+)

### Feature Compatibility

| Feature | Batch | Streaming |
|---------|-------|-----------|
| All chunking strategies | ✅ | ✅ |
| Overlap context | ✅ | ✅ |
| Metadata enrichment | ✅ | ✅ |
| Hierarchical chunking | ✅ | ⚠️ Limited* |
| LaTeX preservation | ✅ | ✅ |
| Nested fencing | ✅ | ✅ |
| Semantic boundaries | ✅ | ❌ Future** |

\* Hierarchy built post-streaming; document summary may be limited  
\** Requires full-document embeddings; planned for future release

---

## See Also

- [Chunker API Reference](chunker.md)
- [Configuration Reference](config.md)
- [Architecture: Streaming Processing](../architecture/README.md#streaming-processing)
- [Performance Guide](../guides/performance.md)
