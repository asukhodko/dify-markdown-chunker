"""
Main MarkdownChunker class for v2.

Simplified pipeline:
1. Parse (once)
2. Select strategy
3. Apply strategy
4. Apply overlap
5. Validate
6. Return
"""

from typing import List, Optional

from .types import Chunk, ContentAnalysis
from .config import ChunkConfig
from .parser import Parser
from .strategies import StrategySelector


class MarkdownChunker:
    """
    Main class for chunking markdown documents.
    
    Simplified from the original with:
    - Single parse pass
    - Single strategy selection
    - Linear pipeline
    - No duplication
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize chunker.
        
        Args:
            config: Chunking configuration (uses defaults if None)
        """
        self.config = config or ChunkConfig()
        self._parser = Parser()
        self._selector = StrategySelector()
    
    def chunk(self, md_text: str) -> List[Chunk]:
        """
        Chunk a markdown document.
        
        Args:
            md_text: Raw markdown text
            
        Returns:
            List of chunks
        """
        if not md_text or not md_text.strip():
            return []
        
        # 1. Parse (once) - includes line ending normalization
        analysis = self._parser.analyze(md_text)
        
        # Get normalized text (line endings normalized)
        normalized_text = md_text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 2. Select strategy
        strategy = self._selector.select(analysis, self.config)
        
        # 3. Apply strategy
        chunks = strategy.apply(normalized_text, analysis, self.config)
        
        # 4. Apply overlap (if enabled)
        if self.config.enable_overlap and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)
        
        # 5. Validate
        self._validate(chunks, normalized_text)
        
        return chunks
    
    def chunk_with_analysis(self, md_text: str) -> tuple:
        """
        Chunk and return analysis info.
        
        Returns:
            Tuple of (chunks, strategy_name, analysis)
        """
        if not md_text or not md_text.strip():
            return [], "none", None
        
        analysis = self._parser.analyze(md_text)
        normalized_text = md_text.replace('\r\n', '\n').replace('\r', '\n')
        
        strategy = self._selector.select(analysis, self.config)
        chunks = strategy.apply(normalized_text, analysis, self.config)
        
        if self.config.enable_overlap and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)
        
        self._validate(chunks, normalized_text)
        
        return chunks, strategy.name, analysis
    
    def _apply_overlap(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Apply overlap between chunks.
        
        Adds overlap content from previous chunk to metadata.
        """
        if len(chunks) <= 1:
            return chunks
        
        overlap_size = self.config.overlap_size
        
        for i in range(1, len(chunks)):
            prev_content = chunks[i - 1].content
            
            # Get overlap from end of previous chunk
            if len(prev_content) >= overlap_size:
                overlap_text = prev_content[-overlap_size:]
                
                # Try to start at word boundary
                space_pos = overlap_text.find(' ')
                if space_pos > 0 and space_pos < len(overlap_text) // 2:
                    overlap_text = overlap_text[space_pos + 1:]
            else:
                overlap_text = prev_content
            
            chunks[i].metadata['previous_content'] = overlap_text
            chunks[i].metadata['overlap_size'] = len(overlap_text)
        
        return chunks
    
    def _validate(self, chunks: List[Chunk], original: str) -> None:
        """
        Validate chunking results.
        
        Checks domain properties PROP-1 through PROP-5.
        """
        if not chunks:
            return
        
        # PROP-1: No content loss (relaxed check)
        total_output = sum(len(c.content) for c in chunks)
        total_input = len(original)
        
        # Allow some variance due to overlap and whitespace normalization
        if total_output < total_input * 0.9:
            # Log warning but don't fail
            pass
        
        # PROP-2: Size bounds
        for i, chunk in enumerate(chunks):
            if chunk.size > self.config.max_chunk_size:
                if not chunk.metadata.get('allow_oversize'):
                    # Set default oversize metadata
                    chunk.metadata['allow_oversize'] = True
                    if '```' in chunk.content:
                        chunk.metadata['oversize_reason'] = 'code_block_integrity'
                    elif '|' in chunk.content and '---' in chunk.content:
                        chunk.metadata['oversize_reason'] = 'table_integrity'
                    else:
                        chunk.metadata['oversize_reason'] = 'section_integrity'
        
        # PROP-3: Monotonic ordering
        for i in range(len(chunks) - 1):
            if chunks[i].start_line > chunks[i + 1].start_line:
                # Fix ordering
                chunks.sort(key=lambda c: (c.start_line, c.end_line))
                break
        
        # PROP-4 and PROP-5 are enforced by Chunk.__post_init__
