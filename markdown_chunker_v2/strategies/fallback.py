"""
Fallback strategy for markdown_chunker v2.

Universal strategy that works for any document.
Splits by paragraphs and groups to max_chunk_size.
"""

from typing import List

from ..types import Chunk, ContentAnalysis
from ..config import ChunkConfig
from .base import BaseStrategy


class FallbackStrategy(BaseStrategy):
    """
    Universal fallback strategy.
    
    Works for any document by splitting on paragraph boundaries
    and grouping paragraphs to fit within max_chunk_size.
    
    Priority: 3 (lowest - used when no other strategy applies)
    """
    
    @property
    def name(self) -> str:
        return "fallback"
    
    @property
    def priority(self) -> int:
        return 3
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """Always returns True - fallback handles everything."""
        return True
    
    def apply(
        self,
        md_text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply fallback strategy.
        
        Splits document by paragraphs and groups them to fit max_chunk_size.
        """
        if not md_text.strip():
            return []
        
        # Split by double newlines (paragraphs)
        paragraphs = md_text.split('\n\n')
        
        chunks = []
        current_content = ""
        current_start_line = 1
        current_line = 1
        
        for para in paragraphs:
            if not para.strip():
                current_line += para.count('\n') + 2
                continue
            
            para_with_sep = para + '\n\n'
            para_lines = para.count('\n') + 2
            
            # Check if adding this paragraph exceeds limit
            if current_content and len(current_content) + len(para_with_sep) > config.max_chunk_size:
                # Save current chunk
                if current_content.strip():
                    end_line = current_line - 1
                    chunks.append(self._create_chunk(
                        current_content.rstrip(),
                        current_start_line,
                        end_line,
                    ))
                
                # Start new chunk
                current_content = para_with_sep
                current_start_line = current_line
                current_line += para_lines
            else:
                current_content += para_with_sep
                current_line += para_lines
        
        # Save last chunk
        if current_content.strip():
            end_line = current_line - 1
            chunks.append(self._create_chunk(
                current_content.rstrip(),
                current_start_line,
                max(end_line, current_start_line),
            ))
        
        return chunks
