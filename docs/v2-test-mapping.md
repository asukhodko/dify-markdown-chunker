# V2 Test Specification to Test File Mapping

This document maps each SPEC from `docs/v2-test-specification/v2-test-specification.md` to its implementation in the test files.

## Summary

- **Total Specifications**: 52
- **Total Tests**: 148
- **Coverage**: 77% of markdown_chunker_v2

## Test Files

| File | SPECs | Tests |
|------|-------|-------|
| `test_v2_parser_properties.py` | SPEC-001 to SPEC-007 | 28 |
| `test_v2_chunker_properties.py` | SPEC-008 to SPEC-015 | 30 |
| `test_v2_core_properties.py` | SPEC-023 to SPEC-026 | 12 |
| `test_v2_integration.py` | SPEC-020 to SPEC-022 | 17 |
| `test_v2_strategy_properties.py` | SPEC-016 to SPEC-019 | 16 |
| `test_v2_additional.py` | SPEC-027 to SPEC-052 | 45 |

## Detailed Mapping

### Parser Specifications (SPEC-001 to SPEC-007)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-001 | `TestSPEC001ContentAnalysisMetrics` | test_v2_parser_properties.py |
| SPEC-002 | `TestSPEC002FencedBlockExtraction` | test_v2_parser_properties.py |
| SPEC-003 | `TestSPEC003HeaderDetection` | test_v2_parser_properties.py |
| SPEC-004 | `TestSPEC004TableDetection` | test_v2_parser_properties.py |
| SPEC-005 | `TestSPEC005PreambleDetection` | test_v2_parser_properties.py |
| SPEC-006 | `TestSPEC006LineNumberAccuracy` | test_v2_parser_properties.py |
| SPEC-007 | `TestSPEC007ParserEdgeCases` | test_v2_parser_properties.py |

### Chunker Specifications (SPEC-008 to SPEC-015)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-008 | `TestSPEC008BasicChunking` | test_v2_chunker_properties.py |
| SPEC-009 | `TestSPEC009MaxChunkSize` | test_v2_chunker_properties.py |
| SPEC-010 | `TestSPEC010MinChunkSize` | test_v2_chunker_properties.py |
| SPEC-011 | `TestSPEC011OverlapMetadata` | test_v2_chunker_properties.py |
| SPEC-012 | `TestSPEC012AtomicBlockPreservation` | test_v2_chunker_properties.py |
| SPEC-013 | `TestSPEC013ChunkMetadata` | test_v2_chunker_properties.py |
| SPEC-014 | `TestSPEC014StrategySelection` | test_v2_chunker_properties.py |
| SPEC-015 | `TestSPEC015ConfigValidation` | test_v2_chunker_properties.py |

### Strategy Specifications (SPEC-016 to SPEC-019)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-016 | `TestSPEC016CodeAwareStrategy` | test_v2_strategy_properties.py |
| SPEC-017 | `TestSPEC017StructuralStrategy` | test_v2_strategy_properties.py |
| SPEC-018 | `TestSPEC018FallbackStrategy` | test_v2_strategy_properties.py |
| SPEC-019 | `TestSPEC019StrategyOverride` | test_v2_strategy_properties.py |

### Integration Specifications (SPEC-020 to SPEC-022)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-020 | `TestSPEC020EndToEndPipeline` | test_v2_integration.py |
| SPEC-021 | `TestSPEC021SerializationRoundtrip` | test_v2_integration.py |
| SPEC-022 | `TestSPEC022ErrorRecovery` | test_v2_integration.py |

### Core Property Specifications (SPEC-023 to SPEC-026)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-023 | `TestSPEC023DataPreservation` | test_v2_core_properties.py |
| SPEC-024 | `TestSPEC024MonotonicOrdering` | test_v2_core_properties.py |
| SPEC-025 | `TestSPEC025NoEmptyChunks` | test_v2_core_properties.py |
| SPEC-026 | `TestSPEC026Idempotence` | test_v2_core_properties.py |

### Additional Specifications (SPEC-027 to SPEC-052)

| SPEC | Test Class | File |
|------|------------|------|
| SPEC-027 | `TestSPEC027HeaderPathAccuracy` | test_v2_additional.py |
| SPEC-028 | `TestSPEC028OverlapSizeConstraint` | test_v2_additional.py |
| SPEC-030 | `TestSPEC030ConfigProfiles` | test_v2_additional.py |
| SPEC-033 | `TestSPEC033APIBackwardCompatibility` | test_v2_additional.py |
| SPEC-035 | `TestSPEC035ChunkIndexCorrectness` | test_v2_additional.py |
| SPEC-036 | `TestSPEC036ContentTypeDetection` | test_v2_additional.py |
| SPEC-039 | `TestSPEC039UnicodeContentHandling` | test_v2_additional.py |
| SPEC-040 | `TestSPEC040LineEndingNormalization` | test_v2_additional.py |
| SPEC-041 | `TestSPEC041MetadataSerialization` | test_v2_additional.py |
| SPEC-045 | `TestSPEC045CodeBlockLanguageDetection` | test_v2_additional.py |
| SPEC-046 | `TestSPEC046TableColumnCounting` | test_v2_additional.py |
| SPEC-048 | `TestSPEC048ChunkSizeDistribution` | test_v2_additional.py |
| SPEC-049 | `TestSPEC049ErrorMessageQuality` | test_v2_additional.py |
| SPEC-050 | `TestSPEC050ConfigDefaults` | test_v2_additional.py |

## Running Tests

```bash
# Run all v2 tests
python -m pytest tests/test_v2_*.py -v

# Run with coverage
python -m pytest tests/test_v2_*.py --cov=markdown_chunker_v2 --cov-report=term-missing

# Run specific SPEC
python -m pytest tests/test_v2_parser_properties.py::TestSPEC001ContentAnalysisMetrics -v

# Run property tests only
python -m pytest tests/test_v2_*.py -k "property" -v
```

## Coverage by Component

| Component | Coverage |
|-----------|----------|
| parser.py | 97% |
| chunker.py | 93% |
| code_aware.py | 96% |
| fallback.py | 95% |
| structural.py | 73% |
| types.py | 89% |
| config.py | 76% |
| **TOTAL** | **77%** |
