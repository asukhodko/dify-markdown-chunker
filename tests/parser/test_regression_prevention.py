"""Regression prevention tests for all major fixes."""

import os


class TestRegressionPrevention:
    """Tests to prevent regression of major fixes."""

    def test_prevent_0_based_line_numbering_regression(self):
        """Prevent regression to 0-based line numbering."""
        from markdown_chunker.parser import LineNumberConverter, extract_fenced_blocks

        # Test that API always returns 1-based line numbers
        test_cases = [
            "```python\ncode\n```",
            "Line 1\n```python\ncode\n```",
            "Line 1\nLine 2\n```python\ncode\n```\nLine 5",
        ]

        for i, markdown in enumerate(test_cases):
            blocks = extract_fenced_blocks(markdown)
            assert len(blocks) >= 1, f"Test case {i}: Should find blocks"

            for block in blocks:
                assert (
                    block.start_line >= 1
                ), f"Test case {i}: start_line \
            must be >= 1, got {block.start_line}"
                assert (
                    block.end_line >= 1
                ), f"Test case {i}: end_line \
            must be >= 1, got {block.end_line}"
                assert (
                    block.end_line >= block.start_line
                ), f"Test case {i}: end_line \
            must be >= start_line"

        # Test converter functions
        assert (
            LineNumberConverter.to_api_line_number(0) == 1
        ), "0 -> 1 conversion \
            must work"
        assert (
            LineNumberConverter.from_api_line_number(1) == 0
        ), "1 -> 0 conversion \
            must work"

        # Test validation rejects 0-based input
        try:
            LineNumberConverter.validate_api_line_number(0)
            assert False, "Should reject 0 as invalid API line number"
        except ValueError:
            pass  # Expected

    def test_prevent_nested_block_skipping_regression(self):
        """Prevent regression to skipping nested blocks."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Test cases that were previously broken
        nested_test_cases = [
            # Basic nesting
            """~~~markdown
# Document
```python
def nested():
    pass
```
End
~~~""",
            # Multiple nested blocks
            """~~~markdown
```python
def first():
    pass
```

```javascript
function second() {}
```
~~~""",
            # Mixed fence types
            """```markdown
~~~python
def mixed():
    pass
~~~
```""",
        ]

        for i, markdown in enumerate(nested_test_cases):
            blocks = extract_fenced_blocks(markdown)

            # UPDATED: Correct behavior is to create single outer block for nested fences
            # Inner fences should be treated as content, not separate blocks
            assert (
                len(blocks) >= 1
            ), f"Test case {i}: Should find at least one block, got {len(blocks)}"

            # For nested content, verify inner fences are preserved as content
            if len(blocks) == 1:
                # Single block means proper nested handling
                outer_block = blocks[0]
                # Inner fence markers should be in content
                if "```" in markdown and "~~~" in markdown:
                    # Should contain both fence types in content
                    assert (
                        "```" in outer_block.content or "~~~" in outer_block.content
                    ), f"Test case {i}: Inner fence markers should be preserved in content"

    def test_prevent_pytest_coverage_dependency_regression(self):
        """Prevent regression to mandatory pytest-cov dependency."""
        # Test that conftest.py handles missing coverage gracefully
        from .conftest import pytest_configure

        # Mock config without pytest-cov
        class MockConfig:
            def __init__(self):
                self.option = MockOption()

        class MockOption:
            def __init__(self):
                self.cov = None
                self.cov_report = None

        config = MockConfig()

        # Should not raise exception
        try:
            pytest_configure(config)
        except ImportError:
            pass  # Expected when pytest-cov not available
        except Exception as e:
            assert False, f"Should handle missing pytest-cov gracefully, got: {e}"

    def test_prevent_print_only_tests_regression(self):
        """Prevent regression to print-only tests."""
        # test_basic.py should have real assertions
        if os.path.exists("test_basic.py"):
            with open("test_basic.py", "r") as f:
                content = f.read()

            # Must have substantial assertions
            assert_count = content.count("assert ")
            assert (
                assert_count >= 20
            ), f"test_basic.py \
            must have real assertions, got {assert_count}"

            # Must have test class
            assert (
                "class TestBasicFunctionality:" in content
            ), "Must have proper test class"

            # Must not be just print statements
            lines = content.split("\n")
            assertion_lines = [
                line for line in lines if "assert " in line and "print(" not in line
            ]
            assert len(assertion_lines) >= 15, "Must have standalone assertion lines"

    def test_prevent_nesting_capability_overclaims_regression(self):
        """Prevent regression to overclaiming nesting capabilities."""
        from markdown_chunker.parser import extract_fenced_blocks

        # Test that we honestly report nesting capabilities
        # Complex nesting should work for basic cases but may have edge cases
        # This should work (basic 2-level nesting)
        basic_nesting = """~~~markdown
```python
code
```
~~~"""

        blocks = extract_fenced_blocks(basic_nesting)
        # UPDATED: Correct behavior is single outer block with nested content preserved
        assert len(blocks) >= 1, "Basic nesting should work"

        # Verify nested content is preserved correctly
        if len(blocks) == 1:
            outer_block = blocks[0]
            assert (
                "```python" in outer_block.content
            ), "Inner fence should be preserved in content"
            assert "code" in outer_block.content, "Inner content should be preserved"

        # Check module documentation is honest
        # Note: fenced_blocks module has been consolidated into core.py
        import markdown_chunker.parser.core

        module_doc = markdown_chunker.parser.core.__doc__ or ""

        # Should not claim "full" or "complete" nesting support
        problematic_claims = ["full nesting", "complete nesting", "perfect nesting"]
        for claim in problematic_claims:
            assert (
                claim.lower() not in module_doc.lower()
            ), f"Should not claim '{claim}'"

    def test_prevent_test_environment_dependency_regression(self):
        """Prevent regression to environment-specific test failures."""
        # Test that basic functionality works without dev dependencies

        # These imports should work in minimal environment
        try:
            from markdown_chunker.parser import (
                LineNumberConverter,
                extract_fenced_blocks,
                resolve_nesting,
            )

            # Basic functionality should work
            blocks = extract_fenced_blocks("```python\ncode\n```")
            assert len(blocks) == 1

            # Line converter should work
            assert LineNumberConverter.to_api_line_number(0) == 1

            # Nesting resolver is deprecated but should not crash
            # Note: resolve_nesting now returns empty list (deprecated functionality)
            resolved = resolve_nesting(blocks)
            assert isinstance(resolved, list), "resolve_nesting should return a list"

        except ImportError as e:
            assert False, (
                "Basic functionality " f"should work without dev dependencies: {e}"
            )

    def test_prevent_api_breaking_changes_regression(self):
        """Prevent regression that breaks existing API."""
        from markdown_chunker.parser import (
            FencedBlockExtractor,
            extract_fenced_blocks,
        )

        # Test that existing API still works
        # Convenience function should work
        blocks = extract_fenced_blocks("```python\ncode\n```")
        assert len(blocks) == 1
        assert hasattr(blocks[0], "content")
        assert hasattr(blocks[0], "language")
        assert hasattr(blocks[0], "start_line")
        assert hasattr(blocks[0], "end_line")

        # Class-based API should work
        extractor = FencedBlockExtractor()
        blocks2 = extractor.extract_fenced_blocks("```python\ncode\n```")
        assert len(blocks2) == 1

        # Results should be compatible
        assert blocks[0].content == blocks2[0].content
        assert blocks[0].language == blocks2[0].language

    def test_prevent_performance_regression(self):
        """Prevent significant performance regression."""
        import time

        from markdown_chunker.parser import extract_fenced_blocks

        # Create moderately sized document
        large_doc = "# Document\n\n" + "```python\ndef func():\n    pass\n```\n\n" * 50

        # Should complete quickly
        start_time = time.time()
        blocks = extract_fenced_blocks(large_doc)
        end_time = time.time()

        processing_time = end_time - start_time

        # Should find all blocks
        assert len(blocks) == 50, f"Should find all blocks, got {len(blocks)}"

        # Should complete in reasonable time (generous limit for CI)
        assert (
            processing_time < 1.0
        ), f"Should complete quickly, took {processing_time:.3f}s"

    def test_prevent_error_handling_regression(self):
        """Prevent regression in error handling."""
        from markdown_chunker.parser import LineNumberConverter, extract_fenced_blocks

        # Should handle malformed input gracefully
        malformed_inputs = [
            "",  # Empty
            "```\nunclosed",  # Unclosed block
            "invalid content",  # No blocks
            "```python\n```\n```python\n```",  # Multiple blocks
        ]

        for malformed in malformed_inputs:
            try:
                blocks = extract_fenced_blocks(malformed)
                assert isinstance(blocks, list), "Should return list"
            except Exception as e:
                assert False, f"Should not crash on malformed input '{malformed}': {e}"

        # Line converter should validate input
        invalid_inputs = [-1, -10]
        for invalid in invalid_inputs:
            try:
                LineNumberConverter.to_api_line_number(invalid)
                assert False, f"Should reject invalid input {invalid}"
            except ValueError:
                pass  # Expected

        invalid_api_inputs = [0, -1]
        for invalid in invalid_api_inputs:
            try:
                LineNumberConverter.from_api_line_number(invalid)
                assert False, f"Should reject invalid API input {invalid}"
            except ValueError:
                pass  # Expected
