"""
Property-based tests for test analyzer components.

These tests validate universal correctness properties of the test analysis system.
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import tempfile
import os
from pathlib import Path
from typing import List, Dict

from .analyzer import TestAnalyzer, ImportAnalyzer, CoverageAnalyzer, TestCategorizer
from .config import CleanupConfig
from .models import TestAnalysis, TestType, TestCategory


# Test data generation strategies
@st.composite
def generate_test_file_content(draw):
    """Generate realistic test file content."""
    imports = draw(st.lists(
        st.sampled_from([
            "import unittest",
            "import pytest", 
            "from markdown_chunker_v2 import MarkdownChunker",
            "from markdown_chunker import ChunkConfig",
            "from adapter import MigrationAdapter",
            "import hypothesis",
            "from hypothesis import given",
        ]),
        min_size=1,
        max_size=5
    ))
    
    test_functions = draw(st.lists(
        st.sampled_from([
            "def test_chunking_basic():",
            "def test_error_handling():",
            "def test_configuration():",
            "def test_performance():",
            "def test_integration():",
            "def test_parsing():",
            "def test_validation():",
        ]),
        min_size=1,
        max_size=8
    ))
    
    content_parts = imports + [""] + test_functions + ["    pass"]
    return "\n".join(content_parts)


@st.composite
def generate_test_file_path(draw):
    """Generate realistic test file paths."""
    base_names = [
        "test_chunking",
        "test_integration", 
        "test_performance",
        "test_property_based",
        "test_regression",
        "test_unit",
        "test_error_handling",
    ]
    
    base_name = draw(st.sampled_from(base_names))
    suffix = draw(st.sampled_from(["", "_basic", "_advanced", "_edge_cases"]))
    
    return f"tests/{base_name}{suffix}.py"


class TestAnalyzerStateMachine(RuleBasedStateMachine):
    """State machine for testing analyzer consistency."""
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.config = CleanupConfig.from_project_root(self.temp_dir)
        self.analyzer = TestAnalyzer(self.config)
        self.analyzed_files: Dict[str, TestAnalysis] = {}
    
    @rule(file_path=generate_test_file_path(), content=generate_test_file_content())
    def create_test_file(self, file_path: str, content: str):
        """Create a test file and analyze it."""
        full_path = os.path.join(self.temp_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
        
        analysis = self.analyzer.analyze_test_file(full_path)
        self.analyzed_files[full_path] = analysis
    
    @invariant()
    def analysis_consistency(self):
        """Verify that analysis results are consistent."""
        for file_path, analysis in self.analyzed_files.items():
            # File path should match
            assert analysis.file_path == file_path
            
            # Test functions should start with 'test_'
            for func_name in analysis.test_functions:
                assert func_name.startswith('test_'), f"Invalid test function name: {func_name}"
            
            # Legacy imports should be detected correctly
            has_legacy = any(
                pattern in " ".join(analysis.imports) 
                for pattern in self.config.legacy_import_patterns
            )
            assert analysis.has_legacy_imports == has_legacy
            
            # Complexity should be non-negative
            assert analysis.complexity_score >= 0
            
            # Line count should be positive for valid files
            if analysis.test_functions:  # If we found test functions, file was parsed
                assert analysis.line_count > 0


# Property 1: Test Categorization Accuracy
@given(st.lists(generate_test_file_content(), min_size=1, max_size=10))
@settings(max_examples=50, deadline=5000)
def test_property_1_categorization_accuracy(test_contents: List[str]):
    """
    Property 1: Test Categorization Accuracy
    
    For any set of legacy test files, the categorization system should correctly 
    identify redundant tests (those with coverage overlap), valuable tests 
    (those with unique coverage), and test types (unit, integration, performance, property-based).
    
    Validates: Requirements 1.1, 1.2, 1.3, 1.5
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        analyzer = TestAnalyzer(config)
        
        # Create test files
        analyses = []
        for i, content in enumerate(test_contents):
            file_path = os.path.join(temp_dir, f"tests/test_file_{i}.py")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            analysis = analyzer.analyze_test_file(file_path)
            analyses.append(analysis)
        
        # Categorize tests
        categorization = analyzer.categorize_tests(analyses)
        
        # Verify categorization properties
        all_tests = (categorization.redundant_tests + 
                    categorization.valuable_tests + 
                    categorization.unique_tests +
                    categorization.migration_compatible_tests)
        
        # Property: All analyzed tests should be categorized
        assert len(all_tests) == len(analyses), "Not all tests were categorized"
        
        # Property: No test should appear in multiple categories
        all_paths = [test.path for test in all_tests]
        assert len(all_paths) == len(set(all_paths)), "Tests appear in multiple categories"
        
        # Property: Test types should be valid
        for test in all_tests:
            assert isinstance(test.analysis.test_type, TestType), "Invalid test type"
            assert isinstance(test.category, TestCategory), "Invalid test category"
        
        # Property: Legacy imports should be detected correctly
        for test in all_tests:
            if test.category == TestCategory.MIGRATION_COMPATIBLE:
                assert not test.analysis.has_legacy_imports, "Migration-compatible test has legacy imports"


@given(st.lists(generate_test_file_content(), min_size=2, max_size=8))
@settings(max_examples=30, deadline=5000)
def test_property_duplicate_detection_consistency(test_contents: List[str]):
    """
    Property: Duplicate Detection Consistency
    
    For any set of test files, duplicate detection should be consistent and symmetric.
    If test A is a duplicate of test B, then they should have significant coverage overlap.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        analyzer = TestAnalyzer(config)
        
        # Create test files with some having similar content
        analyses = []
        for i, content in enumerate(test_contents):
            file_path = os.path.join(temp_dir, f"tests/test_file_{i}.py")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            analysis = analyzer.analyze_test_file(file_path)
            analyses.append(analysis)
        
        categorization = analyzer.categorize_tests(analyses)
        duplicate_report = analyzer.identify_duplicates(categorization)
        
        # Property: Duplicate pairs should have meaningful overlap
        for legacy_path, migration_path in duplicate_report.duplicate_pairs:
            legacy_analysis = next(a for a in analyses if a.file_path == legacy_path)
            migration_analysis = next(a for a in analyses if a.file_path == migration_path)
            
            legacy_coverage = set(legacy_analysis.coverage_areas)
            migration_coverage = set(migration_analysis.coverage_areas)
            
            if legacy_coverage and migration_coverage:
                overlap = legacy_coverage.intersection(migration_coverage)
                overlap_ratio = len(overlap) / len(legacy_coverage)
                assert overlap_ratio >= config.duplicate_similarity_threshold, \
                    f"Duplicate pair has insufficient overlap: {overlap_ratio}"


@given(st.text(min_size=20, max_size=500, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pc', 'Pd', 'Ps', 'Pe', 'Po', 'Zs'))))
@settings(max_examples=50, deadline=3000, suppress_health_check=[HealthCheck.filter_too_much])
def test_property_import_analysis_correctness(content: str):
    """
    Property: Import Analysis Correctness
    
    For any Python content, import analysis should correctly identify all import statements
    and detect legacy imports based on configured patterns.
    """
    # Create more realistic Python content
    python_content = f"""
import os
import sys
{content}
def test_example():
    pass
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        import_analyzer = ImportAnalyzer(config)
        
        # Try to parse the content
        try:
            import ast
            tree = ast.parse(python_content)
        except SyntaxError:
            # Skip invalid Python content
            return
        
        imports = import_analyzer.extract_imports(tree, python_content)
        has_legacy = import_analyzer.has_legacy_imports(imports)
        
        # Property: All imports should be valid import statements
        for import_stmt in imports:
            assert import_stmt.startswith(('import ', 'from ')), f"Invalid import: {import_stmt}"
        
        # Property: Legacy detection should be consistent with patterns
        import_text = " ".join(imports)
        expected_legacy = any(pattern in import_text for pattern in config.legacy_import_patterns)
        assert has_legacy == expected_legacy, "Legacy import detection inconsistent"


@given(st.sampled_from([
    "import pytest\ndef test_basic(): pass",
    "from markdown_chunker_v2 import MarkdownChunker\ndef test_chunking(): pass", 
    "import unittest\ndef test_parsing(): pass",
    "def test_validation(): assert True",
    "# Test file\ndef test_example(): pass"
]))
@settings(max_examples=20, deadline=3000, suppress_health_check=[HealthCheck.filter_too_much])
def test_property_coverage_analysis_completeness(content: str):
    """
    Property: Coverage Analysis Completeness
    
    For any test content, coverage analysis should identify relevant functionality areas
    and the results should be consistent with the content.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        coverage_analyzer = CoverageAnalyzer(config)
        
        try:
            import ast
            tree = ast.parse(content)
        except SyntaxError:
            return  # Skip invalid content
        
        coverage_areas = coverage_analyzer.analyze_coverage(tree, content)
        
        # Property: Coverage areas should be strings
        for area in coverage_areas:
            assert isinstance(area, str), f"Coverage area is not a string: {area}"
            assert len(area) > 0, "Empty coverage area found"
        
        # Property: No duplicate coverage areas
        assert len(coverage_areas) == len(set(coverage_areas)), "Duplicate coverage areas found"


# Integration property test
@given(st.integers(min_value=1, max_value=5))
@settings(max_examples=20, deadline=10000)
def test_property_end_to_end_analysis_workflow(num_files: int):
    """
    Property: End-to-End Analysis Workflow
    
    For any number of test files, the complete analysis workflow should produce
    consistent and valid results at each step.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        analyzer = TestAnalyzer(config)
        
        # Create test files with varied content
        test_contents = [
            "import unittest\ndef test_basic(): pass",
            "from markdown_chunker_v2 import MarkdownChunker\ndef test_legacy(): pass",
            "import pytest\ndef test_integration(): pass",
            "from hypothesis import given\ndef test_property(): pass",
            "import time\ndef test_performance(): pass",
        ]
        
        analyses = []
        for i in range(num_files):
            content = test_contents[i % len(test_contents)]
            file_path = os.path.join(temp_dir, f"tests/test_file_{i}.py")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            analysis = analyzer.analyze_test_file(file_path)
            analyses.append(analysis)
        
        # Run complete workflow
        categorization = analyzer.categorize_tests(analyses)
        duplicate_report = analyzer.identify_duplicates(categorization)
        
        # Property: Workflow should complete without errors
        assert len(analyses) == num_files, "Not all files were analyzed"
        
        # Property: Categorization should account for all analyses
        total_categorized = (len(categorization.redundant_tests) +
                           len(categorization.valuable_tests) +
                           len(categorization.unique_tests) +
                           len(categorization.migration_compatible_tests))
        assert total_categorized == num_files, "Categorization count mismatch"
        
        # Property: Duplicate report should be valid
        assert isinstance(duplicate_report.duplicate_pairs, list), "Invalid duplicate pairs"
        assert isinstance(duplicate_report.redundant_files, list), "Invalid redundant files"
        assert isinstance(duplicate_report.unique_coverage_areas, list), "Invalid unique coverage areas"


if __name__ == "__main__":
    # Run property tests
    pytest.main([__file__, "-v", "--tb=short"])