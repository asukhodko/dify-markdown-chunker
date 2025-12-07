"""
Test suite for line number tracking bug fix.

This test suite validates the fix for a critical bug where the _split_text_to_size()
method in BaseStrategy was incorrectly calculating line numbers, causing them to
overflow beyond the actual input text boundaries.

Bug Details:
- When splitting text into chunks, line numbers would exceed the input text
- Example: Input with 295 lines would produce chunks with end_line=304, 312
- This caused validation errors: "end_line (298) must be >= start_line (305)"
- Root cause: Off-by-one error when starting new chunks after a split

The fix uses an offset-based approach for tracking line numbers to prevent overflow.
"""

import pytest

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig
from markdown_chunker_v2.strategies.base import BaseStrategy


class ConcreteStrategy(BaseStrategy):
    """Concrete implementation of BaseStrategy for testing."""

    @property
    def name(self) -> str:
        return "test_strategy"

    @property
    def priority(self) -> int:
        return 0

    def can_handle(self, text: str, config: ChunkConfig) -> bool:
        return True

    def apply(self, text: str, config: ChunkConfig):
        """Simple implementation that just uses _split_text_to_size."""
        return self._split_text_to_size(text, start_line=1, config=config)


class TestLineNumberTrackingBug:
    """Test suite for line number tracking bug fix."""

    @pytest.fixture
    def strategy(self):
        """Provide a concrete strategy instance for testing."""
        return ConcreteStrategy()

    @pytest.fixture
    def config(self):
        """Provide a default config for testing."""
        return ChunkConfig(max_chunk_size=1000)

    def test_line_numbers_within_bounds_simple(self, strategy, config):
        """Test that chunks don't exceed input text boundaries."""
        # Create 100 lines of text
        lines = [f"Line {i} with some content here" for i in range(1, 101)]
        text = "\n".join(lines)

        chunks = strategy._split_text_to_size(text, start_line=1, config=config)

        # Verify line numbers stay within bounds
        max_line = 100  # We have 100 lines
        for i, chunk in enumerate(chunks):
            assert (
                chunk.start_line >= 1
            ), f"Chunk {i}: start_line {chunk.start_line} < 1"
            assert (
                chunk.end_line <= max_line
            ), f"Chunk {i}: end_line {chunk.end_line} > {max_line}"
            assert (
                chunk.end_line >= chunk.start_line
            ), f"Chunk {i}: end_line {chunk.end_line} < start_line {chunk.start_line}"

    def test_line_numbers_within_bounds_exact_scenario(self, strategy, config):
        """Test the exact scenario that triggered the original bug.

        The bug occurred when list_aware strategy extracted text from lines 1-295
        (before a list block at line 296) and passed it to _split_text_to_size().
        The method would create chunks with line numbers exceeding 295.
        """
        # Simulate extracting text before line 296
        lines = [f"### Section {i // 20}\nContent for line {i}" for i in range(1, 296)]
        text_before = "\n".join(lines)

        # This should create multiple chunks due to max_chunk_size=1000
        chunks = strategy._split_text_to_size(
            text_before, start_line=1, config=ChunkConfig(max_chunk_size=1000)
        )

        # Calculate actual max line number
        max_line = 1 + text_before.count("\n")

        # CRITICAL: Before the fix, chunks would have end_line values like 304, 312
        # which exceeded the actual line count (295)
        for i, chunk in enumerate(chunks):
            assert (
                chunk.end_line <= max_line
            ), f"REGRESSION: Chunk {i} ends at line {chunk.end_line}, but input only has {max_line} lines"

    def test_offset_start_line(self, strategy, config):
        """Test that line tracking works correctly with non-1 start_line."""
        lines = [f"Line {i}" for i in range(1, 51)]
        text = "\n".join(lines)

        # Start from line 100 instead of line 1
        chunks = strategy._split_text_to_size(text, start_line=100, config=config)

        # Total lines in text
        total_lines = text.count("\n") + 1

        for chunk in chunks:
            assert chunk.start_line >= 100
            assert chunk.end_line < 100 + total_lines
            assert chunk.end_line >= chunk.start_line

    def test_single_paragraph_no_overflow(self, strategy, config):
        """Test that a single paragraph doesn't overflow line numbers."""
        text = "Single paragraph with no splits\nSecond line\nThird line"

        chunks = strategy._split_text_to_size(text, start_line=1, config=config)

        assert len(chunks) == 1
        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 3  # Exactly 3 lines, not more

    def test_multiple_splits_sequential_lines(self, strategy, config):
        """Test that multiple splits create sequential, non-overlapping line ranges."""
        # Create text that will require multiple chunks
        paragraphs = [f"Paragraph {i}\n" + "content " * 50 for i in range(20)]
        text = "\n\n".join(paragraphs)

        chunks = strategy._split_text_to_size(
            text, start_line=1, config=ChunkConfig(max_chunk_size=500)
        )

        # Verify chunks are sequential and don't overlap
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]

            # Next chunk should start exactly after current chunk ends
            assert (
                next_chunk.start_line == current_chunk.end_line + 1
            ), f"Gap or overlap between chunk {i} and {i+1}"

    def test_newline_counting_accuracy(self, strategy, config):
        """Test that newline counting is accurate for line number tracking."""
        # Text with known newline count
        text = "Line 1\nLine 2\n\nLine 4\nLine 5"  # 4 newlines = 5 lines

        chunks = strategy._split_text_to_size(text, start_line=10, config=config)

        # Should create one chunk spanning from line 10 to line 14 (5 lines)
        assert len(chunks) == 1
        assert chunks[0].start_line == 10
        assert chunks[0].end_line == 14  # 10 + 4 newlines = 14

    def test_empty_paragraphs_dont_break_tracking(self, strategy, config):
        """Test that empty paragraphs between content don't break line tracking."""
        text = "Para 1\n\n\n\nPara 2\n\n\n\nPara 3"

        chunks = strategy._split_text_to_size(text, start_line=1, config=config)

        # Calculate expected end line
        expected_end = 1 + text.count("\n")

        if len(chunks) == 1:
            assert chunks[0].end_line == expected_end
        else:
            # Last chunk should end at expected line
            assert chunks[-1].end_line == expected_end

    def test_very_long_document_no_overflow(self, strategy, config):
        """Test that very long documents don't cause line number overflow."""
        # Create 1000 lines
        lines = [f"Line {i} with content" for i in range(1, 1001)]
        text = "\n".join(lines)

        chunks = strategy._split_text_to_size(
            text, start_line=1, config=ChunkConfig(max_chunk_size=2000)
        )

        # Verify no chunk exceeds line 1000
        for chunk in chunks:
            assert chunk.end_line <= 1000, f"Chunk exceeded max line: {chunk.end_line}"

    def test_paragraph_separator_handling(self, strategy, config):
        """Test that paragraph separators (\\n\\n) are handled correctly in line counting."""
        # Each paragraph is 2 lines (text + newline), separated by blank line
        text = "Para 1\nMore 1\n\nPara 2\nMore 2\n\nPara 3\nMore 3"
        # Line breakdown:
        # 1: Para 1
        # 2: More 1
        # 3: (blank)
        # 4: Para 2
        # 5: More 2
        # 6: (blank)
        # 7: Para 3
        # 8: More 3
        # Total: 8 lines

        chunks = strategy._split_text_to_size(text, start_line=1, config=config)

        expected_lines = text.count("\n") + 1
        assert chunks[-1].end_line == expected_lines


class TestLineNumberTrackingRegression:
    """Regression tests to ensure the bug stays fixed in real-world scenarios."""

    def test_regression_no_validation_error(self):
        """
        Test using a real changelog file from the test corpus.

        This validates the fix using a complex document with:
        - File: tests/corpus/changelogs/changelogs_004.md (241 lines)
        - Multiple headers and list blocks
        - Strategy: list_aware
        """
        test_file = "tests/corpus/changelogs/changelogs_004.md"
        with open(test_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Use the same configuration that could trigger line number bugs
        config = ChunkConfig(max_chunk_size=1000, strategy_override="list_aware")
        chunker = MarkdownChunker(config)

        # This should complete without validation errors
        chunks = chunker.chunk(text)

        # Verify all chunks have valid line numbers
        assert len(chunks) > 0
        total_lines = text.count("\n") + 1

        for i, chunk in enumerate(chunks):
            assert (
                chunk.start_line >= 1
            ), f"Chunk {i}: invalid start_line {chunk.start_line}"
            assert (
                chunk.end_line <= total_lines
            ), f"Chunk {i}: end_line {chunk.end_line} exceeds total lines {total_lines}"
            assert (
                chunk.end_line >= chunk.start_line
            ), f"Chunk {i}: end_line {chunk.end_line} < start_line {chunk.start_line}"

    def test_regression_with_default_chunk_size(self):
        """Test with default chunk size (4096) to ensure bug doesn't reappear."""
        test_file = "tests/corpus/changelogs/changelogs_004.md"
        with open(test_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Use default chunk size
        config = ChunkConfig(strategy_override="list_aware")
        chunker = MarkdownChunker(config)

        chunks = chunker.chunk(text)

        total_lines = text.count("\n") + 1
        for chunk in chunks:
            assert chunk.start_line >= 1
            assert chunk.end_line <= total_lines
            assert chunk.end_line >= chunk.start_line
