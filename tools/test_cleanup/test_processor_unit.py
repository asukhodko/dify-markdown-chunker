"""
Unit tests for test processor components.
"""

import os
import tempfile

import pytest

from .config import CleanupConfig
from .models import (
    AdaptationPlan,
    CodeChange,
    DuplicateReport,
    TestAnalysis,
    TestCategory,
    TestFile,
    TestType,
)
from .processor import FileManager, RedundancyDetector, TestAdapter, TestProcessor


class TestRedundancyDetector:
    """Unit tests for RedundancyDetector."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.detector = RedundancyDetector(self.config)

    def test_extract_unique_assertions_complex(self):
        """Test extraction of complex assertions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_example.py")
            content = """
import pytest

def test_complex():
    result = [1, 2, 3]
    assert isinstance(result, list)
    assert len(result) >= 3 and all(x > 0 for x in result)
    assert result != []
    assert True  # Should be filtered out
"""
            with open(test_file, "w") as f:
                f.write(content)

            assertions = self.detector.extract_unique_assertions(test_file)

            # Should preserve complex assertions
            complex_assertions = [
                a for a in assertions if "isinstance" in a or "len(" in a or "!=" in a
            ]
            assert len(complex_assertions) > 0, "Should preserve complex assertions"

            # Should not preserve basic assertions
            basic_assertions = [a for a in assertions if a.strip() == "assert True"]
            assert len(basic_assertions) == 0, "Should not preserve basic assertions"

    def test_extract_unique_assertions_syntax_error(self):
        """Test handling of files with syntax errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "test_broken.py")
            content = """
def test_broken(
    # Missing closing parenthesis
    assert True
"""
            with open(test_file, "w") as f:
                f.write(content)

            assertions = self.detector.extract_unique_assertions(test_file)

            # Should return empty list for broken files
            assert assertions == []

    def test_is_unique_assertion_patterns(self):
        """Test unique assertion detection patterns."""
        test_cases = [
            ("assert True", False),
            ("assert False", False),
            ("assert x is not None", False),
            ("assert len(result) > 0", False),
            ("assert len(result) == 3", False),
            ("assert isinstance(x, int)", True),
            ("assert hasattr(obj, 'method')", True),
            ("assert result.startswith('test')", True),
            ("assert 'key' in dictionary", True),
            ("assert x >= 5 and y <= 10", True),
            ("assert result != expected", True),
        ]

        for assertion, expected_unique in test_cases:
            result = self.detector._is_unique_assertion(assertion)
            assert result == expected_unique, f"Failed for: {assertion}"


class TestTestAdapter:
    """Unit tests for TestAdapter."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.adapter = TestAdapter(self.config)

    def test_plan_import_changes(self):
        """Test planning of import changes."""
        imports = [
            "import pytest",
            "from markdown_chunker_v2 import MarkdownChunker",
            "from markdown_chunker import ChunkConfig",
            "import os",
        ]

        changes = self.adapter._plan_import_changes(imports)

        # Should plan changes for legacy imports
        assert len(changes) >= 2, "Should plan changes for legacy imports"

        # Check specific replacements
        legacy_import = "from markdown_chunker_v2 import MarkdownChunker"
        assert legacy_import in changes, "Should plan change for MarkdownChunker import"
        assert changes[legacy_import] == "from adapter import MigrationAdapter"

    def test_plan_code_changes(self):
        """Test planning of code changes."""
        import ast

        content = """
def test_example():
    chunker = MarkdownChunker()
    result = chunker.chunk("test text")
    assert len(result) > 0
"""
        tree = ast.parse(content)

        changes = self.adapter._plan_code_changes(tree, content)

        # Should plan changes for MarkdownChunker usage
        instantiation_changes = [c for c in changes if c.change_type == "instantiation"]
        method_changes = [c for c in changes if c.change_type == "method_call"]

        assert len(instantiation_changes) > 0, "Should plan instantiation changes"
        assert len(method_changes) > 0, "Should plan method call changes"

        # Check specific changes
        inst_change = instantiation_changes[0]
        assert "MigrationAdapter(" in inst_change.new_code

        method_change = method_changes[0]
        assert ".run_chunking(" in method_change.new_code

    def test_create_adaptation_plan(self):
        """Test creation of adaptation plans."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file_path = os.path.join(temp_dir, "test_legacy.py")
            content = """
from markdown_chunker_v2 import MarkdownChunker
import pytest

def test_chunking():
    chunker = MarkdownChunker()
    result = chunker.chunk("# Test")
    assert len(result) > 0
"""
            with open(test_file_path, "w") as f:
                f.write(content)

            # Create TestFile object
            analysis = TestAnalysis(
                file_path=test_file_path,
                imports=[
                    "from markdown_chunker_v2 import MarkdownChunker",
                    "import pytest",
                ],
                test_functions=["test_chunking"],
                coverage_areas=["chunking"],
                test_type=TestType.UNIT,
                dependencies=["pytest"],
                complexity_score=2.0,
                has_legacy_imports=True,
            )

            test_file = TestFile(
                path=test_file_path, analysis=analysis, category=TestCategory.VALUABLE
            )

            plan = self.adapter.create_adaptation_plan(test_file)

            # Verify plan structure
            assert isinstance(plan, AdaptationPlan)
            assert plan.original_file == test_file_path
            assert plan.adapted_file != test_file_path
            assert "_adapted" in plan.adapted_file
            assert len(plan.import_changes) > 0
            assert len(plan.code_changes) > 0
            assert isinstance(plan.preserved_assertions, list)

    def test_execute_adaptation(self):
        """Test execution of adaptation plans."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create original test file
            original_file = os.path.join(temp_dir, "test_original.py")
            content = """
from markdown_chunker_v2 import MarkdownChunker

def test_basic():
    chunker = MarkdownChunker()
    result = chunker.chunk("test")
    assert len(result) > 0
"""
            with open(original_file, "w") as f:
                f.write(content)

            # Create adaptation plan
            adapted_file = os.path.join(temp_dir, "test_adapted.py")
            plan = AdaptationPlan(
                original_file=original_file,
                adapted_file=adapted_file,
                import_changes={
                    "from markdown_chunker_v2 import MarkdownChunker": (
                        "from adapter import MigrationAdapter"
                    )
                },
                code_changes=[
                    CodeChange(
                        line_number=5,  # Line with "chunker = MarkdownChunker()"
                        old_code="MarkdownChunker()",
                        new_code="MigrationAdapter()",
                        change_type="instantiation",
                    ),
                    CodeChange(
                        line_number=6,  # Line with "result = chunker.chunk("test")"
                        old_code=".chunk(",
                        new_code=".run_chunking(",
                        change_type="method_call",
                    ),
                ],
                preserved_assertions=["assert len(result) > 0"],
            )

            # Execute adaptation
            success = self.adapter.execute_adaptation(plan)

            assert success, "Adaptation should succeed"
            assert os.path.exists(adapted_file), "Adapted file should be created"

            # Verify adapted content
            with open(adapted_file, "r") as f:
                adapted_content = f.read()

            assert "from adapter import MigrationAdapter" in adapted_content
            assert "MigrationAdapter()" in adapted_content
            assert ".run_chunking(" in adapted_content

            # Check that legacy imports are replaced in the actual code
            # (not in comments)
            lines = adapted_content.splitlines()
            code_lines = [
                line
                for line in lines
                if not line.strip().startswith("#") and '"""' not in line
            ]
            code_content = "\n".join(code_lines)
            assert "from markdown_chunker_v2 import" not in code_content

    def test_generate_adapted_path(self):
        """Test generation of adapted file paths."""
        test_cases = [
            ("tests/test_basic.py", "tests/test_basic_adapted.py"),
            ("test_example.py", "test_example_adapted.py"),
            ("tests/test_already_adapted.py", "tests/test_already_adapted.py"),
        ]

        for original, expected in test_cases:
            result = self.adapter._generate_adapted_path(original)
            assert (
                result == expected
            ), f"Failed for {original}: got {result}, expected {expected}"


class TestFileManager:
    """Unit tests for FileManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.file_manager = FileManager(self.config)

    def test_remove_file_success(self):
        """Test successful file removal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.config.create_backups = False

            # Create test file
            test_file = os.path.join(temp_dir, "test_remove.py")
            with open(test_file, "w") as f:
                f.write("def test_example(): pass")

            # Remove file
            result = self.file_manager.remove_file(test_file)

            assert result is True, "Removal should succeed"
            assert not os.path.exists(test_file), "File should be removed"

    def test_remove_file_with_backup(self):
        """Test file removal with backup creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.config.backup_directory = os.path.join(temp_dir, ".backup")
            self.config.create_backups = True

            # Create test file
            test_file = os.path.join(temp_dir, "test_backup.py")
            content = "def test_example(): pass"
            with open(test_file, "w") as f:
                f.write(content)

            # Remove file
            result = self.file_manager.remove_file(test_file)

            assert result is True, "Removal should succeed"
            assert not os.path.exists(test_file), "Original file should be removed"

            # Check backup was created
            backup_path = os.path.join(self.config.backup_directory, "test_backup.py")
            assert os.path.exists(backup_path), "Backup should be created"

            with open(backup_path, "r") as f:
                backup_content = f.read()
            assert backup_content == content, "Backup should have same content"

    def test_remove_nonexistent_file(self):
        """Test removal of non-existent file."""
        nonexistent_file = "/tmp/does_not_exist.py"

        result = self.file_manager.remove_file(nonexistent_file)

        assert result is False, "Should return False for non-existent file"

    def test_update_makefile_references(self):
        """Test updating Makefile references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir

            # Create Makefile
            makefile_path = os.path.join(temp_dir, "Makefile")
            makefile_content = """
test:
\tpython -m pytest test_remove_me.py test_keep.py

test-all:
\tpython -m pytest tests/test_remove_me.py tests/
"""
            with open(makefile_path, "w") as f:
                f.write(makefile_content)

            # Update references
            removed_file = "tests/test_remove_me.py"
            changes = self.file_manager.update_makefile_references(removed_file)

            assert len(changes) > 0, "Should make changes to Makefile"

            # Verify Makefile was updated
            with open(makefile_path, "r") as f:
                updated_content = f.read()

            assert (
                "test_remove_me.py" not in updated_content
            ), "References should be removed"
            assert "test_keep.py" in updated_content, "Other references should remain"

    def test_dry_run_mode(self):
        """Test dry run mode doesn't actually remove files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.config.dry_run = True

            # Create test file
            test_file = os.path.join(temp_dir, "test_dry_run.py")
            with open(test_file, "w") as f:
                f.write("def test_example(): pass")

            # Try to remove file in dry run mode
            result = self.file_manager.remove_file(test_file)

            assert result is True, "Should report success in dry run"
            assert os.path.exists(test_file), "File should still exist in dry run"


class TestTestProcessor:
    """Unit tests for TestProcessor integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = CleanupConfig.from_project_root("/tmp")
        self.processor = TestProcessor(self.config)

    def test_remove_redundant_tests_integration(self):
        """Test integration of redundant test removal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.config.project_root = temp_dir
            self.config.create_backups = False

            # Create test files
            test_files = ["test_redundant_1.py", "test_redundant_2.py"]
            for test_file in test_files:
                full_path = os.path.join(temp_dir, test_file)
                with open(full_path, "w") as f:
                    f.write(
                        """
def test_example():
    assert isinstance(42, int)
    assert True
"""
                    )

            # Create duplicate report
            duplicate_report = DuplicateReport(
                duplicate_pairs=[
                    ("test_redundant_1.py", "test_migration_1.py"),
                    ("test_redundant_2.py", "test_migration_2.py"),
                ],
                redundant_files=[os.path.join(temp_dir, f) for f in test_files],
                unique_coverage_areas=["chunking"],
            )

            # Execute removal
            removal_report = self.processor.remove_redundant_tests(duplicate_report)

            # Verify results
            assert len(removal_report.removed_files) == 2, "Should remove both files"
            assert (
                len(removal_report.preserved_assertions) > 0
            ), "Should preserve assertions"

            # Verify files are actually removed
            for test_file in test_files:
                full_path = os.path.join(temp_dir, test_file)
                assert not os.path.exists(
                    full_path
                ), f"File should be removed: {test_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
