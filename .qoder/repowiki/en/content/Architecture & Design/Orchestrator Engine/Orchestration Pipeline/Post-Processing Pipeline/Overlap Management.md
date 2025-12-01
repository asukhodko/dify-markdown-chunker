# Overlap Management

<cite>
**Referenced Files in This Document**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py)
- [test_overlap_manager.py](file://tests/chunker/test_components/test_overlap_manager.py)
- [types.py](file://markdown_chunker/chunker/types.py)
- [core.py](file://markdown_chunker/chunker/core.py)
- [rag_integration.py](file://examples/rag_integration.py)
- [mixed.md](file://tests/fixtures/mixed.md)
- [code_heavy.md](file://tests/fixtures/code_heavy.md)
- [list_heavy.md](file://tests/fixtures/list_heavy.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Configuration System](#configuration-system)
5. [Internal Logic and Implementation](#internal-logic-and-implementation)
6. [Overlap Application Process](#overlap-application-process)
7. [Content Boundary Preservation](#content-boundary-preservation)
8. [Edge Cases and Error Handling](#edge-cases-and-error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Integration Examples](#integration-examples)
11. [Testing and Validation](#testing-and-validation)
12. [Best Practices](#best-practices)

## Introduction

The OverlapManager component is a critical part of the markdown chunking system that creates overlapping content between adjacent chunks to maintain context continuity, particularly important for Retrieval-Augmented Generation (RAG) systems. This component ensures that when documents are divided into smaller chunks for processing, the contextual information from one chunk to the next is preserved, preventing information loss and improving the effectiveness of downstream AI applications.

The overlap mechanism works by extracting content from the end of previous chunks and prepending it to subsequent chunks, creating a seamless transition between adjacent segments. This approach is essential for maintaining semantic coherence when chunks are processed independently, such as in vector database retrieval or LLM context windows.

## Architecture Overview

The OverlapManager operates as part of a multi-stage chunking pipeline, positioned after strategy selection and before metadata enrichment. It integrates seamlessly with the broader chunking system through the main MarkdownChunker orchestration.

```mermaid
flowchart TD
A["Input Markdown Document"] --> B["Stage 1: Content Analysis"]
B --> C["Stage 2: Strategy Selection"]
C --> D["Stage 3: Chunk Generation"]
D --> E["OverlapManager.apply_overlap()"]
E --> F["Metadata Enrichment"]
F --> G["Validation & Preamble Processing"]
G --> H["Final Chunked Output"]
I["ChunkConfig"] --> E
J["Overlap Settings"] --> I
K["Content Boundaries"] --> E
E --> L["Sentence Boundary Detection"]
E --> M["Code Block Integrity Check"]
E --> N["Overlap Size Calculation"]
E --> O["Content Extraction"]
```

**Diagram sources**
- [core.py](file://markdown_chunker/chunker/core.py#L280-L286)
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L37-L79)

**Section sources**
- [core.py](file://markdown_chunker/chunker/core.py#L138-L140)
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L12-L32)

## Core Components

### OverlapManager Class Structure

The OverlapManager is implemented as a focused, stateless component that handles all aspects of overlap creation and management. It operates on lists of Chunk objects and applies overlap according to configuration settings.

```mermaid
classDiagram
class OverlapManager {
+ChunkConfig config
+str SENTENCE_END_PATTERN
+__init__(config : ChunkConfig)
+apply_overlap(chunks : List[Chunk]) List[Chunk]
+calculate_overlap_statistics(chunks : List[Chunk]) dict
-_extract_overlap(chunk : Chunk, is_suffix : bool) str
-_extract_suffix_overlap(content : str, target_size : int) str
-_extract_prefix_overlap(content : str, target_size : int) str
-_add_overlap_prefix(chunk : Chunk, overlap_text : str) Chunk
-_split_into_sentences(content : str) List[str]
-_truncate_preserving_sentences(text : str, max_size : int) str
-_is_code_chunk(chunk : Chunk) bool
-_has_unbalanced_fences(text : str) bool
}
class Chunk {
+str content
+int start_line
+int end_line
+Dict metadata
+size() int
+get_metadata(key : str, default : Any) Any
}
class ChunkConfig {
+bool enable_overlap
+int overlap_size
+float overlap_percentage
+int max_chunk_size
}
OverlapManager --> ChunkConfig : uses
OverlapManager --> Chunk : processes
```

**Diagram sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L13-L447)
- [types.py](file://markdown_chunker/chunker/types.py#L36-L49)

### Key Internal Components

The OverlapManager utilizes several specialized methods for different aspects of overlap management:

- **Sentence Boundary Detection**: Uses regex patterns to identify natural sentence breaks
- **Content Extraction**: Implements both suffix and prefix overlap extraction
- **Code Block Integrity**: Prevents overlap from breaking code fence structures
- **Size Compliance**: Ensures overlap respects configured size limits
- **Metadata Management**: Adds overlap-related metadata to chunks

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L25-L447)

## Configuration System

The OverlapManager relies on the ChunkConfig system to determine overlap behavior. Configuration options provide fine-grained control over overlap characteristics and behavior.

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enable_overlap` | bool | True | Enables or disables overlap creation |
| `overlap_size` | int | 200 | Fixed overlap size in characters |
| `overlap_percentage` | float | 0.1 | Percentage of chunk size for overlap |
| `max_chunk_size` | int | 4096 | Maximum chunk size constraint |

### Priority System

The overlap calculation follows a specific priority order:

1. **Fixed Size Override**: If `overlap_size > 0`, it takes precedence
2. **Percentage Calculation**: Uses `overlap_percentage` as fallback
3. **Size Limiting**: Maximum overlap is capped at 40% of source chunk size
4. **Ratio Constraint**: Final overlap must not exceed 50% of resulting chunk size

**Section sources**
- [types.py](file://markdown_chunker/chunker/types.py#L574-L583)
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L125-L140)

## Internal Logic and Implementation

### apply_overlap Method

The main entry point for overlap application implements a sophisticated algorithm that processes chunks sequentially while maintaining context preservation.

```mermaid
flowchart TD
A["apply_overlap(chunks)"] --> B{"Empty or Single Chunk?"}
B --> |Yes| C["Return Original Chunks"]
B --> |No| D{"Overlap Enabled?"}
D --> |No| C
D --> |Yes| E["Initialize Result List"]
E --> F["Process Each Chunk"]
F --> G{"First Chunk?"}
G --> |Yes| H["Add Unmodified"]
G --> |No| I["Extract Previous Overlap"]
I --> J{"Unbalanced Fences?"}
J --> |Yes| K["Skip Overlap"]
J --> |No| L["Add Overlap Prefix"]
H --> M["Continue to Next"]
K --> M
L --> M
M --> N{"More Chunks?"}
N --> |Yes| F
N --> |No| O["Return Result"]
```

**Diagram sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L37-L79)

### Overlap Extraction Process

The `_extract_overlap` method implements the core overlap calculation logic:

1. **Size Determination**: Calculates target overlap size using priority system
2. **Boundary Detection**: Identifies sentence boundaries for natural breaks
3. **Content Collection**: Gathers content from appropriate direction (suffix/prefix)
4. **Size Validation**: Ensures overlap doesn't exceed configured limits
5. **Integrity Check**: Verifies code block balance if applicable

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L109-L154)

## Overlap Application Process

### Suffix vs Prefix Overlap

The system supports both suffix and prefix overlap extraction depending on the context:

- **Suffix Overlap**: Extracts from the end of previous chunks (default for RAG)
- **Prefix Overlap**: Extracts from the beginning of current chunks (rare use case)

### Sentence Boundary Preservation

The overlap system prioritizes natural sentence boundaries to maintain readability:

```mermaid
flowchart TD
A["Content with Sentences"] --> B["Split by Sentence Pattern"]
B --> C["Collect Sentences Until Target Size"]
C --> D{"First Sentence Allowed?"}
D --> |Yes| E["Add with Tolerance"]
D --> |No| F["Check Size Constraints"]
F --> G{"Within Limits?"}
G --> |Yes| H["Add Sentence"]
G --> |No| I["Stop Collection"]
E --> J["Build Overlap Text"]
H --> J
I --> J
J --> K["Return Formatted Overlap"]
```

**Diagram sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L155-L204)

### Code Block Integrity Protection

The system includes sophisticated protection against breaking code block structures:

- **Fence Detection**: Identifies code fence markers (` ``` `)
- **Balance Checking**: Ensures overlap doesn't create unbalanced fences
- **Fallback Strategy**: Skips overlap when integrity would be compromised

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L81-L107)

## Content Boundary Preservation

### Sentence Boundary Detection

The overlap system uses regex-based sentence boundary detection to maintain natural text flow:

- **Pattern Matching**: Uses `.!?` followed by whitespace as sentence indicators
- **Reconstruction**: Preserves punctuation and spacing in extracted content
- **Fallback Handling**: Gracefully handles content without clear sentence boundaries

### Content Type Awareness

The system recognizes different content types and applies appropriate overlap strategies:

- **Text Content**: Full sentence-aware overlap
- **Code Blocks**: Fence-aware overlap with integrity checks
- **Lists**: Structure-preserving overlap
- **Tables**: Atomic-block overlap

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L286-L318)

## Edge Cases and Error Handling

### Single Chunk Scenarios

The overlap system handles various edge cases gracefully:

- **Empty Lists**: Returns empty result without processing
- **Single Chunks**: No overlap applied, chunks returned unchanged
- **Very Short Chunks**: Overlap size adjusted to chunk size limitations
- **Zero or Negative Sizes**: Handled through configuration validation

### Configuration Validation

The system includes comprehensive validation for overlap settings:

- **Size Constraints**: Ensures overlap size doesn't exceed chunk size
- **Percentage Bounds**: Validates overlap percentage is between 0.0 and 1.0
- **Ratio Limits**: Prevents overlap from dominating resulting chunks
- **Integrity Checks**: Validates code block balance before applying overlap

### Error Recovery

When overlap processing encounters issues, the system implements graceful degradation:

- **Exception Handling**: Catches and logs errors without failing chunking
- **Fallback Behavior**: Returns original chunks when overlap would cause problems
- **Integrity Preservation**: Maintains document structure even when overlap is skipped

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L47-L78)
- [test_overlap_manager.py](file://tests/chunker/test_components/test_overlap_manager.py#L16-L58)

## Performance Considerations

### Computational Complexity

The overlap system is designed for efficiency while maintaining quality:

- **Linear Processing**: Each chunk is processed individually with O(n) complexity
- **Regex Optimization**: Sentence boundary detection uses compiled patterns
- **Early Termination**: Content collection stops when size limits are reached
- **Memory Efficiency**: Processes chunks without storing intermediate results

### Scalability Factors

Several factors affect overlap performance at scale:

- **Chunk Count**: Linear scaling with number of chunks
- **Content Length**: Proportional to average chunk size
- **Sentence Density**: Higher density requires more processing
- **Code Block Frequency**: Additional parsing overhead for code content

### Optimization Strategies

The system includes several optimization measures:

- **Lazy Evaluation**: Only processes overlap when needed
- **Size Caching**: Avoids repeated calculations of chunk sizes
- **Pattern Compilation**: Regex patterns are compiled once during initialization
- **Early Validation**: Checks for overlap conflicts early in processing

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L125-L140)

## Integration Examples

### RAG System Integration

The overlap manager is specifically designed for RAG applications, where context preservation is crucial:

```mermaid
sequenceDiagram
participant Client as RAG Client
participant Chunker as MarkdownChunker
participant OverlapMgr as OverlapManager
participant VectorDB as Vector Database
Client->>Chunker : chunk_with_analysis(document)
Chunker->>OverlapMgr : apply_overlap(chunks)
OverlapMgr->>OverlapMgr : extract_previous_overlaps()
OverlapMgr->>OverlapMgr : preserve_sentence_boundaries()
OverlapMgr->>OverlapMgr : validate_code_integrity()
OverlapMgr-->>Chunker : overlapped_chunks
Chunker-->>Client : ChunkingResult
Client->>VectorDB : store_chunks_with_overlap
VectorDB-->>Client : stored_chunks
```

**Diagram sources**
- [rag_integration.py](file://examples/rag_integration.py#L13-L53)
- [core.py](file://markdown_chunker/chunker/core.py#L280-L286)

### Configuration for Different Use Cases

The system supports various configuration profiles for different scenarios:

- **RAG Optimization**: Small chunks with generous overlap (50-100 characters)
- **Documentation**: Balanced approach for technical content
- **Code Documentation**: Larger overlap to maintain context across code examples
- **Research Papers**: Conservative overlap to avoid redundancy

**Section sources**
- [rag_integration.py](file://examples/rag_integration.py#L13-L70)

## Testing and Validation

### Comprehensive Test Coverage

The overlap manager includes extensive test coverage for various scenarios:

- **Basic Functionality**: Core overlap application and metadata addition
- **Edge Cases**: Empty inputs, single chunks, very short content
- **Configuration Variants**: Fixed size vs percentage-based overlap
- **Content Types**: Text, code, lists, and mixed content
- **Error Conditions**: Invalid configurations, unbalanced fences

### Statistical Analysis

The system provides overlap statistics for monitoring and optimization:

- **Overlap Percentage**: Ratio of chunks with overlap
- **Average Size**: Mean overlap size across all chunks
- **Total Overlap**: Cumulative overlap across all chunks
- **Distribution Analysis**: Size distribution of overlap content

**Section sources**
- [test_overlap_manager.py](file://tests/chunker/test_components/test_overlap_manager.py#L406-L447)

## Best Practices

### Configuration Guidelines

For optimal results, follow these configuration recommendations:

- **RAG Systems**: Use small overlap sizes (50-100 characters) with percentage-based fallback
- **Documentation**: Balance overlap with chunk size (10-20% of target size)
- **Code Documentation**: Increase overlap for better context preservation
- **Large Documents**: Consider streaming configuration with moderate overlap

### Content Preparation

Prepare content for optimal overlap effectiveness:

- **Structured Content**: Use clear headings and logical organization
- **Sentence Structure**: Maintain natural sentence boundaries in content
- **Code Organization**: Group related code examples together
- **List Formatting**: Use consistent list styles for better chunking

### Monitoring and Optimization

Monitor overlap effectiveness and adjust configuration as needed:

- **Coverage Analysis**: Track how much content is covered by overlap
- **Quality Metrics**: Monitor chunk quality and context preservation
- **Performance Tracking**: Measure overlap processing time impact
- **Feedback Loops**: Adjust configuration based on downstream application performance

**Section sources**
- [overlap_manager.py](file://markdown_chunker/chunker/components/overlap_manager.py#L405-L447)