# ChunkConfig API

Complete API documentation for the ChunkConfig class (v2.0).

## Overview

`ChunkConfig` controls chunking behavior and strategy selection. In v2.0, configuration was simplified from 32 parameters to 8 core parameters.

## Class: ChunkConfig

### Import

```python
from markdown_chunker_v2 import ChunkConfig
# For adaptive sizing
from markdown_chunker_v2.config import AdaptiveSizeConfig
```

### Constructor

```python
ChunkConfig(
    max_chunk_size: int = 4096,
    min_chunk_size: int = 512,
    overlap_size: int = 200,
    preserve_atomic_blocks: bool = True,
    extract_preamble: bool = True,
    code_threshold: float = 0.3,
    structure_threshold: int = 3,
    strategy_override: Optional[str] = None,
    use_adaptive_sizing: bool = False,
    adaptive_config: Optional[AdaptiveSizeConfig] = None
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_chunk_size` | int | 4096 | Maximum chunk size in characters |
| `min_chunk_size` | int | 512 | Minimum chunk size in characters |
| `overlap_size` | int | 200 | Overlap size (0 = disabled) |
| `preserve_atomic_blocks` | bool | True | Keep code blocks and tables intact |
| `extract_preamble` | bool | True | Extract content before first header |
| `code_threshold` | float | 0.3 | Code ratio threshold for CodeAwareStrategy |
| `structure_threshold` | int | 3 | Min headers for StructuralStrategy |
| `strategy_override` | str | None | Force strategy: "code_aware", "structural", "fallback" |
| `use_adaptive_sizing` | bool | False | Enable adaptive chunk sizing based on content complexity |
| `adaptive_config` | AdaptiveSizeConfig | None | Adaptive sizing configuration (uses defaults if not provided) |

**Example:**
```python
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    overlap_size=100,
    use_adaptive_sizing=True  # Enable adaptive sizing
)
```

---

## Class: AdaptiveSizeConfig

### Overview

`AdaptiveSizeConfig` controls adaptive chunk sizing behavior. When enabled, the chunker automatically adjusts chunk sizes based on content complexity.

### Import

```python
from markdown_chunker_v2.config import AdaptiveSizeConfig
```

### Constructor

```python
AdaptiveSizeConfig(
    base_size: int = 1500,
    min_scale: float = 0.5,
    max_scale: float = 1.5,
    code_weight: float = 0.4,
    table_weight: float = 0.3,
    list_weight: float = 0.2,
    sentence_length_weight: float = 0.1
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_size` | int | 1500 | Base chunk size for medium complexity content |
| `min_scale` | float | 0.5 | Minimum scaling factor (0.5 = 50% of base_size) |
| `max_scale` | float | 1.5 | Maximum scaling factor (1.5 = 150% of base_size) |
| `code_weight` | float | 0.4 | Weight for code ratio in complexity calculation |
| `table_weight` | float | 0.3 | Weight for table ratio in complexity calculation |
| `list_weight` | float | 0.2 | Weight for list ratio in complexity calculation |
| `sentence_length_weight` | float | 0.1 | Weight for avg sentence length in complexity calculation |

**Validation Rules:**

- `base_size` must be between 500 and 10000
- `min_scale` must be between 0.1 and 1.0
- `max_scale` must be between 1.0 and 3.0
- `min_scale` must be < `max_scale`
- All weights must sum to 1.0 (±0.01 tolerance)
- All weights must be non-negative

**Example:**
```python
from markdown_chunker_v2.config import AdaptiveSizeConfig

config = AdaptiveSizeConfig(
    base_size=1500,
    min_scale=0.5,
    max_scale=1.5,
    code_weight=0.4,
    table_weight=0.3,
    list_weight=0.2,
    sentence_length_weight=0.1
)
```

### How It Works

1. **Content Analysis**: The chunker analyzes content complexity:
   - Code ratio (percentage of code blocks)
   - Table ratio (percentage of tables)
   - List ratio (percentage of lists)
   - Average sentence length

2. **Complexity Calculation**: Weighted sum of factors:
   ```
   complexity = (code_ratio × code_weight) + 
                (table_ratio × table_weight) + 
                (list_ratio × list_weight) + 
                (sentence_length_norm × sentence_length_weight)
   ```
   Result: 0.0 (simple) to 1.0 (complex)

3. **Scale Factor**: Linear interpolation between min_scale and max_scale:
   ```
   scale_factor = min_scale + (complexity × (max_scale - min_scale))
   ```

4. **Adaptive Size**: Apply scale to base size:
   ```
   adaptive_size = base_size × scale_factor
   ```

### Behavior Examples

| Content Type | Complexity | Scale Factor | Adaptive Size (base=1500) |
|--------------|------------|--------------|---------------------------|
| Simple text, short sentences | 0.0 | 0.5 | 750 chars |
| Mixed content | 0.5 | 1.0 | 1500 chars |
| Code-heavy documentation | 1.0 | 1.5 | 2250 chars |

### Performance Impact

- Size calculation overhead: **<0.1%** (negligible)
- Chunking time impact: **<0.1%** (negligible)
- Memory overhead: **17.4%** metadata (3 additional fields per chunk)

See [Performance Guide](../guides/performance.md#adaptive-sizing-performance) for details.

### Tuning Recommendations

**Adjust base_size:**
- Lower (1000-1500) for simple content
- Higher (1500-2000) for technical content

**Adjust scale range:**
- Narrow (0.8-1.2) for similar content
- Wide (0.5-1.5) for mixed content

**Adjust complexity weights:**
- Increase `code_weight` (0.5) for technical docs
- Increase `table_weight` (0.4) for data-heavy content
- Increase `list_weight` (0.3) for structured content
- Decrease `sentence_length_weight` (0.05) if not relevant

---

## Configuration Profiles

Pre-configured profiles for common use cases.

### default()

```python
ChunkConfig.default() -> ChunkConfig
```

Default configuration for general use.

**Settings:**
- max_chunk_size: 4096
- min_chunk_size: 512
- overlap_size: 200

### for_code_heavy()

```python
ChunkConfig.for_code_heavy() -> ChunkConfig
```

Optimized for code-heavy documentation.

**Settings:**
- max_chunk_size: 8192
- min_chunk_size: 1024
- overlap_size: 100
- code_threshold: 0.2

**Example:**
```python
config = ChunkConfig.for_code_heavy()
```

### for_structured()

```python
ChunkConfig.for_structured() -> ChunkConfig
```

Optimized for structured documents with headers.

**Settings:**
- max_chunk_size: 4096
- min_chunk_size: 512
- overlap_size: 200
- structure_threshold: 2

**Example:**
```python
config = ChunkConfig.for_structured()
```

### minimal()

```python
ChunkConfig.minimal() -> ChunkConfig
```

Minimal configuration with small chunks.

**Settings:**
- max_chunk_size: 1024
- min_chunk_size: 256
- overlap_size: 50

**Example:**
```python
config = ChunkConfig.minimal()
```

## Serialization

### to_dict()

```python
config.to_dict() -> dict
```

Serialize config to dictionary.

**Example:**
```python
config = ChunkConfig(max_chunk_size=2048)
data = config.to_dict()
# {'max_chunk_size': 2048, 'min_chunk_size': 512, ...}
```

### from_dict()

```python
ChunkConfig.from_dict(data: dict) -> ChunkConfig
```

Create config from dictionary.

**Example:**
```python
data = {'max_chunk_size': 2048, 'overlap_size': 100}
config = ChunkConfig.from_dict(data)
```

### from_legacy()

```python
ChunkConfig.from_legacy(**kwargs) -> ChunkConfig
```

Create config from legacy v1.x parameters with deprecation warnings.

**Example:**
```python
# Migrating from v1.x
config = ChunkConfig.from_legacy(
    max_size=2048,  # renamed to max_chunk_size
    enable_overlap=True,  # removed, use overlap_size > 0
    overlap_size=100
)
```

## Usage Examples

### Basic Configuration

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

config = ChunkConfig(max_chunk_size=2048)
chunker = MarkdownChunker(config)
```

### With Overlap

```python
config = ChunkConfig(
    max_chunk_size=2048,
    overlap_size=100  # 0 = disabled
)
```

### Force Strategy

```python
# Force code-aware strategy
config = ChunkConfig(strategy_override="code_aware")

# Force structural strategy
config = ChunkConfig(strategy_override="structural")

# Force fallback strategy
config = ChunkConfig(strategy_override="fallback")
```

### Using Profiles

```python
# For code documentation
config = ChunkConfig.for_code_heavy()

# For structured documents
config = ChunkConfig.for_structured()

# For small chunks
config = ChunkConfig.minimal()
```

## Properties

### enable_overlap

```python
config.enable_overlap -> bool
```

Returns True if overlap is enabled (overlap_size > 0).

## Validation

ChunkConfig validates parameters on creation:

- `max_chunk_size` must be positive
- `min_chunk_size` must be positive
- `min_chunk_size` is auto-adjusted if > `max_chunk_size`
- `overlap_size` must be non-negative
- `overlap_size` must be < `max_chunk_size`
- `code_threshold` must be between 0 and 1
- `structure_threshold` must be >= 1
- `strategy_override` must be one of: "code_aware", "structural", "fallback", or None

## Migration from v1.x

| v1.x Parameter | v2.0 Equivalent |
|----------------|-----------------|
| `max_size` | `max_chunk_size` |
| `min_size` | `min_chunk_size` |
| `enable_overlap` | Use `overlap_size > 0` |
| `force_strategy` | `strategy_override` |
| `preserve_code_blocks` | Always enabled |
| `preserve_tables` | Always enabled |

See [Migration Guide](../MIGRATION.md) for full details.

## See Also

- [MarkdownChunker API](chunker.md) - Main chunking class
- [Chunking Strategies](../architecture/strategies.md) - Strategy details
- [Migration Guide](../MIGRATION.md) - Migration from v1.x
