# API Reference

Complete API documentation for Python Markdown Chunker v2.0.

## Table of Contents

- [Main API](#main-api)
- [Configuration](#configuration)
- [Data Types](#data-types)
- [Convenience Functions](#convenience-functions)
- [Validation](#validation)

---

## Main API

### MarkdownChunker

Main class for chunking markdown documents.

```python
from markdown_chunker_v2 import MarkdownChunker
```

#### Constructor

```python
MarkdownChunker(config: ChunkConfig = None)
```

**Parameters:**
- `config` (ChunkConfig, optional): Configuration for chunking. Defaults to `ChunkConfig()`.

**Example:**
```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2048)
chunker = MarkdownChunker(config)
```

#### Methods

##### chunk()

Chunk markdown content into pieces.

```python
chunk(text: str) -> List[Chunk]
```

**Parameters:**
- `text` (str): Markdown content to chunk

**Returns:**
- `List[Chunk]`: List of chunks

**Example:**
```python
chunks = chunker.chunk("# Hello\n\nWorld")
for chunk in chunks:
    print(f"Content: {chunk.content}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
```

##### chunk_with_metrics()

Chunk markdown content with detailed metrics.

```python
chunk_with_metrics(text: str) -> ChunkingResult
```

**Parameters:**
- `text` (str): Markdown content to chunk

**Returns:**
- `ChunkingResult`: Complete chunking result with metrics

**Example:**
```python
result = chunker.chunk_with_metrics("# Hello\n\nWorld")
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
```

See [MarkdownChunker API](chunker.md) for full documentation.

---

## Configuration

### ChunkConfig

Configuration for chunking behavior. Simplified from 32 to 8 parameters in v2.0.

```python
from markdown_chunker_v2 import ChunkConfig
```

#### Constructor

```python
ChunkConfig(
    max_chunk_size: int = 4096,
    min_chunk_size: int = 512,
    overlap_size: int = 200,
    preserve_atomic_blocks: bool = True,
    extract_preamble: bool = True,
    code_threshold: float = 0.3,
    structure_threshold: int = 3,
    strategy_override: Optional[str] = None
)
```

#### Configuration Profiles

```python
# Default configuration
config = ChunkConfig.default()

# For code-heavy documents
config = ChunkConfig.for_code_heavy()

# For structured documents
config = ChunkConfig.for_structured()

# For small chunks
config = ChunkConfig.minimal()
```

See [ChunkConfig API](config.md) for full documentation.

---

## Data Types

### Chunk

Represents a single chunk of markdown content.

```python
from markdown_chunker_v2 import Chunk
```

#### Properties

- `content` (str): Chunk content
- `start_line` (int): Starting line number (1-based)
- `end_line` (int): Ending line number
- `metadata` (dict): Additional metadata

#### Metadata Fields

- `strategy` (str): Strategy used
- `content_type` (str): Content type (text, code, table, mixed)
- `header_path` (str): Hierarchical header path
- `chunk_index` (int): Index in sequence
- `previous_content` (str, optional): Overlap from previous chunk
- `next_content` (str, optional): Overlap to next chunk

### ChunkingResult

Complete result of chunking operation.

```python
from markdown_chunker_v2 import ChunkingResult
```

#### Properties

- `chunks` (List[Chunk]): List of chunks
- `strategy_used` (str): Strategy that was used
- `metrics` (ChunkingMetrics): Processing metrics
- `analysis` (ContentAnalysis): Content analysis

### ContentAnalysis

Content analysis results.

```python
from markdown_chunker_v2 import ContentAnalysis
```

#### Properties

- `code_ratio` (float): Ratio of code content (0.0-1.0)
- `header_count` (int): Number of headers
- `code_block_count` (int): Number of code blocks
- `table_count` (int): Number of tables
- `total_lines` (int): Total line count
- `total_chars` (int): Total character count

See [Data Types](types.md) for full documentation.

---

## Convenience Functions

### chunk_text()

Quick function to chunk markdown text.

```python
from markdown_chunker_v2 import chunk_text

chunks = chunk_text("# Hello\n\nWorld")
```

### chunk_file()

Quick function to chunk markdown file.

```python
from markdown_chunker_v2 import chunk_file

chunks = chunk_file("README.md")
```

---

## Validation

### validate_chunks()

Validate chunks for correctness.

```python
from markdown_chunker_v2 import validate_chunks

result = validate_chunks(chunks, original_text)
if result.is_valid:
    print("Chunks are valid")
else:
    print(f"Errors: {result.errors}")
```

### Validator

Full validation class.

```python
from markdown_chunker_v2 import Validator

validator = Validator()
result = validator.validate(chunks, original_text)
```

---

## Usage Examples

### Basic Chunking

```python
from markdown_chunker_v2 import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk("# Hello\n\nWorld")

for chunk in chunks:
    print(f"Chunk: {chunk.content}")
```

### With Configuration

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig(
    max_chunk_size=2048,
    overlap_size=100
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown)
```

### Using Profiles

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig.for_code_heavy()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown)
```

### Force Strategy

```python
config = ChunkConfig(strategy_override="structural")
chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown)
```

### Serialization

```python
from markdown_chunker_v2 import MarkdownChunker
import json

chunker = MarkdownChunker()
result = chunker.chunk_with_metrics("# Test")

# Serialize
result_dict = result.to_dict()
json_str = json.dumps(result_dict, indent=2)
```

---

## Strategies

v2.0 uses 3 strategies (reduced from 6):

| Strategy | When Used |
|----------|-----------|
| **CodeAware** | Code blocks, tables, or code_ratio ≥ 30% |
| **Structural** | ≥3 headers |
| **Fallback** | Default for all other content |

See [Chunking Strategies](../architecture/strategies.md) for details.

---

## Migration from v1.x

Key changes in v2.0:
- Module renamed: `markdown_chunker` → `markdown_chunker_v2`
- Strategies reduced: 6 → 3
- Configuration simplified: 32 → 8 parameters
- `chunk_with_analysis()` → `chunk_with_metrics()`
- `chunk_simple()` → `chunk()`

See [Migration Guide](../MIGRATION.md) for full details.

---

## See Also

- [Quick Start Guide](../quickstart.md) - Get started quickly
- [Usage Guide](../usage.md) - Detailed usage examples
- [Configuration Reference](../reference/configuration.md) - Complete configuration options

---

**Last Updated:** December 5, 2024  
**Version:** 2.0.0
