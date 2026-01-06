"""Unit tests for InputValidator component.

Tests validation and default value handling for library output.
"""

import pytest

from input_validator import InputValidator


class TestInputValidator:
    """Tests for InputValidator class."""

    def test_missing_is_leaf_defaults_to_true(self):
        """Missing is_leaf field defaults to True."""
        chunks = [{"content": "test", "metadata": {}}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["metadata"]["is_leaf"] is True

    def test_missing_is_root_defaults_to_false(self):
        """Missing is_root field defaults to False."""
        chunks = [{"content": "test", "metadata": {}}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["metadata"]["is_root"] is False

    def test_existing_is_leaf_not_changed(self):
        """Existing is_leaf value is preserved."""
        chunks = [{"content": "test", "metadata": {"is_leaf": False}}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["metadata"]["is_leaf"] is False

    def test_existing_is_root_not_changed(self):
        """Existing is_root value is preserved."""
        chunks = [{"content": "test", "metadata": {"is_root": True}}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["metadata"]["is_root"] is True

    def test_empty_chunks_list(self):
        """Empty list returns empty list."""
        validator = InputValidator()
        result = validator.validate_and_fix([])

        assert result == []

    def test_multiple_chunks_validated(self):
        """All chunks in list are validated."""
        chunks = [
            {"content": "chunk1", "metadata": {}},
            {"content": "chunk2", "metadata": {}},
            {"content": "chunk3", "metadata": {}},
        ]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert len(result) == 3
        for chunk in result:
            assert "is_leaf" in chunk["metadata"]
            assert "is_root" in chunk["metadata"]

    def test_missing_metadata_key(self):
        """Chunk without metadata key gets metadata dict."""
        chunks = [{"content": "test"}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert "metadata" in result[0]
        assert result[0]["metadata"]["is_leaf"] is True
        assert result[0]["metadata"]["is_root"] is False

    def test_other_metadata_preserved(self):
        """Other metadata fields are preserved."""
        chunks = [
            {
                "content": "test",
                "metadata": {
                    "header_path": "/Section",
                    "content_type": "code",
                },
            }
        ]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["metadata"]["header_path"] == "/Section"
        assert result[0]["metadata"]["content_type"] == "code"
        assert result[0]["metadata"]["is_leaf"] is True
        assert result[0]["metadata"]["is_root"] is False

    def test_content_preserved(self):
        """Chunk content is not modified."""
        chunks = [{"content": "original content", "metadata": {}}]

        validator = InputValidator()
        result = validator.validate_and_fix(chunks)

        assert result[0]["content"] == "original content"
