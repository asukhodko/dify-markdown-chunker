# P0 Test Migration Task Tracker

**Phase**: Phase 1 - Foundation  
**Sprint Goal**: Migrate all P0 priority tests to be v2-compatible  
**Target Completion**: End of current sprint

## Task Overview

| Task # | Test File | Status | Estimated | Actual | Assignee | Blocker |
|--------|-----------|--------|-----------|--------|----------|---------|
| 1 | test_monotonic_ordering_property.py | 🔴 Not Started | 30min | - | - | - |
| 2 | test_no_empty_chunks_property.py | 🔴 Not Started | 30min | - | - | - |
| 3 | test_serialization_roundtrip_property.py | 🔴 Not Started | 30min | - | - | - |
| 4 | test_overlap_new_model.py | 🔴 Not Started | 1h | - | - | - |
| 5 | test_smoke.py (parser) | 🔴 Not Started | 1h | - | - | - |
| 6 | test_career_matrix.py | 🔴 Not Started | 45min | - | - | - |

**Legend**: 🔴 Not Started | 🟡 In Progress | 🟢 Complete | ⚫ Blocked

**Total Effort**: ~4.5 hours

## Task Details

---

### Task 1: Migrate Monotonic Ordering Property Test

**File**: `tests/chunker/test_monotonic_ordering_property.py`  
**Category**: A (High Value + Easy Migration)  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.chunker.core'
```

**Required Changes**:

1. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# NEW (v2)
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
```

2. **Config adaptation** (if applicable):
   - Review ChunkConfig usage in tests
   - Adapt to v2's 8 parameters (from legacy 32)

3. **Assertion updates**:
   - Verify monotonic ordering property still holds in v2
   - Check metadata field names (may differ in v2)

**Validation Steps**:
- [ ] File imports successfully
- [ ] All test functions/methods run without errors
- [ ] All assertions pass
- [ ] No deprecation warnings
- [ ] Test validates same property in v2 as it did in legacy

**Acceptance Criteria**:
- Test file runs successfully with `pytest tests/chunker/test_monotonic_ordering_property.py -v`
- All tests pass
- Property PROP-3 (Monotonic Ordering) is validated

---

### Task 2: Migrate No Empty Chunks Property Test

**File**: `tests/chunker/test_no_empty_chunks_property.py`  
**Category**: A (High Value + Easy Migration)  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.chunker.core'
```

**Required Changes**:

1. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# NEW (v2)
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
```

2. **Config adaptation** (if applicable):
   - Review ChunkConfig usage
   - Adapt to v2 parameters

3. **Assertion updates**:
   - Verify no empty chunks property holds in v2
   - Check that v2 filters empty chunks correctly

**Validation Steps**:
- [ ] File imports successfully
- [ ] All test functions/methods run without errors
- [ ] All assertions pass
- [ ] No deprecation warnings
- [ ] Test validates same property in v2

**Acceptance Criteria**:
- Test file runs successfully
- All tests pass
- Property PROP-4 (No Empty Chunks) is validated

---

### Task 3: Migrate Serialization Roundtrip Property Test

**File**: `tests/chunker/test_serialization_roundtrip_property.py`  
**Category**: A (High Value + Easy Migration)  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.chunker.core'
```

**Required Changes**:

1. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig, Chunk

# NEW (v2)
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig, Chunk
```

2. **Type adaptation**:
   - Verify v2 Chunk type has same serializable fields
   - Check if v2 types use Pydantic (should be compatible)

3. **Serialization logic**:
   - Verify serialization methods (to_dict, from_dict, JSON)
   - Ensure roundtrip works with v2 types

**Validation Steps**:
- [ ] File imports successfully
- [ ] Chunk serialization works
- [ ] Roundtrip preserves all data
- [ ] All tests pass
- [ ] JSON serialization works

**Acceptance Criteria**:
- Test file runs successfully
- Serialization roundtrip property holds
- No data loss during serialization/deserialization

---

### Task 4: Migrate Overlap New Model Test

**File**: `tests/chunker/test_components/test_overlap_new_model.py`  
**Category**: A (High Value + Easy Migration) *but may be moderate effort*  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.chunker.components'
```

**Required Changes**:

1. **Understanding v2 overlap**:
   - V2 does not have separate OverlapManager component
   - Overlap is integrated into strategies
   - Review v2 overlap implementation in strategies/base.py

2. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.chunker.components import OverlapManager
from markdown_chunker.chunker.types import ChunkConfig

# NEW (v2) - depends on what's being tested
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
from markdown_chunker_v2.chunker import MarkdownChunker
# May need to access overlap logic through strategies or chunker
```

3. **Test logic adaptation**:
   - Identify what "new model" refers to
   - Check if this was designed for v2 overlap already
   - Adapt tests to v2's integrated overlap approach

**Investigation Needed**:
- [ ] Read test file to understand what it validates
- [ ] Check if it tests metadata mode vs legacy mode
- [ ] Determine if test is already v2-oriented
- [ ] Identify v2 equivalent functionality

**Validation Steps**:
- [ ] Understand test purpose
- [ ] Update imports appropriately
- [ ] Adapt test logic to v2 overlap
- [ ] Verify overlap behavior matches expectations
- [ ] All tests pass

**Acceptance Criteria**:
- Test validates v2 overlap functionality
- Overlap metadata is correct
- Test passes with v2 implementation

**Notes**:
- This test was categorized as "likely designed for v2" in the registry
- May already be v2-compatible after import fixes

---

### Task 5: Migrate Parser Smoke Tests

**File**: `tests/parser/test_smoke.py`  
**Category**: A (High Value + Easy Migration) *but moderate effort*  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.parser'
```

**Required Changes**:

1. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.parser import (
    ParserInterface,
    extract_fenced_blocks,
    ContentAnalysis,
    # ... other legacy parser imports
)

# NEW (v2)
from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ContentAnalysis, FencedBlock
```

2. **API adaptation**:
   - V2 parser has simplified interface
   - Legacy: `ParserInterface()` with complex API
   - V2: `Parser()` with clean parse() method

3. **Test updates**:
   - Adapt parser instantiation
   - Update method calls to v2 API
   - Verify smoke tests cover v2 parser basics

**V2 Parser API Reference**:
```python
# V2 usage
parser = Parser()
analysis = parser.parse(md_text)
# Returns ContentAnalysis with fenced_blocks, headers, etc.
```

**Validation Steps**:
- [ ] Understand legacy parser API being tested
- [ ] Map legacy API to v2 equivalents
- [ ] Update all parser method calls
- [ ] Verify smoke tests pass with v2
- [ ] Check coverage of basic parser functionality

**Acceptance Criteria**:
- Smoke tests validate basic v2 parser functionality
- All critical parser features are tested
- Tests run quickly (smoke tests should be fast)

---

### Task 6: Migrate Career Matrix Integration Test

**File**: `tests/integration/test_career_matrix.py`  
**Category**: A (High Value + Easy Migration)  
**Priority**: P0  
**Status**: 🔴 Not Started

**Current Issue**:
```
ModuleNotFoundError: No module named 'markdown_chunker.chunker.core'
```

**Required Changes**:

1. **Import updates**:
```python
# OLD (legacy)
from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig

# NEW (v2)
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig
```

2. **Config adaptation**:
   - Career matrix test likely uses custom config
   - Map legacy config parameters to v2 (8 params)
   - Example mapping:
     ```python
     # Legacy (32 params)
     config = ChunkConfig(
         max_chunk_size=2048,
         min_chunk_size=256,
         enable_overlap=True,
         block_based_splitting=True,
         preserve_code_blocks=True,
         # ... 27 more params
     )
     
     # V2 (8 params)
     config = ChunkConfig(
         max_chunk_size=2048,
         min_chunk_size=256,
         overlap_size=100,
         enable_overlap=True,
         preserve_atomic_blocks=True,  # replaces several legacy flags
     )
     ```

3. **Assertion adaptation**:
   - Real-world document test validates chunking quality
   - May need to adapt assertions to v2 behavior
   - Strategy selection may differ (v2 has 3 strategies vs legacy 6)

**Investigation Needed**:
- [ ] Check what career matrix document contains
- [ ] Understand what test validates (chunk count, metadata, etc.)
- [ ] Identify config parameters used

**Validation Steps**:
- [ ] File imports successfully
- [ ] Config parameters mapped correctly
- [ ] Document chunks successfully
- [ ] Assertions reflect v2 behavior
- [ ] Test validates real-world chunking quality

**Acceptance Criteria**:
- Test runs successfully with v2
- Real-world document chunks appropriately
- Quality metrics (if any) are met
- Test validates production-ready behavior

---

## Progress Tracking

### Daily Standup

**What was completed yesterday**:
- [Update with completed tasks]

**What will be worked on today**:
- [Update with current focus]

**Blockers**:
- [Update with any blockers]

### Weekly Summary

**Week of**: [Date]

**Completed**:
- [ ] Task 1: test_monotonic_ordering_property.py
- [ ] Task 2: test_no_empty_chunks_property.py
- [ ] Task 3: test_serialization_roundtrip_property.py
- [ ] Task 4: test_overlap_new_model.py
- [ ] Task 5: test_smoke.py
- [ ] Task 6: test_career_matrix.py

**Completion Rate**: 0/6 (0%)

**Total Time Spent**: 0h / 4.5h estimated

**Blockers Encountered**:
- None yet

**Learnings**:
- [Document any insights from migration process]

## Success Criteria

The P0 test migration is complete when:

1. ✅ All 6 test files import successfully
2. ✅ `make test-p0` runs without collection errors
3. ✅ All P0 tests pass (100% pass rate)
4. ✅ No deprecation warnings in P0 tests
5. ✅ Test coverage for v2 is >70%
6. ✅ Documentation updated with migration notes

## Next Steps After P0 Completion

1. **Update CI/CD**: Add `make test-p0` to CI pipeline
2. **Document learnings**: Create migration guide based on P0 experience
3. **Plan P1 migration**: Apply learnings to 67 P1 test files
4. **Celebrate**: P0 completion is a major milestone! 🎉

## References

- **Status Report**: [test-migration-status.md](./test-migration-status.md)
- **Design Document**: [legacy-test-analysis.md](./legacy-test-analysis.md)
- **V2 API**: See `markdown_chunker_v2/` module documentation
- **Migration Guide**: [docs/MIGRATION.md](../../docs/MIGRATION.md)
