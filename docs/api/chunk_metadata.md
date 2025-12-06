# Chunk Metadata Reference

## Overview

Each chunk produced by `markdown_chunker_v2` contains metadata that provides context about the chunk's position in the document structure. This metadata is essential for RAG (Retrieval-Augmented Generation) pipelines to filter, navigate, and understand chunks.

## Metadata Fields

### Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `chunk_index` | `int` | Sequential index of the chunk in the document (0-based) |
| `content_type` | `str` | Type of content: `"text"`, `"code"`, `"table"`, `"mixed"`, `"preamble"`, `"section"` |
| `has_code` | `bool` | Whether the chunk contains code blocks (``` fences) |
| `strategy` | `str` | Strategy that created this chunk: `"structural"`, `"code_aware"`, `"fallback"` |
| `start_line` | `int` | Starting line number (1-indexed) |
| `end_line` | `int` | Ending line number (1-indexed) |

### Header Path

| Field | Type | Description |
|-------|------|-------------|
| `header_path` | `str` | Hierarchical path to the first header in the chunk |
| `header_level` | `int` | Level of the first header (1-6) |
| `sub_headers` | `List[str]` | Optional: additional header texts within the chunk |

#### header_path Format

The `header_path` field represents the hierarchical position of the chunk in the document structure:

```
Format: /<level1_text>/<level2_text>/<level3_text>/...

Examples:
- "/__preamble__"                                    # Preamble chunk
- "/Introduction"                                    # H1 only
- "/Introduction/Getting Started"                   # H1 + H2
- "/Introduction/Getting Started/Installation"      # H1 + H2 + H3
```

**Rules:**
1. Path reflects hierarchy up to and including the **first header** in the chunk
2. Each segment corresponds to a header level (`#` = 1st segment, `##` = 2nd, etc.)
3. Preamble chunks use special path `"/__preamble__"`
4. Never empty for chunks containing headers (structural strategy)

#### sub_headers Field

When a chunk contains multiple headers, the `sub_headers` field lists additional headers beyond the first:

```python
# Example chunk with multiple headers
chunk.metadata = {
    "header_path": "/Grades/SDE 12/Impact (Delivery)",
    "sub_headers": ["Complexity", "Leadership"],  # Additional ### headers
    ...
}
```

### Preamble Handling

Content before the first `#` header is treated as **preamble** and placed in a separate chunk:

| Metadata | Value |
|----------|-------|
| `content_type` | `"preamble"` |
| `header_path` | `"/__preamble__"` |

**Example:**
```markdown
Links to other resources:
- https://example.com/doc1
- https://example.com/doc2

# Main Title
...
```

This produces:
1. Preamble chunk with links (`header_path: "/__preamble__"`)
2. Structural chunk starting with `# Main Title`

### Small Chunk Handling

| Field | Type | Description |
|-------|------|-------------|
| `small_chunk` | `bool` | `True` if chunk size < `min_chunk_size` and cannot be merged |
| `small_chunk_reason` | `str` | Reason for small chunk: `"cannot_merge"` |

**Conditions for `small_chunk: true`:**
1. Chunk size is below `min_chunk_size` configuration
2. Cannot merge with adjacent chunks without exceeding `max_chunk_size`
3. Preamble chunks are never merged with structural chunks
4. Merge prefers chunks in the same logical section (same `header_path` prefix up to `##` level)
5. Left (previous) chunk is preferred over right (next) chunk for merging

### Oversize Handling

| Field | Type | Description |
|-------|------|-------------|
| `allow_oversize` | `bool` | `True` if chunk intentionally exceeds `max_chunk_size` |
| `oversize_reason` | `str` | Reason: `"code_block_integrity"`, `"table_integrity"`, `"section_integrity"` |

### Overlap Fields

When overlap is enabled (`overlap_size > 0`):

| Field | Type | Description |
|-------|------|-------------|
| `previous_content` | `str` | Last N characters from previous chunk |
| `next_content` | `str` | First N characters from next chunk |
| `overlap_size` | `int` | Actual overlap size in characters |

## Usage Examples

### Filtering by Section

```python
from markdown_chunker_v2 import MarkdownChunker

chunker = MarkdownChunker()
chunks = chunker.chunk(document)

# Find all chunks in "Installation" section
installation_chunks = [
    c for c in chunks 
    if "Installation" in c.metadata.get("header_path", "")
]
```

### Handling Preamble

```python
# Separate preamble from main content
preamble = [c for c in chunks if c.metadata.get("content_type") == "preamble"]
main_content = [c for c in chunks if c.metadata.get("content_type") != "preamble"]
```

### Building Navigation

```python
# Extract unique header paths for navigation
paths = set()
for chunk in chunks:
    path = chunk.metadata.get("header_path", "")
    if path and path != "/__preamble__":
        paths.add(path)

# Sort by hierarchy depth
sorted_paths = sorted(paths, key=lambda p: p.count("/"))
```

## Configuration Impact

| Config Parameter | Impact on Metadata |
|-----------------|-------------------|
| `max_chunk_size` | Affects `allow_oversize`, `small_chunk` |
| `min_chunk_size` | Affects `small_chunk` marking |
| `overlap_size` | Enables `previous_content`, `next_content` |
| `structure_threshold` | Determines if structural strategy is used |
