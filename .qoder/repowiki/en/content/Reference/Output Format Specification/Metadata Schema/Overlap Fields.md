# Overlap Fields

<cite>
**Referenced Files in This Document**   
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py)
- [types.py](file://markdown_chunker_legacy/chunker/types.py)
- [core.py](file://markdown_chunker_legacy/chunker/core.py)
- [metadata_enricher.py](file://markdown_chunker_legacy/chunker/components/metadata_enricher.py)
- [block_overlap_manager.py](file://markdown_chunker_legacy/chunker/block_overlap_manager.py)
- [test_overlap_properties.py](file://tests/chunker/test_overlap_properties.py)
- [test_components/test_overlap_metadata_mode.py](file://tests/chunker/test_components/test_overlap_metadata_mode.py)
- [test_components/test_overlap_new_model.py](file://tests/chunker/test_components/test_overlap_new_model.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Overlap Metadata Fields](#overlap-metadata-fields)
3. [Configuration Parameters](#configuration-parameters)
4. [Overlap Processing Workflow](#overlap-processing-workflow)
5. [Downstream System Benefits](#downstream-system-benefits)
6. [Performance Considerations](#performance-considerations)
7. [Examples and Usage](#examples-and-usage)
8. [Conclusion](#conclusion)

## Introduction

The overlap metadata fields play a crucial role in maintaining context continuity when chunking Markdown documents for retrieval-augmented generation (RAG) applications. When overlap is enabled in the chunking process, two key metadata fields are used to indicate and describe the overlapping content between adjacent chunks: `has_overlap` and `overlap_type`. These fields help downstream systems handle duplicate content and maintain context continuity across chunk boundaries.

The chunking system provides two modes for handling overlap: legacy mode, where overlap content is merged directly into the chunk content, and metadata mode, where overlap context is stored in metadata fields while keeping the core content clean. This documentation explains how these fields are implemented, configured, and used throughout the chunking pipeline.

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L1-L927)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L1-L1080)

## Overlap Metadata Fields

### has_overlap Field

The `has_overlap` field is a boolean metadata flag that indicates whether a chunk contains overlapping content from adjacent chunks. This field is set to `True` when a chunk has either preceding or succeeding context from neighboring chunks, and `False` otherwise.

In the implementation, this field is added to chunk metadata during the overlap processing phase. For example, in the block-based overlap manager, the field is explicitly set when overlap content is applied:

```python
new_metadata["has_overlap"] = True
```

The `has_overlap` field serves as a quick indicator for downstream systems to identify chunks that contain overlapping content. This is particularly useful for RAG applications where duplicate content detection and context preservation are critical. Systems can use this flag to implement deduplication strategies or to give appropriate weighting to overlapping content during retrieval and generation.

**Section sources**
- [block_overlap_manager.py](file://markdown_chunker_legacy/chunker/block_overlap_manager.py#L250)
- [metadata_enricher.py](file://markdown_chunker_legacy/chunker/components/metadata_enricher.py#L632)
- [test_overlap_properties.py](file://tests/chunker/test_overlap_properties.py#L192)

### overlap_type Field

The `overlap_type` field specifies the nature of the overlap applied to a chunk. It indicates whether the overlap is a prefix (content from the previous chunk) or a suffix (content from the next chunk). In the current implementation, this field is used to distinguish between different types of overlap, such as "prefix" for content taken from the beginning of the next chunk.

The overlap type is determined during the overlap extraction process. When context is extracted from neighboring chunks, the system identifies whether it's taking content from the end of the previous chunk (creating a suffix overlap) or from the beginning of the next chunk (creating a prefix overlap). This information is then stored in the metadata:

```python
new_metadata["overlap_type"] = "block_based"
```

For downstream RAG applications, knowing the overlap type helps in understanding the context flow between chunks. Prefix overlaps provide forward context, helping to anticipate what comes next in the document, while suffix overlaps provide backward context, helping to understand what preceded the current content. This distinction can be valuable for maintaining narrative continuity and improving the coherence of generated responses.

**Section sources**
- [block_overlap_manager.py](file://markdown_chunker_legacy/chunker/block_overlap_manager.py#L252)
- [test_overlap_properties.py](file://tests/chunker/test_overlap_properties.py#L217)

## Configuration Parameters

### Enabling Overlap

Overlap behavior is controlled through configuration parameters in the `ChunkConfig` class. The primary parameter is `enable_overlap`, which is a boolean flag that enables or disables the overlap feature globally. By default, this is set to `True` to ensure context continuity in most use cases.

```python
enable_overlap: bool = True
```

When `enable_overlap` is set to `False`, no overlap processing is performed, and neither the `has_overlap` nor `overlap_type` fields are added to chunk metadata. This can be useful in scenarios where strict content separation is required or when downstream systems handle context continuity independently.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L523)

### Overlap Size Configuration

The size of the overlap is controlled by two complementary parameters: `overlap_size` and `overlap_percentage`. The `overlap_size` parameter specifies the fixed size of overlap in characters, while `overlap_percentage` defines the overlap as a percentage of the chunk size.

```python
overlap_size: int = 200
overlap_percentage: float = 0.1  # 10% overlap
```

The system calculates the effective overlap size by prioritizing the fixed size when both parameters are set. If only the percentage is specified, the system uses the average chunk size to determine the actual overlap size. This flexible configuration allows users to adapt the overlap behavior to different document types and use cases.

An important constraint is that the overlap size is limited to a maximum of 40% of the source chunk size to prevent excessive duplication. This is implemented in the overlap manager:

```python
max_overlap = max(50, int(len(content) * 0.40))
actual_target = min(target_size, max_overlap)
```

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L583)
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L180)

### Block-Based Overlap

The chunking system supports block-based overlap through the `block_based_overlap` configuration parameter. When enabled, overlap boundaries align with content block boundaries (such as paragraphs, headers, lists, and code blocks) rather than being character-based.

```python
block_based_overlap: bool = True
```

This ensures that overlap respects the structural integrity of the document, preventing partial blocks from being included in the overlap. The block-based approach is particularly important for maintaining the coherence of code blocks, tables, and other structured content that should not be split across chunk boundaries.

When block-based overlap is enabled, the system uses a different overlap mechanism that operates at the block level rather than the character level, as indicated in the core processing logic:

```python
if self.config.enable_overlap and chunks and not getattr(self.config, "block_based_overlap", False):
    chunks = self._overlap_manager.apply_overlap(chunks, include_metadata)
```

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L633)
- [core.py](file://markdown_chunker_legacy/chunker/core.py#L291)

## Overlap Processing Workflow

### Processing Pipeline

The overlap processing workflow is integrated into the main chunking pipeline through the `OverlapManager` class. The process begins after the initial chunking is complete and proceeds through several stages:

1. **Validation**: The system first checks if overlap is enabled and if there are multiple chunks to process.
2. **Size Calculation**: The effective overlap size is calculated based on configuration parameters.
3. **Context Extraction**: Context is extracted from neighboring chunks using block-aligned methods.
4. **Mode Application**: Depending on the `include_metadata` parameter, context is either stored in metadata or merged into content.

The workflow is implemented in the `apply_overlap` method of the `OverlapManager` class:

```python
def apply_overlap(self, chunks: List[Chunk], include_metadata: bool = False) -> List[Chunk]:
    if not chunks or len(chunks) < 2:
        return chunks
        
    if not self.config.enable_overlap:
        return chunks
        
    effective_overlap = self._calculate_effective_overlap(chunks)
    # ... processing logic
```

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L62)

### Metadata Mode vs. Legacy Mode

The chunking system supports two distinct modes for handling overlap, controlled by the `include_metadata` parameter:

**Metadata Mode** (`include_metadata=True`): In this mode, overlap context is stored in metadata fields while keeping the original content unchanged. The `previous_content` and `next_content` fields contain the context from adjacent chunks, allowing downstream systems to access the context without altering the core content.

```python
if include_metadata:
    new_chunk = self._add_context_to_metadata(
        chunk,
        previous_content,
        next_content,
        previous_chunk_index,
        next_chunk_index,
    )
```

**Legacy Mode** (`include_metadata=False`): In this mode, overlap context is merged directly into the chunk content, creating a single string that combines the context with the core content. This was the original behavior and is maintained for backward compatibility.

```python
else:
    new_chunk = self._merge_context_into_content(
        chunk, previous_content, next_content
    )
```

The default behavior maintains backward compatibility by using legacy mode when the `include_metadata` parameter is not specified.

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L120)
- [test_components/test_overlap_metadata_mode.py](file://tests/chunker/test_components/test_overlap_metadata_mode.py#L231)

### Block-Aware Extraction

The overlap system uses block-aware extraction to ensure that overlap boundaries align with content blocks. This prevents partial blocks from being included in the overlap, which could disrupt the structural integrity of the content.

The system identifies different types of content blocks, including:
- Code blocks (``` ... ```)
- Paragraphs (separated by double newlines)
- Headers (lines starting with #)
- Lists (lines starting with -, *, +, or numbers)
- Tables (structured content with pipes)

During overlap extraction, the system attempts to include complete blocks rather than splitting them. If no complete block fits within the target overlap size, the system may return an empty overlap rather than including a partial block.

```python
def _extract_block_aligned_overlap(self, chunk: Chunk, target_size: int) -> Optional[str]:
    # Collect blocks from end until we reach target size
    selected_blocks: List[ContentBlock] = []
    total_size = 0
    
    for block in reversed(blocks):
        block_size = block.size
        
        if total_size == 0:
            if block_size <= target_size * 1.2:
                selected_blocks.insert(0, block)
                total_size += block_size
        elif total_size + block_size + 2 <= target_size:
            selected_blocks.insert(0, block)
            total_size += block_size + 2
        else:
            break
```

This block-aware approach ensures that code blocks, tables, and other structured content remain intact in the overlap context.

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L651)

## Downstream System Benefits

### Context Continuity in RAG Applications

The overlap metadata fields provide significant benefits for retrieval-augmented generation (RAG) applications by maintaining context continuity across chunk boundaries. When a query spans multiple chunks, the overlapping content ensures that relevant context is preserved, improving the quality and coherence of generated responses.

For example, consider a technical document where a code explanation spans two chunks. Without overlap, the second chunk might lack the context needed to understand the code being discussed. With overlap, the second chunk includes the relevant context from the end of the first chunk, enabling more accurate and contextually appropriate responses.

The `has_overlap` field allows downstream systems to identify chunks with overlapping content and potentially weight them differently in retrieval algorithms. Chunks with overlap might be given higher priority since they contain additional context that could be relevant to a broader range of queries.

**Section sources**
- [test_components/test_overlap_new_model.py](file://tests/chunker/test_components/test_overlap_new_model.py#L159)

### Duplicate Content Handling

The overlap metadata fields help downstream systems handle duplicate content more effectively. By explicitly marking chunks that contain overlapping content, systems can implement sophisticated deduplication strategies that preserve context while avoiding redundant processing.

For example, a search index might use the `has_overlap` field to identify overlapping content and adjust ranking algorithms accordingly. Documents with well-placed overlaps might be ranked higher since they provide better context continuity. Alternatively, a summarization system might use the `overlap_type` field to avoid double-counting information that appears in both the suffix of one chunk and the prefix of the next.

The metadata mode of overlap processing is particularly beneficial for duplicate content handling, as it keeps the core content separate from the overlapping context. This allows systems to process the core content once while still having access to the contextual information when needed.

**Section sources**
- [test_components/test_overlap_metadata_mode.py](file://tests/chunker/test_components/test_overlap_metadata_mode.py#L223)

### Integration with Chunking Strategy

The overlap fields are closely integrated with the overall chunking strategy, enhancing the effectiveness of different chunking approaches. For example:

- **Code Strategy**: When processing code-heavy documents, overlap ensures that function definitions and their usage are kept in context, even when they span multiple chunks.
- **Structural Strategy**: For documents with clear section hierarchies, overlap helps maintain the relationship between sections and their content.
- **Mixed Strategy**: In documents with diverse content types, overlap preserves the context between different content types, such as code blocks and their explanations.

The configuration parameters for overlap can be tailored to specific chunking strategies. For example, code-heavy documents might benefit from larger overlap sizes to ensure that related code segments remain in context, while list-heavy documents might use smaller overlaps since list items are often self-contained.

**Section sources**
- [core.py](file://markdown_chunker_legacy/chunker/core.py#L139)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L748)

## Performance Considerations

### Overlap Size Impact

The size of the overlap has a direct impact on both storage requirements and processing performance. Larger overlaps increase the total amount of text that needs to be stored and processed, which can affect:

- **Storage**: Increased storage requirements due to duplicated content
- **Indexing**: Longer indexing times and larger index sizes
- **Retrieval**: More data to search through during retrieval operations
- **Generation**: More context to process during generation, potentially affecting latency

The system mitigates these impacts through several mechanisms:
- **Size Limiting**: Overlap size is limited to 40% of the source chunk size to prevent excessive duplication
- **Block Alignment**: Overlap respects block boundaries, preventing inefficient partial block storage
- **Conditional Application**: Overlap is only applied when beneficial, such as when there are multiple chunks

### Processing Overhead

The overlap processing adds computational overhead to the chunking pipeline, particularly in the context extraction phase. The block-aware extraction algorithm must parse the content to identify block boundaries, which requires additional processing time.

However, this overhead is generally justified by the benefits of improved context continuity. The system optimizes the processing through:
- **Efficient Parsing**: Using regular expressions and optimized text processing algorithms
- **Caching**: Reusing parsed block structures when possible
- **Early Termination**: Stopping extraction when the target size is reached

The performance impact can be monitored and adjusted through configuration parameters, allowing users to balance context quality with processing efficiency.

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L180)
- [core.py](file://markdown_chunker_legacy/chunker/core.py#L123)

## Examples and Usage

### Basic Overlap Configuration

The following example demonstrates how to configure and use overlap in the chunking system:

```python
# Create configuration with custom overlap settings
config = ChunkConfig(
    enable_overlap=True,
    overlap_size=300,
    block_based_overlap=True
)

# Initialize chunker with configuration
chunker = MarkdownChunker(config)

# Process markdown content
result = chunker.chunk(markdown_text, include_analysis=True)

# Check overlap metadata
for i, chunk in enumerate(result.chunks):
    has_overlap = chunk.metadata.get('has_overlap', False)
    if has_overlap:
        print(f"Chunk {i} has overlap")
        if 'previous_content' in chunk.metadata:
            print(f"  Previous context: {chunk.metadata['previous_content'][:50]}...")
        if 'next_content' in chunk.metadata:
            print(f"  Next context: {chunk.metadata['next_content'][:50]}...")
```

This example shows how to enable overlap with a larger size (300 characters) and block-based alignment. The resulting chunks include metadata that can be used to access the overlapping context.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L501)
- [core.py](file://markdown_chunker_legacy/chunker/core.py#L156)

### RAG Application Integration

In a RAG application, the overlap metadata fields can be used to enhance retrieval and generation:

```python
def process_retrieved_chunks(chunks):
    """Process retrieved chunks for RAG application."""
    processed_content = []
    
    for chunk in chunks:
        # Check if chunk has overlap
        has_overlap = chunk.metadata.get('has_overlap', False)
        
        # Extract core content and context
        core_content = chunk.content
        previous_context = chunk.metadata.get('previous_content', '')
        next_context = chunk.metadata.get('next_content', '')
        
        # Create enhanced context for generation
        enhanced_context = {
            'core': core_content,
            'has_overlap': has_overlap,
            'backward_context': previous_context,
            'forward_context': next_context
        }
        
        processed_content.append(enhanced_context)
    
    return processed_content
```

This function processes retrieved chunks by extracting both the core content and the overlapping context. The enhanced context can then be used to generate more coherent and contextually appropriate responses.

**Section sources**
- [overlap_manager.py](file://markdown_chunker_legacy/chunker/components/overlap_manager.py#L343)
- [test_components/test_overlap_metadata_mode.py](file://tests/chunker/test_components/test_overlap_metadata_mode.py#L61)

## Conclusion

The overlap metadata fields `has_overlap` and `overlap_type` are essential components of the chunking system, providing critical information about overlapping content between adjacent chunks. These fields enable downstream systems, particularly RAG applications, to maintain context continuity and handle duplicate content effectively.

The system offers flexible configuration options for controlling overlap behavior, including size, percentage, and block-based alignment. The two processing modes—metadata mode and legacy mode—provide compatibility with different use cases and integration requirements.

By understanding and leveraging these overlap fields, developers can create more effective document processing pipelines that preserve context while maintaining content integrity. The block-aware extraction approach ensures that structured content like code blocks and tables remain coherent across chunk boundaries, enhancing the overall quality of the chunked output.