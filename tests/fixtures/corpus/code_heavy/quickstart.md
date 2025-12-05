# 🚀 Quick Start

Get started with Dify Markdown Chunker in 5 minutes.

## 📦 Installation

### As Dify Plugin

1. Download the plugin package (`.difypkg` file)
2. In Dify UI: Settings → Plugins → Install Plugin
3. Upload the `.difypkg` file
4. Configure the plugin in your workflows

### For Development

```bash
# Clone the repository
git clone <repository-url>
cd dify-markdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
make test
```

## 🎯 Basic Usage

### Using in Dify Workflows

```yaml
# In Dify workflow configuration
- tool: markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
```

### Using as Python Library

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Basic usage
chunker = MarkdownChunker()
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)

print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
for i, chunk in enumerate(result.chunks, 1):
    print(f"Chunk {i}: {chunk.size} chars, lines {chunk.start_line}-{chunk.end_line}")
```

### With Custom Configuration

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Custom configuration
config = ChunkConfig(
    max_chunk_size=2048,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100
)

chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)

# Access analysis
print(f"Content type: {result.analysis.content_type}")
print(f"Code ratio: {result.analysis.code_ratio:.2%}")
print(f"Complexity: {result.analysis.complexity_score:.2f}")
```

### Using Configuration Profiles

```python
from markdown_chunker import ChunkConfig

# For API documentation
config = ChunkConfig.for_api_docs()

# For code documentation
config = ChunkConfig.for_code_docs()

# For RAG systems (Dify default)
config = ChunkConfig.for_dify_rag()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

## 📝 Example: Processing a Document

```python
from markdown_chunker import MarkdownChunker

markdown_text = """
# API Documentation

## Introduction

This is example documentation with code:

```python
def hello_world():
    print("Hello, World!")
    return "success"
```

### Features

- Multiple language support
- Automatic content type detection
- Metadata extraction

| Parameter | Type | Description |
|-----------|------|-------------|
| name | str | Function name |
| result | any | Execution result |
"""

# Process document
chunker = MarkdownChunker()
result = chunker.chunk(markdown_text, include_analysis=True)

# Print results
print(f"📄 Processed document: {result.analysis.total_chars} chars")
print(f"🔍 Found elements:")
print(f"  - Headers: {result.analysis.header_count}")
print(f"  - Code blocks: {result.analysis.code_block_count}")
print(f"  - Lists: {result.analysis.list_count}")
print(f"  - Tables: {result.analysis.table_count}")
print(f"📊 Content type: {result.analysis.content_type}")
print(f"⚡ Strategy used: {result.strategy_used}")
print(f"📦 Created {len(result.chunks)} chunks")
```

## 🔧 Advanced Usage

### Using Parser Interface

```python
from markdown_chunker import ParserInterface

# Parse markdown
parser = ParserInterface()
analysis = parser.analyze("# Hello\n\n```python\nprint('world')\n```")

print(f"Content type: {analysis.content_type}")
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Complexity: {analysis.complexity_score:.2f}")
```

### Extracting Preamble

```python
from markdown_chunker import extract_preamble

markdown_with_frontmatter = """---
title: My Document
author: John Doe
---

# Content starts here
"""

preamble = extract_preamble(markdown_with_frontmatter)
if preamble:
    print(f"Preamble type: {preamble.type}")
    print(f"Preamble content: {preamble.content}")
    print(f"Remaining text: {preamble.remaining_text[:50]}...")
```

### Convenience Functions

```python
from markdown_chunker import chunk_text, chunk_file

# Chunk text directly
chunks = chunk_text("# Hello\n\nWorld")

# Chunk from file
chunks = chunk_file("README.md")

# With custom config
from markdown_chunker import ChunkConfig
config = ChunkConfig.for_code_docs()
chunks = chunk_file("docs/api.md", config)
```

## 🎨 Chunking Strategies

The chunker automatically selects the best strategy based on content analysis:

1. **Code Strategy**: For code-heavy documents (>30% code)
2. **Mixed Strategy**: For balanced content (code + text)
3. **List Strategy**: For list-heavy documents
4. **Table Strategy**: For table-heavy documents
5. **Structural Strategy**: For well-structured documents with headers
6. **Sentences Strategy**: Fallback for simple text

You can also force a specific strategy:

```python
config = ChunkConfig(force_strategy="code")
chunker = MarkdownChunker(config)
```

## 🧪 Testing Your Setup

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-coverage

# Run quick tests only
make test-quick
```

## 📚 Next Steps

1. Read the [Usage Guide](usage.md) for detailed examples
2. Check the [API Reference](api/README.md) for complete API documentation
3. Learn about [Chunking Strategies](architecture/strategies.md)
4. See [Configuration Reference](reference/configuration.md) for all options
5. Review [Dify Integration](architecture/dify-integration.md) for workflow setup

## 🆘 Troubleshooting

### Import Errors

```python
# ❌ Wrong
from stage1 import process_markdown

# ✅ Correct
from markdown_chunker import MarkdownChunker
```

### Configuration Issues

```python
# Make sure to use ChunkConfig
from markdown_chunker import ChunkConfig

config = ChunkConfig(max_chunk_size=2048)
```

### Common Issues

- **"Module not found"**: Make sure you installed dependencies: `pip install -r requirements.txt`
- **"Tests failing"**: Activate virtual environment: `source venv/bin/activate`
- **"Import errors"**: Use correct imports from `markdown_chunker` package

For more help, see [Troubleshooting Guide](guides/troubleshooting.md).
