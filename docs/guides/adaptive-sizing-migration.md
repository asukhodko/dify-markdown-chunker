# Adaptive Sizing Migration Guide

> **Version**: v2.0+  
> **Feature**: Adaptive Chunk Sizing  
> **Status**: Available (Opt-in)

This guide helps you migrate to adaptive chunk sizing, which automatically adjusts chunk sizes based on content complexity.

---

## Overview

### What is Adaptive Sizing?

Adaptive sizing automatically calculates optimal chunk sizes based on content complexity:

- **Code-heavy content** → Larger chunks (up to 1.5x base size)
- **Simple text** → Smaller chunks (down to 0.5x base size)
- **Mixed content** → Medium chunks (around base size)

### Why Use It?

✅ **Better Semantic Coherence**: Chunk sizes match content density  
✅ **Improved RAG Quality**: More context for complex content, less noise for simple content  
✅ **Automatic Optimization**: No manual size tuning needed  
✅ **Minimal Overhead**: <0.1% performance impact  

### When NOT to Use It?

❌ **Uniform sizes required**: Some RAG systems expect fixed chunk sizes  
❌ **Backward compatibility**: Existing chunk size expectations  
❌ **Simple uniform content**: No benefit if all content has similar complexity  

---

## Migration Steps

### Step 1: Basic Enable

**Before (Standard Chunking):**
```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=4096)
chunker = MarkdownChunker(config)
chunks = chunker.chunk(document)
```

**After (Adaptive Sizing):**
```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig(
    max_chunk_size=4096,
    use_adaptive_sizing=True  # ← Add this flag
)
chunker = MarkdownChunker(config)
chunks = chunker.chunk(document)
```

**Changes:**
- ✓ Adds 3 metadata fields: `adaptive_size`, `content_complexity`, `size_scale_factor`
- ✓ Chunk sizes now vary based on content (750-2250 chars by default)
- ✓ No breaking changes to existing code

---

### Step 2: Custom Configuration (Optional)

**Default Behavior:**
```python
# Default adaptive sizing settings
config = ChunkConfig(
    use_adaptive_sizing=True
    # Uses default AdaptiveSizeConfig:
    # - base_size=1500
    # - min_scale=0.5 (750 chars)
    # - max_scale=1.5 (2250 chars)
    # - code_weight=0.4, table_weight=0.3, list_weight=0.2, sentence_length_weight=0.1
)
```

**Custom Configuration:**
```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
from markdown_chunker_v2.config import AdaptiveSizeConfig

config = ChunkConfig(
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=2000,       # Higher base for technical content
        min_scale=0.8,        # Narrower range for more uniform sizes
        max_scale=1.2,
        code_weight=0.5,      # Prioritize code complexity
        table_weight=0.2,
        list_weight=0.2,
        sentence_length_weight=0.1
    )
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(document)
```

---

### Step 3: Using Configuration Profiles

**Quick Enable with Profiles:**
```python
# Enable adaptive sizing for code-heavy documents
config = ChunkConfig.for_code_heavy()
config.use_adaptive_sizing = True

# Enable adaptive sizing for structured documents
config = ChunkConfig.for_structured()
config.use_adaptive_sizing = True
```

---

## Configuration Tuning

### Tuning base_size

Choose `base_size` based on your typical content:

| Content Type | Recommended base_size | Reasoning |
|--------------|----------------------|-----------|
| Simple notes, blogs | 1000-1500 | Smaller chunks for simple content |
| Mixed documentation | 1500-2000 | Balanced for varied content |
| Technical docs | 1500-2000 | Larger chunks for complex content |
| Code-heavy | 2000-2500 | Maximum context for code |

**Example:**
```python
# For technical documentation
config = AdaptiveSizeConfig(base_size=2000)
```

### Tuning Scale Range

Adjust `min_scale` and `max_scale` based on content variance:

| Content Variance | min_scale | max_scale | Range | Use Case |
|------------------|-----------|-----------|-------|----------|
| Low (uniform) | 0.8 | 1.2 | 0.4x | Similar content throughout |
| Medium | 0.6 | 1.4 | 0.8x | Some variation |
| High | 0.5 | 1.5 | 1.0x | Mixed content (default) |
| Very high | 0.3 | 2.0 | 1.7x | Extreme variation |

**Example:**
```python
# For uniform content
config = AdaptiveSizeConfig(
    base_size=1500,
    min_scale=0.8,  # More uniform sizes
    max_scale=1.2
)
```

### Tuning Complexity Weights

Adjust weights to prioritize different content types:

**Default weights:**
```python
code_weight=0.4           # 40% - Code blocks
table_weight=0.3          # 30% - Tables
list_weight=0.2           # 20% - Lists
sentence_length_weight=0.1 # 10% - Sentence length
```

**For code-heavy documentation:**
```python
config = AdaptiveSizeConfig(
    code_weight=0.5,           # Increase code priority
    table_weight=0.2,
    list_weight=0.2,
    sentence_length_weight=0.1
)
```

**For data-heavy content:**
```python
config = AdaptiveSizeConfig(
    code_weight=0.2,
    table_weight=0.5,          # Increase table priority
    list_weight=0.2,
    sentence_length_weight=0.1
)
```

**For structured documentation:**
```python
config = AdaptiveSizeConfig(
    code_weight=0.3,
    table_weight=0.2,
    list_weight=0.4,           # Increase list priority
    sentence_length_weight=0.1
)
```

**Validation:** Weights must sum to 1.0 (±0.01 tolerance).

---

## Behavior Changes

### Chunk Size Distribution

**Before Adaptive Sizing:**
```
All chunks: ~4000 chars (± merging/splitting)
```

**After Adaptive Sizing (base_size=1500):**
```
Simple chunks:   750-1050 chars  (complexity 0.0-0.2)
Mixed chunks:   1350-1650 chars  (complexity 0.4-0.6)
Complex chunks: 2100-2250 chars  (complexity 0.8-1.0)
```

### Metadata Changes

**New Fields Added:**

| Field | Type | Description |
|-------|------|-------------|
| `adaptive_size` | `int` | Calculated optimal chunk size |
| `content_complexity` | `float` | Complexity score 0.0-1.0 |
| `size_scale_factor` | `float` | Applied scaling factor |

**Example:**
```python
chunks = chunker.chunk(document)

for chunk in chunks:
    if 'adaptive_size' in chunk.metadata:
        print(f"Complexity: {chunk.metadata['content_complexity']:.2f}")
        print(f"Adaptive Size: {chunk.metadata['adaptive_size']} chars")
        print(f"Actual Size: {len(chunk.content)} chars")
```

**Note:** `adaptive_size` is the calculated optimal size. Actual chunk size may differ due to:
- Atomic block preservation (code blocks, tables)
- Header boundaries
- Min/max size constraints

---

## Testing Your Migration

### Step 1: Test with Sample Document

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
from markdown_chunker_v2.config import AdaptiveSizeConfig

# Your document
document = """
# Technical Guide

Simple introduction text.

## Code Example

```python
def example():
    pass
```

## Summary

Short conclusion.
"""

# Test with adaptive sizing
config = ChunkConfig(
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(base_size=1500)
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(document)

# Analyze results
for i, chunk in enumerate(chunks):
    meta = chunk.metadata
    print(f"\nChunk {i}:")
    print(f"  Size: {len(chunk.content)} chars")
    print(f"  Complexity: {meta.get('content_complexity', 'N/A')}")
    print(f"  Scale Factor: {meta.get('size_scale_factor', 'N/A')}")
    print(f"  Header: {meta.get('header_path', 'N/A')}")
```

### Step 2: Compare Before/After

```python
# Before: Standard chunking
config_before = ChunkConfig(max_chunk_size=4096)
chunker_before = MarkdownChunker(config_before)
chunks_before = chunker_before.chunk(document)

# After: Adaptive sizing
config_after = ChunkConfig(
    max_chunk_size=4096,
    use_adaptive_sizing=True
)
chunker_after = MarkdownChunker(config_after)
chunks_after = chunker_after.chunk(document)

# Compare
print(f"Chunks before: {len(chunks_before)}")
print(f"Chunks after: {len(chunks_after)}")

print("\nSize distribution before:")
for c in chunks_before:
    print(f"  {len(c.content)} chars")

print("\nSize distribution after:")
for c in chunks_after:
    complexity = c.metadata.get('content_complexity', 0)
    print(f"  {len(c.content)} chars (complexity: {complexity:.2f})")
```

### Step 3: Verify Performance

```python
import time

# Measure without adaptive sizing
start = time.perf_counter()
for _ in range(100):
    chunker_before.chunk(document)
time_before = (time.perf_counter() - start) / 100

# Measure with adaptive sizing
start = time.perf_counter()
for _ in range(100):
    chunker_after.chunk(document)
time_after = (time.perf_counter() - start) / 100

# Calculate overhead
overhead_pct = ((time_after - time_before) / time_before) * 100
print(f"Performance overhead: {overhead_pct:.2f}%")
print(f"Expected: <0.1% (should be negligible)")
```

---

## Common Issues

### Issue 1: Weights Don't Sum to 1.0

**Error:**
```
ValueError: Weights must sum to 1.0 (current sum: 0.9)
```

**Solution:**
Ensure weights sum to exactly 1.0:
```python
config = AdaptiveSizeConfig(
    code_weight=0.4,
    table_weight=0.3,
    list_weight=0.2,
    sentence_length_weight=0.1  # Sum = 1.0 ✓
)
```

### Issue 2: Scale Range Invalid

**Error:**
```
ValueError: min_scale (1.2) must be < max_scale (1.0)
```

**Solution:**
Ensure `min_scale` < `max_scale`:
```python
config = AdaptiveSizeConfig(
    min_scale=0.5,  # Must be less than max_scale
    max_scale=1.5
)
```

### Issue 3: Unexpected Chunk Sizes

**Problem:** Chunks are not sized as expected.

**Debugging:**
```python
# Check adaptive size vs actual size
for chunk in chunks:
    adaptive = chunk.metadata.get('adaptive_size', 'N/A')
    actual = len(chunk.content)
    complexity = chunk.metadata.get('content_complexity', 'N/A')
    
    print(f"Adaptive: {adaptive}, Actual: {actual}, Complexity: {complexity}")
    
    if actual > adaptive * 1.5:
        print("  → Likely atomic block (code/table) preserved")
    elif actual < adaptive * 0.5:
        print("  → Likely forced merge due to min_chunk_size")
```

**Causes:**
- Atomic blocks (code, tables) preserved intact
- Section boundaries respected
- `min_chunk_size` / `max_chunk_size` constraints

---

## Rollback Plan

### Disabling Adaptive Sizing

If you need to rollback:

```python
# Simply set use_adaptive_sizing=False
config = ChunkConfig(
    max_chunk_size=4096,
    use_adaptive_sizing=False  # Disable
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(document)

# Or use default config
config = ChunkConfig.default()  # use_adaptive_sizing=False by default
```

**Effect:**
- Returns to standard chunking behavior
- No adaptive sizing metadata fields
- Chunk sizes return to previous distribution

---

## Performance Expectations

### Overhead Measurements

| Metric | Measured Value | Target | Status |
|--------|----------------|--------|--------|
| Size Calculation | 0.1% | < 5% | ✓ Exceeds |
| Chunking Time | -0.1% | < 5% | ✓ Negligible |
| Memory Overhead | 17.4% metadata | < 20% | ✓ Acceptable |

**Conclusion:** Adaptive sizing has negligible performance impact.

### Scalability

Adaptive sizing maintains linear scaling:

| Document Size | Overhead | Notes |
|---------------|----------|-------|
| 1-10 KB | <0.1% | Negligible |
| 10-100 KB | <0.1% | Negligible |
| 100KB-1MB | <0.2% | Still negligible |

---

## Best Practices

### 1. Start with Defaults

```python
# Start simple
config = ChunkConfig(use_adaptive_sizing=True)
```

Only customize if needed.

### 2. Test on Representative Corpus

Before deploying:

```python
# Test on your actual documents
import os

test_docs = [
    "docs/technical_guide.md",
    "docs/simple_readme.md",
    "docs/code_heavy.md"
]

for doc_path in test_docs:
    with open(doc_path) as f:
        document = f.read()
    
    chunks = chunker.chunk(document)
    
    complexities = [c.metadata.get('content_complexity', 0) for c in chunks]
    avg_complexity = sum(complexities) / len(complexities)
    
    print(f"{doc_path}: {len(chunks)} chunks, avg complexity: {avg_complexity:.2f}")
```

### 3. Monitor Complexity Distribution

Track whether complexity scores make sense:

```python
complexities = [c.metadata.get('content_complexity', 0) for c in chunks]

print(f"Min complexity: {min(complexities):.2f}")
print(f"Max complexity: {max(complexities):.2f}")
print(f"Avg complexity: {sum(complexities)/len(complexities):.2f}")

# Should see reasonable distribution (0.0-1.0)
# If all chunks have similar complexity, adaptive sizing may not help
```

### 4. Tune for Your Use Case

If default behavior doesn't match expectations:

```python
# Analyze what's driving complexity
for chunk in chunks:
    meta = chunk.metadata
    if 'content_complexity' in meta:
        print(f"Complexity: {meta['content_complexity']:.2f}")
        
        # Check content analysis for this chunk's section
        # (you may need to run separate analysis)
        # Then adjust weights accordingly
```

---

## FAQs

### Q: Will this break my existing RAG pipeline?

**A:** No. Adaptive sizing is backward compatible:
- Disabled by default (`use_adaptive_sizing=False`)
- Chunk structure unchanged (same `Chunk` class)
- Only adds optional metadata fields

### Q: Can I use adaptive sizing with overlap?

**A:** Yes. Adaptive sizing and overlap are independent:
```python
config = ChunkConfig(
    use_adaptive_sizing=True,
    overlap_size=200  # Both work together
)
```

### Q: Does adaptive sizing work with all strategies?

**A:** Yes. Adaptive sizing works with:
- CodeAwareStrategy
- StructuralStrategy  
- FallbackStrategy

### Q: How do I choose base_size?

**A:** Start with defaults (1500). If chunks are consistently too small/large:
- Increase `base_size` for larger chunks
- Decrease `base_size` for smaller chunks

Don't adjust `min_scale`/`max_scale` unless you want to change the variance.

### Q: What if my content has uniform complexity?

**A:** Adaptive sizing still works but provides minimal benefit. All chunks will receive similar scale factors (~1.0). Consider disabling if all chunks have complexity 0.4-0.6.

---

## See Also

- [AdaptiveSizeConfig API](../api/config.md#class-adaptivesizeconfig) - Complete API reference
- [Chunk Metadata](../api/chunk_metadata.md#adaptive-sizing-fields) - Metadata field documentation
- [Performance Guide](performance.md#adaptive-sizing-performance) - Performance benchmarks
- [Configuration Reference](../reference/configuration.md) - All configuration options

---

**Last Updated**: December 2025  
**Feature Version**: v2.0+  
**Status**: Production Ready
