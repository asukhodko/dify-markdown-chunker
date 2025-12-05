# Getting Started

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [requirements.txt](file://requirements.txt)
- [installation.md](file://docs/installation.md)
- [quickstart.md](file://docs/quickstart.md)
- [usage.md](file://docs/usage.md)
- [basic_usage.py](file://examples/basic_usage.py)
- [manifest.yaml](file://manifest.yaml)
- [main.py](file://main.py)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py)
</cite>

## Table of Contents
1. [Installation](#installation)
2. [Environment Setup](#environment-setup)
3. [Quick Start Example](#quick-start-example)
4. [Configuration and ChunkingResult](#configuration-and-chunkingresult)
5. [Common Setup Issues and Troubleshooting](#common-setup-issues-and-troubleshooting)

## Installation

The dify-markdown-chunker.qoder library can be installed through multiple methods depending on your use case. The primary installation methods are via pip for Python library usage or direct repository installation for development and Dify plugin integration.

For Python library installation, you can install directly from the repository:

```bash
# Install from source
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker
pip install -e .
```

For Dify plugin installation, download the `.difypkg` file from the [Releases](https://github.com/asukhodko/dify-markdown-chunker/releases) page and upload it through the Dify interface under Settings → Plugins → Install Plugin. This method is recommended for users who want to integrate the chunker into Dify workflows without managing Python dependencies directly.

**Section sources**
- [README.md](file://README.md#L75-L87)
- [installation.md](file://docs/installation.md#L55-L60)

## Environment Setup

Before using the dify-markdown-chunker.qoder library, ensure your environment meets the requirements. The library requires Python 3.12 or higher, as specified in the manifest.yaml file. This version requirement ensures compatibility with the latest language features and dependency requirements.

After cloning the repository, create a virtual environment to isolate the dependencies:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac: venv\Scripts\activate on Windows
```

Install the required dependencies using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

The requirements.txt file contains all necessary dependencies including `dify_plugin==0.5.0b15`, `markdown-it-py>=3.0.0`, `pydantic>=2.0.0`, and other core packages needed for the chunker to function properly. Development dependencies can be installed with `pip install -e ".[dev]"` for contributors who need testing and code quality tools.

**Section sources**
- [README.md](file://README.md#L95-L103)
- [requirements.txt](file://requirements.txt#L1-L21)
- [manifest.yaml](file://manifest.yaml#L38)

## Quick Start Example

Let's walk through a complete example that demonstrates basic chunking of a simple Markdown document. This example shows the input, configuration, and expected output when using the library.

```python
from markdown_chunker import MarkdownChunker

# Simple chunking with default configuration
chunker = MarkdownChunker()
markdown = """# My Document

This is an introduction paragraph with some text content.

## Section 1

Here's some content in section 1.

```python
def hello():
    return "world"
```

## Section 2

More content in section 2."""

chunks = chunker.chunk(markdown)
```

This example demonstrates the core API usage pattern from examples/basic_usage.py. The MarkdownChunker class is instantiated without any configuration, using the default settings. The `chunk()` method processes the input Markdown text and returns a list of chunks. Each chunk preserves structural elements like headers and code blocks, ensuring that code blocks remain intact as atomic units and header hierarchy is maintained.

For more detailed analysis, you can use the `chunk_with_analysis()` method which returns a ChunkingResult object containing additional metadata about the chunking process, including the strategy used, processing time, and any fallbacks that were applied.

**Section sources**
- [basic_usage.py](file://examples/basic_usage.py#L14-L48)
- [README.md](file://README.md#L181-L192)

## Configuration and ChunkingResult

The minimal configuration needed to run the chunker consists of creating a MarkdownChunker instance with optional ChunkConfig parameters. The default configuration works for most use cases, but you can customize behavior through the ChunkConfig class.

The ChunkingResult output provides comprehensive information about the chunking process. When using `include_analysis=True`, the result includes:

- `strategy_used`: The chunking strategy that was applied
- `processing_time`: Time taken to process the document
- `fallback_used`: Whether fallback strategies were needed
- `chunks`: List of generated chunks with metadata
- Various statistics like total characters, line count, and complexity score

Each chunk in the result contains properties such as content, start_line, end_line, size, content_type, and strategy. The metadata includes additional context-specific information like programming language for code blocks, list types, or table dimensions. This rich metadata helps in downstream processing, especially in RAG systems where context preservation is critical.

Configuration profiles are available for common use cases:
- `ChunkConfig.for_code_heavy()` - Optimized for code documentation
- `ChunkConfig.for_dify_rag()` - Tailored for Dify RAG systems
- `ChunkConfig.for_search_indexing()` - Designed for search applications

**Section sources**
- [basic_usage.py](file://examples/basic_usage.py#L50-L93)
- [README.md](file://README.md#L370-L388)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py#L130-L137)

## Common Setup Issues and Troubleshooting

New users may encounter several common setup issues when getting started with the dify-markdown-chunker.qoder library. Understanding these issues and their solutions can help ensure a smooth onboarding experience.

One frequent issue is the "ModuleNotFoundError: No module named 'markdown_chunker'" error. This typically occurs when the virtual environment is not activated or dependencies are not properly installed. Ensure you've activated your virtual environment with `source venv/bin/activate` (or `venv\Scripts\activate` on Windows) and installed dependencies with `pip install -r requirements.txt`.

Another common problem is import errors due to incorrect import statements. Use the correct imports from the markdown_chunker package:
```python
# Correct
from markdown_chunker import MarkdownChunker

# Incorrect
from stage1 import process_markdown
```

For Dify plugin users, "Plugin package is invalid" errors may occur if the wrong `.difypkg` file is downloaded or if there's a version compatibility issue with Dify. Ensure you're using Dify version 1.9.0 or higher, as specified in the manifest.yaml file.

When using the library programmatically, configuration issues can arise from incorrect parameter usage. Always use the ChunkConfig class to set parameters rather than passing them directly to the chunker. For example:
```python
from markdown_chunker import ChunkConfig
config = ChunkConfig(max_chunk_size=2048)
chunker = MarkdownChunker(config)
```

For development environments, test failures may occur if development dependencies are missing. Install them with `pip install -e ".[dev]"` and run tests with `make test` to verify your setup.

**Section sources**
- [installation.md](file://docs/installation.md#L128-L158)
- [quickstart.md](file://docs/quickstart.md#L244-L268)
- [test_dependencies.py](file://tests/test_dependencies.py#L15-L94)
- [test_entry_point.py](file://tests/test_entry_point.py#L15-L240)