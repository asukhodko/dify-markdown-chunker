# 🔖 Advanced Markdown Chunker for Dify

<div align="center">

**Intelligent Markdown document chunking for RAG systems with structural awareness**

[![Version](https://img.shields.io/badge/version-2.0.0--a3-orange.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/dify-1.9.0+-green.svg)](https://dify.ai/)
[![Tests](https://img.shields.io/badge/tests-1366+-brightgreen.svg)](#testing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
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
- [License](#-license)

---

## Overview

**Advanced Markdown Chunker** is a Dify plugin that intelligently splits Markdown documents into semantically meaningful chunks optimized for RAG (Retrieval-Augmented Generation) systems. Unlike simple text splitting, it preserves document structure, keeps code blocks intact, and automatically selects the best chunking strategy based on content analysis.

### Why Use This Plugin?

| Simple Chunking Problems | Advanced Markdown Chunker Solution |
|--------------------------|-----------------------------------|
| Breaks code blocks mid-function | Preserves code blocks as atomic units |
| Loses header context | Maintains hierarchical section structure |
| Splits tables and lists | Keeps tables and lists intact |
| One-size-fits-all approach | 6 adaptive strategies based on content |
| No overlap support | Smart overlap for better retrieval |

---

## ✨ Features

### 🎯 Adaptive Chunking
- **6 intelligent strategies** — automatic selection based on content analysis
- **Structure preservation** — headers, lists, tables, and code stay intact
- **Smart overlap** — configurable context overlap between chunks

### 🔍 Deep Content Analysis
- **AST parsing** — full Markdown syntax analysis
- **Content type detection** — code-heavy, text-heavy, mixed
- **Complexity scoring** — optimizes strategy selection

### 🛡️ Reliability
- **1366+ tests** — comprehensive test coverage
- **Property-Based Testing** — formal correctness guarantees with Hypothesis
- **4-level fallback** — graceful degradation on errors

### 🔌 Integration
- **Dify Plugin** — ready-to-use in Dify workflows
- **Python Library** — standalone usage
- **REST API Ready** — adapters for API integration

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
| `max_chunk_size` | number | 1000 | Maximum chunk size in characters |
| `chunk_overlap` | number | 100 | Overlap between consecutive chunks |
| `strategy` | select | auto | Chunking strategy (auto/code/structural/mixed) |
| `include_metadata` | boolean | true | Include chunk metadata |

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

### Strategy Selection

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()

# Automatic selection (recommended)
chunks = chunker.chunk(text)

# Force specific strategy
chunks = chunker.chunk(text, strategy="code")
chunks = chunker.chunk(text, strategy="structural")
```

### Configuration Profiles

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# For code-heavy documents
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
| **Code** | 1 (highest) | code_ratio ≥ 30%, ≥1 code block | Technical docs, tutorials |
| **Mixed** | 2 | code_ratio ≥ 30%, complexity ≥ 0.3 | Balanced content |
| **List** | 3 | ≥5 lists OR list_ratio > 60% | Task lists, outlines |
| **Table** | 4 | ≥3 tables OR table_ratio > 40% | Data reports |
| **Structural** | 5 | ≥3 headers, depth > 1 | Documentation |
| **Sentences** | 6 (fallback) | Always applicable | Simple text |

---

## ⚙️ Configuration

### Basic Parameters

```python
from markdown_chunker import ChunkConfig

config = ChunkConfig(
    # Size limits
    max_chunk_size=4096,      # Maximum chunk size (chars)
    min_chunk_size=512,       # Minimum chunk size
    target_chunk_size=2048,   # Target size
    
    # Overlap
    enable_overlap=True,      # Enable overlap
    overlap_size=200,         # Overlap size (chars)
    
    # Behavior
    preserve_code_blocks=True,    # Keep code blocks intact
    preserve_tables=True,         # Keep tables intact
    preserve_list_hierarchy=True, # Keep list structure
    allow_oversize=True,          # Allow oversized chunks
    
    # Fallback
    enable_fallback=True,     # Enable fallback strategies
    max_fallback_level=4,     # Maximum fallback depth
)
```

### Configuration Profiles

| Profile | Use Case | Max Size | Overlap |
|---------|----------|----------|---------|
| `default()` | General use | 4096 | 200 |
| `for_code_heavy()` | Code documentation | 6144 | 300 |
| `for_structured_docs()` | Structured docs | 3072 | 150 |
| `for_dify_rag()` | Dify RAG systems | 3072 | 150 |
| `for_api_docs()` | API documentation | 3072 | 150 |
| `for_code_docs()` | Code docs | 2048 | 100 |
| `for_chat_context()` | LLM context | 1536 | 200 |
| `for_search_indexing()` | Search | 1024 | 100 |
| `for_large_documents()` | Large files | 8192 | 400 |
| `for_fast_processing()` | Batch processing | 8192 | 100 |
| `compact()` | Fine-grained | 2048 | 100 |

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
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  ParserInterface │ │ StrategySelector │ │ FallbackManager │
│   (Stage 1)      │ │                   │ │                 │
│                  │ │ • CodeStrategy    │ │ • 4 levels      │
│ • AST Building   │ │ • MixedStrategy   │ │ • Graceful      │
│ • Fenced Blocks  │ │ • ListStrategy    │ │   degradation   │
│ • Element Detect │ │ • TableStrategy   │ │                 │
│ • Content Analyze│ │ • StructuralStr.  │ │                 │
│                  │ │ • SentencesStr.   │ │                 │
└─────────────────┘ └─────────────────┘ └─────────────────┘
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
| `markdown_chunker/parser/` | AST parsing, content analysis, element detection |
| `markdown_chunker/chunker/` | Chunking strategies, orchestration, validation |
| `markdown_chunker/chunker/strategies/` | 6 chunking strategy implementations |
| `markdown_chunker/api/` | REST API adapters, request validation |
| `provider/` | Dify plugin provider |
| `tools/` | Dify plugin tools |

### Project Structure

```
dify-markdown-chunker/
├── markdown_chunker/          # Core library
│   ├── parser/                # Parsing and analysis
│   ├── chunker/               # Chunking logic
│   │   └── strategies/        # 6 chunking strategies
│   └── api/                   # API adapters
├── provider/                  # Dify plugin provider
├── tools/                     # Dify plugin tools
├── tests/                     # Test suite (1366+ tests)
├── docs/                      # Documentation
├── examples/                  # Usage examples
├── benchmarks/                # Performance benchmarks
├── manifest.yaml              # Dify plugin manifest
└── requirements.txt           # Dependencies
```

---

## ⚡ Performance

### Benchmarks

| Document Size | Processing Time | Throughput | Chunks |
|--------------|-----------------|------------|--------|
| 1 KB | ~800 ms | 1.3 KB/s | 6 |
| 10 KB | ~150 ms | 66 KB/s | 44 |
| 50 KB | ~1.9 s | 27 KB/s | 215 |
| 100 KB | ~7 s | 14 KB/s | 429 |

### Performance Monitoring

```python
chunker = MarkdownChunker(enable_performance_monitoring=True)

for doc in documents:
    chunker.chunk(doc)

stats = chunker.get_performance_stats()
print(f"Average time: {stats['chunk']['avg_time']:.3f}s")
```

---

## 🧪 Development

### Testing

```bash
# Run all tests (1366+)
make test

# Verbose output
make test-verbose

# With coverage report
make test-coverage

# Quick tests
make test-quick
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

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 📝 Changelog

**Current Version:** 2.0.0-a3 (December 2024)

### Recent Changes
- Redesigned overlap handling with metadata-based neighbor context
- Regression and duplication validation
- Block-based chunking implementation
- Improved API documentation

Full changelog: [CHANGELOG.md](CHANGELOG.md)

---

<div align="center">

**[⬆ Back to Top](#-advanced-markdown-chunker-for-dify)**

</div>
