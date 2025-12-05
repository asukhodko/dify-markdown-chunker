# Standalone Library Usage

<cite>
**Referenced Files in This Document**
- [markdown_chunker/__init__.py](file://markdown_chunker/__init__.py)
- [markdown_chunker_v2/chunker.py](file://markdown_chunker_v2/chunker.py)
- [markdown_chunker_v2/config.py](file://markdown_chunker_v2/config.py)
- [markdown_chunker_v2/types.py](file://markdown_chunker_v2/types.py)
- [markdown_chunker_v2/compat.py](file://markdown_chunker_v2/compat.py)
- [markdown_chunker_v2/parser.py](file://markdown_chunker_v2/parser.py)
- [examples/rag_integration.py](file://examples/rag_integration.py)
- [examples/api_usage.py](file://examples/api_usage.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Installation and Setup](#installation-and-setup)
3. [Basic Usage](#basic-usage)
4. [Configuration Options](#configuration-options)
5. [Chunking Methods](#chunking-methods)
6. [Advanced Integration Patterns](#advanced-integration-patterns)
7. [API Adapter Usage](#api-adapter-usage)
8. [Configuration Profiles](#configuration-profiles)
9. [Common Issues and Solutions](#common-issues-and-solutions)
10. [Performance Considerations](#performance-considerations)
11. [Best Practices](#best-practices)

## Introduction

The Markdown Chunker is a production-ready library designed for splitting Markdown documents into semantically meaningful chunks, optimized for Retrieval-Augmented Generation (RAG) systems and AI applications. It provides sophisticated chunking strategies that preserve document structure while maintaining context and metadata.

The library offers multiple integration approaches:
- **Direct API**: Import and instantiate `MarkdownChunker` directly
- **API Adapter**: REST API-compatible interface for web services
- **Convenience Functions**: Simple functions for basic use cases
- **Configuration Profiles**: Pre-built configurations for common scenarios

## Installation and Setup

The library is distributed as a Python package with automatic installation of dependencies.

```bash
pip install markdown-chunker
```

### Basic Import

```python
from markdown_chunker import MarkdownChunker, ChunkConfig
```

### Alternative Imports

```python
# Individual components
from markdown_chunker import chunk_text, chunk_file

# Legacy compatibility
from markdown_chunker import LegacyMarkdownChunker, LegacyChunkConfig
```

**Section sources**
- [markdown_chunker/__init__.py](file://markdown_chunker/__init__.py#L1-L33)

## Basic Usage

### Simple Chunking

The most straightforward way to use the library is with the `chunk_text` convenience function:

```python
from markdown_chunker import chunk_text

markdown_content = """
# Getting Started

This is a sample markdown document.

## Features

- Easy to use
- Intelligent chunking
- Metadata preservation

```python
def example():
    return "Hello, World!"
```
"""

chunks = chunk_text(markdown_content)
for chunk in chunks:
    print(f"Chunk {chunk.metadata.get('chunk_index', '?')}: "
          f"{len(chunk.content)} chars, "
          f"type: {chunk.metadata.get('content_type', 'text')}")
```

### Manual Chunker Instantiation

For more control, instantiate `MarkdownChunker` directly:

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Create configuration
config = ChunkConfig(
    max_chunk_size=1024,
    min_chunk_size=256,
    enable_overlap=True,
    overlap_size=100
)

# Instantiate chunker
chunker = MarkdownChunker(config)

# Process markdown
markdown_content = "# Document Title\n\nContent here..."
chunks = chunker.chunk(markdown_content)

# Access chunk metadata
for chunk in chunks:
    print(f"Lines {chunk.start_line}-{chunk.end_line}: "
          f"{chunk.size} chars, "
          f"strategy: {chunk.metadata.get('strategy')}")
```

**Section sources**
- [markdown_chunker_v2/compat.py](file://markdown_chunker_v2/compat.py#L97-L106)
- [markdown_chunker_v2/chunker.py](file://markdown_chunker_v2/chunker.py#L43-L90)

## Configuration Options

### Core Configuration Parameters

The `ChunkConfig` class provides fine-grained control over chunking behavior:

```python
from markdown_chunker import ChunkConfig

config = ChunkConfig(
    # Size parameters
    max_chunk_size=4096,      # Maximum chunk size in characters
    min_chunk_size=512,       # Minimum chunk size in characters
    overlap_size=200,         # Overlap between chunks (0 = disabled)
    
    # Behavior parameters
    preserve_atomic_blocks=True,  # Keep code blocks and tables intact
    extract_preamble=True,        # Extract content before first header
    
    # Strategy selection thresholds
    code_threshold=0.3,           # Code ratio threshold for CodeAwareStrategy
    structure_threshold=3,        # Header count threshold for StructuralStrategy
    
    # Override parameters
    strategy_override=None        # Force specific strategy
)
```

### Configuration Validation

The library automatically validates configuration parameters:

```python
# Invalid configurations are automatically corrected
config = ChunkConfig(max_chunk_size=100, min_chunk_size=2000)
# Automatically adjusts min_chunk_size to 500 (half of max_chunk_size)

# Overlap size validation
config = ChunkConfig(max_chunk_size=500, overlap_size=600)
# Raises ValueError: overlap_size must be less than max_chunk_size
```

### Legacy Configuration Compatibility

For backward compatibility with older versions:

```python
from markdown_chunker import LegacyChunkConfig

# Legacy parameter names are mapped to new ones
config = LegacyChunkConfig.create(
    max_size=2048,      # Maps to max_chunk_size
    min_size=256,       # Maps to min_chunk_size
    enable_overlap=True # Maps to overlap_size > 0
)
```

**Section sources**
- [markdown_chunker_v2/config.py](file://markdown_chunker_v2/config.py#L12-L170)
- [markdown_chunker_v2/compat.py](file://markdown_chunker_v2/compat.py#L17-L55)

## Chunking Methods

### Available Methods

The `MarkdownChunker` class provides several chunking methods, each serving different use cases:

#### 1. `chunk(md_text: str) -> List[Chunk]`

Returns a list of `Chunk` objects with basic metadata.

```python
chunks = chunker.chunk("""
# Quick Start

This is a simple example.

## Features

- Fast processing
- Smart splitting
""")

for chunk in chunks:
    print(f"Lines {chunk.start_line}-{chunk.end_line}: "
          f"{chunk.size} chars")
```

#### 2. `chunk_with_analysis(md_text: str) -> tuple[List[Chunk], str, ContentAnalysis]`

Returns chunks plus strategy name and content analysis.

```python
chunks, strategy, analysis = chunker.chunk_with_analysis(markdown_content)

print(f"Used strategy: {strategy}")
print(f"Content type: {analysis.content_type}")
print(f"Code ratio: {analysis.code_ratio:.2f}")
```

#### 3. `chunk_with_metrics(md_text: str) -> tuple[List[Chunk], ChunkingMetrics]`

Returns chunks plus performance metrics.

```python
chunks, metrics = chunker.chunk_with_metrics(markdown_content)

print(f"Average chunk size: {metrics.avg_chunk_size:.1f}")
print(f"Standard deviation: {metrics.std_dev_size:.1f}")
print(f"Undersize chunks: {metrics.undersize_count}")
```

### Return Types

#### Chunk Object Structure

Each `Chunk` contains:
- `content`: The actual text content
- `start_line`: Starting line number (1-indexed)
- `end_line`: Ending line number (1-indexed)
- `metadata`: Dictionary with additional information

#### Metadata Fields

Key metadata fields automatically populated:
- `chunk_index`: Sequential index of the chunk
- `content_type`: 'text', 'code', 'table', or 'mixed'
- `has_code`: Boolean indicating presence of code blocks
- `strategy`: Strategy used for chunking
- `header_path`: List of parent headers (if available)

**Section sources**
- [markdown_chunker_v2/chunker.py](file://markdown_chunker_v2/chunker.py#L43-L128)
- [markdown_chunker_v2/types.py](file://markdown_chunker_v2/types.py#L100-L187)

## Advanced Integration Patterns

### RAG Pipeline Integration

The library provides specialized patterns for Retrieval-Augmented Generation systems:

#### Embedding Preparation

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

def prepare_chunks_for_embeddings(markdown: str, max_chunk_size: int = 500) -> List[Dict[str, Any]]:
    """Prepare markdown chunks for embedding generation."""
    
    config = ChunkConfig(
        max_chunk_size=max_chunk_size,
        min_chunk_size=100,
        enable_overlap=True,
        overlap_size=50
    )
    
    chunker = MarkdownChunker(config)
    result = chunker.chunk_with_analysis(markdown)
    
    embeddings_data = []
    for chunk in result.chunks:
        embeddings_data.append({
            'id': f"chunk_{chunk.index}",
            'text': chunk.content,
            'metadata': {
                'chunk_index': chunk.index,
                'lines': f"{chunk.start_line}-{chunk.end_line}",
                'size': chunk.size,
                'content_type': chunk.metadata.get('content_type', 'text'),
                'strategy': result.strategy_used,
                'has_code': 'language' in chunk.metadata,
                'has_table': 'column_count' in chunk.metadata,
                'has_list': 'list_type' in chunk.metadata,
                'complexity': result.complexity_score,
            }
        })
    
    return embeddings_data
```

#### Vector Database Preparation

```python
def prepare_for_vector_database(documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """Prepare multiple documents for vector database storage."""
    
    chunker = MarkdownChunker(ChunkConfig(
        max_chunk_size=500,
        enable_overlap=True,
        overlap_size=50
    ))
    
    all_chunks = []
    
    for doc in documents:
        doc_id = doc['id']
        content = doc['content']
        
        result = chunker.chunk_with_analysis(content)
        
        for chunk in result.chunks:
            all_chunks.append({
                'id': f"{doc_id}_chunk_{chunk.index}",
                'doc_id': doc_id,
                'chunk_id': chunk.index,
                'text': chunk.content,
                'metadata': {
                    'doc_id': doc_id,
                    'chunk_index': chunk.index,
                    'total_chunks': len(result.chunks),
                    'lines': f"{chunk.start_line}-{chunk.end_line}",
                    'size': chunk.size,
                    'strategy': result.strategy_used,
                    'content_type': result.content_type,
                    **chunk.metadata
                }
            })
    
    return all_chunks
```

#### Context Window Creation

```python
def create_context_window(chunks: List[Dict[str, Any]], target_chunk_id: str, window_size: int = 2) -> str:
    """Create context window around a target chunk for RAG."""
    
    # Find target chunk index
    target_idx = next((i for i, chunk in enumerate(chunks) if chunk['id'] == target_chunk_id), None)
    
    if target_idx is None:
        return ""
    
    # Get window
    start_idx = max(0, target_idx - window_size)
    end_idx = min(len(chunks), target_idx + window_size + 1)
    
    window_chunks = chunks[start_idx:end_idx]
    
    # Combine with markers
    context_parts = []
    for chunk in window_chunks:
        marker = ">>> TARGET <<<" if chunk['id'] == target_chunk_id else ""
        context_parts.append(f"{marker}\n{chunk['text']}\n")
    
    return "\n".join(context_parts)
```

**Section sources**
- [examples/rag_integration.py](file://examples/rag_integration.py#L13-L432)

### Content Type Filtering

```python
def filter_chunks_by_type(chunks: List[Dict[str, Any]], content_type: str) -> List[Dict[str, Any]]:
    """Filter chunks by content type."""
    return [
        chunk for chunk in chunks
        if chunk['metadata'].get('content_type') == content_type
    ]

def get_code_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get only chunks containing code."""
    return [
        chunk for chunk in chunks
        if chunk['metadata'].get('has_code', False)
    ]

def get_table_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get only chunks containing tables."""
    return [
        chunk for chunk in chunks
        if chunk['metadata'].get('has_table', False)
    ]
```

**Section sources**
- [examples/rag_integration.py](file://examples/rag_integration.py#L139-L171)

## API Adapter Usage

### REST API Integration

The library provides an `APIAdapter` class for REST API integration:

```python
from markdown_chunker.api import APIAdapter, APIRequest, APIResponse

# Create adapter
adapter = APIAdapter()

# Create request
request = APIRequest(
    content="# Hello World\n\nThis is a test document.",
    config=None,  # Use defaults
    strategy="auto"
)

# Process request
response = adapter.process_request(request)

if response.success:
    print(f"Chunks: {len(response.chunks)}")
    print(f"Strategy: {response.metadata['strategy_used']}")
    
    for i, chunk in enumerate(response.chunks):
        print(f"Chunk {i}: {chunk['content'][:50]}...")
else:
    print(f"Error: {response.error['message']}")
```

### Custom Configuration

```python
adapter = APIAdapter()

request = APIRequest(
    content="""
    # API Documentation
    
    ## Overview
    
    This is an API documentation example.
    
    ```python
    def hello():
        return "world"
    ```
    
    ## Endpoints
    
    - GET /users
    - POST /users
    - DELETE /users
    """,
    config={
        "max_chunk_size": 500,
        "min_chunk_size": 100,
        "enable_overlap": True,
        "overlap_size": 50
    },
    strategy="auto"
)

response = adapter.process_request(request)

if response.success:
    print(f"Chunks: {len(response.chunks)}")
    print(f"Processing time: {response.metadata['processing_time']:.3f}s")
    
    # Access statistics
    stats = response.metadata['statistics']
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Avg chunk size: {stats['avg_chunk_size']:.1f} chars")
```

### Error Handling

```python
def example_error_handling():
    """Example of robust error handling."""
    
    adapter = APIAdapter()
    
    test_cases = [
        {
            "name": "Empty content",
            "request": APIRequest(content="", config=None)
        },
        {
            "name": "Invalid strategy",
            "request": APIRequest(
                content="# Test",
                strategy="invalid_strategy"
            )
        },
        {
            "name": "Invalid config",
            "request": APIRequest(
                content="# Test",
                config={"max_chunk_size": -100}
            )
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        response = adapter.process_request(test['request'])
        
        if not response.success:
            print(f"  ❌ Error (expected): {response.error['message']}")
            print(f"  Error code: {response.error.get('code', 'N/A')}")
        else:
            print(f"  ✅ Unexpectedly succeeded")
```

### JSON Serialization

```python
import json

adapter = APIAdapter()

request = APIRequest(content="# Test\n\nContent here.")
response = adapter.process_request(request)

if response.success:
    # Convert to JSON
    response_dict = {
        "success": response.success,
        "chunks": response.chunks,
        "metadata": response.metadata
    }
    
    json_str = json.dumps(response_dict, indent=2)
    
    # Parse back
    parsed = json.loads(json_str)
    print(f"JSON round-trip successful: {len(parsed['chunks'])} chunks")
```

**Section sources**
- [examples/api_usage.py](file://examples/api_usage.py#L16-L356)

## Configuration Profiles

### Pre-built Profiles

The library provides several pre-configured profiles optimized for specific use cases:

#### 1. Default Profile

```python
from markdown_chunker import ChunkConfig

# Balanced settings for general use
config = ChunkConfig.default()
# Equivalent to: ChunkConfig()
```

#### 2. Code-Heavy Documents

```python
# Optimized for technical documentation
config = ChunkConfig.for_code_heavy()
# - max_chunk_size: 8192
# - min_chunk_size: 1024
# - overlap_size: 100
# - code_threshold: 0.2
```

#### 3. Structured Documents

```python
# Optimized for documents with clear structure
config = ChunkConfig.for_structured()
# - max_chunk_size: 4096
# - min_chunk_size: 512
# - overlap_size: 200
# - structure_threshold: 2
```

#### 4. Chat Context

```python
# Optimized for LLM chat contexts
config = ChunkConfig.for_chat_context()
# - max_chunk_size: 1536
# - min_chunk_size: 200
# - overlap_size: 200
# - code_ratio_threshold: 0.5
```

#### 5. Search Indexing

```python
# Optimized for search engines
config = ChunkConfig.for_search_indexing()
# - max_chunk_size: 1024
# - min_chunk_size: 100
# - overlap_size: 100
# - code_ratio_threshold: 0.4
```

### Custom Profiles

```python
class CustomProfiles:
    @classmethod
    def for_api_docs(cls) -> ChunkConfig:
        """Configuration optimized for API documentation."""
        return ChunkConfig(
            max_chunk_size=3072,
            min_chunk_size=256,
            code_ratio_threshold=0.6
        )
    
    @classmethod
    def for_large_documents(cls) -> ChunkConfig:
        """Configuration for very large documents."""
        return ChunkConfig(
            max_chunk_size=8192,
            min_chunk_size=1024,
            overlap_size=200,
            preserve_atomic_blocks=True
        )

# Usage
config = CustomProfiles.for_api_docs()
```

**Section sources**
- [markdown_chunker_v2/config.py](file://markdown_chunker_v2/config.py#L138-L170)

## Common Issues and Solutions

### Handling Empty Input

```python
from markdown_chunker import MarkdownChunker

def safe_chunking(markdown: str) -> List[Chunk]:
    """Safely handle empty or whitespace-only input."""
    
    if not markdown or not markdown.strip():
        return []
    
    chunker = MarkdownChunker()
    return chunker.chunk(markdown)

# Usage
empty_content = "   \n\t  \n   "
chunks = safe_chunking(empty_content)
print(f"Processed {len(chunks)} chunks")  # Output: Processed 0 chunks
```

### Choosing Appropriate Chunk Sizes

```python
def choose_optimal_chunk_size(llm_context_window: int, content_type: str) -> int:
    """Choose optimal chunk size based on LLM context window."""
    
    # Reserve 10% for overlap and metadata
    available_space = int(llm_context_window * 0.9)
    
    # Adjust based on content type
    if content_type == "code":
        # Code needs more context, use smaller chunks
        return int(available_space * 0.7)
    elif content_type == "table":
        # Tables need to stay intact, use larger chunks
        return int(available_space * 1.2)
    else:
        # General content
        return int(available_space * 0.8)

# Example usage
context_window = 4096
chunk_size = choose_optimal_chunk_size(context_window, "mixed")
config = ChunkConfig(max_chunk_size=chunk_size)
```

### Preserving Metadata for Downstream Processing

```python
def preserve_metadata_during_processing(chunks: List[Chunk]) -> List[Dict[str, Any]]:
    """Preserve essential metadata for downstream processing."""
    
    processed_chunks = []
    for chunk in chunks:
        processed_chunks.append({
            'original_content': chunk.content,
            'processed_content': chunk.content,  # Modify as needed
            'metadata': {
                'chunk_index': chunk.metadata.get('chunk_index'),
                'content_type': chunk.metadata.get('content_type'),
                'has_code': chunk.metadata.get('has_code'),
                'has_table': chunk.metadata.get('has_table'),
                'strategy': chunk.metadata.get('strategy'),
                'start_line': chunk.start_line,
                'end_line': chunk.end_line,
                'size': chunk.size,
                'header_path': chunk.metadata.get('header_path', []),
                'original_metadata': dict(chunk.metadata)  # Deep copy
            }
        })
    
    return processed_chunks
```

### Performance Optimization

```python
def optimize_for_performance(content: str, target_chunks: int = 10) -> ChunkConfig:
    """Optimize configuration for performance vs. chunk count balance."""
    
    estimated_chunk_size = max(512, len(content) // target_chunks)
    
    return ChunkConfig(
        max_chunk_size=estimated_chunk_size,
        min_chunk_size=max(256, estimated_chunk_size // 2),
        enable_overlap=False,  # Disable for speed
        overlap_size=0
    )

# Usage
large_document = "..." * 1000  # Very large content
config = optimize_for_performance(large_document, target_chunks=20)
```

## Performance Considerations

### Processing Speed

The library is optimized for performance with several strategies:

```python
import time
from markdown_chunker import MarkdownChunker

def benchmark_chunking_performance():
    """Benchmark chunking performance."""
    
    markdown_content = """
    # Performance Test
    
    This is a test document for performance evaluation.
    
    ```python
    def test_function():
        return "performance test"
    ```
    
    ## Sections
    - Item 1
    - Item 2
    - Item 3
    """
    
    chunker = MarkdownChunker()
    
    # Warm up
    chunker.chunk(markdown_content)
    
    # Benchmark
    start_time = time.time()
    chunks = chunker.chunk(markdown_content)
    end_time = time.time()
    
    print(f"Processed {len(chunks)} chunks in {end_time - start_time:.3f} seconds")
    print(f"Average chunk size: {sum(len(c.content) for c in chunks) / len(chunks):.1f} chars")
```

### Memory Usage

```python
def monitor_memory_usage():
    """Monitor memory usage during chunking."""
    
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Process large document
    large_doc = "# Document\n\n" + ("Content " * 10000)
    chunker = MarkdownChunker()
    chunks = chunker.chunk(large_doc)
    
    final_memory = process.memory_info().rss / 1024 / 1024  # MB
    print(f"Memory delta: {final_memory - initial_memory:.2f} MB")
```

### Batch Processing

```python
def batch_process_documents(documents: List[str], batch_size: int = 10) -> List[List[Chunk]]:
    """Process multiple documents efficiently."""
    
    chunker = MarkdownChunker()
    results = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_results = []
        
        for doc in batch:
            chunks = chunker.chunk(doc)
            batch_results.extend(chunks)
        
        results.append(batch_results)
    
    return results
```

## Best Practices

### Configuration Guidelines

1. **Start with Profiles**: Use predefined profiles as starting points
2. **Environment-Specific**: Create different configs for development and production
3. **Performance vs Features**: Balance features with performance needs
4. **Validation**: Always validate configurations before use
5. **Documentation**: Document custom configuration choices

### Content-Specific Recommendations

```python
def get_recommendations_for_content(content: str) -> Dict[str, Any]:
    """Get configuration recommendations based on content analysis."""
    
    from markdown_chunker import MarkdownChunker
    
    chunker = MarkdownChunker()
    _, _, analysis = chunker.chunk_with_analysis(content)
    
    recommendations = {}
    
    if analysis.code_ratio > 0.5:
        recommendations['config'] = ChunkConfig.for_code_heavy()
        recommendations['strategy'] = "Code-focused approach recommended"
    elif analysis.header_count > 10:
        recommendations['config'] = ChunkConfig.for_structured()
        recommendations['strategy'] = "Structured document detected"
    elif analysis.table_count > 5:
        recommendations['config'] = ChunkConfig.for_search_indexing()
        recommendations['strategy'] = "Table-heavy content detected"
    else:
        recommendations['config'] = ChunkConfig.default()
        recommendations['strategy'] = "General-purpose configuration"
    
    return recommendations
```

### Error Handling Best Practices

```python
def robust_chunking_pipeline(markdown_content: str) -> Dict[str, Any]:
    """Complete chunking pipeline with comprehensive error handling."""
    
    try:
        # Validate input
        if not markdown_content or not markdown_content.strip():
            return {
                'success': False,
                'error': 'Empty or whitespace-only content',
                'chunks': [],
                'metadata': {}
            }
        
        # Choose optimal configuration
        config = ChunkConfig.default()
        
        # Process with timeout protection
        chunker = MarkdownChunker(config)
        chunks, strategy, analysis = chunker.chunk_with_analysis(markdown_content)
        
        # Validate results
        if not chunks:
            return {
                'success': False,
                'error': 'No chunks generated',
                'chunks': [],
                'metadata': {}
            }
        
        # Prepare results
        return {
            'success': True,
            'chunks': [chunk.to_dict() for chunk in chunks],
            'metadata': {
                'strategy_used': strategy,
                'total_chunks': len(chunks),
                'content_type': analysis.content_type,
                'processing_time': 0.0,  # Would be calculated in real scenario
                'statistics': {
                    'total_chars': analysis.total_chars,
                    'total_lines': analysis.total_lines,
                    'avg_chunk_size': sum(c.size for c in chunks) / len(chunks)
                }
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'chunks': [],
            'metadata': {}
        }
```

### Integration Testing

```python
def test_chunking_consistency():
    """Test that chunking produces consistent results."""
    
    test_content = """
    # Test Document
    
    This is a test document for consistency checking.
    
    ```python
    def test_function():
        return "consistent"
    ```
    
    ## Sections
    - Item 1
    - Item 2
    """
    
    chunker = MarkdownChunker()
    
    # Run multiple times
    results = []
    for _ in range(5):
        chunks, strategy, _ = chunker.chunk_with_analysis(test_content)
        results.append((len(chunks), strategy))
    
    # Check consistency
    unique_results = set(results)
    assert len(unique_results) == 1, f"Inconsistent results: {unique_results}"
    
    print(f"Consistent chunking: {results[0][0]} chunks, strategy: {results[0][1]}")
```

**Section sources**
- [markdown_chunker_v2/chunker.py](file://markdown_chunker_v2/chunker.py#L206-L245)