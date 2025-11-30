"""
API adapter for REST integration.

Provides high-level interface for processing API requests.
"""

from typing import Optional

from markdown_chunker.api.types import APIRequest, APIResponse
from markdown_chunker.api.validator import APIValidator
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class APIAdapter:
    """
    Adapter for processing API requests.

    Handles request validation, chunking, and response formatting.
    Caches chunker instance for performance.
    """

    def __init__(
        self, validator: Optional[APIValidator] = None, cache_chunker: bool = True
    ):
        """
        Initialize API adapter.

        Args:
            validator: Optional custom validator
            cache_chunker: Whether to cache chunker instance
        """
        self.validator = validator or APIValidator()
        self.cache_chunker = cache_chunker
        self._cached_chunker: Optional[MarkdownChunker] = None
        self._cached_config_hash: Optional[int] = None

    def process_request(self, request: APIRequest) -> APIResponse:
        """
        Process API request.

        Args:
            request: API request to process

        Returns:
            API response with chunks or errors
        """
        # Validate request
        validation_errors = self.validator.validate_request(request)
        if validation_errors:
            return APIResponse.error_response(
                errors=[error.message for error in validation_errors]
            )

        try:
            # Get or create chunker
            chunker = self._get_chunker(request.config)

            # Process content
            # Convert "auto" strategy to None for automatic selection
            strategy = None if request.strategy == "auto" else request.strategy
            result = chunker.chunk(
                request.content, strategy=strategy, include_analysis=True
            )

            # Convert to API response
            chunks = [chunk.to_dict() for chunk in result.chunks]

            metadata = {
                "strategy_used": result.strategy_used,
                "processing_time": result.processing_time,
                "fallback_used": result.fallback_used,
                "fallback_level": result.fallback_level,
                "total_chunks": result.total_chunks,
                "total_chars": result.total_chars,
                "content_type": result.content_type,
                "complexity_score": result.complexity_score,
            }

            # Add request metadata if provided
            if request.metadata:
                metadata["request_metadata"] = request.metadata

            return APIResponse.success_response(
                chunks=chunks, metadata=metadata, warnings=result.warnings
            )

        except Exception as e:
            # Handle processing errors
            return APIResponse.error_response(
                errors=[f"Processing failed: {str(e)}"],
                metadata={"error_type": type(e).__name__},
            )

    def _get_chunker(self, config_dict: Optional[dict] = None) -> MarkdownChunker:
        """
        Get chunker instance (cached or new).

        Args:
            config_dict: Optional configuration dictionary

        Returns:
            MarkdownChunker instance
        """
        # If no caching, always create new
        if not self.cache_chunker:
            return self._create_chunker(config_dict)

        # Calculate config hash for cache key
        config_hash = hash(str(sorted(config_dict.items()))) if config_dict else 0

        # Return cached if config matches
        if self._cached_chunker and self._cached_config_hash == config_hash:
            return self._cached_chunker

        # Create and cache new chunker
        self._cached_chunker = self._create_chunker(config_dict)
        self._cached_config_hash = config_hash

        return self._cached_chunker

    def _create_chunker(self, config_dict: Optional[dict] = None) -> MarkdownChunker:
        """
        Create new chunker instance.

        Args:
            config_dict: Optional configuration dictionary

        Returns:
            New MarkdownChunker instance
        """
        if config_dict:
            config = ChunkConfig.from_dict(config_dict)
            return MarkdownChunker(config)
        return MarkdownChunker()

    def clear_cache(self) -> None:
        """Clear cached chunker instance."""
        self._cached_chunker = None
        self._cached_config_hash = None

    def process_dict(self, request_dict: dict) -> dict:
        """
        Process request from dictionary.

        Convenience method for direct dictionary processing.

        Args:
            request_dict: Request as dictionary

        Returns:
            Response as dictionary
        """
        try:
            request = APIRequest.from_dict(request_dict)
            response = self.process_request(request)
            return response.to_dict()
        except Exception as e:
            return APIResponse.error_response(
                errors=[f"Request parsing failed: {str(e)}"]
            ).to_dict()
