"""
API module for REST integration.

Provides types, validators, and adapters for REST API integration.
"""

from markdown_chunker.api.adapter import APIAdapter
from markdown_chunker.api.error_handler import (
    APIErrorHandler,
    create_error_handler,
    handle_api_error,
)
from markdown_chunker.api.types import APIError, APIRequest, APIResponse
from markdown_chunker.api.validator import APIValidator

__all__ = [
    "APIRequest",
    "APIResponse",
    "APIError",
    "APIValidator",
    "APIAdapter",
    "APIErrorHandler",
    "create_error_handler",
    "handle_api_error",
]
