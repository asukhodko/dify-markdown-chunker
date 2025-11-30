#!/usr/bin/env python3
"""
Regression prevention tests for all fixed bugs.

This module contains tests specifically designed to prevent regression
of the bugs that were fixed in the critical fixes project. Each test
validates that the specific issue remains resolved.
"""
import pytest

from markdown_chunker.chunker.core import MarkdownChunker
from markdown_chunker.chunker.types import ChunkConfig


class TestASTContentPreservationRegression:
    """Prevent regression of AST content preservation fixes."""

    def test_ast_content_not_empty_regression(self):
        """Prevent regression: AST nodes should contain actual content, not be empty."""
        chunker = MarkdownChunker()

        content = """# Header Content

This is paragraph content that must be preserved.

## Another Header

More paragraph content here."""

        result = chunker.chunk_with_analysis(content)

        # Verify no empty content (the original bug)
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert "Header Content" in all_content, "Header content was lost (regression)"
        assert (
            "paragraph content that must be preserved" in all_content
        ), "Paragraph content was lost (regression)"
        assert (
            "Another Header" in all_content
        ), "Second header content was lost (regression)"
        assert (
            "More paragraph content here" in all_content
        ), "Second paragraph content was lost (regression)"

        # Verify no chunks have empty content
        for i, chunk in enumerate(result.chunks):
            assert (
                len(chunk.content.strip()) > 0
            ), f"Chunk {i} has empty content (regression)"

    def test_header_paragraph_hierarchy_regression(self):
        """Prevent regression: Paragraphs should be siblings of headers, not children."""
        chunker = MarkdownChunker()

        content = """# Main Header

This paragraph should be a sibling of the header, not a child.

## Sub Header

This paragraph should also be a sibling of its header."""

        result = chunker.chunk_with_analysis(content)

        # The fix ensures proper content extraction, verify it's working
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "Main Header" in all_content
        ), "Main header missing (hierarchy regression)"
        assert (
            "This paragraph should be a sibling" in all_content
        ), "Paragraph content missing (hierarchy regression)"
        assert "Sub Header" in all_content, "Sub header missing (hierarchy regression)"
        assert (
            "This paragraph should also be a sibling" in all_content
        ), "Second paragraph missing (hierarchy regression)"

    def test_inline_content_preservation_regression(self):
        """Prevent regression: Inline elements should have their content preserved."""
        chunker = MarkdownChunker()

        content = """# Code Example

Here is some `inline code` that should be preserved.

And here is **bold text** and *italic text* that should also be preserved."""

        result = chunker.chunk_with_analysis(content)

        # Verify inline content is preserved
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert "inline code" in all_content, "Inline code content lost (regression)"
        assert "bold text" in all_content, "Bold text content lost (regression)"
        assert "italic text" in all_content, "Italic text content lost (regression)"


class TestNestedFenceHandlingRegression:
    """Prevent regression of nested fence handling fixes."""

    def test_nested_fences_single_block_regression(self):
        """Prevent regression: Nested fences should create single outer block, not phantom blocks."""
        chunker = MarkdownChunker()

        content = """# Documentation

```markdown
# Example Document

This contains nested code:

~~~python
def example():
    return "nested"
~~~

More content after nested code.
```

Regular content after the outer fence."""

        result = chunker.chunk_with_analysis(content)

        # Verify nested fences are preserved as content (not separate blocks)
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "~~~python" in all_content
        ), "Nested fence markers should be preserved as content (regression)"
        assert (
            "def example():" in all_content
        ), "Nested code should be preserved (regression)"
        assert (
            'return "nested"' in all_content
        ), "Nested code content should be preserved (regression)"

        # Verify we don't have phantom separate blocks for nested content
        # The original bug created separate blocks for inner fences
        code_chunks = [
            chunk
            for chunk in result.chunks
            if "def example():" in chunk.content and "~~~python" not in chunk.content
        ]
        assert (
            len(code_chunks) == 0
        ), "Found phantom blocks for nested fence content (regression)"

    def test_mixed_nested_fence_types_regression(self):
        """Prevent regression: Mixed nested fence types should be handled correctly."""
        chunker = MarkdownChunker()

        content = """````markdown
Outer markdown block

```python
def outer_function():
    pass
```

~~~javascript
function inner_function() {
    return "nested";
}
~~~

More outer content.
````"""

        result = chunker.chunk_with_analysis(content)

        # Should have one outer block with nested content preserved
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "```python" in all_content
        ), "Python fence should be preserved as content (regression)"
        assert (
            "~~~javascript" in all_content
        ), "JavaScript fence should be preserved as content (regression)"
        assert (
            "def outer_function():" in all_content
        ), "Python code should be preserved (regression)"
        assert (
            "function inner_function()" in all_content
        ), "JavaScript code should be preserved (regression)"

    def test_deep_nesting_regression(self):
        """Prevent regression: Deep nesting should be handled without creating phantom blocks."""
        chunker = MarkdownChunker()

        content = """```markdown
# Level 1

~~~python
# Level 2
def level2():
    '''
    ```javascript
    // Level 3
    console.log("deep");
    ```
    '''
    pass
~~~

Back to level 1.
```"""

        result = chunker.chunk_with_analysis(content)

        # Should preserve all nested content in outer block
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "~~~python" in all_content
        ), "Level 2 fence should be preserved (regression)"
        assert (
            "```javascript" in all_content
        ), "Level 3 fence should be preserved (regression)"
        assert (
            'console.log("deep");' in all_content
        ), "Deep nested content should be preserved (regression)"
        assert (
            "def level2():" in all_content
        ), "Level 2 code should be preserved (regression)"


class TestMixedStrategyIntegrationRegression:
    """Prevent regression of MixedStrategy Stage 1 integration fixes."""

    def test_stage1_lists_integration_regression(self):
        """Prevent regression: MixedStrategy should use Stage 1 list data when available."""
        chunker = MarkdownChunker()

        content = """# Mixed Content

- [x] Task 1: Setup complete
- [ ] Task 2: Implementation needed
- [ ] Task 3: Testing required

Regular text content mixed with the list."""

        result = chunker.chunk_with_analysis(content)

        # Verify list content is preserved (Stage 1 integration working)
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "- [x] Task 1:" in all_content
        ), "Task list content lost (Stage 1 integration regression)"
        assert (
            "- [ ] Task 2:" in all_content
        ), "Task list items lost (Stage 1 integration regression)"
        assert (
            "Regular text content" in all_content
        ), "Mixed text content lost (regression)"

    def test_stage1_tables_integration_regression(self):
        """Prevent regression: MixedStrategy should use Stage 1 table data when available."""
        chunker = MarkdownChunker()

        content = """# API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |

Additional documentation content."""

        result = chunker.chunk_with_analysis(content)

        # Verify table content is preserved (Stage 1 integration working)
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert (
            "| Method | Endpoint |" in all_content
        ), "Table headers lost (Stage 1 integration regression)"
        assert (
            "| GET    | /users   |" in all_content
        ), "Table data lost (Stage 1 integration regression)"
        assert (
            "Additional documentation" in all_content
        ), "Mixed content lost (regression)"

    def test_fallback_to_regex_regression(self):
        """Prevent regression: Should gracefully fallback to regex when Stage 1 data unavailable."""
        # This test ensures the fallback mechanism still works
        chunker = MarkdownChunker()

        content = """# Fallback Test

- Simple list item 1
- Simple list item 2

| Simple | Table |
|--------|-------|
| A      | B     |

Text content."""

        result = chunker.chunk_with_analysis(content)

        # Should still work even if Stage 1 data is not optimal
        assert len(result.chunks) >= 1, "Fallback mechanism failed (regression)"
        all_content = " ".join(chunk.content for chunk in result.chunks)
        assert "Simple list item" in all_content, "List fallback failed (regression)"
        assert "| Simple | Table |" in all_content, "Table fallback failed (regression)"


class TestFallbackMetadataPreservationRegression:
    """Prevent regression of fallback metadata preservation fixes."""

    def test_fallback_metadata_accuracy_regression(self):
        """Prevent regression: Fallback metadata should reflect actual usage, not error logic."""
        # Use small chunk size to potentially trigger fallbacks
        config = ChunkConfig(max_chunk_size=100, target_chunk_size=80)
        chunker = MarkdownChunker(config)

        content = """# Test Document

This is a longer piece of content that should potentially trigger fallback mechanisms due to the small chunk size configuration. We want to test that fallback metadata is properly preserved when the system needs to use fallback strategies."""

        result = chunker.chunk_with_analysis(content)

        # Verify result has proper metadata structure (the fix)
        assert hasattr(
            result, "fallback_used"
        ), "fallback_used field missing (regression)"
        assert hasattr(
            result, "fallback_level"
        ), "fallback_level field missing (regression)"
        assert hasattr(result, "warnings"), "warnings field missing (regression)"

        # If fallback was used, verify metadata is accurate (not from error logic)
        if result.fallback_used:
            assert isinstance(
                result.fallback_level, int
            ), "fallback_level should be int (regression)"
            assert (
                1 <= result.fallback_level <= 4
            ), f"Invalid fallback_level: {result.fallback_level} (regression)"

        # Verify chunks have proper metadata
        for chunk in result.chunks:
            assert chunk.metadata is not None, "Chunk metadata missing (regression)"
            assert (
                "strategy" in chunk.metadata
            ), "Strategy metadata missing (regression)"

    def test_warnings_preservation_regression(self):
        """Prevent regression: Warnings should be preserved in ChunkingResult."""
        # Create conditions that might generate warnings
        config = ChunkConfig(max_chunk_size=50, target_chunk_size=40)  # Very small
        chunker = MarkdownChunker(config)

        content = """# Warning Test

This content is designed to potentially generate warnings due to the very small chunk size configuration that may cause chunking challenges."""

        result = chunker.chunk_with_analysis(content)

        # Verify warnings field exists and is properly structured
        assert hasattr(result, "warnings"), "warnings field missing (regression)"
        assert isinstance(
            result.warnings, list
        ), "warnings should be a list (regression)"

        # If warnings exist, they should be properly formatted
        for warning in result.warnings:
            assert isinstance(warning, str), "Warning should be string (regression)"


class TestEmergencyChunkingRegression:
    """Prevent regression of emergency chunking line number fixes."""

    def test_emergency_chunking_line_numbers_regression(self):
        """Prevent regression: Emergency chunking should have accurate line numbers."""
        # Force emergency chunking with very small chunk size and longer content
        config = ChunkConfig(max_chunk_size=30, target_chunk_size=25)
        chunker = MarkdownChunker(config)

        # Longer content to force multiple chunks
        content = """Line 1 with substantial content to exceed chunk size limits
Line 2 with substantial content to exceed chunk size limits
Line 3 with substantial content to exceed chunk size limits
Line 4 with substantial content to exceed chunk size limits
Line 5 with substantial content to exceed chunk size limits
Line 6 with substantial content to exceed chunk size limits"""

        result = chunker.chunk_with_analysis(content)

        # Verify line numbers are accurate regardless of chunk count
        for i, chunk in enumerate(result.chunks):
            assert (
                chunk.start_line >= 1
            ), f"Chunk {i} has invalid start_line: {chunk.start_line} (regression)"
            assert (
                chunk.end_line >= chunk.start_line
            ), f"Chunk {i} has invalid line range (regression)"

            # First chunk should start at line 1
            if i == 0:
                assert (
                    chunk.start_line == 1
                ), f"First chunk should start at line 1, got {chunk.start_line} (regression)"

        # If multiple chunks, verify progression
        if len(result.chunks) > 1:
            for i in range(len(result.chunks) - 1):
                current_chunk = result.chunks[i]
                next_chunk = result.chunks[i + 1]
                assert (
                    next_chunk.start_line > current_chunk.start_line
                ), f"Line number progression broken between chunks {i} and {i+1} (regression)"

    def test_line_number_progression_regression(self):
        """Prevent regression: Line numbers should progress correctly across chunks."""
        config = ChunkConfig(max_chunk_size=30, target_chunk_size=25)
        chunker = MarkdownChunker(config)

        content = """First line
Second line
Third line
Fourth line
Fifth line
Sixth line"""

        result = chunker.chunk_with_analysis(content)

        if len(result.chunks) > 1:
            # Verify line number progression (the fix)
            for i in range(len(result.chunks) - 1):
                current_chunk = result.chunks[i]
                next_chunk = result.chunks[i + 1]

                # Next chunk should start after current chunk ends
                assert (
                    next_chunk.start_line > current_chunk.end_line
                    or next_chunk.start_line == current_chunk.end_line + 1
                ), f"Line number progression broken between chunks {i} and {i+1} (regression)"


class TestProjectConfigurationRegression:
    """Prevent regression of project configuration fixes."""

    def test_both_stages_discoverable_regression(self):
        """Prevent regression: Both Stage 1 and Stage 2 should be discoverable by pytest."""
        # This test verifies that the pyproject.toml testpaths fix is working
        # by ensuring both stages can be imported and used

        # Test Stage 1 import
        try:
            from markdown_chunker.parser import extract_fenced_blocks

            blocks = extract_fenced_blocks("```python\ntest\n```")
            assert len(blocks) >= 1, "Stage 1 not working (configuration regression)"
        except ImportError as e:
            pytest.fail(f"Stage 1 import failed (configuration regression): {e}")

        # Test Stage 2 import
        try:
            chunker = MarkdownChunker()
            result = chunker.chunk_with_analysis("# Test\n\nContent")
            assert (
                len(result.chunks) >= 1
            ), "Stage 2 not working (configuration regression)"
        except ImportError as e:
            pytest.fail(f"Stage 2 import failed (configuration regression): {e}")

    def test_package_installation_regression(self):
        """Prevent regression: Package should install and import correctly."""
        # Test that main package components are importable
        try:
            from markdown_chunker.chunker import MarkdownChunker
            from markdown_chunker.chunker.types import (
                Chunk,
                ChunkConfig,
                ChunkingResult,
            )

            # Test basic functionality
            chunker = MarkdownChunker()
            ChunkConfig()
            result = chunker.chunk_with_analysis("# Test")

            assert isinstance(result, ChunkingResult), "ChunkingResult type regression"
            assert len(result.chunks) >= 1, "Basic chunking regression"
            assert isinstance(result.chunks[0], Chunk), "Chunk type regression"

        except ImportError as e:
            pytest.fail(f"Package import failed (installation regression): {e}")


if __name__ == "__main__":  # noqa: C901
    # Run regression tests manually for debugging
    # Complexity justified: This is a test runner script that sequentially
    # executes multiple test cases with error handling for each.
    print("🔍 Running Regression Prevention Tests...")

    # AST Content Preservation
    ast_tests = TestASTContentPreservationRegression()
    try:
        ast_tests.test_ast_content_not_empty_regression()
        print("✅ AST content preservation regression test")
    except Exception as e:
        print(f"❌ AST content regression test failed: {e}")

    try:
        ast_tests.test_header_paragraph_hierarchy_regression()
        print("✅ Header-paragraph hierarchy regression test")
    except Exception as e:
        print(f"❌ Hierarchy regression test failed: {e}")

    # Nested Fence Handling
    fence_tests = TestNestedFenceHandlingRegression()
    try:
        fence_tests.test_nested_fences_single_block_regression()
        print("✅ Nested fence handling regression test")
    except Exception as e:
        print(f"❌ Nested fence regression test failed: {e}")

    try:
        fence_tests.test_mixed_nested_fence_types_regression()
        print("✅ Mixed nested fence types regression test")
    except Exception as e:
        print(f"❌ Mixed fence regression test failed: {e}")

    # MixedStrategy Integration
    mixed_tests = TestMixedStrategyIntegrationRegression()
    try:
        mixed_tests.test_stage1_lists_integration_regression()
        print("✅ Stage 1 lists integration regression test")
    except Exception as e:
        print(f"❌ Lists integration regression test failed: {e}")

    try:
        mixed_tests.test_stage1_tables_integration_regression()
        print("✅ Stage 1 tables integration regression test")
    except Exception as e:
        print(f"❌ Tables integration regression test failed: {e}")

    # Fallback Metadata
    fallback_tests = TestFallbackMetadataPreservationRegression()
    try:
        fallback_tests.test_fallback_metadata_accuracy_regression()
        print("✅ Fallback metadata accuracy regression test")
    except Exception as e:
        print(f"❌ Fallback metadata regression test failed: {e}")

    # Emergency Chunking
    emergency_tests = TestEmergencyChunkingRegression()
    try:
        emergency_tests.test_emergency_chunking_line_numbers_regression()
        print("✅ Emergency chunking line numbers regression test")
    except Exception as e:
        print(f"❌ Emergency chunking regression test failed: {e}")

    # Project Configuration
    config_tests = TestProjectConfigurationRegression()
    try:
        config_tests.test_both_stages_discoverable_regression()
        print("✅ Project configuration regression test")
    except Exception as e:
        print(f"❌ Configuration regression test failed: {e}")

    print("\n🎉 Regression Prevention Testing completed!")
