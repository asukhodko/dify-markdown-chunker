# Dify Markdown Chunker v2.0

A streamlined, property-driven markdown chunker designed for RAG applications and LLM context management.

## Overview

Version 2.0 is a complete architectural redesign that reduces complexity while maintaining all essential functionality:

- **80% fewer files**: 55 → 11 core files
- **75% fewer config parameters**: 32 → 8 parameters  
- **Simpler architecture**: 3-stage linear pipeline
- **Better testing**: Property-based tests verify correctness
- **Faster performance**: Single-pass parser, optimized strategies

## Quick Start

### Installation

```bash
pip install dify-markdown-chunker
```

### Basic Usage

```python
from markdown_chunker_v2 import chunk_markdown, ChunkConfig

# Simple usage with defaults
text = """
# My Document

Some content here.

## Section 1
More content.
"""

result = chunk_markdown(text)
print(f"Created {result.chunk_count} chunks using {result.strategy_used} strategy")

for chunk in result.chunks:
    print(f"Lines {chunk.start_line}-{chunk.end_line}: {len(chunk.content)} chars")
```

### Custom Configuration

```python
# For code documentation
config = ChunkConfig.for_code_docs()
result = chunk_markdown(code_heavy_text, config)

# For RAG applications  
config = ChunkConfig.for_rag()
result = chunk_markdown(article_text, config)

# Custom configuration
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    overlap_size=100,
    preserve_atomic_blocks=True,
    extract_preamble=True,
    code_threshold=0.3
)
result = chunk_markdown(text, config)
```

## Configuration

### Parameters (8 total)

#### Size Constraints (3)
- **max_chunk_size** (default: 4096): Maximum characters per chunk
- **min_chunk_size** (default: 512): Minimum characters per chunk
- **overlap_size** (default: 200): Character overlap between chunks

#### Behavior Flags (3)
- **preserve_atomic_blocks** (default: True): Never split code blocks or tables
- **extract_preamble** (default: True): Include preceding text with code/tables
- **allow_oversize** (default: True): Allow atomic blocks to exceed max_chunk_size

#### Strategy Thresholds (2)
- **code_threshold** (default: 0.3): Code ratio to trigger CodeAware strategy
- **structure_threshold** (default: 3): Minimum headers for Structural strategy

### Factory Methods

```python
# Optimized for RAG (default settings)
ChunkConfig.for_rag()

# Optimized for code documentation (larger chunks, more overlap)
ChunkConfig.for_code_docs()  # max=6144, overlap=300, code_threshold=0.2
```

## Architecture

### 3-Stage Pipeline

```
Input Text
    ↓
┌─────────────────────┐
│  Stage 1: Parser    │  Single-pass content analysis
│  - Extract headers  │  (markdown-it-py)
│  - Extract code     │
│  - Extract tables   │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Stage 2: Strategy   │  Automatic strategy selection
│  Selection          │  (priority-based)
│  1. Table           │
│  2. CodeAware       │
│  3. Structural      │
│  4. Fallback        │
└─────────────────────┘
    ↓
┌─────────────────────┐
│ Stage 3: Post-      │  Validation & enrichment
│  Processing         │  - Filter invalid chunks
│  - Validate         │  - Add metadata
│  - Enrich metadata  │
└─────────────────────┘
    ↓
ChunkingResult
```

### Strategies

#### 1. TableStrategy (Priority 1)
**Activates when**: Document contains tables
**Behavior**: Preserves table integrity, never splits tables across chunks
**Use case**: Documents with data tables, comparison tables

#### 2. CodeAwareStrategy (Priority 2)
**Activates when**: Document contains code blocks
**Behavior**: Preserves code block integrity, maintains code-documentation relationship
**Use case**: Technical documentation, API docs, tutorials

#### 3. StructuralStrategy (Priority 3)
**Activates when**: Document has sufficient headers (≥3 by default)
**Behavior**: Uses headers as semantic boundaries, maintains section coherence
**Use case**: Well-structured articles, documentation, guides

#### 4. FallbackStrategy (Priority 4)
**Activates when**: No other strategy applies (always succeeds)
**Behavior**: Sentence-based chunking with paragraph boundaries
**Use case**: Plain text, unstructured content

## API Reference

### Main Functions

#### `chunk_markdown(text: str, config: ChunkConfig = None) -> ChunkingResult`

Chunk markdown text using the 3-stage pipeline.

**Parameters**:
- `text`: Markdown text to chunk
- `config`: Optional configuration (uses defaults if None)

**Returns**: `ChunkingResult` with chunks and metadata

### Classes

#### `ChunkConfig`

Configuration dataclass with 8 parameters.

**Methods**:
- `for_rag() -> ChunkConfig`: Factory for RAG applications
- `for_code_docs() -> ChunkConfig`: Factory for code documentation

**Properties**:
- `target_chunk_size: int`: Computed as (max + min) / 2
- `min_effective_chunk_size: int`: Computed as max - overlap
- `overlap_enabled: bool`: True if overlap_size > 0

#### `ChunkingResult`

Result of chunking operation.

**Attributes**:
- `chunks: List[Chunk]`: Generated chunks
- `strategy_used: str`: Name of strategy applied
- `processing_time: float`: Execution time in seconds
- `metadata: Dict`: Result-level metadata

**Properties**:
- `chunk_count: int`: Total number of chunks
- `total_size: int`: Total size of all chunks
- `average_chunk_size: float`: Average chunk size

**Methods**:
- `to_dict() -> Dict`: Serialize to dictionary
- `from_dict(data: Dict) -> ChunkingResult`: Deserialize from dictionary

#### `Chunk`

Individual chunk of text.

**Attributes**:
- `content: str`: Chunk text content
- `start_line: int`: Starting line number (1-based)
- `end_line: int`: Ending line number (inclusive)
- `metadata: Dict`: Chunk-level metadata

**Properties**:
- `size: int`: Character count
- `line_count: int`: Number of lines

## Domain Properties

v2.0 maintains and verifies 10 domain properties:

1. **Completeness**: All input content appears in output chunks
2. **No Duplication**: Content appears exactly once (except overlap)
3. **Order Preservation**: Chunks maintain input order
4. **Line Accuracy**: Line numbers correctly reference input
5. **Atomic Integrity**: Code blocks and tables never split
6. **Size Constraints**: Chunks respect max_chunk_size (with exceptions for atomic blocks)
7. **Overlap Consistency**: Overlap applied uniformly between chunks
8. **Determinism**: Same input always produces same output
9. **Strategy Consistency**: Strategy selection based on content analysis
10. **Error Handling**: Invalid inputs handled gracefully

All properties verified through property-based testing with Hypothesis.

## Migration from v1.x

### Breaking Changes

1. **Import paths changed**:
   ```python
   # v1.x
   from dify_markdown_chunker import MarkdownChunker
   
   # v2.0
   from markdown_chunker_v2 import chunk_markdown, MarkdownChunker
   ```

2. **Configuration simplified**:
   ```python
   # v1.x (32 parameters)
   config = ChunkConfig(
       max_chunk_size=4096,
       enable_phase2=True,
       tree_mode="hierarchical",
       # ... 29 more parameters
   )
   
   # v2.0 (8 parameters)
   config = ChunkConfig(
       max_chunk_size=4096,
       overlap_size=200
   )
   ```

3. **Strategy consolidation**:
   - Code + Mixed → CodeAware
   - Simplified Structural (no Phase 2)
   - Sentences → Fallback

4. **Result structure**:
   ```python
   # v1.x
   result.total_chunks
   
   # v2.0
   result.chunk_count
   ```

### Migration Guide

See [MIGRATION.md](MIGRATION.md) for detailed migration steps.

## Performance

### Expected Improvements

- **Parser**: 50% faster (single-pass vs dual invocation)
- **Strategy Selection**: Near-instant (no tree building)
- **Memory**: Lower (streamlined data structures)
- **Startup**: Faster (fewer imports)

### Benchmarks

*(Coming soon)*

## Development

### Running Tests

```bash
# All tests
pytest tests_v2/ -v

# Unit tests only
pytest tests_v2/unit_tests/ -v

# Integration tests
pytest tests_v2/integration_tests/ -v

# Property tests
pytest tests_v2/property_tests/ -v
```

### Test Coverage

- **62 tests total** (100% passing)
- 35 unit tests
- 8 integration tests
- 19 property-based tests

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome! Please see CONTRIBUTING.md for guidelines.

## Support

- **Issues**: https://github.com/dify-ai/dify-markdown-chunker/issues
- **Discussions**: https://github.com/dify-ai/dify-markdown-chunker/discussions

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Credits

Developed for the Dify AI platform.
