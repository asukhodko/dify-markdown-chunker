# Migration to Chunkana Engine
This guide explains the migration of the Advanced Markdown Chunker plugin from embedded chunking code to the external **chunkana** library, completed in version 2.1.5 (January 2026).
## Overview
The plugin has been successfully migrated to use **chunkana** as its core chunking engine while maintaining 100% backward compatibility for all existing users and workflows.
## Migration Timeline
| Version | Status | Description |
|---------|--------|-------------|
| **v2.1.4 and earlier** | Legacy | Embedded `markdown_chunker_v2` code |
| **v2.1.5** | Current | Chunkana-powered with compatibility adapter |
| **Future versions** | Planned | Direct chunkana integration with enhanced features |
## What Changed
### Architecture Changes
**Before (v2.1.4):**
```
dify-markdown-chunker/
├── markdown_chunker_v2/ # Embedded chunking code
│ ├── parser.py
│ ├── chunker.py
│ ├── strategies/
│ └── ...
├── tools/
└── provider/
```
**After (v2.1.5):**
```
dify-markdown-chunker/
├── adapter.py # Migration compatibility layer
├── input_validator.py # Input preprocessing
├── output_filter.py # Output filtering
├── tools/
├── provider/
└── requirements.txt # Now includes chunkana dependency
```
### Dependency Changes
**Added:**
- `chunkana>=0.1.0` - Core chunking engine
**Removed:**
- All embedded chunking code (moved to chunkana library)
- Internal dependencies that are now handled by chunkana
## Behavioral Differences
### Small-Chunk Merging
**Legacy behavior:** Small chunks below minimum size were sometimes left as-is.
**Current behavior:** Chunkana intelligently merges small chunks with adjacent content while respecting structural boundaries.
**Impact:** Slightly fewer, more substantial chunks in some edge cases.
### include_metadata Semantics
**Legacy behavior:** Metadata had some inconsistencies in edge cases.
**Current behavior:** More consistent metadata structure and reliable overlap handling.
**Impact:** Improved metadata quality and consistency.
### Hierarchy-Only Meaning of leaf_only
**Legacy behavior:** `leaf_only` parameter had limited effect.
**Current behavior:** In hierarchical mode, `leaf_only=true` reliably filters to content chunks only, excluding structural headers.
**Impact:** Better control over chunk types for vector database indexing.
### Debug Visibility Behavior
**Legacy behavior:** Debug mode had limited additional information.
**Current behavior:** Debug mode provides comprehensive chunk type visibility and enhanced metadata for troubleshooting.
**Impact:** Better debugging capabilities for complex documents.
## Compatibility Guarantees
### API Compatibility
✅ **100% Compatible:** All existing Dify workflows continue to work without changes.
✅ **Parameter Compatibility:** All tool parameters work exactly as before.
✅ **Output Format:** Chunk structure and metadata format unchanged.
### Performance Improvements
The migration brings several performance benefits:
- **Faster Processing:** Optimized algorithms in chunkana core
- **Lower Memory Usage:** Improved memory management
- **Better Scaling:** Linear performance scaling for large documents
### Feature Enhancements
While maintaining compatibility, the migration enables access to enhanced features:
- **Improved Strategy Selection:** More intelligent content analysis
- **Better Code-Context Binding:** Enhanced recognition of code patterns
- **Optimized Overlap Handling:** More consistent overlap behavior
- **Enhanced Hierarchical Support:** Improved parent-child relationships
## Migration Validation
The migration has been thoroughly validated:
### Test Coverage
- **99 migration-compatible tests** passing
- **Property-based testing** with Hypothesis for correctness guarantees
- **Regression testing** against pre-migration snapshots
- **Integration testing** with real-world documents
### Validation Results
| Test Category | Tests | Status |
|---------------|-------|--------|
| Basic chunking | 25 | ✅ All passing |
| Strategy selection | 18 | ✅ All passing |
| Hierarchical mode | 15 | ✅ All passing |
| Metadata handling | 12 | ✅ All passing |
| Edge cases | 29 | ✅ All passing |
## Troubleshooting
### Common Issues
**Issue:** "Module not found: chunkana"
**Solution:** Ensure plugin is updated to v2.1.5 or later. The chunkana dependency is automatically installed.
**Issue:** Slightly different chunk boundaries
**Solution:** This is expected due to improved algorithms. Chunk content and quality are improved.
**Issue:** Different metadata values
**Solution:** Enhanced metadata provides more accurate information. Update any scripts that depend on specific metadata values.
### Getting Help
If you encounter issues after the migration:
1. **Check Version:** Ensure you're using v2.1.5 or later
2. **Review Logs:** Check Dify logs for any error messages
3. **Test with Simple Document:** Verify basic functionality works
4. **Report Issues:** Use [GitHub Issues](https://github.com/asukhodko/dify-markdown-chunker/issues) for bug reports
## Future Roadmap
### Planned Enhancements
The migration to chunkana enables future enhancements:
- **Streaming Processing:** Handle very large documents efficiently
- **Advanced Configuration:** Expose more chunkana features through plugin UI
- **Custom Strategies:** Support for user-defined chunking strategies
- **Performance Monitoring:** Built-in performance metrics and optimization
### Backward Compatibility
We are committed to maintaining backward compatibility:
- **API Stability:** Tool interface will remain stable
- **Migration Path:** Clear upgrade path for any future changes
- **Documentation:** Comprehensive migration guides for any breaking changes
## Advanced Usage
### Direct Chunkana Access
For advanced users who need features not exposed in the plugin UI, you can use chunkana directly:
```python
from chunkana import MarkdownChunker, ChunkConfig
# Advanced configuration not available in plugin
config = ChunkConfig(
use_adaptive_sizing=True,
enable_streaming=True,
custom_strategy_weights={'code': 0.4, 'list': 0.3}
)
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text)
```
### Plugin vs. Direct Usage
| Feature | Plugin UI | Direct chunkana |
|---------|-----------|-----------------|
| Basic chunking | ✅ | ✅ |
| Strategy selection | ✅ | ✅ |
| Hierarchical mode | ✅ | ✅ |
| Adaptive sizing | ❌ | ✅ |
| Streaming processing | ❌ | ✅ |
| Custom strategies | ❌ | ✅ |
| Performance monitoring | ❌ | ✅ |
## Conclusion
The migration to chunkana represents a significant improvement in the plugin's architecture and capabilities while maintaining complete backward compatibility. Users benefit from improved performance, enhanced features, and better maintainability without any required changes to existing workflows.
For questions or issues related to the migration, please refer to our [troubleshooting guide](troubleshooting.md) or open an issue on GitHub.