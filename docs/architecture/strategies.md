# Chunking Strategies
Detailed documentation for all 5 chunking strategies powered by the chunkana engine.
## Overview
The Advanced Markdown Chunker plugin uses 5 intelligent strategies to chunk markdown documents. The system automatically selects the best strategy based on content analysis, or you can force a specific strategy using the `strategy` parameter in the plugin UI or `strategy_override` in direct chunkana usage.
## Strategy Selection
The chunkana engine analyzes content and selects a strategy based on:
- **Code ratio**: Percentage of content that is code (threshold: 30%)
- **Code blocks**: Presence of fenced code blocks
- **Tables**: Presence of markdown tables
- **List ratio**: Percentage of content that is lists (threshold: 40%)
- **List count**: Number of list items (threshold: 5)
- **Headers**: Number of headers (threshold: 3)
- **Document structure**: Overall structural complexity
## The 5 Strategies
### 1. Code-Aware Strategy
**When Used:**
- Documents with ≥30% code content
- Documents with any code blocks
- Documents with tables
**Behavior:**
- Preserves code blocks intact (never splits code)
- Preserves tables intact
- Groups related code with surrounding text
- Maintains code-text relationships
- Enhanced code-context binding (chunkana feature)
- Handles nested fencing (quadruple/quintuple backticks)
- Recognizes Before/After patterns and Code+Output pairs
**Best For:**
- Technical documentation
- API references with code examples
- Tutorial content with code samples
- Data documentation with tables
- Meta-documentation with nested code examples
**Example:**
```markdown
# API Documentation
The `process` function handles data:
```python
def process(data):
return data.upper
```
This function is thread-safe and returns uppercase strings.
```
**Chunking Result:**
- Chunk 1: Header + explanation + code block + note (all together)
- Code block never split, context preserved
**Plugin UI Configuration:**
```yaml
config:
strategy: code_aware
max_chunk_size: 6144 # Larger chunks for code
```
**Direct chunkana Configuration:**
```python
from chunkana import ChunkConfig
config = ChunkConfig(
strategy_override="code_aware",
enable_code_context_binding=True, # Enhanced feature
preserve_before_after_pairs=True # Enhanced feature
)
```
### 2. List-Aware Strategy
**When Used:**
- Documents with ≥40% list content (list_ratio ≥ 0.4)
- Documents with ≥5 list items
- Changelogs, release notes, feature lists
**Behavior:**
- Preserves list hierarchy intact (never splits parent from children)
- Detects and binds introduction context to lists
- Handles bullet lists (`-`, `*`, `+`)
- Handles numbered lists (`1.`, `2.`)
- Handles checkbox lists (`- `, `- [x]`)
- Maintains nested list structure
- Smart list grouping with context binding (chunkana enhancement)
- Intelligent hierarchy preservation
**Best For:**
- Changelogs and release notes
- Feature lists and requirements
- Task lists and TODO lists
- Documentation with extensive lists
- Meeting notes with action items
- Structured outlines and checklists
**Example:**
```markdown
# Release Notes v2.0
New features include:
- Authentication improvements
- OAuth2 support
- JWT tokens
- MFA options
- SMS verification
- Authenticator apps
- Performance optimizations
- Caching layer
- Database indexing
- Bug fixes
```
**Chunking Result:**
- Chunk 1: Header + introduction + complete Authentication hierarchy
- Chunk 2: Performance optimizations with all sub-items
- Chunk 3: Bug fixes
- Lists are never split mid-hierarchy
- Parent items always kept with their children
**Plugin UI Configuration:**
```yaml
config:
strategy: list_aware
max_chunk_size: 4096
```
**Direct chunkana Configuration:**
```python
config = ChunkConfig(
strategy_override="list_aware",
list_ratio_threshold=0.35, # Lower threshold for changelogs
list_count_threshold=3 # Activate with fewer lists
)
```
### 3. Structural Strategy
**When Used:** Documents with ≥3 headers
**Behavior:**
- Chunks by sections (headers)
- Maintains hierarchical structure
- Preserves section relationships
- Builds header path for context
- Respects header hierarchy levels
**Best For:**
- Long-form documentation
- User guides
- Structured articles
- README files
- Academic papers
**Example:**
```markdown
# Chapter 1: Introduction
Introduction text here.
## Section 1.1: Getting Started
Section content with details.
## Section 1.2: Advanced Topics
More detailed content.
# Chapter 2: Implementation
New chapter begins.
```
**Chunking Result:**
- Chunk 1: Chapter 1 introduction
- Chunk 2: Section 1.1 with full content
- Chunk 3: Section 1.2 with full content
- Chunk 4: Chapter 2 beginning
- Header paths preserved: "/Chapter 1", "/Chapter 1/Section 1.1", etc.
**Plugin UI Configuration:**
```yaml
config:
strategy: structural
max_chunk_size: 4096
```
**Direct chunkana Configuration:**
```python
config = ChunkConfig(
strategy_override="structural",
structure_threshold=2 # Activate with fewer headers
)
```
### 4. Fallback Strategy
**When Used:**
- Simple text without special structure
- Documents that don't match other strategies
- Always available as fallback
- Error recovery situations
**Behavior:**
- Chunks by paragraphs and sentence boundaries
- Respects paragraph boundaries
- Simple but reliable text splitting
- Handles any content type gracefully
- Maintains readability
**Best For:**
- Plain text documents
- Simple content
- Unstructured content
- Error recovery scenarios
**Example:**
```markdown
This is a simple document with multiple paragraphs. It doesn't have complex structure.
This is a new paragraph. It continues the content with more information about the topic.
Another paragraph here with additional details and explanations.
```
**Chunking Result:**
- Chunks based on paragraph boundaries and size limits
- Clean breaks at sentence boundaries when possible
**Plugin UI Configuration:**
```yaml
config:
strategy: fallback
max_chunk_size: 2048
```
**Direct chunkana Configuration:**
```python
config = ChunkConfig(strategy_override="fallback")
```
### 5. Auto Strategy (Default)
**When Used:** Default selection (strategy: auto)
**Behavior:**
- Automatically analyzes content
- Selects the optimal strategy based on content characteristics
- Provides the best chunking quality without manual configuration
- Falls back gracefully if primary strategy fails
**Best For:**
- General-purpose chunking
- Mixed content documents
- When you want optimal results without manual tuning
- Production systems requiring reliability
**Plugin UI Configuration:**
```yaml
config:
strategy: auto # Default
```
**Direct chunkana Configuration:**
```python
config = ChunkConfig(strategy_override=None) # Auto-select
```
## Strategy Selection Algorithm
```
1. Analyze content:
- Calculate code_ratio (percentage of code content)
- Count code blocks and tables
- Calculate list_ratio (percentage of list content)
- Count list items and nesting levels
- Count headers and analyze hierarchy
- Assess document complexity
2. Select strategy (by priority):
Priority 1: CodeAwareStrategy
if code_ratio >= 0.30 OR has_code_blocks OR has_tables:
use CodeAwareStrategy
Priority 2: ListAwareStrategy
if list_ratio >= 0.40 OR list_count >= 5:
use ListAwareStrategy
Priority 3: StructuralStrategy
elif header_count >= 3 AND has_hierarchy:
use StructuralStrategy
Priority 4: FallbackStrategy
else:
use FallbackStrategy (reliable default)
3. Apply strategy with chunkana enhancements:
- Code-context binding for code-aware
- List hierarchy preservation for list-aware
- Header path building for structural
- Graceful degradation for fallback
```
## Enhanced Features by Strategy
### Code-Aware Enhancements (chunkana)
- **Nested Fencing Support**: Handles quadruple/quintuple backticks for meta-documentation
- **Code-Context Binding**: Intelligently binds code blocks to explanations
- **Before/After Recognition**: Keeps refactoring examples together
- **Code+Output Pairing**: Groups execution results with code
- **Language-Aware Processing**: Optimizes based on programming language
### List-Aware Enhancements (chunkana)
- **Smart Context Binding**: Automatically attaches introduction paragraphs to lists
- **Hierarchy Preservation**: Never splits nested lists across depth levels
- **Type Detection**: Handles bullets, numbers, and checkboxes intelligently
- **Relationship Maintenance**: Preserves parent-child relationships
### Structural Enhancements (chunkana)
- **Header Path Building**: Creates hierarchical paths like "/Chapter 1/Section 1.1"
- **Section Boundary Respect**: Never splits sections inappropriately
- **Hierarchy Navigation**: Enables parent-child chunk relationships
## Performance Characteristics
| Strategy | Speed | Quality | Memory | Best For |
|----------|-------|---------|--------|----------|
| Code-Aware | Fast | Very High | Medium | Code/table-heavy docs |
| List-Aware | Fast | Very High | Low | List-heavy docs, changelogs |
| Structural | Medium | Very High | Medium | Structured docs |
| Fallback | Very Fast | Medium | Very Low | Simple text |
| Auto | Medium | Very High | Medium | General purpose |
## Plugin UI vs Direct chunkana
### Plugin UI Strategy Options
Available in the plugin `strategy` parameter:
- `auto` - Automatic selection (recommended)
- `code_aware` - Force code-aware strategy
- `list_aware` - Force list-aware strategy
- `structural` - Force structural strategy
- `fallback` - Force fallback strategy
### Direct chunkana Strategy Control
```python
from chunkana import MarkdownChunker, ChunkConfig
# Auto-selection with custom thresholds
config = ChunkConfig(
strategy_override=None, # Auto-select
code_threshold=0.25, # Lower threshold for code strategy
list_ratio_threshold=0.35, # Lower threshold for list strategy
structure_threshold=2 # Fewer headers needed
)
# Force specific strategy with enhancements
config = ChunkConfig(
strategy_override="code_aware",
enable_code_context_binding=True,
preserve_before_after_pairs=True,
bind_output_blocks=True
)
chunker = MarkdownChunker(config)
```
## Strategy Comparison Example
Given the same document, different strategies produce different results:
**Document:**
```markdown
# API Reference
The process function handles data transformation.
```python
def process(data):
return data.upper
```
Additional notes about thread safety.
## Parameters
- data: Input string
- returns: Uppercase string
```
**Strategy Results:**
| Strategy | Chunks | Behavior |
|----------|--------|----------|
| **Code-Aware** | 1 chunk | All content together, code block preserved |
| **List-Aware** | 2 chunks | Header+code in chunk 1, Parameters list in chunk 2 |
| **Structural** | 2 chunks | Main section in chunk 1, Parameters section in chunk 2 |
| **Fallback** | 3-4 chunks | Split by paragraphs and size |
| **Auto** | 1 chunk | Selects Code-Aware due to code block presence |
## Advanced Configuration
### Strategy-Specific Tuning (Direct chunkana)
```python
# Code-heavy document optimization
config = ChunkConfig(
strategy_override="code_aware",
max_chunk_size=6144, # Larger chunks for code
enable_code_context_binding=True,
max_context_chars_before=500,
preserve_before_after_pairs=True
)
# Changelog optimization
config = ChunkConfig(
strategy_override="list_aware",
list_ratio_threshold=0.30, # More sensitive
list_count_threshold=3, # Activate sooner
max_chunk_size=3072 # Smaller chunks for lists
)
# Documentation optimization
config = ChunkConfig(
strategy_override="structural",
structure_threshold=2, # Fewer headers needed
enable_hierarchy=True, # Parent-child relationships
include_metadata=True # Rich metadata
)
```
### Content-Adaptive Strategy Selection
```python
from chunkana import MarkdownChunker
def adaptive_strategy_config(content: str) -> ChunkConfig:
"""Select optimal configuration based on content analysis."""
chunker = MarkdownChunker
analysis = chunker.analyze_content(content)
if analysis.code_ratio > 0.4:
return ChunkConfig(
strategy_override="code_aware",
max_chunk_size=6144,
enable_code_context_binding=True
)
elif analysis.list_ratio > 0.3:
return ChunkConfig(
strategy_override="list_aware",
list_ratio_threshold=0.25
)
elif analysis.header_count > 5:
return ChunkConfig(
strategy_override="structural",
enable_hierarchy=True
)
else:
return ChunkConfig # Auto-select
# Use adaptive configuration
config = adaptive_strategy_config(markdown_content)
chunker = MarkdownChunker(config)
```
## Migration Notes
### From Legacy Versions
| Legacy Strategy | Current Strategy | Notes |
|----------------|------------------|-------|
| Code | code_aware | Enhanced with context binding |
| Table | code_aware | Tables handled by code-aware |
| Mixed | code_aware | Merged into code-aware |
| List | list_aware | Enhanced hierarchy preservation |
| Structural | structural | Improved header handling |
| Sentences | fallback | Simplified and more reliable |
### Plugin Migration
No changes needed for existing Dify workflows - all strategy names remain compatible.
## Troubleshooting
### Strategy Not Working as Expected
**Issue**: Wrong strategy selected automatically
**Solution**: Use explicit strategy selection or adjust thresholds
**Issue**: Code blocks being split
**Solution**: Force `code_aware` strategy or check chunk size limits
**Issue**: Lists being split inappropriately
**Solution**: Force `list_aware` strategy or reduce chunk size
**Issue**: Need advanced features
**Solution**: Use direct chunkana instead of plugin UI
### Performance Issues
**Issue**: Slow processing
**Solution**: Use `fallback` strategy for simple content or increase chunk size
**Issue**: High memory usage
**Solution**: Reduce chunk size or disable advanced features
## See Also
- [Usage Guide](../usage.md) - How to use strategies in practice
- [Configuration Guide](../reference/configuration.md) - Detailed configuration options
- [API Reference](../api/README.md) - Complete API documentation
- [Migration to Chunkana Guide](../guides/migration-to-chunkana.md) - Migration information