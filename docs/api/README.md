# API Reference

Complete API documentation for the Advanced Markdown Chunker plugin, powered by the chunkana engine.

## Table of Contents

- [Plugin Tool Interface](#plugin-tool-interface)
- [Direct chunkana Usage](#direct-chunkana-usage)
- [Parameter Mapping](#parameter-mapping)
- [Output Format](#output-format)
- [Migration Adapter](#migration-adapter)

---

## Plugin Tool Interface

### Tool Parameters

The plugin exposes the following parameters through the Dify tool interface:

```yaml
tool: advanced_markdown_chunker
parameters:
  input_text: string (required)
  max_chunk_size: number (default: 4096)
  chunk_overlap: number (default: 200)
  strategy: select (default: auto)
  include_metadata: boolean (default: true)
  enable_hierarchy: boolean (default: false)
  debug: boolean (default: false)
  leaf_only: boolean (default: false)
```

#### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_text` | string | required | Markdown text to chunk |
| `max_chunk_size` | number | 4096 | Maximum chunk size in characters |
| `chunk_overlap` | number | 200 | Overlap between chunks (capped at 35% of chunk size) |
| `strategy` | select | auto | Chunking strategy (auto/code_aware/list_aware/structural/fallback) |
| `include_metadata` | boolean | true | Embed metadata in chunk text |
| `enable_hierarchy` | boolean | false | Create parent-child relationships |
| `debug` | boolean | false | Include all chunk types in hierarchical mode |
| `leaf_only` | boolean | false | Return only leaf chunks in hierarchical mode |

### Tool Output Format

#### Standard Mode (enable_hierarchy=false)

```json
{
  "result": [
    {
      "content": "# Section\n\nContent here...",
      "metadata": {
        "content_type": "text",
        "header_path": "/Section",
        "start_line": 1,
        "end_line": 5,
        "chunk_index": 0,
        "strategy": "structural"
      }
    }
  ]
}
```

#### Hierarchical Mode (enable_hierarchy=true)

```json
{
  "result": [
    {
      "content": "# Section\n\nContent here...",
      "metadata": {
        "chunk_id": "abc12345",
        "parent_id": "root123",
        "children_ids": ["def67890"],
        "hierarchy_level": 1,
        "is_leaf": false,
        "is_root": false,
        "indexable": true,
        "content_type": "text",
        "header_path": "/Section"
      }
    }
  ]
}
```

#### Metadata Embedding (include_metadata=true)

When `include_metadata=true`, chunks include a metadata block:

```
<metadata>
{
  "content_type": "text",
  "header_path": "/Installation/Requirements",
  "start_line": 45,
  "end_line": 52
}
</metadata>
# Requirements

Python 3.12 or higher is required...
```

---

## Direct chunkana Usage

For advanced features not available in the plugin UI, use chunkana directly:

### Basic Usage

```python
from chunkana import MarkdownChunker

# Create chunker
chunker = MarkdownChunker()

# Chunk markdown
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

# Access chunks
for chunk in result.chunks:
    print(f"Content: {chunk.content[:50]}...")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Size: {chunk.size} chars")
```

### Advanced Configuration

```python
from chunkana import MarkdownChunker, ChunkConfig, AdaptiveSizeConfig

# Advanced configuration not available in plugin
config = ChunkConfig(
    max_chunk_size=4096,
    overlap_size=200,
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=1500,
        min_scale=0.5,
        max_scale=1.5
    ),
    enable_code_context_binding=True,
    group_related_tables=True
)

chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text)
```

### Hierarchical Chunking

```python
from chunkana import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk_hierarchical(markdown_text)

# Navigate hierarchy
root = result.get_chunk(result.root_id)
sections = result.get_children(result.root_id)

for section in sections:
    print(f"Section: {section.metadata['header_path']}")
    subsections = result.get_children(section.metadata['chunk_id'])
```

---

## Parameter Mapping

### Plugin → chunkana Mapping

| Plugin Parameter | chunkana Config | Notes |
|------------------|-----------------|-------|
| `max_chunk_size` | `max_chunk_size` | Direct mapping |
| `chunk_overlap` | `overlap_size` | Capped at 35% of chunk size in plugin |
| `strategy` | `strategy_override` | `auto` → automatic selection |
| `include_metadata` | `include_metadata` | Controls metadata embedding |
| `enable_hierarchy` | `enable_hierarchy` | Enables hierarchical chunking |
| `debug` | `debug_mode` | Controls chunk type visibility |
| `leaf_only` | `leaf_only` | Filters to content chunks only |

### Advanced Features (chunkana Only)

Features available only through direct chunkana usage:

```python
config = ChunkConfig(
    # Adaptive sizing
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(...),
    
    # Code-context binding
    enable_code_context_binding=True,
    max_context_chars_before=500,
    preserve_before_after_pairs=True,
    
    # Table grouping
    group_related_tables=True,
    table_grouping_config=TableGroupingConfig(...),
    
    # Streaming
    enable_streaming=True,
    streaming_config=StreamingConfig(...)
)
```

---

## Output Format

### Chunk Structure

Each chunk has the following structure:

```python
@dataclass
class Chunk:
    content: str           # Chunk content (with metadata if enabled)
    start_line: int        # Start line (1-based)
    end_line: int          # End line
    metadata: Dict[str, Any]  # Chunk metadata
    
    # Properties
    size: int              # Size in characters
    line_count: int        # Number of lines
    content_type: str      # Content type
    strategy: str          # Strategy used
```

### Standard Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `content_type` | str | Type of content (text, code, table, list, mixed) |
| `header_path` | str | Hierarchical path of section headers |
| `start_line` | int | Source line number (1-based) |
| `end_line` | int | End line number |
| `chunk_index` | int | Index in sequence |
| `strategy` | str | Chunking strategy used |

### Hierarchical Metadata Fields

Additional fields when `enable_hierarchy=true`:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | str | Unique 8-character identifier |
| `parent_id` | str | Parent chunk ID (None for root) |
| `children_ids` | List[str] | Child chunk IDs |
| `hierarchy_level` | int | 0=document, 1=section, 2=subsection, 3=paragraph |
| `is_leaf` | bool | Has no children |
| `is_root` | bool | Document-level chunk |
| `indexable` | bool | Recommended for vector database indexing |

### Overlap Handling

#### With include_metadata=true (default)

Overlap stored in metadata fields:

```json
{
  "metadata": {
    "previous_content": "...end of previous chunk...",
    "next_content": "...start of next chunk..."
  }
}
```

#### With include_metadata=false

Overlap embedded directly in chunk text:

```
...end of previous chunk...
# Current Section
Main content of this chunk...
...start of next chunk...
```

---

## Migration Adapter

The plugin includes a migration adapter (`adapter.py`) that provides compatibility with legacy APIs while using chunkana internally.

### Adapter Interface

```python
from adapter import MigrationAdapter

adapter = MigrationAdapter()
result = adapter.chunk_markdown(
    text=markdown_text,
    max_chunk_size=2048,
    chunk_overlap=100,
    strategy="auto",
    include_metadata=True
)
```

### Compatibility Features

- **API Compatibility**: Maintains exact interface compatibility
- **Parameter Mapping**: Translates plugin parameters to chunkana config
- **Output Filtering**: Applies plugin-specific filtering (debug, leaf_only)
- **Error Handling**: Provides consistent error messages

---

## Usage Examples

### Basic Plugin Usage

```yaml
workflow:
  - node: chunk_document
    type: tool
    tool: advanced_markdown_chunker
    config:
      input_text: ${document.content}
      max_chunk_size: 2048
      strategy: auto
      include_metadata: true
```

### Hierarchical Chunking

```yaml
workflow:
  - node: hierarchical_chunks
    type: tool
    tool: advanced_markdown_chunker
    config:
      input_text: ${document.content}
      enable_hierarchy: true
      leaf_only: true  # Only content chunks for vector DB
      debug: false
```

### Direct chunkana for Advanced Features

```python
from chunkana import MarkdownChunker, ChunkConfig

# Use features not available in plugin UI
config = ChunkConfig(
    max_chunk_size=4096,
    use_adaptive_sizing=True,
    enable_code_context_binding=True,
    group_related_tables=True
)

chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)

# Access advanced metadata
for chunk in result.chunks:
    if chunk.metadata.get('is_table_group'):
        print(f"Grouped {chunk.metadata['table_group_count']} tables")
    
    if chunk.metadata.get('adaptive_size'):
        print(f"Adaptive size: {chunk.metadata['adaptive_size']}")
```

---

## Error Handling

### Plugin Errors

The plugin provides user-friendly error messages:

```json
{
  "error": "Invalid chunk_overlap: must be between 0 and max_chunk_size * 0.35",
  "details": {
    "parameter": "chunk_overlap",
    "value": 2000,
    "max_allowed": 1433
  }
}
```

### chunkana Errors

Direct chunkana usage provides detailed error information:

```python
try:
    result = chunker.chunk(markdown_text)
except ChunkingError as e:
    print(f"Error: {e.message}")
    print(f"Context: {e.context}")
    print(f"Suggestions: {e.suggestions}")
```

---

## Performance Considerations

### Plugin Performance

- **Processing Speed**: ~0.25 ms/KB
- **Memory Usage**: <1 MB for typical documents
- **Throughput**: 4-5 MB/s sustained

### Optimization Tips

1. **Use appropriate chunk sizes**: 2048-4096 chars for RAG
2. **Enable hierarchy only when needed**: Adds processing overhead
3. **Use leaf_only for vector DB**: Reduces output size
4. **Consider direct chunkana for large documents**: Better memory management

---

## See Also

- [Usage Guide](../usage.md) - Detailed usage examples
- [Migration to Chunkana Guide](../guides/migration-to-chunkana.md) - Migration information
- [Chunking Strategies](../architecture/strategies.md) - Strategy details
- [Configuration Guide](../reference/configuration.md) - Configuration options
- [Troubleshooting Guide](../guides/troubleshooting.md) - Common issues and solutions
- [chunkana Documentation](https://github.com/asukhodko/chunkana) - Full chunkana API reference

---

**Last Updated:** January 10, 2026  
**Version:** 2.1.5 (chunkana-powered)
