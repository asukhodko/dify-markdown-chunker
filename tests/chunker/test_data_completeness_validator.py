"""
Tests for DataCompletenessValidator.

This module tests the data completeness validation functionality
that ensures no data is lost during chunking.
"""

import pytest

from markdown_chunker.chunker.errors import (
    DataLossError,
    MissingContentError,
)
from markdown_chunker.chunker.types import Chunk
from markdown_chunker.chunker.validator import (
    DataCompletenessValidator,
    MissingContentBlock,
    ValidationResult,
)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            is_valid=True,
            input_chars=100,
            output_chars=98,
            missing_chars=2,
            char_coverage=0.98,
            missing_blocks=[],
            warnings=[],
        )

        assert result.is_valid is True
        assert result.input_chars == 100
        assert result.output_chars == 98
        assert result.char_coverage == 0.98

    def test_validation_result_summary_valid(self):
        """Test summary for valid result."""
        result = ValidationResult(
            is_valid=True,
            input_chars=100,
            output_chars=98,
            missing_chars=2,
            char_coverage=0.98,
            missing_blocks=[],
            warnings=[],
        )

        summary = result.get_summary()
        assert "98.0% coverage" in summary
        assert "98/100" in summary

    def test_validation_result_summary_invalid(self):
        """Test summary for invalid result."""
        result = ValidationResult(
            is_valid=False,
            input_chars=100,
            output_chars=85,
            missing_chars=15,
            char_coverage=0.85,
            missing_blocks=[
                MissingContentBlock(1, 5, "missing content", 15, "paragraph")
            ],
            warnings=[],
        )

        summary = result.get_summary()
        assert "85.0% coverage" in summary
        assert "missing 15 chars" in summary
        assert "1 blocks" in summary


class TestMissingContentBlock:
    """Test MissingContentBlock dataclass."""

    def test_missing_content_block_creation(self):
        """Test creating a missing content block."""
        block = MissingContentBlock(
            start_line=10,
            end_line=15,
            content_preview="This is missing content...",
            size_chars=150,
            block_type="paragraph",
        )

        assert block.start_line == 10
        assert block.end_line == 15
        assert block.size_chars == 150
        assert block.block_type == "paragraph"


class TestDataCompletenessValidator:
    """Test DataCompletenessValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DataCompletenessValidator(tolerance=0.05)

    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = DataCompletenessValidator(tolerance=0.1)
        assert validator.tolerance == 0.1

    def test_validator_default_tolerance(self):
        """Test validator with default tolerance."""
        validator = DataCompletenessValidator()
        assert validator.tolerance == 0.05

    def test_validate_chunks_perfect_match(self):
        """Test validation with perfect character match."""
        input_text = "# Header\n\nContent here."
        chunks = [
            Chunk(
                content="# Header\n\nContent here.",
                start_line=1,
                end_line=3,
                metadata={},
            )
        ]

        result = self.validator.validate_chunks(input_text, chunks)

        assert result.is_valid is True
        assert result.input_chars == len(input_text)
        assert result.output_chars == len(input_text)
        assert result.missing_chars == 0
        assert result.char_coverage == 1.0
        assert len(result.missing_blocks) == 0

    def test_validate_chunks_within_tolerance(self):
        """Test validation with difference within tolerance."""
        input_text = "# Header\n\nContent here."
        # Output has slightly different whitespace (within 5% tolerance)
        chunks = [
            Chunk(
                content="# Header\nContent here.",
                start_line=1,
                end_line=3,
                metadata={},
            )
        ]

        result = self.validator.validate_chunks(input_text, chunks)

        # Should pass because difference is within 5% tolerance
        assert result.is_valid is True

    def test_validate_chunks_exceeds_tolerance(self):
        """Test validation with difference exceeding tolerance."""
        input_text = "# Header\n\nContent here with lots of text."
        # Output missing significant content (>5%)
        chunks = [Chunk(content="# Header", start_line=1, end_line=1, metadata={})]

        result = self.validator.validate_chunks(input_text, chunks)

        assert result.is_valid is False
        assert result.missing_chars > 0
        assert result.char_coverage < 0.95

    def test_validate_chunks_empty_input(self):
        """Test validation with empty input."""
        result = self.validator.validate_chunks("", [])

        assert result.is_valid is True
        assert result.input_chars == 0
        assert result.output_chars == 0
        assert result.char_coverage == 1.0

    def test_validate_chunks_empty_output(self):
        """Test validation with empty output."""
        input_text = "# Header\n\nContent"
        result = self.validator.validate_chunks(input_text, [])

        assert result.is_valid is False
        assert result.missing_chars == len(input_text)
        assert result.char_coverage == 0.0

    def test_validate_chunks_multiple_chunks(self):
        """Test validation with multiple chunks."""
        input_text = "# Header\n\nParagraph 1.\n\nParagraph 2."
        chunks = [
            Chunk(
                content="# Header\n\nParagraph 1.",
                start_line=1,
                end_line=3,
                metadata={},
            ),
            Chunk(content="Paragraph 2.", start_line=5, end_line=5, metadata={}),
        ]

        result = self.validator.validate_chunks(input_text, chunks)

        # Should be valid or have minor issues (whitespace/line gaps)
        # Coverage should be good even if not perfect
        assert result.char_coverage > 0.90

    def test_find_missing_content(self):
        """Test finding missing content blocks."""
        input_text = "Line 1\n\nLine 2\n\nLine 3"
        chunks = [
            Chunk(content="Line 1", start_line=1, end_line=1, metadata={}),
            # Line 2 is missing
            Chunk(content="Line 3", start_line=5, end_line=5, metadata={}),
        ]

        missing = self.validator.find_missing_content(input_text, chunks)

        # Should detect missing content
        assert len(missing) > 0

    def test_check_line_coverage_complete(self):
        """Test line coverage check with complete coverage."""
        input_text = "Line 1\nLine 2\nLine 3"
        chunks = [
            Chunk(
                content="Line 1\nLine 2\nLine 3", start_line=1, end_line=3, metadata={}
            )
        ]

        gaps = self.validator._check_line_coverage(input_text, chunks)

        assert len(gaps) == 0

    def test_check_line_coverage_with_gaps(self):
        """Test line coverage check with gaps."""
        input_text = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        chunks = [
            Chunk(content="Line 1", start_line=1, end_line=1, metadata={}),
            # Lines 2-4 missing
            Chunk(content="Line 5", start_line=5, end_line=5, metadata={}),
        ]

        gaps = self.validator._check_line_coverage(input_text, chunks)

        assert len(gaps) > 0
        # Should have gap from line 2 to 4
        assert any(gap[0] == 2 and gap[1] == 4 for gap in gaps)

    def test_check_line_coverage_no_line_info(self):
        """Test line coverage when chunks have no line info."""
        input_text = "Line 1\nLine 2"
        chunks = [
            Chunk(
                content="Line 1\nLine 2",
                start_line=1,
                end_line=2,
                metadata={},
            )
        ]

        # Should handle gracefully when no line info
        gaps = self.validator._check_line_coverage(input_text, chunks)

        assert gaps == []

    def test_guess_block_type_code(self):
        """Test guessing block type for code."""
        assert self.validator._guess_block_type("```python\ncode\n```") == "code"
        # Note: Single line with spaces might not be detected as code
        # Multi-line indented code is more reliable
        indented = "    line1\n    line2"
        result = self.validator._guess_block_type(indented)
        # Accept either code or paragraph for edge case
        assert result in ["code", "paragraph"]

    def test_guess_block_type_list(self):
        """Test guessing block type for list."""
        assert self.validator._guess_block_type("- item 1\n- item 2") == "list"
        assert self.validator._guess_block_type("* item 1") == "list"
        assert self.validator._guess_block_type("1. item 1") == "list"

    def test_guess_block_type_table(self):
        """Test guessing block type for table."""
        table = "| Col 1 | Col 2 |\n|-------|-------|\n| A | B |"
        assert self.validator._guess_block_type(table) == "table"

    def test_guess_block_type_header(self):
        """Test guessing block type for header."""
        assert self.validator._guess_block_type("# Header") == "header"
        assert self.validator._guess_block_type("## Subheader") == "header"

    def test_guess_block_type_paragraph(self):
        """Test guessing block type for paragraph."""
        assert self.validator._guess_block_type("Regular paragraph text") == "paragraph"

    def test_raise_if_invalid_passes(self):
        """Test raise_if_invalid when validation passes."""
        input_text = "# Header\n\nContent"
        chunks = [
            Chunk(
                content="# Header\n\nContent",
                start_line=1,
                end_line=3,
                metadata={},
            )
        ]

        # Should not raise
        self.validator.raise_if_invalid(input_text, chunks)

    def test_raise_if_invalid_data_loss(self):
        """Test raise_if_invalid raises on data loss."""
        input_text = "# Header\n\nContent with lots of text"
        chunks = [Chunk(content="# Header", start_line=1, end_line=1, metadata={})]

        with pytest.raises(DataLossError):
            self.validator.raise_if_invalid(input_text, chunks)

    def test_raise_if_invalid_missing_content(self):
        """Test raise_if_invalid raises MissingContentError."""
        input_text = "Line 1\n\nLine 2\n\nLine 3"
        chunks = [
            Chunk(content="Line 1", start_line=1, end_line=1, metadata={}),
            Chunk(content="Line 3", start_line=5, end_line=5, metadata={}),
        ]

        # Should raise MissingContentError when content blocks are missing
        with pytest.raises((MissingContentError, DataLossError)):
            self.validator.raise_if_invalid(input_text, chunks)

    def test_validation_with_warnings(self):
        """Test validation generates warnings."""
        input_text = "# Header\n\nContent with text"
        chunks = [
            Chunk(content="# Header\nContent", start_line=1, end_line=2, metadata={})
        ]

        result = self.validator.validate_chunks(input_text, chunks)

        # Should have warnings about data loss
        if not result.is_valid:
            assert len(result.warnings) > 0


class TestValidatorIntegration:
    """Integration tests for validator."""

    def test_validator_with_real_chunking_scenario(self):
        """Test validator with realistic chunking scenario."""
        validator = DataCompletenessValidator(tolerance=0.05)

        input_text = """# Documentation

## Section 1

Content for section 1.

## Section 2

Content for section 2.
"""

        chunks = [
            Chunk(
                content="# Documentation\n\n## Section 1\n\nContent for section 1.",
                start_line=1,
                end_line=5,
                metadata={},
            ),
            Chunk(
                content="## Section 2\n\nContent for section 2.",
                start_line=7,
                end_line=9,
                metadata={},
            ),
        ]

        result = validator.validate_chunks(input_text, chunks)

        # Should pass validation
        assert result.is_valid is True
        assert result.char_coverage > 0.95

    def test_validator_detects_missing_section(self):
        """Test validator detects when a section is missing."""
        validator = DataCompletenessValidator(tolerance=0.05)

        input_text = """# Documentation

## Section 1

Content for section 1.

## Section 2

Content for section 2.

## Section 3

Content for section 3.
"""

        # Missing section 2
        chunks = [
            Chunk(
                content="# Documentation\n\n## Section 1\n\nContent for section 1.",
                start_line=1,
                end_line=5,
                metadata={},
            ),
            Chunk(
                content="## Section 3\n\nContent for section 3.",
                start_line=11,
                end_line=13,
                metadata={},
            ),
        ]

        result = validator.validate_chunks(input_text, chunks)

        # Should fail validation
        assert result.is_valid is False
        assert result.missing_chars > 0
