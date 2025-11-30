"""Tests for parser.ast module (skeleton tests)."""

from markdown_chunker.parser import ast


class TestMarkdownNode:
    """Test MarkdownNode class (skeleton)."""

    def test_can_instantiate(self):
        """Test that MarkdownNode can be instantiated."""
        # Will need proper NodeType after migration
        node = ast.MarkdownNode(node_type="paragraph", content="test")
        assert node is not None


class TestASTBuilder:
    """Test ASTBuilder class (skeleton)."""

    def test_can_instantiate(self):
        """Test that ASTBuilder can be instantiated."""
        builder = ast.ASTBuilder()
        assert builder is not None

    def test_can_instantiate_with_parser_name(self):
        """Test that ASTBuilder can be instantiated with parser name."""
        builder = ast.ASTBuilder(parser_name="markdown-it-py")
        assert builder is not None


class TestBackwardCompatibility:
    """Test backward compatibility aliases (skeleton)."""

    def test_enhanced_ast_builder_alias(self):
        """Test that EnhancedASTBuilder alias exists."""
        assert hasattr(ast, "EnhancedASTBuilder")
        assert ast.EnhancedASTBuilder is ast.ASTBuilder
