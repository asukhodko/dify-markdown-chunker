# Changelog - Overlap Redesign

## Version: Overlap Redesign (UNRELEASED)

### Breaking Changes

#### Metadata Field Changes

**Removed Fields:**
- `overlap_prefix` - Replaced by `previous_content`
- `overlap_suffix` - Replaced by `next_content`
- `has_overlap` - Replaced by presence/absence of context fields
- `overlap_type` - No longer needed (direction is implicit in field names)
- `overlap_size` - Derivable from context field lengths
- `overlap_block_ids` - Internal implementation detail, removed from external API
- `overlap_start_offset` - Internal implementation detail, removed from external API
- `new_content_start_offset` - Internal implementation detail, removed from external API

**New Fields:**
- `previous_content` (string, optional) - Context fragment from the end of the preceding chunk
- `next_content` (string, optional) - Context fragment from the beginning of the following chunk
- `previous_chunk_index` (int|null, optional) - Index of the chunk from which `previous_content` was extracted
- `next_chunk_index` (int|null, optional) - Index of the chunk from which `next_content` was extracted

#### Semantic Changes

**Old Model:**
- `overlap_prefix`: Fragment of the CURRENT chunk intended for overlap
- `overlap_suffix`: Fragment of the CURRENT chunk intended for overlap

**New Model:**
- `previous_content`: Context FROM the PREVIOUS chunk (neighbor's ending)
- `next_content`: Context FROM the NEXT chunk (neighbor's beginning)

This is a fundamental semantic shift from "what I share" to "what context I receive from neighbors".

### New Features

#### Explicit Neighbor Context Model

The overlap mechanism now uses an explicit neighbor context model:

1. **Independent Extraction**: `previous_content` and `next_content` are independently extracted from neighbors
2. **No Symmetry Requirement**: No requirement that `chunks[i].next_content == chunks[i+1].previous_content`
3. **Traceability**: Chunk index fields allow tracking context to source chunks
4. **Clean Separation**: In metadata mode, chunk content is completely separate from neighbor context

#### Mode-Specific Behavior

**Metadata Mode** (`include_metadata=true`):
- `content` field contains only the chunk's core content
- `len(content) == end_offset - start_offset` (strict equality)
- Neighbor contexts stored in metadata fields
- Full context: `previous_content + content + next_content`

**Legacy Mode** (`include_metadata=false`):
- `content` field contains merged context: `previous_content + content_core + next_content`
- `start_offset` and `end_offset` still describe only the core content range
- `len(content) != end_offset - start_offset` in general
- No context fields added to metadata

#### Improved Edge Case Handling

1. **Overlap Disabled**: Proper no-op when `enable_overlap=false` or `effective_overlap=0`
2. **Boundary Chunks**: First chunk has no `previous_content`, last chunk has no `next_content`
3. **Empty Contexts**: Fields are omitted entirely when context extraction yields empty string
4. **Section Isolation**: No cross-section context extraction

### Bug Fixes

#### Anti-Fraud Duplication Issue

Fixed critical bug where content could be duplicated within a single chunk due to incorrect overlap handling.

**Example:**
- Phrase "Изучил подходы anti fraud в других компаниях." previously appeared twice consecutively
- Now appears once in chunk content and once in neighbor's context (separate fields)

**Root Cause:**
- Old model merged overlap into current chunk's content incorrectly
- Led to duplication when overlap zones overlapped with chunk boundaries

**Solution:**
- New neighbor context model prevents duplication
- Clear separation between chunk content and neighbor contexts
- Block-aligned extraction ensures structural integrity

### Implementation Details

#### OverlapManager Refactoring

**File**: `markdown_chunker/chunker/components/overlap_manager.py`

- Complete rewrite of `apply_overlap()` method
- New single-pass processing over core chunks
- Added `_calculate_effective_overlap()` for computing overlap limits
- Added `_extract_suffix_context()` for extracting `previous_content`
- Added `_extract_prefix_context()` for extracting `next_content`
- Added `_add_context_to_metadata()` for metadata mode
- Added `_merge_context_into_content()` for legacy mode
- Removed deprecated methods (9 methods removed)

#### Effective Overlap Calculation

```python
effective_overlap = min(
    overlap_size,                           # = chunk_overlap parameter
    overlap_percentage * len(content_core)  # percentage-based limit
)
```

Additional constraints:
- Maximum 40% ratio relative to source chunk size
- Minimum 50 characters for small chunks
- Block-aligned extraction preserved

### Migration Guide

#### For Applications Using Metadata

**Before:**
```python
if 'overlap_prefix' in chunk.metadata:
    prefix = chunk.metadata['overlap_prefix']
if 'overlap_suffix' in chunk.metadata:
    suffix = chunk.metadata['overlap_suffix']
```

**After:**
```python
if 'previous_content' in chunk.metadata:
    prev_context = chunk.metadata['previous_content']
    prev_index = chunk.metadata.get('previous_chunk_index')
    
if 'next_content' in chunk.metadata:
    next_context = chunk.metadata['next_content']
    next_index = chunk.metadata.get('next_chunk_index')
```

#### For Applications Using Legacy Mode

No changes required - legacy mode maintains backward-compatible behavior of merging context into content.

#### Semantic Differences

**Old Model** - "What I share":
- `overlap_prefix`: Part of my content that overlaps with previous
- `overlap_suffix`: Part of my content that overlaps with next

**New Model** - "What context I receive":
- `previous_content`: Context from my predecessor
- `next_content`: Context from my successor

### Testing

#### New Test Files

1. `tests/chunker/test_components/test_overlap_new_model.py` - 15 unit tests
2. `tests/integration/test_overlap_redesign_integration.py` - 10 integration tests
3. `tests/regression/test_overlap_duplication.py` - 7 regression tests

#### Test Coverage

- Context field validation
- Mode equivalence testing
- Offset integrity verification
- Boundary condition handling
- Anti-fraud duplication regression
- Code fence balancing
- Section isolation

### Performance

Expected performance impact: Within 5% of baseline (to be validated)

### Documentation Updates

- README.md - Updated overlap handling section
- tools/markdown_chunk_tool.py - Updated metadata filtering
- OVERLAP_REDESIGN_STATUS.md - Implementation status document

### Backward Compatibility

#### Compatible

- Legacy mode (`include_metadata=false`) maintains merged content behavior
- Overall chunking logic unchanged
- Configuration parameters unchanged (`enable_overlap`, `overlap_size`, `overlap_percentage`)

#### Incompatible

- Metadata field names changed (breaking change for metadata consumers)
- Semantic meaning of overlap changed (from "what I share" to "what context I receive")
- Legacy metadata fields (`has_overlap`, `overlap_type`, `overlap_size`) removed

### Future Work

- Property-based testing with Hypothesis
- Performance benchmarking
- Additional documentation in wiki knowledge base
- Configuration guide updates

### Credits

- Design Document: `/data/.task/design.md`
- Implementation: Complete core functionality
- Testing: Comprehensive test suite created
