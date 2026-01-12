# Advanced Markdown Chunker for Dify

**Intelligent Markdown document chunking for RAG systems with structural awareness**

[![Version](https://img.shields.io/badge/version-2.1.7-orange.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/dify-1.9.0+-green.svg)](https://dify.ai/)
[![Tests](https://img.shields.io/badge/tests-473-brightgreen.svg)](#testing)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Data & Privacy](#-data--privacy)
- [Quick Start in Dify UI](#quick-start-in-dify-ui)
- [Output Format](#output-format)
- [Chunking Strategies](#chunking-strategies)
- [Configuration](#-configuration)
- [API Reference](#-api-reference)
- [Architecture](#-architecture)
- [Performance](#-performance)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)
- [Development](#-development)
- [Compatibility](#compatibility)

---

## Overview

Advanced Markdown Chunker is a Dify plugin that intelligently splits Markdown documents into semantically meaningful chunks optimized for RAG (Retrieval-Augmented Generation) systems. Powered by the **chunkana** engine, it provides advanced structural awareness that goes beyond simple text splitting.

### Primary Use Case: RAG Systems

This plugin is designed specifically for **RAG (Retrieval-Augmented Generation)** workflows where document chunks are embedded and stored in vector databases for semantic search. Built on the robust chunkana library, it provides enterprise-grade chunking capabilities through a user-friendly Dify interface. By default, each chunk includes embedded metadata (header paths, content type, line numbers) directly in the chunk text, which improves retrieval quality by providing additional context for vector representations.

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
| **Mathematical formulas split** | **LaTeX formula preservation (`$...$`, environments)** |

---

## ✨ Features

### 🎯 Adaptive Chunking
- **4 intelligent strategies** — automatic selection based on content analysis
- **Adaptive Chunk Sizing** — automatic size optimization based on content complexity
  - Code-heavy content → larger chunks (up to 1.5x base size)
  - Simple text → smaller chunks (down to 0.5x base size)
  - Configurable complexity weights and scaling bounds
  - Optional feature (disabled by default for backward compatibility)
- **Hierarchical Chunking** — parent-child relationships between chunks
  - Multi-level retrieval support (overview vs. detail)
  - Programmatic navigation (siblings, ancestors, children)
  - O(1) chunk lookup performance
  - Backward compatible with flat chunking
- **Streaming Processing** — memory-efficient processing for large files
  - Process files >10MB with <50MB RAM usage
  - Configurable buffer management (100KB default window)
  - Progress tracking support for long-running operations
  - Maintains quality through smart window boundary detection
- **List-Aware Strategy** — preserves nested list hierarchies and context (unique competitive advantage)
- **Nested Fencing Support** — correctly handles quadruple/quintuple backticks and tilde fencing for meta-documentation (unique capability)
- **Enhanced Code-Context Binding** — intelligently binds code blocks to explanations, recognizes Before/After patterns, Code+Output pairs, and sequential examples (unique competitive advantage)
- **LaTeX Formula Handling** — preserves mathematical formulas as atomic blocks
  - Display math (`$...$`) never split across chunks
  - Environment blocks (`\begin{equation}`, `\begin{align}`) preserved complete
  - Supported in all 4 chunking strategies
  - Critical for scientific papers and technical documentation
- **Table Grouping Option** — groups related tables in same chunk for better retrieval
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
- **473 tests** — comprehensive test coverage with property-based testing (97 plugin tests + 376 chunkana library tests)
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
The plugin processes all Markdown content locally within your Dify instance. No data is transmitted to external services.

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

## When to Use

**✅ Perfect for:**
- Technical documentation with code and tables
- API documentation with examples
- User guides with structured content
- Legal documents with articles and clauses
- Changelogs with nested change lists

**❌ Not recommended for:**
- Simple text without structure
- Short documents (< 1000 characters)
- Documents where exact chunk size is critical

## Quick Start in Dify UI

### Step 1: Install Plugin

1. Download the `.difypkg` file from [Releases](https://github.com/asukhodko/dify-markdown-chunker/releases)
2. In Dify: **Settings → Plugins → Install Plugin**
3. Upload the `.difypkg` file
4. Plugin is ready to use

**Requirements:** Dify version 1.9.0 or higher

### Step 2: Create Knowledge Base

1. **Create new Knowledge Base**
   - Go to Knowledge section
   - Click "Create Knowledge"
   - Select "Text" type

2. **Configure Data Source**
   - Add your Markdown files
   - Choose "File Upload" or "Web Crawling"

3. **Configure Text Processing**
   - **Text Splitter**: select "Advanced Markdown Chunker"
   - Configure parameters (see below)

### Step 3: Parameter Configuration

<!-- params-table:start -->
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_chunk_size` | number | 4096 | Maximum size of each chunk in characters. Larger values create bigger chunks with more context. |
| `chunk_overlap` | number | 200 | Characters to overlap between chunks (default: 200, 0 to disable). With include_metadata=true, overlap is in metadata fields. With include_metadata=false, overlap is embedded in chunk text. |
| `strategy` | select | auto | Document chunking strategy (default: auto - automatically detect best strategy based on content analysis) (auto/code_aware/list_aware/structural/fallback) |
| `include_metadata` | boolean | true | Embed metadata in text (default: true). When enabled, chunks have <metadata> block with content_type, header_path, line numbers; overlap stays in metadata. When disabled, overlap is embedded into text: previous_content + main + next_content. |
| `enable_hierarchy` | boolean | false | Create parent-child relationships between chunks (default: false). When enabled, returns hierarchical structure with navigation metadata (parent_id, children_ids, level). Useful for multi-level retrieval and context navigation. |
| `debug` | boolean | false | Enable debug mode (default: false). When enabled with enable_hierarchy=true, returns all chunks (root, intermediate, and leaf). By default, only leaf chunks are returned. Future: will also control metadata field filtering. |
| `leaf_only` | boolean | false | Return only leaf chunks in hierarchical mode (default: false). When enabled, excludes internal nodes (sections with children). Recommended for vector DB indexing where you want only content chunks, not structural headers. |
<!-- params-table:end -->

### Step 4: Recommended Settings

**For technical documentation:**
```
max_chunk_size: 3000
strategy: code_aware
include_metadata: true
```

**For legal documents:**
```
max_chunk_size: 2500
strategy: structural
enable_hierarchy: true
```

**For API documentation:**
```
max_chunk_size: 2000
strategy: code_aware
include_metadata: true
```

## Output Format

### With Metadata (include_metadata: true)

Each chunk includes a `<metadata>` block with content information:

```
<metadata>
{
  "content_type": "text",
  "header_path": "/Installation/Requirements",
  "start_line": 45,
  "end_line": 52,
  "strategy": "structural",
  "chunk_index": 2
}
</metadata>
# Requirements

Python 3.12 or higher...
```

**Key metadata fields:**
- `content_type` — content type (text, code, table, list, mixed)
- `header_path` — hierarchical path of section headers
- `start_line` / `end_line` — line numbers in source file
- `strategy` — chunking strategy used
- `chunk_index` — sequential chunk number
- `previous_content` / `next_content` — overlap context from adjacent chunks

### Without Metadata (include_metadata: false)

Chunks contain only clean Markdown content with embedded overlap:

```
...end of previous chunk...

# Requirements

Python 3.12 or higher...

...start of next chunk...
```

## Chunking Strategies

The system automatically selects the optimal strategy based on content analysis:

| Strategy | Priority | Activation Conditions | Best For |
|----------|----------|----------------------|----------|
| **Code-Aware** | 1 (highest) | code ≥ 30% OR has code blocks/tables | Technical docs, API docs |
| **List-Aware** | 2 | lists > 40% OR list count ≥ 5 | Changelogs, feature lists |
| **Structural** | 3 | ≥3 headers with hierarchy | Documentation, guides |
| **Fallback** | 4 (default) | Always applicable | Simple text, mixed content |

### Understanding chunk_overlap

**Chunk overlap** controls how many characters of context are shared between consecutive chunks to preserve semantic continuity.

**Behavior depends on `include_metadata`:**

| `include_metadata` | Overlap Behavior |
|--------------------|------------------|
| `true` (default) | Overlap stored in metadata fields `previous_content` / `next_content`. Chunk content stays clean. |
| `false` | Overlap embedded directly into chunk text: `previous_content + "\n" + main + "\n" + next_content` |

---

## ⚙️ Configuration

### Basic Parameters

```python
from chunkana import ChunkConfig

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
from chunkana import ChunkConfig, TableGroupingConfig

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
from chunkana import ChunkConfig, AdaptiveSizeConfig

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
- **Mixed content** → size close to base

### Configuration Profiles

| Profile | Use Case | Max Size | Overlap |
|---------|----------|----------|---------|
| `for_dify_rag()` | RAG systems | 4096 | 200 |
| `for_code_heavy()` | Technical documentation | 3072 | 150 |
| `for_search_indexing()` | Search indexing | 2048 | 100 |
| `minimal()` | Fine-grained chunking | 1024 | 50 |

### Overlap Handling

Two modes for overlap handling:

**Metadata mode** (`include_metadata: true`):
- Overlap stored in `previous_content` / `next_content` fields
- Main chunk content stays clean
- Perfect for RAG systems with vector representations

**Embedded text mode** (`include_metadata: false`):
- Overlap physically embedded into chunk text
- Format: `previous + "\n" + main + "\n" + next`
- Suitable for sliding window processing

## Troubleshooting

### Frequently Asked Questions

**Q: Why are chunks too large/small?**
A: Adjust `max_chunk_size`. For technical docs, recommend 2000-4000 characters, for simple text — 1000-2000.

**Q: Code is split in the middle of functions**
A: Ensure `code_aware` strategy is used (automatically activated when code blocks are present).

**Q: Lists are broken incorrectly**
A: For documents with many lists, use `list_aware` strategy or `auto`.

**Q: Metadata interferes with results**
A: Set `include_metadata: false` to get clean text.

**Q: Need only content chunks without headers**
A: Use `enable_hierarchy: true` and `leaf_only: true`.

### Markdown Limitations

For best results, follow these recommendations:

- **Headers**: use `#`, `##`, `###` (not "visual" headers without #)
- **Lists**: `a./b.` often not recognized as ordered list — use `1./2.`
- **Tables**: use GitHub-flavored markdown format
- **Code**: use triple backticks with language specification

### Configuration Recipes

**Legal documents:**
```
strategy: structural
enable_hierarchy: true
include_metadata: true
```

**API documentation:**
```
strategy: code_aware
max_chunk_size: 2500
```

**General documentation:**
```
strategy: auto
include_metadata: true
```

## Usage Examples

Detailed examples with input files, configurations, and results are available in the `examples/` folder:

- `examples/inputs/` — sample input files
- `examples/configs/` — configurations for each example
- `examples/outputs/` — reference results

---

## 📚 API Reference

### MarkdownChunker

Main class for chunking Markdown documents.

```python
from chunkana import MarkdownChunker, ChunkConfig

# Create with default settings
chunker = MarkdownChunker()

# Create with custom configuration
config = ChunkConfig(
    max_chunk_size=2048,
    overlap_size=100,
    strategy_override="code_aware"
)
chunker = MarkdownChunker(config)
```

#### Core Methods

**`chunk(text: str, **kwargs) -> List[Chunk]`**
```python
# Simple chunking
chunks = chunker.chunk(markdown_text)

# With analysis
result = chunker.chunk(markdown_text, include_analysis=True)
print(f"Strategy used: {result.strategy_used}")
```

**`chunk_hierarchical(text: str, **kwargs) -> HierarchicalResult`**
```python
# Hierarchical chunking
result = chunker.chunk_hierarchical(markdown_text)

# Navigate hierarchy
root = result.get_chunk(result.root_id)
children = result.get_children(result.root_id)
leaf_chunks = result.get_flat_chunks()
```

**`chunk_file_streaming(file_path: str, config: StreamingConfig) -> Iterator[Chunk]`**
```python
# Streaming processing for large files
streaming_config = StreamingConfig(buffer_size=100_000)
for chunk in chunker.chunk_file_streaming("large_doc.md", streaming_config):
    process_chunk(chunk)
```

#### Configuration Profiles

```python
# Pre-configured profiles
config = ChunkConfig.for_code_heavy()      # For code documentation
config = ChunkConfig.for_dify_rag()        # For RAG systems in Dify
config = ChunkConfig.for_search_indexing() # For search indexing
config = ChunkConfig.with_adaptive_sizing() # With adaptive sizing
```

### Chunk

Class representing a single document chunk.

```python
class Chunk:
    content: str           # Text content of the chunk
    start_line: int        # Starting line in source document
    end_line: int          # Ending line in source document
    size: int              # Size in characters
    content_type: str      # Content type (text, code, table, list, mixed)
    strategy: str          # Strategy used
    metadata: Dict[str, Any]  # Additional metadata
```

#### Metadata Fields

- `chunk_index` — sequential chunk number
- `header_path` — hierarchical path of headers
- `code_language` — programming language (for code blocks)
- `previous_content` / `next_content` — overlap context
- `adaptive_size` — calculated optimal size (when adaptive sizing enabled)
- `content_complexity` — complexity score 0.0-1.0
- `code_role` — code block role (example, setup, output, before, after, error)
- `has_related_code` — whether chunk contains related code blocks
- `code_relationship` — relationship type (before_after, code_output, sequential)

### Helper Functions

```python
from chunkana import chunk_text, chunk_file

# Direct text chunking
chunks = chunk_text("# My Document\n\nContent...")

# Chunk from file
chunks = chunk_file("README.md")
```

---

## 🏗️ Architecture

### Component Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dify Plugin   │───▶│  Chunkana Engine │───▶│   Strategies    │
│   (Adapter)     │    │   (Core Logic)   │    │   (Algorithms)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Input/Output   │    │   AST Parser     │    │  Content Types  │
│   Validation    │    │   & Analysis     │    │   Detection     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Processing Flow

1. **Input Validation** — parameter and content validation
2. **AST Parsing** — Markdown parsing into syntax tree
3. **Content Analysis** — content type and complexity detection
4. **Strategy Selection** — automatic or forced algorithm selection
5. **Chunking** — applying selected strategy
6. **Post-processing** — adding metadata and overlaps
7. **Output Formatting** — preparing result for Dify

### Chunking Strategies

#### CodeAwareStrategy
- **Goal:** Preserve code blocks and tables
- **Algorithm:** Detects fenced block boundaries, groups related code
- **Activation:** code_ratio ≥ 30% OR presence of code blocks/tables

#### ListAwareStrategy  
- **Goal:** Preserve list hierarchies
- **Algorithm:** Analyzes list nesting, groups by levels
- **Activation:** list_ratio > 40% OR list_count ≥ 5

#### StructuralStrategy
- **Goal:** Split by headers
- **Algorithm:** Uses header hierarchy as chunk boundaries
- **Activation:** ≥3 headers with hierarchy

#### FallbackStrategy
- **Goal:** Universal chunking
- **Algorithm:** Sentence-based splitting with size consideration
- **Activation:** Always applicable as fallback

### Adaptive Capabilities

#### Adaptive Sizing
```python
optimal_size = base_size * (min_scale + complexity * scale_range)
```
- Analyzes content complexity (code, tables, lists)
- Scales chunk size from 0.5x to 1.5x base size
- Preserves atomic blocks regardless of size

#### Smart Overlap
```python
max_overlap = min(overlap_size, chunk_size * 0.35)
```
- Adaptive overlap limit up to 35% of chunk size
- Context-dependent placement (in metadata or text)

---

## ⚡ Performance

### Benchmarks

**Test Environment:** Windows 11, Intel Core i7, 16GB RAM, SSD

| Document Size | Processing Time | Memory | Chunks |
|---------------|-----------------|--------|--------|
| 10KB (article) | 15ms | 12MB | 3-5 |
| 100KB (manual) | 45ms | 14MB | 25-35 |
| 1MB (API docs) | 180ms | 18MB | 180-220 |
| 10MB (large documentation) | 1.2s | 35MB | 1500-2000 |

### Optimizations

**Streaming Processing:**
- Files >10MB processed using <50MB RAM
- 100KB window buffering with smart boundary detection
- Progress tracking support for long-running operations

**AST Caching:**
- Reuse parsed tree for different configurations
- Incremental analysis for large documents

**Memory:**
- Base usage: 12.3MB + 0.14MB per KB input
- Streaming mode: fixed usage regardless of file size

### Performance Monitoring

> **Note:** Performance data based on benchmarks from `docs/research/07_benchmark_results.md` conducted on Windows 11, Intel Core i7, 16GB RAM, SSD. Actual performance may vary depending on system configuration, document complexity, and content type.

---

---

## 🧪 Development

### Testing

The project uses pytest for testing. The test suite is optimized and includes:

**Test Structure:**
- `tests/plugin/` — 97 Dify plugin tests
- `tests/chunkana/` — 376 chunkana library tests
- **Property-based tests** — formal correctness guarantees with Hypothesis
- **Benchmarks** — automated performance regression detection

**Running Tests:**
```bash
# All tests
make test

# Plugin tests only
pytest tests/plugin/ -v

# Property-based tests only
pytest tests/ -k "property" -v

# With coverage
pytest --cov=. --cov-report=html
```

**Test Categories:**
- **Unit tests** — individual components and functions
- **Integration tests** — component interactions
- **Property tests** — universal correctness properties
- **Performance tests** — performance regressions
- **Golden tests** — reference inputs/outputs

### Development Setup

```bash
# Clone repository
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Verify installation
make test
```

### Dependencies

**Core:**
- `chunkana>=2.1.7` — chunking engine
- `dify_plugin==0.5.0b15` — Dify integration

**Development:**
- `pytest>=8.0.0` — testing
- `hypothesis>=6.0.0` — property-based testing
- `pytest-cov` — code coverage
- `black` — code formatting
- `flake8` — linting

### Building Plugin

```bash
# Build .difypkg file
make package

# Verify before building
make verify

# Clean build artifacts
make clean
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

**PR Requirements:**
- All tests must pass
- Code coverage must not decrease
- Code must follow style (black, flake8)
- Documentation must be updated

## Compatibility

**Tested on:**
- Dify versions 1.9.0, 1.9.1, 1.9.2
- Python 3.12+
- Windows 11, macOS 14+, Ubuntu 22.04+

**Expected compatibility:**
- Dify versions 1.9.x and higher
- Python 3.12 and higher

## Support

- **Documentation:** [docs/](docs/)
- **Questions and discussions:** [GitHub Discussions](https://github.com/asukhodko/dify-markdown-chunker/discussions)
- **Bug reports:** [GitHub Issues](https://github.com/asukhodko/dify-markdown-chunker/issues)

## License

MIT License — see [LICENSE](LICENSE)

---

**Author:** Aleksandr Sukhodko ([@asukhodko](https://github.com/asukhodko))  
**Repository:** https://github.com/asukhodko/dify-markdown-chunker