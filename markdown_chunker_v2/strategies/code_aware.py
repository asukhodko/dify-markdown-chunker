"""
Code-aware strategy for markdown_chunker v2.

For documents with code blocks or tables.
Consolidates CodeStrategy + MixedStrategy + TableStrategy.
"""

from typing import List, Tuple

from ..types import Chunk, ContentAnalysis, FencedBlock, TableBlock
from ..config import ChunkConfig
from .base import BaseStrategy


class CodeAwareStrategy(BaseStrategy):
    """
    Strategy for documents with code blocks or tables.
    
    Preserves atomic blocks (code, tables) intact.
    Splits text around atomic blocks.
    
    Priority: 1 (highest - used when document has code or tables)
    """
    
    @property
    def name(self) -> str:
        return "code_aware"
    
    @property
    def priority(self) -> int:
        return 1
    
    def can_handle(self, analysis: ContentAnalysis, config: ChunkConfig) -> bool:
        """
        Can handle if document has code blocks or tables.
        """
        return (
            analysis.code_block_count >= 1 or
            analysis.table_count >= 1 or
            analysis.code_ratio >= config.code_threshold
        )
    
    def apply(
        self,
        md_text: str,
        analysis: ContentAnalysis,
        config: ChunkConfig
    ) -> List[Chunk]:
        """
        Apply code-aware strategy.
        
        1. Identify atomic blocks (code, tables)
        2. Split document around atomic blocks
        3. Create chunks preserving atomic blocks
        """
        if not md_text.strip():
            return []
        
        lines = md_text.split('\n')
        
        # Get atomic block ranges
        atomic_ranges = self._get_atomic_ranges(analysis)
        
        if not atomic_ranges:
            # No atomic blocks - use simple splitting
            return self._split_text_to_size(md_text, 1, config)
        
        chunks = []
        current_line = 1
        
        for block_start, block_end, block_type in atomic_ranges:
            # Handle text before atomic block
            if current_line < block_start:
                text_lines = lines[current_line - 1:block_start - 1]
                text_content = '\n'.join(text_lines)
                
                if text_content.strip():
                    text_chunks = self._split_text_to_size(
                        text_content,
                        current_line,
                        config
                    )
                    chunks.extend(text_chunks)
            
            # Handle atomic block
            block_lines = lines[block_start - 1:block_end]
            block_content = '\n'.join(block_lines)
            
            if block_content.strip():
                chunk = self._create_chunk(
                    block_content,
                    block_start,
                    block_end,
                    content_type=block_type,
                    is_atomic=True,
                )
                
                # Set oversize metadata if needed
                if chunk.size > config.max_chunk_size:
                    reason = "code_block_integrity" if block_type == "code" else "table_integrity"
                    self._set_oversize_metadata(chunk, reason, config)
                
                chunks.append(chunk)
            
            current_line = block_end + 1
        
        # Handle text after last atomic block
        if current_line <= len(lines):
            text_lines = lines[current_line - 1:]
            text_content = '\n'.join(text_lines)
            
            if text_content.strip():
                text_chunks = self._split_text_to_size(
                    text_content,
                    current_line,
                    config
                )
                chunks.extend(text_chunks)
        
        # Ensure fence balance
        chunks = self._ensure_fence_balance(chunks)
        
        return chunks
    
    def _get_atomic_ranges(
        self,
        analysis: ContentAnalysis
    ) -> List[Tuple[int, int, str]]:
        """
        Get line ranges of atomic blocks.
        
        Returns list of (start_line, end_line, block_type) tuples,
        sorted by start_line.
        """
        ranges = []
        
        # Add code blocks
        for block in analysis.code_blocks:
            ranges.append((block.start_line, block.end_line, "code"))
        
        # Add tables
        for table in analysis.tables:
            ranges.append((table.start_line, table.end_line, "table"))
        
        # Sort by start line
        ranges.sort(key=lambda x: x[0])
        
        return ranges
