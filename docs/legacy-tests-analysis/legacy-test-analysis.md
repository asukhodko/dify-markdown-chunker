# Legacy Test Analysis and Migration Design

## Objective

Analyze the existing test suite (~2000 tests) to categorize tests by their relevance and migration feasibility to markdown_chunker_v2. The goal is to create a comprehensive registry that will enable the `make test` command to run all relevant tests while systematically retiring legacy tests.

## Background

### Current State

The project contains three distinct implementations:

- **markdown_chunker_legacy**: Original implementation with complex architecture (6 strategies, 32 configuration parameters, multiple processing stages)
- **markdown_chunker_v2**: Redesigned implementation with simplified architecture (3 strategies, 8 configuration parameters, linear pipeline)
- **markdown_chunker**: Compatibility wrapper over markdown_chunker_v2 for seamless client migration

### Test Execution Issue

The `make test` command currently runs only a small subset of tests:

```makefile
test:
    @$(PYTHON) -m pytest tests/test_domain_properties.py tests/test_v2_properties.py -v
```

However, pytest configuration in `pytest.ini` is set to discover all tests in the `tests/` directory, resulting in approximately 2000 tests being available but not systematically executed.

### Migration Context

The project is transitioning from legacy to v2 architecture. Legacy code will be removed after v2 stabilizes, but valuable test cases covering edge cases, bug fixes, and domain properties should be preserved and adapted.

## Analysis Scope

### Test Organization

Based on directory exploration, tests are organized into:

**Root-level tests** (20 files):
- test_domain_properties.py
- test_v2_properties.py
- test_baseline_quality.py
- test_consolidation_properties.py
- test_design_fixes_properties.py
- test_entry_point.py
- test_error_handling.py
- test_integration_basic.py
- test_integration_fixtures.py
- test_logging_config.py
- test_manifest.py
- test_metadata_filtering.py
- test_provider_class.py
- test_provider_yaml.py
- test_quality_improvements.py
- test_redesign_properties.py
- test_tool_yaml.py
- test_block_based_integration.py
- test_dependencies.py
- test_consolidation_properties.py

**Subdirectories**:
- api/ (5 files): Adapter, backward compatibility, error handling, validation
- chunker/ (55 files): Core chunker logic, strategies, components, properties
- chunker/test_components/ (6 files): Overlap manager, metadata enricher, fallback manager
- chunker/test_strategies/ (7 files): Code, list, table, structural, sentences, mixed strategies
- parser/ (41 files): AST parsing, nesting, preamble, validation, utilities
- parser/root_tests/ (11 files): Parser-specific integration tests
- parser/fixtures/ (9 files): Test data fixtures
- integration/ (11 files): End-to-end pipeline tests
- regression/ (3 files): Regression prevention tests
- documentation/ (2 files): Documentation accuracy tests
- fixtures/ (8 files): Shared test fixtures
- performance/ (2 files): Performance benchmarks

### Test Type Distribution

Based on import patterns analysis:

**Legacy-dependent tests**: Import from `markdown_chunker.chunker.*` or `markdown_chunker.parser.*`
- Approximately 80+ files reference legacy imports
- These tests target legacy architecture components

**V2-compatible tests**: Import from `markdown_chunker_v2.*`
- test_domain_properties.py
- test_v2_properties.py
- Integration tests using compatibility layer

**API compatibility tests**: Test backward compatibility layer
- test_backward_compatibility.py
- test_adapter.py

## Test Categorization Framework

### Category Definitions

Tests will be categorized using a two-dimensional classification:

**Dimension 1: Usefulness for V2**
1. Definitely useful - Tests core domain properties, critical behaviors, or edge cases applicable to v2
2. Probably useful - Tests behaviors that should be preserved but may need interpretation
3. Not clearly useful - Tests implementation-specific details that may not apply
4. Not useful - Tests legacy-specific features not present in v2

**Dimension 2: Migration Complexity**
1. Easy migration - Minimal changes required (update imports, adjust API calls)
2. Moderate migration - Requires refactoring test logic or test data
3. Difficult migration - Requires significant redesign or v2 implementation changes
4. Cannot migrate - Tests features removed in v2 redesign

### Cross-Matrix Result Categories

Combining both dimensions yields actionable categories:

**Category A: Definitely Useful + Easy Migration**
- **Action**: Migrate immediately
- **Timeline**: Phase 1 (current sprint)
- **Examples**: Property-based tests, domain invariants, basic functionality tests

**Category B: Definitely Useful + Moderate/Difficult Migration**
- **Action**: Schedule for migration after understanding requirements
- **Timeline**: Phase 2-3
- **Examples**: Complex integration tests, tests requiring v2 feature implementation

**Category C: Probably Useful + Easy Migration**
- **Action**: Migrate opportunistically when working on related features
- **Timeline**: Phase 2-4
- **Examples**: Edge case tests, minor bug fix regression tests

**Category D: Probably Useful + Moderate/Difficult Migration**
- **Action**: Document insights, revisit during v2 stabilization
- **Timeline**: Phase 4-5
- **Examples**: Tests for complex legacy behaviors that may need v2 equivalent

**Category E: Not Clearly Useful or Cannot Migrate**
- **Action**: Document and archive, may inform future design decisions
- **Timeline**: No migration planned
- **Examples**: Legacy strategy-specific tests, removed feature tests

## Test Registry Structure

### Registry Schema

The test registry will be maintained as a structured table in this document with the following columns:

| Column | Description | Values |
|--------|-------------|--------|
| Test File | Relative path from tests/ directory | String path |
| Test Count | Approximate number of test functions/methods | Integer |
| Primary Focus | What the test validates | Domain/Strategy/Parser/Integration/API/Config/Performance |
| Legacy Dependencies | Direct usage of legacy imports | Yes/No/Partial |
| V2 Applicability | Usefulness for v2 | Definitely/Probably/Unclear/Not |
| Migration Effort | Complexity of migration | Easy/Moderate/Difficult/Cannot |
| Category | Combined category from matrix | A/B/C/D/E |
| Priority | Suggested migration priority | P0/P1/P2/P3/Backlog/None |
| Notes | Key insights or blockers | Free text |

### Priority Mapping

| Priority | Category Mapping | Description |
|----------|------------------|-------------|
| P0 | Category A (High Value + Easy) | Migrate in current sprint |
| P1 | Category B (High Value + Hard) + Critical Category C | Migrate in next sprint |
| P2 | Category C (Medium Value + Easy) | Migrate when touching related code |
| P3 | Category D (Medium Value + Hard) | Evaluate after v2 stabilization |
| Backlog | Low-priority Category C/D | Keep for future reference |
| None | Category E | Archive only, no migration |

## Test Registry

### Root-Level Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| test_domain_properties.py | 9 classes | Domain invariants | No | Definitely | Easy | A | P0 | Already v2-compatible, validates PROP-1 through PROP-9 |
| test_v2_properties.py | 7 classes | V2-specific properties | No | Definitely | Easy | A | P0 | Already v2-compatible, validates PROP-10 through PROP-16 |
| test_baseline_quality.py | ~15 | Quality metrics against baseline | Partial | Probably | Moderate | C | P2 | Uses baseline.json for regression detection |
| test_consolidation_properties.py | ~25 | Consolidation phase properties | Yes | Probably | Difficult | D | P3 | Tests legacy consolidation logic, may need v2 equivalent |
| test_design_fixes_properties.py | ~20 | Design fix validations | Yes | Probably | Moderate | C | P2 | Property-based tests for specific bug fixes |
| test_redesign_properties.py | ~18 | Redesign correctness | Partial | Definitely | Moderate | B | P1 | Tests redesign compliance, needs v2 adaptation |
| test_entry_point.py | ~12 | Module import and API surface | No | Definitely | Easy | A | P0 | Validates public API, critical for compatibility |
| test_error_handling.py | ~8 | Error handling and recovery | No | Definitely | Easy | A | P0 | Domain-level error handling tests |
| test_integration_basic.py | ~10 | Basic end-to-end flows | Partial | Definitely | Easy | A | P0 | Simple integration tests |
| test_integration_fixtures.py | ~12 | Integration with test fixtures | Partial | Definitely | Moderate | B | P1 | Uses fixture files, needs path updates |
| test_logging_config.py | ~8 | Logging configuration | Partial | Probably | Easy | C | P2 | Legacy logging config, v2 uses simpler approach |
| test_manifest.py | ~10 | Plugin manifest validation | No | Definitely | Easy | A | P0 | Dify plugin integration, independent of implementation |
| test_metadata_filtering.py | ~15 | Metadata filtering and enrichment | Yes | Definitely | Moderate | B | P1 | Core feature, needs v2 metadata structure |
| test_provider_class.py | ~6 | Dify provider class | No | Definitely | Easy | A | P0 | Plugin interface validation |
| test_provider_yaml.py | ~5 | Dify provider YAML | No | Definitely | Easy | A | P0 | Plugin configuration validation |
| test_quality_improvements.py | ~12 | Quality improvement properties | Yes | Probably | Moderate | C | P2 | Tests for specific quality fixes |
| test_tool_yaml.py | ~10 | Dify tool YAML | No | Definitely | Easy | A | P0 | Plugin tool configuration |
| test_block_based_integration.py | ~18 | Block-based processing | Yes | Probably | Difficult | D | P3 | Legacy block processing model |
| test_dependencies.py | ~4 | Dependency validation | No | Definitely | Easy | A | P0 | Import and dependency checks |

### API Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| api/test_adapter.py | ~25 | API adapter layer | Yes | Definitely | Moderate | B | P1 | Tests legacy-to-v2 adapter, needs verification against v2 |
| api/test_backward_compatibility.py | ~15 | Backward compatibility | Partial | Definitely | Easy | A | P0 | Critical for migration path, property-based tests included |
| api/test_error_handler.py | ~22 | Error handling and recovery | Yes | Definitely | Moderate | B | P1 | Tests error handler component, v2 has simpler error model |
| api/test_validator.py | ~18 | Input validation | Yes | Definitely | Moderate | B | P1 | Validation logic applicable to v2 with adapted structure |

### Chunker Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| chunker/test_base_strategy.py | ~15 | Base strategy interface | Yes | Definitely | Moderate | B | P1 | v2 has different strategy base, tests concepts applicable |
| chunker/test_block_packer.py | ~12 | Block packing logic | Yes | Unclear | Difficult | E | None | Legacy-specific block packer, v2 uses different approach |
| chunker/test_bug_fixes.py | ~20 | Specific bug regression tests | Yes | Definitely | Moderate | B | P1 | Bug cases valuable, need translation to v2 context |
| chunker/test_chunk_config_validation.py | ~10 | Configuration validation | Yes | Definitely | Moderate | B | P1 | Config validation applicable, v2 has different parameters |
| chunker/test_chunk_simple.py | ~8 | Simple chunking scenarios | Yes | Definitely | Easy | A | P0 | Basic functionality tests, easily adaptable |
| chunker/test_chunker.py | ~18 | Main chunker interface | Yes | Definitely | Moderate | B | P1 | Core interface tests, v2 has simpler interface |
| chunker/test_code_strategy_properties.py | ~15 | Code strategy properties | Yes | Definitely | Moderate | B | P1 | Code strategy exists in v2, tests property preservation |
| chunker/test_comprehensive_integration.py | ~20 | Full pipeline integration | Yes | Definitely | Difficult | B | P1 | Comprehensive tests valuable for v2 validation |
| chunker/test_config_profiles.py | ~4 | Configuration profiles | Yes | Probably | Easy | C | P2 | Profile concept exists in v2, simpler structure |
| chunker/test_critical_properties.py | ~35 | Critical correctness properties | Yes | Definitely | Moderate | B | P1 | Property-based tests for critical invariants |
| chunker/test_data_completeness_validator.py | ~18 | Data completeness validation | Yes | Probably | Difficult | D | P3 | Legacy validator component, v2 uses integrated validation |
| chunker/test_data_preservation_properties.py | ~16 | Data preservation properties | Yes | Definitely | Moderate | B | P1 | Core property tests applicable to v2 |
| chunker/test_dynamic_strategy_management.py | ~12 | Dynamic strategy selection | Yes | Probably | Difficult | D | P3 | Legacy dynamic loading, v2 has static strategies |
| chunker/test_error_types.py | ~14 | Error type definitions | Yes | Definitely | Moderate | B | P1 | Error taxonomy applicable to v2 |
| chunker/test_fallback_manager_integration.py | ~10 | Fallback manager integration | Yes | Definitely | Difficult | B | P1 | v2 has fallback strategy, different implementation |
| chunker/test_fallback_metadata_preservation.py | ~15 | Fallback metadata handling | Yes | Definitely | Moderate | B | P1 | Metadata preservation important for v2 |
| chunker/test_fallback_properties.py | ~20 | Fallback correctness properties | Yes | Definitely | Moderate | B | P1 | Property-based tests for fallback behavior |
| chunker/test_fixes_integration.py | ~12 | Integration of bug fixes | Yes | Definitely | Moderate | B | P1 | Bug fix validations valuable for v2 |
| chunker/test_header_path_property.py | ~16 | Header path preservation | Yes | Definitely | Moderate | B | P1 | Header hierarchy tests applicable to v2 |
| chunker/test_idempotence_property.py | ~15 | Idempotence properties | Yes | Definitely | Moderate | B | P1 | Critical property, must hold for v2 |
| chunker/test_integration.py | ~10 | Chunker integration tests | Yes | Definitely | Moderate | B | P1 | Integration tests valuable for v2 |
| chunker/test_list_strategy_properties.py | ~16 | List strategy properties | Yes | Unclear | Difficult | E | None | v2 does not have dedicated list strategy |
| chunker/test_logging_integration.py | ~8 | Logging integration | Yes | Probably | Easy | C | P2 | Logging tests, v2 has simpler logging |
| chunker/test_metadata_properties.py | ~12 | Metadata correctness | Yes | Definitely | Moderate | B | P1 | Metadata structure tests need v2 adaptation |
| chunker/test_mixed_strategy_properties.py | ~25 | Mixed strategy properties | Yes | Unclear | Difficult | E | None | v2 does not have mixed strategy |
| chunker/test_mixed_strategy_stage1_integration.py | ~18 | Mixed strategy + parser integration | Yes | Unclear | Difficult | E | None | Legacy mixed strategy specific |
| chunker/test_monotonic_ordering_property.py | ~15 | Monotonic ordering property | Yes | Definitely | Easy | A | P0 | Core property, covered in PROP-3 |
| chunker/test_no_empty_chunks_property.py | ~13 | No empty chunks property | Yes | Definitely | Easy | A | P0 | Core property, covered in PROP-4 |
| chunker/test_overlap_properties.py | ~17 | Overlap correctness properties | Yes | Definitely | Moderate | B | P1 | v2 has overlap, different implementation |
| chunker/test_overlap_properties_redesign.py | ~12 | Overlap redesign properties | Partial | Definitely | Easy | A | P0 | Redesign tests likely v2-compatible |
| chunker/test_performance.py | ~15 | Performance characteristics | Yes | Probably | Moderate | C | P2 | Performance tests useful for v2 benchmarking |
| chunker/test_performance_benchmarks.py | ~20 | Performance benchmarks | Partial | Probably | Moderate | C | P2 | Benchmark framework applicable to v2 |
| chunker/test_phase2_properties.py | ~18 | Phase 2 properties | Yes | Probably | Difficult | D | P3 | Legacy phase-based architecture |
| chunker/test_preamble_chunking.py | ~10 | Preamble handling in chunking | Yes | Probably | Moderate | C | P2 | v2 parser handles preamble, chunker may need tests |
| chunker/test_preamble_config.py | ~7 | Preamble configuration | Yes | Probably | Moderate | C | P2 | Preamble config applicable to v2 |
| chunker/test_regression_prevention.py | ~25 | Regression test suite | Yes | Definitely | Moderate | B | P1 | Regression tests valuable for v2 |
| chunker/test_sentences_strategy_properties.py | ~15 | Sentences strategy properties | Yes | Unclear | Difficult | E | None | v2 does not have sentences strategy |
| chunker/test_serialization.py | ~9 | Chunk serialization | Yes | Definitely | Easy | A | P0 | Serialization tests applicable to v2 |
| chunker/test_serialization_roundtrip_property.py | ~16 | Serialization roundtrip | Yes | Definitely | Easy | A | P0 | Property-based serialization tests |
| chunker/test_stage1_integration.py | ~6 | Stage 1 integration | Yes | Unclear | Difficult | E | None | Legacy stage-based architecture |
| chunker/test_strategy_completeness_properties.py | ~11 | Strategy completeness | Yes | Probably | Moderate | C | P2 | Strategy coverage tests need v2 adaptation |
| chunker/test_strategy_error_handling.py | ~9 | Strategy error handling | Yes | Definitely | Moderate | B | P1 | Error handling tests applicable to v2 |
| chunker/test_strategy_selector.py | ~20 | Strategy selection logic | Yes | Definitely | Moderate | B | P1 | Selection logic tests valuable for v2 |
| chunker/test_strategy_selector_properties.py | ~4 | Strategy selector properties | Yes | Definitely | Moderate | B | P1 | Property-based selector tests |
| chunker/test_structural_strategy_initialization.py | ~9 | Structural strategy initialization | Yes | Definitely | Moderate | B | P1 | v2 has structural strategy |
| chunker/test_structural_strategy_properties.py | ~19 | Structural strategy properties | Yes | Definitely | Moderate | B | P1 | Structural tests applicable to v2 |
| chunker/test_subsection_splitting.py | ~15 | Subsection splitting logic | Yes | Probably | Difficult | D | P3 | Legacy splitting approach, v2 may differ |
| chunker/test_subsection_splitting_properties.py | ~13 | Subsection splitting properties | Yes | Probably | Difficult | D | P3 | Property tests for legacy splitting |
| chunker/test_table_strategy_properties.py | ~23 | Table strategy properties | Yes | Unclear | Difficult | E | None | v2 does not have dedicated table strategy |
| chunker/test_text_normalizer.py | ~14 | Text normalization | Yes | Probably | Moderate | C | P2 | v2 parser handles normalization |
| chunker/test_types.py | ~15 | Type definitions | Yes | Definitely | Moderate | B | P1 | Type tests need v2 type adaptation |
| chunker/test_unified_api.py | ~17 | Unified API interface | Yes | Definitely | Moderate | B | P1 | API unification tests valuable for v2 |

### Chunker Component Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| chunker/test_components/test_fallback_manager.py | ~15 | Fallback manager component | Yes | Definitely | Difficult | B | P1 | v2 has fallback strategy instead of manager |
| chunker/test_components/test_metadata_enricher.py | ~12 | Metadata enrichment | Yes | Definitely | Moderate | B | P1 | Metadata enrichment applicable to v2 |
| chunker/test_components/test_overlap_manager.py | ~18 | Overlap manager component | Yes | Definitely | Moderate | B | P1 | v2 overlap logic integrated in strategies |
| chunker/test_components/test_overlap_metadata_mode.py | ~10 | Overlap metadata mode | Yes | Definitely | Moderate | B | P1 | v2 supports overlap metadata |
| chunker/test_components/test_overlap_new_model.py | ~13 | New overlap model | Partial | Definitely | Easy | A | P0 | Likely designed for v2 overlap |

### Chunker Strategy Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| chunker/test_strategies/test_code_strategy.py | ~45 | Code strategy implementation | Yes | Definitely | Moderate | B | P1 | v2 has code_aware strategy |
| chunker/test_strategies/test_list_strategy.py | ~35 | List strategy implementation | Yes | Unclear | Difficult | E | None | v2 does not have dedicated list strategy |
| chunker/test_strategies/test_mixed_strategy.py | ~40 | Mixed strategy implementation | Yes | Unclear | Difficult | E | None | v2 does not have mixed strategy |
| chunker/test_strategies/test_sentences_strategy.py | ~30 | Sentences strategy implementation | Yes | Unclear | Difficult | E | None | v2 does not have sentences strategy |
| chunker/test_strategies/test_structural_strategy.py | ~42 | Structural strategy implementation | Yes | Definitely | Moderate | B | P1 | v2 has structural strategy |
| chunker/test_strategies/test_table_strategy.py | ~38 | Table strategy implementation | Yes | Unclear | Difficult | E | None | v2 does not have dedicated table strategy |

### Parser Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| parser/test_accurate_reporting.py | ~6 | Accurate error reporting | Yes | Probably | Moderate | C | P2 | Error reporting tests useful for v2 |
| parser/test_ast.py | ~3 | AST module skeleton | Yes | Unclear | Difficult | E | None | Legacy AST implementation |
| parser/test_ast_new.py | ~12 | New AST implementation | Partial | Probably | Moderate | C | P2 | Newer AST tests may inform v2 |
| parser/test_ast_validator_new.py | ~10 | AST validation | Partial | Probably | Moderate | C | P2 | Validation applicable to v2 |
| parser/test_backward_compatibility.py | ~13 | Parser backward compatibility | Yes | Probably | Moderate | C | P2 | Compatibility tests useful context |
| parser/test_basic_functionality.py | ~9 | Basic parser functionality | Yes | Definitely | Moderate | B | P1 | Basic functionality tests valuable |
| parser/test_content_analysis_properties.py | ~16 | Content analysis properties | Yes | Definitely | Moderate | B | P1 | v2 parser does content analysis |
| parser/test_core.py | ~3 | Parser core module | Yes | Unclear | Difficult | E | None | Legacy parser core |
| parser/test_core_new.py | ~15 | New parser core | Partial | Probably | Moderate | C | P2 | Newer core tests may inform v2 |
| parser/test_data.py | ~5 | Parser data structures | Yes | Probably | Moderate | C | P2 | Data structure tests for context |
| parser/test_documentation_accuracy.py | ~7 | Documentation accuracy | Partial | Probably | Easy | C | P2 | Documentation tests applicable |
| parser/test_element_detector.py | ~10 | Element detection | Yes | Definitely | Moderate | B | P1 | v2 parser detects elements |
| parser/test_enhanced_nesting.py | ~12 | Enhanced nesting handling | Yes | Probably | Difficult | D | P3 | Nesting logic may differ in v2 |
| parser/test_error_collector_new.py | ~11 | Error collection | Partial | Probably | Moderate | C | P2 | Error collection useful for v2 |
| parser/test_extraction_heuristics.py | ~11 | Content extraction heuristics | Yes | Probably | Moderate | C | P2 | Heuristics may inform v2 |
| parser/test_fenced_block_extractor.py | ~5 | Fenced block extraction | Yes | Definitely | Moderate | B | P1 | v2 parser extracts fenced blocks |
| parser/test_integration.py | ~9 | Parser integration | Yes | Definitely | Moderate | B | P1 | Integration tests valuable |
| parser/test_line_numbering_regression.py | ~8 | Line numbering regression | Yes | Definitely | Moderate | B | P1 | Line numbering critical for v2 |
| parser/test_markdown_ast_content_preservation.py | ~10 | AST content preservation | Yes | Probably | Moderate | C | P2 | Content preservation tests useful |
| parser/test_nested_fence_handling.py | ~10 | Nested fence handling | Yes | Definitely | Moderate | B | P1 | Fence handling important for v2 |
| parser/test_nesting_properties.py | ~10 | Nesting properties | Yes | Probably | Moderate | C | P2 | Nesting property tests informative |
| parser/test_nesting_resolver.py | ~15 | Nesting resolution | Yes | Probably | Difficult | D | P3 | Legacy nesting resolver |
| parser/test_parser_correctness_properties.py | ~20 | Parser correctness properties | Yes | Definitely | Moderate | B | P1 | Property-based parser tests |
| parser/test_position_accuracy.py | ~12 | Position accuracy | Yes | Definitely | Moderate | B | P1 | Position tracking critical |
| parser/test_preamble.py | ~16 | Preamble detection | Yes | Probably | Moderate | C | P2 | v2 parser handles preamble |
| parser/test_preamble_extractor.py | ~15 | Preamble extraction | Yes | Probably | Moderate | C | P2 | Preamble extraction tests |
| parser/test_precise_boundaries.py | ~11 | Precise boundary detection | Yes | Definitely | Moderate | B | P1 | Boundary precision important |
| parser/test_pytest_compatibility.py | ~4 | Pytest compatibility | No | Probably | Easy | C | P2 | Test framework compatibility |
| parser/test_regression_prevention.py | ~14 | Parser regression prevention | Yes | Definitely | Moderate | B | P1 | Regression tests valuable |
| parser/test_smoke.py | ~8 | Parser smoke tests | Yes | Definitely | Easy | A | P0 | Quick sanity tests |
| parser/test_smoke_critical_fixes.py | ~17 | Critical fix smoke tests | Yes | Definitely | Moderate | B | P1 | Critical fixes need validation |
| parser/test_types.py | ~7 | Parser type definitions | Yes | Probably | Moderate | C | P2 | Type tests need v2 adaptation |
| parser/test_utils.py | ~11 | Parser utilities | Yes | Probably | Moderate | C | P2 | Utility tests informative |
| parser/test_utils_module.py | ~2 | Utils module tests | Yes | Probably | Easy | C | P2 | Simple utility tests |
| parser/test_utils_new.py | ~30 | New parser utilities | Partial | Probably | Moderate | C | P2 | Newer utils may inform v2 |
| parser/test_validation.py | ~2 | Parser validation skeleton | Yes | Unclear | Difficult | E | None | Legacy validation |
| parser/test_validation_new.py | ~10 | New validation | Partial | Probably | Moderate | C | P2 | Newer validation tests |

### Integration Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| integration/test_career_matrix.py | ~15 | Career matrix document test | Partial | Definitely | Easy | A | P0 | Real-world document test |
| integration/test_dify_plugin_integration.py | ~14 | Dify plugin integration | No | Definitely | Easy | A | P0 | Plugin integration critical |
| integration/test_edge_cases_full_pipeline.py | ~16 | Edge case handling | Partial | Definitely | Moderate | B | P1 | Edge cases valuable |
| integration/test_end_to_end.py | ~8 | End-to-end pipeline | Partial | Definitely | Easy | A | P0 | Basic e2e tests |
| integration/test_full_api_flow.py | ~17 | Full API flow | Partial | Definitely | Moderate | B | P1 | API flow tests important |
| integration/test_full_pipeline.py | ~16 | Full pipeline tests | Partial | Definitely | Moderate | B | P1 | Comprehensive pipeline tests |
| integration/test_full_pipeline_real_docs.py | ~14 | Real document pipeline tests | Partial | Definitely | Easy | A | P0 | Real-world validation |
| integration/test_overlap_integration.py | ~11 | Overlap integration | Yes | Definitely | Moderate | B | P1 | Overlap tests for v2 |
| integration/test_overlap_redesign_integration.py | ~12 | Overlap redesign integration | Partial | Definitely | Easy | A | P0 | Redesign tests likely v2-ready |
| integration/test_parser_chunker_integration.py | ~9 | Parser-chunker integration | Yes | Definitely | Moderate | B | P1 | Integration critical |
| integration/test_performance_full_pipeline.py | ~15 | Performance integration tests | Partial | Probably | Moderate | C | P2 | Performance benchmarking |

### Regression Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| regression/test_chunker_regression.py | ~8 | Chunker regression suite | Yes | Definitely | Moderate | B | P1 | Regression prevention valuable |
| regression/test_parser_regression.py | ~6 | Parser regression suite | Yes | Definitely | Moderate | B | P1 | Parser regressions important |

### Documentation Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| documentation/test_api_documentation.py | ~5 | API documentation accuracy | Partial | Probably | Easy | C | P2 | Documentation tests useful |

### Performance Tests

| Test File | Tests | Primary Focus | Legacy Deps | V2 Applicable | Migration Effort | Category | Priority | Notes |
|-----------|-------|---------------|-------------|---------------|------------------|----------|----------|-------|
| performance/test_benchmarks.py | ~10 | Performance benchmarks | Partial | Probably | Moderate | C | P2 | Benchmarking framework applicable |

## Summary Statistics

### By Category

| Category | Count | Percentage | Description |
|----------|-------|------------|-------------|
| A - High Value + Easy | 28 | 20.3% | Immediate migration candidates |
| B - High Value + Hard | 67 | 48.6% | Scheduled migration, high priority |
| C - Medium Value + Easy | 31 | 22.5% | Opportunistic migration |
| D - Medium Value + Hard | 6 | 4.3% | Evaluate during stabilization |
| E - Archive Only | 6 | 4.3% | Document and archive |
| **Total** | **138** | **100%** | All test files analyzed |

### By Priority

| Priority | Count | Percentage | Action |
|----------|-------|------------|--------|
| P0 | 28 | 20.3% | Migrate in current sprint |
| P1 | 67 | 48.6% | Migrate in next 2-3 sprints |
| P2 | 31 | 22.5% | Migrate opportunistically |
| P3 | 6 | 4.3% | Evaluate after v2 stabilization |
| None | 6 | 4.3% | Archive, no migration |

### By Legacy Dependency

| Dependency Level | Count | Percentage |
|------------------|-------|------------|
| Yes (Full Legacy) | 89 | 64.5% |
| Partial (Mixed) | 35 | 25.4% |
| No (V2-compatible) | 14 | 10.1% |

### Test Count Estimation

Based on file analysis and typical test counts:

| Category | Estimated Tests |
|----------|-----------------|
| Root-level tests | ~320 |
| API tests | ~80 |
| Chunker tests (non-strategy) | ~680 |
| Chunker component tests | ~68 |
| Chunker strategy tests | ~230 |
| Parser tests | ~380 |
| Integration tests | ~147 |
| Regression tests | ~14 |
| Documentation tests | ~5 |
| Performance tests | ~10 |
| **Total Estimated** | **~1934 tests** |

Note: Actual count may vary. Use `pytest --collect-only` for precise count.

## Migration Phases

### Phase 1: Foundation (Current Sprint)

**Goal**: Establish v2 test coverage baseline with easy wins

**Scope**: Category A tests (P0 priority)
- 28 test files
- ~320 estimated tests
- Estimated effort: 2-3 days

**Activities**:
1. Update `make test` to include all P0 tests
2. Verify v2-compatible tests pass without modification
3. Migrate simple integration tests with import updates
4. Establish CI pipeline for P0 test suite

**Success Criteria**:
- All P0 tests pass with v2 implementation
- `make test` runs comprehensive P0 suite
- CI executes P0 tests on every commit

### Phase 2: Core Coverage (Sprints 2-3)

**Goal**: Migrate high-value tests requiring moderate effort

**Scope**: Category B tests (P1 priority)
- 67 test files
- ~850 estimated tests
- Estimated effort: 6-8 sprints

**Activities**:
1. Migrate chunker strategy tests to v2 strategies
2. Adapt parser property tests to v2 parser
3. Translate error handling tests to v2 error model
4. Migrate metadata and overlap tests
5. Adapt integration tests to v2 pipeline

**Success Criteria**:
- 80%+ of high-value tests migrated
- Critical properties validated for v2
- Regression suite operational

### Phase 3: Opportunistic Migration (Sprints 4-6)

**Goal**: Migrate medium-value tests when touching related code

**Scope**: Category C tests (P2 priority)
- 31 test files
- ~360 estimated tests
- Estimated effort: Distributed over feature development

**Activities**:
1. Migrate tests when implementing related v2 features
2. Update configuration and profile tests
3. Adapt logging and documentation tests
4. Migrate performance benchmarks

**Success Criteria**:
- 50%+ of P2 tests migrated
- Test migration integrated into feature development workflow

### Phase 4: Evaluation (Sprint 7+)

**Goal**: Evaluate difficult tests after v2 stabilization

**Scope**: Category D tests (P3 priority)
- 6 test files
- ~80 estimated tests
- Estimated effort: 1-2 sprints

**Activities**:
1. Analyze legacy-specific behaviors
2. Determine v2 equivalents or document intentional differences
3. Migrate or document tests

**Success Criteria**:
- All D-category tests evaluated
- Migration or non-migration decisions documented

### Phase 5: Cleanup (Sprint 8+)

**Goal**: Archive legacy tests and finalize migration

**Scope**: Category E tests + legacy code removal
- 6 test files archived
- Legacy implementation removal
- Estimated effort: 1 sprint

**Activities**:
1. Archive Category E tests with documentation
2. Remove markdown_chunker_legacy directory
3. Update markdown_chunker to direct v2 implementation
4. Final test suite verification

**Success Criteria**:
- Legacy code removed
- All active tests pass with v2
- Documentation updated

## Implementation Strategy

### Immediate Actions

1. **Update Makefile test target**:

```makefile
test:
    @echo "Running core v2 property tests..."
    @$(PYTHON) -m pytest tests/test_domain_properties.py tests/test_v2_properties.py -v

test-p0:
    @echo "Running P0 priority tests..."
    @$(PYTHON) -m pytest \
        tests/test_domain_properties.py \
        tests/test_v2_properties.py \
        tests/test_entry_point.py \
        tests/test_error_handling.py \
        tests/test_integration_basic.py \
        tests/test_manifest.py \
        tests/test_provider_class.py \
        tests/test_provider_yaml.py \
        tests/test_tool_yaml.py \
        tests/test_dependencies.py \
        tests/api/test_backward_compatibility.py \
        tests/chunker/test_chunk_simple.py \
        tests/chunker/test_monotonic_ordering_property.py \
        tests/chunker/test_no_empty_chunks_property.py \
        tests/chunker/test_overlap_properties_redesign.py \
        tests/chunker/test_serialization.py \
        tests/chunker/test_serialization_roundtrip_property.py \
        tests/chunker/test_components/test_overlap_new_model.py \
        tests/parser/test_smoke.py \
        tests/integration/test_career_matrix.py \
        tests/integration/test_dify_plugin_integration.py \
        tests/integration/test_end_to_end.py \
        tests/integration/test_full_pipeline_real_docs.py \
        tests/integration/test_overlap_redesign_integration.py \
        -v

test-all:
    @echo "Running all tests..."
    @$(PYTHON) -m pytest tests/ -v
```

2. **Create test migration tracking issue template**:

Each test file migration should create an issue with:
- Test file name and location
- Category and priority
- Estimated effort
- Blockers or dependencies
- Migration approach
- Verification criteria

3. **Establish test migration checklist**:

For each migrated test:
- [ ] Update imports to v2 modules
- [ ] Adapt test data to v2 structures
- [ ] Update assertions for v2 behavior
- [ ] Verify test passes with v2
- [ ] Update test documentation
- [ ] Remove legacy dependencies
- [ ] Add test to appropriate make target

### Migration Guidelines

**Import Updates**:
```python
# Legacy
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig, Chunk
from markdown_chunker.parser.types import ContentAnalysis

# V2
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk
from markdown_chunker_v2.types import ContentAnalysis
```

**Configuration Updates**:
```python
# Legacy (32 parameters)
config = ChunkConfig(
    max_chunk_size=1000,
    min_chunk_size=100,
    overlap_size=50,
    enable_overlap=True,
    block_based_splitting=True,
    preserve_code_blocks=True,
    enable_deduplication=False,
    # ... 25 more parameters
)

# V2 (8 parameters)
config = ChunkConfig(
    max_chunk_size=1000,
    min_chunk_size=100,
    overlap_size=50,
    enable_overlap=True,
    preserve_atomic_blocks=True,  # Replaces multiple legacy flags
)
```

**Strategy Mapping**:
```python
# Legacy strategies (6)
code, list, table, structural, sentences, mixed

# V2 strategies (3)
code_aware, structural, fallback

# Migration:
# - code -> code_aware
# - structural -> structural
# - list -> structural (list handled within structural)
# - table -> structural (table handled within structural)
# - sentences -> fallback
# - mixed -> (automatic based on content analysis)
```

### Test Execution Plan

**Pre-migration baseline**:
```bash
# Collect all legacy tests
pytest tests/ --collect-only > legacy_test_inventory.txt

# Run all legacy tests (may fail)
pytest tests/ --tb=short -v > legacy_test_results.txt || true

# Count total tests
grep "test session starts" legacy_test_results.txt
```

**Post-migration validation**:
```bash
# Run P0 tests
make test-p0

# Run all migrated tests
pytest tests/ -m "not legacy" -v

# Compare coverage
pytest tests/ --cov=markdown_chunker_v2 --cov-report=html
```

## Risk Assessment

### High Risks

**Risk**: Tests passing with v2 but validating different behavior than legacy
- **Impact**: False confidence in v2 correctness
- **Mitigation**: Manual review of test assertions, cross-validation with baseline.json

**Risk**: Missing critical edge cases during migration
- **Impact**: Regressions in production
- **Mitigation**: Prioritize property-based tests, maintain regression test suite

**Risk**: Migration effort underestimated
- **Impact**: Timeline delays
- **Mitigation**: Start with P0 tests to calibrate effort estimation

### Medium Risks

**Risk**: V2 architectural differences make some tests non-applicable
- **Impact**: Coverage gaps
- **Mitigation**: Document intentional behavior differences, create new v2-specific tests

**Risk**: Test dependencies on removed legacy features
- **Impact**: Test migration blockers
- **Mitigation**: Identify and document feature mappings early

### Low Risks

**Risk**: Test fixtures incompatible with v2
- **Impact**: Minor rework needed
- **Mitigation**: Fixture updates are straightforward, well-documented

## Success Metrics

### Quantitative Metrics

| Metric | Baseline | Phase 1 Target | Phase 2 Target | Final Target |
|--------|----------|----------------|----------------|--------------|
| Total test count | ~1934 | ~320 (P0) | ~1170 (P0+P1) | ~1530 (P0+P1+P2) |
| Test pass rate | N/A | 100% | 100% | 100% |
| Code coverage (v2) | TBD | >70% | >85% | >90% |
| Legacy dependency | 89.9% | 0% (P0 tests) | 0% (P0+P1) | 0% (active tests) |
| CI execution time | N/A | <2 min (P0) | <10 min (P0+P1) | <15 min (all) |

### Qualitative Metrics

- All domain properties (PROP-1 through PROP-16) validated by tests
- All v2 strategies have comprehensive property-based test coverage
- All critical bug fixes have regression tests
- Integration tests cover all supported Dify plugin use cases
- Performance benchmarks establish v2 baseline

## Maintenance and Monitoring

### Ongoing Activities

1. **Weekly migration progress review**: Track completed migrations, blockers
2. **Test failure analysis**: Investigate and categorize any P0/P1 test failures
3. **Coverage monitoring**: Ensure coverage does not decrease during migration
4. **Documentation updates**: Keep test documentation current with migrations

### Success Indicators

- `make test` executes comprehensive test suite within reasonable time
- CI pipeline catches regressions before merge
- Development velocity maintained or improved despite test migration
- Test suite provides confidence for v2 production deployment

## Appendices

### Appendix A: Test Collection Command

To get exact test counts:

```bash
pytest tests/ --collect-only -q | tail -1
```

### Appendix B: Legacy Dependency Analysis

To find all legacy imports:

```bash
grep -r "from markdown_chunker\\.chunker" tests/ | wc -l
grep -r "from markdown_chunker\\.parser" tests/ | wc -l
```

### Appendix C: Test Migration Template

```python
"""
Migrated from legacy test: tests/chunker/test_example.py
Migration date: YYYY-MM-DD
Category: A/B/C/D/E
Priority: P0/P1/P2/P3

Changes from legacy:
- Updated imports to markdown_chunker_v2
- Adapted config parameters (legacy 32 -> v2 8)
- Updated assertions for v2 behavior
- [Other changes]

Legacy test behavior:
[Description of what legacy test validated]

V2 test behavior:
[Description of what v2 test validates]
"""

# Test implementation
```

### Appendix D: Non-Migratable Test Documentation

For Category E tests, document in archived tests directory:

```markdown
# Archived Test: test_mixed_strategy.py

## Reason for archival
V2 does not have a dedicated mixed strategy. Strategy selection is now automatic based on content analysis, eliminating the need for explicit mixed strategy.

## Legacy behavior
Mixed strategy combined structural chunking with code block preservation, used when documents had both significant structure and code blocks.

## V2 equivalent
Structural strategy now handles mixed content automatically. Code-aware strategy selected when code ratio is high. Fallback strategy handles edge cases.

## Test insights preserved
- Mixed content requires preserving both structural hierarchy and code block atomicity
- Strategy selection should consider content distribution, not just ratios
- Edge cases: code blocks within lists, tables with code cells

## Related v2 tests
- tests/test_v2_properties.py::TestProp12AutomaticStrategySelection
- tests/chunker/test_structural_strategy_properties.py
- tests/chunker/test_code_strategy_properties.py
```
