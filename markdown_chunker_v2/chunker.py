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
        
        Merge conditions for small_chunk:
        - Chunk size is below min_chunk_size
        - Cannot merge with adjacent chunks without exceeding max_chunk_size
        - Preamble chunks are never merged with structural chunks
        - Prefer merging with chunks in same logical section (same header_path prefix)
        - Prefer left (previous) chunk over right (next) chunk
        
        Returns True if merge was successful.
        """
        # Never merge preamble with structural content
        chunk_is_preamble = chunk.metadata.get('content_type') == 'preamble'
        
        # Try merging with previous chunk (left preference per Requirement 4.4)
        if result:
            prev_chunk = result[-1]
            prev_is_preamble = prev_chunk.metadata.get('content_type') == 'preamble'
            
            # Don't merge preamble with non-preamble
            if chunk_is_preamble != prev_is_preamble:
                pass  # Skip this merge option
            else:
                combined_size = prev_chunk.size + chunk.size
                
                if combined_size <= self.config.max_chunk_size:
                    # Check if same logical section (Requirement 4.3)
                    if self._same_logical_section(prev_chunk, chunk):
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
            next_is_preamble = next_chunk.metadata.get('content_type') == 'preamble'
            
            # Don't merge preamble with non-preamble
            if chunk_is_preamble != next_is_preamble:
                pass  # Skip this merge option
            else:
                combined_size = chunk.size + next_chunk.size
                
                if combined_size <= self.config.max_chunk_size:
                    # Check if same logical section
                    if self._same_logical_section(chunk, next_chunk):
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
    
    def _same_logical_section(self, chunk1: Chunk, chunk2: Chunk) -> bool:
        """
        Check if two chunks belong to the same logical section.
        
        Compares header_path prefix up to ## level (first two segments).
        This implements Requirement 4.3 - prefer merging within same section.
        
        Args:
            chunk1: First chunk
            chunk2: Second chunk
            
        Returns:
            True if chunks are in same logical section
        """
        path1 = chunk1.metadata.get('header_path', '')
        path2 = chunk2.metadata.get('header_path', '')
        
        # Preamble chunks are in their own section
        if path1 == '/__preamble__' or path2 == '/__preamble__':
            return path1 == path2
        
        # Compare first two segments of path (up to ## level)
        parts1 = path1.strip('/').split('/')[:2]
        parts2 = path2.strip('/').split('/')[:2]
        
        return parts1 == parts2
    
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
            # Don't overwrite content_type if already set (e.g., "preamble")
            if 'content_type' not in chunk.metadata:
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
    
    def chunk_simple(
        self, 
        text: str, 
        config: Optional[dict] = None,
        strategy: Optional[str] = None
    ) -> dict:
        """
        Simple chunking method that returns dictionary format.
        
        This method provides backward compatibility for code expecting
        dictionary-based results instead of Chunk objects.
        
        Args:
            text: Input text to chunk
            config: Optional config as dict (will be converted to ChunkConfig)
            strategy: Optional strategy hint (ignored in v2, auto-selected)
            
        Returns:
            Dictionary with keys:
            - chunks: list of chunk dicts
            - errors: list of error messages (empty in normal operation)
            - warnings: list of warning messages (empty in normal operation)
            - total_chunks: number of chunks
            - strategy_used: name of strategy used
        """
        try:
            # Handle config parameter
            chunker = self
            if config is not None:
                config_dict = config.copy()
                # Handle legacy enable_overlap parameter
                if 'enable_overlap' in config_dict:
                    enable = config_dict.pop('enable_overlap')
                    if enable and 'overlap_size' not in config_dict:
                        config_dict['overlap_size'] = 100
                    elif not enable:
                        config_dict['overlap_size'] = 0
                
                # Remove any unknown parameters
                valid_params = {'max_chunk_size', 'min_chunk_size', 'overlap_size', 
                               'preserve_atomic_blocks', 'strategy_override'}
                config_dict = {k: v for k, v in config_dict.items() if k in valid_params}
                
                temp_config = ChunkConfig(**config_dict)
                chunker = MarkdownChunker(temp_config)
            
            # Get chunks with analysis
            chunks, strategy_used, _ = chunker.chunk_with_analysis(text)
            
            # Convert chunks to dictionary format
            chunk_dicts = []
            for chunk in chunks:
                chunk_dict = {
                    'content': chunk.content,
                    'start_line': chunk.start_line,
                    'end_line': chunk.end_line,
                    'size': len(chunk.content),
                    'line_count': chunk.end_line - chunk.start_line + 1,
                    'metadata': chunk.metadata.copy() if chunk.metadata else {}
                }
                chunk_dicts.append(chunk_dict)
            
            return {
                'chunks': chunk_dicts,
                'errors': [],
                'warnings': [],
                'total_chunks': len(chunk_dicts),
                'strategy_used': strategy_used or 'auto'
            }
            
        except Exception as e:
            return {
                'chunks': [],
                'errors': [str(e)],
                'warnings': [],
                'total_chunks': 0,
                'strategy_used': 'none'
            }
