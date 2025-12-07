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
    "header_path": "/Grades/DEV-4/Impact (Delivery)",
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
| `small_chunk` | `bool` | `True` if chunk is small AND structurally weak |
| `small_chunk_reason` | `str` | Reason for small chunk: `"cannot_merge"` |

**Conditions for `small_chunk: true` (ALL must be met):**
1. Chunk size is below `min_chunk_size` configuration
2. Cannot merge with adjacent chunks without exceeding `max_chunk_size`
3. Chunk is structurally weak (lacks strong headers, multiple paragraphs, or meaningful content)

**Important:** A chunk below `min_chunk_size` that is **structurally strong** will NOT be flagged as `small_chunk`. Structural strength indicators:
- Has header level 2 (`##`) or 3 (`###`)
- Contains at least 3 lines of non-header content
- Text content exceeds 100 characters after header extraction
- Contains at least 2 paragraph breaks (double newline)

**Current Limitation:** Lists (bullet/numbered) are not yet considered as structural strength indicators. This may be added in future versions.

**Merge behavior:**
- Preamble chunks are never merged with structural chunks
- Merge prefers chunks in the same logical section (same `header_path` prefix up to `##` level)
- Left (previous) chunk is preferred over right (next) chunk for merging
- Small header-only chunks (level 1-2, < 150 chars) are merged with their section body before size-based merging

### Oversize Handling

| Field | Type | Description |
|-------|------|-------------|
| `allow_oversize` | `bool` | `True` if chunk intentionally exceeds `max_chunk_size` |
| `oversize_reason` | `str` | Reason: `"code_block_integrity"`, `"table_integrity"`, `"section_integrity"` |

### Overlap Fields

**Overview:** The overlap model in v2 uses metadata-only context windows. There is **no physical text duplication** in `chunk.content`. Context from neighboring chunks is stored only in metadata fields.

When overlap is enabled (`overlap_size > 0`):

| Field | Type | Description |
|-------|------|-------------|
| `previous_content` | `str` | Last N characters from previous chunk (metadata only) |
| `next_content` | `str` | First N characters from next chunk (metadata only) |
| `overlap_size` | `int` | Size of context window in characters (NOT physical text overlap) |

**Key Points:**
- `overlap_size` is the **context window size**, not the amount of duplicated text
- `chunk.content` contains **distinct, non-overlapping text**
- `previous_content` and `next_content` provide **metadata context only**
- Context fields help language models understand chunk boundaries without text duplication
- This design avoids index bloat and semantic search confusion

**Example:**
```python
chunker = MarkdownChunker(ChunkConfig(overlap_size=100))
chunks = chunker.chunk(document)

# chunk.content does NOT contain duplicated text
assert chunks[1].content not in chunks[0].content
assert chunks[0].content not in chunks[1].content

# Context is in metadata only
if 'previous_content' in chunks[1].metadata:
    # This context is from chunks[0], but not in chunks[1].content
    context = chunks[1].metadata['previous_content']
    assert context in chunks[0].content
```

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
