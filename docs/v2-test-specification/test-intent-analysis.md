# Test Intent Analysis

This document contains the extracted intents from all P1 legacy tests,
mapped to v2 API concepts.

## Summary

- **Total test files analyzed**: 126
- **Total tests**: 3188
- **V2 applicable tests**: 2369
- **Removed functionality tests**: 819

## Parser Tests

**Files analyzed**: 46
**Total tests**: 1067
**V2 applicable**: 814
**Removed functionality**: 253

### tests/parser/root_tests/test_all_regression_prevention.py

```yaml
test_file: tests/parser/root_tests/test_all_regression_prevention.py
test_count: 2
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_all_regression_prevention
    intent: "Test all regression prevention measures."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_specific_regression_scenarios
    intent: "Test specific scenarios that were previously broken."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_ast_validation_enhanced.py

```yaml
test_file: tests/parser/root_tests/test_ast_validation_enhanced.py
test_count: 2
legacy_imports:
  - markdown_chunker.parser.EnhancedASTBuilder
v2_applicable: true
removed_functionality: false

tests:
  - name: test_enhanced_ast_validation
    intent: "Test enhanced AST validation functionality."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error_detection
    intent: "Test that validation properly detects errors."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_automated_tests.py

```yaml
test_file: tests/parser/root_tests/test_automated_tests.py
test_count: 4
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_basic_is_automated
    intent: "Test that test_basic.py is now automated with assertions."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_basic_runs_and_validates
    intent: "Test that test_basic.py actually validates functionality."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_pytest_compatibility
    intent: "Test that pytest-compatible version exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_more_print_only_tests
    intent: "Test that we don't have print-only tests anymore."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_comprehensive_integration.py

```yaml
test_file: tests/parser/root_tests/test_comprehensive_integration.py
test_count: 5
legacy_imports:
  - markdown_chunker.parser.LineNumberConverter
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.analyzer.analyze_content
  - markdown_chunker.parser.elements.detect_elements
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_complete_pipeline_with_fixes
    intent: "Test complete pipeline with all fixes applied."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_with_fixes
    intent: "Test that fixes don't significantly degrade performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_backward_compatibility
    intent: "Test that fixes maintain backward compatibility."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_with_fixes
    intent: "Test error handling with all fixes applied."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_fixes_integration
    intent: "Test that all fixes work together correctly."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_content_analysis_validation.py

```yaml
test_file: tests/parser/root_tests/test_content_analysis_validation.py
test_count: 3
legacy_imports:
  - markdown_chunker.parser.types.ContentAnalysis
  - markdown_chunker.parser.types.ElementCollection
  - markdown_chunker.parser.types.FencedBlock
v2_applicable: true
removed_functionality: false

tests:
  - name: test_content_analysis_validation
    intent: "Test ContentAnalysis validation functionality."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cross_component_validation
    intent: "Test cross-component validation."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_serialization_validation
    intent: "Test serialization validation specifically."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_critical_fixes.py

```yaml
test_file: tests/parser/root_tests/test_critical_fixes.py
test_count: 5
legacy_imports:
  - markdown_chunker.parser.EnhancedASTBuilder
  - markdown_chunker.parser.types.NodeType
  - markdown_chunker.parser.ErrorCollector
  - markdown_chunker.parser.SourceLocation
  - markdown_chunker.parser.FenceHandler
v2_applicable: false
removed_functionality: true

tests:
  - name: test_enhanced_ast
    intent: "Test enhanced AST building."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_error_collection
    intent: "Test error collection system."
    v2_component: Error handling
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fence_handling
    intent: "Test fence handling."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_text_recovery
    intent: "Test text recovery utilities."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_validation
    intent: "Test API validation."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/root_tests/test_nested_extraction.py

```yaml
test_file: tests/parser/root_tests/test_nested_extraction.py
test_count: 6
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_simple_nested_blocks
    intent: "Test extraction of simple nested blocks - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_nested_levels
    intent: "Test extraction with multiple nesting levels - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types
    intent: "Test nested blocks with mixed fence types - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_skipping_inner_blocks
    intent: "Test that inner blocks are preserved as content - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlapping_blocks_handling
    intent: "Test handling of overlapping blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_nested_blocks
    intent: "Test handling of unclosed nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_nesting_documentation.py

```yaml
test_file: tests/parser/root_tests/test_nesting_documentation.py
test_count: 4
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.FencedBlockExtractor
v2_applicable: true
removed_functionality: false

tests:
  - name: test_documented_nesting_capabilities
    intent: "Test that documented nesting capabilities work with NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_documented_limitations
    intent: "Test that documented limitations are accurate."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_documentation_honesty
    intent: "Test that documentation is honest about capabilities."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_capabilities_file
    intent: "Test that NESTING_CAPABILITIES.md was archived."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_pytest_config.py

```yaml
test_file: tests/parser/root_tests/test_pytest_config.py
test_count: 3
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_pytest_without_coverage
    intent: "Test that pytest works without pytest-cov."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_coverage_detection
    intent: "Test coverage detection logic."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration_scenarios
    intent: "Test different configuration scenarios."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_pytest_no_coverage.py

```yaml
test_file: tests/parser/root_tests/test_pytest_no_coverage.py
test_count: 3
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_pytest_runs_without_coverage
    intent: "Test that pytest can run without coverage dependencies."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_conftest_configuration
    intent: "Test that conftest.py handles missing coverage gracefully."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_pyproject_toml_configuration
    intent: "Test that pyproject.toml doesn't require coverage."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/root_tests/test_updated_tests.py

```yaml
test_file: tests/parser/root_tests/test_updated_tests.py
test_count: 3
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.FencedBlockExtractor
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.types.FencedBlock
v2_applicable: true
removed_functionality: false

tests:
  - name: test_updated_position_calculation
    intent: "Test the updated position calculation test."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_updated_nesting_calculation
    intent: "Test the updated nesting calculation test."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_tests
    intent: "Test the regression tests."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_accurate_reporting.py

```yaml
test_file: tests/parser/test_accurate_reporting.py
test_count: 10
legacy_imports:
  - markdown_chunker.parser.LineNumberConverter
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_actual_test_count_validation
    intent: "Test that we can accurately count tests."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_test_count_accuracy
    intent: "Test that reported test counts match reality."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_automated_vs_manual_tests
    intent: "Test distinction between automated and manual tests."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_prevention
    intent: "Test that we have regression prevention tests."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_documentation_matches_implementation
    intent: "Test that documentation claims match implementation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_actual_test_count_validation
    intent: "Test that we can accurately count tests."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_test_count_accuracy
    intent: "Test that reported test counts match reality."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_automated_vs_manual_tests
    intent: "Test distinction between automated and manual tests."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_prevention
    intent: "Test that we have regression prevention tests."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_documentation_matches_implementation
    intent: "Test that documentation claims match implementation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_ast.py

```yaml
test_file: tests/parser/test_ast.py
test_count: 8
legacy_imports:
  - markdown_chunker.parser.ast
v2_applicable: true
removed_functionality: false

tests:
  - name: test_can_instantiate
    intent: "Test that MarkdownNode can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ASTBuilder can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate_with_parser_name
    intent: "Test that ASTBuilder can be instantiated with parser name."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enhanced_ast_builder_alias
    intent: "Test that EnhancedASTBuilder alias exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that MarkdownNode can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ASTBuilder can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate_with_parser_name
    intent: "Test that ASTBuilder can be instantiated with parser name."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enhanced_ast_builder_alias
    intent: "Test that EnhancedASTBuilder alias exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_ast_new.py

```yaml
test_file: tests/parser/test_ast_new.py
test_count: 58
legacy_imports:
  - markdown_chunker.parser.ast.ASTBuilder
  - markdown_chunker.parser.ast.EnhancedASTBuilder
  - markdown_chunker.parser.ast.MarkdownNode
  - markdown_chunker.parser.types.Position
  - markdown_chunker.parser.types.Position
v2_applicable: true
removed_functionality: false

tests:
  - name: test_instantiation
    intent: "Test that MarkdownNode can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_properties
    intent: "Test MarkdownNode properties."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_child
    intent: "Test adding child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_remove_child
    intent: "Test removing child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_children
    intent: "Test finding direct children by type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_descendants
    intent: "Test finding all descendants by type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_content
    intent: "Test getting all text content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_leaf
    intent: "Test checking if node is a leaf."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test converting node to dictionary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_position
    intent: "Test node with position information."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_range
    intent: "Test getting line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation
    intent: "Test that ASTBuilder can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation_with_parser_name
    intent: "Test instantiation with specific parser."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_simple_document
    intent: "Test building AST from simple document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_code_block
    intent: "Test building AST with code block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_empty_document
    intent: "Test building AST from empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_headers
    intent: "Test building AST with multiple headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_lists
    intent: "Test building AST with lists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_resolution
    intent: "Test that nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enhanced_ast_builder_alias
    intent: "Test that EnhancedASTBuilder is an alias."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_unicode
    intent: "Test building AST with unicode content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_nesting_resolution
    intent: "Test list nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_hierarchy_resolution
    intent: "Test header hierarchy is resolved."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blockquote_nesting_resolution
    intent: "Test blockquote nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_empty_content
    intent: "Test node with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_none_content
    intent: "Test node with None content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_children
    intent: "Test node with many children."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deep_nesting
    intent: "Test deeply nested structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_manipulation
    intent: "Test metadata can be added and modified."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation
    intent: "Test that MarkdownNode can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_properties
    intent: "Test MarkdownNode properties."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_child
    intent: "Test adding child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_remove_child
    intent: "Test removing child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_children
    intent: "Test finding direct children by type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_descendants
    intent: "Test finding all descendants by type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_content
    intent: "Test getting all text content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_leaf
    intent: "Test checking if node is a leaf."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test converting node to dictionary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_position
    intent: "Test node with position information."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_range
    intent: "Test getting line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation
    intent: "Test that ASTBuilder can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation_with_parser_name
    intent: "Test instantiation with specific parser."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_simple_document
    intent: "Test building AST from simple document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_code_block
    intent: "Test building AST with code block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_empty_document
    intent: "Test building AST from empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_headers
    intent: "Test building AST with multiple headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_lists
    intent: "Test building AST with lists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_resolution
    intent: "Test that nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enhanced_ast_builder_alias
    intent: "Test that EnhancedASTBuilder is an alias."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_with_unicode
    intent: "Test building AST with unicode content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_nesting_resolution
    intent: "Test list nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_hierarchy_resolution
    intent: "Test header hierarchy is resolved."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blockquote_nesting_resolution
    intent: "Test blockquote nesting is resolved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_empty_content
    intent: "Test node with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_node_with_none_content
    intent: "Test node with None content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_children
    intent: "Test node with many children."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deep_nesting
    intent: "Test deeply nested structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_manipulation
    intent: "Test metadata can be added and modified."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_ast_validator_new.py

```yaml
test_file: tests/parser/test_ast_validator_new.py
test_count: 38
legacy_imports:
  - markdown_chunker.parser.ast.MarkdownNode
  - markdown_chunker.parser.validation.ASTValidator
  - markdown_chunker.parser.validation.ValidationIssue
  - markdown_chunker.parser.validation.ValidationResult
  - markdown_chunker.parser.validation.validate_ast_structure
v2_applicable: true
removed_functionality: false

tests:
  - name: test_instantiation
    intent: "Test that ASTValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_simple_ast
    intent: "Test validating a simple AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_empty_ast
    intent: "Test validating empty AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_nested_ast
    intent: "Test validating nested AST structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_properties
    intent: "Test ValidationResult properties."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_add_issue
    intent: "Test adding issues to ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_get_errors
    intent: "Test getting errors from ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_get_warnings
    intent: "Test getting warnings from ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_has_errors
    intent: "Test has_errors method."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_has_warnings
    intent: "Test has_warnings method."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_validate_ast_structure
    intent: "Test validate_ast_structure convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_issue_creation
    intent: "Test creating ValidationIssue."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_issue_optional_fields
    intent: "Test ValidationIssue with optional fields."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_content
    intent: "Test validating AST with invalid content type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_metadata
    intent: "Test validating AST with invalid metadata type."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_children
    intent: "Test validating AST with invalid children type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_deeply_nested_ast
    intent: "Test validating deeply nested AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_many_children
    intent: "Test validating AST with many children."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_exception
    intent: "Test that validator handles exceptions gracefully."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation
    intent: "Test that ASTValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_simple_ast
    intent: "Test validating a simple AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_empty_ast
    intent: "Test validating empty AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_nested_ast
    intent: "Test validating nested AST structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_properties
    intent: "Test ValidationResult properties."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_add_issue
    intent: "Test adding issues to ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_get_errors
    intent: "Test getting errors from ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_get_warnings
    intent: "Test getting warnings from ValidationResult."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_has_errors
    intent: "Test has_errors method."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_has_warnings
    intent: "Test has_warnings method."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_validate_ast_structure
    intent: "Test validate_ast_structure convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_issue_creation
    intent: "Test creating ValidationIssue."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_issue_optional_fields
    intent: "Test ValidationIssue with optional fields."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_content
    intent: "Test validating AST with invalid content type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_metadata
    intent: "Test validating AST with invalid metadata type."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_invalid_children
    intent: "Test validating AST with invalid children type."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_deeply_nested_ast
    intent: "Test validating deeply nested AST."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_many_children
    intent: "Test validating AST with many children."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_ast_with_exception
    intent: "Test that validator handles exceptions gracefully."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_backward_compatibility.py

```yaml
test_file: tests/parser/test_backward_compatibility.py
test_count: 32
legacy_imports:
  - markdown_chunker.parser.FencedBlock
  - markdown_chunker.parser.Position
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.FencedBlock
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_extract_fenced_blocks_signature
    intent: "Test that extract_fenced_blocks signature is preserved."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fenced_block_essential_fields
    intent: "Test that FencedBlock essential fields are preserved."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_1_based_line_numbering_preserved
    intent: "Test that 1-based line numbering is preserved."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_support_preserved
    intent: "Test that basic nesting support is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_support
    intent: "Test that multiple blocks are still supported."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handling
    intent: "Test that empty language handling is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_handling
    intent: "Test that unclosed block handling is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fence_type_detection
    intent: "Test that fence type detection is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_extraction_accuracy
    intent: "Test that content extraction accuracy is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_position_data_structure
    intent: "Test that Position data structure is available."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_graceful
    intent: "Test that error handling remains graceful."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_language_normalization_behavior
    intent: "Test that language normalization behavior is consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_boundaries_accuracy
    intent: "Test that block boundary detection remains accurate."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_existing_code_patterns
    intent: "Test common existing code patterns still work."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_import_compatibility
    intent: "Test that essential imports still work."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_regression_in_core_functionality
    intent: "Test that core functionality has no regressions."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_fenced_blocks_signature
    intent: "Test that extract_fenced_blocks signature is preserved."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fenced_block_essential_fields
    intent: "Test that FencedBlock essential fields are preserved."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_1_based_line_numbering_preserved
    intent: "Test that 1-based line numbering is preserved."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_support_preserved
    intent: "Test that basic nesting support is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_support
    intent: "Test that multiple blocks are still supported."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handling
    intent: "Test that empty language handling is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_handling
    intent: "Test that unclosed block handling is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fence_type_detection
    intent: "Test that fence type detection is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_extraction_accuracy
    intent: "Test that content extraction accuracy is preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_position_data_structure
    intent: "Test that Position data structure is available."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_graceful
    intent: "Test that error handling remains graceful."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_language_normalization_behavior
    intent: "Test that language normalization behavior is consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_boundaries_accuracy
    intent: "Test that block boundary detection remains accurate."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_existing_code_patterns
    intent: "Test common existing code patterns still work."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_import_compatibility
    intent: "Test that essential imports still work."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_regression_in_core_functionality
    intent: "Test that core functionality has no regressions."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_basic_functionality.py

```yaml
test_file: tests/parser/test_basic_functionality.py
test_count: 14
legacy_imports:
  - markdown_chunker.parser.types.NodeType
  - markdown_chunker.parser.types.Position
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_data_structures
    intent: "Test basic data structures."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fenced_block_extraction
    intent: "Test fenced block extraction with assertions."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_element_detection
    intent: "Test basic element detection (Stage 2 functionality moved)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis
    intent: "Test basic content analysis (Stage 2 functionality moved)."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration
    intent: "Test basic configuration (Stage 2 functionality moved)."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering_fixes
    intent: "Test that line numbering fixes are working."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_block_fixes
    intent: "Test that nested block fixes are working."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_structures
    intent: "Test basic data structures."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fenced_block_extraction
    intent: "Test fenced block extraction with assertions."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_element_detection
    intent: "Test basic element detection (Stage 2 functionality moved)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis
    intent: "Test basic content analysis (Stage 2 functionality moved)."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration
    intent: "Test basic configuration (Stage 2 functionality moved)."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering_fixes
    intent: "Test that line numbering fixes are working."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_block_fixes
    intent: "Test that nested block fixes are working."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_content_analysis_properties.py

```yaml
test_file: tests/parser/test_content_analysis_properties.py
test_count: 20
legacy_imports:
  - markdown_chunker.parser.analyzer.ContentAnalyzer
  - markdown_chunker.parser.elements.detect_elements
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_basic_metrics_non_negative
    intent: "**Property 12a: Non-negative Metrics**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, all numeric metrics should be non-negative."
  - name: test_property_ratios_sum_to_one
    intent: "**Property 12b: Ratio Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, code_ratio + text_ratio should approximately equal 1."
  - name: test_property_code_blocks_detected
    intent: "**Property 12c: Code Block Detection**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, code_block_count should match
the number of fenced blocks."
  - name: test_property_mixed_content_detection
    intent: "**Property 12d: Mixed Content Detection**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_complexity_score_bounded
    intent: "**Property 12e: Complexity Score Bounds**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, complexity_score should be between 0 and 1."
  - name: test_property_content_type_valid
    intent: "**Property 12f: Content Type Classification**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, content_type should be one of the valid types."
  - name: test_property_header_count_consistency
    intent: "**Property 12g: Header Count Consistency**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, sum of header_count values should equal
total number of detected headers."
  - name: test_property_language_extraction
    intent: "**Property 12h: Language Extraction**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_line_metrics_consistency
    intent: "**Property 12i: Line Metrics Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, line-related metrics should be consistent."
  - name: test_property_boolean_flags_consistency
    intent: "**Property 12j: Boolean Flags Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, boolean flags should be consistent with counts."
  - name: test_property_basic_metrics_non_negative
    intent: "**Property 12a: Non-negative Metrics**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, all numeric metrics should be non-negative."
  - name: test_property_ratios_sum_to_one
    intent: "**Property 12b: Ratio Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, code_ratio + text_ratio should approximately equal 1."
  - name: test_property_code_blocks_detected
    intent: "**Property 12c: Code Block Detection**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, code_block_count should match
the number of fenced blocks."
  - name: test_property_mixed_content_detection
    intent: "**Property 12d: Mixed Content Detection**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_complexity_score_bounded
    intent: "**Property 12e: Complexity Score Bounds**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, complexity_score should be between 0 and 1."
  - name: test_property_content_type_valid
    intent: "**Property 12f: Content Type Classification**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, content_type should be one of the valid types."
  - name: test_property_header_count_consistency
    intent: "**Property 12g: Header Count Consistency**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, sum of header_count values should equal
total number of detected headers."
  - name: test_property_language_extraction
    intent: "**Property 12h: Language Extraction**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_line_metrics_consistency
    intent: "**Property 12i: Line Metrics Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, line-related metrics should be consistent."
  - name: test_property_boolean_flags_consistency
    intent: "**Property 12j: Boolean Flags Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown text, boolean flags should be consistent with counts."
```

### tests/parser/test_core.py

```yaml
test_file: tests/parser/test_core.py
test_count: 6
legacy_imports:
  - markdown_chunker.parser.core
v2_applicable: true
removed_functionality: false

tests:
  - name: test_can_instantiate
    intent: "Test that FencedBlockExtractor can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ParserInterface can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_fenced_blocks_exists
    intent: "Test that extract_fenced_blocks function exists."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that FencedBlockExtractor can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ParserInterface can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_fenced_blocks_exists
    intent: "Test that extract_fenced_blocks function exists."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_core_new.py

```yaml
test_file: tests/parser/test_core_new.py
test_count: 60
legacy_imports:
  - markdown_chunker.parser.core.FencedBlockExtractor
  - markdown_chunker.parser.core.ParserInterface
  - markdown_chunker.parser.core.Stage1Interface
  - markdown_chunker.parser.core.extract_fenced_blocks
  - markdown_chunker.parser.errors.MarkdownParsingError
v2_applicable: false
removed_functionality: true

tests:
  - name: test_instantiation
    intent: "Test that FencedBlockExtractor can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_simple_code_block
    intent: "Test extracting a simple fenced code block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_multiple_blocks
    intent: "Test extracting multiple fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_block_without_language
    intent: "Test extracting block without language specifier."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_nested_blocks
    intent: "Test extracting nested fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_unclosed_block
    intent: "Test handling of unclosed fenced block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_empty_document
    intent: "Test extracting from empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_no_blocks
    intent: "Test document with no fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_line_numbers
    intent: "Test that line numbers are correctly tracked."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_nesting_level
    intent: "Test that nesting levels are tracked."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_instantiation
    intent: "Test that ParserInterface can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_simple_document
    intent: "Test processing a simple markdown document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_empty_document
    intent: "Test processing empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_document_with_multiple_blocks
    intent: "Test processing document with multiple code blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_prepare_for_chunking
    intent: "Test prepare_for_chunking method."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_stage1_interface_alias
    intent: "Test that Stage1Interface is an alias for ParserInterface."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_time_tracked
    intent: "Test that processing time is tracked."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_content_analysis_present
    intent: "Test that content analysis is performed."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_function
    intent: "Test extract_fenced_blocks convenience function."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_empty
    intent: "Test extract_fenced_blocks with empty input."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_no_blocks
    intent: "Test extract_fenced_blocks with no code blocks."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_backticks_in_content
    intent: "Test block containing backticks in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_consecutive_blocks
    intent: "Test consecutive blocks without text between."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_empty_lines
    intent: "Test block with empty lines in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_indented_block
    intent: "Test indented fenced block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_special_characters
    intent: "Test block with special characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_long_document
    intent: "Test processing very long document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_document_with_unicode
    intent: "Test document with unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_document_with_mixed_line_endings
    intent: "Test document with mixed line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_null_input_handling
    intent: "Test handling of None input."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_instantiation
    intent: "Test that FencedBlockExtractor can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_simple_code_block
    intent: "Test extracting a simple fenced code block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_multiple_blocks
    intent: "Test extracting multiple fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_block_without_language
    intent: "Test extracting block without language specifier."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_nested_blocks
    intent: "Test extracting nested fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_unclosed_block
    intent: "Test handling of unclosed fenced block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_empty_document
    intent: "Test extracting from empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_no_blocks
    intent: "Test document with no fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_line_numbers
    intent: "Test that line numbers are correctly tracked."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_nesting_level
    intent: "Test that nesting levels are tracked."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_instantiation
    intent: "Test that ParserInterface can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_simple_document
    intent: "Test processing a simple markdown document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_empty_document
    intent: "Test processing empty document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_process_document_with_multiple_blocks
    intent: "Test processing document with multiple code blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_prepare_for_chunking
    intent: "Test prepare_for_chunking method."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_stage1_interface_alias
    intent: "Test that Stage1Interface is an alias for ParserInterface."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_time_tracked
    intent: "Test that processing time is tracked."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_content_analysis_present
    intent: "Test that content analysis is performed."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_function
    intent: "Test extract_fenced_blocks convenience function."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_empty
    intent: "Test extract_fenced_blocks with empty input."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_fenced_blocks_no_blocks
    intent: "Test extract_fenced_blocks with no code blocks."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_backticks_in_content
    intent: "Test block containing backticks in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_consecutive_blocks
    intent: "Test consecutive blocks without text between."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_empty_lines
    intent: "Test block with empty lines in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_indented_block
    intent: "Test indented fenced block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_with_special_characters
    intent: "Test block with special characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_long_document
    intent: "Test processing very long document."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_document_with_unicode
    intent: "Test document with unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_document_with_mixed_line_endings
    intent: "Test document with mixed line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_null_input_handling
    intent: "Test handling of None input."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_documentation_accuracy.py

```yaml
test_file: tests/parser/test_documentation_accuracy.py
test_count: 14
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.LineNumberConverter
  - markdown_chunker.parser.config.Stage1Config
v2_applicable: false
removed_functionality: true

tests:
  - name: test_line_numbering_documentation
    intent: "Test that line numbering is documented as 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_nested_block_documentation
    intent: "Test that nested block capabilities match documentation."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_test_count_accuracy
    intent: "Test that reported test counts match actual tests."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_automated_test_validation
    intent: "Test that test_basic_functionality.py is actually automated."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_coverage_optional_documentation
    intent: "Test that coverage is actually optional."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_compliance_documentation
    intent: "Test that API actually complies with 1-based specification."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_configuration_documentation
    intent: "Test that configuration works as documented."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_line_numbering_documentation
    intent: "Test that line numbering is documented as 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_nested_block_documentation
    intent: "Test that nested block capabilities match documentation."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_test_count_accuracy
    intent: "Test that reported test counts match actual tests."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_automated_test_validation
    intent: "Test that test_basic_functionality.py is actually automated."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_coverage_optional_documentation
    intent: "Test that coverage is actually optional."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_compliance_documentation
    intent: "Test that API actually complies with 1-based specification."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_configuration_documentation
    intent: "Test that configuration works as documented."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_element_detector.py

```yaml
test_file: tests/parser/test_element_detector.py
test_count: 24
legacy_imports:
  - markdown_chunker.parser.elements.ElementDetector
  - markdown_chunker.parser.elements.detect_elements
  - markdown_chunker.parser.types.ListItem
v2_applicable: true
removed_functionality: false

tests:
  - name: test_simple_detection
    intent: "Test detecting elements in simple markdown."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_lists
    intent: "Test detecting complex nested lists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tables_detection
    intent: "Test detecting tables with different alignments."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_hierarchy
    intent: "Test header hierarchy building."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_lists
    intent: "Test task list detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_table
    intent: "Test handling malformed tables."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_headers
    intent: "Test handling empty headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anchor_generation
    intent: "Test anchor generation for headers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_item_parsing
    intent: "Test parsing individual list items."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detector_initialization
    intent: "Test detector initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_alignment_parsing
    intent: "Test table alignment parsing."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_type_determination
    intent: "Test list type determination."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simple_detection
    intent: "Test detecting elements in simple markdown."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_lists
    intent: "Test detecting complex nested lists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tables_detection
    intent: "Test detecting tables with different alignments."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_hierarchy
    intent: "Test header hierarchy building."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_lists
    intent: "Test task list detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_table
    intent: "Test handling malformed tables."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_headers
    intent: "Test handling empty headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anchor_generation
    intent: "Test anchor generation for headers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_item_parsing
    intent: "Test parsing individual list items."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detector_initialization
    intent: "Test detector initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_alignment_parsing
    intent: "Test table alignment parsing."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_type_determination
    intent: "Test list type determination."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_enhanced_nesting.py

```yaml
test_file: tests/parser/test_enhanced_nesting.py
test_count: 16
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_mixed_fence_types_nesting
    intent: "Test mixed fence types - NEW CORRECT BEHAVIOR: nested content preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deep_nesting_levels
    intent: "Test deep nesting - NEW CORRECT BEHAVIOR: content preservation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_sibling_blocks_same_level
    intent: "Test sibling blocks at the same nesting level."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_level_calculation_precision
    intent: "Test precise nesting level calculation - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_incorrect_nesting_handling
    intent: "Test handling of incorrect/overlapping nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_nested_blocks
    intent: "Test nested blocks with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_with_different_fence_lengths
    intent: "Test nesting with different fence lengths."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_nesting_level_consistency
    intent: "Regression test: nesting levels should be consistent."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types_nesting
    intent: "Test mixed fence types - NEW CORRECT BEHAVIOR: nested content preserved."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deep_nesting_levels
    intent: "Test deep nesting - NEW CORRECT BEHAVIOR: content preservation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_sibling_blocks_same_level
    intent: "Test sibling blocks at the same nesting level."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_level_calculation_precision
    intent: "Test precise nesting level calculation - NEW CORRECT BEHAVIOR."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_incorrect_nesting_handling
    intent: "Test handling of incorrect/overlapping nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_nested_blocks
    intent: "Test nested blocks with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_with_different_fence_lengths
    intent: "Test nesting with different fence lengths."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_nesting_level_consistency
    intent: "Regression test: nesting levels should be consistent."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_error_collector_new.py

```yaml
test_file: tests/parser/test_error_collector_new.py
test_count: 50
legacy_imports:
  - markdown_chunker.parser.errors.ErrorCollector
  - markdown_chunker.parser.errors.ErrorInfo
  - markdown_chunker.parser.errors.ErrorSeverity
  - markdown_chunker.parser.errors.ErrorSummary
  - markdown_chunker.parser.errors.SourceLocation
v2_applicable: true
removed_functionality: false

tests:
  - name: test_instantiation
    intent: "Test that ErrorCollector can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_error
    intent: "Test adding an error."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_warning
    intent: "Test adding a warning."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_critical_error
    intent: "Test adding a critical error."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_errors_initially_false
    intent: "Test that has_errors is initially False."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_warnings_initially_false
    intent: "Test that has_warnings is initially False."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary
    intent: "Test getting error summary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear
    intent: "Test clearing errors and warnings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_format_report
    intent: "Test formatting error report."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_creation
    intent: "Test creating SourceLocation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_with_filename
    intent: "Test SourceLocation with filename."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_str
    intent: "Test SourceLocation string representation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_source_location_from_position
    intent: "Test creating SourceLocation from Position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_info_creation
    intent: "Test creating ErrorInfo."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_info_str
    intent: "Test ErrorInfo string representation."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warning_info_creation
    intent: "Test creating WarningInfo."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warning_info_str
    intent: "Test WarningInfo string representation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_creation
    intent: "Test creating ErrorSummary."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_errors
    intent: "Test has_errors method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_warnings
    intent: "Test has_warnings method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_critical_errors
    intent: "Test has_critical_errors method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_get_total_issues
    intent: "Test get_total_issues method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_full_workflow
    intent: "Test complete error collection workflow."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_location
    intent: "Test adding error with location."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_categories
    intent: "Test errors from multiple categories."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_instantiation
    intent: "Test that ErrorCollector can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_error
    intent: "Test adding an error."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_warning
    intent: "Test adding a warning."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_critical_error
    intent: "Test adding a critical error."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_errors_initially_false
    intent: "Test that has_errors is initially False."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_warnings_initially_false
    intent: "Test that has_warnings is initially False."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary
    intent: "Test getting error summary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear
    intent: "Test clearing errors and warnings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_format_report
    intent: "Test formatting error report."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_creation
    intent: "Test creating SourceLocation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_with_filename
    intent: "Test SourceLocation with filename."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_source_location_str
    intent: "Test SourceLocation string representation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_source_location_from_position
    intent: "Test creating SourceLocation from Position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_info_creation
    intent: "Test creating ErrorInfo."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_info_str
    intent: "Test ErrorInfo string representation."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warning_info_creation
    intent: "Test creating WarningInfo."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warning_info_str
    intent: "Test WarningInfo string representation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_creation
    intent: "Test creating ErrorSummary."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_errors
    intent: "Test has_errors method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_warnings
    intent: "Test has_warnings method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_has_critical_errors
    intent: "Test has_critical_errors method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_summary_get_total_issues
    intent: "Test get_total_issues method."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_full_workflow
    intent: "Test complete error collection workflow."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_location
    intent: "Test adding error with location."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_categories
    intent: "Test errors from multiple categories."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_extraction_heuristics.py

```yaml
test_file: tests/parser/test_extraction_heuristics.py
test_count: 26
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_false_positive_prevention
    intent: "Test prevention of false positive block detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_minimum_fence_length
    intent: "Test minimum fence length requirements."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_indented_fences
    intent: "Test handling of indented fences."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fence_with_extra_characters
    intent: "Test fences with extra characters after language."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_lengths
    intent: "Test blocks with different fence lengths."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_handling
    intent: "Test handling of unclosed blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handling
    intent: "Test handling of blocks without language specification."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_case_insensitive_language_detection
    intent: "Test case-insensitive language detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_special_characters_in_content
    intent: "Test blocks with special characters in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_handling
    intent: "Test handling of various whitespace scenarios."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_boundary_detection_accuracy
    intent: "Test accuracy of block boundary detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_consecutive_blocks_boundaries
    intent: "Test boundary detection for consecutive blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_phantom_block_prevention
    intent: "Regression test: ensure phantom blocks are not created."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_false_positive_prevention
    intent: "Test prevention of false positive block detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_minimum_fence_length
    intent: "Test minimum fence length requirements."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_indented_fences
    intent: "Test handling of indented fences."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fence_with_extra_characters
    intent: "Test fences with extra characters after language."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_lengths
    intent: "Test blocks with different fence lengths."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_handling
    intent: "Test handling of unclosed blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handling
    intent: "Test handling of blocks without language specification."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_case_insensitive_language_detection
    intent: "Test case-insensitive language detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_special_characters_in_content
    intent: "Test blocks with special characters in content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_handling
    intent: "Test handling of various whitespace scenarios."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_boundary_detection_accuracy
    intent: "Test accuracy of block boundary detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_consecutive_blocks_boundaries
    intent: "Test boundary detection for consecutive blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_phantom_block_prevention
    intent: "Regression test: ensure phantom blocks are not created."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_fenced_block_extractor.py

```yaml
test_file: tests/parser/test_fenced_block_extractor.py
test_count: 20
legacy_imports:
  - markdown_chunker.parser.FencedBlockExtractor
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_simple_extraction
    intent: "Test extracting simple fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks
    intent: "Test extracting fenced blocks from document with nested structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_languages
    intent: "Test extracting blocks with different languages."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block
    intent: "Test handling unclosed blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types
    intent: "Test handling mixed fence types."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input
    intent: "Test handling empty input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only
    intent: "Test handling whitespace-only input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_position_calculation
    intent: "Test position calculation."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extractor_initialization
    intent: "Test extractor initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_offset
    intent: "Test offset calculation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simple_extraction
    intent: "Test extracting simple fenced blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks
    intent: "Test extracting fenced blocks from document with nested structure."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_languages
    intent: "Test extracting blocks with different languages."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block
    intent: "Test handling unclosed blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types
    intent: "Test handling mixed fence types."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input
    intent: "Test handling empty input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only
    intent: "Test handling whitespace-only input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_position_calculation
    intent: "Test position calculation."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extractor_initialization
    intent: "Test extractor initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_offset
    intent: "Test offset calculation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_integration.py

```yaml
test_file: tests/parser/test_integration.py
test_count: 32
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.validate_and_normalize_input
v2_applicable: true
removed_functionality: false

tests:
  - name: test_simple_document_processing
    intent: "Test processing a simple document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_document_processing
    intent: "Test processing a complex document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_processing
    intent: "Test processing document with nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prepare_for_chunking
    intent: "Test preparing results for Stage 2."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_summary
    intent: "Test getting processing summary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_results_validation
    intent: "Test results validation."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling
    intent: "Test error handling in integration."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration_usage
    intent: "Test using input validation and normalization."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_markdown
    intent: "Test markdown processing convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_markdown
    intent: "Test markdown analysis convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prepare_for_stage2
    intent: "Test Stage 2 preparation."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_time
    intent: "Test that processing time is reasonable."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_usage
    intent: "Test memory usage doesn't grow excessively."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_input_recovery
    intent: "Test recovery from malformed input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_handling
    intent: "Test handling of empty input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_input
    intent: "Test handling of very large input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simple_document_processing
    intent: "Test processing a simple document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_document_processing
    intent: "Test processing a complex document."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_processing
    intent: "Test processing document with nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prepare_for_chunking
    intent: "Test preparing results for Stage 2."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_summary
    intent: "Test getting processing summary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_results_validation
    intent: "Test results validation."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling
    intent: "Test error handling in integration."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration_usage
    intent: "Test using input validation and normalization."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_markdown
    intent: "Test markdown processing convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_markdown
    intent: "Test markdown analysis convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prepare_for_stage2
    intent: "Test Stage 2 preparation."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_time
    intent: "Test that processing time is reasonable."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_usage
    intent: "Test memory usage doesn't grow excessively."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_input_recovery
    intent: "Test recovery from malformed input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_handling
    intent: "Test handling of empty input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_input
    intent: "Test handling of very large input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_line_numbering_regression.py

```yaml
test_file: tests/parser/test_line_numbering_regression.py
test_count: 14
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.LineNumberConverter
v2_applicable: true
removed_functionality: false

tests:
  - name: test_prevent_zero_based_line_numbers
    intent: "Ensure line numbers are never 0-based (regression test)."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_never_zero_based
    intent: "Ensure multiple blocks never use 0-based numbering."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_consistency
    intent: "Test that line numbers are consistent across different scenarios."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_line_numbers
    intent: "Test that unclosed blocks also use 1-based numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_line_numbers
    intent: "Test that nested blocks use 1-based numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_compliance_validation
    intent: "Test that all returned blocks comply with 1-based API specification."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_validation_methods
    intent: "Test that line number validation methods work correctly."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_zero_based_line_numbers
    intent: "Ensure line numbers are never 0-based (regression test)."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_never_zero_based
    intent: "Ensure multiple blocks never use 0-based numbering."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_consistency
    intent: "Test that line numbers are consistent across different scenarios."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_line_numbers
    intent: "Test that unclosed blocks also use 1-based numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_line_numbers
    intent: "Test that nested blocks use 1-based numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_compliance_validation
    intent: "Test that all returned blocks comply with 1-based API specification."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_validation_methods
    intent: "Test that line number validation methods work correctly."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_markdown_ast_content_preservation.py

```yaml
test_file: tests/parser/test_markdown_ast_content_preservation.py
test_count: 11
legacy_imports:
  - markdown_chunker.parser.parse_to_ast
  - markdown_chunker.parser.types.NodeType
v2_applicable: true
removed_functionality: false

tests:
  - name: test_paragraph_has_actual_content
    intent: "Test that paragraph nodes contain actual content, not empty strings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_has_actual_content
    intent: "Test that header nodes contain actual content, not empty strings."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_not_nesting_paragraphs
    intent: "Test that paragraphs are siblings of headers, not children."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_inline_code_content_preserved
    intent: "Test that inline code content is preserved in parent paragraphs."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_inline_elements
    intent: "Test content preservation with multiple inline elements."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_nested_structure
    intent: "Test proper hierarchy with complex nested structures."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_lines_handling
    intent: "Test that empty lines don't break content preservation."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_preservation
    intent: "Test content preservation in mixed content scenarios."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_empty_content_bug
    intent: "Regression test to ensure the empty content bug doesn't return."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_word_content
    intent: "Test content preservation for single words."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_special_characters_content
    intent: "Test content preservation with special characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_nested_fence_handling.py

```yaml
test_file: tests/parser/test_nested_fence_handling.py
test_count: 12
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_nested_fences_not_separate_blocks
    intent: "Test that nested fences create only one outer block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fences_mixed_types
    intent: "Test nested fences with mixed types (``` containing ~~~)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fences_reverse_mixed_types
    intent: "Test nested fences with reverse mixed types (~~~ containing ```)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deep_nesting
    intent: "Test deep nesting scenarios (3+ levels)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_nested_blocks
    intent: "Test handling of unclosed nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_nested_blocks_same_level
    intent: "Test multiple nested blocks at the same level."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_with_same_fence_type
    intent: "Test nesting with same fence type (different lengths)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_with_language_attributes
    intent: "Test nested blocks with language attributes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_phantom_blocks_for_inner_fences
    intent: "Test that inner fence markers don't create phantom blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complex_real_world_example
    intent: "Test complex real-world nested fence example."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_edge_case_empty_nested_block
    intent: "Test edge case with empty nested block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_no_phantom_blocks
    intent: "Regression test to ensure no phantom blocks are created."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_nesting_properties.py

```yaml
test_file: tests/parser/test_nesting_properties.py
test_count: 10
legacy_imports:
  - markdown_chunker.parser.nesting_resolver.BlockCandidate
  - markdown_chunker.parser.nesting_resolver.resolve_nesting
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_parent_contains_children
    intent: "**Property 7a: Parent Containment**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_no_overlaps_at_same_level
    intent: "**Property 7b: No Overlaps at Same Level**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_nesting_level_consistency
    intent: "**Property 7c: Nesting Level Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_resolution_is_deterministic
    intent: "**Property 7d: Deterministic Resolution**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_blocks_have_nesting_info
    intent: "**Property 7e: Complete Nesting Information**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_parent_contains_children
    intent: "**Property 7a: Parent Containment**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_no_overlaps_at_same_level
    intent: "**Property 7b: No Overlaps at Same Level**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_nesting_level_consistency
    intent: "**Property 7c: Nesting Level Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_resolution_is_deterministic
    intent: "**Property 7d: Deterministic Resolution**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_blocks_have_nesting_info
    intent: "**Property 7e: Complete Nesting Information**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_nesting_resolver.py

```yaml
test_file: tests/parser/test_nesting_resolver.py
test_count: 50
legacy_imports:
  - markdown_chunker.parser.nesting_resolver.BlockCandidate
  - markdown_chunker.parser.nesting_resolver.NestingResolver
  - markdown_chunker.parser.nesting_resolver.get_children
  - markdown_chunker.parser.nesting_resolver.get_max_nesting_depth
  - markdown_chunker.parser.nesting_resolver.get_nesting_tree
v2_applicable: false
removed_functionality: true

tests:
  - name: test_contains_true
    intent: "Test that contains() returns True for proper containment."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_contains_false_separate
    intent: "Test that contains() returns False for separate blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_contains_false_adjacent
    intent: "Test that contains() returns False for adjacent blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_true
    intent: "Test that overlaps() returns True for overlapping blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_false_separate
    intent: "Test that overlaps() returns False for separate blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_false_containment
    intent: "Test that overlaps() returns False for proper containment."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_flat_blocks_no_nesting
    intent: "Test resolution of flat blocks (no nesting)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_simple_nesting_one_level
    intent: "Test resolution of simple one-level nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deep_nesting_multiple_levels
    intent: "Test resolution of deep nesting (multiple levels)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlapping_blocks_raises_error
    intent: "Test that overlapping blocks raise ValueError."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_children_same_parent
    intent: "Test resolution with multiple children of same parent."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_empty_blocks_list
    intent: "Test resolution with no blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_flat
    intent: "Test resolve_nesting with flat blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_nested
    intent: "Test resolve_nesting with nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_empty
    intent: "Test resolve_nesting with empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_valid_nesting
    intent: "Test validation of valid nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_invalid_nesting
    intent: "Test validation of invalid nesting (overlapping)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_empty_list
    intent: "Test validation of empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_nesting_tree
    intent: "Test get_nesting_tree function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_children
    intent: "Test get_children function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_max_nesting_depth
    intent: "Test get_max_nesting_depth function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_max_nesting_depth_empty
    intent: "Test get_max_nesting_depth with empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_adjacent_blocks_not_overlapping
    intent: "Test that adjacent blocks are not considered overlapping."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_single_block
    intent: "Test resolution with single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_blocks_with_metadata
    intent: "Test that block metadata is preserved during resolution."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_contains_true
    intent: "Test that contains() returns True for proper containment."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_contains_false_separate
    intent: "Test that contains() returns False for separate blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_contains_false_adjacent
    intent: "Test that contains() returns False for adjacent blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_true
    intent: "Test that overlaps() returns True for overlapping blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_false_separate
    intent: "Test that overlaps() returns False for separate blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlaps_false_containment
    intent: "Test that overlaps() returns False for proper containment."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_flat_blocks_no_nesting
    intent: "Test resolution of flat blocks (no nesting)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_simple_nesting_one_level
    intent: "Test resolution of simple one-level nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deep_nesting_multiple_levels
    intent: "Test resolution of deep nesting (multiple levels)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_overlapping_blocks_raises_error
    intent: "Test that overlapping blocks raise ValueError."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_children_same_parent
    intent: "Test resolution with multiple children of same parent."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_empty_blocks_list
    intent: "Test resolution with no blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_flat
    intent: "Test resolve_nesting with flat blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_nested
    intent: "Test resolve_nesting with nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_resolve_nesting_empty
    intent: "Test resolve_nesting with empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_valid_nesting
    intent: "Test validation of valid nesting."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_invalid_nesting
    intent: "Test validation of invalid nesting (overlapping)."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_empty_list
    intent: "Test validation of empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_nesting_tree
    intent: "Test get_nesting_tree function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_children
    intent: "Test get_children function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_max_nesting_depth
    intent: "Test get_max_nesting_depth function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_max_nesting_depth_empty
    intent: "Test get_max_nesting_depth with empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_adjacent_blocks_not_overlapping
    intent: "Test that adjacent blocks are not considered overlapping."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_single_block
    intent: "Test resolution with single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_blocks_with_metadata
    intent: "Test that block metadata is preserved during resolution."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_parser_correctness_properties.py

```yaml
test_file: tests/parser/test_parser_correctness_properties.py
test_count: 16
legacy_imports:
  - markdown_chunker.parser.core.Stage1Interface
  - markdown_chunker.parser.elements.detect_elements
  - markdown_chunker.parser.types.NodeType
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_all_headers_detected
    intent: "**Property 11a: Header Detection Completeness**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_code_blocks_detected
    intent: "**Property 11b: Code Block Detection Completeness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_lists_detected
    intent: "**Property 11c: List Detection Completeness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_tables_detected
    intent: "**Property 11d: Table Detection Completeness**"
    v2_component: ContentAnalysis.tables
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_parser_never_crashes
    intent: "**Property 11e: Parser Robustness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_ast_structure_valid
    intent: "**Property 11f: AST Structure Validity**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_code_block_content_preserved
    intent: "**Property 11g: Code Block Content Preservation**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_analysis_metrics_consistent
    intent: "**Property 11h: Analysis Metrics Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown input:
- analysis metrics must be internally consistent
- ratios must sum to approximately 1."
  - name: test_property_all_headers_detected
    intent: "**Property 11a: Header Detection Completeness**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_code_blocks_detected
    intent: "**Property 11b: Code Block Detection Completeness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_lists_detected
    intent: "**Property 11c: List Detection Completeness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_all_tables_detected
    intent: "**Property 11d: Table Detection Completeness**"
    v2_component: ContentAnalysis.tables
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_parser_never_crashes
    intent: "**Property 11e: Parser Robustness**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_ast_structure_valid
    intent: "**Property 11f: AST Structure Validity**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_code_block_content_preserved
    intent: "**Property 11g: Code Block Content Preservation**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_property_analysis_metrics_consistent
    intent: "**Property 11h: Analysis Metrics Consistency**"
    v2_component: Parser
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown input:
- analysis metrics must be internally consistent
- ratios must sum to approximately 1."
```

### tests/parser/test_position_accuracy.py

```yaml
test_file: tests/parser/test_position_accuracy.py
test_count: 38
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.elements.detect_elements
v2_applicable: true
removed_functionality: false

tests:
  - name: test_header_line_numbers_accurate
    intent: "Test that header line numbers are accurate."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_offset_accurate
    intent: "Test that header offsets are accurate."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_headers_positions
    intent: "Test positions of multiple headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_item_line_numbers
    intent: "Test that list item line numbers are accurate."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_list_positions
    intent: "Test positions of nested list items."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_start_end_lines
    intent: "Test list start and end line numbers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_line_numbers
    intent: "Test that table line numbers are accurate."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_tables_positions
    intent: "Test positions of multiple tables."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_block_line_numbers
    intent: "Test that code block line numbers are accurate."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_block_offsets
    intent: "Test that code block offsets are accurate."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_code_blocks_positions
    intent: "Test positions of multiple code blocks."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_and_lists_positions
    intent: "Test positions when headers and lists are mixed."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_element_types_positions
    intent: "Test positions when all element types are present."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_and_offset_consistency
    intent: "Test that line numbers and offsets are consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_start_end_line_consistency
    intent: "Test that start and end lines are consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_elements_position_hierarchy
    intent: "Test that nested elements maintain position hierarchy."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_lines_dont_affect_positions
    intent: "Test that empty lines don't affect position accuracy."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_windows_line_endings
    intent: "Test position handling with Windows line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content_positions
    intent: "Test position handling with Unicode content."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_line_numbers_accurate
    intent: "Test that header line numbers are accurate."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_offset_accurate
    intent: "Test that header offsets are accurate."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_headers_positions
    intent: "Test positions of multiple headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_item_line_numbers
    intent: "Test that list item line numbers are accurate."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_list_positions
    intent: "Test positions of nested list items."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_start_end_lines
    intent: "Test list start and end line numbers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_line_numbers
    intent: "Test that table line numbers are accurate."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_tables_positions
    intent: "Test positions of multiple tables."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_block_line_numbers
    intent: "Test that code block line numbers are accurate."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_block_offsets
    intent: "Test that code block offsets are accurate."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_code_blocks_positions
    intent: "Test positions of multiple code blocks."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_and_lists_positions
    intent: "Test positions when headers and lists are mixed."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_element_types_positions
    intent: "Test positions when all element types are present."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_and_offset_consistency
    intent: "Test that line numbers and offsets are consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_start_end_line_consistency
    intent: "Test that start and end lines are consistent."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_elements_position_hierarchy
    intent: "Test that nested elements maintain position hierarchy."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_lines_dont_affect_positions
    intent: "Test that empty lines don't affect position accuracy."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_windows_line_endings
    intent: "Test position handling with Windows line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content_positions
    intent: "Test position handling with Unicode content."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_preamble.py

```yaml
test_file: tests/parser/test_preamble.py
test_count: 50
legacy_imports:
  - markdown_chunker.parser.types.PreambleInfo
  - markdown_chunker.parser.analyzer.PreambleExtractor
  - markdown_chunker.parser.analyzer.PreambleExtractor
  - markdown_chunker.parser.analyzer.PreambleExtractor
  - markdown_chunker.parser.analyzer.PreambleExtractor
v2_applicable: true
removed_functionality: false

tests:
  - name: test_create_introduction_preamble
    intent: "Test creating an introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_metadata_preamble
    intent: "Test creating a metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_type_raises_error
    intent: "Test that invalid type raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_line_count_raises_error
    intent: "Test that negative line_count raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_char_count_raises_error
    intent: "Test that negative char_count raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_metadata_without_fields_raises_error
    intent: "Test that has_metadata=True without fields raises ValueError."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test converting preamble to dictionary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_preamble_types
    intent: "Test all valid preamble types."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_introduction_preamble
    intent: "Test extracting introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_preamble
    intent: "Test extracting metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_summary_preamble
    intent: "Test extracting summary preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_starts_with_header
    intent: "Test document starting with header has no preamble."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_empty_document
    intent: "Test empty document has no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_too_short_ignored
    intent: "Test very short preamble is ignored."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_general_preamble_type
    intent: "Test preamble without specific keywords is general."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_setext_header_detection
    intent: "Test detection of Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_metadata_fields
    intent: "Test extracting multiple metadata fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_char_and_line_count
    intent: "Test accurate char and line counting."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis_with_preamble
    intent: "Test ContentAnalysis includes preamble."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis_without_preamble
    intent: "Test ContentAnalysis without preamble."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary_includes_preamble
    intent: "Test get_summary includes preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_extracts_preamble
    intent: "Test that analyze_content extracts preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_no_preamble
    intent: "Test analyze_content with no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_with_metadata_preamble
    intent: "Test analyze_content extracts metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary_includes_preamble_from_analyzer
    intent: "Test get_summary includes preamble from analyzer."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_introduction_preamble
    intent: "Test creating an introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_metadata_preamble
    intent: "Test creating a metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_type_raises_error
    intent: "Test that invalid type raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_line_count_raises_error
    intent: "Test that negative line_count raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_char_count_raises_error
    intent: "Test that negative char_count raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_metadata_without_fields_raises_error
    intent: "Test that has_metadata=True without fields raises ValueError."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test converting preamble to dictionary."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_preamble_types
    intent: "Test all valid preamble types."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_introduction_preamble
    intent: "Test extracting introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_preamble
    intent: "Test extracting metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_summary_preamble
    intent: "Test extracting summary preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_starts_with_header
    intent: "Test document starting with header has no preamble."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_empty_document
    intent: "Test empty document has no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_too_short_ignored
    intent: "Test very short preamble is ignored."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_general_preamble_type
    intent: "Test preamble without specific keywords is general."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_setext_header_detection
    intent: "Test detection of Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_metadata_fields
    intent: "Test extracting multiple metadata fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_char_and_line_count
    intent: "Test accurate char and line counting."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis_with_preamble
    intent: "Test ContentAnalysis includes preamble."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_analysis_without_preamble
    intent: "Test ContentAnalysis without preamble."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary_includes_preamble
    intent: "Test get_summary includes preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_extracts_preamble
    intent: "Test that analyze_content extracts preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_no_preamble
    intent: "Test analyze_content with no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_analyze_content_with_metadata_preamble
    intent: "Test analyze_content extracts metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_summary_includes_preamble_from_analyzer
    intent: "Test get_summary includes preamble from analyzer."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_preamble_extractor.py

```yaml
test_file: tests/parser/test_preamble_extractor.py
test_count: 58
legacy_imports:
  - markdown_chunker.parser.preamble.PreambleExtractor
  - markdown_chunker.parser.preamble.PreambleInfo
  - markdown_chunker.parser.preamble.PreambleType
  - markdown_chunker.parser.preamble.extract_preamble
v2_applicable: true
removed_functionality: false

tests:
  - name: test_enum_values
    intent: "Test that all enum values are defined."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_creation
    intent: "Test creating PreambleInfo."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test serialization to dict."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test extractor initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_preamble
    intent: "Test extracting metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_introduction_preamble
    intent: "Test extracting introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_summary_preamble
    intent: "Test extracting summary preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_general_preamble
    intent: "Test extracting general preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_starts_with_header
    intent: "Test document starting with header has no preamble."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_empty_document
    intent: "Test empty document has no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_too_short_ignored
    intent: "Test preamble below minimum thresholds is ignored."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_setext_header_detection
    intent: "Test detection of Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_metadata
    intent: "Test type detection for metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_summary
    intent: "Test type detection for summary."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_introduction
    intent: "Test type detection for introduction."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_general
    intent: "Test type detection for general content."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields
    intent: "Test metadata field extraction."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields_case_insensitive
    intent: "Test metadata extraction is case-insensitive."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields_empty
    intent: "Test metadata extraction with no metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_atx
    intent: "Test finding ATX-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_setext
    intent: "Test finding Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_none
    intent: "Test when no header is found."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_metadata_pattern
    intent: "Test metadata pattern detection."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_preamble_function
    intent: "Test convenience function works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_preamble_with_custom_params
    intent: "Test convenience function with custom parameters."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_headers_uses_first
    intent: "Test that only content before first header is extracted."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_lines_in_preamble
    intent: "Test preamble with empty lines."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test preamble with Unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_header_types
    intent: "Test document with both ATX and Setext headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enum_values
    intent: "Test that all enum values are defined."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_creation
    intent: "Test creating PreambleInfo."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_dict
    intent: "Test serialization to dict."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test extractor initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_preamble
    intent: "Test extracting metadata preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_introduction_preamble
    intent: "Test extracting introduction preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_summary_preamble
    intent: "Test extracting summary preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_general_preamble
    intent: "Test extracting general preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_starts_with_header
    intent: "Test document starting with header has no preamble."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_empty_document
    intent: "Test empty document has no preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_too_short_ignored
    intent: "Test preamble below minimum thresholds is ignored."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_setext_header_detection
    intent: "Test detection of Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_metadata
    intent: "Test type detection for metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_summary
    intent: "Test type detection for summary."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_introduction
    intent: "Test type detection for introduction."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detect_preamble_type_general
    intent: "Test type detection for general content."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields
    intent: "Test metadata field extraction."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields_case_insensitive
    intent: "Test metadata extraction is case-insensitive."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_metadata_fields_empty
    intent: "Test metadata extraction with no metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_atx
    intent: "Test finding ATX-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_setext
    intent: "Test finding Setext-style headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_first_header_none
    intent: "Test when no header is found."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_has_metadata_pattern
    intent: "Test metadata pattern detection."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_preamble_function
    intent: "Test convenience function works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_preamble_with_custom_params
    intent: "Test convenience function with custom parameters."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_headers_uses_first
    intent: "Test that only content before first header is extracted."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_lines_in_preamble
    intent: "Test preamble with empty lines."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test preamble with Unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_header_types
    intent: "Test document with both ATX and Setext headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_precise_boundaries.py

```yaml
test_file: tests/parser/test_precise_boundaries.py
test_count: 16
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
v2_applicable: true
removed_functionality: false

tests:
  - name: test_sequential_blocks_precise_boundaries
    intent: "Test sequential blocks have precise boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_precise_boundaries
    intent: "Test nested blocks have precise boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_phantom_prevention_boundaries
    intent: "Test phantom prevention doesn't affect legitimate boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types_boundaries
    intent: "Test mixed fence types have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_boundaries
    intent: "Test unclosed blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_blocks_boundaries
    intent: "Test empty blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_blocks_boundaries
    intent: "Test single-line blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_no_phantom_blocks_in_sequence
    intent: "Regression test: sequential blocks should not create phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_sequential_blocks_precise_boundaries
    intent: "Test sequential blocks have precise boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_blocks_precise_boundaries
    intent: "Test nested blocks have precise boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_phantom_prevention_boundaries
    intent: "Test phantom prevention doesn't affect legitimate boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_fence_types_boundaries
    intent: "Test mixed fence types have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_block_boundaries
    intent: "Test unclosed blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_blocks_boundaries
    intent: "Test empty blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_blocks_boundaries
    intent: "Test single-line blocks have correct boundaries."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_regression_no_phantom_blocks_in_sequence
    intent: "Regression test: sequential blocks should not create phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_pytest_compatibility.py

```yaml
test_file: tests/parser/test_pytest_compatibility.py
test_count: 12
legacy_imports:
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.LineNumberConverter
  - markdown_chunker.parser.resolve_nesting
  - markdown_chunker.parser.types.FencedBlock
  - markdown_chunker.parser.core
v2_applicable: true
removed_functionality: false

tests:
  - name: test_basic_functionality
    intent: "Test basic functionality works."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_imports_work
    intent: "Test that all imports work without coverage."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering
    intent: "Test line numbering functionality."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_resolver
    intent: "Test nesting resolver functionality."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_coverage_optional
    intent: "Test that coverage is optional."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_coverage_dependency
    intent: "Test that tests can run without coverage dependency."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_basic_functionality
    intent: "Test basic functionality works."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_imports_work
    intent: "Test that all imports work without coverage."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering
    intent: "Test line numbering functionality."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nesting_resolver
    intent: "Test nesting resolver functionality."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_coverage_optional
    intent: "Test that coverage is optional."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_coverage_dependency
    intent: "Test that tests can run without coverage dependency."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_regression_prevention.py

```yaml
test_file: tests/parser/test_regression_prevention.py
test_count: 18
legacy_imports:
  - markdown_chunker.parser.LineNumberConverter
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.parser.core
v2_applicable: true
removed_functionality: false

tests:
  - name: test_prevent_0_based_line_numbering_regression
    intent: "Prevent regression to 0-based line numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_nested_block_skipping_regression
    intent: "Prevent regression to skipping nested blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_pytest_coverage_dependency_regression
    intent: "Prevent regression to mandatory pytest-cov dependency."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_print_only_tests_regression
    intent: "Prevent regression to print-only tests."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_nesting_capability_overclaims_regression
    intent: "Prevent regression to overclaiming nesting capabilities."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_test_environment_dependency_regression
    intent: "Prevent regression to environment-specific test failures."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_api_breaking_changes_regression
    intent: "Prevent regression that breaks existing API."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_performance_regression
    intent: "Prevent significant performance regression."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_error_handling_regression
    intent: "Prevent regression in error handling."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_0_based_line_numbering_regression
    intent: "Prevent regression to 0-based line numbering."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_nested_block_skipping_regression
    intent: "Prevent regression to skipping nested blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_pytest_coverage_dependency_regression
    intent: "Prevent regression to mandatory pytest-cov dependency."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_print_only_tests_regression
    intent: "Prevent regression to print-only tests."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_nesting_capability_overclaims_regression
    intent: "Prevent regression to overclaiming nesting capabilities."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_test_environment_dependency_regression
    intent: "Prevent regression to environment-specific test failures."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_api_breaking_changes_regression
    intent: "Prevent regression that breaks existing API."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_performance_regression
    intent: "Prevent significant performance regression."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_prevent_error_handling_regression
    intent: "Prevent regression in error handling."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_smoke.py

```yaml
test_file: tests/parser/test_smoke.py
test_count: 28
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_basic_extraction_works
    intent: "Basic extraction works."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering_is_1based
    intent: "Line numbering is 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_work
    intent: "Multiple blocks work correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handled
    intent: "Empty language is handled."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_language_normalization
    intent: "Language names are extracted correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_reasonable
    intent: "Performance is reasonable for typical documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_graceful
    intent: "Error handling is graceful."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_extracted
    intent: "Headers are extracted correctly."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tables_extracted
    intent: "Tables are extracted correctly."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_metrics
    intent: "Content metrics are calculated correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_detection
    intent: "Preamble detection works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_blocks_inside_headers_ignored
    intent: "Headers inside code blocks are not extracted."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_at_position
    intent: "Line at position works correctly."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_position_at_line
    intent: "Position at line works correctly."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_basic_extraction_works
    intent: "Basic extraction works."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_numbering_is_1based
    intent: "Line numbering is 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_work
    intent: "Multiple blocks work correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_language_handled
    intent: "Empty language is handled."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_language_normalization
    intent: "Language names are extracted correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_reasonable
    intent: "Performance is reasonable for typical documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_graceful
    intent: "Error handling is graceful."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_extracted
    intent: "Headers are extracted correctly."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tables_extracted
    intent: "Tables are extracted correctly."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_metrics
    intent: "Content metrics are calculated correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_detection
    intent: "Preamble detection works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_blocks_inside_headers_ignored
    intent: "Headers inside code blocks are not extracted."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_at_position
    intent: "Line at position works correctly."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_position_at_line
    intent: "Position at line works correctly."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_smoke_critical_fixes.py

```yaml
test_file: tests/parser/test_smoke_critical_fixes.py
test_count: 36
legacy_imports:
  - markdown_chunker.parser.EnhancedASTBuilder
  - markdown_chunker.parser.ErrorCollector
  - markdown_chunker.parser.SourceLocation
  - markdown_chunker.parser.Stage1Interface
  - markdown_chunker.parser.create_text_recovery_utils
v2_applicable: false
removed_functionality: true

tests:
  - name: test_ast_building_with_inline_elements
    intent: "Test AST building with inline elements works."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_ast_validation_works
    intent: "Test AST validation catches basic issues."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_position_tracking_works
    intent: "Test position tracking in AST nodes."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_validation_prevents_failures
    intent: "Test API validation prevents common failures."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validation_catches_inconsistencies
    intent: "Test validation catches data inconsistencies."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_error_collector_works
    intent: "Test ErrorCollector basic functionality."
    v2_component: Error handling
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_source_location_works
    intent: "Test SourceLocation functionality."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_logging_replaces_print
    intent: "Test that logging is used instead of print."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_content_analysis_validation
    intent: "Test content analysis validation works."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fence_handler_basic_functionality
    intent: "Test fence handler basic operations."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fence_indentation_handling
    intent: "Test fence indentation is handled correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_closing_fence_detection
    intent: "Test closing fence detection works."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_text_recovery_basic_functionality
    intent: "Test text recovery basic operations."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_context_recovery
    intent: "Test block context recovery."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_performance
    intent: "Test that processing completes in reasonable time."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_smoke_tests_run_quickly
    intent: "Test that smoke tests themselves run quickly."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_pipeline_integration
    intent: "Test full pipeline works end-to-end."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_error_handling_integration
    intent: "Test error handling works across components."
    v2_component: Error handling
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_ast_building_with_inline_elements
    intent: "Test AST building with inline elements works."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_ast_validation_works
    intent: "Test AST validation catches basic issues."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_position_tracking_works
    intent: "Test position tracking in AST nodes."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_validation_prevents_failures
    intent: "Test API validation prevents common failures."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validation_catches_inconsistencies
    intent: "Test validation catches data inconsistencies."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_error_collector_works
    intent: "Test ErrorCollector basic functionality."
    v2_component: Error handling
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_source_location_works
    intent: "Test SourceLocation functionality."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_logging_replaces_print
    intent: "Test that logging is used instead of print."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_content_analysis_validation
    intent: "Test content analysis validation works."
    v2_component: Parser.analyze() → ContentAnalysis
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fence_handler_basic_functionality
    intent: "Test fence handler basic operations."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fence_indentation_handling
    intent: "Test fence indentation is handled correctly."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_closing_fence_detection
    intent: "Test closing fence detection works."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_text_recovery_basic_functionality
    intent: "Test text recovery basic operations."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_block_context_recovery
    intent: "Test block context recovery."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_processing_performance
    intent: "Test that processing completes in reasonable time."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_smoke_tests_run_quickly
    intent: "Test that smoke tests themselves run quickly."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_pipeline_integration
    intent: "Test full pipeline works end-to-end."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_error_handling_integration
    intent: "Test error handling works across components."
    v2_component: Error handling
    test_type: integration
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_types.py

```yaml
test_file: tests/parser/test_types.py
test_count: 24
legacy_imports:
  - markdown_chunker.parser.types.FencedBlock
  - markdown_chunker.parser.types.MarkdownNode
  - markdown_chunker.parser.types.NodeType
  - markdown_chunker.parser.types.Position
v2_applicable: true
removed_functionality: false

tests:
  - name: test_valid_position
    intent: "Test creating valid position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_line
    intent: "Test invalid line number."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_column
    intent: "Test invalid column number."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_offset
    intent: "Test invalid offset."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_node
    intent: "Test creating a markdown node."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_children
    intent: "Test finding child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_content
    intent: "Test getting text content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_range
    intent: "Test getting line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_leaf
    intent: "Test leaf node detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_fenced_block
    intent: "Test creating a fenced block."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_hash
    intent: "Test getting content hash."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_block
    intent: "Test invalid block detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_position
    intent: "Test creating valid position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_line
    intent: "Test invalid line number."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_column
    intent: "Test invalid column number."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_offset
    intent: "Test invalid offset."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_node
    intent: "Test creating a markdown node."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_children
    intent: "Test finding child nodes."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_content
    intent: "Test getting text content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_range
    intent: "Test getting line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_leaf
    intent: "Test leaf node detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_fenced_block
    intent: "Test creating a fenced block."
    v2_component: ContentAnalysis.code_blocks
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_hash
    intent: "Test getting content hash."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_block
    intent: "Test invalid block detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_utils_module.py

```yaml
test_file: tests/parser/test_utils_module.py
test_count: 10
legacy_imports:
  - markdown_chunker.parser.utils
v2_applicable: true
removed_functionality: false

tests:
  - name: test_to_1_based
    intent: "Test to_1_based conversion."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_0_based
    intent: "Test to_0_based conversion."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that TextRecoveryUtils can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that PhantomBlockPreventer can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_text_recovery_utils
    intent: "Test create_text_recovery_utils function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_1_based
    intent: "Test to_1_based conversion."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_0_based
    intent: "Test to_0_based conversion."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that TextRecoveryUtils can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that PhantomBlockPreventer can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_text_recovery_utils
    intent: "Test create_text_recovery_utils function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_utils_new.py

```yaml
test_file: tests/parser/test_utils_new.py
test_count: 130
legacy_imports:
  - markdown_chunker.parser.utils.LineNumberConverter
  - markdown_chunker.parser.utils.PhantomBlockPreventer
  - markdown_chunker.parser.utils.TextRecoveryUtils
  - markdown_chunker.parser.utils.convert_from_api_lines
  - markdown_chunker.parser.utils.convert_to_api_lines
v2_applicable: true
removed_functionality: false

tests:
  - name: test_to_api_line_number
    intent: "Test converting 0-based to 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_api_line_number_negative
    intent: "Test that negative internal line raises ValueError."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_from_api_line_number
    intent: "Test converting 1-based to 0-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_from_api_line_number_invalid
    intent: "Test that API line < 1 raises ValueError."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_api_line_number_valid
    intent: "Test validating valid API line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_api_line_number_invalid
    intent: "Test validating invalid API line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_valid
    intent: "Test validating valid line ranges."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_invalid_order
    intent: "Test that end < start raises ValueError."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_invalid_values
    intent: "Test that invalid line numbers raise ValueError."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_round_trip_conversion
    intent: "Test that conversion is reversible."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_to_api_lines_function
    intent: "Test convert_to_api_lines convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_from_api_lines_function
    intent: "Test convert_from_api_lines convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_to_api_lines_invalid
    intent: "Test convert_to_api_lines with invalid input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_from_api_lines_invalid
    intent: "Test convert_from_api_lines with invalid input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_zero_to_one
    intent: "Test converting line 0 to line 1."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_numbers
    intent: "Test with large line numbers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_range
    intent: "Test range with same start and end."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test TextRecoveryUtils initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_with_fences
    intent: "Test recovering block text with fences."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_without_fences
    intent: "Test recovering block content only."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_invalid_range
    intent: "Test handling invalid line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context
    intent: "Test getting block with context."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_text_valid
    intent: "Test getting text of a specific line."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_text_invalid
    intent: "Test getting text of invalid line."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range
    intent: "Test getting text range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range_single_line
    intent: "Test getting single line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range_invalid
    intent: "Test getting invalid text range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position
    intent: "Test finding text at specific position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position_invalid_line
    intent: "Test finding text at invalid line."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position_boundary
    intent: "Test finding text at line boundary."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_valid
    intent: "Test validating valid block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_invalid_range
    intent: "Test validating block with invalid range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_out_of_bounds
    intent: "Test validating block exceeding document bounds."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_create_text_recovery_utils
    intent: "Test create_text_recovery_utils convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_source_text
    intent: "Test with empty source text."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_source
    intent: "Test with single line source."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_with_raw_content_fallback
    intent: "Test block with raw_content attribute."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context_at_document_start
    intent: "Test getting context at document start."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context_at_document_end
    intent: "Test getting context at document end."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test with unicode content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_lines
    intent: "Test with very long lines."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_line_endings
    intent: "Test with mixed line endings (already normalized)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_empty
    intent: "Test validating empty block sequence."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_single_block
    intent: "Test validating single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_valid_blocks
    intent: "Test validating valid non-overlapping blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_overlapping
    intent: "Test detecting overlapping blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_proper_nesting
    intent: "Test proper nesting doesn't trigger warnings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_adjacent_suspicious
    intent: "Test detecting suspicious adjacent blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_empty
    intent: "Test filtering empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_single
    intent: "Test filtering single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_valid_blocks
    intent: "Test filtering valid blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_removes_suspicious
    intent: "Test filtering removes suspicious phantom blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_keeps_longer
    intent: "Test filtering keeps longer block when both suspicious."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_proper_nesting
    intent: "Test proper nesting detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_not_proper_nesting
    intent: "Test improper nesting detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_same_fence_short
    intent: "Test phantom detection with same fence type and short content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_different_fence
    intent: "Test phantom detection with different fence types."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_long_content
    intent: "Test phantom detection with long content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_validate_block_sequence
    intent: "Test validate_block_sequence convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_filter_phantom_blocks
    intent: "Test filter_phantom_blocks convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unsorted_blocks
    intent: "Test that blocks are sorted before processing."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_adjacent_blocks
    intent: "Test multiple adjacent suspicious blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_within_nested
    intent: "Test deeply nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_content_blocks
    intent: "Test blocks with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_content
    intent: "Test blocks with whitespace-only content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_api_line_number
    intent: "Test converting 0-based to 1-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_to_api_line_number_negative
    intent: "Test that negative internal line raises ValueError."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_from_api_line_number
    intent: "Test converting 1-based to 0-based."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_from_api_line_number_invalid
    intent: "Test that API line < 1 raises ValueError."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_api_line_number_valid
    intent: "Test validating valid API line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_api_line_number_invalid
    intent: "Test validating invalid API line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_valid
    intent: "Test validating valid line ranges."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_invalid_order
    intent: "Test that end < start raises ValueError."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_line_range_invalid_values
    intent: "Test that invalid line numbers raise ValueError."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_round_trip_conversion
    intent: "Test that conversion is reversible."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_to_api_lines_function
    intent: "Test convert_to_api_lines convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_from_api_lines_function
    intent: "Test convert_from_api_lines convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_to_api_lines_invalid
    intent: "Test convert_to_api_lines with invalid input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convert_from_api_lines_invalid
    intent: "Test convert_from_api_lines with invalid input."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_zero_to_one
    intent: "Test converting line 0 to line 1."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_numbers
    intent: "Test with large line numbers."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_range
    intent: "Test range with same start and end."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test TextRecoveryUtils initialization."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_with_fences
    intent: "Test recovering block text with fences."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_without_fences
    intent: "Test recovering block content only."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_text_invalid_range
    intent: "Test handling invalid line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context
    intent: "Test getting block with context."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_text_valid
    intent: "Test getting text of a specific line."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_line_text_invalid
    intent: "Test getting text of invalid line."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range
    intent: "Test getting text range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range_single_line
    intent: "Test getting single line range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_text_range_invalid
    intent: "Test getting invalid text range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position
    intent: "Test finding text at specific position."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position_invalid_line
    intent: "Test finding text at invalid line."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_text_at_position_boundary
    intent: "Test finding text at line boundary."
    v2_component: ContentAnalysis (positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_valid
    intent: "Test validating valid block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_invalid_range
    intent: "Test validating block with invalid range."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_recovery_out_of_bounds
    intent: "Test validating block exceeding document bounds."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_create_text_recovery_utils
    intent: "Test create_text_recovery_utils convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_source_text
    intent: "Test with empty source text."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_source
    intent: "Test with single line source."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_with_raw_content_fallback
    intent: "Test block with raw_content attribute."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context_at_document_start
    intent: "Test getting context at document start."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_block_context_at_document_end
    intent: "Test getting context at document end."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test with unicode content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_lines
    intent: "Test with very long lines."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_line_endings
    intent: "Test with mixed line endings (already normalized)."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_empty
    intent: "Test validating empty block sequence."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_single_block
    intent: "Test validating single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_valid_blocks
    intent: "Test validating valid non-overlapping blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_overlapping
    intent: "Test detecting overlapping blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_proper_nesting
    intent: "Test proper nesting doesn't trigger warnings."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_block_sequence_adjacent_suspicious
    intent: "Test detecting suspicious adjacent blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_empty
    intent: "Test filtering empty list."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_single
    intent: "Test filtering single block."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_valid_blocks
    intent: "Test filtering valid blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_removes_suspicious
    intent: "Test filtering removes suspicious phantom blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filter_phantom_blocks_keeps_longer
    intent: "Test filtering keeps longer block when both suspicious."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_proper_nesting
    intent: "Test proper nesting detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_is_not_proper_nesting
    intent: "Test improper nesting detection."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_same_fence_short
    intent: "Test phantom detection with same fence type and short content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_different_fence
    intent: "Test phantom detection with different fence types."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_looks_like_phantom_block_long_content
    intent: "Test phantom detection with long content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_validate_block_sequence
    intent: "Test validate_block_sequence convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_convenience_function_filter_phantom_blocks
    intent: "Test filter_phantom_blocks convenience function."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unsorted_blocks
    intent: "Test that blocks are sorted before processing."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_adjacent_blocks
    intent: "Test multiple adjacent suspicious blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_within_nested
    intent: "Test deeply nested blocks."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_content_blocks
    intent: "Test blocks with empty content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_content
    intent: "Test blocks with whitespace-only content."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/parser/test_validation.py

```yaml
test_file: tests/parser/test_validation.py
test_count: 10
legacy_imports:
  - markdown_chunker.parser.validation
v2_applicable: true
removed_functionality: false

tests:
  - name: test_can_instantiate
    intent: "Test that InputValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that APIValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ASTValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_and_normalize_input_exists
    intent: "Test that validate_and_normalize_input function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_stage1_result_exists
    intent: "Test that validate_stage1_result function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_instantiate
    intent: "Test that InputValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that APIValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_can_instantiate
    intent: "Test that ASTValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_and_normalize_input_exists
    intent: "Test that validate_and_normalize_input function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_stage1_result_exists
    intent: "Test that validate_stage1_result function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/parser/test_validation_new.py

```yaml
test_file: tests/parser/test_validation_new.py
test_count: 56
legacy_imports:
  - markdown_chunker.parser.validation.APIValidator
  - markdown_chunker.parser.validation.InputValidator
  - markdown_chunker.parser.validation.Stage1APIValidator
  - markdown_chunker.parser.validation.normalize_line_endings
  - markdown_chunker.parser.validation.validate_and_normalize_input
v2_applicable: false
removed_functionality: true

tests:
  - name: test_validate_and_normalize_string
    intent: "Test validating and normalizing a string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_none
    intent: "Test validating None returns empty string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_invalid_type
    intent: "Test validating invalid type raises TypeError."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_crlf
    intent: "Test normalizing Windows CRLF line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_cr
    intent: "Test normalizing old Mac CR line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_mixed
    intent: "Test normalizing mixed line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_non_empty_true
    intent: "Test validate_non_empty with non-empty text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_non_empty_false
    intent: "Test validate_non_empty with empty text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_line_count
    intent: "Test getting line count."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_encoding_valid
    intent: "Test validating valid UTF-8 encoding."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convenience_function_validate_and_normalize
    intent: "Test convenience function validate_and_normalize_input."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convenience_function_normalize_line_endings
    intent: "Test convenience function normalize_line_endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_instantiation
    intent: "Test that Stage1APIValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_validator_alias
    intent: "Test that APIValidator is an alias."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_process_document_result_basic
    intent: "Test basic validation of Stage1Results."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validator_has_required_methods
    intent: "Test that validator has all required methods."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_empty_string
    intent: "Test with empty string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_whitespace_only
    intent: "Test with whitespace only."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_long_text
    intent: "Test with very long text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_unicode_characters
    intent: "Test with various unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_special_characters
    intent: "Test with special characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_line_ending_types
    intent: "Test text with multiple types of line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_input_function
    intent: "Test validate_and_normalize_input function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_input_with_none
    intent: "Test validate_and_normalize_input with None."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_function
    intent: "Test normalize_line_endings function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_stage1_result_function_exists
    intent: "Test that validate_stage1_result function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_workflow
    intent: "Test complete validation and normalization workflow."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_markdown_document_validation
    intent: "Test validating a markdown document."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_string
    intent: "Test validating and normalizing a string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_none
    intent: "Test validating None returns empty string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_invalid_type
    intent: "Test validating invalid type raises TypeError."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_crlf
    intent: "Test normalizing Windows CRLF line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_cr
    intent: "Test normalizing old Mac CR line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_mixed
    intent: "Test normalizing mixed line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_non_empty_true
    intent: "Test validate_non_empty with non-empty text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_non_empty_false
    intent: "Test validate_non_empty with empty text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_line_count
    intent: "Test getting line count."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_encoding_valid
    intent: "Test validating valid UTF-8 encoding."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convenience_function_validate_and_normalize
    intent: "Test convenience function validate_and_normalize_input."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convenience_function_normalize_line_endings
    intent: "Test convenience function normalize_line_endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_instantiation
    intent: "Test that Stage1APIValidator can be instantiated."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_api_validator_alias
    intent: "Test that APIValidator is an alias."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_process_document_result_basic
    intent: "Test basic validation of Stage1Results."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validator_has_required_methods
    intent: "Test that validator has all required methods."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_empty_string
    intent: "Test with empty string."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_whitespace_only
    intent: "Test with whitespace only."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_long_text
    intent: "Test with very long text."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_unicode_characters
    intent: "Test with various unicode characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_special_characters
    intent: "Test with special characters."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_line_ending_types
    intent: "Test text with multiple types of line endings."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_input_function
    intent: "Test validate_and_normalize_input function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_and_normalize_input_with_none
    intent: "Test validate_and_normalize_input with None."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_normalize_line_endings_function
    intent: "Test normalize_line_endings function."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_stage1_result_function_exists
    intent: "Test that validate_stage1_result function exists."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_workflow
    intent: "Test complete validation and normalization workflow."
    v2_component: Parser
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_markdown_document_validation
    intent: "Test validating a markdown document."
    v2_component: Validator
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

## Chunker Tests

**Files analyzed**: 63
**Total tests**: 1702
**V2 applicable**: 1150
**Removed functionality**: 552

### tests/chunker/test_base_strategy.py

```yaml
test_file: tests/chunker/test_base_strategy.py
test_count: 32
legacy_imports:
  - markdown_chunker.chunker.strategies.base.BaseStrategy
  - markdown_chunker.chunker.strategies.base.StrategyConfigError
  - markdown_chunker.chunker.strategies.base.StrategyContentError
  - markdown_chunker.chunker.strategies.base.StrategyError
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_abstract_methods_required
    intent: "Test that BaseStrategy cannot be instantiated directly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mock_strategy_creation
    intent: "Test creating a mock strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metrics_can_handle
    intent: "Test get_metrics when strategy can handle content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metrics_cannot_handle
    intent: "Test get_metrics when strategy cannot handle content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_final_score_calculation
    intent: "Test final score calculation combining priority and quality."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_chunk_helper
    intent: "Test _create_chunk helper method."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_content
    intent: "Test chunk validation removes empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_oversize_warning
    intent: "Test chunk validation handles oversized atomic chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_splits_non_atomic_oversize
    intent: "Test chunk validation splits non-atomic oversized chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_adds_missing_metadata
    intent: "Test chunk validation adds missing required metadata."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_creation
    intent: "Test creating StrategyError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_with_original
    intent: "Test StrategyError with original exception."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_config_error
    intent: "Test StrategyConfigError inheritance."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_content_error
    intent: "Test StrategyContentError inheritance."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_strategies_comparison
    intent: "Test comparing multiple strategies for selection."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_edge_cases
    intent: "Test strategy selection edge cases."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_abstract_methods_required
    intent: "Test that BaseStrategy cannot be instantiated directly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mock_strategy_creation
    intent: "Test creating a mock strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metrics_can_handle
    intent: "Test get_metrics when strategy can handle content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metrics_cannot_handle
    intent: "Test get_metrics when strategy cannot handle content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_final_score_calculation
    intent: "Test final score calculation combining priority and quality."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_chunk_helper
    intent: "Test _create_chunk helper method."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_content
    intent: "Test chunk validation removes empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_oversize_warning
    intent: "Test chunk validation handles oversized atomic chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_splits_non_atomic_oversize
    intent: "Test chunk validation splits non-atomic oversized chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_adds_missing_metadata
    intent: "Test chunk validation adds missing required metadata."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_creation
    intent: "Test creating StrategyError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_with_original
    intent: "Test StrategyError with original exception."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_config_error
    intent: "Test StrategyConfigError inheritance."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_content_error
    intent: "Test StrategyContentError inheritance."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_strategies_comparison
    intent: "Test comparing multiple strategies for selection."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_edge_cases
    intent: "Test strategy selection edge cases."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_block_packer.py

```yaml
test_file: tests/chunker/test_block_packer.py
test_count: 32
legacy_imports:
  - markdown_chunker.chunker.block_packer.Block
  - markdown_chunker.chunker.block_packer.BlockPacker
  - markdown_chunker.chunker.block_packer.BlockType
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_extract_code_block
    intent: "Test code block extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_table
    intent: "Test table block extraction."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_list
    intent: "Test list block extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_header
    intent: "Test header block extraction."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_paragraphs
    intent: "Test paragraph extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_url_pool
    intent: "Test detection of URL pool (3+ consecutive URLs)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_no_url_pool_for_two_urls
    intent: "Test that 2 URLs don't create a pool."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_url_pool_with_blank_lines
    intent: "Test URL pool detection with blank lines between URLs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_small_blocks
    intent: "Test packing small blocks into single chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_large_blocks_splits
    intent: "Test that large blocks cause splits."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_with_section_header
    intent: "Test packing with section header prepended."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_preserves_block_boundaries
    intent: "Test that blocks are never split (MC-002)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_metadata_preserved
    intent: "Test that block metadata is preserved in chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_not_split
    intent: "Test that lists are extracted as complete blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_not_split
    intent: "Test that tables are extracted as complete blocks."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_block_not_split
    intent: "Test that code blocks are extracted as complete blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_code_block
    intent: "Test code block extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_table
    intent: "Test table block extraction."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_list
    intent: "Test list block extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_header
    intent: "Test header block extraction."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_paragraphs
    intent: "Test paragraph extraction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_url_pool
    intent: "Test detection of URL pool (3+ consecutive URLs)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_no_url_pool_for_two_urls
    intent: "Test that 2 URLs don't create a pool."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_url_pool_with_blank_lines
    intent: "Test URL pool detection with blank lines between URLs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_small_blocks
    intent: "Test packing small blocks into single chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_large_blocks_splits
    intent: "Test that large blocks cause splits."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_pack_with_section_header
    intent: "Test packing with section header prepended."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_preserves_block_boundaries
    intent: "Test that blocks are never split (MC-002)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_metadata_preserved
    intent: "Test that block metadata is preserved in chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_not_split
    intent: "Test that lists are extracted as complete blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_not_split
    intent: "Test that tables are extracted as complete blocks."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_block_not_split
    intent: "Test that code blocks are extracted as complete blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_bug_fixes.py

```yaml
test_file: tests/chunker/test_bug_fixes.py
test_count: 34
legacy_imports:
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.dedup_validator.calculate_duplication_ratio
  - markdown_chunker.chunker.dedup_validator.validate_no_excessive_duplication
  - markdown_chunker.chunker.size_enforcer.split_oversized_chunk
v2_applicable: true
removed_functionality: false

tests:
  - name: test_russian_text_concatenation
    intent: "Test the original Russian text bug from the report."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_join_blocks_preserves_whitespace
    intent: "Test that joining blocks maintains proper whitespace."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_colon_concatenation_fix
    intent: "Test Russian colon concatenation issue."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_at_word_boundary
    intent: "Test that truncation doesn't split words."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_chunk_starts_with_fragment
    intent: "Test that chunks don't start with word fragments."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_word_boundaries
    intent: "Test that overlap doesn't create word fragments."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_internal_duplication_detection
    intent: "Test detection of duplication within a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_excessive_duplication_validation
    intent: "Test that validation catches excessive duplication."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_duplication_beyond_overlap
    intent: "Test that duplication beyond declared overlap is detected."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_non_atomic_oversized_chunk_is_split
    intent: "Test that non-atomic oversized chunks are split."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_atomic_oversized_chunk_allowed
    intent: "Test that atomic elements can exceed size limit."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_chunks_respect_size_limit
    intent: "Test end-to-end that non-atomic chunks respect size limits."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unordered_list_preserved
    intent: "Test that unordered lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_ordered_list_preserved
    intent: "Test that ordered lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_list_preserved
    intent: "Test that task lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_list_structure
    intent: "Test that nested lists are preserved."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_real_world_document
    intent: "Test with a realistic document containing all bug patterns."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_russian_text_concatenation
    intent: "Test the original Russian text bug from the report."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_join_blocks_preserves_whitespace
    intent: "Test that joining blocks maintains proper whitespace."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_colon_concatenation_fix
    intent: "Test Russian colon concatenation issue."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_at_word_boundary
    intent: "Test that truncation doesn't split words."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_chunk_starts_with_fragment
    intent: "Test that chunks don't start with word fragments."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_word_boundaries
    intent: "Test that overlap doesn't create word fragments."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_internal_duplication_detection
    intent: "Test detection of duplication within a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_excessive_duplication_validation
    intent: "Test that validation catches excessive duplication."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_duplication_beyond_overlap
    intent: "Test that duplication beyond declared overlap is detected."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_non_atomic_oversized_chunk_is_split
    intent: "Test that non-atomic oversized chunks are split."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_atomic_oversized_chunk_allowed
    intent: "Test that atomic elements can exceed size limit."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_chunks_respect_size_limit
    intent: "Test end-to-end that non-atomic chunks respect size limits."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unordered_list_preserved
    intent: "Test that unordered lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_ordered_list_preserved
    intent: "Test that ordered lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_list_preserved
    intent: "Test that task lists maintain their structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_list_structure
    intent: "Test that nested lists are preserved."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_real_world_document
    intent: "Test with a realistic document containing all bug patterns."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_chunk_config_validation.py

```yaml
test_file: tests/chunker/test_chunk_config_validation.py
test_count: 26
legacy_imports:
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_default_config_valid
    intent: "Test that default configuration is valid."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_max_chunk_size_auto_adjustment
    intent: "Test auto-adjustment when max_chunk_size is smaller than default min_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_small_max_chunk_size
    intent: "Test auto-adjustment with very small max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tiny_max_chunk_size
    intent: "Test auto-adjustment with tiny max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_min_chunk_size_one
    intent: "Test that min_chunk_size never goes below 1."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_target_chunk_size_adjustment_too_large
    intent: "Test target_chunk_size adjustment when it's larger than max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_target_chunk_size_adjustment_too_small
    intent: "Test target_chunk_size adjustment when it's smaller than min_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_equal_sizes_allowed
    intent: "Test that equal min, target, and max sizes are allowed."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_size_invariants_maintained
    intent: "Test that size invariants are always maintained after adjustment."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_percentage_validation
    intent: "Test that percentage values are validated correctly."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_positive_size_validation
    intent: "Test that size values must be positive."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_integration_test_scenarios
    intent: "Test scenarios that were failing in integration tests."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_factory_methods_still_work
    intent: "Test that factory methods still work after validation changes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_default_config_valid
    intent: "Test that default configuration is valid."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_max_chunk_size_auto_adjustment
    intent: "Test auto-adjustment when max_chunk_size is smaller than default min_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_small_max_chunk_size
    intent: "Test auto-adjustment with very small max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tiny_max_chunk_size
    intent: "Test auto-adjustment with tiny max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_min_chunk_size_one
    intent: "Test that min_chunk_size never goes below 1."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_target_chunk_size_adjustment_too_large
    intent: "Test target_chunk_size adjustment when it's larger than max_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_target_chunk_size_adjustment_too_small
    intent: "Test target_chunk_size adjustment when it's smaller than min_chunk_size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_equal_sizes_allowed
    intent: "Test that equal min, target, and max sizes are allowed."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_size_invariants_maintained
    intent: "Test that size invariants are always maintained after adjustment."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_percentage_validation
    intent: "Test that percentage values are validated correctly."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_positive_size_validation
    intent: "Test that size values must be positive."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_integration_test_scenarios
    intent: "Test scenarios that were failing in integration tests."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_factory_methods_still_work
    intent: "Test that factory methods still work after validation changes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_chunk_simple.py

```yaml
test_file: tests/chunker/test_chunk_simple.py
test_count: 26
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunk_simple_basic
    intent: "Test basic chunk_simple usage."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_returns_dict_chunks
    intent: "Test that chunks are dictionaries."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_config_dict
    intent: "Test chunk_simple with config dictionary."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_strategy
    intent: "Test chunk_simple with strategy parameter (ignored in v2)."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_metadata_structure
    intent: "Test metadata structure in chunk dicts."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_preserves_original_config
    intent: "Test that chunk_simple doesn't permanently change config."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_empty_content
    intent: "Test chunk_simple with empty content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_json_serializable
    intent: "Test that result is JSON serializable."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_code_content
    intent: "Test chunk_simple with code-heavy content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_errors_list
    intent: "Test that errors list is present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_warnings_list
    intent: "Test that warnings list is present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_complete_workflow
    intent: "Test complete workflow with chunk_simple."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_vs_chunk_with_analysis
    intent: "Test that chunk_simple produces same results as chunk_with_analysis."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_basic
    intent: "Test basic chunk_simple usage."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_returns_dict_chunks
    intent: "Test that chunks are dictionaries."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_config_dict
    intent: "Test chunk_simple with config dictionary."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_strategy
    intent: "Test chunk_simple with strategy parameter (ignored in v2)."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_metadata_structure
    intent: "Test metadata structure in chunk dicts."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_preserves_original_config
    intent: "Test that chunk_simple doesn't permanently change config."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_empty_content
    intent: "Test chunk_simple with empty content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_json_serializable
    intent: "Test that result is JSON serializable."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_with_code_content
    intent: "Test chunk_simple with code-heavy content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_errors_list
    intent: "Test that errors list is present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_warnings_list
    intent: "Test that warnings list is present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_complete_workflow
    intent: "Test complete workflow with chunk_simple."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_vs_chunk_with_analysis
    intent: "Test that chunk_simple produces same results as chunk_with_analysis."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_chunker.py

```yaml
test_file: tests/chunker/test_chunker.py
test_count: 32
legacy_imports:
  - markdown_chunker.chunker.core.ChunkingError
  - markdown_chunker.chunker.core.ConfigurationError
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.types.ChunkingResult
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunker_creation_default_config
    intent: "Test creating chunker with default configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_creation_custom_config
    intent: "Test creating chunker with custom configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_available_strategies_loaded
    intent: "Test getting available strategies when they are loaded."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_valid
    intent: "Test config validation with valid configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_invalid
    intent: "Test config validation with invalid configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_stage1_success
    intent: "Test chunk_with_analysis with successful Stage 1 processing."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunk_with_analysis_stage1_failure
    intent: "Test chunk_with_analysis with Stage 1 processing failure."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunk_method_delegates_to_chunk_with_analysis
    intent: "Test that chunk() method delegates to chunk_with_analysis()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_strategy_override
    intent: "Test chunking with strategy override parameter."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_initialization_components
    intent: "Test that chunker initializes all required components."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_creation
    intent: "Test creating ChunkingError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration_error_inheritance
    intent: "Test ConfigurationError inheritance."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_error_inheritance
    intent: "Test StrategySelectionError inheritance."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_with_empty_input
    intent: "Test chunker behavior with empty input."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_with_various_configs
    intent: "Test chunker with different configuration presets."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_performance_timing
    intent: "Test that chunker properly measures processing time."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_creation_default_config
    intent: "Test creating chunker with default configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_creation_custom_config
    intent: "Test creating chunker with custom configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_available_strategies_loaded
    intent: "Test getting available strategies when they are loaded."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_valid
    intent: "Test config validation with valid configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_invalid
    intent: "Test config validation with invalid configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_stage1_success
    intent: "Test chunk_with_analysis with successful Stage 1 processing."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunk_with_analysis_stage1_failure
    intent: "Test chunk_with_analysis with Stage 1 processing failure."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunk_method_delegates_to_chunk_with_analysis
    intent: "Test that chunk() method delegates to chunk_with_analysis()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_strategy_override
    intent: "Test chunking with strategy override parameter."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_initialization_components
    intent: "Test that chunker initializes all required components."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_creation
    intent: "Test creating ChunkingError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_configuration_error_inheritance
    intent: "Test ConfigurationError inheritance."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_error_inheritance
    intent: "Test StrategySelectionError inheritance."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_with_empty_input
    intent: "Test chunker behavior with empty input."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_with_various_configs
    intent: "Test chunker with different configuration presets."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_performance_timing
    intent: "Test that chunker properly measures processing time."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_code_strategy_properties.py

```yaml
test_file: tests/chunker/test_code_strategy_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_code_blocks_never_split
    intent: "**Property 10a: Code Blocks Never Split**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, each code block should appear
in exactly one chunk (never split across chunks)."
  - name: test_property_code_blocks_have_metadata
    intent: "**Property 10b: Code Blocks Have Metadata**"
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks processed by code strategy,
chunks containing code should have appropriate metadata."
  - name: test_property_code_blocks_preserve_fences
    intent: "**Property 10c: Code Blocks Preserve Fences**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, the fences (```) should be
preserved in the chunks."
  - name: test_property_multiple_code_blocks_handled
    intent: "**Property 10d: Multiple Code Blocks Handled**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with multiple code blocks, all blocks should be
preserved and properly chunked."
  - name: test_property_large_code_blocks_allowed_oversize
    intent: "**Property 10e: Large Code Blocks Allowed Oversize**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with large code blocks, blocks larger than
max_chunk_size should be allowed (marked as oversize)."
  - name: test_property_code_block_content_preserved
    intent: "**Property 10f: Code Block Content Preserved**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, the content inside code blocks
should be preserved (allowing for whitespace normalization)."
  - name: test_property_code_blocks_never_split
    intent: "**Property 10a: Code Blocks Never Split**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, each code block should appear
in exactly one chunk (never split across chunks)."
  - name: test_property_code_blocks_have_metadata
    intent: "**Property 10b: Code Blocks Have Metadata**"
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks processed by code strategy,
chunks containing code should have appropriate metadata."
  - name: test_property_code_blocks_preserve_fences
    intent: "**Property 10c: Code Blocks Preserve Fences**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, the fences (```) should be
preserved in the chunks."
  - name: test_property_multiple_code_blocks_handled
    intent: "**Property 10d: Multiple Code Blocks Handled**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with multiple code blocks, all blocks should be
preserved and properly chunked."
  - name: test_property_large_code_blocks_allowed_oversize
    intent: "**Property 10e: Large Code Blocks Allowed Oversize**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with large code blocks, blocks larger than
max_chunk_size should be allowed (marked as oversize)."
  - name: test_property_code_block_content_preserved
    intent: "**Property 10f: Code Block Content Preserved**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown with code blocks, the content inside code blocks
should be preserved (allowing for whitespace normalization)."
```

### tests/chunker/test_components/test_fallback_manager.py

```yaml
test_file: tests/chunker/test_components/test_fallback_manager.py
test_count: 36
legacy_imports:
  - markdown_chunker.chunker.components.fallback_manager.FallbackError
  - markdown_chunker.chunker.components.fallback_manager.FallbackLevel
  - markdown_chunker.chunker.components.fallback_manager.FallbackManager
  - markdown_chunker.chunker.components.fallback_manager.create_fallback_manager
  - markdown_chunker.chunker.components.fallback_manager.validate_fallback_chain
v2_applicable: false
removed_functionality: true

tests:
  - name: test_manager_creation
    intent: "Test creating fallback manager."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_success
    intent: "Test successful execution with primary strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_failure_fallback_to_structural
    intent: "Test fallback to structural strategy when primary fails."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_returns_empty_fallback
    intent: "Test fallback when primary strategy returns empty chunks."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_sentences_strategy_is_primary_uses_structural
    intent: "Test that when sentences is primary and fails, structural is tried."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_all_strategies_fail_returns_empty
    intent: "Test that when all strategies fail, empty result is returned."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_fallback_chain_valid
    intent: "Test validation of valid fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_fallback_chain_disabled
    intent: "Test validation when fallback is disabled."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_fallback_statistics
    intent: "Test getting fallback statistics."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_added
    intent: "Test that fallback metadata is added to chunks."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_level_enum_values
    intent: "Test that FallbackLevel enum has correct values."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_returns_empty_triggers_fallback
    intent: "Test that primary returning empty chunks triggers fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_fallback_manager
    intent: "Test creating fallback manager with utility function."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_test_fallback_chain
    intent: "Test the fallback chain testing utility."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_error_creation
    intent: "Test creating FallbackError with error list."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_fallback_scenario
    intent: "Test realistic scenario with actual strategies."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_complete_failure_scenario
    intent: "Test scenario where all strategies fail."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_preserves_errors_and_warnings
    intent: "Test that fallback preserves all errors and warnings."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_manager_creation
    intent: "Test creating fallback manager."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_success
    intent: "Test successful execution with primary strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_failure_fallback_to_structural
    intent: "Test fallback to structural strategy when primary fails."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_strategy_returns_empty_fallback
    intent: "Test fallback when primary strategy returns empty chunks."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_sentences_strategy_is_primary_uses_structural
    intent: "Test that when sentences is primary and fails, structural is tried."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_all_strategies_fail_returns_empty
    intent: "Test that when all strategies fail, empty result is returned."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_fallback_chain_valid
    intent: "Test validation of valid fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_validate_fallback_chain_disabled
    intent: "Test validation when fallback is disabled."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_fallback_statistics
    intent: "Test getting fallback statistics."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_added
    intent: "Test that fallback metadata is added to chunks."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_level_enum_values
    intent: "Test that FallbackLevel enum has correct values."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_primary_returns_empty_triggers_fallback
    intent: "Test that primary returning empty chunks triggers fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_fallback_manager
    intent: "Test creating fallback manager with utility function."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_test_fallback_chain
    intent: "Test the fallback chain testing utility."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_error_creation
    intent: "Test creating FallbackError with error list."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_fallback_scenario
    intent: "Test realistic scenario with actual strategies."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_complete_failure_scenario
    intent: "Test scenario where all strategies fail."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_preserves_errors_and_warnings
    intent: "Test that fallback preserves all errors and warnings."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_components/test_metadata_enricher.py

```yaml
test_file: tests/chunker/test_components/test_metadata_enricher.py
test_count: 36
legacy_imports:
  - markdown_chunker.chunker.components.metadata_enricher.MetadataEnricher
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_initialization
    intent: "Test MetadataEnricher initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_chunks_empty
    intent: "Test enriching empty chunk list."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_single_chunk
    intent: "Test enriching a single chunk."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_multiple_chunks
    intent: "Test enriching multiple chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_with_document_id
    intent: "Test enriching with document ID."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_content_statistics
    intent: "Test content statistics calculation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_code_metadata
    intent: "Test code metadata enrichment."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_list_metadata
    intent: "Test list metadata enrichment."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_table_metadata
    intent: "Test table metadata enrichment."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_structural_metadata
    intent: "Test structural metadata enrichment."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_searchability_metadata
    intent: "Test searchability metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_metadata_valid
    intent: "Test metadata validation with valid chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_metadata_missing_fields
    intent: "Test metadata validation with missing fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metadata_summary
    intent: "Test metadata summary generation."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metadata_summary_empty
    intent: "Test metadata summary with empty list."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_original_metadata
    intent: "Test that enrichment preserves original metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_document_enrichment
    intent: "Test enrichment with realistic document chunks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrichment_with_all_content_types
    intent: "Test enrichment with all content types."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test MetadataEnricher initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_chunks_empty
    intent: "Test enriching empty chunk list."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_single_chunk
    intent: "Test enriching a single chunk."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_multiple_chunks
    intent: "Test enriching multiple chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_with_document_id
    intent: "Test enriching with document ID."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_content_statistics
    intent: "Test content statistics calculation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_code_metadata
    intent: "Test code metadata enrichment."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_list_metadata
    intent: "Test list metadata enrichment."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_table_metadata
    intent: "Test table metadata enrichment."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrich_structural_metadata
    intent: "Test structural metadata enrichment."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_searchability_metadata
    intent: "Test searchability metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_metadata_valid
    intent: "Test metadata validation with valid chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_metadata_missing_fields
    intent: "Test metadata validation with missing fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metadata_summary
    intent: "Test metadata summary generation."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_metadata_summary_empty
    intent: "Test metadata summary with empty list."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_original_metadata
    intent: "Test that enrichment preserves original metadata."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_document_enrichment
    intent: "Test enrichment with realistic document chunks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enrichment_with_all_content_types
    intent: "Test enrichment with all content types."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_components/test_overlap_manager.py

```yaml
test_file: tests/chunker/test_components/test_overlap_manager.py
test_count: 42
legacy_imports:
  - markdown_chunker.chunker.components.overlap_manager.OverlapManager
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_initialization
    intent: "Test OverlapManager initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_disabled
    intent: "Test that overlap is not applied when disabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_single_chunk
    intent: "Test that single chunk is unchanged."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_empty_list
    intent: "Test that empty list is handled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_two_chunks
    intent: "Test overlap between two chunks in legacy mode (default)."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_multiple_chunks
    intent: "Test overlap across multiple chunks in legacy mode."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_suffix_context_simple
    intent: "Test extracting suffix context from a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_prefix_context_simple
    intent: "Test extracting prefix context from a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_extraction
    intent: "Test extracting blocks from content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_extraction_single_block
    intent: "Test extracting blocks from single-block content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_percentage
    intent: "Test overlap using percentage (when overlap_size is 0)."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_fixed_size
    intent: "Test overlap using fixed size."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_metadata
    intent: "Test that overlap preserves original chunk metadata."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_short_chunks
    intent: "Test overlap with very short chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_no_overlap
    intent: "Test statistics when no overlap is applied."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_with_overlap
    intent: "Test statistics when overlap is applied in metadata mode."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_empty
    intent: "Test statistics with empty chunk list."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_multiline_content
    intent: "Test overlap with multiline content in legacy mode."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_boundary_preservation
    intent: "Test that overlap preserves block boundaries."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_document_chunking_with_overlap
    intent: "Test overlap with realistic document chunks in legacy mode."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_code_chunks
    intent: "Test overlap with code chunks - overlap should be skipped if it would create unbalanced fences."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_initialization
    intent: "Test OverlapManager initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_disabled
    intent: "Test that overlap is not applied when disabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_single_chunk
    intent: "Test that single chunk is unchanged."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_empty_list
    intent: "Test that empty list is handled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_two_chunks
    intent: "Test overlap between two chunks in legacy mode (default)."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_apply_overlap_multiple_chunks
    intent: "Test overlap across multiple chunks in legacy mode."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_suffix_context_simple
    intent: "Test extracting suffix context from a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_extract_prefix_context_simple
    intent: "Test extracting prefix context from a chunk."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_extraction
    intent: "Test extracting blocks from content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_extraction_single_block
    intent: "Test extracting blocks from single-block content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_percentage
    intent: "Test overlap using percentage (when overlap_size is 0)."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_fixed_size
    intent: "Test overlap using fixed size."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_metadata
    intent: "Test that overlap preserves original chunk metadata."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_short_chunks
    intent: "Test overlap with very short chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_no_overlap
    intent: "Test statistics when no overlap is applied."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_with_overlap
    intent: "Test statistics when overlap is applied in metadata mode."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_calculate_overlap_statistics_empty
    intent: "Test statistics with empty chunk list."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_multiline_content
    intent: "Test overlap with multiline content in legacy mode."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_boundary_preservation
    intent: "Test that overlap preserves block boundaries."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_document_chunking_with_overlap
    intent: "Test overlap with realistic document chunks in legacy mode."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_code_chunks
    intent: "Test overlap with code chunks - overlap should be skipped if it would create unbalanced fences."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_components/test_overlap_metadata_mode.py

```yaml
test_file: tests/chunker/test_components/test_overlap_metadata_mode.py
test_count: 16
legacy_imports:
  - markdown_chunker.chunker.components.OverlapManager
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_overlap_metadata_mode_enabled
    intent: "Test overlap stored in metadata instead of content."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_legacy_mode_disabled
    intent: "Test legacy mode where overlap is merged into content."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_mode_single_chunk
    intent: "Test single chunk document - no context keys should be present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_mode_with_code_fences
    intent: "Test overlap extraction with unbalanced code fences."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_field_presence
    intent: "Test that context fields are only present when context exists."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_no_keys
    intent: "Test that context keys are not added when overlap is disabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_preservation_both_modes
    intent: "Test that content is preserved correctly in both modes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_backward_compatibility_default_false
    intent: "Test that default parameter (False) maintains backward compatibility."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_mode_enabled
    intent: "Test overlap stored in metadata instead of content."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_legacy_mode_disabled
    intent: "Test legacy mode where overlap is merged into content."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_mode_single_chunk
    intent: "Test single chunk document - no context keys should be present."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_mode_with_code_fences
    intent: "Test overlap extraction with unbalanced code fences."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_metadata_field_presence
    intent: "Test that context fields are only present when context exists."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_no_keys
    intent: "Test that context keys are not added when overlap is disabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_preservation_both_modes
    intent: "Test that content is preserved correctly in both modes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_backward_compatibility_default_false
    intent: "Test that default parameter (False) maintains backward compatibility."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_components/test_overlap_new_model.py

```yaml
test_file: tests/chunker/test_components/test_overlap_new_model.py
test_count: 24
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_no_old_overlap_fields
    intent: "Verify removal of deprecated overlap fields."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_size_limits
    intent: "Validate context length constraints."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_boundary_chunks
    intent: "Validate first and last chunks have no context fields on boundaries."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_mode_no_content_merge
    intent: "Ensure contexts are in metadata, not merged into content."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled
    intent: "Test no-op when overlap disabled (overlap_size=0)."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_chunk_no_context
    intent: "Test single chunk document has no context fields."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_is_substring_of_neighbor
    intent: "Verify context originates from correct neighbor."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_size_in_metadata
    intent: "Verify overlap_size is recorded in metadata when overlap is applied."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_code_blocks
    intent: "Test overlap works correctly with code blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_chunk_order
    intent: "Test that overlap doesn't affect chunk ordering."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_large_document
    intent: "Test overlap with a larger document."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enable_overlap_property
    intent: "Test that enable_overlap property works correctly."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_no_old_overlap_fields
    intent: "Verify removal of deprecated overlap fields."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_size_limits
    intent: "Validate context length constraints."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_boundary_chunks
    intent: "Validate first and last chunks have no context fields on boundaries."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_mode_no_content_merge
    intent: "Ensure contexts are in metadata, not merged into content."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled
    intent: "Test no-op when overlap disabled (overlap_size=0)."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_chunk_no_context
    intent: "Test single chunk document has no context fields."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_is_substring_of_neighbor
    intent: "Verify context originates from correct neighbor."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_size_in_metadata
    intent: "Verify overlap_size is recorded in metadata when overlap is applied."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_code_blocks
    intent: "Test overlap works correctly with code blocks."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_preserves_chunk_order
    intent: "Test that overlap doesn't affect chunk ordering."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_with_large_document
    intent: "Test overlap with a larger document."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enable_overlap_property
    intent: "Test that enable_overlap property works correctly."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_comprehensive_integration.py

```yaml
test_file: tests/chunker/test_comprehensive_integration.py
test_count: 14
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_mixed_content_document_complete_pipeline
    intent: "Test complete pipeline with mixed content document."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_automatic_strategy_selection_with_fixes
    intent: "Test automatic strategy selection works with all fixes applied."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_benchmarks_integration
    intent: "Test performance benchmarks with complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_ast_content_preservation_integration
    intent: "Test AST content preservation works in complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fence_handling_integration
    intent: "Test nested fence handling works in complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_strategy_stage1_integration
    intent: "Test MixedStrategy Stage 1 integration works in complete pipeline."
    v2_component: REMOVED: MixedStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_preservation_integration
    intent: "Test fallback metadata preservation works in complete pipeline."
    v2_component: FallbackStrategy
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_document_complete_pipeline
    intent: "Test complete pipeline with mixed content document."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_automatic_strategy_selection_with_fixes
    intent: "Test automatic strategy selection works with all fixes applied."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_benchmarks_integration
    intent: "Test performance benchmarks with complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_ast_content_preservation_integration
    intent: "Test AST content preservation works in complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fence_handling_integration
    intent: "Test nested fence handling works in complete pipeline."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_strategy_stage1_integration
    intent: "Test MixedStrategy Stage 1 integration works in complete pipeline."
    v2_component: REMOVED: MixedStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_preservation_integration
    intent: "Test fallback metadata preservation works in complete pipeline."
    v2_component: FallbackStrategy
    test_type: integration
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_config_profiles.py

```yaml
test_file: tests/chunker/test_config_profiles.py
test_count: 10
legacy_imports:
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_for_api_default
    intent: "Test API default profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_for_dify_rag
    intent: "Test Dify RAG profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_for_fast_processing
    intent: "Test fast processing profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_profiles_valid
    intent: "Test all profiles are created successfully."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_profiles_have_different_settings
    intent: "Test profiles have distinct settings."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_for_api_default
    intent: "Test API default profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_for_dify_rag
    intent: "Test Dify RAG profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_for_fast_processing
    intent: "Test fast processing profile."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_profiles_valid
    intent: "Test all profiles are created successfully."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_profiles_have_different_settings
    intent: "Test profiles have distinct settings."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_critical_properties.py

```yaml
test_file: tests/chunker/test_critical_properties.py
test_count: 30
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_data_preservation
    intent: "**Property 1: Data Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown document, every user-visible non-whitespace
token from the input must appear in at least one output chunk."
  - name: test_property_chunk_ordering
    intent: "**Property 2: Chunk Ordering**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunked document, chunks must have monotonically non-decreasing
start_line values."
  - name: test_property_ordering_all_strategies
    intent: "Verify ordering holds for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all strategies."
  - name: test_property_idempotence
    intent: "**Property 3: Idempotence**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown document, chunking the same input twice must produce
identical results."
  - name: test_property_metadata_toggle_equivalence
    intent: "**Property 4: Metadata Toggle Equivalence**"
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_empty_output
    intent: "**Property 5: No Empty Output**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown document, the chunker must produce at least
one non-empty chunk."
  - name: test_property_fallback_code_strategy
    intent: "**Property 6: Fallback Chain Correctness**"
    v2_component: CodeAwareStrategy
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_word_splitting
    intent: "**Property 7: No Word Splitting**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk boundary, the boundary must not occur in the middle of
a word."
  - name: test_property_atomic_code_blocks
    intent: "**Property 8: Atomic Elements Preserved**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_overlap_exactness
    intent: "**Property 9: Overlap Exactness**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_overlap_size_limits
    intent: "**Property 10: Overlap Size Limits**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_size_compliance
    intent: "**Property 11: Size Compliance**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_auto_not_list_for_text
    intent: "**Property 12: Auto Strategy Appropriateness**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_clean_chunk_text
    intent: "**Property 13: Clean Chunk Text**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_list_chunk_quality
    intent: "**Property 14: List Chunk Quality**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_data_preservation
    intent: "**Property 1: Data Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown document, every user-visible non-whitespace
token from the input must appear in at least one output chunk."
  - name: test_property_chunk_ordering
    intent: "**Property 2: Chunk Ordering**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunked document, chunks must have monotonically non-decreasing
start_line values."
  - name: test_property_ordering_all_strategies
    intent: "Verify ordering holds for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all strategies."
  - name: test_property_idempotence
    intent: "**Property 3: Idempotence**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown document, chunking the same input twice must produce
identical results."
  - name: test_property_metadata_toggle_equivalence
    intent: "**Property 4: Metadata Toggle Equivalence**"
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_empty_output
    intent: "**Property 5: No Empty Output**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown document, the chunker must produce at least
one non-empty chunk."
  - name: test_property_fallback_code_strategy
    intent: "**Property 6: Fallback Chain Correctness**"
    v2_component: CodeAwareStrategy
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_word_splitting
    intent: "**Property 7: No Word Splitting**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk boundary, the boundary must not occur in the middle of
a word."
  - name: test_property_atomic_code_blocks
    intent: "**Property 8: Atomic Elements Preserved**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_overlap_exactness
    intent: "**Property 9: Overlap Exactness**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_overlap_size_limits
    intent: "**Property 10: Overlap Size Limits**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_size_compliance
    intent: "**Property 11: Size Compliance**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_auto_not_list_for_text
    intent: "**Property 12: Auto Strategy Appropriateness**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_clean_chunk_text
    intent: "**Property 13: Clean Chunk Text**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_list_chunk_quality
    intent: "**Property 14: List Chunk Quality**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_data_completeness_validator.py

```yaml
test_file: tests/chunker/test_data_completeness_validator.py
test_count: 54
legacy_imports:
  - markdown_chunker.chunker.errors.DataLossError
  - markdown_chunker.chunker.errors.MissingContentError
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.validator.DataCompletenessValidator
  - markdown_chunker.chunker.validator.MissingContentBlock
v2_applicable: true
removed_functionality: false

tests:
  - name: test_validation_result_creation
    intent: "Test creating a validation result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_summary_valid
    intent: "Test summary for valid result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_summary_invalid
    intent: "Test summary for invalid result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_missing_content_block_creation
    intent: "Test creating a missing content block."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_initialization
    intent: "Test validator initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_default_tolerance
    intent: "Test validator with default tolerance."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_perfect_match
    intent: "Test validation with perfect character match."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_within_tolerance
    intent: "Test validation with difference within tolerance."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_exceeds_tolerance
    intent: "Test validation with difference exceeding tolerance."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_input
    intent: "Test validation with empty input."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_output
    intent: "Test validation with empty output."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_multiple_chunks
    intent: "Test validation with multiple chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_missing_content
    intent: "Test finding missing content blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_complete
    intent: "Test line coverage check with complete coverage."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_with_gaps
    intent: "Test line coverage check with gaps."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_no_line_info
    intent: "Test line coverage when chunks have no line info."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_code
    intent: "Test guessing block type for code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_list
    intent: "Test guessing block type for list."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_table
    intent: "Test guessing block type for table."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_header
    intent: "Test guessing block type for header."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_paragraph
    intent: "Test guessing block type for paragraph."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_passes
    intent: "Test raise_if_invalid when validation passes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_data_loss
    intent: "Test raise_if_invalid raises on data loss."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_missing_content
    intent: "Test raise_if_invalid raises MissingContentError."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_with_warnings
    intent: "Test validation generates warnings."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_with_real_chunking_scenario
    intent: "Test validator with realistic chunking scenario."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_detects_missing_section
    intent: "Test validator detects when a section is missing."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_creation
    intent: "Test creating a validation result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_summary_valid
    intent: "Test summary for valid result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_result_summary_invalid
    intent: "Test summary for invalid result."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_missing_content_block_creation
    intent: "Test creating a missing content block."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_initialization
    intent: "Test validator initialization."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_default_tolerance
    intent: "Test validator with default tolerance."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_perfect_match
    intent: "Test validation with perfect character match."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_within_tolerance
    intent: "Test validation with difference within tolerance."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_exceeds_tolerance
    intent: "Test validation with difference exceeding tolerance."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_input
    intent: "Test validation with empty input."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_empty_output
    intent: "Test validation with empty output."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunks_multiple_chunks
    intent: "Test validation with multiple chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_find_missing_content
    intent: "Test finding missing content blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_complete
    intent: "Test line coverage check with complete coverage."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_with_gaps
    intent: "Test line coverage check with gaps."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_check_line_coverage_no_line_info
    intent: "Test line coverage when chunks have no line info."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_code
    intent: "Test guessing block type for code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_list
    intent: "Test guessing block type for list."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_table
    intent: "Test guessing block type for table."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_header
    intent: "Test guessing block type for header."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_guess_block_type_paragraph
    intent: "Test guessing block type for paragraph."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_passes
    intent: "Test raise_if_invalid when validation passes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_data_loss
    intent: "Test raise_if_invalid raises on data loss."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_raise_if_invalid_missing_content
    intent: "Test raise_if_invalid raises MissingContentError."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_with_warnings
    intent: "Test validation generates warnings."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_with_real_chunking_scenario
    intent: "Test validator with realistic chunking scenario."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validator_detects_missing_section
    intent: "Test validator detects when a section is missing."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_data_preservation_properties.py

```yaml
test_file: tests/chunker/test_data_preservation_properties.py
test_count: 18
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_data_preservation
    intent: "**Property 1: Data Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_plain_text_preservation
    intent: "Property: Plain text should be fully preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text (no markdown), all content should appear in output."
  - name: test_property_list_content_preservation
    intent: "Property: List content should be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of items, all items should appear in output."
  - name: test_property_code_block_preservation
    intent: "Property: Code blocks should be preserved intact."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, it should appear in output without modification."
  - name: test_property_preservation_across_strategies
    intent: "Property: Data preservation should work for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown and any strategy, data should be preserved."
  - name: test_property_preservation_with_different_chunk_sizes
    intent: "Property: Data preservation should work with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, data should be preserved."
  - name: test_property_whitespace_only_input
    intent: "Property: Whitespace-only input should produce empty output."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any whitespace-only input, output should be empty or minimal."
  - name: test_property_single_line_preservation
    intent: "Property: Single line should be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line of text, it should appear in output."
  - name: test_property_multiple_paragraphs_preservation
    intent: "Property: Multiple paragraphs should all be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, all should appear in output."
  - name: test_property_data_preservation
    intent: "**Property 1: Data Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_plain_text_preservation
    intent: "Property: Plain text should be fully preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text (no markdown), all content should appear in output."
  - name: test_property_list_content_preservation
    intent: "Property: List content should be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of items, all items should appear in output."
  - name: test_property_code_block_preservation
    intent: "Property: Code blocks should be preserved intact."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, it should appear in output without modification."
  - name: test_property_preservation_across_strategies
    intent: "Property: Data preservation should work for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown and any strategy, data should be preserved."
  - name: test_property_preservation_with_different_chunk_sizes
    intent: "Property: Data preservation should work with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, data should be preserved."
  - name: test_property_whitespace_only_input
    intent: "Property: Whitespace-only input should produce empty output."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any whitespace-only input, output should be empty or minimal."
  - name: test_property_single_line_preservation
    intent: "Property: Single line should be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line of text, it should appear in output."
  - name: test_property_multiple_paragraphs_preservation
    intent: "Property: Multiple paragraphs should all be preserved."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, all should appear in output."
```

### tests/chunker/test_dynamic_strategy_management.py

```yaml
test_file: tests/chunker/test_dynamic_strategy_management.py
test_count: 22
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.strategies.base.BaseStrategy
  - markdown_chunker.chunker.types.Chunk
v2_applicable: false
removed_functionality: true

tests:
  - name: test_add_strategy_recreates_selector
    intent: "Test that add_strategy recreates the strategy selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_selection_works_after_addition
    intent: "Test that strategy selection works after adding a strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_remove_strategy_works
    intent: "Test that remove_strategy removes the strategy and recreates selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_remove_nonexistent_strategy_safe
    intent: "Test that removing non-existent strategy doesn't break anything."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_mode_preserved_on_add
    intent: "Test that selector mode is preserved when adding strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_mode_preserved_on_remove
    intent: "Test that selector mode is preserved when removing strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_strategy_operations
    intent: "Test multiple add/remove operations in sequence."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_add_duplicate_strategy_name
    intent: "Test adding strategy with duplicate name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_not_none_after_operations
    intent: "Test that selector is never None after any operation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunking_works_after_all_operations
    intent: "Test that chunking continues to work after all operations."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_available_strategies_updated
    intent: "Test that get_available_strategies reflects changes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_add_strategy_recreates_selector
    intent: "Test that add_strategy recreates the strategy selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_selection_works_after_addition
    intent: "Test that strategy selection works after adding a strategy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_remove_strategy_works
    intent: "Test that remove_strategy removes the strategy and recreates selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_remove_nonexistent_strategy_safe
    intent: "Test that removing non-existent strategy doesn't break anything."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_mode_preserved_on_add
    intent: "Test that selector mode is preserved when adding strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_mode_preserved_on_remove
    intent: "Test that selector mode is preserved when removing strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_strategy_operations
    intent: "Test multiple add/remove operations in sequence."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_add_duplicate_strategy_name
    intent: "Test adding strategy with duplicate name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_selector_not_none_after_operations
    intent: "Test that selector is never None after any operation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_chunking_works_after_all_operations
    intent: "Test that chunking continues to work after all operations."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_available_strategies_updated
    intent: "Test that get_available_strategies reflects changes."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_error_types.py

```yaml
test_file: tests/chunker/test_error_types.py
test_count: 62
legacy_imports:
  - markdown_chunker.chunker.errors.ChunkingError
  - markdown_chunker.chunker.errors.DataLossError
  - markdown_chunker.chunker.errors.EmptyInputError
  - markdown_chunker.chunker.errors.IncompleteCoverageError
  - markdown_chunker.chunker.errors.InputValidationError
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunking_error_creation
    intent: "Test creating a chunking error."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_with_context
    intent: "Test chunking error with context."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_inheritance
    intent: "Test that ChunkingError inherits from Exception."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_input_validation_error
    intent: "Test InputValidationError."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error
    intent: "Test EmptyInputError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error_custom_message
    intent: "Test EmptyInputError with custom message."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_encoding_error
    intent: "Test InvalidEncodingError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error
    intent: "Test StrategyError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_with_preview
    intent: "Test StrategyError with content preview."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_not_found_error
    intent: "Test StrategyNotFoundError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_failed_error
    intent: "Test StrategyFailedError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_failed_error_with_preview
    intent: "Test StrategyFailedError with content preview."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_strategy_can_handle_error
    intent: "Test NoStrategyCanHandleError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error
    intent: "Test DataLossError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error_with_percentage
    intent: "Test DataLossError with input chars for percentage."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error_with_blocks
    intent: "Test DataLossError with missing blocks."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_missing_content_error
    intent: "Test MissingContentError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_incomplete_coverage_error
    intent: "Test IncompleteCoverageError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error
    intent: "Test ValidationError."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_chunk_error
    intent: "Test InvalidChunkError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_metadata_error
    intent: "Test InvalidMetadataError."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_metadata_error_no_fields
    intent: "Test InvalidMetadataError without specific fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_errors_inherit_from_chunking_error
    intent: "Test that all custom errors inherit from ChunkingError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_input_validation_hierarchy
    intent: "Test InputValidationError hierarchy."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_hierarchy
    intent: "Test StrategyError hierarchy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_hierarchy
    intent: "Test DataLossError hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error_hierarchy
    intent: "Test ValidationError hierarchy."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_catching_specific_error
    intent: "Test catching specific error type."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_catching_base_error
    intent: "Test catching base ChunkingError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_context_preservation
    intent: "Test that error context is preserved."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_error_handling
    intent: "Test handling nested errors."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_creation
    intent: "Test creating a chunking error."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_with_context
    intent: "Test chunking error with context."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_error_inheritance
    intent: "Test that ChunkingError inherits from Exception."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_input_validation_error
    intent: "Test InputValidationError."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error
    intent: "Test EmptyInputError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error_custom_message
    intent: "Test EmptyInputError with custom message."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_encoding_error
    intent: "Test InvalidEncodingError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error
    intent: "Test StrategyError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_with_preview
    intent: "Test StrategyError with content preview."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_not_found_error
    intent: "Test StrategyNotFoundError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_failed_error
    intent: "Test StrategyFailedError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_failed_error_with_preview
    intent: "Test StrategyFailedError with content preview."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_strategy_can_handle_error
    intent: "Test NoStrategyCanHandleError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error
    intent: "Test DataLossError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error_with_percentage
    intent: "Test DataLossError with input chars for percentage."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_error_with_blocks
    intent: "Test DataLossError with missing blocks."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_missing_content_error
    intent: "Test MissingContentError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_incomplete_coverage_error
    intent: "Test IncompleteCoverageError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error
    intent: "Test ValidationError."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_chunk_error
    intent: "Test InvalidChunkError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_metadata_error
    intent: "Test InvalidMetadataError."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_metadata_error_no_fields
    intent: "Test InvalidMetadataError without specific fields."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_errors_inherit_from_chunking_error
    intent: "Test that all custom errors inherit from ChunkingError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_input_validation_hierarchy
    intent: "Test InputValidationError hierarchy."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_error_hierarchy
    intent: "Test StrategyError hierarchy."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_data_loss_hierarchy
    intent: "Test DataLossError hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error_hierarchy
    intent: "Test ValidationError hierarchy."
    v2_component: Validator
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_catching_specific_error
    intent: "Test catching specific error type."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_catching_base_error
    intent: "Test catching base ChunkingError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_context_preservation
    intent: "Test that error context is preserved."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_error_handling
    intent: "Test handling nested errors."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_fallback_manager_integration.py

```yaml
test_file: tests/chunker/test_fallback_manager_integration.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkingResult
v2_applicable: true
removed_functionality: false

tests:
  - name: test_execute_with_fallback_called_correctly
    intent: "Test that execute_with_fallback is called with correct parameters."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_unpacking_works
    intent: "Test that ChunkingResult is unpacked correctly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_info_structure
    intent: "Test that fallback_info is structured correctly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_bypasses_fallback_manager
    intent: "Test that manual strategy selection doesn't use fallback manager."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_chunking_on_exception
    intent: "Test that emergency chunking is used when fallback manager fails."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_apply_with_fallback_method_called
    intent: "Test that the old apply_with_fallback method is not called."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_execute_with_fallback_called_correctly
    intent: "Test that execute_with_fallback is called with correct parameters."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_unpacking_works
    intent: "Test that ChunkingResult is unpacked correctly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_info_structure
    intent: "Test that fallback_info is structured correctly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_bypasses_fallback_manager
    intent: "Test that manual strategy selection doesn't use fallback manager."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_chunking_on_exception
    intent: "Test that emergency chunking is used when fallback manager fails."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_apply_with_fallback_method_called
    intent: "Test that the old apply_with_fallback method is not called."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_fallback_metadata_preservation.py

```yaml
test_file: tests/chunker/test_fallback_metadata_preservation.py
test_count: 20
legacy_imports:
  - markdown_chunker.chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.types.ChunkingResult
v2_applicable: true
removed_functionality: false

tests:
  - name: test_no_fallback_metadata_when_primary_succeeds
    intent: "Test that fallback metadata is correct when primary strategy succeeds."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_preserved_from_fallback_manager
    intent: "Test that fallback metadata from FallbackManager is preserved."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_not_overwritten_by_error_logic
    intent: "Test that fallback metadata is not overwritten by error-based logic."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_fallback_metadata
    intent: "Test metadata when emergency fallback is used."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_in_chunk_metadata
    intent: "Test that fallback metadata is included in individual chunk metadata."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warnings_preserved_from_fallback_manager
    intent: "Test that warnings from FallbackManager are preserved in final result."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_no_fallback_metadata
    intent: "Test that manual strategy selection doesn't use fallback metadata."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_stage1_failure_fallback_metadata
    intent: "Test fallback metadata when Stage 1 processing fails."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_complete_pipeline_with_fallback
    intent: "Test complete pipeline preserves fallback metadata correctly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_enricher_receives_fallback_info
    intent: "Test that MetadataEnricher receives and uses fallback information."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_fallback_metadata_when_primary_succeeds
    intent: "Test that fallback metadata is correct when primary strategy succeeds."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_preserved_from_fallback_manager
    intent: "Test that fallback metadata from FallbackManager is preserved."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_not_overwritten_by_error_logic
    intent: "Test that fallback metadata is not overwritten by error-based logic."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_fallback_metadata
    intent: "Test metadata when emergency fallback is used."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_in_chunk_metadata
    intent: "Test that fallback metadata is included in individual chunk metadata."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warnings_preserved_from_fallback_manager
    intent: "Test that warnings from FallbackManager are preserved in final result."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_no_fallback_metadata
    intent: "Test that manual strategy selection doesn't use fallback metadata."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_stage1_failure_fallback_metadata
    intent: "Test fallback metadata when Stage 1 processing fails."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_complete_pipeline_with_fallback
    intent: "Test complete pipeline preserves fallback metadata correctly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_enricher_receives_fallback_info
    intent: "Test that MetadataEnricher receives and uses fallback information."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_fallback_properties.py

```yaml
test_file: tests/chunker/test_fallback_properties.py
test_count: 11
legacy_imports:
  - markdown_chunker.chunker.components.fallback_manager.FallbackManager
  - markdown_chunker.chunker.strategies.base.BaseStrategy
  - markdown_chunker.chunker.strategies.sentences_strategy.SentencesStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.types.ChunkingResult
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_fallback_produces_valid_chunks_on_failure
    intent: "Property: When primary strategy fails, fallback produces valid chunks."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: when primary strategy fails, fallback produces valid chunks."
  - name: test_property_fallback_metadata_correct
    intent: "Property: Fallback chunks have correct metadata."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: fallback chunks have correct metadata."
  - name: test_property_empty_chunks_trigger_fallback
    intent: "Property: When primary strategy returns empty chunks, fallback is triggered."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: when primary strategy returns empty chunks, fallback is triggered."
  - name: test_property_fallback_preserves_content
    intent: "Property: Fallback preserves content (minimal data loss)."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: fallback preserves content (minimal data loss)."
  - name: test_property_fallback_is_deterministic
    intent: "Property: Fallback behavior is deterministic (same input → same output)."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: fallback behavior is deterministic (same input → same output)."
  - name: test_property_sentences_strategy_never_fails
    intent: "Property: Sentences strategy (fallback) never fails."
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: sentences strategy (fallback) never fails."
  - name: test_property_fallback_errors_accumulated
    intent: "Property: Fallback accumulates errors from failed strategies."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "property: fallback accumulates errors from failed strategies."
  - name: test_fallback_skipped_when_primary_is_sentences
    intent: "Test that fallback is skipped when primary is already sentences strategy."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_validation
    intent: "Test fallback chain validation."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_validation_disabled
    intent: "Test fallback chain validation when disabled."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_statistics
    intent: "Test fallback statistics."
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_fixes_integration.py

```yaml
test_file: tests/chunker/test_fixes_integration.py
test_count: 26
legacy_imports:
  - markdown_chunker.chunker.MarkdownChunker
  - markdown_chunker.chunker.selector.StrategySelectionError
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.strategies.sentences_strategy.SentencesStrategy
v2_applicable: false
removed_functionality: true

tests:
  - name: test_full_pipeline_with_automatic_strategy_selection
    intent: "Test full pipeline with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_manual_strategy_selection
    intent: "Test manual strategy selection works."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_invalid_strategy_raises_strategy_selection_error
    intent: "Test that invalid strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_small_chunk_size_configuration_works
    intent: "Test that small chunk size configuration works with auto-adjustment."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_dynamic_strategy_addition_removal
    intent: "Test dynamic strategy management works."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_small_document_performance
    intent: "Test small document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_medium_document_performance
    intent: "Test medium document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_document_performance
    intent: "Test large document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_chain_execution
    intent: "Test that fallback chain executes properly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_emergency_chunking_fallback
    intent: "Test emergency chunking as last resort."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_metadata_present
    intent: "Test that strategy metadata is present in chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_tracking
    intent: "Test that fallback metadata is tracked."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_custom_config_integration
    intent: "Test that custom configuration works with all fixes."
    v2_component: ChunkConfig
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_full_pipeline_with_automatic_strategy_selection
    intent: "Test full pipeline with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_manual_strategy_selection
    intent: "Test manual strategy selection works."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_invalid_strategy_raises_strategy_selection_error
    intent: "Test that invalid strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_small_chunk_size_configuration_works
    intent: "Test that small chunk size configuration works with auto-adjustment."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_dynamic_strategy_addition_removal
    intent: "Test dynamic strategy management works."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_small_document_performance
    intent: "Test small document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_medium_document_performance
    intent: "Test medium document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_document_performance
    intent: "Test large document chunking performance."
    v2_component: Performance
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_chain_execution
    intent: "Test that fallback chain executes properly."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_emergency_chunking_fallback
    intent: "Test emergency chunking as last resort."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_metadata_present
    intent: "Test that strategy metadata is present in chunks."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_metadata_tracking
    intent: "Test that fallback metadata is tracked."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_custom_config_integration
    intent: "Test that custom configuration works with all fixes."
    v2_component: ChunkConfig
    test_type: integration
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_header_path_property.py

```yaml
test_file: tests/chunker/test_header_path_property.py
test_count: 18
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_header_path_accuracy
    intent: "**Property 9: Header Path Accuracy**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_header_path_consistency
    intent: "Property: Header paths should be consistent across chunks."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks under the same header should have
consistent header_path prefixes."
  - name: test_property_single_header_path
    intent: "Property: Single header should have correct header_path."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single header, the header_path should contain that header."
  - name: test_simple_hierarchy
    intent: "Test simple H1 > H2 > H3 hierarchy."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_hierarchy
    intent: "Test nested header hierarchy."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_flat_hierarchy
    intent: "Test flat hierarchy (all same level)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_no_headers
    intent: "Test document with no headers."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_only
    intent: "Test document with only headers, no content."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_skipped_levels
    intent: "Test hierarchy with skipped levels (H1 -> H3)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_header_path_accuracy
    intent: "**Property 9: Header Path Accuracy**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_header_path_consistency
    intent: "Property: Header paths should be consistent across chunks."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks under the same header should have
consistent header_path prefixes."
  - name: test_property_single_header_path
    intent: "Property: Single header should have correct header_path."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single header, the header_path should contain that header."
  - name: test_simple_hierarchy
    intent: "Test simple H1 > H2 > H3 hierarchy."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_hierarchy
    intent: "Test nested header hierarchy."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_flat_hierarchy
    intent: "Test flat hierarchy (all same level)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_no_headers
    intent: "Test document with no headers."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_headers_only
    intent: "Test document with only headers, no content."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_skipped_levels
    intent: "Test hierarchy with skipped levels (H1 -> H3)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_idempotence_property.py

```yaml
test_file: tests/chunker/test_idempotence_property.py
test_count: 20
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_idempotence
    intent: "**Property 6: Idempotence**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_idempotence_plain_text
    intent: "Property: Plain text chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunking twice should produce identical results."
  - name: test_property_idempotence_with_lists
    intent: "Property: List chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunking twice should produce identical results."
  - name: test_property_idempotence_with_code
    intent: "Property: Code block chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunking twice should produce identical results."
  - name: test_property_idempotence_across_strategies
    intent: "Property: Idempotence should work for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown and any strategy, chunking twice should produce identical results."
  - name: test_property_idempotence_with_different_chunk_sizes
    intent: "Property: Idempotence with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, chunking twice should produce identical results."
  - name: test_property_idempotence_single_line
    intent: "Property: Single line chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line, chunking twice should produce identical results."
  - name: test_property_idempotence_multiple_paragraphs
    intent: "Property: Multiple paragraphs chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, chunking twice should produce identical results."
  - name: test_property_idempotence_headers_only
    intent: "Property: Headers-only documents chunking should be idempotent."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header, chunking twice should produce identical results."
  - name: test_property_idempotence_multiple_runs
    intent: "Property: Multiple runs should all produce identical results."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: multiple runs should all produce identical results."
  - name: test_property_idempotence
    intent: "**Property 6: Idempotence**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_idempotence_plain_text
    intent: "Property: Plain text chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunking twice should produce identical results."
  - name: test_property_idempotence_with_lists
    intent: "Property: List chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunking twice should produce identical results."
  - name: test_property_idempotence_with_code
    intent: "Property: Code block chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunking twice should produce identical results."
  - name: test_property_idempotence_across_strategies
    intent: "Property: Idempotence should work for all strategies."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown and any strategy, chunking twice should produce identical results."
  - name: test_property_idempotence_with_different_chunk_sizes
    intent: "Property: Idempotence with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, chunking twice should produce identical results."
  - name: test_property_idempotence_single_line
    intent: "Property: Single line chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line, chunking twice should produce identical results."
  - name: test_property_idempotence_multiple_paragraphs
    intent: "Property: Multiple paragraphs chunking should be idempotent."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, chunking twice should produce identical results."
  - name: test_property_idempotence_headers_only
    intent: "Property: Headers-only documents chunking should be idempotent."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header, chunking twice should produce identical results."
  - name: test_property_idempotence_multiple_runs
    intent: "Property: Multiple runs should all produce identical results."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: multiple runs should all produce identical results."
```

### tests/chunker/test_integration.py

```yaml
test_file: tests/chunker/test_integration.py
test_count: 32
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_simple_text_document
    intent: "Test chunking simple text document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test chunking code-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test chunking list-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_heavy_document
    intent: "Test chunking table-heavy document."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_override
    intent: "Test manual strategy selection."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_enabled
    intent: "Test chunking with overlap enabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_enrichment
    intent: "Test that metadata is enriched."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_chain
    intent: "Test fallback chain execution."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_content
    intent: "Test handling empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_document
    intent: "Test handling very long document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_strategy_selection
    intent: "Test that code strategy is selected for code-heavy content."
    v2_component: CodeAwareStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_selection
    intent: "Test that structural strategy is selected for structured content."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_strategy_name
    intent: "Test handling invalid strategy name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_content_recovery
    intent: "Test recovery from malformed content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_time_recorded
    intent: "Test that processing time is recorded."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_reasonable_chunk_count
    intent: "Test that chunk count is reasonable."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simple_text_document
    intent: "Test chunking simple text document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test chunking code-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test chunking list-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_heavy_document
    intent: "Test chunking table-heavy document."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_manual_strategy_override
    intent: "Test manual strategy selection."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_enabled
    intent: "Test chunking with overlap enabled."
    v2_component: ChunkConfig.overlap_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_enrichment
    intent: "Test that metadata is enriched."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_chain
    intent: "Test fallback chain execution."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_content
    intent: "Test handling empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_document
    intent: "Test handling very long document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_strategy_selection
    intent: "Test that code strategy is selected for code-heavy content."
    v2_component: CodeAwareStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_selection
    intent: "Test that structural strategy is selected for structured content."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_strategy_name
    intent: "Test handling invalid strategy name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_content_recovery
    intent: "Test recovery from malformed content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_time_recorded
    intent: "Test that processing time is recorded."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_reasonable_chunk_count
    intent: "Test that chunk count is reasonable."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_list_strategy_properties.py

```yaml
test_file: tests/chunker/test_list_strategy_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_list_structure_preserved
    intent: "For any markdown with lists, list structure should be preserved"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists, list structure should be preserved
in chunks (items not reordered or lost)."
  - name: test_property_nested_lists_preserved
    intent: "For any markdown with nested lists, nesting structure should be"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with nested lists, nesting structure should be
preserved in chunks."
  - name: test_property_list_items_not_split
    intent: "For any markdown with lists, individual list items should not be"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists, individual list items should not be
split across chunks (item content stays together)."
  - name: test_property_list_metadata_present
    intent: "**Property 11d: List Metadata Present**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists processed by list strategy,
chunks containing lists should have appropriate metadata."
  - name: test_property_task_lists_detected
    intent: "**Property 11e: Task Lists Detected**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with task lists (checkboxes), the task list
type should be detected and preserved."
  - name: test_property_ordered_list_numbering_preserved
    intent: "**Property 11f: Ordered List Numbering Preserved**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with ordered lists, the numbering should be
preserved in chunks."
  - name: test_property_list_structure_preserved
    intent: "For any markdown with lists, list structure should be preserved"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists, list structure should be preserved
in chunks (items not reordered or lost)."
  - name: test_property_nested_lists_preserved
    intent: "For any markdown with nested lists, nesting structure should be"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with nested lists, nesting structure should be
preserved in chunks."
  - name: test_property_list_items_not_split
    intent: "For any markdown with lists, individual list items should not be"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists, individual list items should not be
split across chunks (item content stays together)."
  - name: test_property_list_metadata_present
    intent: "**Property 11d: List Metadata Present**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with lists processed by list strategy,
chunks containing lists should have appropriate metadata."
  - name: test_property_task_lists_detected
    intent: "**Property 11e: Task Lists Detected**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with task lists (checkboxes), the task list
type should be detected and preserved."
  - name: test_property_ordered_list_numbering_preserved
    intent: "**Property 11f: Ordered List Numbering Preserved**"
    v2_component: REMOVED: ListStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with ordered lists, the numbering should be
preserved in chunks."
```

### tests/chunker/test_logging_integration.py

```yaml
test_file: tests/chunker/test_logging_integration.py
test_count: 16
legacy_imports:
  - markdown_chunker.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_logging_basic_chunking
    intent: "Test that basic chunking produces expected log messages."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_with_manual_strategy
    intent: "Test logging when using manual strategy override."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_error_handling
    intent: "Test that errors are logged appropriately."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_levels
    intent: "Test that different log levels work correctly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_includes_metrics
    intent: "Test that log messages include useful metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_with_fallback
    intent: "Test logging when fallback is triggered."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_can_be_disabled
    intent: "Test that logging can be effectively disabled."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_respects_level
    intent: "Test that logging respects configured level."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_basic_chunking
    intent: "Test that basic chunking produces expected log messages."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_with_manual_strategy
    intent: "Test logging when using manual strategy override."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_error_handling
    intent: "Test that errors are logged appropriately."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_levels
    intent: "Test that different log levels work correctly."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_includes_metrics
    intent: "Test that log messages include useful metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_with_fallback
    intent: "Test logging when fallback is triggered."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_can_be_disabled
    intent: "Test that logging can be effectively disabled."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_logging_respects_level
    intent: "Test that logging respects configured level."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_metadata_properties.py

```yaml
test_file: tests/chunker/test_metadata_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.components.metadata_enricher.MetadataEnricher
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_metadata_has_required_fields
    intent: "Property: All chunks have required metadata fields."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: all chunks have required metadata fields."
  - name: test_property_chunk_indices_correct
    intent: "Property: Chunk indices are correct and sequential."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunk indices are correct and sequential."
  - name: test_property_total_chunks_consistent
    intent: "Property: total_chunks is consistent across all chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: total_chunks is consistent across all chunks."
  - name: test_property_first_last_flags_correct
    intent: "Property: is_first_chunk and is_last_chunk flags are correct."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: is_first_chunk and is_last_chunk flags are correct."
  - name: test_property_content_statistics_present
    intent: "Property: Content statistics are present and valid."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: content statistics are present and valid."
  - name: test_property_document_id_propagated
    intent: "Property: Document ID is propagated to all chunks."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: document id is propagated to all chunks."
  - name: test_property_validation_passes
    intent: "Property: Enriched chunks pass validation."
    v2_component: Validator
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: enriched chunks pass validation."
  - name: test_code_metadata_enrichment
    intent: "Test code-specific metadata enrichment."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_list_metadata_enrichment
    intent: "Test list-specific metadata enrichment."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_table_metadata_enrichment
    intent: "Test table-specific metadata enrichment."
    v2_component: ContentAnalysis.tables
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_searchability_metadata
    intent: "Test searchability metadata."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_summary
    intent: "Test metadata summary generation."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_mixed_strategy_properties.py

```yaml
test_file: tests/chunker/test_mixed_strategy_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_mixed_content_detected
    intent: "**Property 14a: Mixed Content Detected**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with multiple content types, mixed strategy
should be selected when appropriate."
  - name: test_property_no_content_loss
    intent: "**Property 14b: No Content Loss**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, all content should be preserved
across all chunks regardless of which strategies are used."
  - name: test_property_section_boundaries_preserved
    intent: "**Property 14c: Section Boundaries Preserved**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, section boundaries (headers) should be
preserved and not split across chunks inappropriately."
  - name: test_property_appropriate_strategies_used
    intent: "**Property 14d: Appropriate Strategies Used**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, if mixed strategy is used, it should
apply appropriate sub-strategies for different content types."
  - name: test_property_metadata_consistency
    intent: "**Property 14e: Metadata Consistency**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, chunks should have consistent and
appropriate metadata indicating which strategies were used."
  - name: test_property_handles_complex_documents
    intent: "**Property 14f: Handles Complex Documents**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any complex mixed document, the strategy should handle it
without errors and produce reasonable chunks."
  - name: test_property_mixed_content_detected
    intent: "**Property 14a: Mixed Content Detected**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with multiple content types, mixed strategy
should be selected when appropriate."
  - name: test_property_no_content_loss
    intent: "**Property 14b: No Content Loss**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, all content should be preserved
across all chunks regardless of which strategies are used."
  - name: test_property_section_boundaries_preserved
    intent: "**Property 14c: Section Boundaries Preserved**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, section boundaries (headers) should be
preserved and not split across chunks inappropriately."
  - name: test_property_appropriate_strategies_used
    intent: "**Property 14d: Appropriate Strategies Used**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, if mixed strategy is used, it should
apply appropriate sub-strategies for different content types."
  - name: test_property_metadata_consistency
    intent: "**Property 14e: Metadata Consistency**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any mixed document, chunks should have consistent and
appropriate metadata indicating which strategies were used."
  - name: test_property_handles_complex_documents
    intent: "**Property 14f: Handles Complex Documents**"
    v2_component: REMOVED: MixedStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any complex mixed document, the strategy should handle it
without errors and produce reasonable chunks."
```

### tests/chunker/test_mixed_strategy_stage1_integration.py

```yaml
test_file: tests/chunker/test_mixed_strategy_stage1_integration.py
test_count: 8
legacy_imports:
  - markdown_chunker.chunker.strategies.mixed_strategy.MixedStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
  - markdown_chunker.parser.types.ElementCollection
  - markdown_chunker.parser.types.ListItem
v2_applicable: false
removed_functionality: true

tests:
  - name: test_mixed_strategy_uses_stage1_lists
    intent: "Test that MixedStrategy uses Stage1Results lists instead of regex."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_uses_stage1_tables
    intent: "Test that MixedStrategy uses Stage1Results tables instead of regex."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_fallback_to_regex_lists
    intent: "Test fallback to regex when Stage 1 list data unavailable."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_fallback_to_regex_tables
    intent: "Test fallback to regex when Stage 1 table data unavailable."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_content_preserves_all_structure
    intent: "Test that mixed content preserves structure from Stage 1."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_empty_stage1_results
    intent: "Test behavior with empty Stage1Results."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_stage1_priority_over_regex
    intent: "Test that Stage 1 data takes priority over regex detection."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_integration_with_chunking
    intent: "Test complete integration with chunking process."
    v2_component: REMOVED: MixedStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_monotonic_ordering_property.py

```yaml
test_file: tests/chunker/test_monotonic_ordering_property.py
test_count: 20
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_monotonic_ordering
    intent: "**Property 7: Monotonic Chunk Ordering**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_monotonic_ordering_plain_text
    intent: "Property: Plain text chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_with_lists
    intent: "Property: List chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_with_code
    intent: "Property: Code block chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_auto_strategy
    intent: "Property: Monotonic ordering should work with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks should be in monotonic order regardless of
which strategy v2 selects automatically."
  - name: test_property_monotonic_ordering_with_different_chunk_sizes
    intent: "Property: Monotonic ordering with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, chunks should be in monotonic order."
  - name: test_property_monotonic_ordering_multiple_paragraphs
    intent: "Property: Multiple paragraphs should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, chunks should be in monotonic order."
  - name: test_property_strict_monotonic_ordering
    intent: "Property: Verify strict monotonic ordering (no equal start_lines)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: verify strict monotonic ordering (no equal start_lines)."
  - name: test_property_end_line_consistency
    intent: "Property: Verify end_line is also monotonic (with overlap consideration)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any document, end_line values should generally be monotonic,
though overlap may cause some variation."
  - name: test_property_no_backwards_chunks
    intent: "Property: No chunk should appear before previous chunk in document."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any document, each chunk's start should be at or after
the previous chunk's start."
  - name: test_property_monotonic_ordering
    intent: "**Property 7: Monotonic Chunk Ordering**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_monotonic_ordering_plain_text
    intent: "Property: Plain text chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_with_lists
    intent: "Property: List chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_with_code
    intent: "Property: Code block chunks should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunk start_line values should be monotonically increasing."
  - name: test_property_monotonic_ordering_auto_strategy
    intent: "Property: Monotonic ordering should work with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks should be in monotonic order regardless of
which strategy v2 selects automatically."
  - name: test_property_monotonic_ordering_with_different_chunk_sizes
    intent: "Property: Monotonic ordering with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, chunks should be in monotonic order."
  - name: test_property_monotonic_ordering_multiple_paragraphs
    intent: "Property: Multiple paragraphs should be in monotonic order."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, chunks should be in monotonic order."
  - name: test_property_strict_monotonic_ordering
    intent: "Property: Verify strict monotonic ordering (no equal start_lines)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: verify strict monotonic ordering (no equal start_lines)."
  - name: test_property_end_line_consistency
    intent: "Property: Verify end_line is also monotonic (with overlap consideration)."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any document, end_line values should generally be monotonic,
though overlap may cause some variation."
  - name: test_property_no_backwards_chunks
    intent: "Property: No chunk should appear before previous chunk in document."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any document, each chunk's start should be at or after
the previous chunk's start."
```

### tests/chunker/test_no_empty_chunks_property.py

```yaml
test_file: tests/chunker/test_no_empty_chunks_property.py
test_count: 18
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_no_empty_chunks
    intent: "**Property 2: No Empty Chunks for Non-Empty Input**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_empty_chunks_plain_text
    intent: "Property: Plain text should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty plain text, all chunks should have content."
  - name: test_property_no_empty_chunks_with_lists
    intent: "Property: Markdown lists should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of items, all chunks should have content."
  - name: test_property_no_empty_chunks_with_code
    intent: "Property: Code blocks should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, all chunks should have content."
  - name: test_property_no_empty_chunks_auto_strategy
    intent: "Property: No empty chunks should work with automatic strategy selection."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown, no chunks should be empty regardless of
which strategy v2 selects automatically."
  - name: test_property_no_empty_chunks_with_different_chunk_sizes
    intent: "Property: No empty chunks with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, no chunks should be empty."
  - name: test_property_no_empty_chunks_single_line
    intent: "Property: Single line should not produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line of text, chunks should have content."
  - name: test_property_no_empty_chunks_multiple_paragraphs
    intent: "Property: Multiple paragraphs should not produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, all chunks should have content."
  - name: test_property_no_empty_chunks_headers_only
    intent: "Property: Headers-only documents should not produce empty chunks."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header, chunks should have content."
  - name: test_property_no_empty_chunks
    intent: "**Property 2: No Empty Chunks for Non-Empty Input**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_no_empty_chunks_plain_text
    intent: "Property: Plain text should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty plain text, all chunks should have content."
  - name: test_property_no_empty_chunks_with_lists
    intent: "Property: Markdown lists should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of items, all chunks should have content."
  - name: test_property_no_empty_chunks_with_code
    intent: "Property: Code blocks should never produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, all chunks should have content."
  - name: test_property_no_empty_chunks_auto_strategy
    intent: "Property: No empty chunks should work with automatic strategy selection."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any non-empty markdown, no chunks should be empty regardless of
which strategy v2 selects automatically."
  - name: test_property_no_empty_chunks_with_different_chunk_sizes
    intent: "Property: No empty chunks with different chunk sizes."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any chunk size configuration, no chunks should be empty."
  - name: test_property_no_empty_chunks_single_line
    intent: "Property: Single line should not produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line of text, chunks should have content."
  - name: test_property_no_empty_chunks_multiple_paragraphs
    intent: "Property: Multiple paragraphs should not produce empty chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of paragraphs, all chunks should have content."
  - name: test_property_no_empty_chunks_headers_only
    intent: "Property: Headers-only documents should not produce empty chunks."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header, chunks should have content."
```

### tests/chunker/test_overlap_properties.py

```yaml
test_file: tests/chunker/test_overlap_properties.py
test_count: 11
legacy_imports:
  - markdown_chunker.chunker.components.overlap_manager.OverlapManager
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_overlap_is_exact_duplicate
    intent: "Property: Overlapping content is exact duplicate from previous chunk."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlapping content is exact duplicate from previous chunk."
  - name: test_property_overlap_size_within_bounds
    intent: "Property: Overlap size is within configured bounds."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap size is within configured bounds."
  - name: test_property_overlap_percentage_works
    intent: "Property: Percentage-based overlap works correctly."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: percentage-based overlap works correctly."
  - name: test_property_overlap_metadata_correct
    intent: "Property: Overlap metadata is correct and complete."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap metadata is correct and complete."
  - name: test_property_no_overlap_when_disabled
    intent: "Property: No overlap applied when disabled."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: no overlap applied when disabled."
  - name: test_property_overlap_preserves_sentence_boundaries
    intent: "Property: Overlap preserves sentence boundaries (no mid-sentence cuts)."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap preserves sentence boundaries (no mid-sentence cuts)."
  - name: test_property_overlap_statistics_accurate
    intent: "Property: Overlap statistics are accurate."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap statistics are accurate."
  - name: test_overlap_single_chunk
    intent: "Test that single chunk has no overlap."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_empty_chunks
    intent: "Test that empty chunk list is handled."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_statistics_empty
    intent: "Test statistics for empty chunk list."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_statistics_no_overlap
    intent: "Test statistics when no overlap applied."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_overlap_properties_redesign.py

```yaml
test_file: tests/chunker/test_overlap_properties_redesign.py
test_count: 18
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_previous_content_is_suffix
    intent: "Property: previous_content is a suffix of the previous chunk's content."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: previous_content is a suffix of the previous chunk's content."
  - name: test_property_first_chunk_no_previous
    intent: "Property: First chunk has no previous_content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: first chunk has no previous_content."
  - name: test_property_overlap_size_constraint
    intent: "Property: Overlap size respects configuration with tolerance."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap size respects configuration with tolerance."
  - name: test_property_overlap_disabled_no_metadata
    intent: "Property: When overlap_size=0, no overlap metadata is added."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: when overlap_size=0, no overlap metadata is added."
  - name: test_property_content_unchanged_with_overlap
    intent: "Property: Chunk content is unchanged by overlap processing."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunk content is unchanged by overlap processing."
  - name: test_property_line_numbers_unchanged
    intent: "Property: Line numbers are unchanged by overlap processing."
    v2_component: ContentAnalysis (line positions)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: line numbers are unchanged by overlap processing."
  - name: test_property_overlap_with_structural_chunks
    intent: "Property: Overlap works correctly with structural (header-based) chunks."
    v2_component: StructuralStrategy
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap works correctly with structural (header-based) chunks."
  - name: test_single_chunk_no_overlap
    intent: "Property: Single chunk has no overlap metadata."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: single chunk has no overlap metadata."
  - name: test_overlap_size_zero_no_metadata
    intent: "Property: When overlap_size=0, no overlap metadata is added."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: when overlap_size=0, no overlap metadata is added."
  - name: test_property_previous_content_is_suffix
    intent: "Property: previous_content is a suffix of the previous chunk's content."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: previous_content is a suffix of the previous chunk's content."
  - name: test_property_first_chunk_no_previous
    intent: "Property: First chunk has no previous_content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: first chunk has no previous_content."
  - name: test_property_overlap_size_constraint
    intent: "Property: Overlap size respects configuration with tolerance."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap size respects configuration with tolerance."
  - name: test_property_overlap_disabled_no_metadata
    intent: "Property: When overlap_size=0, no overlap metadata is added."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: when overlap_size=0, no overlap metadata is added."
  - name: test_property_content_unchanged_with_overlap
    intent: "Property: Chunk content is unchanged by overlap processing."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunk content is unchanged by overlap processing."
  - name: test_property_line_numbers_unchanged
    intent: "Property: Line numbers are unchanged by overlap processing."
    v2_component: ContentAnalysis (line positions)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: line numbers are unchanged by overlap processing."
  - name: test_property_overlap_with_structural_chunks
    intent: "Property: Overlap works correctly with structural (header-based) chunks."
    v2_component: StructuralStrategy
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: overlap works correctly with structural (header-based) chunks."
  - name: test_single_chunk_no_overlap
    intent: "Property: Single chunk has no overlap metadata."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: single chunk has no overlap metadata."
  - name: test_overlap_size_zero_no_metadata
    intent: "Property: When overlap_size=0, no overlap metadata is added."
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: when overlap_size=0, no overlap metadata is added."
```

### tests/chunker/test_performance.py

```yaml
test_file: tests/chunker/test_performance.py
test_count: 60
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.performance.ChunkCache
  - markdown_chunker.chunker.performance.MemoryEfficientProcessor
  - markdown_chunker.chunker.performance.PerformanceMonitor
  - markdown_chunker.chunker.performance.PerformanceOptimizer
v2_applicable: true
removed_functionality: false

tests:
  - name: test_lazy_loading
    intent: "Test that strategies are loaded lazily."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_strategies
    intent: "Test caching multiple strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test clearing cache."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_record_metrics
    intent: "Test recording performance metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_operations
    intent: "Test monitoring multiple operations."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_calculation
    intent: "Test throughput calculation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_disabled_monitoring
    intent: "Test that disabled monitoring doesn't record."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_metrics
    intent: "Test clearing metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_put_get
    intent: "Test basic cache operations."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_miss
    intent: "Test cache miss."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_lru_eviction
    intent: "Test LRU eviction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_access_order_update
    intent: "Test that access updates order."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_size
    intent: "Test cache size tracking."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test clearing cache."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_same_content_same_key
    intent: "Test that same content generates same key."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_different_content_different_key
    intent: "Test that different content generates different keys."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_different_config_different_key
    intent: "Test that different config generates different keys."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_in_chunks
    intent: "Test processing content in chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_estimation
    intent: "Test memory usage estimation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_decision
    intent: "Test caching decision logic."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_streaming_decision
    intent: "Test streaming decision logic."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_optimal_chunk_size
    intent: "Test optimal chunk size calculation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_monitoring_disabled_by_default
    intent: "Test that performance monitoring is disabled by default."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_monitoring_enabled
    intent: "Test performance monitoring when enabled."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enable_disable_monitoring
    intent: "Test enabling and disabling monitoring."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_caches
    intent: "Test clearing caches."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_performance
    intent: "Test performance on small documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test performance on medium documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test performance on large documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_performance
    intent: "Test performance on code-heavy documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_lazy_loading
    intent: "Test that strategies are loaded lazily."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_strategies
    intent: "Test caching multiple strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test clearing cache."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_record_metrics
    intent: "Test recording performance metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_operations
    intent: "Test monitoring multiple operations."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_calculation
    intent: "Test throughput calculation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_disabled_monitoring
    intent: "Test that disabled monitoring doesn't record."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_metrics
    intent: "Test clearing metrics."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_put_get
    intent: "Test basic cache operations."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_miss
    intent: "Test cache miss."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_lru_eviction
    intent: "Test LRU eviction."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_access_order_update
    intent: "Test that access updates order."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_size
    intent: "Test cache size tracking."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test clearing cache."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_same_content_same_key
    intent: "Test that same content generates same key."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_different_content_different_key
    intent: "Test that different content generates different keys."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_different_config_different_key
    intent: "Test that different config generates different keys."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_in_chunks
    intent: "Test processing content in chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_estimation
    intent: "Test memory usage estimation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_cache_decision
    intent: "Test caching decision logic."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_streaming_decision
    intent: "Test streaming decision logic."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_optimal_chunk_size
    intent: "Test optimal chunk size calculation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_monitoring_disabled_by_default
    intent: "Test that performance monitoring is disabled by default."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_monitoring_enabled
    intent: "Test performance monitoring when enabled."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_enable_disable_monitoring
    intent: "Test enabling and disabling monitoring."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_caches
    intent: "Test clearing caches."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_performance
    intent: "Test performance on small documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test performance on medium documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test performance on large documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_performance
    intent: "Test performance on code-heavy documents."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_performance_benchmarks.py

```yaml
test_file: tests/chunker/test_performance_benchmarks.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_small_document_performance
    intent: "Test small document processing performance (< 0.1s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test medium document processing performance (< 1.0s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test large document processing performance (< 5.0s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_regression_check
    intent: "Test that fixes haven't caused performance regression."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_chunk_config_performance
    intent: "Test performance with small chunk configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_chunk_config_performance
    intent: "Test performance with large chunk configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_performance
    intent: "Test small document processing performance (< 0.1s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test medium document processing performance (< 1.0s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test large document processing performance (< 5.0s target)."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_regression_check
    intent: "Test that fixes haven't caused performance regression."
    v2_component: Performance
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_chunk_config_performance
    intent: "Test performance with small chunk configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_chunk_config_performance
    intent: "Test performance with large chunk configuration."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_phase2_properties.py

```yaml
test_file: tests/chunker/test_phase2_properties.py
test_count: 14
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_1_header_content_cohesion
    intent: "**Property 1: Header-Content Cohesion**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with headers and content, headers should always
appear with at least some content in the same chunk (no orphan headers)."
  - name: test_property_2_section_boundary_integrity
    intent: "**Property 2: Section Boundary Integrity**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any multi-section document, each chunk should belong to a single
major section (no mixing of unrelated sections)."
  - name: test_property_3_sub_block_boundary_respect
    intent: "**Property 3: Sub-Block Boundary Respect**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, splits should only occur at block boundaries,
never mid-paragraph or mid-block."
  - name: test_property_4_markdown_structure_preservation
    intent: "**Property 4: Markdown Structure Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, all markdown formatting should be preserved
in the output chunks."
  - name: test_property_5_source_traceability_completeness
    intent: "**Property 5: Source Traceability Completeness**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, all chunks should have complete source metadata
(section_path, start_line, end_line)."
  - name: test_property_6_atomic_element_integrity
    intent: "**Property 6: Atomic Element Integrity**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with urls, urls should never be split across chunks."
  - name: test_property_7_section_aware_overlap
    intent: "**Property 7: Section-Aware Overlap**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with overlap enabled, overlap should not cross
major section boundaries."
  - name: test_property_1_header_content_cohesion
    intent: "**Property 1: Header-Content Cohesion**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with headers and content, headers should always
appear with at least some content in the same chunk (no orphan headers)."
  - name: test_property_2_section_boundary_integrity
    intent: "**Property 2: Section Boundary Integrity**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any multi-section document, each chunk should belong to a single
major section (no mixing of unrelated sections)."
  - name: test_property_3_sub_block_boundary_respect
    intent: "**Property 3: Sub-Block Boundary Respect**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, splits should only occur at block boundaries,
never mid-paragraph or mid-block."
  - name: test_property_4_markdown_structure_preservation
    intent: "**Property 4: Markdown Structure Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, all markdown formatting should be preserved
in the output chunks."
  - name: test_property_5_source_traceability_completeness
    intent: "**Property 5: Source Traceability Completeness**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document, all chunks should have complete source metadata
(section_path, start_line, end_line)."
  - name: test_property_6_atomic_element_integrity
    intent: "**Property 6: Atomic Element Integrity**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with urls, urls should never be split across chunks."
  - name: test_property_7_section_aware_overlap
    intent: "**Property 7: Section-Aware Overlap**"
    v2_component: ChunkConfig.overlap_size
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any document with overlap enabled, overlap should not cross
major section boundaries."
```

### tests/chunker/test_preamble_chunking.py

```yaml
test_file: tests/chunker/test_preamble_chunking.py
test_count: 28
legacy_imports:
  - markdown_chunker.chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_preamble_added_to_first_chunk_metadata
    intent: "Test that preamble is added to first chunk metadata by default."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk
    intent: "Test creating separate chunk for preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_no_metadata
    intent: "Test that documents without preamble don't get preamble metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_extraction_disabled
    intent: "Test that preamble extraction can be disabled."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_metadata_fields
    intent: "Test that metadata fields are extracted correctly."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_type_in_chunk_metadata
    intent: "Test that preamble type is correctly identified."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_chunk_type
    intent: "Test that separate preamble chunk has correct content_type."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_line_numbers
    intent: "Test that preamble chunk has correct line numbers."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_integration_with_strategies
    intent: "Test that preamble works with different strategies."
    v2_component: ContentAnalysis.has_preamble
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_edge_cases
    intent: "Test preamble with edge cases."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_full_analysis
    intent: "Test preamble with full analysis result."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_dict_format
    intent: "Test preamble with dictionary return format."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_preserved_in_overlap
    intent: "Test that preamble metadata is preserved when overlap is enabled."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_manual_strategy
    intent: "Test preamble with manually specified strategy."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_added_to_first_chunk_metadata
    intent: "Test that preamble is added to first chunk metadata by default."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk
    intent: "Test creating separate chunk for preamble."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_no_metadata
    intent: "Test that documents without preamble don't get preamble metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_extraction_disabled
    intent: "Test that preamble extraction can be disabled."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_metadata_fields
    intent: "Test that metadata fields are extracted correctly."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_type_in_chunk_metadata
    intent: "Test that preamble type is correctly identified."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_chunk_type
    intent: "Test that separate preamble chunk has correct content_type."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_line_numbers
    intent: "Test that preamble chunk has correct line numbers."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_integration_with_strategies
    intent: "Test that preamble works with different strategies."
    v2_component: ContentAnalysis.has_preamble
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_edge_cases
    intent: "Test preamble with edge cases."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_full_analysis
    intent: "Test preamble with full analysis result."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_dict_format
    intent: "Test preamble with dictionary return format."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_preserved_in_overlap
    intent: "Test that preamble metadata is preserved when overlap is enabled."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_manual_strategy
    intent: "Test preamble with manually specified strategy."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_preamble_config.py

```yaml
test_file: tests/chunker/test_preamble_config.py
test_count: 22
legacy_imports:
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_default_preamble_settings
    intent: "Test default preamble settings."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_custom_preamble_settings
    intent: "Test custom preamble settings."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_preamble_min_size_raises_error
    intent: "Test that negative preamble_min_size raises ValueError."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_disabled
    intent: "Test disabling preamble extraction."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk_enabled
    intent: "Test enabling separate preamble chunk."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_factory_methods_preserve_preamble_defaults
    intent: "Test that factory methods preserve preamble defaults."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_added_to_first_chunk_metadata
    intent: "Test that preamble is added to first chunk metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk
    intent: "Test creating separate preamble chunk."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_no_metadata
    intent: "Test that no preamble means no preamble metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_extraction_disabled
    intent: "Test that disabling preamble extraction works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_metadata_fields
    intent: "Test preamble with metadata fields."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_default_preamble_settings
    intent: "Test default preamble settings."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_custom_preamble_settings
    intent: "Test custom preamble settings."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_negative_preamble_min_size_raises_error
    intent: "Test that negative preamble_min_size raises ValueError."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_disabled
    intent: "Test disabling preamble extraction."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk_enabled
    intent: "Test enabling separate preamble chunk."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_factory_methods_preserve_preamble_defaults
    intent: "Test that factory methods preserve preamble defaults."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_added_to_first_chunk_metadata
    intent: "Test that preamble is added to first chunk metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_separate_preamble_chunk
    intent: "Test creating separate preamble chunk."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_preamble_no_metadata
    intent: "Test that no preamble means no preamble metadata."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_extraction_disabled
    intent: "Test that disabling preamble extraction works."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preamble_with_metadata_fields
    intent: "Test preamble with metadata fields."
    v2_component: ContentAnalysis.has_preamble
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_regression_prevention.py

```yaml
test_file: tests/chunker/test_regression_prevention.py
test_count: 30
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.extract_fenced_blocks
  - markdown_chunker.chunker.MarkdownChunker
  - markdown_chunker.chunker.types.Chunk
v2_applicable: true
removed_functionality: false

tests:
  - name: test_ast_content_not_empty_regression
    intent: "Prevent regression: AST nodes should contain actual content, not be empty."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_paragraph_hierarchy_regression
    intent: "Prevent regression: Paragraphs should be siblings of headers, not children."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_inline_content_preservation_regression
    intent: "Prevent regression: Inline elements should have their content preserved."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fences_single_block_regression
    intent: "Prevent regression: Nested fences should create single outer block, not phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_nested_fence_types_regression
    intent: "Prevent regression: Mixed nested fence types should be handled correctly."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deep_nesting_regression
    intent: "Prevent regression: Deep nesting should be handled without creating phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_stage1_lists_integration_regression
    intent: "Prevent regression: MixedStrategy should use Stage 1 list data when available."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_stage1_tables_integration_regression
    intent: "Prevent regression: MixedStrategy should use Stage 1 table data when available."
    v2_component: ContentAnalysis.tables
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_to_regex_regression
    intent: "Prevent regression: Should gracefully fallback to regex when Stage 1 data unavailable."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_accuracy_regression
    intent: "Prevent regression: Fallback metadata should reflect actual usage, not error logic."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warnings_preservation_regression
    intent: "Prevent regression: Warnings should be preserved in ChunkingResult."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_chunking_line_numbers_regression
    intent: "Prevent regression: Emergency chunking should have accurate line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_progression_regression
    intent: "Prevent regression: Line numbers should progress correctly across chunks."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_both_stages_discoverable_regression
    intent: "Prevent regression: Both Stage 1 and Stage 2 should be discoverable by pytest."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_package_installation_regression
    intent: "Prevent regression: Package should install and import correctly."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_ast_content_not_empty_regression
    intent: "Prevent regression: AST nodes should contain actual content, not be empty."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_header_paragraph_hierarchy_regression
    intent: "Prevent regression: Paragraphs should be siblings of headers, not children."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_inline_content_preservation_regression
    intent: "Prevent regression: Inline elements should have their content preserved."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_nested_fences_single_block_regression
    intent: "Prevent regression: Nested fences should create single outer block, not phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_nested_fence_types_regression
    intent: "Prevent regression: Mixed nested fence types should be handled correctly."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deep_nesting_regression
    intent: "Prevent regression: Deep nesting should be handled without creating phantom blocks."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_stage1_lists_integration_regression
    intent: "Prevent regression: MixedStrategy should use Stage 1 list data when available."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_stage1_tables_integration_regression
    intent: "Prevent regression: MixedStrategy should use Stage 1 table data when available."
    v2_component: ContentAnalysis.tables
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_to_regex_regression
    intent: "Prevent regression: Should gracefully fallback to regex when Stage 1 data unavailable."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_metadata_accuracy_regression
    intent: "Prevent regression: Fallback metadata should reflect actual usage, not error logic."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_warnings_preservation_regression
    intent: "Prevent regression: Warnings should be preserved in ChunkingResult."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_emergency_chunking_line_numbers_regression
    intent: "Prevent regression: Emergency chunking should have accurate line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_line_number_progression_regression
    intent: "Prevent regression: Line numbers should progress correctly across chunks."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_both_stages_discoverable_regression
    intent: "Prevent regression: Both Stage 1 and Stage 2 should be discoverable by pytest."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_package_installation_regression
    intent: "Prevent regression: Package should install and import correctly."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_sentences_strategy_properties.py

```yaml
test_file: tests/chunker/test_sentences_strategy_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_no_data_loss
    intent: "**Property 13a: No Data Loss**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, all input text should appear in output chunks
(sentences strategy preserves all content)."
  - name: test_property_paragraph_boundaries_respected
    intent: "**Property 13b: Paragraph Boundaries Respected**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text with paragraphs, paragraph boundaries should be
preserved when possible (no mid-paragraph splits unless necessary)."
  - name: test_property_chunk_size_limits_respected
    intent: "**Property 13c: Chunk Size Limits Respected**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, chunks should not exceed max_chunk_size
(unless a single sentence is larger)."
  - name: test_property_sentence_boundaries_preserved
    intent: "**Property 13d: Sentence Boundaries Preserved**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, sentences should not be split mid-sentence
(sentence boundaries are preserved)."
  - name: test_property_works_as_fallback
    intent: "**Property 13e: Works as Universal Fallback**"
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, sentences strategy should always be able
to process it (never fails)."
  - name: test_property_metadata_present
    intent: "**Property 13f: Metadata Present**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content processed by sentences strategy,
chunks should have appropriate metadata."
  - name: test_property_no_data_loss
    intent: "**Property 13a: No Data Loss**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, all input text should appear in output chunks
(sentences strategy preserves all content)."
  - name: test_property_paragraph_boundaries_respected
    intent: "**Property 13b: Paragraph Boundaries Respected**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text with paragraphs, paragraph boundaries should be
preserved when possible (no mid-paragraph splits unless necessary)."
  - name: test_property_chunk_size_limits_respected
    intent: "**Property 13c: Chunk Size Limits Respected**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, chunks should not exceed max_chunk_size
(unless a single sentence is larger)."
  - name: test_property_sentence_boundaries_preserved
    intent: "**Property 13d: Sentence Boundaries Preserved**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, sentences should not be split mid-sentence
(sentence boundaries are preserved)."
  - name: test_property_works_as_fallback
    intent: "**Property 13e: Works as Universal Fallback**"
    v2_component: FallbackStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content, sentences strategy should always be able
to process it (never fails)."
  - name: test_property_metadata_present
    intent: "**Property 13f: Metadata Present**"
    v2_component: REMOVED: SentencesStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any text content processed by sentences strategy,
chunks should have appropriate metadata."
```

### tests/chunker/test_serialization.py

```yaml
test_file: tests/chunker/test_serialization.py
test_count: 26
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunk_to_dict_basic
    intent: "Test basic chunk to_dict conversion."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_from_dict_basic
    intent: "Test basic chunk from_dict creation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_roundtrip
    intent: "Test chunk serialization roundtrip."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_json_serialization
    intent: "Test chunk can be serialized to JSON."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_to_dict_basic
    intent: "Test basic result to_dict conversion."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_from_dict_basic
    intent: "Test basic result from_dict creation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_roundtrip
    intent: "Test result serialization roundtrip."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_json_serialization
    intent: "Test result can be serialized to JSON."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_to_dict_basic
    intent: "Test basic config to_dict conversion."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_from_dict_basic
    intent: "Test basic config from_dict creation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_roundtrip
    intent: "Test config serialization roundtrip."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_json_serialization
    intent: "Test config can be serialized to JSON."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_from_dict_with_defaults
    intent: "Test config from_dict applies defaults for missing values."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_to_dict_basic
    intent: "Test basic chunk to_dict conversion."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_from_dict_basic
    intent: "Test basic chunk from_dict creation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_roundtrip
    intent: "Test chunk serialization roundtrip."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_json_serialization
    intent: "Test chunk can be serialized to JSON."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_to_dict_basic
    intent: "Test basic result to_dict conversion."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_from_dict_basic
    intent: "Test basic result from_dict creation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_roundtrip
    intent: "Test result serialization roundtrip."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_result_json_serialization
    intent: "Test result can be serialized to JSON."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_to_dict_basic
    intent: "Test basic config to_dict conversion."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_from_dict_basic
    intent: "Test basic config from_dict creation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_roundtrip
    intent: "Test config serialization roundtrip."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_json_serialization
    intent: "Test config can be serialized to JSON."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_from_dict_with_defaults
    intent: "Test config from_dict applies defaults for missing values."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_serialization_roundtrip_property.py

```yaml
test_file: tests/chunker/test_serialization_roundtrip_property.py
test_count: 18
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_serialization_roundtrip
    intent: "**Property 14: Serialization Round-Trip**"
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_serialization_roundtrip_plain_text
    intent: "Property: Plain text chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunks should survive round-trip."
  - name: test_property_serialization_roundtrip_with_lists
    intent: "Property: List chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunks should survive round-trip."
  - name: test_property_serialization_roundtrip_with_code
    intent: "Property: Code block chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunks should survive round-trip."
  - name: test_property_serialization_auto_strategy
    intent: "Property: Serialization should work with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks should survive round-trip regardless of
which strategy v2 selects automatically."
  - name: test_property_serialization_single_line
    intent: "Property: Single line chunks can be serialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line, chunks should survive round-trip."
  - name: test_property_metadata_serialization
    intent: "Property: Metadata should be serializable."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunk metadata should survive round-trip."
  - name: test_special_characters_serialization
    intent: "Test serialization with special characters."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_metadata_serialization
    intent: "Test serialization with empty or None metadata."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_serialization_roundtrip
    intent: "**Property 14: Serialization Round-Trip**"
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_serialization_roundtrip_plain_text
    intent: "Property: Plain text chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any plain text, chunks should survive round-trip."
  - name: test_property_serialization_roundtrip_with_lists
    intent: "Property: List chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list, chunks should survive round-trip."
  - name: test_property_serialization_roundtrip_with_code
    intent: "Property: Code block chunks can be serialized and deserialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any code content, chunks should survive round-trip."
  - name: test_property_serialization_auto_strategy
    intent: "Property: Serialization should work with automatic strategy selection."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunks should survive round-trip regardless of
which strategy v2 selects automatically."
  - name: test_property_serialization_single_line
    intent: "Property: Single line chunks can be serialized."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any single line, chunks should survive round-trip."
  - name: test_property_metadata_serialization
    intent: "Property: Metadata should be serializable."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any markdown, chunk metadata should survive round-trip."
  - name: test_special_characters_serialization
    intent: "Test serialization with special characters."
    v2_component: Chunk.to_dict() / from_dict()
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_metadata_serialization
    intent: "Test serialization with empty or None metadata."
    v2_component: Chunk.metadata
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_stage1_integration.py

```yaml
test_file: tests/chunker/test_stage1_integration.py
test_count: 5
legacy_imports:
  - markdown_chunker.chunker.strategies.list_strategy.ListStrategy
  - markdown_chunker.chunker.strategies.mixed_strategy.MixedStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.process_markdown
  - markdown_chunker.parser.types.ListItem
v2_applicable: false
removed_functionality: true

tests:
  - name: test_mixed_strategy_with_real_stage1_lists
    intent: "Test MixedStrategy uses real Stage 1 list data without AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_with_real_stage1_tables
    intent: "Test MixedStrategy uses real Stage 1 table data without AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_strategy_with_real_stage1_data
    intent: "Test ListStrategy uses real Stage 1 list data."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_no_attribute_errors_on_real_structures
    intent: "Ensure no AttributeError when accessing Stage 1 structures correctly."
    v2_component: Error handling
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_stage1_usage_rate_high
    intent: "Verify Stage 1 data usage rate is high when mixed content is present."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_code_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_code_strategy.py
test_count: 46
legacy_imports:
  - markdown_chunker.chunker.strategies.code_strategy.CodeSegment
  - markdown_chunker.chunker.strategies.code_strategy.CodeStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
  - markdown_chunker.parser.types.FencedBlock
v2_applicable: false
removed_functionality: true

tests:
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_sufficient_code
    intent: "Test can_handle with sufficient code ratio and blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_code_ratio
    intent: "Test can_handle with insufficient code ratio."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_code_blocks
    intent: "Test can_handle with insufficient code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_code_ratio
    intent: "Test quality calculation for high code ratio."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_code
    intent: "Test quality calculation for moderate code content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_python
    intent: "Test language detection for Python code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_javascript
    intent: "Test language detection for JavaScript code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_unknown
    intent: "Test language detection for unknown code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_function_names_python
    intent: "Test function name extraction for Python."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_class_names_python
    intent: "Test class name extraction for Python."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_function_names_javascript
    intent: "Test function name extraction for JavaScript."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_line_number
    intent: "Test line number calculation from position."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_code_blocks
    intent: "Test applying strategy to content without code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_code_document
    intent: "Test applying strategy to simple code document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_segment_around_code_blocks
    intent: "Test segmentation around code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_segment_creation
    intent: "Test creating CodeSegment."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_segment_with_metadata
    intent: "Test CodeSegment with function and class names."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_tutorial_chunking
    intent: "Test chunking realistic tutorial with code examples."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_oversize_code_block_handling
    intent: "Test handling of oversized code blocks."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_languages_detection
    intent: "Test handling documents with multiple programming languages."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_sufficient_code
    intent: "Test can_handle with sufficient code ratio and blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_code_ratio
    intent: "Test can_handle with insufficient code ratio."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_code_blocks
    intent: "Test can_handle with insufficient code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_code_ratio
    intent: "Test quality calculation for high code ratio."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_code
    intent: "Test quality calculation for moderate code content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_python
    intent: "Test language detection for Python code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_javascript
    intent: "Test language detection for JavaScript code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_language_unknown
    intent: "Test language detection for unknown code."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_function_names_python
    intent: "Test function name extraction for Python."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_class_names_python
    intent: "Test class name extraction for Python."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_function_names_javascript
    intent: "Test function name extraction for JavaScript."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_line_number
    intent: "Test line number calculation from position."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_code_blocks
    intent: "Test applying strategy to content without code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_code_document
    intent: "Test applying strategy to simple code document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_segment_around_code_blocks
    intent: "Test segmentation around code blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_segment_creation
    intent: "Test creating CodeSegment."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_code_segment_with_metadata
    intent: "Test CodeSegment with function and class names."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_tutorial_chunking
    intent: "Test chunking realistic tutorial with code examples."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_oversize_code_block_handling
    intent: "Test handling of oversized code blocks."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_multiple_languages_detection
    intent: "Test handling documents with multiple programming languages."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_list_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_list_strategy.py
test_count: 78
legacy_imports:
  - markdown_chunker.chunker.strategies.list_strategy.ListGroup
  - markdown_chunker.chunker.strategies.list_strategy.ListItemInfo
  - markdown_chunker.chunker.strategies.list_strategy.ListStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: false
removed_functionality: true

tests:
  - name: test_list_item_creation
    intent: "Test creating a list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_ordered_list_item
    intent: "Test creating an ordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_task_list_item
    intent: "Test creating a task list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_group_creation
    intent: "Test creating a list group."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_list_count
    intent: "Test can_handle with high list count."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_list_ratio
    intent: "Test can_handle with high list ratio."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_lists
    intent: "Test can_handle with insufficient lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_lists
    intent: "Test quality calculation for high list content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_lists
    intent: "Test quality calculation for moderate list content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_unordered
    intent: "Test parsing unordered list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_ordered
    intent: "Test parsing ordered list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_task
    intent: "Test parsing task list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_nested
    intent: "Test parsing nested list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_non_list
    intent: "Test parsing non-list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_task
    intent: "Test determining task list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_ordered
    intent: "Test determining ordered list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_unordered
    intent: "Test determining unordered list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_list_hierarchy_simple
    intent: "Test building simple list hierarchy."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_item_size
    intent: "Test calculating item size including children."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_unordered
    intent: "Test formatting unordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_ordered
    intent: "Test formatting ordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_task
    intent: "Test formatting task list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_nested
    intent: "Test formatting nested list items."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_count_items
    intent: "Test counting items including children."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_max_nesting
    intent: "Test calculating maximum nesting level."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_lists
    intent: "Test applying strategy to content without lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_list
    intent: "Test applying strategy to simple list."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_list_statistics
    intent: "Test getting list statistics."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_list_statistics_empty
    intent: "Test getting statistics for empty chunk list."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_todo_list
    intent: "Test with realistic todo list document."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_list_types
    intent: "Test handling documents with mixed list types."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deeply_nested_lists
    intent: "Test handling deeply nested lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_list_splitting
    intent: "Test splitting large lists that exceed chunk size."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_list_items_real_stage1_data
    intent: "Test extracting list items with real Stage 1 data."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convert_stage1_lists_field_access
    intent: "Test that _convert_stage1_lists uses correct field names."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_pipeline_with_real_stage1_data
    intent: "Test full ListStrategy pipeline with real Stage 1 data."
    v2_component: REMOVED: ListStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_list_item_creation
    intent: "Test creating a list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_ordered_list_item
    intent: "Test creating an ordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_task_list_item
    intent: "Test creating a task list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_group_creation
    intent: "Test creating a list group."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_list_count
    intent: "Test can_handle with high list count."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_list_ratio
    intent: "Test can_handle with high list ratio."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_lists
    intent: "Test can_handle with insufficient lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_lists
    intent: "Test quality calculation for high list content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_lists
    intent: "Test quality calculation for moderate list content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_unordered
    intent: "Test parsing unordered list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_ordered
    intent: "Test parsing ordered list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_task
    intent: "Test parsing task list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_nested
    intent: "Test parsing nested list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_parse_list_line_non_list
    intent: "Test parsing non-list line."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_task
    intent: "Test determining task list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_ordered
    intent: "Test determining ordered list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_determine_list_type_unordered
    intent: "Test determining unordered list type."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_list_hierarchy_simple
    intent: "Test building simple list hierarchy."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_item_size
    intent: "Test calculating item size including children."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_unordered
    intent: "Test formatting unordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_ordered
    intent: "Test formatting ordered list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_task
    intent: "Test formatting task list item."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_format_list_item_nested
    intent: "Test formatting nested list items."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_count_items
    intent: "Test counting items including children."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_max_nesting
    intent: "Test calculating maximum nesting level."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_lists
    intent: "Test applying strategy to content without lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_list
    intent: "Test applying strategy to simple list."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_list_statistics
    intent: "Test getting list statistics."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_list_statistics_empty
    intent: "Test getting statistics for empty chunk list."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_todo_list
    intent: "Test with realistic todo list document."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_list_types
    intent: "Test handling documents with mixed list types."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_deeply_nested_lists
    intent: "Test handling deeply nested lists."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_list_splitting
    intent: "Test splitting large lists that exceed chunk size."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_extract_list_items_real_stage1_data
    intent: "Test extracting list items with real Stage 1 data."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_convert_stage1_lists_field_access
    intent: "Test that _convert_stage1_lists uses correct field names."
    v2_component: REMOVED: ListStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_full_pipeline_with_real_stage1_data
    intent: "Test full ListStrategy pipeline with real Stage 1 data."
    v2_component: REMOVED: ListStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_mixed_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_mixed_strategy.py
test_count: 40
legacy_imports:
  - markdown_chunker.chunker.strategies.mixed_strategy.ContentElement
  - markdown_chunker.chunker.strategies.mixed_strategy.LogicalSection
  - markdown_chunker.chunker.strategies.mixed_strategy.MixedStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: false
removed_functionality: true

tests:
  - name: test_content_element_creation
    intent: "Test creating a content element."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_logical_section_creation
    intent: "Test creating a logical section."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_size
    intent: "Test calculating section size."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_element_types
    intent: "Test getting element types."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_mixed_content
    intent: "Test can_handle with mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_code_dominates
    intent: "Test can_handle when code dominates."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_text
    intent: "Test can_handle with insufficient text."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_mixed
    intent: "Test quality calculation for highly mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_code_dominates
    intent: "Test quality calculation when code dominates."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_mixed_content
    intent: "Test applying strategy to simple mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_group_into_logical_sections
    intent: "Test grouping elements into logical sections."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_has_indivisible_elements
    intent: "Test checking for indivisible elements."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_tutorial_document
    intent: "Test with realistic tutorial document."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_content_with_indivisible_elements
    intent: "Test handling indivisible elements."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_real_stage1_list_and_table_integration
    intent: "Test MixedStrategy with real Stage 1 list and table objects."
    v2_component: REMOVED: MixedStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_list_processing_no_attribute_error
    intent: "Test that list processing doesn't cause AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_processing_no_attribute_error
    intent: "Test that table processing doesn't cause AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_content_element_creation
    intent: "Test creating a content element."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_logical_section_creation
    intent: "Test creating a logical section."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_size
    intent: "Test calculating section size."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_element_types
    intent: "Test getting element types."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_mixed_content
    intent: "Test can_handle with mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_code_dominates
    intent: "Test can_handle when code dominates."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_text
    intent: "Test can_handle with insufficient text."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_mixed
    intent: "Test quality calculation for highly mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_code_dominates
    intent: "Test quality calculation when code dominates."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_mixed_content
    intent: "Test applying strategy to simple mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_group_into_logical_sections
    intent: "Test grouping elements into logical sections."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_has_indivisible_elements
    intent: "Test checking for indivisible elements."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_tutorial_document
    intent: "Test with realistic tutorial document."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_content_with_indivisible_elements
    intent: "Test handling indivisible elements."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_real_stage1_list_and_table_integration
    intent: "Test MixedStrategy with real Stage 1 list and table objects."
    v2_component: REMOVED: MixedStrategy
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_list_processing_no_attribute_error
    intent: "Test that list processing doesn't cause AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_processing_no_attribute_error
    intent: "Test that table processing doesn't cause AttributeError."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_sentences_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_sentences_strategy.py
test_count: 40
legacy_imports:
  - markdown_chunker.chunker.strategies.sentences_strategy.SentencesStrategy
  - markdown_chunker.chunker.strategies.sentences_strategy.count_sentences
  - markdown_chunker.chunker.strategies.sentences_strategy.preview_sentence_splitting
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: false
removed_functionality: true

tests:
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_always_true
    intent: "Test that sentences strategy can always handle any content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_simple_text
    intent: "Test quality calculation for simple text content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_complex_content
    intent: "Test quality calculation for complex structured content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_paragraphs
    intent: "Test paragraph splitting functionality."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_sentences_basic
    intent: "Test basic sentence splitting."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_sentences_edge_cases
    intent: "Test sentence splitting with edge cases."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_single_sentence
    intent: "Test applying strategy to single sentence."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_multiple_sentences_single_chunk
    intent: "Test applying strategy to multiple sentences that fit in one chunk."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_multiple_chunks_needed
    intent: "Test applying strategy when multiple chunks are needed."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_paragraph_boundaries
    intent: "Test that paragraph boundaries are respected."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_very_long_sentence
    intent: "Test handling of very long sentences that exceed chunk size."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_chunk_statistics_empty
    intent: "Test chunk statistics with empty chunk list."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_chunk_statistics_with_chunks
    intent: "Test chunk statistics with actual chunks."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_count_sentences
    intent: "Test sentence counting utility."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_preview_sentence_splitting
    intent: "Test sentence splitting preview utility."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_text_chunking
    intent: "Test chunking realistic text content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_behavior
    intent: "Test that sentences strategy works as a reliable fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_always_true
    intent: "Test that sentences strategy can always handle any content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_simple_text
    intent: "Test quality calculation for simple text content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_complex_content
    intent: "Test quality calculation for complex structured content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_paragraphs
    intent: "Test paragraph splitting functionality."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_sentences_basic
    intent: "Test basic sentence splitting."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_into_sentences_edge_cases
    intent: "Test sentence splitting with edge cases."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_single_sentence
    intent: "Test applying strategy to single sentence."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_multiple_sentences_single_chunk
    intent: "Test applying strategy to multiple sentences that fit in one chunk."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_multiple_chunks_needed
    intent: "Test applying strategy when multiple chunks are needed."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_paragraph_boundaries
    intent: "Test that paragraph boundaries are respected."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_very_long_sentence
    intent: "Test handling of very long sentences that exceed chunk size."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_chunk_statistics_empty
    intent: "Test chunk statistics with empty chunk list."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_chunk_statistics_with_chunks
    intent: "Test chunk statistics with actual chunks."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_count_sentences
    intent: "Test sentence counting utility."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_preview_sentence_splitting
    intent: "Test sentence splitting preview utility."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_text_chunking
    intent: "Test chunking realistic text content."
    v2_component: REMOVED: SentencesStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_behavior
    intent: "Test that sentences strategy works as a reliable fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_structural_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_structural_strategy.py
test_count: 48
legacy_imports:
  - markdown_chunker.chunker.strategies.structural_strategy.HeaderInfo
  - markdown_chunker.chunker.strategies.structural_strategy.Section
  - markdown_chunker.chunker.strategies.structural_strategy.StructuralStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: false
removed_functionality: true

tests:
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_sufficient_headers
    intent: "Test can_handle with sufficient headers and hierarchy."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_headers
    intent: "Test can_handle with insufficient headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_no_hierarchy
    intent: "Test can_handle with no header hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_structure
    intent: "Test quality calculation for highly structured content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_code_heavy
    intent: "Test quality calculation for code-heavy content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_headers_manual_atx
    intent: "Test manual header detection with ATX headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_headers_manual_setext
    intent: "Test manual header detection with Setext headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_hierarchy_simple
    intent: "Test building header hierarchy with simple structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_hierarchy_multiple_roots
    intent: "Test building hierarchy with multiple root headers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_header_path_simple
    intent: "Test building header path for simple hierarchy."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_header_path_root
    intent: "Test building header path for root header."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_sections
    intent: "Test creating sections from headers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_headers
    intent: "Test applying strategy to content without headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_structure
    intent: "Test applying strategy to simple structured content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_large_section_splitting
    intent: "Test that large sections are split appropriately."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_combine_small_chunks
    intent: "Test combining small chunks to meet minimum size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_header_info_creation
    intent: "Test creating HeaderInfo."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_header_info_with_parent
    intent: "Test HeaderInfo with parent relationship."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_section_creation
    intent: "Test creating Section."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_documentation_chunking
    intent: "Test chunking realistic documentation structure."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_to_manual_detection
    intent: "Test fallback to manual header detection when Stage 1 fails."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_sufficient_headers
    intent: "Test can_handle with sufficient headers and hierarchy."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_headers
    intent: "Test can_handle with insufficient headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_no_hierarchy
    intent: "Test can_handle with no header hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_structure
    intent: "Test quality calculation for highly structured content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_code_heavy
    intent: "Test quality calculation for code-heavy content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_headers_manual_atx
    intent: "Test manual header detection with ATX headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_headers_manual_setext
    intent: "Test manual header detection with Setext headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_hierarchy_simple
    intent: "Test building header hierarchy with simple structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_hierarchy_multiple_roots
    intent: "Test building hierarchy with multiple root headers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_header_path_simple
    intent: "Test building header path for simple hierarchy."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_build_header_path_root
    intent: "Test building header path for root header."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_sections
    intent: "Test creating sections from headers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_headers
    intent: "Test applying strategy to content without headers."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_structure
    intent: "Test applying strategy to simple structured content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_large_section_splitting
    intent: "Test that large sections are split appropriately."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_combine_small_chunks
    intent: "Test combining small chunks to meet minimum size."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_header_info_creation
    intent: "Test creating HeaderInfo."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_header_info_with_parent
    intent: "Test HeaderInfo with parent relationship."
    v2_component: ContentAnalysis.headers
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_section_creation
    intent: "Test creating Section."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_documentation_chunking
    intent: "Test chunking realistic documentation structure."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_to_manual_detection
    intent: "Test fallback to manual header detection when Stage 1 fails."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategies/test_table_strategy.py

```yaml
test_file: tests/chunker/test_strategies/test_table_strategy.py
test_count: 60
legacy_imports:
  - markdown_chunker.chunker.strategies.table_strategy.TableInfo
  - markdown_chunker.chunker.strategies.table_strategy.TableRowGroup
  - markdown_chunker.chunker.strategies.table_strategy.TableStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: false
removed_functionality: true

tests:
  - name: test_table_info_creation
    intent: "Test creating a table info object."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_full_content
    intent: "Test getting full table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_size
    intent: "Test calculating table size."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_row_group_creation
    intent: "Test creating a table row group."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_table_count
    intent: "Test can_handle with high table count."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_table_ratio
    intent: "Test can_handle with high table ratio."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_tables
    intent: "Test can_handle with insufficient tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_tables
    intent: "Test quality calculation for high table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_tables
    intent: "Test quality calculation for moderate table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_header
    intent: "Test table header detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_separator
    intent: "Test table separator detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_row
    intent: "Test table row detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_simple
    intent: "Test detecting a simple table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_multiple
    intent: "Test detecting multiple tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_no_data_rows
    intent: "Test that tables without data rows are ignored."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_table_rows
    intent: "Test splitting table rows into groups."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_tables
    intent: "Test applying strategy to content without tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_table
    intent: "Test applying strategy to simple table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_table_chunk
    intent: "Test creating a chunk from a table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_table_group_chunk
    intent: "Test creating a chunk from a table row group."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_table_statistics
    intent: "Test getting table statistics."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_table_statistics_empty
    intent: "Test getting statistics for empty chunk list."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_api_documentation
    intent: "Test with realistic API documentation table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_table_splitting
    intent: "Test splitting a large table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_content_with_tables
    intent: "Test handling mixed content with tables and text."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_wide_table_handling
    intent: "Test handling wide tables that might exceed chunk size."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_with_alignment
    intent: "Test handling tables with column alignment."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_info_creation
    intent: "Test creating a table info object."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_full_content
    intent: "Test getting full table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_size
    intent: "Test calculating table size."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_row_group_creation
    intent: "Test creating a table row group."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_properties
    intent: "Test basic strategy properties."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_table_count
    intent: "Test can_handle with high table count."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_high_table_ratio
    intent: "Test can_handle with high table ratio."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_can_handle_insufficient_tables
    intent: "Test can_handle with insufficient tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_high_tables
    intent: "Test quality calculation for high table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_calculate_quality_moderate_tables
    intent: "Test quality calculation for moderate table content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_header
    intent: "Test table header detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_separator
    intent: "Test table separator detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_is_table_row
    intent: "Test table row detection."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_simple
    intent: "Test detecting a simple table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_multiple
    intent: "Test detecting multiple tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_detect_tables_no_data_rows
    intent: "Test that tables without data rows are ignored."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_split_table_rows
    intent: "Test splitting table rows into groups."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_empty_content
    intent: "Test applying strategy to empty content."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_no_tables
    intent: "Test applying strategy to content without tables."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_apply_simple_table
    intent: "Test applying strategy to simple table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_table_chunk
    intent: "Test creating a chunk from a table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_create_table_group_chunk
    intent: "Test creating a chunk from a table row group."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_selection_reason
    intent: "Test selection reason generation."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_table_statistics
    intent: "Test getting table statistics."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_get_table_statistics_empty
    intent: "Test getting statistics for empty chunk list."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_realistic_api_documentation
    intent: "Test with realistic API documentation table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_large_table_splitting
    intent: "Test splitting a large table."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_content_with_tables
    intent: "Test handling mixed content with tables and text."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_wide_table_handling
    intent: "Test handling wide tables that might exceed chunk size."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_table_with_alignment
    intent: "Test handling tables with column alignment."
    v2_component: REMOVED: TableStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_strategy_completeness_properties.py

```yaml
test_file: tests/chunker/test_strategy_completeness_properties.py
test_count: 14
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_chunker_completeness
    intent: "**Property 6: Strategy Completeness**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_plain_text_completeness
    intent: "Property: Chunker should handle plain text."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunker should handle plain text."
  - name: test_property_nested_document_completeness
    intent: "Property: Strategies should handle nested documents."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: strategies should handle nested documents."
  - name: test_property_explicit_strategy_completeness
    intent: "Property: Explicitly requested strategies should produce chunks."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: explicitly requested strategies should produce chunks."
  - name: test_property_single_paragraph_completeness
    intent: "Property: Single paragraph documents should be handled."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: single paragraph documents should be handled."
  - name: test_property_headers_only_completeness
    intent: "Property: Documents with only headers should be handled."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: documents with only headers should be handled."
  - name: test_property_completeness_with_size_constraints
    intent: "Property: Strategies should respect size constraints."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: strategies should respect size constraints."
  - name: test_property_chunker_completeness
    intent: "**Property 6: Strategy Completeness**"
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_plain_text_completeness
    intent: "Property: Chunker should handle plain text."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunker should handle plain text."
  - name: test_property_nested_document_completeness
    intent: "Property: Strategies should handle nested documents."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: strategies should handle nested documents."
  - name: test_property_explicit_strategy_completeness
    intent: "Property: Explicitly requested strategies should produce chunks."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: explicitly requested strategies should produce chunks."
  - name: test_property_single_paragraph_completeness
    intent: "Property: Single paragraph documents should be handled."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: single paragraph documents should be handled."
  - name: test_property_headers_only_completeness
    intent: "Property: Documents with only headers should be handled."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: documents with only headers should be handled."
  - name: test_property_completeness_with_size_constraints
    intent: "Property: Strategies should respect size constraints."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: strategies should respect size constraints."
```

### tests/chunker/test_strategy_error_handling.py

```yaml
test_file: tests/chunker/test_strategy_error_handling.py
test_count: 24
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.selector.StrategySelectionError
v2_applicable: true
removed_functionality: false

tests:
  - name: test_invalid_strategy_name_raises_error
    intent: "Test that invalid strategy name raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_message_includes_available_strategies
    intent: "Test that error message includes list of available strategies."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_strategy_name_does_not_raise_error
    intent: "Test that valid strategy names don't raise StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_validation_before_try_block
    intent: "Test that strategy validation happens before try block."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_error_not_caught_by_general_except
    intent: "Test that StrategySelectionError is not caught by general exception handler."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_other_exceptions_still_caught
    intent: "Test that other exceptions are still caught and trigger emergency fallback."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_automatic_strategy_selection_errors_handled
    intent: "Test that errors in automatic strategy selection are handled properly."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_propagates_strategy_error
    intent: "Test that chunk_with_analysis also propagates StrategySelectionError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_available_strategies_returns_correct_list
    intent: "Test that get_available_strategies returns the correct strategy names."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_case_sensitivity_in_strategy_names
    intent: "Test that strategy names are case sensitive."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_strategy_name
    intent: "Test that empty strategy name raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_none_strategy_uses_automatic_selection
    intent: "Test that None strategy uses automatic selection (no error)."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_strategy_name_raises_error
    intent: "Test that invalid strategy name raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_message_includes_available_strategies
    intent: "Test that error message includes list of available strategies."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_strategy_name_does_not_raise_error
    intent: "Test that valid strategy names don't raise StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_validation_before_try_block
    intent: "Test that strategy validation happens before try block."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_error_not_caught_by_general_except
    intent: "Test that StrategySelectionError is not caught by general exception handler."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_other_exceptions_still_caught
    intent: "Test that other exceptions are still caught and trigger emergency fallback."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_automatic_strategy_selection_errors_handled
    intent: "Test that errors in automatic strategy selection are handled properly."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_propagates_strategy_error
    intent: "Test that chunk_with_analysis also propagates StrategySelectionError."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_available_strategies_returns_correct_list
    intent: "Test that get_available_strategies returns the correct strategy names."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_case_sensitivity_in_strategy_names
    intent: "Test that strategy names are case sensitive."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_strategy_name
    intent: "Test that empty strategy name raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_none_strategy_uses_automatic_selection
    intent: "Test that None strategy uses automatic selection (no error)."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_strategy_selector.py

```yaml
test_file: tests/chunker/test_strategy_selector.py
test_count: 46
legacy_imports:
  - markdown_chunker.chunker.selector.StrategySelectionError
  - markdown_chunker.chunker.selector.StrategySelector
  - markdown_chunker.chunker.strategies.base.BaseStrategy
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.parser.types.ContentAnalysis
v2_applicable: true
removed_functionality: false

tests:
  - name: test_selector_creation_strict_mode
    intent: "Test creating selector in strict mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_selector_creation_weighted_mode
    intent: "Test creating selector in weighted mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_selector_invalid_mode
    intent: "Test creating selector with invalid mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strict_selection_first_applicable
    intent: "Test strict mode selects first applicable strategy by priority."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strict_selection_no_applicable
    intent: "Test strict mode uses emergency fallback when no strategy can handle."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_selection_best_score
    intent: "Test weighted mode selects strategy with best combined score."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_selection_no_applicable
    intent: "Test weighted mode raises error when no strategy can handle."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_applicable_strategies
    intent: "Test getting all applicable strategies with scores."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_metrics
    intent: "Test getting detailed metrics for all strategies."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all strategies."
  - name: test_explain_selection
    intent: "Test selection explanation functionality."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_valid
    intent: "Test strategy validation with valid configuration."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_no_strategies
    intent: "Test validation with no strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_duplicate_priorities
    intent: "Test validation with duplicate priorities."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_no_fallback
    intent: "Test validation without fallback strategy."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_duplicate_names
    intent: "Test validation with duplicate strategy names."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_by_name
    intent: "Test getting strategy by name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_strategy
    intent: "Test adding strategy to selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_strategy_duplicate_name
    intent: "Test adding strategy with duplicate name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_remove_strategy
    intent: "Test removing strategy from selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_names
    intent: "Test getting list of strategy names."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_string_representations
    intent: "Test string representations of selector."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_strategy_selection
    intent: "Test strategy selection with realistic scenarios."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_vs_strict_comparison
    intent: "Test difference between weighted and strict selection."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_selector_creation_strict_mode
    intent: "Test creating selector in strict mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_selector_creation_weighted_mode
    intent: "Test creating selector in weighted mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_selector_invalid_mode
    intent: "Test creating selector with invalid mode."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strict_selection_first_applicable
    intent: "Test strict mode selects first applicable strategy by priority."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strict_selection_no_applicable
    intent: "Test strict mode uses emergency fallback when no strategy can handle."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_selection_best_score
    intent: "Test weighted mode selects strategy with best combined score."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_selection_no_applicable
    intent: "Test weighted mode raises error when no strategy can handle."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_applicable_strategies
    intent: "Test getting all applicable strategies with scores."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_metrics
    intent: "Test getting detailed metrics for all strategies."
    v2_component: Strategy (base)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all strategies."
  - name: test_explain_selection
    intent: "Test selection explanation functionality."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_valid
    intent: "Test strategy validation with valid configuration."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_no_strategies
    intent: "Test validation with no strategies."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_duplicate_priorities
    intent: "Test validation with duplicate priorities."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_no_fallback
    intent: "Test validation without fallback strategy."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_strategies_duplicate_names
    intent: "Test validation with duplicate strategy names."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_by_name
    intent: "Test getting strategy by name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_strategy
    intent: "Test adding strategy to selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_add_strategy_duplicate_name
    intent: "Test adding strategy with duplicate name."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_remove_strategy
    intent: "Test removing strategy from selector."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_get_strategy_names
    intent: "Test getting list of strategy names."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_string_representations
    intent: "Test string representations of selector."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_realistic_strategy_selection
    intent: "Test strategy selection with realistic scenarios."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_weighted_vs_strict_comparison
    intent: "Test difference between weighted and strict selection."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_strategy_selector_properties.py

```yaml
test_file: tests/chunker/test_strategy_selector_properties.py
test_count: 1
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.selector.StrategySelector
  - markdown_chunker.chunker.strategies.CodeStrategy
  - markdown_chunker.chunker.strategies.ListStrategy
  - markdown_chunker.chunker.strategies.MixedStrategy
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_selection_is_deterministic
    intent: "Property 5a: Strategy selection is deterministic."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any document, selecting strategy twice should give same result."
```

### tests/chunker/test_structural_strategy_initialization.py

```yaml
test_file: tests/chunker/test_structural_strategy_initialization.py
test_count: 20
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.strategies.sentences_strategy.SentencesStrategy
  - markdown_chunker.chunker.strategies.structural_strategy.StructuralStrategy
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_fallback_strategy_is_set_in_init
    intent: "Test that fallback strategies are set in FallbackManager during initialization."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_strategy_types_are_correct
    intent: "Test that the fallback strategies are of correct types."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_manager_has_3_level_chain
    intent: "Test that FallbackManager has 3-level fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_chain_execution_through_levels
    intent: "Test that fallback chain can execute through all levels."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_strategy_used_in_fallback
    intent: "Test that fallback strategy is actually used in fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_initialization_with_custom_config
    intent: "Test that fallback manager initialization works with custom config."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_structural_strategy_is_available
    intent: "Test that structural strategy is available in fallback chain."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_sentences_strategy_is_final_fallback
    intent: "Test that sentences strategy is the final fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_manager_config_consistency
    intent: "Test that FallbackManager uses the same config as chunker."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_all_strategies_fail_returns_empty
    intent: "Test that when all strategies fail, empty result is returned."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_strategy_is_set_in_init
    intent: "Test that fallback strategies are set in FallbackManager during initialization."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_strategy_types_are_correct
    intent: "Test that the fallback strategies are of correct types."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_manager_has_3_level_chain
    intent: "Test that FallbackManager has 3-level fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_chain_execution_through_levels
    intent: "Test that fallback chain can execute through all levels."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_strategy_used_in_fallback
    intent: "Test that fallback strategy is actually used in fallback chain."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_initialization_with_custom_config
    intent: "Test that fallback manager initialization works with custom config."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_structural_strategy_is_available
    intent: "Test that structural strategy is available in fallback chain."
    v2_component: StructuralStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_sentences_strategy_is_final_fallback
    intent: "Test that sentences strategy is the final fallback."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_manager_config_consistency
    intent: "Test that FallbackManager uses the same config as chunker."
    v2_component: FallbackStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_all_strategies_fail_returns_empty
    intent: "Test that when all strategies fail, empty result is returned."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/chunker/test_structural_strategy_properties.py

```yaml
test_file: tests/chunker/test_structural_strategy_properties.py
test_count: 14
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_chunk_boundaries_at_headers
    intent: "**Property 3a: Chunk Boundaries at Headers**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunks should start at header boundaries
(except for the first chunk which may include preamble)."
  - name: test_property_no_data_loss
    intent: "**Property 3b: No Data Loss**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, all content should appear in chunks
(allowing for overlap)."
  - name: test_property_monotonic_line_numbers
    intent: "**Property 3c: Monotonic Line Numbers**"
    v2_component: ContentAnalysis (line positions)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunk line numbers should be monotonically
increasing (start_line of chunk n+1 >= end_line of chunk n)."
  - name: test_property_header_metadata_present
    intent: "**Property 3d: Header Metadata Present**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown processed by structural strategy,
chunks should have header-related metadata."
  - name: test_property_respects_size_limits
    intent: "**Property 3e: Respects Size Limits**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunks should respect max_chunk_size
(unless a single section is indivisible and larger)."
  - name: test_property_header_path_consistency
    intent: "**Property 3f: Header Path Consistency**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, header paths should be consistent
with document hierarchy."
  - name: test_property_subsection_splitting
    intent: "**Property 3g: Subsection Splitting**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_chunk_boundaries_at_headers
    intent: "**Property 3a: Chunk Boundaries at Headers**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunks should start at header boundaries
(except for the first chunk which may include preamble)."
  - name: test_property_no_data_loss
    intent: "**Property 3b: No Data Loss**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, all content should appear in chunks
(allowing for overlap)."
  - name: test_property_monotonic_line_numbers
    intent: "**Property 3c: Monotonic Line Numbers**"
    v2_component: ContentAnalysis (line positions)
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunk line numbers should be monotonically
increasing (start_line of chunk n+1 >= end_line of chunk n)."
  - name: test_property_header_metadata_present
    intent: "**Property 3d: Header Metadata Present**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown processed by structural strategy,
chunks should have header-related metadata."
  - name: test_property_respects_size_limits
    intent: "**Property 3e: Respects Size Limits**"
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, chunks should respect max_chunk_size
(unless a single section is indivisible and larger)."
  - name: test_property_header_path_consistency
    intent: "**Property 3f: Header Path Consistency**"
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any structured markdown, header paths should be consistent
with document hierarchy."
  - name: test_property_subsection_splitting
    intent: "**Property 3g: Subsection Splitting**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_subsection_splitting.py

```yaml
test_file: tests/chunker/test_subsection_splitting.py
test_count: 24
legacy_imports:
  - markdown_chunker.chunker.strategies.structural_strategy.HeaderInfo
  - markdown_chunker.chunker.strategies.structural_strategy.Section
  - markdown_chunker.chunker.strategies.structural_strategy.StructuralStrategy
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_split_by_subsections_small_subsections
    intent: "Test splitting section with small subsections."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_large_subsection
    intent: "Test splitting section with large subsection that needs recursive split."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_nested_hierarchy
    intent: "Test splitting with nested subsection hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_empty_subsections
    intent: "Test handling empty subsections."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_simple
    intent: "Test splitting section by paragraphs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_respects_size_limit
    intent: "Test that paragraph splitting respects size limits."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_empty_paragraphs
    intent: "Test handling empty paragraphs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_empty_current
    intent: "Test building content with empty current."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_with_current
    intent: "Test building content with existing current."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_preserves_formatting
    intent: "Test that content building preserves paragraph separation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_full_pipeline_with_subsections
    intent: "Test full chunking pipeline with subsections."
    v2_component: MarkdownChunker
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_subsection_metadata_preserved
    intent: "Test that subsection metadata is preserved."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_small_subsections
    intent: "Test splitting section with small subsections."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_large_subsection
    intent: "Test splitting section with large subsection that needs recursive split."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_nested_hierarchy
    intent: "Test splitting with nested subsection hierarchy."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_subsections_empty_subsections
    intent: "Test handling empty subsections."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_simple
    intent: "Test splitting section by paragraphs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_respects_size_limit
    intent: "Test that paragraph splitting respects size limits."
    v2_component: ChunkConfig.max_chunk_size / min_chunk_size
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_split_by_paragraphs_empty_paragraphs
    intent: "Test handling empty paragraphs."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_empty_current
    intent: "Test building content with empty current."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_with_current
    intent: "Test building content with existing current."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_build_potential_content_preserves_formatting
    intent: "Test that content building preserves paragraph separation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_full_pipeline_with_subsections
    intent: "Test full chunking pipeline with subsections."
    v2_component: MarkdownChunker
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_subsection_metadata_preserved
    intent: "Test that subsection metadata is preserved."
    v2_component: Chunk.metadata
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_subsection_splitting_properties.py

```yaml
test_file: tests/chunker/test_subsection_splitting_properties.py
test_count: 10
legacy_imports:
  - markdown_chunker.chunker.strategies.structural_strategy.StructuralStrategy
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_subsection_hierarchy_preservation
    intent: "**Property 3: Subsection Hierarchy Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_multiple_sections_preserved
    intent: "Property: Multiple sections should all be preserved in output."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of sections, all section content should appear in chunks."
  - name: test_property_header_levels_preserved
    intent: "Property: Header levels should be correctly identified in metadata."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header level (1-6), chunks containing that header should
have correct header_level in metadata."
  - name: test_property_large_content_split
    intent: "Property: Large content should be split into multiple chunks."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any large content block, it should be split appropriately."
  - name: test_property_empty_sections_handled
    intent: "Property: Empty sections should be handled gracefully."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of section titles (even with empty content),
chunking should not fail."
  - name: test_property_subsection_hierarchy_preservation
    intent: "**Property 3: Subsection Hierarchy Preservation**"
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_property_multiple_sections_preserved
    intent: "Property: Multiple sections should all be preserved in output."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of sections, all section content should appear in chunks."
  - name: test_property_header_levels_preserved
    intent: "Property: Header levels should be correctly identified in metadata."
    v2_component: ContentAnalysis.headers
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any header level (1-6), chunks containing that header should
have correct header_level in metadata."
  - name: test_property_large_content_split
    intent: "Property: Large content should be split into multiple chunks."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any large content block, it should be split appropriately."
  - name: test_property_empty_sections_handled
    intent: "Property: Empty sections should be handled gracefully."
    v2_component: MarkdownChunker
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any list of section titles (even with empty content),
chunking should not fail."
```

### tests/chunker/test_table_strategy_properties.py

```yaml
test_file: tests/chunker/test_table_strategy_properties.py
test_count: 12
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: false
removed_functionality: true

tests:
  - name: test_property_tables_never_split
    intent: "**Property 12a: Tables Never Split**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, each complete table should appear
in exactly one chunk (tables are atomic)."
  - name: test_property_table_headers_preserved
    intent: "**Property 12b: Table Headers Preserved**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, table headers should be preserved
in all chunks containing table data."
  - name: test_property_table_structure_maintained
    intent: "**Property 12c: Table Structure Maintained**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, the table structure (columns, rows)
should be maintained in chunks."
  - name: test_property_large_tables_split_by_rows
    intent: "**Property 12d: Large Tables Split by Rows**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with large tables, tables should be split by rows
(not mid-row) with headers duplicated in each chunk."
  - name: test_property_wide_tables_allowed_oversize
    intent: "**Property 12e: Wide Tables Allowed Oversize**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with wide tables (single row exceeds max_chunk_size),
tables should be allowed to exceed size limit (marked as oversize)."
  - name: test_property_table_metadata_present
    intent: "**Property 12f: Table Metadata Present**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables processed by table strategy,
chunks containing tables should have appropriate metadata."
  - name: test_property_tables_never_split
    intent: "**Property 12a: Tables Never Split**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, each complete table should appear
in exactly one chunk (tables are atomic)."
  - name: test_property_table_headers_preserved
    intent: "**Property 12b: Table Headers Preserved**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, table headers should be preserved
in all chunks containing table data."
  - name: test_property_table_structure_maintained
    intent: "**Property 12c: Table Structure Maintained**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables, the table structure (columns, rows)
should be maintained in chunks."
  - name: test_property_large_tables_split_by_rows
    intent: "**Property 12d: Large Tables Split by Rows**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with large tables, tables should be split by rows
(not mid-row) with headers duplicated in each chunk."
  - name: test_property_wide_tables_allowed_oversize
    intent: "**Property 12e: Wide Tables Allowed Oversize**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with wide tables (single row exceeds max_chunk_size),
tables should be allowed to exceed size limit (marked as oversize)."
  - name: test_property_table_metadata_present
    intent: "**Property 12f: Table Metadata Present**"
    v2_component: REMOVED: TableStrategy
    test_type: property
    v2_applicable: false
    removed_functionality: true
    property: "for any markdown with tables processed by table strategy,
chunks containing tables should have appropriate metadata."
```

### tests/chunker/test_text_normalizer.py

```yaml
test_file: tests/chunker/test_text_normalizer.py
test_count: 78
legacy_imports:
  - markdown_chunker.chunker.text_normalizer.ensure_list_formatting
  - markdown_chunker.chunker.text_normalizer.ensure_space_between_tokens
  - markdown_chunker.chunker.text_normalizer.join_content_blocks
  - markdown_chunker.chunker.text_normalizer.normalize_list_content
  - markdown_chunker.chunker.text_normalizer.normalize_whitespace
v2_applicable: true
removed_functionality: false

tests:
  - name: test_single_newline_to_space
    intent: "Single newline should be replaced with space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_double_newline_preserved
    intent: "Double newlines should be preserved as paragraph breaks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_concatenated_words_fixed
    intent: "Adjacent words should have space inserted."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_spaces_normalized
    intent: "Multiple spaces should be collapsed to single space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_punctuation_spacing
    intent: "Punctuation should be followed by space before next word."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input
    intent: "Empty input should return empty output."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_intentional_formatting
    intent: "Should preserve intentional paragraph structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_joins_with_default_separator
    intent: "Should join blocks with double newline by default."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_joins_with_custom_separator
    intent: "Should use custom separator when provided."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filters_empty_blocks
    intent: "Should filter out empty blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_list
    intent: "Empty list should return empty string."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_block
    intent: "Single block should be returned trimmed."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validates_no_token_adjacency
    intent: "Should validate proper whitespace between tokens."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unordered_list_normalized
    intent: "Unordered list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_ordered_list_normalized
    intent: "Ordered list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_list_normalized
    intent: "Task list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_indentation
    intent: "Should preserve indentation for nested lists."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_non_list_lines
    intent: "Should preserve lines that aren't list items."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_spacing
    intent: "Should return True for properly spaced text."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_sentence_concatenation
    intent: "Should detect period followed by capital without space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_colon_concatenation
    intent: "Should detect colon followed by letter without space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_string_valid
    intent: "Empty string should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_none_input_valid
    intent: "None input should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fixes_ordered_list_spacing
    intent: "Should add space after ordered list markers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fixes_unordered_list_spacing
    intent: "Should add space after unordered list markers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handles_multiple_items
    intent: "Should handle multiple list items."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_from_start
    intent: "Should truncate from end, keeping start."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_from_end
    intent: "Should truncate from start, keeping end."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_truncation_needed
    intent: "Should return original if under limit."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_word_boundary_found
    intent: "Should return truncated text if no boundary found."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_text
    intent: "Should return True for text without fragments."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_fragment_at_start
    intent: "Should detect fragment at start."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_allows_valid_lowercase_starts
    intent: "Should allow valid words that start with lowercase."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_string_valid
    intent: "Empty string should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_short_string_valid
    intent: "Very short strings should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_1_scenario
    intent: "Test BLOCK-1: Text concatenation without spaces."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_russian_text_colon_spacing
    intent: "Test Russian text with colon (BLOCK-1)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_formatting_preservation
    intent: "Test CRIT-2: List structure preservation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_joining
    intent: "Test joining multiple blocks without concatenation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_newline_to_space
    intent: "Single newline should be replaced with space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_double_newline_preserved
    intent: "Double newlines should be preserved as paragraph breaks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_concatenated_words_fixed
    intent: "Adjacent words should have space inserted."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_spaces_normalized
    intent: "Multiple spaces should be collapsed to single space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_punctuation_spacing
    intent: "Punctuation should be followed by space before next word."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input
    intent: "Empty input should return empty output."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_intentional_formatting
    intent: "Should preserve intentional paragraph structure."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_joins_with_default_separator
    intent: "Should join blocks with double newline by default."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_joins_with_custom_separator
    intent: "Should use custom separator when provided."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_filters_empty_blocks
    intent: "Should filter out empty blocks."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_list
    intent: "Empty list should return empty string."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_block
    intent: "Single block should be returned trimmed."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validates_no_token_adjacency
    intent: "Should validate proper whitespace between tokens."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unordered_list_normalized
    intent: "Unordered list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_ordered_list_normalized
    intent: "Ordered list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_task_list_normalized
    intent: "Task list markers should have single space after."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_indentation
    intent: "Should preserve indentation for nested lists."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_preserves_non_list_lines
    intent: "Should preserve lines that aren't list items."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_spacing
    intent: "Should return True for properly spaced text."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_sentence_concatenation
    intent: "Should detect period followed by capital without space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_colon_concatenation
    intent: "Should detect colon followed by letter without space."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_string_valid
    intent: "Empty string should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_none_input_valid
    intent: "None input should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fixes_ordered_list_spacing
    intent: "Should add space after ordered list markers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fixes_unordered_list_spacing
    intent: "Should add space after unordered list markers."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handles_multiple_items
    intent: "Should handle multiple list items."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_from_start
    intent: "Should truncate from end, keeping start."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_truncate_from_end
    intent: "Should truncate from start, keeping end."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_truncation_needed
    intent: "Should return original if under limit."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_word_boundary_found
    intent: "Should return truncated text if no boundary found."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_valid_text
    intent: "Should return True for text without fragments."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_detects_fragment_at_start
    intent: "Should detect fragment at start."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_allows_valid_lowercase_starts
    intent: "Should allow valid words that start with lowercase."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_string_valid
    intent: "Empty string should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_short_string_valid
    intent: "Very short strings should be considered valid."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_1_scenario
    intent: "Test BLOCK-1: Text concatenation without spaces."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_russian_text_colon_spacing
    intent: "Test Russian text with colon (BLOCK-1)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_formatting_preservation
    intent: "Test CRIT-2: List structure preservation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_blocks_joining
    intent: "Test joining multiple blocks without concatenation."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_types.py

```yaml
test_file: tests/chunker/test_types.py
test_count: 38
legacy_imports:
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkConfig
  - markdown_chunker.chunker.types.ChunkingResult
  - markdown_chunker.chunker.types.ContentType
  - markdown_chunker.chunker.types.StrategyMetrics
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunk_creation_valid
    intent: "Test creating a valid chunk."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_creation_minimal
    intent: "Test creating chunk with minimal required fields."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_invalid_line_numbers
    intent: "Test chunk creation with invalid line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_empty_content
    intent: "Test chunk creation with empty or whitespace content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_metadata_operations
    intent: "Test chunk metadata operations."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_properties
    intent: "Test chunk computed properties."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_creation
    intent: "Test creating a chunking result."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_statistics
    intent: "Test chunking result statistics calculation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_empty_chunks
    intent: "Test chunking result with no chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_error_handling
    intent: "Test chunking result error and warning handling."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_summary
    intent: "Test chunking result summary generation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_default_creation
    intent: "Test creating default configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_factory_methods
    intent: "Test configuration factory methods."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_validation
    intent: "Test configuration validation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_effective_overlap_size
    intent: "Test effective overlap size calculation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_metrics_creation
    intent: "Test creating strategy metrics."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_metrics_validation
    intent: "Test strategy metrics validation."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_type_enum
    intent: "Test ContentType enum."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_type_enum
    intent: "Test StrategyType enum."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_creation_valid
    intent: "Test creating a valid chunk."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_creation_minimal
    intent: "Test creating chunk with minimal required fields."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_invalid_line_numbers
    intent: "Test chunk creation with invalid line numbers."
    v2_component: ContentAnalysis (line positions)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_empty_content
    intent: "Test chunk creation with empty or whitespace content."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_metadata_operations
    intent: "Test chunk metadata operations."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_properties
    intent: "Test chunk computed properties."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_creation
    intent: "Test creating a chunking result."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_statistics
    intent: "Test chunking result statistics calculation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_empty_chunks
    intent: "Test chunking result with no chunks."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_error_handling
    intent: "Test chunking result error and warning handling."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_result_summary
    intent: "Test chunking result summary generation."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_default_creation
    intent: "Test creating default configuration."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_factory_methods
    intent: "Test configuration factory methods."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_validation
    intent: "Test configuration validation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_effective_overlap_size
    intent: "Test effective overlap size calculation."
    v2_component: ChunkConfig
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_metrics_creation
    intent: "Test creating strategy metrics."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_metrics_validation
    intent: "Test strategy metrics validation."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_content_type_enum
    intent: "Test ContentType enum."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_type_enum
    intent: "Test StrategyType enum."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/chunker/test_unified_api.py

```yaml
test_file: tests/chunker/test_unified_api.py
test_count: 58
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.chunker.types.Chunk
  - markdown_chunker.chunker.types.ChunkingResult
  - markdown_chunker.chunker.selector.StrategySelectionError
  - markdown_chunker.chunker.selector.StrategySelectionError
v2_applicable: true
removed_functionality: false

tests:
  - name: test_chunk_default_returns_list
    intent: "Test that chunk() with defaults returns List[Chunk]."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_returns_result
    intent: "Test that chunk(include_analysis=True) returns ChunkingResult."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_dict_format_returns_dict
    intent: "Test that chunk(return_format='dict') returns dict."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_dict_with_analysis_returns_full_dict
    intent: "Test that chunk(include_analysis=True, return_format='dict') returns full dict."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_parameter_works
    intent: "Test that strategy parameter is respected."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_strategy_raises_error
    intent: "Test that invalid strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_strategy_raises_error
    intent: "Test that empty strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_text_returns_empty_result
    intent: "Test that empty text returns empty result (backward compatibility)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_return_format_raises_error
    intent: "Test that invalid return_format raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_include_analysis_type_raises_error
    intent: "Test that non-boolean include_analysis raises TypeError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_md_text_type_raises_error
    intent: "Test that non-string md_text raises TypeError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_default_behavior_matches_old_chunk
    intent: "Test that chunk() default behavior matches old chunk()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_include_analysis_matches_old_chunk_with_analysis
    intent: "Test that chunk(include_analysis=True) matches old chunk_with_analysis()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_matches_old_chunk_simple
    intent: "Test that chunk(return_format='dict') matches old chunk_simple()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_objects_format_without_analysis
    intent: "Test objects format without analysis returns List[Chunk]."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_objects_format_with_analysis
    intent: "Test objects format with analysis returns ChunkingResult."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_without_analysis
    intent: "Test dict format without analysis returns simplified dict."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_with_analysis
    intent: "Test dict format with analysis returns full dict."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test unified API with code-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test unified API with list-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_document
    intent: "Test unified API with table document."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_document
    intent: "Test unified API with mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_small_document
    intent: "Test with very small document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_whitespace_between_content
    intent: "Test document with lots of whitespace."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test with unicode content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_parameters_combined
    intent: "Test with all parameters specified."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_emits_warning
    intent: "Test that chunk_with_analysis() emits deprecation warning."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_emits_warning
    intent: "Test that chunk_simple() emits deprecation warning."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deprecated_methods_still_functional
    intent: "Test that deprecated methods still produce correct results."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_default_returns_list
    intent: "Test that chunk() with defaults returns List[Chunk]."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_returns_result
    intent: "Test that chunk(include_analysis=True) returns ChunkingResult."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_dict_format_returns_dict
    intent: "Test that chunk(return_format='dict') returns dict."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_dict_with_analysis_returns_full_dict
    intent: "Test that chunk(include_analysis=True, return_format='dict') returns full dict."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_parameter_works
    intent: "Test that strategy parameter is respected."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_strategy_raises_error
    intent: "Test that invalid strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_strategy_raises_error
    intent: "Test that empty strategy raises StrategySelectionError."
    v2_component: Strategy (base)
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_text_returns_empty_result
    intent: "Test that empty text returns empty result (backward compatibility)."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_return_format_raises_error
    intent: "Test that invalid return_format raises ValueError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_include_analysis_type_raises_error
    intent: "Test that non-boolean include_analysis raises TypeError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_invalid_md_text_type_raises_error
    intent: "Test that non-string md_text raises TypeError."
    v2_component: Error handling
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_default_behavior_matches_old_chunk
    intent: "Test that chunk() default behavior matches old chunk()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_include_analysis_matches_old_chunk_with_analysis
    intent: "Test that chunk(include_analysis=True) matches old chunk_with_analysis()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_matches_old_chunk_simple
    intent: "Test that chunk(return_format='dict') matches old chunk_simple()."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_objects_format_without_analysis
    intent: "Test objects format without analysis returns List[Chunk]."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_objects_format_with_analysis
    intent: "Test objects format with analysis returns ChunkingResult."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_without_analysis
    intent: "Test dict format without analysis returns simplified dict."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_dict_format_with_analysis
    intent: "Test dict format with analysis returns full dict."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test unified API with code-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test unified API with list-heavy document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_document
    intent: "Test unified API with table document."
    v2_component: ContentAnalysis.tables
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_document
    intent: "Test unified API with mixed content."
    v2_component: REMOVED: MixedStrategy
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_very_small_document
    intent: "Test with very small document."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_whitespace_between_content
    intent: "Test document with lots of whitespace."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_content
    intent: "Test with unicode content."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_parameters_combined
    intent: "Test with all parameters specified."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_analysis_emits_warning
    intent: "Test that chunk_with_analysis() emits deprecation warning."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_simple_emits_warning
    intent: "Test that chunk_simple() emits deprecation warning."
    v2_component: MarkdownChunker.chunk() → List[Chunk]
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deprecated_methods_still_functional
    intent: "Test that deprecated methods still produce correct results."
    v2_component: MarkdownChunker
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

## Integration Tests

**Files analyzed**: 11
**Total tests**: 265
**V2 applicable**: 254
**Removed functionality**: 11

### tests/integration/test_career_matrix.py

```yaml
test_file: tests/integration/test_career_matrix.py
test_count: 22
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_structural_strategy_no_fragmentation
    intent: "Test that structural strategy doesn't fragment logical blocks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_no_section_mixing
    intent: "Test that chunks don't mix content from different major sections."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_markdown_structure_preserved
    intent: "Test that Markdown structure is preserved in chunks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_urls_not_broken
    intent: "Test that URLs are not broken across chunks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_data_loss
    intent: "Test that no content is lost during chunking."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_completeness
    intent: "Test that chunks have complete metadata."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_size_respected
    intent: "Test that chunk sizes are reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_produces_results
    intent: "Test that chunking produces non-empty results."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_auto_strategy_no_content_loss
    intent: "Test that auto strategy doesn't lose content."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_metrics
    intent: "Test chunk_with_metrics returns valid metrics."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_for_mixed_document
    intent: "Test that appropriate strategy is selected for mixed documents."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_no_fragmentation
    intent: "Test that structural strategy doesn't fragment logical blocks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_no_section_mixing
    intent: "Test that chunks don't mix content from different major sections."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_markdown_structure_preserved
    intent: "Test that Markdown structure is preserved in chunks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_urls_not_broken
    intent: "Test that URLs are not broken across chunks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_data_loss
    intent: "Test that no content is lost during chunking."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_completeness
    intent: "Test that chunks have complete metadata."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_size_respected
    intent: "Test that chunk sizes are reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunking_produces_results
    intent: "Test that chunking produces non-empty results."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_auto_strategy_no_content_loss
    intent: "Test that auto strategy doesn't lose content."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_metrics
    intent: "Test chunk_with_metrics returns valid metrics."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_selection_for_mixed_document
    intent: "Test that appropriate strategy is selected for mixed documents."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_dify_plugin_integration.py

```yaml
test_file: tests/integration/test_dify_plugin_integration.py
test_count: 28
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_basic_chunking_workflow
    intent: "Test basic chunking workflow with Dify-style input."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_output_format_with_metadata
    intent: "Test that output format matches Dify expectations with metadata."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_output_format_without_metadata
    intent: "Test that output format is correct when metadata is disabled."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error
    intent: "Test that empty input returns error message."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_input_error
    intent: "Test that whitespace-only input is handled (chunker processes it)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_parameter_mapping
    intent: "Test that strategy parameter is correctly mapped."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_handling
    intent: "Test handling of large documents."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test with code-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test with list-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_document
    intent: "Test with table document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_document
    intent: "Test with mixed content document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_parameter_defaults
    intent: "Test that parameter defaults work correctly."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_filtering_integration
    intent: "Test that metadata filtering works end-to-end."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_invalid_strategy
    intent: "Test error handling with invalid strategy."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_basic_chunking_workflow
    intent: "Test basic chunking workflow with Dify-style input."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_output_format_with_metadata
    intent: "Test that output format matches Dify expectations with metadata."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_output_format_without_metadata
    intent: "Test that output format is correct when metadata is disabled."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_input_error
    intent: "Test that empty input returns error message."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_input_error
    intent: "Test that whitespace-only input is handled (chunker processes it)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_strategy_parameter_mapping
    intent: "Test that strategy parameter is correctly mapped."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_handling
    intent: "Test handling of large documents."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test with code-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_list_heavy_document
    intent: "Test with list-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_table_document
    intent: "Test with table document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_content_document
    intent: "Test with mixed content document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_parameter_defaults
    intent: "Test that parameter defaults work correctly."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_metadata_filtering_integration
    intent: "Test that metadata filtering works end-to-end."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_invalid_strategy
    intent: "Test error handling with invalid strategy."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_edge_cases_full_pipeline.py

```yaml
test_file: tests/integration/test_edge_cases_full_pipeline.py
test_count: 58
legacy_imports:
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_empty_document
    intent: "Test handling of empty document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_document
    intent: "Test document with only whitespace."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_character_document
    intent: "Test document with single character."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_document
    intent: "Test document with single line."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_document
    intent: "Test handling of very large document (1MB+)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_single_line
    intent: "Test document with very long single line."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_many_small_sections
    intent: "Test document with many small sections."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_code_block
    intent: "Test markdown with unclosed code block."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mismatched_headers
    intent: "Test markdown with mismatched header levels."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_table
    intent: "Test markdown with malformed table."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_list
    intent: "Test markdown with malformed list."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_heavy_document
    intent: "Test document with heavy unicode usage."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_special_markdown_characters
    intent: "Test document with special markdown characters."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_mixed_line_endings
    intent: "Test document with mixed line endings (LF, CRLF)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_cr_only
    intent: "Test document with CR only line endings."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_code
    intent: "Test document containing only code blocks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_inline_code
    intent: "Test document with only inline code."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_text
    intent: "Test document with only plain text (no markdown)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_paragraphs
    intent: "Test document with only paragraphs (no headers)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_headers
    intent: "Test document with deeply nested headers."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_lists
    intent: "Test document with deeply nested lists."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_blockquotes
    intent: "Test document with deeply nested blockquotes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_small_chunk_size
    intent: "Test with very small max_chunk_size."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_chunk_size
    intent: "Test with very large max_chunk_size."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_zero_overlap
    intent: "Test with zero overlap."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_100_percent_overlap
    intent: "Test with 100% overlap."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_chain_activation
    intent: "Test that fallback chain activates when needed."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_recovery_from_invalid_strategy
    intent: "Test recovery when invalid strategy specified."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_graceful_degradation
    intent: "Test graceful degradation on problematic content."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_empty_document
    intent: "Test handling of empty document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_whitespace_only_document
    intent: "Test document with only whitespace."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_character_document
    intent: "Test document with single character."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_line_document
    intent: "Test document with single line."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_document
    intent: "Test handling of very large document (1MB+)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_long_single_line
    intent: "Test document with very long single line."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_many_small_sections
    intent: "Test document with many small sections."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unclosed_code_block
    intent: "Test markdown with unclosed code block."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mismatched_headers
    intent: "Test markdown with mismatched header levels."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_table
    intent: "Test markdown with malformed table."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_malformed_list
    intent: "Test markdown with malformed list."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_unicode_heavy_document
    intent: "Test document with heavy unicode usage."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_special_markdown_characters
    intent: "Test document with special markdown characters."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_mixed_line_endings
    intent: "Test document with mixed line endings (LF, CRLF)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_cr_only
    intent: "Test document with CR only line endings."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_code
    intent: "Test document containing only code blocks."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_inline_code
    intent: "Test document with only inline code."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_text
    intent: "Test document with only plain text (no markdown)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_document_with_only_paragraphs
    intent: "Test document with only paragraphs (no headers)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_headers
    intent: "Test document with deeply nested headers."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_lists
    intent: "Test document with deeply nested lists."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_deeply_nested_blockquotes
    intent: "Test document with deeply nested blockquotes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_small_chunk_size
    intent: "Test with very small max_chunk_size."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_very_large_chunk_size
    intent: "Test with very large max_chunk_size."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_zero_overlap
    intent: "Test with zero overlap."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_100_percent_overlap
    intent: "Test with 100% overlap."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_fallback_chain_activation
    intent: "Test that fallback chain activates when needed."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_recovery_from_invalid_strategy
    intent: "Test recovery when invalid strategy specified."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_graceful_degradation
    intent: "Test graceful degradation on problematic content."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_end_to_end.py

```yaml
test_file: tests/integration/test_end_to_end.py
test_count: 10
legacy_imports:
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_end_to_end_readme_document
    intent: "Test complete pipeline with README-style document."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_code_heavy_document
    intent: "Test complete pipeline with code-heavy document."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_table_document
    intent: "Test complete pipeline with table document."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_with_custom_config
    intent: "Test pipeline with custom configuration."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_metadata_present
    intent: "Test that all chunks have required metadata."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_empty_input
    intent: "Test pipeline handles empty input gracefully."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_minimal_input
    intent: "Test pipeline with minimal valid input."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_large_document
    intent: "Test pipeline with larger document."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_mixed_content
    intent: "Test pipeline with mixed content types."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_performance
    intent: "Test that chunking completes in reasonable time."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_full_api_flow.py

```yaml
test_file: tests/integration/test_full_api_flow.py
test_count: 50
legacy_imports:
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunk_text
  - markdown_chunker.api.APIAdapter
  - markdown_chunker.api.APIRequest
v2_applicable: true
removed_functionality: false

tests:
  - name: test_end_to_end_basic_flow
    intent: "Test basic end-to-end flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_with_config
    intent: "Test end-to-end with custom configuration."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_json_round_trip
    intent: "Test JSON serialization round-trip."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_all_strategies
    intent: "Test all strategies through API."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_api_adapter_caching
    intent: "Test that adapter caches chunker instances."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_adapter_config_changes
    intent: "Test adapter handles config changes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_validation_integration
    intent: "Test validation integration in API flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_api_error_handling_integration
    intent: "Test error handling throughout API."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_serialization_integration
    intent: "Test Chunk serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_config_serialization_integration
    intent: "Test ChunkConfig serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_result_serialization_integration
    intent: "Test ChunkingResult serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_all_profiles_work
    intent: "Test all configuration profiles."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_profiles_through_api
    intent: "Test profiles through API adapter."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_text_integration
    intent: "Test chunk_text convenience function."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_text_with_config
    intent: "Test chunk_text with custom config."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simplified_api_integration
    intent: "Test simplified API integration."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error_flow
    intent: "Test validation error through full flow."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_error_recovery
    intent: "Test processing error recovery."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_processing
    intent: "Test processing large document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_batch_processing_performance
    intent: "Test batch processing performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_profile_performance
    intent: "Test different config profiles performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_documentation_scenario
    intent: "Test API documentation chunking scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_tutorial_scenario
    intent: "Test code tutorial chunking scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_rag_preparation_scenario
    intent: "Test RAG system preparation scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_search_indexing_scenario
    intent: "Test search indexing scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_basic_flow
    intent: "Test basic end-to-end flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_with_config
    intent: "Test end-to-end with custom configuration."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_json_round_trip
    intent: "Test JSON serialization round-trip."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_all_strategies
    intent: "Test all strategies through API."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_api_adapter_caching
    intent: "Test that adapter caches chunker instances."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_adapter_config_changes
    intent: "Test adapter handles config changes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_validation_integration
    intent: "Test validation integration in API flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_api_error_handling_integration
    intent: "Test error handling throughout API."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_serialization_integration
    intent: "Test Chunk serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_config_serialization_integration
    intent: "Test ChunkConfig serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_result_serialization_integration
    intent: "Test ChunkingResult serialization in full flow."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_all_profiles_work
    intent: "Test all configuration profiles."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_profiles_through_api
    intent: "Test profiles through API adapter."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_text_integration
    intent: "Test chunk_text convenience function."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_text_with_config
    intent: "Test chunk_text with custom config."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_simplified_api_integration
    intent: "Test simplified API integration."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_error_flow
    intent: "Test validation error through full flow."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_processing_error_recovery
    intent: "Test processing error recovery."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_processing
    intent: "Test processing large document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_batch_processing_performance
    intent: "Test batch processing performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_config_profile_performance
    intent: "Test different config profiles performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_documentation_scenario
    intent: "Test API documentation chunking scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_tutorial_scenario
    intent: "Test code tutorial chunking scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_rag_preparation_scenario
    intent: "Test RAG system preparation scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_search_indexing_scenario
    intent: "Test search indexing scenario."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_full_pipeline.py

```yaml
test_file: tests/integration/test_full_pipeline.py
test_count: 5
legacy_imports:
  - markdown_chunker.chunker.MarkdownChunker
  - markdown_chunker.parser.Stage1Interface
v2_applicable: false
removed_functionality: true

tests:
  - name: test_complete_pipeline
    intent: "Test the complete Stage 1 + Stage 2 pipeline"
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_strategy_selection
    intent: "Test that different document types select appropriate strategies"
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_chain
    intent: "Test that fallback chain works correctly"
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_metadata_accuracy
    intent: "Test that metadata is accurate and complete"
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_performance_consistency
    intent: "Test that performance is consistent across runs"
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/integration/test_full_pipeline_real_docs.py

```yaml
test_file: tests/integration/test_full_pipeline_real_docs.py
test_count: 30
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_api_documentation_chunking
    intent: "Test chunking of API documentation."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_documentation_preserves_code_blocks
    intent: "Test that code blocks are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tutorial_chunking
    intent: "Test chunking of tutorial."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tutorial_preserves_examples
    intent: "Test that examples are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_readme_chunking
    intent: "Test chunking of README."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_readme_preserves_badges
    intent: "Test that badges/links are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blog_post_chunking
    intent: "Test chunking of blog post."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blog_post_preserves_tables
    intent: "Test that tables are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_chunking
    intent: "Test chunking of technical specification."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_large_document
    intent: "Test handling of large document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_documents_no_content_loss
    intent: "Test no content loss for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_all_documents_metadata_valid
    intent: "Test metadata validity for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_all_documents_line_numbers_valid
    intent: "Test line numbers validity for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_strategy_selection_appropriate
    intent: "Test that appropriate strategy is selected."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_sizes_reasonable
    intent: "Test that chunk sizes are reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_documentation_chunking
    intent: "Test chunking of API documentation."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_api_documentation_preserves_code_blocks
    intent: "Test that code blocks are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tutorial_chunking
    intent: "Test chunking of tutorial."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_tutorial_preserves_examples
    intent: "Test that examples are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_readme_chunking
    intent: "Test chunking of README."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_readme_preserves_badges
    intent: "Test that badges/links are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blog_post_chunking
    intent: "Test chunking of blog post."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_blog_post_preserves_tables
    intent: "Test that tables are preserved."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_chunking
    intent: "Test chunking of technical specification."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_large_document
    intent: "Test handling of large document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_all_documents_no_content_loss
    intent: "Test no content loss for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_all_documents_metadata_valid
    intent: "Test metadata validity for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_all_documents_line_numbers_valid
    intent: "Test line numbers validity for all documents."
    v2_component: End-to-end pipeline
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for all documents."
  - name: test_strategy_selection_appropriate
    intent: "Test that appropriate strategy is selected."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_sizes_reasonable
    intent: "Test that chunk sizes are reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_overlap_integration.py

```yaml
test_file: tests/integration/test_overlap_integration.py
test_count: 14
legacy_imports:
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_end_to_end_metadata_mode
    intent: "Test full pipeline with metadata mode."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_legacy_mode
    intent: "Test full pipeline with legacy mode."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_content_preservation_both_modes
    intent: "Test that content is preserved in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_chunk_both_modes
    intent: "Test single chunk document in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_no_keys
    intent: "Test that overlap keys are not added when overlap disabled."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_metadata_mode
    intent: "Test overlap metadata mode with structural strategy."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_sentences_strategy_both_modes
    intent: "Test overlap with sentences strategy in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_end_to_end_metadata_mode
    intent: "Test full pipeline with metadata mode."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_end_to_end_legacy_mode
    intent: "Test full pipeline with legacy mode."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_content_preservation_both_modes
    intent: "Test that content is preserved in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_single_chunk_both_modes
    intent: "Test single chunk document in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_no_keys
    intent: "Test that overlap keys are not added when overlap disabled."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_metadata_mode
    intent: "Test overlap metadata mode with structural strategy."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_sentences_strategy_both_modes
    intent: "Test overlap with sentences strategy in both modes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/integration/test_overlap_redesign_integration.py

```yaml
test_file: tests/integration/test_overlap_redesign_integration.py
test_count: 16
legacy_imports:
v2_applicable: true
removed_functionality: false

tests:
  - name: test_full_pipeline_metadata_mode
    intent: "End-to-end test with metadata mode (v2 default)."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_full_pipeline_no_overlap
    intent: "End-to-end test with overlap disabled."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_mode_equivalence_full_document
    intent: "Test chunking produces consistent results."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_section_boundary_isolation
    intent: "Verify chunks maintain section boundaries."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_real_document_context_tracking
    intent: "Test with actual markdown document structure."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_offset_boundaries
    intent: "Verify context extraction works correctly."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test with code-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_integration
    intent: "Test full pipeline with overlap disabled."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_full_pipeline_metadata_mode
    intent: "End-to-end test with metadata mode (v2 default)."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_full_pipeline_no_overlap
    intent: "End-to-end test with overlap disabled."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
  - name: test_mode_equivalence_full_document
    intent: "Test chunking produces consistent results."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_section_boundary_isolation
    intent: "Verify chunks maintain section boundaries."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_real_document_context_tracking
    intent: "Test with actual markdown document structure."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_context_offset_boundaries
    intent: "Verify context extraction works correctly."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_heavy_document
    intent: "Test with code-heavy document."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_overlap_disabled_integration
    intent: "Test full pipeline with overlap disabled."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: true
    removed_functionality: false
```

### tests/integration/test_parser_chunker_integration.py

```yaml
test_file: tests/integration/test_parser_chunker_integration.py
test_count: 2
legacy_imports:
  - markdown_chunker.chunker.core.MarkdownChunker
  - markdown_chunker.parser.Stage1Interface
v2_applicable: false
removed_functionality: true

tests:
  - name: test_stage1_interface_integration
    intent: "Test that Stage1Interface produces valid data for Stage 2."
    v2_component: End-to-end pipeline
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_fallback_rate_monitoring
    intent: "Test fallback rate monitoring to ensure it stays below 10%."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
```

### tests/integration/test_performance_full_pipeline.py

```yaml
test_file: tests/integration/test_performance_full_pipeline.py
test_count: 30
legacy_imports:
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_small_document_performance
    intent: "Test that small documents process quickly (<2s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_multiple_runs
    intent: "Test consistency across multiple runs."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test that medium documents process in reasonable time (<3s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_performance
    intent: "Test technical specification (20KB) performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test that large documents process in reasonable time (<10s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_100kb_document_performance
    intent: "Test 100KB document performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_calculation
    intent: "Test throughput across different document sizes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_with_different_configs
    intent: "Test throughput with different configurations."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_usage_reasonable
    intent: "Test that memory usage is reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_memory_leaks_multiple_documents
    intent: "Test that processing multiple documents doesn't leak memory."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_performance
    intent: "Test structural strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_strategy_performance
    intent: "Test code strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_strategy_performance
    intent: "Test mixed strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_baseline_performance
    intent: "Establish baseline performance metrics."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_with_overlap
    intent: "Test that overlap doesn't significantly slow down processing."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_performance
    intent: "Test that small documents process quickly (<2s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_small_document_multiple_runs
    intent: "Test consistency across multiple runs."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_medium_document_performance
    intent: "Test that medium documents process in reasonable time (<3s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_technical_spec_performance
    intent: "Test technical specification (20KB) performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_large_document_performance
    intent: "Test that large documents process in reasonable time (<10s)."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_100kb_document_performance
    intent: "Test 100KB document performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_calculation
    intent: "Test throughput across different document sizes."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_throughput_with_different_configs
    intent: "Test throughput with different configurations."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_memory_usage_reasonable
    intent: "Test that memory usage is reasonable."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_memory_leaks_multiple_documents
    intent: "Test that processing multiple documents doesn't leak memory."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_structural_strategy_performance
    intent: "Test structural strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_code_strategy_performance
    intent: "Test code strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_mixed_strategy_performance
    intent: "Test mixed strategy performance."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_baseline_performance
    intent: "Establish baseline performance metrics."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_performance_with_overlap
    intent: "Test that overlap doesn't significantly slow down processing."
    v2_component: End-to-end pipeline
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

## API Tests

**Files analyzed**: 4
**Total tests**: 138
**V2 applicable**: 138
**Removed functionality**: 0

### tests/api/test_adapter.py

```yaml
test_file: tests/api/test_adapter.py
test_count: 38
legacy_imports:
  - markdown_chunker.api.adapter.APIAdapter
  - markdown_chunker.api.types.APIRequest
  - markdown_chunker.api.validator.APIValidator
v2_applicable: true
removed_functionality: false

tests:
  - name: test_adapter_initialization
    intent: "Test adapter can be initialized."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_adapter_with_custom_validator
    intent: "Test adapter with custom validator."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_successful_request_processing
    intent: "Test successful request processing."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_request_with_custom_config
    intent: "Test request with custom configuration."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_request_with_strategy_override
    intent: "Test request with strategy override."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_content
    intent: "Test validation rejects invalid content."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_strategy
    intent: "Test validation rejects invalid strategy."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_config
    intent: "Test validation rejects invalid config."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_for_processing_failure
    intent: "Test error handling for processing failures."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_caching_enabled
    intent: "Test chunker is cached between requests."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_cache_invalidated_on_config_change
    intent: "Test chunker cache is invalidated when config changes."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_caching_disabled
    intent: "Test chunker is not cached when caching disabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test cache can be cleared."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_dict_convenience_method
    intent: "Test process_dict convenience method."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_dict_handles_invalid_request
    intent: "Test process_dict handles invalid request dict."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_response_includes_request_metadata
    intent: "Test response includes request metadata."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_response_includes_warnings
    intent: "Test response includes warnings from chunking."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complete_workflow
    intent: "Test complete request-response workflow."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_requests_with_caching
    intent: "Test multiple requests benefit from caching."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_adapter_initialization
    intent: "Test adapter can be initialized."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_adapter_with_custom_validator
    intent: "Test adapter with custom validator."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_successful_request_processing
    intent: "Test successful request processing."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_request_with_custom_config
    intent: "Test request with custom configuration."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_request_with_strategy_override
    intent: "Test request with strategy override."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_content
    intent: "Test validation rejects invalid content."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_strategy
    intent: "Test validation rejects invalid strategy."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validation_rejects_invalid_config
    intent: "Test validation rejects invalid config."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_handling_for_processing_failure
    intent: "Test error handling for processing failures."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_caching_enabled
    intent: "Test chunker is cached between requests."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_cache_invalidated_on_config_change
    intent: "Test chunker cache is invalidated when config changes."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_chunker_caching_disabled
    intent: "Test chunker is not cached when caching disabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_clear_cache
    intent: "Test cache can be cleared."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_dict_convenience_method
    intent: "Test process_dict convenience method."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_process_dict_handles_invalid_request
    intent: "Test process_dict handles invalid request dict."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_response_includes_request_metadata
    intent: "Test response includes request metadata."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_response_includes_warnings
    intent: "Test response includes warnings from chunking."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complete_workflow
    intent: "Test complete request-response workflow."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_requests_with_caching
    intent: "Test multiple requests benefit from caching."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/api/test_backward_compatibility.py

```yaml
test_file: tests/api/test_backward_compatibility.py
test_count: 14
legacy_imports:
  - markdown_chunker.ChunkConfig
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.types.Chunk
v2_applicable: true
removed_functionality: false

tests:
  - name: test_property_basic_chunk_method_works
    intent: "Property: Basic chunk() method works for any input."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "for any input."
  - name: test_property_config_parameter_works
    intent: "Property: ChunkConfig parameter works correctly."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: chunkconfig parameter works correctly."
  - name: test_property_chunk_attributes_present
    intent: "Property: All chunks have required attributes."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
    property: "property: all chunks have required attributes."
  - name: test_basic_chunk_method
    intent: "Test basic chunk() method works."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_default_config
    intent: "Test chunk() with default configuration."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_custom_config
    intent: "Test chunk() with custom config."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_returns_list
    intent: "Test chunk() returns list."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_empty_string
    intent: "Test chunk() handles empty string."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_with_whitespace_only
    intent: "Test chunk() handles whitespace-only input."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_metadata_structure
    intent: "Test that chunk metadata has expected structure."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_line_numbers
    intent: "Test that chunks have valid line numbers."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_multiple_chunkers_independent
    intent: "Test that multiple chunker instances are independent."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_config_profiles
    intent: "Test ChunkConfig profile methods work."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
  - name: test_chunk_preserves_content_order
    intent: "Test that chunks preserve content order."
    v2_component: API layer
    test_type: property
    v2_applicable: true
    removed_functionality: false
```

### tests/api/test_error_handler.py

```yaml
test_file: tests/api/test_error_handler.py
test_count: 44
legacy_imports:
  - markdown_chunker.api.error_handler.APIErrorHandler
  - markdown_chunker.api.error_handler.create_error_handler
  - markdown_chunker.api.error_handler.handle_api_error
  - markdown_chunker.api.types.APIResponse
  - markdown_chunker.chunker.core.ChunkingError
v2_applicable: true
removed_functionality: false

tests:
  - name: test_handler_initialization
    intent: "Test handler can be initialized."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handler_with_traceback
    intent: "Test handler with traceback enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_strategy_selection_error
    intent: "Test handling strategy selection errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_configuration_error
    intent: "Test handling configuration errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_chunking_error
    intent: "Test handling chunking errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_value_error
    intent: "Test handling value errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_type_error
    intent: "Test handling type errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_generic_error
    intent: "Test handling generic errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_context
    intent: "Test error handling with context."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_traceback
    intent: "Test error includes traceback when enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_without_traceback
    intent: "Test error doesn't include traceback by default."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_success
    intent: "Test wrapping successful operation."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_failure
    intent: "Test wrapping failing operation."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_with_args
    intent: "Test wrapping operation with arguments."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_returns_api_response
    intent: "Test wrapping operation that returns APIResponse."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_error_handler
    intent: "Test create_error_handler factory."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_error_handler_with_traceback
    intent: "Test factory with traceback enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_api_error_convenience
    intent: "Test handle_api_error convenience function."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_api_error_with_context
    intent: "Test convenience function with context."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complete_error_handling_workflow
    intent: "Test complete error handling workflow."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_response_structure
    intent: "Test error response has correct structure."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_response_serializable
    intent: "Test error response is JSON serializable."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handler_initialization
    intent: "Test handler can be initialized."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handler_with_traceback
    intent: "Test handler with traceback enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_strategy_selection_error
    intent: "Test handling strategy selection errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_configuration_error
    intent: "Test handling configuration errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_chunking_error
    intent: "Test handling chunking errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_value_error
    intent: "Test handling value errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_type_error
    intent: "Test handling type errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_generic_error
    intent: "Test handling generic errors."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_context
    intent: "Test error handling with context."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_with_traceback
    intent: "Test error includes traceback when enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_without_traceback
    intent: "Test error doesn't include traceback by default."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_success
    intent: "Test wrapping successful operation."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_failure
    intent: "Test wrapping failing operation."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_with_args
    intent: "Test wrapping operation with arguments."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_wrap_operation_returns_api_response
    intent: "Test wrapping operation that returns APIResponse."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_error_handler
    intent: "Test create_error_handler factory."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_create_error_handler_with_traceback
    intent: "Test factory with traceback enabled."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_api_error_convenience
    intent: "Test handle_api_error convenience function."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_handle_api_error_with_context
    intent: "Test convenience function with context."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_complete_error_handling_workflow
    intent: "Test complete error handling workflow."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_response_structure
    intent: "Test error response has correct structure."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_error_response_serializable
    intent: "Test error response is JSON serializable."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/api/test_validator.py

```yaml
test_file: tests/api/test_validator.py
test_count: 42
legacy_imports:
  - markdown_chunker.api.APIValidator
v2_applicable: true
removed_functionality: false

tests:
  - name: test_validate_chunk_sizes_valid_max_size
    intent: "Test validation accepts valid max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_invalid_max_size_type
    intent: "Test validation rejects non-integer max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_max_size_too_small
    intent: "Test validation rejects max_chunk_size below minimum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_max_size_too_large
    intent: "Test validation rejects max_chunk_size above maximum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_valid_min_size
    intent: "Test validation accepts valid min_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_invalid_min_size_type
    intent: "Test validation rejects non-integer min_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_min_size_too_small
    intent: "Test validation rejects min_chunk_size below minimum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_min_greater_than_max
    intent: "Test validation rejects min_chunk_size > max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_valid_relationship
    intent: "Test validation accepts valid min/max relationship."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_valid_size
    intent: "Test validation accepts valid overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_invalid_type
    intent: "Test validation rejects non-integer overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_negative_value
    intent: "Test validation rejects negative overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_zero_value
    intent: "Test validation accepts zero overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_calls_chunk_sizes
    intent: "Test validate_config properly calls _validate_chunk_sizes."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_calls_overlap
    intent: "Test validate_config properly calls _validate_overlap."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_accumulates_errors
    intent: "Test validate_config accumulates errors from all validators."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_empty_config
    intent: "Test validate_config handles empty config."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_complex_invalid_config
    intent: "Test validate_config with multiple invalid fields."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_single_responsibility
    intent: "Test _validate_chunk_sizes focuses on chunk size validation only."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_single_responsibility
    intent: "Test _validate_overlap focuses on overlap validation only."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_methods_are_independent
    intent: "Test refactored methods can be called independently."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_valid_max_size
    intent: "Test validation accepts valid max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_invalid_max_size_type
    intent: "Test validation rejects non-integer max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_max_size_too_small
    intent: "Test validation rejects max_chunk_size below minimum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_max_size_too_large
    intent: "Test validation rejects max_chunk_size above maximum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_valid_min_size
    intent: "Test validation accepts valid min_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_invalid_min_size_type
    intent: "Test validation rejects non-integer min_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_min_size_too_small
    intent: "Test validation rejects min_chunk_size below minimum."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_min_greater_than_max
    intent: "Test validation rejects min_chunk_size > max_chunk_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_valid_relationship
    intent: "Test validation accepts valid min/max relationship."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_valid_size
    intent: "Test validation accepts valid overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_invalid_type
    intent: "Test validation rejects non-integer overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_negative_value
    intent: "Test validation rejects negative overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_zero_value
    intent: "Test validation accepts zero overlap_size."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_calls_chunk_sizes
    intent: "Test validate_config properly calls _validate_chunk_sizes."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_calls_overlap
    intent: "Test validate_config properly calls _validate_overlap."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_accumulates_errors
    intent: "Test validate_config accumulates errors from all validators."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_empty_config
    intent: "Test validate_config handles empty config."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_config_complex_invalid_config
    intent: "Test validate_config with multiple invalid fields."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_chunk_sizes_single_responsibility
    intent: "Test _validate_chunk_sizes focuses on chunk size validation only."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_validate_overlap_single_responsibility
    intent: "Test _validate_overlap focuses on overlap validation only."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_methods_are_independent
    intent: "Test refactored methods can be called independently."
    v2_component: API layer
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

## Regression Tests

**Files analyzed**: 2
**Total tests**: 16
**V2 applicable**: 13
**Removed functionality**: 3

### tests/regression/test_critical_fixes.py

```yaml
test_file: tests/regression/test_critical_fixes.py
test_count: 4
legacy_imports:
  - markdown_chunker.chunker.MarkdownChunker
v2_applicable: true
removed_functionality: false

tests:
  - name: test_mixed_strategy_lists
    intent: "Test MixedStrategy uses Stage 1 list data."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_mixed_strategy_tables
    intent: "Test MixedStrategy uses Stage 1 table data."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: false
    removed_functionality: true
  - name: test_list_strategy_integration
    intent: "Test ListStrategy uses Stage 1 list items."
    v2_component: Regression prevention
    test_type: integration
    v2_applicable: false
    removed_functionality: true
  - name: test_no_attribute_errors
    intent: "Test that no AttributeErrors occur."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

### tests/regression/test_overlap_duplication.py

```yaml
test_file: tests/regression/test_overlap_duplication.py
test_count: 12
legacy_imports:
  - markdown_chunker.MarkdownChunker
  - markdown_chunker.chunker.types.ChunkConfig
v2_applicable: true
removed_functionality: false

tests:
  - name: test_anti_fraud_phrase_no_duplication_metadata_mode
    intent: "Test that the anti-fraud phrase doesn't appear twice in metadata mode."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anti_fraud_phrase_context_separation
    intent: "Verify proper separation of phrase between content and context."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anti_fraud_phrase_legacy_mode_no_duplication
    intent: "Test that legacy mode also doesn't duplicate the phrase."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_content_duplication_at_boundaries
    intent: "General test that content is not duplicated at chunk boundaries."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_offset_based_verification
    intent: "Use start_offset and end_offset to verify no duplication."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_aligned_extraction_prevents_duplication
    intent: "Verify that block-aligned overlap extraction prevents additional duplication."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anti_fraud_phrase_no_duplication_metadata_mode
    intent: "Test that the anti-fraud phrase doesn't appear twice in metadata mode."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anti_fraud_phrase_context_separation
    intent: "Verify proper separation of phrase between content and context."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_anti_fraud_phrase_legacy_mode_no_duplication
    intent: "Test that legacy mode also doesn't duplicate the phrase."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_no_content_duplication_at_boundaries
    intent: "General test that content is not duplicated at chunk boundaries."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_offset_based_verification
    intent: "Use start_offset and end_offset to verify no duplication."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
  - name: test_block_aligned_extraction_prevents_duplication
    intent: "Verify that block-aligned overlap extraction prevents additional duplication."
    v2_component: Regression prevention
    test_type: unit
    v2_applicable: true
    removed_functionality: false
```

## Performance Tests

**Files analyzed**: 0
**Total tests**: 0
**V2 applicable**: 0
**Removed functionality**: 0


---

## Analysis Methodology

### Intent Extraction Process

1. **AST Parsing**: Each test file was parsed using Python's AST module
2. **Function Discovery**: Test functions (starting with `test_`) were extracted
3. **Docstring Analysis**: Docstrings were analyzed for intent descriptions
4. **Import Analysis**: Legacy imports were identified for v2 applicability
5. **Component Mapping**: Tests were mapped to v2 API components

### V2 Component Mapping Rules

| Pattern | V2 Component |
|---------|--------------|
| `content_analysis` | Parser.analyze() → ContentAnalysis |
| `fenced_block`, `code_block` | ContentAnalysis.code_blocks |
| `header` | ContentAnalysis.headers |
| `table` | ContentAnalysis.tables |
| `preamble` | ContentAnalysis.has_preamble |
| `chunk` | MarkdownChunker.chunk() |
| `config` | ChunkConfig |
| `overlap` | ChunkConfig.overlap_size |
| `code_strategy`, `code_aware` | CodeAwareStrategy |
| `structural` | StructuralStrategy |
| `fallback` | FallbackStrategy |

### Removed Functionality Detection

Tests were marked as "removed functionality" if they referenced:
- `list_strategy`, `table_strategy`, `sentences_strategy`, `mixed_strategy`
- `stage1`, `stage2`, `phase1`, `phase2`
- `block_packer`, `nesting_resolver`, `dynamic_strategy`

---

## Statistics Summary

| Category | Count |
|----------|-------|
| Total test files | 126 |
| Total tests | 3188 |
| V2 applicable | 2369 (74%) |
| Removed functionality | 819 (26%) |
| Parser tests | 1067 |
| Chunker tests | 1702 |
| Integration tests | 265 |
| API tests | 138 |
| Regression tests | 16 |

---

## Связанные файлы

### Документация в этой папке
- [README.md](./README.md) — точка входа, как пользоваться
- [SUMMARY.md](./SUMMARY.md) — краткая сводка
- [Semantic Groups](./semantic-groups.md) — 26 смысловых групп
- [V2 Test Specification](./v2-test-specification.md) — 52 спецификации тестов
- [Implementation Roadmap](./implementation-roadmap.md) — план реализации

### Связанные файлы в репозитории
- [Analysis Script](../../scripts/analyze_p1_tests.py) — скрипт анализа
- [Property Tests](../../tests/test_p1_specification_properties.py) — валидация спецификации

---

*Сгенерировано скриптом scripts/analyze_p1_tests.py*
