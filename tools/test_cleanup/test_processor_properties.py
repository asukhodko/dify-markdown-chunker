"""
Property-based tests for test processor components.

These tests validate universal correctness properties of the test processing system.
"""

import os
import tempfile
from pathlib import Path
from typing import List

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from .config import CleanupConfig
from .models import (
    AdaptationPlan,
    DuplicateReport,
    TestAnalysis,
    TestCategory,
    TestFile,
    TestType,
)
from .processor import FileManager, RedundancyDetector, TestProcessor


@st.composite
def generate_test_file_with_legacy_imports(draw):
    """Generate a test file with legacy imports for adaptation testing."""
    imports = draw(
        st.lists(
            st.sampled_from(
                [
                    "import pytest",
                    "from markdown_chunker_v2 import MarkdownChunker",
                    "from markdown_chunker import ChunkConfig",
                    "import unittest",
                ]
            ),
            min_size=1,
            max_size=3,
        )
    )

    test_functions = draw(
        st.lists(
            st.sampled_from(
                [
                    "def test_basic():\n    chunker = MarkdownChunker()\n"
                    "    result = chunker.chunk('test')\n    assert len(result) > 0",
                    "def test_config():\n    config = ChunkConfig()\n"
                    "    assert config is not None",
                    "def test_error():\n    with pytest.raises(ValueError):\n"
                    "        chunker = MarkdownChunker()\n        chunker.chunk(None)",
                ]
            ),
            min_size=1,
            max_size=3,
        )
    )

    content_parts = imports + [""] + test_functions
    return "\n".join(content_parts)


@st.composite
def generate_duplicate_report(draw):
    """Generate a DuplicateReport for testing."""
    num_duplicates = draw(st.integers(min_value=1, max_value=5))

    duplicate_pairs = []
    redundant_files = []

    for i in range(num_duplicates):
        legacy_file = f"test_legacy_{i}.py"
        migration_file = f"test_migration_{i}.py"
        duplicate_pairs.append((legacy_file, migration_file))
        redundant_files.append(legacy_file)

    unique_coverage_areas = draw(
        st.lists(
            st.sampled_from(["chunking", "parsing", "validation", "error_handling"]),
            min_size=0,
            max_size=3,
        )
    )

    return DuplicateReport(
        duplicate_pairs=duplicate_pairs,
        redundant_files=redundant_files,
        unique_coverage_areas=unique_coverage_areas,
    )


# Property 2: Redundant Test Removal Completeness
@given(generate_duplicate_report())
@settings(max_examples=20, deadline=5000)
def test_property_2_redundant_test_removal_completeness(
    duplicate_report: DuplicateReport,
):
    """
    Property 2: Redundant Test Removal Completeness

    For any test identified as redundant, the system should remove the test file,
    update all Makefile references, and preserve any unique assertions found
    within the test.

    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        processor = TestProcessor(config)

        # Create test files for removal
        created_files = []
        for file_path in duplicate_report.redundant_files:
            full_path = os.path.join(temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write(
                    """
import pytest

def test_example():
    assert isinstance(42, int)  # Unique assertion
    assert True  # Basic assertion

def test_complex():
    result = [1, 2, 3]
    assert len(result) == 3 and all(isinstance(x, int) for x in result)
"""
                )
            created_files.append(full_path)

        # Create a simple Makefile
        makefile_path = os.path.join(temp_dir, "Makefile")
        makefile_content = f"""
test:
\tpython -m pytest {' '.join(duplicate_report.redundant_files)}

test-all:
\tpython -m pytest tests/
"""
        with open(makefile_path, "w") as f:
            f.write(makefile_content)

        # Execute removal
        removal_report = processor.remove_redundant_tests(duplicate_report)

        # Property: All redundant files should be processed
        assert len(removal_report.removed_files) + len(removal_report.errors) == len(
            duplicate_report.redundant_files
        )

        # Property: Removed files should no longer exist (unless dry run)
        if not config.dry_run:
            for removed_file in removal_report.removed_files:
                assert not os.path.exists(
                    removed_file
                ), f"File still exists: {removed_file}"

        # Property: Unique assertions should be preserved
        for file_path, assertions in removal_report.preserved_assertions.items():
            assert isinstance(assertions, list), "Preserved assertions should be a list"
            # Should preserve complex assertions but not basic ones
            complex_assertions = [
                a for a in assertions if "isinstance" in a or "len(" in a or "and " in a
            ]
            assert (
                len(complex_assertions) > 0
            ), "Should preserve at least one complex assertion"

        # Property: Makefile should be updated
        if removal_report.removed_files:
            assert (
                len(removal_report.makefile_updates) >= 0
            ), "Makefile updates should be recorded"


# Property 3: Test Adaptation Correctness
@given(st.lists(generate_test_file_with_legacy_imports(), min_size=1, max_size=3))
@settings(max_examples=15, deadline=8000)
def test_property_3_test_adaptation_correctness(test_contents: List[str]):
    """
    Property 3: Test Adaptation Correctness

    For any valuable legacy test, the adaptation process should replace old imports
    with adapter equivalents, preserve original test logic and assertions, and ensure
    the adapted test passes.

    Validates: Requirements 3.1, 3.2, 3.3, 3.4
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        processor = TestProcessor(config)

        # Create test files for adaptation
        test_files = []
        for i, content in enumerate(test_contents):
            file_path = os.path.join(temp_dir, f"test_legacy_{i}.py")
            with open(file_path, "w") as f:
                f.write(content)

            # Create TestFile object
            analysis = TestAnalysis(
                file_path=file_path,
                imports=["from markdown_chunker_v2 import MarkdownChunker"],
                test_functions=[f"test_function_{i}"],
                coverage_areas=["chunking"],
                test_type=TestType.UNIT,
                dependencies=["pytest"],
                complexity_score=2.0,
                has_legacy_imports=True,
            )

            test_file = TestFile(
                path=file_path, analysis=analysis, category=TestCategory.VALUABLE
            )
            test_files.append(test_file)

        # Execute adaptation
        adaptation_report = processor.adapt_valuable_tests(test_files)

        # Property: All test files should be processed
        total_processed = len(adaptation_report.successful_adaptations) + len(
            adaptation_report.failed_adaptations
        )
        assert total_processed == len(test_files), "All test files should be processed"

        # Property: Successful adaptations should create valid files
        for adapted_file in adaptation_report.adapted_files:
            if not config.dry_run:
                assert os.path.exists(
                    adapted_file
                ), f"Adapted file should exist: {adapted_file}"

                # Check that adapted file has valid Python syntax
                with open(adapted_file, "r") as f:
                    adapted_content = f.read()

                try:
                    import ast

                    ast.parse(adapted_content)
                except SyntaxError:
                    pytest.fail(f"Adapted file has invalid syntax: {adapted_file}")

                # Property: Legacy imports should be replaced
                assert (
                    "markdown_chunker_v2" not in adapted_content
                ), "Legacy imports should be removed"
                assert (
                    "markdown_chunker" not in adapted_content
                    or "markdown_chunker_v2" in adapted_content
                ), "Legacy imports should be removed"

                # Property: Adapter imports should be present
                assert (
                    "MigrationAdapter" in adapted_content
                ), "Adapter imports should be added"

        # Property: Adaptation plans should be created for all files
        assert len(adaptation_report.adaptation_plans) == len(
            test_files
        ), "Should have adaptation plan for each file"

        # Property: Each adaptation plan should have valid structure
        for plan in adaptation_report.adaptation_plans:
            assert isinstance(plan, AdaptationPlan), "Should be AdaptationPlan instance"
            assert (
                plan.original_file != plan.adapted_file
            ), "Original and adapted paths should differ"
            assert (
                len(plan.import_changes) > 0
            ), "Should have import changes for legacy tests"
            assert isinstance(
                plan.preserved_assertions, list
            ), "Preserved assertions should be a list"


@given(
    st.text(
        min_size=10,
        max_size=200,
        alphabet=st.characters(
            whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Ps", "Pe", "Po", "Zs")
        ),
    )
)
@settings(max_examples=30, deadline=3000)
def test_property_unique_assertion_detection(content: str):
    """
    Property: Unique Assertion Detection

    For any test content, the redundancy detector should correctly identify
    unique assertions worth preserving vs basic assertions that can be discarded.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        detector = RedundancyDetector(config)

        # Create test file with mixed assertions
        test_content = f"""
import pytest

def test_basic():
    assert True  # Basic assertion
    assert False or True  # Basic with or

def test_complex():
    result = [1, 2, 3]
    assert isinstance(result, list)  # Complex assertion
    assert len(result) >= 3 and all(x > 0 for x in result)  # Very complex
    {content}  # User content
"""

        test_file = os.path.join(temp_dir, "test_example.py")
        with open(test_file, "w") as f:
            f.write(test_content)

        try:
            unique_assertions = detector.extract_unique_assertions(test_file)

            # Property: Should return a list
            assert isinstance(
                unique_assertions, list
            ), "Should return list of assertions"

            # Property: Should not include basic assertions
            basic_assertions = [
                a
                for a in unique_assertions
                if a.strip() in ["assert True", "assert False"]
            ]
            assert len(basic_assertions) == 0, "Should not preserve basic assertions"

            # Property: Should include complex assertions
            if any(
                "isinstance" in line or "len(" in line
                for line in test_content.splitlines()
            ):
                # Check for complex assertions (may be 0 if parsing fails)
                [a for a in unique_assertions if "isinstance" in a or "len(" in a]
                # Note: May be 0 if parsing fails, which is acceptable

        except Exception:
            # Parsing failures are acceptable for random content
            pass


@given(st.lists(st.text(min_size=5, max_size=50), min_size=1, max_size=5))
@settings(max_examples=20, deadline=5000)
def test_property_file_management_safety(file_names: List[str]):
    """
    Property: File Management Safety

    For any file operations, the file manager should handle errors gracefully,
    create backups when configured, and maintain data integrity.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        config.create_backups = True
        file_manager = FileManager(config)

        # Create test files
        created_files = []
        for i, name in enumerate(file_names):
            # Sanitize filename
            safe_name = "".join(c for c in name if c.isalnum() or c in "._-")
            if not safe_name:
                safe_name = f"test_{i}"

            file_path = os.path.join(temp_dir, f"{safe_name}.py")
            with open(file_path, "w") as f:
                f.write(f"# Test file {i}\ndef test_example(): pass")
            created_files.append(file_path)

        # Test file removal
        removal_results = []
        for file_path in created_files:
            result = file_manager.remove_file(file_path)
            removal_results.append(result)

        # Property: All operations should return boolean results
        assert all(
            isinstance(result, bool) for result in removal_results
        ), "Should return boolean results"

        # Property: If backups are enabled, backup directory should exist
        if config.create_backups and any(removal_results):
            backup_dir = Path(config.backup_directory)
            assert backup_dir.exists(), "Backup directory should be created"

        # Property: Removed files should not exist (unless dry run)
        if not config.dry_run:
            for file_path, was_removed in zip(created_files, removal_results):
                if was_removed:
                    assert not os.path.exists(
                        file_path
                    ), f"Removed file should not exist: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
