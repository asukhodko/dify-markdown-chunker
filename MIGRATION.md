# Migration Guide: v1.x → v2.0

This guide helps you migrate from Dify Markdown Chunker v1.x to v2.0.

## Overview of Changes

### Major Improvements
- ✅ 80% reduction in files (55 → 11)
- ✅ 75% reduction in config parameters (32 → 8)
- ✅ Simplified architecture (3-stage linear pipeline)
- ✅ Better performance (single-pass parser)
- ✅ Property-based testing (all domain properties verified)

### Breaking Changes
1. Import paths changed
2. Configuration significantly simplified
3. Strategy names updated
4. Result structure modified
5. Error types consolidated

## Step-by-Step Migration

### Step 1: Update Imports

**Before (v1.x)**:
```python
from dify_markdown_chunker import MarkdownChunker, ChunkConfig
from dify_markdown_chunker.types import Chunk, ChunkingResult
```

**After (v2.0)**:
```python
from markdown_chunker_v2 import chunk_markdown, MarkdownChunker, ChunkConfig
from markdown_chunker_v2 import Chunk, ChunkingResult
```

### Step 2: Update Configuration

#### Basic Usage

**Before (v1.x)**:
```python
from dify_markdown_chunker import MarkdownChunker, ChunkConfig

config = ChunkConfig(
    max_chunk_size=4096,
    min_chunk_size=512,
    overlap_size=200,
    enable_phase2=True,
    phase2_mode="hierarchical",
    atomic_threshold=0.8,
    merge_threshold=0.7,
    split_threshold=1.2,
    # ... 24+ more parameters
)

chunker = MarkdownChunker(config)
result = chunker.chunk(text)
```

**After (v2.0)**:
```python
from markdown_chunker_v2 import chunk_markdown, ChunkConfig

# Simple usage
result = chunk_markdown(text)

# Or with custom config (only 8 parameters now!)
config = ChunkConfig(
    max_chunk_size=4096,
    min_chunk_size=512,
    overlap_size=200,
    preserve_atomic_blocks=True,
    extract_preamble=True,
    allow_oversize=True,
    code_threshold=0.3,
    structure_threshold=3
)

result = chunk_markdown(text, config)
```

#### Factory Methods

**Before (v1.x)**:
```python
# Manual configuration for different use cases
config_rag = ChunkConfig(max_chunk_size=4096, ...)
config_code = ChunkConfig(max_chunk_size=6144, ...)
```

**After (v2.0)**:
```python
# Use factory methods
config_rag = ChunkConfig.for_rag()
config_code = ChunkConfig.for_code_docs()
```

### Step 3: Update Configuration Parameters

#### Parameter Mapping

| v1.x Parameter | v2.0 Equivalent | Notes |
|----------------|-----------------|-------|
| `max_chunk_size` | `max_chunk_size` | ✅ Same |
| `min_chunk_size` | `min_chunk_size` | ✅ Same |
| `overlap_size` | `overlap_size` | ✅ Same |
| `enable_phase2` | ❌ Removed | Phase 2 eliminated |
| `phase2_mode` | ❌ Removed | No longer needed |
| `atomic_threshold` | `preserve_atomic_blocks` | Now boolean |
| `merge_threshold` | ❌ Removed | Automatic merging |
| `split_threshold` | ❌ Removed | Automatic splitting |
| `code_block_handling` | `code_threshold` | Now a ratio |
| `table_handling` | `preserve_atomic_blocks` | Unified flag |
| `header_aware` | `structure_threshold` | Count-based |
| `preamble_extraction` | `extract_preamble` | ✅ Same concept |
| `allow_oversize_chunks` | `allow_oversize` | ✅ Renamed |
| 20+ other params | ❌ Removed | YAGNI principle |

#### Parameter Defaults

```python
# v2.0 defaults (sensible for most use cases)
ChunkConfig(
    max_chunk_size=4096,      # Same as v1.x
    min_chunk_size=512,       # Same as v1.x
    overlap_size=200,         # Same as v1.x
    preserve_atomic_blocks=True,   # Replaces atomic_threshold
    extract_preamble=True,    # Replaces preamble_extraction
    allow_oversize=True,      # Replaces allow_oversize_chunks
    code_threshold=0.3,       # Replaces code_block_handling
    structure_threshold=3     # Replaces header_aware
)
```

### Step 4: Update Result Handling

**Before (v1.x)**:
```python
result = chunker.chunk(text)

print(f"Total chunks: {result.total_chunks}")
print(f"Strategy: {result.strategy_name}")

for chunk in result.chunks:
    print(f"Chunk: {chunk.content[:50]}")
```

**After (v2.0)**:
```python
result = chunk_markdown(text)

# Changed: total_chunks → chunk_count
print(f"Total chunks: {result.chunk_count}")

# Changed: strategy_name → strategy_used
print(f"Strategy: {result.strategy_used}")

for chunk in result.chunks:
    print(f"Chunk: {chunk.content[:50]}")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Metadata: {chunk.metadata}")
```

### Step 5: Update Strategy Names

| v1.x Strategy | v2.0 Strategy | Notes |
|---------------|---------------|-------|
| `Simple` | `fallback` | Renamed |
| `Code` | `code_aware` | Renamed |
| `Mixed` | `code_aware` | Merged with Code |
| `Structural` | `structural` | Simplified (no Phase 2) |
| `Table` | `table` | ✅ Same |
| `Paragraph` | `fallback` | Merged |
| `Sentences` | `fallback` | Merged |

**Before (v1.x)**:
```python
if result.strategy_name == "Code":
    print("Code strategy used")
elif result.strategy_name == "Mixed":
    print("Mixed strategy used")
```

**After (v2.0)**:
```python
if result.strategy_used == "code_aware":
    print("Code-aware strategy used (handles both code and mixed)")
```

### Step 6: Update Error Handling

**Before (v1.x)**: 15+ error types
```python
from dify_markdown_chunker.errors import (
    ChunkingError,
    ConfigError,
    ParserError,
    StrategyError,
    ValidationError,
    # ... 10+ more error types
)
```

**After (v2.0)**: 4 consolidated error types
```python
from markdown_chunker_v2.types import (
    ChunkingError,          # Base error
    ConfigurationError,     # Config validation
    ParsingError,           # Parser failures
    ValidationError,        # Input validation
)
```

### Step 7: Update Advanced Usage

#### Custom Strategy Selection (v1.x)

**Before**:
```python
# v1.x allowed forcing specific strategies
chunker = MarkdownChunker(config, force_strategy="Code")
```

**After**:
```python
# v2.0 uses automatic selection based on content analysis
# To influence selection, adjust thresholds:

# Prefer structural strategy
config = ChunkConfig(structure_threshold=2)  # Lower threshold

# Prefer code-aware strategy
config = ChunkConfig(code_threshold=0.2)  # Lower threshold
```

#### Chunk Metadata (v1.x → v2.0)

**Before (v1.x)**:
```python
for chunk in result.chunks:
    strategy = chunk.metadata.get("strategy_type")
    phase = chunk.metadata.get("phase")
    merged = chunk.metadata.get("was_merged")
```

**After (v2.0)**:
```python
for chunk in result.chunks:
    strategy = chunk.metadata.get("strategy")  # Simpler
    chunk_type = chunk.metadata.get("chunk_type")  # "code", "table", "text"
    chunk_index = chunk.metadata.get("chunk_index")  # Auto-added
    total = chunk.metadata.get("total_chunks")  # Auto-added
```

## Common Migration Patterns

### Pattern 1: Simple Chunking

**Before (v1.x)**:
```python
from dify_markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk(text)
for chunk in result.chunks:
    process(chunk)
```

**After (v2.0)**:
```python
from markdown_chunker_v2 import chunk_markdown

result = chunk_markdown(text)
for chunk in result.chunks:
    process(chunk)
```

### Pattern 2: Custom Configuration

**Before (v1.x)**:
```python
config = ChunkConfig(
    max_chunk_size=2048,
    enable_phase2=True,
    atomic_threshold=0.9,
    merge_threshold=0.8
)
chunker = MarkdownChunker(config)
result = chunker.chunk(text)
```

**After (v2.0)**:
```python
config = ChunkConfig(
    max_chunk_size=2048,
    preserve_atomic_blocks=True
)
result = chunk_markdown(text, config)
```

### Pattern 3: Code Documentation

**Before (v1.x)**:
```python
config = ChunkConfig(
    max_chunk_size=6144,
    code_block_handling="preserve",
    preamble_extraction=True,
    overlap_size=300
)
```

**After (v2.0)**:
```python
# Use factory method
config = ChunkConfig.for_code_docs()

# Or customize
config = ChunkConfig(
    max_chunk_size=6144,
    code_threshold=0.2,
    overlap_size=300
)
```

### Pattern 4: Batch Processing

**Before (v1.x)**:
```python
chunker = MarkdownChunker(config)
for doc in documents:
    result = chunker.chunk(doc)
    store_chunks(result.chunks)
```

**After (v2.0)**:
```python
# Reuse config, recreate chunker each time (lightweight)
config = ChunkConfig.for_rag()
for doc in documents:
    result = chunk_markdown(doc, config)
    store_chunks(result.chunks)
```

## Verification Checklist

After migration, verify:

- [ ] All imports updated
- [ ] Configuration simplified (8 parameters or less)
- [ ] `total_chunks` → `chunk_count` updated
- [ ] `strategy_name` → `strategy_used` updated
- [ ] Error handling uses 4 new error types
- [ ] Tests updated and passing
- [ ] Results match expected behavior

## Troubleshooting

### Issue: Missing Configuration Parameters

**Problem**: v1.x code uses removed parameters

**Solution**: Most removed parameters were YAGNI - defaults work for 95% of cases
- Review [Configuration](#step-2-update-configuration) section
- Use factory methods: `for_rag()` or `for_code_docs()`
- If truly needed, file an issue

### Issue: Different Chunking Results

**Problem**: v2.0 produces different chunks than v1.x

**Explanation**: This is expected and intentional:
- Simplified strategies may chunk differently
- Phase 2 removed (was adding unnecessary complexity)
- Single-pass parser is more accurate

**Verification**: Run property tests to verify domain properties maintained

### Issue: Strategy Not Selected

**Problem**: Expected strategy not being used

**Solution**: Adjust thresholds:
```python
# For structural strategy
config = ChunkConfig(structure_threshold=2)  # Lower from default 3

# For code-aware strategy
config = ChunkConfig(code_threshold=0.2)  # Lower from default 0.3
```

### Issue: Performance Regression

**Problem**: v2.0 seems slower

**Investigation**:
1. Ensure using latest version
2. Check if you're creating new chunker instances unnecessarily
3. Run benchmarks (see Performance section)
4. File issue with reproducible test case

Expected: v2.0 should be 20-50% faster due to single-pass parser

## Getting Help

- **Documentation**: See [README_v2.md](README_v2.md)
- **Issues**: https://github.com/dify-ai/dify-markdown-chunker/issues
- **Discussions**: https://github.com/dify-ai/dify-markdown-chunker/discussions

## Feedback

Please report any migration issues or suggestions for improving this guide!
