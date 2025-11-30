"""Tests for logging configuration module."""

import logging

from markdown_chunker.logging_config import get_logger, setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_default_configuration(self):
        """Test setup_logging with default parameters."""
        logger = setup_logging()

        assert logger.name == "markdown_chunker"
        assert logger.level == logging.WARNING
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)

    def test_custom_level_info(self):
        """Test setup_logging with INFO level."""
        logger = setup_logging(level="INFO")

        assert logger.level == logging.INFO

    def test_custom_level_debug(self):
        """Test setup_logging with DEBUG level."""
        logger = setup_logging(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_custom_level_error(self):
        """Test setup_logging with ERROR level."""
        logger = setup_logging(level="ERROR")

        assert logger.level == logging.ERROR

    def test_custom_format(self):
        """Test setup_logging with custom format."""
        custom_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logger = setup_logging(level="INFO", format=custom_format)

        handler = logger.handlers[0]
        assert handler.formatter._fmt == custom_format

    def test_logger_does_not_propagate(self):
        """Test that logger does not propagate to root logger."""
        logger = setup_logging()

        assert logger.propagate is False

    def test_multiple_calls_no_duplicate_handlers(self):
        """Test that calling setup_logging multiple times doesn't create duplicate handlers."""
        logger1 = setup_logging(level="INFO")
        logger2 = setup_logging(level="DEBUG")

        # Should be the same logger instance
        assert logger1 is logger2
        # Should have only one handler
        assert len(logger2.handlers) == 1

    def test_case_insensitive_level(self):
        """Test that level parameter is case-insensitive."""
        logger_lower = setup_logging(level="info")
        logger_upper = setup_logging(level="INFO")
        logger_mixed = setup_logging(level="Info")

        assert logger_lower.level == logging.INFO
        assert logger_upper.level == logging.INFO
        assert logger_mixed.level == logging.INFO

    def test_invalid_level_defaults_to_warning(self):
        """Test that invalid level defaults to WARNING."""
        logger = setup_logging(level="INVALID")

        assert logger.level == logging.WARNING

    def test_custom_logger_name(self):
        """Test setup_logging with custom logger name."""
        logger = setup_logging(logger_name="custom_logger")

        assert logger.name == "custom_logger"


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_with_module_name(self):
        """Test get_logger with __name__ pattern."""
        logger = get_logger("markdown_chunker.parser.analyzer")

        assert logger.name == "markdown_chunker.parser.analyzer"

    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        assert logger1 is logger2


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_logging_output(self, caplog):
        """Test that logging actually outputs messages."""
        # Clear any existing handlers
        logger = logging.getLogger("markdown_chunker")
        logger.handlers.clear()

        # Don't use setup_logging as it sets propagate=False
        # Instead configure logger to work with caplog
        logger.setLevel(logging.INFO)
        logger.propagate = True

        with caplog.at_level(logging.INFO, logger="markdown_chunker"):
            logger.info("Test message")

        assert "Test message" in caplog.text

    def test_debug_level_shows_debug_messages(self, caplog):
        """Test that DEBUG level shows debug messages."""
        # Clear any existing handlers
        logger = logging.getLogger("markdown_chunker")
        logger.handlers.clear()
        logger.setLevel(logging.DEBUG)
        logger.propagate = True

        with caplog.at_level(logging.DEBUG, logger="markdown_chunker"):
            logger.debug("Debug message")
            logger.info("Info message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text

    def test_warning_level_hides_info_messages(self, caplog):
        """Test that WARNING level hides INFO messages."""
        # Clear any existing handlers
        logger = logging.getLogger("markdown_chunker")
        logger.handlers.clear()
        logger.setLevel(logging.WARNING)
        logger.propagate = True

        # caplog captures at WARNING level to match logger level
        with caplog.at_level(logging.WARNING, logger="markdown_chunker"):
            logger.info("Info message")
            logger.warning("Warning message")

        # Info should not appear (logger level is WARNING), warning should
        assert "Info message" not in caplog.text
        assert "Warning message" in caplog.text

    def test_child_logger_inherits_configuration(self, caplog):
        """Test that child loggers inherit parent configuration."""
        # Clear parent logger handlers
        parent_logger = logging.getLogger("markdown_chunker")
        parent_logger.handlers.clear()
        parent_logger.setLevel(logging.INFO)
        parent_logger.propagate = True

        # Get child logger
        child_logger = get_logger("markdown_chunker.parser")
        child_logger.propagate = True

        with caplog.at_level(logging.INFO):
            child_logger.info("Child message")

        assert "Child message" in caplog.text
