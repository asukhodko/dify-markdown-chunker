# Chunking Strategies

<cite>
**Referenced Files in This Document**   
- [base.py](file://markdown_chunker/chunker/strategies/base.py)
- [code_strategy.py](file://markdown_chunker/chunker/strategies/code_strategy.py)
- [mixed_strategy.py](file://markdown_chunker/chunker/strategies/mixed_strategy.py)
- [sentences_strategy.py](file://markdown_chunker/chunker/strategies/sentences_strategy.py)
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py)
- [table_strategy.py](file://markdown_chunker/chunker/strategies/table_strategy.py)
- [selector.py](file://markdown_chunker/chunker/selector.py)
</cite>

## Update Summary
**Changes Made**   
- Removed the unused ListStrategy from the documentation
- Merged Code and Mixed strategies into a new CodeAwareStrategy
- Updated all references to the old strategies with the new CodeAwareStrategy
- Removed the List Strategy section from the Table of Contents and document
- Updated the Strategy Selection section to reflect the new strategy count and priorities

## Table of Contents
1. [Introduction](#introduction)
2. [CodeAware Strategy](#codeaware-strategy)
3. [Table Strategy](#table-strategy)
4. [Structural Strategy](#structural-strategy)
5. [Sentences Strategy](#sentences-strategy)
6. [Strategy Selection](#strategy-selection)
7. [Common Issues and Mitigations](#common-issues-and-mitigations)
8. [Strategy Selection Guidance](#strategy-selection-guidance)

## Introduction
The Markdown Chunker implements a sophisticated strategy-based system for splitting Markdown documents into meaningful chunks. Each strategy is designed to handle specific document types and content patterns, preserving semantic relationships and context while respecting size constraints. The system uses a priority-based selection mechanism to automatically choose the most appropriate strategy based on content analysis. This document details each chunking strategy, explaining its purpose, implementation logic, ideal use cases, and behavior with concrete examples from the codebase.

**Section sources**
- [base.py](file://markdown_chunker/chunker/strategies/base.py#L1-L380)

## CodeAware Strategy
The CodeAware Strategy is a unified approach that combines the functionality of the former Code and Mixed strategies, specializing in handling documents with code content while maintaining context with surrounding text. This strategy is ideal for technical documentation, API references, and tutorials with code examples.

### Purpose and Logic
The CodeAware Strategy identifies code blocks and segments content around them, creating separate chunks for code and associated explanatory text. Code blocks are kept atomic (never split) to preserve their integrity, while large text segments may be split at sentence boundaries. The strategy extracts metadata such as programming language, function names, and class names from code blocks to enhance context. It also handles mixed content types by detecting and preserving other elements like lists and tables.

### Implementation Details
The strategy traverses the AST by first extracting code blocks from the Stage 1 results, then segmenting the content around these blocks. It creates alternating text and code segments, processing each according to its type. Code segments are always kept intact, while text segments are split only if they exceed the maximum chunk size. The strategy also detects and preserves other content elements like lists and tables.

### Context Preservation
The strategy preserves context by grouping explanatory text with relevant code blocks. When a code block is surrounded by text, the text is included in the same chunk or adjacent chunks to maintain the relationship between code and explanation.

### Edge Cases
The strategy handles edge cases such as unclosed code fences by attempting to reconstruct the complete code block from the content. It also handles multiple programming languages within a single document by detecting language-specific patterns in the code content.

### Strategy-Specific Parameters
- `code_ratio_threshold`: Minimum ratio of code to total content (default: 0.7)
- `min_code_blocks`: Minimum number of code blocks (default: 3)
- `allow_oversize`: Whether to allow chunks larger than the maximum size for atomic code blocks

```mermaid
classDiagram
class CodeAwareStrategy {
+name : str = "code_aware"
+priority : int = 1
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) List[Chunk]
-extract_code_blocks(stage1_results) List[FencedBlock]
-segment_around_code_blocks(content, code_blocks) List[CodeSegment]
-process_segments(segments, config) List[Chunk]
-create_code_chunk(segment, config) Chunk
-create_text_chunk(segment, config) Chunk
-split_text_segment(segment, config) List[Chunk]
-detect_language(code_content) Optional[str]
-extract_function_names(code_content, language) List[str]
-extract_class_names(code_content, language) List[str]
}
class CodeSegment {
+type : str
+content : str
+start_line : int
+end_line : int
+language : Optional[str]
+is_fenced : bool
+function_names : Optional[List[str]]
+class_names : Optional[List[str]]
}
CodeAwareStrategy --> CodeSegment : "creates"
```

**Diagram sources**
- [code_strategy.py](file://markdown_chunker/chunker/strategies/code_strategy.py#L42-L625)
- [mixed_strategy.py](file://markdown_chunker/chunker/strategies/mixed_strategy.py#L75-L849)

**Section sources**
- [code_strategy.py](file://markdown_chunker/chunker/strategies/code_strategy.py#L1-L625)
- [mixed_strategy.py](file://markdown_chunker/chunker/strategies/mixed_strategy.py#L1-L849)

## Table Strategy
The Table Strategy preserves table structure and handles large tables by splitting rows while duplicating headers for readability. This strategy is ideal for documents with extensive tabular data such as specifications, API documentation, and data reports.

### Purpose and Logic
The Table Strategy detects markdown tables and processes them into chunks, preserving the table structure and formatting. For large tables, it splits by rows while duplicating headers in each chunk. When splitting, it duplicates the header and separator in each chunk.

### Implementation Details
The strategy traverses the AST by detecting tables using regex patterns that match table headers, separators, and rows. It creates chunks from tables, keeping small tables intact and splitting large tables by rows. When splitting, it duplicates the header and separator in each chunk.

### Context Preservation
The strategy preserves context by duplicating table headers in each chunk when a table is split. This ensures that each chunk contains the column names, making the data readable and understandable even when separated from the original table header.

### Edge Cases
The strategy handles edge cases such as tables without headers by still preserving the structure. It also handles wide tables that might exceed chunk size by allowing oversize chunks when necessary.

### Strategy-Specific Parameters
- `table_count_threshold`: Minimum number of tables (default: 3)
- `table_ratio_threshold`: Minimum ratio of table content (default: 0.4)
- `max_chunk_size`: Maximum size for each chunk

```mermaid
classDiagram
class TableStrategy {
+name : str = "table"
+priority : int = 2
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) List[Chunk]
-detect_tables(content) List[TableInfo]
-is_table_header(line) bool
-is_table_separator(line) bool
-is_table_row(line) bool
-create_chunks_from_tables(tables, content, config) List[Chunk]
-split_table_rows(table, max_chunk_size) List[TableRowGroup]
-create_table_chunk(table, config) Chunk
-create_table_group_chunk(group, config) Chunk
}
class TableInfo {
+header : str
+separator : str
+rows : List[str]
+start_line : int
+end_line : int
+column_count : int
+get_full_content() str
+calculate_size() int
}
class TableRowGroup {
+header : str
+separator : str
+rows : List[str]
+start_line : int
+end_line : int
+part_number : int
+total_parts : int
+total_rows : int
}
TableStrategy --> TableInfo : "creates"
TableStrategy --> TableRowGroup : "creates"
```

**Diagram sources**
- [table_strategy.py](file://markdown_chunker/chunker/strategies/table_strategy.py#L56-L466)

**Section sources**
- [table_strategy.py](file://markdown_chunker/chunker/strategies/table_strategy.py#L1-L466)

## Structural Strategy
The Structural Strategy chunks documents based on header hierarchy, creating semantically meaningful sections while preserving document structure. This strategy is ideal for well-structured documents with clear section organization.

### Purpose and Logic
The Structural Strategy splits content by header boundaries, preserving the header hierarchy in metadata. It combines short sections to meet minimum size requirements and supports multi-level structures (H1-H6). The strategy adds header path information to chunks to maintain context.

### Implementation Details
The strategy traverses the AST by extracting headers from the Stage 1 results or detecting them manually. It builds a header hierarchy by establishing parent-child relationships based on header levels. Sections are created based on header boundaries and processed into chunks, with large sections split by paragraphs or subsections.

### Context Preservation
The strategy preserves context by including header path information in chunk metadata. Each chunk contains the full path from the root header to the current header, allowing reconstruction of the document structure.

### Edge Cases
The strategy handles edge cases such as missing Stage 1 data by falling back to manual header detection. It also handles complex header structures with multiple levels by building a proper hierarchy.

### Strategy-Specific Parameters
- `header_count_threshold`: Minimum number of headers (default: 3)
- `min_chunk_size`: Minimum size for each chunk
- `max_chunk_size`: Maximum size for each chunk

```mermaid
classDiagram
class StructuralStrategy {
+name : str = "structural"
+priority : int = 3
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) List[Chunk]
-extract_headers(content, stage1_results) List[HeaderInfo]
-detect_headers_manual(content) List[HeaderInfo]
-build_hierarchy(headers) List[HeaderInfo]
-create_sections(content, headers) List[Section]
-process_sections(sections, config) List[Chunk]
-create_section_chunk(section, config) Chunk
-split_large_section(section, config) List[Chunk]
-split_by_subsections(section, config) List[Chunk]
-split_by_paragraphs(section, config) List[Chunk]
-split_preserving_code_blocks(content) List[str]
-combine_small_chunks(chunks, config) List[Chunk]
-build_header_path(header) str
-estimate_line_number(content, position) int
}
class HeaderInfo {
+level : int
+text : str
+line : int
+position : int
+parent : Optional[HeaderInfo]
+children : Optional[List[HeaderInfo]]
}
class Section {
+header : HeaderInfo
+content : str
+start_line : int
+end_line : int
+size : int
+has_subsections : bool
+subsections : Optional[List[Section]]
}
StructuralStrategy --> HeaderInfo : "creates"
StructuralStrategy --> Section : "creates"
HeaderInfo --> HeaderInfo : "parent/child"
Section --> Section : "contains"
```

**Diagram sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L55-L1381)

**Section sources**
- [structural_strategy.py](file://markdown_chunker/chunker/strategies/structural_strategy.py#L1-L1381)

## Sentences Strategy
The Sentences Strategy provides a reliable fallback for any type of content by splitting text into sentences and grouping them into appropriately sized chunks. This strategy is ideal for simple text documents and as a universal fallback.

### Purpose and Logic
The Sentences Strategy splits content into sentences using regex patterns and groups them into chunks respecting size limits. It preserves paragraph boundaries when possible and provides reliable, predictable chunking for any content type.

### Implementation Details
The strategy traverses the AST by first splitting content into paragraphs, then splitting each paragraph into sentences. Sentences are grouped into chunks, with the grouping respecting the maximum chunk size. The strategy preserves structured content (headers, lists, tables) intact when possible.

### Context Preservation
The strategy preserves context by keeping structured content intact and grouping related sentences together. It also preserves paragraph boundaries to maintain the flow of the text.

### Edge Cases
The strategy handles edge cases such as sentences with abbreviations by using sophisticated regex patterns. It also handles structured content by detecting and preserving it.

### Strategy-Specific Parameters
- `max_chunk_size`: Maximum size for each chunk
- `min_chunk_size`: Minimum size for each chunk
- `allow_oversize`: Whether to allow oversized chunks

```mermaid
classDiagram
class SentencesStrategy {
+name : str = "sentences"
+priority : int = 4
+can_handle(analysis, config) bool
+calculate_quality(analysis) float
+apply(content, stage1_results, config) List[Chunk]
-split_into_paragraphs(content) List[str]
-is_structured_content(text) bool
-split_into_sentences(text) List[str]
-get_chunk_statistics(chunks) dict
}
SentencesStrategy : SENTENCE_PATTERNS List[str]
SentencesStrategy : _sentence_regex Optional[Pattern]
```

**Diagram sources**
- [sentences_strategy.py](file://markdown_chunker/chunker/strategies/sentences_strategy.py#L21-L526)

**Section sources**
- [sentences_strategy.py](file://markdown_chunker/chunker/strategies/sentences_strategy.py#L1-L526)

## Strategy Selection
The Strategy Selector evaluates and scores each strategy based on content analysis to determine the optimal strategy for a given document. The selection process uses a combination of priority and quality scoring.

### Selection Process
The selector first checks if a strategy can handle the content based on thresholds (e.g., code ratio, list count). Then it calculates a quality score based on how well-suited the strategy is for the content. The final score combines priority and quality, with higher priority strategies receiving higher weights.

### Scoring Mechanism
Each strategy calculates its quality score based on factors specific to its domain. For example, the CodeAware Strategy gives higher scores for higher code ratios and more code blocks, while the Table Strategy scores higher for more tables and higher table ratios.

### Selection Modes
The selector supports two modes:
- **Strict mode**: Selects the first applicable strategy by priority
- **Weighted mode**: Selects the strategy with the highest combined priority and quality score

```mermaid
sequenceDiagram
participant Selector as StrategySelector
participant Analysis as ContentAnalysis
participant Config as ChunkConfig
participant Strategy as BaseStrategy
Selector->>Selector : select_strategy(analysis, config)
alt Strict Mode
loop For each strategy by priority
Strategy->>Strategy : can_handle(analysis, config)
alt Can handle
Selector-->>Selector : Return strategy
break
end
end
else Weighted Mode
loop For each strategy
Strategy->>Strategy : get_metrics(analysis, config)
Strategy-->>Selector : StrategyMetrics
end
Selector->>Selector : Find strategy with highest final_score
Selector-->>Selector : Return best strategy
end
```

**Diagram sources**
- [selector.py](file://markdown_chunker/chunker/selector.py#L23-L322)

**Section sources**
- [selector.py](file://markdown_chunker/chunker/selector.py#L1-L322)

## Common Issues and Mitigations
### Over-chunking
Over-chunking occurs when documents are split into too many small chunks, breaking semantic relationships. Each strategy mitigates this by:
- **CodeAware Strategy**: Grouping related text with code blocks
- **Table Strategy**: Keeping small tables intact
- **Structural Strategy**: Combining small sections
- **Sentences Strategy**: Grouping multiple sentences

### Context Loss
Context loss happens when chunks are separated from their surrounding context. Mitigations include:
- **CodeAware Strategy**: Preserving code block atomicity
- **Table Strategy**: Duplicating headers in split table chunks
- **Structural Strategy**: Adding header path information to chunks

### Edge Case Handling
All strategies include fallback mechanisms for edge cases:
- Using regex patterns when Stage 1 data is unavailable
- Handling malformed content gracefully
- Preserving atomic elements (code blocks, tables) intact
- Validating and fixing chunks after creation

## Strategy Selection Guidance
### When to Force a Specific Strategy
Force a specific strategy when:
- The document has a known structure that matches a particular strategy
- Testing or debugging specific chunking behavior
- The automatic selection is not producing optimal results for a particular use case

### When to Allow Automatic Selection
Allow automatic selection when:
- Processing diverse document types
- The optimal strategy is unclear
- Maximizing adaptability to different content patterns
- Leveraging the system's content analysis capabilities

The automatic selection system is designed to choose the most appropriate strategy based on comprehensive content analysis, making it suitable for most use cases. Forcing a specific strategy should be done only when there's a clear benefit to overriding the automatic selection.