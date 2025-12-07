# Chunk Metadata Reference

<cite>
**Referenced Files in This Document**   
- [types.py](file://markdown_chunker_v2/types.py)
- [chunker.py](file://markdown_chunker_v2/chunker.py)
- [config.py](file://markdown_chunker_v2/config.py)
- [structural.py](file://markdown_chunker_v2/strategies/structural.py)
- [parser.py](file://markdown_chunker_v2/parser.py)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md)
- [output-format.md](file://docs/reference/output-format.md)
- [test_metadata_unit.py](file://tests/test_metadata_unit.py)
- [test_metadata_properties.py](file://tests/test_metadata_properties.py)
</cite>

## Table of Contents
1. [Overview](#overview)
2. [Core Metadata Fields](#core-metadata-fields)
3. [Header Path and Hierarchy](#header-path-and-hierarchy)
4. [Preamble Handling](#preamble-handling)
5. [Small Chunk Detection](#small-chunk-detection)
6. [Oversize Chunk Handling](#oversize-chunk-handling)
7. [Overlap Context Model](#overlap-context-model)
8. [Configuration Impact](#configuration-impact)
9. [Validation and Testing](#validation-and-testing)

## Overview

Each chunk produced by `markdown_chunker_v2` contains metadata that provides context about the chunk's position in the document structure. This metadata is essential for RAG (Retrieval-Augmented Generation) pipelines to filter, navigate, and understand chunks. The metadata system has been redesigned to provide hierarchical context while maintaining compatibility with Dify's knowledge pipeline UI.

The chunk metadata system serves several key purposes:
- **Structural Context**: Provides hierarchical path information through `header_path`
- **Content Classification**: Identifies content types and structural elements
- **Navigation Support**: Enables building document navigation from chunk metadata
- **RAG Optimization**: Includes fields specifically useful for retrieval systems
- **Debugging and Analysis**: Contains information for troubleshooting and performance monitoring

**Section sources**
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#overview)
- [types.py](file://markdown_chunker_v2/types.py#L100-L148)

## Core Metadata Fields

The core metadata fields are present in every chunk and provide fundamental information about the chunk's content and position.

| Field | Type | Description |
|-------|------|-------------|
| `chunk_index` | `int` | Sequential index of the chunk in the document (0-based) |
| `content_type` | `str` | Type of content: `"text"`, `"code"`, `"table"`, `"mixed"`, `"preamble"`, `"section"` |
| `has_code` | `bool` | Whether the chunk contains code blocks (``` fences) |
| `strategy` | `str` | Strategy that created this chunk: `"structural"`, `"code_aware"`, `"fallback"` |
| `start_line` | `int` | Starting line number (1-indexed) - approximate location in source document |
| `end_line` | `int` | Ending line number (1-indexed) - approximate location in source document |

The `start_line` and `end_line` fields provide approximate locations in the source document. Line ranges may overlap between adjacent chunks. For precise chunk location, use the content text itself rather than relying solely on line numbers.

Additional content-specific fields are included based on the chunk's content:
- **For Lists**: `list_type` (ordered/unordered), `has_nested_lists`, `has_nested_items`
- **For Code**: `language` (programming language), `has_syntax_highlighting`
- **For Tables**: `row_count`, `column_count`, `has_header`

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L115-L135)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#core-fields)

## Header Path and Hierarchy

The header path system provides hierarchical context for chunks, enabling navigation and structural understanding of the document.

### header_path Format

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

### sub_headers Field

When a chunk contains multiple headers, the `sub_headers` field lists additional headers beyond the first:

```python
# Example chunk with multiple headers
chunk.metadata = {
    "header_path": "/Grades/DEV-4/Impact (Delivery)",
    "sub_headers": ["Complexity", "Leadership"],  # Additional ### headers
    ...
}
```

The `sub_headers` field contains headers that are children of the root section (last header in `header_path`). This includes:
- Headers with level greater than the contextual level (deeper than root section)
- Headers with the same level as the contextual level but different text (siblings of root, not root itself)

This design ensures that all chunks within a section (e.g., DEV-4) have the same `header_path`, while still capturing the local section structure within the chunk.

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L119-L127)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#header-path)
- [structural.py](file://markdown_chunker_v2/strategies/structural.py#L390-L481)

## Preamble Handling

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

The preamble separation ensures that introductory content, links, or metadata before the main document structure is preserved as a distinct unit. This is particularly useful for documents that begin with references, disclaimers, or other non-structural content.

Preamble chunks are never merged with structural chunks during the merging process, maintaining their separation throughout the chunking pipeline.

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L95-L97)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#preamble-handling)
- [parser.py](file://markdown_chunker_v2/parser.py#L249-L269)

## Small Chunk Detection

The system includes sophisticated small chunk detection to identify chunks that may be problematic for retrieval systems.

| Field | Type | Description |
|-------|------|-------------|
| `small_chunk` | `bool` | `True` if chunk is small AND structurally weak |
| `small_chunk_reason` | `str` | Reason for small chunk: `"cannot_merge"` |

**Conditions for `small_chunk: true` (ALL must be met):**
1. Chunk size is below `min_chunk_size` configuration
2. Cannot merge with adjacent chunks without exceeding `max_chunk_size`
3. Chunk is structurally weak (lacks strong headers, multiple paragraphs, or meaningful content)

**Structural Strength Indicators (ANY prevents small_chunk flag):**
- Has header level 2 (`##`) or 3 (`###`)
- Contains at least 3 lines of non-header content
- Text content exceeds 100 characters after header extraction
- Contains at least 2 paragraph breaks (double newline)

**Merge behavior:**
- Preamble chunks are never merged with structural chunks
- Merge prefers chunks in the same logical section (same `header_path` prefix up to `##` level)
- Left (previous) chunk is preferred over right (next) chunk for merging
- Small header-only chunks (level 1-2, < 150 chars) are merged with their section body before size-based merging

A chunk below `min_chunk_size` that is **structurally strong** will NOT be flagged as `small_chunk`. This prevents meaningful content like section headers with brief descriptions from being marked as problematic.

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L128-L137)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#small-chunk-handling)
- [chunker.py](file://markdown_chunker_v2/chunker.py#L422-L468)

## Oversize Chunk Handling

The system handles chunks that intentionally exceed the maximum size limit through oversize metadata.

| Field | Type | Description |
|-------|------|-------------|
| `allow_oversize` | `bool` | `True` if chunk intentionally exceeds `max_chunk_size` |
| `oversize_reason` | `str` | Reason: `"code_block_integrity"`, `"table_integrity"`, `"section_integrity"` |

Oversize chunks are created when preserving atomic blocks (code blocks, tables) or maintaining section integrity is more important than adhering to size limits. The system automatically sets these metadata fields when a chunk exceeds `max_chunk_size` due to valid reasons:

- **Code Block Integrity**: When a code block cannot be split without breaking syntax
- **Table Integrity**: When a table cannot be split without breaking structure
- **Section Integrity**: When a logical section should remain intact

This metadata helps downstream systems understand why a chunk is oversized and handle it appropriately in retrieval and processing.

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L114-L118)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#oversize-handling)
- [chunker.py](file://markdown_chunker_v2/chunker.py#L242-L253)

## Overlap Context Model

The overlap model in v2 uses metadata-only context windows. There is **no physical text duplication** in `chunk.content`. Context from neighboring chunks is stored only in metadata fields.

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

This metadata-only overlap model provides context for language models while avoiding the problems associated with text duplication in retrieval systems.

**Section sources**
- [types.py](file://markdown_chunker_v2/types.py#L138-L148)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#overlap-fields)
- [chunker.py](file://markdown_chunker_v2/chunker.py#L130-L175)

## Configuration Impact

Configuration parameters directly affect the metadata generated for chunks:

| Config Parameter | Impact on Metadata |
|-----------------|-------------------|
| `max_chunk_size` | Affects `allow_oversize`, `small_chunk` |
| `min_chunk_size` | Affects `small_chunk` marking |
| `overlap_size` | Enables `previous_content`, `next_content` |
| `structure_threshold` | Determines if structural strategy is used |

The configuration system allows fine-tuning of the chunking behavior to suit different document types and use cases. For example:

- **Code-heavy documents**: Use larger `max_chunk_size` and `min_chunk_size` to accommodate large code blocks
- **Structured documents**: Lower `structure_threshold` to enable structural strategy on documents with fewer headers
- **Precision retrieval**: Enable overlap with appropriate `overlap_size` for better context preservation

The system also provides configuration profiles for common use cases:
- `for_code_heavy()`: Optimized for code documentation
- `for_structured()`: Optimized for documents with hierarchical structure
- `minimal()`: Creates small chunks for fine-grained retrieval

**Section sources**
- [config.py](file://markdown_chunker_v2/config.py#L21-L45)
- [chunk_metadata.md](file://docs/api/chunk_metadata.md#configuration-impact)
- [chunker.py](file://markdown_chunker_v2/chunker.py#L32-L42)

## Validation and Testing

The chunk metadata system is validated through comprehensive testing to ensure correctness and reliability.

### Property-Based Testing

The system uses property-based testing to verify key behaviors:

```python
class TestProperty1FirstHeaderDeterminesPath:
    """
    For any chunk containing one or more headers, the header_path SHALL end with
    the text of the first header in that chunk.
    """
    
class TestProperty2PreambleSeparation:
    """
    For any markdown document with non-empty content before the first # header,
    chunking SHALL produce a separate preamble chunk.
    """
    
class TestProperty3NoPreambleWithoutContent:
    """
    For any markdown document with no content before the first header,
    chunking SHALL NOT produce a preamble chunk.
    """
```

These properties ensure that the metadata system behaves correctly across a wide range of document structures and edge cases.

### Unit Testing

Specific examples are tested to verify correct behavior:

```python
class TestDEV4ImpactCase:
    """
    Test that chunk with Impact/Complexity/Leadership has header_path
    ending with "Impact (Delivery)", not "Complexity".
    """
    
class TestPreambleSeparation:
    """
    Test that links before # Критерии грейдов DEV are in separate preamble chunk.
    """
```

The testing framework validates that:
- Header paths correctly reflect document hierarchy
- Preamble content is properly separated
- Small chunks are correctly identified and marked
- Overlap context is properly generated
- Configuration parameters correctly influence metadata

These tests ensure that the metadata system provides reliable and predictable behavior for downstream applications.

**Section sources**
- [test_metadata_unit.py](file://tests/test_metadata_unit.py)
- [test_metadata_properties.py](file://tests/test_metadata_properties.py)
- [output-format.md](file://docs/reference/output-format.md)