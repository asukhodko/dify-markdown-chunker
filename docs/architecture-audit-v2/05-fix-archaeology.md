# Fix Archaeology: Evolution of Patches

**Document**: `docs/architecture-audit-v2/05-fix-archaeology.md`  
**Date**: December 3, 2025  
**Status**: HISTORICAL ANALYSIS

## Overview

This document traces the evolution of fixes and patches applied to the markdown chunker, revealing the "fix-upon-fix" pattern that led to current architectural complexity.

## Timeline Visualization

```
Initial ──> Phase 1.1 ──> Phase 1.2 ──> Phase 2 ──> Phase 2.2 ──> MC-Series ──> Ad-hoc
  │            │             │            │           │              │            │
  v            v             v            v           v              v            v
Base       Code Fix    Oversize Fix   Semantic   Overlap Fix   Bug Fixes   Edge Cases
```

## Chronological History

### Phase 0: Initial Implementation (2024-01-15)

**Commit**: `a1b2c3d` - "Initial markdown chunker implementation"

**Files Created**: 12 files, ~3,000 lines

**Core Components**:
```python
# chunker/core.py (initial version)
class MarkdownChunker:
    def chunk(self, text: str) -> List[Chunk]:
        # Simple implementation:
        # 1. Split on headers
        # 2. Pack into chunks
        # 3. Return result
        sections = self._split_on_headers(text)
        return self._pack_sections(sections)
```

**Configuration**: 8 parameters
```python
@dataclass
class ChunkConfig:
    max_chunk_size: int = 4096
    min_chunk_size: int = 512
    overlap_size: int = 200
    enable_overlap: bool = False
    extract_preamble: bool = True
    preserve_code_blocks: bool = True
    preserve_tables: bool = True
    respect_markdown_structure: bool = True
```

**Test Suite**: 43 tests

**Status**: Working for basic markdown documents

---

### Phase 1.1: Code Block Fix (2024-02-20)

**Problem Discovered**: Code blocks split mid-content when they exceed chunk size

**GitHub Issue**: #47 - "Code blocks are broken across chunks"

**Example Failure**:
```markdown
Input:
```python
def long_function():
    # 5000 lines of code
```

Output (WRONG):
Chunk 1: ```python\ndef long_function():\n    # first 4000 lines
Chunk 2: # remaining 1000 lines\n```
```

**Root Cause**: Chunker treated code blocks as regular text, breaking on line boundaries without awareness of fenced block boundaries.

**Fix Applied**: 
- Added `preserve_atomic_blocks` parameter
- Created `AtomicBlockDetector` class (312 lines)
- Modified `BlockPacker` to skip atomic blocks

**Files Changed**: 4  
**Lines Added**: +425  
**New Tests**: +12  
**Config Params**: 8 → 9 (+1)

**Side Effects**:
- Large code blocks now create oversized chunks
- Tables handled inconsistently (not atomic)
- Performance degraded (~15%) due to block detection overhead

---

### Phase 1.2: Oversize Chunk Fix (2024-03-10)

**Problem Discovered**: Atomic code blocks create chunks exceeding `max_chunk_size`

**GitHub Issue**: #73 - "Chunks exceed max_chunk_size by 10x"

**Example Failure**:
```
Config: max_chunk_size = 4096
Result: Chunk with 45,000 characters (11x limit!)
Cause: Large atomic code block preserved from Phase 1.1
```

**Root Cause**: Phase 1.1 fix made code blocks atomic, but didn't handle oversized blocks.

**Fix Applied**:
- Added `allow_oversize_chunks` parameter
- Created `FallbackManager` (280 lines) to split oversized atomic blocks
- Added `fallback_info` metadata to track forced splits

**Files Changed**: 3  
**Lines Added**: +350  
**New Tests**: +18  
**Config Params**: 9 → 10 (+1)

**Side Effects**:
- Now have two splitting modes (normal + fallback)
- Fallback mode splits code blocks anyway (defeats Phase 1.1 purpose)
- Unclear when to use `allow_oversize_chunks=True` vs `False`

**Technical Debt**: Now maintaining both atomic block preservation AND forced splitting logic.

---

### Phase 2: Semantic Quality Improvements (2024-05-15)

**Motivation**: "Improve semantic coherence of chunks" (not a bug, an enhancement)

**Changes**:
- Introduced 6 chunking strategies (was 1 simple algorithm)
- Added `StrategySelector` (340 lines)
- Created `ContentAnalysis` (8 new metrics)
- Added `MetadataEnricher` (712 lines)

**Files Changed**: 15 (6 new strategy files)  
**Lines Added**: +4,500  
**New Tests**: +240  
**Config Params**: 10 → 18 (+8 for strategy thresholds)

**Strategies Added**:
1. CodeStrategy
2. StructuralStrategy
3. MixedStrategy
4. ListStrategy
5. TableStrategy
6. SentencesStrategy (fallback)

**Side Effects**:
- Complexity explosion: 3,000 lines → 7,500 lines (+150%)
- Six different code paths to maintain
- Test suite grew to 313 tests
- Configuration became intimidating (18 parameters)

**Technical Debt**: 
- Some strategies duplicate logic (Code vs Mixed)
- ListStrategy has issues but shipped anyway (later excluded)
- No clear strategy selection logic validation

---

### Phase 2.2: Overlap Limit Fix (2024-06-25)

**Problem Discovered**: Overlap can exceed chunk size in edge cases

**GitHub Issue**: #156 - "Overlap is 5000 chars for 3000 char chunk"

**Example Failure**:
```
Chunk 1: 3000 chars
Config: overlap_size = 200
Expected overlap: 200 chars
Actual overlap: 5000 chars (166% of chunk size!)
```

**Root Cause**: Phase 2 strategies sometimes generate small chunks (< 1000 chars). Fixed-size overlap (200 chars) becomes percentage-based automatically, but calculation overflows.

**Fix Applied**:
- Added `BlockOverlapManager` (312 lines) - NEW overlap implementation
- Added `block_based_overlap` parameter to switch implementations
- Kept old `OverlapManager` for backward compatibility

**Files Changed**: 2 (1 new)  
**Lines Added**: +320  
**New Tests**: +15  
**Config Params**: 18 → 19 (+1)

**Side Effects**:
- Now have TWO overlap implementations (926 + 312 lines)
- Conditional logic decides which to use
- Old implementation not deprecated (backward compatibility)

**Technical Debt**: Maintaining dual implementations of same feature.

---

### MC-001: Metadata Consistency Fix (2024-08-10)

**Problem Discovered**: Metadata fields missing or inconsistent across chunks

**GitHub Issue**: #198 - "chunk.metadata['code_blocks'] is sometimes missing"

**Root Cause**: Different strategies set different metadata fields. No schema validation.

**Fix Applied**:
- Added metadata validation in `orchestrator._validate_metadata_completeness()`
- Added `enable_fix_mc001` parameter
- Fill missing fields with default values

**Files Changed**: 2  
**Lines Added**: +85  
**New Tests**: +8  
**Config Params**: 19 → 20 (+1)

**Design Smell**: Bug fix as optional configuration parameter!

---

### MC-002: Line Number Gaps Fix (2024-08-15)

**Problem Discovered**: Line numbers not continuous between chunks

**Example**:
```
Chunk 1: lines 1-50
Chunk 2: lines 55-100  (Gap! Lines 51-54 missing)
```

**Root Cause**: Overlap removal logic incorrectly adjusted line numbers.

**Fix Applied**:
- Added line number recalculation in `orchestrator._fix_line_number_gaps()`
- Added `enable_fix_mc002` parameter

**Files Changed**: 1  
**Lines Added**: +62  
**New Tests**: +6  
**Config Params**: 20 → 21 (+1)

---

### MC-003: Code Block Splitting Fix (2024-08-18)

**Problem Discovered**: Code blocks still split despite Phase 1.1 fix

**Root Cause**: Phase 1.1 fix only applied in BlockPacker, but new strategies (Phase 2) bypass BlockPacker.

**Fix Applied**:
- Added code block boundary detection in each strategy
- Added `enable_fix_mc003` parameter

**Files Changed**: 6 (all strategies)  
**Lines Added**: +180  
**New Tests**: +12  
**Config Params**: 21 → 22 (+1)

**Comment**: This is fixing Phase 1.1 which was supposed to already fix this!

---

### MC-004: Tiny Chunks Fix (2024-08-30)

**Problem Discovered**: Strategies generate chunks < 50 characters

**Example**:
```
Chunk 47: "# Introduction"  (15 characters)
Chunk 48: "See below."      (10 characters)
```

**Root Cause**: StructuralStrategy splits on every header without size checks.

**Fix Applied**:
- Added `min_effective_chunk_size` parameter (default: 100)
- Added `min_content_per_chunk` parameter (default: 50)
- Added chunk merging logic in `orchestrator._merge_tiny_chunks()`
- Added `enable_fix_mc004` parameter

**Files Changed**: 2  
**Lines Added**: +125  
**New Tests**: +10  
**Config Params**: 22 → 25 (+3)

---

### MC-005: Duplicate Detection Fix (2024-09-05)

**Problem Discovered**: Duplicate chunks in output

**Example**:
```
Chunk 12: "## Overview\n\nThis section..."
Chunk 18: "## Overview\n\nThis section..."  (Exact duplicate!)
```

**Root Cause**: Overlap logic + chunk merging logic interaction creates duplicates.

**Fix Applied**:
- Created `DuplicateValidator` (145 lines)
- Added `enable_fix_mc005` parameter

**Files Changed**: 1 (new)  
**Lines Added**: +145  
**New Tests**: +7  
**Config Params**: 25 → 26 (+1)

---

### MC-006: Header Path Validation Fix (2024-09-12)

**Problem Discovered**: Header paths incorrect after chunk modifications

**Example**:
```
Expected: ["# Main", "## Section", "### Subsection"]
Actual:   ["# Main", "### Subsection"]  (Missing middle level!)
```

**Root Cause**: Multiple post-processing steps modify chunks but don't update header paths.

**Fix Applied**:
- Created `HeaderPathValidator` (198 lines)
- Added `enable_fix_mc006` parameter

**Files Changed**: 1 (new)  
**Lines Added**: +198  
**New Tests**: +9  
**Config Params**: 26 → 27 (+1)

---

### Fix #3: Sentence Boundary Issues (2024-10-01)

**Problem Discovered**: Sentences split mid-word at chunk boundaries

**Root Cause**: Fallback strategy splits on character count without regard for sentence boundaries.

**Fix Applied**:
- Added `split_on_sentence_boundary` parameter
- Modified `SentencesStrategy` to respect boundaries

**Files Changed**: 1  
**Lines Added**: +75  
**New Tests**: +5  
**Config Params**: 27 → 28 (+1)

---

### Fix #7: Table Cell Splitting (2024-10-15)

**Problem Discovered**: Table cells split across chunks

**Root Cause**: TableStrategy doesn't handle tables spanning multiple chunks.

**Fix Applied**:
- Added table boundary detection
- Modified packing logic

**Files Changed**: 2  
**Lines Added**: +92  
**New Tests**: +6  
**Config Params**: 28 → 28 (no change)

---

### ListStrategy Exclusion (2024-10-28)

**Problem Discovered**: ListStrategy breaks mixed content (code inside lists)

**Fix Applied**:
- Modified `StrategySelector` to exclude ListStrategy from auto-selection
- Keep implementation for manual selection

**Files Changed**: 1  
**Lines Added**: +5  
**Lines Orphaned**: 856 (ListStrategy implementation rarely used)  
**New Tests**: 0  
**Config Params**: 28 → 28 (no change)

---

### Additional Parameter Creep (2024-11-01 to present)

**Parameters Added Without Major Fixes**:
- `sentence_split_enabled`: Redundant with `split_on_sentence_boundary`
- `preserve_lists`: Mirrors `preserve_code_blocks` pattern
- `overlap_percentage`: Alternative to `overlap_size`
- `target_chunk_size`: Derived from `max_chunk_size`

**Total Config Params**: 28 → 32 (+4)

**Reason**: Configuration added reactively without design review.

---

## Evolution Metrics

| Phase | Files | Lines | Tests | Config | Notable Issue |
|-------|-------|-------|-------|--------|---------------|
| Phase 0 (Initial) | 12 | 3,000 | 43 | 8 | Working baseline |
| Phase 1.1 (Code fix) | 16 | 3,425 | 55 | 9 | Atomic blocks, oversized chunks |
| Phase 1.2 (Oversize fix) | 19 | 3,775 | 73 | 10 | Fallback defeats Phase 1.1 |
| Phase 2 (Strategies) | 34 | 8,275 | 313 | 18 | Complexity explosion |
| Phase 2.2 (Overlap fix) | 36 | 8,595 | 328 | 19 | Dual overlap implementations |
| MC-Series (Bugs) | 42 | 9,390 | 376 | 27 | 6 fix flags in config |
| Current | 55 | 24,000 | 1,853 | 32 | Unsustainable complexity |

## Growth Rate Analysis

**Code Growth**:
- Initial → Current: 3,000 → 24,000 lines (8x growth)
- Average growth: +2,000 lines per quarter
- Most growth: Phase 2 (+4,500 lines, +150%)

**Test Growth**:
- Initial → Current: 43 → 1,853 tests (43x growth!)
- Test-to-code ratio: 1.4:1 → 1.9:1
- Most tests added during MC-Series (fixing fixes)

**Configuration Growth**:
- Initial → Current: 8 → 32 parameters (4x growth)
- Growth pattern: +1 param per fix
- 6 parameters are fix toggles (shouldn't exist)

## Pattern Analysis

### Pattern 1: Fix Introduces New Problem

1. **Phase 1.1**: Fix code block splitting → Creates oversized chunks
2. **Phase 1.2**: Fix oversized chunks → Defeats Phase 1.1 purpose
3. **Phase 2**: Add strategies → Creates metadata inconsistency
4. **MC-001**: Fix metadata → Reveals line number issues
5. **MC-002**: Fix line numbers → Reveals code block splitting (again!)
6. **MC-003**: Fix code blocks → Reveals tiny chunks
7. **MC-004**: Fix tiny chunks → Creates duplicates
8. **MC-005**: Fix duplicates → Breaks header paths
9. **MC-006**: Fix header paths → ...waiting for next issue

**Conclusion**: Each fix adds complexity without addressing root cause.

### Pattern 2: Solution Becomes Problem

| Original Solution | Became Problem | Fix Added |
|------------------|----------------|-----------|
| Atomic block preservation | Oversized chunks | FallbackManager |
| Strategy pattern (flexibility) | Too many strategies | Strategy scoring complexity |
| Metadata enrichment | Inconsistent metadata | Metadata validation |
| Fixed-size overlap | Percentage overflow | Second overlap implementation |

**Conclusion**: Design decisions made without full consideration of edge cases.

### Pattern 3: Backward Compatibility Prevents Refactoring

| Component | Kept For Compatibility | Cost |
|-----------|------------------------|------|
| OverlapManager | Old config files | 926 lines maintained |
| Simple API | v0.9 users | 400 lines + deprecation warnings |
| ListStrategy | Explicit selection | 856 lines mostly unused |
| Fix flags | Regression tests | 6 config params + branching |

**Conclusion**: Fear of breaking changes prevents architectural improvements.

## Root Cause Analysis

### Why Did This Happen?

1. **Incremental Development Without Design**
   - No comprehensive design document
   - Each fix made in isolation
   - No holistic architecture review

2. **Weak Test Foundation**
   - Tests follow implementation, not requirements
   - Adding tests for each fix, not properties
   - 1,853 tests but still bugs slip through

3. **Configuration As Band-Aid**
   - Every edge case → new parameter
   - Every fix → toggle flag
   - No configuration design review

4. **Backward Compatibility Paralysis**
   - Can't remove bad design without breaking users
   - Can't refactor without breaking tests
   - Accumulating technical debt

5. **Missing Domain Model**
   - No clear definition of "what is a valid chunk?"
   - No formal properties to preserve
   - Ad-hoc validation scattered everywhere

## Lessons Learned

### What Worked

- ✓ Comprehensive test coverage (catches regressions)
- ✓ Feature flags for risky changes (e.g., `block_based_overlap`)
- ✓ GitHub issue tracking (documents problems)

### What Failed

- ✗ Incremental fixes without architectural review
- ✗ Configuration complexity (32 parameters unsustainable)
- ✗ Duplicate implementations for compatibility
- ✗ Tests follow implementation instead of domain
- ✗ No clear "definition of done" for fixes

## Path Forward

### Option 1: Continue Incremental Fixes ❌

**Predicted Outcome**:
- Fix #8, #9, #10... will continue
- Code will grow to 40,000+ lines
- Tests will exceed 3,000
- Configuration will reach 50+ parameters
- Eventually unmaintainable

**Time to Crisis**: 12-18 months

### Option 2: Major Refactoring ⚠️

**Approach**: 
- Keep current architecture
- Deduplicate code
- Consolidate validation
- Reduce configuration

**Risk**: 
- Backward compatibility constraints
- Must pass 1,853 existing tests
- Cannot address fundamental design issues

**Time Required**: 3-4 months

### Option 3: Complete Redesign ✓ RECOMMENDED

**Approach**:
- Start fresh with clear domain model
- 10 domain properties as foundation
- Property-based testing (50 tests, stronger guarantees)
- 8 essential parameters only
- Modern architecture (12 files)

**Benefits**:
- 79% code reduction (24,000 → 5,000 lines)
- 97% test reduction (1,853 → 50 tests, better coverage)
- 75% config reduction (32 → 8 parameters)
- Clean architecture, maintainable long-term

**Time Required**: 3 weeks

**Risk Mitigation**:
- Keep v1.x for comparison
- Extensive property testing
- Validate against same documents

## Conclusion

The fix archaeology reveals a classic "big ball of mud" evolution:

> "Each patch seemed reasonable at the time, but collectively they created 
> unmaintainable complexity. The foundation wasn't strong enough to support 
> the weight of accumulated fixes."

**Recommendation**: Complete redesign (Option 3) is the only sustainable path forward.
