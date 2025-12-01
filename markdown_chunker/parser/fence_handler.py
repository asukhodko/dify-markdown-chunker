"""
Enhanced Fence Handler with proper indentation support.

This module provides improved fence handling that correctly processes
closing fences according to Markdown specification, including proper
indentation handling and structured error reporting.
"""

import logging
import re
from dataclasses import dataclass
from typing import List, Optional

from .errors import EnhancedErrorCollector, SourceLocation


@dataclass
class FenceInfo:
    """Information about a fence (opening or closing)."""

    fence_type: str  # "```" or "~~~"
    fence_length: int  # Length of the fence
    indent: int  # Indentation level
    language: str  # Language identifier (for opening fences)
    line_number: int  # Line number (1-based)
    raw_line: str  # Original line content

    def is_opening_fence(self) -> bool:
        """Check if this is an opening fence (has language or attributes)."""
        return bool(self.language.strip())

    def is_closing_fence(self) -> bool:
        """Check if this is a closing fence (no language or attributes)."""
        return not self.language.strip()

    def can_close_fence(self, opening_fence: "FenceInfo") -> bool:
        """Check if this fence can close the given opening fence."""
        # Must be same fence type
        if self.fence_type != opening_fence.fence_type:
            return False

        # Must be at least as long as opening fence
        if self.fence_length < opening_fence.fence_length:
            return False

        # Must not be more indented than opening fence
        if self.indent > opening_fence.indent:
            return False

        # Must be a closing fence
        if not self.is_closing_fence():
            return False

        return True


class FenceHandler:
    """Enhanced fence handler with proper Markdown specification compliance."""

    def __init__(
        self, error_collector: Optional[EnhancedErrorCollector] = None
    ):
        """Initialize fence handler."""
        self.error_collector = error_collector or EnhancedErrorCollector()
        self.logger = logging.getLogger(__name__)

        # Patterns for fence detection
        self.fence_pattern = re.compile(
            r"^(\s*)([`~]{3,})\s*([a-zA-Z0-9_+-]*)\s*(.*?)$"
        )

    def find_closing_fence(
        self, lines: List[str], start_line: int, opening_fence: FenceInfo
    ) -> Optional[int]:
        """
        Find closing fence with proper indentation and specification compliance.

        Args:
            lines: List of all lines in the document
            start_line: Line number to start searching from (0-based)
            opening_fence: Information about the opening fence

        Returns:
            Line number of closing fence (0-based) or None if not found
        """

        self.logger.debug(
            f"Searching for closing fence starting at line {start_line + 1}, "
            f"opening fence: {opening_fence.fence_type} "
            f"(indent: {opening_fence.indent})"
        )

        for i in range(start_line, len(lines)):
            line = lines[i]

            # Parse potential fence
            fence_info = self._parse_fence_line(line, i + 1)  # Convert to 1-based

            if fence_info:
                # Check if this can close our opening fence
                if fence_info.can_close_fence(opening_fence):
                    self.logger.debug(f"Found closing fence at line {i + 1}")
                    return i

                # Check for malformed fences
                elif fence_info.fence_type == opening_fence.fence_type:
                    self._handle_malformed_fence(fence_info, opening_fence)

        # No closing fence found
        location = SourceLocation(
            line=opening_fence.line_number, column=opening_fence.indent
        )
        self.error_collector.add_warning(
            f"Unclosed {opening_fence.fence_type} fence starting at "
            f"line {opening_fence.line_number}",
            category="fence_parsing",
            location=location,
            details=f"Fence type: {opening_fence.fence_type}, "
            f"length: {opening_fence.fence_length}, "
            f"indent: {opening_fence.indent}",
        )

        return None

    def parse_opening_fence(self, line: str, line_number: int) -> Optional[FenceInfo]:
        """
        Parse a line to check if it's an opening fence.

        Args:
            line: The line to parse
            line_number: Line number (1-based)

        Returns:
            FenceInfo if it's an opening fence, None otherwise
        """

        fence_info = self._parse_fence_line(line, line_number)

        if fence_info and fence_info.is_opening_fence():
            return fence_info

        return None

    def _parse_fence_line(self, line: str, line_number: int) -> Optional[FenceInfo]:
        """Parse a line to extract fence information."""

        match = self.fence_pattern.match(line)
        if not match:
            return None

        indent_str = match.group(1)
        fence_chars = match.group(2)
        language = match.group(3) or ""
        extra_attrs = match.group(4) or ""

        # Calculate indentation (spaces only, tabs count as 4 spaces)
        indent = 0
        for char in indent_str:
            if char == " ":
                indent += 1
            elif char == "\t":
                indent += 4

        # Determine fence type
        fence_type = fence_chars[:3]  # First 3 characters determine type

        # Combine language and extra attributes
        full_language = f"{language} {extra_attrs}".strip()

        return FenceInfo(
            fence_type=fence_type,
            fence_length=len(fence_chars),
            indent=indent,
            language=full_language,
            line_number=line_number,
            raw_line=line,
        )

    def _handle_malformed_fence(self, fence_info: FenceInfo, opening_fence: FenceInfo):
        """Handle malformed fence that can't properly close the opening fence."""

        location = SourceLocation(line=fence_info.line_number, column=fence_info.indent)

        if fence_info.fence_length < opening_fence.fence_length:
            self.error_collector.add_warning(
                f"Fence at line {fence_info.line_number} too short to close "
                "opening fence "
                f"(length {fence_info.fence_length} < {opening_fence.fence_length})",
                category="fence_parsing",
                location=location,
                details=f"Opening fence at line {opening_fence.line_number}",
            )

        elif fence_info.indent > opening_fence.indent:
            self.error_collector.add_warning(
                f"Fence at line {fence_info.line_number} too indented to close "
                f"opening fence (indent {fence_info.indent} > "
                f"{opening_fence.indent})",
                category="fence_parsing",
                location=location,
                details=f"Opening fence at line {opening_fence.line_number}",
            )

        elif fence_info.is_opening_fence():
            self.error_collector.add_warning(
                f"Found opening fence at line {fence_info.line_number} while "
                "looking for closing fence",
                category="fence_parsing",
                location=location,
                details="Expected closing fence for opening fence at "
                f"line {opening_fence.line_number}",
            )

    def validate_fence_structure(self, lines: List[str]) -> List[str]:
        """
        Validate the overall fence structure in a document.

        Returns:
            List of validation issues found
        """

        issues = []
        fence_stack = []  # Stack of opening fences

        for i, line in enumerate(lines):
            line_number = i + 1
            fence_info = self._parse_fence_line(line, line_number)

            if fence_info:
                if fence_info.is_opening_fence():
                    # Opening fence
                    fence_stack.append(fence_info)

                elif fence_info.is_closing_fence():
                    # Closing fence
                    if not fence_stack:
                        issues.append(
                            f"Closing fence without opening at line {line_number}"
                        )
                    else:
                        opening_fence = fence_stack[-1]
                        if fence_info.can_close_fence(opening_fence):
                            fence_stack.pop()
                        else:
                            issues.append(
                                f"Mismatched closing fence at line {line_number} "
                                f"for opening fence at line {opening_fence.line_number}"
                            )

        # Check for unclosed fences
        for opening_fence in fence_stack:
            issues.append(f"Unclosed fence at line {opening_fence.line_number}")

        return issues

    def get_fence_indent(self, line: str) -> int:
        """Get the indentation level of a line."""
        indent = 0
        for char in line:
            if char == " ":
                indent += 1
            elif char == "\t":
                indent += 4
            else:
                break
        return indent

    def normalize_fence_type(self, fence_chars: str) -> str:
        """Normalize fence characters to standard type."""
        if fence_chars.startswith("`"):
            return "```"
        elif fence_chars.startswith("~"):
            return "~~~"
        else:
            return fence_chars[:3]

    def is_valid_fence_length(self, fence_chars: str) -> bool:
        """Check if fence has valid length (at least 3 characters)."""
        return len(fence_chars) >= 3

    def extract_language_from_fence(self, fence_line: str) -> Optional[str]:
        """Extract language identifier from opening fence line."""
        fence_info = self._parse_fence_line(fence_line, 1)
        if fence_info and fence_info.is_opening_fence():
            # Return just the language part (first word)
            language_parts = fence_info.language.split()
            return language_parts[0] if language_parts else None
        return None


def create_fence_info(
    fence_type: str,
    fence_length: int,
    indent: int,
    language: str = "",
    line_number: int = 1,
    raw_line: str = "",
) -> FenceInfo:
    """Convenience function to create FenceInfo."""
    return FenceInfo(
        fence_type=fence_type,
        fence_length=fence_length,
        indent=indent,
        language=language,
        line_number=line_number,
        raw_line=raw_line,
    )
