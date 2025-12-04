"""
Preamble extraction for Markdown documents.

This module extracts and classifies content before the first header (preamble),
which often contains metadata, introductions, or summaries.

Algorithm Documentation:
    - Preamble Handler: docs/markdown-extractor/04-components/preamble-handler.md
    - Content Analysis: docs/markdown-extractor/02-algorithm-core/content-analysis.md

Classes:
    PreambleType: Enum of preamble types
    PreambleInfo: Dataclass with preamble information
    PreambleExtractor: Main extractor class
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PreambleType(Enum):
    """Types of preamble content."""

    INTRODUCTION = "introduction"  # Introductory text
    SUMMARY = "summary"  # Brief summary (TL;DR, abstract)
    METADATA = "metadata"  # Structured metadata (Author:, Date:, etc.)
    GENERAL = "general"  # Other content before first header


@dataclass
class PreambleInfo:
    """Information about extracted preamble."""

    type: PreambleType
    content: str
    start_line: int
    end_line: int
    line_count: int
    char_count: int
    has_metadata: bool = False
    metadata_fields: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Serialize to dictionary.

        Returns:
            Dictionary representation of preamble info.

        Examples:
            >>> preamble=PreambleInfo(
            ...     type=PreambleType.METADATA,
            ...     content="Author: John",
            ...     start_line=1,
            ...     end_line=1,
            ...     line_count=1,
            ...     char_count=12,
            ...     has_metadata=True,
            ...     metadata_fields={"author": "John"}
            ... )
            >>> result=preamble.to_dict()
            >>> result["type"]
            'metadata'
        """
        return {
            "type": self.type.value,
            "content": self.content,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "line_count": self.line_count,
            "char_count": self.char_count,
            "has_metadata": self.has_metadata,
            "metadata_fields": self.metadata_fields,
        }


class PreambleExtractor:
    """
    Extract preamble (content before first header) from Markdown documents.

    The preamble often contains important metadata, introductions, or summaries
    that should be preserved and classified appropriately.

    Examples:
        >>> extractor=PreambleExtractor()
        >>> text="Author: John\\nDate: 2025\\n\\n# Title\\nContent"
        >>> preamble=extractor.extract_preamble(text)
        >>> preamble.type
        <PreambleType.METADATA: 'metadata'>
        >>> preamble.metadata_fields["author"]
        'John'
    """

    def __init__(self, min_lines: int = 2, min_chars: int = 50):
        """
        Initialize preamble extractor.

        Args:
            min_lines: Minimum number of lines for valid preamble (default: 2)
            min_chars: Minimum number of characters for valid preamble (default: 50)
        """
        self.min_lines = min_lines
        self.min_chars = min_chars

        # Keywords for type detection
        self.introduction_keywords = [
            "introduction",
            "overview",
            "about",
            "welcome",
            "getting started",
        ]
        self.summary_keywords = ["tl;dr", "summary", "abstract", "synopsis", "tldr"]

        # Metadata patterns (key: value format)
        self.metadata_patterns = [
            r"^(author|date|version|title|tags|status|created|updated):\s*(.+)$"
        ]

    def extract_preamble(self, text: str) -> Optional[PreambleInfo]:
        """
        Extract preamble from markdown text.

        Args:
            text: Markdown document text

        Returns:
            PreambleInfo if preamble found and valid, None otherwise

        Examples:
            >>> extractor=PreambleExtractor()
            >>> text="This is an introduction.\\n\\n# Chapter 1\\nContent"
            >>> preamble=extractor.extract_preamble(text)
            >>> preamble.type
            <PreambleType.INTRODUCTION: 'introduction'>
        """
        if not text or not text.strip():
            return None

        lines = text.split("\n")

        # Find first header
        first_header_line = self._find_first_header(lines)
        if first_header_line is None or first_header_line == 0:
            return None

        # Extract preamble lines
        preamble_lines = lines[:first_header_line]
        preamble_content = "\n".join(preamble_lines).strip()

        # Check minimum requirements
        if len(preamble_lines) < self.min_lines:
            return None
        if len(preamble_content) < self.min_chars:
            return None

        # Detect type
        preamble_type = self.detect_preamble_type(preamble_content)

        # Extract metadata if applicable
        metadata_fields = {}
        has_metadata = False
        if preamble_type == PreambleType.METADATA:
            metadata_fields = self.extract_metadata_fields(preamble_content)
            has_metadata = len(metadata_fields) > 0

        return PreambleInfo(
            type=preamble_type,
            content=preamble_content,
            start_line=1,
            end_line=first_header_line,
            line_count=len(preamble_lines),
            char_count=len(preamble_content),
            has_metadata=has_metadata,
            metadata_fields=metadata_fields,
        )

    def detect_preamble_type(self, text: str) -> PreambleType:
        """
        Detect the type of preamble content.

        Args:
            text: Preamble text content

        Returns:
            PreambleType enum value

        Examples:
            >>> extractor=PreambleExtractor()
            >>> extractor.detect_preamble_type("Author: John\\nDate: 2025")
            <PreambleType.METADATA: 'metadata'>
            >>> extractor.detect_preamble_type("TL;DR: This is a summary")
            <PreambleType.SUMMARY: 'summary'>
        """
        text_lower = text.lower()

        # Check for metadata pattern
        if self._has_metadata_pattern(text):
            return PreambleType.METADATA

        # Check for summary keywords
        for keyword in self.summary_keywords:
            if keyword in text_lower:
                return PreambleType.SUMMARY

        # Check for introduction keywords
        for keyword in self.introduction_keywords:
            if keyword in text_lower:
                return PreambleType.INTRODUCTION

        # Default to general
        return PreambleType.GENERAL

    def extract_metadata_fields(self, text: str) -> Dict[str, str]:
        """
        Extract metadata fields from preamble text.

        Looks for key: value patterns like "Author: John Doe".

        Args:
            text: Preamble text content

        Returns:
            Dictionary of metadata fields (lowercase keys)

        Examples:
            >>> extractor=PreambleExtractor()
            >>> text="Author: John Doe\\nDate: 2025-11-16\\nVersion: 1.0"
            >>> fields=extractor.extract_metadata_fields(text)
            >>> fields["author"]
            'John Doe'
            >>> fields["date"]
            '2025-11-16'
        """
        fields = {}

        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            for pattern in self.metadata_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    key = match.group(1).lower()
                    value = match.group(2).strip()
                    fields[key] = value
                    break

        return fields

    def _find_first_header(self, lines: List[str]) -> Optional[int]:
        """
        Find the line number of the first header.

        Supports both ATX headers (# Title) and Setext headers (Title\\n====).

        Args:
            lines: List of document lines

        Returns:
            Line index (0-based) of first header, or None if no header found

        Examples:
            >>> extractor=PreambleExtractor()
            >>> lines=["Preamble", "", "# Header", "Content"]
            >>> extractor._find_first_header(lines)
            2
        """
        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # ATX header: # Title, ## Title, etc.
            if line_stripped.startswith("#") and len(line_stripped) > 1:
                # Check it's a valid header (has space after #)
                if line_stripped[1] == " " or line_stripped[1] == "#":
                    return i

            # Setext header: Title\n==== or Title\n----
            if i > 0 and line_stripped:
                # Check if line is all=or all -
                if all(c in "=-" for c in line_stripped) and len(line_stripped) >= 3:
                    # Previous line should be non-empty
                    if lines[i - 1].strip():
                        return i - 1

        return None

    def _has_metadata_pattern(self, text: str) -> bool:
        """
        Check if text contains metadata patterns.

        Args:
            text: Text to check

        Returns:
            True if metadata pattern found, False otherwise

        Examples:
            >>> extractor=PreambleExtractor()
            >>> extractor._has_metadata_pattern("Author: John")
            True
            >>> extractor._has_metadata_pattern("Just some text")
            False
        """
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            for pattern in self.metadata_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    return True

        return False


# Convenience function
def extract_preamble(
    text: str, min_lines: int = 2, min_chars: int = 50
) -> Optional[PreambleInfo]:
    """
    Convenience function to extract preamble from markdown text.

    Args:
        text: Markdown document text
        min_lines: Minimum number of lines for valid preamble
        min_chars: Minimum number of characters for valid preamble

    Returns:
        PreambleInfo if found, None otherwise

    Examples:
        >>> text="Author: John\\n\\n# Title\\nContent"
        >>> preamble=extract_preamble(text)
        >>> preamble.type.value
        'metadata'
    """
    extractor = PreambleExtractor(min_lines=min_lines, min_chars=min_chars)
    return extractor.extract_preamble(text)
