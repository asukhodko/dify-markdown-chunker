from markdown_chunker.api.adapter import APIAdapter
from markdown_chunker.api.types import APIRequest
from markdown_chunker.api.validator import APIValidator

"""Tests for API adapter."""


class TestAPIAdapter:
    """Test API adapter functionality."""

    def test_adapter_initialization(self):
        """Test adapter can be initialized."""
        adapter = APIAdapter()
        assert adapter is not None
        assert isinstance(adapter.validator, APIValidator)
        assert adapter.cache_chunker is True

    def test_adapter_with_custom_validator(self):
        """Test adapter with custom validator."""
        validator = APIValidator(max_content_size=1000)
        adapter = APIAdapter(validator=validator)
        assert adapter.validator is validator

    def test_successful_request_processing(self):
        """Test successful request processing."""
        adapter = APIAdapter()
        request = APIRequest(content="# Test Header\n\nThis is test content.")

        response = adapter.process_request(request)

        assert response.success is True
        assert len(response.chunks) > 0
        assert "strategy_used" in response.metadata
        assert "processing_time" in response.metadata
        assert len(response.errors) == 0

    def test_request_with_custom_config(self):
        """Test request with custom configuration."""
        adapter = APIAdapter()
        request = APIRequest(
            content="# Test\n\nContent here.",
            config={"max_chunk_size": 2048, "min_chunk_size": 100},
        )

        response = adapter.process_request(request)

        assert response.success is True
        assert len(response.chunks) > 0

    def test_request_with_strategy_override(self):
        """Test request with strategy override."""
        adapter = APIAdapter()
        request = APIRequest(content="# Test\n\nContent here.", strategy="sentences")

        response = adapter.process_request(request)

        assert response.success is True
        assert response.metadata["strategy_used"] == "sentences"

    def test_validation_rejects_invalid_content(self):
        """Test validation rejects invalid content."""
        adapter = APIAdapter()
        request = APIRequest(content="")  # Empty content

        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0
        # Check for validation error message
        assert any(
            keyword in response.errors[0].lower()
            for keyword in ["empty", "whitespace", "small", "content"]
        )

    def test_validation_rejects_invalid_strategy(self):
        """Test validation rejects invalid strategy."""
        adapter = APIAdapter()
        request = APIRequest(content="# Test\n\nContent", strategy="invalid_strategy")

        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0
        assert "strategy" in response.errors[0].lower()

    def test_validation_rejects_invalid_config(self):
        """Test validation rejects invalid config."""
        adapter = APIAdapter()
        request = APIRequest(
            content="# Test\n\nContent", config={"max_chunk_size": -100}  # Invalid size
        )

        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0

    def test_error_handling_for_processing_failure(self):
        """Test error handling for processing failures."""
        adapter = APIAdapter()
        # Create request that might cause processing issues
        request = APIRequest(
            content="# Test\n\nContent",
            config={
                "max_chunk_size": 1,
                "min_chunk_size": 1000,
            },  # Invalid relationship
        )

        response = adapter.process_request(request)

        assert response.success is False
        assert len(response.errors) > 0

    def test_chunker_caching_enabled(self):
        """Test chunker is cached between requests."""
        adapter = APIAdapter(cache_chunker=True)

        request1 = APIRequest(content="# Test 1\n\nContent")
        request2 = APIRequest(content="# Test 2\n\nDifferent content")

        response1 = adapter.process_request(request1)
        chunker1 = adapter._cached_chunker

        response2 = adapter.process_request(request2)
        chunker2 = adapter._cached_chunker

        # Same chunker should be reused
        assert chunker1 is chunker2
        assert response1.success is True
        assert response2.success is True

    def test_chunker_cache_invalidated_on_config_change(self):
        """Test chunker cache is invalidated when config changes."""
        adapter = APIAdapter(cache_chunker=True)

        request1 = APIRequest(
            content="# Test\n\nContent", config={"max_chunk_size": 2048}
        )
        request2 = APIRequest(
            content="# Test\n\nContent",
            config={"max_chunk_size": 4096},  # Different config
        )

        adapter.process_request(request1)
        chunker1 = adapter._cached_chunker

        adapter.process_request(request2)
        chunker2 = adapter._cached_chunker

        # Different chunker should be created
        assert chunker1 is not chunker2

    def test_chunker_caching_disabled(self):
        """Test chunker is not cached when caching disabled."""
        adapter = APIAdapter(cache_chunker=False)

        request1 = APIRequest(content="# Test 1\n\nContent")
        request2 = APIRequest(content="# Test 2\n\nContent")

        adapter.process_request(request1)
        adapter.process_request(request2)

        # No chunker should be cached
        assert adapter._cached_chunker is None

    def test_clear_cache(self):
        """Test cache can be cleared."""
        adapter = APIAdapter(cache_chunker=True)

        request = APIRequest(content="# Test\n\nContent")
        adapter.process_request(request)

        assert adapter._cached_chunker is not None

        adapter.clear_cache()

        assert adapter._cached_chunker is None
        assert adapter._cached_config_hash is None

    def test_process_dict_convenience_method(self):
        """Test process_dict convenience method."""
        adapter = APIAdapter()

        request_dict = {"content": "# Test\n\nContent here.", "strategy": "sentences"}

        response_dict = adapter.process_dict(request_dict)

        assert isinstance(response_dict, dict)
        assert response_dict["success"] is True
        assert "chunks" in response_dict
        assert "metadata" in response_dict

    def test_process_dict_handles_invalid_request(self):
        """Test process_dict handles invalid request dict."""
        adapter = APIAdapter()

        # Missing required 'content' field
        request_dict = {"strategy": "sentences"}

        response_dict = adapter.process_dict(request_dict)

        assert isinstance(response_dict, dict)
        assert response_dict["success"] is False
        assert len(response_dict["errors"]) > 0

    def test_response_includes_request_metadata(self):
        """Test response includes request metadata."""
        adapter = APIAdapter()
        request = APIRequest(
            content="# Test\n\nContent",
            metadata={"request_id": "12345", "user": "test_user"},
        )

        response = adapter.process_request(request)

        assert response.success is True
        assert "request_metadata" in response.metadata
        assert response.metadata["request_metadata"]["request_id"] == "12345"

    def test_response_includes_warnings(self):
        """Test response includes warnings from chunking."""
        adapter = APIAdapter()
        # Create content that might generate warnings
        request = APIRequest(
            content="# Test\n\n" + "x" * 10000,  # Very long content
            config={"max_chunk_size": 100},
        )

        response = adapter.process_request(request)

        assert response.success is True
        # Warnings may or may not be present depending on content
        assert isinstance(response.warnings, list)


class TestAPIAdapterIntegration:
    """Integration tests for API adapter."""

    def test_complete_workflow(self):
        """Test complete request-response workflow."""
        adapter = APIAdapter()

        # Create request
        request = APIRequest(
            content="# Introduction\n\nThis is a test document.\n\n## Section 1\n\nContent here.",
            config={"max_chunk_size": 4096},
            strategy="structural",
            metadata={"source": "test"},
        )

        # Process request
        response = adapter.process_request(request)

        # Verify response
        assert response.success is True
        assert len(response.chunks) > 0

        # Verify chunks have expected structure
        for chunk in response.chunks:
            assert "content" in chunk
            assert "start_line" in chunk
            assert "end_line" in chunk
            assert "metadata" in chunk

        # Verify metadata
        assert response.metadata["strategy_used"] == "structural"
        assert "processing_time" in response.metadata
        assert "request_metadata" in response.metadata

    def test_multiple_requests_with_caching(self):
        """Test multiple requests benefit from caching."""
        adapter = APIAdapter(cache_chunker=True)

        requests = [APIRequest(content=f"# Test {i}\n\nContent {i}") for i in range(5)]

        responses = [adapter.process_request(req) for req in requests]

        # All should succeed
        assert all(r.success for r in responses)

        # Chunker should be cached
        assert adapter._cached_chunker is not None
