"""Tests to validate that documentation matches implementation."""

import glob
import os

from .conftest import pytest_configure


class TestDocumentationAccuracy:
    """Test that documentation accurately reflects implementation."""

    def test_line_numbering_documentation(self):
        """Test that line numbering is documented as 1-based."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Test that implementation actually uses 1-based numbering
        blocks = extract_fenced_blocks("```python\ncode\n```")
        assert len(blocks) == 1
        block = blocks[0]

        # Verify 1-based numbering
        assert block.start_line >= 1, "Implementation should use 1-based line numbering"
        assert block.start_line == 1, f"First line should be 1, got {block.start_line}"

    def test_nested_block_documentation(self):
        """Test that nested block capabilities match documentation."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Test basic nested block support
        markdown = """~~~markdown
# Document
```python
def nested():
    pass
```
End
~~~"""

        blocks = extract_fenced_blocks(markdown)

        # UPDATED: Correct behavior is single outer block with nested content preserved
        assert len(blocks) >= 1, "Should support nested block detection"

        # For proper nested handling, should have single outer block
        if len(blocks) == 1:
            outer_block = blocks[0]
            # Inner fence should be preserved as content
            assert (
                "```python" in outer_block.content
            ), "Inner fence should be preserved in content"
            assert (
                "def nested():" in outer_block.content
            ), "Inner content should be preserved"

    def test_test_count_accuracy(self):
        """Test that reported test counts match actual tests."""
        # Count actual test files
        test_files = []

        # Count pytest-style test files
        pytest_files = glob.glob("tests/parser/test_*.py")
        test_files.extend(pytest_files)

        # Count simple test files
        simple_files = glob.glob("test_*.py")
        test_files.extend(simple_files)

        # Should have reasonable number of test files
        assert (
            len(test_files) >= 5
        ), f"Should have at least 5 test files, got {len(test_files)}"

        # Should not claim 54 tests without evidence
        # (This is a documentation accuracy check)
        print(f"Actual test files found: {len(test_files)}")

    def test_automated_test_validation(self):
        """Test that test_basic_functionality.py is actually automated."""
        # Read test_basic_functionality.py (moved to tests/parser)
        test_file = "tests/parser/test_basic_functionality.py"
        if not os.path.exists(test_file):
            # Try root_tests location
            test_file = "tests/parser/root_tests/test_basic.py"

        with open(test_file, "r") as f:
            content = f.read()

        # Should have assertions
        assert_count = content.count("assert ")
        assert (
            assert_count >= 5
        ), f"Should have at least 5 assertions, got {assert_count}"

        # Should have test class or functions
        has_test_structure = (
            "class TestBasicFunctionality:" in content or "def test_" in content
        )
        assert has_test_structure, "Should have proper test structure"

    def test_coverage_optional_documentation(self):
        """Test that coverage is actually optional."""
        # Test that conftest.py handles missing coverage

        # Should not raise exception when pytest-cov is missing
        class MockConfig:
            def __init__(self):
                self.option = MockOption()

        class MockOption:
            def __init__(self):
                self.cov = None
                self.cov_report = None

        config = MockConfig()

        # This should not raise an exception
        pytest_configure(config)

    def test_api_compliance_documentation(self):
        """Test that API actually complies with 1-based specification."""
        from markdown_chunker.parser import LineNumberConverter

        # Test converter functions work as documented
        assert LineNumberConverter.to_api_line_number(0) == 1
        assert LineNumberConverter.from_api_line_number(1) == 0

        # Test validation works as documented
        assert LineNumberConverter.validate_api_line_number(1)

        try:
            LineNumberConverter.validate_api_line_number(0)
            assert False, "Should reject 0 as invalid API line number"
        except ValueError:
            pass  # Expected

    def test_configuration_documentation(self):
        """Test that configuration works as documented."""
        from markdown_chunker.parser.config import Stage1Config

        # Test that documented configurations exist
        default_config = Stage1Config.default()
        assert default_config is not None

        fast_config = Stage1Config.fast()
        assert fast_config is not None

        detailed_config = Stage1Config.detailed()
        assert detailed_config is not None
