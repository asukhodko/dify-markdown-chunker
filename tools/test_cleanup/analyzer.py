"""
Test analysis components for the cleanup system.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
import fnmatch

from .models import (
    TestAnalysis,
    TestCategorization,
    TestType,
    TestFile,
    TestCategory,
    DuplicateReport,
)
from .config import CleanupConfig
from .logging_setup import LoggerMixin


class TestAnalyzer(LoggerMixin):
    """Main analyzer for test files and their characteristics."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
        self.import_analyzer = ImportAnalyzer(config)
        self.coverage_analyzer = CoverageAnalyzer(config)
        self.categorizer = TestCategorizer(config)
    
    def analyze_test_file(self, file_path: str) -> TestAnalysis:
        """
        Analyze a single test file to extract its characteristics.
        
        Args:
            file_path: Path to the test file
            
        Returns:
            TestAnalysis object with file analysis results
        """
        self.logger.debug(f"Analyzing test file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to read {file_path}: {e}")
            return self._create_empty_analysis(file_path)
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            self.logger.warning(f"Syntax error in {file_path}: {e}")
            return self._create_empty_analysis(file_path)
        
        # Extract imports
        imports = self.import_analyzer.extract_imports(tree, content)
        
        # Extract test functions
        test_functions = self._extract_test_functions(tree)
        
        # Analyze coverage areas
        coverage_areas = self.coverage_analyzer.analyze_coverage(tree, content)
        
        # Determine test type
        test_type = self._determine_test_type(file_path, tree, content)
        
        # Extract dependencies
        dependencies = self._extract_dependencies(tree)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(tree)
        
        # Check for legacy imports
        has_legacy_imports = self.import_analyzer.has_legacy_imports(imports)
        
        # Count lines
        line_count = len(content.splitlines())
        
        analysis = TestAnalysis(
            file_path=file_path,
            imports=imports,
            test_functions=test_functions,
            coverage_areas=coverage_areas,
            test_type=test_type,
            dependencies=dependencies,
            complexity_score=complexity_score,
            has_legacy_imports=has_legacy_imports,
            line_count=line_count,
        )
        
        self.logger.debug(f"Analysis complete for {file_path}: {len(test_functions)} tests, "
                         f"type={test_type.value}, legacy={has_legacy_imports}")
        
        return analysis
    
    def scan_test_directory(self) -> List[TestAnalysis]:
        """
        Scan the test directory and analyze all test files.
        
        Returns:
            List of TestAnalysis objects for all discovered test files
        """
        self.logger.info(f"Scanning test directory: {self.config.test_directory}")
        
        test_files = self._discover_test_files()
        analyses = []
        
        for file_path in test_files:
            analysis = self.analyze_test_file(file_path)
            analyses.append(analysis)
        
        self.logger.info(f"Analyzed {len(analyses)} test files")
        return analyses
    
    def categorize_tests(self, analyses: List[TestAnalysis]) -> TestCategorization:
        """
        Categorize tests based on their analysis results.
        
        Args:
            analyses: List of test analyses
            
        Returns:
            TestCategorization with tests sorted by category
        """
        self.logger.info("Categorizing tests...")
        return self.categorizer.categorize(analyses)
    
    def identify_duplicates(self, categorization: TestCategorization) -> DuplicateReport:
        """
        Identify duplicate tests between legacy and migration-compatible tests.
        
        Args:
            categorization: Test categorization results
            
        Returns:
            DuplicateReport with identified duplicates
        """
        self.logger.info("Identifying duplicate tests...")
        return self.categorizer.identify_duplicates(categorization)
    
    def _discover_test_files(self) -> List[str]:
        """Discover all test files in the test directory."""
        test_files = []
        test_dir = Path(self.config.test_directory)
        
        if not test_dir.exists():
            self.logger.warning(f"Test directory does not exist: {test_dir}")
            return test_files
        
        for pattern in self.config.test_file_patterns:
            for file_path in test_dir.rglob(pattern):
                if file_path.is_file() and self._should_include_file(str(file_path)):
                    test_files.append(str(file_path))
        
        self.logger.debug(f"Discovered {len(test_files)} test files")
        return sorted(test_files)
    
    def _should_include_file(self, file_path: str) -> bool:
        """Check if a file should be included in analysis."""
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_path, f"*{pattern}*"):
                return False
        return True
    
    def _extract_test_functions(self, tree: ast.AST) -> List[str]:
        """Extract test function names from AST."""
        test_functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_functions.append(node.name)
        
        return test_functions
    
    def _determine_test_type(self, file_path: str, tree: ast.AST, content: str) -> TestType:
        """Determine the type of test based on file path and content."""
        file_name = Path(file_path).name.lower()
        
        # Check file name patterns
        if 'performance' in file_name or 'benchmark' in file_name:
            return TestType.PERFORMANCE
        elif 'integration' in file_name:
            return TestType.INTEGRATION
        elif 'property' in file_name or 'hypothesis' in content:
            return TestType.PROPERTY
        elif 'regression' in file_name:
            return TestType.REGRESSION
        
        # Check content patterns
        if 'hypothesis' in content.lower() or '@given' in content:
            return TestType.PROPERTY
        elif 'time.time()' in content or 'timeit' in content:
            return TestType.PERFORMANCE
        elif any(keyword in content.lower() for keyword in ['integration', 'end-to-end', 'e2e']):
            return TestType.INTEGRATION
        
        return TestType.UNIT
    
    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract dependencies from imports and function calls."""
        dependencies = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                dependencies.add(node.module.split('.')[0])
        
        return sorted(list(dependencies))
    
    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate a simple complexity score for the test file."""
        complexity = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 0.5
            elif isinstance(node, ast.ClassDef):
                complexity += 1
        
        return complexity
    
    def _create_empty_analysis(self, file_path: str) -> TestAnalysis:
        """Create an empty analysis for files that couldn't be parsed."""
        return TestAnalysis(
            file_path=file_path,
            imports=[],
            test_functions=[],
            coverage_areas=[],
            test_type=TestType.UNKNOWN,
            dependencies=[],
            complexity_score=0.0,
            has_legacy_imports=False,
            line_count=0,
        )


class ImportAnalyzer(LoggerMixin):
    """Analyzes imports and dependencies in test files."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
    
    def extract_imports(self, tree: ast.AST, content: str) -> List[str]:
        """Extract all import statements from the AST."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"from {module} import {alias.name}")
        
        return imports
    
    def has_legacy_imports(self, imports: List[str]) -> bool:
        """Check if the imports contain any legacy module references."""
        import_text = " ".join(imports)
        
        for pattern in self.config.legacy_import_patterns:
            if pattern in import_text:
                return True
        
        return False
    
    def get_legacy_imports(self, imports: List[str]) -> List[str]:
        """Get only the legacy imports from the import list."""
        legacy_imports = []
        
        for import_stmt in imports:
            for pattern in self.config.legacy_import_patterns:
                if pattern in import_stmt:
                    legacy_imports.append(import_stmt)
                    break
        
        return legacy_imports


class CoverageAnalyzer(LoggerMixin):
    """Analyzes test coverage areas and functionality mapping."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
    
    def analyze_coverage(self, tree: ast.AST, content: str) -> List[str]:
        """Analyze what functionality areas this test covers."""
        coverage_areas = set()
        
        # Extract from function names
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                areas = self._extract_coverage_from_function_name(node.name)
                coverage_areas.update(areas)
        
        # Extract from string literals and comments
        coverage_areas.update(self._extract_coverage_from_content(content))
        
        # Extract from assertions and function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                areas = self._extract_coverage_from_call(node)
                coverage_areas.update(areas)
        
        return sorted(list(coverage_areas))
    
    def _extract_coverage_from_function_name(self, function_name: str) -> List[str]:
        """Extract coverage areas from test function names."""
        # Remove 'test_' prefix and split by underscores
        name_parts = function_name[5:].split('_')
        
        coverage_areas = []
        
        # Common functionality patterns
        functionality_keywords = {
            'chunk': 'chunking',
            'split': 'chunking',
            'parse': 'parsing',
            'config': 'configuration',
            'error': 'error_handling',
            'exception': 'error_handling',
            'validate': 'validation',
            'format': 'formatting',
            'render': 'rendering',
            'output': 'output_generation',
            'input': 'input_processing',
            'header': 'header_processing',
            'markdown': 'markdown_processing',
            'text': 'text_processing',
            'size': 'size_management',
            'limit': 'size_management',
            'performance': 'performance',
            'speed': 'performance',
            'memory': 'memory_management',
        }
        
        for part in name_parts:
            part_lower = part.lower()
            if part_lower in functionality_keywords:
                coverage_areas.append(functionality_keywords[part_lower])
            elif len(part) > 3:  # Include longer descriptive parts
                coverage_areas.append(part_lower)
        
        return coverage_areas
    
    def _extract_coverage_from_content(self, content: str) -> List[str]:
        """Extract coverage areas from content analysis."""
        coverage_areas = set()
        
        # Look for key functionality patterns in content
        patterns = {
            r'chunk\w*': 'chunking',
            r'split\w*': 'chunking',
            r'parse\w*': 'parsing',
            r'config\w*': 'configuration',
            r'error\w*': 'error_handling',
            r'exception\w*': 'error_handling',
            r'validate\w*': 'validation',
            r'format\w*': 'formatting',
            r'render\w*': 'rendering',
            r'header\w*': 'header_processing',
            r'markdown': 'markdown_processing',
            r'size\w*': 'size_management',
            r'limit\w*': 'size_management',
        }
        
        content_lower = content.lower()
        for pattern, area in patterns.items():
            if re.search(pattern, content_lower):
                coverage_areas.add(area)
        
        return list(coverage_areas)
    
    def _extract_coverage_from_call(self, node: ast.Call) -> List[str]:
        """Extract coverage areas from function calls."""
        coverage_areas = []
        
        if isinstance(node.func, ast.Attribute):
            method_name = node.func.attr.lower()
            if 'chunk' in method_name:
                coverage_areas.append('chunking')
            elif 'parse' in method_name:
                coverage_areas.append('parsing')
            elif 'config' in method_name:
                coverage_areas.append('configuration')
        
        return coverage_areas


class TestCategorizer(LoggerMixin):
    """Categorizes tests and identifies duplicates."""
    
    def __init__(self, config: CleanupConfig):
        self.config = config
    
    def categorize(self, analyses: List[TestAnalysis]) -> TestCategorization:
        """Categorize tests based on their analysis results."""
        redundant_tests = []
        valuable_tests = []
        unique_tests = []
        performance_tests = []
        property_tests = []
        migration_compatible_tests = []
        
        for analysis in analyses:
            test_file = TestFile(
                path=analysis.file_path,
                analysis=analysis,
                category=self._determine_category(analysis)
            )
            
            # Categorize by processing decision
            if test_file.category == TestCategory.REDUNDANT:
                redundant_tests.append(test_file)
            elif test_file.category == TestCategory.VALUABLE:
                valuable_tests.append(test_file)
            elif test_file.category == TestCategory.UNIQUE:
                unique_tests.append(test_file)
            elif test_file.category == TestCategory.MIGRATION_COMPATIBLE:
                migration_compatible_tests.append(test_file)
            
            # Categorize by test type
            if analysis.test_type == TestType.PERFORMANCE:
                performance_tests.append(test_file)
            elif analysis.test_type == TestType.PROPERTY:
                property_tests.append(test_file)
        
        categorization = TestCategorization(
            redundant_tests=redundant_tests,
            valuable_tests=valuable_tests,
            unique_tests=unique_tests,
            performance_tests=performance_tests,
            property_tests=property_tests,
            migration_compatible_tests=migration_compatible_tests,
        )
        
        self.logger.info(f"Categorization complete: {len(redundant_tests)} redundant, "
                        f"{len(valuable_tests)} valuable, {len(unique_tests)} unique, "
                        f"{len(migration_compatible_tests)} migration-compatible")
        
        return categorization
    
    def identify_duplicates(self, categorization: TestCategorization) -> DuplicateReport:
        """Identify duplicate tests between legacy and migration-compatible tests."""
        duplicate_pairs = []
        redundant_files = []
        unique_coverage_areas = set()
        
        # Get coverage areas from migration-compatible tests
        migration_coverage = set()
        for test_file in categorization.migration_compatible_tests:
            migration_coverage.update(test_file.analysis.coverage_areas)
        
        # Check legacy tests against migration coverage
        legacy_tests = (categorization.redundant_tests + 
                       categorization.valuable_tests + 
                       categorization.unique_tests)
        
        for legacy_test in legacy_tests:
            legacy_coverage = set(legacy_test.analysis.coverage_areas)
            
            # Calculate overlap with migration tests
            overlap = legacy_coverage.intersection(migration_coverage)
            overlap_ratio = len(overlap) / len(legacy_coverage) if legacy_coverage else 0
            
            if overlap_ratio >= self.config.duplicate_similarity_threshold:
                # Find the most similar migration test
                best_match = self._find_best_match(legacy_test, categorization.migration_compatible_tests)
                if best_match:
                    duplicate_pairs.append((legacy_test.path, best_match.path))
                    redundant_files.append(legacy_test.path)
            else:
                # This test has unique coverage
                unique_areas = legacy_coverage - migration_coverage
                unique_coverage_areas.update(unique_areas)
        
        return DuplicateReport(
            duplicate_pairs=duplicate_pairs,
            redundant_files=redundant_files,
            unique_coverage_areas=sorted(list(unique_coverage_areas)),
        )
    
    def _determine_category(self, analysis: TestAnalysis) -> TestCategory:
        """Determine the processing category for a test."""
        if not analysis.has_legacy_imports:
            return TestCategory.MIGRATION_COMPATIBLE
        
        # For now, mark all legacy tests as valuable
        # This will be refined by duplicate detection
        return TestCategory.VALUABLE
    
    def _find_best_match(self, legacy_test: TestFile, migration_tests: List[TestFile]) -> Optional[TestFile]:
        """Find the migration test that best matches the legacy test."""
        best_match = None
        best_similarity = 0
        
        legacy_coverage = set(legacy_test.analysis.coverage_areas)
        
        for migration_test in migration_tests:
            migration_coverage = set(migration_test.analysis.coverage_areas)
            
            if not legacy_coverage or not migration_coverage:
                continue
            
            # Calculate Jaccard similarity
            intersection = legacy_coverage.intersection(migration_coverage)
            union = legacy_coverage.union(migration_coverage)
            similarity = len(intersection) / len(union) if union else 0
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = migration_test
        
        return best_match if best_similarity >= 0.3 else None