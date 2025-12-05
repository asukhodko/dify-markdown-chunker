# Parser Architecture

<cite>
**Referenced Files in This Document**   
- [core.py](file://markdown_chunker_legacy/parser/core.py)
- [ast.py](file://markdown_chunker_legacy/parser/ast.py)
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py)
- [nesting_resolver.py](file://markdown_chunker_legacy/parser/nesting_resolver.py)
- [analyzer.py](file://markdown_chunker_legacy/parser/analyzer.py)
- [types.py](file://markdown_chunker_legacy/parser/types.py)
- [validation.py](file://markdown_chunker_legacy/parser/validation.py)
- [utils.py](file://markdown_chunker_legacy/parser/utils.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [AST-Based Parsing Approach](#ast-based-parsing-approach)
4. [Enhanced AST Builder](#enhanced-ast-builder)
5. [Content Analysis Process](#content-analysis-process)
6. [Component Interactions](#component-interactions)
7. [Data Flow](#data-flow)
8. [Performance Considerations](#performance-considerations)
9. [Error Handling](#error-handling)

## Introduction
The parser component is responsible for analyzing Markdown documents and extracting structural information for downstream processing. It uses an AST-based approach with markdown-it-py as the primary parser, enhanced with additional metadata and structural analysis. The parser analyzes document structure, detects code blocks, lists, tables, and other elements, and generates metrics used for strategy selection in the chunking process.

**Section sources**
- [core.py](file://markdown_chunker_legacy/parser/core.py#L1-L654)

## Core Components
The parser architecture consists of several key components that work together to transform raw Markdown into structured analysis results. The core components include the AST builder, enhanced AST builder, nesting resolver, validation modules, and content analyzer. These components are orchestrated through the Stage1Interface, which provides the main entry point for parsing operations.

**Section sources**
- [core.py](file://markdown_chunker_legacy/parser/core.py#L401-L638)
- [ast.py](file://markdown_chunker_legacy/parser/ast.py#L30-L292)
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py#L319-L654)
- [nesting_resolver.py](file://markdown_chunker_legacy/parser/nesting_resolver.py#L74-L273)

## AST-Based Parsing Approach
The parser uses markdown-it-py to generate an Abstract Syntax Tree (AST) from Markdown content. The AST represents the document structure as a tree of nodes, with each node representing a Markdown element such as headers, paragraphs, lists, or code blocks. The parser first validates and normalizes the input text, then processes it through markdown-it-py to generate tokens, which are converted into AST nodes with positional metadata.

```mermaid
classDiagram
class MarkdownNode {
+type : str
+content : str
+children : List[MarkdownNode]
+position : Position
+metadata : Dict[str, Any]
+parent : Optional[MarkdownNode]
+add_child(child : MarkdownNode)
+remove_child(child : MarkdownNode)
+find_children(node_type : str) : List[MarkdownNode]
+find_descendants(node_type : str) : List[MarkdownNode]
+get_text_content() : str
+get_line_range() : tuple
+is_leaf() : bool
+to_dict() : Dict[str, Any]
}
class ASTBuilder {
+parser_name : str
+parser : Any
+build(md_text : str) : MarkdownNode
+build_ast(md_text : str) : MarkdownNode
+_build_from_markdown_it(md_text : str) : MarkdownNode
+_build_from_mistune(md_text : str) : MarkdownNode
+_convert_tokens_to_nodes(tokens, parent : MarkdownNode, md_text : str)
+_token_to_node(token, md_text : str) : MarkdownNode
+_resolve_nesting(root : MarkdownNode)
+_resolve_list_nesting(node : MarkdownNode)
+_resolve_header_hierarchy(node : MarkdownNode)
+_resolve_blockquote_nesting(node : MarkdownNode)
+_calculate_nesting_levels(node : MarkdownNode, level : int)
}
MarkdownNode <|-- ASTBuilder : "uses"
ASTBuilder --> MarkdownNode : "creates"
```

**Diagram sources **
- [ast.py](file://markdown_chunker_legacy/parser/ast.py#L30-L292)

**Section sources**
- [ast.py](file://markdown_chunker_legacy/parser/ast.py#L111-L292)
- [core.py](file://markdown_chunker_legacy/parser/core.py#L448-L450)

## Enhanced AST Builder
The enhanced AST builder extends the basic AST with additional structural and positional metadata. It processes inline elements such as code, links, emphasis, and strong text, creating a more detailed representation of the document. The builder uses a LineTracker to maintain accurate line and column positions, and a SourceRange to represent ranges in the source text. Inline elements are extracted using regular expressions and converted into appropriate node types.

```mermaid
classDiagram
class InlineToken {
+type : str
+content : str
+start_pos : int
+end_pos : int
+raw_content : str
+attributes : Dict[str, str]
+get_length() : int
}
class SourceRange {
+start : Position
+end : Position
+contains_position(position : Position) : bool
+get_text(source_text : str) : str
}
class LineTracker {
+text : str
+lines : List[str]
+line_offsets : List[int]
+_calculate_line_offsets() : List[int]
+get_position_from_offset(offset : int) : Position
+get_offset_from_position(line : int, column : int) : int
+_find_line_for_offset(offset : int) : int
}
class InlineTokenProcessor {
+logger : Logger
+extract_inline_tokens(text : str) : List[InlineToken]
+_extract_inline_code(text : str) : List[InlineToken]
+_extract_links(text : str) : List[InlineToken]
+_extract_emphasis(text : str) : List[InlineToken]
+_overlaps_with_existing(start : int, end : int, tokens : List[InlineToken]) : bool
+_sort_and_merge_tokens(tokens : List[InlineToken]) : List[InlineToken]
}
class MarkdownNodeFactory {
+line_tracker : LineTracker
+create_node(node_type : NodeType, content : str, start_offset : int, end_offset : int, children : Optional[List[MarkdownNode]], metadata : Optional[Dict[str, Any]]) : MarkdownNode
+create_inline_node(token : InlineToken, parent_offset : int) : MarkdownNode
}
class EnhancedASTBuilder {
+inline_processor : InlineTokenProcessor
+logger : Logger
+build_ast(md_text : str) : MarkdownNode
+_normalize_input(md_text : str) : str
+_enhance_with_inline_elements(ast : MarkdownNode, source_text : str, line_tracker : LineTracker, node_factory : MarkdownNodeFactory) : MarkdownNode
+_process_inline_elements(node : MarkdownNode, source_text : str, line_tracker : LineTracker, node_factory : MarkdownNodeFactory) : List[MarkdownNode]
+_validate_ast_structure(ast : MarkdownNode)
+_validate_tree_correctness(ast : MarkdownNode)
+_check_circular_references(node : MarkdownNode, visited : set[int])
+_validate_parent_child_relationships(node : MarkdownNode, parent : Optional[MarkdownNode])
+_check_orphaned_nodes(ast : MarkdownNode)
+_validate_node_relationships(ast : MarkdownNode)
+_validate_position_consistency(node : MarkdownNode)
+_validate_content_consistency(node : MarkdownNode)
+_validate_metadata_consistency(node : MarkdownNode)
}
EnhancedASTBuilder --> InlineTokenProcessor : "uses"
EnhancedASTBuilder --> LineTracker : "uses"
EnhancedASTBuilder --> MarkdownNodeFactory : "uses"
EnhancedASTBuilder --> SourceRange : "uses"
MarkdownNodeFactory --> LineTracker : "uses"
InlineTokenProcessor --> InlineToken : "creates"
```

**Diagram sources **
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py#L17-L654)

**Section sources**
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py#L319-L654)

## Content Analysis Process
The content analysis process generates metrics such as code_ratio and complexity_score that are used for strategy selection. The analyzer calculates various document metrics including total characters, lines, and words, as well as ratios of different content types (code, text, list, table). It also counts specific elements like code blocks, headers, lists, and tables, and extracts programming languages used in code blocks.

```mermaid
classDiagram
class ContentAnalysis {
+total_chars : int
+total_lines : int
+total_words : int
+code_ratio : float
+text_ratio : float
+code_block_count : int
+content_type : str
+header_count : Dict[int, int]
+languages : Dict[str, int]
+list_count : int
+table_count : int
+list_ratio : float
+table_ratio : float
+complexity_score : float
+max_header_depth : int
+has_mixed_content : bool
+nested_list_depth : int
+has_tables : bool
+has_nested_lists : bool
+inline_code_count : int
+average_line_length : float
+max_line_length : int
+empty_lines : int
+indented_lines : int
+punctuation_ratio : float
+special_chars : Dict[str, int]
+block_elements : List[Any]
+preamble : Optional[PreambleInfo]
+get_total_header_count() : int
+_validate_required_fields()
+_normalize_ratios()
+_calculate_derived_metrics()
+_calculate_complexity() : float
+_determine_content_type() : str
+get_summary() : Dict[str, Any]
+recommend_strategy() : str
+get_element_counts() : Dict[str, Any]
+validate_consistency() : List[str]
+validate_structure_integrity() : List[str]
+validate_cross_component_consistency(other_components : Dict[str, Any]) : List[str]
}
class PreambleInfo {
+content : str
+type : str
+line_count : int
+char_count : int
+has_metadata : bool
+metadata_fields : Dict[str, str]
+__post_init__()
+to_dict() : Dict[str, Any]
}
class PreambleExtractor {
+METADATA_PATTERNS : Dict[str, str]
+INTRODUCTION_KEYWORDS : List[str]
+SUMMARY_KEYWORDS : List[str]
+_metadata_regex : Dict[str, Pattern]
+extract(md_text : str) : Optional[PreambleInfo]
+_find_first_header(lines : List[str]) : int
+_classify_type(content : str) : str
+_has_metadata(content : str) : bool
+_extract_metadata(content : str) : dict
}
class ContentAnalyzer {
+code_ratio_threshold : float
+list_ratio_threshold : float
+mixed_content_threshold : float
+analyze_content(md_text : str, fenced_blocks : Optional[List[FencedBlock]], elements : Optional[ElementCollection]) : ContentAnalysis
+_calculate_list_chars(lists) : int
+_calculate_table_chars(tables) : int
+_detect_mixed_content(code_ratio : float, list_ratio : float, table_ratio : float, text_ratio : float) : bool
+_calculate_complexity(code_ratio : float, list_ratio : float, table_ratio : float, text_ratio : float, max_header_depth : int, max_list_nesting : int, total_chars : int, has_mixed_content : bool) : float
+_classify_content_type(code_ratio : float, list_ratio : float, table_ratio : float, has_mixed_content : bool) : str
}
ContentAnalyzer --> ContentAnalysis : "creates"
ContentAnalyzer --> PreambleExtractor : "uses"
PreambleExtractor --> PreambleInfo : "creates"
```

**Diagram sources **
- [analyzer.py](file://markdown_chunker_legacy/parser/analyzer.py#L18-L501)
- [types.py](file://markdown_chunker_legacy/parser/types.py#L436-L500)

**Section sources**
- [analyzer.py](file://markdown_chunker_legacy/parser/analyzer.py#L18-L501)
- [types.py](file://markdown_chunker_legacy/parser/types.py#L436-L500)

## Component Interactions
The parser components interact through well-defined interfaces and data structures. The Stage1Interface orchestrates the parsing process, coordinating between the AST builder, fenced block extractor, element detector, and content analyzer. Results are validated through the APIValidator to ensure consistency across components. The nesting resolver processes fenced blocks to establish parent-child relationships and calculate nesting levels.

```mermaid
sequenceDiagram
participant Client as "Client Application"
participant Interface as "Stage1Interface"
participant ASTBuilder as "ASTBuilder"
participant FencedExtractor as "FencedBlockExtractor"
participant ElementDetector as "ElementDetector"
participant Analyzer as "ContentAnalyzer"
participant Validator as "APIValidator"
Client->>Interface : process_document(md_text)
Interface->>Interface : validate_input()
Interface->>ASTBuilder : build(md_text)
ASTBuilder-->>Interface : AST
Interface->>FencedExtractor : extract_fenced_blocks(md_text)
FencedExtractor-->>Interface : fenced_blocks
Interface->>ElementDetector : detect_elements(md_text)
ElementDetector-->>Interface : elements
Interface->>Analyzer : analyze_content(md_text)
Analyzer-->>Interface : analysis
Interface->>Validator : validate_process_document_result(results)
Validator-->>Interface : validation_result
Interface-->>Client : Stage1Results
```

**Diagram sources **
- [core.py](file://markdown_chunker_legacy/parser/core.py#L401-L638)
- [validation.py](file://markdown_chunker_legacy/parser/validation.py#L162-L588)

**Section sources**
- [core.py](file://markdown_chunker_legacy/parser/core.py#L401-L638)
- [validation.py](file://markdown_chunker_legacy/parser/validation.py#L162-L588)

## Data Flow
The data flow begins with raw Markdown text, which is validated and normalized before being processed by various components. The AST builder generates the document structure, while the fenced block extractor identifies code blocks. The element detector finds structural elements like headers, lists, and tables. The content analyzer calculates metrics based on the document content. All results are combined into a structured analysis result that includes the AST, detected elements, and calculated metrics.

```mermaid
flowchart TD
Start([Raw Markdown]) --> Validate["Validate and Normalize Input"]
Validate --> ParseAST["Parse AST with markdown-it-py"]
ParseAST --> ExtractBlocks["Extract Fenced Blocks"]
ExtractBlocks --> ResolveNesting["Resolve Block Nesting"]
ResolveNesting --> DetectElements["Detect Structural Elements"]
DetectElements --> AnalyzeContent["Analyze Content and Metrics"]
AnalyzeContent --> ValidateResults["Validate Results"]
ValidateResults --> PrepareOutput["Prepare Output for Chunking"]
PrepareOutput --> End([Structured Analysis Results])
ParseAST --> EnhanceAST["Enhance AST with Inline Elements"]
EnhanceAST --> AddPositionalMetadata["Add Positional Metadata"]
AddPositionalMetadata --> ValidateAST["Validate AST Structure"]
ValidateAST --> DetectElements
```

**Diagram sources **
- [core.py](file://markdown_chunker_legacy/parser/core.py#L438-L510)
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py#L326-L349)

**Section sources**
- [core.py](file://markdown_chunker_legacy/parser/core.py#L438-L510)
- [enhanced_ast_builder.py](file://markdown_chunker_legacy/parser/enhanced_ast_builder.py#L326-L349)

## Performance Considerations
The parser is designed to handle large documents efficiently, with several performance optimizations in place. The AST construction process is optimized by using markdown-it-py's efficient tokenization, and positional metadata is calculated during parsing rather than in post-processing. For very large documents, the parser may fall back to mistune if markdown-it-py is not available. Memory usage is managed by processing the document in a single pass and avoiding unnecessary data duplication.

**Section sources**
- [ast.py](file://markdown_chunker_legacy/parser/ast.py#L114-L147)
- [core.py](file://markdown_chunker_legacy/parser/core.py#L448-L450)

## Error Handling
The parser includes comprehensive error handling mechanisms for malformed Markdown and edge cases. The ErrorCollector class aggregates errors and warnings throughout the parsing process. Input validation ensures that the text is properly encoded and normalized. The parser handles unclosed code blocks and overlapping fences gracefully, and includes phantom block prevention to avoid spurious block detection. Validation results include detailed error information that can be used for debugging.

```mermaid
classDiagram
class ErrorCollector {
+errors : List[ProcessingError]
+warnings : List[ProcessingError]
+add_error(error : ProcessingError)
+add_warning(error : ProcessingError)
+has_errors() : bool
+has_warnings() : bool
+has_critical_errors() : bool
+get_summary() : Dict[str, Any]
+clear()
}
class ProcessingError {
+severity : ErrorSeverity
+component : str
+message : str
+details : str
+line_number : Optional[int]
}
class ErrorSeverity {
+ERROR
+WARNING
+INFO
}
class APIValidationError {
+errors : List[str]
+__str__() : str
}
class ValidationResult {
+is_valid : bool
+issues : List[ValidationIssue]
+node_count : int
+max_depth : int
+add_issue(severity : str, message : str, node_type : Optional[Any], position : Optional[Any], details : Optional[str])
+get_errors() : List[ValidationIssue]
+get_warnings() : List[ValidationIssue]
+has_errors() : bool
+has_warnings() : bool
}
class ValidationIssue {
+severity : str
+message : str
+node_type : Optional[Any]
+position : Optional[Any]
+details : Optional[str]
}
ErrorCollector --> ProcessingError : "contains"
ValidationResult --> ValidationIssue : "contains"
APIValidationError --> ValidationResult : "contains"
```

**Diagram sources **
- [core.py](file://markdown_chunker_legacy/parser/core.py#L28-L29)
- [errors.py](file://markdown_chunker_legacy/parser/errors.py#L1-L100)
- [validation.py](file://markdown_chunker_legacy/parser/validation.py#L129-L785)

**Section sources**
- [core.py](file://markdown_chunker_legacy/parser/core.py#L28-L29)
- [validation.py](file://markdown_chunker_legacy/parser/validation.py#L129-L785)