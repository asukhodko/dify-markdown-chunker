"""Tests for API error handler."""

from markdown_chunker.api.error_handler import (
    APIErrorHandler,
    create_error_handler,
    handle_api_error,
)
from markdown_chunker.api.types import APIResponse
from markdown_chunker.chunker.core import ChunkingError, ConfigurationError
from markdown_chunker.chunker.selector import StrategySelectionError


class TestAPIErrorHandler:
    """Test API error handler."""

    def test_handler_initialization(self):
        """Test handler can be initialized."""
        handler = APIErrorHandler()
        assert handler is not None
        assert handler.include_traceback is False

    def test_handler_with_traceback(self):
        """Test handler with traceback enabled."""
        handler = APIErrorHandler(include_traceback=True)
        assert handler.include_traceback is True

    def test_handle_strategy_selection_error(self):
        """Test handling strategy selection errors."""
        handler = APIErrorHandler()
        error = StrategySelectionError("Invalid strategy 'foo'")

        response = handler.handle_exception(error)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert len(response.errors) > 0
        assert "Invalid strategy" in response.errors[0]
        assert response.metadata["error_type"] == "StrategySelectionError"
        assert response.metadata["error_code"] == "INVALID_STRATEGY"

    def test_handle_configuration_error(self):
        """Test handling configuration errors."""
        handler = APIErrorHandler()
        error = ConfigurationError("Invalid config parameter")

        response = handler.handle_exception(error)

        assert response.success is False
        assert "Configuration error" in response.errors[0]
        assert response.metadata["error_code"] == "INVALID_CONFIGURATION"

    def test_handle_chunking_error(self):
        """Test handling chunking errors."""
        handler = APIErrorHandler()
        error = ChunkingError("Chunking failed")

        response = handler.handle_exception(error)

        assert response.success is False
        assert "Chunking failed" in response.errors[0]
        assert response.metadata["error_code"] == "CHUNKING_FAILED"

    def test_handle_value_error(self):
        """Test handling value errors."""
        handler = APIErrorHandler()
        error = ValueError("Invalid value provided")

        response = handler.handle_exception(error)

        assert response.success is False
        assert "Invalid value" in response.errors[0]
        assert response.metadata["error_code"] == "INVALID_VALUE"

    def test_handle_type_error(self):
        """Test handling type errors."""
        handler = APIErrorHandler()
        error = TypeError("Expected str, got int")

        response = handler.handle_exception(error)

        assert response.success is False
        assert "Type error" in response.errors[0]
        assert response.metadata["error_code"] == "INVALID_TYPE"

    def test_handle_generic_error(self):
        """Test handling generic errors."""
        handler = APIErrorHandler()
        error = RuntimeError("Something went wrong")

        response = handler.handle_exception(error)

        assert response.success is False
        assert "Unexpected error" in response.errors[0]
        assert response.metadata["error_code"] == "INTERNAL_ERROR"

    def test_error_with_context(self):
        """Test error handling with context."""
        handler = APIErrorHandler()
        error = ValueError("Test error")
        context = {"request_id": "12345", "user": "test"}

        response = handler.handle_exception(error, context)

        assert response.success is False
        assert "context" in response.metadata["details"]
        assert response.metadata["details"]["context"]["request_id"] == "12345"

    def test_error_with_traceback(self):
        """Test error includes traceback when enabled."""
        handler = APIErrorHandler(include_traceback=True)
        error = ValueError("Test error")

        response = handler.handle_exception(error)

        assert "traceback" in response.metadata["details"]
        assert isinstance(response.metadata["details"]["traceback"], str)

    def test_error_without_traceback(self):
        """Test error doesn't include traceback by default."""
        handler = APIErrorHandler(include_traceback=False)
        error = ValueError("Test error")

        response = handler.handle_exception(error)

        assert "traceback" not in response.metadata["details"]

    def test_wrap_operation_success(self):
        """Test wrapping successful operation."""
        handler = APIErrorHandler()

        def successful_operation():
            return {"chunks": [], "metadata": {}, "warnings": []}

        response = handler.wrap_operation(successful_operation)

        assert isinstance(response, APIResponse)
        assert response.success is True

    def test_wrap_operation_failure(self):
        """Test wrapping failing operation."""
        handler = APIErrorHandler()

        def failing_operation():
            raise ValueError("Operation failed")

        response = handler.wrap_operation(failing_operation)

        assert isinstance(response, APIResponse)
        assert response.success is False
        assert len(response.errors) > 0

    def test_wrap_operation_with_args(self):
        """Test wrapping operation with arguments."""
        handler = APIErrorHandler()

        def operation_with_args(a, b, c=None):
            return {"chunks": [a, b], "metadata": {"c": c}, "warnings": []}

        response = handler.wrap_operation(operation_with_args, 1, 2, c=3)

        assert response.success is True

    def test_wrap_operation_returns_api_response(self):
        """Test wrapping operation that returns APIResponse."""
        handler = APIErrorHandler()

        def operation_returns_response():
            return APIResponse.success_response(chunks=[], metadata={})

        response = handler.wrap_operation(operation_returns_response)

        assert isinstance(response, APIResponse)
        assert response.success is True


class TestErrorHandlerFactories:
    """Test factory functions."""

    def test_create_error_handler(self):
        """Test create_error_handler factory."""
        handler = create_error_handler()
        assert isinstance(handler, APIErrorHandler)
        assert handler.include_traceback is False

    def test_create_error_handler_with_traceback(self):
        """Test factory with traceback enabled."""
        handler = create_error_handler(include_traceback=True)
        assert handler.include_traceback is True

    def test_handle_api_error_convenience(self):
        """Test handle_api_error convenience function."""
        error = ValueError("Test error")
        response = handle_api_error(error)

        assert isinstance(response, APIResponse)
        assert response.success is False

    def test_handle_api_error_with_context(self):
        """Test convenience function with context."""
        error = ValueError("Test error")
        context = {"test": "data"}

        response = handle_api_error(error, context)

        assert response.success is False
        assert "context" in response.metadata["details"]


class TestErrorHandlerIntegration:
    """Integration tests for error handler."""

    def test_complete_error_handling_workflow(self):
        """Test complete error handling workflow."""
        handler = APIErrorHandler(include_traceback=True)

        # Simulate various errors
        errors = [
            StrategySelectionError("Invalid strategy"),
            ConfigurationError("Bad config"),
            ChunkingError("Chunking failed"),
            ValueError("Bad value"),
            TypeError("Bad type"),
            RuntimeError("Generic error"),
        ]

        for error in errors:
            response = handler.handle_exception(error)
            assert isinstance(response, APIResponse)
            assert response.success is False
            assert len(response.errors) > 0
            assert "error_type" in response.metadata
            assert "error_code" in response.metadata
            assert "details" in response.metadata

    def test_error_response_structure(self):
        """Test error response has correct structure."""
        handler = APIErrorHandler()
        error = ValueError("Test")

        response = handler.handle_exception(error)

        # Verify response structure
        assert hasattr(response, "success")
        assert hasattr(response, "errors")
        assert hasattr(response, "metadata")
        assert isinstance(response.errors, list)
        assert isinstance(response.metadata, dict)

    def test_error_response_serializable(self):
        """Test error response is JSON serializable."""
        import json

        handler = APIErrorHandler()
        error = ValueError("Test error")

        response = handler.handle_exception(error)
        response_dict = response.to_dict()

        # Should not raise exception
        json_str = json.dumps(response_dict)
        assert isinstance(json_str, str)
