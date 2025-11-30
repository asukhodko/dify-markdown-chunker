# Getting Started with Python Markdown Chunker

Welcome to the Python Markdown Chunker tutorial! This guide will help you get started with chunking markdown documents for RAG applications.

## What is Markdown Chunking?

Markdown chunking is the process of splitting large markdown documents into smaller, semantically meaningful pieces. This is essential for:

- **RAG (Retrieval-Augmented Generation)**: Breaking documents into chunks that fit in LLM context windows
- **Search Indexing**: Creating searchable document fragments
- **Content Analysis**: Processing documents in manageable pieces

## Installation

Install the package using pip:

```bash
pip install markdown-chunker
```

Or install from source:

```bash
git clone https://github.com/example/markdown-chunker.git
cd markdown-chunker
pip install -e .
```

## Quick Start

Here's a simple example to get you started:

```python
from markdown_chunker import MarkdownChunker

# Create a chunker with default settings
chunker = MarkdownChunker()

# Your markdown content
markdown_text = """
# My Document

This is a sample document with multiple sections.

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

# Chunk the document
chunks = chunker.chunk(markdown_text)

# Print the chunks
for i, chunk in enumerate(chunks, 1):
    print(f"Chunk {i}:")
    print(f"  Lines: {chunk.start_line}-{chunk.end_line}")
    print(f"  Size: {chunk.size} chars")
    print(f"  Content: {chunk.content[:50]}...")
    print()
```

## Configuration

Customize chunking behavior with `ChunkConfig`:

```python
from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# Create custom configuration
config = ChunkConfig(
    max_chunk_size=2048,      # Maximum chunk size in characters
    min_chunk_size=256,       # Minimum chunk size
    enable_overlap=True,      # Enable chunk overlap
    overlap_size=100,         # Overlap size in characters
    preserve_code_blocks=True # Keep code blocks intact
)

# Use custom config
chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown_text)
```

## Configuration Profiles

Use pre-configured profiles for common use cases:

```python
# For code-heavy documents
config = ChunkConfig.for_code_heavy()

# For RAG applications (Dify, LangChain, etc.)
config = ChunkConfig.for_dify_rag()

# For chat/LLM context
config = ChunkConfig.for_chat_context()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

## Working with Chunks

Each chunk contains useful metadata:

```python
chunks = chunker.chunk(markdown_text)

for chunk in chunks:
    # Basic properties
    print(f"Content: {chunk.content}")
    print(f"Size: {chunk.size} characters")
    print(f"Lines: {chunk.start_line} to {chunk.end_line}")
    
    # Metadata
    print(f"Type: {chunk.content_type}")
    print(f"Strategy: {chunk.strategy}")
    
    # Check for code
    if chunk.content_type == "code":
        print(f"Language: {chunk.language}")
    
    # Check if oversized
    if chunk.is_oversize:
        print("Warning: Chunk exceeds max size")
```

## Advanced Features

### Strategy Selection

The chunker automatically selects the best strategy based on content:

```python
# Get detailed analysis
result = chunker.chunk(markdown_text, include_analysis=True)

print(f"Strategy used: {result.strategy_used}")
print(f"Total chunks: {result.total_chunks}")
print(f"Processing time: {result.processing_time:.3f}s")
print(f"Content type: {result.content_type}")
```

### Manual Strategy Override

Force a specific chunking strategy:

```python
# Use structural strategy (header-based)
chunks = chunker.chunk(markdown_text, strategy="structural")

# Use code strategy
chunks = chunker.chunk(code_doc, strategy="code")

# Available strategies:
# - "structural": Header-based chunking
# - "code": For code-heavy documents
# - "sentences": Simple sentence-based
# - "list": For list-heavy documents
# - "table": For table-heavy documents
# - "mixed": For mixed content
```

### Dictionary Format

Get results as dictionaries for JSON serialization:

```python
# Get as dictionary
result = chunker.chunk(markdown_text, return_format="dict")

# Now you can serialize to JSON
import json
json_data = json.dumps(result, indent=2)
print(json_data)
```

## Best Practices

### 1. Choose Appropriate Chunk Sizes

```python
# For RAG with GPT-3.5 (4K context)
config = ChunkConfig(max_chunk_size=1024)

# For RAG with GPT-4 (8K context)
config = ChunkConfig(max_chunk_size=2048)

# For Claude (100K context)
config = ChunkConfig(max_chunk_size=4096)
```

### 2. Enable Overlap for Better Context

```python
config = ChunkConfig(
    enable_overlap=True,
    overlap_size=200,  # 200 characters overlap
    overlap_percentage=0.1  # 10% overlap
)
```

### 3. Preserve Important Elements

```python
config = ChunkConfig(
    preserve_code_blocks=True,  # Keep code blocks intact
    preserve_tables=True,       # Keep tables intact
    preserve_list_hierarchy=True # Keep list items together
)
```

## Common Use Cases

### RAG Application

```python
from markdown_chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# Configure for RAG
config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)

# Process document
with open('documentation.md', 'r') as f:
    content = f.read()

chunks = chunker.chunk(content)

# Store in vector database
for chunk in chunks:
    vector_db.add(
        text=chunk.content,
        metadata={
            'source': 'documentation.md',
            'lines': f"{chunk.start_line}-{chunk.end_line}",
            'type': chunk.content_type
        }
    )
```

### Search Indexing

```python
config = ChunkConfig.for_search_indexing()
chunker = MarkdownChunker(config)

chunks = chunker.chunk(content)

for chunk in chunks:
    search_index.add_document(
        id=f"doc_{chunk.start_line}",
        content=chunk.content,
        metadata=chunk.metadata
    )
```

## Troubleshooting

### Chunks Too Large

If chunks exceed your size limits:

```python
config = ChunkConfig(
    max_chunk_size=1024,  # Reduce max size
    allow_oversize=False  # Strict size enforcement
)
```

### Content Loss

Verify no content is lost:

```python
result = chunker.chunk(content, include_analysis=True)

# Check for errors
if result.errors:
    print("Errors:", result.errors)

# Verify content
original_size = len(content)
chunked_size = sum(len(c.content) for c in result.chunks)
print(f"Original: {original_size}, Chunked: {chunked_size}")
```

## Next Steps

- Read the [API Documentation](api_documentation.md)
- Check out [Examples](examples/)
- Join our [Community](https://community.example.com)

## Support

Need help? Contact us:
- Email: support@example.com
- GitHub: https://github.com/example/markdown-chunker
- Discord: https://discord.gg/example
