"""
Single-pass markdown parser for Stage 1 analysis.

This module eliminates the dual invocation pattern from v1.x where the parser
was called twice (once for analysis, once for preamble extraction).
"""

from typing import List, Set

from markdown_it import MarkdownIt

from .types import ContentAnalysis, FencedBlock, Header, ParsingError, Table


class Parser:
    """
    Markdown parser for Stage 1 analysis (single-pass).

    Uses markdown-it-py for tokenization and extracts all structural
    elements in a single pass.
    """

    def __init__(self) -> None:
        """Initialize parser with markdown-it-py."""
        # Enable tables plugin for table parsing
        self._md = MarkdownIt().enable("table")

    def analyze(self, text: str) -> ContentAnalysis:
        """
        Single-pass analysis producing ContentAnalysis.

        This replaces the old dual invocation pattern where parser was called
        once in orchestrator and again for preamble.

        Args:
            text: Markdown text to analyze

        Returns:
            ContentAnalysis with all metrics

        Raises:
            ParsingError: If markdown cannot be parsed
        """
        if not text:
            return self._create_empty_analysis()

        try:
            # Parse to tokens
            tokens = self._md.parse(text)

            # Extract structural elements in parallel
            code_blocks = self._extract_code_blocks(tokens, text)
            headers = self._extract_headers(tokens, text)
            tables = self._extract_tables(tokens, text)

            # Calculate metrics
            total_chars = len(text)
            total_lines = text.count("\n") + 1

            code_chars = sum(len(cb.content) for cb in code_blocks)
            table_chars = sum(len(t.content) for t in tables)
            text_chars = total_chars - code_chars - table_chars

            code_ratio = code_chars / total_chars if total_chars > 0 else 0.0
            text_ratio = text_chars / total_chars if total_chars > 0 else 0.0

            # Determine content type
            content_type = self._determine_content_type(code_ratio)

            # Extract languages
            languages = {cb.language for cb in code_blocks if cb.language}

            return ContentAnalysis(
                total_chars=total_chars,
                total_lines=total_lines,
                code_ratio=code_ratio,
                text_ratio=text_ratio,
                code_block_count=len(code_blocks),
                header_count=len(headers),
                max_header_depth=max((h.level for h in headers), default=0),
                table_count=len(tables),
                content_type=content_type,
                languages=languages,
                code_blocks=code_blocks,
                headers=headers,
                tables=tables,
            )

        except Exception as e:
            raise ParsingError(f"Failed to parse markdown: {e}") from e

    def _extract_code_blocks(self, tokens: List, text: str) -> List[FencedBlock]:
        """
        Extract all fenced code blocks from tokens.

        Args:
            tokens: markdown-it-py tokens
            text: Original text for line number calculation

        Returns:
            List of FencedBlock objects
        """
        blocks: List[FencedBlock] = []

        for token in tokens:
            if token.type == "fence":
                # Extract code content
                content = token.content
                language = token.info.strip() if token.info else ""

                # Calculate line numbers
                if token.map:
                    start_line = token.map[0] + 1  # Convert to 1-based
                    end_line = token.map[1]  # Already 1-based end
                else:
                    start_line = 1
                    end_line = 1

                blocks.append(
                    FencedBlock(
                        content=content,
                        language=language,
                        fence_type="```",  # markdown-it normalizes
                        start_line=start_line,
                        end_line=end_line,
                    )
                )

        return blocks

    def _extract_headers(self, tokens: List, text: str) -> List[Header]:
        """
        Extract all headers from tokens.

        Args:
            tokens: markdown-it-py tokens
            text: Original text for line number calculation

        Returns:
            List of Header objects
        """
        headers: List[Header] = []

        for i, token in enumerate(tokens):
            if token.type == "heading_open":
                # Extract level from tag (h1 -> 1, h2 -> 2, etc.)
                level = int(token.tag[1])

                # Next token should be inline with header text
                if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                    header_text = tokens[i + 1].content

                    # Calculate line number
                    if token.map:
                        line_number = token.map[0] + 1  # Convert to 1-based
                    else:
                        line_number = 1

                    headers.append(
                        Header(level=level, text=header_text, line_number=line_number)
                    )

        return headers

    def _extract_tables(self, tokens: List, text: str) -> List[Table]:
        """
        Extract all tables from tokens.

        Args:
            tokens: markdown-it-py tokens
            text: Original text for extracting table content

        Returns:
            List of Table objects
        """
        tables: List[Table] = []
        lines = text.split("\n")

        in_table = False
        table_start = 0
        table_end = 0
        table_rows = 0

        for token in tokens:
            if token.type == "table_open":
                in_table = True
                if token.map:
                    table_start = token.map[0]
                table_rows = 0

            elif token.type == "table_close":
                in_table = False
                if token.map:
                    table_end = token.map[1]
                else:
                    table_end = table_start + 3  # Default minimal table size

                # Ensure valid line range
                if table_end <= table_start:
                    table_end = table_start + 3

                # Extract table content
                table_content = "\n".join(lines[table_start:table_end])

                tables.append(
                    Table(
                        content=table_content,
                        start_line=table_start + 1,  # 1-based
                        end_line=max(table_start + 1, table_end),  # Ensure end >= start
                        row_count=table_rows,
                    )
                )

            elif in_table and token.type == "tr_close":
                table_rows += 1

        return tables

    def _determine_content_type(self, code_ratio: float) -> str:
        """
        Determine content type based on code ratio.

        Args:
            code_ratio: Proportion of code content (0.0-1.0)

        Returns:
            "code", "mixed", or "text"
        """
        if code_ratio >= 0.3:
            return "code"
        elif code_ratio >= 0.1:
            return "mixed"
        else:
            return "text"

    def _create_empty_analysis(self) -> ContentAnalysis:
        """Create analysis for empty document."""
        return ContentAnalysis(
            total_chars=0,
            total_lines=0,
            code_ratio=0.0,
            text_ratio=0.0,
            code_block_count=0,
            header_count=0,
            max_header_depth=0,
            table_count=0,
            content_type="text",
            languages=set(),
        )
