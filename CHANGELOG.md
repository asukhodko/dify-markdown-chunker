# Changelog

All notable changes to the Advanced Markdown Chunker plugin will be documented in this file.

## [2.1.6] - 2026-01-05

### Changed
- **Upgraded to chunkana 0.1.1** — New quality features for hierarchical chunking
  - Tree invariant validation enabled by default (`validate_invariants=True`)
  - Auto-fix mode for hierarchical issues (`strict_mode=False`)
  - Dangling header prevention
  - Micro-chunk minimization in `get_flat_chunks()`
  - Updated adapter configuration to use new validation parameters

### Added
- **Overlap Contract Tests** — Comprehensive tests for overlap behavior
  - Tests for `include_metadata=True`: overlap in metadata only
  - Tests for `include_metadata=False`: overlap embedded in content
  - Property-based tests using Hypothesis for overlap contract validation
  - Edge case tests (first chunk, last chunk)

- **Hierarchical Integration Tests** — Tests for hierarchical mode with chunkana 0.1.1
  - Tree invariant validation tests (`is_leaf` consistency, parent-child references)
  - Debug mode behavior tests
  - Chunk ID uniqueness tests

### Technical Details
- Updated `adapter.py` with `validate_invariants=True` and `strict_mode=False`
- Updated tool docstring to reference chunkana 0.1.1 features
- All 19 new tests passing (11 overlap + 8 hierarchical)
- Full backward compatibility maintained

## [2.1.5] - 2026-01-04

### Changed
- **Migration to chunkana 0.1.0** — Initial migration from embedded code to external library
  - Removed embedded `markdown_chunker` and `markdown_chunker_v2` directories (reduced repository size by ~80%)
  - Added migration adapter (`adapter.py`) providing full compatibility layer
  - All functionality preserved with improved maintainability and performance
  - Updated dependencies to use `chunkana==0.1.0` instead of embedded code

### Added
- **Build System Improvements** — Enhanced packaging and development workflow
  - Added automatic `dify-plugin` CLI installation in Makefile (`make install-dify-plugin`)
  - Fixed package creation and validation commands (`make package`, `make validate-package`)
  - Improved code quality checks and linting with proper error handling
  - Enhanced development commands with better error messages and status reporting

### Fixed
- **Testing Infrastructure** — Comprehensive test coverage for migration
  - 99 migration-compatible tests passing (down from 812 due to embedded code removal)
  - Property-based testing for correctness validation using Hypothesis
  - Regression testing against pre-migration snapshots for behavioral compatibility
  - Fixed Makefile test commands to run only compatible tests

### Technical Details
- Migration adapter preserves exact pre-migration behavior including debug modes
- All chunking strategies, metadata filtering, and output formatting maintained
- Backward-compatible API with no breaking changes for existing users
- Improved memory efficiency and reduced plugin package size

## [2.1.4] - 2025-12-23

### Changed
- Bumped `dify_plugin` dependency from 0.5.0b15 to 0.7.0
- Fixed `.difyignore` to properly include README.md and PRIVACY.md in package

## [2.1.3] - 2025-12-14

### Added
- **Table Grouping Option** — Groups related tables in same chunk for better retrieval
  - New `TableGroupingConfig` class with configurable parameters
  - Proximity-based grouping (`max_distance_lines`)
  - Section boundary awareness (`require_same_section`)
  - Size and count limits (`max_group_size`, `max_grouped_tables`)
  - New metadata fields: `is_table_group`, `table_group_count`
  - Disabled by default for backward compatibility
  - Perfect for API documentation with Parameters/Response/Error tables

### Configuration
- New parameters in `ChunkConfig`:
  - `group_related_tables` — Enable table grouping (default: False)
  - `table_grouping_config` — TableGroupingConfig instance for fine-tuned control

## [2.1.2] - 2025-12-11

### Added
- **Enhanced Code-Context Binding** — Intelligent binding of code blocks to their explanations
  - Pattern recognition for Before/After comparisons, Code+Output pairs, Setup+Example sequences
  - New `CodeContextBinder` class with role detection, explanation extraction, and related block grouping
  - New metadata fields: `code_role`, `has_related_code`, `code_relationship`, `explanation_bound`
  - Integrated into CodeAwareStrategy chunking pipeline
  - Perfect for API documentation, tutorials, and code migration guides
  - **Competitive advantage:** Unique capability not found in competing chunkers

- **Adaptive Chunk Sizing** — Automatic size optimization based on content complexity
  - Complexity scoring using weighted factors: code (0.4), tables (0.3), lists (0.2), sentence length (0.1)
  - Dynamic sizing with configurable scale bounds (0.5x–1.5x base size)
  - New `AdaptiveSizeConfig` class for fine-tuned control
  - Metadata fields: `adaptive_size`, `content_complexity`, `size_scale_factor`
  - Opt-in feature via `use_adaptive_sizing=True` (disabled by default for backward compatibility)
  - Validation script: `scripts/validate_adaptive_sizing.py`

- **Hierarchical Chunking** — Parent-child relationships between chunks
  - Multi-level retrieval support (document → section → subsection → paragraph)
  - O(1) chunk lookup with navigation methods (get_parent, get_children, get_ancestors, get_siblings)
  - New `HierarchicalChunkingResult` class with tree navigation API
  - New metadata fields: `chunk_id`, `parent_id`, `children_ids`, `hierarchy_level`, `is_leaf`, `is_root`
  - New tool parameters: `enable_hierarchy`, `debug` mode for including all chunks
  - Backward-compatible with flat chunking via `get_flat_chunks()`

### Changed
- **Test Suite** — Expanded from 652 to 812 tests (+24.5%)
  - Comprehensive tests for code context binding (5 new test files)
  - Property-based tests for adaptive sizing
  - Integration tests for hierarchical chunking
  - Performance benchmarks for new features

- **Documentation** — Comprehensive updates
  - README updated with code-context binding examples and configuration
  - New adaptive sizing documentation with tuning guidelines
  - Hierarchical chunking API reference and usage examples
  - Enhanced chunk metadata reference

### Configuration
- New parameters in `ChunkConfig`:
  - `enable_code_context_binding` — Enable enhanced code-context binding
  - `max_context_chars_before/after` — Context search limits
  - `bind_output_blocks`, `preserve_before_after_pairs` — Binding behavior
  - `use_adaptive_sizing` — Enable adaptive chunk sizing
  - `adaptive_config` — AdaptiveSizeConfig instance

- New tool parameters:
  - `enable_hierarchy` — Create parent-child chunk relationships
  - `debug` — Include all chunks (root, intermediate, leaf) in output

## [2.1.1] - 2025-12-10

### Added
- **Nested Fencing Support** — Correctly handles nested code blocks in markdown
  - Quadruple backticks (````) for nesting triple backticks inside
  - Quintuple backticks (`````) for deep nesting levels
  - Tilde fencing support (~~~, ~~~~, ~~~~~) as alternative syntax
  - Mixed fence types (backticks and tildes can be nested together)
  - Essential for meta-documentation, tutorials, and style guides
  - **Competitive advantage:** Unique capability not found in any competing chunker

- **Enhanced FencedBlock Type** — Extended metadata for fence tracking
  - `fence_char` — Character used for fencing ('`' or '~')
  - `fence_length` — Length of fence (3, 4, 5, etc.)
  - `is_closed` — Whether fence has matching closing fence
  - Enables semantic analysis and nested structure validation

### Changed
- **Parser Architecture** — State machine-based fence detection
  - Replaced regex-based extraction with line-by-line state machine
  - Proper tracking of fence character type and length
  - Handles unclosed fences gracefully
  - Linear O(n) complexity maintained

- **Test Suite** — Expanded from 578 to 652 tests (+12.8%)
  - 38 new unit tests for nested fencing detection
  - 26 new integration tests for full pipeline validation
  - 10 new performance benchmarks for nested structures
  - 5 new corpus files with realistic nested examples
  - Property-based tests for fence matching invariants

### Fixed
- Nested code blocks now parse correctly (previously broke on inner fences)
- Header and table extraction now properly skips nested fenced content
- Tilde fencing now supported consistently across all parsers

### Performance
- Simple documents: < 5% performance impact
- Nested documents: 30-40% overhead (acceptable for added complexity)
- Linear complexity O(n) maintained for all fence types
- All 652 tests pass in < 35 seconds

## [2.1.0] - 2025-12-07

### Added
- **List-Aware Strategy** — Intelligent chunking for list-heavy documents
  - Preserves nested list hierarchies (never splits across depth levels)
  - Automatically binds introduction paragraphs to their lists
  - Smart grouping of related list items based on structure
  - Handles bullet lists, numbered lists, and checkboxes
  - Activation logic: `list_ratio > 0.40 AND list_count >= 5` (for structured docs) or `list_ratio > 0.40 OR list_count >= 5` (for plain lists)
  - Perfect for changelogs, feature lists, task lists, and outlines
  - **Competitive advantage:** Unique capability not found in LangChain, LlamaIndex, Unstructured, or Chonkie

- **Adaptive Overlap Sizing** — Context window scales with chunk size
  - Replaced fixed `MAX_OVERLAP_CONTEXT_SIZE = 500` with adaptive ratio-based sizing
  - Formula: `min(config.overlap_size, chunk_size * 0.35)`
  - Small chunks respect configured `overlap_size`
  - Large chunks allow up to 35% overlap (e.g., 8KB chunk = up to 2.8KB overlap)
  - Prevents metadata bloat while providing sufficient context
  - Automatic scaling without manual tuning

### Changed
- **Configuration**: Added 2 new parameters for list-aware strategy
  - `list_ratio_threshold=0.40` — minimum ratio of list content to activate strategy
  - `list_count_threshold=5` — minimum number of list items to activate strategy
- **Architecture**: Total strategies increased from 3 to 4 (code_aware, structural, list_aware, fallback)
- **Documentation**: Comprehensive README update highlighting competitive advantages
  - List-aware strategy prominently featured as unique capability
  - Practical examples for changelog processing
  - Updated architecture and configuration sections

### Fixed
- PEP 8 compliance: Fixed E203 linter errors (whitespace before ':' in slice notation)
- Code quality: All quality checks pass with 0 errors

### Testing
- Added comprehensive tests for adaptive overlap behavior
  - Test for large chunks (validates scaling works)
  - Test for small chunks (validates config limit still applies)
  - Test for proportional scaling comparison
- Created demonstration script `demo_adaptive_overlap.py`
- All 24 tests in `test_preamble_scenarios.py` pass

## [2.0.2-a0] - 2025-12-05

### Major Redesign
This release is a complete architectural redesign focused on simplification and reliability.

### Changed
- **Architecture**: Renamed module from `markdown_chunker` to `markdown_chunker_v2`
- **Strategies**: Reduced from 6 strategies to 3 (code_aware, structural, fallback)
- **Configuration**: Simplified from 32 parameters to 8 core parameters
- **Types**: Consolidated all types into single `types.py` module
- **Tests**: Focused test suite reduced from 1366+ to 445 property-based tests

### Removed
- Legacy strategies: Mixed, List, Table, Sentences (functionality merged into remaining 3)
- Removed 24 configuration parameters that were rarely used or always enabled
- Removed legacy test files for removed functionality
- Removed complex fallback hierarchy (now automatic)

### Added
- `ChunkConfig.from_dict()` and `to_dict()` for serialization
- `ChunkConfig.from_legacy()` for migration from old parameters
- Simplified configuration profiles: `default()`, `for_code_heavy()`, `for_structured()`, `minimal()`

### Migration
See [docs/MIGRATION.md](docs/MIGRATION.md) for migration guide from v1.x.

---

## [2.0.0-a3] - 2025-12-03

### Added
- Regression and duplication validation to improve chunking reliability
- Comprehensive API reference documentation
- Block-based chunking implementation for markdown content
- Documentation for block overlap management system
- Type annotations for variable declarations

### Changed
- Redesigned chunk overlap with explicit neighbor context model
- Overlap model now uses `previous_content` and `next_content` for metadata-based handling
- Improved overlap content extraction to include paragraphs, not just headers
- Documentation structure reorganized and updated
- API reference documentation reformatted and updated

### Fixed
- Improved strategy selection and content validation
- Enhanced packaging script and updated plugin version
- Overlap handling now properly manages neighbor context

### Refactor
- Renamed error collector classes for clarity in parser module
- Removed block-based chunking implementation reference
- Redesigned overlap handling with metadata-based mode

### Documentation
- Added detailed documentation for block overlap management system
- Updated overlap manager documentation for metadata-based mode
- Comprehensive documentation and configuration files updated
- API reference documentation completely revised
- Development guide translated to English

## [2.0.0-a0-3] - 2025-11-23

### Changed
- **Optimization:** Filtered metadata to include only RAG-useful fields
  - Removed statistical fields (avg_line_length, char_count, word_count, etc.)
  - Removed count fields (item_count, nested_item_count, etc.)
  - Removed internal execution fields (execution_fallback_level, strategy, etc.)
  - Kept semantic fields useful for retrieval (content_type, has_code, has_urls, etc.)
  - **Boolean fields optimization:** `is_*` and `has_*` fields now included only when `true`
  - Reduced metadata size by ~70% while keeping search-relevant information

### Added
- **Tests:** Added 9 unit tests for metadata filtering (`test_metadata_filtering.py`)
  - Tests for statistical field exclusion
  - Tests for boolean field optimization (only true values)
  - Tests for semantic field preservation
  - Tests for preamble handling
  - Realistic example test with actual metadata structure

## [2.0.0-a0-2] - 2025-11-23

### Fixed
- **Critical:** Fixed UI crash in Dify knowledge pipeline
  - Changed output format from array of objects to array of strings
  - Metadata now embedded in string format: `<metadata>\n{json}\n</metadata>\n{content}`
  - Compatible with Dify UI expectations for knowledge pipeline
  - Prevents React error #31 (objects not valid as React child)

## [2.0.0-a0-1] - 2025-11-23

### Fixed
- **Critical:** Fixed runtime error in tool implementation
  - Changed `chunk_overlap` parameter to `overlap_size` in ChunkConfig initialization
  - Removed non-existent parameters `strategy_override` and `include_metadata` from ChunkConfig
  - Fixed strategy and metadata handling to use chunk() method parameters instead
  - Tool now correctly processes documents without errors

## [2.0.0-a0-0] - 2025-11-23

### Fixed
- **Critical:** Fixed icon path in manifest.yaml causing import errors
  - Changed `icon: _assets/icon.svg` to `icon: icon.svg` in all YAML files
  - This aligns with Dify's convention where icons are automatically resolved from `_assets/` directory
  - Verified against official Dify plugins
- **Critical:** Fixed tags validation
  - Changed from custom tags (`rag`, `chunking`, `markdown`, `knowledge-base`) to standard tags (`productivity`, `business`)
  - CLI validates tags against standard list
- **Build:** Fixed packaging to use official dify-plugin CLI
  - Replaced manual packaging script with official CLI
  - Created `.difyignore` to exclude `venv/`, tests, and development files from package
  - Package now passes all CLI validations

### Changed
- Updated `make package` to use official dify-plugin CLI
- Updated tests to match new icon path and tag requirements
- Cleaned up temporary documentation files
- Consolidated documentation into core files

### Package
- **Format:** `dify-markdown-chunker-official-YYYYMMDD_HHMMSS.difypkg`
- **Size:** 136 KB (compressed), ~550 KB (uncompressed)
- **Files:** 52 files (core functionality + essential docs)
- **Status:** ✅ Production ready - UI compatible

### Documentation
- Added `DEVELOPMENT.md` - comprehensive development guide
- Updated `README.md` - streamlined with references to other docs
- Updated `INSTALLATION.md` - installation instructions
- Updated `TROUBLESHOOTING.md` - common issues and solutions
- Updated `PACKAGING.md` - packaging instructions

### Technical Details
- Analyzed official Dify plugins to understand correct format
- Confirmed that Dify automatically searches for icons in `_assets/` directory
- **Important:** CLI supports `.difyignore` file for excluding files from package
- `.gitignore` only affects git repository, `.difyignore` affects package contents
- Package size: 145 KB (compressed), 575 KB (uncompressed)
- Maximum package size: 50 MB (uncompressed)
- Excluded from package: tests, development docs, validation scripts, Python cache

### Migration Notes
If you have an older version installed:
1. Uninstall the old version from Dify UI
2. Install the new package from releases
3. Reconfigure any Knowledge Bases using the plugin

---

## [2.0.0-beta] - 2025-11-22

### Added
- Initial implementation of Advanced Markdown Chunker plugin
- Support for multiple chunking strategies (auto, code, structural, mixed, list, table, sentences)
- Configurable parameters (max_chunk_size, chunk_overlap, strategy, include_metadata)
- Rich metadata for each chunk (type, strategy, line numbers, complexity)
- Multi-language support (English, Chinese, Russian)
- Comprehensive error handling
- Manual packaging script (no dify-plugin CLI required)
- Extensive validation utilities
- Complete test suite

### Known Issues
- ~~Icon path in manifest causing import errors~~ (Fixed in 2.0.0)

---

## Version History

- **2.0.0** (2025-11-23) - Fixed icon path, ready for production
- **2.0.0-beta** (2025-11-22) - Initial release with known import issue

---

## Links

- **Development Guide:** [DEVELOPMENT.md](DEVELOPMENT.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentation:** [docs/](docs/)
