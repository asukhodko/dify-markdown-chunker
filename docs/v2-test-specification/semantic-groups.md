# Semantic Groups for V2 Test Specification

This document defines semantic groups for organizing P1 legacy tests and mapping them to v2 API concepts.

## Summary

- **Total groups**: 26
- **Total tests mapped**: 3188
- **V2 applicable tests**: 2369
- **Archived (removed functionality)**: 819

## Group Categories

### Parser Groups (7 groups)

#### Group 1: Content Analysis
- **ID**: PARSER-001
- **V2 Component**: `Parser.analyze() → ContentAnalysis`
- **Description**: Tests for basic document metrics extraction (total_chars, total_lines, code_ratio)
- **Boundaries**:
  - Includes: Basic metrics calculation, content type detection, ratio computations
  - Excludes: Element extraction (separate groups), position tracking
- **Test Count**: ~120 tests
- **Test Files**:
  - tests/parser/test_content_analysis_properties.py
  - tests/parser/test_basic_functionality.py
  - tests/parser/test_extraction_heuristics.py

#### Group 2: Fenced Block Extraction
- **ID**: PARSER-002
- **V2 Component**: `ContentAnalysis.code_blocks: List[FencedBlock]`
- **Description**: Tests for code block detection, language identification, and content extraction
- **Boundaries**:
  - Includes: Fenced block detection, language parsing, nested blocks, block boundaries
  - Excludes: Code strategy behavior (chunker group)
- **Test Count**: ~80 tests
- **Test Files**:
  - tests/parser/test_fenced_block_extractor.py
  - tests/parser/test_nested_fence_handling.py
  - tests/parser/test_element_detector.py

#### Group 3: Header Detection
- **ID**: PARSER-003
- **V2 Component**: `ContentAnalysis.headers: List[Header]`
- **Description**: Tests for header hierarchy detection and level parsing
- **Boundaries**:
  - Includes: Header level detection (1-6), header text extraction, header hierarchy
  - Excludes: Header-based chunking (strategy group)
- **Test Count**: ~60 tests
- **Test Files**:
  - tests/parser/test_element_detector.py
  - tests/chunker/test_header_path_property.py

#### Group 4: Table Detection
- **ID**: PARSER-004
- **V2 Component**: `ContentAnalysis.tables: List[TableBlock]`
- **Description**: Tests for markdown table structure recognition
- **Boundaries**:
  - Includes: Table detection, column/row counting, table boundaries
  - Excludes: Table preservation in chunks (chunker group)
- **Test Count**: ~40 tests
- **Test Files**:
  - tests/parser/test_element_detector.py

#### Group 5: Preamble Handling
- **ID**: PARSER-005
- **V2 Component**: `ContentAnalysis.has_preamble, preamble_end_line`
- **Description**: Tests for content before first header detection
- **Boundaries**:
  - Includes: Preamble detection, preamble boundary identification
  - Excludes: Preamble chunking behavior
- **Test Count**: ~50 tests
- **Test Files**:
  - tests/parser/test_preamble.py
  - tests/parser/test_preamble_extractor.py
  - tests/chunker/test_preamble_chunking.py
  - tests/chunker/test_preamble_config.py

#### Group 6: Position Accuracy
- **ID**: PARSER-006
- **V2 Component**: `ContentAnalysis (line/char positions)`
- **Description**: Tests for accurate line numbering and character position tracking
- **Boundaries**:
  - Includes: Line number accuracy (1-based), character positions, boundary precision
  - Excludes: Chunk line numbers (chunker group)
- **Test Count**: ~70 tests
- **Test Files**:
  - tests/parser/test_position_accuracy.py
  - tests/parser/test_line_numbering_regression.py
  - tests/parser/test_precise_boundaries.py

#### Group 7: Parser Edge Cases
- **ID**: PARSER-007
- **V2 Component**: `Parser`
- **Description**: Tests for malformed markdown, edge cases, and error handling
- **Boundaries**:
  - Includes: Malformed input, empty documents, special characters, encoding
  - Excludes: Normal parsing behavior
- **Test Count**: ~80 tests
- **Test Files**:
  - tests/parser/test_smoke.py
  - tests/parser/test_smoke_critical_fixes.py
  - tests/parser/test_regression_prevention.py

### Chunker Groups (7 groups)

#### Group 8: Basic Chunking
- **ID**: CHUNKER-001
- **V2 Component**: `MarkdownChunker.chunk() → List[Chunk]`
- **Description**: Tests for basic text splitting functionality
- **Boundaries**:
  - Includes: Simple chunking, chunk creation, basic splitting
  - Excludes: Size constraints, overlap, strategy-specific behavior
- **Test Count**: ~100 tests
- **Test Files**:
  - tests/chunker/test_chunk_simple.py
  - tests/chunker/test_chunker.py
  - tests/chunker/test_integration.py

#### Group 9: Size Constraints
- **ID**: CHUNKER-002
- **V2 Component**: `ChunkConfig.max_chunk_size, min_chunk_size`
- **Description**: Tests for chunk size enforcement and boundary conditions
- **Boundaries**:
  - Includes: Max size enforcement, min size handling, size validation
  - Excludes: Overlap behavior, atomic block handling
- **Test Count**: ~90 tests
- **Test Files**:
  - tests/chunker/test_chunk_config_validation.py
  - tests/chunker/test_critical_properties.py

#### Group 10: Overlap Handling
- **ID**: CHUNKER-003
- **V2 Component**: `ChunkConfig.overlap_size, Chunk.metadata[previous_content/next_content]`
- **Description**: Tests for chunk overlap behavior and metadata
- **Boundaries**:
  - Includes: Overlap size, overlap metadata, overlap boundaries
  - Excludes: Non-overlap chunking
- **Test Count**: ~80 tests
- **Test Files**:
  - tests/chunker/test_overlap_properties.py
  - tests/chunker/test_overlap_properties_redesign.py
  - tests/integration/test_overlap_integration.py
  - tests/integration/test_overlap_redesign_integration.py

#### Group 11: Atomic Block Preservation
- **ID**: CHUNKER-004
- **V2 Component**: `ChunkConfig.preserve_atomic_blocks`
- **Description**: Tests for keeping code blocks and tables intact
- **Boundaries**:
  - Includes: Code block preservation, table preservation, atomic unit handling
  - Excludes: Block detection (parser group)
- **Test Count**: ~70 tests
- **Test Files**:
  - tests/chunker/test_data_preservation_properties.py
  - tests/chunker/test_fallback_metadata_preservation.py

#### Group 12: Chunk Metadata
- **ID**: CHUNKER-005
- **V2 Component**: `Chunk.metadata`
- **Description**: Tests for chunk metadata population and correctness
- **Boundaries**:
  - Includes: Metadata fields, header_path, content_type, strategy info
  - Excludes: Overlap metadata (separate group)
- **Test Count**: ~60 tests
- **Test Files**:
  - tests/chunker/test_metadata_properties.py
  - tests/chunker/test_header_path_property.py

#### Group 13: Strategy Selection
- **ID**: CHUNKER-006
- **V2 Component**: `MarkdownChunker._select_strategy()`
- **Description**: Tests for automatic strategy selection based on content analysis
- **Boundaries**:
  - Includes: Strategy selection logic, threshold-based selection, override behavior
  - Excludes: Individual strategy behavior
- **Test Count**: ~50 tests
- **Test Files**:
  - tests/chunker/test_strategy_selector.py
  - tests/chunker/test_strategy_selector_properties.py

#### Group 14: Configuration Validation
- **ID**: CHUNKER-007
- **V2 Component**: `ChunkConfig`
- **Description**: Tests for configuration validation and defaults
- **Boundaries**:
  - Includes: Config validation, default values, parameter constraints
  - Excludes: Config effects on chunking
- **Test Count**: ~40 tests
- **Test Files**:
  - tests/chunker/test_chunk_config_validation.py
  - tests/chunker/test_config_profiles.py

### Strategy Groups (4 groups)

#### Group 15: CodeAwareStrategy
- **ID**: STRATEGY-001
- **V2 Component**: `CodeAwareStrategy`
- **Description**: Tests for code-heavy document handling
- **Boundaries**:
  - Includes: Code block handling, code_ratio threshold, code-aware splitting
  - Excludes: General chunking behavior
- **Test Count**: ~80 tests
- **Test Files**:
  - tests/chunker/test_code_strategy_properties.py
  - tests/chunker/test_strategies/test_code_strategy.py

#### Group 16: StructuralStrategy
- **ID**: STRATEGY-002
- **V2 Component**: `StructuralStrategy`
- **Description**: Tests for header-based document splitting
- **Boundaries**:
  - Includes: Header-based splitting, structure_threshold, hierarchy handling
  - Excludes: Non-structural content
- **Test Count**: ~70 tests
- **Test Files**:
  - tests/chunker/test_structural_strategy_properties.py
  - tests/chunker/test_structural_strategy_initialization.py
  - tests/chunker/test_strategies/test_structural_strategy.py

#### Group 17: FallbackStrategy
- **ID**: STRATEGY-003
- **V2 Component**: `FallbackStrategy`
- **Description**: Tests for default splitting behavior
- **Boundaries**:
  - Includes: Default splitting, fallback behavior, simple text handling
  - Excludes: Strategy-specific optimizations
- **Test Count**: ~60 tests
- **Test Files**:
  - tests/chunker/test_fallback_properties.py
  - tests/chunker/test_fallback_manager_integration.py

#### Group 18: Strategy Interface
- **ID**: STRATEGY-004
- **V2 Component**: `BaseStrategy`
- **Description**: Tests for base strategy contract and interface
- **Boundaries**:
  - Includes: Strategy interface, base class behavior, strategy contract
  - Excludes: Specific strategy implementations
- **Test Count**: ~30 tests
- **Test Files**:
  - tests/chunker/test_base_strategy.py
  - tests/chunker/test_strategy_error_handling.py

### Integration Groups (4 groups)

#### Group 19: End-to-End Pipeline
- **ID**: INTEGRATION-001
- **V2 Component**: `MarkdownChunker (full pipeline)`
- **Description**: Tests for complete chunking workflow
- **Boundaries**:
  - Includes: Full pipeline, real documents, complete workflow
  - Excludes: Unit-level component tests
- **Test Count**: ~120 tests
- **Test Files**:
  - tests/integration/test_end_to_end.py
  - tests/integration/test_full_pipeline.py
  - tests/integration/test_full_pipeline_real_docs.py
  - tests/integration/test_full_api_flow.py
  - tests/integration/test_edge_cases_full_pipeline.py

#### Group 20: Serialization
- **ID**: INTEGRATION-002
- **V2 Component**: `Chunk.to_dict(), Chunk.from_dict(), Chunk.to_json(), Chunk.from_json()`
- **Description**: Tests for chunk serialization and deserialization
- **Boundaries**:
  - Includes: JSON serialization, dict conversion, roundtrip
  - Excludes: Chunk creation
- **Test Count**: ~40 tests
- **Test Files**:
  - tests/chunker/test_serialization.py
  - tests/chunker/test_serialization_roundtrip_property.py

#### Group 21: Error Handling
- **ID**: INTEGRATION-003
- **V2 Component**: `Error handling across components`
- **Description**: Tests for error recovery and reporting
- **Boundaries**:
  - Includes: Error types, error recovery, error messages
  - Excludes: Normal operation
- **Test Count**: ~50 tests
- **Test Files**:
  - tests/chunker/test_error_types.py
  - tests/chunker/test_strategy_error_handling.py
  - tests/api/test_error_handler.py

#### Group 22: API Compatibility
- **ID**: INTEGRATION-004
- **V2 Component**: `API layer`
- **Description**: Tests for API backward compatibility and validation
- **Boundaries**:
  - Includes: API compatibility, input validation, adapter behavior
  - Excludes: Internal implementation
- **Test Count**: ~80 tests
- **Test Files**:
  - tests/api/test_backward_compatibility.py
  - tests/api/test_adapter.py
  - tests/api/test_validator.py

### Property Groups (4 groups)

#### Group 23: Data Preservation
- **ID**: PROPERTY-001
- **V2 Component**: `MarkdownChunker (invariant)`
- **Description**: Tests for no content loss during chunking
- **Boundaries**:
  - Includes: Content preservation, no data loss, completeness
  - Excludes: Specific chunking behavior
- **Test Count**: ~50 tests
- **Test Files**:
  - tests/chunker/test_data_preservation_properties.py
  - tests/chunker/test_critical_properties.py
  - tests/test_domain_properties.py

#### Group 24: Ordering Invariants
- **ID**: PROPERTY-002
- **V2 Component**: `Chunk.start_line, Chunk.end_line`
- **Description**: Tests for monotonic line number ordering
- **Boundaries**:
  - Includes: Monotonic ordering, line number consistency, no gaps
  - Excludes: Content ordering
- **Test Count**: ~40 tests
- **Test Files**:
  - tests/chunker/test_monotonic_ordering_property.py
  - tests/chunker/test_critical_properties.py

#### Group 25: Idempotence
- **ID**: PROPERTY-003
- **V2 Component**: `MarkdownChunker.chunk() (invariant)`
- **Description**: Tests for deterministic chunking (same input → same output)
- **Boundaries**:
  - Includes: Idempotence, determinism, reproducibility
  - Excludes: Performance variation
- **Test Count**: ~30 tests
- **Test Files**:
  - tests/chunker/test_idempotence_property.py
  - tests/test_domain_properties.py

#### Group 26: Size Bounds
- **ID**: PROPERTY-004
- **V2 Component**: `Chunk.size, ChunkConfig`
- **Description**: Tests for chunks within configured size limits
- **Boundaries**:
  - Includes: Size bounds, max/min enforcement, oversize handling
  - Excludes: Size calculation
- **Test Count**: ~40 tests
- **Test Files**:
  - tests/chunker/test_no_empty_chunks_property.py
  - tests/chunker/test_critical_properties.py
  - tests/test_v2_properties.py

## Archived Groups (Removed Functionality)

### Group A1: List Strategy (ARCHIVED)
- **Status**: REMOVED in v2
- **Reason**: Merged into FallbackStrategy
- **Test Count**: ~50 tests
- **Test Files**:
  - tests/chunker/test_list_strategy_properties.py
  - tests/chunker/test_strategies/test_list_strategy.py

### Group A2: Table Strategy (ARCHIVED)
- **Status**: REMOVED in v2
- **Reason**: Merged into FallbackStrategy
- **Test Count**: ~60 tests
- **Test Files**:
  - tests/chunker/test_table_strategy_properties.py
  - tests/chunker/test_strategies/test_table_strategy.py

### Group A3: Sentences Strategy (ARCHIVED)
- **Status**: REMOVED in v2
- **Reason**: Merged into FallbackStrategy
- **Test Count**: ~45 tests
- **Test Files**:
  - tests/chunker/test_sentences_strategy_properties.py
  - tests/chunker/test_strategies/test_sentences_strategy.py

### Group A4: Mixed Strategy (ARCHIVED)
- **Status**: REMOVED in v2
- **Reason**: Merged into FallbackStrategy
- **Test Count**: ~65 tests
- **Test Files**:
  - tests/chunker/test_mixed_strategy_properties.py
  - tests/chunker/test_mixed_strategy_stage1_integration.py
  - tests/chunker/test_strategies/test_mixed_strategy.py

### Group A5: Legacy Architecture (ARCHIVED)
- **Status**: REMOVED in v2
- **Reason**: Stage-based architecture replaced with linear pipeline
- **Test Count**: ~100 tests
- **Test Files**:
  - tests/chunker/test_stage1_integration.py
  - tests/chunker/test_phase2_properties.py
  - tests/chunker/test_block_packer.py
  - tests/chunker/test_dynamic_strategy_management.py
