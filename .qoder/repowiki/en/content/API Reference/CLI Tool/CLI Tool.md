# CLI Tool

<cite>
**Referenced Files in This Document**   
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py)
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml)
- [provider/markdown_chunker.yaml](file://provider/markdown_chunker.yaml)
- [main.py](file://main.py)
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py)
- [README.md](file://README.md)
- [examples/basic_usage.py](file://examples/basic_usage.py)
- [examples/dify_integration.py](file://examples/dify_integration.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Command-Line Interface Overview](#command-line-interface-overview)
3. [Configuration File Format](#configuration-file-format)
4. [Usage Examples](#usage-examples)
5. [Error Messages and Exit Codes](#error-messages-and-exit-codes)
6. [Shell Scripting Integration](#shell-scripting-integration)
7. [Conclusion](#conclusion)

## Introduction
The Advanced Markdown Chunker is a command-line interface tool designed for intelligent, structure-aware chunking of Markdown documents. It is specifically optimized for Retrieval-Augmented Generation (RAG) systems and integrates seamlessly with Dify's Knowledge Base ingestion pipeline. The tool analyzes Markdown content and intelligently splits it into chunks while preserving document structure, maintaining semantic context, supporting configurable chunk size and overlap, and providing rich metadata for each chunk.

**Section sources**
- [README.md](file://README.md#L1-L281)

## Command-Line Interface Overview
The CLI tool exposes a comprehensive set of commands, options, and arguments through the Dify plugin system. The primary interface is accessed through the `markdown_chunk_tool` which processes Markdown documents according to specified parameters.

### Available Commands and Options
The tool accepts the following parameters through its YAML configuration:

- **input_text** (string, required): The Markdown text content to be chunked
- **max_chunk_size** (number, optional): Maximum size of each chunk in characters (default: 1000)
- **chunk_overlap** (number, optional): Number of characters to overlap between consecutive chunks (default: 100)
- **strategy** (select, optional): Strategy for chunking the document (default: auto)
- **include_metadata** (boolean, optional): Include structural metadata with each chunk (default: true)

The available chunking strategies are:
- **auto**: Automatically detect the best strategy based on content analysis
- **code**: Code-focused strategy optimized for code-heavy documents
- **structural**: Structural strategy that follows document headers
- **mixed**: Mixed content strategy for balanced processing of various content types
- **list**: List-focused strategy that preserves list structures
- **table**: Table-focused strategy that handles tables intelligently

**Section sources**
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml#L1-L128)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L1-L178)

## Configuration File Format
The tool uses YAML configuration files to define its behavior. The primary configuration file is `markdown_chunk_tool.yaml` which defines the tool's parameters, labels, and output schema.

### Core Configuration Structure
The configuration file follows a structured format with the following sections:

- **identity**: Contains the tool's name, author, labels in multiple languages, and icon reference
- **description**: Provides human-readable and LLM-focused descriptions of the tool's capabilities
- **parameters**: Defines all configurable parameters with their types, requirements, defaults, and descriptions
- **output_schema**: Specifies the structure of the output using JSON Schema reference
- **extra**: Contains implementation-specific details like the Python source file

### Mapping to ChunkConfig
The YAML configuration parameters map directly to the `ChunkConfig` class in the core library. Key mappings include:

- `max_chunk_size` maps to `ChunkConfig.max_chunk_size`
- `chunk_overlap` maps to `ChunkConfig.overlap_size`
- `strategy` parameter influences the strategy selection in the chunking process
- `include_metadata` controls whether metadata is included in the output

The `ChunkConfig` class provides factory methods for common scenarios:
- `for_code_heavy()`: Optimized for code-heavy documents
- `for_dify_rag()`: Optimized for RAG systems
- `for_fast_processing()`: Optimized for fast processing of large documents
- `for_api_docs()`: Optimized for API documentation

**Section sources**
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml#L1-L128)
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L497-L928)

## Usage Examples
The tool supports various usage scenarios including file processing, standard input/output, and integration with other command-line tools.

### Basic Usage
```yaml
# In Dify workflow configuration
- tool: markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
```

### File Processing
The tool can process Markdown files by reading their content and passing it as the `input_text` parameter. When processing files, the content is read entirely and processed according to the specified configuration.

### Standard Input/Output
The tool can be integrated into pipelines where Markdown content is passed through standard input and processed chunks are output to standard output. This allows for seamless integration with other command-line tools.

### Integration with Other Tools
The tool can be combined with various command-line utilities for enhanced functionality:

```bash
# Process a file and output JSON
cat document.md | python -c "from markdown_chunker import chunk_text; import sys, json; print(json.dumps(chunk_text(sys.stdin.read())))"

# Chain with grep to process specific sections
grep -A 10 '# API Reference' documentation.md | python -c "from markdown_chunker import chunk_text; import sys; [print(chunk.content) for chunk in chunk_text(sys.stdin.read())]"
```

### Common Scenarios
#### Processing API Documentation
```python
from markdown_chunker import ChunkConfig

# Use configuration profile optimized for API documentation
config = ChunkConfig.for_api_docs()
```

#### Code Documentation Processing
```python
from markdown_chunker import ChunkConfig

# Use configuration profile optimized for code documentation
config = ChunkConfig.for_code_docs()
```

#### RAG System Integration
```python
from markdown_chunker import ChunkConfig

# Use configuration profile optimized for Dify RAG systems
config = ChunkConfig.for_dify_rag()
```

**Section sources**
- [examples/basic_usage.py](file://examples/basic_usage.py#L1-L364)
- [examples/dify_integration.py](file://examples/dify_integration.py#L1-L487)
- [README.md](file://README.md#L73-L80)

## Error Messages and Exit Codes
The tool provides comprehensive error handling with descriptive error messages and appropriate exit codes.

### Error Types
The tool handles several types of errors:

- **Validation errors**: Occur when required parameters are missing or invalid
- **Processing errors**: Occur during the chunking process
- **Configuration errors**: Occur when configuration parameters are invalid

### Specific Error Messages
- "Error: input_text is required and cannot be empty" - When no input text is provided
- "Validation error: {detailed message}" - When parameter validation fails
- "Error chunking document: {detailed message}" - When an unexpected error occurs during processing

### Exit Codes
The tool follows standard exit code conventions:
- **0**: Success - The document was successfully chunked
- **1**: Error - An error occurred during processing
- **2**: Usage error - Incorrect usage of the tool

The error handling is implemented in the `_invoke` method of the `MarkdownChunkTool` class, which catches specific exceptions and general exceptions, providing appropriate error messages for each case.

**Section sources**
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L172-L177)

## Shell Scripting Integration
The tool can be easily integrated into shell scripts and automation workflows.

### Automation Scenarios
#### Batch Processing Multiple Files
```bash
#!/bin/bash
# Process all Markdown files in a directory
for file in *.md; do
    echo "Processing $file..."
    # Call the tool with appropriate parameters
    # This would be implemented based on the specific integration method
done
```

#### Continuous Integration Pipeline
```bash
# In a CI/CD pipeline
make test
make lint
make format
make package
make validate-package
```

#### Monitoring and Logging
```bash
# Process document and log processing time
START_TIME=$(date +%s)
python -c "from markdown_chunker import chunk_text; chunk_text('content')"
END_TIME=$(date +%s)
echo "Processing time: $((END_TIME - START_TIME)) seconds"
```

#### Integration with Dify Workflows
```yaml
# Example Dify workflow configuration
- tool: markdown_chunker
  config:
    max_chunk_size: 3072
    chunk_overlap: 150
    strategy: auto
    include_metadata: true
```

The tool's design supports streaming for large documents and provides performance benchmarks to ensure efficient processing of various document sizes.

**Section sources**
- [Makefile](file://Makefile#L1-L136)
- [examples/dify_integration.py](file://examples/dify_integration.py#L1-L487)

## Conclusion
The Advanced Markdown Chunker CLI tool provides a robust solution for intelligent, structure-aware chunking of Markdown documents. With its comprehensive configuration options, multiple chunking strategies, and seamless integration capabilities, it is well-suited for RAG systems and Knowledge Base ingestion pipelines. The tool's error handling, performance optimization, and support for various usage scenarios make it a versatile component in document processing workflows.

**Section sources**
- [README.md](file://README.md#L1-L281)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L1-L178)