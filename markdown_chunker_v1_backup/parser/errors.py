"""
Error handling and safe functions for Stage 1.

This module provides error handling, logging, and safe wrapper functions
for all Stage 1 components.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .types import ContentAnalysis, ElementCollection, FencedBlock, MarkdownNode


class ErrorSeverity(Enum):
    """Severity levels for processing errors."""

    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ProcessingError:
    """Represents a processing error with context."""

    severity: ErrorSeverity
    component: str  # "parser", "extractor", "detector", "analyzer"
    message: str
    details: Optional[str] = None
    line_number: Optional[int] = None

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [
            f"[{self.severity.value.upper()}]",
            f"({self.component})",
            self.message,
        ]

        if self.line_number is not None:
            parts.append(f"at line {self.line_number}")

        if self.details:
            parts.append(f"- {self.details}")

        return " ".join(parts)


class MarkdownParsingError(Exception):
    """Base exception for Markdown parsing errors."""

    def __init__(
        self,
        message: str,
        component: str = "unknown",
        line_number: Optional[int] = None,
    ):
        super().__init__(message)
        self.component = component
        self.line_number = line_number


class FencedBlockError(MarkdownParsingError):
    """Errors in fenced block extraction."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        super().__init__(message, "extractor", line_number)


class ParserSelectionError(MarkdownParsingError):
    """Errors in parser selection."""

    def __init__(self, message: str):
        super().__init__(message, "parser")


class ElementDetectionError(MarkdownParsingError):
    """Errors in element detection."""

    def __init__(self, message: str, line_number: Optional[int] = None):
        super().__init__(message, "detector", line_number)


class ContentAnalysisError(MarkdownParsingError):
    """Errors in content analysis."""

    def __init__(self, message: str):
        super().__init__(message, "analyzer")


# Configure logging
logger = logging.getLogger(__name__)


def safe_parse_to_ast(
    md_text: str, parser_type: str = "auto"
) -> Optional[MarkdownNode]:
    """Safely parse Markdown to AST with error handling."""
    try:
        from .markdown_ast import parse_to_ast

        return parse_to_ast(md_text, parser_type)
    except Exception as e:
        logger.error(f"AST parsing failed: {e}")
        return None


def safe_extract_fenced_blocks(md_text: str) -> List[FencedBlock]:
    """Safely extract fenced blocks with error handling."""
    try:
        from .core import extract_fenced_blocks

        return extract_fenced_blocks(md_text)
    except Exception as e:
        logger.error(f"Fenced block extraction failed: {e}")
        return []


def safe_detect_elements(md_text: str) -> Optional[ElementCollection]:
    """Safely detect elements with error handling."""
    try:
        from .elements import detect_elements

        return detect_elements(md_text)
    except Exception as e:
        logger.error(f"Element detection failed: {e}")
        return None


def safe_analyze_content(md_text: str) -> Optional[ContentAnalysis]:
    """Safely analyze content with error handling."""
    try:
        from .analyzer import analyze_content

        return analyze_content(md_text)
    except Exception as e:
        logger.error(f"Content analysis failed: {e}")
        return None


def validate_markdown_input(md_text: str) -> List[ProcessingError]:
    """Validate Markdown input and return any issues."""
    errors = []

    if not isinstance(md_text, str):
        errors.append(
            ProcessingError(
                severity=ErrorSeverity.CRITICAL,
                component="validator",
                message="Input must be a string",
                details=f"Got {type(md_text)}",
            )
        )
        return errors

    if len(md_text) == 0:
        errors.append(
            ProcessingError(
                severity=ErrorSeverity.WARNING,
                component="validator",
                message="Input is empty",
            )
        )

    if len(md_text) > 100 * 1024 * 1024:  # 100MB limit
        errors.append(
            ProcessingError(
                severity=ErrorSeverity.ERROR,
                component="validator",
                message="Input exceeds maximum size limit",
                details=f"Size: {len(md_text)} bytes, limit: 100MB",
            )
        )

    # Check for common encoding issues
    try:
        md_text.encode("utf-8")
    except UnicodeEncodeError as e:
        errors.append(
            ProcessingError(
                severity=ErrorSeverity.ERROR,
                component="validator",
                message="Input contains invalid UTF-8 characters",
                details=str(e),
            )
        )

    return errors


def log_processing_error(error: ProcessingError) -> None:
    """Log a processing error with appropriate level."""
    message = str(error)

    if error.severity == ErrorSeverity.WARNING:
        logger.warning(message)
    elif error.severity == ErrorSeverity.ERROR:
        logger.error(message)
    elif error.severity == ErrorSeverity.CRITICAL:
        logger.critical(message)


def create_fallback_ast(md_text: str) -> MarkdownNode:
    """Create a minimal fallback AST when parsing fails."""
    from .types import MarkdownNode, NodeType, Position

    return MarkdownNode(
        type=NodeType.DOCUMENT,
        content=md_text,
        start_pos=Position(line=0, column=0, offset=0),
        end_pos=Position(
            line=len(md_text.split("\n")) - 1, column=0, offset=len(md_text)
        ),
        children=[],
        metadata={"fallback": True, "error": "Parser failed"},
    )


def create_fallback_elements() -> ElementCollection:
    """Create empty element collection as fallback."""
    return ElementCollection()


def create_fallback_analysis(md_text: str) -> ContentAnalysis:
    """Create basic content analysis as fallback."""
    return ContentAnalysis(
        total_chars=len(md_text),
        total_lines=len(md_text.split("\n")),
        total_words=len(md_text.split()),
        code_ratio=0.0,
        text_ratio=1.0,
        code_block_count=0,
        header_count={},  # P1-005: Now Dict[int, int]
        content_type="text_heavy",
        languages={},  # P1-006: Now Dict[str, int]
    )


class SimpleErrorCollector:
    """Simple error collector for basic processing errors."""

    def __init__(self):
        self.errors: List[ProcessingError] = []

    def add_error(self, error: ProcessingError) -> None:
        """Add an error to the collection."""
        self.errors.append(error)
        log_processing_error(error)

    def add_exception(
        self, exception: Exception, component: str, line_number: Optional[int] = None
    ) -> None:
        """Add an exception as an error."""
        severity = (
            ErrorSeverity.CRITICAL
            if isinstance(exception, (MemoryError, SystemError))
            else ErrorSeverity.ERROR
        )

        error = ProcessingError(
            severity=severity,
            component=component,
            message=str(exception),
            details=exception.__class__.__name__,
            line_number=line_number,
        )

        self.add_error(error)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)

    def get_errors_by_severity(self, severity: ErrorSeverity) -> List[ProcessingError]:
        """Get errors by severity level."""
        return [error for error in self.errors if error.severity == severity]

    def get_summary(self) -> Dict[str, int]:
        """Get error summary by severity."""
        summary = {severity.value: 0 for severity in ErrorSeverity}

        for error in self.errors:
            summary[error.severity.value] += 1

        return summary

    def clear(self) -> None:
        """Clear all errors."""
        self.errors.clear()


# Global error collector for the module (uses simple collector)
_simple_error_collector = SimpleErrorCollector()


def get_error_collector() -> SimpleErrorCollector:
    """Get the global error collector."""
    return _simple_error_collector


def reset_error_collector() -> None:
    """Reset the global error collector."""
    global _simple_error_collector
    _simple_error_collector = SimpleErrorCollector()


# Context manager for error handling
class ErrorHandlingContext:
    """Context manager for handling errors in processing."""

    def __init__(self, component: str):
        self.component = component
        self.collector = SimpleErrorCollector()

    def __enter__(self):
        return self.collector

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.collector.add_exception(exc_val, self.component)

        # Don't suppress exceptions
        return False


# ErrorCollector and related classes migrated from error_collector.py

from dataclasses import field  # noqa: E402
from datetime import datetime  # noqa: E402


@dataclass
class SourceLocation:
    """Location in source text where error occurred."""

    line: int
    column: int = 0
    offset: int = 0
    file_name: Optional[str] = None

    def __str__(self) -> str:
        if self.file_name:
            return f"{self.file_name}:{self.line}:{self.column}"
        return f"line {self.line}, column {self.column}"


@dataclass
class ErrorInfo:
    """Information about an error."""

    severity: ErrorSeverity
    message: str
    category: str
    location: Optional[SourceLocation] = None
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        location_str = f" at {self.location}" if self.location else ""
        return (
            f"[{self.severity.value.upper()}] {self.category}: "
            f"{self.message}{location_str}"
        )


@dataclass
class WarningInfo:
    """Information about a warning."""

    message: str
    category: str
    location: Optional[SourceLocation] = None
    details: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)

    def __str__(self) -> str:
        location_str = f" at {self.location}" if self.location else ""
        return f"[WARNING] {self.category}: {self.message}{location_str}"


@dataclass
class ErrorSummary:
    """Summary of collected errors and warnings."""

    error_count: int
    warning_count: int
    info_count: int
    critical_count: int
    errors: List[ErrorInfo] = field(default_factory=list)
    warnings: List[WarningInfo] = field(default_factory=list)
    categories: Dict[str, int] = field(default_factory=dict)

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return self.error_count > 0 or self.critical_count > 0

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return self.warning_count > 0

    def has_critical_errors(self) -> bool:
        """Check if there are critical errors."""
        return self.critical_count > 0

    def get_total_issues(self) -> int:
        """Get total number of issues."""
        return (
            self.error_count
            + self.warning_count
            + self.info_count
            + self.critical_count
        )


class ErrorCollector:
    """
    Enhanced error collector with structured logging.

    Migrated from error_collector.py.
    Provides structured error collection and logging.
    """

    def __init__(self, logger_name: Optional[str] = None):
        """Initialize error collector."""
        self.errors: List[ErrorInfo] = []
        self.warnings: List[WarningInfo] = []
        self.logger = logging.getLogger(logger_name or __name__)

    def add_error(
        self,
        message: str,
        category: str = "general",
        location: Optional[SourceLocation] = None,
        details: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> None:
        """Add an error."""
        error = ErrorInfo(
            severity=ErrorSeverity.ERROR,
            message=message,
            category=category,
            location=location,
            details=details,
            context=context or {},
        )
        self.errors.append(error)
        self.logger.error(str(error))

    def add_warning(
        self,
        message: str,
        category: str = "general",
        location: Optional[SourceLocation] = None,
        details: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> None:
        """Add a warning."""
        warning = WarningInfo(
            message=message,
            category=category,
            location=location,
            details=details,
            context=context or {},
        )
        self.warnings.append(warning)
        self.logger.warning(str(warning))

    def add_critical_error(
        self,
        message: str,
        category: str = "general",
        location: Optional[SourceLocation] = None,
        details: Optional[str] = None,
        context: Optional[Dict] = None,
    ) -> None:
        """Add a critical error."""
        error = ErrorInfo(
            severity=ErrorSeverity.CRITICAL,
            message=message,
            category=category,
            location=location,
            details=details,
            context=context or {},
        )
        self.errors.append(error)
        self.logger.critical(str(error))

    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return any(
            e.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
            for e in self.errors
        )

    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0

    def has_critical_errors(self) -> bool:
        """Check if there are critical errors."""
        return any(e.severity == ErrorSeverity.CRITICAL for e in self.errors)

    def get_errors(self) -> List[ErrorInfo]:
        """Get all error-level issues."""
        return [
            e
            for e in self.errors
            if e.severity in [ErrorSeverity.ERROR, ErrorSeverity.CRITICAL]
        ]

    def get_warnings(self) -> List[WarningInfo]:
        """Get all warnings."""
        return self.warnings

    def get_critical_errors(self) -> List[ErrorInfo]:
        """Get critical errors only."""
        return [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]

    def get_summary(self) -> ErrorSummary:
        """Get summary of all collected issues."""
        error_count = len([e for e in self.errors if e.severity == ErrorSeverity.ERROR])
        critical_count = len(
            [e for e in self.errors if e.severity == ErrorSeverity.CRITICAL]
        )
        warning_count = len(self.warnings)
        info_count = 0  # Not tracking info separately in simplified version

        # Count by category
        categories: Dict[str, int] = {}
        for error in self.errors:
            categories[error.category] = categories.get(error.category, 0) + 1
        for warning in self.warnings:
            categories[warning.category] = categories.get(warning.category, 0) + 1

        return ErrorSummary(
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            critical_count=critical_count,
            errors=self.get_errors(),
            warnings=self.warnings,
            categories=categories,
        )

    def clear(self) -> None:
        """Clear all collected errors and warnings."""
        self.errors.clear()
        self.warnings.clear()

    def format_report(self, include_details: bool = True) -> str:  # noqa: C901
        """Format a comprehensive error report."""
        # Complexity justified: Formats detailed report with multiple sections
        summary = self.get_summary()
        lines = []

        lines.append("=" * 60)
        lines.append("ERROR REPORT")
        lines.append("=" * 60)
        lines.append(f"Total Issues: {summary.get_total_issues()}")
        lines.append(f"  Errors: {summary.error_count}")
        lines.append(f"  Warnings: {summary.warning_count}")
        lines.append(f"  Critical: {summary.critical_count}")
        lines.append("")

        if summary.categories:
            lines.append("Issues by Category:")
            for category, count in sorted(summary.categories.items()):
                lines.append(f"  {category}: {count}")
            lines.append("")

        critical_errors = self.get_critical_errors()
        if critical_errors:
            lines.append("CRITICAL ERRORS:")
            lines.append("-" * 40)
            for error in critical_errors:
                lines.append(str(error))
                if include_details and error.details:
                    lines.append(f"  Details: {error.details}")
            lines.append("")

        regular_errors = [
            e for e in self.get_errors() if e.severity != ErrorSeverity.CRITICAL
        ]
        if regular_errors:
            lines.append("ERRORS:")
            lines.append("-" * 40)
            for error in regular_errors:
                lines.append(str(error))
                if include_details and error.details:
                    lines.append(f"  Details: {error.details}")
            lines.append("")

        if self.warnings:
            lines.append("WARNINGS:")
            lines.append("-" * 40)
            for warning in self.warnings:
                lines.append(str(warning))
                if include_details and warning.details:
                    lines.append(f"  Details: {warning.details}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


def create_source_location(position, file_name: Optional[str] = None) -> SourceLocation:
    """
    Create SourceLocation from Position.

    Args:
        position: Position object with line, column, offset
        file_name: Optional file name

    Returns:
        SourceLocation object
    """
    return SourceLocation(
        line=position.line,
        column=position.column,
        offset=position.offset,
        file_name=file_name,
    )
