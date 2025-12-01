"""Structural element detector for Markdown documents.

This module implements detection of headers, lists, tables, and other structural
elements based on the algorithms from
docs/markdown-extractor/TECHNICAL-SPECIFICATION.md.
"""

import re
from typing import Any, Dict, List, Optional

from .types import ElementCollection, Header, ListItem, MarkdownList, Table


class ElementDetector:
    """Detector for structural elements in Markdown documents."""

    def __init__(self):
        # Patterns for detecting elements (from technical specification)
        self.header_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        self.list_patterns = {
            "unordered": re.compile(r"^(\s*)([-*+])\s+(.+)$"),
            "ordered": re.compile(r"^(\s*)(\d+\.)\s+(.+)$"),
            "task": re.compile(r"^(\s*)[-*+]\s+\[([ xX])\]\s+(.+)$"),
        }
        self.table_separator_pattern = re.compile(r"^\|?[-:\s|]+\|?\s*$")
        self.table_row_pattern = re.compile(r"^\|(.+)\|\s*$")

    def detect_elements(self, md_text: str) -> ElementCollection:
        """Detect all structural elements in the document."""
        lines = md_text.split("\n")

        headers = self._detect_headers(md_text)
        lists = self._detect_lists(lines)
        tables = self._detect_tables(lines)

        return ElementCollection(headers=headers, lists=lists, tables=tables)

    def _detect_headers(self, md_text: str) -> List[Header]:
        """Detect headers and build hierarchy."""
        headers = []
        lines = md_text.split("\n")
        offset = 0

        for line_num, line in enumerate(lines):
            match = self.header_pattern.match(line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()

                header = Header(
                    level=level,
                    text=text,
                    line=line_num,
                    offset=offset,
                    anchor=self._generate_anchor(text),
                )
                headers.append(header)

            offset += len(line) + 1  # +1 for newline character

        return headers

    def _generate_anchor(self, text: str) -> str:
        """Generate anchor for header (GitHub-style)."""
        # Convert to lowercase
        anchor = text.lower()
        # Remove non-alphanumeric characters except spaces and hyphens
        anchor = re.sub(r"[^\w\s-]", "", anchor)
        # Replace spaces with hyphens
        anchor = re.sub(r"[-\s]+", "-", anchor)
        # Remove leading/trailing hyphens
        return anchor.strip("-")

    def _detect_lists(self, lines: List[str]) -> List[MarkdownList]:
        """Detect lists with nesting support."""
        lists: List[MarkdownList] = []
        current_list: Optional[Dict[str, Any]] = None
        current_items: List[ListItem] = []

        for line_num, line in enumerate(lines):
            list_item = self._parse_list_item(line, line_num)

            if list_item:
                if current_list is None:
                    # Start new list
                    current_list = {
                        "type": self._determine_list_type(list_item),
                        "start_line": line_num,
                        "max_nesting": list_item.level,
                    }
                    current_items = [list_item]
                else:
                    # Continue current list
                    current_items.append(list_item)
                    current_list["max_nesting"] = max(
                        int(current_list["max_nesting"]), list_item.level
                    )
            else:
                if current_list is not None:
                    # End current list
                    markdown_list = MarkdownList(
                        type=str(current_list["type"]),
                        items=current_items,
                        start_line=int(current_list["start_line"]),  # type: ignore[arg-type]
                        end_line=line_num - 1,
                        max_nesting_level=int(current_list["max_nesting"]),  # type: ignore[arg-type]
                    )
                    lists.append(markdown_list)
                    current_list = None
                    current_items = []

        # Handle list at end of file
        if current_list is not None:
            markdown_list = MarkdownList(
                type=str(current_list["type"]),
                items=current_items,
                start_line=int(current_list["start_line"]),  # type: ignore[arg-type]
                end_line=len(lines) - 1,
                max_nesting_level=int(current_list["max_nesting"]),  # type: ignore[arg-type]
            )
            lists.append(markdown_list)

        return lists

    def _parse_list_item(self, line: str, line_num: int) -> Optional[ListItem]:
        """Parse a single list item."""
        # Check for task list
        task_match = self.list_patterns["task"].match(line)
        if task_match:
            indent = task_match.group(1)
            checked_char = task_match.group(2)
            content = task_match.group(3)

            return ListItem(
                content=content,
                level=len(indent) // 2,  # Assume 2 spaces per level
                marker="- [ ]",
                line=line_num,
                offset=0,  # Will be calculated later if needed
                is_task=True,
                is_checked=checked_char.lower() == "x",
            )

        # Check for unordered list
        unordered_match = self.list_patterns["unordered"].match(line)
        if unordered_match:
            indent = unordered_match.group(1)
            marker = unordered_match.group(2)
            content = unordered_match.group(3)

            return ListItem(
                content=content,
                level=len(indent) // 2,
                marker=marker,
                line=line_num,
                offset=0,
                is_task=False,
            )

        # Check for ordered list
        ordered_match = self.list_patterns["ordered"].match(line)
        if ordered_match:
            indent = ordered_match.group(1)
            marker = ordered_match.group(2)
            content = ordered_match.group(3)

            return ListItem(
                content=content,
                level=len(indent) // 2,
                marker=marker,
                line=line_num,
                offset=0,
                is_task=False,
            )

        return None

    def _determine_list_type(self, first_item: ListItem) -> str:
        """Determine list type from first item."""
        if first_item.is_task:
            return "task"
        elif first_item.marker.endswith("."):
            return "ordered"
        else:
            return "unordered"

    def _detect_tables(self, lines: List[str]) -> List[Table]:
        """Detect tables with headers and alignment."""
        tables = []
        i = 0

        while i < len(lines):
            table = self._try_parse_table_at_line(lines, i)
            if table:
                tables.append(table)
                i = table.end_line + 1
            else:
                i += 1

        return tables

    def _try_parse_table_at_line(
        self, lines: List[str], start_line: int
    ) -> Optional[Table]:
        """Try to parse a table starting at the given line."""
        if start_line + 1 >= len(lines):
            return None

        # Check if next line is a separator
        if not self.table_separator_pattern.match(lines[start_line + 1]):
            return None

        # Parse header
        header_match = self.table_row_pattern.match(lines[start_line])
        if not header_match:
            return None

        headers = [cell.strip() for cell in header_match.group(1).split("|")]

        # Parse alignment from separator
        separator_line = lines[start_line + 1]
        alignment = self._parse_table_alignment(separator_line, len(headers))

        # Parse data rows
        rows = []
        current_line = start_line + 2

        while current_line < len(lines):
            row_match = self.table_row_pattern.match(lines[current_line])
            if not row_match:
                break

            row_cells = [cell.strip() for cell in row_match.group(1).split("|")]
            # Normalize to header count
            while len(row_cells) < len(headers):
                row_cells.append("")
            row_cells = row_cells[: len(headers)]

            rows.append(row_cells)
            current_line += 1

        if not rows:  # Table must have at least one data row
            return None

        return Table(
            headers=headers,
            rows=rows,
            start_line=start_line,
            end_line=current_line - 1,
            column_count=len(headers),
            alignment=alignment,
        )

    def _parse_table_alignment(
        self, separator_line: str, column_count: int
    ) -> List[str]:
        """Parse column alignment from separator line."""
        alignment = []
        cells = [c.strip() for c in separator_line.split("|") if c.strip()]

        for i in range(min(column_count, len(cells))):
            cell = cells[i]
            # Check if cell contains dashes (valid separator)
            if "-" in cell:
                if cell.startswith(":") and cell.endswith(":"):
                    alignment.append("center")
                elif cell.endswith(":"):
                    alignment.append("right")
                else:
                    alignment.append("left")
            else:
                alignment.append("left")

        # Fill remaining columns with left alignment
        while len(alignment) < column_count:
            alignment.append("left")

        return alignment


def detect_elements(md_text: str) -> ElementCollection:
    """Convenience function to detect elements."""
    detector = ElementDetector()
    return detector.detect_elements(md_text)
