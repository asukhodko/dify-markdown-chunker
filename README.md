# 🔖 Advanced Markdown Chunker for Dify

<div align="center">

**Intelligent Markdown document chunking for RAG systems with structural awareness**

[![Version](https://img.shields.io/badge/version-2.1.5-orange.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/dify-1.9.0+-green.svg)](https://dify.ai/)
[![Tests](https://img.shields.io/badge/tests-812-brightgreen.svg)](#testing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Data & Privacy](#-data--privacy)
- [Installation](#-installation)
- [Dify Integration](#-dify-integration)
- [Quick Start](#-quick-start)
- [Chunking Strategies](#-chunking-strategies)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Performance](#-performance)
- [Development](#-development)
- [Contributing](#-contributing)
- [Author & Support](#-author--support)
- [License](#-license)

---

## Overview

**Advanced Markdown Chunker** is a Dify plugin that intelligently splits Markdown documents into semantically meaningful chunks optimized for RAG (Retrieval-Augmented Generation) systems. Unlike simple text splitting, it preserves document structure, keeps code blocks intact, and automatically selects the best chunking strategy based on content analysis.

### Primary Use Case: RAG Systems

This plugin is designed primarily for **RAG (Retrieval-Augmented Generation)** workflows where chunks are embedded and stored in vector databases for semantic search. By default, each chunk includes embedded metadata (header paths, content type, line numbers) directly in the chunk text, which improves retrieval quality by providing additional context for embeddings.

> **Note for Model Training:** If you need clean text without metadata (e.g., for fine-tuning language models), set `include_metadata: false` or post-process chunks to remove the `<metadata>` block.

### Why Use This Plugin?

| Simple Chunking Problems | Advanced Markdown Chunker Solution |
|--------------------------|-----------------------------------|
| Breaks code blocks mid-function | Preserves code blocks as atomic units |
| Loses header context | Maintains hierarchical section structure |
| Splits tables and lists | Keeps tables and lists intact |
| One-size-fits-all approach | 4 adaptive strategies based on content |
| No overlap support | Smart overlap for better retrieval |
| **Destroys list hierarchies** | **Smart list grouping with context binding** |
| **Breaks nested code examples** | **Handles nested fencing (````, ``````, ~~~~)** |
| **Code examples lose explanatory context** | **Enhanced code-context binding with pattern recognition** |
| **Before/After comparisons split apart** | **Intelligent Before/After pairing** |
| **Code and output separated** | **Automatic Code+Output binding** |
| **Mathematical formulas split** | **LaTeX formula preservation (`$$...$$`, environments)** |

---

## ✨ Features

### 🎯 Adaptive Chunking
- **4 intelligent strategies** — automatic selection based on content analysis
- **Adaptive Chunk Sizing** — automatic size optimization based on content complexity (new)
  - Code-heavy content → larger chunks (up to 1.5x base size)
  - Simple text → smaller chunks (down to 0.5x base size)
  - Configurable complexity weights and scaling bounds
  - Optional feature (disabled by default for backward compatibility)
- **Hierarchical Chunking** — parent-child relationships between chunks (new)
  - Multi-level retrieval support (overview vs. detail)
  - Programmatic navigation (siblings, ancestors, children)
  - O(1) chunk lookup performance
  - Backward compatible with flat chunking
- **Streaming Processing** — memory-efficient processing for large files (new)
  - Process files >10MB with <50MB RAM usage
  - Configurable buffer management (100KB default window)
  - Progress tracking support for long-running operations
  - Maintains quality through smart window boundary detection
- **List-Aware Strategy** — preserves nested list hierarchies and context (unique competitive advantage)
- **Nested Fencing Support** — correctly handles quadruple/quintuple backticks and tilde fencing for meta-documentation (unique capability)
- **Enhanced Code-Context Binding** — intelligently binds code blocks to explanations, recognizes Before/After patterns, Code+Output pairs, and sequential examples (unique competitive advantage)
- **LaTeX Formula Handling** — preserves mathematical formulas as atomic blocks (new)
  - Display math (`$$...$$`) never split across chunks
  - Environment blocks (`\begin{equation}`, `\begin{align}`) preserved complete
  - Supported in all 4 chunking strategies
  - Critical for scientific papers and technical documentation
- **Table Grouping Option** — groups related tables in same chunk for better retrieval (new)
  - Configurable proximity threshold (`max_distance_lines`)
  - Section boundary awareness (`require_same_section`)
  - Size and count limits (`max_group_size`, `max_grouped_tables`)
  - Perfect for API documentation with Parameters/Response/Error tables
- **Structure preservation** — headers, lists, tables, and code stay intact
- **Adaptive overlap** — context window scales with chunk size (up to 35%)

### 🔍 Deep Content Analysis
- **AST parsing** — full Markdown syntax analysis
- **Content type detection** — code-heavy, text-heavy, mixed
- **Complexity scoring** — optimizes strategy selection

### 🛡️ Reliability
- **812 tests** — comprehensive test coverage with property-based testing
- **Property-Based Testing** — formal correctness guarantees with Hypothesis
- **Automatic fallback** — graceful degradation on errors
- **Performance benchmarks** — automated performance regression detection

### 🔌 Integration
- **Dify Plugin** — ready-to-use in Dify workflows
- **Python Library** — standalone usage
- **REST API Ready** — adapters for API integration

---

## 🔒 Data & Privacy

**Local Processing Only**  
The Plugin processes all Markdown content locally within your Dify instance. No data is transmitted to external services.

**What the Plugin does:**
- ✅ Parses Markdown structure using local AST analysis
- ✅ Generates chunks based on document structure
- ✅ Adds metadata for improved retrieval quality

**What the Plugin does NOT do:**
- ❌ Send data to external APIs
- ❌ Store data outside of Dify's standard mechanisms
- ❌ Log or track user content
- ❌ Collect analytics or telemetry

For complete details, see [PRIVACY.md](PRIVACY.md).

---

## 📦 Installation

### Dify Plugin Installation

1. Download the `.difypkg` file from [Releases](https://github.com/asukhodko/dify-markdown-chunker/releases)
2. In Dify: **Settings → Plugins → Install Plugin**
3. Upload the `.difypkg` file
4. The plugin is now available in your workflows

**Requirements:**
- Dify version 1.9.0 or higher
- No additional configuration needed

### Development Installation

```bash
# Clone the repository
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
make test
```

**Requirements:**
- Python 3.12 or higher

---

## 🔌 Dify Integration

### Workflow Configuration

Add the chunker to your Dify workflow:

```yaml
- node: chunk_markdown
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
    chunk_overlap: 100
    include_metadata: true
```

### Plugin Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_text` | string | required | Markdown text to chunk |
| `max_chunk_size` | number | 4096 | Maximum chunk size in characters |
| `chunk_overlap` | number | 200 | Base overlap size (adaptive: actual max = min(overlap_size, chunk_size * 0.35)) |
| `strategy` | select | auto | Chunking strategy (auto/code_aware/list_aware/structural/fallback) |
| `include_metadata` | boolean | true | Embed metadata in chunk text (see below) |
| `enable_hierarchy` | boolean | false | Create parent-child relationships between chunks |
| `debug` | boolean | false | Include all chunks (root, intermediate, leaf) in hierarchical mode |
| `leaf_only` | boolean | false | Return only leaf chunks in hierarchical mode (recommended for vector DB) |

### Hierarchical Chunking Mode

When `enable_hierarchy=true`, the plugin returns chunks organized in a tree structure with parent-child relationships.

**Chunk Types:**

| Type | is_root | is_leaf | indexable | Description |
|------|---------|---------|-----------|-------------|
| Root | true | false | false | Document root, covers entire document |
| Internal | false | false | true | Section headers with children |
| Leaf | false | true | true | Content chunks for indexing |

**Filtering Behavior:**

- `debug=false` (default): Root chunk excluded from results
- `debug=true`: All chunks included for debugging
- `leaf_only=true`: Only leaf chunks returned (recommended for vector DB)

**Recommended Usage for Vector DB:**

```yaml
- node: chunk_for_indexing
  type: tool
  tool: advanced_markdown_chunker
  config:
    enable_hierarchy: true
    leaf_only: true  # Only indexable content chunks
```

**For Debugging Hierarchy:**

```yaml
- node: debug_hierarchy
  type: tool
  tool: advanced_markdown_chunker
  config:
    enable_hierarchy: true
    debug: true  # Include root and internal nodes
```

### Understanding `chunk_overlap`

**Chunk Overlap** controls how many characters of context are shared between consecutive chunks to preserve semantic continuity.

**Behavior depends on `include_metadata`:**

| `include_metadata` | Overlap Behavior |
|--------------------|------------------|
| `true` (default) | Overlap stored in metadata fields `previous_content` / `next_content`. Chunk content stays clean. |
| `false` | Overlap embedded directly into chunk text: `previous_content + "\n" + main + "\n" + next_content` |

**Example with `include_metadata: true`:**
```
<metadata>
{
  "previous_content": "...end of previous chunk...",
  "next_content": "...start of next chunk..."
}
</metadata>
# Current Section

Main content of this chunk...
```

**Example with `include_metadata: false`:**
```
...end of previous chunk...
# Current Section

Main content of this chunk...
...start of next chunk...
```

This allows `chunk_overlap` to work predictably in both modes:
- **RAG mode** (`include_metadata: true`): Overlap available as structured metadata for embeddings
- **Clean text mode** (`include_metadata: false`): Overlap physically present in text for sliding window processing

### Understanding `include_metadata`

When `include_metadata: true` (default), each chunk includes a `<metadata>` block prepended to the content:

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

**Typical metadata fields:**
- `content_type` — type of content (text, code, table, list, mixed)
- `header_path` — hierarchical path of section headers
- `start_line` / `end_line` — source line numbers
- `code_language` — programming language (for code blocks)
- `previous_content` / `next_content` — overlap context from adjacent chunks
- `adaptive_size` — calculated optimal chunk size (when adaptive sizing enabled) *new*
- `content_complexity` — complexity score 0.0-1.0 (when adaptive sizing enabled) *new*
- `size_scale_factor` — applied scaling factor (when adaptive sizing enabled) *new*
- `code_role` — code block role (example, setup, output, before, after, error)
- `has_related_code` — whether chunk contains related code blocks
- `code_relationship` — relationship type (before_after, code_output, sequential)
- `explanation_bound` — whether explanation is bound to code

**When to disable metadata:**
- Fine-tuning language models (need clean training data)
- Exporting chunks for external processing
- When metadata would interfere with downstream tasks

With `include_metadata: false`, chunks contain only the raw Markdown content:

```
# Requirements

Python 3.12 or higher is required...
```

### Example: Knowledge Base Ingestion

```yaml
workflow:
  - node: load_document
    type: document_loader
  
  - node: chunk_markdown
    type: tool
    tool: advanced_markdown_chunker
    input: ${load_document.content}
    config:
      max_chunk_size: 2048
      strategy: auto
      chunk_overlap: 100
  
  - node: embed_chunks
    type: embedding
    input: ${chunk_markdown.chunks}
  
  - node: store_vectors
    type: vector_store
    input: ${embed_chunks.vectors}
```

### Example: API Documentation Processing

```yaml
- node: chunk_api_docs
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 1500
    strategy: code
    include_metadata: true
```

---

## 🚀 Quick Start

### Basic Usage

```python
from markdown_chunker import MarkdownChunker

# Simple chunking
chunker = MarkdownChunker()
chunks = chunker.chunk("# Hello\n\nWorld")

# With analysis
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
```

### Hierarchical Chunking

```python
from markdown_chunker import MarkdownChunker

# Create hierarchical structure with parent-child relationships
chunker = MarkdownChunker()
result = chunker.chunk_hierarchical(markdown_text)

# Access document root
root = result.get_chunk(result.root_id)
print(f"Document: {root.content[:100]}...")

# Navigate hierarchy
sections = result.get_children(result.root_id)
for section in sections:
    print(f"Section: {section.metadata['header_path']}")
    
    # Get subsections
    subsections = result.get_children(section.metadata['chunk_id'])
    for subsection in subsections:
        print(f"  - {subsection.metadata['header_path']}")

# Multi-level retrieval: Find chunk and get context
matched_chunk = sections[0]  # Example: search result
parent_context = result.get_parent(matched_chunk.metadata['chunk_id'])
breadcrumb = [a.metadata['header_path'] for a in result.get_ancestors(matched_chunk.metadata['chunk_id'])]
print(f"Breadcrumb: {' > '.join(reversed(breadcrumb))}")

# Backward-compatible flat access
leaf_chunks = result.get_flat_chunks()
print(f"Total leaf chunks: {len(leaf_chunks)}")
```

### Strategy Selection

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()

# Automatic selection (recommended)
chunks = chunker.chunk(text)

# Force specific strategy
chunks = chunker.chunk(text, strategy="code_aware")
chunks = chunker.chunk(text, strategy="list_aware")  # For list-heavy docs
chunks = chunker.chunk(text, strategy="structural")
```

### List-Aware Strategy Example

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Changelog processing with list-aware strategy
changelog = """
# Changelog

## Version 2.0

New features:
- **Authentication**
  - OAuth 2.0 support
  - SAML integration
  - MFA with SMS and authenticator apps
- **Performance**
  - 50% faster processing
  - Reduced memory usage
"""

config = ChunkConfig(
    max_chunk_size=2000,
    list_ratio_threshold=0.35,  # Lower threshold for changelogs
    list_count_threshold=3       # Activate with fewer lists
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(changelog)

# Result: Nested items stay together, context preserved
for chunk in chunks:
    print(f"Chunk type: {chunk.metadata['content_type']}")
    print(f"List depth: {chunk.metadata.get('max_list_depth', 0)}")
```

### Nested Fencing Support Example

~~~python
from markdown_chunker import MarkdownChunker

# Meta-documentation with nested code blocks
meta_doc = '''
# How to Write Documentation

## Code Examples

When documenting code, use triple backticks. For showing markdown examples,
use quadruple backticks:

````markdown
Here's how to show Python code:

```python
def example():
    return "Hello, World!"
```
````

This preserves the nested structure correctly.
'''

chunker = MarkdownChunker()
chunks = chunker.chunk(meta_doc)

# Result: Nested fences preserved as single code block
# Inner ```python``` stays inside outer ````markdown````
for chunk in chunks:
    if '````' in chunk.content:
        print("Nested fencing preserved!")
        print(f"Has code blocks: {chunk.metadata.get('has_code', False)}")
~~~

### Table Grouping Example

```python
from markdown_chunker import MarkdownChunker, ChunkConfig, TableGroupingConfig

# API documentation with related tables
api_docs = """
## GET /users/{id}

### Parameters

| Parameter | Type | Required |
|-----------|------|----------|
| id | string | yes |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | User name |
| email | string | Email |

### Error Codes

| Code | Message |
|------|---------|
| 404 | Not Found |
"""

# Enable table grouping
config = ChunkConfig(
    group_related_tables=True,
    table_grouping_config=TableGroupingConfig(
        max_distance_lines=10,
        require_same_section=True,
    )
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(api_docs)

# Related tables grouped together for better retrieval
for chunk in chunks:
    if chunk.metadata.get("is_table_group"):
        print(f"Grouped {chunk.metadata['table_group_count']} tables")
```

### Streaming Processing Example

```python
from markdown_chunker import MarkdownChunker, StreamingConfig
import os

# Process large files with minimal memory usage
chunker = MarkdownChunker()

# Configure streaming for memory-constrained environments
streaming_config = StreamingConfig(
    buffer_size=100_000,  # 100KB buffer windows
    max_memory_mb=50      # Strict 50MB memory limit
)

# Stream process large file (e.g., 50MB documentation)
file_path = "large_documentation.md"
chunk_count = 0

for chunk in chunker.chunk_file_streaming(file_path, streaming_config):
    # Process each chunk immediately (e.g., insert to vector DB)
    chunk_count += 1
    print(f"Processed chunk {chunk_count}: {len(chunk.content)} chars")
    
    # Access streaming-specific metadata
    window_idx = chunk.metadata.get('stream_window_index', 0)
    print(f"  From window: {window_idx}")

print(f"Total chunks processed: {chunk_count}")
print(f"Memory usage stayed below {streaming_config.max_memory_mb}MB")

# Progress tracking example
file_size = os.path.getsize(file_path)
processed_bytes = 0

for chunk in chunker.chunk_file_streaming(file_path):
    processed_bytes += len(chunk.content)
    progress = (processed_bytes / file_size) * 100
    print(f"\rProgress: {progress:.1f}%", end="")

print("\nDone!")
```

### Configuration Profiles

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# For code-heavy documents (handles nested fencing)
config = ChunkConfig.for_code_heavy()
chunker = MarkdownChunker(config)

# For Dify RAG systems
config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

# For search indexing
config = ChunkConfig.for_search_indexing()
chunker = MarkdownChunker(config)
```

### Accessing Chunk Metadata

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk(markdown_text, include_analysis=True)

for chunk in result.chunks:
    print(f"Content: {chunk.content[:50]}...")
    print(f"Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"Size: {chunk.size} chars")
    print(f"Type: {chunk.content_type}")
    print(f"Strategy: {chunk.strategy}")
```

### Convenience Functions

```python
from markdown_chunker import chunk_text, chunk_file

# Chunk text directly
chunks = chunk_text("# My Document\n\nContent here...")

# Chunk from file
chunks = chunk_file("README.md")
```

---

## 🎨 Chunking Strategies

The system automatically selects the optimal strategy based on content analysis:

| Strategy | Priority | Activation Conditions | Best For |
|----------|----------|----------------------|----------|
| **Code-Aware** | 1 (highest) | code_ratio ≥ 30% OR has code blocks/tables | Technical docs, API docs |
| **List-Aware** | 2 | list_ratio > 40% OR list_count ≥ 5 (AND logic for structured docs) | Changelogs, feature lists, task lists, outlines |
| **Structural** | 3 | ≥3 headers with hierarchy | Documentation, guides |
| **Fallback** | 4 (default) | Always applicable | Simple text, mixed content |

### List-Aware Strategy: Competitive Advantage

**Unique capability not found in competing solutions** (LangChain, LlamaIndex, Unstructured, Chonkie):

**Intelligent List Processing:**
- **Hierarchy Preservation** — nested lists never split across depth levels
- **Context Binding** — introduction paragraphs automatically attached to their lists
- **Smart Grouping** — related list items kept together based on structure
- **Type Detection** — handles bullet lists, numbered lists, and checkboxes

**Activation Logic:**
```python
# For documents with strong hierarchical structure (many headers):
activate_if: list_ratio > 0.40 AND list_count >= 5

# For documents without strong structure:
activate_if: list_ratio > 0.40 OR list_count >= 5
```

**Perfect for:**
- **Changelogs** — version releases with nested changes
- **Feature lists** — product capabilities with descriptions
- **Task lists** — todos with sub-tasks and checkboxes
- **Outlines** — structured notes and cheatsheets

**Example Input:**
```markdown
Our product includes:

- **Authentication**
  - OAuth 2.0 support
  - SAML integration
  - MFA options
    - SMS
    - Authenticator app
    - Hardware keys

- **Authorization**
  - Role-based access
  - Permission groups
```

**Result:** Two coherent chunks preserving full hierarchies:
- Chunk 1: Introduction + Authentication with all nested items
- Chunk 2: Authorization with all nested items

**Competitor Behavior:** Would split nested items, losing context and relationships.

### Code-Context Binding: Competitive Advantage

**Unique capability for code-heavy documentation** that intelligently binds code blocks to their explanations:

**Pattern Recognition:**
- **Before/After Comparisons** — keeps refactoring examples together
- **Code + Output Pairs** — binds execution results to code
- **Setup + Example** — groups installation with usage
- **Sequential Steps** — maintains tutorial order

**Enhanced Metadata:**
Each code chunk includes:
- `code_role` — Classification (example, setup, output, before, after, error)
- `has_related_code` — Boolean flag for grouped blocks
- `code_relationship` — Relationship type (before_after, code_output, sequential)
- `explanation_bound` — Whether explanation context is available

**Example: Before/After Refactoring**
```markdown
# Code Improvement

## Refactoring

Before:

```python
def old_way():
    x = 1
    y = 2
    return x + y
```

After:

```python
def new_way():
    return 1 + 2
```
```

**Result:** Single chunk containing both code blocks with metadata:
```json
{
  "code_relationship": "before_after",
  "code_roles": ["before", "after"],
  "has_related_code": true,
  "related_code_count": 2
}
```

**Example: Code + Output**
```markdown
Run this command:

```bash
echo "Hello, World!"
```

Output:

```
Hello, World!
```
```

**Result:** Grouped chunk with code-output relationship preserved.

**Configuration:**
```python
config = ChunkConfig(
    enable_code_context_binding=True,    # Enable feature
    bind_output_blocks=True,              # Auto-detect output
    preserve_before_after_pairs=True,     # Keep comparisons together
    max_context_chars_before=500,         # Explanation search limit
)
```

**Perfect for:**
- API documentation with examples
- Tutorial-style technical writing
- Code migration guides
- Troubleshooting documentation

---

## ⚙️ Configuration

### Basic Parameters

```python
from markdown_chunker import ChunkConfig

config = ChunkConfig(
    # Size limits
    max_chunk_size=4096,      # Maximum chunk size (chars)
    min_chunk_size=512,       # Minimum chunk size
    
    # Overlap (adaptive sizing)
    overlap_size=200,         # Base overlap size (0 = disabled)
                              # Actual max = min(overlap_size, chunk_size * 0.35)
    
    # Behavior
    preserve_atomic_blocks=True,  # Keep code blocks and tables intact
    extract_preamble=True,        # Extract content before first header
    
    # Strategy selection thresholds
    code_threshold=0.3,           # Code ratio for CodeAwareStrategy
    structure_threshold=3,        # Min headers for StructuralStrategy
    list_ratio_threshold=0.40,    # List ratio for ListAwareStrategy
    list_count_threshold=5,       # Min list blocks for ListAwareStrategy
    
    # Code-Context Binding (NEW)
    enable_code_context_binding=True,   # Enable enhanced code-context binding
    max_context_chars_before=500,       # Max chars for backward explanation search
    max_context_chars_after=300,        # Max chars for forward explanation search
    related_block_max_gap=5,            # Max line gap for related block detection
    bind_output_blocks=True,            # Auto-bind output blocks to code
    preserve_before_after_pairs=True,   # Keep Before/After pairs together
    
    # Adaptive Chunk Sizing (NEW)
    use_adaptive_sizing=False,          # Enable adaptive chunk sizing
    adaptive_config=None,               # AdaptiveSizeConfig instance (see below)
    
    # Override
    strategy_override=None,   # Force specific strategy (code_aware/list_aware/structural/fallback)
)
```

### Table Grouping Configuration

**Group related tables** in the same chunk for better retrieval quality:

```python
from markdown_chunker import ChunkConfig, TableGroupingConfig

# Enable table grouping
config = ChunkConfig(
    group_related_tables=True,
    table_grouping_config=TableGroupingConfig(
        max_distance_lines=10,    # Max lines between tables to group
        max_grouped_tables=5,     # Max tables per group
        max_group_size=5000,      # Max chars for grouped content
        require_same_section=True # Only group within same header section
    )
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(api_docs)

# Grouped table chunks have metadata:
# - is_table_group: True
# - table_group_count: number of tables in group
```

**When to Use:**
- ✅ API documentation with Parameters/Response/Error tables
- ✅ Data reports with related comparison tables
- ✅ Technical specs with multiple related tables
- ❌ Documents where tables are independent

### Adaptive Chunk Sizing Configuration

**Enable automatic size optimization** based on content complexity:

```python
from markdown_chunker import ChunkConfig, AdaptiveSizeConfig

# Enable with default settings
config = ChunkConfig(
    use_adaptive_sizing=True,
    adaptive_config=AdaptiveSizeConfig(
        base_size=1500,           # Base chunk size for medium complexity
        min_scale=0.5,            # Minimum scaling factor (0.5x = 750 chars)
        max_scale=1.5,            # Maximum scaling factor (1.5x = 2250 chars)
        
        # Complexity weights (must sum to 1.0)
        code_weight=0.4,          # Weight for code ratio
        table_weight=0.3,         # Weight for table ratio
        list_weight=0.2,          # Weight for list ratio
        sentence_length_weight=0.1,  # Weight for average sentence length
    )
)

chunker = MarkdownChunker(config)
chunks = chunker.chunk(text)

# Chunks now have adaptive sizing metadata:
# - adaptive_size: calculated optimal size
# - content_complexity: complexity score (0.0-1.0)
# - size_scale_factor: applied scale factor
```

**Quick Enable with Profile:**

```python
# Use pre-configured adaptive sizing profile
config = ChunkConfig.with_adaptive_sizing()
chunker = MarkdownChunker(config)
```

**How It Works:**

1. **Content Analysis** - Calculates code ratio, table ratio, list ratio, avg sentence length
2. **Complexity Scoring** - Weighted sum of factors produces score 0.0-1.0
3. **Size Calculation** - `optimal_size = base_size * (min_scale + complexity * scale_range)`
4. **Chunk Application** - Chunks respect calculated size while preserving atomic blocks

**Behavior:**
- **Code-heavy documents** (high complexity) → larger chunks (up to 1.5x base size)
- **Simple text** (low complexity) → smaller chunks (down to 0.5x base size)
- **Mixed content** → balanced sizing

**Example Results:**

| Document Type | Code Ratio | Complexity | Scale Factor | Size (base=1500) |
|---------------|------------|------------|--------------|------------------|
| API docs with code | 60% | 0.68 | 1.4x | 2100 chars |
| Technical blog | 20% | 0.30 | 0.8x | 1200 chars |
| Plain text guide | 0% | 0.10 | 0.6x | 900 chars |

**When to Use:**
- ✅ Mixed corpus with varying complexity
- ✅ Want optimal retrieval precision across content types
- ✅ Need larger chunks for code preservation
- ❌ Require predictable chunk sizes (disable for consistency)
```

### Configuration Profiles

| Profile | Use Case | Max Size | Overlap |
|---------|----------|----------|---------|
| `default()` | General use | 4096 | 200 |
| `for_code_heavy()` | Code documentation | 8192 | 100 |
| `for_structured()` | Structured docs | 4096 | 200 |
| `minimal()` | Fine-grained | 1024 | 50 |

### Overlap Handling

Two modes for overlap handling:

- **Metadata mode** (`include_metadata=True`): Overlap stored in `previous_content`/`next_content` fields
- **Content mode** (`include_metadata=False`): Overlap merged into chunk content

---

## 📚 API Reference

### MarkdownChunker

```python
class MarkdownChunker:
    def __init__(
        self,
        config: Optional[ChunkConfig] = None,
        enable_performance_monitoring: bool = False
    )
    
    def chunk(
        self,
        md_text: str,
        strategy: Optional[str] = None,
        include_analysis: bool = False,
        return_format: Literal["objects", "dict"] = "objects",
        include_metadata: bool = True
    ) -> Union[List[Chunk], ChunkingResult, dict]
    
    def chunk_hierarchical(
        self,
        md_text: str
    ) -> HierarchicalChunkingResult
    
    def get_available_strategies(self) -> List[str]
    def add_strategy(self, strategy: BaseStrategy) -> None
    def remove_strategy(self, strategy_name: str) -> None
```

### Chunk

```python
@dataclass
class Chunk:
    content: str           # Chunk content
    start_line: int        # Start line (1-based)
    end_line: int          # End line
    metadata: Dict[str, Any]
    
    # Properties
    size: int              # Size in characters
    line_count: int        # Number of lines
    content_type: str      # Content type (code/text/list/table/mixed)
    strategy: str          # Strategy used
    language: Optional[str] # Programming language (for code)
```

### ChunkingResult

```python
@dataclass
class ChunkingResult:
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    fallback_used: bool
    fallback_level: int
    errors: List[str]
    warnings: List[str]
    
    # Statistics
    total_chars: int
    total_lines: int
    content_type: str
    complexity_score: float
```

### HierarchicalChunkingResult

```python
@dataclass
class HierarchicalChunkingResult:
    chunks: List[Chunk]         # All chunks including root document chunk
    root_id: str                # ID of document-level chunk
    strategy_used: str          # Name of chunking strategy applied
    
    # Navigation methods (O(1) performance)
    def get_chunk(chunk_id: str) -> Optional[Chunk]
    def get_children(chunk_id: str) -> List[Chunk]
    def get_parent(chunk_id: str) -> Optional[Chunk]
    def get_ancestors(chunk_id: str) -> List[Chunk]  # Parent to root
    def get_siblings(chunk_id: str) -> List[Chunk]   # Includes self
    def get_flat_chunks() -> List[Chunk]             # Leaf chunks only
    def get_by_level(level: int) -> List[Chunk]      # 0=doc, 1=section, 2=subsection, 3=paragraph
    def to_tree_dict() -> Dict                       # Serializable tree structure
```

**Hierarchy Metadata Fields:**

Each chunk in hierarchical mode includes these additional metadata fields:

| Field | Type | Description |
|-------|------|-------------|
| `chunk_id` | str | Unique 8-char hash identifier |
| `parent_id` | str | Parent chunk ID (None for root) |
| `children_ids` | List[str] | Child chunk IDs |
| `prev_sibling_id` | str | Previous sibling ID |
| `next_sibling_id` | str | Next sibling ID |
| `hierarchy_level` | int | 0=document, 1=section, 2=subsection, 3=paragraph |
| `is_leaf` | bool | Has no children |
| `is_root` | bool | Document-level chunk |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MarkdownChunker                          │
│                   (Main Orchestrator)                       │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│  ParserInterface │ │ StrategySelector │ │ FallbackManager │
│   (Stage 1)      │ │                  │ │                 │
│                  │ │ • CodeStrategy   │ │ • 4 levels      │
│ • AST Building   │ │ • MixedStrategy  │ │ • Graceful      │
│ • Fenced Blocks  │ │ • ListStrategy   │ │   degradation   │
│ • Element Detect │ │ • TableStrategy  │ │                 │
│ • Content Analyze│ │ • StructuralStr. │ │                 │
│                  │ │ • SentencesStr.  │ │                 │
└──────────────────┘ └──────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │      Post-Processing          │
              │                               │
              │ • OverlapManager              │
              │ • MetadataEnricher            │
              │ • DataCompletenessValidator   │
              │ • PreambleExtractor           │
              └───────────────────────────────┘
```

### Modules

| Module | Description |
|--------|-------------|
| `markdown_chunker_v2/parser.py` | Markdown parsing and content analysis (with list detection) |
| `markdown_chunker_v2/chunker.py` | Main chunking orchestration (with adaptive overlap) |
| `markdown_chunker_v2/strategies/` | 4 chunking strategies (code_aware, list_aware, structural, fallback) |
| `markdown_chunker_v2/config.py` | Configuration (10 parameters) |
| `markdown_chunker_v2/types.py` | Core data types |
| `provider/` | Dify plugin provider |
| `tools/` | Dify plugin tools |

### Project Structure

```
dify-markdown-chunker/
├── markdown_chunker_v2/       # Core library (v2.0 redesign)
│   ├── parser.py              # Markdown parsing (with list detection)
│   ├── chunker.py             # Main chunking logic (adaptive overlap)
│   ├── config.py              # Configuration (10 params)
│   ├── types.py               # Data types
│   └── strategies/            # 4 chunking strategies
│       ├── code_aware.py      # Code-heavy documents
│       ├── list_aware.py      # List-heavy documents
│       ├── structural.py      # Header-based structure
│       └── fallback.py        # Universal fallback
├── provider/                  # Dify plugin provider
├── tools/                     # Dify plugin tools
├── tests/                     # Test suite (812 tests)
│   ├── performance/           # Performance benchmarks
│   ├── integration/           # Integration tests
│   └── ...                    # Unit & property tests
├── docs/                      # Documentation
├── manifest.yaml              # Dify plugin manifest
└── requirements.txt           # Dependencies
```

---

## ⚡ Performance

### Benchmark Results

The v2 architecture delivers excellent performance with linear scaling:

| Document Size | Processing Time | Throughput | Memory |
|---------------|----------------|------------|--------|
| Tiny (<1KB) | 0.23ms | 1,963 KB/s | <0.01 MB |
| Small (1-5KB) | 0.78ms | 4,093 KB/s | 0.02 MB |
| Medium (5-20KB) | 2.06ms | 4,801 KB/s | 0.04 MB |
| Large (20-100KB) | 21.11ms | 4,449 KB/s | 0.31 MB |

**Performance Characteristics:**
- **Processing Speed**: 0.25 ms/KB (very fast)
- **Throughput**: 4-5 MB/s sustained
- **Scaling**: Linear (R² = 0.77)
- **Memory**: <1 MB for typical documents

### Performance Monitoring

```python
chunker = MarkdownChunker(enable_performance_monitoring=True)

for doc in documents:
    chunker.chunk(doc)

stats = chunker.get_performance_stats()
print(f"Average time: {stats['chunk']['avg_time']:.3f}s")
```

For detailed benchmarks and methodology, see [Performance Guide](docs/guides/performance.md).

---

## 🧪 Development

### Testing

```bash
# Run all tests (812)
make test

# Verbose output
make test-verbose

# With coverage report
make test-coverage

# Quick tests
make test-quick

# Performance benchmarks
python tests/performance/run_benchmarks_standalone.py
```

### Code Quality

```bash
# Format code
make format

# Run linter
make lint

# Type checking
make quality-check
```

### Building Plugin

```bash
# Validate structure
make validate

# Build package
make package

# Full release
make release
```

---

## 📦 Dependencies

### Core
- `markdown-it-py>=3.0.0` — Markdown parsing
- `mistune>=3.0.0` — Alternative parser
- `pydantic>=2.0.0` — Data validation
- `dify_plugin==0.5.0b15` — Dify integration

### Development
- `pytest>=8.0.0` — Testing
- `hypothesis>=6.0.0` — Property-based testing
- `black>=23.0.0` — Code formatting
- `mypy>=1.5.0` — Type checking

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

```bash
# 1. Fork the repository
# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Make changes with tests
# 4. Check quality
make test && make quality-check

# 5. Submit Pull Request
```

---

## 👤 Author & Support

**Author:** Aleksandr Sukhodko ([@asukhodko](https://github.com/asukhodko))  
**Repository:** https://github.com/asukhodko/dify-markdown-chunker

### Getting Help

- **Bug Reports & Feature Requests:** [GitHub Issues](https://github.com/asukhodko/dify-markdown-chunker/issues)
- **Questions & Discussions:** [GitHub Discussions](https://github.com/asukhodko/dify-markdown-chunker/discussions)

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 📝 Changelog

**Current Version:** 2.1.5 (January 2026)

### Latest: v2.1.5

**Released:** January 4, 2026

**Changes:**
- ✅ **Migration to chunkana 0.1.0** — Complete migration from embedded code to external library
  - Removed embedded `markdown_chunker` and `markdown_chunker_v2` directories
  - Added migration adapter (`adapter.py`) for full compatibility
  - All functionality preserved with improved maintainability
- ✅ **Build System Improvements** — Enhanced packaging and development workflow
  - Added automatic `dify-plugin` CLI installation in Makefile
  - Fixed package creation and validation commands
  - Improved code quality checks and linting
- ✅ **Testing Infrastructure** — Comprehensive test coverage for migration
  - 99 migration-compatible tests passing
  - Property-based testing for correctness validation
  - Regression testing against pre-migration snapshots

### Previous: v2.1.4

**Released:** December 23, 2025

**Changes:**
- Bumped `dify_plugin` dependency from 0.5.0b15 to 0.7.0
- Fixed `.difyignore` to properly include README.md and PRIVACY.md in package

### v2.1.3

**Released:** December 14, 2025

**New Features:**
- ✅ **Table Grouping Option** — Groups related tables in same chunk for better retrieval
  - Proximity-based grouping (`max_distance_lines`)
  - Section boundary awareness (`require_same_section`)
  - Size and count limits (`max_group_size`, `max_grouped_tables`)
  - Perfect for API documentation with Parameters/Response/Error tables

### Previous: v2.1.2 (December 11, 2025)
- Enhanced Code-Context Binding — Intelligent binding of code blocks to explanations
- Adaptive Chunk Sizing — Automatic size optimization based on content complexity
- Hierarchical Chunking — Parent-child relationships with navigation API

For full release history, see [CHANGELOG.md](CHANGELOG.md).

---

<div align="center">

**[⬆ Back to Top](#-advanced-markdown-chunker-for-dify)**

</div>
