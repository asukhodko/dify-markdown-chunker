# Domain Properties

This document formalizes the core domain properties that any markdown chunking implementation must satisfy.

## Overview

Through analysis of existing tests and requirements, we've identified 10 fundamental properties that define correct behavior for markdown chunking. These properties are implementation-independent and form the contract that the system must uphold.

**Critical Finding**: All 10 properties are currently satisfied by the existing codebase. The issue is not missing functionality but excessive implementation complexity.

---

## Critical Properties (MUST HAVE)

These properties are non-negotiable and must be satisfied by any implementation.

### PROP-1: No Content Loss

**Formal Definition**:
```
∀ doc ∈ ValidMarkdown:
  concat(chunks) - overlaps ≡ doc
```

**Plain Language**: For any valid markdown document, the concatenation of all chunk contents (after removing overlap regions) must be equivalent to the original document.

**Current Coverage**: ✓ Tested in 5+ files
- test_data_preservation_properties.py
- test_critical_properties.py
- test_comprehensive_integration.py
- test_integration.py
- test_stage1_integration.py

**Testing Approach**: Property-based testing with Hypothesis generating random markdown

### PROP-2: Size Bounds

**Formal Definition**:
```
∀ chunk ∈ Chunks:
  len(chunk.content) ≤ config.max_chunk_size 
  ∨ chunk.metadata["allow_oversize"] = True
```

**Plain Language**: Every chunk must either fit within the maximum size limit OR be explicitly marked as oversize (for indivisible elements like large code blocks or tables).

**Current Coverage**: ✓ Tested in 4+ files
- test_critical_properties.py
- test_chunk_simple.py
- test_performance_benchmarks.py
- test_integration.py

**Testing Approach**: Verify all chunks respect size constraints or are properly flagged

### PROP-3: Monotonic Ordering

**Formal Definition**:
```
∀ i < j:
  chunks[i].start_line ≤ chunks[j].start_line
```

**Plain Language**: Chunks must appear in the same order as they appear in the original document (monotonic increasing start_line values).

**Current Coverage**: ✓ Tested in 1 dedicated file
- test_monotonic_ordering_property.py

**Testing Approach**: Verify start_line values are non-decreasing across chunk sequence

### PROP-4: No Empty Chunks

**Formal Definition**:
```
∀ chunk ∈ Chunks:
  chunk.content.strip() ≠ ""
```

**Plain Language**: No chunk may contain only whitespace or be empty.

**Current Coverage**: ✓ Tested in 1 dedicated file + constructor validation
- test_no_empty_chunks_property.py
- Chunk.__post_init__() validation

**Testing Approach**: Check all chunks have non-whitespace content

### PROP-5: Valid Line Numbers

**Formal Definition**:
```
∀ chunk ∈ Chunks:
  chunk.start_line ≥ 1 ∧ chunk.end_line ≥ chunk.start_line
```

**Plain Language**: Line numbers must be 1-based (start_line ≥ 1) and form valid ranges (end_line ≥ start_line).

**Current Coverage**: ✓ Constructor validation
- Chunk.__post_init__() raises ValueError for invalid ranges

**Testing Approach**: Constructor validation ensures this automatically

---

## Important Properties (SHOULD HAVE)

These properties are important for quality but not absolutely critical.

### PROP-6: Code Block Integrity

**Formal Definition**:
```
∀ code_block ∈ doc.code_blocks:
  ∃! chunk ∈ Chunks: code_block ⊆ chunk.content
```

**Plain Language**: Every code block in the source document must appear complete in exactly one chunk (code blocks are never split across chunk boundaries).

**Current Coverage**: ✓ Tested in 3+ files
- test_code_strategy_properties.py
- test_critical_properties.py
- test_integration.py

**Testing Approach**: Extract code blocks from source, verify each appears intact in exactly one chunk

**Rationale**: Splitting code blocks destroys semantic meaning and breaks syntax

### PROP-7: Table Integrity

**Formal Definition**:
```
∀ table ∈ doc.tables:
  ∃! chunk ∈ Chunks: table ⊆ chunk.content
```

**Plain Language**: Every table in the source document must appear complete in exactly one chunk (tables are never split across chunk boundaries).

**Current Coverage**: ✓ Tested in 1 file
- test_table_strategy_properties.py

**Testing Approach**: Extract tables from source, verify each appears intact in exactly one chunk

**Rationale**: Splitting tables loses table header context and structure

### PROP-8: Serialization Round-Trip

**Formal Definition**:
```
∀ result ∈ ChunkingResult:
  ChunkingResult.from_dict(result.to_dict()) ≡ result
```

**Plain Language**: Serializing a chunking result to dictionary format and deserializing it back must produce an equivalent result.

**Current Coverage**: ✓ Tested in 1 dedicated file
- test_serialization_roundtrip_property.py

**Testing Approach**: Round-trip serialization, verify equality

**Rationale**: Required for storing/transmitting chunking results

---

## Desirable Properties (NICE TO HAVE)

These properties improve user experience but are not strictly required.

### PROP-9: Idempotence

**Formal Definition**:
```
∀ doc, config:
  chunk(doc, config) ≡ chunk(doc, config)
```

**Plain Language**: Chunking the same document with the same configuration must always produce the same result (deterministic behavior).

**Current Coverage**: ✓ Tested in 1 dedicated file
- test_idempotence_property.py

**Testing Approach**: Chunk same document twice, verify identical results

**Rationale**: Predictability for users, easier debugging

### PROP-10: Header Path Correctness

**Formal Definition**:
```
∀ chunk with header_path:
  header_path reflects actual document hierarchy
```

**Plain Language**: For any chunk with a header_path metadata field, the path must accurately represent the hierarchy of headers in the source document.

**Current Coverage**: ✓ Tested in 1 dedicated file
- test_header_path_property.py

**Testing Approach**: Build expected hierarchy from document, verify metadata matches

**Rationale**: Enables hierarchical navigation and context understanding

---

## Property Coverage Matrix

| Property | Property Test | Unit Test | Integration Test | Current Status |
|----------|---------------|-----------|------------------|----------------|
| PROP-1: No Content Loss | ✓ | ✓ | ✓ | ✓ PASSING |
| PROP-2: Size Bounds | ✓ | ✓ | ✓ | ✓ PASSING |
| PROP-3: Monotonic Order | ✓ | - | ✓ | ✓ PASSING |
| PROP-4: No Empty Chunks | ✓ | ✓ | - | ✓ PASSING |
| PROP-5: Valid Line Numbers | - | ✓ | - | ✓ PASSING |
| PROP-6: Code Block Integrity | ✓ | ✓ | ✓ | ✓ PASSING |
| PROP-7: Table Integrity | ✓ | ✓ | - | ✓ PASSING |
| PROP-8: Serialization Round-Trip | ✓ | - | - | ✓ PASSING |
| PROP-9: Idempotence | ✓ | - | - | ✓ PASSING |
| PROP-10: Header Path Correctness | ✓ | ✓ | - | ✓ PASSING |

**Key Finding**: Excessive test redundancy - most properties tested in multiple places

---

## Minimal Property Test Suite

For the redesigned system, we recommend this minimal test suite:

### test_core_properties.py (5 tests)
```python
@given(st.text(min_size=10, max_size=10000))
def test_property_no_content_loss(markdown_text):
    """PROP-1: No Content Loss"""
    # Implementation with reconstruction validation

@given(st.text(min_size=10, max_size=10000))
def test_property_size_bounds(markdown_text):
    """PROP-2: Size Bounds"""
    # Verify all chunks within max or properly flagged

@given(st.text(min_size=10, max_size=10000))
def test_property_monotonic_ordering(markdown_text):
    """PROP-3: Monotonic Ordering"""
    # Verify start_line values non-decreasing

@given(st.text(min_size=10, max_size=10000))
def test_property_no_empty_chunks(markdown_text):
    """PROP-4: No Empty Chunks"""
    # Verify all chunks have content

@given(st.text(min_size=10, max_size=10000))
def test_property_valid_line_numbers(markdown_text):
    """PROP-5: Valid Line Numbers"""
    # Verify start_line >= 1, end_line >= start_line
```

### test_integrity_properties.py (2 tests)
```python
@given(markdown_with_code_blocks())
def test_property_code_block_integrity(markdown_text):
    """PROP-6: Code Block Integrity"""
    # Extract code blocks, verify each intact in one chunk

@given(markdown_with_tables())
def test_property_table_integrity(markdown_text):
    """PROP-7: Table Integrity"""
    # Extract tables, verify each intact in one chunk
```

### test_serialization_properties.py (2 tests)
```python
@given(st.text(min_size=10, max_size=10000))
def test_property_serialization_roundtrip(markdown_text):
    """PROP-8: Serialization Round-Trip"""
    # Verify to_dict() → from_dict() preserves data

@given(st.text(min_size=10, max_size=10000))
def test_property_idempotence(markdown_text):
    """PROP-9: Idempotence"""
    # Chunk twice, verify identical results
```

### test_metadata_properties.py (1 test)
```python
@given(markdown_with_headers())
def test_property_header_path_correctness(markdown_text):
    """PROP-10: Header Path Correctness"""
    # Build expected hierarchy, verify metadata
```

**Total**: 10 property tests with 100+ examples each = ~1,000 test scenarios

---

## Property Violations in Current System

Despite all properties passing, we found these issues:

### Over-Testing
- PROP-1 tested in 5+ files (redundant)
- PROP-2 tested in 4+ files (redundant)
- PROP-6 tested in 3+ files (redundant)

### Under-Documented
- PROP-5 relies solely on constructor validation (no explicit property test)
- Property violations caught at different points (constructor vs validation)

### Implementation Leak
- Many tests validate HOW properties are satisfied rather than THAT they are satisfied
- Example: Testing overlap calculation logic instead of testing content preservation

---

## Properties for New Design

The redesigned system must:

1. **Pass all 10 properties** with the minimal test suite
2. **No redundant testing** - each property tested once
3. **Implementation-independent tests** - tests validate WHAT, not HOW
4. **Clear violation messages** - when property fails, message explains which property and why

---

## Conclusion

The existing system satisfies all 10 essential domain properties. The problem is not missing functionality but:

1. **Excessive testing redundancy** (1,853 tests for 10 properties)
2. **Implementation-coupled tests** (tests break on refactoring)
3. **Unclear property boundaries** (validation scattered across codebase)

The redesigned system will maintain these 10 properties while dramatically simplifying the implementation and test suite.
