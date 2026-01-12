# Usage Guide
Comprehensive guide for using the Advanced Markdown Chunker plugin, powered by the chunkana engine, in different scenarios.
## 🎯 Using in Dify Workflows
### Basic Workflow Setup
1. Create or open a workflow in Dify
2. Add a "Tool" node
3. Select "Advanced Markdown Chunker"
4. Configure parameters:
- **max_chunk_size**: 2048 (recommended for RAG)
- **strategy**: auto (automatic selection)
- **chunk_overlap**: 100 (adaptive overlap)
### Example Workflow
```yaml
workflow:
- node: Data Source File → Doc Extractor
type: Data Source File → Doc Extractor
config:
source: file_upload
- node: markdown_chunker
type: tool
tool: advanced_markdown_chunker
config:
max_chunk_size: 2048
strategy: auto
chunk_overlap: 100
include_metadata: true
- node:
type:
input: ${markdown_chunker.result}
```
### Hierarchical Chunking Workflow
```yaml
workflow:
- node: Data Source File → Doc Extractor
type: Data Source File → Doc Extractor
config:
source: file_upload
- node: hierarchical_chunker
type: tool
tool: advanced_markdown_chunker
config:
max_chunk_size: 2048
enable_hierarchy: true
leaf_only: true # Only content chunks for vector DB
include_metadata: true
- node:
type:
input: ${hierarchical_chunker.result}
```
### Output Filtering and Indexable Behavior
The plugin provides sophisticated output filtering for hierarchical chunking:
#### Chunk Types and Indexable Field
| Chunk Type | is_root | is_leaf | indexable | Description |
|------------|---------|---------|-----------|-------------|
| **Root** | true | false | false | Document-level chunk (entire document) |
| **Intermediate** | false | false | true | Section headers with children |
| **Leaf** | false | true | true | Content chunks (recommended for vector DB) |
#### Filtering Options
**Plugin UI Parameters:**
```yaml
config:
enable_hierarchy: true
debug: false # Exclude root chunks (default)
leaf_only: true # Only leaf chunks (content only)
```
**Filtering Behavior:**
- `debug=false` (default): Root chunk excluded from results
- `debug=true`: All chunks included (root, intermediate, leaf)
- `leaf_only=true`: Only leaf chunks returned (recommended for vector DB indexing)
- `leaf_only=false`: Both intermediate and leaf chunks returned
#### Example Output Structure
**With `debug=false, leaf_only=false`:**
```json
[
{
"content": "# Section 1\n\nIntroduction...",
"metadata": {
"is_root": false,
"is_leaf": false,
"indexable": true,
"hierarchy_level": 1
}
},
{
"content": "Detailed content...",
"metadata": {
"is_root": false,
"is_leaf": true,
"indexable": true,
"hierarchy_level": 2
}
}
]
```
**With `leaf_only=true` (Recommended for Vector DB):**
```json
[
{
"content": "Detailed content...",
"metadata": {
"is_root": false,
"is_leaf": true,
"indexable": true,
"hierarchy_level": 2
}
}
]
```
#### Direct chunkana Output Filtering
For advanced filtering with direct chunkana usage:
```python
from chunkana import MarkdownChunker
chunker = MarkdownChunker
result = chunker.chunk_hierarchical(markdown_text)
# Get only indexable chunks
indexable_chunks = [
chunk for chunk in result.chunks
if chunk.metadata.get('indexable', True)
]
# Get only leaf chunks (content only)
leaf_chunks = result.get_flat_chunks
# Get chunks by hierarchy level
section_chunks = result.get_by_level(1) # Top-level sections
content_chunks = result.get_by_level(2) # Content chunks
```
## 🐍 Using Chunkana Directly
For advanced features not available in the plugin UI, use chunkana directly:
### Basic Usage
```python
from chunkana import MarkdownChunker
# Create chunker
chunker = MarkdownChunker
# Chunk markdown
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)
# Access chunks
for chunk in result.chunks:
print(f"Chunk: {chunk.content[:50]}...")
print(f"Lines: {chunk.start_line}-{chunk.end_line}")
print(f"Size: {chunk.size} chars")
```
### With Configuration
```python
from chunkana import MarkdownChunker, ChunkConfig
# Create custom config
config = ChunkConfig(
max_chunk_size=2048,
min_chunk_size=256,
overlap_size=100,
include_metadata=True
)
# Use config
chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text, include_analysis=True)
```
### Configuration Profiles
```python
from chunkana import ChunkConfig
# For code-heavy documents
config = ChunkConfig.for_code_heavy
# For Dify RAG systems (matches plugin defaults)
config = ChunkConfig.for_dify_rag
# For search indexing
config = ChunkConfig.for_search_indexing
```
## 📚 Common Use Cases
### Use Case 1: RAG System (Plugin UI)
**Dify Workflow Configuration:**
```yaml
- node: chunk_for_rag
type: tool
tool: advanced_markdown_chunker
config:
max_chunk_size: 2048
strategy: auto
chunk_overlap: 100
include_metadata: true # Embeds metadata in chunk text
```
**Result:** Chunks with embedded metadata for better retrieval:
```
<metadata>
{
"content_type": "text",
"header_path": "/Installation/Requirements",
"start_line": 45,
"end_line": 52
}
</metadata>
# Requirements
Python 3.12 or higher is required...
```
### Use Case 2: Code Documentation (Direct chunkana)
```python
from chunkana import MarkdownChunker, ChunkConfig
# Configure for code-heavy docs with advanced features
config = ChunkConfig(
max_chunk_size=4096, # Larger chunks for code
strategy_override="code_aware",
enable_code_context_binding=True, # Not available in plugin UI
preserve_before_after_pairs=True # Not available in plugin UI
)
chunker = MarkdownChunker(config)
result = chunker.chunk(code_docs, include_analysis=True)
# Code blocks are preserved with enhanced context
print(f"Strategy used: {result.strategy_used}")
print(f"Code ratio: {result.analysis.code_ratio:.2%}")
```
### Use Case 3: Hierarchical Document Processing
**Plugin UI (Basic Hierarchy):**
```yaml
- node: hierarchical_chunker
type: tool
tool: advanced_markdown_chunker
config:
enable_hierarchy: true
leaf_only: true
debug: false
```
**Direct chunkana (Advanced Hierarchy):**
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
## 🔧 Plugin vs. Direct Usage Comparison
### Feature Availability
| Feature | Plugin UI | Direct chunkana |
|---------|-----------|-----------------|
| Basic chunking | ✅ | ✅ |
| Strategy selection | ✅ (5 strategies) | ✅ (5 strategies) |
| Hierarchical mode | ✅ (basic) | ✅ (full navigation) |
| Metadata | ✅ | ✅ |
| Overlap control | ✅ (capped at 35%) | ✅ (full control) |
| Adaptive sizing | ❌ | ✅ |
| Streaming processing | ❌ | ✅ |
| Code-context binding | ❌ | ✅ (advanced) |
| Table grouping | ❌ | ✅ |
| Custom strategies | ❌ | ✅ |
| Performance monitoring | ❌ | ✅ |
### When to Use Plugin UI
- ✅ Standard RAG workflows in Dify
- ✅ Simple chunking requirements
- ✅ No custom configuration needed
- ✅ Want Dify workflow integration
### When to Use Direct chunkana
- ✅ Advanced configuration requirements
- ✅ Custom chunking strategies
- ✅ Performance monitoring needed
- ✅ Streaming large documents
- ✅ Complex hierarchical navigation
- ✅ Integration with non-Dify systems
## 🔧 Advanced Features (Direct chunkana Only)
### Content Analysis
```python
result = chunker.chunk(markdown, include_analysis=True)
# Access analysis
analysis = result.analysis
print(f"Content type: {analysis.content_type}")
print(f"Code ratio: {analysis.code_ratio:.2%}")
print(f"Complexity: {analysis.complexity_score:.2f}")
print(f"Header count: {analysis.header_count}")
print(f"Code block count: {analysis.code_block_count}")
```
### Streaming Processing
```python
from chunkana import MarkdownChunker, StreamingConfig
# Configure streaming for large files
streaming_config = StreamingConfig(
buffer_size=100_000, # 100KB windows
max_memory_mb=50 # Memory limit
)
# Process large file efficiently
for chunk in chunker.chunk_file_streaming("large_doc.md", streaming_config):
# Process each chunk immediately
vector_db.add(chunk.content, chunk.metadata)
```
### Adaptive Chunk Sizing
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
result = chunker.chunk(markdown)
# Chunks automatically sized based on complexity
for chunk in result.chunks:
print(f"Size: {chunk.size}, Complexity: {chunk.metadata['content_complexity']}")
```
### Convenience Functions
```python
from chunkana import chunk_text, chunk_file
# Chunk text directly
chunks = chunk_text("# Hello\n\nWorld")
# Chunk from file
chunks = chunk_file("README.md")
# With config
config = ChunkConfig.for_code_heavy
chunks = chunk_file("docs/api.md", config)
```
## 📊 Strategy Selection
The system automatically selects the optimal strategy based on content analysis:
| Strategy | Priority | Activation | Best For |
|----------|----------|------------|----------|
| **Code-Aware** | 1 | code_ratio ≥ 30% | Technical docs, API docs |
| **List-Aware** | 2 | list_ratio > 40% OR list_count ≥ 5 | Changelogs, feature lists |
| **Structural** | 3 | ≥3 headers with hierarchy | Documentation, guides |
| **Fallback** | 4 | Always applicable | Simple text, mixed content |
Force a specific strategy:
**Plugin UI:**
```yaml
config:
strategy: code_aware # or list_aware, structural, fallback
```
**Direct chunkana:**
```python
config = ChunkConfig(strategy_override="code_aware")
chunker = MarkdownChunker(config)
```
## 🆘 Troubleshooting
### Plugin-Specific Issues
**Issue:** Chunks are larger/smaller than expected
**Solution:** The plugin caps overlap at 35% of chunk size. For full control, use chunkana directly.
**Issue:** Need advanced features not in plugin UI
**Solution:** Use chunkana directly for features like adaptive sizing, streaming, and custom strategies.
**Issue:** Hierarchical mode not providing enough detail
**Solution:** Use direct chunkana for full hierarchical navigation API.
### General Issues
See [Troubleshooting Guide](guides/troubleshooting.md) for common issues and solutions.
## 📚 Next Steps
- Review [API Reference](api/README.md) - Complete API documentation
- Learn about [Chunking Strategies](architecture/strategies.md) - Strategy details
- Check [Configuration Options](reference/configuration.md) - Advanced configuration
- Read [Migration to Chunkana Guide](guides/migration-to-chunkana.md) - Migration information
- Get help with [Troubleshooting Guide](guides/troubleshooting.md) - Common issues
- Explore [chunkana Documentation](https://github.com/asukhodko/chunkana) - Full library features