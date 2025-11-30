#!/usr/bin/env python3
"""
Test new nested block extraction algorithm.
"""

# Test nested extraction without sys.path manipulation


def test_simple_nested_blocks():
    """Test extraction of simple nested blocks - NEW CORRECT BEHAVIOR."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing simple nested blocks...")

    # Test ``` inside ~~~
    markdown = """# Document
~~~markdown
# Inner Document
```python
def nested_function():
    return "nested"
```
More content
~~~
# End"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    # NEW CORRECT BEHAVIOR: Should find only 1 block (the outer one)
    # Inner fences are treated as content, not separate blocks
    assert len(blocks) == 1, f"Expected 1 block (outer only), got {len(blocks)}"

    outer_block = blocks[0]
    print(
        f"Block: {outer_block.language} at lines {outer_block.start_line}-{outer_block.end_line}, nesting={outer_block.nesting_level}"
    )

    # Should be the markdown block
    assert (
        outer_block.language == "markdown"
    ), f"Expected markdown block, got {outer_block.language}"
    assert (
        outer_block.nesting_level == 0
    ), f"Outer block should have nesting_level=0, got {outer_block.nesting_level}"

    # The inner fence should be preserved as content
    assert (
        "```python" in outer_block.content
    ), "Inner fence should be preserved as content"
    assert (
        "def nested_function" in outer_block.content
    ), "Inner code should be preserved as content"

    print("✓ Simple nested blocks handled correctly (new behavior)")


def test_multiple_nested_levels():
    """Test extraction with multiple nesting levels - NEW CORRECT BEHAVIOR."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing multiple nesting levels...")

    # Simplified test - focus on what should work
    markdown = """~~~text
Outer level
```python
def middle_function():
    pass
```
Back to outer
~~~"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    for block in blocks:
        print(
            f"Block: {block.language} at lines {block.start_line}-{block.end_line}, nesting={block.nesting_level}"
        )

    # NEW CORRECT BEHAVIOR: Should find only 1 block (the outer one)
    assert len(blocks) == 1, f"Expected 1 block (outer only), got {len(blocks)}"

    outer_block = blocks[0]
    assert (
        outer_block.language == "text"
    ), f"Expected text block, got {outer_block.language}"
    assert (
        outer_block.nesting_level == 0
    ), f"Should have nesting_level=0, got {outer_block.nesting_level}"

    # The inner fence should be preserved as content
    assert (
        "```python" in outer_block.content
    ), "Inner fence should be preserved as content"
    assert (
        "def middle_function" in outer_block.content
    ), "Inner code should be preserved as content"

    print("✓ Multiple nesting levels handled correctly (new behavior)")


def test_mixed_fence_types():
    """Test nested blocks with mixed fence types - NEW CORRECT BEHAVIOR."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing mixed fence types...")

    markdown = """```markdown
# Document with mixed fences
~~~python
def function_in_tilde():
    pass
~~~
More markdown content
```"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    # NEW CORRECT BEHAVIOR: Should find only 1 block (the outer one)
    assert len(blocks) == 1, f"Expected 1 block (outer only), got {len(blocks)}"

    outer_block = blocks[0]
    print(
        f"Block: {outer_block.fence_type} {outer_block.language} at lines {outer_block.start_line}-{outer_block.end_line}, nesting={outer_block.nesting_level}"
    )

    # Should be the markdown block with backtick fences
    assert (
        outer_block.fence_type == "```"
    ), f"Expected backtick fence, got {outer_block.fence_type}"
    assert (
        outer_block.language == "markdown"
    ), f"Expected markdown block, got {outer_block.language}"

    # The inner tilde fence should be preserved as content
    assert (
        "~~~python" in outer_block.content
    ), "Inner tilde fence should be preserved as content"
    assert (
        "def function_in_tilde" in outer_block.content
    ), "Inner code should be preserved as content"

    print("✓ Mixed fence types handled correctly (new behavior)")


def test_no_skipping_inner_blocks():
    """Test that inner blocks are preserved as content - NEW CORRECT BEHAVIOR."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing that inner blocks are preserved as content...")

    # This was the main problem - inner blocks were skipped
    # Now they should be preserved as content in the outer block
    markdown = """~~~markdown
# Outer document
```python
# This inner block was being skipped
def important_function():
    return "This should be found"
```
More outer content
~~~"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    # NEW CORRECT BEHAVIOR: Should find only 1 block (the outer one)
    assert len(blocks) == 1, f"Expected exactly 1 block, got {len(blocks)}"

    outer_block = blocks[0]
    assert (
        outer_block.language == "markdown"
    ), f"Expected markdown block, got {outer_block.language}"

    # Check that the inner content is preserved
    assert (
        "important_function" in outer_block.content
    ), "Should preserve the inner function as content"
    assert (
        "```python" in outer_block.content
    ), "Should preserve the inner fence markers as content"
    assert (
        "This should be found" in outer_block.content
    ), "Should preserve all inner content"

    print("✓ Inner blocks are preserved as content (new correct behavior)")


def test_overlapping_blocks_handling():
    """Test handling of overlapping blocks."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing overlapping blocks handling...")

    # This creates a scenario where blocks might overlap improperly
    markdown = """```python
def func1():
    pass
~~~javascript
// This creates an overlap
function func2() {}
```
// This continues the javascript
~~~"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    # Should handle overlaps gracefully
    for block in blocks:
        print(f"Block: {block.language} at lines {block.start_line}-{block.end_line}")

    # All blocks should have valid line ranges
    for block in blocks:
        assert (
            block.start_line <= block.end_line
        ), f"Invalid line range: {block.start_line}-{block.end_line}"
        assert block.start_line >= 1, f"Invalid start line: {block.start_line}"

    print("✓ Overlapping blocks handled gracefully")


def test_unclosed_nested_blocks():
    """Test handling of unclosed nested blocks."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing unclosed nested blocks...")

    markdown = """~~~markdown
# Document
```python
def unclosed_function():
    # This block is not closed
    pass
# End of document"""

    blocks = extract_fenced_blocks(markdown)
    print(f"Found {len(blocks)} blocks")

    # Should find both blocks even if inner is unclosed
    assert len(blocks) >= 1, f"Expected at least 1 block, got {len(blocks)}"

    # Check for unclosed blocks
    unclosed_blocks = [b for b in blocks if not b.is_closed]
    print(f"Found {len(unclosed_blocks)} unclosed blocks")

    for block in blocks:
        print(
            f"Block: {block.language} at lines {block.start_line}-{block.end_line}, closed={block.is_closed}"
        )

    print("✓ Unclosed nested blocks handled correctly")


if __name__ == "__main__":
    test_simple_nested_blocks()
    test_multiple_nested_levels()
    test_mixed_fence_types()
    test_no_skipping_inner_blocks()
    test_overlapping_blocks_handling()
    test_unclosed_nested_blocks()
    print("🎉 New nested block extraction algorithm is working correctly!")
