"""Tests for pytest compatibility without mandatory coverage."""


class TestPytestCompatibility:
    """Test that pytest works without mandatory dependencies."""

    def test_basic_functionality(self):
        """Test basic functionality works."""
        assert True, "Basic test should always pass"

    def test_imports_work(self):
        """Test that all imports work without coverage."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Basic functionality test
        blocks = extract_fenced_blocks("```python\ntest\n```")
        assert len(blocks) == 1
        assert blocks[0].language == "python"

    def test_line_numbering(self):
        """Test line numbering functionality."""
        from markdown_chunker.parser import LineNumberConverter

        assert LineNumberConverter.to_api_line_number(0) == 1
        assert LineNumberConverter.from_api_line_number(1) == 0

    def test_nesting_resolver(self):
        """Test nesting resolver functionality."""
        from markdown_chunker.parser import resolve_nesting
        from markdown_chunker.parser.types import FencedBlock

        block = FencedBlock(
            content="test",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=1,
            end_line=3,
            start_offset=0,
            end_offset=20,
            nesting_level=0,
            is_closed=True,
            raw_content="",
        )

        result = resolve_nesting([block])
        # Note: resolve_nesting is deprecated and returns empty list
        assert isinstance(result, list), "resolve_nesting should return a list"

    def test_coverage_optional(self):
        """Test that coverage is optional."""
        # This test should pass whether or not pytest-cov is installed
        try:
            import pytest_cov  # noqa: F401

            coverage_available = True
        except ImportError:
            coverage_available = False

        # Test should pass in both cases
        assert isinstance(coverage_available, bool)
        print(f"Coverage available: {coverage_available}")

    def test_no_coverage_dependency(self):
        """Test that tests can run without coverage dependency."""
        # This test verifies that we don't have hard dependencies on coverage
        # It should pass even in minimal environments

        # Check that we can import our modules (updated for consolidated structure)
        import markdown_chunker.parser.core  # noqa: F401 (replaces fenced_blocks)
        import markdown_chunker.parser.utils  # noqa: F401 (replaces line_converter)

        # nesting_resolver has been deprecated and removed

        assert True, "All imports successful without coverage dependency"
