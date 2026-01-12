# 🚀 Quick Start
Get started with the Advanced Markdown Chunker plugin in 5 minutes.
## 📦 Installation
### As Dify Plugin (Recommended)
1. **Download Plugin**:
- Go to [GitHub Releases](https://github.com/asukhodko/dify-markdown-chunker/releases/latest)
- Download the `.difypkg` file
2. **Install in Dify**:
- Open Dify: Settings → Plugins → Install Plugin
- Upload the `.difypkg` file
- Plugin will be available immediately
3. **Requirements**:
- Dify version 1.9.0 or higher
- No additional configuration needed
### For Development
```bash
# Clone the repository
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker
# Create virtual environment
python -m venv venv
source venv/bin/activate
# Install dependencies (includes chunkana)
pip install -r requirements.txt
# Run tests
make test
```
## 🎯 Basic Usage
### Using in Dify Workflows
**Simple RAG Configuration:**
```yaml
- node: chunk_document
type: tool
tool: advanced_markdown_chunker
config:
input_text: ${document.content}
max_chunk_size: 2048
strategy: auto
include_metadata: true
```
**Hierarchical Processing:**
```yaml
- node: hierarchical_chunks
type: tool
tool: advanced_markdown_chunker
config:
input_text: ${document.content}
enable_hierarchy: true
leaf_only: true # Only content chunks for vector DB
```
### Using chunkana Directly (Advanced)
For features not available in the plugin UI:
```python
from chunkana import MarkdownChunker
# Basic usage
chunker = MarkdownChunker
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
for i, chunk in enumerate(result.chunks, 1):
print(f"Chunk {i}: {chunk.size} chars, lines {chunk.start_line}-{chunk.end_line}")
```
### With Custom Configuration
```python
from chunkana import MarkdownChunker, ChunkConfig
# Custom configuration
config = ChunkConfig(
max_chunk_size=2048,
overlap_size=100,
include_metadata=True,
strategy_override=None # Auto-select
)
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)
# Access analysis
print(f"Content type: {result.analysis.content_type}")
print(f"Code ratio: {result.analysis.code_ratio:.2%}")
print(f"Complexity: {result.analysis.complexity_score:.2f}")
```
### Using Configuration Profiles
```python
from chunkana import ChunkConfig
# For code-heavy documents
config = ChunkConfig.for_code_heavy
# For Dify RAG systems (matches plugin defaults)
config = ChunkConfig.for_dify_rag
# For search indexing
config = ChunkConfig.for_search_indexing
```
## 📝 Example: Processing a Document
### Plugin UI Example
```yaml
workflow:
- node: load_document
type: Data Source File → Doc Extractor
config:
source: file_upload
- node: chunk_markdown
type: tool
tool: advanced_markdown_chunker
config:
input_text: ${load_document.content}
max_chunk_size: 2048
chunk_overlap: 100
strategy: auto
include_metadata: true
- node: embed_chunks
type:
input: ${chunk_markdown.result}
```
### Direct chunkana Example
```python
from chunkana import MarkdownChunker
markdown_text = """
# API Documentation
## Introduction
This is example documentation with code:
```python
def hello_world:
print("Hello, World!")
return "success"
```
### Features
- Multiple language support
- Automatic content type detection
- Metadata extraction
| Parameter | Type | Description |
|-----------|------|-------------|
| name | str | Function name |
| result | any | Execution result |
"""
# Process document
chunker = MarkdownChunker
result = chunker.chunk(markdown_text, include_analysis=True)
# Print results
print(f"📄 Processed document: {result.analysis.total_chars} chars")
print(f"🔍 Found elements:")
print(f" - Headers: {result.analysis.header_count}")
print(f" - Code blocks: {result.analysis.code_block_count}")
print(f"📊 Content type: {result.analysis.content_type}")
print(f"⚡ Strategy used: {result.strategy_used}")
print(f"📦 Created {len(result.chunks)} chunks")
# Access individual chunks
for i, chunk in enumerate(result.chunks, 1):
print(f"\nChunk {i}:")
print(f" Size: {chunk.size} chars")
print(f" Lines: {chunk.start_line}-{chunk.end_line}")
print(f" Type: {chunk.metadata.get('content_type', 'unknown')}")
print(f" Preview: {chunk.content[:100]}...")
```
## 🔧 Advanced Features
### Hierarchical Chunking
**Plugin UI:**
```yaml
config:
enable_hierarchy: true
leaf_only: true # Only content chunks
debug: false # Exclude root/intermediate chunks
```
**Direct chunkana:**
```python
from chunkana import MarkdownChunker
chunker = MarkdownChunker
result = chunker.chunk_hierarchical(markdown_text)
# Navigate hierarchy
root = result.get_chunk(result.root_id)
sections = result.get_children(result.root_id)
for section in sections:
print(f"Section: {section.metadata['header_path']}")
subsections = result.get_children(section.metadata['chunk_id'])
for subsection in subsections:
print(f" - {subsection.metadata['header_path']}")
```
### Adaptive Chunk Sizing (chunkana only)
```python
from chunkana import ChunkConfig, AdaptiveSizeConfig
# Enable adaptive sizing
config = ChunkConfig(
use_adaptive_sizing=True,
adaptive_config=AdaptiveSizeConfig(
base_size=1500,
min_scale=0.5,
max_scale=1.5
)
)
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text)
# Chunks automatically sized based on complexity
for chunk in result.chunks:
complexity = chunk.metadata.get('content_complexity', 0)
adaptive_size = chunk.metadata.get('adaptive_size', 0)
print(f"Complexity: {complexity:.2f}, Adaptive size: {adaptive_size}")
```
### Convenience Functions
```python
from chunkana import chunk_text, chunk_file
# Chunk text directly
chunks = chunk_text("# Hello\n\nWorld")
# Chunk from file
chunks = chunk_file("README.md")
# With custom config
config = ChunkConfig.for_code_heavy
chunks = chunk_file("docs/api.md", config)
```
## 🎨 Chunking Strategies
The system automatically selects the best strategy based on content analysis:
| Strategy | When Used | Best For |
|----------|-----------|----------|
| **Code-Aware** | ≥30% code content | Technical docs, API references |
| **List-Aware** | ≥40% list content | Changelogs, feature lists |
| **Structural** | ≥3 headers | Documentation, guides |
| **Fallback** | Simple content | Plain text, mixed content |
| **Auto** | Default | General-purpose (recommended) |
**Force a specific strategy:**
Plugin UI:
```yaml
config:
strategy: code_aware # or list_aware, structural, fallback
```
Direct chunkana:
```python
config = ChunkConfig(strategy_override="code_aware")
```
## 🧪 Testing Your Setup
### Plugin Installation Test
1. Create a simple Dify workflow
2. Add the Advanced Markdown Chunker tool
3. Test with sample markdown:
```markdown
# Test Document
This is a test with code:
```python
print("Hello, World!")
```
- Item 1
- Item 2
```
### Development Environment Test
```bash
# Run all tests
make test
# Run with verbose output
make test-verbose
# Run migration compatibility tests
pytest tests/test_migration_*.py -v
# Quick functionality test
python -c "
from chunkana import MarkdownChunker
chunker = MarkdownChunker
result = chunker.chunk('# Test\n\nContent here')
print(f'Success: {len(result.chunks)} chunks created')
"
```
## 📊 Plugin vs Direct Usage
### When to Use Plugin UI
✅ **Use Plugin UI when:**
- Working within Dify workflows
- Need standard chunking features
- Want simple configuration
- Building RAG systems
### When to Use Direct chunkana
✅ **Use Direct chunkana when:**
- Need advanced features (adaptive sizing, streaming, table grouping)
- Want full configuration control
- Building custom applications
- Need performance monitoring
### Feature Comparison
| Feature | Plugin UI | Direct chunkana |
|---------|-----------|-----------------|
| Basic chunking | ✅ | ✅ |
| Strategy selection | ✅ | ✅ |
| Hierarchical mode | ✅ (basic) | ✅ (full) |
| Adaptive sizing | ❌ | ✅ |
| Streaming processing | ❌ | ✅ |
| Table grouping | ❌ | ✅ |
| Performance monitoring | ❌ | ✅ |
## 📚 Next Steps
1. **For Plugin Users**:
- Read [Usage Guide](usage.md) for Dify workflow examples
- Check [Configuration Guide](reference/configuration.md) for parameter details
- See [Troubleshooting Guide](guides/troubleshooting.md) for common issues
2. **For Advanced Users**:
- Explore [chunkana Documentation](https://github.com/asukhodko/chunkana) for full API
- Learn about [Chunking Strategies](architecture/strategies.md) in detail
- Review [API Reference](api/README.md) for complete documentation
3. **For Developers**:
- Check [Migration Guide](guides/migration-to-chunkana.md) for architecture details
- See [Developer Guide](guides/developer-guide.md) for contribution guidelines
## 🆘 Troubleshooting
### Plugin Issues
**Plugin not visible in Dify:**
- Check Dify version ≥ 1.9.0
- Restart Dify application
- Verify plugin status in Settings → Plugins
**Parameter validation errors:**
```yaml
# ❌ Invalid
max_chunk_size: 100 # Too small (min 512)
chunk_overlap: 2000 # Too large (max 35% of chunk_size)
# ✅ Valid
max_chunk_size: 2048
chunk_overlap: 200
```
### Direct chunkana Issues
**Import errors:**
```python
# ❌ Wrong (old embedded code)
from markdown_chunker import MarkdownChunker
# ✅ Correct (chunkana library)
from chunkana import MarkdownChunker
```
**Configuration issues:**
```python
# Make sure to use ChunkConfig from chunkana
from chunkana import ChunkConfig
config = ChunkConfig(max_chunk_size=2048)
```
### Common Solutions
| Issue | Solution |
|-------|----------|
| Plugin not visible | Check Dify version, restart application |
| Chunks too large | Reduce `max_chunk_size` or use `fallback` strategy |
| Code blocks split | Use `strategy: code_aware` |
| Need advanced features | Use chunkana directly instead of plugin UI |
For detailed troubleshooting, see [Troubleshooting Guide](guides/troubleshooting.md).