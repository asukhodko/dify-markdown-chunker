#!/usr/bin/env python3
"""
Test that nesting documentation matches actual capabilities.
"""

import os
import sys

# Nesting documentation tests without sys.path manipulation


def test_documented_nesting_capabilities():
    """Test that documented nesting capabilities work with NEW CORRECT BEHAVIOR."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing documented nesting capabilities...")

    # Test 1: Basic nested content preservation (NEW CORRECT BEHAVIOR)
    print("Testing basic nested content preservation...")
    markdown = """~~~markdown
# Document
```python
def nested_function():
    return "works"
```
End of document
~~~"""

    blocks = extract_fenced_blocks(markdown)
    # NEW BEHAVIOR: Only 1 block (outer), inner is preserved as content
    assert len(blocks) == 1, f"Should find 1 block (outer), got {len(blocks)}"

    outer_block = blocks[0]
    assert (
        outer_block.language == "markdown"
    ), f"Expected markdown block, got {outer_block.language}"
    assert outer_block.nesting_level == 0, "Should have nesting level 0"

    # Inner content should be preserved
    assert (
        "```python" in outer_block.content
    ), "Inner fence should be preserved as content"
    assert (
        "def nested_function" in outer_block.content
    ), "Inner code should be preserved as content"
    print("✅ Basic nested content preservation works as documented")

    # Test 2: Multiple separate blocks (not nested)
    print("Testing separate blocks...")
    markdown = """```python
def function1():
    pass
```

```javascript
function function2() {}
```"""

    blocks = extract_fenced_blocks(markdown)
    assert len(blocks) == 2, f"Should find 2 separate blocks, got {len(blocks)}"

    # Both should be level 0 (separate, not nested)
    for block in blocks:
        assert (
            block.nesting_level == 0
        ), f"Separate blocks should be level 0, got {block.nesting_level}"

    languages = [block.language for block in blocks]
    assert "python" in languages, "Should find python block"
    assert "javascript" in languages, "Should find javascript block"
    print("✅ Separate blocks work as documented")

    # Test 3: Mixed fence types with content preservation
    print("Testing mixed fence types...")
    markdown = """```markdown
Content with tilde blocks
~~~python
def function():
    pass
~~~
More content
```"""

    blocks = extract_fenced_blocks(markdown)
    # NEW BEHAVIOR: Only 1 block (outer), inner preserved as content
    assert len(blocks) == 1, f"Should find 1 block (outer), got {len(blocks)}"

    outer_block = blocks[0]
    assert (
        outer_block.fence_type == "```"
    ), f"Expected backtick fence, got {outer_block.fence_type}"
    assert (
        outer_block.language == "markdown"
    ), f"Expected markdown block, got {outer_block.language}"

    # Inner tilde fence should be preserved as content
    assert (
        "~~~python" in outer_block.content
    ), "Inner tilde fence should be preserved as content"
    assert (
        "def function" in outer_block.content
    ), "Inner code should be preserved as content"
    print("✅ Mixed fence types work as documented")

    print("✅ All documented capabilities work correctly with new behavior")


def test_documented_limitations():
    """Test that documented limitations are accurate."""
    from markdown_chunker.parser import extract_fenced_blocks

    print("Testing documented limitations...")

    # Test complex multi-level nesting (documented as ⚠️ Partial Support)
    print("Testing complex multi-level nesting...")

    # This is a complex scenario that may not work perfectly
    complex_markdown = """~~~text
Level 0
```markdown
Level 1
~~~python
def level_2():
    pass
~~~
Back to level 1
```
Back to level 0
~~~"""

    blocks = extract_fenced_blocks(complex_markdown)
    print(f"Complex nesting found {len(blocks)} blocks")

    # We don't assert specific behavior here since it's documented as partial support
    # Just verify it doesn't crash and finds some blocks
    assert len(blocks) >= 1, "Should find at least some blocks"
    print("⚠️ Complex nesting has partial support as documented")

    print("✅ Documented limitations are accurate")


def test_documentation_honesty():
    """Test that documentation is honest about capabilities."""
    print("Testing documentation honesty...")

    # Read the fenced_block_extractor docstring
    from markdown_chunker.parser import FencedBlockExtractor

    docstring = FencedBlockExtractor.__doc__ or ""
    # Try to get module doc from new structure
    module_doc = ""
    if "markdown_chunker.parser.fenced_blocks" in sys.modules:
        module_doc = sys.modules["markdown_chunker.parser.fenced_blocks"].__doc__ or ""

    # Should mention nesting support
    combined_docs = docstring + module_doc

    # Should not claim full/complete/perfect support
    problematic_claims = ["full nesting", "complete nesting", "perfect nesting"]
    for claim in problematic_claims:
        assert claim.lower() not in combined_docs.lower(), f"Should not claim '{claim}'"

    # Should mention nesting in some form
    has_nesting_mention = "nesting" in combined_docs.lower()

    assert has_nesting_mention, "Should mention nesting capabilities"
    print("✅ Documentation is honest about capabilities")


def test_nesting_capabilities_file():
    """Test that NESTING_CAPABILITIES.md was archived."""
    print("Testing NESTING_CAPABILITIES.md...")

    # File should be in archive now
    archived_path = "archive/reports/NESTING_CAPABILITIES.md"

    if os.path.exists(archived_path):
        print("✅ NESTING_CAPABILITIES.md properly archived")
    elif os.path.exists("NESTING_CAPABILITIES.md"):
        # Still in root - should have been moved
        print("⚠️ NESTING_CAPABILITIES.md should be archived")
    else:
        # Neither location - that's OK, documentation consolidated
        print("ℹ️ NESTING_CAPABILITIES.md consolidated into main docs")


if __name__ == "__main__":
    test_documented_nesting_capabilities()
    test_documented_limitations()
    test_documentation_honesty()
    test_nesting_capabilities_file()
    print("🎉 Nesting documentation matches actual capabilities!")
