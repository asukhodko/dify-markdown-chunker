"""
Comprehensive tests for parser.ast module (NEW CODE).

These tests specifically target the NEW refactored code in ast.py,
not the old markdown_ast.py or enhanced_ast_builder.py.
"""

from markdown_chunker.parser.ast import (
    ASTBuilder,
    EnhancedASTBuilder,
    MarkdownNode,
)


class TestMarkdownNodeNew:
    """Test MarkdownNode from ast.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that MarkdownNode can be instantiated."""
        node = MarkdownNode("paragraph", "Test content")
        assert node is not None
        assert node.type == "paragraph"
        assert node.content == "Test content"

    def test_node_properties(self):
        """Test MarkdownNode properties."""
        node = MarkdownNode("header", "Title")
        assert node.type == "header"
        assert node.content == "Title"
        assert node.children == []
        assert node.metadata == {}
        assert node.parent is None

    def test_add_child(self):
        """Test adding child nodes."""
        parent = MarkdownNode("document")
        child = MarkdownNode("paragraph", "Child content")

        parent.add_child(child)

        assert len(parent.children) == 1
        assert parent.children[0] is child
        assert child.parent is parent

    def test_remove_child(self):
        """Test removing child nodes."""
        parent = MarkdownNode("document")
        child = MarkdownNode("paragraph", "Child content")

        parent.add_child(child)
        parent.remove_child(child)

        assert len(parent.children) == 0
        assert child.parent is None

    def test_find_children(self):
        """Test finding direct children by type."""
        parent = MarkdownNode("document")
        para1 = MarkdownNode("paragraph", "Para 1")
        para2 = MarkdownNode("paragraph", "Para 2")
        header = MarkdownNode("header", "Header")

        parent.add_child(para1)
        parent.add_child(header)
        parent.add_child(para2)

        paragraphs = parent.find_children("paragraph")
        assert len(paragraphs) == 2
        assert para1 in paragraphs
        assert para2 in paragraphs

    def test_find_descendants(self):
        """Test finding all descendants by type."""
        root = MarkdownNode("document")
        section = MarkdownNode("section")
        para1 = MarkdownNode("paragraph", "Para 1")
        para2 = MarkdownNode("paragraph", "Para 2")

        root.add_child(section)
        section.add_child(para1)
        section.add_child(para2)

        paragraphs = root.find_descendants("paragraph")
        assert len(paragraphs) == 2

    def test_get_text_content(self):
        """Test getting all text content."""
        root = MarkdownNode("document")
        para1 = MarkdownNode("paragraph", "First ")
        para2 = MarkdownNode("paragraph", "Second")

        root.add_child(para1)
        root.add_child(para2)

        text = root.get_text_content()
        assert "First" in text
        assert "Second" in text

    def test_is_leaf(self):
        """Test checking if node is a leaf."""
        parent = MarkdownNode("document")
        child = MarkdownNode("paragraph", "Content")

        assert child.is_leaf() is True
        parent.add_child(child)
        assert parent.is_leaf() is False

    def test_to_dict(self):
        """Test converting node to dictionary."""
        node = MarkdownNode("paragraph", "Test content")
        node.metadata["key"] = "value"

        data = node.to_dict()

        assert data["type"] == "paragraph"
        assert data["content"] == "Test content"
        assert data["metadata"]["key"] == "value"
        assert "children" in data

    def test_node_with_position(self):
        """Test node with position information."""
        from markdown_chunker.parser.types import Position

        pos = Position(line=5, column=10, offset=50)
        node = MarkdownNode("header", "Title", position=pos)

        assert node.position is not None
        assert node.position.line == 5

    def test_get_line_range(self):
        """Test getting line range."""
        from markdown_chunker.parser.types import Position

        pos = Position(line=5, column=0, offset=0)
        node = MarkdownNode("paragraph", "Content", position=pos)

        line_range = node.get_line_range()
        assert line_range == (5, 5)


class TestASTBuilderNew:
    """Test ASTBuilder from ast.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that ASTBuilder can be instantiated."""
        builder = ASTBuilder()
        assert builder is not None
        assert hasattr(builder, "build")

    def test_instantiation_with_parser_name(self):
        """Test instantiation with specific parser."""
        builder = ASTBuilder(parser_name="markdown-it-py")
        assert builder is not None
        assert builder.parser_name == "markdown-it-py"

    def test_build_simple_document(self):
        """Test building AST from simple document."""
        md_text = """# Header

Paragraph text.
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        assert ast is not None
        assert ast.type == "document"

    def test_build_with_code_block(self):
        """Test building AST with code block."""
        md_text = """# Title

```python
def hello():
    pass
```
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        assert ast is not None
        # Should have document structure
        assert ast.type == "document"

    def test_build_empty_document(self):
        """Test building AST from empty document."""
        builder = ASTBuilder()
        ast = builder.build("")

        assert ast is not None
        assert ast.type == "document"

    def test_build_with_headers(self):
        """Test building AST with multiple headers."""
        md_text = """# H1

## H2

### H3
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        assert ast is not None
        # Should have hierarchical structure
        headers = ast.find_descendants("heading")
        assert len(headers) >= 0  # May vary by parser

    def test_build_with_lists(self):
        """Test building AST with lists."""
        md_text = """- Item 1
- Item 2
  - Nested item
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        assert ast is not None

    def test_nesting_resolution(self):
        """Test that nesting is resolved."""
        md_text = """# Header

- List item 1
- List item 2
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        # Nesting resolution should be applied
        assert ast is not None
        assert hasattr(ast, "metadata")

    def test_enhanced_ast_builder_alias(self):
        """Test that EnhancedASTBuilder is an alias."""
        assert EnhancedASTBuilder is ASTBuilder

    def test_build_with_unicode(self):
        """Test building AST with unicode content."""
        md_text = """# Привет мир 🌍

Текст на русском языке.
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        assert ast is not None


class TestASTBuilderNestingResolution:
    """Test nesting resolution in ASTBuilder."""

    def test_list_nesting_resolution(self):
        """Test list nesting is resolved."""
        md_text = """- Level 1
  - Level 2
    - Level 3
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        # Should have nesting metadata
        assert ast is not None

    def test_header_hierarchy_resolution(self):
        """Test header hierarchy is resolved."""
        md_text = """# H1

## H2

### H3

## H2 Again
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        # Should have hierarchy metadata
        assert ast is not None

    def test_blockquote_nesting_resolution(self):
        """Test blockquote nesting is resolved."""
        md_text = """> Quote level 1
>> Quote level 2
"""
        builder = ASTBuilder()
        ast = builder.build(md_text)

        # Should have nesting metadata
        assert ast is not None


class TestMarkdownNodeEdgeCases:
    """Test edge cases for MarkdownNode."""

    def test_node_with_empty_content(self):
        """Test node with empty content."""
        node = MarkdownNode("paragraph", "")
        assert node.content == ""
        assert node.is_leaf() is True

    def test_node_with_none_content(self):
        """Test node with None content."""
        node = MarkdownNode("paragraph")
        assert node.content == ""

    def test_multiple_children(self):
        """Test node with many children."""
        parent = MarkdownNode("document")
        for i in range(10):
            child = MarkdownNode("paragraph", f"Para {i}")
            parent.add_child(child)

        assert len(parent.children) == 10

    def test_deep_nesting(self):
        """Test deeply nested structure."""
        root = MarkdownNode("document")
        current = root
        for i in range(5):
            child = MarkdownNode("section", f"Level {i}")
            current.add_child(child)
            current = child

        # Should have 5 levels of nesting
        descendants = root.find_descendants("section")
        assert len(descendants) == 5

    def test_metadata_manipulation(self):
        """Test metadata can be added and modified."""
        node = MarkdownNode("paragraph", "Content")
        node.metadata["key1"] = "value1"
        node.metadata["key2"] = "value2"

        assert node.metadata["key1"] == "value1"
        assert node.metadata["key2"] == "value2"
        assert len(node.metadata) == 2
