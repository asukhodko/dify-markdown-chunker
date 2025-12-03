# Module Structure

This document defines the complete file structure and responsibilities for the redesigned architecture.

## Directory Structure

```
markdown_chunker/
├── __init__.py              # Public API (50 lines)
├── types.py                 # All data structures (600 lines)
├── config.py                # Configuration (200 lines)
├── chunker.py               # Main MarkdownChunker class (400 lines)
├── parser.py                # Stage1 analysis (800 lines)
├── strategies/
│   ├── __init__.py          # Strategy exports (20 lines)
│   ├── base.py              # BaseStrategy abstract class (200 lines)
│   ├── code_aware.py        # Code + mixed content (600 lines)
│   ├── structural.py        # Header-based chunking (500 lines)
│   ├── table.py             # Table preservation (300 lines)
│   └── fallback.py          # Sentence-based fallback (400 lines)
└── utils.py                 # Utilities (300 lines)

Total: 12 files, ~4,370 lines
```

## File Specifications

### `__init__.py` (~50 lines)

**Purpose**: Public API surface with minimal exports

**Exports** (7 total):
```python
__all__ = [
    "MarkdownChunker",      # Main class
    "ChunkConfig",          # Configuration
    "Chunk",                # Data type
    "ChunkingResult",       # Result type
    "ContentAnalysis",      # Analysis type
    "chunk_text",           # Convenience function
    "chunk_file",           # Convenience function
]

__version__ = "2.0.0"

from .chunker import MarkdownChunker
from .types import Chunk, ChunkingResult, ContentAnalysis
from .config import ChunkConfig

def chunk_text(text: str, config: Optional[ChunkConfig] = None) -> ChunkingResult:
    """Convenience function for chunking text."""
    chunker = MarkdownChunker(config or ChunkConfig.default())
    return chunker.chunk(text)

def chunk_file(path: str, config: Optional[ChunkConfig] = None) -> ChunkingResult:
    """Convenience function for chunking file."""
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    return chunk_text(text, config)
```

**Key Points**:
- No deprecated code
- No backward compatibility aliases
- Clean imports only

---

### `types.py` (~600 lines)

**Purpose**: All data structures consolidated

**Classes**:

#### 1. Chunk
```python
@dataclass
class Chunk:
    """Single chunk of markdown content."""
    content: str
    start_line: int
    end_line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate chunk data."""
        if self.start_line < 1:
            raise ValueError("start_line must be >= 1")
        if self.end_line < self.start_line:
            raise ValueError("end_line must be >= start_line")
        if not self.content.strip():
            raise ValueError("chunk content cannot be empty")
    
    @property
    def size(self) -> int:
        return len(self.content)
    
    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1
    
    # ... other properties
```

#### 2. ChunkingResult
```python
@dataclass
class ChunkingResult:
    """Result of chunking operation."""
    chunks: List[Chunk]
    strategy_used: str
    processing_time: float
    fallback_used: bool
    fallback_level: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        # Implementation
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChunkingResult":
        """Deserialize from dictionary."""
        # Implementation
```

#### 3. ContentAnalysis
```python
@dataclass
class ContentAnalysis:
    """Content metrics from Stage1 analysis."""
    total_chars: int
    total_lines: int
    code_ratio: float
    text_ratio: float
    code_block_count: int
    header_count: int
    max_header_depth: int
    table_count: int
    content_type: str  # "code" | "text" | "mixed"
    languages: Set[str]
    
    def get_total_header_count(self) -> int:
        return self.header_count
```

#### 4. MarkdownNode (AST)
```python
@dataclass
class MarkdownNode:
    """AST node for markdown structure."""
    type: str  # "document" | "header" | "paragraph" | "code_block" | etc.
    content: str
    level: Optional[int]  # For headers
    language: Optional[str]  # For code blocks
    children: List["MarkdownNode"] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
```

#### 5. Supporting Types
```python
@dataclass
class FencedBlock:
    """Extracted code block."""
    content: str
    language: str
    fence_type: str  # "```" or "~~~"
    start_line: int
    end_line: int

@dataclass
class Header:
    """Markdown header."""
    level: int
    text: str
    line_number: int

@dataclass
class Table:
    """Markdown table."""
    content: str
    start_line: int
    end_line: int
    row_count: int
```

**Total**: ~600 lines with all dataclasses, properties, validation

---

### `config.py` (~200 lines)

**Purpose**: 8-parameter configuration with 3 profiles

**Implementation**:
```python
@dataclass
class ChunkConfig:
    """Chunking configuration with 8 essential parameters."""
    
    # Size constraints (3 parameters)
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200  # 0 = disabled
    
    # Behavior (3 parameters)
    preserve_atomic_blocks: bool = True  # code blocks, tables
    extract_preamble: bool = True
    allow_oversize: bool = True  # for atomic blocks
    
    # Strategy thresholds (2 parameters)
    code_threshold: float = 0.3
    structure_threshold: int = 3  # min headers
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_chunk_size < self.min_chunk_size:
            raise ValueError("max_chunk_size must be >= min_chunk_size")
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
        """Default configuration for general markdown."""
        return cls()
    
    @classmethod
    def for_code_docs(cls) -> "ChunkConfig":
        """Optimized for technical documentation."""
        return cls(
            max_chunk_size=6144,
            code_threshold=0.2,  # more sensitive to code
            overlap_size=300,
        )
    
    @classmethod
    def for_rag(cls) -> "ChunkConfig":
        """Optimized for RAG systems (embeddings)."""
        return cls(
            max_chunk_size=2048,
            overlap_size=150,
        )
```

**Derived Values**:
```python
@property
def target_chunk_size(self) -> int:
    """Derived: midpoint between min and max."""
    return (self.min_chunk_size + self.max_chunk_size) // 2

@property
def min_effective_chunk_size(self) -> int:
    """Derived: 40% of max (MC-004 fix built-in)."""
    return int(self.max_chunk_size * 0.4)
```

---

### `chunker.py` (~400 lines)

**Purpose**: Main MarkdownChunker class with unified pipeline

**Class Structure**:
```python
class MarkdownChunker:
    """Main markdown chunking engine."""
    
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
            CodeAwareStrategy(self.config),
            StructuralStrategy(self.config),
            TableStrategy(self.config),
            FallbackStrategy(self.config),
        ]
    
    def chunk(self, text: str) -> ChunkingResult:
        """
        Main chunking method with unified 3-stage pipeline.
        
        Stage 1: Parse and analyze
        Stage 2: Select and apply strategy
        Stage 3: Post-process (overlap, metadata, validation)
        """
        start_time = time.time()
        
        # Stage 1: Analysis
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
        """Select and apply strategy with fallback."""
        # Try each strategy by priority
        for strategy in self._strategies:
            if strategy.can_handle(analysis):
                try:
                    chunks = strategy.apply(text, analysis)
                    if chunks:  # Success
                        return chunks, strategy.name, {"used": False, "level": 0}
                except Exception as e:
                    logger.warning(f"{strategy.name} failed: {e}")
                    continue
        
        # All failed, use FallbackStrategy
        fallback = self._strategies[-1]
        chunks = fallback.apply(text, analysis)
        return chunks, fallback.name, {"used": True, "level": len(self._strategies) - 1}
    
    def _apply_overlap(self, chunks: List[Chunk], text: str) -> List[Chunk]:
        """Apply block-based overlap (single mechanism)."""
        if self.config.overlap_size == 0:
            return chunks
        
        # Implementation from BlockOverlapManager
        # ...
        return chunks
    
    def _enrich_metadata(
        self, chunks: List[Chunk], analysis: ContentAnalysis
    ) -> List[Chunk]:
        """Enrich chunks with standardized metadata."""
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                "chunk_id": f"chunk_{i}",
                "chunk_index": i,
                "total_chunks": len(chunks),
                # ... other standard metadata
            })
        return chunks
    
    def _validate_properties(self, chunks: List[Chunk], text: str):
        """Validate all 10 domain properties."""
        # PROP-1: No content loss
        # PROP-2: Size bounds
        # PROP-3: Monotonic ordering
        # PROP-4: No empty chunks
        # PROP-5: Valid line numbers
        # ... validation logic
```

---

### `parser.py` (~800 lines)

**Purpose**: Stage1 markdown parsing and analysis (single-pass)

**Class Structure**:
```python
class Parser:
    """Markdown parser for Stage1 analysis."""
    
    def __init__(self):
        from markdown_it import MarkdownIt
        self._md = MarkdownIt()
    
    def analyze(self, text: str) -> ContentAnalysis:
        """
        Single-pass analysis producing ContentAnalysis.
        
        Consolidates:
        - AST building
        - Code block extraction
        - Element detection (headers, lists, tables)
        - Metric calculation
        """
        # Parse to tokens
        tokens = self._md.parse(text)
        
        # Extract elements
        code_blocks = self._extract_code_blocks(tokens)
        headers = self._extract_headers(tokens)
        tables = self._extract_tables(tokens)
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            text, code_blocks, headers, tables
        )
        
        return ContentAnalysis(
            total_chars=len(text),
            total_lines=text.count('\n') + 1,
            code_ratio=metrics['code_ratio'],
            text_ratio=metrics['text_ratio'],
            code_block_count=len(code_blocks),
            header_count=len(headers),
            max_header_depth=max((h.level for h in headers), default=0),
            table_count=len(tables),
            content_type=self._determine_content_type(metrics),
            languages=self._extract_languages(code_blocks),
        )
    
    def _extract_code_blocks(self, tokens) -> List[FencedBlock]:
        """Extract all code blocks from tokens."""
        # Implementation
    
    def _extract_headers(self, tokens) -> List[Header]:
        """Extract all headers from tokens."""
        # Implementation
    
    def _extract_tables(self, tokens) -> List[Table]:
        """Extract all tables from tokens."""
        # Implementation
    
    def _calculate_metrics(self, text, code_blocks, headers, tables) -> Dict:
        """Calculate content ratios and metrics."""
        total_chars = len(text)
        code_chars = sum(len(cb.content) for cb in code_blocks)
        table_chars = sum(len(t.content) for t in tables)
        
        return {
            'code_ratio': code_chars / total_chars if total_chars > 0 else 0,
            'text_ratio': (total_chars - code_chars - table_chars) / total_chars,
            # ... other metrics
        }
```

---

### `strategies/base.py` (~200 lines)

**Purpose**: BaseStrategy abstract class with shared utilities

**Implementation**:
```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Base class for all chunking strategies."""
    
    def __init__(self, config: ChunkConfig):
        self.config = config
        self.name = self.__class__.__name__.replace("Strategy", "").lower()
    
    @abstractmethod
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        """Check if strategy can handle this content."""
        pass
    
    @abstractmethod
    def apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """Apply strategy to chunk the text."""
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
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by double newlines."""
        return [p for p in text.split('\n\n') if p.strip()]
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by sentence boundaries."""
        # Simple regex-based splitting
        import re
        return re.split(r'[.!?]+\s+', text)
    
    def _is_within_size(self, text: str) -> bool:
        """Check if text fits within max_chunk_size."""
        return len(text) <= self.config.max_chunk_size
```

---

### `strategies/code_aware.py` (~600 lines)

**Purpose**: Unified code handling (merges Code + Mixed strategies)

**Key Method**:
```python
class CodeAwareStrategy(BaseStrategy):
    """Strategy for code-heavy and mixed content."""
    
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        return (
            analysis.code_ratio >= self.config.code_threshold
            or analysis.code_block_count >= 2
        )
    
    def apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Apply code-aware chunking:
        1. Preserve code blocks intact
        2. Group surrounding text with nearest code
        3. Handle mixed content intelligently
        """
        # Get code blocks from parser
        code_blocks = self._extract_code_blocks(text)
        
        # Split text into segments (code + text)
        segments = self._create_segments(text, code_blocks)
        
        # Pack segments into chunks
        chunks = self._pack_segments(segments)
        
        return chunks
    
    def _pack_segments(self, segments) -> List[Chunk]:
        """Pack segments respecting atomic blocks."""
        chunks = []
        current = []
        current_size = 0
        
        for segment in segments:
            if segment.is_code and not self._is_within_size(segment.content):
                # Oversized code block - atomic chunk
                if current:
                    chunks.append(self._create_chunk_from_segments(current))
                    current = []
                    current_size = 0
                
                chunks.append(self._create_chunk(
                    segment.content,
                    segment.start_line,
                    segment.end_line,
                    content_type="code",
                    is_atomic=True,
                    allow_oversize=True,
                ))
            elif current_size + len(segment.content) <= self.config.max_chunk_size:
                # Fits in current chunk
                current.append(segment)
                current_size += len(segment.content)
            else:
                # Flush current, start new
                if current:
                    chunks.append(self._create_chunk_from_segments(current))
                current = [segment]
                current_size = len(segment.content)
        
        # Flush remaining
        if current:
            chunks.append(self._create_chunk_from_segments(current))
        
        return chunks
```

---

### `strategies/structural.py` (~500 lines)

**Purpose**: Header-based chunking (simplified, Phase 2 removed)

```python
class StructuralStrategy(BaseStrategy):
    """Strategy for documents with clear header hierarchy."""
    
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        return (
            analysis.header_count >= self.config.structure_threshold
            and analysis.max_header_depth > 1
            and analysis.code_ratio < self.config.code_threshold
        )
    
    def apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Apply structural chunking:
        1. Extract headers and build hierarchy
        2. Create sections based on headers
        3. Split large sections at subsection boundaries
        """
        headers = self._extract_headers(text)
        sections = self._build_sections(text, headers)
        chunks = self._chunk_sections(sections)
        return chunks
    
    def _build_sections(self, text, headers) -> List[Section]:
        """Build hierarchical sections from headers."""
        # Implementation
    
    def _chunk_sections(self, sections) -> List[Chunk]:
        """Chunk sections, splitting large ones."""
        # Implementation
```

---

### `strategies/table.py` (~300 lines)

**Purpose**: Table preservation (keep as-is from current)

```python
class TableStrategy(BaseStrategy):
    """Strategy for table-heavy documents."""
    
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        return analysis.table_count >= 3 or analysis.table_ratio >= 0.4
    
    def apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """Preserve tables intact, chunk surrounding text."""
        # Implementation similar to current TableStrategy
```

---

### `strategies/fallback.py` (~400 lines)

**Purpose**: Sentence-based universal fallback

```python
class FallbackStrategy(BaseStrategy):
    """Universal fallback strategy (always works)."""
    
    def can_handle(self, analysis: ContentAnalysis) -> bool:
        return True  # Always applicable
    
    def apply(
        self, text: str, analysis: ContentAnalysis
    ) -> List[Chunk]:
        """
        Simple sentence-based chunking:
        1. Split by paragraphs
        2. Split paragraphs by sentences
        3. Group sentences to target size
        """
        paragraphs = self._split_by_paragraphs(text)
        chunks = []
        
        for para in paragraphs:
            if self._is_within_size(para):
                chunks.append(self._create_chunk(para, ...))
            else:
                # Split by sentences and group
                sentences = self._split_by_sentences(para)
                chunks.extend(self._group_sentences(sentences))
        
        return chunks
```

---

### `utils.py` (~300 lines)

**Purpose**: Shared utilities (validation, overlap, metadata)

**Functions**:
```python
def apply_block_overlap(
    chunks: List[Chunk],
    overlap_size: int,
    text: str
) -> List[Chunk]:
    """Apply block-based overlap between chunks."""
    # Implementation from BlockOverlapManager
    
def enrich_chunk_metadata(
    chunks: List[Chunk],
    analysis: ContentAnalysis
) -> List[Chunk]:
    """Add standardized metadata to all chunks."""
    # Implementation
    
def validate_properties(chunks: List[Chunk], text: str):
    """Validate all 10 domain properties."""
    _validate_no_content_loss(chunks, text)
    _validate_size_bounds(chunks)
    _validate_monotonic_order(chunks)
    _validate_no_empty_chunks(chunks)
    _validate_line_numbers(chunks)
    
def _validate_no_content_loss(chunks: List[Chunk], original: str):
    """PROP-1: Verify no content loss."""
    # Implementation
    
# ... other validation functions
```

---

## Implementation Priorities

### Must Have (Week 1)
1. types.py - All data structures
2. config.py - 8-parameter configuration
3. parser.py - Single-pass analysis
4. chunker.py - Main orchestrator (skeleton)

### Should Have (Week 2)
5. strategies/base.py - Abstract base
6. strategies/code_aware.py - Code handling
7. strategies/structural.py - Header-based
8. strategies/fallback.py - Universal fallback
9. strategies/table.py - Table preservation

### Nice to Have (Week 3)
10. utils.py - Helper functions
11. __init__.py - Public API
12. Comprehensive docstrings

---

## Code Standards

All files must follow:
- Line length ≤ 88 characters (Black standard)
- Type annotations for all functions
- Docstrings for all public methods
- No unused imports
- pytest for testing
- Property-based tests with Hypothesis

## Success Metrics

- **All files ≤ 800 lines** (largest: parser.py at ~800)
- **No circular imports**
- **All type checks pass** (mypy)
- **All linting passes** (flake8, Black)
- **Property tests pass** (10 properties × 100 examples)
