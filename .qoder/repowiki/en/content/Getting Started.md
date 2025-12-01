# Getting Started

<cite>
**Referenced Files in This Document**
- [README.md](file://README.md)
- [examples/basic_usage.py](file://examples/basic_usage.py)
- [examples/dify_integration.py](file://examples/dify_integration.py)
- [markdown_chunker/__init__.py](file://markdown_chunker/__init__.py)
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py)
- [markdown_chunker/chunker/core.py](file://markdown_chunker/chunker/core.py)
- [requirements.txt](file://requirements.txt)
- [main.py](file://main.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Basic Usage](#basic-usage)
5. [Configuration Options](#configuration-options)
6. [Advanced Examples](#advanced-examples)
7. [Dify Integration](#dify-integration)
8. [Expected Output Format](#expected-output-format)
9. [Common Pitfalls](#common-pitfalls)
10. [Verification Steps](#verification-steps)
11. [Next Steps](#next-steps)

## Introduction

The MarkdownChunker is an advanced Python library designed to intelligently split Markdown documents into semantically meaningful chunks. It features six adaptive chunking strategies that automatically select the optimal approach based on document content analysis, making it perfect for RAG (Retrieval-Augmented Generation) systems, knowledge bases, and document processing pipelines.

### Key Features

- **Intelligent Strategy Selection**: Automatically chooses between 6 specialized strategies (Code, Mixed, List, Table, Structural, Sentences)
- **Structural Awareness**: Preserves markdown structure, code blocks, and formatting
- **Adaptive Chunking**: Maintains semantic boundaries and context
- **Production Ready**: Comprehensive testing (1366+ tests) and property-based validation
- **Flexible Configuration**: Fine-tuned controls for different use cases

## Installation

### Prerequisites

The library requires Python 3.12 or higher and has several dependencies that will be installed automatically.

### Installation Methods

#### Method 1: Install from PyPI (Recommended)

```bash
pip install markdown-chunker
```

#### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/dify-markdown-chunker.git
cd dify-markdown-chunker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install
```

#### Method 3: Development Installation

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/dify-markdown-chunker.git
cd dify-markdown-chunker
pip install -e ".[dev]"
```

### Dependency Requirements

The library has the following core dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `markdown-it-py` | >=3.0.0 | Markdown parsing |
| `mistune` | >=3.0.0 | Alternative parser |
| `markdown` | >=3.4.0 | Markdown processing |
| `pydantic` | >=2.0.0 | Data validation |
| `dify_plugin` | ==0.5.0b15 | Dify integration |

Development dependencies (optional):
- `pytest` >=8.0.0 - Testing framework
- `hypothesis` >=6.0.0 - Property-based testing
- `black` >=23.0.0 - Code formatting
- `flake8` >=6.0.0 - Linting

**Section sources**
- [README.md](file://README.md#L43-L67)
- [requirements.txt](file://requirements.txt#L1-L21)

## Quick Start

### Minimal Working Example

Here's the simplest way to start using the MarkdownChunker:

```python
from markdown_chunker import MarkdownChunker

# Create chunker instance
chunker = MarkdownChunker()

# Process a simple markdown document
markdown_text = "# Hello World\n\nThis is a test document."
chunks = chunker.chunk(markdown_text)

# Print results
print(f"Generated {len(chunks)} chunks")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}: {chunk.size} characters")
    print(f"Preview: {chunk.content[:50]}...")
```

### Expected Output

```
Generated 1 chunks
Chunk 0: 43 characters
Preview: # Hello World
```

### With Analysis

For more detailed information about the chunking process:

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk_with_analysis("# Test\nContent")

print(f"Strategy used: {result.strategy_used}")
print(f"Total chunks: {len(result.chunks)}")
print(f"Processing time: {result.processing_time:.3f}s")
```

**Section sources**
- [examples/basic_usage.py](file://examples/basic_usage.py#L14-L48)
- [README.md](file://README.md#L81-L102)

## Basic Usage

### Importing the Library

```python
from markdown_chunker import MarkdownChunker, ChunkConfig
```

### Creating a Basic Chunker

```python
# Default configuration
chunker = MarkdownChunker()

# Custom configuration
config = ChunkConfig(max_chunk_size=2048, min_chunk_size=256)
chunker = MarkdownChunker(config)
```

### Processing Markdown Text

```python
# Simple chunking
markdown = "# Introduction\n\nThis is content."
chunks = chunker.chunk(markdown)

# With analysis
result = chunker.chunk_with_analysis(markdown)

# Using convenience functions
from markdown_chunker import chunk_text
chunks = chunk_text(markdown)
```

### Accessing Chunk Information

Each chunk contains valuable metadata:

```python
for i, chunk in enumerate(chunks):
    print(f"Chunk {i}:")
    print(f"  Content type: {chunk.content_type}")
    print(f"  Strategy: {chunk.strategy}")
    print(f"  Size: {chunk.size} chars")
    print(f"  Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"  Has overlap: {chunk.metadata.get('has_overlap', False)}")
```

**Section sources**
- [markdown_chunker/__init__.py](file://markdown_chunker/__init__.py#L50-L164)
- [examples/basic_usage.py](file://examples/basic_usage.py#L49-L87)

## Configuration Options

### Default Configuration

The default configuration works well for most documents:

```python
from markdown_chunker import ChunkConfig

config = ChunkConfig()
# max_chunk_size: 4096
# min_chunk_size: 512  
# target_chunk_size: 2048
# enable_overlap: True
# overlap_size: 200
```

### Custom Configuration

```python
config = ChunkConfig(
    max_chunk_size=2048,      # Maximum chunk size in characters
    min_chunk_size=256,       # Minimum chunk size
    target_chunk_size=1536,   # Target size
    enable_overlap=True,      # Enable overlapping chunks
    overlap_size=100,         # Overlap size in characters
    overlap_percentage=0.1    # Overlap as percentage of chunk size
)
```

### Predefined Configuration Profiles

The library provides optimized configurations for common use cases:

```python
# For code-heavy documentation
config = ChunkConfig.for_code_docs()

# For RAG systems (Dify default)
config = ChunkConfig.for_dify_rag()

# For API documentation
config = ChunkConfig.for_api_docs()

# For search indexing
config = ChunkConfig.for_search_indexing()

# For chat/LLM contexts
config = ChunkConfig.for_chat_context()
```

### Configuration Validation

The library automatically validates and adjusts configuration parameters:

```python
# Invalid values are auto-corrected
config = ChunkConfig(max_chunk_size=100, min_chunk_size=500)
# Automatically adjusts min_chunk_size to 500
```

**Section sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L497-L800)
- [examples/basic_usage.py](file://examples/basic_usage.py#L94-L137)

## Advanced Examples

### Customizing Chunk Size and Overlap

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Create custom configuration
config = ChunkConfig(
    max_chunk_size=1024,      # Smaller chunks
    min_chunk_size=128,       # Minimum size
    enable_overlap=True,      # Enable overlap
    overlap_size=50,          # Small overlap
    overlap_percentage=0.05   # 5% overlap
)

chunker = MarkdownChunker(config)

markdown = """
# Advanced Configuration Example

This document demonstrates custom chunking settings.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

result = chunker.chunk_with_analysis(markdown)

print(f"Generated {len(result.chunks)} chunks")
for i, chunk in enumerate(result.chunks):
    has_overlap = chunk.metadata.get('has_overlap', False)
    overlap_marker = " [OVERLAP]" if has_overlap else ""
    print(f"  Chunk {i}: {chunk.size} chars{overlap_marker}")
```

### Manual Strategy Selection

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()

# Force specific strategy
markdown = """
# Code Example

```python
def hello():
    return "world"
```
"""

# Use code strategy specifically
chunks = chunker.chunk(markdown, strategy="code")
print(f"Used strategy: {chunks[0].metadata['strategy']}")

# Try different strategies
for strategy in ["structural", "code", "list"]:
    chunks = chunker.chunk(markdown, strategy=strategy)
    print(f"{strategy}: {len(chunks)} chunks")
```

### Processing Different Document Types

```python
# Code-heavy document
code_doc = """
# API Reference

```python
class UserAPI:
    def get_user(self, user_id):
        return self.db.query(user_id)
    
    def create_user(self, data):
        return self.db.insert(data)
```

```javascript
function processOrder(order) {
    return api.post('/orders', order);
}
```
"""

# List-heavy document
list_doc = """
# Project Tasks

## Development Phase
- Set up environment
  - Install Python
  - Create virtualenv
  - Install dependencies
- Write code
  - Implement features
  - Add tests
  - Write documentation

## Deployment Phase
- Prepare deployment
  - Build artifacts
  - Configure servers
  - Set up monitoring
"""

# Table-heavy document
table_doc = """
# Data Report

| Name | Age | City | Status |
|------|-----|------|--------|
| Alice | 30 | NYC | Active |
| Bob | 25 | LA | Active |
| Carol | 35 | Chicago | Inactive |
"""
```

**Section sources**
- [examples/basic_usage.py](file://examples/basic_usage.py#L139-L364)

## Dify Integration

### For Dify Users

If you're migrating from Dify's built-in markdown chunker, the library provides seamless integration:

```yaml
# In Dify workflow configuration
- tool: markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
```

### Python Integration Example

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Create chunker optimized for Dify RAG
config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

# Process document
markdown = """
# Product Documentation

## Overview

Our product helps you manage your workflow efficiently.

## Features

- Task management
- Team collaboration
- Real-time updates
"""

result = chunker.chunk_with_analysis(markdown)

# Prepare for Dify
dify_chunks = []
for chunk in result.chunks:
    dify_chunk = {
        "content": chunk.content,
        "metadata": {
            "source": "documentation",
            "chunk_id": f"chunk_{chunk.start_line}_{chunk.end_line}",
            "lines": f"{chunk.start_line}-{chunk.end_line}",
            "size": chunk.size,
            "type": chunk.content_type
        }
    }
    dify_chunks.append(dify_chunk)
```

### RAG-Optimized Configuration

```python
# Configuration optimized for RAG systems
config = ChunkConfig(
    max_chunk_size=1536,  # Optimal for embedding models
    min_chunk_size=200,
    overlap_size=200,     # Overlap for context preservation
    enable_overlap=True
)

chunker = MarkdownChunker(config)
```

**Section sources**
- [examples/dify_integration.py](file://examples/dify_integration.py#L17-L487)
- [README.md](file://README.md#L69-L81)

## Expected Output Format

### Chunk Object Structure

Each chunk contains the following properties:

```python
from markdown_chunker import Chunk

# Chunk properties
print(f"Content: {chunk.content}")           # Actual markdown content
print(f"Start line: {chunk.start_line}")     # Starting line number (1-based)
print(f"End line: {chunk.end_line}")         # Ending line number (1-based)
print(f"Size: {chunk.size}")                 # Character count
print(f"Content type: {chunk.content_type}") # "code", "text", "list", "table", etc.
print(f"Strategy: {chunk.strategy}")         # Applied strategy
print(f"Metadata: {chunk.metadata}")         # Additional information
```

### Chunk Metadata

Common metadata fields:

| Field | Description | Example |
|-------|-------------|---------|
| `content_type` | Type of content | `"code"`, `"text"`, `"list"` |
| `strategy` | Applied strategy | `"code"`, `"structural"` |
| `language` | Programming language | `"python"`, `"javascript"` |
| `has_overlap` | Is overlapping chunk | `True`/`False` |
| `allow_oversize` | Allowed oversized chunk | `True`/`False` |
| `section_path` | Hierarchical path | `["Chapter 1", "Introduction"]` |

### ChunkingResult Structure

When using `chunk_with_analysis()`:

```python
from markdown_chunker import MarkdownChunker

chunker = MarkdownChunker()
result = chunker.chunk_with_analysis("# Test\nContent")

print(f"Strategy used: {result.strategy_used}")
print(f"Total chunks: {len(result.chunks)}")
print(f"Processing time: {result.processing_time:.3f}s")
print(f"Complexity score: {result.complexity_score:.2f}")
print(f"Success: {result.success}")
```

**Section sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L37-L496)

## Common Pitfalls

### 1. Empty or Whitespace Documents

```python
# Problem: Empty content
chunker.chunk("")  # May produce empty chunks

# Solution: Check content first
if markdown.strip():
    chunks = chunker.chunk(markdown)
else:
    print("Empty document")
```

### 2. Incorrect Encoding

```python
# Problem: Non-UTF-8 encoded text
try:
    chunks = chunker.chunk(bad_encoded_text)
except UnicodeDecodeError:
    print("Encoding issue")

# Solution: Ensure UTF-8 encoding
markdown = raw_text.encode('utf-8').decode('utf-8')
```

### 3. Strategy Not Found

```python
# Problem: Invalid strategy name
try:
    chunks = chunker.chunk(text, strategy="invalid")
except StrategySelectionError:
    print("Strategy not found")

# Solution: Use available strategies
available = chunker.get_available_strategies()
print(f"Available strategies: {available}")
```

### 4. Memory Issues with Large Documents

```python
# Problem: Large documents consuming memory
large_doc = "..." * 100000  # Very large text
chunks = chunker.chunk(large_doc)  # May cause memory issues

# Solution: Use streaming or smaller chunks
config = ChunkConfig(max_chunk_size=1024)  # Smaller chunks
chunker = MarkdownChunker(config)
```

### 5. Import Errors

```python
# Problem: Missing dependencies
# ImportError: No module named 'markdown_chunker'

# Solution: Install with dependencies
pip install markdown-chunker
```

**Section sources**
- [markdown_chunker/chunker/core.py](file://markdown_chunker/chunker/core.py#L347-L408)

## Verification Steps

### Step 1: Basic Import Test

```python
# Test 1: Can import the library
try:
    from markdown_chunker import MarkdownChunker
    print("✓ Successfully imported MarkdownChunker")
except ImportError as e:
    print(f"✗ Import failed: {e}")

# Test 2: Check version
try:
    from markdown_chunker import __version__
    print(f"✓ Version: {__version__}")
except:
    print("✗ Version check failed")
```

### Step 2: Simple Functionality Test

```python
# Test 3: Basic chunking works
try:
    chunker = MarkdownChunker()
    test_text = "# Test\nContent"
    chunks = chunker.chunk(test_text)
    print(f"✓ Chunked {len(chunks)} chunks successfully")
except Exception as e:
    print(f"✗ Basic functionality failed: {e}")
```

### Step 3: Configuration Test

```python
# Test 4: Configuration validation
try:
    from markdown_chunker import ChunkConfig
    config = ChunkConfig(max_chunk_size=2048, min_chunk_size=256)
    print("✓ Configuration validated successfully")
except Exception as e:
    print(f"✗ Configuration validation failed: {e}")
```

### Step 4: Strategy Availability Test

```python
# Test 5: Check available strategies
try:
    chunker = MarkdownChunker()
    strategies = chunker.get_available_strategies()
    print(f"✓ Available strategies: {strategies}")
except Exception as e:
    print(f"✗ Strategy availability check failed: {e}")
```

### Step 5: Complete Workflow Test

```python
# Test 6: Full workflow test
try:
    chunker = MarkdownChunker()
    markdown = """
    # Test Document
    
    This is a test document for verification.
    
    ```python
    def test():
        return True
    ```
    """
    
    result = chunker.chunk_with_analysis(markdown)
    
    if result.success and len(result.chunks) > 0:
        print("✓ Complete workflow test passed")
        print(f"  Strategy: {result.strategy_used}")
        print(f"  Chunks: {len(result.chunks)}")
        print(f"  Processing time: {result.processing_time:.3f}s")
    else:
        print("✗ Complete workflow test failed")
        
except Exception as e:
    print(f"✗ Complete workflow test failed: {e}")
```

**Section sources**
- [tests/test_entry_point.py](file://tests/test_entry_point.py#L15-L240)

## Next Steps

### 1. Explore Advanced Features

- Learn about [different chunking strategies](file://examples/basic_usage.py#L139-L166)
- Experiment with [custom configurations](file://examples/basic_usage.py#L94-L137)
- Understand [metadata enrichment](file://examples/basic_usage.py#L28-L48)

### 2. Production Deployment

- Set up [performance monitoring](file://markdown_chunker/chunker/core.py#L661-L703)
- Implement [error handling](file://markdown_chunker/chunker/errors.py)
- Configure [logging](file://markdown_chunker/logging_config.py)

### 3. Integration Patterns

- [Dify plugin integration](file://examples/dify_integration.py#L193-L262)
- [API endpoint simulation](file://examples/dify_integration.py#L193-L262)
- [Batch processing](file://examples/dify_integration.py#L264-L309)

### 4. Performance Optimization

- [Context window optimization](file://examples/dify_integration.py#L368-L395)
- [Embedding preparation](file://examples/dify_integration.py#L314-L367)
- [Memory management](file://markdown_chunker/chunker/core.py#L661-L703)

### 5. Testing and Validation

- Run [comprehensive tests](file://README.md#L149-L162)
- Use [property-based testing](file://README.md#L194-L204)
- Validate [data completeness](file://markdown_chunker/chunker/validator.py)