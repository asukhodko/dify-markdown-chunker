"""
Simplified markdown parser for v2.

Single file (~500 lines) instead of 15 files.
Line ending normalization at the start of pipeline.
"""

import re
from typing import List, Tuple

from .types import ContentAnalysis, FencedBlock, Header, TableBlock


class Parser:
    """
    Markdown document parser.
    
    Extracts:
    - Code blocks (fenced)
    - Headers
    - Tables
    - Content metrics
    
    All line endings are normalized to Unix-style (\\n) before processing.
    """
    
    # Regex patterns
    CODE_BLOCK_PATTERN = re.compile(
        r'^(`{3,})(\w*)\n(.*?)\n\1',
        re.MULTILINE | re.DOTALL
    )
    
    HEADER_PATTERN = re.compile(
        r'^(#{1,6})\s+(.+)$',
        re.MULTILINE
    )
    
    def analyze(self, md_text: str) -> ContentAnalysis:
        """
        Analyze a markdown document.
        
        Args:
            md_text: Raw markdown text
            
        Returns:
            ContentAnalysis with metrics and extracted elements
        """
        # 1. Normalize line endings (CRITICAL - must be first)
        md_text = self._normalize_line_endings(md_text)
        
        # 2. Extract elements
        code_blocks = self._extract_code_blocks(md_text)
        headers = self._extract_headers(md_text)
        tables = self._extract_tables(md_text)
        
        # 3. Calculate metrics
        total_chars = len(md_text)
        total_lines = md_text.count('\n') + 1 if md_text else 0
        
        code_chars = sum(len(b.content) for b in code_blocks)
        code_ratio = code_chars / total_chars if total_chars > 0 else 0.0
        
        max_header_depth = max((h.level for h in headers), default=0)
        
        # 4. Detect preamble
        has_preamble, preamble_end = self._detect_preamble(md_text, headers)
        
        return ContentAnalysis(
            total_chars=total_chars,
            total_lines=total_lines,
            code_ratio=code_ratio,
            code_block_count=len(code_blocks),
            header_count=len(headers),
            max_header_depth=max_header_depth,
            table_count=len(tables),
            code_blocks=code_blocks,
            headers=headers,
            tables=tables,
            has_preamble=has_preamble,
            preamble_end_line=preamble_end,
        )
    
    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize all line endings to Unix-style (\\n).
        
        Handles:
        - Windows: \\r\\n -> \\n
        - Old Mac: \\r -> \\n
        
        This MUST be called before any other processing.
        """
        # First convert CRLF to LF, then convert remaining CR to LF
        return text.replace('\r\n', '\n').replace('\r', '\n')
    
    def _extract_code_blocks(self, md_text: str) -> List[FencedBlock]:
        """
        Extract fenced code blocks.
        
        Handles:
        - Standard ``` fences
        - Language specifiers (```python)
        - Multiple backticks (````, `````)
        """
        blocks = []
        lines = md_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check for fence start
            fence_match = re.match(r'^(`{3,})(\w*)$', line)
            if fence_match:
                fence = fence_match.group(1)
                language = fence_match.group(2) or None
                start_line = i + 1  # 1-indexed
                start_pos = sum(len(lines[j]) + 1 for j in range(i))
                
                # Find matching fence end
                content_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith(fence) and lines[i].strip() == fence:
                        break
                    content_lines.append(lines[i])
                    i += 1
                
                end_line = min(i + 1, len(lines))  # 1-indexed, capped at file length
                end_pos = sum(len(lines[j]) + 1 for j in range(min(i + 1, len(lines))))
                
                blocks.append(FencedBlock(
                    language=language,
                    content='\n'.join(content_lines),
                    start_line=start_line,
                    end_line=end_line,
                    start_pos=start_pos,
                    end_pos=end_pos,
                ))
            
            i += 1
        
        return blocks
    
    def _extract_headers(self, md_text: str) -> List[Header]:
        """
        Extract markdown headers.
        
        Handles:
        - ATX headers (# through ######)
        - Ignores headers inside code blocks
        """
        headers = []
        lines = md_text.split('\n')
        
        # Track code block state to skip headers inside code
        in_code_block = False
        fence_pattern = re.compile(r'^`{3,}')
        
        for i, line in enumerate(lines):
            # Toggle code block state
            if fence_pattern.match(line):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            # Check for header
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                level = len(header_match.group(1))
                text = header_match.group(2).strip()
                pos = sum(len(lines[j]) + 1 for j in range(i))
                
                headers.append(Header(
                    level=level,
                    text=text,
                    line=i + 1,  # 1-indexed
                    pos=pos,
                ))
        
        return headers
    
    def _extract_tables(self, md_text: str) -> List[TableBlock]:
        """
        Extract markdown tables.
        
        A table is identified by:
        - Row with | characters
        - Followed by separator row with |---|
        """
        tables = []
        lines = md_text.split('\n')
        
        # Track code block state
        in_code_block = False
        fence_pattern = re.compile(r'^`{3,}')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Toggle code block state
            if fence_pattern.match(line):
                in_code_block = not in_code_block
                i += 1
                continue
            
            if in_code_block:
                i += 1
                continue
            
            # Check for table start: line with | followed by separator
            if '|' in line and i + 1 < len(lines):
                next_line = lines[i + 1]
                if '|' in next_line and re.search(r'-{3,}', next_line):
                    # Found table
                    start_line = i + 1  # 1-indexed
                    table_lines = [line, next_line]
                    
                    # Count columns from header
                    column_count = line.count('|') - 1
                    if line.startswith('|'):
                        column_count = line.count('|') - 1
                    
                    # Collect remaining rows
                    i += 2
                    while i < len(lines) and '|' in lines[i]:
                        table_lines.append(lines[i])
                        i += 1
                    
                    end_line = i  # 1-indexed (line after last table row)
                    row_count = len(table_lines) - 2  # Exclude header and separator
                    
                    tables.append(TableBlock(
                        content='\n'.join(table_lines),
                        start_line=start_line,
                        end_line=end_line,
                        column_count=max(column_count, 1),
                        row_count=max(row_count, 0),
                    ))
                    continue
            
            i += 1
        
        return tables
    
    def _detect_preamble(self, md_text: str, headers: List[Header]) -> Tuple[bool, int]:
        """
        Detect if document has preamble (content before first header).
        
        Returns:
            Tuple of (has_preamble, preamble_end_line)
        """
        if not headers:
            # No headers = entire document could be preamble
            return False, 0
        
        first_header_line = headers[0].line
        
        # Check if there's non-whitespace content before first header
        lines = md_text.split('\n')
        for i in range(first_header_line - 1):
            if lines[i].strip():
                return True, first_header_line - 1
        
        return False, 0
    
    def get_line_at_position(self, md_text: str, pos: int) -> int:
        """
        Get line number (1-indexed) for character position.
        """
        return md_text[:pos].count('\n') + 1
    
    def get_position_at_line(self, md_text: str, line: int) -> int:
        """
        Get character position for start of line (1-indexed).
        """
        lines = md_text.split('\n')
        return sum(len(lines[i]) + 1 for i in range(line - 1))
