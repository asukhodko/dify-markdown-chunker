# Migration Analysis: Current Plugin Structure

## Task 1.1: Pre-Migration Analysis Complete

This document captures the current plugin structure and dependencies before migration to chunkana 0.1.0.

### Current Tool Schema Parameters

From `tools/markdown_chunk_tool.yaml`:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_text` | string | true | - | The Markdown text content to be chunked |
| `max_chunk_size` | number | false | 4096 | Maximum size of each chunk in characters |
| `chunk_overlap` | number | false | 200 | Characters to overlap between chunks |
| `strategy` | select | false | "auto" | Chunking strategy (auto, code_aware, list_aware, structural, fallback) |
| `include_metadata` | boolean | false | true | Embed metadata in chunk text |
| `enable_hierarchy` | boolean | false | false | Create parent-child relationships between chunks |
| `debug` | boolean | false | false | Enable debug mode (includes all chunks when hierarchy=true) |

**Verification**: Parameters match exactly with `chunkana/tests/baseline/plugin_tool_params.json` ✅

### Current Dependencies

From `requirements.txt`:

**Core Dependencies:**
- `dify_plugin==0.7.0` - Dify plugin framework
- `markdown-it-py>=3.0.0` - Markdown parsing
- `pydantic>=2.0.0` - Data validation
- `PyYAML>=6.0.0` - YAML processing

**Embedded Chunker Dependencies:**
- `mistune>=3.0.0` - Markdown processing
- `markdown>=3.4.0` - Markdown processing
- `mdformat>=0.7.0` - Markdown formatting
- `markdown2>=2.4.0` - Alternative markdown processor
- `dataclasses-json>=0.6.0` - JSON serialization

**Testing Dependencies:**
- `pytest>=8.0.0` - Testing framework
- `hypothesis>=6.0.0` - Property-based testing

**Development Dependencies:**
- `pytest-cov>=4.1.0` - Coverage reporting
- `black>=23.7.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `flake8>=6.0.0` - Linting
- `mypy>=1.5.0` - Type checking

### Current Import Structure

From `tools/markdown_chunk_tool.py`:

**Current Imports:**
```python
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from markdown_chunker import MarkdownChunker, ChunkConfig  # ← EMBEDDED CODE
```

**Embedded Code Usage:**
- `MarkdownChunker` class instantiation
- `ChunkConfig` configuration object
- Direct usage of embedded `markdown_chunker_v2` module

### Current Implementation Structure

**Tool Implementation Pattern:**
1. Parameter extraction and validation
2. `ChunkConfig` creation with strategy mapping ("auto" → None)
3. `MarkdownChunker` instantiation
4. Conditional API selection:
   - `chunker.chunk_hierarchical()` if `enable_hierarchy=True`
   - `chunker.chunk()` if `enable_hierarchy=False`
5. Debug mode chunk filtering (hierarchical only)
6. Output formatting with metadata filtering
7. Result formatting as array of strings

**Key Behavioral Details:**
- Strategy mapping: `"auto"` → `strategy_override=None`
- Hierarchical mode: `debug=True` returns `result.chunks`, `debug=False` returns `result.get_flat_chunks()`
- Metadata filtering: `_filter_metadata_for_rag()` removes statistical fields in non-debug mode
- Output format: `include_metadata=True` uses `<metadata>` blocks, `include_metadata=False` embeds overlap

### Migration Readiness Assessment

**✅ Ready for Migration:**
- Tool schema parameters match chunkana baseline exactly
- Clear separation between tool logic and chunker logic
- Well-defined parameter mapping patterns
- Comprehensive error handling structure

**⚠️ Migration Considerations:**
- Multiple markdown processing dependencies may be redundant after migration
- Embedded code removal will require careful dependency cleanup
- Debug mode behavior needs snapshot verification
- Metadata filtering logic needs preservation

**📋 Next Steps:**
- Task 1.2: Set up testing infrastructure
- Task 1.3: Create pre-migration snapshot with parameter matrix
- Task 1.5: Make test data self-sufficient

### Configuration Defaults Analysis

**Current ChunkConfig Creation:**
```python
config = ChunkConfig(
    max_chunk_size=max_chunk_size,
    overlap_size=chunk_overlap,
    strategy_override=strategy_override,
)
```

**Note**: Only explicit parameters are set. All other ChunkConfig defaults are inherited from the embedded implementation. These defaults will be captured in the pre-migration snapshot (Task 1.3).

### Import Dependencies to Replace

**Runtime Imports to Remove:**
- `from markdown_chunker import MarkdownChunker, ChunkConfig`

**Runtime Imports to Add:**
- `from chunkana import chunk_markdown, chunk_hierarchical, ChunkerConfig`
- `from chunkana.renderers import render_dify_style, render_with_embedded_overlap`

**Analysis Complete**: Task 1.1 ✅