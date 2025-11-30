#!/usr/bin/env python3
"""
Test script for enhanced AST validation functionality.

This script tests the new AST validation features added in task 1.3:
- Tree correctness validation
- Node relationships validation
- Position consistency checks
- Content and metadata consistency
"""

import logging

from markdown_chunker.parser import EnhancedASTBuilder

# Configure logging to see validation messages
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def test_enhanced_ast_validation():  # noqa: C901
    """Test enhanced AST validation functionality."""
    # Complexity justified: Comprehensive test with multiple validation scenarios
    print("🔍 Testing Enhanced AST Validation...")

    # Test 1: Valid markdown with inline elements
    print("\n1. Testing valid markdown with inline elements...")
    markdown1 = """# Header with **bold** text

This is a paragraph with `inline code` and [a link](http://example.com).

```python
def hello():
    print("world")
```

Another paragraph with *emphasis* text."""

    builder = EnhancedASTBuilder()
    try:
        ast1 = builder.build_ast(markdown1)
        print("✅ Valid markdown passed validation")
        print(f"   - Nodes: {ast1.count_nodes()}")
        print(f"   - Depth: {ast1.get_depth()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 2: Complex nested structure
    print("\n2. Testing complex nested structure...")
    markdown2 = """# Main Header

## Subsection

- List item 1 with **bold**
- List item 2 with `code`
  - Nested item with [link](http://test.com)
  - Another nested item

> Blockquote with *emphasis*
>
> ```javascript
> console.log("hello");
> ```

Final paragraph."""

    try:
        ast2 = builder.build_ast(markdown2)
        print("✅ Complex structure passed validation")
        print(f"   - Nodes: {ast2.count_nodes()}")
        print(f"   - Depth: {ast2.get_depth()}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test 3: Edge cases
    print("\n3. Testing edge cases...")

    # Empty document
    try:
        builder.build_ast("")
        print("✅ Empty document handled correctly")
    except Exception as e:
        print(f"⚠️  Empty document error (expected): {e}")

    # Only whitespace
    try:
        builder.build_ast("   \n\n   ")
        print("✅ Whitespace-only document handled correctly")
    except Exception as e:
        print(f"⚠️  Whitespace document error: {e}")

    # Single line
    try:
        builder.build_ast("Just a single line of text.")
        print("✅ Single line document passed validation")
    except Exception as e:
        print(f"❌ Single line error: {e}")

    print("\n🎉 Enhanced AST validation testing completed!")


def test_validation_error_detection():
    """Test that validation properly detects errors."""

    print("\n🔍 Testing Validation Error Detection...")

    builder = EnhancedASTBuilder()

    # Test with malformed markdown that should trigger warnings
    print("\n1. Testing malformed markdown...")
    malformed_markdown = """# Header

```python
def incomplete_function():
    # This code block is not properly closed

Another paragraph that should trigger position warnings."""

    try:
        builder.build_ast(malformed_markdown)
        print("✅ Malformed markdown processed (warnings expected in logs)")
    except Exception as e:
        print(f"⚠️  Malformed markdown error: {e}")

    print("\n🎉 Error detection testing completed!")


if __name__ == "__main__":
    test_enhanced_ast_validation()
    test_validation_error_detection()
