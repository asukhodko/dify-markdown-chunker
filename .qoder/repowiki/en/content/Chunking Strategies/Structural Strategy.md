# Structural Strategy

<cite>
**Referenced Files in This Document**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py)
- [selector.py](file://markdown_chunker/chunker/selector.py)
- [section_builder.py](file://markdown_chunker/chunker/section_builder.py)
- [types.py](file://markdown_chunker/chunker/types.py)
- [base.py](file://markdown_chunker/chunker/strategies/base.py)
- [basic_usage.py](file://examples/basic_usage.py)
- [structural.md](file://tests/fixtures/structural.md)
- [mixed.md](file://tests/fixtures/mixed.md)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Purpose and Philosophy](#purpose-and-philosophy)
3. [Core Architecture](#core-architecture)
4. [Implementation Details](#implementation-details)
5. [Strategy Selection Logic](#strategy-selection-logic)
6. [Header Detection and Hierarchy Building](#header-detection-and-hierarchy-building)
7. [Section Creation and Processing](#section-creation-and-processing)
8. [Chunk Generation and Optimization](#chunk-generation-and-optimization)
9. [Phase 2 Implementation](#phase-2-implementation)
10. [Common Issues and Mitigation](#common-issues-and-mitigation)
11. [Configuration and Usage Guidelines](#configuration-and-usage-guidelines)
12. [Performance Considerations](#performance-considerations)
13. [Best Practices](#best-practices)

## Introduction

The Structural Strategy is a sophisticated chunking approach designed specifically for Markdown documents with clear hierarchical structure. Unlike other strategies that focus on content type (code, lists, tables) or sentence boundaries, the Structural Strategy prioritizes document organization by leveraging header hierarchies to create semantically meaningful chunks that preserve the natural structure of well-organized documentation.

This strategy transforms the way we think about document chunking by recognizing that many technical documents, API references, user manuals, and educational materials are structured around headers that define logical sections and subsections. By respecting these structural boundaries, the strategy ensures that chunks remain coherent and maintain their informational integrity.

## Purpose and Philosophy

### Core Philosophy

The Structural Strategy operates on the principle that **document structure is the primary organizing principle** for many types of content. When a document has a clear header hierarchy (H1-H6), these headers naturally define logical sections that should be treated as cohesive units during chunking.

### Ideal Use Cases

The strategy excels in scenarios where:
- Documents have 3+ headers with multiple levels of hierarchy
- Content is well-organized with clear section boundaries
- Preservation of document structure is crucial for understanding
- The document serves as reference material (API docs, manuals, specifications)
- Users need to navigate between related sections

### Key Benefits

1. **Semantic Coherence**: Chunks maintain logical relationships between related content
2. **Structure Preservation**: Natural document boundaries are respected
3. **Navigation Support**: Header path information enables intelligent navigation
4. **Context Maintenance**: Related content stays together in the same chunk
5. **Hierarchical Awareness**: Deep structure is preserved through metadata

## Core Architecture

The Structural Strategy follows a multi-phase approach that combines header detection, hierarchy building, section creation, and intelligent chunking:

```mermaid
flowchart TD
A["Input Markdown"] --> B["Stage 1 Analysis"]
B --> C["Header Detection"]
C --> D["Hierarchy Building"]
D --> E["Section Creation"]
E --> F["Chunk Processing"]
F --> G["Optimization"]
G --> H["Final Chunks"]
C --> C1["Stage 1 Headers"]
C --> C2["Manual Detection"]
C1 --> D
C2 --> D
D --> D1["Parent-Child Relationships"]
D --> D2["Depth Calculation"]
D1 --> E
D2 --> E
E --> E1["Boundary Definition"]
E --> E2["Content Extraction"]
E1 --> F
E2 --> F
F --> F1["Size Validation"]
F --> F2["Large Section Splitting"]
F1 --> G
F2 --> G
G --> G1["Small Chunk Combination"]
G --> G2["Metadata Enrichment"]
G1 --> H
G2 --> H
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L198-L244)

## Implementation Details

### Strategy Class Structure

The Structural Strategy inherits from `BaseStrategy` and implements the complete chunking pipeline:

```mermaid
classDiagram
class BaseStrategy {
<<abstract>>
+name : str
+priority : int
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) Chunk[]
+get_metrics(analysis, config) StrategyMetrics
+_create_chunk(content, start_line, end_line, **metadata) Chunk
+_validate_chunks(chunks, config) Chunk[]
}
class StructuralStrategy {
+name : "structural"
+priority : 5
+HEADER_PATTERNS : List[str]
+section_builder : SectionBuilder
+_phase2_available : bool
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) Chunk[]
+_extract_headers(content, stage1_results) HeaderInfo[]
+_detect_headers_manual(content) HeaderInfo[]
+_build_hierarchy(headers) HeaderInfo[]
+_create_sections(content, headers) Section[]
+_process_sections(sections, config) Chunk[]
+_split_large_section(section, config) Chunk[]
+_combine_small_chunks(chunks, config) Chunk[]
+_build_header_path(header) str
}
class HeaderInfo {
+level : int
+text : str
+line : int
+position : int
+parent : HeaderInfo
+children : HeaderInfo[]
}
class Section {
+header : HeaderInfo
+content : str
+start_line : int
+end_line : int
+size : int
+has_subsections : bool
+subsections : Section[]
}
BaseStrategy <|-- StructuralStrategy
StructuralStrategy --> HeaderInfo : creates
StructuralStrategy --> Section : processes
Section --> HeaderInfo : contains
Section --> Section : hierarchical
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L22-L49)
- [base.py](file://markdown_chunker/chunker/strategies/base.py#L16-L94)

### Header Detection Patterns

The strategy supports multiple header formats commonly found in Markdown documents:

| Pattern Type | Regex Pattern | Example | Level Determination |
|--------------|---------------|---------|-------------------|
| ATX Headers | `^(#{1,6})\s+(.+?)(?:\s*#*)?$` | `# Title`, `## Section`, `### Subsection` | Number of `#` characters |
| Setext Headers (H1) | `^(.+?)\n([=]{3,})$` | `Title<br>=====` | Underlined with `===` |
| Setext Headers (H2) | `^(.+?)\n([-]{3,})$` | `Title<br>-----` | Underlined with `---` |

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L69-L75)

### Priority and Quality Scoring

The strategy operates with medium-low priority (5) and calculates quality based on several factors:

```mermaid
flowchart TD
A["Content Analysis"] --> B["Header Count"]
A --> C["Max Depth"]
A --> D["Code Ratio"]
A --> E["Hierarchy Presence"]
B --> B1["≥10: +0.5"]
B --> B2["≥5: +0.4"]
B --> B3["≥3: +0.3"]
C --> C1["≥4: +0.3"]
C --> C2["≥3: +0.2"]
C --> C3[">1: +0.1"]
D --> D1[">0.5: ×0.5 penalty"]
D --> D2["≤0.5: no penalty"]
E --> E1["+0.2 bonus if present"]
B1 --> F["Quality Score"]
B2 --> F
B3 --> F
C1 --> F
C2 --> F
C3 --> F
D2 --> F
E1 --> F
F --> G["Final Score: min(1.0, score)"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L140-L196)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L140-L196)

## Strategy Selection Logic

### Can Handle Evaluation

The strategy determines applicability based on two primary criteria:

1. **Minimum Header Count**: At least `header_count_threshold` headers (default: 3)
2. **Maximum Header Depth**: Document must have multiple levels of hierarchy (`max_header_depth > 1`)

### Automatic Selection Process

The StrategySelector evaluates strategies in priority order, selecting the first one that can handle the content:

```mermaid
sequenceDiagram
participant CS as Content Analysis
participant SS as Strategy Selector
participant STR as Structural Strategy
participant Other as Other Strategies
CS->>SS : Provide content analysis
SS->>STR : Check can_handle(CS, Config)
STR->>STR : Evaluate header_count >= 3
STR->>STR : Check max_header_depth > 1
STR-->>SS : Return can_handle result
SS->>Other : Skip other strategies (priority 5)
SS->>STR : Select Structural Strategy
STR->>STR : Calculate quality score
STR-->>SS : Return quality metrics
SS-->>CS : Strategy selected with score
```

**Diagram sources**
- [selector.py](file://markdown_chunker/chunker/selector.py#L79-L98)
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L113-L138)

**Section sources**
- [selector.py](file://markdown_chunker/chunker/selector.py#L79-L98)
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L113-L138)

## Header Detection and Hierarchy Building

### Dual Detection Approach

The strategy employs a two-tier header detection system:

#### Phase 1: Stage 1 Results Utilization
When Stage 1 processing is available, the strategy first attempts to use pre-detected headers from the parsing phase:

```mermaid
flowchart TD
A["Content Input"] --> B{"Stage 1 Results Available?"}
B --> |Yes| C["Extract Headers from Elements"]
B --> |No| D["Manual Detection"]
C --> C1["Use stage1_results.elements.headers"]
C1 --> C2["Convert to HeaderInfo Objects"]
C2 --> E["Sort by Position"]
D --> D1["Regex Pattern Matching"]
D1 --> D2["ATX Header Detection"]
D2 --> D3["Setext Header Detection"]
D3 --> E
E --> F["Hierarchy Building"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L245-L275)

#### Phase 2: Manual Detection Fallback
When Stage 1 results are unavailable or headers are missing, the strategy falls back to manual detection using regex patterns:

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L245-L322)

### Hierarchy Building Algorithm

The hierarchy construction uses a stack-based approach to establish parent-child relationships:

```mermaid
flowchart TD
A["Sorted Headers"] --> B["Initialize Empty Stack"]
B --> C["Process Each Header"]
C --> D{"Current Header Level"}
D --> E{"Stack Top Level"}
E --> F{"Level >= Current Level?"}
F --> |Yes| G["Pop Stack"]
F --> |No| H{"Stack Empty?"}
G --> E
H --> |No| I["Set Parent = Stack Top"]
H --> |Yes| J["Add to Root Headers"]
I --> K["Add to Parent's Children"]
K --> L["Push to Stack"]
J --> L
L --> M{"More Headers?"}
M --> |Yes| C
M --> |No| N["Return Root Headers"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L324-L356)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L324-L356)

### Header Path Construction

The strategy builds hierarchical paths for navigation and metadata enrichment:

```mermaid
flowchart LR
A["Grandchild Header"] --> B["Get Parent"]
B --> C["Get Grandparent"]
C --> D["Build Path Array"]
D --> E["Reverse Array"]
E --> F["Join with '/'"]
F --> G["'/Root/Parent/Child'"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L760-L779)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L760-L779)

## Section Creation and Processing

### Section Definition

Each section is defined by a header and encompasses all content up to the next header of the same or higher level:

```mermaid
classDiagram
class Section {
+HeaderInfo header
+str content
+int start_line
+int end_line
+int size
+bool has_subsections
+Section[] subsections
+__post_init__()
}
class HeaderInfo {
+int level
+str text
+int line
+int position
+HeaderInfo parent
+HeaderInfo[] children
}
Section --> HeaderInfo : contains
Section --> Section : hierarchical
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L38-L52)

### Section Creation Process

The strategy creates sections by defining boundaries between headers:

```mermaid
flowchart TD
A["Headers List"] --> B["Iterate Through Headers"]
B --> C["Determine Start Position"]
C --> D["Find Next Header Position"]
D --> E{"Is Last Header?"}
E --> |No| F["Set End Position = Next Header Start"]
E --> |Yes| G["Set End Position = Document End"]
F --> H["Extract Content Slice"]
G --> H
H --> I["Check for Subsections"]
I --> J["Create Section Object"]
J --> K["Store in Sections List"]
K --> L{"More Headers?"}
L --> |Yes| B
L --> |No| M["Return Sections"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L359-L419)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L359-L419)

## Chunk Generation and Optimization

### Large Section Handling

When sections exceed the maximum chunk size, the strategy employs intelligent splitting:

```mermaid
flowchart TD
A["Large Section Detected"] --> B{"Has Subsections?"}
B --> |Yes| C["Try Subsection Splitting"]
B --> |No| D["Split by Paragraphs"]
C --> C1["Process Each Subsection"]
C1 --> C2{"Subsection Fits?"}
C2 --> |Yes| C3["Create Single Chunk"]
C2 --> |No| C4["Recursive Split"]
C3 --> C5["Collect All Chunks"]
C4 --> C5
D --> D1["Preserve Code Blocks"]
D1 --> D2["Split by Paragraph Boundaries"]
D2 --> D3["Handle Atomic Elements"]
D3 --> D4["Create Final Chunks"]
C5 --> E["Combine Small Chunks"]
D4 --> E
E --> F["Apply Size Constraints"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L485-L532)

### Small Chunk Combination

To avoid creating too many small chunks, the strategy combines adjacent chunks when beneficial:

```mermaid
flowchart TD
A["Chunk List"] --> B["Initialize Current Chunk"]
B --> C["Process Each Chunk"]
C --> D{"Current Chunk < Min Size?"}
D --> |No| E["Add Current to Results"]
D --> |Yes| F{"Can Combine?"}
F --> |No| E
F --> |Yes| G{"Combined ≤ Max Size?"}
G --> |No| E
G --> |Yes| H["Merge with Current"]
H --> I["Update Metadata"]
I --> J["Continue"]
E --> K["Reset Current Chunk"]
K --> J
J --> L{"More Chunks?"}
L --> |Yes| C
L --> |No| M["Add Final Current Chunk"]
M --> N["Return Combined Chunks"]
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L707-L758)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L707-L758)

### Metadata Enrichment

Each chunk receives comprehensive metadata for navigation and context:

| Metadata Field | Description | Example Value |
|----------------|-------------|---------------|
| `header_level` | Numeric header level (1-6) | `2` |
| `header_text` | Header title text | `"Installation"` |
| `header_path` | Full hierarchical path | `"/Documentation/Getting Started/Installation"` |
| `has_subsections` | Whether section has child sections | `true` |
| `parent_header_path` | Path to parent section | `"/Documentation/Getting Started"` |
| `section_part` | Indicates chunk is part of larger section | `true` |
| `original_section_size` | Size of original section | `1500` |

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L452-L483)

## Phase 2 Implementation

### Section Builder Integration

Phase 2 introduces the SectionBuilder for enhanced semantic quality:

```mermaid
classDiagram
class SectionBuilder {
+block_id_counter : int
+build_sections(ast, boundary_level) Section[]
+_walk_ast(node) MarkdownNode[]
+_create_section(header_node, header_stack, level, text) Section
+_create_root_section() Section
+_create_header_block(node) LogicalBlock
+_create_content_block(node) LogicalBlock
+_render_node_to_markdown(node) str
}
class Section {
+block_type : str
+content : str
+ast_node : MarkdownNode
+start_offset : int
+end_offset : int
+start_line : int
+end_line : int
+is_atomic : bool
+metadata : dict
+header : LogicalBlock
+header_level : int
+header_text : str
+header_path : str[]
+content_blocks : LogicalBlock[]
}
class LogicalBlock {
+block_type : str
+content : str
+ast_node : MarkdownNode
+start_offset : int
+end_offset : int
+start_line : int
+end_line : int
+is_atomic : bool
+metadata : dict
}
SectionBuilder --> Section : creates
Section --> LogicalBlock : contains
```

**Diagram sources**
- [section_builder.py](file://markdown_chunker/chunker/section_builder.py#L43-L341)

### Enhanced Chunking Pipeline

Phase 2 provides improved chunking through AST-based section building:

```mermaid
sequenceDiagram
participant PS as Phase 1 Strategy
participant SB as Section Builder
participant AST as AST Tree
participant SC as Section Chunks
PS->>SB : Request section-aware chunking
SB->>AST : Traverse AST nodes
AST-->>SB : Return ordered nodes
SB->>SB : Build section hierarchy
SB->>SC : Create semantic sections
SC-->>PS : Return enriched chunks
```

**Diagram sources**
- [section_builder.py](file://markdown_chunker/chunker/section_builder.py#L62-L130)

**Section sources**
- [section_builder.py](file://markdown_chunker/chunker/section_builder.py#L62-L130)

## Common Issues and Mitigation

### Issue 1: Large Sections with No Subsections

**Problem**: A section is too large to fit in a single chunk but lacks subsections for splitting.

**Solution**: The strategy falls back to paragraph-based splitting while preserving atomic elements:

```mermaid
flowchart TD
A["Large Section"] --> B["Check for Subsections"]
B --> C{"Has Subsections?"}
C --> |Yes| D["Split by Subsections"]
C --> |No| E["Split by Paragraphs"]
E --> F["Preserve Code Blocks"]
F --> G["Split at Paragraph Boundaries"]
G --> H["Handle Oversized Elements"]
H --> I["Create Final Chunks"]
D --> J["Process Each Subsection"]
J --> K{"Subsection Fits?"}
K --> |Yes| L["Single Chunk"]
K --> |No| M["Recursive Split"]
M --> L
L --> I
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L485-L532)

### Issue 2: Deeply Nested Structures

**Problem**: Documents with excessive header nesting can lead to complex chunking decisions.

**Solution**: The strategy maintains hierarchy awareness through metadata and provides flexible boundary levels:

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L485-L532)

### Issue 3: Mixed Content in Sections

**Problem**: Sections containing code blocks, tables, and text require careful handling to avoid breaking atomic elements.

**Solution**: The strategy preserves atomic elements as single units while intelligently splitting surrounding content:

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L534-L611)

## Configuration and Usage Guidelines

### Recommended Configuration Profiles

#### For Structured Documentation
```python
config = ChunkConfig.for_structured_docs()
# Optimized for: Well-organized docs with clear sections
# Settings: header_count_threshold=2, smaller chunks, overlap=150
```

#### For API Documentation
```python
config = ChunkConfig.for_code_heavy()
# Optimized for: API references with code examples
# Settings: header_count_threshold=3, larger chunks, overlap=300
```

### Force Strategy Selection

While the strategy selector automatically chooses the best approach, you can force the Structural Strategy:

```python
# Force structural strategy regardless of content analysis
chunks = chunker.chunk(content, strategy="structural")

# Or use with specific configuration
config = ChunkConfig(
    header_count_threshold=2,  # More aggressive structural detection
    max_chunk_size=3000,       # Medium-sized chunks
    overlap_size=150           # Moderate overlap
)
chunks = chunker.chunk(content, config=config, strategy="structural")
```

### When to Force Structural Strategy

Force the Structural Strategy when:
- Document has clear header hierarchy but low header count
- Content analysis incorrectly identifies document type
- Specific navigation requirements demand structure preservation
- Testing or debugging with known structured content

**Section sources**
- [types.py](file://markdown_chunker/chunker/types.py#L740-L781)

## Performance Considerations

### Memory Usage

The Structural Strategy's memory consumption depends on:
- **Header Count**: More headers require more memory for hierarchy storage
- **Section Complexity**: Deep hierarchies increase memory overhead
- **Content Size**: Larger documents require more processing capacity

### Processing Time

Processing time scales with:
- **Document Length**: Linear scaling with content size
- **Header Density**: More headers increase parsing complexity
- **Hierarchy Depth**: Deeper structures require more tree traversal

### Optimization Strategies

1. **Early Termination**: Stop processing when chunks meet requirements
2. **Lazy Loading**: Process sections only when needed
3. **Caching**: Cache header detection results for repeated processing
4. **Streaming**: Use streaming mode for very large documents

## Best Practices

### Document Preparation

1. **Clear Header Structure**: Use consistent header levels throughout the document
2. **Meaningful Titles**: Ensure header text accurately describes content
3. **Logical Organization**: Arrange headers in a natural reading order
4. **Appropriate Depth**: Limit header nesting to 4-6 levels for readability

### Configuration Tuning

1. **Adjust Thresholds**: Modify `header_count_threshold` based on document characteristics
2. **Size Balancing**: Balance `max_chunk_size` and `min_chunk_size` for optimal results
3. **Overlap Settings**: Use moderate overlap (10-20%) for RAG applications
4. **Priority Management**: Understand how strategy priorities affect selection

### Metadata Utilization

1. **Navigation**: Use `header_path` for intelligent document navigation
2. **Filtering**: Leverage `header_level` for content categorization
3. **Context**: Utilize `parent_header_path` for hierarchical browsing
4. **Quality**: Monitor chunk sizes and combine small chunks for efficiency

### Integration Patterns

1. **Fallback Strategy**: Always configure a fallback strategy for edge cases
2. **Validation**: Validate chunk metadata for consistency
3. **Monitoring**: Track strategy selection and performance metrics
4. **Testing**: Test with representative document samples

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L113-L138)