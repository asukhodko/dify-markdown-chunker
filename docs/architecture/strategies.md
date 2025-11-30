# Chunking Strategies

Detailed documentation for all 6 chunking strategies.

## Overview

The Dify Markdown Chunker uses 6 intelligent strategies to chunk markdown documents. The system automatically selects the best strategy based on content analysis, or you can force a specific strategy.

## Strategy Selection

The chunker analyzes content and selects a strategy based on:

- **Code ratio**: Percentage of content that is code
- **List ratio**: Percentage of content in lists
- **Table ratio**: Percentage of content in tables
- **Structure**: Presence and hierarchy of headers
- **Complexity**: Overall document complexity

## The 6 Strategies

### 1. Code Strategy

**When Used:** Documents with >30% code content

**Behavior:**
- Preserves code blocks intact (never splits code)
- Groups related code with surrounding text
- Maintains code-text relationships

**Best For:**
- Technical documentation
- API references with code examples
- Tutorial content with code samples

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
config = ChunkConfig.for_code_docs()
# or
config = ChunkConfig(force_strategy="code")
```

### 2. Mixed Strategy

**When Used:** Balanced content (10-30% code, mixed elements)

**Behavior:**
- Balances code preservation with text chunking
- Handles mixed content types
- Flexible chunk boundaries

**Best For:**
- General documentation
- README files
- Mixed technical content

**Example:**
```markdown
# Overview

This is a description.

## Features

- Feature 1
- Feature 2

```python
example_code()
```
```

**Chunking Result:**
- Chunk 1: Overview section
- Chunk 2: Features list + code

**Configuration:**
```python
config = ChunkConfig(force_strategy="mixed")
```

### 3. List Strategy

**When Used:** Documents with >40% list content

**Behavior:**
- Preserves list structure
- Groups related list items
- Maintains list hierarchy

**Best For:**
- Feature lists
- Changelogs
- Itemized documentation

**Example:**
```markdown
# Features

- **Parser Module**
  - AST parsing
  - Code extraction
  
- **Chunker Module**
  - 6 strategies
  - Auto selection
```

**Chunking Result:**
- Chunk 1: Header + first main item with sub-items
- Chunk 2: Second main item with sub-items

**Configuration:**
```python
config = ChunkConfig(force_strategy="list")
```

### 4. Table Strategy

**When Used:** Documents with >30% table content

**Behavior:**
- Preserves tables intact
- Groups related tables
- Maintains table context

**Best For:**
- Data documentation
- Comparison tables
- Specification sheets

**Example:**
```markdown
# Performance

| Size | Time | Throughput |
|------|------|------------|
| 1KB  | 800ms| 1.3 KB/s   |
| 10KB | 150ms| 66 KB/s    |
```

**Chunking Result:**
- Chunk 1: Header + complete table (never split)

**Configuration:**
```python
config = ChunkConfig(force_strategy="table")
```

### 5. Structural Strategy

**When Used:** Well-structured documents with clear header hierarchy

**Behavior:**
- Chunks by sections (headers)
- Maintains hierarchical structure
- Preserves section relationships

**Best For:**
- Long-form documentation
- User guides
- Structured articles

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
config = ChunkConfig(force_strategy="structural")
```

### 6. Sentences Strategy

**When Used:** Simple text without special structure (fallback)

**Behavior:**
- Chunks by sentences
- Respects paragraph boundaries
- Simple text splitting

**Best For:**
- Plain text documents
- Simple content
- Fallback for unstructured content

**Example:**
```markdown
This is a simple document. It has multiple sentences. 
Each sentence is considered for chunking.

This is a new paragraph. It continues the content.
```

**Chunking Result:**
- Chunks based on sentence boundaries and size limits

**Configuration:**
```python
config = ChunkConfig(force_strategy="sentences")
```

## Strategy Selection Algorithm

```
1. Analyze content:
   - Calculate code_ratio
   - Calculate list_ratio
   - Calculate table_ratio
   - Analyze header structure
   - Calculate complexity

2. Select strategy:
   if code_ratio > 0.30:
       use Code Strategy
   elif table_ratio > 0.30:
       use Table Strategy
   elif list_ratio > 0.40:
       use List Strategy
   elif has_clear_structure:
       use Structural Strategy
   elif code_ratio > 0.10:
       use Mixed Strategy
   else:
       use Sentences Strategy
```

## Performance Characteristics

| Strategy | Speed | Quality | Best For |
|----------|-------|---------|----------|
| Code | Fast | High | Code-heavy docs |
| Mixed | Medium | High | General docs |
| List | Fast | High | List-heavy docs |
| Table | Fast | High | Table-heavy docs |
| Structural | Medium | Very High | Structured docs |
| Sentences | Very Fast | Medium | Simple text |

## Forcing a Strategy

You can override automatic selection:

```python
from markdown_chunker import MarkdownChunker, ChunkConfig

# Force code strategy
config = ChunkConfig(force_strategy="code")
chunker = MarkdownChunker(config)

# Force structural strategy
config = ChunkConfig(force_strategy="structural")
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

**Code Strategy:** 1 chunk (all together)
**Structural Strategy:** 1 chunk (one section)
**Sentences Strategy:** 2-3 chunks (by sentences)

## See Also

- [Architecture Overview](README.md) - System architecture
- [ChunkConfig API](../api/config.md) - Configuration options
- [Performance Guide](../guides/performance.md) - Performance tips
