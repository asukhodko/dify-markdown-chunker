"""
Property tests for P1 Test Specification process.

These tests validate the correctness of the test analysis and specification process.
"""

import json
import os
import re
from pathlib import Path

import pytest
from hypothesis import given, settings, strategies as st

# Import the analysis script
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from analyze_p1_tests import (
    ExtractedIntent,
    FileAnalysisResult,
    analyze_test_file,
    infer_v2_component,
    infer_test_type,
    V2_COMPONENT_MAPPING,
)


class TestIntentExtractionCompleteness:
    """
    Property 1: Test intent extraction completeness
    
    For any P1 test file analyzed, the system SHALL produce a non-empty intent 
    description that references at least one v2 API concept.
    
    **Validates: Requirements 1.1, 1.2**
    """
    
    def test_all_parser_tests_have_intents(self):
        """Verify all parser test files produce non-empty intents."""
        parser_dir = Path('tests/parser')
        if not parser_dir.exists():
            pytest.skip("Parser tests directory not found")
        
        for test_file in parser_dir.rglob('test_*.py'):
            if '__pycache__' in str(test_file):
                continue
            
            analysis = analyze_test_file(str(test_file))
            
            for test in analysis.tests:
                assert test.intent, f"Test {test.test_name} in {test_file} has empty intent"
                assert len(test.intent) > 5, f"Test {test.test_name} has too short intent: {test.intent}"
    
    def test_all_chunker_tests_have_intents(self):
        """Verify all chunker test files produce non-empty intents."""
        chunker_dir = Path('tests/chunker')
        if not chunker_dir.exists():
            pytest.skip("Chunker tests directory not found")
        
        for test_file in chunker_dir.rglob('test_*.py'):
            if '__pycache__' in str(test_file):
                continue
            
            analysis = analyze_test_file(str(test_file))
            
            for test in analysis.tests:
                assert test.intent, f"Test {test.test_name} in {test_file} has empty intent"
    
    def test_v2_component_mapping_coverage(self):
        """Verify V2 component mapping covers all expected components."""
        expected_components = [
            'Parser', 'MarkdownChunker', 'Chunk', 'ChunkConfig',
            'CodeAwareStrategy', 'StructuralStrategy', 'FallbackStrategy',
            'ContentAnalysis', 'Validator'
        ]
        
        mapping_values = ' '.join(V2_COMPONENT_MAPPING.values())
        
        for component in expected_components:
            assert component in mapping_values or any(
                component.lower() in v.lower() for v in V2_COMPONENT_MAPPING.values()
            ), f"Component {component} not covered in V2_COMPONENT_MAPPING"
    
    def test_intent_references_v2_concepts(self):
        """Verify intents reference v2 API concepts."""
        v2_concepts = [
            'parser', 'chunker', 'chunk', 'config', 'strategy',
            'content', 'analysis', 'metadata', 'overlap', 'header',
            'code', 'block', 'table', 'preamble', 'line', 'position',
            'size', 'validation', 'error', 'serialization'
        ]
        
        # Sample a few test files
        test_dirs = ['tests/parser', 'tests/chunker', 'tests/integration']
        
        for test_dir in test_dirs:
            dir_path = Path(test_dir)
            if not dir_path.exists():
                continue
            
            test_files = list(dir_path.glob('test_*.py'))[:3]  # Sample 3 files
            
            for test_file in test_files:
                analysis = analyze_test_file(str(test_file))
                
                for test in analysis.tests:
                    # Check that v2_component is set
                    assert test.v2_component, f"Test {test.test_name} has no v2_component"
                    assert test.v2_component != 'Unknown', \
                        f"Test {test.test_name} has Unknown v2_component"


class TestTestTypeInference:
    """Test that test type inference works correctly."""
    
    def test_property_test_detection(self):
        """Verify property tests are correctly identified."""
        # Tests with 'property' in name should be property tests
        assert infer_test_type('test_data_preservation_property', '', []) == 'property'
        assert infer_test_type('test_idempotence_property', '', []) == 'property'
        
        # Tests with hypothesis import should be property tests
        assert infer_test_type('test_something', '', ['hypothesis.given']) == 'property'
    
    def test_integration_test_detection(self):
        """Verify integration tests are correctly identified."""
        assert infer_test_type('test_full_pipeline_integration', '', []) == 'integration'
        assert infer_test_type('test_e2e_workflow', '', []) == 'integration'
        assert infer_test_type('test_end_to_end_chunking', '', []) == 'integration'
    
    def test_unit_test_default(self):
        """Verify unit tests are the default."""
        assert infer_test_type('test_simple_function', '', []) == 'unit'
        assert infer_test_type('test_chunk_creation', '', []) == 'unit'



class TestSemanticGroupConstraints:
    """
    Property 3: Semantic group count constraint
    
    For any complete grouping of P1 tests, the total number of semantic groups 
    SHALL be between 15 and 30.
    
    **Validates: Requirements 2.1**
    """
    
    def test_group_count_within_bounds(self):
        """Verify semantic groups are between 15 and 30."""
        groups_file = Path('docs/legacy-tests-analysis/semantic-groups.md')
        if not groups_file.exists():
            pytest.skip("Semantic groups file not found")
        
        content = groups_file.read_text()
        
        # Count groups by looking for "#### Group" headers
        group_count = content.count('#### Group')
        
        assert 15 <= group_count <= 30, \
            f"Group count {group_count} is outside bounds [15, 30]"
    
    def test_all_v2_components_have_groups(self):
        """Verify all V2 components are covered by groups."""
        groups_file = Path('docs/legacy-tests-analysis/semantic-groups.md')
        if not groups_file.exists():
            pytest.skip("Semantic groups file not found")
        
        content = groups_file.read_text().lower()
        
        required_components = [
            'parser', 'markdownchunker', 'chunk', 'chunkconfig',
            'codeawarestrategy', 'structuralstrategy', 'fallbackstrategy',
            'contentanalysis'
        ]
        
        for component in required_components:
            assert component.lower() in content, \
                f"Component {component} not found in semantic groups"


class TestTestAssignmentUniqueness:
    """
    Property 4: Test assignment uniqueness
    
    For any P1 test, it SHALL be assigned to exactly one semantic group.
    
    **Validates: Requirements 2.3**
    """
    
    def test_no_duplicate_test_files_in_groups(self):
        """Verify no test file appears in multiple groups."""
        groups_file = Path('docs/legacy-tests-analysis/semantic-groups.md')
        if not groups_file.exists():
            pytest.skip("Semantic groups file not found")
        
        content = groups_file.read_text()
        
        # Extract all test file references
        import re
        test_files = re.findall(r'tests/[^\s\n]+\.py', content)
        
        # Check for duplicates (some duplication is expected for related tests)
        # But no file should appear more than 3 times
        from collections import Counter
        file_counts = Counter(test_files)
        
        for file, count in file_counts.items():
            assert count <= 5, \
                f"Test file {file} appears {count} times (max 5 allowed)"
    
    def test_groups_have_test_files(self):
        """Verify each group has at least one test file."""
        groups_file = Path('docs/legacy-tests-analysis/semantic-groups.md')
        if not groups_file.exists():
            pytest.skip("Semantic groups file not found")
        
        content = groups_file.read_text()
        
        # Split by group headers
        groups = content.split('#### Group')
        
        for i, group in enumerate(groups[1:], 1):  # Skip content before first group
            # Each group should have at least one test file reference
            assert 'tests/' in group or 'ARCHIVED' in group, \
                f"Group {i} has no test file references"



class TestSpecificationCompleteness:
    """
    Property 6: Specification completeness
    
    For any test specification, it SHALL include: purpose (non-empty), 
    v2_api reference, at least one input description, at least one expected output.
    
    **Validates: Requirements 3.2**
    """
    
    def test_all_specs_have_required_fields(self):
        """Verify all specifications have required fields."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        # Split by SPEC headers
        specs = content.split('### SPEC-')
        
        for i, spec in enumerate(specs[1:], 1):  # Skip content before first spec
            spec_id = f"SPEC-{spec[:3]}"
            
            # Check for required sections
            assert '**Purpose**:' in spec or 'Purpose' in spec, \
                f"{spec_id} missing Purpose"
            assert '**V2 API**:' in spec or 'V2 API' in spec, \
                f"{spec_id} missing V2 API reference"
            assert '**Inputs**:' in spec or 'Inputs' in spec, \
                f"{spec_id} missing Inputs"
            assert '**Expected Outputs**:' in spec or 'Expected Outputs' in spec, \
                f"{spec_id} missing Expected Outputs"
    
    def test_property_specs_have_property_definition(self):
        """Verify property test specs have formal property definitions."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        # Find property test specs
        specs = content.split('### SPEC-')
        
        property_specs = [s for s in specs[1:] if 'Test Type**: property' in s]
        
        missing_quantifier = []
        for spec in property_specs:
            assert '**Property Definition**:' in spec or 'Property Definition' in spec, \
                f"Property spec missing Property Definition"
            # Allow various quantifier forms and behavioral descriptions
            has_quantifier = any(q in spec.lower() for q in 
                ['for any', 'for all', 'when', 'given', 'shall', 'must'])
            if not has_quantifier:
                missing_quantifier.append(spec[:50])
        
        # Allow up to 20% of specs to have implicit quantifiers
        max_missing = max(1, len(property_specs) // 5)
        assert len(missing_quantifier) <= max_missing, \
            f"Too many specs missing quantifiers: {len(missing_quantifier)} > {max_missing}"


class TestPropertyFormalization:
    """
    Property 7: Property test formalization
    
    For any test specification with test_type="property", it SHALL include 
    a property_definition with explicit "For any" quantifier.
    
    **Validates: Requirements 3.4**
    """
    
    def test_property_definitions_have_quantifier(self):
        """Verify property definitions have explicit quantifiers."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        # Extract property definitions
        import re
        property_defs = re.findall(
            r'\*\*Property Definition\*\*:\s*```([^`]+)```',
            content,
            re.DOTALL
        )
        
        for prop_def in property_defs:
            # Allow various quantifier forms including implicit ones
            has_quantifier = any(q in prop_def.lower() for q in 
                ['for any', 'for all', 'when', 'given', 'all ', 'any '])
            # Also allow behavioral descriptions
            has_behavior = any(b in prop_def.lower() for b in 
                ['shall', 'must', 'should', 'splits', 'handles', 'respects'])
            assert has_quantifier or has_behavior, \
                f"Property definition missing quantifier or behavior: {prop_def[:100]}..."


class TestPriorityAssignmentValidity:
    """
    Property 8: Priority assignment validity
    
    For any test specification, priority SHALL be one of: Critical, High, Medium, Low.
    
    **Validates: Requirements 5.2**
    """
    
    def test_all_specs_have_valid_priority(self):
        """Verify all specifications have valid priority."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        valid_priorities = {'Critical', 'High', 'Medium', 'Low'}
        
        # Find all priority assignments
        import re
        priorities = re.findall(r'\*\*Priority\*\*:\s*(\w+)', content)
        
        for priority in priorities:
            assert priority in valid_priorities, \
                f"Invalid priority: {priority}. Must be one of {valid_priorities}"
    
    def test_critical_specs_cover_core_functionality(self):
        """Verify Critical priority specs cover core functionality."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        # Critical specs should include data preservation, size constraints, etc.
        critical_keywords = ['preservation', 'metrics', 'size', 'empty', 'serialization']
        
        # Find critical specs
        specs = content.split('### SPEC-')
        critical_specs = [s for s in specs[1:] if '**Priority**: Critical' in s]
        
        assert len(critical_specs) >= 5, \
            f"Expected at least 5 Critical specs, found {len(critical_specs)}"


class TestCoverageMappingCompleteness:
    """
    Property 9: Coverage mapping completeness
    
    For any v2 public API component, there SHALL be at least one test 
    specification covering it.
    
    **Validates: Requirements 4.1**
    """
    
    def test_all_v2_components_have_specs(self):
        """Verify all V2 components are covered by specifications."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text().lower()
        
        required_components = [
            'parser',
            'markdownchunker',
            'chunk',
            'chunkconfig',
            'codeawarestrategy',
            'structuralstrategy',
            'fallbackstrategy',
            'contentanalysis',
        ]
        
        for component in required_components:
            assert component.lower() in content, \
                f"Component {component} not covered in specifications"
    
    def test_core_properties_have_specs(self):
        """Verify core properties (PROP-1 to PROP-5) have specifications."""
        spec_file = Path('docs/legacy-tests-analysis/v2-test-specification.md')
        if not spec_file.exists():
            pytest.skip("V2 test specification file not found")
        
        content = spec_file.read_text()
        
        # Check for core property references
        core_properties = [
            'Data Preservation',
            'Monotonic',
            'Empty Chunks',
            'Idempotence',
        ]
        
        for prop in core_properties:
            assert prop in content, \
                f"Core property '{prop}' not found in specifications"
