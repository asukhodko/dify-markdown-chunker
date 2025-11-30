"""
Tests for PreambleExtractor.

Basic unit tests for preamble extraction functionality.
More comprehensive tests will be added in task 2.4.
"""

from markdown_chunker.parser.preamble import (
    PreambleExtractor,
    PreambleInfo,
    PreambleType,
    extract_preamble,
)


class TestPreambleType:
    """Test PreambleType enum."""

    def test_enum_values(self):
        """Test that all enum values are defined."""
        assert PreambleType.INTRODUCTION.value == "introduction"
        assert PreambleType.SUMMARY.value == "summary"
        assert PreambleType.METADATA.value == "metadata"
        assert PreambleType.GENERAL.value == "general"


class TestPreambleInfo:
    """Test PreambleInfo dataclass."""

    def test_creation(self):
        """Test creating PreambleInfo."""
        info = PreambleInfo(
            type=PreambleType.METADATA,
            content="Author: John",
            start_line=1,
            end_line=1,
            line_count=1,
            char_count=12,
            has_metadata=True,
            metadata_fields={"author": "John"},
        )

        assert info.type == PreambleType.METADATA
        assert info.content == "Author: John"
        assert info.start_line == 1
        assert info.end_line == 1
        assert info.line_count == 1
        assert info.char_count == 12
        assert info.has_metadata is True
        assert info.metadata_fields == {"author": "John"}

    def test_to_dict(self):
        """Test serialization to dict."""
        info = PreambleInfo(
            type=PreambleType.INTRODUCTION,
            content="Welcome",
            start_line=1,
            end_line=2,
            line_count=2,
            char_count=7,
        )

        result = info.to_dict()

        assert result["type"] == "introduction"
        assert result["content"] == "Welcome"
        assert result["start_line"] == 1
        assert result["end_line"] == 2
        assert result["line_count"] == 2
        assert result["char_count"] == 7
        assert result["has_metadata"] is False
        assert result["metadata_fields"] == {}


class TestPreambleExtractor:
    """Test PreambleExtractor class."""

    def test_initialization(self):
        """Test extractor initialization."""
        extractor = PreambleExtractor()
        assert extractor.min_lines == 2
        assert extractor.min_chars == 50

        extractor = PreambleExtractor(min_lines=3, min_chars=100)
        assert extractor.min_lines == 3
        assert extractor.min_chars == 100

    def test_extract_metadata_preamble(self):
        """Test extracting metadata preamble."""
        text = "Author: John Doe\nDate: 2025-11-16\nVersion: 1.0\nStatus: Draft\n\n# Title\n\nContent here."

        extractor = PreambleExtractor(min_lines=2, min_chars=30)
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert preamble.type == PreambleType.METADATA
        assert preamble.start_line == 1
        assert preamble.has_metadata is True
        assert "author" in preamble.metadata_fields
        assert preamble.metadata_fields["author"] == "John Doe"
        assert preamble.metadata_fields["date"] == "2025-11-16"
        assert preamble.metadata_fields["version"] == "1.0"

    def test_extract_introduction_preamble(self):
        """Test extracting introduction preamble."""
        text = """This is an introduction to the document.
It provides an overview of what you'll find here.

# Chapter 1

Content starts here."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert preamble.type == PreambleType.INTRODUCTION
        assert "introduction" in preamble.content.lower()

    def test_extract_summary_preamble(self):
        """Test extracting summary preamble."""
        text = """TL;DR: This document explains the markdown chunking algorithm
in detail with examples and best practices.

# Introduction

Full content here."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert preamble.type == PreambleType.SUMMARY
        assert "tl;dr" in preamble.content.lower()

    def test_extract_general_preamble(self):
        """Test extracting general preamble."""
        text = """This is some content before the first header.
It doesn't match any specific pattern.

# First Header

Main content."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert preamble.type == PreambleType.GENERAL

    def test_no_preamble_starts_with_header(self):
        """Test document starting with header has no preamble."""
        text = """# Title

Content here."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is None

    def test_no_preamble_empty_document(self):
        """Test empty document has no preamble."""
        extractor = PreambleExtractor()

        assert extractor.extract_preamble("") is None
        assert extractor.extract_preamble("   ") is None
        assert extractor.extract_preamble("\n\n") is None

    def test_preamble_too_short_ignored(self):
        """Test preamble below minimum thresholds is ignored."""
        text = """Short

# Title

Content."""

        extractor = PreambleExtractor(min_lines=2, min_chars=50)
        preamble = extractor.extract_preamble(text)

        # Too few characters
        assert preamble is None

    def test_setext_header_detection(self):
        """Test detection of Setext-style headers."""
        text = """This is a preamble before the header.
It has enough content to be valid.

Title
=====

Content here."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert "preamble" in preamble.content.lower()

    def test_detect_preamble_type_metadata(self):
        """Test type detection for metadata."""
        extractor = PreambleExtractor()

        text = "Author: John\nDate: 2025"
        assert extractor.detect_preamble_type(text) == PreambleType.METADATA

    def test_detect_preamble_type_summary(self):
        """Test type detection for summary."""
        extractor = PreambleExtractor()

        text = "TL;DR: This is a summary of the document"
        assert extractor.detect_preamble_type(text) == PreambleType.SUMMARY

        text = "Abstract: This document describes..."
        assert extractor.detect_preamble_type(text) == PreambleType.SUMMARY

    def test_detect_preamble_type_introduction(self):
        """Test type detection for introduction."""
        extractor = PreambleExtractor()

        text = "This introduction explains the purpose"
        assert extractor.detect_preamble_type(text) == PreambleType.INTRODUCTION

        text = "Welcome to this overview of the system"
        assert extractor.detect_preamble_type(text) == PreambleType.INTRODUCTION

    def test_detect_preamble_type_general(self):
        """Test type detection for general content."""
        extractor = PreambleExtractor()

        text = "Some random content without keywords"
        assert extractor.detect_preamble_type(text) == PreambleType.GENERAL

    def test_extract_metadata_fields(self):
        """Test metadata field extraction."""
        extractor = PreambleExtractor()

        text = """Author: John Doe
Date: 2025-11-16
Version: 1.0.0
Title: My Document
Tags: python, markdown"""

        fields = extractor.extract_metadata_fields(text)

        assert len(fields) == 5
        assert fields["author"] == "John Doe"
        assert fields["date"] == "2025-11-16"
        assert fields["version"] == "1.0.0"
        assert fields["title"] == "My Document"
        assert fields["tags"] == "python, markdown"

    def test_extract_metadata_fields_case_insensitive(self):
        """Test metadata extraction is case-insensitive."""
        extractor = PreambleExtractor()

        text = """AUTHOR: John
Date: 2025
version: 1.0"""

        fields = extractor.extract_metadata_fields(text)

        assert fields["author"] == "John"
        assert fields["date"] == "2025"
        assert fields["version"] == "1.0"

    def test_extract_metadata_fields_empty(self):
        """Test metadata extraction with no metadata."""
        extractor = PreambleExtractor()

        text = "Just some regular text without metadata"
        fields = extractor.extract_metadata_fields(text)

        assert len(fields) == 0

    def test_find_first_header_atx(self):
        """Test finding ATX-style headers."""
        extractor = PreambleExtractor()

        lines = ["Preamble", "", "# Header", "Content"]
        assert extractor._find_first_header(lines) == 2

        lines = ["Preamble", "## Header 2", "Content"]
        assert extractor._find_first_header(lines) == 1

    def test_find_first_header_setext(self):
        """Test finding Setext-style headers."""
        extractor = PreambleExtractor()

        lines = ["Preamble", "", "Header", "====", "Content"]
        assert extractor._find_first_header(lines) == 2

        lines = ["Preamble", "Header", "----", "Content"]
        assert extractor._find_first_header(lines) == 1

    def test_find_first_header_none(self):
        """Test when no header is found."""
        extractor = PreambleExtractor()

        lines = ["Just", "some", "text"]
        assert extractor._find_first_header(lines) is None

    def test_has_metadata_pattern(self):
        """Test metadata pattern detection."""
        extractor = PreambleExtractor()

        assert extractor._has_metadata_pattern("Author: John") is True
        assert extractor._has_metadata_pattern("Date: 2025") is True
        assert extractor._has_metadata_pattern("Version: 1.0") is True
        assert extractor._has_metadata_pattern("Just text") is False
        assert extractor._has_metadata_pattern("") is False


class TestConvenienceFunction:
    """Test convenience function."""

    def test_extract_preamble_function(self):
        """Test convenience function works."""
        text = "Author: John Doe\nDate: 2025-11-16\nVersion: 1.0\n\n# Title\n\nContent."

        preamble = extract_preamble(text, min_chars=30)

        assert preamble is not None
        assert preamble.type == PreambleType.METADATA

    def test_extract_preamble_with_custom_params(self):
        """Test convenience function with custom parameters."""
        text = """Short text

# Title

Content."""

        # Should fail with default params
        preamble = extract_preamble(text)
        assert preamble is None

        # Should succeed with relaxed params
        preamble = extract_preamble(text, min_lines=1, min_chars=5)
        assert preamble is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_multiple_headers_uses_first(self):
        """Test that only content before first header is extracted."""
        text = """Preamble content here.
This is before any headers.

# First Header

Some content.

## Second Header

More content."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert "First Header" not in preamble.content
        assert "Second Header" not in preamble.content

    def test_empty_lines_in_preamble(self):
        """Test preamble with empty lines."""
        text = """First line of preamble.

Second line after empty line.

# Header

Content."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert preamble.line_count == 4  # Including empty lines

    def test_unicode_content(self):
        """Test preamble with Unicode characters."""
        text = """Автор: Иван Иванов
Дата: 2025-11-16
Описание: Документ с Unicode символами 中文

# Заголовок

Контент."""

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        # Should still detect as metadata despite Cyrillic
        # (pattern matches English keys)

    def test_mixed_header_types(self):
        """Test document with both ATX and Setext headers."""
        text = "Preamble here with enough content to pass minimum requirements.\n\n# ATX Header\n\nContent.\n\nSetext Header\n=============\n\nMore content."

        extractor = PreambleExtractor()
        preamble = extractor.extract_preamble(text)

        assert preamble is not None
        assert "ATX Header" not in preamble.content
