#!/usr/bin/env python3
"""
Test script for nested fence handling fixes.

This script tests the critical fixes for FencedBlockExtractor:
- Single outer block creation for nested fences
- Mixed fence types (``` containing ~~~)
- Deep nesting scenarios (3+ levels)
- Unclosed nested blocks
- Inner fence markers as content, not separate blocks
"""


from markdown_chunker.parser import extract_fenced_blocks


def test_nested_fences_not_separate_blocks():
    """Test that nested fences create only one outer block."""
    md = """````markdown
Outer block
~~~python
print("nested")
~~~
More outer content
````"""

    blocks = extract_fenced_blocks(md)

    # Should be exactly 1 block
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].is_closed is True

    # Inner ~~~ should be part of content, not separate block
    assert "~~~python" in blocks[0].content
    assert 'print("nested")' in blocks[0].content
    assert "~~~" in blocks[0].content


def test_nested_fences_mixed_types():
    """Test nested fences with mixed types (``` containing ~~~)."""
    md = """````text
Before
~~~
Nested tilde fence
~~~
After
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].is_closed is True
    assert "~~~" in blocks[0].content  # Tildes are content


def test_nested_fences_reverse_mixed_types():
    """Test nested fences with reverse mixed types (~~~ containing ```)."""
    md = """~~~markdown
Before
```python
def hello():
    print("world")
```
After
~~~"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "~~~"
    assert blocks[0].is_closed is True
    assert "```python" in blocks[0].content
    assert "def hello():" in blocks[0].content
    assert "```" in blocks[0].content


def test_deep_nesting():
    """Test deep nesting scenarios (3+ levels)."""
    md = """`````
Level 1
````
Level 2
~~~
Level 3
~~~
````
`````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1  # Only the outermost block
    assert blocks[0].fence_type == "```"
    assert blocks[0].is_closed is True

    # All inner content should be preserved
    content = blocks[0].content
    assert "Level 1" in content
    assert "````" in content
    assert "Level 2" in content
    assert "~~~" in content
    assert "Level 3" in content


def test_unclosed_nested_blocks():
    """Test handling of unclosed nested blocks."""
    md = """````markdown
Outer block
~~~python
print("nested but not closed")
# No closing ~~~
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].is_closed is True

    # Inner unclosed ~~~ should still be content
    assert "~~~python" in blocks[0].content
    assert 'print("nested but not closed")' in blocks[0].content


def test_multiple_nested_blocks_same_level():
    """Test multiple nested blocks at the same level."""
    md = """````markdown
First section
~~~python
code1()
~~~

Second section
~~~javascript
code2();
~~~
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"

    content = blocks[0].content
    assert "First section" in content
    assert "~~~python" in content
    assert "code1()" in content
    assert "Second section" in content
    assert "~~~javascript" in content
    assert "code2();" in content


def test_nested_with_same_fence_type():
    """Test nesting with same fence type (different lengths)."""
    md = """`````
Outer with 5 backticks
````
Inner with 4 backticks
````
`````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].is_closed is True

    content = blocks[0].content
    assert "Outer with 5 backticks" in content
    assert "````" in content
    assert "Inner with 4 backticks" in content


def test_nested_with_language_attributes():
    """Test nested blocks with language attributes."""
    md = """````markdown title="Example"
# Markdown Example

~~~python {.highlight}
def example():
    return "nested"
~~~
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].language == "markdown"

    content = blocks[0].content
    assert "# Markdown Example" in content
    assert "~~~python {.highlight}" in content
    assert "def example():" in content


def test_no_phantom_blocks_for_inner_fences():
    """Test that inner fence markers don't create phantom blocks."""
    md = """````
Outer
~~~
This should not be a separate block
~~~
````"""

    blocks = extract_fenced_blocks(md)

    # Should only have 1 block, not 2
    assert len(blocks) == 1

    # Should not have any blocks with ~~~ fence_type
    tilde_blocks = [b for b in blocks if b.fence_type == "~~~"]
    assert len(tilde_blocks) == 0


def test_complex_real_world_example():
    """Test complex real-world nested fence example."""
    md = """````markdown
# Documentation Example

This shows how to use code blocks:

~~~python
# Python example
def process_data(data):
    '''Process the data'''
    return data.strip()
~~~

And here's a JavaScript example:

~~~javascript
// JavaScript example
function processData(data) {
    return data.trim();
}
~~~

That's how you document code!
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"
    assert blocks[0].language == "markdown"

    content = blocks[0].content
    # Should contain all the nested content
    assert "# Documentation Example" in content
    assert "~~~python" in content
    assert "def process_data" in content
    assert "~~~javascript" in content
    assert "function processData" in content
    assert "That's how you document code!" in content


def test_edge_case_empty_nested_block():
    """Test edge case with empty nested block."""
    md = """````
Outer
~~~
~~~
````"""

    blocks = extract_fenced_blocks(md)
    assert len(blocks) == 1
    assert blocks[0].fence_type == "```"

    content = blocks[0].content
    assert "Outer" in content
    assert "~~~" in content


def test_regression_no_phantom_blocks():
    """Regression test to ensure no phantom blocks are created."""
    md = """````markdown
Example with nested code:

~~~python
print("hello")
~~~

End of example.
````"""

    blocks = extract_fenced_blocks(md)

    # Critical: Should be exactly 1 block, not 2
    assert len(blocks) == 1, f"Expected 1 block, got {len(blocks)}"

    # Should be the outer markdown block
    assert blocks[0].fence_type == "```"
    assert blocks[0].language == "markdown"

    # Should not have any ~~~ blocks
    for block in blocks:
        assert block.fence_type != "~~~", "Found phantom ~~~ block"


if __name__ == "__main__":  # noqa: C901
    # Run tests manually for debugging
    # Complexity justified: Test runner with sequential execution
    print("🔍 Testing Nested Fence Handling...")

    try:
        test_nested_fences_not_separate_blocks()
        print("✅ Basic nested fence handling")
    except Exception as e:
        print(f"❌ Basic nested fence test failed: {e}")

    try:
        test_nested_fences_mixed_types()
        print("✅ Mixed fence types")
    except Exception as e:
        print(f"❌ Mixed fence types test failed: {e}")

    try:
        test_deep_nesting()
        print("✅ Deep nesting")
    except Exception as e:
        print(f"❌ Deep nesting test failed: {e}")

    try:
        test_no_phantom_blocks_for_inner_fences()
        print("✅ No phantom blocks")
    except Exception as e:
        print(f"❌ Phantom blocks test failed: {e}")

    try:
        test_regression_no_phantom_blocks()
        print("✅ Regression test passed")
    except Exception as e:
        print(f"❌ Regression test failed: {e}")

    print("\n🎉 Nested Fence Handling testing completed!")
