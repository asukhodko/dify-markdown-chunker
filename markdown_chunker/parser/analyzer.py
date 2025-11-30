"""
Content analyzer for Markdown documents.

This module implements content analysis and metrics calculation based on the
algorithms from docs/markdown-extractor/TECHNICAL-SPECIFICATION.md.

Algorithm Documentation:
    - Content Analyzer: docs/markdown-extractor/04-components/content-analyzer.md
    - Content Analysis: docs/markdown-extractor/02-algorithm-core/content-analysis.md
    - Metrics: docs/markdown-extractor/06-algorithms/metrics.md
"""

from typing import List, Optional

from .types import ContentAnalysis, ElementCollection, FencedBlock


class ContentAnalyzer:
    """Analyzer for document content and metrics calculation."""

    def __init__(self):
        # Thresholds from technical specification
        self.code_ratio_threshold = 0.7
        self.list_ratio_threshold = 0.6
        self.mixed_content_threshold = 0.3

    def analyze_content(
        self,
        md_text: str,
        fenced_blocks: Optional[List[FencedBlock]] = None,
        elements: Optional[ElementCollection] = None,
    ) -> ContentAnalysis:
        """Analyze document content and calculate metrics."""

        # Import functions if data not provided
        if fenced_blocks is None:
            from .core import extract_fenced_blocks

            fenced_blocks = extract_fenced_blocks(md_text)

        if elements is None:
            from .elements import detect_elements

            elements = detect_elements(md_text)

        # Basic metrics
        total_chars = len(md_text)
        total_lines = len(md_text.split("\n"))

        # Calculate content sizes
        code_chars = sum(len(block.content) for block in fenced_blocks)
        list_chars = self._calculate_list_chars(elements.lists)
        table_chars = self._calculate_table_chars(elements.tables)
        text_chars = total_chars - code_chars - list_chars - table_chars

        # Calculate ratios
        code_ratio = code_chars / total_chars if total_chars > 0 else 0
        text_ratio = text_chars / total_chars if total_chars > 0 else 0
        list_ratio = list_chars / total_chars if total_chars > 0 else 0
        table_ratio = table_chars / total_chars if total_chars > 0 else 0

        # Element counts
        code_block_count = len(fenced_blocks)
        list_count = len(elements.lists)
        table_count = len(elements.tables)

        # P1-006: Programming languages with occurrence counts
        languages = {}
        for block in fenced_blocks:
            if block.language:
                lang = block.language.lower()
                languages[lang] = languages.get(lang, 0) + 1

        # P1-005: Header count by level
        header_count_by_level = {}
        for header in elements.headers:
            level = header.level
            header_count_by_level[level] = header_count_by_level.get(level, 0) + 1

        # Structural depth
        max_header_depth = max((h.level for h in elements.headers), default=0)
        # P1-003: Nested list depth
        nested_list_depth = max(
            (lst.max_nesting_level for lst in elements.lists), default=0
        )

        # P1-002: Count inline code (backtick code)
        import re

        inline_code_pattern = re.compile(r"`[^`\n]+`")
        inline_code_count = len(inline_code_pattern.findall(md_text))

        # P1-001: Calculate ContentMetrics fields
        lines = md_text.split("\n")
        average_line_length = (
            sum(len(line) for line in lines) / len(lines) if lines else 0.0
        )
        max_line_length = max((len(line) for line in lines), default=0)
        empty_lines = sum(1 for line in lines if not line.strip())
        indented_lines = sum(1 for line in lines if line.startswith((" ", "\t")))

        # Calculate punctuation ratio
        import string

        punctuation_chars = sum(1 for char in md_text if char in string.punctuation)
        punctuation_ratio = punctuation_chars / total_chars if total_chars > 0 else 0.0

        # Count special characters
        special_chars = {}
        special_char_set = {"#", "*", "_", "`", "[", "]", "(", ")", "|", "-", "+", "~"}
        for char in md_text:
            if char in special_char_set:
                special_chars[char] = special_chars.get(char, 0) + 1

        # P1-004: Build block elements list (in document order)
        block_elements = []
        # Add headers
        for header in elements.headers:
            block_elements.append(
                {
                    "type": "header",
                    "start_line": header.line,
                    "level": header.level,
                    "text": header.text,
                }
            )
        # Add code blocks
        for block in fenced_blocks:
            block_elements.append(
                {
                    "type": "code_block",
                    "start_line": block.start_line,
                    "language": block.language,
                }
            )
        # Add lists
        for lst in elements.lists:
            block_elements.append(
                {"type": "list", "start_line": lst.start_line, "list_type": lst.type}
            )
        # Add tables
        for table in elements.tables:
            block_elements.append(
                {
                    "type": "table",
                    "start_line": table.start_line,
                    "columns": table.column_count,
                }
            )
        # Sort by start_line to maintain document order
        block_elements.sort(key=lambda x: x["start_line"])

        # Mixed content detection
        has_mixed_content = self._detect_mixed_content(
            code_ratio, list_ratio, table_ratio, text_ratio
        )

        # Complexity calculation
        complexity_score = self._calculate_complexity(
            code_ratio,
            list_ratio,
            table_ratio,
            text_ratio,
            max_header_depth,
            nested_list_depth,
            total_chars,
            has_mixed_content,
        )

        # Content type classification
        content_type = self._classify_content_type(
            code_ratio, list_ratio, table_ratio, has_mixed_content
        )

        # Extract preamble
        preamble_extractor = PreambleExtractor()
        preamble = preamble_extractor.extract(md_text)

        return ContentAnalysis(
            total_chars=total_chars,
            total_lines=total_lines,
            total_words=len(md_text.split()),
            code_ratio=code_ratio,
            text_ratio=text_ratio,
            code_block_count=code_block_count,
            header_count=header_count_by_level,  # P1-005: Now Dict[int, int]
            content_type=content_type,
            languages=languages,  # P1-006: Now Dict[str, int]
            list_count=list_count,
            table_count=table_count,
            list_ratio=list_ratio,
            table_ratio=table_ratio,
            complexity_score=complexity_score,
            max_header_depth=max_header_depth,
            has_mixed_content=has_mixed_content,
            nested_list_depth=nested_list_depth,  # P1-003
            inline_code_count=inline_code_count,  # P1-002
            average_line_length=average_line_length,  # P1-001
            max_line_length=max_line_length,  # P1-001
            empty_lines=empty_lines,  # P1-001
            indented_lines=indented_lines,  # P1-001
            punctuation_ratio=punctuation_ratio,  # P1-001
            special_chars=special_chars,  # P1-001
            block_elements=block_elements,  # P1-004
            preamble=preamble,
        )

    def _calculate_list_chars(self, lists) -> int:
        """Calculate total characters in lists."""
        total = 0
        for lst in lists:
            for item in lst.items:
                total += len(item.content)
        return total

    def _calculate_table_chars(self, tables) -> int:
        """Calculate total characters in tables."""
        total = 0
        for table in tables:
            total += table.get_total_size()
        return total

    def _detect_mixed_content(
        self,
        code_ratio: float,
        list_ratio: float,
        table_ratio: float,
        text_ratio: float,
    ) -> bool:
        """Detect mixed content based on ratios."""
        # Mixed content when multiple content types are significant
        significant_types = 0

        if code_ratio > 0.1:
            significant_types += 1
        if list_ratio > 0.1:
            significant_types += 1
        if table_ratio > 0.1:
            significant_types += 1
        if text_ratio > 0.2:
            significant_types += 1

        return significant_types >= 2 and code_ratio < self.code_ratio_threshold

    def _calculate_complexity(
        self,
        code_ratio: float,
        list_ratio: float,
        table_ratio: float,
        text_ratio: float,
        max_header_depth: int,
        max_list_nesting: int,
        total_chars: int,
        has_mixed_content: bool,
    ) -> float:
        """Calculate document complexity score (0-1)."""

        # Structural complexity (0-0.3)
        structural_complexity = (
            min(max_header_depth / 10.0, 0.1)
            + min(max_list_nesting / 10.0, 0.1)
            + (0.1 if table_ratio > 0 else 0.0)
        )

        # Content complexity (0-0.4)
        content_complexity = (code_ratio * 0.2) + (0.2 if has_mixed_content else 0.0)

        # Size complexity (0-0.3)
        size_complexity = (
            0.3
            if total_chars > 50000
            else 0.2 if total_chars > 20000 else 0.1 if total_chars > 10000 else 0.0
        )

        return min(structural_complexity + content_complexity + size_complexity, 1.0)

    def _classify_content_type(
        self,
        code_ratio: float,
        list_ratio: float,
        table_ratio: float,
        has_mixed_content: bool,
    ) -> str:
        """Classify document content type."""

        if code_ratio >= self.code_ratio_threshold:
            return "code_heavy"
        elif list_ratio >= self.list_ratio_threshold and code_ratio < 0.3:
            return "list_heavy"
        elif has_mixed_content:
            return "mixed"
        else:
            return "primary"


class PreambleExtractor:
    """
    Extractor for document preamble (content before first header).

    The preamble is content that appears before the first header in a
    markdown document. It often contains introductory text, metadata,
    or document summaries.
    """

    # Metadata patterns for detection
    METADATA_PATTERNS = {
        "author": r"^(?:author|by):\s*(.+)$",
        "date": r"^date:\s*(.+)$",
        "version": r"^version:\s*(.+)$",
        "title": r"^title:\s*(.+)$",
        "description": r"^description:\s*(.+)$",
        "tags": r"^tags:\s*(.+)$",
    }

    # Keywords for type classification
    INTRODUCTION_KEYWORDS = [
        "introduction",
        "overview",
        "about",
        "welcome",
        "getting started",
        "intro",
        "preface",
    ]

    SUMMARY_KEYWORDS = [
        "summary",
        "tldr",
        "tl;dr",
        "abstract",
        "synopsis",
        "brie",
        "executive summary",
    ]

    def __init__(self):
        """Initialize preamble extractor."""
        import re

        self._metadata_regex = {
            key: re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for key, pattern in self.METADATA_PATTERNS.items()
        }

    def extract(self, md_text: str) -> Optional["PreambleInfo"]:  # noqa: F821
        """
        Extract preamble from markdown text.

        Args:
            md_text: Markdown content to analyze

        Returns:
            PreambleInfo if preamble exists, None otherwise

        Examples:
            >>> extractor=PreambleExtractor()
            >>> text="This is intro.\\n\\n# Header\\nContent"
            >>> preamble=extractor.extract(text)
            >>> print(preamble.type)
            'introduction'
        """
        from .types import PreambleInfo

        if not md_text or not md_text.strip():
            return None

        # Find first header
        lines = md_text.split("\n")
        first_header_idx = self._find_first_header(lines)

        if first_header_idx == 0:
            # No preamble - document starts with header
            return None

        # Extract preamble content
        preamble_lines = lines[:first_header_idx]
        preamble_content = "\n".join(preamble_lines).strip()

        if not preamble_content or len(preamble_content) < 10:
            # Too short to be meaningful preamble
            return None

        # Analyze preamble
        preamble_type = self._classify_type(preamble_content)
        has_metadata = self._has_metadata(preamble_content)
        metadata_fields = (
            self._extract_metadata(preamble_content) if has_metadata else {}
        )

        return PreambleInfo(
            content=preamble_content,
            type=preamble_type,
            line_count=len(preamble_lines),
            char_count=len(preamble_content),
            has_metadata=has_metadata,
            metadata_fields=metadata_fields,
        )

    def _find_first_header(self, lines: List[str]) -> int:
        """
        Find index of first header line.

        Args:
            lines: List of document lines

        Returns:
            Index of first header, or len(lines) if no header found
        """
        import re

        # ATX headers: # Header
        atx_pattern = re.compile(r"^\s{0,3}#{1,6}\s+.+")

        # Setext headers: underlined with=or -
        setext_pattern = re.compile(r"^\s{0,3}[=-]{3,}\s*$")

        for i, line in enumerate(lines):
            # Check ATX header
            if atx_pattern.match(line):
                return i

            # Check Setext header (underline on next line)
            if i > 0 and setext_pattern.match(line):
                # Previous line is the header text
                prev_line = lines[i - 1].strip()
                if prev_line:  # Not empty
                    return i - 1

        return len(lines)

    def _classify_type(self, content: str) -> str:
        """
        Classify preamble type based on content.

        Args:
            content: Preamble content

        Returns:
            Type: "introduction", "summary", "metadata", or "general"
        """
        content_lower = content.lower()

        # Check for metadata
        if self._has_metadata(content):
            return "metadata"

        # Check for introduction keywords
        for keyword in self.INTRODUCTION_KEYWORDS:
            if keyword in content_lower:
                return "introduction"

        # Check for summary keywords
        for keyword in self.SUMMARY_KEYWORDS:
            if keyword in content_lower:
                return "summary"

        # Default to general
        return "general"

    def _has_metadata(self, content: str) -> bool:
        """
        Check if content contains structured metadata.

        Args:
            content: Content to check

        Returns:
            True if metadata patterns found
        """
        for pattern in self._metadata_regex.values():
            if pattern.search(content):
                return True
        return False

    def _extract_metadata(self, content: str) -> dict:
        """
        Extract metadata fields from content.

        Args:
            content: Content to extract from

        Returns:
            Dictionary of metadata fields
        """
        metadata = {}

        for key, pattern in self._metadata_regex.items():
            match = pattern.search(content)
            if match:
                metadata[key] = match.group(1).strip()

        return metadata


def analyze_content(md_text: str) -> ContentAnalysis:
    """Convenience function to analyze content."""
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(md_text)
