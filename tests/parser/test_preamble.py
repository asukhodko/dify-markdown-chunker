"""
Tests for preamble extraction functionality.

Tests the PreambleInfo dataclass and PreambleExtractor class.
"""

import pytest

from markdown_chunker.parser.types import PreambleInfo


class TestPreambleInfo:
    """Tests for PreambleInfo dataclass."""

    def test_create_introduction_preamble(self):
        """Test creating an introduction preamble."""
        preamble = PreambleInfo(
            content="This is an introduction.",
            type="introduction",
            line_count=1,
            char_count=24,
            has_metadata=False,
            metadata_fields={},
        )

        assert preamble.content == "This is an introduction."
        assert preamble.type == "introduction"
        assert preamble.line_count == 1
        assert preamble.char_count == 24
        assert not preamble.has_metadata
        assert preamble.metadata_fields == {}

    def test_create_metadata_preamble(self):
        """Test creating a metadata preamble."""
        preamble = PreambleInfo(
            content="Author: John Doe\nDate: 2025-11-10",
            type="metadata",
            line_count=2,
            char_count=34,
            has_metadata=True,
            metadata_fields={"author": "John Doe", "date": "2025-11-10"},
        )

        assert preamble.type == "metadata"
        assert preamble.has_metadata
        assert preamble.metadata_fields["author"] == "John Doe"
        assert preamble.metadata_fields["date"] == "2025-11-10"

    def test_invalid_type_raises_error(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="type must be one o"):
            PreambleInfo(
                content="Test",
                type="invalid",
                line_count=1,
                char_count=4,
                has_metadata=False,
            )

    def test_negative_line_count_raises_error(self):
        """Test that negative line_count raises ValueError."""
        with pytest.raises(ValueError, match="line_count must be non-negative"):
            PreambleInfo(
                content="Test",
                type="general",
                line_count=-1,
                char_count=4,
                has_metadata=False,
            )

    def test_negative_char_count_raises_error(self):
        """Test that negative char_count raises ValueError."""
        with pytest.raises(ValueError, match="char_count must be non-negative"):
            PreambleInfo(
                content="Test",
                type="general",
                line_count=1,
                char_count=-1,
                has_metadata=False,
            )

    def test_has_metadata_without_fields_raises_error(self):
        """Test that has_metadata=True without fields raises ValueError."""
        with pytest.raises(
            ValueError, match="has_metadata is True but metadata_fields is empty"
        ):
            PreambleInfo(
                content="Test",
                type="metadata",
                line_count=1,
                char_count=4,
                has_metadata=True,
                metadata_fields={},
            )

    def test_to_dict(self):
        """Test converting preamble to dictionary."""
        preamble = PreambleInfo(
            content="Summary of document",
            type="summary",
            line_count=1,
            char_count=19,
            has_metadata=False,
            metadata_fields={},
        )

        result = preamble.to_dict()

        assert result["content"] == "Summary of document"
        assert result["type"] == "summary"
        assert result["line_count"] == 1
        assert result["char_count"] == 19
        assert result["has_metadata"] is False
        assert result["metadata_fields"] == {}

    def test_all_preamble_types(self):
        """Test all valid preamble types."""
        types = ["introduction", "summary", "metadata", "general"]

        for preamble_type in types:
            preamble = PreambleInfo(
                content="Test content",
                type=preamble_type,
                line_count=1,
                char_count=12,
                has_metadata=False,
            )
            assert preamble.type == preamble_type


class TestPreambleExtractor:
    """Tests for PreambleExtractor class."""

    def test_extract_introduction_preamble(self):
        """Test extracting introduction preamble."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """This is an introduction to the document.
It provides context and overview.

# First Header
Content here."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.type == "introduction"
        assert "introduction" in preamble.content.lower()
        assert preamble.line_count == 3  # Includes empty line before header
        assert not preamble.has_metadata

    def test_extract_metadata_preamble(self):
        """Test extracting metadata preamble."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """Author: John Doe
Date: 2025-11-10
Version: 1.0

# Document Title
Content here."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.type == "metadata"
        assert preamble.has_metadata
        assert preamble.metadata_fields["author"] == "John Doe"
        assert preamble.metadata_fields["date"] == "2025-11-10"
        assert preamble.metadata_fields["version"] == "1.0"

    def test_extract_summary_preamble(self):
        """Test extracting summary preamble."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """TL;DR: This document explains the system architecture.

# Architecture
Details here."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.type == "summary"
        assert "tl;dr" in preamble.content.lower()

    def test_no_preamble_starts_with_header(self):
        """Test document starting with header has no preamble."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """# First Header
Content here."""

        preamble = extractor.extract(text)

        assert preamble is None

    def test_no_preamble_empty_document(self):
        """Test empty document has no preamble."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()

        assert extractor.extract("") is None
        assert extractor.extract("   ") is None

    def test_preamble_too_short_ignored(self):
        """Test very short preamble is ignored."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """Short

# Header
Content."""

        preamble = extractor.extract(text)

        assert preamble is None  # Less than 10 chars

    def test_general_preamble_type(self):
        """Test preamble without specific keywords is general."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """This is some content before the first header.
It doesn't match any specific type.

# Header
Content."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.type == "general"

    def test_setext_header_detection(self):
        """Test detection of Setext-style headers."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """This is preamble content.

First Header
============
Content here."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert "preamble content" in preamble.content

    def test_multiple_metadata_fields(self):
        """Test extracting multiple metadata fields."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """Title: My Document
Author: Jane Smith
Date: 2025-11-10
Version: 2.0
Tags: python, markdown, parser

# Introduction
Content."""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.has_metadata
        assert len(preamble.metadata_fields) == 5
        assert preamble.metadata_fields["title"] == "My Document"
        assert preamble.metadata_fields["tags"] == "python, markdown, parser"

    def test_char_and_line_count(self):
        """Test accurate char and line counting."""
        from markdown_chunker.parser.analyzer import PreambleExtractor

        extractor = PreambleExtractor()
        text = """Line 1
Line 2
Line 3

# Header"""

        preamble = extractor.extract(text)

        assert preamble is not None
        assert preamble.line_count == 4  # Includes empty line before header
        assert preamble.char_count == len("Line 1\nLine 2\nLine 3")


class TestContentAnalysisWithPreamble:
    """Tests for ContentAnalysis with preamble field."""

    def test_content_analysis_with_preamble(self):
        """Test ContentAnalysis includes preamble."""
        from markdown_chunker.parser.types import ContentAnalysis, PreambleInfo

        preamble = PreambleInfo(
            content="Test preamble",
            type="introduction",
            line_count=1,
            char_count=13,
            has_metadata=False,
        )

        analysis = ContentAnalysis(
            total_chars=100,
            total_lines=10,
            total_words=20,
            code_ratio=0.3,
            text_ratio=0.7,
            code_block_count=1,
            header_count=2,
            content_type="text_heavy",
            preamble=preamble,
        )

        assert analysis.preamble is not None
        assert analysis.preamble.type == "introduction"

    def test_content_analysis_without_preamble(self):
        """Test ContentAnalysis without preamble."""
        from markdown_chunker.parser.types import ContentAnalysis

        analysis = ContentAnalysis(
            total_chars=100,
            total_lines=10,
            total_words=20,
            code_ratio=0.3,
            text_ratio=0.7,
            code_block_count=1,
            header_count=2,
            content_type="text_heavy",
        )

        assert analysis.preamble is None

    def test_get_summary_includes_preamble(self):
        """Test get_summary includes preamble."""
        from markdown_chunker.parser.types import ContentAnalysis, PreambleInfo

        preamble = PreambleInfo(
            content="Summary text",
            type="summary",
            line_count=1,
            char_count=12,
            has_metadata=False,
        )

        analysis = ContentAnalysis(
            total_chars=100,
            total_lines=10,
            total_words=20,
            code_ratio=0.3,
            text_ratio=0.7,
            code_block_count=1,
            header_count=2,
            content_type="text_heavy",
            preamble=preamble,
        )

        summary = analysis.get_summary()

        assert "preamble" in summary
        assert summary["preamble"] is not None
        assert summary["preamble"]["type"] == "summary"


class TestContentAnalyzerIntegration:
    """Tests for ContentAnalyzer integration with preamble."""

    def test_analyze_content_extracts_preamble(self):
        """Test that analyze_content extracts preamble."""
        from markdown_chunker.parser.analyzer import ContentAnalyzer

        analyzer = ContentAnalyzer()
        text = """This is an introduction to the document.

# First Header
Content here."""

        analysis = analyzer.analyze_content(text)

        assert analysis.preamble is not None
        assert analysis.preamble.type == "introduction"
        assert "introduction" in analysis.preamble.content.lower()

    def test_analyze_content_no_preamble(self):
        """Test analyze_content with no preamble."""
        from markdown_chunker.parser.analyzer import ContentAnalyzer

        analyzer = ContentAnalyzer()
        text = """# First Header
Content here."""

        analysis = analyzer.analyze_content(text)

        assert analysis.preamble is None

    def test_analyze_content_with_metadata_preamble(self):
        """Test analyze_content extracts metadata preamble."""
        from markdown_chunker.parser.analyzer import ContentAnalyzer

        analyzer = ContentAnalyzer()
        text = """Author: John Doe
Date: 2025-11-10

# Document
Content."""

        analysis = analyzer.analyze_content(text)

        assert analysis.preamble is not None
        assert analysis.preamble.type == "metadata"
        assert analysis.preamble.has_metadata
        assert "author" in analysis.preamble.metadata_fields

    def test_get_summary_includes_preamble_from_analyzer(self):
        """Test get_summary includes preamble from analyzer."""
        from markdown_chunker.parser.analyzer import ContentAnalyzer

        analyzer = ContentAnalyzer()
        text = """Summary: This is a test document.

# Header
Content."""

        analysis = analyzer.analyze_content(text)
        summary = analysis.get_summary()

        assert "preamble" in summary
        assert summary["preamble"] is not None
        assert summary["preamble"]["type"] == "summary"
