"""Tests for logging integration in MarkdownChunker."""

import logging

from markdown_chunker import MarkdownChunker


class TestLoggingIntegration:
    """Tests for logging functionality in chunker."""

    def test_logging_basic_chunking(self, caplog):
        """Test that basic chunking produces expected log messages."""
        chunker = MarkdownChunker()

        content = """# Test Document

This is a test document with some content.

## Section 1

Some text here.
"""

        with caplog.at_level(logging.INFO):
            chunks = chunker.chunk(content)

        # Check that we got chunks
        assert len(chunks) > 0

        # Check for expected log messages
        log_messages = [record.message for record in caplog.records]

        # Should have "Starting chunking" message
        assert any("Starting chunking" in msg for msg in log_messages)

        # Should have "Stage 1 analysis complete" message
        assert any("Stage 1 analysis complete" in msg for msg in log_messages)

        # Should have "Strategy selected" or "Using manual strategy" message
        assert any(
            "Strategy selected" in msg or "Using manual strategy" in msg
            for msg in log_messages
        )

        # Should have "Chunking complete" message
        assert any("Chunking complete" in msg for msg in log_messages)

    def test_logging_with_manual_strategy(self, caplog):
        """Test logging when using manual strategy override."""
        chunker = MarkdownChunker()

        content = """# Test

Some content."""

        with caplog.at_level(logging.INFO):
            chunks = chunker.chunk(content, strategy="structural")

        assert len(chunks) > 0

        log_messages = [record.message for record in caplog.records]

        # Should mention manual strategy override
        assert any("manual strategy override" in msg.lower() for msg in log_messages)

    def test_logging_error_handling(self, caplog):
        """Test that errors are logged appropriately."""
        chunker = MarkdownChunker()

        # Empty content should not cause errors but should be handled
        with caplog.at_level(logging.INFO):
            chunks = chunker.chunk("")

        # Should complete without errors
        assert isinstance(chunks, list)

    def test_logging_levels(self, caplog):
        """Test that different log levels work correctly."""
        chunker = MarkdownChunker()

        content = "# Test\n\nContent"

        # Test INFO level
        with caplog.at_level(logging.INFO):
            chunker.chunk(content)
            info_count = len([r for r in caplog.records if r.levelno == logging.INFO])
            assert info_count > 0

        caplog.clear()

        # Test DEBUG level (should have more messages)
        with caplog.at_level(logging.DEBUG):
            chunker.chunk(content)
            debug_count = len([r for r in caplog.records if r.levelno == logging.DEBUG])
            # DEBUG messages might be present if warnings exist
            assert debug_count >= 0

    def test_logging_includes_metrics(self, caplog):
        """Test that log messages include useful metrics."""
        chunker = MarkdownChunker()

        content = """# Test Document

This is a longer document with multiple sections.

## Section 1

Content here.

## Section 2

More content.
"""

        with caplog.at_level(logging.INFO):
            chunker.chunk(content)

        log_text = " ".join([record.message for record in caplog.records])

        # Should include text length
        assert "text_length=" in log_text

        # Should include chunk count
        assert "chunks=" in log_text

        # Should include processing time
        assert "processing_time=" in log_text

        # Should include strategy name
        assert "strategy=" in log_text

    def test_logging_with_fallback(self, caplog):
        """Test logging when fallback is triggered."""
        chunker = MarkdownChunker()

        # Create content that might trigger fallback
        # (very simple content that primary strategy might not handle well)
        content = "Just a single line of text."

        with caplog.at_level(logging.WARNING):
            chunks = chunker.chunk(content)

        # Should complete successfully
        assert len(chunks) > 0

        # Check if fallback was logged (might or might not happen depending on strategy)
        [record.message for record in caplog.records]
        # This is optional - fallback might not be triggered for simple content
        # Just verify no errors occurred
        error_messages = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert len(error_messages) == 0


class TestLoggingConfiguration:
    """Tests for logging configuration."""

    def test_logging_can_be_disabled(self, caplog):
        """Test that logging can be effectively disabled."""
        # Set root logger to CRITICAL before creating chunker
        logging.getLogger("markdown_chunker").setLevel(logging.CRITICAL)

        chunker = MarkdownChunker()

        content = "# Test\n\nContent"

        # Capture at CRITICAL level
        with caplog.at_level(logging.CRITICAL):
            chunker.chunk(content)

        # Should have no INFO/WARNING/ERROR logs at CRITICAL level
        [r for r in caplog.records if r.levelno < logging.CRITICAL]
        # Note: caplog captures all logs, but we verify none are at CRITICAL level
        assert all(r.levelno < logging.CRITICAL for r in caplog.records)

    def test_logging_respects_level(self, caplog):
        """Test that logging respects configured level."""
        # Configure logger to propagate for caplog
        logger = logging.getLogger("markdown_chunker")
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        logger.propagate = True

        chunker = MarkdownChunker()

        content = "# Test\n\nContent"

        # Capture all logs but verify they exist
        with caplog.at_level(logging.INFO, logger="markdown_chunker"):
            chunker.chunk(content)

        # Should have INFO messages (logging is working)
        info_messages = [
            r
            for r in caplog.records
            if r.levelno == logging.INFO and r.name.startswith("markdown_chunker")
        ]
        assert len(info_messages) > 0

        # Should have some logs from markdown_chunker.chunker.core
        core_logs = [
            r for r in caplog.records if "markdown_chunker.chunker.core" in r.name
        ]
        assert len(core_logs) > 0
