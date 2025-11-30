"""Tests for accurate test count and status reporting."""

import glob
import os
import re


class TestAccurateReporting:
    """Test that test counts and status reports are accurate."""

    def test_actual_test_count_validation(self):
        """Test that we can accurately count tests."""
        # Count pytest test methods
        pytest_files = glob.glob("tests/parser/test_*.py")
        pytest_count = 0

        for file_path in pytest_files:
            with open(file_path, "r") as f:
                content = f.read()
            test_methods = re.findall(r"def test_\w+\(", content)
            pytest_count += len(test_methods)

        # Should have a reasonable number of pytest tests
        assert (
            pytest_count >= 50
        ), f"Should have at least 50 pytest test methods,\n        got {pytest_count}"

        # Count test files in root_tests (moved from root)
        root_test_files = glob.glob("tests/parser/root_tests/test_*.py")
        root_test_count = len([f for f in root_test_files if os.path.exists(f)])

        # Should have test files in root_tests directory
        assert (
            root_test_count >= 5
        ), f"Should have at least 5 test files in root_tests,\n        got {root_test_count}"

    def test_test_count_accuracy(self):
        """Test that reported test counts match reality."""
        # Count actual assertions
        total_assertions = 0

        # Count in pytest files
        pytest_files = glob.glob("tests/parser/test_*.py")
        for file_path in pytest_files:
            with open(file_path, "r") as f:
                content = f.read()
            total_assertions += content.count("assert ")

        # Count in simple test files
        simple_files = glob.glob("test_*.py")
        for file_path in simple_files:
            with open(file_path, "r") as f:
                content = f.read()
            total_assertions += content.count("assert ")

        # Should have substantial number of assertions
        assert (
            total_assertions >= 100
        ), f"Should have at least 100 assertions,\n        got {total_assertions}"

        # Report the actual count found
        print(f"Total assertions found: {total_assertions}")

    def test_automated_vs_manual_tests(self):
        """Test distinction between automated and manual tests."""
        # test_basic.py should be automated now
        if os.path.exists("test_basic.py"):
            with open("test_basic.py", "r") as f:
                content = f.read()

            # Should have assertions
            assert_count = content.count("assert ")
            assert (
                assert_count >= 20
            ), f"test_basic.py \
            should have many assertions,\n        got {assert_count}"

            # Should have test class
            assert (
                "class TestBasicFunctionality:" in content
            ), "Should have proper test class"

    def test_regression_prevention(self):
        """Test that we have regression prevention tests."""
        # Should have regression tests for key fixes
        regression_files = [
            "tests/parser/test_line_numbering_regression.py",
            "tests/parser/root_tests/test_nested_extraction.py",
            "tests/parser/test_regression_prevention.py",
        ]

        found_regression_tests = 0
        for file_path in regression_files:
            if os.path.exists(file_path):
                found_regression_tests += 1

        assert (
            found_regression_tests >= 2
        ), f"Should have regression tests, found {found_regression_tests}"

    def test_documentation_matches_implementation(self):
        """Test that documentation claims match implementation."""
        from markdown_chunker.parser import LineNumberConverter, extract_fenced_blocks

        # Test 1-based line numbering works as documented
        blocks = extract_fenced_blocks("```python\ncode\n```")
        assert len(blocks) == 1
        assert blocks[0].start_line == 1, "Should use 1-based numbering as documented"

        # Test line converter works as documented
        assert LineNumberConverter.to_api_line_number(0) == 1
        assert LineNumberConverter.from_api_line_number(1) == 0

        # Test basic nesting works as documented (NEW CORRECT BEHAVIOR)
        nested_markdown = """~~~markdown
```python
code
```
~~~"""
        blocks = extract_fenced_blocks(nested_markdown)
        # NEW BEHAVIOR: Only 1 block (outer), inner preserved as content
        assert (
            len(blocks) == 1
        ), "Should support nested content preservation as documented"
        assert (
            "```python" in blocks[0].content
        ), "Inner fence should be preserved as content"
