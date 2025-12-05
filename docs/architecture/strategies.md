# Chunking Strategies

Detailed documentation for all 3 chunking strategies in v2.0.

## Overview

The Dify Markdown Chunker v2.0 uses 3 intelligent strategies to chunk markdown documents. The system automatically selects the best strategy based on content analysis, or you can force a specific strategy using `strategy_override`.

## Strategy Selection

The chunker analyzes content and selects a strategy based on:

- **Code ratio**: Percentage of content that is code (threshold: 30%)
- **Code blocks**: Presence of fenced code blocks
- **Tables**: Presence of markdown tables
- **Headers**: Number of headers (threshold: 3)

## The 3 Strategies

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

### 2. Structural Strategy

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

### 3. Fallback Strategy

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
   - Count headers

2. Select strategy:
   if code_ratio >= 0.30 OR has_code_blocks OR has_tables:
       use CodeAwareStrategy
   elif header_count >= 3:
       use StructuralStrategy
   else:
       use FallbackStrategy
```

## Performance Characteristics

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| Code-Aware | Fast | High | Code/table-heavy docs |
| Structural | Medium | Very High | Structured docs |
| Fallback | Very Fast | Medium | Simple text |

## Forcing a Strategy

You can override automatic selection:

```python
from markdown_chunker_v2 import MarkdownChunker, ChunkConfig

# Force code-aware strategy
config = ChunkConfig(strategy_override="code_aware")
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
**Structural Strategy:** 1 chunk (one section)
**Fallback Strategy:** 2-3 chunks (by paragraphs)

## Migration from v1.x

| v1.x Strategy | v2.0 Strategy |
|---------------|---------------|
| Code | CodeAware |
| Table | CodeAware |
| Mixed | CodeAware |
| List | CodeAware |
| Structural | Structural |
| Sentences | Fallback |

## See Also

- [Architecture Overview](README.md) - System architecture
- [ChunkConfig API](../api/config.md) - Configuration options
- [Migration Guide](../MIGRATION.md) - Migration from v1.x
