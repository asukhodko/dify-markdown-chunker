# Configuration Profiles

<cite>
**Referenced Files in This Document**   
- [config.py](file://markdown_chunker_v2/config.py)
- [types.py](file://markdown_chunker_legacy/chunker/types.py)
- [configuration.md](file://docs/architecture-preaudit/04-configuration.md)
- [technical_spec.md](file://tests/fixtures/real_documents/technical_spec.md)
- [blog_post.md](file://tests/fixtures/real_documents/blog_post.md)
- [dify_integration.py](file://examples/dify_integration.py)
- [rag_integration.py](file://examples/rag_integration.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Configuration Profiles](#core-configuration-profiles)
3. [Profile Use Case Recommendations](#profile-use-case-recommendations)
4. [Creating and Using Profiles](#creating-and-using-profiles)
5. [Custom Profile Creation](#custom-profile-creation)
6. [Profile-Parameter Relationships](#profile-parameter-relationships)
7. [Predefined Profiles vs Custom Configurations](#predefined-profiles-vs-custom-configurations)
8. [Conclusion](#conclusion)

## Introduction

The configuration profile system in the markdown chunker provides a set of factory methods that create optimized configurations for specific document types and application requirements. These profiles simplify the configuration process by providing sensible defaults for various use cases, eliminating the need for users to manually tune numerous parameters. The system has evolved from a complex configuration with 32 parameters to a streamlined approach with fewer core parameters and well-defined profiles.

The profiles are implemented as class methods on the `ChunkConfig` class, allowing for easy creation of configurations tailored to specific scenarios such as code-heavy documents, RAG applications, search indexing, and chat contexts. This documentation provides comprehensive information about each profile, including their parameter values, optimization goals, and recommended use cases.

**Section sources**
- [technical_spec.md](file://tests/fixtures/real_documents/technical_spec.md#L278-L320)
- [configuration.md](file://docs/architecture-preaudit/04-configuration.md#L1-L236)

## Core Configuration Profiles

The configuration profile system offers several factory methods that create optimized configurations for specific use cases. These profiles are designed to address common scenarios encountered when processing markdown documents.

### Default Profile

The default profile provides balanced settings suitable for general-purpose markdown processing. It represents the baseline configuration with moderate chunk sizes and standard overlap settings.

```python
config = ChunkConfig.default()
```

This profile uses the following parameter values:
- max_chunk_size: 4096 characters
- min_chunk_size: 512 characters
- target_chunk_size: 2048 characters
- overlap_size: 200 characters
- enable_overlap: True

The default profile is appropriate for general markdown documents that don't have specific requirements for chunk size or structure preservation.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L686-L712)
- [technical_spec.md](file://tests/fixtures/real_documents/technical_spec.md#L283-L286)

### Code-Heavy Profile

The code_heavy profile is optimized for technical documentation and code-heavy documents. It prioritizes preserving code blocks and maintaining context for code examples.

```python
config = ChunkConfig.for_code_heavy()
```

This profile uses the following parameter values:
- max_chunk_size: 8192 characters (in v2) or 6144 characters (in legacy)
- min_chunk_size: 1024 characters (in v2) or 512 characters (in legacy)
- overlap_size: 100 characters (in v2) or 300 characters (in legacy)
- code_threshold: 0.2 (in v2) or code_ratio_threshold: 0.5 (in legacy)
- preserve_code_blocks: True

The code-heavy profile is designed to handle documents with extensive code examples, API references, and technical tutorials. It uses a lower code threshold to more aggressively detect code-heavy sections and larger chunk sizes to accommodate complete code blocks.

**Section sources**
- [config.py](file://markdown_chunker_v2/config.py#L143-L151)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L714-L757)

### Structured Documents Profile

The structured_docs profile is optimized for documents with clear hierarchical structure, such as user manuals, technical specifications, and organized documentation.

```python
config = ChunkConfig.for_structured_docs()
```

This profile uses the following parameter values:
- max_chunk_size: 3072 characters
- target_chunk_size: 1536 characters
- header_count_threshold: 2 (more aggressive structural detection)
- preserve_list_hierarchy: True
- overlap_size: 150 characters

The structured documents profile emphasizes preserving the document's hierarchical structure, including headers and list nesting. It uses smaller chunk sizes to maintain better section granularity and ensure that chunks respect section boundaries.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L760-L800)

### Dify RAG Profile

The Dify RAG profile is specifically optimized for Retrieval-Augmented Generation systems, particularly those integrated with the Dify platform.

```python
config = ChunkConfig.for_dify_rag()
```

This profile uses the following parameter values:
- max_chunk_size: 3072 characters
- min_chunk_size: 256 characters
- target_chunk_size: 1536 characters
- overlap_size: 150 characters
- enable_overlap: True
- preserve_code_blocks: True
- preserve_list_hierarchy: True
- allow_oversize: False

The Dify RAG profile is tuned for optimal performance in RAG applications, with moderate chunk sizes that balance semantic coherence with retrieval precision. It preserves structural elements like code blocks and list hierarchies while preventing oversized chunks that could negatively impact retrieval quality.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L907-L924)
- [blog_post.md](file://tests/fixtures/real_documents/blog_post.md#L98-L105)

### Chat Context Profile

The chat_context profile is optimized for use in chat applications and LLM contexts where token limitations are critical.

```python
config = ChunkConfig.for_chat_context()
```

This profile uses the following parameter values:
- max_chunk_size: 1536 characters
- min_chunk_size: 200 characters
- overlap_size: 200 characters
- enable_overlap: True
- code_ratio_threshold: 0.5
- list_count_threshold: 4
- table_count_threshold: 2
- min_complexity: 0.1

The chat context profile creates smaller chunks suitable for chat context windows, ensuring that each chunk fits within typical LLM token limits while maintaining sufficient context through overlap. This profile is ideal for applications where chunks are used as context in conversational AI systems.

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L981-L997)

## Profile Use Case Recommendations

### When to Use Each Profile

#### Default Profile Use Cases
- General markdown documents without specific requirements
- Mixed content with balanced text and code
- Documents of moderate length (1-10KB)
- Initial testing and prototyping
- When no specific optimization is needed

The default profile serves as a good starting point for most applications and can be used when the document characteristics are unknown or varied.

#### Code-Heavy Profile Use Cases
- Technical documentation with extensive code examples
- API reference manuals
- Programming tutorials
- Code-heavy README files
- Documentation with multiple programming languages
- Documents where code block integrity is critical

This profile should be used when preserving complete code blocks is more important than strict chunk size limits, and when code context needs to be maintained across chunk boundaries.

#### Structured Documents Profile Use Cases
- User manuals and guides
- Technical specifications
- Organized documentation with clear sections
- Documents with deep header hierarchies
- Content with nested lists and structured data
- Documentation requiring precise section boundaries

Use this profile when document structure and hierarchy preservation are paramount, and when chunks should align with logical document sections.

#### Dify RAG Profile Use Cases
- Retrieval-Augmented Generation systems
- Semantic search applications
- Knowledge base indexing
- Question-answering systems
- Document retrieval for LLMs
- Applications requiring high retrieval accuracy

This profile is specifically designed for RAG applications where chunk quality directly impacts retrieval performance and answer accuracy.

#### Chat Context Profile Use Cases
- Chatbot applications
- Conversational AI systems
- LLM context window optimization
- Real-time document processing
- Applications with strict token limitations
- Interactive documentation systems

Use this profile when chunks will be directly injected into LLM prompts and token efficiency is critical.

**Section sources**
- [technical_spec.md](file://tests/fixtures/real_documents/technical_spec.md#L278-L320)
- [dify_integration.py](file://examples/dify_integration.py#L200-L253)
- [rag_integration.py](file://examples/rag_integration.py#L359-L409)

## Creating and Using Profiles

### Basic Profile Creation

Creating and using configuration profiles is straightforward using the factory methods provided by the `ChunkConfig` class:

```python
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker import MarkdownChunker

# Create a configuration using a profile
config = ChunkConfig.for_dify_rag()

# Use the configuration with a chunker
chunker = MarkdownChunker(config)

# Process a document
chunks = chunker.chunk(documentation)
```

### Integration with Processing Pipelines

Profiles can be easily integrated into document processing pipelines:

```python
def process_document_with_profile(document, profile_name):
    """Process a document using a specific configuration profile."""
    profile_methods = {
        'default': ChunkConfig.default,
        'code_heavy': ChunkConfig.for_code_heavy,
        'structured': ChunkConfig.for_structured_docs,
        'dify_rag': ChunkConfig.for_dify_rag,
        'chat_context': ChunkConfig.for_chat_context
    }
    
    if profile_name not in profile_methods:
        raise ValueError(f"Unknown profile: {profile_name}")
    
    config = profile_methods[profile_name]()
    chunker = MarkdownChunker(config)
    return chunker.chunk(document)
```

### Example Usage Scenarios

#### RAG System Integration
```python
# For a RAG system using Dify
config = ChunkConfig.for_dify_rag()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(technical_documentation)

# Results in 95% answer accuracy with zero broken code examples
```

#### Code Documentation Processing
```python
# For processing API documentation with code examples
config = ChunkConfig.for_code_heavy()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(api_reference)

# Preserves code blocks and maintains context for code examples
```

#### Chat Application Context
```python
# For a chatbot that needs to reference documentation
config = ChunkConfig.for_chat_context()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(user_guide)

# Creates chunks optimized for LLM context windows
```

**Section sources**
- [dify_integration.py](file://examples/dify_integration.py#L200-L253)
- [rag_integration.py](file://examples/rag_integration.py#L359-L409)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L558-L562)

## Custom Profile Creation

### Subclassing Approach

While the predefined profiles cover many common use cases, custom profiles can be created through subclassing or direct configuration:

```python
class CustomConfig(ChunkConfig):
    @classmethod
    def for_my_use_case(cls) -> "ChunkConfig":
        """Custom configuration for specific use case."""
        return cls(
            max_chunk_size=4096,
            min_chunk_size=512,
            overlap_size=200,
            code_ratio_threshold=0.4,
            preserve_code_blocks=True,
            preserve_list_hierarchy=True
        )
```

### Composition Approach

Custom configurations can also be created by modifying existing profiles:

```python
def create_custom_profile(base_profile_name, **overrides):
    """Create a custom profile based on an existing profile."""
    base_profiles = {
        'default': ChunkConfig.default,
        'code_heavy': ChunkConfig.for_code_heavy,
        'dify_rag': ChunkConfig.for_dify_rag,
        'chat_context': ChunkConfig.for_chat_context
    }
    
    if base_profile_name not in base_profiles:
        raise ValueError(f"Unknown base profile: {base_profile_name}")
    
    # Create base configuration
    config = base_profiles[base_profile_name]()
    
    # Apply overrides
    config_dict = config.to_dict()
    config_dict.update(overrides)
    
    return ChunkConfig.from_dict(config_dict)

# Example: Create a custom RAG profile with larger chunks
custom_rag_config = create_custom_profile(
    'dify_rag', 
    max_chunk_size=4096, 
    overlap_size=300
)
```

### Advanced Customization

For more complex customization, you can create profiles that adapt to document characteristics:

```python
def adaptive_profile(document_text):
    """Create a profile based on document analysis."""
    # Simple analysis to determine document type
    code_ratio = document_text.count('```') / len(document_text.split('\n'))
    
    if code_ratio > 0.1:
        return ChunkConfig.for_code_heavy()
    elif '##' in document_text and document_text.count('##') > 5:
        return ChunkConfig.for_structured_docs()
    else:
        return ChunkConfig.default()
```

**Section sources**
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L1035-L1047)
- [config.py](file://markdown_chunker_v2/config.py#L81-L135)

## Profile-Parameter Relationships

### Core Parameters Modified by Profiles

The configuration profiles modify several key parameters to optimize for specific use cases:

| Parameter | Purpose | Profiles That Modify |
|---------|-------|---------------------|
| max_chunk_size | Maximum size of a chunk in characters | All profiles |
| min_chunk_size | Minimum size of a chunk in characters | Most profiles |
| overlap_size | Size of overlap between chunks | Most profiles |
| code_ratio_threshold | Threshold for code strategy selection | code_heavy, chat_context |
| header_count_threshold | Minimum headers for structural strategy | structured_docs |
| preserve_code_blocks | Keep code blocks intact | code_heavy, dify_rag |
| preserve_list_hierarchy | Preserve list nesting structure | structured_docs, dify_rag |

### Parameter Optimization Goals

Each profile optimizes parameters with specific goals in mind:

- **Default Profile**: Balanced settings for general use
- **Code-Heavy Profile**: Preserve code block integrity and context
- **Structured Docs Profile**: Respect document hierarchy and section boundaries
- **Dify RAG Profile**: Optimize for retrieval accuracy and semantic coherence
- **Chat Context Profile**: Fit within LLM token limits while maintaining context

### Version Differences

There are notable differences between the legacy and v2 configuration systems:

- **Legacy system**: 32 parameters with extensive configurability
- **V2 system**: 8 core parameters with simplified configuration
- **Parameter renaming**: Some parameters have been renamed (e.g., code_ratio_threshold to code_threshold)
- **Behavior changes**: Some behaviors are now enabled by default (e.g., block-based splitting)

The v2 system represents a simplification of the configuration model, focusing on the most impactful parameters while maintaining backward compatibility through the `from_legacy` method.

**Section sources**
- [config.py](file://markdown_chunker_v2/config.py#L11-L45)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L577-L635)
- [configuration.md](file://docs/architecture-preaudit/04-configuration.md#L1-L236)

## Predefined Profiles vs Custom Configurations

### When to Use Predefined Profiles

Predefined profiles should be used when:

- The document type matches one of the supported categories (code-heavy, structured, RAG, etc.)
- Rapid prototyping or initial implementation is needed
- Best practices for specific use cases should be followed
- Consistency across multiple applications or teams is important
- The user is not an expert in chunking configuration

The predefined profiles encapsulate best practices and lessons learned from real-world usage, making them ideal for most common scenarios.

### When to Use Custom Configurations

Custom configurations are appropriate when:

- Specific application requirements are not met by existing profiles
- Fine-tuning is needed for optimal performance
- Unique document types or structures are being processed
- Performance characteristics need to be optimized for specific hardware
- Integration with specialized downstream systems requires custom settings

Custom configurations provide maximum flexibility but require deeper understanding of the chunking process and its parameters.

### Migration Strategy

For users transitioning from the legacy system to v2:

1. Start with the closest predefined profile
2. Compare results with the legacy configuration
3. Make incremental adjustments as needed
4. Validate that document integrity is maintained
5. Test performance and quality metrics

The `from_legacy` method provides backward compatibility, allowing gradual migration from the legacy parameter set to the simplified v2 model.

**Section sources**
- [config.py](file://markdown_chunker_v2/config.py#L81-L135)
- [types.py](file://markdown_chunker_legacy/chunker/types.py#L540-L575)

## Conclusion

The configuration profile system provides a powerful and user-friendly way to optimize markdown chunking for various use cases. By offering predefined profiles for common scenarios like code-heavy documents, RAG applications, and chat contexts, the system simplifies configuration while ensuring optimal performance.

The evolution from a complex 32-parameter system to a streamlined approach with focused profiles represents a significant improvement in usability and maintainability. Users can now select from well-tuned configurations that embody best practices, rather than needing to understand and tune numerous parameters.

For most applications, the predefined profiles provide excellent results out of the box. When specific requirements demand more control, the system supports custom configurations through subclassing, composition, or direct parameter manipulation. This flexibility ensures that the chunking system can adapt to a wide range of use cases while maintaining simplicity for common scenarios.