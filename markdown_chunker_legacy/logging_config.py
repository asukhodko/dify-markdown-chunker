"""
Logging configuration for markdown_chunker.

This module provides utilities for configuring logging throughout the library.
Users can easily enable and customize logging to debug and monitor the chunking process.

Example:
    Basic usage with default settings:

    >>> import logging
    >>> logging.basicConfig(level=logging.INFO)
    >>> from markdown_chunker import MarkdownChunker
    >>> chunker=MarkdownChunker()
    >>> chunks=chunker.chunk(text)  # Logs will be output

    Custom configuration:

    >>> from markdown_chunker.logging_config import setup_logging
    >>> logger=setup_logging(level="DEBUG")
    >>> # Now all markdown_chunker logs will use DEBUG level
"""

import logging
from typing import Optional


def setup_logging(
    level: str = "WARNING",
    format: Optional[str] = None,
    logger_name: str = "markdown_chunker",
) -> logging.Logger:
    """
    Configure logging for the markdown_chunker library.

    Args:
        level: Logging level. One of: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
        format: Custom log format string. If None, uses a default format.
        logger_name: Name of the logger to configure. Default is "markdown_chunker"

    Returns:
        Configured logger instance

    Example:
        >>> logger=setup_logging(level="INFO")
        >>> logger.info("Logging is configured")

        >>> # Custom format
        >>> logger=setup_logging(
        ...     level="DEBUG",
        ...     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ... )
    """
    # Get or create logger
    logger = logging.getLogger(logger_name)

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.WARNING)
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(numeric_level)

    # Set format
    if format is None:
        format = "%(levelname)s - %(name)s - %(message)s"

    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    This is a convenience function for getting loggers within the library.
    All loggers are children of the "markdown_chunker" logger.

    Args:
        name: Name of the module (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> # In a module file
        >>> logger=get_logger(__name__)
        >>> logger.info("Processing started")
    """
    return logging.getLogger(name)
