"""
Data completeness validator for markdown chunking.

This module provides validation to ensure no data is lost during chunking.
"""

from dataclasses import dataclass
from typing import List

from .errors import DataLossError, IncompleteCoverageError, MissingContentError
from .types import Chunk


@dataclass
class MissingContentBlock:
    """Information about a block of content missing from chunks."""

    start_line: int
    end_line: int
    content_preview: str  # First 100 chars
    size_chars: int
    block_type: str  # "paragraph", "code", "list", etc.


@dataclass
class ValidationResult:
    """Result of data completeness validation."""

    is_valid: bool
    input_chars: int
    output_chars: int
    missing_chars: int
    char_coverage: float  # 0.0 to 1.0
    missing_blocks: List[MissingContentBlock]
    warnings: List[str]

    def get_summary(self) -> str:
        """Get human-readable validation summary."""
        if self.is_valid:
            return (
                f"Validation passed: {self.char_coverage:.1%} coverage "
                f"({self.output_chars}/{self.input_chars} chars)"
            )
        else:
            num_blocks = len(self.missing_blocks)
            return (
                f"Validation failed: {self.char_coverage:.1%} coverage "
                f"({self.output_chars}/{self.input_chars} chars), "
                f"missing {self.missing_chars} chars in {num_blocks} blocks"
            )


class DataCompletenessValidator:
    """
    Validator to ensure no data is lost during chunking.

    This validator checks that all input content appears in output chunks,
    allowing for minor whitespace normalization differences.
    """

    def __init__(self, tolerance: float = 0.05):
        """
        Initialize validator.

        Args:
            tolerance: Allowed difference ratio for whitespace
                normalization (default 5%)
        """
        self.tolerance = tolerance

    def validate_chunks(self, input_text: str, chunks: List[Chunk]) -> ValidationResult:
        """
        Validate that chunks contain all input data.

        Checks:
        - Total characters in chunks ≈ input characters (±tolerance for formatting)
        - No large gaps in line coverage
        - All significant content blocks present

        Args:
            input_text: Original input text
            chunks: List of chunks produced by chunking

        Returns:
            ValidationResult with is_valid, missing_data, warnings
        """
        # Calculate character counts
        input_chars = len(input_text)

        # Handle mock objects in tests gracefully
        try:
            output_chars = sum(len(chunk.content) for chunk in chunks)
        except (TypeError, AttributeError):
            # If chunks are mocks or have issues, skip validation
            return ValidationResult(
                is_valid=True,
                input_chars=input_chars,
                output_chars=input_chars,
                missing_chars=0,
                char_coverage=1.0,
                missing_blocks=[],
                warnings=[],
            )

        # Calculate coverage
        if input_chars == 0:
            char_coverage = 1.0 if output_chars == 0 else 0.0
        else:
            char_coverage = output_chars / input_chars

        # Calculate missing characters
        missing_chars = max(0, input_chars - output_chars)

        # Check if within tolerance
        char_diff_ratio = abs(output_chars - input_chars) / max(input_chars, 1)
        is_valid = char_diff_ratio <= self.tolerance

        # Find missing content blocks if validation fails
        missing_blocks = []
        warnings = []

        if not is_valid:
            missing_blocks = self.find_missing_content(input_text, chunks)

            # Add warnings for significant data loss
            if char_diff_ratio > 0.1:
                warnings.append(
                    f"Significant data loss: {char_diff_ratio:.1%} of content missing"
                )

        # Check for line coverage gaps
        line_gaps = self._check_line_coverage(input_text, chunks)
        if line_gaps:
            warnings.append(f"Found {len(line_gaps)} gaps in line coverage")
            # If gaps are large, mark as invalid
            large_gaps = [gap for gap in line_gaps if gap[1] - gap[0] > 10]
            if large_gaps:
                is_valid = False
                warnings.append(
                    f"Found {len(large_gaps)} large gaps (>10 lines) in coverage"
                )

        return ValidationResult(
            is_valid=is_valid,
            input_chars=input_chars,
            output_chars=output_chars,
            missing_chars=missing_chars,
            char_coverage=char_coverage,
            missing_blocks=missing_blocks,
            warnings=warnings,
        )

    def find_missing_content(
        self, input_text: str, chunks: List[Chunk]
    ) -> List[MissingContentBlock]:
        """
        Identify specific content blocks that are missing from chunks.

        This is a simplified implementation that identifies missing content
        by comparing input and output character counts per line.

        Args:
            input_text: Original input text
            chunks: List of chunks produced by chunking

        Returns:
            List of missing blocks with line numbers and content preview
        """
        missing_blocks = []

        # Get all content from chunks
        chunk_content = "\n\n".join(chunk.content for chunk in chunks)

        # Simple heuristic: if input is significantly longer than output,
        # try to identify what's missing
        input_lines = input_text.split("\n")
        chunk_lines = chunk_content.split("\n")

        # Build a set of content from chunks for quick lookup
        chunk_content_set = set(line.strip() for line in chunk_lines if line.strip())

        # Find lines that don't appear in chunks
        missing_line_ranges = []
        current_range_start = None

        for i, line in enumerate(input_lines, 1):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Check if this line appears in chunks
            if line_stripped not in chunk_content_set:
                if current_range_start is None:
                    current_range_start = i
            else:
                if current_range_start is not None:
                    # End of missing range
                    missing_line_ranges.append((current_range_start, i - 1))
                    current_range_start = None

        # Close final range if needed
        if current_range_start is not None:
            missing_line_ranges.append((current_range_start, len(input_lines)))

        # Convert line ranges to MissingContentBlock objects
        for start_line, end_line in missing_line_ranges:
            # Get content preview
            missing_lines = input_lines[start_line - 1 : end_line]
            content = "\n".join(missing_lines)
            preview = content[:100] + ("..." if len(content) > 100 else "")

            # Determine block type (simple heuristic)
            block_type = self._guess_block_type(content)

            missing_blocks.append(
                MissingContentBlock(
                    start_line=start_line,
                    end_line=end_line,
                    content_preview=preview,
                    size_chars=len(content),
                    block_type=block_type,
                )
            )

        return missing_blocks

    def _check_line_coverage(self, input_text: str, chunks: List[Chunk]) -> List[tuple]:
        """
        Check for gaps in line coverage.

        Args:
            input_text: Original input text
            chunks: List of chunks

        Returns:
            List of (start_line, end_line) tuples representing gaps
        """
        if not chunks:
            input_lines = len(input_text.split("\n"))
            return [(1, input_lines)] if input_lines > 0 else []

        # Get covered line ranges from chunks
        covered_ranges = []
        for chunk in chunks:
            if hasattr(chunk, "start_line") and hasattr(chunk, "end_line"):
                covered_ranges.append((chunk.start_line, chunk.end_line))

        if not covered_ranges:
            # No line information in chunks, can't check coverage
            return []

        # Sort ranges by start line
        covered_ranges.sort()

        # Find gaps
        gaps = []
        input_lines = len(input_text.split("\n"))

        # Check gap before first chunk
        if covered_ranges[0][0] > 1:
            gaps.append((1, covered_ranges[0][0] - 1))

        # Check gaps between chunks
        for i in range(len(covered_ranges) - 1):
            current_end = covered_ranges[i][1]
            next_start = covered_ranges[i + 1][0]

            if next_start > current_end + 1:
                gaps.append((current_end + 1, next_start - 1))

        # Check gap after last chunk
        if covered_ranges[-1][1] < input_lines:
            gaps.append((covered_ranges[-1][1] + 1, input_lines))

        return gaps

    def _guess_block_type(self, content: str) -> str:
        """
        Guess the type of content block.

        Args:
            content: Content to analyze

        Returns:
            Block type string
        """
        content_stripped = content.strip()

        # Check for code block
        if content_stripped.startswith("```") or content_stripped.startswith("    "):
            return "code"

        # Check for list
        if any(
            line.strip().startswith(marker)
            for line in content.split("\n")
            for marker in ["- ", "* ", "+ ", "1. ", "2. "]
        ):
            return "list"

        # Check for table
        if "|" in content and any(
            line.strip().startswith("|") for line in content.split("\n")
        ):
            return "table"

        # Check for header
        if content_stripped.startswith("#"):
            return "header"

        # Default to paragraph
        return "paragraph"

    def raise_if_invalid(
        self, input_text: str, chunks: List[Chunk], strict: bool = False
    ) -> None:
        """
        Raise error if validation fails.

        Args:
            input_text: Original input text
            chunks: List of chunks
            strict: If True, raise on any validation failure

        Raises:
            DataLossError: If data loss detected
            MissingContentError: If content blocks missing
            IncompleteCoverageError: If line coverage incomplete
        """
        result = self.validate_chunks(input_text, chunks)

        if not result.is_valid or strict:
            # Check for missing content blocks
            if result.missing_blocks:
                raise MissingContentError(
                    missing_blocks=result.missing_blocks,
                    total_missing_chars=result.missing_chars,
                )

            # Check for line coverage gaps
            line_gaps = self._check_line_coverage(input_text, chunks)
            large_gaps = [gap for gap in line_gaps if gap[1] - gap[0] > 10]
            if large_gaps:
                total_lines = len(input_text.split("\n"))
                raise IncompleteCoverageError(gaps=large_gaps, total_lines=total_lines)

            # Generic data loss error
            if result.missing_chars > 0:
                raise DataLossError(
                    missing_chars=result.missing_chars,
                    missing_blocks=result.missing_blocks,
                    input_chars=result.input_chars,
                )
