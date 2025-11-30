"""
Comprehensive tests for ErrorCollector (NEW CODE).

These tests specifically target the NEW ErrorCollector in errors.py.
"""

from markdown_chunker.parser.errors import (
    ErrorCollector,
    ErrorInfo,
    ErrorSeverity,
    ErrorSummary,
    SourceLocation,
    WarningInfo,
    create_source_location,
)
from markdown_chunker.parser.types import Position


class TestErrorCollectorNew:
    """Test ErrorCollector from errors.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that ErrorCollector can be instantiated."""
        collector = ErrorCollector()
        assert collector is not None
        assert hasattr(collector, "add_error")
        assert hasattr(collector, "add_warning")

    def test_add_error(self):
        """Test adding an error."""
        collector = ErrorCollector()
        collector.add_error("Test error", category="test")

        assert collector.has_errors() is True
        assert len(collector.get_errors()) == 1
        assert collector.get_errors()[0].message == "Test error"

    def test_add_warning(self):
        """Test adding a warning."""
        collector = ErrorCollector()
        collector.add_warning("Test warning", category="test")

        assert collector.has_warnings() is True
        assert len(collector.get_warnings()) == 1
        assert collector.get_warnings()[0].message == "Test warning"

    def test_add_critical_error(self):
        """Test adding a critical error."""
        collector = ErrorCollector()
        collector.add_critical_error("Critical error", category="test")

        assert collector.has_critical_errors() is True
        assert len(collector.get_critical_errors()) == 1

    def test_has_errors_initially_false(self):
        """Test that has_errors is initially False."""
        collector = ErrorCollector()
        assert collector.has_errors() is False

    def test_has_warnings_initially_false(self):
        """Test that has_warnings is initially False."""
        collector = ErrorCollector()
        assert collector.has_warnings() is False

    def test_get_summary(self):
        """Test getting error summary."""
        collector = ErrorCollector()
        collector.add_error("Error 1")
        collector.add_error("Error 2")
        collector.add_warning("Warning 1")

        summary = collector.get_summary()

        assert summary.error_count == 2
        assert summary.warning_count == 1
        assert summary.get_total_issues() == 3

    def test_clear(self):
        """Test clearing errors and warnings."""
        collector = ErrorCollector()
        collector.add_error("Error")
        collector.add_warning("Warning")

        assert collector.has_errors() is True
        assert collector.has_warnings() is True

        collector.clear()

        assert collector.has_errors() is False
        assert collector.has_warnings() is False

    def test_format_report(self):
        """Test formatting error report."""
        collector = ErrorCollector()
        collector.add_error("Error 1", category="parsing")
        collector.add_warning("Warning 1", category="validation")

        report = collector.format_report()

        assert "ERROR REPORT" in report
        assert "Error 1" in report
        assert "Warning 1" in report


class TestSourceLocationNew:
    """Test SourceLocation dataclass."""

    def test_source_location_creation(self):
        """Test creating SourceLocation."""
        location = SourceLocation(line=10, column=5, offset=100)

        assert location.line == 10
        assert location.column == 5
        assert location.offset == 100

    def test_source_location_with_filename(self):
        """Test SourceLocation with filename."""
        location = SourceLocation(line=10, column=5, file_name="test.md")

        assert location.file_name == "test.md"
        assert "test.md" in str(location)

    def test_source_location_str(self):
        """Test SourceLocation string representation."""
        location = SourceLocation(line=10, column=5)

        str_repr = str(location)
        assert "10" in str_repr
        assert "5" in str_repr

    def test_create_source_location_from_position(self):
        """Test creating SourceLocation from Position."""
        position = Position(line=10, column=5, offset=100)
        location = create_source_location(position)

        assert location.line == 10
        assert location.column == 5
        assert location.offset == 100


class TestErrorInfoNew:
    """Test ErrorInfo dataclass."""

    def test_error_info_creation(self):
        """Test creating ErrorInfo."""
        location = SourceLocation(line=10, column=5)
        error = ErrorInfo(
            severity=ErrorSeverity.ERROR,
            message="Test error",
            category="test",
            location=location,
        )

        assert error.severity == ErrorSeverity.ERROR
        assert error.message == "Test error"
        assert error.category == "test"
        assert error.location == location

    def test_error_info_str(self):
        """Test ErrorInfo string representation."""
        error = ErrorInfo(
            severity=ErrorSeverity.ERROR, message="Test error", category="test"
        )

        str_repr = str(error)
        assert "ERROR" in str_repr
        assert "Test error" in str_repr


class TestWarningInfoNew:
    """Test WarningInfo dataclass."""

    def test_warning_info_creation(self):
        """Test creating WarningInfo."""
        warning = WarningInfo(message="Test warning", category="test")

        assert warning.message == "Test warning"
        assert warning.category == "test"

    def test_warning_info_str(self):
        """Test WarningInfo string representation."""
        warning = WarningInfo(message="Test warning", category="test")

        str_repr = str(warning)
        assert "WARNING" in str_repr
        assert "Test warning" in str_repr


class TestErrorSummaryNew:
    """Test ErrorSummary dataclass."""

    def test_error_summary_creation(self):
        """Test creating ErrorSummary."""
        summary = ErrorSummary(
            error_count=2, warning_count=1, info_count=0, critical_count=0
        )

        assert summary.error_count == 2
        assert summary.warning_count == 1

    def test_error_summary_has_errors(self):
        """Test has_errors method."""
        summary = ErrorSummary(
            error_count=1, warning_count=0, info_count=0, critical_count=0
        )

        assert summary.has_errors() is True

    def test_error_summary_has_warnings(self):
        """Test has_warnings method."""
        summary = ErrorSummary(
            error_count=0, warning_count=1, info_count=0, critical_count=0
        )

        assert summary.has_warnings() is True

    def test_error_summary_has_critical_errors(self):
        """Test has_critical_errors method."""
        summary = ErrorSummary(
            error_count=0, warning_count=0, info_count=0, critical_count=1
        )

        assert summary.has_critical_errors() is True

    def test_error_summary_get_total_issues(self):
        """Test get_total_issues method."""
        summary = ErrorSummary(
            error_count=2, warning_count=3, info_count=1, critical_count=1
        )

        assert summary.get_total_issues() == 7


class TestErrorCollectorIntegration:
    """Integration tests for ErrorCollector."""

    def test_full_workflow(self):
        """Test complete error collection workflow."""
        collector = ErrorCollector()

        # Add various issues
        collector.add_error("Error 1", category="parsing")
        collector.add_error("Error 2", category="validation")
        collector.add_warning("Warning 1", category="parsing")
        collector.add_critical_error("Critical", category="fatal")

        # Check summary
        summary = collector.get_summary()
        assert summary.error_count == 2
        assert summary.warning_count == 1
        assert summary.critical_count == 1
        assert summary.get_total_issues() == 4

        # Check categories
        assert "parsing" in summary.categories
        assert "validation" in summary.categories
        assert "fatal" in summary.categories

    def test_error_with_location(self):
        """Test adding error with location."""
        collector = ErrorCollector()
        location = SourceLocation(line=10, column=5, file_name="test.md")

        collector.add_error(
            "Error at location",
            category="parsing",
            location=location,
            details="Additional details",
        )

        errors = collector.get_errors()
        assert len(errors) == 1
        assert errors[0].location == location
        assert errors[0].details == "Additional details"

    def test_multiple_categories(self):
        """Test errors from multiple categories."""
        collector = ErrorCollector()

        collector.add_error("Parse error", category="parsing")
        collector.add_error("Validation error", category="validation")
        collector.add_warning("Style warning", category="style")

        summary = collector.get_summary()
        assert len(summary.categories) == 3
        assert summary.categories["parsing"] == 1
        assert summary.categories["validation"] == 1
        assert summary.categories["style"] == 1
