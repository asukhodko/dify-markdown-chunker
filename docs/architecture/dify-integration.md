# Dify Integration

Complete guide for Dify plugin integration.

## Overview

The Dify Markdown Chunker integrates with Dify as a tool plugin, providing intelligent markdown chunking for knowledge bases and workflows.

## Architecture

### Components

1. **MarkdownChunkerProvider** - Plugin provider class
2. **Tool Implementation** - Chunking tool for workflows
3. **Configuration** - Dify-specific settings

### Integration Flow

```
Dify Workflow → Tool Node → MarkdownChunker → Chunks → Next Node
```

## Using in Dify Workflows

### Basic Setup

1. Install plugin in Dify
2. Add tool node to workflow
3. Select "Advanced Markdown Chunker"
4. Configure parameters

### Workflow Configuration

```yaml
- node: markdown_chunker
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
    enable_overlap: false
```

### Example Workflow

**Document Processing Pipeline:**

```yaml
workflow:
  - node: load_document
    type: document_loader
  
  - node: chunk_markdown
    type: tool
    tool: advanced_markdown_chunker
    input: ${load_document.content}
    config:
      max_chunk_size: 2048
      strategy: auto
  
  - node: embed_chunks
    type: embedding
    input: ${chunk_markdown.chunks}
  
  - node: store_vectors
    type: vector_store
    input: ${embed_chunks.vectors}
```

## Configuration Parameters

### max_chunk_size
- **Type**: integer
- **Default**: 2048
- **Range**: 100-10000
- **Description**: Maximum chunk size in characters

### strategy
- **Type**: string
- **Default**: "auto"
- **Options**: "auto", "code", "mixed", "list", "table", "structural", "sentences"
- **Description**: Chunking strategy selection

### enable_overlap
- **Type**: boolean
- **Default**: false
- **Description**: Enable chunk overlap

### overlap_size
- **Type**: integer
- **Default**: 100
- **Description**: Overlap size in characters (if enabled)

## Use Cases

### Knowledge Base Ingestion

```yaml
- tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
    enable_overlap: true
    overlap_size: 100
```

### API Documentation Processing

```yaml
- tool: advanced_markdown_chunker
  config:
    max_chunk_size: 1500
    strategy: code
```

### General Documentation

```yaml
- tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: structural
```

## Troubleshooting

### Plugin Not Showing

**Problem**: Plugin doesn't appear in tool list

**Solution**:
- Verify plugin is installed: Settings → Plugins
- Check plugin status is "Active"
- Restart Dify if needed

### Chunking Issues

**Problem**: Chunks are too large/small

**Solution**:
- Adjust max_chunk_size parameter
- Try different strategy
- Enable overlap for better context

### Performance Issues

**Problem**: Slow processing

**Solution**:
- Use simpler strategy (sentences)
- Reduce max_chunk_size
- Process smaller documents

## See Also

- [Installation Guide](../installation.md) - Plugin installation
- [Usage Guide](../usage.md) - Usage examples
- [Chunking Strategies](strategies.md) - Strategy details
