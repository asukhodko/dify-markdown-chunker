# Test Migration Status Report

**Generated**: 2025-12-05  
**Phase**: Phase 1 - Foundation  
**Design Document**: [legacy-test-analysis.md](./legacy-test-analysis.md)

## Executive Summary

- **Total tests in repository**: 475 collected tests
- **Tests with import errors**: 98 (legacy dependency issues)
- **Successfully loadable tests**: 377 (79.4%)
- **P0 priority tests identified**: 28 test files (~320 estimated tests)
- **P0 tests successfully running**: 18 test files (210 tests collected)
- **P0 tests requiring migration**: 6 test files (import errors)

## Current Test Execution Status

### `make test` (Current Default)
**Status**: ✅ **PASSING**

Runs core v2 property tests:
- tests/test_domain_properties.py
- tests/test_v2_properties.py

These tests are fully v2-compatible and serve as the baseline.

### `make test-p0` (Newly Added)
**Status**: ❌ **FAILING** (6/24 test files have import errors)

**Successfully collected**: 210 tests from 18 files  
**Import errors**: 6 test files

**Failing test files** (legacy imports):
1. `tests/chunker/test_monotonic_ordering_property.py` - imports from `markdown_chunker.chunker.core`
2. `tests/chunker/test_no_empty_chunks_property.py` - imports from `markdown_chunker.chunker.core`
3. `tests/chunker/test_serialization_roundtrip_property.py` - imports from `markdown_chunker.chunker.core`
4. `tests/chunker/test_components/test_overlap_new_model.py` - imports from `markdown_chunker.chunker.components`
5. `tests/parser/test_smoke.py` - imports from `markdown_chunker.parser`
6. `tests/integration/test_career_matrix.py` - imports from `markdown_chunker.chunker.core`

### `make test-all`
**Status**: ⚠️ **PARTIAL** (377/475 tests loadable, 98 import errors)

## Phase 1 Migration Tasks

### Immediate Priority: Fix P0 Test Import Errors

The following 6 tests files need import migration to become runnable:

#### Task 1: Migrate Monotonic Ordering Property Test
**File**: `tests/chunker/test_monotonic_ordering_property.py`  
**Estimated effort**: 30 minutes  
**Changes required**:
- Update import: `from markdown_chunker.chunker.core import MarkdownChunker` → `from markdown_chunker_v2 import MarkdownChunker`
- Update import: `from markdown_chunker.chunker.types import ChunkConfig` → `from markdown_chunker_v2 import ChunkConfig`
- Verify property tests pass with v2

#### Task 2: Migrate No Empty Chunks Property Test
**File**: `tests/chunker/test_no_empty_chunks_property.py`  
**Estimated effort**: 30 minutes  
**Changes required**:
- Update import: `from markdown_chunker.chunker.core import MarkdownChunker` → `from markdown_chunker_v2 import MarkdownChunker`
- Update import: `from markdown_chunker.chunker.types import ChunkConfig` → `from markdown_chunker_v2 import ChunkConfig`
- Verify property tests pass with v2

#### Task 3: Migrate Serialization Roundtrip Property Test
**File**: `tests/chunker/test_serialization_roundtrip_property.py`  
**Estimated effort**: 30 minutes  
**Changes required**:
- Update import: `from markdown_chunker.chunker.core import MarkdownChunker` → `from markdown_chunker_v2 import MarkdownChunker`
- Update import: `from markdown_chunker.chunker.types import ChunkConfig, Chunk` → `from markdown_chunker_v2 import ChunkConfig, Chunk`
- Verify serialization roundtrip with v2 types

#### Task 4: Migrate Overlap New Model Test
**File**: `tests/chunker/test_components/test_overlap_new_model.py`  
**Estimated effort**: 1 hour  
**Changes required**:
- Identify v2 overlap implementation (integrated in strategies)
- Update imports to v2 modules
- Adapt test logic to v2 overlap model
- May require understanding v2 overlap metadata structure

#### Task 5: Migrate Parser Smoke Tests
**File**: `tests/parser/test_smoke.py`  
**Estimated effort**: 1 hour  
**Changes required**:
- Update import: `from markdown_chunker.parser import ...` → `from markdown_chunker_v2.parser import Parser`
- Adapt to v2 parser API (simplified interface)
- Update assertions for v2 parser behavior

#### Task 6: Migrate Career Matrix Integration Test
**File**: `tests/integration/test_career_matrix.py`  
**Estimated effort**: 45 minutes  
**Changes required**:
- Update import: `from markdown_chunker.chunker.core import MarkdownChunker` → `from markdown_chunker_v2 import MarkdownChunker`
- Update config if needed for v2 (8 parameters vs 32)
- Verify real-world document test passes with v2

**Total estimated effort for P0 import fixes**: ~4.5 hours

### Already Passing P0 Tests

The following 18 test files are successfully collected and ready to run:

1. ✅ tests/test_domain_properties.py (9 test classes, ~50 tests)
2. ✅ tests/test_v2_properties.py (7 test classes, ~40 tests)
3. ✅ tests/test_entry_point.py (~12 tests)
4. ✅ tests/test_error_handling.py (~8 tests)
5. ✅ tests/test_integration_basic.py (~10 tests)
6. ✅ tests/test_manifest.py (~10 tests)
7. ✅ tests/test_provider_class.py (~6 tests)
8. ✅ tests/test_provider_yaml.py (~5 tests)
9. ✅ tests/test_tool_yaml.py (~10 tests)
10. ✅ tests/test_dependencies.py (~4 tests)
11. ✅ tests/api/test_backward_compatibility.py (~15 tests)
12. ✅ tests/chunker/test_chunk_simple.py (~8 tests)
13. ✅ tests/chunker/test_overlap_properties_redesign.py (~12 tests)
14. ✅ tests/chunker/test_serialization.py (~9 tests)
15. ✅ tests/integration/test_dify_plugin_integration.py (~14 tests)
16. ✅ tests/integration/test_end_to_end.py (~8 tests)
17. ✅ tests/integration/test_full_pipeline_real_docs.py (~14 tests)
18. ✅ tests/integration/test_overlap_redesign_integration.py (~12 tests)

**Note**: 4 tests originally marked as P0 are not in this list (monotonic_ordering, no_empty_chunks, serialization_roundtrip, overlap_new_model) because they have import errors.

## Legacy Import Analysis

### Import Error Categories

**Category 1: Direct legacy chunker imports** (most common)
```python
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig, Chunk
```
**Fix**: 
```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk
```

**Category 2: Legacy component imports**
```python
from markdown_chunker.chunker.components import OverlapManager
```
**Fix**: Components are integrated in v2, use strategy-level overlap or compatibility layer

**Category 3: Legacy parser imports**
```python
from markdown_chunker.parser import ParserInterface, extract_fenced_blocks
```
**Fix**:
```python
from markdown_chunker_v2.parser import Parser
```

**Category 4: Legacy strategy imports**
```python
from markdown_chunker.chunker.strategies.code_strategy import CodeStrategy
```
**Fix**:
```python
from markdown_chunker_v2.strategies import CodeAwareStrategy
```

### Files with Most Import Errors

Based on test collection, the top directories with import errors:

1. **tests/chunker/** - 50+ import errors (legacy chunker core)
2. **tests/parser/** - 25+ import errors (legacy parser)
3. **tests/integration/** - 10+ import errors (legacy pipeline)
4. **tests/api/** - 5+ import errors (legacy API layer)

## Next Steps

### Immediate Actions (This Sprint)

1. ✅ **COMPLETED**: Update Makefile with `test-p0` target
2. ✅ **COMPLETED**: Document P0 test failures and migration requirements
3. **TODO**: Migrate 6 failing P0 tests (Tasks 1-6 above)
4. **TODO**: Verify all P0 tests pass after migration
5. **TODO**: Update CI to run `make test-p0` on every commit

### Short-term Actions (Next Sprint)

1. Create migration scripts for common import patterns
2. Begin P1 test migration (67 test files)
3. Establish test coverage baseline for v2
4. Document v2 behavioral differences from legacy

### Medium-term Actions (Sprints 3-4)

1. Migrate P2 tests opportunistically
2. Archive non-migratable tests (Category E)
3. Remove legacy code dependencies
4. Achieve 90% test coverage for v2

## Metrics Tracking

### Test Count Over Time

| Date | Total Tests | P0 Tests Passing | P1 Tests Passing | Coverage % |
|------|-------------|------------------|------------------|------------|
| 2025-12-05 (Baseline) | 475 | 210/~320 (66%) | 0/~850 (0%) | TBD |
| Target (End of Sprint) | 475 | ~320/~320 (100%) | 0/~850 (0%) | >70% |

### Import Error Tracking

| Date | Total Import Errors | P0 Import Errors | P1 Import Errors |
|------|---------------------|------------------|------------------|
| 2025-12-05 (Baseline) | 98 | 6 | ~60 |
| Target (End of Sprint) | ~92 | 0 | ~60 |

## Test Migration Checklist Template

Use this checklist when migrating each test file:

```markdown
### Test File: [filename]

- [ ] Read test file and understand what it validates
- [ ] Update imports to v2 modules
- [ ] Adapt ChunkConfig usage (8 params vs 32)
- [ ] Update strategy references (6 strategies → 3)
- [ ] Adapt test assertions for v2 behavior
- [ ] Run test and verify it passes
- [ ] Check for deprecation warnings
- [ ] Update test documentation/comments
- [ ] Remove legacy-specific test cases
- [ ] Add migration note to test docstring
- [ ] Commit changes with descriptive message
```

## Risk Log

### Active Risks

**Risk 1**: Some P0 tests may pass after import migration but validate different behavior
- **Mitigation**: Manual review of each migrated test's assertions
- **Status**: Monitoring during migration

**Risk 2**: V2 behavioral differences may cause unexpected test failures
- **Mitigation**: Document intentional differences, adapt tests accordingly
- **Status**: To be addressed during migration

### Resolved Risks

None yet.

## Appendix: Commands Reference

### Test Collection
```bash
# Count all tests
pytest tests/ --collect-only -q | tail -1

# List all test files with errors
pytest tests/ --collect-only 2>&1 | grep ERROR

# Collect tests from specific directory
pytest tests/chunker/ --collect-only -q
```

### Test Execution
```bash
# Run core v2 tests
make test

# Run P0 tests (after migration)
make test-p0

# Run all tests (with errors)
make test-all

# Run specific test file
venv/bin/python3.12 -m pytest tests/test_domain_properties.py -v

# Run with coverage
make test-coverage
```

### Import Analysis
```bash
# Find legacy chunker imports
grep -r "from markdown_chunker\.chunker" tests/ | wc -l

# Find legacy parser imports
grep -r "from markdown_chunker\.parser" tests/ | wc -l

# Find specific import pattern
grep -r "from markdown_chunker\.chunker\.core import" tests/
```

## References

- **Design Document**: [legacy-test-analysis.md](./legacy-test-analysis.md)
- **Migration Guide**: [docs/MIGRATION.md](../../docs/MIGRATION.md)
- **V2 Documentation**: [docs/README.md](../../docs/README.md)
- **Test Framework**: pytest configuration in [pytest.ini](../../pytest.ini)
