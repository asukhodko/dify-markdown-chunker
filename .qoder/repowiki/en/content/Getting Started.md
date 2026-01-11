# Getting Started

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [Makefile](file://Makefile)
- [manifest.yaml](file://manifest.yaml)
- [provider/markdown_chunker.py](file://provider/markdown_chunker.py)
- [provider/markdown_chunker.yaml](file://provider/markdown_chunker.yaml)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py)
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml)
- [main.py](file://main.py)
- [adapter.py](file://adapter.py)
</cite>

## Table of Contents
1. [Installation](#installation)
2. [Usage Modes](#usage-modes)
3. [Configuration Basics](#configuration-basics)
4. [Execution Flow](#execution-flow)
5. [Common Initial Issues](#common-initial-issues)

## Installation

The dify-markdown-chunker-1 tool can be installed through package manager or direct cloning. The installation process requires Python 3.12 or higher and uses standard Python packaging tools.

To install via direct cloning:
```bash
# Clone the repository
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

The requirements.txt file specifies the core dependencies including dify_plugin>=0.7.0, chunkana>=0.1.6, and various Markdown processing libraries. Development dependencies like black, isort, flake8, and mypy are optional and can be installed separately for code quality checks.

For Dify plugin installation, download the .difypkg file from Releases and upload it through Dify's plugin interface under Settings → Plugins → Install Plugin. The plugin requires Dify version 1.9.0 or higher to function properly.

The Makefile provides convenient commands for development tasks. Key commands include:
- `make setup`: Creates virtual environment and installs all dependencies
- `make install`: Installs dependencies (requires existing venv)
- `make install-dev`: Installs with development tools
- `make test`: Runs all tests
- `make lint`: Runs linter on adapter and tools
- `make format`: Formats code with black
- `make clean`: Cleans temporary files
- `make clean-all`: Cleans everything including venv

**Section sources**
- [README.md](file://README.md#L138-L168)
- [requirements.txt](file://requirements.txt#L1-L22)
- [Makefile](file://Makefile#L1-L196)

## Usage Modes

The dify-markdown-chunker-1 tool can be used in three primary modes: as a Dify plugin, as a Python library, and via command-line interface.

### As a Dify Plugin

The tool is designed to integrate with Dify workflows through the manifest.yaml configuration. The plugin is defined in manifest.yaml with the entrypoint pointing to main.py. The plugin structure follows Dify's plugin architecture with provider/markdown_chunker.yaml defining the tool provider and tools/markdown_chunk_tool.yaml defining the specific tool.

To use in a Dify workflow:
```yaml
- node: chunk_markdown
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    strategy: auto
    chunk_overlap: 100
    include_metadata: true
```

The plugin parameters are defined in tools/markdown_chunk_tool.yaml and include input_text (required), max_chunk_size, chunk_overlap, strategy, include_metadata, enable_hierarchy, debug, and leaf_only. These parameters map to the underlying chunkana library configuration through the MigrationAdapter in adapter.py.

### As a Python Library

The tool can be used directly as a Python library by importing the chunkana functions. The adapter.py file provides a compatibility layer that exposes the chunkana library through a familiar interface.

Basic usage:
```python
from chunkana import MarkdownChunker

# Simple chunking
chunker = MarkdownChunker()
chunks = chunker.chunk("# Hello\n\nWorld")

# With analysis
result = chunker.chunk("# Hello\n\nWorld", include_analysis=True)
print(f"Strategy: {result.strategy_used}")
print(f"Chunks: {len(result.chunks)}")
```

Convenience functions are also available:
```python
from chunkana import chunk_text, chunk_file

# Chunk text directly
chunks = chunk_text("# My Document\n\nContent here...")

# Chunk from file
chunks = chunk_file("README.md")
```

### Via Command-Line Interface

The tool can be used through the command-line interface via tools/markdown_chunk_tool.py. This script implements the Tool class for the Advanced Markdown Chunker plugin and processes input through the MigrationAdapter.

The command-line tool accepts parameters through the tool_parameters dictionary and yields results as ToolInvokeMessage objects. The processing pipeline includes input validation, parameter mapping to chunkana configuration, chunking through the adapter, and output formatting.

**Section sources**
- [manifest.yaml](file://manifest.yaml#L1-L49)
- [provider/markdown_chunker.yaml](file://provider/markdown_chunker.yaml#L1-L23)
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml#L1-L178)
- [adapter.py](file://adapter.py#L1-L352)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L1-L126)

## Configuration Basics

The tool's behavior is controlled through configuration parameters that can be set at different levels. The default configuration is defined in the tool parameters with max_chunk_size defaulting to 4096 characters, chunk_overlap to 200 characters, strategy to "auto", and include_metadata to true.

The configuration is managed through the MigrationAdapter class in adapter.py which maps plugin parameters to chunkana library configuration. Key configuration options include:

- **max_chunk_size**: Maximum size of each chunk in characters
- **chunk_overlap**: Characters to overlap between chunks
- **strategy**: Chunking strategy (auto, code_aware, list_aware, structural, fallback)
- **include_metadata**: Whether to embed metadata in chunk text
- **enable_hierarchy**: Whether to create parent-child relationships between chunks
- **debug**: Debug mode to include all chunks
- **leaf_only**: Whether to return only leaf chunks in hierarchical mode

The tool uses a two-stage processing pipeline: chunking (boundary-invariant) and rendering (formatting). This ensures that chunk boundaries do not depend on include_metadata, maintaining consistency across different output formats.

Configuration profiles are available for different use cases:
- `for_code_heavy()`: For code-heavy documents
- `for_dify_rag()`: For Dify RAG systems
- `for_search_indexing()`: For search indexing

**Section sources**
- [tools/markdown_chunk_tool.yaml](file://tools/markdown_chunk_tool.yaml#L38-L167)
- [adapter.py](file://adapter.py#L94-L119)
- [README.md](file://README.md#L207-L225)

## Execution Flow

The execution flow of the dify-markdown-chunker-1 tool begins with the main.py entry point, which is specified in manifest.yaml as the entrypoint. The main.py file creates a Plugin instance with a 300-second timeout and runs it when executed directly.

The execution flow proceeds as follows:
1. main.py creates a Plugin instance and calls its run() method
2. The plugin loads the tool provider from provider/markdown_chunker.py
3. The tool provider manages the Advanced Markdown Chunker tool
4. When the tool is invoked, tools/markdown_chunk_tool.py processes the request
5. The tool extracts parameters and creates a MigrationAdapter instance
6. The adapter builds chunker configuration and runs chunking
7. Results are formatted and returned through the plugin interface

The MigrationAdapter in adapter.py serves as a compatibility layer between the plugin interface and the chunkana library. It handles parameter mapping, input validation, and output formatting. The adapter uses a two-stage processing pipeline: chunking (which is boundary-invariant) and rendering (which depends on include_metadata).

The chunking process preserves document structure including headers, code blocks, tables, and lists. The tool automatically selects the optimal strategy based on content analysis, with four available strategies: Code-Aware, List-Aware, Structural, and Fallback.

**Section sources**
- [main.py](file://main.py#L1-L38)
- [provider/markdown_chunker.py](file://provider/markdown_chunker.py#L1-L36)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L1-L126)
- [adapter.py](file://adapter.py#L43-L352)

## Common Initial Issues

Common initial issues when using the dify-markdown-chunker-1 tool typically relate to environment setup, dependency resolution, and basic invocation patterns.

### Environment Setup

Ensure Python 3.12 or higher is installed and a virtual environment is created. The Makefile provides a convenient setup command:
```bash
make setup
```

This creates a virtual environment and installs all dependencies. Verify the installation by running tests:
```bash
make test
```

### Dependency Resolution

The tool depends on several packages specified in requirements.txt. If encountering dependency issues, ensure pip is up to date:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

For development, install additional tools:
```bash
make install-dev
```

### Basic Invocation Patterns

When using as a Dify plugin, ensure the input_text parameter is provided and not empty. The tool will return an error if input_text is missing or empty.

When using as a Python library, import from chunkana and use the provided functions:
```python
from chunkana import chunk_text, chunk_file
chunks = chunk_text("Your markdown content")
```

For command-line usage, ensure the correct parameters are passed to the tool. The tool parameters are validated before processing, and appropriate error messages are returned for invalid inputs.

Common configuration mistakes include:
- Setting chunk_overlap too high, which can lead to excessive context duplication
- Using inappropriate chunking strategies for the content type
- Not considering the impact of include_metadata on downstream processing
- Overlooking the hierarchical chunking options when they would be beneficial

**Section sources**
- [test_entry_point.py](file://tests/test_entry_point.py#L1-L240)
- [test_manifest.py](file://tests/test_manifest.py#L1-L185)
- [README.md](file://README.md#L152-L168)
- [Makefile](file://Makefile#L1-L196)