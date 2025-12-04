"""
Unified Markdown parser with adapters for different libraries.

This module provides a unified interface for parsing Markdown documents
using different Python libraries, with automatic selection of the best
available parser based on benchmarking results.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .types import MarkdownNode, NodeType, Position


class MarkdownParser(ABC):
    """Abstract base class for Markdown parsers."""

    @abstractmethod
    def parse(self, text: str) -> MarkdownNode:
        """Parse Markdown text into an AST."""

    @abstractmethod
    def supports_positions(self) -> bool:
        """Check if the parser supports position information."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the name of the parser."""


class MarkdownItPyAdapter(MarkdownParser):
    """Adapter for markdown-it-py library."""

    def __init__(self):
        self._parser = None
        self._init_parser()

    def _init_parser(self):
        """Initialize the markdown-it-py parser."""
        try:
            from markdown_it import MarkdownIt

            self._parser = MarkdownIt("commonmark", {"breaks": True, "html": True})
        except ImportError as e:
            raise ImportError(f"markdown-it-py not available: {e}")

    def parse(self, text: str) -> MarkdownNode:
        """Parse text using markdown-it-py."""
        if not self._parser:
            raise RuntimeError("Parser not initialized")

        # Parse to tokens
        tokens = self._parser.parse(text)

        # Convert to our AST format
        return self._convert_tokens_to_ast(tokens, text)

    def _convert_tokens_to_ast(self, tokens, text: str) -> MarkdownNode:
        """Convert markdown-it-py tokens to our AST format."""
        lines = text.split("\n")

        # Create root document node
        root = MarkdownNode(
            type=NodeType.DOCUMENT,
            content="",
            start_pos=Position(line=0, column=0, offset=0),
            end_pos=Position(
                line=len(lines) - 1,
                column=len(lines[-1]) if lines else 0,
                offset=len(text),
            ),
            children=[],
            metadata={},
        )

        # Process tokens
        stack = [root]

        for token in tokens:
            # CRITICAL FIX: Handle closing tokens FIRST
            if token.nesting == -1:  # Closing tag
                if len(stack) > 1:
                    # Aggregate content from children before popping
                    current_node = stack[-1]
                    self._aggregate_child_content(current_node)
                    stack.pop()
                continue

            # Process opening and self-closing tokens
            node = self._token_to_node(token, text, lines)
            if node:
                stack[-1].children.append(node)
                if token.nesting == 1:  # Opening token
                    stack.append(node)
            else:
                # Handle inline content tokens
                self._process_inline_token(token, stack[-1])

        # Final content aggregation for remaining nodes
        for node in stack:
            self._aggregate_child_content(node)

        return root

    def _token_to_node(
        self, token, text: str, lines: List[str]
    ) -> Optional[MarkdownNode]:
        """Convert a single token to a MarkdownNode."""
        # Map token types to our NodeType enum
        type_mapping = {
            "heading_open": NodeType.HEADER,
            "paragraph_open": NodeType.PARAGRAPH,
            "code_block": NodeType.CODE_BLOCK,
            "fence": NodeType.CODE_BLOCK,
            "list_item_open": NodeType.LIST_ITEM,
            "bullet_list_open": NodeType.LIST,
            "ordered_list_open": NodeType.LIST,
            "blockquote_open": NodeType.BLOCKQUOTE,
            "table_open": NodeType.TABLE,
            "tr_open": NodeType.TABLE_ROW,
            "td_open": NodeType.TABLE_CELL,
            "th_open": NodeType.TABLE_CELL,
            "text": NodeType.TEXT,
            "code_inline": NodeType.TEXT,
            "em_open": NodeType.EMPHASIS,
            "strong_open": NodeType.STRONG,
            "link_open": NodeType.LINK,
            "image": NodeType.IMAGE,
            "hr": NodeType.HORIZONTAL_RULE,
            "softbreak": NodeType.LINE_BREAK,
            "hardbreak": NodeType.LINE_BREAK,
        }

        node_type = type_mapping.get(token.type)
        if not node_type:
            return None

        # Calculate positions
        start_pos, end_pos = self._calculate_positions(token, text, lines)

        # Extract content
        content = getattr(token, "content", "") or ""
        if hasattr(token, "children") and token.children:
            # For tokens with children, concatenate their content
            content = "".join(
                child.content or ""
                for child in token.children
                if hasattr(child, "content")
            )

        # Create metadata
        metadata = {}
        if hasattr(token, "info") and token.info:
            metadata["info"] = token.info
        if hasattr(token, "tag") and token.tag:
            metadata["tag"] = token.tag
        if hasattr(token, "level") and token.level:
            metadata["level"] = token.level
        if hasattr(token, "markup") and token.markup:
            metadata["markup"] = token.markup

        return MarkdownNode(
            type=node_type,
            content=content,
            start_pos=start_pos,
            end_pos=end_pos,
            children=[],
            metadata=metadata,
        )

    def _calculate_positions(
        self, token, text: str, lines: List[str]
    ) -> tuple[Position, Position]:
        """Calculate start and end positions for a token."""
        # markdown-it-py provides line numbers in map attribute
        if hasattr(token, "map") and token.map:
            start_line = token.map[0]
            end_line = token.map[1] - 1  # markdown-it-py uses exclusive end

            # Calculate offsets
            start_offset = sum(len(line) + 1 for line in lines[:start_line])
            end_offset = sum(len(line) + 1 for line in lines[: end_line + 1]) - 1

            start_pos = Position(line=start_line, column=0, offset=start_offset)
            end_pos = Position(
                line=end_line,
                column=len(lines[end_line]) if end_line < len(lines) else 0,
                offset=end_offset,
            )
        else:
            # Fallback to document bounds
            start_pos = Position(line=0, column=0, offset=0)
            end_pos = Position(
                line=len(lines) - 1,
                column=len(lines[-1]) if lines else 0,
                offset=len(text),
            )

        return start_pos, end_pos

    def _process_inline_token(self, token, parent_node: MarkdownNode):
        """Process inline tokens and add content to parent."""
        if token.type in ["text", "code_inline"]:
            content = getattr(token, "content", "") or ""
            if content:
                # Append to parent's content
                if parent_node.content:
                    parent_node.content += content
                else:
                    parent_node.content = content

        # Process children tokens with link context tracking
        if hasattr(token, "children") and token.children:
            self._process_inline_children(token.children, parent_node)

    def _process_inline_children(  # noqa: C901
        self, children, parent_node: MarkdownNode
    ) -> None:
        """Process inline token children with link/emphasis context tracking.

        This method handles link_open, link_close, image, and text tokens,
        creating proper LINK and IMAGE nodes in the AST.
        """
        current_link: Optional[MarkdownNode] = None

        for child in children:
            if child.type == "link_open":
                # Extract href from token attributes
                href = ""
                if hasattr(child, "attrGet"):
                    href = child.attrGet("href") or ""
                elif hasattr(child, "attrs") and child.attrs:
                    # Fallback: attrs might be a list of tuples
                    for attr in child.attrs:
                        if attr[0] == "href":
                            href = attr[1]
                            break

                # Create LINK node
                current_link = MarkdownNode(
                    type=NodeType.LINK,
                    content="",
                    start_pos=Position(line=0, column=0, offset=0),
                    end_pos=Position(line=0, column=0, offset=0),
                    children=[],
                    metadata={"href": href},
                )
                parent_node.children.append(current_link)

            elif child.type == "link_close":
                # Close current link context
                current_link = None

            elif child.type == "text":
                # Add text to current link or parent
                content = getattr(child, "content", "") or ""
                if content:
                    target = current_link if current_link else parent_node
                    if target.content:
                        target.content += content
                    else:
                        target.content = content

            elif child.type == "code_inline":
                # Add inline code to current link or parent
                content = getattr(child, "content", "") or ""
                if content:
                    target = current_link if current_link else parent_node
                    # Wrap in backticks for inline code
                    code_content = f"`{content}`"
                    if target.content:
                        target.content += code_content
                    else:
                        target.content = code_content

            elif child.type == "image":
                # Extract image attributes
                src = ""
                alt = getattr(child, "content", "") or ""
                if hasattr(child, "attrGet"):
                    src = child.attrGet("src") or ""
                elif hasattr(child, "attrs") and child.attrs:
                    for attr in child.attrs:
                        if attr[0] == "src":
                            src = attr[1]
                            break

                # Create IMAGE node
                image_node = MarkdownNode(
                    type=NodeType.IMAGE,
                    content=alt,
                    start_pos=Position(line=0, column=0, offset=0),
                    end_pos=Position(line=0, column=0, offset=0),
                    children=[],
                    metadata={"src": src, "alt": alt},
                )

                # Add to current link (for badges) or parent
                target = current_link if current_link else parent_node
                target.children.append(image_node)

            elif child.type == "softbreak":
                # Add newline
                target = current_link if current_link else parent_node
                if target.content:
                    target.content += "\n"
                else:
                    target.content = "\n"

            elif child.type == "hardbreak":
                # Add line break
                target = current_link if current_link else parent_node
                if target.content:
                    target.content += "\n"
                else:
                    target.content = "\n"

    def _aggregate_child_content(self, node: MarkdownNode):
        """Aggregate content from child nodes for headers/paragraphs."""
        if node.type in [NodeType.HEADER, NodeType.PARAGRAPH]:
            if not node.content and node.children:
                # Collect content from text children
                content_parts = []
                for child in node.children:
                    if child.type == NodeType.TEXT and child.content:
                        content_parts.append(child.content)

                if content_parts:
                    node.content = "".join(content_parts)

    def supports_positions(self) -> bool:
        """markdown-it-py supports position information."""
        return True

    def get_name(self) -> str:
        """Get parser name."""
        return "markdown-it-py"


class MistuneAdapter(MarkdownParser):
    """Adapter for mistune library."""

    def __init__(self):
        self._parser = None
        self._init_parser()

    def _init_parser(self):
        """Initialize the mistune parser."""
        try:
            from mistune import create

            self._parser = create(renderer=None)  # Use AST renderer
        except ImportError as e:
            raise ImportError(f"mistune not available: {e}")

    def parse(self, text: str) -> MarkdownNode:
        """Parse text using mistune."""
        if not self._parser:
            raise RuntimeError("Parser not initialized")

        # Parse to AST
        ast = self._parser(text)

        # Convert to our format
        return self._convert_mistune_ast(ast, text)

    def _convert_mistune_ast(self, ast, text: str) -> MarkdownNode:
        """Convert mistune AST to our format."""
        lines = text.split("\n")

        if isinstance(ast, list):
            # Root level is a list of nodes
            root = MarkdownNode(
                type=NodeType.DOCUMENT,
                content="",
                start_pos=Position(line=0, column=0, offset=0),
                end_pos=Position(
                    line=len(lines) - 1,
                    column=len(lines[-1]) if lines else 0,
                    offset=len(text),
                ),
                children=[],
                metadata={},
            )

            for item in ast:
                child = self._convert_mistune_node(item, text, lines)
                if child:
                    root.children.append(child)

            return root
        else:
            return self._convert_mistune_node(ast, text, lines)

    def _convert_mistune_node(
        self, node, text: str, lines: List[str]
    ) -> Optional[MarkdownNode]:
        """Convert a single mistune node."""
        if not isinstance(node, dict):
            return None

        node_type_str = node.get("type", "")

        # Map mistune types to our NodeType enum
        type_mapping = {
            "heading": NodeType.HEADER,
            "paragraph": NodeType.PARAGRAPH,
            "code_block": NodeType.CODE_BLOCK,
            "fenced_code": NodeType.CODE_BLOCK,
            "list": NodeType.LIST,
            "list_item": NodeType.LIST_ITEM,
            "blockquote": NodeType.BLOCKQUOTE,
            "table": NodeType.TABLE,
            "table_row": NodeType.TABLE_ROW,
            "table_cell": NodeType.TABLE_CELL,
            "text": NodeType.TEXT,
            "emphasis": NodeType.EMPHASIS,
            "strong": NodeType.STRONG,
            "link": NodeType.LINK,
            "image": NodeType.IMAGE,
            "thematic_break": NodeType.HORIZONTAL_RULE,
            "linebreak": NodeType.LINE_BREAK,
        }

        node_type = type_mapping.get(node_type_str, NodeType.TEXT)

        # Extract content
        content = node.get("raw", "") or node.get("text", "") or ""

        # Calculate positions (mistune doesn't provide detailed position info)
        start_pos = Position(line=0, column=0, offset=0)
        end_pos = Position(line=0, column=len(content), offset=len(content))

        # Create metadata
        metadata = {}
        if "level" in node:
            metadata["level"] = node["level"]
        if "info" in node:
            metadata["info"] = node["info"]
        if "lang" in node:
            metadata["language"] = node["lang"]

        # Create node
        result = MarkdownNode(
            type=node_type,
            content=content,
            start_pos=start_pos,
            end_pos=end_pos,
            children=[],
            metadata=metadata,
        )

        # Process children
        if "children" in node and isinstance(node["children"], list):
            for child in node["children"]:
                child_node = self._convert_mistune_node(child, text, lines)
                if child_node:
                    result.children.append(child_node)

        return result

    def supports_positions(self) -> bool:
        """mistune has limited position support."""
        return False

    def get_name(self) -> str:
        """Get parser name."""
        return "mistune"


class CommonMarkAdapter(MarkdownParser):
    """Adapter for commonmark library."""

    def __init__(self):
        self._parser = None
        self._init_parser()

    def _init_parser(self):
        """Initialize the commonmark parser."""
        try:
            import commonmark

            self._parser = commonmark.Parser()
        except ImportError as e:
            raise ImportError(f"commonmark not available: {e}")

    def parse(self, text: str) -> MarkdownNode:
        """Parse text using commonmark."""
        if not self._parser:
            raise RuntimeError("Parser not initialized")

        # Parse to AST
        ast = self._parser.parse(text)

        # Convert to our format
        return self._convert_commonmark_ast(ast, text)

    def _convert_commonmark_ast(self, ast, text: str) -> MarkdownNode:
        """Convert commonmark AST to our format."""
        lines = text.split("\n")
        return self._convert_commonmark_node(ast, text, lines)

    def _convert_commonmark_node(
        self, node, text: str, lines: List[str]
    ) -> MarkdownNode:
        """Convert a single commonmark node."""
        # Map commonmark types to our NodeType enum
        type_mapping = {
            "document": NodeType.DOCUMENT,
            "heading": NodeType.HEADER,
            "paragraph": NodeType.PARAGRAPH,
            "code_block": NodeType.CODE_BLOCK,
            "list": NodeType.LIST,
            "item": NodeType.LIST_ITEM,
            "block_quote": NodeType.BLOCKQUOTE,
            "text": NodeType.TEXT,
            "emph": NodeType.EMPHASIS,
            "strong": NodeType.STRONG,
            "link": NodeType.LINK,
            "image": NodeType.IMAGE,
            "thematic_break": NodeType.HORIZONTAL_RULE,
            "linebreak": NodeType.LINE_BREAK,
            "softbreak": NodeType.LINE_BREAK,
        }

        node_type = type_mapping.get(node.t, NodeType.TEXT)

        # Extract content
        content = getattr(node, "literal", "") or ""

        # Calculate positions (commonmark doesn't provide detailed position info)
        start_pos = Position(line=0, column=0, offset=0)
        end_pos = Position(line=0, column=len(content), offset=len(content))

        # Create metadata
        metadata = {}
        if hasattr(node, "level"):
            metadata["level"] = node.level
        if hasattr(node, "info"):
            metadata["info"] = node.info

        # Create node
        result = MarkdownNode(
            type=node_type,
            content=content,
            start_pos=start_pos,
            end_pos=end_pos,
            children=[],
            metadata=metadata,
        )

        # Process children
        child = node.first_child
        while child:
            child_node = self._convert_commonmark_node(child, text, lines)
            result.children.append(child_node)
            child = child.nxt

        return result

    def supports_positions(self) -> bool:
        """commonmark has no position support."""
        return False

    def get_name(self) -> str:
        """Get parser name."""
        return "commonmark"


# Parser registry and selection
_parser_registry: Dict[str, MarkdownParser] = {}
_default_parser: Optional[str] = None


def register_parser(name: str, parser: MarkdownParser) -> None:
    """Register a parser instance."""
    _parser_registry[name] = parser


def get_available_parsers() -> List[str]:
    """Get list of available parser names."""
    return list(_parser_registry.keys())


def _auto_select_parser() -> MarkdownParser:
    """Automatically select the best available parser."""
    global _default_parser

    if _default_parser and _default_parser in _parser_registry:
        return _parser_registry[_default_parser]

    # Priority order based on capabilities
    priority_order = ["markdown-it-py", "mistune", "commonmark"]

    for parser_name in priority_order:
        try:
            parser: MarkdownParser
            if parser_name == "markdown-it-py":
                parser = MarkdownItPyAdapter()
            elif parser_name == "mistune":
                parser = MistuneAdapter()
            elif parser_name == "commonmark":
                parser = CommonMarkAdapter()
            else:
                continue

            register_parser(parser_name, parser)
            _default_parser = parser_name
            return parser

        except ImportError:
            continue

    raise RuntimeError(
        "No Markdown parser libraries available. "
        "Please install markdown-it-py, mistune, or commonmark."
    )


def _get_parser(parser_type: str) -> MarkdownParser:
    """Get a parser instance by type."""
    if parser_type == "auto":
        return _auto_select_parser()
    elif parser_type in _parser_registry:
        return _parser_registry[parser_type]
    else:
        # Try to create the parser
        try:
            parser: MarkdownParser
            if parser_type == "markdown-it-py":
                parser = MarkdownItPyAdapter()
            elif parser_type == "mistune":
                parser = MistuneAdapter()
            elif parser_type == "commonmark":
                parser = CommonMarkAdapter()
            else:
                raise ValueError(f"Unknown parser type: {parser_type}")

            register_parser(parser_type, parser)
            return parser

        except ImportError as e:
            raise ValueError(f"Parser {parser_type} not available: {e}")


def parse_to_ast(md_text: str, parser_type: str = "auto") -> MarkdownNode:
    """
    Parse Markdown text to AST using the specified parser.

    Args:
        md_text: The Markdown text to parse
        parser_type: Parser to use ("auto", "markdown-it-py", "mistune", "commonmark")

    Returns:
        MarkdownNode representing the root of the AST

    Raises:
        ValueError: If parser_type is unknown or not available
        RuntimeError: If no parsers are available
    """
    if not md_text.strip():
        # Return empty document for empty input
        return MarkdownNode(
            type=NodeType.DOCUMENT,
            content="",
            start_pos=Position(line=0, column=0, offset=0),
            end_pos=Position(line=0, column=0, offset=0),
            children=[],
            metadata={},
        )

    parser = _get_parser(parser_type)
    return parser.parse(md_text)


def set_default_parser(parser_name: str) -> None:
    """Set the default parser for auto selection."""
    global _default_parser
    if parser_name in get_available_parsers() or parser_name in [
        "markdown-it-py",
        "mistune",
        "commonmark",
    ]:
        _default_parser = parser_name
    else:
        raise ValueError(f"Unknown parser: {parser_name}")


def get_parser_info(parser_name: str) -> Dict[str, Any]:
    """Get information about a parser."""
    try:
        parser = _get_parser(parser_name)
        return {
            "name": parser.get_name(),
            "supports_positions": parser.supports_positions(),
            "available": True,
        }
    except (ValueError, ImportError):
        return {"name": parser_name, "supports_positions": False, "available": False}
