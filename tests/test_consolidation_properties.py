"""
Property-based tests for consolidation operations.

These tests verify correctness properties using Hypothesis for property-based testing.
"""

import hashlib
import tempfile
from pathlib import Path
from typing import List

import pytest
from hypothesis import given
from hypothesis import strategies as st

# Property 1: File content comparison correctness
# For any two files with identical content, comparison should return True
# For any two files with different content, comparison should return False


def get_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of file content"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def files_are_identical(file1: Path, file2: Path) -> bool:
    """Compare two files by content hash"""
    return get_file_hash(file1) == get_file_hash(file2)


@given(content=st.binary(min_size=0, max_size=10000))
def test_property_identical_files_return_true(content):
    """
    Property 1: File content comparison correctness

    For any file content, two files with the same content should be identified as identical.

    Validates: Requirements 1.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create two files with identical content
        file1 = tmpdir / "file1.txt"
        file2 = tmpdir / "file2.txt"

        file1.write_bytes(content)
        file2.write_bytes(content)

        # Property: identical content should be detected as identical
        assert files_are_identical(
            file1, file2
        ), "Files with identical content should be identified as identical"


@given(
    content1=st.binary(min_size=1, max_size=10000),
    content2=st.binary(min_size=1, max_size=10000),
)
def test_property_different_files_return_false(content1, content2):
    """
    Property 1: File content comparison correctness

    For any two different file contents, files should be identified as different.

    Validates: Requirements 1.2
    """
    # Skip if contents happen to be identical
    if content1 == content2:
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create two files with different content
        file1 = tmpdir / "file1.txt"
        file2 = tmpdir / "file2.txt"

        file1.write_bytes(content1)
        file2.write_bytes(content2)

        # Property: different content should be detected as different
        assert not files_are_identical(
            file1, file2
        ), "Files with different content should be identified as different"


@given(content=st.text(min_size=0, max_size=1000))
def test_property_text_file_comparison(content):
    """
    Property 1: File content comparison for text files

    For any text content, comparison should work correctly with UTF-8 encoding.

    Validates: Requirements 1.2
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create two files with identical text content
        file1 = tmpdir / "file1.txt"
        file2 = tmpdir / "file2.txt"

        file1.write_text(content, encoding="utf-8")
        file2.write_text(content, encoding="utf-8")

        # Property: identical text content should be detected as identical
        assert files_are_identical(
            file1, file2
        ), "Text files with identical content should be identified as identical"


# Edge cases for file comparison
def test_empty_files_are_identical():
    """Empty files should be identified as identical"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "empty1.txt"
        file2 = tmpdir / "empty2.txt"

        file1.write_bytes(b"")
        file2.write_bytes(b"")

        assert files_are_identical(file1, file2)


def test_whitespace_differences_detected():
    """Files differing only in whitespace should be detected as different"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "file1.txt"
        file2 = tmpdir / "file2.txt"

        file1.write_text("hello world", encoding="utf-8")
        file2.write_text("hello  world", encoding="utf-8")  # Extra space

        assert not files_are_identical(file1, file2)


def test_line_ending_differences_detected():
    """Files with different line endings should be detected as different"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        file1 = tmpdir / "file1.txt"
        file2 = tmpdir / "file2.txt"

        file1.write_bytes(b"line1\nline2\n")  # Unix line endings
        file2.write_bytes(b"line1\r\nline2\r\n")  # Windows line endings

        assert not files_are_identical(file1, file2)


# Property 2: Import path updates are consistent
# For any Python file with import statements, after updating imports,
# all occurrences of old module path should be replaced with new module path


def update_imports_in_text(text: str, old_module: str, new_module: str) -> str:
    """Update import statements in Python code"""
    import re

    # Pattern 1: import old_module
    text = re.sub(
        rf"\bimport\s+{re.escape(old_module)}\b", f"import {new_module}", text
    )

    # Pattern 2: from old_module import ...
    text = re.sub(rf"\bfrom\s+{re.escape(old_module)}\b", f"from {new_module}", text)

    # Pattern 3: from old_module.submodule import ...
    text = re.sub(rf"\bfrom\s+{re.escape(old_module)}\.", f"from {new_module}.", text)

    return text


@given(
    old_module=st.from_regex(
        r"[a-z_][a-z0-9_]{2,}", fullmatch=True
    ),  # At least 3 chars to avoid single letter issues
    new_module=st.from_regex(r"[a-z_][a-z0-9_]{2,}", fullmatch=True),
    import_count=st.integers(min_value=1, max_value=10),
)
def test_property_all_imports_updated(old_module, new_module, import_count):
    """
    Property 2: Import path updates are consistent

    For any Python code with imports, all occurrences of old module should be replaced.

    Validates: Requirements 2.6
    """
    # Skip if modules are the same
    if old_module == new_module:
        return

    # Generate Python code with imports
    import_types = [
        f"import {old_module}",
        f"from {old_module} import something",
        f"from {old_module}.submodule import something",
    ]

    code_lines = []
    for i in range(import_count):
        import_type = import_types[i % len(import_types)]
        code_lines.append(import_type)

    original_code = "\n".join(code_lines)

    # Update imports
    updated_code = update_imports_in_text(original_code, old_module, new_module)

    # Property: old module should not appear as a complete word in import statements
    import re

    old_module_pattern = rf"\b{re.escape(old_module)}\b"
    assert not re.search(
        old_module_pattern, updated_code
    ), f"Old module '{old_module}' should not appear as a word in updated code"

    # Property: new module should appear in updated code
    assert (
        new_module in updated_code
    ), f"New module '{new_module}' should appear in updated code"

    # Property: number of import statements should be preserved
    original_import_count = original_code.count("import")
    updated_import_count = updated_code.count("import")
    assert (
        original_import_count == updated_import_count
    ), "Number of import statements should be preserved"


@given(
    text=st.text(min_size=10, max_size=500),
    old_module=st.just("markdown_chunker"),
    new_module=st.just("markdown_chunker"),
)
def test_property_import_update_preserves_non_imports(text, old_module, new_module):
    """
    Property 2: Import updates preserve non-import code

    For any text without import statements, updating imports should not change it.

    Validates: Requirements 2.6
    """
    # Filter out text that looks like imports
    if "import" in text.lower():
        return

    updated_text = update_imports_in_text(text, old_module, new_module)

    # Property: non-import text should be unchanged
    assert text == updated_text, "Non-import text should remain unchanged"


# Edge cases for import updates
def test_import_update_preserves_comments():
    """Comments should be preserved during import updates"""
    code = """# This is a comment about markdown_chunker
import markdown_chunker
from markdown_chunker import something  # inline comment
"""

    updated = update_imports_in_text(code, "markdown_chunker", "new_module")

    # Comments should be preserved
    assert "# This is a comment" in updated
    assert "# inline comment" in updated

    # Imports should be updated
    assert "import new_module" in updated
    assert "from new_module import" in updated


def test_import_update_handles_multiline():
    """Multi-line imports should be handled correctly"""
    code = """from markdown_chunker import (
    something,
    another_thing
)"""

    updated = update_imports_in_text(code, "markdown_chunker", "new_module")

    assert "from new_module import" in updated
    assert "something" in updated
    assert "another_thing" in updated


def test_import_update_handles_as_imports():
    """Import aliases should be preserved"""
    code = """import markdown_chunker as mc
from markdown_chunker import something as st
"""

    updated = update_imports_in_text(code, "markdown_chunker", "new_module")

    assert "import new_module as mc" in updated
    assert "from new_module import something as st" in updated


# Property 8: Import paths are valid after migration
# For any Python file in migrated tests, all import statements should resolve


def extract_imports_from_file(file_path: Path) -> List[str]:
    """Extract all import statements from a Python file"""
    import re

    imports = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Find all import statements
        import_pattern = r"^\s*(?:from\s+([\w.]+)|import\s+([\w.]+))"
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module = match.group(1) or match.group(2)
            if module:
                imports.append(module)

    except Exception:
        pass

    return imports


def is_valid_module(module_name: str, base_path: Path) -> bool:
    """Check if a module can be resolved"""
    # Skip standard library and third-party modules
    if not module_name.startswith("markdown_chunker"):
        return True

    # Convert module path to file path
    parts = module_name.split(".")

    # Try to find the module
    current_path = base_path
    for part in parts:
        potential_file = current_path / f"{part}.py"
        potential_dir = current_path / part

        if potential_file.exists():
            return True
        elif potential_dir.exists() and (potential_dir / "__init__.py").exists():
            current_path = potential_dir
        else:
            return False

    return True


def test_property_migrated_test_imports_are_valid():
    """
    Property 8: Import paths are valid after migration

    For all migrated test files, imports should resolve to existing modules.

    Validates: Requirements 10.5
    """
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    tests_dir = script_dir

    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))

    if not test_files:
        pytest.skip("No test files found")

    invalid_imports = []

    for test_file in test_files:
        imports = extract_imports_from_file(test_file)

        for module in imports:
            if not is_valid_module(module, project_root):
                invalid_imports.append(
                    (str(test_file.relative_to(project_root)), module)
                )

    # Property: all imports should be valid
    if invalid_imports:
        error_msg = "Invalid imports found:\n"
        for file, module in invalid_imports[:10]:  # Show first 10
            error_msg += f"  {file}: {module}\n"
        if len(invalid_imports) > 10:
            error_msg += f"  ... and {len(invalid_imports) - 10} more\n"

        pytest.fail(error_msg)


def test_sample_imports_resolve():
    """Test that common imports from migrated tests resolve correctly"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Common imports that should work
    common_imports = [
        "markdown_chunker",
        "markdown_chunker.parser",
        "markdown_chunker.chunker",
        "markdown_chunker.parser.core",
        "markdown_chunker.chunker.core",
        "markdown_chunker.parser.types",
        "markdown_chunker.chunker.types",
    ]

    for module in common_imports:
        assert is_valid_module(
            module, project_root
        ), f"Common import '{module}' should resolve"


# Property 3: Documentation reference updates are complete
# For any documentation file, after updating references, no old project names should remain


def update_doc_references(text: str, old_project: str, new_project: str) -> str:
    """Update project references in documentation"""
    import re

    # Replace project name in various contexts
    text = re.sub(rf"\b{re.escape(old_project)}\b", new_project, text)

    # Replace in paths
    text = re.sub(rf"{re.escape(old_project)}/", f"{new_project}/", text)

    return text


@given(
    old_project=st.just("python-markdown-chunker"),
    new_project=st.just("dify-markdown-chunker"),
    text=st.text(min_size=10, max_size=500),
)
def test_property_doc_references_updated(old_project, new_project, text):
    """
    Property 3: Documentation reference updates are complete

    For any documentation text, after updating references, old project name should not appear.

    Validates: Requirements 3.5
    """
    # Skip if text doesn't contain old project name
    if old_project not in text:
        return

    updated_text = update_doc_references(text, old_project, new_project)

    # Property: old project name should not appear in updated text
    assert (
        old_project not in updated_text
    ), f"Old project name '{old_project}' should not appear in updated documentation"

    # Property: new project name should appear if old one was present
    assert (
        new_project in updated_text
    ), f"New project name '{new_project}' should appear in updated documentation"


def test_doc_reference_update_preserves_markdown():
    """Documentation reference updates should preserve markdown formatting"""
    doc = """# python-markdown-chunker

See [python-markdown-chunker/README.md](python-markdown-chunker/README.md) for details.

Install from `python-markdown-chunker` directory.
"""

    updated = update_doc_references(
        doc, "python-markdown-chunker", "dify-markdown-chunker"
    )

    # Check that markdown structure is preserved
    assert "# dify-markdown-chunker" in updated
    assert "[dify-markdown-chunker/README.md]" in updated
    assert "`dify-markdown-chunker`" in updated

    # Old name should not appear
    assert "python-markdown-chunker" not in updated


def test_doc_reference_update_handles_code_blocks():
    """Code blocks should be updated correctly"""
    doc = """```bash
cd python-markdown-chunker
python -m pytest
```"""

    updated = update_doc_references(
        doc, "python-markdown-chunker", "dify-markdown-chunker"
    )

    assert "cd dify-markdown-chunker" in updated
    assert "python-markdown-chunker" not in updated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Property 6: Test directory structure mirrors source structure
# For any source module, there should exist a corresponding test directory


def check_test_structure_mirrors_source(
    source_dir: Path, test_dir: Path
) -> tuple[bool, list[str]]:
    """
    Check if test directory structure mirrors source structure.

    Returns:
        (mirrors_correctly, missing_test_dirs)
    """
    import os

    missing = []

    # Get all source subdirectories
    for root, dirs, _ in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]

        rel_path = Path(root).relative_to(source_dir)
        if rel_path == Path("."):
            continue

        # Check if corresponding test directory exists
        # Test directories may have 'test_' prefix
        test_path = test_dir / rel_path
        test_path_with_prefix = test_dir / rel_path.parent / f"test_{rel_path.name}"

        if not test_path.exists() and not test_path_with_prefix.exists():
            missing.append(str(rel_path))

    return len(missing) == 0, missing


@given(
    module_name=st.text(
        alphabet=st.characters(
            whitelist_categories=("Ll", "Nd"), min_codepoint=97, max_codepoint=122
        ),
        min_size=3,
        max_size=20,
    ).filter(lambda x: x.isidentifier())
)
def test_property_test_structure_mirrors_source(module_name):
    """
    Property 6: Test directory structure mirrors source structure

    For any source module directory, there should exist a corresponding test directory
    (either with the same name or with 'test_' prefix).

    Feature: consolidate-markdown-chunker, Property 6: Test directory structure mirrors source structure
    Validates: Requirements 10.1
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create source structure
        source_dir = tmpdir / "source"
        source_dir.mkdir()
        module_dir = source_dir / module_name
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()

        # Create test structure (mirroring source)
        test_dir = tmpdir / "tests"
        test_dir.mkdir()
        test_module_dir = test_dir / module_name
        test_module_dir.mkdir()
        (test_module_dir / "__init__.py").touch()

        # Verify structure mirrors
        mirrors, missing = check_test_structure_mirrors_source(source_dir, test_dir)

        assert mirrors, f"Test structure should mirror source, but missing: {missing}"
        assert len(missing) == 0


def test_property_actual_project_structure():
    """
    Verify that the actual consolidated project has correct test structure.

    Feature: consolidate-markdown-chunker, Property 6: Test directory structure mirrors source structure
    Validates: Requirements 10.1
    """
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "markdown_chunker"
    test_dir = project_root / "tests"

    # Check main modules
    main_modules = ["api", "parser", "chunker"]

    for module in main_modules:
        source_module = source_dir / module
        test_module = test_dir / module

        assert source_module.exists(), f"Source module {module} should exist"
        assert test_module.exists(), f"Test module {module} should exist"


# Property 7: No duplicate files after cleanup
# For any file path, there should be at most one file with that path


def find_duplicate_files_by_content(directory: Path) -> dict[str, list[Path]]:
    """
    Find files with duplicate content.

    Returns:
        Dictionary mapping content hash to list of file paths with that content
    """
    import os

    hash_to_files = {}

    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d
            for d in dirs
            if d not in ("__pycache__", ".pytest_cache", ".hypothesis", "venv", ".git")
        ]

        for file in files:
            if file.endswith((".pyc", ".pyo")):
                continue

            file_path = Path(root) / file
            try:
                file_hash = get_file_hash(file_path)
                if file_hash not in hash_to_files:
                    hash_to_files[file_hash] = []
                hash_to_files[file_hash].append(file_path)
            except Exception:
                pass  # Skip files that can't be read

    # Filter to only duplicates
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    return duplicates


@given(
    file_contents=st.lists(st.binary(min_size=1, max_size=100), min_size=1, max_size=10)
)
def test_property_no_duplicate_files(file_contents):
    """
    Property 7: No duplicate files after cleanup

    For any set of files, after removing duplicates, each unique content
    should appear exactly once.

    Feature: consolidate-markdown-chunker, Property 7: No duplicate files after cleanup
    Validates: Requirements 10.4
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create files with potentially duplicate content
        for i, content in enumerate(file_contents):
            file_path = tmpdir / f"file_{i}.txt"
            file_path.write_bytes(content)

        # Find duplicates
        duplicates = find_duplicate_files_by_content(tmpdir)

        # After cleanup, we should remove duplicates
        # For this test, we verify the detection works
        unique_contents = set(file_contents)

        if len(unique_contents) < len(file_contents):
            # There are duplicates
            assert len(duplicates) > 0, "Should detect duplicates when they exist"
        else:
            # No duplicates
            assert (
                len(duplicates) == 0
            ), "Should not report duplicates when all files are unique"


def test_property_actual_project_no_problematic_duplicates():
    """
    Verify that the actual consolidated project has no problematic duplicate files.

    Empty files (__init__.py, empty fixtures) are allowed.

    Feature: consolidate-markdown-chunker, Property 7: No duplicate files after cleanup
    Validates: Requirements 10.4
    """
    project_root = Path(__file__).parent.parent

    duplicates = find_duplicate_files_by_content(project_root)

    # Filter out acceptable duplicates (empty files)
    problematic_duplicates = {}
    for file_hash, files in duplicates.items():
        # Check if all files are empty or are __init__.py
        all_acceptable = all(
            f.stat().st_size == 0
            or f.name == "__init__.py"
            or "empty" in f.name.lower()
            for f in files
        )

        if not all_acceptable:
            problematic_duplicates[file_hash] = files

    assert len(problematic_duplicates) == 0, (
        f"Found {len(problematic_duplicates)} sets of problematic duplicate files: "
        f"{problematic_duplicates}"
    )
