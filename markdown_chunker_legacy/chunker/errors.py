"""
Error types for markdown chunking.

This module defines a hierarchy of specific error types to replace
generic exception handling and provide better error context.
"""

from typing import List, Optional


class ChunkingError(Exception):
    """Base exception for all chunking errors."""

    def __init__(self, message: str, context: Optional[dict] = None):
        """
        Initialize chunking error.

        Args:
            message: Error message
            context: Optional context dictionary with additional info
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}


class InputValidationError(ChunkingError):
    """Error during input validation."""

    pass


class EmptyInputError(InputValidationError):
    """Input is empty or contains only whitespace."""

    def __init__(self, message: str = "Input is empty or whitespace-only"):
        super().__init__(message)


class InvalidEncodingError(InputValidationError):
    """Input has invalid encoding."""

    def __init__(self, message: str, encoding: Optional[str] = None):
        super().__init__(message)
        self.encoding = encoding


class StrategyError(ChunkingError):
    """Strategy failed to process content."""

    def __init__(
        self,
        strategy_name: str,
        reason: str,
        content_preview: Optional[str] = None,
    ):
        """
        Initialize strategy error.

        Args:
            strategy_name: Name of the strategy that failed
            reason: Reason for failure
            content_preview: Optional preview of content (first 100 chars)
        """
        message = f"Strategy '{strategy_name}' failed: {reason}"
        super().__init__(message)
        self.strategy_name = strategy_name
        self.reason = reason
        self.content_preview = content_preview


class StrategyNotFoundError(StrategyError):
    """Requested strategy not found."""

    def __init__(self, strategy_name: str, available_strategies: List[str]):
        reason = (
            f"Strategy not found. "
            f"Available strategies: {', '.join(available_strategies)}"
        )
        super().__init__(strategy_name, reason)
        self.available_strategies = available_strategies


class StrategyFailedError(StrategyError):
    """Strategy execution failed."""

    def __init__(
        self,
        strategy_name: str,
        original_error: Exception,
        content_preview: Optional[str] = None,
    ):
        reason = f"{type(original_error).__name__}: {str(original_error)}"
        super().__init__(strategy_name, reason, content_preview)
        self.original_error = original_error


class NoStrategyCanHandleError(StrategyError):
    """No strategy can handle the content."""

    def __init__(self, content_type: str, tried_strategies: List[str]):
        reason = (
            f"No strategy can handle content type '{content_type}'. "
            f"Tried: {', '.join(tried_strategies)}"
        )
        super().__init__("auto", reason)
        self.content_type = content_type
        self.tried_strategies = tried_strategies


class DataLossError(ChunkingError):
    """Data was lost during chunking."""

    def __init__(
        self,
        missing_chars: int,
        missing_blocks: Optional[List] = None,
        input_chars: Optional[int] = None,
    ):
        """
        Initialize data loss error.

        Args:
            missing_chars: Number of missing characters
            missing_blocks: List of missing content blocks
            input_chars: Total input characters
        """
        if input_chars:
            loss_pct = (missing_chars / input_chars) * 100
            message = (
                f"Data loss detected: {missing_chars} chars missing "
                f"({loss_pct:.1f}% of input)"
            )
        else:
            message = f"Data loss detected: {missing_chars} chars missing"

        super().__init__(message)
        self.missing_chars = missing_chars
        self.missing_blocks = missing_blocks or []
        self.input_chars = input_chars


class MissingContentError(DataLossError):
    """Specific content blocks are missing."""

    def __init__(self, missing_blocks: List, total_missing_chars: int):
        super().__init__(
            missing_chars=total_missing_chars, missing_blocks=missing_blocks
        )
        self.message = (
            f"Missing {len(missing_blocks)} content blocks "
            f"({total_missing_chars} chars)"
        )


class IncompleteCoverageError(DataLossError):
    """Line coverage is incomplete with large gaps."""

    def __init__(self, gaps: List[tuple], total_lines: int):
        """
        Initialize incomplete coverage error.

        Args:
            gaps: List of (start_line, end_line) tuples for gaps
            total_lines: Total number of lines in input
        """
        missing_lines = sum(end - start + 1 for start, end in gaps)
        message = (
            f"Incomplete line coverage: {len(gaps)} gaps "
            f"covering {missing_lines}/{total_lines} lines"
        )
        super().__init__(missing_chars=0)
        self.message = message
        self.gaps = gaps
        self.total_lines = total_lines


class ValidationError(ChunkingError):
    """Validation failed."""

    pass


class InvalidChunkError(ValidationError):
    """Chunk has invalid structure or content."""

    def __init__(self, chunk_index: int, reason: str):
        message = f"Invalid chunk at index {chunk_index}: {reason}"
        super().__init__(message)
        self.chunk_index = chunk_index
        self.reason = reason


class InvalidMetadataError(ValidationError):
    """Chunk metadata is invalid or incomplete."""

    def __init__(self, chunk_index: int, missing_fields: Optional[List[str]] = None):
        if missing_fields:
            fields_str = ", ".join(missing_fields)
            message = (
                f"Invalid metadata at chunk {chunk_index}: "
                f"missing fields: {fields_str}"
            )
        else:
            message = f"Invalid metadata at chunk {chunk_index}"

        super().__init__(message)
        self.chunk_index = chunk_index
        self.missing_fields = missing_fields or []
