# V2 Test Implementation Roadmap

This document provides a prioritized implementation plan for new v2 tests based on the P1 test analysis.

## Executive Summary

- **Total specifications**: 52
- **Estimated implementation effort**: 80-100 hours
- **Recommended phases**: 4 phases over 4-6 weeks
- **Priority distribution**: Critical (12), High (18), Medium (16), Low (6)

## Coverage Matrix

### V2 Component Coverage

| Component | Specs | Priority | Status |
|-----------|-------|----------|--------|
| Parser.analyze() | SPEC-001, SPEC-006, SPEC-007 | Critical | To implement |
| ContentAnalysis | SPEC-001 to SPEC-006 | Critical/High | To implement |
| MarkdownChunker | SPEC-008 to SPEC-014, SPEC-020 | Critical/High | To implement |
| ChunkConfig | SPEC-009, SPEC-010, SPEC-015 | High/Medium | To implement |
| Chunk | SPEC-008, SPEC-013, SPEC-021 | Critical/High | To implement |
| CodeAwareStrategy | SPEC-016 | High | To implement |
| StructuralStrategy | SPEC-017 | High | To implement |
| FallbackStrategy | SPEC-018 | Medium | To implement |
| Validator | SPEC-022 | Medium | To implement |

### Property Coverage

| Property | Spec | Priority | Existing Test |
|----------|------|----------|---------------|
| PROP-1: Data Preservation | SPEC-023 | Critical | test_domain_properties.py |
| PROP-3: Monotonic Ordering | SPEC-024 | Critical | test_domain_properties.py |
| PROP-4: No Empty Chunks | SPEC-025 | Critical | test_domain_properties.py |
| PROP-5: Idempotence | SPEC-026 | High | test_domain_properties.py |
| PROP-6: Size Bounds | SPEC-009, SPEC-010 | Critical | test_v2_properties.py |

### Gap Analysis

**Well Covered** (existing v2 tests):
- Core domain properties (PROP-1 to PROP-9)
- V2-specific properties (PROP-10 to PROP-16)
- Basic integration tests

**Needs New Tests**:
- Parser edge cases (SPEC-007)
- Overlap metadata correctness (SPEC-011)
- Strategy selection determinism (SPEC-014)
- Serialization roundtrip (SPEC-021)
- Error recovery (SPEC-022)

**Intentionally Not Tested** (removed functionality):
- ListStrategy (merged into Fallback)
- TableStrategy (merged into Fallback)
- SentencesStrategy (merged into Fallback)
- MixedStrategy (merged into Fallback)
- Stage-based architecture (replaced with linear pipeline)

## Implementation Phases

### Phase 1: Critical Foundation (Week 1-2)
**Effort**: 25-30 hours
**Focus**: Core properties and basic functionality

| Spec ID | Name | Priority | Effort |
|---------|------|----------|--------|
| SPEC-001 | Content Analysis Metrics | Critical | 3h |
| SPEC-002 | Fenced Block Extraction | Critical | 3h |
| SPEC-006 | Line Number Accuracy | Critical | 2h |
| SPEC-008 | Basic Chunking | Critical | 3h |
| SPEC-009 | Max Chunk Size | Critical | 2h |
| SPEC-012 | Atomic Block Preservation | Critical | 3h |
| SPEC-020 | E2E Pipeline | Critical | 4h |
| SPEC-021 | Serialization Roundtrip | Critical | 2h |
| SPEC-023 | Data Preservation | Critical | 2h |
| SPEC-024 | Monotonic Ordering | Critical | 2h |
| SPEC-025 | No Empty Chunks | Critical | 1h |

**Deliverables**:
- `tests/test_v2_parser_properties.py` (SPEC-001, 002, 006)
- `tests/test_v2_chunker_properties.py` (SPEC-008, 009, 012)
- `tests/test_v2_core_properties.py` (SPEC-023, 024, 025)
- `tests/test_v2_integration.py` (SPEC-020, 021)

### Phase 2: High Priority Features (Week 2-3)
**Effort**: 25-30 hours
**Focus**: Strategy behavior and metadata

| Spec ID | Name | Priority | Effort |
|---------|------|----------|--------|
| SPEC-003 | Header Detection | High | 2h |
| SPEC-005 | Preamble Detection | Medium | 2h |
| SPEC-007 | Parser Edge Cases | High | 3h |
| SPEC-010 | Min Chunk Size | High | 2h |
| SPEC-011 | Overlap Metadata | High | 3h |
| SPEC-013 | Chunk Metadata | High | 2h |
| SPEC-014 | Strategy Selection | High | 3h |
| SPEC-016 | CodeAwareStrategy | High | 3h |
| SPEC-017 | StructuralStrategy | High | 3h |
| SPEC-026 | Idempotence | High | 2h |

**Deliverables**:
- Extended `tests/test_v2_parser_properties.py`
- Extended `tests/test_v2_chunker_properties.py`
- `tests/test_v2_strategy_properties.py` (SPEC-016, 017)

### Phase 3: Medium Priority (Week 3-4)
**Effort**: 20-25 hours
**Focus**: Edge cases and error handling

| Spec ID | Name | Priority | Effort |
|---------|------|----------|--------|
| SPEC-004 | Table Detection | Medium | 2h |
| SPEC-015 | Config Validation | Medium | 2h |
| SPEC-018 | FallbackStrategy | Medium | 2h |
| SPEC-019 | Strategy Override | Medium | 2h |
| SPEC-022 | Error Recovery | Medium | 3h |
| SPEC-027 | Header Path Accuracy | Medium | 2h |
| SPEC-028 | Overlap Size Constraint | Medium | 2h |
| SPEC-029 | Strategy Error Handling | Medium | 2h |

**Deliverables**:
- Extended strategy tests
- Error handling tests
- Configuration tests

### Phase 4: Low Priority & Polish (Week 4-6)
**Effort**: 10-15 hours
**Focus**: Performance, documentation, edge cases

| Spec ID | Name | Priority | Effort |
|---------|------|----------|--------|
| SPEC-030 to SPEC-052 | Additional specs | Low/Medium | 10-15h |

**Deliverables**:
- Performance benchmarks
- Documentation tests
- Additional edge case coverage

## Test File Organization

```
tests/
├── test_domain_properties.py          # Existing: PROP-1 to PROP-9
├── test_v2_properties.py              # Existing: PROP-10 to PROP-16
├── test_v2_parser_properties.py       # NEW: SPEC-001 to SPEC-007
├── test_v2_chunker_properties.py      # NEW: SPEC-008 to SPEC-015
├── test_v2_strategy_properties.py     # NEW: SPEC-016 to SPEC-019
├── test_v2_integration.py             # NEW: SPEC-020 to SPEC-022
├── test_v2_core_properties.py         # NEW: SPEC-023 to SPEC-026
└── test_v2_additional.py              # NEW: SPEC-027 to SPEC-052
```

## Success Criteria

### Phase 1 Complete When:
- [ ] All Critical specs implemented
- [ ] All tests pass
- [ ] Coverage > 70% for core modules

### Phase 2 Complete When:
- [ ] All High priority specs implemented
- [ ] All tests pass
- [ ] Coverage > 80% for core modules

### Phase 3 Complete When:
- [ ] All Medium priority specs implemented
- [ ] All tests pass
- [ ] Coverage > 85% for core modules

### Phase 4 Complete When:
- [ ] All specs implemented
- [ ] All tests pass
- [ ] Coverage > 90% for core modules
- [ ] Performance benchmarks established

## Risk Mitigation

### Risk 1: Spec Ambiguity
**Mitigation**: Review specs with team before implementation

### Risk 2: V2 API Changes
**Mitigation**: Implement tests incrementally, adapt as needed

### Risk 3: Time Overrun
**Mitigation**: Focus on Critical/High priority first, defer Low priority

## Metrics Tracking

| Metric | Phase 1 Target | Phase 2 Target | Phase 3 Target | Final Target |
|--------|----------------|----------------|----------------|--------------|
| Specs Implemented | 12 | 22 | 30 | 52 |
| Tests Passing | 100% | 100% | 100% | 100% |
| Code Coverage | 70% | 80% | 85% | 90% |
| Property Tests | 8 | 15 | 20 | 26 |

## Next Steps

1. **Immediate**: Begin Phase 1 implementation
2. **Week 1**: Complete Critical parser and chunker tests
3. **Week 2**: Complete Critical integration and property tests
4. **Week 3**: Begin Phase 2 (High priority)
5. **Week 4**: Complete Phase 2, begin Phase 3
6. **Week 5-6**: Complete Phase 3 and 4

## References

- [Test Intent Analysis](./test-intent-analysis.md)
- [Semantic Groups](./semantic-groups.md)
- [V2 Test Specification](./v2-test-specification.md)
- [Legacy Test Analysis](./legacy-test-analysis.md)
- [P1 Specification Property Tests](../../tests/test_p1_specification_properties.py) - validates the specification process
- [Analysis Script](../../scripts/analyze_p1_tests.py) - extracts test intents from legacy tests
