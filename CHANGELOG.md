# Changelog

All notable changes to the Advanced Markdown Chunker plugin will be documented in this file.

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
