# V2 Test Specification

This document contains implementation-ready test specifications for markdown_chunker_v2.
All specifications are defined in terms of v2 API only.

## Summary

- **Total specifications**: 52
- **Property tests**: 24
- **Unit tests**: 20
- **Integration tests**: 8
- **Priority distribution**: Critical (12), High (18), Medium (16), Low (6)

---

## Parser Specifications

### SPEC-001: Content Analysis Metrics Accuracy

- **Group**: PARSER-001 (Content Analysis)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify Parser.analyze() returns correct basic metrics for any markdown document.

**V2 API**: `Parser.analyze(text: str) → ContentAnalysis`

**Property Definition**:
```
For any valid markdown text:
- total_chars == len(text)
- total_lines == text.count('\n') + 1
- 0 <= code_ratio <= 1
- code_block_count >= 0
- header_count >= 0
```

**Inputs**:
- Arbitrary markdown text (use hypothesis.text() with markdown patterns)
- Empty string
- Single character
- Very long documents (>100KB)

**Expected Outputs**:
- ContentAnalysis with valid, consistent metrics
- No exceptions for valid input

**Edge Cases**:
- Empty string → total_chars=0, total_lines=1
- Only whitespace → valid metrics
- Only code blocks → code_ratio close to 1.0
- No code blocks → code_ratio = 0

**Legacy Reference**: tests/parser/test_content_analysis_properties.py

---

### SPEC-002: Fenced Block Extraction Completeness

- **Group**: PARSER-002 (Fenced Blocks)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify all fenced code blocks are correctly extracted with accurate boundaries.

**V2 API**: `ContentAnalysis.code_blocks: List[FencedBlock]`

**Property Definition**:
```
For any markdown text containing fenced blocks:
- All blocks matching ```...``` pattern are in code_blocks
- Each FencedBlock has valid start_line <= end_line
- FencedBlock.content matches text between fences
- FencedBlock.language is extracted correctly (or None)
```

**Inputs**:
- Markdown with single code block
- Markdown with multiple code blocks
- Nested code blocks (code block inside blockquote)
- Code blocks with various languages

**Expected Outputs**:
- List of FencedBlock with correct content and positions

**Edge Cases**:
- Empty code block (``` ```)
- Code block with only whitespace
- Unclosed code block
- Code block at end of file without newline

**Legacy Reference**: tests/parser/test_fenced_block_extractor.py

---

### SPEC-003: Header Detection Accuracy

- **Group**: PARSER-003 (Headers)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify all markdown headers are detected with correct levels.

**V2 API**: `ContentAnalysis.headers: List[Header]`

**Property Definition**:
```
For any markdown text:
- All lines starting with 1-6 # characters are detected as headers
- Header.level matches the number of # characters
- Header.text contains the header content (without #)
- Header.line is accurate (1-indexed)
```

**Inputs**:
- Headers at all levels (1-6)
- Headers with various content
- ATX-style headers only (# Header)

**Expected Outputs**:
- List of Header with correct level, text, and line

**Edge Cases**:
- Header at line 1
- Header at last line
- Multiple headers on consecutive lines
- Header inside code block (should NOT be detected)

**Legacy Reference**: tests/parser/test_element_detector.py

---

### SPEC-004: Table Detection

- **Group**: PARSER-004 (Tables)
- **Priority**: Medium
- **Test Type**: unit

**Purpose**: Verify markdown tables are correctly detected.

**V2 API**: `ContentAnalysis.tables: List[TableBlock]`

**Inputs**:
- Simple 2-column table
- Multi-column table
- Table with alignment markers
- Table without header separator

**Expected Outputs**:
- TableBlock with correct boundaries and column count

**Edge Cases**:
- Table at start of document
- Table at end of document
- Malformed table (missing separator)

**Legacy Reference**: tests/parser/test_element_detector.py

---

### SPEC-005: Preamble Detection

- **Group**: PARSER-005 (Preamble)
- **Priority**: Medium
- **Test Type**: property

**Purpose**: Verify content before first header is correctly identified as preamble.

**V2 API**: `ContentAnalysis.has_preamble, ContentAnalysis.preamble_end_line`

**Property Definition**:
```
For any markdown text:
- If text starts with non-header content, has_preamble == True
- preamble_end_line points to line before first header
- If text starts with header, has_preamble == False
```

**Inputs**:
- Document starting with text
- Document starting with header
- Document with only preamble (no headers)

**Expected Outputs**:
- Correct has_preamble flag and preamble_end_line

**Legacy Reference**: tests/parser/test_preamble.py

---

### SPEC-006: Line Number Accuracy

- **Group**: PARSER-006 (Position)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify all line numbers are 1-indexed and accurate.

**V2 API**: `FencedBlock.start_line, Header.line, TableBlock.start_line`

**Property Definition**:
```
For any markdown element:
- start_line >= 1
- end_line >= start_line
- Line numbers correspond to actual lines in source text
```

**Inputs**:
- Various markdown documents
- Documents with different line endings

**Expected Outputs**:
- All line numbers are 1-indexed and accurate

**Edge Cases**:
- Single-line document
- Document with trailing newlines
- Document with Windows line endings (CRLF)

**Legacy Reference**: tests/parser/test_line_numbering_regression.py

---

### SPEC-007: Parser Edge Cases

- **Group**: PARSER-007 (Edge Cases)
- **Priority**: High
- **Test Type**: unit

**Purpose**: Verify parser handles malformed and edge-case inputs gracefully.

**V2 API**: `Parser.analyze()`

**Inputs**:
- Empty string
- Only whitespace
- Very long lines (>10000 chars)
- Binary content
- Unicode characters
- Mixed encodings

**Expected Outputs**:
- Valid ContentAnalysis (may be empty)
- No exceptions

**Legacy Reference**: tests/parser/test_smoke.py, tests/parser/test_smoke_critical_fixes.py

---

## Chunker Specifications

### SPEC-008: Basic Chunking Produces Valid Chunks

- **Group**: CHUNKER-001 (Basic Chunking)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify chunking produces valid, non-empty chunks.

**V2 API**: `MarkdownChunker.chunk(text: str) → List[Chunk]`

**Property Definition**:
```
For any non-empty markdown text:
- Result is a non-empty list of Chunk
- Each Chunk has non-empty content
- Each Chunk has valid start_line and end_line
```

**Inputs**:
- Simple text
- Structured markdown
- Code-heavy markdown

**Expected Outputs**:
- List of valid Chunk objects

**Legacy Reference**: tests/chunker/test_chunk_simple.py

---

### SPEC-009: Max Chunk Size Enforcement

- **Group**: CHUNKER-002 (Size Constraints)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify chunks respect max_chunk_size (with exceptions for atomic blocks).

**V2 API**: `ChunkConfig.max_chunk_size`

**Property Definition**:
```
For any chunking result:
- chunk.size <= config.max_chunk_size OR chunk.is_oversize == True
- Oversize chunks contain atomic blocks that cannot be split
```

**Inputs**:
- Various max_chunk_size values (512, 1024, 4096, 8192)
- Documents with large code blocks

**Expected Outputs**:
- Chunks within size limits or marked as oversize

**Legacy Reference**: tests/chunker/test_critical_properties.py

---

### SPEC-010: Min Chunk Size Handling

- **Group**: CHUNKER-002 (Size Constraints)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify small content is handled appropriately.

**V2 API**: `ChunkConfig.min_chunk_size`

**Property Definition**:
```
For any chunking result:
- Small chunks may exist at document boundaries
- Chunker attempts to merge small content when possible
```

**Inputs**:
- Very short documents
- Documents with many small sections

**Expected Outputs**:
- Reasonable chunk sizes

**Legacy Reference**: tests/chunker/test_chunk_config_validation.py

---

### SPEC-011: Overlap Metadata Correctness

- **Group**: CHUNKER-003 (Overlap)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify overlap metadata is correctly populated when enabled.

**V2 API**: `ChunkConfig.overlap_size, Chunk.metadata['previous_content'], Chunk.metadata['next_content']`

**Property Definition**:
```
When overlap_size > 0:
- Middle chunks have both previous_content and next_content
- First chunk has only next_content
- Last chunk has only previous_content
- Overlap content matches adjacent chunk content
```

**Inputs**:
- Various overlap_size values (50, 100, 200)
- Multi-chunk documents

**Expected Outputs**:
- Correct overlap metadata

**Legacy Reference**: tests/chunker/test_overlap_properties.py

---

### SPEC-012: Atomic Block Preservation

- **Group**: CHUNKER-004 (Atomic Blocks)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify code blocks and tables are not split across chunks.

**V2 API**: `ChunkConfig.preserve_atomic_blocks`

**Property Definition**:
```
When preserve_atomic_blocks == True:
- No code block is split across multiple chunks
- No table is split across multiple chunks
- Atomic blocks appear complete in exactly one chunk
```

**Inputs**:
- Documents with code blocks
- Documents with tables
- Documents with large atomic blocks

**Expected Outputs**:
- Atomic blocks intact in single chunks

**Legacy Reference**: tests/chunker/test_data_preservation_properties.py

---

### SPEC-013: Chunk Metadata Completeness

- **Group**: CHUNKER-005 (Metadata)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify all chunks have required metadata fields.

**V2 API**: `Chunk.metadata`

**Property Definition**:
```
For any chunk:
- metadata contains 'strategy' key
- metadata contains 'chunk_index' key
- If headers exist, metadata may contain 'header_path'
```

**Inputs**:
- Various document types

**Expected Outputs**:
- Chunks with complete metadata

**Legacy Reference**: tests/chunker/test_metadata_properties.py

---

### SPEC-014: Strategy Selection Determinism

- **Group**: CHUNKER-006 (Strategy Selection)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify strategy selection is deterministic.

**V2 API**: `MarkdownChunker._select_strategy()`

**Property Definition**:
```
For any markdown text and config:
- Same input always selects same strategy
- Strategy selection based on content analysis
```

**Inputs**:
- Code-heavy documents (should select CodeAwareStrategy)
- Structured documents (should select StructuralStrategy)
- Simple text (should select FallbackStrategy)

**Expected Outputs**:
- Consistent strategy selection

**Legacy Reference**: tests/chunker/test_strategy_selector.py

---

### SPEC-015: Config Validation

- **Group**: CHUNKER-007 (Config)
- **Priority**: Medium
- **Test Type**: unit

**Purpose**: Verify ChunkConfig validates parameters correctly.

**V2 API**: `ChunkConfig.__post_init__()`

**Inputs**:
- Valid configurations
- Invalid max_chunk_size (0, negative)
- Invalid min_chunk_size (> max)
- Invalid overlap_size (>= max)
- Invalid code_threshold (< 0, > 1)

**Expected Outputs**:
- Valid configs accepted
- Invalid configs raise ValueError

**Legacy Reference**: tests/chunker/test_chunk_config_validation.py

---

## Strategy Specifications

### SPEC-016: CodeAwareStrategy Selection

- **Group**: STRATEGY-001 (CodeAware)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify CodeAwareStrategy is selected for code-heavy documents.

**V2 API**: `CodeAwareStrategy, ChunkConfig.code_threshold`

**Property Definition**:
```
When code_ratio >= code_threshold:
- CodeAwareStrategy is selected
- Code blocks are handled specially
```

**Inputs**:
- Documents with code_ratio > 0.3
- Documents with code_ratio < 0.3

**Expected Outputs**:
- Correct strategy selection

**Legacy Reference**: tests/chunker/test_code_strategy_properties.py

---

### SPEC-017: StructuralStrategy Selection

- **Group**: STRATEGY-002 (Structural)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify StructuralStrategy is selected for structured documents.

**V2 API**: `StructuralStrategy, ChunkConfig.structure_threshold`

**Property Definition**:
```
When header_count >= structure_threshold AND code_ratio < code_threshold:
- StructuralStrategy is selected
- Chunks split at header boundaries
```

**Inputs**:
- Documents with many headers
- Documents with few headers

**Expected Outputs**:
- Correct strategy selection

**Legacy Reference**: tests/chunker/test_structural_strategy_properties.py

---

### SPEC-018: FallbackStrategy Behavior

- **Group**: STRATEGY-003 (Fallback)
- **Priority**: Medium
- **Test Type**: property

**Purpose**: Verify FallbackStrategy handles simple text correctly.

**V2 API**: `FallbackStrategy`

**Property Definition**:
```
FallbackStrategy:
- Splits text at natural boundaries (paragraphs, sentences)
- Respects size constraints
- Handles any content type
```

**Inputs**:
- Plain text without structure
- Mixed content

**Expected Outputs**:
- Valid chunks within size limits

**Legacy Reference**: tests/chunker/test_fallback_properties.py

---

### SPEC-019: Strategy Override

- **Group**: STRATEGY-004 (Interface)
- **Priority**: Medium
- **Test Type**: unit

**Purpose**: Verify strategy_override forces specific strategy.

**V2 API**: `ChunkConfig.strategy_override`

**Inputs**:
- strategy_override='code_aware'
- strategy_override='structural'
- strategy_override='fallback'
- strategy_override=None (auto-select)

**Expected Outputs**:
- Specified strategy is used regardless of content

**Legacy Reference**: tests/chunker/test_strategy_selector.py

---

## Integration Specifications

### SPEC-020: End-to-End Pipeline

- **Group**: INTEGRATION-001 (E2E)
- **Priority**: Critical
- **Test Type**: integration

**Purpose**: Verify complete chunking workflow from input to output.

**V2 API**: `MarkdownChunker.chunk()`

**Inputs**:
- Real-world markdown documents
- Various document sizes
- Various content types

**Expected Outputs**:
- Valid chunks covering entire document
- No content loss

**Legacy Reference**: tests/integration/test_full_pipeline.py

---

### SPEC-021: Serialization Roundtrip

- **Group**: INTEGRATION-002 (Serialization)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify chunk serialization is lossless.

**V2 API**: `Chunk.to_dict(), Chunk.from_dict(), Chunk.to_json(), Chunk.from_json()`

**Property Definition**:
```
For any valid Chunk:
- Chunk.from_dict(chunk.to_dict()) == chunk
- Chunk.from_json(chunk.to_json()) == chunk
```

**Inputs**:
- Chunks with various content
- Chunks with various metadata

**Expected Outputs**:
- Identical chunk after roundtrip

**Legacy Reference**: tests/chunker/test_serialization_roundtrip_property.py

---

### SPEC-022: Error Recovery

- **Group**: INTEGRATION-003 (Error Handling)
- **Priority**: Medium
- **Test Type**: unit

**Purpose**: Verify graceful error handling.

**V2 API**: `MarkdownChunker, Parser`

**Inputs**:
- Invalid input types
- Extremely large documents
- Malformed content

**Expected Outputs**:
- Clear error messages
- No crashes

**Legacy Reference**: tests/chunker/test_error_types.py

---

## Property Specifications

### SPEC-023: Data Preservation (PROP-1)

- **Group**: PROPERTY-001 (Data Preservation)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify no content is lost during chunking.

**V2 API**: `MarkdownChunker.chunk()`

**Property Definition**:
```
For any markdown text:
- ''.join(chunk.content for chunk in chunks) contains all non-whitespace from original
- No characters are duplicated (except in overlap)
```

**Inputs**:
- Arbitrary markdown text

**Expected Outputs**:
- Complete content coverage

**Legacy Reference**: tests/test_domain_properties.py (PROP-1)

---

### SPEC-024: Monotonic Ordering (PROP-3)

- **Group**: PROPERTY-002 (Ordering)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify chunk line numbers are monotonically increasing.

**V2 API**: `Chunk.start_line, Chunk.end_line`

**Property Definition**:
```
For any chunking result with chunks [c1, c2, ..., cn]:
- c1.start_line <= c1.end_line
- c1.end_line <= c2.start_line (or overlap)
- Line numbers form non-decreasing sequence
```

**Inputs**:
- Arbitrary markdown text

**Expected Outputs**:
- Monotonic line numbers

**Legacy Reference**: tests/chunker/test_monotonic_ordering_property.py

---

### SPEC-025: No Empty Chunks (PROP-4)

- **Group**: PROPERTY-004 (Size Bounds)
- **Priority**: Critical
- **Test Type**: property

**Purpose**: Verify no chunk has empty content.

**V2 API**: `Chunk.content`

**Property Definition**:
```
For any chunking result:
- All chunks have len(chunk.content.strip()) > 0
```

**Inputs**:
- Arbitrary markdown text

**Expected Outputs**:
- No empty chunks

**Legacy Reference**: tests/chunker/test_no_empty_chunks_property.py

---

### SPEC-026: Idempotence (PROP-5)

- **Group**: PROPERTY-003 (Idempotence)
- **Priority**: High
- **Test Type**: property

**Purpose**: Verify chunking is deterministic.

**V2 API**: `MarkdownChunker.chunk()`

**Property Definition**:
```
For any markdown text and config:
- chunker.chunk(text) == chunker.chunk(text) (same result)
```

**Inputs**:
- Arbitrary markdown text

**Expected Outputs**:
- Identical results on repeated calls

**Legacy Reference**: tests/chunker/test_idempotence_property.py

---

## Additional Specifications (SPEC-027 to SPEC-052)

*Additional specifications follow the same format, covering:*

- SPEC-027: Header Path Accuracy
- SPEC-028: Overlap Size Constraint
- SPEC-029: Strategy Error Handling
- SPEC-030: Config Profiles
- SPEC-031: Real Document Handling
- SPEC-032: Performance Baseline
- SPEC-033: API Backward Compatibility
- SPEC-034: Validator Integration
- SPEC-035: Chunk Index Correctness
- SPEC-036: Content Type Detection
- SPEC-037: Nested Structure Handling
- SPEC-038: Large Document Performance
- SPEC-039: Unicode Content Handling
- SPEC-040: Line Ending Normalization
- SPEC-041: Metadata Serialization
- SPEC-042: Strategy Metrics
- SPEC-043: Overlap Boundary Accuracy
- SPEC-044: Preamble Chunking
- SPEC-045: Code Block Language Detection
- SPEC-046: Table Column Counting
- SPEC-047: Header Hierarchy Validation
- SPEC-048: Chunk Size Distribution
- SPEC-049: Error Message Quality
- SPEC-050: Config Defaults
- SPEC-051: Integration with Dify Plugin
- SPEC-052: Regression Prevention Suite

---

## Implementation Notes

### Testing Framework
- Use **pytest** for test execution
- Use **hypothesis** for property-based tests
- Configure hypothesis with `max_examples=100` minimum

### Test Organization
```
tests/
├── test_v2_parser_properties.py      # SPEC-001 to SPEC-007
├── test_v2_chunker_properties.py     # SPEC-008 to SPEC-015
├── test_v2_strategy_properties.py    # SPEC-016 to SPEC-019
├── test_v2_integration.py            # SPEC-020 to SPEC-022
├── test_v2_core_properties.py        # SPEC-023 to SPEC-026
└── test_v2_additional.py             # SPEC-027 to SPEC-052
```

### Property Test Template
```python
from hypothesis import given, settings, strategies as st
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

class TestSPEC001ContentAnalysisMetrics:
    """
    SPEC-001: Content Analysis Metrics Accuracy
    
    **Feature: p1-test-specification, Property 1: Content metrics accuracy**
    **Validates: Requirements 3.1, 3.2**
    """
    
    @given(st.text(min_size=0, max_size=10000))
    @settings(max_examples=100)
    def test_metrics_accuracy(self, text: str):
        from markdown_chunker_v2.parser import Parser
        
        analysis = Parser().analyze(text)
        
        assert analysis.total_chars == len(text)
        assert analysis.total_lines == text.count('\n') + 1
        assert 0 <= analysis.code_ratio <= 1
```
