"""
AST building and node classes for markdown documents.

This module consolidates all AST-related functionality including node classes,
AST building, and nesting resolution.

Algorithm Documentation:
    - AST Building: docs/markdown-extractor/06-algorithms/parsing.md
    - Data Structures: docs/markdown-extractor/05-data-structures/

Consolidates:
- markdown_ast.py::MarkdownNode and related classes
- enhanced_ast_builder.py::EnhancedASTBuilder
- nesting_resolver.py::NestingResolver

Classes:
    MarkdownNode: Base AST node with position tracking
    ASTBuilder: Build markdown AST with nesting resolution

Aliases:
    EnhancedASTBuilder: Backward compatibility alias for ASTBuilder
"""

from typing import Any, Dict, List, Optional

# Imports will be added during migration
# from .types import NodeType, Position


class MarkdownNode:
    """Base class for all AST nodes."""

    def __init__(self, node_type: str, content: str = "", position=None):
        """Initialize a markdown node."""
        self.type = node_type
        self.content = content
        self.children: List["MarkdownNode"] = []
        self.position = position
        self.metadata: Dict[str, Any] = {}
        self.parent: Optional["MarkdownNode"] = None

    def add_child(self, child: "MarkdownNode") -> None:
        """Add a child node."""
        child.parent = self
        self.children.append(child)

    def remove_child(self, child: "MarkdownNode") -> None:
        """Remove a child node."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def find_children(self, node_type: str) -> List["MarkdownNode"]:
        """Find direct children of specified type."""
        return [child for child in self.children if child.type == node_type]

    def find_descendants(self, node_type: str) -> List["MarkdownNode"]:
        """Find all descendants of specified type."""
        result = []
        for child in self.children:
            if child.type == node_type:
                result.append(child)
            result.extend(child.find_descendants(node_type))
        return result

    def get_text_content(self) -> str:
        """Get all text content from this node and children."""
        text_parts = [self.content] if self.content else []
        for child in self.children:
            text_parts.append(child.get_text_content())
        return "".join(text_parts)

    def get_line_range(self) -> tuple:
        """Get the line range (start, end) for this node."""
        if self.position:
            return (self.position.line, self.position.line)
        return (0, 0)

    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        result = {
            "type": self.type,
            "content": self.content,
            "metadata": self.metadata.copy(),
            "children": [child.to_dict() for child in self.children],
        }
        if self.position:
            result["position"] = {
                "line": self.position.line,
                "column": self.position.column,
                "offset": self.position.offset,
            }
        return result

    def __repr__(self) -> str:
        """String representation for debugging."""
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return (
            f"MarkdownNode(type='{self.type}', "
            f"content='{content_preview}', "
            f"children={len(self.children)})"
        )


class ASTBuilder:
    """Build markdown AST with enhanced features."""

    def __init__(self, parser_name: str = "markdown-it-py"):
        """Initialize AST builder."""
        self.parser_name = parser_name
        self._setup_parser()

    def _setup_parser(self):
        """Setup the underlying parser."""
        if self.parser_name == "markdown-it-py":
            try:
                from markdown_it import MarkdownIt

                self.parser = MarkdownIt()
            except ImportError:
                self.parser_name = "mistune"
                self._setup_mistune()
        else:
            self._setup_mistune()

    def _setup_mistune(self):
        """Setup mistune parser as fallback."""
        try:
            import mistune

            self.parser = mistune.create_markdown(renderer=None)
        except ImportError:
            raise ImportError("Neither markdown-it-py nor mistune is available")

    def build(self, md_text: str) -> MarkdownNode:
        """Build AST from markdown text."""
        if self.parser_name == "markdown-it-py":
            return self._build_from_markdown_it(md_text)
        else:
            return self._build_from_mistune(md_text)

    # Backward compatibility alias
    def build_ast(self, md_text: str) -> MarkdownNode:
        """Alias for build() (backward compatibility)."""
        return self.build(md_text)

    def _build_from_markdown_it(self, md_text: str) -> MarkdownNode:
        """Build AST using markdown-it-py."""
        tokens = self.parser.parse(md_text)
        root = MarkdownNode("document")
        self._convert_tokens_to_nodes(tokens, root, md_text)
        self._resolve_nesting(root)
        return root

    def _build_from_mistune(self, md_text: str) -> MarkdownNode:
        """Build AST using mistune."""
        root = MarkdownNode("document")
        # Simplified mistune conversion
        root.content = md_text
        return root

    def _convert_tokens_to_nodes(self, tokens, parent: MarkdownNode, md_text: str):
        """Convert markdown-it tokens to MarkdownNode tree."""
        for token in tokens:
            node = self._token_to_node(token, md_text)
            parent.add_child(node)

            # Handle nested tokens
            if hasattr(token, "children") and token.children:
                self._convert_tokens_to_nodes(token.children, node, md_text)

    def _token_to_node(self, token, md_text: str) -> MarkdownNode:
        """Convert a single token to MarkdownNode."""
        from .types import Position

        node_type = token.type
        content = getattr(token, "content", "")

        # Create position if available
        position = None
        if hasattr(token, "map") and token.map:
            line_start, line_end = token.map
            position = Position(line=line_start + 1, column=0, offset=0)

        node = MarkdownNode(node_type, content, position)

        # Add token-specific metadata
        if hasattr(token, "info"):
            node.metadata["info"] = token.info
        if hasattr(token, "level"):
            node.metadata["level"] = token.level
        if hasattr(token, "markup"):
            node.metadata["markup"] = token.markup

        return node

    def _resolve_nesting(self, root: MarkdownNode) -> None:
        """Resolve nesting relationships (integrated from NestingResolver)."""
        # Enhanced nesting resolution from nesting_resolver.py
        self._resolve_list_nesting(root)
        self._resolve_header_hierarchy(root)
        self._resolve_blockquote_nesting(root)
        self._calculate_nesting_levels(root)

    def _resolve_list_nesting(self, node: MarkdownNode) -> None:
        """Resolve list item nesting with proper depth calculation."""
        if node.type == "list":
            self._process_list_items(node)

        for child in node.children:
            self._resolve_list_nesting(child)

    def _process_list_items(self, list_node: MarkdownNode) -> None:
        """Process list items and calculate nesting depth."""
        current_depth = 0
        for child in list_node.children:
            if child.type == "list_item":
                child.metadata["nesting_depth"] = current_depth
                # Check for nested lists
                nested_lists = child.find_children("list")
                for nested_list in nested_lists:
                    self._increase_list_depth(nested_list, current_depth + 1)

    def _increase_list_depth(self, list_node: MarkdownNode, depth: int) -> None:
        """Recursively increase depth for nested lists."""
        list_node.metadata["nesting_depth"] = depth
        for item in list_node.find_children("list_item"):
            item.metadata["nesting_depth"] = depth
            # Process further nested lists
            for nested in item.find_children("list"):
                self._increase_list_depth(nested, depth + 1)

    def _resolve_header_hierarchy(self, node: MarkdownNode) -> None:
        """Resolve header hierarchy with proper parent-child relationships."""
        headers = node.find_descendants("heading")
        header_stack = []  # Stack to track header hierarchy

        for header in headers:
            level = header.metadata.get("level", 1)
            header.metadata["hierarchy_level"] = level

            # Pop headers with higher or equal level from stack
            while header_stack and header_stack[-1].metadata.get("level", 1) >= level:
                header_stack.pop()

            # Set parent relationship
            if header_stack:
                parent_header = header_stack[-1]
                header.metadata["parent_header"] = parent_header
                if "child_headers" not in parent_header.metadata:
                    parent_header.metadata["child_headers"] = []
                parent_header.metadata["child_headers"].append(header)

            header_stack.append(header)

    def _resolve_blockquote_nesting(self, node: MarkdownNode) -> None:
        """Resolve blockquote nesting levels."""
        if node.type == "blockquote":
            self._calculate_blockquote_depth(node, 0)

        for child in node.children:
            self._resolve_blockquote_nesting(child)

    def _calculate_blockquote_depth(self, node: MarkdownNode, depth: int) -> None:
        """Calculate blockquote nesting depth."""
        node.metadata["nesting_depth"] = depth

        for child in node.children:
            if child.type == "blockquote":
                self._calculate_blockquote_depth(child, depth + 1)
            else:
                child.metadata["blockquote_depth"] = depth

    def _calculate_nesting_levels(self, node: MarkdownNode, level: int = 0) -> None:
        """Calculate overall nesting levels for all nodes."""
        node.metadata["overall_nesting_level"] = level

        for child in node.children:
            child_level = level
            if child.type in ["list", "blockquote", "list_item"]:
                child_level += 1
            self._calculate_nesting_levels(child, child_level)


# Backward compatibility alias
EnhancedASTBuilder = ASTBuilder


# Backward compatibility alias
EnhancedASTBuilder = ASTBuilder
