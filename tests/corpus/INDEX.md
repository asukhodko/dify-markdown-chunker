# Test Corpus Index

**Generated:** 2024-12-06  
**Total Documents:** 470+  
**Total Size:** ~2.0 MB  
**Purpose:** Comprehensive testing of markdown chunking strategies

## Overview

This corpus contains diverse markdown documents organized into 9 categories, designed to thoroughly test the Advanced Markdown Chunker's parsing, strategy selection, and chunking capabilities.

## Directory Structure

```
corpus/
├── technical_docs/           # 100 files - Technical documentation
│   ├── kubernetes/           # 25 files
│   ├── docker/               # 25 files
│   ├── react/                # 25 files
│   └── aws/                  # 25 files
├── github_readmes/           # 160 files - Project READMEs
│   ├── python/               # 40 files
│   ├── javascript/           # 40 files
│   ├── go/                   # 40 files
│   └── rust/                 # 40 files
├── changelogs/               # 50 files - Version changelogs
├── engineering_blogs/        # 50 files - Technical blog posts
├── personal_notes/           # 30 files - Personal documentation
│   ├── unstructured/         # 10 files
│   ├── journals/             # 10 files
│   └── cheatsheets/          # 10 files
├── debug_logs/               # 20 files - Debugging documentation
├── nested_fencing/           # 20 files - Meta-documentation with nested fences
├── research_notes/           # 20 files - Research documentation
└── mixed_content/            # 20 files - Edge cases and mixed content
```

## Category Descriptions

### 1. Technical Documentation (100 files)

**Purpose:** Test code-heavy documentation with API references, configuration examples, and command-line usage.

**Characteristics:**
- Well-structured with clear header hierarchy
- Mix of code examples in multiple languages (Bash, YAML, Python, JavaScript)
- Tables for API parameters and configuration options
- Varied sizes from 2KB to 50KB
- Expected strategy: Code-Aware or Structural

**Technologies covered:**
- Kubernetes (container orchestration)
- Docker (containerization)
- React (frontend framework)
- AWS (cloud services)

### 2. GitHub README-style Documents (160 files)

**Purpose:** Test project documentation with badges, installation instructions, usage examples, and contributing guidelines.

**Characteristics:**
- Badges and shields at top
- Installation and quick start sections
- API reference tables
- Code examples for basic and advanced usage
- Contributing guidelines
- Feature lists and roadmaps
- Expected strategy: Code-Aware or Structural

**Languages represented:**
- Python projects
- JavaScript/TypeScript projects
- Go projects
- Rust projects

### 3. Changelogs (50 files)

**Purpose:** Test version history documentation with structured change categorization.

**Characteristics:**
- "Keep a Changelog" format
- Version headers with dates
- Categorized changes (Added, Changed, Fixed, Removed, Security)
- Links to issues and PRs
- Multiple versions per file
- Expected strategy: Structural

### 4. Engineering Blog Posts (50 files)

**Purpose:** Test long-form technical content with explanations, diagrams, code examples, and performance data.

**Characteristics:**
- Long-form content (2000-8000 words)
- Code examples in multiple languages
- Architecture diagrams (text-based)
- Performance comparison tables
- Lessons learned sections
- Expected strategy: Structural or Code-Aware

**Topics covered:**
- Scaling infrastructure
- Performance optimization
- Architecture migration
- Real-time data pipelines
- Deployment strategies
- Distributed systems

### 5. Personal Notes (30 files)

**Purpose:** Test unstructured, informal markdown with irregular formatting.

#### 5.1 Unstructured Notes (10 files)

- No clear structure or hierarchy
- Mixed topics within single document
- Incomplete sentences and abbreviations
- Sometimes unfenced code snippets
- TODO items scattered throughout
- Expected strategy: Fallback

#### 5.2 Engineering Journals (10 files)

- Date-based entries
- Problem-solution structure
- Before/after code comparisons
- Debugging steps
- Personal reflections and lessons learned
- Expected strategy: Code-Aware or Structural

#### 5.3 Cheatsheets (10 files)

- Dense information with minimal prose
- Command reference tables
- Code snippets for common tasks
- Categorized by operation type
- Expected strategy: Code-Aware or Structural

### 6. Debug Logs (20 files)

**Purpose:** Test debugging documentation with multi-language code blocks and diagnostic output.

**Characteristics:**
- Problem description and symptoms
- Code under investigation (potentially buggy)
- Diagnostic output (stack traces, memory dumps, profiling)
- Root cause analysis
- Fixed implementation
- Verification results
- Expected strategy: Code-Aware

**Technologies:**
- Node.js, Python, Java, Go applications
- Various issue types (memory leaks, performance, crashes, data corruption)

### 7. Nested Fencing (20 files)

**Purpose:** Test meta-documentation with nested code fences (documentation about documentation).

**Characteristics:**
- Triple, quadruple, and quintuple backtick nesting
- Markdown examples within markdown
- Mixed fence types (backticks and tildes)
- Meta-documentation explaining how to write code examples
- Nesting levels: 3 to 5 deep
- Expected strategy: Code-Aware

### 8. Research Notes (20 files)

**Purpose:** Test academic/research documentation with literature references, methodology, data tables, and analysis code.

**Characteristics:**
- Abstract and introduction
- Literature review with citations
- Methodology section with code
- Results tables with metrics
- Statistical analysis
- Discussion and conclusions
- Bibliography
- Expected strategy: Structural or Code-Aware

**Fields represented:**
- Machine Learning
- Distributed Systems
- Database Theory
- Computer Vision

### 9. Mixed Content (20 files)

**Purpose:** Test edge cases and extreme scenarios that combine multiple content types.

**Characteristics:**
- All content types in one document
- Unicode characters (multiple scripts, emoji)
- Very wide tables (20+ columns)
- Deeply nested lists (10+ levels)
- Very long lines (300+ words)
- Empty sections
- Consecutive code blocks without text
- Expected strategy: Varies (all strategies may be triggered)

## Content Characteristics Distribution

Based on metadata analysis:

| Characteristic | Count | Percentage |
|----------------|-------|------------|
| Code-heavy (code_ratio >= 0.5) | 1 | <1% |
| Structural (header_count >= 3) | 457 | 97% |
| Table-rich (table_count >= 3) | ~150 | 32% |
| List-heavy (list_count >= 10) | ~200 | 43% |

## Size Distribution

| Category | Count | Size Range |
|----------|-------|------------|
| Tiny (< 1KB) | ~20 | 100-900 bytes |
| Small (1-5KB) | ~100 | 1-5 KB |
| Medium (5-20KB) | ~250 | 5-20 KB |
| Large (20-100KB) | ~90 | 20-100 KB |
| Very Large (> 100KB) | ~10 | 100-500 KB |

## Metadata

Each markdown file has an accompanying `.meta.json` file containing:

- Filename and category
- Size (bytes) and line count
- Source (all are "synthetic" in this corpus)
- Content characteristics:
  - `code_ratio`: Proportion of content in code blocks
  - `table_count`: Number of tables
  - `list_count`: Number of list items
  - `header_count`: Number of headers
  - `max_header_depth`: Maximum header nesting level
  - `code_block_count`: Number of fenced code blocks
  - `nesting_level`: Fence nesting depth (for nested fencing docs)
- Expected chunking strategy based on content analysis
- Content hash for deduplication verification

## Files

- `README.md` — Original corpus specification
- `INDEX.md` — This file
- `metadata_index.json` — JSON array of all document metadata
- `metadata.csv` — CSV export of metadata for analysis
- `COLLECTION_REPORT.md` — Generation report with statistics

## Usage

### Loading Documents

```python
from pathlib import Path
import json

corpus_root = Path("tests/corpus")

# Load a specific document
doc_path = corpus_root / "technical_docs" / "kubernetes" / "kubernetes_000.md"
content = doc_path.read_text()

# Load with metadata
meta_path = doc_path.with_suffix(".md.meta.json")
metadata = json.loads(meta_path.read_text())

print(f"Document: {metadata['filename']}")
print(f"Expected strategy: {metadata['expected_strategy']}")
print(f"Code ratio: {metadata['code_ratio']:.2%}")
```

### Filtering by Characteristics

```python
import json
from pathlib import Path

# Load all metadata
corpus_root = Path("tests/corpus")
metadata_index = json.loads((corpus_root / "metadata_index.json").read_text())

# Find code-heavy documents
code_heavy = [
    doc for doc in metadata_index
    if doc.get("code_ratio", 0) >= 0.5
]

# Find large structural documents
large_structural = [
    doc for doc in metadata_index
    if doc.get("header_count", 0) >= 5
    and doc.get("size_bytes", 0) > 20000
]

# Find documents with nested fencing
nested = [
    doc for doc in metadata_index
    if doc.get("nesting_level", 0) >= 3
]
```

### Benchmarking

```python
from markdown_chunker_v2 import MarkdownChunker
from pathlib import Path
import time

chunker = MarkdownChunker()
corpus_root = Path("tests/corpus")

results = []

for md_file in corpus_root.rglob("*.md"):
    if md_file.name in ["README.md", "INDEX.md", "COLLECTION_REPORT.md"]:
        continue
    
    content = md_file.read_text()
    
    start = time.time()
    result = chunker.chunk(content, include_analysis=True)
    elapsed = time.time() - start
    
    results.append({
        "file": str(md_file.relative_to(corpus_root)),
        "size": len(content),
        "chunks": len(result.chunks),
        "strategy": result.strategy_used,
        "time": elapsed,
    })

# Analyze results
import pandas as pd
df = pd.DataFrame(results)
print(df.groupby("strategy").agg({
    "time": ["mean", "median", "max"],
    "chunks": "mean",
}))
```

## Validation

The corpus has been validated for:

- ✓ Total file count >= 400 (actual: 470+)
- ✓ All categories represented per specification
- ✓ Size distribution covers all ranges
- ✓ Content characteristics varied (code, tables, lists, structure)
- ✓ All files are valid markdown (parseable)
- ✓ Metadata complete for all files
- ✓ Expected strategies distributed across all types

## Maintenance

To regenerate or extend the corpus:

```bash
# Full regeneration (creates 410 new documents)
python3 scripts/build_full_corpus.py

# Individual categories can be generated using:
python3 -c "
from scripts.corpus_builder.synthetic_generator import SyntheticGenerator
from pathlib import Path

gen = SyntheticGenerator(
    Path('tests/corpus/debug_logs'),
    category='debug_logs'
)
gen.generate(5)  # Generate 5 more debug logs
"
```

## License

All synthetic documents in this corpus are generated specifically for testing purposes and are part of the Advanced Markdown Chunker project. They are provided under the same MIT license as the project.

---

**Last Updated:** 2024-12-06  
**Generator Version:** 1.0  
**Total Documents:** 470+
