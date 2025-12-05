"""
Structural strategy for markdown_chunker v2.

For documents with hierarchical headers.
Simplified from 1720 lines to ~150 lines.
"""

from typing import List

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
            
            # Build header path
            header_path = self._build_header_path(headers[:i + 1])
            
            # Check if section fits in one chunk
            if len(section_content) <= config.max_chunk_size:
                chunks.append(self._create_chunk(
                    section_content,
                    start_line,
                    end_line,
                    content_type="section",
                    header_path=header_path,
                    header_level=header.level,
                ))
            else:
                # Split large section
                section_chunks = self._split_text_to_size(
                    section_content,
                    start_line,
                    config
                )
                for chunk in section_chunks:
                    chunk.metadata["header_path"] = header_path
                    chunk.metadata["header_level"] = header.level
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
