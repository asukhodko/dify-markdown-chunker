"""
Enhanced AST Builder with inline token support.

This module provides improved AST building capabilities that properly handle
inline elements like code, links, emphasis, and other inline tokens according
to the Markdown specification.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .types import MarkdownNode, NodeType, Position


@dataclass
class InlineToken:
    """Represents an inline token (code, link, emphasis, etc.)."""

    type: str  # "inline_code", "link", "emphasis", "strong", "text"
    content: str  # Content of the token
    start_pos: int  # Position in parent text
    end_pos: int  # End position in parent text
    raw_content: str  # Original text with markup
    attributes: Dict[str, str] = field(default_factory=dict)  # href for links, etc.

    def get_length(self) -> int:
        """Get the length of the token."""
        return self.end_pos - self.start_pos


@dataclass
class SourceRange:
    """Represents a range in the source text."""

    start: Position
    end: Position

    def contains_position(self, position: Position) -> bool:
        """Check if the range contains a position."""
        return (
            position.line > self.start.line
            or (
                position.line == self.start.line
                and position.column >= self.start.column
            )
        ) and (
            position.line < self.end.line
            or (position.line == self.end.line and position.column <= self.end.column)
        )

    def get_text(self, source_text: str) -> str:
        """Extract text from the source for this range."""
        return source_text[self.start.offset : self.end.offset]


class LineTracker:
    """Tracks line and column positions in text."""

    def __init__(self, text: str):
        self.text = text
        self.lines = text.split("\n")
        self.line_offsets = self._calculate_line_offsets()

    def _calculate_line_offsets(self) -> List[int]:
        """Calculate offset of each line start."""
        offsets = [0]
        current_offset = 0

        for line in self.lines[:-1]:  # Exclude last line
            current_offset += len(line) + 1  # +1 for \n
            offsets.append(current_offset)

        return offsets

    def get_position_from_offset(self, offset: int) -> Position:
        """Get position (line, column) from offset."""
        if offset < 0 or offset > len(self.text):
            raise ValueError(f"Offset {offset} out of range")

        # Binary search for line
        line_index = self._find_line_for_offset(offset)
        line_start_offset = self.line_offsets[line_index]
        column = offset - line_start_offset

        return Position(
            line=line_index + 1, column=column + 1, offset=offset  # 1-based  # 1-based
        )

    def get_offset_from_position(self, line: int, column: int) -> int:
        """Get offset from position (line, column)."""
        if line < 1 or line > len(self.lines):
            raise ValueError(f"Line {line} out of range")

        line_index = line - 1  # Convert to 0-based
        line_start_offset = self.line_offsets[line_index]

        if column < 1:
            raise ValueError(f"Column {column} must be >= 1")

        column_offset = column - 1  # Convert to 0-based
        return line_start_offset + column_offset

    def _find_line_for_offset(self, offset: int) -> int:
        """Find line index for given offset using binary search."""
        left, right = 0, len(self.line_offsets) - 1

        while left <= right:
            mid = (left + right) // 2

            if mid == len(self.line_offsets) - 1:
                return mid

            if self.line_offsets[mid] <= offset < self.line_offsets[mid + 1]:
                return mid
            elif offset < self.line_offsets[mid]:
                right = mid - 1
            else:
                left = mid + 1

        return len(self.line_offsets) - 1


class InlineTokenProcessor:
    """Processes inline tokens in text."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_inline_tokens(self, text: str) -> List[InlineToken]:
        """Extract all inline tokens from text."""
        tokens = []

        # Extract inline code first (highest priority)
        tokens.extend(self._extract_inline_code(text))

        # Extract links
        tokens.extend(self._extract_links(text))

        # Extract emphasis and strong
        tokens.extend(self._extract_emphasis(text))

        # Sort tokens by position and merge overlapping
        return self._sort_and_merge_tokens(tokens)

    def _extract_inline_code(self, text: str) -> List[InlineToken]:
        """Extract inline code (`code`)."""
        tokens = []
        pattern = r"`([^`]+)`"

        for match in re.finditer(pattern, text):
            token = InlineToken(
                type="inline_code",
                content=match.group(1),
                start_pos=match.start(),
                end_pos=match.end(),
                raw_content=match.group(0),
            )
            tokens.append(token)

        return tokens

    def _extract_links(self, text: str) -> List[InlineToken]:
        """Extract links [text](url) and [text][ref]."""
        tokens = []

        # Inline links [text](url)
        inline_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(inline_pattern, text):
            token = InlineToken(
                type="link",
                content=match.group(1),
                start_pos=match.start(),
                end_pos=match.end(),
                raw_content=match.group(0),
                attributes={"hre": match.group(2)},
            )
            tokens.append(token)

        # Reference links [text][ref]
        ref_pattern = r"\[([^\]]+)\]\[([^\]]*)\]"
        for match in re.finditer(ref_pattern, text):
            ref = match.group(2) if match.group(2) else match.group(1)
            token = InlineToken(
                type="link",
                content=match.group(1),
                start_pos=match.start(),
                end_pos=match.end(),
                raw_content=match.group(0),
                attributes={"re": ref},
            )
            tokens.append(token)

        return tokens

    def _extract_emphasis(self, text: str) -> List[InlineToken]:
        """Extract emphasis (*text* and _text_) and strong (**text** and __text__)."""
        tokens = []

        # Strong emphasis **text** and __text__
        strong_patterns = [r"\*\*([^*]+)\*\*", r"__([^_]+)__"]
        for pattern in strong_patterns:
            for match in re.finditer(pattern, text):
                token = InlineToken(
                    type="strong",
                    content=match.group(1),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    raw_content=match.group(0),
                )
                tokens.append(token)

        # Emphasis *text* and _text_
        emphasis_patterns = [r"\*([^*]+)\*", r"_([^_]+)_"]
        for pattern in emphasis_patterns:
            for match in re.finditer(pattern, text):
                # Skip if already covered by strong emphasis
                if not self._overlaps_with_existing(match.start(), match.end(), tokens):
                    token = InlineToken(
                        type="emphasis",
                        content=match.group(1),
                        start_pos=match.start(),
                        end_pos=match.end(),
                        raw_content=match.group(0),
                    )
                    tokens.append(token)

        return tokens

    def _overlaps_with_existing(
        self, start: int, end: int, tokens: List[InlineToken]
    ) -> bool:
        """Check if position range overlaps with existing tokens."""
        for token in tokens:
            if not (end <= token.start_pos or start >= token.end_pos):
                return True
        return False

    def _sort_and_merge_tokens(self, tokens: List[InlineToken]) -> List[InlineToken]:
        """Sort tokens by position and handle overlaps."""
        # Sort by start position
        tokens.sort(key=lambda t: t.start_pos)

        # Remove overlapping tokens (keep first one)
        merged: List[InlineToken] = []
        for token in tokens:
            if not merged or token.start_pos >= merged[-1].end_pos:
                merged.append(token)
            else:
                # Log overlap for debugging
                self.logger.debug(f"Skipping overlapping token: {token.raw_content}")

        return merged


class MarkdownNodeFactory:
    """Factory for creating MarkdownNode instances."""

    def __init__(self, line_tracker: LineTracker):
        self.line_tracker = line_tracker

    def create_node(
        self,
        node_type: NodeType,
        content: str,
        start_offset: int,
        end_offset: int,
        children: Optional[List[MarkdownNode]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MarkdownNode:
        """Create a MarkdownNode with proper positioning."""

        start_pos = self.line_tracker.get_position_from_offset(start_offset)
        end_pos = self.line_tracker.get_position_from_offset(end_offset)

        return MarkdownNode(
            type=node_type,
            content=content,
            start_pos=start_pos,
            end_pos=end_pos,
            children=children or [],
            metadata=metadata or {},
        )

    def create_inline_node(
        self, token: InlineToken, parent_offset: int
    ) -> MarkdownNode:
        """Create a MarkdownNode from an inline token."""

        # Map token types to NodeType
        type_mapping = {
            "inline_code": NodeType.TEXT,  # Special handling for inline code
            "link": NodeType.LINK,
            "emphasis": NodeType.EMPHASIS,
            "strong": NodeType.STRONG,
            "text": NodeType.TEXT,
        }

        node_type = type_mapping.get(token.type, NodeType.TEXT)

        # Calculate absolute positions
        start_offset = parent_offset + token.start_pos
        end_offset = parent_offset + token.end_pos

        metadata = token.attributes.copy()
        if token.type == "inline_code":
            metadata["inline_code"] = "true"

        return self.create_node(
            node_type=node_type,
            content=token.content,
            start_offset=start_offset,
            end_offset=end_offset,
            metadata=metadata,
        )


class EnhancedASTBuilder:
    """Enhanced AST builder with inline token support."""

    def __init__(self):
        self.inline_processor = InlineTokenProcessor()
        self.logger = logging.getLogger(__name__)

    def build_ast(self, md_text: str) -> MarkdownNode:
        """Build complete AST with inline and child tokens."""

        # Normalize input
        normalized_text = self._normalize_input(md_text)

        # Create line tracker
        line_tracker = LineTracker(normalized_text)
        node_factory = MarkdownNodeFactory(line_tracker)

        # Parse structure using existing parser
        from .markdown_ast import parse_to_ast

        base_ast = parse_to_ast(normalized_text)

        # Enhance with inline elements
        enhanced_ast = self._enhance_with_inline_elements(
            base_ast, normalized_text, line_tracker, node_factory
        )

        # Validate structure
        self._validate_ast_structure(enhanced_ast)

        return enhanced_ast

    def _normalize_input(self, md_text: str) -> str:
        """Normalize input text."""
        if not isinstance(md_text, str):
            raise TypeError("Input must be a string")

        # Normalize line endings
        normalized = md_text.replace("\r\n", "\n").replace("\r", "\n")

        return normalized

    def _enhance_with_inline_elements(
        self,
        ast: MarkdownNode,
        source_text: str,
        line_tracker: LineTracker,
        node_factory: MarkdownNodeFactory,
    ) -> MarkdownNode:
        """Enhance AST nodes with inline elements."""

        # Process current node if it can contain inline elements
        if ast.type in [NodeType.PARAGRAPH, NodeType.HEADER]:
            ast.children = self._process_inline_elements(
                ast, source_text, line_tracker, node_factory
            )

        # Recursively process children
        for child in ast.children:
            self._enhance_with_inline_elements(
                child, source_text, line_tracker, node_factory
            )

        return ast

    def _process_inline_elements(
        self,
        node: MarkdownNode,
        source_text: str,
        line_tracker: LineTracker,
        node_factory: MarkdownNodeFactory,
    ) -> List[MarkdownNode]:
        """Process inline elements in a node's content."""

        if not node.content:
            return []

        # Extract inline tokens
        inline_tokens = self.inline_processor.extract_inline_tokens(node.content)

        if not inline_tokens:
            # No inline elements, return text node
            return [
                node_factory.create_node(
                    NodeType.TEXT,
                    node.content,
                    node.start_pos.offset,
                    node.end_pos.offset,
                )
            ]

        # Create nodes for text and inline elements
        children = []
        last_pos = 0

        for token in inline_tokens:
            # Add text before token if any
            if token.start_pos > last_pos:
                text_content = node.content[last_pos : token.start_pos]
                if text_content.strip():  # Only add non-empty text
                    text_node = node_factory.create_node(
                        NodeType.TEXT,
                        text_content,
                        node.start_pos.offset + last_pos,
                        node.start_pos.offset + token.start_pos,
                    )
                    children.append(text_node)

            # Add inline element node
            inline_node = node_factory.create_inline_node(token, node.start_pos.offset)
            children.append(inline_node)

            last_pos = token.end_pos

        # Add remaining text after last token
        if last_pos < len(node.content):
            text_content = node.content[last_pos:]
            if text_content.strip():
                text_node = node_factory.create_node(
                    NodeType.TEXT,
                    text_content,
                    node.start_pos.offset + last_pos,
                    node.end_pos.offset,
                )
                children.append(text_node)

        return children

    def _validate_ast_structure(self, ast: MarkdownNode) -> None:
        """Validate AST structure and relationships using comprehensive validator."""
        from .ast_validator import ASTValidator

        validator = ASTValidator()
        validation_result = validator.validate_ast(ast)

        # Log validation results
        if validation_result.has_errors():
            error_messages = [issue.message for issue in validation_result.get_errors()]
            self.logger.error(
                f"AST validation failed with {len(error_messages)} errors:"
            )
            for error in error_messages:
                self.logger.error(f"  - {error}")
            raise ValueError(f"AST validation failed: {'; '.join(error_messages)}")

        if validation_result.has_warnings():
            warning_messages = [
                issue.message for issue in validation_result.get_warnings()
            ]
            self.logger.warning(
                f"AST validation completed with {len(warning_messages)} warnings:"
            )
            for warning in warning_messages:
                self.logger.warning(f"  - {warning}")

        # Log validation statistics
        self.logger.info(
            f"AST validation successful: {validation_result.node_count} nodes, "
            f"max depth: {validation_result.max_depth}, "
            f"issues: {len(validation_result.issues)}"
        )

        # Additional validation for tree correctness and node relationships
        self._validate_tree_correctness(ast)
        self._validate_node_relationships(ast)

    def _validate_tree_correctness(self, ast: MarkdownNode) -> None:
        """Validate correctness of tree structure and node connections."""

        # Check for circular references
        visited_nodes: set[int] = set()
        self._check_circular_references(ast, visited_nodes)

        # Validate parent-child relationships
        self._validate_parent_child_relationships(ast, None)

        # Check for orphaned nodes
        self._check_orphaned_nodes(ast)

        self.logger.debug("Tree correctness validation completed")

    def _check_circular_references(self, node: MarkdownNode, visited: set[int]) -> None:
        """Check for circular references in the tree."""
        visited_nodes = visited
        node_id = id(node)

        if node_id in visited_nodes:
            raise ValueError(f"Circular reference detected in AST at node {node.type}")

        visited_nodes.add(node_id)

        for child in node.children:
            self._check_circular_references(child, visited.copy())

    def _validate_parent_child_relationships(
        self, node: MarkdownNode, parent: Optional[MarkdownNode]
    ) -> None:
        """Validate parent-child relationships are consistent."""

        # Check that node has correct parent reference if it exists
        if hasattr(node, "parent") and node.parent != parent:
            self.logger.warning(f"Node {node.type} has incorrect parent reference")

        # Validate each child
        for child in node.children:
            if not isinstance(child, MarkdownNode):
                raise ValueError(
                    f"Child of {node.type} is not a MarkdownNode: {type(child)}"
                )

            # Recursively validate children
            self._validate_parent_child_relationships(child, node)

    def _check_orphaned_nodes(self, ast: MarkdownNode) -> None:
        """Check for orphaned nodes that should have parents."""

        def collect_all_nodes(node: MarkdownNode, all_nodes: set[int], parent_map: dict[int, int]) -> None:
            all_nodes.add(id(node))
            for child in node.children:
                parent_map[id(child)] = id(node)
                collect_all_nodes(child, all_nodes, parent_map)

        all_nodes: set[int] = set()
        parent_map: dict[int, int] = {}
        collect_all_nodes(ast, all_nodes, parent_map)

        # Root should not have parent
        root_id = id(ast)
        if root_id in parent_map:
            self.logger.warning("Root node appears to have a parent")

        # All other nodes should have parents
        for node_id in all_nodes:
            if node_id != root_id and node_id not in parent_map:
                self.logger.warning("Found orphaned node without parent")

    def _validate_node_relationships(self, ast: MarkdownNode) -> None:
        """Validate relationships between nodes for consistency."""

        # Check position consistency between parent and children
        self._validate_position_consistency(ast)

        # Check content consistency
        self._validate_content_consistency(ast)

        # Check metadata consistency
        self._validate_metadata_consistency(ast)

        self.logger.debug("Node relationships validation completed")

    def _validate_position_consistency(self, node: MarkdownNode) -> None:
        """Validate that positions are consistent across the tree."""

        for child in node.children:
            # Child should be within parent bounds
            if (
                child.start_pos.offset < node.start_pos.offset
                or child.end_pos.offset > node.end_pos.offset
            ):
                self.logger.warning(
                    f"Child {child.type} position outside parent {node.type} bounds: "
                    f"child({child.start_pos.offset}-{child.end_pos.offset}) "
                    f"parent({node.start_pos.offset}-{node.end_pos.offset})"
                )

            # Check for gaps between siblings
            for i, sibling in enumerate(node.children[1:], 1):
                prev_child = node.children[i - 1]
                if sibling.start_pos.offset < prev_child.end_pos.offset:
                    self.logger.warning(
                        f"Overlapping siblings in {node.type}: "
                        f"{prev_child.type}({prev_child.start_pos.offset}-"
                        f"{prev_child.end_pos.offset}) and "
                        f"{sibling.type}({sibling.start_pos.offset}-"
                        f"{sibling.end_pos.offset})"
                    )

            # Recursively validate children
            self._validate_position_consistency(child)

    def _validate_content_consistency(self, node: MarkdownNode) -> None:
        """Validate that content is consistent with node type and children."""

        # For nodes with children, content should be derivable from children
        if node.children and node.type in [NodeType.PARAGRAPH, NodeType.HEADER]:
            # Content should match combined children content
            children_content = "".join(child.content for child in node.children)
            if (
                node.content
                and children_content
                and node.content.replace(" ", "") != children_content.replace(" ", "")
            ):
                self.logger.warning(
                    f"Content mismatch between {node.type} and its children: "
                    f"node='{node.content[:50]}...' "
                    f"children='{children_content[:50]}...'"
                )

        # Recursively validate children
        for child in node.children:
            self._validate_content_consistency(child)

    def _validate_metadata_consistency(self, node: MarkdownNode) -> None:
        """Validate that metadata is consistent and complete."""

        # Check required metadata for specific node types
        if node.type == NodeType.HEADER:
            if "level" not in node.metadata:
                self.logger.warning("Header node missing required 'level' metadata")
            elif not isinstance(node.metadata["level"], int) or not (
                1 <= node.metadata["level"] <= 6
            ):
                self.logger.warning(
                    f"Header node has invalid level: {node.metadata.get('level')}"
                )

        elif node.type == NodeType.CODE_BLOCK:
            # Code blocks should have language info
            if "language" in node.metadata and not isinstance(
                node.metadata["language"], str
            ):
                self.logger.warning(
                    "Code block has invalid language metadata: "
                    f"{node.metadata.get('language')}"
                )

        elif node.type == NodeType.LINK:
            if "hre" not in node.metadata and "re" not in node.metadata:
                self.logger.warning("Link node missing href or ref metadata")

        # Recursively validate children
        for child in node.children:
            self._validate_metadata_consistency(child)
