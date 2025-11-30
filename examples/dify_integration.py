"""
Dify integration example for Python Markdown Chunker.

This script demonstrates how to integrate the chunker with Dify RAG system.
This is a preparation example for Stage 3 implementation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_chunker import MarkdownChunker, ChunkConfig
from markdown_chunker.api import APIAdapter, APIRequest
import json


def example_1_dify_compatible_output():
    """Example 1: Generate Dify-compatible output format."""
    print("=" * 60)
    print("Example 1: Dify-Compatible Output")
    print("=" * 60)

    chunker=MarkdownChunker()

    markdown="""# Product Documentation

## Overview

Our product helps you manage your workflow efficiently.

## Features

- Task management
- Team collaboration
- Real-time updates

## Getting Started

```python
from product import Client

client=Client(api_key="your-key")
client.create_task("My first task")
```
"""

    # Use simplified API for dict output
    result=chunker.chunk_simple(markdown)

    # Transform to Dify format
    dify_chunks=[]
    for chunk in result['chunks']:
        dify_chunk={
            "content": chunk['content'],
            "metadata": {
                "source": "documentation",
                "chunk_id": f"chunk_{chunk['start_line']}_{chunk['end_line']}",
                "lines": f"{chunk['start_line']}-{chunk['end_line']}",
                "size": chunk['size'],
                "type": chunk['content_type']
            }
        }
        dify_chunks.append(dify_chunk)

    print(f"\nGenerated {len(dify_chunks)} Dify-compatible chunks")
    print(f"\nFirst chunk:")
    print(json.dumps(dify_chunks[0], indent=2))


def example_2_rag_optimized_chunking():
    """Example 2: RAG-optimized chunking configuration."""
    print("=" * 60)
    print("Example 2: RAG-Optimized Chunking")
    print("=" * 60)

    # Configuration optimized for RAG systems
    config=ChunkConfig(
        max_chunk_size=1536,  # Optimal for embedding models
        min_chunk_size=200,
        overlap_size=200,     # Overlap for context preservation
        enable_overlap=True
    )

    chunker=MarkdownChunker(config)

    markdown="""# API Authentication

## Overview

Authentication is required for all API requests.

## API Keys

Generate an API key from your dashboard:

1. Go to Settings
2. Click "API Keys"
3. Generate new key

## Usage

```python
import requests

headers={
    "Authorization": f"Bearer {api_key}"
}

response=requests.get(
    "https://api.example.com/users",
    headers=headers
)
```

## Security

- Never commit API keys to version control
- Rotate keys regularly
- Use environment variables
"""

    result=chunker.chunk_with_analysis(markdown)

    print(f"\nRAG-optimized chunking:")
    print(f"  Strategy: {result.strategy_used}")
    print(f"  Chunks: {len(result.chunks)}")
    print(f"  Avg size: {result.statistics['avg_chunk_size']:.1f} chars")

    # Show overlap information
    overlap_count=sum(1 for c in result.chunks if c.metadata.get('has_overlap'))
    print(f"  Chunks with overlap: {overlap_count}")


def example_3_semantic_search_preparation():
    """Example 3: Prepare chunks for semantic search."""
    print("=" * 60)
    print("Example 3: Semantic Search Preparation")
    print("=" * 60)

    # Use search indexing profile
    config=ChunkConfig.for_search_indexing()
    chunker=MarkdownChunker(config)

    markdown="""# Troubleshooting Guide

## Connection Issues

If you can't connect to the service:

1. Check your internet connection
2. Verify API endpoint URL
3. Confirm API key is valid

## Authentication Errors

Common authentication errors:

- 401 Unauthorized: Invalid API key
- 403 Forbidden: Insufficient permissions
- 429 Too Many Requests: Rate limit exceeded

## Performance Issues

If experiencing slow performance:

- Use pagination for large datasets
- Enable caching
- Optimize query parameters
"""

    result=chunker.chunk_with_analysis(markdown)

    # Prepare for semantic search
    search_documents=[]
    for i, chunk in enumerate(result.chunks):
        doc={
            "id": f"doc_{i}",
            "text": chunk.content,
            "metadata": {
                "chunk_index": i,
                "lines": f"{chunk.start_line}-{chunk.end_line}",
                "type": chunk.content_type,
                "size": chunk.size
            }
        }
        search_documents.append(doc)

    print(f"\nPrepared {len(search_documents)} documents for semantic search")
    print(f"Avg document size: {sum(d['metadata']['size'] for d in search_documents) / len(search_documents):.1f} chars")


def example_4_api_endpoint_simulation():
    """Example 4: Simulate Dify API endpoint."""
    print("=" * 60)
    print("Example 4: Dify API Endpoint Simulation")
    print("=" * 60)

    adapter=APIAdapter()

    # Simulate incoming request from Dify
    dify_request={
        "document": {
            "content": """# User Guide

## Installation

Install using pip:

```bash
pip install our-package
```

## Quick Start

```python
from our_package import Client

client=Client()
result=client.process("data")
```
""",
            "metadata": {
                "source": "user_guide.md",
                "version": "1.0"
            }
        },
        "chunking_config": {
            "max_chunk_size": 1536,
            "strategy": "auto"
        }
    }

    # Process request
    request=APIRequest(
        content=dify_request['document']['content'],
        config=dify_request['chunking_config'],
        metadata=dify_request['document']['metadata']
    )

    response=adapter.process_request(request)

    if response.success:
        # Format response for Dify
        dify_response={
            "status": "success",
            "chunks": response.chunks,
            "metadata": {
                "strategy": response.metadata['strategy_used'],
                "total_chunks": response.metadata['statistics']['total_chunks'],
                "processing_time": response.metadata['processing_time'],
                "source_metadata": dify_request['document']['metadata']
            }
        }

        print(f"\n✅ Processed successfully")
        print(f"Chunks: {dify_response['metadata']['total_chunks']}")
        print(f"Strategy: {dify_response['metadata']['strategy']}")
        print(f"Time: {dify_response['metadata']['processing_time']:.3f}s")

        print(f"\nResponse preview:")
        print(json.dumps(dify_response, indent=2)[:500] + "...")


def example_5_batch_document_processing():
    """Example 5: Batch process multiple documents for Dify."""
    print("=" * 60)
    print("Example 5: Batch Document Processing")
    print("=" * 60)

    adapter=APIAdapter()

    # Simulate multiple documents from Dify knowledge base
    documents=[
        {
            "id": "doc_1",
            "title": "Getting Started",
            "content": "# Getting Started\n\nWelcome to our platform..."
        },
        {
            "id": "doc_2",
            "title": "API Reference",
            "content": "# API Reference\n\n## Endpoints\n\n- GET /users\n- POST /users"
        },
        {
            "id": "doc_3",
            "title": "Troubleshooting",
            "content": "# Troubleshooting\n\n## Common Issues\n\n1. Connection errors\n2. Auth failures"
        }
    ]

    results=[]

    for doc in documents:
        request=APIRequest(
            content=doc['content'],
            metadata={"doc_id": doc['id'], "title": doc['title']}
        )

        response=adapter.process_request(request)

        if response.success:
            results.append({
                "doc_id": doc['id'],
                "title": doc['title'],
                "chunks": len(response.chunks),
                "strategy": response.metadata['strategy_used']
            })

    print(f"\nBatch processing results:")
    for result in results:
        print(f"  {result['title']}: {result['chunks']} chunks ({result['strategy']})")


def example_6_embedding_preparation():
    """Example 6: Prepare chunks for embedding generation."""
    print("=" * 60)
    print("Example 6: Embedding Preparation")
    print("=" * 60)

    # Use chat context profile (good for embeddings)
    config=ChunkConfig.for_chat_context()
    chunker=MarkdownChunker(config)

    markdown="""# Product Features

## Core Features

### Task Management
Create, assign, and track tasks efficiently.

### Team Collaboration
Work together with real-time updates.

### Analytics
Get insights into your team's productivity.

## Advanced Features

### Automation
Automate repetitive tasks with workflows.

### Integrations
Connect with your favorite tools.
"""

    result=chunker.chunk_with_analysis(markdown)

    # Prepare for embedding
    embedding_inputs=[]
    for chunk in result.chunks:
        # Format for embedding model
        embedding_input={
            "text": chunk.content,
            "metadata": {
                "lines": f"{chunk.start_line}-{chunk.end_line}",
                "type": chunk.content_type
            }
        }
        embedding_inputs.append(embedding_input)

    print(f"\nPrepared {len(embedding_inputs)} texts for embedding")
    print(f"Avg text length: {sum(len(e['text']) for e in embedding_inputs) / len(embedding_inputs):.1f} chars")

    print(f"\nFirst embedding input:")
    print(json.dumps(embedding_inputs[0], indent=2))


def example_7_context_window_optimization():
    """Example 7: Optimize chunks for LLM context windows."""
    print("=" * 60)
    print("Example 7: Context Window Optimization")
    print("=" * 60)

    # Different configs for different LLM context windows
    configs={
        "GPT-3.5 (4K)": ChunkConfig(max_chunk_size=1536),
        "GPT-4 (8K)": ChunkConfig(max_chunk_size=3072),
        "GPT-4 (32K)": ChunkConfig(max_chunk_size=6144),
    }

    markdown="""# Documentation

""" + ("## Section\n\nContent here with details.\n\n" * 20)

    print(f"\nChunking for different context windows:")

    for model, config in configs.items():
        chunker=MarkdownChunker(config)
        result=chunker.chunk_with_analysis(markdown)

        print(f"\n{model}:")
        print(f"  Max chunk size: {config.max_chunk_size}")
        print(f"  Chunks generated: {len(result.chunks)}")
        print(f"  Avg chunk size: {result.statistics['avg_chunk_size']:.1f} chars")


def example_8_metadata_enrichment():
    """Example 8: Enrich chunks with metadata for Dify."""
    print("=" * 60)
    print("Example 8: Metadata Enrichment")
    print("=" * 60)

    chunker=MarkdownChunker()

    markdown="""# API Documentation

## Authentication

Use Bearer tokens for authentication.

```python
headers={"Authorization": "Bearer TOKEN"}
```

## Rate Limits

- 1000 requests per hour
- 10 requests per second
"""

    result=chunker.chunk_with_analysis(markdown)

    # Enrich with additional metadata
    enriched_chunks=[]
    for i, chunk in enumerate(result.chunks):
        enriched={
            "content": chunk.content,
            "metadata": {
                # Original metadata
                **chunk.metadata,
                # Additional Dify metadata
                "chunk_id": f"chunk_{i}",
                "document_id": "api_docs_v1",
                "section": "authentication" if i == 0 else "rate_limits",
                "language": "en",
                "version": "1.0",
                "indexed_at": "2025-11-09T00:00:00Z",
                # Chunking metadata
                "chunking_strategy": result.strategy_used,
                "chunk_index": i,
                "total_chunks": len(result.chunks)
            }
        }
        enriched_chunks.append(enriched)

    print(f"\nEnriched {len(enriched_chunks)} chunks with metadata")
    print(f"\nExample enriched chunk:")
    print(json.dumps(enriched_chunks[0], indent=2))


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Dify Integration Examples")
    print("Preparation for Stage 3 Implementation")
    print("=" * 60 + "\n")

    examples=[
        example_1_dify_compatible_output,
        example_2_rag_optimized_chunking,
        example_3_semantic_search_preparation,
        example_4_api_endpoint_simulation,
        example_5_batch_document_processing,
        example_6_embedding_preparation,
        example_7_context_window_optimization,
        example_8_metadata_enrichment,
    ]

    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
            print()

    print("=" * 60)
    print("Note: These are preparation examples.")
    print("Full Dify plugin implementation will be in Stage 3.")
    print("=" * 60)


if __name__ == "__main__":
    main()
