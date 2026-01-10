"""
Property-based tests for infrastructure updater components.

These tests validate universal correctness properties of the infrastructure
update system.
"""

import os
import tempfile
from typing import List

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from .config import CleanupConfig
from .updater import (
    ChangeReport,
    DocumentationUpdater,
    InfrastructureUpdater,
    MakefileUpdater,
    PytestConfigUpdater,
)


@st.composite
def generate_makefile_content(draw):
    """Generate realistic Makefile content for testing."""
    targets = draw(
        st.lists(
            st.sampled_from(
                [
                    "test:\n\tpython -m pytest tests/",
                    "test-all:\n\tpython -m pytest tests/ -v",
                    "test-unit:\n\tpython -m pytest tests/test_unit_*.py",
                    "test-integration:\n\tpython -m pytest tests/test_integration_*.py",
                    "lint:\n\tflake8 .",
                    "clean:\n\trm -rf __pycache__",
                ]
            ),
            min_size=2,
            max_size=6,
        )
    )

    return "\n\n".join(targets)


@st.composite
def generate_file_lists(draw):
    """Generate lists of removed and adapted files."""
    removed_files = draw(
        st.lists(
            st.sampled_from(
                [
                    "tests/test_legacy_1.py",
                    "tests/test_legacy_2.py",
                    "tests/test_redundant.py",
                    "tests/old/test_deprecated.py",
                ]
            ),
            min_size=0,
            max_size=4,
        )
    )

    adapted_files = draw(
        st.lists(
            st.sampled_from(
                [
                    "tests/test_valuable_adapted.py",
                    "tests/test_important_adapted.py",
                    "tests/test_unique_adapted.py",
                ]
            ),
            min_size=0,
            max_size=3,
        )
    )

    return removed_files, adapted_files


# Property 4: Infrastructure Update Consistency
@given(generate_file_lists())
@settings(max_examples=20, deadline=5000)
def test_property_4_infrastructure_update_consistency(file_lists):
    """
    Property 4: Infrastructure Update Consistency

    For any changes made to the test suite, the infrastructure updates should correctly
    modify pytest configuration, update Makefile targets, and ensure test discovery
    works with the new structure.

    Validates: Requirements 4.2, 4.3, 4.4, 4.5
    """
    removed_files, adapted_files = file_lists

    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        updater = InfrastructureUpdater(config)

        # Create initial Makefile
        makefile_content = """
test:
\tpython -m pytest tests/test_legacy_1.py tests/test_legacy_2.py

test-all:
\tpython -m pytest tests/

lint:
\tflake8 .
"""
        makefile_path = os.path.join(temp_dir, "Makefile")
        with open(makefile_path, "w") as f:
            f.write(makefile_content)

        # Create initial pytest.ini
        pytest_ini_content = """[tool:pytest]
testpaths = tests
addopts = -v
"""
        pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
        with open(pytest_ini_path, "w") as f:
            f.write(pytest_ini_content)

        # Execute infrastructure updates
        updater.update_makefile(removed_files, adapted_files)

        excluded_dirs = ["tests/legacy_removed", "tests/old"] if removed_files else []
        updater.update_pytest_config(excluded_dirs)

        # Property: Makefile should be updated consistently
        if os.path.exists(makefile_path):
            with open(makefile_path, "r") as f:
                updated_makefile = f.read()

            # Removed files should not be referenced in Makefile
            for removed_file in removed_files:
                file_name = os.path.basename(removed_file)
                assert (
                    file_name not in updated_makefile
                ), f"Removed file {file_name} still referenced in Makefile"

        # Property: pytest.ini should be updated consistently
        if os.path.exists(pytest_ini_path):
            with open(pytest_ini_path, "r") as f:
                updated_pytest_ini = f.read()

            # Should contain ignore patterns for excluded directories
            for excluded_dir in excluded_dirs:
                if excluded_dir:  # Only check non-empty directories
                    assert (
                        "--ignore=" in updated_pytest_ini
                        or excluded_dir in updated_pytest_ini
                    ), f"pytest.ini should reference excluded directory {excluded_dir}"

        # Property: Updates should be idempotent
        # Running updates again should not cause additional changes
        original_makefile = (
            open(makefile_path, "r").read() if os.path.exists(makefile_path) else ""
        )
        original_pytest = (
            open(pytest_ini_path, "r").read() if os.path.exists(pytest_ini_path) else ""
        )

        # Run updates again
        updater.update_makefile(removed_files, adapted_files)
        updater.update_pytest_config(excluded_dirs)

        final_makefile = (
            open(makefile_path, "r").read() if os.path.exists(makefile_path) else ""
        )
        final_pytest = (
            open(pytest_ini_path, "r").read() if os.path.exists(pytest_ini_path) else ""
        )

        assert (
            original_makefile == final_makefile
        ), "Makefile updates should be idempotent"
        assert (
            original_pytest == final_pytest
        ), "pytest.ini updates should be idempotent"


@given(
    st.lists(
        st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
        ),
        min_size=1,
        max_size=5,
    )
)
@settings(max_examples=15, deadline=5000)
def test_property_makefile_reference_removal(file_names: List[str]):
    """
    Property: Makefile Reference Removal

    For any file removed from the test suite, all references to that file
    should be removed from the Makefile while preserving other content.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        makefile_updater = MakefileUpdater(config)

        # Create Makefile with file references
        test_files = [f"test_{name}.py" for name in file_names]
        makefile_content = f"""
test:
\tpython -m pytest {' '.join(test_files)} tests/test_keep.py

test-all:
\tpython -m pytest tests/

other-target:
\techo "This should be preserved"
"""

        makefile_path = os.path.join(temp_dir, "Makefile")
        with open(makefile_path, "w") as f:
            f.write(makefile_content)

        # Remove references to some files
        files_to_remove = test_files[: len(test_files) // 2] if test_files else []
        files_to_keep = test_files[len(test_files) // 2 :] if test_files else []

        makefile_updater.update_targets(files_to_remove, [])

        # Property: Removed files should not be referenced
        with open(makefile_path, "r") as f:
            updated_content = f.read()

        for removed_file in files_to_remove:
            assert (
                removed_file not in updated_content
            ), f"Removed file {removed_file} still in Makefile"

        # Property: Kept files should still be referenced
        for kept_file in files_to_keep:
            if kept_file:  # Only check non-empty file names
                assert (
                    kept_file in updated_content
                ), f"Kept file {kept_file} was incorrectly removed"

        # Property: Other content should be preserved
        assert "test_keep.py" in updated_content, "Unrelated files should be preserved"
        assert (
            "other-target:" in updated_content
        ), "Unrelated targets should be preserved"
        assert (
            "This should be preserved" in updated_content
        ), "Unrelated content should be preserved"


@given(
    st.lists(
        st.text(
            min_size=1,
            max_size=15,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
        ),
        min_size=0,
        max_size=4,
    )
)
@settings(max_examples=15, deadline=5000)
def test_property_pytest_config_exclusion(excluded_dirs: List[str]):
    """
    Property: Pytest Configuration Exclusion

    For any directories excluded from test discovery, the pytest configuration
    should be updated to ignore those directories while preserving other settings.
    """
    # Filter out empty strings and duplicates
    excluded_dirs = list(
        set(dir_name for dir_name in excluded_dirs if dir_name.strip())
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        pytest_updater = PytestConfigUpdater(config)

        # Create initial pytest.ini
        initial_content = """[tool:pytest]
testpaths = tests
addopts = -v --tb=short
python_files = test_*.py
"""
        pytest_ini_path = os.path.join(temp_dir, "pytest.ini")
        with open(pytest_ini_path, "w") as f:
            f.write(initial_content)

        # Update configuration
        pytest_updater.update_config(excluded_dirs)

        # Property: Configuration should be updated
        with open(pytest_ini_path, "r") as f:
            updated_content = f.read()

        # Property: Excluded directories should be ignored
        for excluded_dir in excluded_dirs:
            if excluded_dir:  # Only check non-empty directories
                assert (
                    f"--ignore={excluded_dir}" in updated_content
                    or excluded_dir in updated_content
                ), f"Excluded directory {excluded_dir} should be in ignore patterns"

        # Property: Original settings should be preserved
        assert (
            "testpaths = tests" in updated_content
        ), "Original testpaths should be preserved"
        assert (
            "python_files = test_*.py" in updated_content
        ), "Original python_files should be preserved"

        # Property: Configuration should remain valid
        assert (
            "[tool:pytest]" in updated_content or "[pytest]" in updated_content
        ), "Should have valid pytest section header"


@given(st.integers(min_value=0, max_value=10), st.integers(min_value=0, max_value=10))
@settings(max_examples=20, deadline=5000)
def test_property_documentation_update_completeness(num_removed: int, num_adapted: int):
    """
    Property: Documentation Update Completeness

    For any test suite changes, documentation updates should accurately reflect
    the changes and provide complete information about the new test structure.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CleanupConfig.from_project_root(temp_dir)
        doc_updater = DocumentationUpdater(config)

        # Create initial README.md
        readme_content = """# Test Project

This is a test project.

## Installation

Install dependencies...

## Usage

Use the project...
"""
        readme_path = os.path.join(temp_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme_content)

        # Create change report
        from .models import AdaptedTest, RemovedTest

        changes = ChangeReport(
            removed_tests=[
                RemovedTest(
                    file_path=f"test_removed_{i}.py",
                    test_functions=[],
                    removal_reason="redundant",
                )
                for i in range(num_removed)
            ],
            adapted_tests=[
                AdaptedTest(
                    original_path=f"test_adapted_{i}.py",
                    adapted_path=f"test_adapted_{i}.py",
                    changes_made=["migration adapter integration"],
                    adaptation_success=True,
                )
                for i in range(num_adapted)
            ],
        )

        # Update documentation
        doc_changes = doc_updater.update_docs(changes)

        # Property: Documentation should be updated
        assert len(doc_changes) > 0, "Should make documentation changes"

        # Property: README should contain testing information
        with open(readme_path, "r") as f:
            updated_readme = f.read()

        assert "## Testing" in updated_readme, "README should have Testing section"
        assert "make test" in updated_readme, "README should mention test commands"

        # Property: Should mention the number of removed tests
        if num_removed > 0:
            assert (
                str(num_removed) in updated_readme
            ), f"Should mention {num_removed} removed tests"

        # Property: TESTING.md should be created
        testing_path = os.path.join(temp_dir, "TESTING.md")
        assert os.path.exists(testing_path), "Should create TESTING.md"

        with open(testing_path, "r") as f:
            testing_content = f.read()

        assert (
            "# Testing Documentation" in testing_content
        ), "TESTING.md should have proper header"
        assert "Test Suite Overview" in testing_content, "Should have overview section"
        assert (
            str(num_removed) in testing_content
        ), f"Should mention {num_removed} removed tests"
        assert (
            str(num_adapted) in testing_content
        ), f"Should mention {num_adapted} adapted tests"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
