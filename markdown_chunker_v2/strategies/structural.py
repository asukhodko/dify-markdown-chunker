"""
Structural strategy for markdown_chunker v2.

For documents with hierarchical headers.
Simplified from 1720 lines to ~150 lines.
"""

import re
from typing import List, Tuple

from ..types import Chunk, ContentAnalysis, Header
from ..config import ChunkConfig
from .base import BaseStrategy


class StructuralStrategy(BaseStrategy):
    """
    Strategy for structured documents with headers.
    
    Splits document by headers, maintaining header hierarchy.
    
    Priority: 2 (used when document has headers but no code/tables)
    """
    
    @property
    def name(self) -> str:
        return "structural"
    
    @property
    def priority(self) -> int:
        return 2
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Can handle if document has enough headers and hierarchy.
        """
        return (
            analysis.header_count >= config.structure_threshold and
            analysis.max_header_depth > 1
        )
    
    def apply(
        self,
        md_text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply structural strategy.
        
        Splits document by headers into sections.
        """
        if not md_text.strip():
            return []
        
        lines = md_text.split('\n')
        headers = analysis.headers
        
        if not headers:
            # No headers - use fallback behavior
            return self._split_text_to_size(md_text, 1, config)
        
        chunks = []
        
        # Handle preamble (content before first header)
        # Preamble gets special header_path "/__preamble__" to distinguish from structural content
        first_header_line = headers[0].line if headers else len(lines) + 1
        if first_header_line > 1:
            preamble_lines = lines[:first_header_line - 1]
            preamble_content = '\n'.join(preamble_lines)
            if preamble_content.strip():
                chunks.append(self._create_chunk(
                    preamble_content,
                    1,
                    first_header_line - 1,
                    content_type="preamble",
                    header_path="/__preamble__",
                ))
        
        # Process sections between headers
        for i, header in enumerate(headers):
            # Determine section boundaries
            start_line = header.line
            
            if i + 1 < len(headers):
                end_line = headers[i + 1].line - 1
            else:
                end_line = len(lines)
            
            # Extract section content
            section_lines = lines[start_line - 1:end_line]
            section_content = '\n'.join(section_lines)
            
            if not section_content.strip():
                continue
            
            # Check if section fits in one chunk
            if len(section_content) <= config.max_chunk_size:
                # Build header_path from FIRST header in chunk content
                header_path, sub_headers = self._build_header_path_for_chunk(
                    section_content, headers, start_line
                )
                
                chunk_meta = {
                    "content_type": "section",
                    "header_path": header_path,
                    "header_level": header.level,
                }
                if sub_headers:
                    chunk_meta["sub_headers"] = sub_headers
                
                chunks.append(self._create_chunk(
                    section_content,
                    start_line,
                    end_line,
                    **chunk_meta,
                ))
            else:
                # Split large section
                section_chunks = self._split_text_to_size(
                    section_content,
                    start_line,
                    config
                )
                # Set header_path for each sub-chunk based on its content
                for chunk in section_chunks:
                    chunk_path, chunk_sub = self._build_header_path_for_chunk(
                        chunk.content, headers, chunk.start_line
                    )
                    # If chunk has no headers, use the section's header path
                    if not chunk_path:
                        chunk_path = self._build_header_path(headers[:i + 1])
                    chunk.metadata["header_path"] = chunk_path
                    chunk.metadata["header_level"] = header.level
                    if chunk_sub:
                        chunk.metadata["sub_headers"] = chunk_sub
                chunks.extend(section_chunks)
        
        return chunks
    
    def _build_header_path(self, headers: List[Header]) -> str:
        """
        Build header path from header hierarchy.
        
        Example: "/Chapter 1/Section 1.1/Subsection"
        """
        if not headers:
            return "/"
        
        # Build path maintaining hierarchy
        path_parts = []
        current_level = 0
        
        for header in headers:
            if header.level > current_level:
                path_parts.append(header.text)
            elif header.level == current_level:
                if path_parts:
                    path_parts[-1] = header.text
                else:
                    path_parts.append(header.text)
            else:
                # Going up in hierarchy
                while len(path_parts) > header.level - 1:
                    path_parts.pop()
                path_parts.append(header.text)
            
            current_level = header.level
        
        return "/" + "/".join(path_parts)
    
    def _find_headers_in_range(
        self, 
        headers: List[Header], 
        start_line: int, 
        end_line: int
    ) -> List[Header]:
        """
        Find all headers within a line range.
        
        Args:
            headers: List of all headers in document
            start_line: Start line (1-indexed, inclusive)
            end_line: End line (1-indexed, inclusive)
            
        Returns:
            List of headers within the range
        """
        return [h for h in headers if start_line <= h.line <= end_line]
    
    def _find_headers_in_content(self, content: str) -> List[Tuple[int, str]]:
        """
        Find headers directly in chunk content.
        
        Args:
            content: Chunk text content
            
        Returns:
            List of (level, text) tuples for each header found
        """
        headers = []
        in_code_block = False
        
        for line in content.split('\n'):
            # Track code blocks to skip headers inside them
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            # Check for ATX header
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headers.append((level, text))
        
        return headers
    
    def _build_header_path_for_chunk(
        self, 
        chunk_content: str, 
        all_headers: List[Header],
        chunk_start_line: int
    ) -> Tuple[str, List[str]]:
        """
        Build header_path based on FIRST header in chunk content.
        
        This ensures header_path reflects the primary section of the chunk,
        not the last header encountered before the chunk.
        
        Args:
            chunk_content: The text content of the chunk
            all_headers: All headers in the document (for building hierarchy)
            chunk_start_line: Starting line of the chunk (1-indexed)
            
        Returns:
            Tuple of (header_path, sub_headers_list)
            - header_path: Path to first header in chunk
            - sub_headers_list: List of additional header texts in chunk
        """
        # Find headers in chunk content
        chunk_headers = self._find_headers_in_content(chunk_content)
        
        if not chunk_headers:
            # No headers in chunk - return empty
            return "", []
        
        first_level, first_text = chunk_headers[0]
        
        # Build hierarchy path for the first header
        # Find all ancestor headers (headers before this chunk with lower level)
        ancestors = []
        for h in all_headers:
            if h.line >= chunk_start_line:
                break
            # Keep track of hierarchy
            if h.level < first_level:
                # This could be an ancestor
                # Remove any ancestors at same or higher level
                while ancestors and ancestors[-1].level >= h.level:
                    ancestors.pop()
                ancestors.append(h)
        
        # Build path from ancestors + first header
        path_parts = [h.text for h in ancestors]
        path_parts.append(first_text)
        
        header_path = "/" + "/".join(path_parts)
        
        # Collect sub_headers (additional headers after the first)
        sub_headers = [text for _, text in chunk_headers[1:]]
        
        return header_path, sub_headers
