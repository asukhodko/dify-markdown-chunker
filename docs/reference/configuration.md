# Configuration Guide

## 🎯 Overview

The Advanced Markdown Chunker plugin provides configuration through two levels:
1. **Plugin UI Parameters** - Simple configuration through Dify's tool interface
2. **Direct chunkana Configuration** - Advanced configuration for direct library usage

## 📋 Plugin UI Configuration

### Available Parameters

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

### Parameter Details

#### Basic Parameters

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| `max_chunk_size` | number | 4096 | 512-16384 | Maximum chunk size in characters |
| `chunk_overlap` | number | 200 | 0-35% of chunk_size | Overlap between consecutive chunks |
| `strategy` | select | auto | auto, code_aware, list_aware, structural, fallback | Chunking strategy selection |

#### Metadata and Output Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `include_metadata` | boolean | true | Embed metadata block in chunk text |
| `enable_hierarchy` | boolean | false | Create parent-child relationships between chunks |
| `debug` | boolean | false | Include all chunk types (root, intermediate, leaf) |
| `leaf_only` | boolean | false | Return only leaf chunks (content only, no headers) |

### Configuration Examples

#### Basic RAG Configuration

```yaml
- node: chunk_for_rag
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    chunk_overlap: 100
    strategy: auto
    include_metadata: true
```

#### Hierarchical Processing

```yaml
- node: hierarchical_chunks
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 4096
    enable_hierarchy: true
    leaf_only: true  # Only content chunks for vector DB
    debug: false
```

#### Code Documentation Processing

```yaml
- node: code_docs_chunks
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 6144  # Larger chunks for code
    chunk_overlap: 200
    strategy: code_aware
    include_metadata: true
```

#### Clean Text Output

```yaml
- node: clean_text_chunks
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    chunk_overlap: 100
    include_metadata: false  # No metadata embedding
```

## 🔧 Direct chunkana Configuration

For advanced features not available in the plugin UI, use chunkana directly:

### Basic Configuration

```python
from chunkana import MarkdownChunker, ChunkConfig

# Basic configuration
config = ChunkConfig(
    max_chunk_size=4096,
    min_chunk_size=512,
    overlap_size=200,
    include_metadata=True,
    preserve_atomic_blocks=True
)

chunker = MarkdownChunker(config)
```

### Advanced Configuration

```python
from chunkana import ChunkConfig, AdaptiveSizeConfig, TableGroupingConfig

# Advanced configuration with all features
config = ChunkConfig(
    # Size control
    max_chunk_size=4096,
    min_chunk_size=512,
    overlap_size=200,
    
    # Strategy control
    strategy_override=None,  # None = auto-select
    code_threshold=0.3,
    structure_threshold=3,
    list_ratio_threshold=0.40,
    list_count_threshold=5,
    
    # Advanced features (not in plugin UI)
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=1500,
        min_scale=0.5,
        max_scale=1.5,
        code_weight=0.4,
        table_weight=0.3,
        list_weight=0.2,
        sentence_length_weight=0.1
    ),
    
    # Code-context binding
    enable_code_context_binding=True,
    max_context_chars_before=500,
    max_context_chars_after=300,
    bind_output_blocks=True,
    preserve_before_after_pairs=True,
    
    # Table grouping
    group_related_tables=True,
    table_grouping_config=TableGroupingConfig(
        max_distance_lines=10,
        max_grouped_tables=5,
        max_group_size=5000,
        require_same_section=True
    ),
    
    # Hierarchy
    enable_hierarchy=False,
    debug_mode=False,
    leaf_only=False,
    
    # Performance
    enable_streaming=False,
    streaming_config=None
)
```

### Configuration Profiles

```python
from chunkana import ChunkConfig

# Predefined profiles
config = ChunkConfig.for_code_heavy()      # Code documentation
config = ChunkConfig.for_dify_rag()        # Matches plugin defaults
config = ChunkConfig.for_search_indexing() # Search optimization
config = ChunkConfig.minimal()             # Minimal processing
```

## 📊 Parameter Mapping: Plugin → chunkana

### Direct Mappings

| Plugin Parameter | chunkana Config | Notes |
|------------------|-----------------|-------|
| `max_chunk_size` | `max_chunk_size` | Direct 1:1 mapping |
| `chunk_overlap` | `overlap_size` | Plugin caps at 35% of chunk size |
| `include_metadata` | `include_metadata` | Direct 1:1 mapping |
| `enable_hierarchy` | `enable_hierarchy` | Direct 1:1 mapping |
| `debug` | `debug_mode` | Direct 1:1 mapping |
| `leaf_only` | `leaf_only` | Direct 1:1 mapping |

### Strategy Mapping

| Plugin Value | chunkana Config | Behavior |
|--------------|-----------------|----------|
| `auto` | `strategy_override=None` | Automatic selection based on content |
| `code_aware` | `strategy_override="code_aware"` | Force code-aware strategy |
| `list_aware` | `strategy_override="list_aware"` | Force list-aware strategy |
| `structural` | `strategy_override="structural"` | Force structural strategy |
| `fallback` | `strategy_override="fallback"` | Force fallback strategy |

### Advanced Features (chunkana Only)

Features available only through direct chunkana usage:

```python
# Adaptive chunk sizing
config.use_adaptive_sizing = True
config.adaptive_config = AdaptiveSizeConfig(...)

# Code-context binding
config.enable_code_context_binding = True
config.preserve_before_after_pairs = True

# Table grouping
config.group_related_tables = True
config.table_grouping_config = TableGroupingConfig(...)

# Streaming processing
config.enable_streaming = True
config.streaming_config = StreamingConfig(...)

# Custom strategy thresholds
config.code_threshold = 0.25
config.list_ratio_threshold = 0.35
```

## 🎯 Configuration Patterns

### Environment-Based Configuration

```python
import os
from chunkana import ChunkConfig

def create_config_from_env() -> ChunkConfig:
    """Create configuration from environment variables."""
    return ChunkConfig(
        max_chunk_size=int(os.getenv("CHUNK_SIZE", "4096")),
        overlap_size=int(os.getenv("CHUNK_OVERLAP", "200")),
        include_metadata=os.getenv("INCLUDE_METADATA", "true").lower() == "true",
        strategy_override=os.getenv("STRATEGY_OVERRIDE", None)
    )

config = create_config_from_env()
```

### Content-Adaptive Configuration

```python
from chunkana import MarkdownChunker, ChunkConfig

def adaptive_config(md_text: str) -> ChunkConfig:
    """Create configuration based on content analysis."""
    # Quick analysis
    chunker = MarkdownChunker()
    analysis = chunker.analyze_content(md_text)
    
    if analysis.code_ratio > 0.5:
        # Code-heavy document
        return ChunkConfig(
            max_chunk_size=6144,  # Larger chunks for code
            strategy_override="code_aware",
            enable_code_context_binding=True,
            preserve_before_after_pairs=True
        )
    elif analysis.list_ratio > 0.4:
        # List-heavy document
        return ChunkConfig(
            strategy_override="list_aware",
            list_ratio_threshold=0.35  # Lower threshold
        )
    elif analysis.table_count > 3:
        # Table-heavy document
        return ChunkConfig(
            group_related_tables=True,
            table_grouping_config=TableGroupingConfig(
                max_distance_lines=15,
                require_same_section=True
            )
        )
    else:
        # Standard document
        return ChunkConfig.for_dify_rag()

# Use adaptive configuration
config = adaptive_config(markdown_text)
chunker = MarkdownChunker(config)
```

### Performance-Optimized Configuration

```python
# Fast processing (minimal features)
fast_config = ChunkConfig(
    max_chunk_size=2048,
    overlap_size=0,  # No overlap
    include_metadata=False,
    strategy_override="fallback",  # Fastest strategy
    use_adaptive_sizing=False,
    enable_code_context_binding=False,
    group_related_tables=False
)

# Quality processing (all features)
quality_config = ChunkConfig(
    max_chunk_size=4096,
    overlap_size=200,
    include_metadata=True,
    use_adaptive_sizing=True,
    enable_code_context_binding=True,
    group_related_tables=True,
    enable_hierarchy=True
)
```

## 📁 Configuration Files

### JSON Configuration

```python
import json
from chunkana import ChunkConfig

def load_config_from_json(file_path: str) -> ChunkConfig:
    """Load configuration from JSON file."""
    with open(file_path, 'r') as f:
        config_data = json.load(f)
    
    return ChunkConfig(**config_data)

# Example JSON configuration
config_json = {
    "max_chunk_size": 4096,
    "overlap_size": 200,
    "include_metadata": True,
    "strategy_override": None,
    "use_adaptive_sizing": True,
    "enable_code_context_binding": True,
    "group_related_tables": True,
    "adaptive_config": {
        "base_size": 1500,
        "min_scale": 0.5,
        "max_scale": 1.5
    },
    "table_grouping_config": {
        "max_distance_lines": 10,
        "require_same_section": True
    }
}
```

### YAML Configuration

```yaml
# chunkana_config.yaml
max_chunk_size: 4096
overlap_size: 200
include_metadata: true
strategy_override: null

# Advanced features
use_adaptive_sizing: true
adaptive_config:
  base_size: 1500
  min_scale: 0.5
  max_scale: 1.5
  code_weight: 0.4
  table_weight: 0.3
  list_weight: 0.2
  sentence_length_weight: 0.1

enable_code_context_binding: true
max_context_chars_before: 500
preserve_before_after_pairs: true

group_related_tables: true
table_grouping_config:
  max_distance_lines: 10
  max_grouped_tables: 5
  require_same_section: true

# Strategy thresholds
code_threshold: 0.3
list_ratio_threshold: 0.40
list_count_threshold: 5
```

## 🔍 Configuration Validation

### Plugin Parameter Validation

The plugin automatically validates parameters:

```yaml
# This will be rejected
config:
  max_chunk_size: 100  # Too small (minimum 512)
  chunk_overlap: 2000  # Too large (max 35% of chunk_size)
```

### chunkana Configuration Validation

```python
from chunkana import ChunkConfig, ConfigValidationError

try:
    config = ChunkConfig(
        max_chunk_size=100,  # Invalid: too small
        overlap_size=5000    # Invalid: larger than chunk size
    )
    config.validate()
except ConfigValidationError as e:
    print(f"Configuration error: {e}")
    print(f"Suggestions: {e.suggestions}")
```

## 📊 Configuration Impact

### Performance Comparison

| Configuration | Processing Speed | Memory Usage | Feature Completeness |
|---------------|------------------|--------------|---------------------|
| Plugin UI (basic) | Fast | Low | Medium |
| Plugin UI (hierarchical) | Medium | Medium | Medium-High |
| chunkana (minimal) | Very Fast | Very Low | Low |
| chunkana (full features) | Medium | Medium | Very High |

### Feature Matrix

| Feature | Plugin UI | Direct chunkana |
|---------|-----------|-----------------|
| Basic chunking | ✅ | ✅ |
| Strategy selection | ✅ (5 strategies) | ✅ (5 strategies + custom) |
| Overlap control | ✅ (capped) | ✅ (full control) |
| Metadata embedding | ✅ | ✅ |
| Hierarchical chunking | ✅ (basic) | ✅ (full navigation) |
| Adaptive sizing | ❌ | ✅ |
| Code-context binding | ❌ | ✅ |
| Table grouping | ❌ | ✅ |
| Streaming processing | ❌ | ✅ |
| Custom strategies | ❌ | ✅ |
| Performance monitoring | ❌ | ✅ |

## 🎯 Best Practices

### Plugin UI Configuration

1. **Start with defaults**: Default parameters work well for most RAG use cases
2. **Use hierarchical mode carefully**: Only enable when you need parent-child relationships
3. **Consider chunk_overlap cap**: Plugin caps overlap at 35% of chunk size
4. **Use leaf_only for vector DB**: Filters out structural headers

### Direct chunkana Configuration

1. **Profile-based approach**: Start with predefined profiles
2. **Content-adaptive**: Analyze content to choose optimal configuration
3. **Performance vs features**: Balance processing speed with feature completeness
4. **Validation**: Always validate configurations before production use
5. **Environment-specific**: Use different configs for dev/test/prod

### Common Patterns

```python
# Development: Full features for testing
dev_config = ChunkConfig(
    use_adaptive_sizing=True,
    enable_code_context_binding=True,
    group_related_tables=True,
    debug_mode=True
)

# Production: Optimized for performance
prod_config = ChunkConfig(
    max_chunk_size=2048,
    overlap_size=100,
    include_metadata=True,
    strategy_override=None,  # Auto-select
    use_adaptive_sizing=False  # Consistent sizing
)

# Vector DB indexing: Content chunks only
vector_config = ChunkConfig(
    enable_hierarchy=True,
    leaf_only=True,
    include_metadata=True,
    debug_mode=False
)
```

## 🆘 Troubleshooting

### Common Configuration Issues

**Issue**: Chunks too large/small
**Solution**: Adjust `max_chunk_size` or enable adaptive sizing

**Issue**: Missing context between chunks
**Solution**: Increase `chunk_overlap` (plugin) or `overlap_size` (chunkana)

**Issue**: Code blocks split incorrectly
**Solution**: Use `strategy: code_aware` or enable code-context binding

**Issue**: Need advanced features
**Solution**: Use chunkana directly instead of plugin UI

### Configuration Debugging

```python
# Debug configuration impact
config = ChunkConfig(debug_mode=True)
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)

print(f"Strategy used: {result.strategy_used}")
print(f"Config applied: {result.config_summary}")
print(f"Performance: {result.processing_time:.3f}s")
```