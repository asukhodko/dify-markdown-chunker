"""
Unit tests for test analyzer components.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from .analyzer import TestAnalyzer, ImportAnalyzer, CoverageAnalyzer, TestCategorizer
from .config import CleanupConfig
from .models import TestAnalysis, TestType, TestCategory


class TestImportAnalyzer:
    """Unit tests for ImportAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.analyzer = ImportAnalyzer(self.config)
    
    def test_extract_imports_basic(self):
        """Test basic import extraction."""
        import ast
        content = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        tree = ast.parse(content)
        imports = self.analyzer.extract_imports(tree, content)
        
        expected_imports = [
            "import os",
            "import sys", 
            "from pathlib import Path",
            "from typing import List",
            "from typing import Dict",
        ]
        
        assert len(imports) == len(expected_imports)
        for expected in expected_imports:
            assert expected in imports
    
    def test_has_legacy_imports_positive(self):
        """Test detection of legacy imports."""
        imports = [
            "import os",
            "from markdown_chunker_v2 import MarkdownChunker",
            "import pytest",
        ]
        
        assert self.analyzer.has_legacy_imports(imports) is True
    
    def test_has_legacy_imports_negative(self):
        """Test no legacy imports detected."""
        imports = [
            "import os",
            "import pytest",
            "from adapter import MigrationAdapter",
        ]
        
        assert self.analyzer.has_legacy_imports(imports) is False
    
    def test_get_legacy_imports(self):
        """Test extraction of only legacy imports."""
        imports = [
            "import os",
            "from markdown_chunker_v2 import MarkdownChunker",
            "import pytest",
            "from markdown_chunker import ChunkConfig",
        ]
        
        legacy_imports = self.analyzer.get_legacy_imports(imports)
        
        assert len(legacy_imports) == 2
        assert "from markdown_chunker_v2 import MarkdownChunker" in legacy_imports
        assert "from markdown_chunker import ChunkConfig" in legacy_imports


class TestCoverageAnalyzer:
    """Unit tests for CoverageAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.analyzer = CoverageAnalyzer(self.config)
    
    def test_analyze_coverage_from_function_names(self):
        """Test coverage extraction from function names."""
        import ast
        content = """
def test_chunking_basic():
    pass

def test_error_handling():
    pass

def test_config_validation():
    pass
"""
        tree = ast.parse(content)
        coverage_areas = self.analyzer.analyze_coverage(tree, content)
        
        expected_areas = ['chunking', 'error_handling', 'configuration', 'validation']
        for area in expected_areas:
            assert area in coverage_areas
    
    def test_analyze_coverage_from_content(self):
        """Test coverage extraction from content patterns."""
        import ast
        content = """
def test_something():
    # Test chunking functionality
    chunker = SomeChunker()
    result = chunker.parse(text)
    validate_result(result)
"""
        tree = ast.parse(content)
        coverage_areas = self.analyzer.analyze_coverage(tree, content)
        
        expected_areas = ['chunking', 'parsing', 'validation']
        for area in expected_areas:
            assert area in coverage_areas
    
    def test_extract_coverage_from_function_name(self):
        """Test coverage extraction from individual function names."""
        test_cases = [
            ("test_chunk_markdown_text", ['chunking', 'markdown_processing', 'text_processing']),
            ("test_parse_config_file", ['parsing', 'configuration', 'file']),
            ("test_error_handling_invalid_input", ['error_handling', 'invalid', 'input_processing']),
        ]
        
        for function_name, expected_areas in test_cases:
            areas = self.analyzer._extract_coverage_from_function_name(function_name)
            for expected in expected_areas:
                assert expected in areas


class TestTestCategorizer:
    """Unit tests for TestCategorizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.categorizer = TestCategorizer(self.config)
    
    def test_determine_category_migration_compatible(self):
        """Test categorization of migration-compatible tests."""
        analysis = TestAnalysis(
            file_path="test_migration.py",
            imports=["import pytest", "from adapter import MigrationAdapter"],
            test_functions=["test_basic"],
            coverage_areas=["chunking"],
            test_type=TestType.UNIT,
            dependencies=["pytest"],
            complexity_score=1.0,
            has_legacy_imports=False,
        )
        
        category = self.categorizer._determine_category(analysis)
        assert category == TestCategory.MIGRATION_COMPATIBLE
    
    def test_determine_category_legacy(self):
        """Test categorization of legacy tests."""
        analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=["import pytest", "from markdown_chunker_v2 import MarkdownChunker"],
            test_functions=["test_basic"],
            coverage_areas=["chunking"],
            test_type=TestType.UNIT,
            dependencies=["pytest"],
            complexity_score=1.0,
            has_legacy_imports=True,
        )
        
        category = self.categorizer._determine_category(analysis)
        assert category == TestCategory.VALUABLE
    
    def test_find_best_match(self):
        """Test finding best matching migration test."""
        from .models import TestFile
        
        # Create legacy test
        legacy_analysis = TestAnalysis(
            file_path="test_legacy.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "parsing"],
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        legacy_test = TestFile(
            path="test_legacy.py",
            analysis=legacy_analysis,
            category=TestCategory.VALUABLE
        )
        
        # Create migration tests
        migration_analysis_1 = TestAnalysis(
            file_path="test_migration_1.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "validation"],  # 1 overlap
            test_type=TestType.UNIT,
            dependencies=[],
            complexity_score=1.0,
        )
        migration_test_1 = TestFile(
            path="test_migration_1.py",
            analysis=migration_analysis_1,
            category=TestCategory.MIGRATION_COMPATIBLE
        )
        
        migration_analysis_2 = TestAnalysis(
            file_path="test_migration_2.py",
            imports=[],
            test_functions=[],
            coverage_areas=["chunking", "parsing", "formatting"],  # 2 overlaps
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
        
        assert best_match == migration_test_2  # Should pick the one with more overlap


class TestTestAnalyzer:
    """Unit tests for TestAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            self.config = CleanupConfig.from_project_root(temp_dir)
            self.analyzer = TestAnalyzer(self.config)
    
    def test_analyze_test_file_basic(self):
        """Test basic test file analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            # Create a test file
            test_content = """
import pytest
from markdown_chunker_v2 import MarkdownChunker

def test_chunking_basic():
    chunker = MarkdownChunker()
    result = chunker.chunk("# Test")
    assert len(result) > 0

def test_error_handling():
    with pytest.raises(ValueError):
        chunker = MarkdownChunker()
        chunker.chunk(None)
"""
            
            test_file = os.path.join(temp_dir, "test_example.py")
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            analysis = analyzer.analyze_test_file(test_file)
            
            assert analysis.file_path == test_file
            assert len(analysis.test_functions) == 2
            assert "test_chunking_basic" in analysis.test_functions
            assert "test_error_handling" in analysis.test_functions
            assert analysis.has_legacy_imports is True
            assert "chunking" in analysis.coverage_areas
            assert "error_handling" in analysis.coverage_areas
            assert analysis.line_count > 0
    
    def test_analyze_test_file_syntax_error(self):
        """Test handling of files with syntax errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            # Create a file with syntax error
            test_content = """
import pytest
def test_broken(
    # Missing closing parenthesis
    pass
"""
            
            test_file = os.path.join(temp_dir, "test_broken.py")
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            analysis = analyzer.analyze_test_file(test_file)
            
            # Should return empty analysis for broken files
            assert analysis.file_path == test_file
            assert len(analysis.test_functions) == 0
            assert analysis.test_type == TestType.UNKNOWN
    
    def test_determine_test_type_performance(self):
        """Test performance test type detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            import ast
            content = """
import time
def test_performance():
    start = time.time()
    # do something
    end = time.time()
    assert end - start < 1.0
"""
            tree = ast.parse(content)
            test_type = analyzer._determine_test_type("test_performance.py", tree, content)
            
            assert test_type == TestType.PERFORMANCE
    
    def test_determine_test_type_integration(self):
        """Test integration test type detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            import ast
            content = """
def test_integration():
    # Integration test content
    pass
"""
            tree = ast.parse(content)
            test_type = analyzer._determine_test_type("test_integration_basic.py", tree, content)
            
            assert test_type == TestType.INTEGRATION
    
    def test_determine_test_type_property(self):
        """Test property-based test type detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            import ast
            content = """
from hypothesis import given
import hypothesis.strategies as st

@given(st.text())
def test_property(text):
    pass
"""
            tree = ast.parse(content)
            test_type = analyzer._determine_test_type("test_property.py", tree, content)
            
            assert test_type == TestType.PROPERTY
    
    def test_should_include_file(self):
        """Test file inclusion filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            # Should include regular test files
            assert analyzer._should_include_file("tests/test_basic.py") is True
            
            # Should exclude migration-compatible files
            assert analyzer._should_include_file("tests/test_migration_adapter.py") is False
            
            # Should exclude cache directories
            assert analyzer._should_include_file("tests/__pycache__/test.py") is False
    
    def test_discover_test_files(self):
        """Test test file discovery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CleanupConfig.from_project_root(temp_dir)
            analyzer = TestAnalyzer(config)
            
            # Create test directory structure
            test_dir = os.path.join(temp_dir, "tests")
            os.makedirs(test_dir)
            
            # Create test files
            test_files = [
                "test_basic.py",
                "test_advanced.py", 
                "test_migration_adapter.py",  # Should be excluded
                "helper.py",  # Should be excluded (doesn't match pattern)
            ]
            
            for filename in test_files:
                with open(os.path.join(test_dir, filename), 'w') as f:
                    f.write("def test_example(): pass")
            
            discovered = analyzer._discover_test_files()
            
            # Should find test files but exclude migration files
            assert len(discovered) == 2
            assert any("test_basic.py" in path for path in discovered)
            assert any("test_advanced.py" in path for path in discovered)
            assert not any("test_migration_adapter.py" in path for path in discovered)
            assert not any("helper.py" in path for path in discovered)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])