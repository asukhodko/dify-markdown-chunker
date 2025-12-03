# Target Architecture (To-Be)

**Version**: 2.0  
**Status**: Design Proposal  
**Date**: December 3, 2025

## Overview

This directory defines the simplified target architecture for the Dify Markdown Chunker redesign. The goal is to maintain all functional requirements (10 domain properties) while dramatically reducing complexity.

## Design Goals

| Goal | Target | Rationale |
|------|--------|-----------|
| **Simplicity** | 12 files vs 55 | Easier navigation and understanding |
| **Clarity** | 8 config params vs 32 | Clear decision-making |
| **Testability** | 50 tests vs 1,853 | Test behavior, not implementation |
| **Maintainability** | ~5,000 LOC vs ~24,000 | Easier to modify and extend |
| **Performance** | Within 20% | Simplicity may have minor cost |

## Design Principles

### 1. Domain-Driven Design
- Focus on 10 core domain properties (PROP-1 through PROP-10)
- Separate business logic from implementation details
- Clear ubiquitous language

### 2. YAGNI (You Aren't Gonna Need It)
- No speculative features
- Remove all unused parameters
- Remove deprecated code

### 3. Single Path
- One overlap mechanism (block-based)
- One post-processing pipeline
- One validation point

### 4. Fail Fast
- Clear error messages
- No silent fallbacks through multiple layers
- 4 error types instead of 15+

### 5. Property-Based Testing
- Tests validate properties, not implementation
- Hypothesis generates test cases
- 10 property tests replace 1,853 implementation tests

## Architecture Documents

| Document | Description |
|----------|-------------|
| [01-module-structure.md](01-module-structure.md) | 12-file organization |
| [02-data-flow.md](02-data-flow.md) | Unified 3-stage pipeline |
| [03-strategies.md](03-strategies.md) | 4 consolidated strategies |
| [04-configuration.md](04-configuration.md) | 8-parameter config |
| [05-public-api.md](05-public-api.md) | Minimal 7-export API |
| [06-testing-strategy.md](06-testing-strategy.md) | Property-based test suite |

## Comparison

| Aspect | Current | Target | Change |
|--------|---------|--------|--------|
| **Files** | 55 | 12 | -78% |
| **Lines of Code** | ~24,000 | ~5,000 | -79% |
| **Config Parameters** | 32 | 8 | -75% |
| **Strategies** | 6 | 4 | -33% |
| **Test Files** | 162 | ~30 | -81% |
| **Total Tests** | 1,853 | ~50 | -97% |
| **Test LOC** | ~45,600 | ~2,000 | -96% |
| **Public API Exports** | 50+ | 7 | -86% |

## Key Changes

### Module Consolidation
- **Parser**: 15 files → 1 file (parser.py)
- **Chunker**: 26 files → 1 file (chunker.py) + 4 strategy files
- **API**: 5 files → removed (functionality in chunker.py)
- **Types**: 2 files (chunker/types.py, parser/types.py) → 1 file (types.py)

### Strategy Consolidation
- **CodeAwareStrategy**: Merges Code + Mixed
- **StructuralStrategy**: Simplified, Phase 2 removed
- **TableStrategy**: Kept as-is (simple, focused)
- **FallbackStrategy**: Renamed from Sentences
- **ListStrategy**: Removed (was excluded from auto-selection)

### Configuration Simplification

**8 Parameters** (down from 32):
```python
# Size constraints (3)
max_chunk_size: int = 4096
min_chunk_size: int = 512
overlap_size: int = 200  # 0 = disabled

# Behavior (3)
preserve_atomic_blocks: bool = True
extract_preamble: bool = True
allow_oversize: bool = True

# Strategy thresholds (2)
code_threshold: float = 0.3
structure_threshold: int = 3
```

### Removed Parameters Justification
- target_chunk_size: Derived as (min + max) / 2
- overlap_percentage: Use overlap_size only
- enable_overlap: overlap_size = 0 means disabled
- All MC-* flags: Make fixes default behavior
- Phase 2 flags: Simplified design doesn't need them
- enable_streaming: Not implemented
- fallback_strategy: Hardcoded to FallbackStrategy

### Public API
```python
__all__ = [
    "MarkdownChunker",      # Main class
    "ChunkConfig",          # Configuration
    "Chunk",                # Data type
    "ChunkingResult",       # Result type
    "ContentAnalysis",      # Analysis type
    "chunk_text",           # Convenience
    "chunk_file",           # Convenience
]
```

## Architecture Diagram

```
markdown_chunker/
├── __init__.py              # 7 public exports
├── types.py                 # All data structures
├── config.py                # 8-parameter config
├── chunker.py               # Main MarkdownChunker class
├── parser.py                # Stage1 analysis
├── strategies/
│   ├── __init__.py
│   ├── base.py              # BaseStrategy
│   ├── code_aware.py        # Code + Mixed
│   ├── structural.py        # Header-based
│   ├── table.py             # Table preservation
│   └── fallback.py          # Sentence-based
└── utils.py                 # Utilities
```

## Data Flow

```
Input (Markdown Text)
    ↓
Stage 1: Parser.analyze()
    ├── Build AST
    ├── Extract code blocks
    ├── Extract elements
    └── Calculate metrics
    ↓
    ContentAnalysis
    ↓
Stage 2: Chunker.chunk()
    ├── Select Strategy
    ├── Apply Strategy
    └── Fallback if needed
    ↓
    List[Chunk]
    ↓
Stage 3: Post-Processing
    ├── Apply block overlap
    ├── Enrich metadata
    └── Validate properties
    ↓
Output (ChunkingResult)
```

## Success Criteria

### Code Metrics
- ✓ Files ≤ 15 (target: 12)
- ✓ Lines of code ≤ 6,000 (target: ~5,000)
- ✓ Config parameters ≤ 10 (target: 8)
- ✓ No files > 800 lines
- ✓ No circular dependencies

### Quality Metrics
- ✓ All 10 domain properties pass
- ✓ Code coverage ≥ 85%
- ✓ Public API ≤ 10 exports (target: 7)

### Functional Metrics
- ✓ Output equivalence ≥ 95% on real documents
- ✓ Performance within 20% of current
- ✓ All Dify integration tests pass

## Dependencies

**Required** (3 dependencies):
- markdown-it-py >= 3.0.0  # Primary parser
- pydantic >= 2.0.0        # Data validation
- dify_plugin == 0.5.0b15  # Dify integration

**Development** (2 dependencies):
- pytest >= 7.0.0
- hypothesis >= 6.0.0      # Property-based testing

**Removed** (2 dependencies):
- mistune  # Redundant parser
- markdown # Redundant parser

## Migration Strategy

This redesign will be released as **version 2.0.0** (major version bump due to breaking changes).

### Public API Compatibility
- MarkdownChunker class interface preserved
- ChunkConfig simplified but maintains core parameters
- Chunk and ChunkingResult structures preserved

### Breaking Changes
- 24 configuration parameters removed
- 2 strategies removed (List, Mixed merged into Code)
- Parser module no longer exports 50+ symbols
- Deprecated Simple API removed

### Migration Support
- Migration guide (1.x → 2.0)
- Configuration migration utility
- Deprecation warnings in 2.0 (removed in 3.0)
- Old codebase archived for 1 month

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Feature Loss | Property tests ensure all requirements met |
| Performance Regression | Benchmark suite, 20% variance acceptable |
| Edge Cases | Keep old implementation for comparison |
| User Migration | Migration guide, backward compat period |

## Next Steps

1. Review and approve this target architecture
2. Review implementation plan (architecture-audit-v2-redesign-plan)
3. Execute 3-week implementation
4. Validate with property tests and real documents
5. Release as version 2.0.0
