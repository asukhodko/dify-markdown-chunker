"""
RAG (Retrieval-Augmented Generation) integration example.

This example shows how to use the chunker for RAG pipelines,
including vector database preparation and embedding generation.
"""

from typing import List, Dict, Any
from markdown_chunker.chunker import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


def prepare_chunks_for_embeddings(markdown: str, max_chunk_size: int=500) -> List[Dict[str, Any]]:
    """
    Prepare markdown chunks for embedding generation.

    Args:
        markdown: Markdown content to process
        max_chunk_size: Maximum chunk size (smaller for embeddings)

    Returns:
        List of dictionaries ready for embedding
    """
    # Configure for embeddings (smaller chunks with overlap)
    config=ChunkConfig(
        max_chunk_size=max_chunk_size,
        min_chunk_size=100,
        enable_overlap=True,
        overlap_size=50  # 10% overlap for context
    )

    chunker=MarkdownChunker(config)
    result=chunker.chunk_with_analysis(markdown)

    embeddings_data=[]
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


def prepare_for_vector_database(documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Prepare multiple documents for vector database storage.

    Args:
        documents: List of documents with 'id' and 'content' keys

    Returns:
        List of chunks ready for vector database
    """
    chunker=MarkdownChunker(ChunkConfig(
        max_chunk_size=500,
        enable_overlap=True,
        overlap_size=50
    ))

    all_chunks=[]

    for doc in documents:
        doc_id=doc['id']
        content=doc['content']

        result=chunker.chunk_with_analysis(content)

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


def create_context_window(chunks: List[Dict[str, Any]], target_chunk_id: str,
                         window_size: int=2) -> str:
    """
    Create context window around a target chunk for RAG.

    Args:
        chunks: List of all chunks
        target_chunk_id: ID of the target chunk
        window_size: Number of chunks before/after to include

    Returns:
        Combined context string
    """
    # Find target chunk index
    target_idx=None
    for i, chunk in enumerate(chunks):
        if chunk['id'] == target_chunk_id:
            target_idx=i
            break

    if target_idx is None:
        return ""

    # Get window
    start_idx=max(0, target_idx - window_size)
    end_idx=min(len(chunks), target_idx + window_size + 1)

    window_chunks=chunks[start_idx:end_idx]

    # Combine with markers
    context_parts=[]
    for chunk in window_chunks:
        marker=">>> TARGET <<<" if chunk['id'] == target_chunk_id else ""
        context_parts.append(f"{marker}\n{chunk['text']}\n")

    return "\n".join(context_parts)


def filter_chunks_by_type(chunks: List[Dict[str, Any]],
                         content_type: str) -> List[Dict[str, Any]]:
    """
    Filter chunks by content type.

    Args:
        chunks: List of chunks
        content_type: Type to filter ('code', 'text', 'mixed', etc.)

    Returns:
        Filtered chunks
    """
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


def example_1_basic_rag_preparation():
    """Example 1: Basic RAG preparation."""
    print("=" * 60)
    print("Example 1: Basic RAG Preparation")
    print("=" * 60)

    markdown="""# Python Tutorial

## Introduction

Python is a high-level programming language.

```python
def hello_world():
    print("Hello, World!")
```

## Features

- Easy to learn
- Powerful libraries
- Large community

## Data Types

| Type | Example | Mutable |
|------|---------|---------|
| int | 42 | No |
| str | "hello" | No |
| list | [1,2,3] | Yes |
"""

    embeddings_data=prepare_chunks_for_embeddings(markdown)

    print(f"\nPrepared {len(embeddings_data)} chunks for embeddings:")
    for item in embeddings_data:
        print(f"\nChunk ID: {item['id']}")
        print(f"  Text length: {len(item['text'])} chars")
        print(f"  Has code: {item['metadata']['has_code']}")
        print(f"  Has table: {item['metadata']['has_table']}")
        print(f"  Content type: {item['metadata']['content_type']}")


def example_2_multi_document_processing():
    """Example 2: Process multiple documents."""
    print("=" * 60)
    print("Example 2: Multi-Document Processing")
    print("=" * 60)

    documents=[
        {
            'id': 'doc1',
            'content': """# Document 1

This is the first document with some content.

```python
def func1():
    pass
```
"""
        },
        {
            'id': 'doc2',
            'content': """# Document 2

This is the second document.

- Item 1
- Item 2
- Item 3
"""
        },
        {
            'id': 'doc3',
            'content': """# Document 3

| Col1 | Col2 |
|------|------|
| A | B |
| C | D |
"""
        }
    ]

    all_chunks=prepare_for_vector_database(documents)

    print(f"\nProcessed {len(documents)} documents into {len(all_chunks)} chunks:")

    for doc_id in ['doc1', 'doc2', 'doc3']:
        doc_chunks=[c for c in all_chunks if c['doc_id'] == doc_id]
        print(f"\n{doc_id}: {len(doc_chunks)} chunks")
        for chunk in doc_chunks:
            print(f"  - {chunk['id']}: {chunk['size']} chars")


def example_3_context_window():
    """Example 3: Create context windows."""
    print("=" * 60)
    print("Example 3: Context Windows")
    print("=" * 60)

    markdown="""# Tutorial

## Part 1
Content for part 1.

## Part 2
Content for part 2.

## Part 3
Content for part 3.

## Part 4
Content for part 4.

## Part 5
Content for part 5.
"""

    embeddings_data=prepare_chunks_for_embeddings(markdown, max_chunk_size=100)

    # Create context window around chunk 2
    if len(embeddings_data) >= 3:
        target_id=embeddings_data[2]['id']
        context=create_context_window(embeddings_data, target_id, window_size=1)

        print(f"\nContext window around {target_id}:")
        print(context)


def example_4_filtering_chunks():
    """Example 4: Filter chunks by type."""
    print("=" * 60)
    print("Example 4: Filtering Chunks")
    print("=" * 60)

    markdown="""# Mixed Content

Some text here.

```python
def code_example():
    return True
```

More text.

| Table | Data |
|-------|------|
| A | 1 |
| B | 2 |

Final text.
"""

    embeddings_data=prepare_chunks_for_embeddings(markdown)

    # Filter by type
    code_chunks=get_code_chunks(embeddings_data)
    table_chunks=get_table_chunks(embeddings_data)

    print(f"\nTotal chunks: {len(embeddings_data)}")
    print(f"Code chunks: {len(code_chunks)}")
    print(f"Table chunks: {len(table_chunks)}")

    if code_chunks:
        print("\nCode chunks:")
        for chunk in code_chunks:
            lang=chunk['metadata'].get('language', 'unknown')
            print(f"  - {chunk['id']}: {lang}")

    if table_chunks:
        print("\nTable chunks:")
        for chunk in table_chunks:
            cols=chunk['metadata'].get('column_count', 0)
            rows=chunk['metadata'].get('row_count', 0)
            print(f"  - {chunk['id']}: {cols}x{rows} table")


def example_5_semantic_search_preparation():
    """Example 5: Prepare for semantic search."""
    print("=" * 60)
    print("Example 5: Semantic Search Preparation")
    print("=" * 60)

    markdown="""# API Documentation

## Authentication

Use API keys for authentication.

```python
import requests

headers={'Authorization': 'Bearer YOUR_API_KEY'}
response=requests.get('https://api.example.com/data', headers=headers)
```

## Endpoints

### GET /users

Retrieve user list.

### POST /users

Create new user.

```python
data={'name': 'John', 'email': 'john@example.com'}
response=requests.post('https://api.example.com/users', json=data)
```
"""

    # Prepare with rich metadata for search
    embeddings_data=prepare_chunks_for_embeddings(markdown, max_chunk_size=300)

    print(f"\nPrepared {len(embeddings_data)} chunks for semantic search:")

    for item in embeddings_data:
        metadata=item['metadata']

        # Create search tags
        tags=[]
        if metadata['has_code']:
            tags.append('code')
        if metadata['has_table']:
            tags.append('table')
        if metadata['has_list']:
            tags.append('list')

        print(f"\n{item['id']}:")
        print(f"  Preview: {item['text'][:60]}...")
        print(f"  Tags: {', '.join(tags) if tags else 'text'}")
        print(f"  Strategy: {metadata['strategy']}")


def main():
    """Run all examples."""
    examples=[
        example_1_basic_rag_preparation,
        example_2_multi_document_processing,
        example_3_context_window,
        example_4_filtering_chunks,
        example_5_semantic_search_preparation,
    ]

    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print()


if __name__ == "__main__":
    main()
