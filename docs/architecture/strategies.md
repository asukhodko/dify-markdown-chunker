# Chunking Strategies

Detailed documentation for all 4 chunking strategies in v2.0.

## Overview

The Dify Markdown Chunker v2.0 uses 4 intelligent strategies to chunk markdown documents. The system automatically selects the best strategy based on content analysis, or you can force a specific strategy using `strategy_override`.

## Strategy Selection

The chunker analyzes content and selects a strategy based on:

- **Code ratio**: Percentage of content that is code (threshold: 30%)
- **Code blocks**: Presence of fenced code blocks
- **Tables**: Presence of markdown tables
- **List ratio**: Percentage of content that is lists (threshold: 40%)
- **List count**: Number of list items (threshold: 5)
- **Headers**: Number of headers (threshold: 3)

## The 4 Strategies

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

**Best For:**
- Technical documentation
- API references with code examples
- Tutorial content with code samples
- Data documentation with tables

**Example:**
```markdown
# API Documentation

The `process()` function handles data:

```python
def process(data):
    return data.upper()
```

This function is thread-safe.
```

**Chunking Result:**
- Chunk 1: Header + explanation + code block + note (all together)

**Configuration:**
```python
config = ChunkConfig(strategy_override="code_aware")
# or use profile
config = ChunkConfig.for_code_heavy()
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
- Handles checkbox lists (`- [ ]`, `- [x]`)
- Maintains nested list structure

**Best For:**
- Changelogs and release notes
- Feature lists and requirements
- Task lists and TODO lists
- Documentation with extensive lists
- Meeting notes with action items

**Example:**
```markdown
# Release Notes v2.0

New features include:

- Authentication improvements
  - OAuth2 support
  - JWT tokens
- Performance optimizations
  - Caching layer
  - Database indexing
- Bug fixes
```

**Chunking Result:**
- Chunk 1: Header + introduction + complete list hierarchy
- Lists are never split mid-hierarchy
- Parent items always kept with their children

**Configuration:**
```python
config = ChunkConfig(strategy_override="list_aware")
# or use profile
config = ChunkConfig.for_changelogs()
```

### 3. Structural Strategy

**When Used:** Documents with ≥3 headers

**Behavior:**
- Chunks by sections (headers)
- Maintains hierarchical structure
- Preserves section relationships
- Builds header path for context

**Best For:**
- Long-form documentation
- User guides
- Structured articles
- README files

**Example:**
```markdown
# Chapter 1

Introduction text.

## Section 1.1

Section content.

## Section 1.2

More content.

# Chapter 2

New chapter.
```

**Chunking Result:**
- Chunk 1: Chapter 1 intro
- Chunk 2: Section 1.1
- Chunk 3: Section 1.2
- Chunk 4: Chapter 2

**Configuration:**
```python
config = ChunkConfig(strategy_override="structural")
# or use profile
config = ChunkConfig.for_structured()
```

### 4. Fallback Strategy

**When Used:** 
- Simple text without special structure
- Documents that don't match other strategies
- Always available as fallback

**Behavior:**
- Chunks by paragraphs
- Respects paragraph boundaries
- Simple text splitting
- Handles any content type

**Best For:**
- Plain text documents
- Simple content
- Unstructured content

**Example:**
```markdown
This is a simple document. It has multiple paragraphs.

This is a new paragraph. It continues the content.

Another paragraph here.
```

**Chunking Result:**
- Chunks based on paragraph boundaries and size limits

**Configuration:**
```python
config = ChunkConfig(strategy_override="fallback")
```

## Strategy Selection Algorithm

```
1. Analyze content:
   - Calculate code_ratio
   - Count code blocks
   - Count tables
   - Calculate list_ratio
   - Count list items
   - Count headers

2. Select strategy (by priority):
   Priority 1: CodeAwareStrategy
      if code_ratio >= 0.30 OR has_code_blocks OR has_tables:
          use CodeAwareStrategy
   
   Priority 2: ListAwareStrategy
      elif list_ratio >= 0.40 OR list_count >= 5:
          use ListAwareStrategy
   
   Priority 3: StructuralStrategy
      elif header_count >= 3:
          use StructuralStrategy
   
   Priority 4: FallbackStrategy
      else:
          use FallbackStrategy
```

## Performance Characteristics

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| Code-Aware | Fast | High | Code/table-heavy docs |
| List-Aware | Fast | High | List-heavy docs, changelogs |
| Structural | Medium | Very High | Structured docs |
| Fallback | Very Fast | Medium | Simple text |

## Forcing a Strategy

You can override automatic selection:

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

# Force code-aware strategy
config = ChunkConfig(strategy_override="code_aware")
chunker = MarkdownChunker(config)

# Force list-aware strategy
config = ChunkConfig(strategy_override="list_aware")
chunker = MarkdownChunker(config)

# Force structural strategy
config = ChunkConfig(strategy_override="structural")
chunker = MarkdownChunker(config)

# Force fallback strategy
config = ChunkConfig(strategy_override="fallback")
chunker = MarkdownChunker(config)
```

## Strategy Comparison Example

Given the same document, different strategies produce different results:

**Document:**
```markdown
# API

Description here.

```python
def example():
    pass
```

More text.
```

**Code-Aware Strategy:** 1 chunk (code block preserved)
**List-Aware Strategy:** 2 chunks (by list hierarchy if large)
**Structural Strategy:** 1 chunk (one section)
**Fallback Strategy:** 2-3 chunks (by paragraphs)

## Migration from v1.x

| v1.x Strategy | v2.0 Strategy |
|---------------|---------------|
| Code | CodeAware |
| Table | CodeAware |
| Mixed | CodeAware |
| List | ListAware |
| Structural | Structural |
| Sentences | Fallback |

## See Also

- [Architecture Overview](README.md) - System architecture
- [ChunkConfig API](../api/config.md) - Configuration options
- [Migration Guide](../MIGRATION.md) - Migration from v1.x
