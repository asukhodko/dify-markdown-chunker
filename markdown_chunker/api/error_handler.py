"""
Error handler for API operations.

Provides standardized error handling and response formatting.
"""

import logging
import traceback
from typing import Any, Dict, Optional

from markdown_chunker.api.types import APIResponse
from markdown_chunker.chunker.core import ChunkingError, ConfigurationError
from markdown_chunker.chunker.selector import StrategySelectionError

logger = logging.getLogger(__name__)


class APIErrorHandler:
    """
    Centralized error handler for API operations.

    Converts exceptions into standardized API responses with
    appropriate error codes and messages.
    """

    def __init__(self, include_traceback: bool = False):
        """
        Initialize error handler.

        Args:
            include_traceback: Whether to include stack traces in error details
        """
        self.include_traceback = include_traceback

    def handle_exception(
        self, exception: Exception, context: Optional[Dict[str, Any]] = None
    ) -> APIResponse:
        """
        Handle exception and return standardized error response.

        Args:
            exception: The exception to handle
            context: Optional context information

        Returns:
            APIResponse with error information
        """
        # Log the exception
        logger.error(f"Error occurred: {type(exception).__name__}: {str(exception)}")

        # Determine error type and create appropriate response
        if isinstance(exception, StrategySelectionError):
            return self._handle_strategy_error(exception, context)
        elif isinstance(exception, ConfigurationError):
            return self._handle_configuration_error(exception, context)
        elif isinstance(exception, ChunkingError):
            return self._handle_chunking_error(exception, context)
        elif isinstance(exception, ValueError):
            return self._handle_value_error(exception, context)
        elif isinstance(exception, TypeError):
            return self._handle_type_error(exception, context)
        else:
            return self._handle_generic_error(exception, context)

    def _handle_strategy_error(
        self, exception: StrategySelectionError, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle strategy selection errors."""
        error_msg = str(exception)
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": "StrategySelectionError",
                "error_code": "INVALID_STRATEGY",
                "details": details,
            },
        )

    def _handle_configuration_error(
        self, exception: ConfigurationError, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle configuration errors."""
        error_msg = f"Configuration error: {str(exception)}"
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": "ConfigurationError",
                "error_code": "INVALID_CONFIGURATION",
                "details": details,
            },
        )

    def _handle_chunking_error(
        self, exception: ChunkingError, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle chunking errors."""
        error_msg = f"Chunking failed: {str(exception)}"
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": "ChunkingError",
                "error_code": "CHUNKING_FAILED",
                "details": details,
            },
        )

    def _handle_value_error(
        self, exception: ValueError, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle value errors."""
        error_msg = f"Invalid value: {str(exception)}"
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": "ValueError",
                "error_code": "INVALID_VALUE",
                "details": details,
            },
        )

    def _handle_type_error(
        self, exception: TypeError, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle type errors."""
        error_msg = f"Type error: {str(exception)}"
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": "TypeError",
                "error_code": "INVALID_TYPE",
                "details": details,
            },
        )

    def _handle_generic_error(
        self, exception: Exception, context: Optional[Dict[str, Any]]
    ) -> APIResponse:
        """Handle generic/unexpected errors."""
        error_msg = f"Unexpected error: {str(exception)}"
        details = self._build_error_details(exception, context)

        return APIResponse.error_response(
            errors=[error_msg],
            metadata={
                "error_type": type(exception).__name__,
                "error_code": "INTERNAL_ERROR",
                "details": details,
            },
        )

    def _build_error_details(
        self, exception: Exception, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build error details dictionary."""
        details: Dict[str, Any] = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }

        if context:
            details["context"] = context

        if self.include_traceback:
            details["traceback"] = traceback.format_exc()

        return details

    def wrap_operation(self, operation, *args, **kwargs) -> APIResponse:
        """
        Wrap an operation with error handling.

        Args:
            operation: Callable to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation

        Returns:
            APIResponse (either success or error)
        """
        try:
            result = operation(*args, **kwargs)

            # If result is already an APIResponse, return it
            if isinstance(result, APIResponse):
                return result

            # Otherwise, wrap in success response
            return APIResponse.success_response(
                chunks=result.get("chunks", []),
                metadata=result.get("metadata", {}),
                warnings=result.get("warnings", []),
            )
        except Exception as e:
            return self.handle_exception(e, context={"operation": operation.__name__})


def create_error_handler(include_traceback: bool = False) -> APIErrorHandler:
    """
    Factory function to create error handler.

    Args:
        include_traceback: Whether to include tracebacks

    Returns:
        APIErrorHandler instance
    """
    return APIErrorHandler(include_traceback=include_traceback)


def handle_api_error(
    exception: Exception, context: Optional[Dict[str, Any]] = None
) -> APIResponse:
    """
    Convenience function to handle an error.

    Args:
        exception: Exception to handle
        context: Optional context

    Returns:
        APIResponse with error
    """
    handler = APIErrorHandler()
    return handler.handle_exception(exception, context)
