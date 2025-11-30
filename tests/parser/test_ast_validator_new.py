"""
Comprehensive tests for ASTValidator (NEW CODE).

These tests specifically target the NEW ASTValidator in validation.py.
"""

from markdown_chunker.parser.ast import MarkdownNode
from markdown_chunker.parser.validation import (
    ASTValidator,
    ValidationIssue,
    ValidationResult,
    validate_ast_structure,
)


class TestASTValidatorNew:
    """Test ASTValidator from validation.py (NEW CODE)."""

    def test_instantiation(self):
        """Test that ASTValidator can be instantiated."""
        validator = ASTValidator()
        assert validator is not None
        assert hasattr(validator, "validate_ast")

    def test_validate_simple_ast(self):
        """Test validating a simple AST."""
        root = MarkdownNode("document")
        para = MarkdownNode("paragraph", "Test content")
        root.add_child(para)

        validator = ASTValidator()
        result = validator.validate_ast(root)

        assert result is not None
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_validate_empty_ast(self):
        """Test validating empty AST."""
        root = MarkdownNode("document")

        validator = ASTValidator()
        result = validator.validate_ast(root)

        assert result is not None
        assert result.is_valid is True

    def test_validate_nested_ast(self):
        """Test validating nested AST structure."""
        root = MarkdownNode("document")
        section = MarkdownNode("section")
        para1 = MarkdownNode("paragraph", "Para 1")
        para2 = MarkdownNode("paragraph", "Para 2")

        root.add_child(section)
        section.add_child(para1)
        section.add_child(para2)

        validator = ASTValidator()
        result = validator.validate_ast(root)

        assert result is not None
        assert result.is_valid is True

    def test_validation_result_properties(self):
        """Test ValidationResult properties."""
        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.issues == []
        assert result.node_count == 0
        assert result.max_depth == 0

    def test_validation_result_add_issue(self):
        """Test adding issues to ValidationResult."""
        result = ValidationResult(is_valid=True)

        result.add_issue("error", "Test error")

        assert result.is_valid is False
        assert len(result.issues) == 1
        assert result.issues[0].severity == "error"
        assert result.issues[0].message == "Test error"

    def test_validation_result_get_errors(self):
        """Test getting errors from ValidationResult."""
        result = ValidationResult(is_valid=True)

        result.add_issue("error", "Error 1")
        result.add_issue("warning", "Warning 1")
        result.add_issue("error", "Error 2")

        errors = result.get_errors()
        assert len(errors) == 2
        assert all(e.severity == "error" for e in errors)

    def test_validation_result_get_warnings(self):
        """Test getting warnings from ValidationResult."""
        result = ValidationResult(is_valid=True)

        result.add_issue("error", "Error 1")
        result.add_issue("warning", "Warning 1")
        result.add_issue("warning", "Warning 2")

        warnings = result.get_warnings()
        assert len(warnings) == 2
        assert all(w.severity == "warning" for w in warnings)

    def test_validation_result_has_errors(self):
        """Test has_errors method."""
        result = ValidationResult(is_valid=True)

        assert result.has_errors() is False

        result.add_issue("error", "Test error")
        assert result.has_errors() is True

    def test_validation_result_has_warnings(self):
        """Test has_warnings method."""
        result = ValidationResult(is_valid=True)

        assert result.has_warnings() is False

        result.add_issue("warning", "Test warning")
        assert result.has_warnings() is True

    def test_convenience_function_validate_ast_structure(self):
        """Test validate_ast_structure convenience function."""
        root = MarkdownNode("document")
        para = MarkdownNode("paragraph", "Content")
        root.add_child(para)

        result = validate_ast_structure(root)

        assert result is not None
        assert isinstance(result, ValidationResult)


class TestValidationIssueNew:
    """Test ValidationIssue dataclass."""

    def test_validation_issue_creation(self):
        """Test creating ValidationIssue."""
        issue = ValidationIssue(
            severity="error",
            message="Test error",
            node_type="paragraph",
            details="Additional details",
        )

        assert issue.severity == "error"
        assert issue.message == "Test error"
        assert issue.node_type == "paragraph"
        assert issue.details == "Additional details"

    def test_validation_issue_optional_fields(self):
        """Test ValidationIssue with optional fields."""
        issue = ValidationIssue(severity="warning", message="Test warning")

        assert issue.severity == "warning"
        assert issue.message == "Test warning"
        assert issue.node_type is None
        assert issue.position is None
        assert issue.details is None


class TestASTValidatorEdgeCases:
    """Test edge cases for ASTValidator."""

    def test_validate_ast_with_invalid_content(self):
        """Test validating AST with invalid content type."""
        root = MarkdownNode("document")
        # Manually set invalid content
        root.content = 123  # Should be string

        validator = ASTValidator()
        result = validator.validate_ast(root)

        # Should detect error
        assert len(result.get_errors()) > 0

    def test_validate_ast_with_invalid_metadata(self):
        """Test validating AST with invalid metadata type."""
        root = MarkdownNode("document")
        # Manually set invalid metadata
        root.metadata = "invalid"  # Should be dict

        validator = ASTValidator()
        result = validator.validate_ast(root)

        # Should detect error
        assert len(result.get_errors()) > 0

    def test_validate_ast_with_invalid_children(self):
        """Test validating AST with invalid children type."""
        root = MarkdownNode("document")
        # Manually set invalid children
        root.children = "invalid"  # Should be list

        validator = ASTValidator()
        result = validator.validate_ast(root)

        # Should detect error
        assert len(result.get_errors()) > 0

    def test_validate_deeply_nested_ast(self):
        """Test validating deeply nested AST."""
        root = MarkdownNode("document")
        current = root

        # Create 10 levels of nesting
        for i in range(10):
            child = MarkdownNode("section", f"Level {i}")
            current.add_child(child)
            current = child

        validator = ASTValidator()
        result = validator.validate_ast(root)

        # Should handle deep nesting
        assert result is not None

    def test_validate_ast_with_many_children(self):
        """Test validating AST with many children."""
        root = MarkdownNode("document")

        # Add 100 children
        for i in range(100):
            child = MarkdownNode("paragraph", f"Para {i}")
            root.add_child(child)

        validator = ASTValidator()
        result = validator.validate_ast(root)

        # Should handle many children
        assert result is not None

    def test_validate_ast_with_exception(self):
        """Test that validator handles exceptions gracefully."""

        # Create a mock object that will cause an exception
        class BadNode:
            pass

        bad_node = BadNode()

        validator = ASTValidator()
        result = validator.validate_ast(bad_node)

        # Should catch exception and add error
        assert result.is_valid is False
        assert len(result.get_errors()) > 0
