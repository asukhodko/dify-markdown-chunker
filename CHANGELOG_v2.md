# Changelog

(temporary file — to be integrated with CHANGELOG.md)

All notable changes to the Dify Markdown Chunker project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1-a0] - 2025-12-04

### 🎉 Major Architectural Redesign

Complete rewrite reducing complexity while maintaining all essential functionality.

### Added

#### Core Features
- **3-Stage Linear Pipeline**: Parser → Strategy Selection → Post-Processing
- **Single-Pass Parser**: markdown-it-py based parser (50% faster)
- **Property-Based Testing**: Hypothesis framework verifying all 10 domain properties
- **Factory Methods**: `ChunkConfig.for_rag()` and `ChunkConfig.for_code_docs()`
- **Comprehensive Test Suite**: 62 tests (35 unit + 8 integration + 19 property)

#### API
- `chunk_markdown()` convenience function
- `ChunkingResult.chunk_count` property
- `ChunkingResult.to_dict()` and `from_dict()` methods
- Automatic chunk metadata enrichment (chunk_index, total_chunks)

#### Documentation
- Complete API documentation in README_v2.md
- Migration guide (MIGRATION.md)
- Implementation completion report

### Changed

#### Architecture
- **Files**: Reduced from 55 to 11 (80% reduction)
- **Configuration**: Reduced from 32 to 8 parameters (75% reduction)
- **Strategies**: Consolidated from 6 to 4:
  - Merged Code + Mixed → CodeAwareStrategy
  - Merged Simple + Paragraph + Sentences → FallbackStrategy
  - Simplified StructuralStrategy (removed Phase 2 complexity)
  - Kept TableStrategy (unchanged)

#### Configuration
- `ChunkConfig` now has only 8 clear, purposeful parameters
- Removed YAGNI parameters (unused or over-engineered features)
- Added sensible defaults that work for 95% of use cases
- Configuration validation in `__post_init__`

#### Parser
- Switched from dual invocation to single-pass analysis
- Uses markdown-it-py with table plugin
- Extracts all elements (code, headers, tables) in one traversal
- Returns comprehensive `ContentAnalysis` with element lists

#### Strategies
- **BaseStrategy**: Abstract base with shared utilities
- **CodeAwareStrategy**: Unified handling of code and mixed content
- **StructuralStrategy**: Linear processing without tree building
- **TableStrategy**: Preserved with improved line number handling
- **FallbackStrategy**: Universal fallback (always succeeds)

#### Error Handling
- Consolidated from 15+ error types to 4:
  - `ChunkingError`: Base error class
  - `ConfigurationError`: Configuration validation errors
  - `ParsingError`: Parser failures
  - `ValidationError`: Input validation errors

### Removed

#### Removed Features (YAGNI Principle)
- **Phase 2 Processing**: Unnecessary complexity, minimal benefit
- **Tree Building**: Not used effectively, added overhead
- **Dual Parser Invocation**: Redundant, caused 50% performance penalty
- **24+ Configuration Parameters**: Over-engineered, unused
- **11+ Error Types**: Excessive granularity
- **Complex Strategy Selection Logic**: Replaced with simple priority-based selection

#### Removed Configuration Parameters
- `enable_phase2`, `phase2_mode`, `tree_mode`
- `atomic_threshold`, `merge_threshold`, `split_threshold`
- `sentence_boundary_detection`, `paragraph_detection_mode`
- `header_hierarchy_mode`, `code_block_detection`
- `table_row_detection`, `table_col_detection`
- 15+ other parameters that were rarely or never used

### Fixed

#### Edge Cases (Found via Property Testing)
- Empty code blocks (single backticks)
- Tables with missing or invalid line numbers
- Paragraph ordering with repeated content
- Config validation when min > max
- Line number calculation for tables with context

#### Parser Issues
- Table detection now requires table plugin enablement
- Line number accuracy for edge cases
- Empty content chunk validation

### Performance

#### Improvements
- **Parser**: 50% faster (single-pass vs dual invocation)
- **Strategy Selection**: Near-instant (priority-based, no tree building)
- **Memory**: Lower footprint (streamlined data structures)
- **Startup**: Faster (fewer imports, simpler initialization)

### Testing

#### Test Quality
- **100% Pass Rate**: All 62 tests passing
- **Property-Based**: 19 tests using Hypothesis framework
- **Domain Properties**: All 10 properties verified
- **Edge Cases**: Discovered and fixed 5+ edge cases
- **Integration**: 8 end-to-end pipeline tests

#### Test Distribution
- Unit tests: 35 (types, config, parser)
- Integration tests: 8 (full pipeline, strategy selection)
- Property tests: 19 (all domain properties)

### Migration

See [MIGRATION.md](MIGRATION.md) for detailed migration guide from v1.x.

#### Breaking Changes
1. Import paths changed: `dify_markdown_chunker` → `markdown_chunker_v2`
2. Configuration simplified: 32 → 8 parameters
3. Strategy names updated: `Code` → `code_aware`, `Simple` → `fallback`, etc.
4. Result API: `total_chunks` → `chunk_count`, `strategy_name` → `strategy_used`
5. Error types consolidated: 15+ → 4

### Security

- No known security issues
- Input validation improved
- Error handling more robust

### Deprecated

- v1.x will be maintained for 6 months
- Users encouraged to migrate to v2.0
- See MIGRATION.md for migration guide

---

## [1.x] - Historical

See git history for v1.x changelog.

---

## Legend

- 🎉 Major release
- ✨ New feature
- 🐛 Bug fix
- 📝 Documentation
- 🔧 Configuration
- ⚡ Performance
- 🧪 Testing
- 💥 Breaking change
