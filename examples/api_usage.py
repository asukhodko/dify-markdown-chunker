"""
API usage examples for Python Markdown Chunker.

This script demonstrates how to use the API adapters for REST integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from markdown_chunker.api import APIAdapter, APIRequest, APIResponse
from markdown_chunker import MarkdownChunker
import json


def example_1_basic_api_request():
    """Example 1: Basic API request."""
    print("=" * 60)
    print("Example 1: Basic API Request")
    print("=" * 60)

    # Create adapter
    adapter=APIAdapter()

    # Create request
    request=APIRequest(
        content="# Hello World\n\nThis is a test document.",
        config=None,  # Use defaults
        strategy="auto"
    )

    # Process request
    response=adapter.process_request(request)

    if response.success:
        print(f"\n✅ Success!")
        print(f"Chunks: {len(response.chunks)}")
        print(f"Strategy: {response.metadata['strategy_used']}")

        for i, chunk in enumerate(response.chunks):
            print(f"\nChunk {i}:")
            print(f"  Content: {chunk['content'][:50]}...")
            print(f"  Size: {chunk['size']} chars")
    else:
        print(f"\n❌ Error: {response.error['message']}")


def example_2_custom_configuration():
    """Example 2: API request with custom configuration."""
    print("=" * 60)
    print("Example 2: Custom Configuration")
    print("=" * 60)

    adapter=APIAdapter()

    # Request with custom config
    request=APIRequest(
        content="""# API Documentation

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

    response=adapter.process_request(request)

    if response.success:
        print(f"\n✅ Request processed successfully")
        print(f"Chunks: {len(response.chunks)}")
        print(f"Strategy: {response.metadata['strategy_used']}")
        print(f"Processing time: {response.metadata['processing_time']:.3f}s")

        # Show statistics
        stats=response.metadata['statistics']
        print(f"\nStatistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Total size: {stats['total_size']} chars")
        print(f"  Avg chunk size: {stats['avg_chunk_size']:.1f} chars")


def example_3_json_serialization():
    """Example 3: JSON serialization."""
    print("=" * 60)
    print("Example 3: JSON Serialization")
    print("=" * 60)

    adapter=APIAdapter()

    request=APIRequest(
        content="# Test\n\nContent here.",
        config={"max_chunk_size": 1000}
    )

    response=adapter.process_request(request)

    if response.success:
        # Convert to JSON
        response_dict={
            "success": response.success,
            "chunks": response.chunks,
            "metadata": response.metadata
        }

        json_str=json.dumps(response_dict, indent=2)

        print("\nJSON Response:")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)

        # Parse back
        parsed=json.loads(json_str)
        print(f"\n✅ JSON round-trip successful")
        print(f"Parsed chunks: {len(parsed['chunks'])}")


def example_4_error_handling():
    """Example 4: Error handling."""
    print("=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)

    adapter=APIAdapter()

    # Test various error conditions
    test_cases=[
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
        response=adapter.process_request(test['request'])

        if not response.success:
            print(f"  ❌ Error (expected): {response.error['message']}")
            print(f"  Error code: {response.error.get('code', 'N/A')}")
        else:
            print(f"  ✅ Unexpectedly succeeded")


def example_5_simplified_api():
    """Example 5: Using simplified API."""
    print("=" * 60)
    print("Example 5: Simplified API")
    print("=" * 60)

    chunker=MarkdownChunker()

    # Use simplified API that returns dicts
    result=chunker.chunk_simple("""# Documentation

## Section 1

Content here.

## Section 2

More content.
""")

    print(f"\nSimplified API result:")
    print(f"  Strategy: {result['strategy_used']}")
    print(f"  Chunks: {result['statistics']['total_chunks']}")

    print(f"\nFirst chunk:")
    first_chunk=result['chunks'][0]
    print(f"  Content: {first_chunk['content'][:50]}...")
    print(f"  Lines: {first_chunk['start_line']}-{first_chunk['end_line']}")
    print(f"  Size: {first_chunk['size']} chars")

    # Easy to serialize
    json_str=json.dumps(result, indent=2)
    print(f"\n✅ JSON serialization: {len(json_str)} bytes")


def example_6_configuration_profiles():
    """Example 6: Using configuration profiles."""
    print("=" * 60)
    print("Example 6: Configuration Profiles")
    print("=" * 60)

    adapter=APIAdapter()

    markdown="""# API Reference

```python
class UserAPI:
    def get_user(self, id):
        return self.db.get(id)
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /users | List users |
| POST | /users | Create user |
"""

    # Test different profiles
    profiles={
        "API Docs": {
            "max_chunk_size": 3072,
            "min_chunk_size": 256,
            "code_ratio_threshold": 0.6
        },
        "Code Docs": {
            "max_chunk_size": 2048,
            "min_chunk_size": 128,
            "enable_overlap": False,
            "code_ratio_threshold": 0.8
        },
        "Chat Context": {
            "max_chunk_size": 1536,
            "min_chunk_size": 200,
            "overlap_size": 200
        }
    }

    for profile_name, config in profiles.items():
        request=APIRequest(
            content=markdown,
            config=config
        )

        response=adapter.process_request(request)

        if response.success:
            print(f"\n{profile_name} Profile:")
            print(f"  Chunks: {len(response.chunks)}")
            print(f"  Strategy: {response.metadata['strategy_used']}")
            print(f"  Avg size: {response.metadata['statistics']['avg_chunk_size']:.1f} chars")


def example_7_batch_processing():
    """Example 7: Batch processing multiple documents."""
    print("=" * 60)
    print("Example 7: Batch Processing")
    print("=" * 60)

    adapter=APIAdapter()

    documents=[
        "# Doc 1\n\nFirst document content.",
        "# Doc 2\n\nSecond document content.",
        "# Doc 3\n\nThird document content."
    ]

    results=[]

    for i, doc in enumerate(documents):
        request=APIRequest(content=doc)
        response=adapter.process_request(request)

        if response.success:
            results.append({
                "doc_id": i,
                "chunks": len(response.chunks),
                "strategy": response.metadata['strategy_used']
            })

    print(f"\nProcessed {len(results)} documents:")
    for result in results:
        print(f"  Doc {result['doc_id']}: {result['chunks']} chunks ({result['strategy']})")


def example_8_streaming_response():
    """Example 8: Simulating streaming response."""
    print("=" * 60)
    print("Example 8: Streaming Response Simulation")
    print("=" * 60)

    adapter=APIAdapter()

    request=APIRequest(
        content="""# Large Document

""" + ("## Section\n\nContent here.\n\n" * 10)
    )

    response=adapter.process_request(request)

    if response.success:
        print(f"\nStreaming {len(response.chunks)} chunks:")

        for i, chunk in enumerate(response.chunks):
            # Simulate streaming by yielding chunks
            print(f"\n[Chunk {i}]")
            print(f"Size: {chunk['size']} chars")
            print(f"Preview: {chunk['content'][:80]}...")

            # In real streaming, you'd yield here
            # yield json.dumps(chunk)


def main():
    """Run all examples."""
    examples=[
        example_1_basic_api_request,
        example_2_custom_configuration,
        example_3_json_serialization,
        example_4_error_handling,
        example_5_simplified_api,
        example_6_configuration_profiles,
        example_7_batch_processing,
        example_8_streaming_response,
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


if __name__ == "__main__":
    main()
