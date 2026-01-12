# Troubleshooting Guide
Comprehensive troubleshooting guide for the Advanced Markdown Chunker plugin and chunkana integration.
## 🚨 Plugin Installation Issues
### Plugin Not Showing in Dify
**Problem**: Plugin doesn't appear in Dify tool list after installation
**Solutions**:
1. **Verify Installation**:
- Go to Dify Settings → Plugins
- Check if "Advanced Markdown Chunker" is listed
- Ensure status shows "Active" or "Installed"
2. **Check Plugin Version**:
- Ensure you have v2.1.5 or later (chunkana-powered)
- Older versions may have compatibility issues
3. **Restart Dify**:
- Restart Dify application
- Clear browser cache if using web interface
4. **Check Dify Version**:
- Requires Dify 1.9.0 or higher
- Update Dify if using older version
### Plugin Installation Fails
**Problem**: `.difypkg` installation fails with error
**Solutions**:
1. **Check File Integrity**:
- Re-download plugin from [GitHub Releases](https://github.com/asukhodko/dify-markdown-chunker/releases)
- Verify file size and checksum if provided
2. **Check Permissions**:
- Ensure Dify has write permissions to plugin directory
- Run Dify with appropriate user permissions
3. **Check Dependencies**:
- Plugin automatically installs chunkana dependency
- If manual installation needed: `pip install chunkana>=0.1.0`
## 🔧 Configuration Issues
### Parameter Validation Errors
**Problem**: "Invalid parameter value" errors in Dify workflow
**Solutions**:
1. **Check Parameter Ranges**:
```yaml
# Valid ranges
max_chunk_size: 512-16384
chunk_overlap: 0 to (max_chunk_size * 0.35)
```
2. **Common Invalid Configurations**:
```yaml
# ❌ Invalid
max_chunk_size: 100 # Too small (min 512)
chunk_overlap: 2000 # Too large for chunk_size
# ✅ Valid
max_chunk_size: 2048
chunk_overlap: 200 # ~10% of chunk_size
```
### Chunk Overlap Issues
**Problem**: Overlap not working as expected
**Solutions**:
1. **Understand Overlap Cap**:
- Plugin caps overlap at 35% of chunk_size
- `chunk_overlap: 2000` with `max_chunk_size: 4096` → actual overlap: 1433
2. **Check Metadata Mode**:
```yaml
# With include_metadata: true (default)
# Overlap in metadata fields: previous_content, next_content
# With include_metadata: false
# Overlap embedded in chunk text
```
3. **For Full Overlap Control**:
- Use chunkana directly instead of plugin UI
- No 35% cap limitation
### Strategy Selection Issues
**Problem**: Wrong chunking strategy selected automatically
**Solutions**:
1. **Force Specific Strategy**:
```yaml
config:
strategy: code_aware # Force code-aware
strategy: list_aware # Force list-aware
strategy: structural # Force structural
strategy: fallback # Force fallback
```
2. **Understand Strategy Selection**:
- `auto` analyzes content and selects optimal strategy
- Code blocks/tables → code_aware
- Many lists → list_aware
- Headers → structural
- Simple text → fallback
## 📊 Output Issues
### Chunks Too Large/Small
**Problem**: Chunk sizes don't match expectations
**Solutions**:
1. **Check Actual vs Target Size**:
- `max_chunk_size` is a target, not absolute limit
- Atomic blocks (code, tables) preserved intact
- May result in larger chunks
2. **Adjust Configuration**:
```yaml
# For smaller chunks
max_chunk_size: 1024
# For larger chunks (code-heavy docs)
max_chunk_size: 6144
strategy: code_aware
```
3. **Use Adaptive Sizing** (chunkana direct):
```python
config = ChunkConfig(
use_adaptive_sizing=True,
adaptive_config=AdaptiveSizeConfig(
base_size=1500,
min_scale=0.5,
max_scale=1.5
)
)
```
### Missing Metadata
**Problem**: Chunks don't contain expected metadata
**Solutions**:
1. **Enable Metadata **:
```yaml
config:
include_metadata: true # Default, but verify
```
2. **Check Metadata Format**:
```
<metadata>
{
"content_type": "text",
"header_path": "/Section",
"start_line": 1,
"end_line": 5
}
</metadata>
# Actual content here...
```
3. **For Clean Text** (no metadata):
```yaml
config:
include_metadata: false
```
### Hierarchical Mode Issues
**Problem**: Hierarchical chunking not working as expected
**Solutions**:
1. **Enable Hierarchy**:
```yaml
config:
enable_hierarchy: true
debug: false # Exclude root/intermediate chunks
leaf_only: true # Only content chunks (recommended for vector DB)
```
2. **Understand Chunk Types**:
- **Root**: Document-level chunk (excluded by default)
- **Intermediate**: Section headers with children
- **Leaf**: Content chunks (recommended for indexing)
3. **Debug Hierarchy**:
```yaml
config:
enable_hierarchy: true
debug: true # Include all chunk types
leaf_only: false # See full hierarchy
```
## 🐛 Processing Errors
### chunkana Dependency Issues
**Problem**: "Module not found: chunkana" or import errors
**Solutions**:
1. **Check Plugin Version**:
- Ensure v2.1.5 or later (chunkana-powered)
- Earlier versions used embedded code
2. **Manual Dependency Installation**:
```bash
pip install chunkana>=0.1.0
```
3. **Check Python Environment**:
- Ensure Dify uses same Python environment
- Virtual environment activation if needed
### Memory Issues
**Problem**: Out of memory errors with large documents
**Solutions**:
1. **Reduce Chunk Size**:
```yaml
config:
max_chunk_size: 2048 # Smaller chunks
chunk_overlap: 100 # Reduce overlap
```
2. **Use Streaming** (chunkana direct):
```python
from chunkana import MarkdownChunker, StreamingConfig
streaming_config = StreamingConfig(
buffer_size=100_000,
max_memory_mb=50
)
for chunk in chunker.chunk_file_streaming(file_path, streaming_config):
# Process chunk immediately
pass
```
3. **Disable Advanced Features**:
```yaml
config:
enable_hierarchy: false
debug: false
```
### Processing Timeout
**Problem**: Processing takes too long or times out
**Solutions**:
1. **Use Simpler Strategy**:
```yaml
config:
strategy: fallback # Fastest strategy
```
2. **Reduce Document Size**:
- Split large documents before processing
- Process sections separately
3. **Optimize Configuration**:
```yaml
config:
max_chunk_size: 2048 # Smaller chunks process faster
strategy: fallback # Skip complex analysis
```
## 🔍 Content-Specific Issues
### Code Blocks Split Incorrectly
**Problem**: Code blocks broken across chunks
**Solutions**:
1. **Force Code-Aware Strategy**:
```yaml
config:
strategy: code_aware
max_chunk_size: 6144 # Larger chunks for code
```
2. **Check Code Block Size**:
- Very large code blocks may exceed chunk size
- Consider splitting large code examples
3. **Use Enhanced Code Handling** (chunkana direct):
```python
config = ChunkConfig(
strategy_override="code_aware",
enable_code_context_binding=True,
preserve_before_after_pairs=True
)
```
### Lists Split Inappropriately
**Problem**: Nested lists broken across chunks
**Solutions**:
1. **Force List-Aware Strategy**:
```yaml
config:
strategy: list_aware
```
2. **Adjust List Thresholds** (chunkana direct):
```python
config = ChunkConfig(
strategy_override="list_aware",
list_ratio_threshold=0.30, # More sensitive
list_count_threshold=3 # Activate sooner
)
```
### Tables Not Preserved
**Problem**: Tables split or malformed
**Solutions**:
1. **Use Code-Aware Strategy**:
```yaml
config:
strategy: code_aware # Handles tables
```
2. **Enable Table Grouping** (chunkana direct):
```python
config = ChunkConfig(
group_related_tables=True,
table_grouping_config=TableGroupingConfig(
max_distance_lines=10,
require_same_section=True
)
)
```
## 🚀 Performance Issues
### Slow Processing
**Problem**: Chunking takes too long
**Solutions**:
1. **Use Faster Strategy**:
```yaml
config:
strategy: fallback # Fastest processing
```
2. **Reduce Chunk Size**:
```yaml
config:
max_chunk_size: 2048 # Smaller chunks
chunk_overlap: 0 # No overlap
```
3. **Disable Advanced Features**:
```yaml
config:
enable_hierarchy: false
include_metadata: false # Minimal processing
```
### High Memory Usage
**Problem**: Memory consumption too high
**Solutions**:
1. **Process in Batches**:
- Split large documents into smaller sections
- Process sections separately
2. **Use Streaming** (chunkana direct):
```python
# Process large files with minimal memory
for chunk in chunker.chunk_file_streaming(file_path):
# Process immediately, don't accumulate
vector_db.add(chunk)
```
3. **Optimize Configuration**:
```yaml
config:
max_chunk_size: 1024 # Smaller chunks
enable_hierarchy: false
debug: false
```
## 🔄 Migration Issues
### Behavioral Differences After Migration
**Problem**: Different chunking results after v2.1.5 migration
**Solutions**:
1. **Understand Migration Changes**:
- Small-chunk merging improved
- More consistent metadata structure
- Enhanced overlap handling
2. **Check Migration Guide**:
- See [Migration to Chunkana Guide](migration-to-chunkana.md)
- Review behavioral differences section
3. **Validate Results**:
```python
# Compare pre/post migration results
# Check chunk boundaries and content
```
### Legacy API References
**Problem**: Old documentation or examples not working
**Solutions**:
1. **Update Import Statements**:
```python
# ❌ Old (no longer works)
from markdown_chunker_v2 import MarkdownChunker
# ✅ New (direct chunkana usage)
from chunkana import MarkdownChunker
```
2. **Use Plugin UI Instead**:
- For Dify workflows, use plugin tool interface
- No code changes needed
3. **Check Current Documentation**:
- Use current API reference
- Follow updated examples
## 🆘 Getting Help
### Diagnostic Information
When reporting issues, include:
1. **Plugin Version**:
```yaml
# Check in Dify Settings → Plugins
Version: 2.1.5 or later
```
2. **Configuration**:
```yaml
# Your tool configuration
config:
max_chunk_size: 4096
strategy: auto
# ... other parameters
```
3. **Sample Input**:
```markdown
# Minimal example that reproduces the issue
```
4. **Expected vs Actual Output**:
- What you expected to happen
- What actually happened
### Debug Mode
Enable debug mode for detailed information:
```yaml
config:
enable_hierarchy: true
debug: true # Shows all chunk types
```
### Performance Profiling
For performance issues (chunkana direct):
```python
chunker = MarkdownChunker(enable_performance_monitoring=True)
result = chunker.chunk(markdown_text)
# Check performance stats
stats = chunker.get_performance_stats
print(f"Processing time: {stats['chunk']['avg_time']:.3f}s")
print(f"Memory usage: {stats['memory']['peak_mb']:.1f}MB")
```
### Support Channels
1. **GitHub Issues**: [Report bugs and feature requests](https://github.com/asukhodko/dify-markdown-chunker/issues)
2. **GitHub Discussions**: [Ask questions and get help](https://github.com/asukhodko/dify-markdown-chunker/discussions)
3. **Documentation**: Check [Usage Guide](../usage.md) and [API Reference](../api/README.md)
### Common Solutions Summary
| Issue | Quick Fix |
|-------|-----------|
| Plugin not visible | Check Dify version ≥1.9.0, restart Dify |
| Chunks too large | Reduce `max_chunk_size`, use `fallback` strategy |
| Code blocks split | Use `strategy: code_aware`, increase chunk size |
| Lists split | Use `strategy: list_aware` |
| Slow processing | Use `strategy: fallback`, reduce chunk size |
| Memory issues | Use streaming (chunkana direct) or smaller chunks |
| Need advanced features | Use chunkana directly instead of plugin UI |
## 📚 Additional Resources
- [Usage Guide](../usage.md) - Comprehensive usage examples
- [Configuration Guide](../reference/configuration.md) - Detailed configuration options
- [Migration Guide](migration-to-chunkana.md) - Migration information
- [API Reference](../api/README.md) - Complete API documentation
- [Performance Guide](performance.md) - Performance optimization tips