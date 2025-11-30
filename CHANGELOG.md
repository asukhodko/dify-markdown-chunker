# Changelog

All notable changes to the Advanced Markdown Chunker plugin will be documented in this file.

## [2.0.3] - 2025-11-23

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

## [2.0.2] - 2025-11-23

### Fixed
- **Critical:** Fixed UI crash in Dify knowledge pipeline
  - Changed output format from array of objects to array of strings
  - Metadata now embedded in string format: `<metadata>\n{json}\n</metadata>\n{content}`
  - Compatible with Dify UI expectations for knowledge pipeline
  - Prevents React error #31 (objects not valid as React child)

## [2.0.1] - 2025-11-23

### Fixed
- **Critical:** Fixed runtime error in tool implementation
  - Changed `chunk_overlap` parameter to `overlap_size` in ChunkConfig initialization
  - Removed non-existent parameters `strategy_override` and `include_metadata` from ChunkConfig
  - Fixed strategy and metadata handling to use chunk() method parameters instead
  - Tool now correctly processes documents without errors

## [2.0.0] - 2025-11-23

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
