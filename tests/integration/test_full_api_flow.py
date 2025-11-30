"""Integration tests for full API flow."""

import json

import pytest

from markdown_chunker import ChunkConfig, MarkdownChunker, chunk_text
from markdown_chunker.api import APIAdapter, APIRequest
from markdown_chunker.chunker.types import ChunkingResult


class TestFullAPIFlow:
    """Test complete API flow from request to response."""

    def test_end_to_end_basic_flow(self):
        """Test basic end-to-end flow."""
        # Create adapter
        adapter = APIAdapter()

        # Create request
        request = APIRequest(content="# Hello\n\nWorld", config=None, strategy="auto")

        # Process
        response = adapter.process_request(request)

        # Verify
        assert response.success is True
        assert len(response.chunks) > 0
        assert "strategy_used" in response.metadata
        assert "processing_time" in response.metadata

    def test_end_to_end_with_config(self):
        """Test end-to-end with custom configuration."""
        adapter = APIAdapter()

        request = APIRequest(
            content="# Test\n\nContent here.",
            config={"max_chunk_size": 1000, "enable_overlap": True},
        )

        response = adapter.process_request(request)

        assert response.success is True
        assert len(response.chunks) > 0

    def test_end_to_end_json_round_trip(self):
        """Test JSON serialization round-trip."""
        chunker = MarkdownChunker()

        # Chunk
        result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Serialize
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)

        # Deserialize
        parsed = json.loads(json_str)
        restored = ChunkingResult.from_dict(parsed)

        # Verify
        assert len(restored.chunks) == len(result.chunks)
        assert restored.strategy_used == result.strategy_used
        assert restored.chunks[0].content == result.chunks[0].content

    def test_end_to_end_all_strategies(self):
        """Test all strategies through API."""
        adapter = APIAdapter()

        test_cases = [
            ("auto", "# Test\n\nContent"),
            ("structural", "# H1\n\n## H2\n\nContent"),
            ("code", "```python\ncode\n```"),
            ("mixed", "# Test\n\n```python\ncode\n```\n\nText"),
            ("list", "- Item 1\n- Item 2\n- Item 3"),
            ("sentences", "Sentence one. Sentence two. Sentence three."),
        ]

        for strategy, content in test_cases:
            request = APIRequest(content=content, strategy=strategy)

            response = adapter.process_request(request)
            assert response.success is True, f"Strategy {strategy} failed"
            assert len(response.chunks) > 0


class TestAPIIntegration:
    """Test API adapter integration."""

    def test_api_adapter_caching(self):
        """Test that adapter caches chunker instances."""
        adapter = APIAdapter()

        # Process multiple requests
        for _ in range(3):
            request = APIRequest(content="# Test")
            response = adapter.process_request(request)
            assert response.success is True

        # Chunker should be reused (cached)
        assert adapter._cached_chunker is not None

    def test_api_adapter_config_changes(self):
        """Test adapter handles config changes."""
        adapter = APIAdapter()

        # First request with config A
        request1 = APIRequest(content="# Test", config={"max_chunk_size": 1000})
        response1 = adapter.process_request(request1)

        # Second request with config B
        request2 = APIRequest(content="# Test", config={"max_chunk_size": 2000})
        response2 = adapter.process_request(request2)

        # Both should succeed
        assert response1.success is True
        assert response2.success is True

    def test_api_validation_integration(self):
        """Test validation integration in API flow."""
        adapter = APIAdapter()

        # Invalid content
        request = APIRequest(content="")
        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0
        assert any("empty" in err.lower() for err in response.errors)

    def test_api_error_handling_integration(self):
        """Test error handling throughout API."""
        adapter = APIAdapter()

        # Invalid strategy
        request = APIRequest(content="# Test", strategy="invalid_strategy")
        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0
        assert any("strategy" in err.lower() for err in response.errors)


class TestSerializationIntegration:
    """Test serialization integration across all types."""

    def test_chunk_serialization_integration(self):
        """Test Chunk serialization in full flow."""
        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Serialize chunk
        chunk = result.chunks[0]
        chunk_dict = chunk.to_dict()

        # Verify all fields
        assert "content" in chunk_dict
        assert "start_line" in chunk_dict
        assert "end_line" in chunk_dict
        assert "size" in chunk_dict
        assert "content_type" in chunk_dict
        assert "metadata" in chunk_dict

    def test_config_serialization_integration(self):
        """Test ChunkConfig serialization in full flow."""
        config = ChunkConfig(max_chunk_size=2000)

        # Serialize
        config_dict = config.to_dict()

        # Use in API
        adapter = APIAdapter()
        request = APIRequest(content="# Test", config=config_dict)
        response = adapter.process_request(request)

        assert response.success is True

    def test_result_serialization_integration(self):
        """Test ChunkingResult serialization in full flow."""
        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis("# Test\n\nContent")

        # Serialize
        result_dict = result.to_dict()

        # Verify structure
        assert "chunks" in result_dict
        assert "strategy_used" in result_dict
        assert "processing_time" in result_dict
        assert "statistics" in result_dict

        # Verify chunks are dicts
        assert isinstance(result_dict["chunks"], list)
        assert isinstance(result_dict["chunks"][0], dict)


class TestConfigurationProfiles:
    """Test configuration profiles integration."""

    def test_all_profiles_work(self):
        """Test all configuration profiles."""
        profiles = [
            ChunkConfig.for_api_docs(),
            ChunkConfig.for_code_docs(),
            ChunkConfig.for_chat_context(),
            ChunkConfig.for_search_indexing(),
            ChunkConfig.for_large_documents(),
        ]

        markdown = "# Test\n\n```python\ncode\n```\n\nText"

        for config in profiles:
            chunker = MarkdownChunker(config)
            result = chunker.chunk_with_analysis(markdown)

            assert len(result.chunks) > 0
            assert result.strategy_used is not None

    def test_profiles_through_api(self):
        """Test profiles through API adapter."""
        adapter = APIAdapter()

        # Use API docs profile
        config = ChunkConfig.for_api_docs()
        request = APIRequest(
            content="# API\n\n```python\ncode\n```", config=config.to_dict()
        )

        response = adapter.process_request(request)
        assert response.success is True


class TestConvenienceFunctions:
    """Test convenience functions integration."""

    def test_chunk_text_integration(self):
        """Test chunk_text convenience function."""
        chunks = chunk_text("# Test\n\nContent")

        assert len(chunks) > 0
        assert chunks[0].content is not None

    def test_chunk_text_with_config(self):
        """Test chunk_text with custom config."""
        config = ChunkConfig(max_chunk_size=1000)
        chunks = chunk_text("# Test\n\nContent", config)

        assert len(chunks) > 0

    def test_simplified_api_integration(self):
        """Test simplified API integration."""
        chunker = MarkdownChunker()
        result = chunker.chunk_simple("# Test\n\nContent")

        # Verify dict structure
        assert isinstance(result, dict)
        assert "chunks" in result
        assert "metadata" in result
        assert "strategy_used" in result["metadata"]
        assert "statistics" in result["metadata"]

        # Verify chunks are dicts
        assert isinstance(result["chunks"], list)
        assert isinstance(result["chunks"][0], dict)


class TestErrorHandlingIntegration:
    """Test error handling integration."""

    def test_validation_error_flow(self):
        """Test validation error through full flow."""
        adapter = APIAdapter()

        request = APIRequest(content="")
        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0

    def test_processing_error_recovery(self):
        """Test processing error recovery."""
        adapter = APIAdapter()

        # Valid request should work
        request = APIRequest(content="# Test")
        response = adapter.process_request(request)

        assert response.success is True

        # Invalid request should fail gracefully
        request = APIRequest(content="")
        response = adapter.process_request(request)

        assert response.success is False

        # Next valid request should work
        request = APIRequest(content="# Test 2")
        response = adapter.process_request(request)

        assert response.success is True


class TestPerformanceIntegration:
    """Test performance-related integration."""

    def test_large_document_processing(self):
        """Test processing large document."""
        # Generate large document
        markdown = "# Large Doc\n\n" + ("## Section\n\nContent.\n\n" * 100)

        chunker = MarkdownChunker()
        result = chunker.chunk_with_analysis(markdown)

        assert len(result.chunks) > 0
        assert result.processing_time > 0

    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        adapter = APIAdapter()

        documents = ["# Doc {}\n\nContent".format(i) for i in range(10)]

        for doc in documents:
            request = APIRequest(content=doc)
            response = adapter.process_request(request)
            assert response.success is True

    def test_config_profile_performance(self):
        """Test different config profiles performance."""
        markdown = "# Test\n\n" + ("Content here.\n\n" * 50)

        configs = [
            ChunkConfig.for_chat_context(),
            ChunkConfig.for_large_documents(),
        ]

        for config in configs:
            chunker = MarkdownChunker(config)
            result = chunker.chunk_with_analysis(markdown)

            assert len(result.chunks) > 0
            assert result.processing_time < 1.0  # Should be fast


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_api_documentation_scenario(self):
        """Test API documentation chunking scenario."""
        markdown = """# API Reference

## Authentication

Use Bearer tokens.

```python
headers={"Authorization": "Bearer TOKEN"}
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /users | List users |
| POST | /users | Create user |

## Rate Limits

- 1000 requests/hour
- 10 requests/second
"""

        config = ChunkConfig.for_api_docs()
        chunker = MarkdownChunker(config)
        result = chunker.chunk_with_analysis(markdown)

        assert len(result.chunks) > 0
        assert result.strategy_used in ["code", "mixed", "structural"]

    def test_code_tutorial_scenario(self):
        """Test code tutorial chunking scenario."""
        markdown = """# Python Tutorial

## Variables

```python
x=10
y=20
```

## Functions

```python
def add(a, b):
    return a + b
```

## Classes

```python
class Calculator:
    def add(self, a, b):
        return a + b
```
"""

        config = ChunkConfig.for_code_docs()
        chunker = MarkdownChunker(config)
        result = chunker.chunk_with_analysis(markdown)

        assert len(result.chunks) > 0
        # Strategy should be code or structural (both valid for code docs)
        assert result.strategy_used in ["code", "structural", "mixed"]

    def test_rag_preparation_scenario(self):
        """Test RAG system preparation scenario."""
        markdown = """# Product Guide

## Features

Our product offers:
- Task management
- Team collaboration
- Analytics

## Getting Started

1. Sign up
2. Create workspace
3. Invite team
"""

        # Use chat context for RAG
        config = ChunkConfig.for_chat_context()
        chunker = MarkdownChunker(config)
        result = chunker.chunk_simple(markdown)

        # Verify RAG-ready format
        assert isinstance(result, dict)
        assert "chunks" in result
        assert result["success"] is True

        # Check chunk sizes are appropriate for embeddings
        for chunk in result["chunks"]:
            assert chunk["size"] <= 1536  # Typical embedding limit

    def test_search_indexing_scenario(self):
        """Test search indexing scenario."""
        markdown = """# Troubleshooting

## Connection Issues

Check your network.

## Authentication Errors

Verify your credentials.

## Performance Problems

Optimize your queries.
"""

        config = ChunkConfig.for_search_indexing()
        chunker = MarkdownChunker(config)
        result = chunker.chunk_with_analysis(markdown)

        # Verify chunks are small for search
        for chunk in result.chunks:
            assert chunk.size <= 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
