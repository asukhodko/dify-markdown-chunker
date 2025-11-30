"""
Tests for chunking error types.

This module tests the error hierarchy and specific error types
used throughout the chunking system.
"""

from markdown_chunker.chunker.errors import (
    ChunkingError,
    DataLossError,
    EmptyInputError,
    IncompleteCoverageError,
    InputValidationError,
    InvalidChunkError,
    InvalidEncodingError,
    InvalidMetadataError,
    MissingContentError,
    NoStrategyCanHandleError,
    StrategyError,
    StrategyFailedError,
    StrategyNotFoundError,
    ValidationError,
)


class TestChunkingError:
    """Test base ChunkingError class."""

    def test_chunking_error_creation(self):
        """Test creating a chunking error."""
        error = ChunkingError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.context == {}

    def test_chunking_error_with_context(self):
        """Test chunking error with context."""
        context = {"file": "test.md", "line": 42}
        error = ChunkingError("Test error", context=context)

        assert error.message == "Test error"
        assert error.context == context
        assert error.context["file"] == "test.md"

    def test_chunking_error_inheritance(self):
        """Test that ChunkingError inherits from Exception."""
        error = ChunkingError("Test")
        assert isinstance(error, Exception)


class TestInputValidationErrors:
    """Test input validation error types."""

    def test_input_validation_error(self):
        """Test InputValidationError."""
        error = InputValidationError("Invalid input")
        assert isinstance(error, ChunkingError)
        assert "Invalid input" in str(error)

    def test_empty_input_error(self):
        """Test EmptyInputError."""
        error = EmptyInputError()
        assert isinstance(error, InputValidationError)
        assert "empty" in str(error).lower()

    def test_empty_input_error_custom_message(self):
        """Test EmptyInputError with custom message."""
        error = EmptyInputError("Custom empty message")
        assert "Custom empty message" in str(error)

    def test_invalid_encoding_error(self):
        """Test InvalidEncodingError."""
        error = InvalidEncodingError("Bad encoding", encoding="utf-16")
        assert isinstance(error, InputValidationError)
        assert error.encoding == "utf-16"
        assert "Bad encoding" in str(error)


class TestStrategyErrors:
    """Test strategy error types."""

    def test_strategy_error(self):
        """Test StrategyError."""
        error = StrategyError("structural", "Failed to parse")
        assert isinstance(error, ChunkingError)
        assert error.strategy_name == "structural"
        assert error.reason == "Failed to parse"
        assert "structural" in str(error)
        assert "Failed to parse" in str(error)

    def test_strategy_error_with_preview(self):
        """Test StrategyError with content preview."""
        error = StrategyError("code", "Syntax error", content_preview="def foo():")
        assert error.content_preview == "def foo():"

    def test_strategy_not_found_error(self):
        """Test StrategyNotFoundError."""
        available = ["structural", "code", "sentences"]
        error = StrategyNotFoundError("invalid", available)

        assert isinstance(error, StrategyError)
        assert error.strategy_name == "invalid"
        assert error.available_strategies == available
        assert "structural" in str(error)
        assert "code" in str(error)

    def test_strategy_failed_error(self):
        """Test StrategyFailedError."""
        original = ValueError("Original error")
        error = StrategyFailedError("structural", original)

        assert isinstance(error, StrategyError)
        assert error.strategy_name == "structural"
        assert error.original_error == original
        assert "ValueError" in str(error)

    def test_strategy_failed_error_with_preview(self):
        """Test StrategyFailedError with content preview."""
        original = RuntimeError("Runtime issue")
        error = StrategyFailedError("mixed", original, content_preview="# Header")

        assert error.content_preview == "# Header"

    def test_no_strategy_can_handle_error(self):
        """Test NoStrategyCanHandleError."""
        tried = ["structural", "code", "list"]
        error = NoStrategyCanHandleError("unknown", tried)

        assert isinstance(error, StrategyError)
        assert error.content_type == "unknown"
        assert error.tried_strategies == tried
        assert "structural" in str(error)


class TestDataLossErrors:
    """Test data loss error types."""

    def test_data_loss_error(self):
        """Test DataLossError."""
        error = DataLossError(missing_chars=150)

        assert isinstance(error, ChunkingError)
        assert error.missing_chars == 150
        assert error.missing_blocks == []
        assert "150" in str(error)

    def test_data_loss_error_with_percentage(self):
        """Test DataLossError with input chars for percentage."""
        error = DataLossError(missing_chars=50, input_chars=1000)

        assert error.missing_chars == 50
        assert error.input_chars == 1000
        # Should show percentage
        assert "5.0%" in str(error) or "5%" in str(error)

    def test_data_loss_error_with_blocks(self):
        """Test DataLossError with missing blocks."""
        blocks = [{"start": 10, "end": 20}, {"start": 30, "end": 40}]
        error = DataLossError(missing_chars=100, missing_blocks=blocks)

        assert error.missing_blocks == blocks
        assert len(error.missing_blocks) == 2

    def test_missing_content_error(self):
        """Test MissingContentError."""
        blocks = [{"line": 5, "content": "missing"}]
        error = MissingContentError(blocks, total_missing_chars=50)

        assert isinstance(error, DataLossError)
        assert error.missing_blocks == blocks
        assert error.missing_chars == 50
        assert "1" in error.message  # 1 block
        assert "50" in error.message  # 50 chars

    def test_incomplete_coverage_error(self):
        """Test IncompleteCoverageError."""
        gaps = [(5, 10), (20, 25)]
        error = IncompleteCoverageError(gaps, total_lines=100)

        assert isinstance(error, DataLossError)
        assert error.gaps == gaps
        assert error.total_lines == 100
        assert "2" in error.message  # 2 gaps
        # Should mention missing lines
        assert "11" in error.message or "lines" in error.message.lower()


class TestValidationErrors:
    """Test validation error types."""

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation failed")
        assert isinstance(error, ChunkingError)
        assert "Validation failed" in str(error)

    def test_invalid_chunk_error(self):
        """Test InvalidChunkError."""
        error = InvalidChunkError(chunk_index=3, reason="Missing content")

        assert isinstance(error, ValidationError)
        assert error.chunk_index == 3
        assert error.reason == "Missing content"
        assert "3" in str(error)
        assert "Missing content" in str(error)

    def test_invalid_metadata_error(self):
        """Test InvalidMetadataError."""
        missing_fields = ["strategy", "content_type"]
        error = InvalidMetadataError(chunk_index=5, missing_fields=missing_fields)

        assert isinstance(error, ValidationError)
        assert error.chunk_index == 5
        assert error.missing_fields == missing_fields
        assert "strategy" in str(error)
        assert "content_type" in str(error)

    def test_invalid_metadata_error_no_fields(self):
        """Test InvalidMetadataError without specific fields."""
        error = InvalidMetadataError(chunk_index=2)

        assert error.chunk_index == 2
        assert error.missing_fields == []
        assert "2" in str(error)


class TestErrorHierarchy:
    """Test error hierarchy relationships."""

    def test_all_errors_inherit_from_chunking_error(self):
        """Test that all custom errors inherit from ChunkingError."""
        errors = [
            InputValidationError("test"),
            EmptyInputError(),
            InvalidEncodingError("test"),
            StrategyError("test", "reason"),
            StrategyNotFoundError("test", []),
            StrategyFailedError("test", Exception()),
            NoStrategyCanHandleError("test", []),
            DataLossError(10),
            MissingContentError([], 10),
            IncompleteCoverageError([], 10),
            ValidationError("test"),
            InvalidChunkError(0, "test"),
            InvalidMetadataError(0),
        ]

        for error in errors:
            assert isinstance(error, ChunkingError)
            assert isinstance(error, Exception)

    def test_input_validation_hierarchy(self):
        """Test InputValidationError hierarchy."""
        assert issubclass(EmptyInputError, InputValidationError)
        assert issubclass(InvalidEncodingError, InputValidationError)

    def test_strategy_error_hierarchy(self):
        """Test StrategyError hierarchy."""
        assert issubclass(StrategyNotFoundError, StrategyError)
        assert issubclass(StrategyFailedError, StrategyError)
        assert issubclass(NoStrategyCanHandleError, StrategyError)

    def test_data_loss_hierarchy(self):
        """Test DataLossError hierarchy."""
        assert issubclass(MissingContentError, DataLossError)
        assert issubclass(IncompleteCoverageError, DataLossError)

    def test_validation_error_hierarchy(self):
        """Test ValidationError hierarchy."""
        assert issubclass(InvalidChunkError, ValidationError)
        assert issubclass(InvalidMetadataError, ValidationError)


class TestErrorUsage:
    """Test practical error usage scenarios."""

    def test_catching_specific_error(self):
        """Test catching specific error type."""
        try:
            raise StrategyNotFoundError("invalid", ["valid1", "valid2"])
        except StrategyNotFoundError as e:
            assert e.strategy_name == "invalid"
            assert "valid1" in str(e)

    def test_catching_base_error(self):
        """Test catching base ChunkingError."""
        try:
            raise InvalidChunkError(0, "test")
        except ChunkingError as e:
            assert isinstance(e, InvalidChunkError)

    def test_error_context_preservation(self):
        """Test that error context is preserved."""
        context = {"file": "test.md", "operation": "chunking"}
        error = ChunkingError("Test", context=context)

        try:
            raise error
        except ChunkingError as e:
            assert e.context == context
            assert e.context["file"] == "test.md"

    def test_nested_error_handling(self):
        """Test handling nested errors."""
        original = ValueError("Original problem")

        try:
            raise StrategyFailedError("structural", original)
        except StrategyFailedError as e:
            assert e.original_error == original
            assert isinstance(e.original_error, ValueError)
