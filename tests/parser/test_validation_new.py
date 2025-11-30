"""
Comprehensive tests for parser.validation module (NEW CODE).

These tests specifically target the NEW refactored code in validation.py,
testing InputValidator and Stage1APIValidator.
"""

import pytest

from markdown_chunker.parser.validation import (
    APIValidator,
    InputValidator,
    Stage1APIValidator,
    normalize_line_endings,
    validate_and_normalize_input,
    validate_stage1_result,
)


class TestInputValidatorNew:
    """Test InputValidator from validation.py (NEW CODE)."""

    def test_validate_and_normalize_string(self):
        """Test validating and normalizing a string."""
        result = InputValidator.validate_and_normalize("test content")
        assert result == "test content"

    def test_validate_and_normalize_none(self):
        """Test validating None returns empty string."""
        result = InputValidator.validate_and_normalize(None)
        assert result == ""

    def test_validate_and_normalize_invalid_type(self):
        """Test validating invalid type raises TypeError."""
        with pytest.raises(TypeError):
            InputValidator.validate_and_normalize(123)

    def test_normalize_line_endings_crlf(self):
        """Test normalizing Windows CRLF line endings."""
        text = "line1\r\nline2\r\nline3"
        result = InputValidator.normalize_line_endings(text)
        assert result == "line1\nline2\nline3"
        assert "\r\n" not in result

    def test_normalize_line_endings_cr(self):
        """Test normalizing old Mac CR line endings."""
        text = "line1\rline2\rline3"
        result = InputValidator.normalize_line_endings(text)
        assert result == "line1\nline2\nline3"
        assert "\r" not in result

    def test_normalize_line_endings_mixed(self):
        """Test normalizing mixed line endings."""
        text = "line1\r\nline2\rline3\nline4"
        result = InputValidator.normalize_line_endings(text)
        assert result == "line1\nline2\nline3\nline4"

    def test_validate_non_empty_true(self):
        """Test validate_non_empty with non-empty text."""
        assert InputValidator.validate_non_empty("content") is True
        assert InputValidator.validate_non_empty("  content  ") is True

    def test_validate_non_empty_false(self):
        """Test validate_non_empty with empty text."""
        assert InputValidator.validate_non_empty("") is False
        assert InputValidator.validate_non_empty("   ") is False

    def test_get_line_count(self):
        """Test getting line count."""
        assert InputValidator.get_line_count("") == 0
        assert InputValidator.get_line_count("single line") == 1
        assert InputValidator.get_line_count("line1\nline2\nline3") == 3

    def test_validate_encoding_valid(self):
        """Test validating valid UTF-8 encoding."""
        assert InputValidator.validate_encoding("Hello world") is True
        assert InputValidator.validate_encoding("Привет мир 🌍") is True

    def test_convenience_function_validate_and_normalize(self):
        """Test convenience function validate_and_normalize_input."""
        result = validate_and_normalize_input("test\r\ncontent")
        assert result == "test\ncontent"

    def test_convenience_function_normalize_line_endings(self):
        """Test convenience function normalize_line_endings."""
        result = normalize_line_endings("test\r\ncontent")
        assert result == "test\ncontent"


class TestStage1APIValidatorNew:
    """Test Stage1APIValidator from validation.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that Stage1APIValidator can be instantiated."""
        validator = Stage1APIValidator()
        assert validator is not None
        assert hasattr(validator, "validate_process_document_result")

    def test_api_validator_alias(self):
        """Test that APIValidator is an alias."""
        assert APIValidator is Stage1APIValidator

    def test_validate_process_document_result_basic(self):
        """Test basic validation of Stage1Results."""
        # This test requires a mock Stage1Results object
        # For now, just test that the method exists
        validator = Stage1APIValidator()
        assert hasattr(validator, "validate_process_document_result")

    def test_validator_has_required_methods(self):
        """Test that validator has all required methods."""
        validator = Stage1APIValidator()
        assert hasattr(validator, "_validate_ast_structure")
        assert hasattr(validator, "_validate_element_counts")
        assert hasattr(validator, "_validate_content_analysis")
        assert hasattr(validator, "_validate_fenced_blocks")
        assert hasattr(validator, "_cross_validate_components")


class TestInputValidatorEdgeCases:
    """Test edge cases for InputValidator."""

    def test_empty_string(self):
        """Test with empty string."""
        result = InputValidator.validate_and_normalize("")
        assert result == ""

    def test_whitespace_only(self):
        """Test with whitespace only."""
        result = InputValidator.validate_and_normalize("   \t\n  ")
        assert result == "   \t\n  "  # Whitespace is preserved

    def test_very_long_text(self):
        """Test with very long text."""
        long_text = "x" * 100000
        result = InputValidator.validate_and_normalize(long_text)
        assert len(result) == 100000

    def test_unicode_characters(self):
        """Test with various unicode characters."""
        text = "Hello 世界 🌍 Привет مرحبا"
        result = InputValidator.validate_and_normalize(text)
        assert result == text

    def test_special_characters(self):
        """Test with special characters."""
        text = "Test <>&\"'`~!@#$%^&*()"
        result = InputValidator.validate_and_normalize(text)
        assert result == text

    def test_multiple_line_ending_types(self):
        """Test text with multiple types of line endings."""
        text = "line1\r\nline2\rline3\nline4"
        result = InputValidator.validate_and_normalize(text)
        # All should be normalized to \n
        assert result.count("\r") == 0
        assert result.count("\n") == 3


class TestConvenienceFunctionsNew:
    """Test convenience functions from validation.py."""

    def test_validate_and_normalize_input_function(self):
        """Test validate_and_normalize_input function."""
        result = validate_and_normalize_input("test")
        assert result == "test"

    def test_validate_and_normalize_input_with_none(self):
        """Test validate_and_normalize_input with None."""
        result = validate_and_normalize_input(None)
        assert result == ""

    def test_normalize_line_endings_function(self):
        """Test normalize_line_endings function."""
        result = normalize_line_endings("test\r\nline")
        assert result == "test\nline"

    def test_validate_stage1_result_function_exists(self):
        """Test that validate_stage1_result function exists."""
        assert callable(validate_stage1_result)


class TestInputValidatorIntegration:
    """Integration tests for InputValidator."""

    def test_full_workflow(self):
        """Test complete validation and normalization workflow."""
        # Start with problematic input
        input_text = "Line 1\r\nLine 2\rLine 3\nLine 4"

        # Validate and normalize
        result = InputValidator.validate_and_normalize(input_text)

        # Check results
        assert InputValidator.validate_non_empty(result)
        assert InputValidator.validate_encoding(result)
        assert InputValidator.get_line_count(result) == 4
        assert "\r" not in result

    def test_markdown_document_validation(self):
        """Test validating a markdown document."""
        md_text = """# Header\r\n\r\nParagraph text.\r\n\r\n```python\r\ncode\r\n```"""

        result = InputValidator.validate_and_normalize(md_text)

        assert "# Header" in result
        assert "```python" in result
        assert "\r\n" not in result
        assert result.count("\n") > 0
