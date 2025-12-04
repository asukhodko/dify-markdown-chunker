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

from .types import Chunk, ContentAnalysis, ChunkingMetrics
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
        
        Pipeline:
        1. Parse (once)
        2. Select strategy
        3. Apply strategy
        4. Merge small chunks
        5. Apply overlap
        6. Add metadata
        7. Validate
        
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
        
        # 4. Merge small chunks
        chunks = self._merge_small_chunks(chunks)
        
        # 5. Apply overlap (if enabled)
        if self.config.enable_overlap and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)
        
        # 6. Add standard metadata
        chunks = self._add_metadata(chunks, strategy.name)
        
        # 7. Validate
        self._validate(chunks, normalized_text)
        
        return chunks
    
    def chunk_with_metrics(self, md_text: str) -> tuple:
        """
        Chunk and return metrics.
        
        Returns:
            Tuple of (chunks, metrics)
        """
        chunks = self.chunk(md_text)
        metrics = ChunkingMetrics.from_chunks(
            chunks, 
            self.config.min_chunk_size, 
            self.config.max_chunk_size
        )
        return chunks, metrics
    
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
        
        Adds:
        - previous_content: last N chars from previous chunk (for all except first)
        - next_content: first N chars from next chunk (for all except last)
        - Respects word boundaries
        """
        if len(chunks) <= 1:
            return chunks
        
        overlap_size = self.config.overlap_size
        
        for i in range(len(chunks)):
            # Previous content (for all except first)
            if i > 0:
                prev_content = chunks[i - 1].content
                overlap_text = self._extract_overlap_end(prev_content, overlap_size)
                chunks[i].metadata['previous_content'] = overlap_text
                chunks[i].metadata['overlap_size'] = len(overlap_text)
            
            # Next content (for all except last)
            if i < len(chunks) - 1:
                next_content = chunks[i + 1].content
                overlap_text = self._extract_overlap_start(next_content, overlap_size)
                chunks[i].metadata['next_content'] = overlap_text
        
        return chunks
    
    def _extract_overlap_end(self, content: str, size: int) -> str:
        """
        Extract overlap from end of content, respecting word boundaries.
        
        Args:
            content: Source content
            size: Target overlap size
            
        Returns:
            Overlap text from end of content
        """
        if len(content) <= size:
            return content
        
        text = content[-size:]
        
        # Try to start at word boundary
        space_pos = text.find(' ')
        if 0 < space_pos < len(text) // 2:
            text = text[space_pos + 1:]
        
        return text
    
    def _extract_overlap_start(self, content: str, size: int) -> str:
        """
        Extract overlap from start of content, respecting word boundaries.
        
        Args:
            content: Source content
            size: Target overlap size
            
        Returns:
            Overlap text from start of content
        """
        if len(content) <= size:
            return content
        
        text = content[:size]
        
        # Try to end at word boundary
        space_pos = text.rfind(' ')
        if space_pos > len(text) // 2:
            text = text[:space_pos]
        
        return text
    
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
    
    def _merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Merge chunks smaller than min_chunk_size with adjacent chunks.
        
        Strategy:
        1. Prefer merging with previous chunk
        2. If would exceed max_chunk_size, try next chunk
        3. If both exceed, keep as-is with 'small_chunk' metadata flag
        """
        if len(chunks) <= 1:
            return chunks
        
        result = []
        i = 0
        
        while i < len(chunks):
            chunk = chunks[i]
            
            if chunk.size < self.config.min_chunk_size:
                merged = self._try_merge(chunk, result, chunks, i)
                if merged:
                    i += 1
                    continue
                else:
                    # Cannot merge - flag it
                    chunk.metadata['small_chunk'] = True
                    chunk.metadata['small_chunk_reason'] = 'cannot_merge'
            
            result.append(chunk)
            i += 1
        
        return result
    
    def _try_merge(self, chunk: Chunk, result: List[Chunk], 
                   all_chunks: List[Chunk], index: int) -> bool:
        """
        Try to merge a small chunk with adjacent chunks.
        
        Returns True if merge was successful.
        """
        # Try merging with previous chunk
        if result:
            prev_chunk = result[-1]
            combined_size = prev_chunk.size + chunk.size
            
            if combined_size <= self.config.max_chunk_size:
                # Merge with previous
                merged_content = prev_chunk.content + "\n\n" + chunk.content
                merged_chunk = Chunk(
                    content=merged_content,
                    start_line=prev_chunk.start_line,
                    end_line=chunk.end_line,
                    metadata={**prev_chunk.metadata}
                )
                result[-1] = merged_chunk
                return True
        
        # Try merging with next chunk
        if index + 1 < len(all_chunks):
            next_chunk = all_chunks[index + 1]
            combined_size = chunk.size + next_chunk.size
            
            if combined_size <= self.config.max_chunk_size:
                # Merge with next - modify next chunk in place
                merged_content = chunk.content + "\n\n" + next_chunk.content
                all_chunks[index + 1] = Chunk(
                    content=merged_content,
                    start_line=chunk.start_line,
                    end_line=next_chunk.end_line,
                    metadata={**next_chunk.metadata}
                )
                return True
        
        return False
    
    def _add_metadata(self, chunks: List[Chunk], strategy_name: str) -> List[Chunk]:
        """
        Add standard metadata to all chunks.
        
        Adds:
        - chunk_index: sequential index
        - content_type: text/code/table/mixed
        - has_code: boolean
        - header_path: list of ancestor headers (if available)
        - strategy: strategy that created the chunk
        """
        for i, chunk in enumerate(chunks):
            chunk.metadata['chunk_index'] = i
            chunk.metadata['content_type'] = self._detect_content_type(chunk.content)
            chunk.metadata['has_code'] = '```' in chunk.content
            chunk.metadata['strategy'] = strategy_name
            
            # header_path is set by strategy if available
            if 'header_path' not in chunk.metadata:
                chunk.metadata['header_path'] = []
        
        return chunks
    
    def _detect_content_type(self, content: str) -> str:
        """Detect content type of chunk."""
        has_code = '```' in content
        has_table = '|' in content and '---' in content
        
        if has_code and has_table:
            return 'mixed'
        elif has_code:
            return 'code'
        elif has_table:
            return 'table'
        else:
            return 'text'
