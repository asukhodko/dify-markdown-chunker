# Core Concepts

<cite>
**Referenced Files in This Document**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py)
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py)
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py)
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py)
- [markdown_chunker/parser/analyzer.py](file://markdown_chunker/parser/analyzer.py)
- [markdown_chunker/chunker/strategies/base.py](file://markdown_chunker/chunker/strategies/base.py)
- [markdown_chunker/chunker/strategies/code_strategy.py](file://markdown_chunker/chunker/strategies/code_strategy.py)
- [markdown_chunker/chunker/strategies/mixed_strategy.py](file://markdown_chunker/chunker/strategies/mixed_strategy.py)
- [markdown_chunker/chunker/strategies/structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py)
- [examples/basic_usage.py](file://examples/basic_usage.py)
- [examples/api_usage.py](file://examples/api_usage.py)
- [tests/fixtures/code_heavy.md](file://tests/fixtures/code_heavy.md)
- [tests/fixtures/mixed.md](file://tests/fixtures/mixed.md)
- [tests/fixtures/structural.md](file://tests/fixtures/structural.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Markdown AST Parsing Fundamentals](#markdown-ast-parsing-fundamentals)
3. [Understanding Chunks and Logical Blocks](#understanding-chunks-and-logical-blocks)
4. [Content Analysis Metrics](#content-analysis-metrics)
5. [Strategy Scoring and Selection](#strategy-scoring-and-selection)
6. [Configuration Profiles](#configuration-profiles)
7. [Header Paths and Metadata Enrichment](#header-paths-and-metadata-enrichment)
8. [Idempotent Processing](#idempotent-processing)
9. [Practical Implementation Examples](#practical-implementation-examples)
10. [Advanced Concepts](#advanced-concepts)

## Introduction

The Markdown Chunker system represents a sophisticated approach to breaking down Markdown documents into semantically meaningful fragments. At its core, this system combines **Abstract Syntax Tree (AST) parsing**, **intelligent content analysis**, and **adaptive strategy selection** to produce chunks that preserve document structure while optimizing for downstream applications like Retrieval-Augmented Generation (RAG), search indexing, and chat contexts.

The system operates in two distinct phases:
- **Stage 1 (Analysis)**: Content analysis and metrics calculation
- **Stage 2 (Chunking)**: Strategy selection and chunk generation

This dual-phase approach ensures that documents are processed according to their inherent structure and content characteristics, resulting in chunks that maintain semantic coherence and contextual relevance.

## Markdown AST Parsing Fundamentals

### What is an Abstract Syntax Tree?

An Abstract Syntax Tree (AST) is a hierarchical representation of a document's structure, where each node corresponds to a specific element in the Markdown document. Unlike plain text parsing, AST parsing captures the semantic relationships between different components, enabling intelligent chunking decisions.

```mermaid
graph TD
A["Markdown Document"] --> B["AST Builder"]
B --> C["Document Root"]
C --> D["Header Level 1"]
C --> E["Paragraph"]
C --> F["Code Block"]
C --> G["List"]
C --> H["Table"]
D --> I["Header Level 2"]
D --> J["Header Level 3"]
G --> K["List Item 1"]
G --> L["List Item 2"]
G --> M["Nested List"]
F --> N["Python Code"]
F --> O["JavaScript Code"]
```

**Diagram sources**
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py#L58-L118)
- [markdown_chunker/parser/analyzer.py](file://markdown_chunker/parser/analyzer.py#L18-L499)

### AST Node Types

The system recognizes several fundamental node types that form the building blocks of Markdown documents:

| Node Type | Description | Example |
|-----------|-------------|---------|
| `DOCUMENT` | Root container for the entire document | Entire Markdown file |
| `HEADER` | Heading elements (H1-H6) | `# Main Title`, `## Section` |
| `PARAGRAPH` | Text paragraphs | Normal flowing text |
| `CODE_BLOCK` | Fenced code blocks | ```python<br/>def func():<br/>    pass<br/>``` |
| `LIST` | Ordered or unordered lists | `- Item 1`, `1. Step 1` |
| `LIST_ITEM` | Individual list entries | Child nodes of LIST |
| `TABLE` | Tabular data structure | Markdown tables with headers |
| `BLOCKQUOTE` | Quoted text blocks | `> Important note` |
| `TEXT` | Inline text content | Plain text within elements |

### Enhanced AST Features

The system extends basic AST functionality with enhanced capabilities:

```mermaid
classDiagram
class MarkdownNode {
+NodeType type
+string content
+Position start_pos
+Position end_pos
+MarkdownNode[] children
+Dict~string,Any~ metadata
+find_children(node_type) MarkdownNode[]
+get_text_content() string
+get_line_range() tuple
+get_size() int
+is_leaf() bool
+contains_position(position) bool
}
class Position {
+int line
+int column
+int offset
}
class FencedBlock {
+string content
+string language
+string fence_type
+int fence_length
+int start_line
+int end_line
+int start_offset
+int end_offset
+int nesting_level
+bool is_closed
+string raw_content
+get_size() int
+is_valid() bool
+get_hash() string
}
MarkdownNode --> Position : "uses"
FencedBlock --> Position : "uses"
```

**Diagram sources**
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py#L58-L118)
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py#L217-L249)

**Section sources**
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py#L58-L118)
- [markdown_chunker/parser/types.py](file://markdown_chunker/parser/types.py#L217-L249)

## Understanding Chunks and Logical Blocks

### What is a Chunk?

A **chunk** represents a semantically meaningful fragment of a Markdown document that preserves context while fitting within size constraints. Each chunk contains not just the text content, but comprehensive metadata that describes its origin, structure, and relationships.

```mermaid
classDiagram
class Chunk {
+string content
+int start_line
+int end_line
+Dict~string,Any~ metadata
+size() int
+line_count() int
+content_type() string
+strategy() string
+language() string
+is_oversize() bool
+add_metadata(key, value) void
+get_metadata(key, default) Any
+get_section_path() string[]
+get_source_range() tuple
+get_section_id() string
+to_dict() Dict
+from_dict(data) Chunk
}
class ContentType {
<<enumeration>>
CODE
TEXT
LIST
TABLE
MIXED
HEADER
PREAMBLE
}
class StrategyType {
<<enumeration>>
CODE
MIXED
LIST
TABLE
STRUCTURAL
SENTENCES
}
Chunk --> ContentType : "has"
Chunk --> StrategyType : "created_by"
```

**Diagram sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L36-L321)

### Logical Block Preservation

The system distinguishes between different types of content blocks and applies appropriate preservation strategies:

| Block Type | Preservation Strategy | Reasoning |
|------------|----------------------|-----------|
| **Code Blocks** | Atomic preservation | Code integrity depends on complete context |
| **Tables** | Atomic preservation | Table structure broken by splitting |
| **Lists** | Hierarchical preservation | List items depend on parent-child relationships |
| **Headers** | Boundary preservation | Headers define document sections |
| **Paragraphs** | Semantic splitting | Can be split at natural boundaries |

### Chunk Properties and Metadata

Each chunk carries rich metadata that enables downstream applications to understand its context:

```mermaid
graph LR
A["Chunk"] --> B["Content"]
A --> C["Position Info"]
A --> D["Content Type"]
A --> E["Strategy Used"]
A --> F["Language Info"]
A --> G["Relationships"]
A --> H["Quality Metrics"]
C --> C1["start_line"]
C --> C2["end_line"]
C --> C3["size_bytes"]
D --> D1["content_type"]
D --> D2["language"]
E --> E1["strategy"]
E --> E2["allow_oversize"]
G --> G1["section_path"]
G --> G2["section_id"]
G --> G3["parent_header"]
H --> H1["complexity_score"]
H --> H2["quality_rating"]
```

**Diagram sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L36-L321)

**Section sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L36-L321)

## Content Analysis Metrics

### Fundamental Metrics

The content analysis system calculates comprehensive metrics that characterize document structure and content distribution:

```mermaid
graph TD
A["Content Analysis"] --> B["Basic Metrics"]
A --> C["Content Distribution"]
A --> D["Structural Elements"]
A --> E["Complexity Scores"]
B --> B1["total_chars"]
B --> B2["total_lines"]
B --> B3["total_words"]
C --> C1["code_ratio"]
C --> C2["text_ratio"]
C --> C3["list_ratio"]
C --> C4["table_ratio"]
D --> D1["header_count"]
D --> D2["code_block_count"]
D --> D3["list_count"]
D --> D4["table_count"]
E --> E1["complexity_score"]
E --> E2["max_header_depth"]
E --> E3["has_mixed_content"]
```

**Diagram sources**
- [markdown_chunker/parser/analyzer.py](file://markdown_chunker/parser/analyzer.py#L28-L499)

### Code Ratio Calculation

The code ratio metric determines the proportion of code content versus other content types:

```python
# Formula: code_chars / total_chars
code_ratio = code_chars / total_chars if total_chars > 0 else 0
```

**Thresholds for Strategy Selection:**
- **Code-heavy**: `code_ratio >= 0.7` → Code strategy
- **Mixed**: `0.3 <= code_ratio < 0.7` → Mixed strategy  
- **Text-heavy**: `code_ratio < 0.3` → Sentence strategy

### List Density Analysis

List density measures the concentration of list content relative to overall document size:

```python
# Formula: list_chars / total_chars
list_density = list_chars / total_chars if total_chars > 0 else 0
```

**Strategic Implications:**
- High list density (`> 0.6`) favors list strategy
- Moderate density (`0.3-0.6`) considered in mixed strategy
- Low density (`< 0.3`) ignored for list strategy

### Structural Complexity Scoring

The complexity score combines multiple factors to assess document intricacy:

```mermaid
flowchart TD
A["Complexity Calculation"] --> B["Structural Complexity"]
A --> C["Content Complexity"]
A --> D["Size Complexity"]
B --> B1["Header Depth"]
B --> B2["List Nesting"]
B --> B3["Table Presence"]
C --> C1["Code Ratio"]
C --> C2["Mixed Content"]
D --> D1["Document Size"]
B1 --> E["Max: 0.3"]
B2 --> E
B3 --> E
C1 --> F["Max: 0.4"]
C2 --> F
D1 --> G["Max: 0.3"]
E --> H["Complexity Score"]
F --> H
G --> H
```

**Diagram sources**
- [markdown_chunker/parser/analyzer.py](file://markdown_chunker/parser/analyzer.py#L245-L276)

**Section sources**
- [markdown_chunker/parser/analyzer.py](file://markdown_chunker/parser/analyzer.py#L28-L499)

## Strategy Scoring and Selection

### Strategy Selection Framework

The system employs a sophisticated selection mechanism that evaluates multiple strategies against content characteristics:

```mermaid
sequenceDiagram
participant CA as Content Analyzer
participant SS as Strategy Selector
participant S1 as Code Strategy
participant S2 as Mixed Strategy
participant S3 as Structural Strategy
participant S4 as Fallback Strategy
CA->>SS : Submit Content Analysis
SS->>S1 : Evaluate can_handle()
S1->>SS : Quality Score : 0.8
SS->>S2 : Evaluate can_handle()
S2->>SS : Quality Score : 0.6
SS->>S3 : Evaluate can_handle()
S3->>SS : Quality Score : 0.4
SS->>S4 : Evaluate can_handle()
S4->>SS : Quality Score : 0.2
SS->>SS : Select Best Strategy
SS->>CA : Strategy Recommendation
```

**Diagram sources**
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py#L58-L322)
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py#L169-L340)

### Strategy Metrics System

Each strategy produces comprehensive metrics for evaluation:

| Metric | Description | Range | Purpose |
|--------|-------------|-------|---------|
| `can_handle` | Strategy applicability | `true/false` | Determines eligibility |
| `quality_score` | Content fit assessment | `0.0-1.0` | Measures suitability |
| `priority` | Strategy precedence | `1-6` | Resolution for ties |
| `final_score` | Combined evaluation | `0.0-1.0` | Primary selection criterion |

### Threshold-Based Selection

The selection process uses configurable thresholds to determine strategy applicability:

```mermaid
flowchart TD
A["Content Analysis"] --> B{"Code Ratio >= 0.7?"}
B --> |Yes| C["Code Strategy"]
B --> |No| D{"Mixed Content?"}
D --> |Yes| E["Mixed Strategy"]
D --> |No| F{"List Ratio > 0.6?"}
F --> |Yes| G["List Strategy"]
F --> |No| H{"Table Ratio > 0.4?"}
H --> |Yes| I["Table Strategy"]
H --> |No| J{"Headers >= 3?"}
J --> |Yes| K["Structural Strategy"]
J --> |No| L["Sentences Strategy"]
C --> M["Apply Strategy"]
E --> M
G --> M
I --> M
K --> M
L --> M
```

**Diagram sources**
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py#L58-L322)

**Section sources**
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py#L58-L322)

## Configuration Profiles

### Predefined Configuration Profiles

The system provides specialized configuration profiles optimized for different use cases:

| Profile | Use Case | Key Characteristics |
|---------|----------|-------------------|
| `for_code_heavy()` | API documentation, tutorials | Large chunks, aggressive code detection |
| `for_structured_docs()` | User manuals, documentation | Medium chunks, header preservation |
| `for_dify_rag()` | RAG systems | Balanced chunks, overlap support |
| `for_chat_context()` | Chat/LLM contexts | Small chunks, high overlap |
| `for_search_indexing()` | Search applications | Small chunks, granular content |

### Configuration Parameter Impact

Each configuration parameter affects chunking behavior differently:

```mermaid
graph TD
A["Configuration Parameters"] --> B["Size Control"]
A --> C["Strategy Selection"]
A --> D["Preservation Rules"]
A --> E["Performance Tuning"]
B --> B1["max_chunk_size"]
B --> B2["min_chunk_size"]
B --> B3["target_chunk_size"]
C --> C1["code_ratio_threshold"]
C --> C2["list_count_threshold"]
C --> C3["table_count_threshold"]
D --> D1["preserve_code_blocks"]
D --> D2["preserve_tables"]
D --> D3["preserve_list_hierarchy"]
E --> E1["enable_overlap"]
E --> E2["overlap_size"]
E --> E3["enable_streaming"]
```

**Diagram sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L498-L1061)

### Custom Configuration Examples

**Code Documentation Profile:**
```python
config = ChunkConfig(
    max_chunk_size=2048,      # Smaller for atomic code blocks
    min_chunk_size=128,       # Minimum code block size
    overlap_size=100,         # Minimal overlap
    code_ratio_threshold=0.8, # Aggressive code detection
    preserve_code_blocks=True, # Keep code atomic
    list_count_threshold=8,   # Handle dense lists
    table_count_threshold=5   # Handle complex tables
)
```

**Chat Context Profile:**
```python
config = ChunkConfig(
    max_chunk_size=1536,      # Fits LLM context windows
    min_chunk_size=200,       # Minimum meaningful content
    overlap_size=200,         # Preserve context
    enable_overlap=True,      # Context preservation
    code_ratio_threshold=0.5, # Balanced approach
    list_count_threshold=4,   # Moderate list handling
    table_count_threshold=2   # Simple table support
)
```

**Section sources**
- [markdown_chunker/chunker/types.py](file://markdown_chunker/chunker/types.py#L498-L1061)

## Header Paths and Metadata Enrichment

### Hierarchical Header Path Construction

The system builds comprehensive header paths that enable precise navigation and semantic understanding:

```mermaid
graph TD
A["Document Structure"] --> B["Root Document"]
B --> C["H1: Introduction"]
B --> D["H1: Main Content"]
B --> E["H1: Conclusion"]
C --> F["H2: Background"]
C --> G["H2: Motivation"]
D --> H["H2: Theory"]
D --> I["H2: Practice"]
H --> J["H3: Concepts"]
H --> K["H3: Applications"]
I --> L["H3: Examples"]
I --> M["H3: Exercises"]
style A fill:#e1f5fe
style B fill:#f3e5f5
style C fill:#e8f5e8
style D fill:#e8f5e8
style E fill:#e8f5e8
style F fill:#fff3e0
style G fill:#fff3e0
style H fill:#fff3e0
style I fill:#fff3e0
style J fill:#fce4ec
style K fill:#fce4ec
style L fill:#fce4ec
style M fill:#fce4ec
```

**Diagram sources**
- [markdown_chunker/chunker/strategies/structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L22-L53)

### Metadata Enrichment Features

The system enriches chunks with comprehensive metadata for downstream applications:

| Metadata Field | Purpose | Example Value |
|----------------|---------|---------------|
| `section_path` | Hierarchical navigation | `["Introduction", "Setup"]` |
| `section_id` | Unique identification | `"introduction-setup"` |
| `header_level` | Structural depth | `2` |
| `header_text` | Title content | `"Installation Guide"` |
| `parent_header_path` | Parent relationships | `["Introduction"]` |
| `has_subsections` | Structural awareness | `true` |
| `content_type` | Chunk categorization | `"code"`, `"text"`, `"list"` |

### Phase 2 Semantic Quality Improvements

The system implements advanced semantic quality features in Phase 2:

```mermaid
sequenceDiagram
participant PS as Phase 1 Parser
participant SB as Section Builder
participant CS as Chunk Strategy
participant CE as Chunk Enricher
PS->>SB : AST with positions
SB->>SB : Build section hierarchy
SB->>CS : Section-aware boundaries
CS->>CE : Enrich with semantic metadata
CE->>CE : Add header paths, IDs
CE->>CS : Return enriched chunks
```

**Diagram sources**
- [markdown_chunker/chunker/strategies/structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L77-L102)

**Section sources**
- [markdown_chunker/chunker/strategies/structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L22-L53)

## Idempotent Processing

### Definition and Importance

**Idempotent processing** ensures that applying the chunker multiple times to the same document produces identical results, maintaining consistency and reliability.

### Implementation Strategies

The system achieves idempotency through several mechanisms:

```mermaid
flowchart TD
A["Input Document"] --> B["Deterministic Analysis"]
B --> C["Consistent Strategy Selection"]
C --> D["Predictable Chunk Boundaries"]
D --> E["Identical Output"]
B --> B1["Fixed Random Seeds"]
B --> B2["Deterministic Sorting"]
B --> B3["Stable Position Calculations"]
C --> C1["Threshold-Based Selection"]
C --> C2["Priority-Ordered Evaluation"]
C --> C3["Consistent Tie-Breaking"]
D --> D1["Position-Aware Splitting"]
D --> D2["Atomic Element Preservation"]
D --> D3["Overlap Consistency"]
```

### Testing Idempotency

The system includes comprehensive tests to verify idempotent behavior:

```python
# Example idempotency test pattern
def test_idempotence():
    initial_result = chunker.chunk(document)
    second_result = chunker.chunk(document)
    
    # Compare results
    assert len(initial_result.chunks) == len(second_result.chunks)
    for chunk1, chunk2 in zip(initial_result.chunks, second_result.chunks):
        assert chunk1.content == chunk2.content
        assert chunk1.start_line == chunk2.start_line
        assert chunk1.end_line == chunk2.end_line
        assert chunk1.metadata == chunk2.metadata
```

**Section sources**
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py#L98-L101)

## Practical Implementation Examples

### Basic Usage Patterns

The system provides multiple interfaces for different use cases:

```python
# Simple chunking with default configuration
chunker = MarkdownChunker()
chunks = chunker.chunk(markdown_text)

# Chunking with analysis and metrics
result = chunker.chunk_with_analysis(markdown_text)
print(f"Strategy used: {result.strategy_used}")
print(f"Complexity score: {result.complexity_score}")

# Custom configuration
config = ChunkConfig(max_chunk_size=1000, enable_overlap=True)
chunker = MarkdownChunker(config)
chunks = chunker.chunk(markdown_text)
```

### Strategy Override Examples

Manually specifying strategies for specific use cases:

```python
# Force code strategy for code-heavy documents
chunks = chunker.chunk(markdown_text, strategy="code")

# Force structural strategy for well-structured documents  
chunks = chunker.chunk(markdown_text, strategy="structural")

# Force sentences strategy for simple text
chunks = chunker.chunk(markdown_text, strategy="sentences")
```

### Configuration Profile Usage

Using predefined profiles for common scenarios:

```python
# API documentation optimization
config = ChunkConfig.for_api_docs()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(api_documentation)

# Chat context optimization
config = ChunkConfig.for_chat_context()
chunker = MarkdownChunker(config)
chunks = chunker.chunk(chat_documentation)
```

**Section sources**
- [examples/basic_usage.py](file://examples/basic_usage.py#L14-L364)
- [examples/api_usage.py](file://examples/api_usage.py#L16-L356)

## Advanced Concepts

### Multi-Strategy Coordination

The system coordinates multiple strategies through a sophisticated orchestration framework:

```mermaid
classDiagram
class ChunkingOrchestrator {
+ChunkConfig config
+StrategySelector strategy_selector
+FallbackManager fallback_manager
+ParserInterface parser
+chunk_with_strategy(md_text, strategy_override) ChunkingResult
+_run_stage1_analysis(md_text) Stage1Results
+_select_and_apply_strategy(md_text, stage1_results) ChunkingResult
}
class StrategySelector {
+BaseStrategy[] strategies
+string mode
+select_strategy(analysis, config) BaseStrategy
+get_applicable_strategies(analysis, config) List
+validate_strategies() List
}
class FallbackManager {
+execute_with_fallback(md_text, stage1_results, strategy) ChunkingResult
+get_fallback_strategies() List
}
ChunkingOrchestrator --> StrategySelector : "uses"
ChunkingOrchestrator --> FallbackManager : "uses"
StrategySelector --> BaseStrategy : "manages"
```

**Diagram sources**
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py#L23-L340)
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py#L19-L322)

### Error Handling and Recovery

The system implements robust error handling with fallback mechanisms:

```mermaid
flowchart TD
A["Chunking Attempt"] --> B{"Primary Strategy Success?"}
B --> |Yes| C["Return Results"]
B --> |No| D["Log Error"]
D --> E["Try Fallback Strategy"]
E --> F{"Fallback Success?"}
F --> |Yes| G["Return Fallback Results"]
F --> |No| H["Try Emergency Strategy"]
H --> I{"Emergency Success?"}
I --> |Yes| J["Return Emergency Results"]
I --> |No| K["Return Error"]
C --> L["Success"]
G --> L
J --> L
K --> M["Failure"]
```

**Diagram sources**
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py#L276-L340)

### Performance Optimization

The system includes several performance optimization features:

| Optimization | Purpose | Implementation |
|--------------|---------|----------------|
| **Streaming** | Memory efficiency for large documents | Configurable threshold (10MB default) |
| **Overlap Management** | Context preservation | Configurable overlap size and percentage |
| **Lazy Loading** | Reduced memory footprint | On-demand AST construction |
| **Caching** | Repeated analysis optimization | Memoized analysis results |

**Section sources**
- [markdown_chunker/chunker/orchestrator.py](file://markdown_chunker/chunker/orchestrator.py#L23-L340)
- [markdown_chunker/chunker/selector.py](file://markdown_chunker/chunker/selector.py#L19-L322)