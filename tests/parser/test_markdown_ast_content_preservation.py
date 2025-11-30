#!/usr/bin/env python3
"""
Test script for AST content preservation fixes.

This script tests the critical fixes for MarkdownItPyAdapter:
- Content preservation in paragraph and header nodes
- Proper hierarchy (paragraphs as siblings, not children of headers)
- Inline code content preservation
- Complex nested structures
"""


from markdown_chunker.parser import parse_to_ast
from markdown_chunker.parser.types import NodeType


def test_paragraph_has_actual_content():
    """Test that paragraph nodes contain actual content, not empty strings."""
    md = "This is a paragraph with content."
    ast = parse_to_ast(md)

    # Should have one paragraph child
    assert len(ast.children) == 1
    paragraph = ast.children[0]
    assert paragraph.type == NodeType.PARAGRAPH
    assert paragraph.content == "This is a paragraph with content."
    assert paragraph.content != ""  # Critical: content should not be empty


def test_header_has_actual_content():
    """Test that header nodes contain actual content, not empty strings."""
    md = "# Header Text"
    ast = parse_to_ast(md)

    # Should have one header child
    assert len(ast.children) == 1
    header = ast.children[0]
    assert header.type == NodeType.HEADER
    assert header.content == "Header Text"
    assert header.content != ""  # Critical: content should not be empty


def test_header_not_nesting_paragraphs():
    """Test that paragraphs are siblings of headers, not children."""
    md = """# Header

Paragraph text."""
    ast = parse_to_ast(md)

    # Should have 2 children: header + paragraph as siblings
    assert len(ast.children) == 2
    assert ast.children[0].type == NodeType.HEADER
    assert ast.children[1].type == NodeType.PARAGRAPH

    # CRITICAL: Paragraph should NOT be child of header
    header = ast.children[0]
    assert len(header.children) == 0, "Header should not have paragraph as child"

    # Both should have content
    assert header.content == "Header"
    assert ast.children[1].content == "Paragraph text."


def test_inline_code_content_preserved():
    """Test that inline code content is preserved in parent paragraphs."""
    md = "Text with `inline code` here."
    ast = parse_to_ast(md)

    # Should have one paragraph
    assert len(ast.children) == 1
    paragraph = ast.children[0]
    assert paragraph.type == NodeType.PARAGRAPH

    # Content should include the inline code
    content = paragraph.content
    assert "inline code" in content or "`inline code`" in content
    assert content != ""  # Should not be empty


def test_multiple_inline_elements():
    """Test content preservation with multiple inline elements."""
    md = "Text with `code` and **bold** and *italic* elements."
    ast = parse_to_ast(md)

    # Should have one paragraph
    assert len(ast.children) == 1
    paragraph = ast.children[0]
    assert paragraph.type == NodeType.PARAGRAPH

    # Content should include all text
    content = paragraph.content
    assert "Text with" in content
    assert "code" in content
    assert "bold" in content
    assert "italic" in content
    assert "elements" in content
    assert content != ""


def test_complex_nested_structure():
    """Test proper hierarchy with complex nested structures."""
    md = """# Main Header

This is the first paragraph.

## Subsection

This is another paragraph.

### Deep Header

Final paragraph here."""

    ast = parse_to_ast(md)

    # Should have multiple top-level children
    assert len(ast.children) >= 6  # 3 headers + 3 paragraphs

    # Check that all nodes have content
    for child in ast.children:
        if child.type in [NodeType.HEADER, NodeType.PARAGRAPH]:
            assert child.content != "", f"Node {child.type} should have content"

    # Verify specific content
    main_header = ast.children[0]
    assert main_header.type == NodeType.HEADER
    assert "Main Header" in main_header.content

    first_paragraph = ast.children[1]
    assert first_paragraph.type == NodeType.PARAGRAPH
    assert "first paragraph" in first_paragraph.content


def test_empty_lines_handling():
    """Test that empty lines don't break content preservation."""
    md = """# Header


Paragraph after empty lines.


Another paragraph."""

    ast = parse_to_ast(md)

    # Should have header and paragraphs with content
    header_found = False
    paragraph_count = 0

    for child in ast.children:
        if child.type == NodeType.HEADER:
            assert child.content != ""
            assert "Header" in child.content
            header_found = True
        elif child.type == NodeType.PARAGRAPH:
            assert child.content != ""
            paragraph_count += 1

    assert header_found
    assert paragraph_count >= 2


def test_mixed_content_preservation():
    """Test content preservation in mixed content scenarios."""
    md = """# API Documentation

This document describes the API endpoints.

```python
def hello():
    return "world"
```

The function above returns a greeting."""

    ast = parse_to_ast(md)

    # Find and verify different node types
    header_found = False
    paragraph_count = 0

    for child in ast.children:
        if child.type == NodeType.HEADER:
            assert child.content != ""
            assert "API Documentation" in child.content
            header_found = True
        elif child.type == NodeType.PARAGRAPH:
            assert child.content != ""
            paragraph_count += 1
        elif child.type == NodeType.CODE_BLOCK:
            pass

    assert header_found
    assert paragraph_count >= 2
    # Note: Code block handling may vary by parser


def test_regression_empty_content_bug():
    """Regression test to ensure the empty content bug doesn't return."""
    md = """# Test Header

Test paragraph with content.

## Another Header

Another paragraph."""

    ast = parse_to_ast(md)

    # Every header and paragraph should have non-empty content
    empty_content_nodes = []

    for child in ast.children:
        if child.type in [NodeType.HEADER, NodeType.PARAGRAPH]:
            if not child.content or child.content.strip() == "":
                empty_content_nodes.append(child.type)

    assert (
        len(empty_content_nodes) == 0
    ), f"Found nodes with empty content: {empty_content_nodes}"


def test_single_word_content():
    """Test content preservation for single words."""
    md = "Word"
    ast = parse_to_ast(md)

    assert len(ast.children) == 1
    paragraph = ast.children[0]
    assert paragraph.type == NodeType.PARAGRAPH
    assert paragraph.content == "Word"


def test_special_characters_content():
    """Test content preservation with special characters."""
    md = "Text with special chars: @#$%^&*()_+-=[]{}|;':\",./<>?"
    ast = parse_to_ast(md)

    assert len(ast.children) == 1
    paragraph = ast.children[0]
    assert paragraph.type == NodeType.PARAGRAPH
    assert "@#$%^&*" in paragraph.content
    assert paragraph.content != ""


if __name__ == "__main__":  # noqa: C901
    # Run tests manually for debugging
    # Complexity justified: Test runner with sequential execution
    print("🔍 Testing AST Content Preservation...")

    try:
        test_paragraph_has_actual_content()
        print("✅ Paragraph content preservation")
    except Exception as e:
        print(f"❌ Paragraph content test failed: {e}")

    try:
        test_header_has_actual_content()
        print("✅ Header content preservation")
    except Exception as e:
        print(f"❌ Header content test failed: {e}")

    try:
        test_header_not_nesting_paragraphs()
        print("✅ Proper header-paragraph hierarchy")
    except Exception as e:
        print(f"❌ Hierarchy test failed: {e}")

    try:
        test_inline_code_content_preserved()
        print("✅ Inline code content preservation")
    except Exception as e:
        print(f"❌ Inline code test failed: {e}")

    try:
        test_regression_empty_content_bug()
        print("✅ Regression test passed")
    except Exception as e:
        print(f"❌ Regression test failed: {e}")

    print("\n🎉 AST Content Preservation testing completed!")
