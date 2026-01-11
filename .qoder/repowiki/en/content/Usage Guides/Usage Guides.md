# Usage Guides

<cite>
**Referenced Files in This Document**   
- [README.md](file://README.md)
- [docs/usage.md](file://docs/usage.md)
- [docs/quickstart.md](file://docs/quickstart.md)
- [docs/installation.md](file://docs/installation.md)
- [docs/guides/performance.md](file://docs/guides/performance.md)
- [docs/guides/troubleshooting.md](file://docs/guides/troubleshooting.md)
- [docs/guides/migration-to-chunkana.md](file://docs/guides/migration-to-chunkana.md)
- [docs/guides/developer-guide.md](file://docs/guides/developer-guide.md)
- [docs/reference/configuration.md](file://docs/reference/configuration.md)
- [docs/reference/output-format.md](file://docs/reference/output-format.md)
- [provider/markdown_chunker.py](file://provider/markdown_chunker.py)
- [provider/markdown_chunker.yaml](file://provider/markdown_chunker.yaml)
- [main.py](file://main.py)
- [tools/markdown_chunk_tool.py](file://tools/markdown_chunk_tool.py)
- [adapter.py](file://adapter.py)
- [tests/test_migration_adapter.py](file://tests/test_migration_adapter.py)
- [tests/test_migration_regression.py](file://tests/test_migration_regression.py)
- [tests/golden_before_migration/snapshot_index.json](file://tests/golden_before_migration/snapshot_index.json)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Integrating with Dify Workflows](#integrating-with-dify-workflows)
3. [Using as a Python Library in RAG Pipelines](#using-as-a-python-library-in-rag-pipelines)
4. [Batch Processing via CLI](#batch-processing-via-cli)
5. [Performance Optimization Techniques](#performance-optimization-techniques)
6. [Memory Management for Large Documents](#memory-management-for-large-documents)
7. [Troubleshooting Common Issues](#troubleshooting-common-issues)
8. [Testing Procedures](#testing-procedures)
9. [Migration Guidance](#migration-guidance)
10. [Developer Workflows and Customization](#developer-workflows-and-customization)
11. [Conclusion](#conclusion)

## Introduction

This guide provides comprehensive usage scenarios for the dify-markdown-chunker-1 plugin, a powerful tool for intelligent Markdown document chunking designed for Retrieval-Augmented Generation (RAG) systems. The plugin leverages the **chunkana** engine to provide advanced structural awareness, preserving document integrity by keeping code blocks, tables, and lists intact during the chunking process.

The documentation covers practical workflows from basic integration to advanced customization. It details how to use the plugin within Dify workflows, as a standalone Python library, and via command-line interface for batch processing. The guide also includes performance optimization techniques, memory management strategies for large documents, and comprehensive troubleshooting guidance for common issues such as malformed Markdown, unexpected chunk boundaries, and configuration errors.

For developers, the document provides insights into testing procedures using the comprehensive suite in the `tests/` directory, migration guidance from previous versions, and extension points for customization as documented in the developer guide. The content is structured to progress from basic usage to advanced patterns and edge case handling, ensuring users can effectively leverage the full capabilities of the markdown chunker.

**Section sources**
- [README.md](file://README.md#L1-L1469)
- [docs/usage.md](file://docs/usage.md#L1-L450)

## Integrating with Dify Workflows

Integrating the Advanced Markdown Chunker into Dify workflows is straightforward and enables intelligent document processing for RAG systems. The plugin is designed to work seamlessly within Dify's architecture, providing structure-aware chunking that preserves the semantic integrity of Markdown documents.

To install the plugin, download the `.difypkg` file from the GitHub releases page and upload it through the Dify interface under Settings → Plugins → Install Plugin. The plugin requires Dify version 1.9.0 or higher and Python 3.12+. Once installed, it becomes available as a tool in your workflows.

When configuring the plugin in a Dify workflow, several key parameters control the chunking behavior:

- `max_chunk_size`: Sets the maximum size of each chunk in characters (default: 4096)
- `chunk_overlap`: Controls the overlap between consecutive chunks (default: 200)
- `strategy`: Determines the chunking strategy (auto, code_aware, list_aware, structural, fallback)
- `include_metadata`: Embeds metadata in the chunk text for improved retrieval quality
- `enable_hierarchy`: Creates parent-child relationships between chunks for hierarchical navigation

The plugin automatically selects the optimal strategy based on content analysis. For code-heavy documents (≥30% code content), it uses the code-aware strategy; for list-heavy documents (≥40% list content), it employs the list-aware strategy; and for documents with multiple headers, it applies the structural strategy. The fallback strategy is used for simple text content.

A typical workflow configuration for RAG systems looks like this:

```yaml
workflow:
  - node: document_loader
    type: document_loader
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
  
  - node: embedding
    type: embedding
    input: ${markdown_chunker.result}
  
  - node: store_vectors
    type: vector_store
    input: ${embed_chunks.vectors}
```

For hierarchical processing, which is recommended for complex documents, enable the hierarchy mode and filter to leaf chunks only for vector database indexing:

```yaml
- node: hierarchical_chunker
  type: tool
  tool: advanced_markdown_chunker
  config:
    max_chunk_size: 2048
    enable_hierarchy: true
    leaf_only: true
    include_metadata: true
```

The plugin outputs chunks as an array of strings, with metadata embedded in a `<metadata>` block when `include_metadata` is enabled. This format is compatible with Dify's knowledge pipeline UI and provides rich context for embeddings.

**Section sources**
- [README.md](file://README.md#L138-L373)
- [docs/usage.md](file://docs/usage.md#L5-L130)
- [docs/quickstart.md](file://docs/quickstart.md#L42-L65)
- [provider/markdown_chunker.yaml](file://provider/markdown_chunker.yaml#L1-L23)

## Using as a Python Library in RAG Pipelines

The Advanced Markdown Chunker can be used directly as a Python library, providing access to advanced features not available in the Dify plugin UI. This approach is ideal for RAG pipelines that require fine-grained control over chunking parameters and access to enhanced functionality.

To use the library, install the package and import the `MarkdownChunker` class from the `chunkana` module. The library provides a rich API for document chunking with comprehensive configuration options.

Basic usage is straightforward:

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

For advanced scenarios, you can create custom configurations using the `ChunkConfig` class. This allows you to leverage features such as adaptive chunk sizing, streaming processing, code-context binding, and table grouping:

```python
from chunkana import MarkdownChunker, ChunkConfig, AdaptiveSizeConfig

# Enable adaptive sizing based on content complexity
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
```

The library also supports hierarchical chunking, which creates parent-child relationships between chunks for multi-level retrieval:

```python
# Create hierarchical structure
result = chunker.chunk_hierarchical(markdown_text)

# Navigate hierarchy
root = result.get_chunk(result.root_id)
sections = result.get_children(result.root_id)

for section in sections:
    print(f"Section: {section.metadata['header_path']}")
    subsections = result.get_children(section.metadata['chunk_id'])
```

For convenience, the library provides utility functions for chunking text and files directly:

```python
from chunkana import chunk_text, chunk_file

# Chunk text directly
chunks = chunk_text("# My Document\n\nContent here...")

# Chunk from file
chunks = chunk_file("README.md")
```

The library also includes configuration profiles for common use cases:

```python
from chunkana import ChunkConfig

# For code-heavy documents
config = ChunkConfig.for_code_heavy()

# For Dify RAG systems (matches plugin defaults)
config = ChunkConfig.for_dify_rag()

# For search indexing
config = ChunkConfig.for_search_indexing()
```

When using the library in RAG pipelines, you can access detailed chunk metadata that includes content type, header path, line numbers, and other contextual information. This metadata is embedded in the chunk text when `include_metadata` is enabled, providing additional context for embeddings.

**Section sources**
- [README.md](file://README.md#L389-L663)
- [docs/usage.md](file://docs/usage.md#L156-L222)
- [docs/quickstart.md](file://docs/quickstart.md#L67-L120)
- [docs/reference/configuration.md](file://docs/reference/configuration.md#L100-L177)

## Batch Processing via CLI

The Advanced Markdown Chunker supports batch processing of multiple documents through command-line interface (CLI) operations, enabling efficient processing of large document collections. This capability is particularly useful for ingesting knowledge bases, documentation repositories, or large sets of technical documents into RAG systems.

While the plugin itself doesn't provide a dedicated CLI tool, the underlying `chunkana` library can be easily integrated into custom scripts for batch processing. This approach allows for automation of document ingestion workflows and integration with existing data pipelines.

A basic batch processing script would iterate through a directory of Markdown files and process each one:

```python
from chunkana import MarkdownChunker, chunk_file
import os
import glob

# Initialize chunker
chunker = MarkdownChunker()

# Process all Markdown files in a directory
input_dir = "documents/"
output_dir = "chunks/"

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Find all Markdown files
markdown_files = glob.glob(os.path.join(input_dir, "**/*.md"), recursive=True)

for file_path in markdown_files:
    try:
        # Extract relative path for output structure
        rel_path = os.path.relpath(file_path, input_dir)
        output_path = os.path.join(output_dir, rel_path)
        
        # Create output directory for this file
        output_dir_for_file = os.path.dirname(output_path)
        os.makedirs(output_dir_for_file, exist_ok=True)
        
        # Process the file
        chunks = chunk_file(file_path)
        
        # Save chunks to individual files or a single file
        chunk_data = {
            "source_file": file_path,
            "chunks": [
                {
                    "content": chunk.content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
        }
        
        # Save as JSON
        output_json = output_path.replace(".md", "_chunks.json")
        with open(output_json, 'w') as f:
            json.dump(chunk_data, f, indent=2)
            
        print(f"Processed {file_path} -> {output_json}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
```

For processing very large documents or when memory is constrained, the library supports streaming processing:

```python
from chunkana import MarkdownChunker, StreamingConfig

# Configure streaming for memory-constrained environments
streaming_config = StreamingConfig(
    buffer_size=100_000,  # 100KB buffer windows
    max_memory_mb=50      # Strict 50MB memory limit
)

# Process large file in streaming mode
for chunk in chunker.chunk_file_streaming("large_document.md", streaming_config):
    # Process each chunk immediately (e.g., insert to vector DB)
    vector_db.add(chunk.content, chunk.metadata)
    print(f"Processed chunk: {len(chunk.content)} chars")
```

The batch processing workflow can be further enhanced with error handling, progress tracking, and logging:

```python
import logging
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Process files with progress bar
for file_path in tqdm(markdown_files, desc="Processing files"):
    try:
        chunks = chunk_file(file_path)
        # Save chunks...
        logger.info(f"Successfully processed {file_path}")
    except Exception as e:
        logger.error(f"Failed to process {file_path}: {str(e)}")
        continue
```

For integration with Dify workflows, the batch processing script can generate output in the exact format expected by the plugin, ensuring compatibility with existing pipelines.

**Section sources**
- [README.md](file://README.md#L575-L617)
- [docs/quickstart.md](file://docs/quickstart.md#L328-L334)
- [docs/guides/performance.md](file://docs/guides/performance.md#L327-L336)

## Performance Optimization Techniques

The Advanced Markdown Chunker incorporates several performance optimization techniques to ensure efficient processing of Markdown documents while maintaining high-quality chunking. These optimizations are documented in the performance.md guide and are critical for achieving optimal results in production environments.

The architecture is designed for linear scaling with document size, exhibiting predictable performance characteristics. Processing time follows the formula: `Processing Time = coefficient × Document Size (KB) + baseline overhead`, with a coefficient of approximately 0.5-1.0 ms per KB and a baseline overhead of 5-10 ms. This linear relationship (R² > 0.95) ensures no performance cliffs or exponential degradation.

Key performance characteristics include:
- Typical processing speed of 5-15ms per 10KB for medium-sized documents
- Throughput of 500-2000 KB/s depending on content type
- Memory efficiency of <0.2 MB per KB of input (excluding Python base)

The v2 architecture achieves these performance metrics through several optimizations:
- **Single-pass parsing**: The document is parsed once, and the analysis is reused across processing stages
- **Optimized strategies**: Reduced from 6 to 3 high-performance strategies
- **Metadata-only overlap**: Overlap context is stored in metadata fields rather than duplicating text, resulting in minimal overhead
- **Linear scaling**: Consistent performance across document sizes up to 1MB

Configuration choices have minimal impact on performance, with variation typically less than 20% across the 1024-8192 character range. The `max_chunk_size` parameter primarily affects the number of chunks rather than processing time.

The overlap processing overhead is negligible due to the metadata-only approach:
- 0 overlap: Baseline performance
- 50 overlap: <2% overhead
- 100 overlap: <5% overhead
- 200 overlap: <10% overhead
- 400 overlap: <15% overhead

Adaptive sizing, which automatically adjusts chunk size based on content complexity, adds negligible overhead (typically <10% to chunking time) while improving semantic coherence. The complexity scoring is highly optimized, with size calculation overhead of only 0.1%.

For optimal performance, consider these best practices:
- Reuse chunker instances across documents rather than creating new instances
- Use configuration profiles for common use cases
- Validate document size before processing
- Monitor memory usage in production environments

The performance guide also provides recommendations for different content types:
- **Technical Docs (CodeAware)**: Baseline performance
- **GitHub READMEs (CodeAware/Structural)**: Fast processing
- **Changelogs (Structural)**: Fast processing
- **Engineering Blogs (CodeAware)**: Moderate processing
- **Personal Notes (Fallback)**: Fastest processing
- **Debug Logs (CodeAware)**: Moderate processing
- **Mixed Content (CodeAware)**: Moderate processing

**Section sources**
- [docs/guides/performance.md](file://docs/guides/performance.md#L1-L212)

## Memory Management for Large Documents

Effective memory management is crucial when processing large Markdown documents with the Advanced Markdown Chunker. The system provides several mechanisms to handle memory efficiently, particularly for documents exceeding typical sizes.

Memory usage scales linearly with document size, following the formula: `Memory(MB) = coefficient × Size(KB) + base_memory`. The typical coefficient is 0.14-0.18 MB per KB of input, with a base memory of 12-15 MB for the Python runtime and libraries.

For documents of various sizes, peak memory usage is approximately:
- 1 KB: 12-15 MB (base Python overhead dominates)
- 10 KB: 15-18 MB
- 100 KB: 30-40 MB
- 1 MB: 150-200 MB

The performance guide provides projections for larger documents:
- 1 MB: ~500-800 ms processing time, ~150-200 MB memory
- 5 MB: ~2.5-4 s processing time, ~750 MB-1 GB memory
- 10 MB: ~5-8 s processing time, ~1.5-2 GB memory
- 50 MB: ~25-40 s processing time, ~7-10 GB memory
- 100 MB: ~50-80 s processing time, ~14-20 GB memory

For documents larger than 10MB, consider implementing streaming processing to manage memory usage. The chunkana library supports streaming with configurable buffer sizes:

```python
from chunkana import MarkdownChunker, StreamingConfig

# Configure streaming for large files
streaming_config = StreamingConfig(
    buffer_size=100_000,  # 100KB windows
    max_memory_mb=50      # Memory limit
)

# Process large file efficiently
for chunk in chunker.chunk_file_streaming("large_documentation.md", streaming_config):
    # Process each chunk immediately (e.g., insert to vector DB)
    chunk_count += 1
    print(f"Processed chunk {chunk_count}: {len(chunk.content)} chars")
```

Additional memory optimization tips include:
- **Process Large Documents in Batches**: Split very large documents before processing or process sections independently
- **Use Appropriate Configuration**: Smaller `max_chunk_size` reduces memory per chunk; disable overlap if context is not needed (`overlap_size=0`)
- **Monitor Memory on Production**: Set memory limits for document processing and implement timeout/size limits for user-uploaded documents

For production environments, implement size validation before processing:

```python
MAX_SIZE = 1_000_000  # 1MB

if len(document) > MAX_SIZE:
    # Handle large document specially
    # - Split into sections
    # - Use streaming
    # - Return error to user
```

When processing multiple documents, process them sequentially rather than in parallel to avoid memory accumulation. If parallel processing is necessary, limit the number of concurrent operations and monitor memory usage.

The migration to the chunkana engine has improved memory efficiency, with better memory management and lower memory usage compared to previous versions. However, for extremely large documents (50MB+), streaming processing is strongly recommended to prevent memory issues.

**Section sources**
- [docs/guides/performance.md](file://docs/guides/performance.md#L269-L293)

## Troubleshooting Common Issues

This section provides guidance for troubleshooting common issues encountered when using the Advanced Markdown Chunker, including problems with malformed Markdown, unexpected chunk boundaries, and configuration errors.

### Plugin Installation Issues

**Problem**: Plugin not visible in Dify
- **Solution**: Verify Dify version is 1.9.0 or higher, restart Dify application, and check plugin status in Settings → Plugins

**Problem**: Plugin installation fails
- **Solution**: Re-download the `.difypkg` file from GitHub Releases, ensure file integrity, and check Dify logs for detailed error messages

### Configuration Issues

**Problem**: Parameter validation errors
- **Solution**: Ensure parameters are within valid ranges:
  - `max_chunk_size`: 512-16384 characters
  - `chunk_overlap`: 0 to (max_chunk_size * 0.35) due to 35% cap
  - Example of valid configuration:
    ```yaml
    max_chunk_size: 2048
    chunk_overlap: 200  # ~10% of chunk_size
    ```

**Problem**: Overlap not working as expected
- **Solution**: Understand that the plugin caps overlap at 35% of chunk_size. For full control over overlap, use the chunkana library directly instead of the plugin UI.

### Output Issues

**Problem**: Chunks too large or small
- **Solution**: Adjust `max_chunk_size` or use adaptive sizing. Remember that atomic blocks (code, tables) are preserved intact, which may result in larger chunks than the specified maximum.

**Problem**: Missing metadata
- **Solution**: Ensure `include_metadata` is set to `true` in the configuration. Verify that the metadata format is correct with the `<metadata>` block containing JSON.

**Problem**: Hierarchical mode not working as expected
- **Solution**: Ensure `enable_hierarchy` is set to `true`. Understand the different chunk types:
  - **Root**: Document-level chunk (excluded by default)
  - **Intermediate**: Section headers with children
  - **Leaf**: Content chunks (recommended for indexing)

### Processing Errors

**Problem**: "Module not found: chunkana" or import errors
- **Solution**: Ensure you are using plugin version 2.1.5 or later (chunkana-powered). If needed, manually install the dependency: `pip install chunkana>=0.1.0`.

**Problem**: Out of memory errors with large documents
- **Solution**: Reduce chunk size, use streaming processing (available in chunkana direct), or disable advanced features like hierarchy and debug mode.

**Problem**: Processing timeout
- **Solution**: Use a simpler strategy (e.g., `fallback`), reduce document size by splitting large documents, or optimize configuration with smaller chunks and simpler strategies.

### Content-Specific Issues

**Problem**: Code blocks split incorrectly
- **Solution**: Force the code-aware strategy and increase `max_chunk_size`. For enhanced code handling, use the chunkana library directly with code-context binding enabled.

**Problem**: Lists split inappropriately
- **Solution**: Force the list-aware strategy. For more control over list thresholds, use the chunkana library directly.

**Problem**: Tables not preserved
- **Solution**: Use the code-aware strategy or enable table grouping in the chunkana library.

### Migration Issues

**Problem**: Different chunking results after v2.1.5 migration
- **Solution**: Understand that the migration to chunkana includes improvements like better small-chunk merging and more consistent metadata structure. These changes improve chunk quality while maintaining backward compatibility.

**Problem**: Old documentation or examples not working
- **Solution**: Update import statements to use `from chunkana import MarkdownChunker` instead of legacy imports. For Dify workflows, use the plugin tool interface without code changes.

For detailed diagnostic information when reporting issues, include:
- Plugin version (check in Dify Settings → Plugins)
- Configuration parameters
- Sample input that reproduces the issue
- Expected vs. actual output

Enable debug mode for detailed information:
```yaml
config:
  enable_hierarchy: true
  debug: true  # Shows all chunk types
```

**Section sources**
- [docs/guides/troubleshooting.md](file://docs/guides/troubleshooting.md#L1-L523)

## Testing Procedures

The Advanced Markdown Chunker includes a comprehensive testing suite with over 470 tests to ensure reliability and correctness. The testing procedures are documented in the testing-guide.md and include unit tests, integration tests, property-based testing, and regression testing.

The test suite is organized into several categories:
- **Unit Tests**: Component-level testing in the `tests/parser/` and `tests/chunker/` directories
- **Integration Tests**: End-to-end workflows in the `tests/integration/` directory
- **Property Tests**: Universal properties tested with Hypothesis for formal correctness guarantees
- **Regression Tests**: Prevention of known bugs in the `tests/regression/` directory
- **Performance Tests**: Verification of performance characteristics

To run the tests, use the provided Makefile commands:
```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run with coverage
make test-coverage

# Run quick tests only
make test-quick
```

The testing suite includes specific tests for the migration adapter that ensures backward compatibility with previous versions. The `test_migration_adapter.py` file contains tests for the adapter's functionality:

```python
class TestMigrationAdapter:
    """Test migration adapter functionality."""
    
    def test_build_chunker_config_defaults(self):
        """Test build_chunker_config with default parameters."""
        config = self.adapter.build_chunker_config()
        assert isinstance(config, ChunkerConfig)
        assert config.max_chunk_size == 4096
        assert config.overlap_size == 200
        assert config.strategy_override is None
    
    def test_parse_tool_flags_custom(self):
        """Test parse_tool_flags with custom values."""
        include_metadata, enable_hierarchy, debug, leaf_only = (
            self.adapter.parse_tool_flags(
                include_metadata=False,
                enable_hierarchy=True,
                debug=True,
                leaf_only=True,
            )
        )
        assert include_metadata is False
        assert enable_hierarchy is True
        assert debug is True
        assert leaf_only is True
```

Regression testing ensures that the migration to the chunkana engine preserves exact behavior. The `test_migration_regression.py` file contains tests that compare current output with golden snapshots from before the migration:

```python
class TestMigrationRegression:
    """Test that migration preserves exact behavior."""
    
    @pytest.mark.parametrize("snapshot_id", [...])
    def test_snapshot_compatibility(self, snapshot_id: str):
        """Test that adapter produces same output as pre-migration snapshot."""
        # Load snapshot
        snapshot_data = self.load_snapshot(snapshot_id)
        fixture_name = snapshot_data["fixture_name"]
        parameters = snapshot_data["parameters"]
        expected_output = snapshot_data["output"]
        
        # Load fixture and run through adapter
        fixture_content = self.load_fixture(fixture_name)
        actual_output = self.run_adapter_chunking(fixture_content, parameters)
        
        # Compare outputs
        assert len(actual_output) == len(expected_output)
```

The golden snapshots are stored in the `tests/golden_before_migration/` directory and include 228 snapshots across 12 fixtures with 19 parameter combinations. Each snapshot captures the exact output for a specific input and configuration, ensuring backward compatibility.

The testing suite also includes property-based testing with Hypothesis, which provides formal correctness guarantees by testing universal properties across a wide range of inputs. This approach helps identify edge cases and ensures robustness.

For performance testing, the suite includes benchmarks that measure processing speed, memory usage, and scalability. These tests help detect performance regressions and ensure the system meets its performance targets.

**Section sources**
- [docs/guides/testing-guide.md](file://docs/guides/testing-guide.md#L1-L32)
- [tests/test_migration_adapter.py](file://tests/test_migration_adapter.py#L1-L189)
- [tests/test_migration_regression.py](file://tests/test_migration_regression.py#L1-L205)
- [tests/golden_before_migration/snapshot_index.json](file://tests/golden_before_migration/snapshot_index.json#L1-L800)

## Migration Guidance

The migration from previous versions of the Advanced Markdown Chunker to the current chunkana-powered version (2.1.5) is designed to be seamless with 100% backward compatibility. This section provides guidance for users upgrading from earlier versions.

The key change in version 2.1.5 is the migration from embedded chunking code to the external **chunkana** library as the core chunking engine. This architectural change brings several benefits while maintaining compatibility with existing workflows.

### Migration Timeline
- **v2.1.4 and earlier**: Legacy version with embedded `markdown_chunker_v2` code
- **v2.1.5**: Current version powered by chunkana with compatibility adapter
- **Future versions**: Planned enhancements with direct chunkana integration

### Behavioral Differences
Several improvements were introduced in the migration:
- **Small-chunk merging**: Chunkana intelligently merges small chunks with adjacent content while respecting structural boundaries
- **include_metadata semantics**: More consistent metadata structure and reliable overlap handling
- **Hierarchy-only meaning of leaf_only**: In hierarchical mode, `leaf_only=true` reliably filters to content chunks only
- **Debug visibility behavior**: Enhanced debugging capabilities with comprehensive chunk type visibility

### Compatibility Guarantees
The migration maintains full compatibility:
- **API Compatibility**: All existing Dify workflows continue to work without changes
- **Parameter Compatibility**: All tool parameters work exactly as before
- **Output Format**: Chunk structure and metadata format remain unchanged

### Getting Help with Migration
If you encounter issues after the migration:
1. **Check Version**: Ensure you're using v2.1.5 or later
2. **Review Logs**: Check Dify logs for any error messages
3. **Test with Simple Document**: Verify basic functionality works
4. **Report Issues**: Use GitHub Issues for bug reports

### Advanced Usage
For users who need features not exposed in the plugin UI, direct access to chunkana is available:

```python
from chunkana import MarkdownChunker, ChunkConfig

# Advanced configuration not available in plugin
config = ChunkConfig(
    use_adaptive_sizing=True,
    enable_streaming=True,
    custom_strategy_weights={'code': 0.4, 'list': 0.3}
)

chunker = MarkdownChunker(config)
result = chunker.chunk(markdown_text)
```

The migration enables future enhancements while maintaining backward compatibility:
- **Streaming Processing**: Handle very large documents efficiently
- **Advanced Configuration**: Expose more chunkana features through plugin UI
- **Custom Strategies**: Support for user-defined chunking strategies
- **Performance Monitoring**: Built-in performance metrics and optimization

For detailed migration information, refer to the complete migration guide at [migration-to-chunkana.md](file://docs/guides/migration-to-chunkana.md).

**Section sources**
- [docs/guides/migration-to-chunkana.md](file://docs/guides/migration-to-chunkana.md#L1-L212)

## Developer Workflows and Customization

The Advanced Markdown Chunker provides several extension points and customization patterns for developers, as documented in the developer-guide.md. These capabilities enable advanced users to extend the functionality beyond the standard plugin interface.

### Architecture Overview
The system follows a two-stage architecture:
1. **Stage 1: Analysis** - Parse document structure and extract metadata
2. **Stage 2: Chunking** - Create semantically meaningful chunks

The architecture includes a strategy selector that automatically chooses the optimal chunking strategy based on content analysis, with six available strategies: CodeStrategy, StructuralStrategy, MixedStrategy, ListStrategy, TableStrategy, and SentencesStrategy.

### Adding a New Strategy
Developers can extend the chunker by adding custom strategies. To create a new strategy:
1. Create a strategy class that inherits from `BaseStrategy`
2. Implement the `can_handle` method to determine when the strategy should be used
3. Implement the `apply` method to define the chunking logic
4. Register the strategy in the `MarkdownChunker.__init__()` method
5. Add tests and update documentation

Example of a custom strategy:
```python
class MyStrategy(BaseStrategy):
    def __init__(self):
        super().__init__()
        self.name = "my_strategy"
        self.priority = 50
    
    def can_handle(self, analysis, config: ChunkConfig) -> bool:
        return (analysis.some_metric > config.some_threshold 
                and analysis.some_count >= 3)
    
    def apply(self, text: str, chunking_result: ChunkingResult, 
              config: ChunkConfig) -> List[Chunk]:
        # Custom chunking logic
        pass
```

### Development Setup
The development environment requires Python 3.8+, pip or poetry, and git. Install in development mode:
```bash
git clone https://github.com/asukhodko/dify-markdown-chunker.git
cd dify-markdown-chunker
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Coding Standards
The project follows these standards:
- PEP 8 style guide
- Black for formatting (line length: 88)
- Ruff for linting
- Google-style docstrings
- Type hints for all public APIs

### Performance Profiling
The library includes built-in performance monitoring:
```python
chunker = MarkdownChunker(enable_performance_monitoring=True)
result = chunker.chunk(content)

# Get stats
stats = chunker.get_performance_stats()
print(f"Processing time: {stats['chunk']['avg_time']:.3f}s")
print(f"Memory usage: {stats['memory']['peak_mb']:.1f}MB")
```

### Contribution Guidelines
The project welcomes contributions following a structured process:
1. Fork and clone the repository
2. Create a feature branch
3. Make changes with tests and documentation
4. Run linter and formatter
5. Test thoroughly
6. Commit with conventional commit messages
7. Push and create a pull request

The release process follows semantic versioning with a comprehensive checklist including version updates, full test suite execution, documentation updates, and publishing to PyPI.

For debugging, the system provides detailed logging at different levels:
- **DEBUG**: Detailed information for diagnosing problems
- **INFO**: Confirmation that things are working
- **WARNING**: Indication of potential issues
- **ERROR**: Serious problems

**Section sources**
- [docs/guides/developer-guide.md](file://docs/guides/developer-guide.md#L1-L937)

## Conclusion

The Advanced Markdown Chunker for Dify provides a comprehensive solution for intelligent Markdown document chunking, with applications in RAG systems, knowledge management, and document processing workflows. This guide has covered the essential usage scenarios, from basic integration with Dify workflows to advanced customization patterns for developers.

Key takeaways include:
- The plugin seamlessly integrates with Dify workflows, providing structure-aware chunking that preserves document integrity
- As a Python library, it offers advanced features like adaptive sizing, streaming processing, and hierarchical chunking
- Batch processing via custom scripts enables automation of document ingestion pipelines
- Performance optimization techniques ensure efficient processing with linear scaling characteristics
- Memory management strategies, particularly streaming processing, allow handling of large documents
- Comprehensive troubleshooting guidance addresses common issues with configuration, output, and content-specific problems
- Testing procedures with golden snapshots ensure reliability and backward compatibility
- Migration guidance facilitates smooth upgrades from previous versions
- Developer workflows provide extension points for customization and contribution

The migration to the chunkana engine represents a significant improvement in architecture and capabilities while maintaining complete backward compatibility. Users benefit from improved performance, enhanced features, and better maintainability without any required changes to existing workflows.

For ongoing support and updates, refer to the comprehensive documentation in the repository and the GitHub repository for issue reporting and feature requests.

**Section sources**
- [README.md](file://README.md#L209-L210)
- [docs/guides/migration-to-chunkana.md](file://docs/guides/migration-to-chunkana.md#L208-L212)