"""
Unit tests for test categorization logic.
"""

import pytest
import tempfile
import os
from unittest.mock import Mock

from .analyzer import TestCategorizer
from .config import CleanupConfig
from .models import (
    TestAnalysis, TestFile, TestType, TestCategory, 
    TestCategorization, DuplicateReport
)


class TestTestCategorizerUnit:
    """Unit tests for TestCategorizer categorization logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.categorizer = TestCategorizer(self.config)
    
    def test_categorize_mixed_tests(self):
        """Test categorization of mixed test types."""
        # Create test analyses
        analyses = [
            # Migration-compatible test
            TestAnalysis(
                file_path="test_migration.py",
                imports=["import pytest", "from adapter import MigrationAdapter"],
                test_functions=["test_basic"],
                coverage_areas=["chunking"],
                test_type=TestType.UNIT,
                dependencies=["pytest"],
                complexity_score=1.0,
                has_legacy_imports=False,
            ),
            # Legacy test (will be marked as valuable)
            TestAnalysis(
                file_path="test_legacy.py",
                imports=["import pytest", "from markdown_chunker_v2 import MarkdownChunker"],
                test_functions=["test_legacy"],
                coverage_areas=["parsing"],
                test_type=TestType.UNIT,
                dependencies=["pytest"],
                complexity_score=2.0,
                has_legacy_imports=True,
            ),
            # Performance test
            TestAnalysis(
                file_path="test_performance.py",
                imports=["import time"],
                test_functions=["test_speed"],
                coverage_areas=["performance"],
                test_type=TestType.PERFORMANCE,
                dependencies=["time"],
                complexity_score=3.0,
                has_legacy_imports=True,
            ),
            # Property test
            TestAnalysis(
                file_path="test_property.py",
                imports=["from hypothesis import given"],
                test_functions=["test_property"],
                coverage_areas=["validation"],
                test_type=TestType.PROPERTY,
                dependencies=["hypothesis"],
                complexity_score=1.5,
                has_legacy_imports=True,
            ),
        ]
        
        categorization = self.categorizer.categorize(analyses)
        
        # Verify categorization results
        assert len(categorization.migration_compatible_tests) == 1
        assert len(categorization.valuable_tests) == 3  # All legacy tests marked as valuable initially
        assert len(categorization.performance_tests) == 1
        assert len(categorization.property_tests) == 1
        
        # Check specific categorizations
        migration_test = categorization.migration_compatible_tests[0]
        assert migration_test.path == "test_migration.py"
        assert migration_test.category == TestCategory.MIGRATION_COMPATIBLE
        
        performance_test = categorization.performance_tests[0]
        assert performance_test.path == "test_performance.py"
        assert performance_test.analysis.test_type == TestType.PERFORMANCE
        
        property_test = categorization.property_tests[0]
        assert property_test.path == "test_property.py"
        assert property_test.analysis.test_type == TestType.PROPERTY
    
    def test_identify_duplicates_high_overlap(self):
        """Test duplicate identification with high coverage overlap."""
        # Create categorization with overlapping tests
        legacy_analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=["from markdown_chunker_v2 import MarkdownChunker"],
            test_functions=["test_chunk"],
            coverage_areas=["chunking", "parsing", "validation"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=2.0,
            has_legacy_imports=True,
        )
        legacy_test = TestFile(
            path="test_legacy.py",
            analysis=legacy_analysis,
            category=TestCategory.VALUABLE
        )
        
        migration_analysis = TestAnalysis(
            file_path="test_migration.py",
            imports=["from adapter import MigrationAdapter"],
            test_functions=["test_chunk_migration"],
            coverage_areas=["chunking", "parsing", "formatting"],  # 2/3 overlap
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.5,
            has_legacy_imports=False,
        )
        migration_test = TestFile(
            path="test_migration.py",
            analysis=migration_analysis,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        categorization = TestCategorization(
            redundant_tests=[],
            valuable_tests=[legacy_test],
            unique_tests=[],
            performance_tests=[],
            property_tests=[],
            migration_compatible_tests=[migration_test],
        )
        
        duplicate_report = self.categorizer.identify_duplicates(categorization)
        
        # Should identify as duplicate due to high overlap (2/3 = 0.67 > 0.8 threshold? No)
        # Actually, let's check the exact calculation
        legacy_coverage = {"chunking", "parsing", "validation"}
        migration_coverage = {"chunking", "parsing", "formatting"}
        overlap = legacy_coverage.intersection(migration_coverage)  # {"chunking", "parsing"}
        overlap_ratio = len(overlap) / len(legacy_coverage)  # 2/3 = 0.67
        
        # With default threshold of 0.8, this should NOT be a duplicate
        assert len(duplicate_report.duplicate_pairs) == 0
        assert len(duplicate_report.redundant_files) == 0
        
        # The unique coverage should include "validation" (from legacy) and "formatting" (from migration)
        # But since migration test is not legacy, only legacy unique areas are reported
        assert "validation" in duplicate_report.unique_coverage_areas
    
    def test_identify_duplicates_exact_match(self):
        """Test duplicate identification with exact coverage match."""
        # Create categorization with exactly matching tests
        legacy_analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=["from markdown_chunker_v2 import MarkdownChunker"],
            test_functions=["test_chunk"],
            coverage_areas=["chunking", "parsing"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=2.0,
            has_legacy_imports=True,
        )
        legacy_test = TestFile(
            path="test_legacy.py",
            analysis=legacy_analysis,
            category=TestCategory.VALUABLE
        )
        
        migration_analysis = TestAnalysis(
            file_path="test_migration.py",
            imports=["from adapter import MigrationAdapter"],
            test_functions=["test_chunk_migration"],
            coverage_areas=["chunking", "parsing"],  # Exact match
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.5,
            has_legacy_imports=False,
        )
        migration_test = TestFile(
            path="test_migration.py",
            analysis=migration_analysis,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        categorization = TestCategorization(
            redundant_tests=[],
            valuable_tests=[legacy_test],
            unique_tests=[],
            performance_tests=[],
            property_tests=[],
            migration_compatible_tests=[migration_test],
        )
        
        duplicate_report = self.categorizer.identify_duplicates(categorization)
        
        # Should identify as duplicate due to exact match (overlap_ratio = 1.0 >= 0.8)
        assert len(duplicate_report.duplicate_pairs) == 1
        assert duplicate_report.duplicate_pairs[0] == ("test_legacy.py", "test_migration.py")
        assert "test_legacy.py" in duplicate_report.redundant_files
        assert len(duplicate_report.unique_coverage_areas) == 0  # No unique areas
    
    def test_find_best_match_no_match(self):
        """Test finding best match when no good match exists."""
        legacy_analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=[],
            test_functions=[],
            coverage_areas=["unique_functionality", "special_case"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        legacy_test = TestFile(
            path="test_legacy.py",
            analysis=legacy_analysis,
            category=TestCategory.VALUABLE
        )
        
        migration_analysis = TestAnalysis(
            file_path="test_migration.py",
            imports=[],
            test_functions=[],
            coverage_areas=["completely_different", "unrelated"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        migration_test = TestFile(
            path="test_migration.py",
            analysis=migration_analysis,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        migration_tests = [migration_test]
        best_match = self.categorizer._find_best_match(legacy_test, migration_tests)
        
        # Should return None due to no overlap (similarity < 0.3 threshold)
        assert best_match is None
    
    def test_find_best_match_multiple_candidates(self):
        """Test finding best match among multiple candidates."""
        legacy_analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "parsing", "validation"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        legacy_test = TestFile(
            path="test_legacy.py",
            analysis=legacy_analysis,
            category=TestCategory.VALUABLE
        )
        
        # Migration test with low similarity
        migration_analysis_1 = TestAnalysis(
            file_path="test_migration_1.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "formatting"],  # 1/4 union = 0.25 similarity
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        migration_test_1 = TestFile(
            path="test_migration_1.py",
            analysis=migration_analysis_1,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        # Migration test with higher similarity
        migration_analysis_2 = TestAnalysis(
            file_path="test_migration_2.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "parsing", "error_handling"],  # 2/4 union = 0.5 similarity
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        migration_test_2 = TestFile(
            path="test_migration_2.py",
            analysis=migration_analysis_2,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        migration_tests = [migration_test_1, migration_test_2]
        best_match = self.categorizer._find_best_match(legacy_test, migration_tests)
        
        # Should return the test with higher similarity
        assert best_match == migration_test_2
    
    def test_determine_category_edge_cases(self):
        """Test category determination for edge cases."""
        # Test with no imports
        analysis_no_imports = TestAnalysis(
            file_path="test_no_imports.py",
            imports=[],
            test_functions=["test_something"],
            coverage_areas=["basic"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
            has_legacy_imports=False,
        )
        
        category = self.categorizer._determine_category(analysis_no_imports)
        assert category == TestCategory.MIGRATION_COMPATIBLE
        
        # Test with mixed imports (legacy + modern)
        analysis_mixed = TestAnalysis(
            file_path="test_mixed.py",
            imports=[
                "import pytest",
                "from markdown_chunker_v2 import MarkdownChunker",
                "from adapter import MigrationAdapter"
            ],
            test_functions=["test_mixed"],
            coverage_areas=["mixed"],
            test_type=TestType.UNIT,
            dependencies=["pytest"],
            complexity_score=2.0,
            has_legacy_imports=True,  # Has legacy imports
        )
        
        category = self.categorizer._determine_category(analysis_mixed)
        assert category == TestCategory.VALUABLE  # Legacy imports present
    
    def test_categorization_totals(self):
        """Test that categorization totals are calculated correctly."""
        analyses = [
            TestAnalysis(
                file_path=f"test_{i}.py",
                imports=["from markdown_chunker_v2 import MarkdownChunker"] if i % 2 == 0 else ["import pytest"],
                test_functions=[f"test_{i}"],
                coverage_areas=[f"area_{i}"],
                test_type=TestType.UNIT,
                dependencies=[],
                complexity_score=1.0,
                has_legacy_imports=(i % 2 == 0),
            )
            for i in range(6)
        ]
        
        categorization = self.categorizer.categorize(analyses)
        
        # Should have 3 legacy tests (even indices) and 3 migration-compatible (odd indices)
        assert len(categorization.valuable_tests) == 3
        assert len(categorization.migration_compatible_tests) == 3
        assert categorization.total_legacy_tests == 3
        
        # All tests should be accounted for
        total_categorized = (len(categorization.redundant_tests) +
                           len(categorization.valuable_tests) +
                           len(categorization.unique_tests) +
                           len(categorization.migration_compatible_tests))
        assert total_categorized == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])