# Implementation Phase Breakdown

This document provides detailed task breakdowns for each of the 6 implementation phases.

## Phase 1: Foundation (Days 1-3)

**Objective**: Establish new structure and write property tests

### Day 1: Project Setup

**Tasks**:
1. Create `/markdown_chunker_v2/` directory (parallel to current)
2. Set up git branch `feature/redesign-v2`
3. Create initial file structure (12 empty files)
4. Configure pytest for v2 directory
5. Configure mypy for strict type checking

**Deliverables**:
```
markdown_chunker_v2/
├── __init__.py (empty)
├── types.py (empty)
├── config.py (empty)
├── chunker.py (empty)
├── parser.py (empty)
├── strategies/
│   ├── __init__.py (empty)
│   ├── base.py (empty)
│   ├── code_aware.py (empty)
│   ├── structural.py (empty)
│   ├── table.py (empty)
│   └── fallback.py (empty)
└── utils.py (empty)

tests_v2/
├── property_tests/
│   ├── test_core_properties.py (skeleton)
│   ├── test_integrity_properties.py (skeleton)
│   ├── test_serialization_properties.py (skeleton)
│   └── test_metadata_properties.py (skeleton)
└── conftest.py
```

**Validation**: Directory structure created, pytest runs (no tests yet)

### Day 2: Core Data Types

**Tasks**:
1. Implement `types.py`:
   - Chunk dataclass with __post_init__ validation
   - ChunkingResult dataclass with to_dict/from_dict
   - ContentAnalysis dataclass
   - MarkdownNode dataclass (AST)
   - FencedBlock, Header, Table datatypes
2. Write unit tests for types (validation edge cases)

**Code Example** (Chunk):
```python
@dataclass
class Chunk:
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1 (1-based indexing)")
        if self.end_line < self.start_line:
            raise ValueError(f"end_line ({self.end_line}) must be >= start_line ({self.start_line})")
        if not self.content.strip():
            raise ValueError("chunk content cannot be empty or whitespace-only")
    
    @property
    def size(self) -> int:
        """Size in characters."""
        return len(self.content)
    
    @property
    def line_count(self) -> int:
        """Number of lines in chunk."""
        return self.end_line - self.start_line + 1
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata field."""
        self.metadata[key] = value
```

**Deliverables**:
- `types.py` (~600 lines)
- `test_types.py` (~100 lines)

**Validation**: `pytest tests_v2/test_types.py` passes

### Day 3: Configuration & Property Tests

**Tasks**:
1. Implement `config.py`:
   - ChunkConfig with 8 parameters
   - __post_init__ validation
   - Three factory methods (default, for_code_docs, for_rag)
2. Write 10 property-based tests using Hypothesis
3. Run property tests against **old codebase** to establish baseline

**Code Example** (Config):
```python
@dataclass
class ChunkConfig:
    # Size constraints (3)
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200
    
    # Behavior (3)
    preserve_atomic_blocks: bool = True
    extract_preamble: bool = True
    allow_oversize: bool = True
    
    # Strategy thresholds (2)
    code_threshold: float = 0.3
    structure_threshold: int = 3
    
    def __post_init__(self):
        if self.max_chunk_size < self.min_chunk_size:
            raise ValueError(
                f"max_chunk_size ({self.max_chunk_size}) must be >= "
                f"min_chunk_size ({self.min_chunk_size})"
            )
        if self.overlap_size < 0:
            raise ValueError("overlap_size must be >= 0")
        if self.overlap_size >= self.max_chunk_size:
            raise ValueError("overlap_size must be < max_chunk_size")
        if not 0 <= self.code_threshold <= 1:
            raise ValueError("code_threshold must be in [0, 1]")
        if self.structure_threshold < 1:
            raise ValueError("structure_threshold must be >= 1")
    
    @classmethod
    def default(cls) -> "ChunkConfig":
        """Balanced configuration for general markdown."""
        return cls()
    
    @classmethod
    def for_code_docs(cls) -> "ChunkConfig":
        """Optimized for technical documentation with code."""
        return cls(
            max_chunk_size=6144,
            code_threshold=0.2,  # more sensitive
            overlap_size=300,
        )
    
    @classmethod
    def for_rag(cls) -> "ChunkConfig":
        """Optimized for RAG/embedding systems."""
        return cls(
            max_chunk_size=2048,
            overlap_size=150,
        )
```

**Property Tests** (test_core_properties.py):
```python
from hypothesis import given, strategies as st
import pytest

@given(st.text(min_size=10, max_size=10000))
def test_property_no_content_loss(markdown_text):
    """
    PROP-1: No Content Loss
    
    For any markdown document, concatenating all chunk contents
    (after removing overlap) must equal the original document.
    """
    from markdown_chunker import MarkdownChunker, ChunkConfig
    
    chunker = MarkdownChunker(ChunkConfig.default())
    result = chunker.chunk(markdown_text)
    
    # Reconstruct document
    reconstructed = ""
    for i, chunk in enumerate(result.chunks):
        content = chunk.content
        
        # Remove overlap from previous chunk
        if i > 0 and "overlap_prev_size" in chunk.metadata:
            overlap_size = chunk.metadata["overlap_prev_size"]
            content = content[overlap_size:]
        
        # Remove overlap to next chunk
        if i < len(result.chunks) - 1 and "overlap_next_size" in chunk.metadata:
            overlap_size = chunk.metadata["overlap_next_size"]
            content = content[:-overlap_size]
        
        reconstructed += content
    
    # Normalize whitespace for comparison
    def normalize(text):
        return text.strip().replace('\r\n', '\n')
    
    assert normalize(reconstructed) == normalize(markdown_text), \
        "Reconstructed content does not match original"


@given(st.text(min_size=10, max_size=10000))
def test_property_size_bounds(markdown_text):
    """
    PROP-2: Size Bounds
    
    Every chunk must be <= max_chunk_size OR explicitly marked as oversize.
    """
    from markdown_chunker import MarkdownChunker, ChunkConfig
    
    config = ChunkConfig.default()
    chunker = MarkdownChunker(config)
    result = chunker.chunk(markdown_text)
    
    for i, chunk in enumerate(result.chunks):
        if chunk.size > config.max_chunk_size:
            # Must be marked as oversize
            assert chunk.metadata.get("allow_oversize") is True, \
                f"Chunk {i} exceeds max_chunk_size ({chunk.size} > {config.max_chunk_size}) " \
                f"but is not marked as allow_oversize"


@given(st.text(min_size=10, max_size=10000))
def test_property_monotonic_ordering(markdown_text):
    """
    PROP-3: Monotonic Ordering
    
    Chunks must appear in document order (start_line values non-decreasing).
    """
    from markdown_chunker import MarkdownChunker, ChunkConfig
    
    chunker = MarkdownChunker(ChunkConfig.default())
    result = chunker.chunk(markdown_text)
    
    for i in range(len(result.chunks) - 1):
        curr = result.chunks[i]
        next_chunk = result.chunks[i + 1]
        
        assert curr.start_line <= next_chunk.start_line, \
            f"Chunks out of order: chunk {i} starts at line {curr.start_line}, " \
            f"chunk {i+1} starts at line {next_chunk.start_line}"


@given(st.text(min_size=10, max_size=10000))
def test_property_no_empty_chunks(markdown_text):
    """
    PROP-4: No Empty Chunks
    
    No chunk may be empty or contain only whitespace.
    """
    from markdown_chunker import MarkdownChunker, ChunkConfig
    
    chunker = MarkdownChunker(ChunkConfig.default())
    result = chunker.chunk(markdown_text)
    
    for i, chunk in enumerate(result.chunks):
        assert chunk.content.strip(), \
            f"Chunk {i} is empty or whitespace-only"


@given(st.text(min_size=10, max_size=10000))
def test_property_valid_line_numbers(markdown_text):
    """
    PROP-5: Valid Line Numbers
    
    All chunks must have start_line >= 1 and end_line >= start_line.
    """
    from markdown_chunker import MarkdownChunker, ChunkConfig
    
    chunker = MarkdownChunker(ChunkConfig.default())
    result = chunker.chunk(markdown_text)
    
    for i, chunk in enumerate(result.chunks):
        assert chunk.start_line >= 1, \
            f"Chunk {i} has invalid start_line: {chunk.start_line} (must be >= 1)"
        assert chunk.end_line >= chunk.start_line, \
            f"Chunk {i} has end_line ({chunk.end_line}) < start_line ({chunk.start_line})"
```

**Deliverables**:
- `config.py` (~200 lines)
- `test_core_properties.py` (5 property tests)
- `test_integrity_properties.py` (2 property tests for code/table integrity)
- `test_serialization_properties.py` (2 property tests)
- `test_metadata_properties.py` (1 property test)

**Validation**:
- Config validation works (test invalid configs raise errors)
- Property tests run (may fail against old code - that's OK, baseline established)

**Phase 1 Completion Criteria**:
- ✓ Directory structure created
- ✓ types.py implemented and tested
- ✓ config.py implemented and tested
- ✓ 10 property tests written
- ✓ Property tests run successfully (against old or new code)

---

## Phase 2: Parser Redesign (Days 4-5)

**Objective**: Single-pass Stage1 analysis without dual invocation

### Day 4: Parser Implementation

**Tasks**:
1. Implement `parser.py` with single `analyze()` method
2. Use markdown-it-py for tokenization
3. Extract code blocks, headers, tables in one pass
4. Calculate ContentAnalysis metrics
5. Remove dependencies on mistune and markdown

**Code Structure** (parser.py):
```python
from markdown_it import MarkdownIt
from typing import List, Set
from .types import ContentAnalysis, FencedBlock, Header, Table

class Parser:
    """Markdown parser for Stage1 analysis (single-pass)."""
    
    def __init__(self):
        self._md = MarkdownIt()
    
    def analyze(self, text: str) -> ContentAnalysis:
        """
        Single-pass analysis producing ContentAnalysis.
        
        This replaces the old dual invocation pattern where
        parser was called once in orchestrator and again for preamble.
        
        Returns:
            ContentAnalysis with all metrics
        """
        if not text:
            return self._create_empty_analysis()
        
        # Parse to tokens
        tokens = self._md.parse(text)
        
        # Extract structural elements
        code_blocks = self._extract_code_blocks(tokens, text)
        headers = self._extract_headers(tokens, text)
        tables = self._extract_tables(tokens, text)
        
        # Calculate metrics
        total_chars = len(text)
        total_lines = text.count('\n') + 1
        
        code_chars = sum(len(cb.content) for cb in code_blocks)
        table_chars = sum(len(t.content) for t in tables)
        text_chars = total_chars - code_chars - table_chars
        
        code_ratio = code_chars / total_chars if total_chars > 0 else 0.0
        text_ratio = text_chars / total_chars if total_chars > 0 else 0.0
        
        # Determine content type
        if code_ratio >= 0.3:
            content_type = "code"
        elif code_ratio >= 0.1:
            content_type = "mixed"
        else:
            content_type = "text"
        
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
        )
    
    def _extract_code_blocks(
        self, tokens, text: str
    ) -> List[FencedBlock]:
        """Extract all fenced code blocks."""
        blocks = []
        
        for i, token in enumerate(tokens):
            if token.type == "fence":
                # Extract code content
                content = token.content
                language = token.info.strip() if token.info else ""
                
                # Calculate line numbers
                start_line = text[:token.map[0]].count('\n') + 1 if token.map else 0
                end_line = text[:token.map[1]].count('\n') + 1 if token.map else 0
                
                blocks.append(FencedBlock(
                    content=content,
                    language=language,
                    fence_type="```",  # markdown-it normalizes to ```
                    start_line=start_line,
                    end_line=end_line,
                ))
        
        return blocks
    
    def _extract_headers(
        self, tokens, text: str
    ) -> List[Header]:
        """Extract all headers."""
        headers = []
        
        for token in tokens:
            if token.type == "heading_open":
                level = int(token.tag[1])  # h1 -> 1, h2 -> 2, etc.
                
                # Next token should be inline with header text
                idx = tokens.index(token)
                if idx + 1 < len(tokens) and tokens[idx + 1].type == "inline":
                    header_text = tokens[idx + 1].content
                    line_number = text[:token.map[0]].count('\n') + 1 if token.map else 0
                    
                    headers.append(Header(
                        level=level,
                        text=header_text,
                        line_number=line_number,
                    ))
        
        return headers
    
    def _extract_tables(
        self, tokens, text: str
    ) -> List[Table]:
        """Extract all tables."""
        tables = []
        
        in_table = False
        table_start = 0
        table_end = 0
        table_rows = 0
        
        for token in tokens:
            if token.type == "table_open":
                in_table = True
                table_start = token.map[0] if token.map else 0
                table_rows = 0
            elif token.type == "table_close":
                in_table = False
                table_end = token.map[1] if token.map else 0
                
                # Extract table content
                table_content = '\n'.join(
                    text.split('\n')[table_start:table_end]
                )
                
                tables.append(Table(
                    content=table_content,
                    start_line=table_start + 1,
                    end_line=table_end + 1,
                    row_count=table_rows,
                ))
            elif in_table and token.type == "tr_close":
                table_rows += 1
        
        return tables
    
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
```

**Deliverables**:
- `parser.py` (~800 lines)

**Validation**: Manual testing with sample markdown files

### Day 5: Parser Testing

**Tasks**:
1. Write unit tests for parser edge cases:
   - Empty document
   - Document with only code blocks
   - Document with only headers
   - Nested code blocks
   - Tables with special characters
2. Write integration tests for real markdown files
3. Performance benchmarking (should be faster than old dual-invocation)

**Test Examples** (test_parser.py):
```python
def test_parser_empty_document():
    """Parser handles empty document."""
    parser = Parser()
    analysis = parser.analyze("")
    
    assert analysis.total_chars == 0
    assert analysis.total_lines == 0
    assert analysis.code_ratio == 0.0
    assert analysis.content_type == "text"


def test_parser_code_heavy_document():
    """Parser correctly identifies code-heavy document."""
    parser = Parser()
    markdown = """
# Code Example

```python
def hello():
    print("world")
```

Some text here.

```javascript
console.log("test");
```
"""
    analysis = parser.analyze(markdown)
    
    assert analysis.code_block_count == 2
    assert analysis.code_ratio > 0.3
    assert analysis.content_type == "code"
    assert "python" in analysis.languages
    assert "javascript" in analysis.languages


def test_parser_structured_document():
    """Parser extracts header hierarchy."""
    parser = Parser()
    markdown = """
# Main Title

## Section 1

### Subsection 1.1

## Section 2
"""
    analysis = parser.analyze(markdown)
    
    assert analysis.header_count == 4
    assert analysis.max_header_depth == 3
```

**Deliverables**:
- `test_parser.py` (~150 lines, 5 tests)
- Performance benchmark results

**Validation**: 
- All parser tests pass
- Parser faster than old implementation

**Phase 2 Completion Criteria**:
- ✓ parser.py implemented (~800 lines)
- ✓ Single-pass analysis working
- ✓ No dual invocation needed
- ✓ Parser tests pass (5 edge case tests)
- ✓ Property tests still pass

---

## Phase 3: Strategy Consolidation (Days 6-8)

**Objective**: Reduce 6 strategies to 4, remove ListStrategy

### Day 6: Base Strategy & CodeAware

**Tasks**:
1. Implement `strategies/base.py`:
   - Abstract BaseStrategy class
   - Shared utility methods (_create_chunk, _split_by_paragraphs, etc.)
2. Implement `strategies/code_aware.py`:
   - Merge Code + Mixed strategies
   - Preserve code blocks intact
   - Handle mixed content intelligently

**Code Example** (base.py):
```python
from abc import ABC, abstractmethod
from typing import List
from ..types import Chunk, ChunkConfig, ContentAnalysis

class BaseStrategy(ABC):
    """Base class for all chunking strategies."""
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self.name = self.__class__.__name__.replace("Strategy", "").lower()
    
    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """
        Check if strategy can handle this content type.
        
        Returns:
            True if strategy should be applied, False otherwise
        """
        pass
    
    @abstractmethod
    def apply(
        self,
        text: str,
        analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Apply strategy to chunk the text.
        
        Args:
            text: Original markdown text
            analysis: Content analysis from parser
        
        Returns:
            List of chunks
        """
        pass
    
    # Shared utilities
    
    def _create_chunk(
        self,
        content: str,
        start_line: int,
        end_line: int,
        **metadata
    ) -> Chunk:
        """Create chunk with standard metadata."""
        return Chunk(
            content=content,
            start_line=start_line,
            end_line=end_line,
            metadata={
                "strategy": self.name,
                **metadata,
            },
        )
    
    def _is_within_size(self, text: str) -> bool:
        """Check if text fits within max_chunk_size."""
        return len(text) <= self.config.max_chunk_size
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs (double newline separator)."""
        paragraphs = []
        for para in text.split('\n\n'):
            if para.strip():
                paragraphs.append(para)
        return paragraphs
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        import re
        # Simple sentence splitting (can be improved)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s for s in sentences if s.strip()]
```

**Deliverables**:
- `strategies/base.py` (~200 lines)
- `strategies/code_aware.py` (~600 lines)

**Validation**: CodeAwareStrategy can chunk code-heavy documents

### Day 7: Structural & Table Strategies

**Tasks**:
1. Implement `strategies/structural.py`:
   - Simplified version (no Phase 2 complexity)
   - Header-based section building
   - Split large sections at subsection boundaries
2. Implement `strategies/table.py`:
   - Minimal changes from current TableStrategy
   - Preserve tables intact
   - Chunk surrounding text

**Deliverables**:
- `strategies/structural.py` (~500 lines)
- `strategies/table.py` (~300 lines)

**Validation**: Both strategies work on sample documents

### Day 8: Fallback Strategy & Tests

**Tasks**:
1. Implement `strategies/fallback.py`:
   - Rename from SentencesStrategy
   - Universal fallback (always works)
   - Paragraph and sentence-based chunking
2. Write strategy tests (~8 tests):
   - Test each strategy's can_handle() logic
   - Test basic chunking for each strategy
   - Test fallback behavior

**Test Example** (test_strategies.py):
```python
def test_code_aware_can_handle():
    """CodeAwareStrategy handles code-heavy content."""
    from markdown_chunker_v2.strategies.code_aware import CodeAwareStrategy
    from markdown_chunker_v2.types import ContentAnalysis
    from markdown_chunker_v2.config import ChunkConfig
    
    strategy = CodeAwareStrategy(ChunkConfig.default())
    
    # Code-heavy document
    analysis = ContentAnalysis(
        total_chars=1000,
        total_lines=50,
        code_ratio=0.5,  # 50% code
        text_ratio=0.5,
        code_block_count=3,
        header_count=2,
        max_header_depth=1,
        table_count=0,
        content_type="code",
        languages={"python"},
    )
    
    assert strategy.can_handle(analysis) is True
    
    # Text-heavy document
    analysis_text = ContentAnalysis(
        total_chars=1000,
        total_lines=50,
        code_ratio=0.1,  # 10% code
        text_ratio=0.9,
        code_block_count=1,
        header_count=5,
        max_header_depth=2,
        table_count=0,
        content_type="text",
        languages=set(),
    )
    
    assert strategy.can_handle(analysis_text) is False
```

**Deliverables**:
- `strategies/fallback.py` (~400 lines)
- `test_strategies.py` (~200 lines, 8 tests)

**Validation**: All 4 strategies work, strategy tests pass

**Phase 3 Completion Criteria**:
- ✓ Base strategy implemented
- ✓ 4 strategies implemented (CodeAware, Structural, Table, Fallback)
- ✓ ListStrategy removed
- ✓ Strategy tests pass (8 tests)
- ✓ Property tests still pass

---

## Phase 4: Chunker Implementation (Days 9-10)

**Objective**: Unified orchestration pipeline

### Day 9: Chunker Core

**Tasks**:
1. Implement `chunker.py`:
   - MarkdownChunker class
   - Initialize 4 strategies
   - Unified 3-stage pipeline
   - Strategy selection with fallback
2. Implement overlap logic (block-based only)
3. Implement metadata enrichment

**Code Skeleton** (chunker.py):
```python
class MarkdownChunker:
    """Main markdown chunking engine with unified pipeline."""
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self._parser = Parser()
        self._strategies = self._init_strategies()
    
    def _init_strategies(self) -> List[BaseStrategy]:
        """Initialize 4 strategies in priority order."""
        from .strategies import (
            CodeAwareStrategy,
            StructuralStrategy,
            TableStrategy,
            FallbackStrategy,
        )
        return [
            CodeAwareStrategy(self.config),  # Priority 1
            StructuralStrategy(self.config),  # Priority 2
            TableStrategy(self.config),       # Priority 3
            FallbackStrategy(self.config),    # Priority 4 (always works)
        ]
    
    def chunk(self, text: str) -> ChunkingResult:
        """
        Main chunking method with unified 3-stage pipeline.
        
        Stage 1: Parse and analyze (single-pass)
        Stage 2: Select and apply strategy (with fallback)
        Stage 3: Post-process (overlap, metadata, validation)
        
        Args:
            text: Markdown text to chunk
        
        Returns:
            ChunkingResult with chunks and metadata
        """
        import time
        start_time = time.time()
        
        # Stage 1: Analysis (single-pass, no dual invocation)
        analysis = self._parser.analyze(text)
        
        # Stage 2: Chunking
        chunks, strategy_used, fallback_info = self._apply_strategy(
            text, analysis
        )
        
        # Stage 3: Post-processing
        chunks = self._apply_overlap(chunks, text)
        chunks = self._enrich_metadata(chunks, analysis)
        self._validate_properties(chunks, text)
        
        return ChunkingResult(
            chunks=chunks,
            strategy_used=strategy_used,
            processing_time=time.time() - start_time,
            fallback_used=fallback_info["used"],
            fallback_level=fallback_info["level"],
        )
    
    def _apply_strategy(
        self, text: str, analysis: ContentAnalysis
    ) -> Tuple[List[Chunk], str, Dict]:
        """
        Select and apply strategy with fallback.
        
        Try strategies in priority order. If a strategy can handle
        the content but fails, try next strategy. FallbackStrategy
        is always the last resort.
        """
        for i, strategy in enumerate(self._strategies):
            if not strategy.can_handle(analysis):
                continue
            
            try:
                chunks = strategy.apply(text, analysis)
                if chunks:  # Success
                    return chunks, strategy.name, {
                        "used": False,
                        "level": 0
                    }
            except Exception as e:
                logger.warning(f"{strategy.name} failed: {e}")
                continue
        
        # All failed, use last strategy (FallbackStrategy)
        fallback = self._strategies[-1]
        chunks = fallback.apply(text, analysis)
        return chunks, fallback.name, {
            "used": True,
            "level": len(self._strategies) - 1
        }
```

**Deliverables**:
- `chunker.py` core implementation (~400 lines)

**Validation**: Can chunk basic markdown documents

### Day 10: Utils & Integration Tests

**Tasks**:
1. Implement `utils.py`:
   - apply_block_overlap() function
   - enrich_chunk_metadata() function
   - validate_properties() function
2. Complete `__init__.py` with public API exports
3. Write integration tests (~13 tests):
   - Full pipeline on real markdown files
   - Test with different config profiles
   - Test Dify plugin integration

**Integration Test Example** (test_integration.py):
```python
def test_full_pipeline_code_heavy():
    """Test full pipeline on code-heavy document."""
    from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
    
    markdown = """
# API Documentation

## Authentication

```python
import requests

def authenticate(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}"}
```

## Endpoints

```python
def get_users():
    return requests.get("/users")
```
"""
    
    chunker = MarkdownChunker(ChunkConfig.for_code_docs())
    result = chunker.chunk(markdown)
    
    # Assertions
    assert len(result.chunks) > 0
    assert result.strategy_used == "codeaware"
    assert not result.fallback_used
    
    # Check code blocks preserved
    code_chunks = [c for c in result.chunks if c.metadata.get("content_type") == "code"]
    assert len(code_chunks) >= 2


def test_full_pipeline_structured():
    """Test full pipeline on structured document."""
    from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
    
    markdown = """
# Main Title

## Section 1

Content for section 1.

### Subsection 1.1

More content.

## Section 2

Content for section 2.
"""
    
    chunker = MarkdownChunker(ChunkConfig.default())
    result = chunker.chunk(markdown)
    
    assert len(result.chunks) > 0
    assert result.strategy_used == "structural"
    
    # Check header paths
    for chunk in result.chunks:
        if "header_path" in chunk.metadata:
            assert isinstance(chunk.metadata["header_path"], list)
```

**Deliverables**:
- `utils.py` (~300 lines)
- `__init__.py` (~50 lines)
- `test_integration.py` (~400 lines, 13 tests)

**Validation**: Integration tests pass on real documents

**Phase 4 Completion Criteria**:
- ✓ chunker.py implemented
- ✓ utils.py implemented
- ✓ __init__.py implemented
- ✓ Public API working
- ✓ Integration tests pass (13 tests)
- ✓ Property tests pass
- ✓ All 12 files complete

---

## Phase 5: Validation & Comparison (Days 11-13)

**Objective**: Ensure no regressions vs old implementation

### Day 11: Property Test Validation

**Tasks**:
1. Run all 10 property tests on new implementation
2. Debug any failures
3. Fix implementation to pass all properties
4. Document any intentional behavioral changes

**Validation Script**:
```bash
# Run property tests
pytest tests_v2/property_tests/ -v --hypothesis-show-statistics

# Expected output:
# - PROP-1: No Content Loss: PASSED (100 examples)
# - PROP-2: Size Bounds: PASSED (100 examples)
# - PROP-3: Monotonic Ordering: PASSED (100 examples)
# - PROP-4: No Empty Chunks: PASSED (100 examples)
# - PROP-5: Valid Line Numbers: PASSED (100 examples)
# - PROP-6: Code Block Integrity: PASSED (100 examples)
# - PROP-7: Table Integrity: PASSED (100 examples)
# - PROP-8: Serialization Round-Trip: PASSED (100 examples)
# - PROP-9: Idempotence: PASSED (100 examples)
# - PROP-10: Header Path Correctness: PASSED (100 examples)
```

**Deliverables**:
- All property tests passing
- Bug fixes if needed

**Validation**: 10/10 property tests pass

### Day 12: Output Comparison

**Tasks**:
1. Create comparison script to run both old and new implementations
2. Collect 100 real markdown documents (from tests, examples, docs)
3. Chunk all documents with both implementations
4. Compare outputs:
   - Chunk count
   - Chunk sizes
   - Content preservation
   - Metadata presence
5. Calculate equivalence percentage
6. Document differences

**Comparison Script** (compare_implementations.py):
```python
def compare_chunking(markdown_text: str) -> dict:
    """Compare old vs new implementation."""
    from markdown_chunker import MarkdownChunker as OldChunker
    from markdown_chunker_v2 import MarkdownChunker as NewChunker
    from markdown_chunker import ChunkConfig as OldConfig
    from markdown_chunker_v2 import ChunkConfig as NewConfig
    
    # Chunk with both
    old_result = OldChunker(OldConfig.default()).chunk(markdown_text)
    new_result = NewChunker(NewConfig.default()).chunk(markdown_text)
    
    # Compare
    return {
        "chunk_count_old": len(old_result.chunks),
        "chunk_count_new": len(new_result.chunks),
        "strategy_old": old_result.strategy_used,
        "strategy_new": new_result.strategy_used,
        "equivalent": _are_equivalent(old_result, new_result),
        "differences": _find_differences(old_result, new_result),
    }

# Run on 100 documents
results = []
for doc_path in test_documents:
    with open(doc_path) as f:
        text = f.read()
    results.append(compare_chunking(text))

# Calculate metrics
total = len(results)
equivalent = sum(1 for r in results if r["equivalent"])
equivalence_rate = equivalent / total * 100

print(f"Equivalence rate: {equivalence_rate:.1f}%")
```

**Deliverables**:
- Comparison report (CSV with results)
- Equivalence percentage
- List of intentional changes

**Validation**: Equivalence rate ≥ 95%

### Day 13: Performance Benchmarking & Regression Tests

**Tasks**:
1. Performance benchmarking:
   - Measure processing time for various document sizes
   - Compare old vs new implementation
   - Ensure new implementation within 20% of old
2. Write regression tests for known critical bugs:
   - MC-001: Section fragmentation
   - MC-003: Overlap issues
   - MC-006: Header path issues
3. Create validation report

**Benchmark Script**:
```python
import time

def benchmark_implementation(implementation, documents):
    """Benchmark implementation on documents."""
    results = []
    
    for doc in documents:
        start = time.time()
        result = implementation.chunk(doc.text)
        elapsed = time.time() - start
        
        results.append({
            "size": len(doc.text),
            "chunks": len(result.chunks),
            "time": elapsed,
        })
    
    return results

# Run benchmarks
old_bench = benchmark_implementation(old_chunker, test_docs)
new_bench = benchmark_implementation(new_chunker, test_docs)

# Compare
for old, new in zip(old_bench, new_bench):
    speedup = old["time"] / new["time"]
    print(f"Doc size: {old['size']:>6} | "
          f"Old: {old['time']:.3f}s | "
          f"New: {new['time']:.3f}s | "
          f"Speedup: {speedup:.2f}x")
```

**Deliverables**:
- Performance benchmark results
- Regression tests (test_regressions.py, 5 tests)
- Validation report document

**Validation**: Performance within 20% (preferably faster)

**Phase 5 Completion Criteria**:
- ✓ All 10 property tests pass
- ✓ Output equivalence ≥ 95%
- ✓ Performance within 20%
- ✓ Regression tests pass
- ✓ Validation report complete

---

## Phase 6: Migration & Cleanup (Days 14-15)

**Objective**: Production release

### Day 14: Documentation & Migration Guide

**Tasks**:
1. Update README.md with simplified API examples
2. Update docs/quickstart.md with 8-parameter config
3. Update docs/api/ with new API reference
4. Create MIGRATION.md guide for users (1.x → 2.0)
5. Update CHANGELOG.md

**Migration Guide Structure** (MIGRATION.md):
```markdown
# Migration Guide: v1.x → v2.0

## Overview
Version 2.0 is a complete redesign focused on simplicity while
maintaining all functionality.

## Breaking Changes

### Configuration Parameters
24 parameters removed. Mapping:

| v1.x Parameter | v2.0 Equivalent | Action |
|----------------|-----------------|--------|
| target_chunk_size | Derived: (min + max) / 2 | Remove |
| overlap_percentage | Use overlap_size | Convert: size = max * percentage |
| enable_overlap | overlap_size = 0 | Set overlap_size = 0 to disable |
| block_based_overlap | Always block-based | Remove |
| All MC-* flags | Always enabled | Remove |

### Strategies
- ListStrategy removed (was excluded from auto-selection)
- MixedStrategy merged into CodeAwareStrategy

### Public API
- Parser no longer exports 50+ symbols
- Use only markdown_chunker.* exports

## Migration Steps

1. **Update Configuration**:
   ```python
   # v1.x
   config = ChunkConfig(
       max_chunk_size=4096,
       overlap_size=200,
       overlap_percentage=0.1,  # REMOVE
       enable_overlap=True,  # REMOVE
       block_based_overlap=True,  # REMOVE
   )
   
   # v2.0
   config = ChunkConfig(
       max_chunk_size=4096,
       overlap_size=200,  # 0 to disable
   )
   ```

2. **Update Imports**:
   ```python
   # v1.x - avoid internal imports
   from markdown_chunker.parser import ParserInterface
   
   # v2.0 - use public API only
   from markdown_chunker import MarkdownChunker, ChunkConfig
   ```

3. **Test Migration**:
   ```bash
   # Install v2.0
   pip install markdown-chunker==2.0.0
   
   # Run tests
   pytest your_tests/
   ```
```

**Deliverables**:
- Updated README.md
- Updated docs/quickstart.md
- Updated docs/api/
- MIGRATION.md
- CHANGELOG.md

**Validation**: Documentation accurate and complete

### Day 15: Release Preparation

**Tasks**:
1. Tag v1.x codebase: `git tag v1.x.x`
2. Move new implementation to main location:
   ```bash
   mv markdown_chunker markdown_chunker_v1_archive
   mv markdown_chunker_v2 markdown_chunker
   ```
3. Update manifest.yaml version to 2.0.0
4. Update requirements.txt (remove mistune, markdown)
5. Run full test suite
6. Update Dify plugin if needed
7. Create release PR
8. Tag v2.0.0: `git tag v2.0.0`

**Release Checklist**:
- [ ] All tests pass (property + integration + regression)
- [ ] Code coverage ≥ 85%
- [ ] Documentation updated
- [ ] CHANGELOG.md complete
- [ ] manifest.yaml version = 2.0.0
- [ ] requirements.txt updated
- [ ] No circular dependencies (verified)
- [ ] No files > 800 lines (verified)
- [ ] Public API ≤ 10 exports (verified)

**Deliverables**:
- v2.0.0 tagged and ready for release
- Old code archived in markdown_chunker_v1_archive/

**Validation**: All release criteria met

**Phase 6 Completion Criteria**:
- ✓ Documentation updated
- ✓ Migration guide complete
- ✓ Version 2.0.0 tagged
- ✓ Old code archived
- ✓ Release ready

---

## Rollback Plan

If critical issues are discovered after release:

1. **Immediate**: Revert to v1.x tag
2. **Short-term**: Fix issues in v2.0.1
3. **Communication**: Notify users of issue and timeline

## Post-Implementation

After 3 weeks, we'll have:
- ✓ 12 files (~5,000 lines) instead of 55 files (~24,000 lines)
- ✓ 8 config parameters instead of 32
- ✓ 4 strategies instead of 6
- ✓ ~50 tests instead of 1,853
- ✓ All 10 domain properties passing
- ✓ ≥ 95% output equivalence
- ✓ Performance within 20%
