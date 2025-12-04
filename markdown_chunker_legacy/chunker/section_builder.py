"""
Section builder for Phase 2 semantic quality improvements.

This module builds logical sections from AST, grouping content under
appropriate headers while respecting section boundaries.
"""

from typing import List

try:
    from markdown_chunker.parser.types import MarkdownNode, NodeType, Stage1Results
except ImportError:
    # Fallback for testing environment
    try:
        from ..parser.types import (  # type: ignore[no-redef]
            MarkdownNode,
            NodeType,
            Stage1Results,
        )
    except ImportError:
        # Create dummy classes for testing
        class MarkdownNode:  # type: ignore[no-redef]
            def __init__(self):
                self.type = None
                self.metadata = {}
                self.children = []
                self.start_pos = type("Position", (), {"offset": 0, "line": 0})()
                self.end_pos = type("Position", (), {"offset": 0, "line": 0})()

            def get_text_content(self):
                return ""

        class NodeType:  # type: ignore[no-redef]
            HEADER = "header"
            PARAGRAPH = "paragraph"
            LIST = "list"
            LIST_ITEM = "list_item"
            CODE_BLOCK = "code_block"
            TABLE = "table"
            BLOCKQUOTE = "blockquote"
            TEXT = "text"
            LINK = "link"
            EMPHASIS = "emphasis"
            STRONG = "strong"

        class Stage1Results:  # type: ignore[no-redef]
            def __init__(self):
                self.ast = None


from .logical_blocks import LogicalBlock, Section


class SectionBuilder:
    """
    Builds logical sections from Markdown AST.

    A section consists of a header and all content blocks that follow it
    until the next header of the same or higher level. Sections can be
    nested (H3 under H2, etc.) and are used for section-aware chunking.

    Examples:
        >>> builder = SectionBuilder()
        >>> sections = builder.build_sections(
        ...     stage1_results.ast, boundary_level=2
        ... )
        >>> for section in sections:
        ...     blocks_count = len(section.content_blocks)
        ...     print(f"Section: {section.header_text} ({blocks_count} blocks)")
    """

    def __init__(self):
        """Initialize section builder."""
        self.block_id_counter = 0

    def _get_header_level(self, node: MarkdownNode) -> int:
        """
        Extract header level from node metadata.

        Handles different metadata formats:
        - level: direct level number (1-6)
        - tag: 'h1', 'h2', etc.
        - markup: '#', '##', etc.

        Args:
            node: Header AST node

        Returns:
            Header level (1-6), defaults to 1 if not found
        """
        metadata = node.metadata

        # Try direct level first
        if "level" in metadata:
            return metadata["level"]

        # Try tag (h1, h2, etc.)
        if "tag" in metadata:
            tag = metadata["tag"]
            if isinstance(tag, str) and tag.startswith("h") and len(tag) == 2:
                try:
                    return int(tag[1])
                except ValueError:
                    pass

        # Try markup (#, ##, etc.)
        if "markup" in metadata:
            markup = metadata["markup"]
            if isinstance(markup, str) and markup.startswith("#"):
                return len(markup)

        # Default to level 1
        return 1

    def build_sections(
        self, ast: MarkdownNode, boundary_level: int = 2
    ) -> List[Section]:
        """
        Build sections from AST respecting boundary level.

        Args:
            ast: Parsed Markdown AST (root node)
            boundary_level: Header level that defines section boundaries (1-6).
                           Headers at or below this level start new sections.
                           Default: 2 (H1 and H2 are section boundaries)

        Returns:
            List of Section objects with hierarchical structure

        Examples:
            >>> builder = SectionBuilder()
            >>> # Split at H2 level (default)
            >>> sections = builder.build_sections(ast, boundary_level=2)
            >>>
            >>> # Split at H1 level only
            >>> sections = builder.build_sections(ast, boundary_level=1)
        """
        sections = []
        current_section = None
        header_stack: List[str] = []  # Track header hierarchy
        has_seen_header = False

        # Walk through AST nodes
        for node in self._walk_ast(ast):
            if node.type == NodeType.HEADER:
                has_seen_header = True
                level = self._get_header_level(node)
                text = node.get_text_content().strip()

                # Check if this is a boundary header
                if level <= boundary_level:
                    # Save current section
                    if current_section:
                        sections.append(current_section)

                    # Start new section
                    current_section = self._create_section(
                        node, header_stack, level, text
                    )

                    # Update header stack
                    header_stack = header_stack[: level - 1] + [text]
                else:
                    # Sub-header within section
                    # If no current section exists (first header is deeper
                    # than boundary), create a root section to avoid losing content
                    if current_section is None:
                        current_section = self._create_root_section()

                    block = self._create_header_block(node)
                    current_section.content_blocks.append(block)

            elif node.type in [
                NodeType.PARAGRAPH,
                NodeType.LIST,
                NodeType.CODE_BLOCK,
                NodeType.TABLE,
            ]:
                # Handle content before first header (root section)
                if not has_seen_header and current_section is None:
                    # Create root section for content before first header
                    current_section = self._create_root_section()

                if current_section:
                    block = self._create_content_block(node)
                    current_section.content_blocks.append(block)

        # Add final section
        if current_section:
            sections.append(current_section)

        return sections

    def _walk_ast(self, node: MarkdownNode) -> List[MarkdownNode]:
        """
        Walk AST in document order, yielding block-level nodes.

        Args:
            node: Root AST node

        Yields:
            Block-level nodes (headers, paragraphs, lists, code, tables)
        """
        nodes = []

        def walk(n: MarkdownNode):
            # Yield block-level nodes
            if n.type in [
                NodeType.HEADER,
                NodeType.PARAGRAPH,
                NodeType.LIST,
                NodeType.CODE_BLOCK,
                NodeType.TABLE,
                NodeType.BLOCKQUOTE,
            ]:
                nodes.append(n)

            # Recurse into children
            for child in n.children:
                walk(child)

        walk(node)
        return nodes

    def _create_section(
        self, header_node: MarkdownNode, header_stack: List[str], level: int, text: str
    ) -> Section:
        """
        Create a new section from header node.

        Args:
            header_node: AST node for the header
            header_stack: Current header hierarchy
            level: Header level (1-6)
            text: Header text content

        Returns:
            New Section object
        """
        header_block = self._create_header_block(header_node)

        # Build header path from stack
        header_path = header_stack[: level - 1] + [text]

        return Section(
            block_type="section",
            content="",  # Will be calculated from blocks
            ast_node=None,
            start_offset=header_node.start_pos.offset,
            end_offset=header_node.end_pos.offset,
            start_line=header_node.start_pos.line + 1,  # Convert to 1-based
            end_line=header_node.end_pos.line + 1,
            is_atomic=False,
            metadata={"id": f"section_{self.block_id_counter}"},
            header=header_block,
            header_level=level,
            header_text=text,
            header_path=header_path,
            content_blocks=[],
        )

    def _create_root_section(self) -> Section:
        """
        Create a root section for content before first header.

        Returns:
            Section with no header (root section)
        """
        self.block_id_counter += 1
        return Section(
            block_type="section",
            content="",
            ast_node=None,
            start_offset=0,
            end_offset=0,
            start_line=1,
            end_line=1,
            is_atomic=False,
            metadata={"id": f"section_{self.block_id_counter}"},
            header=None,
            header_level=0,
            header_text="",
            header_path=[],
            content_blocks=[],
        )

    def _create_header_block(self, node: MarkdownNode) -> LogicalBlock:
        """
        Create a LogicalBlock from header node.

        Args:
            node: Header AST node

        Returns:
            LogicalBlock representing the header
        """
        self.block_id_counter += 1
        level = self._get_header_level(node)
        text = node.get_text_content().strip()

        # Render header with markdown syntax
        content = "#" * level + " " + text

        return LogicalBlock(
            block_type="header",
            content=content,
            ast_node=node,
            start_offset=node.start_pos.offset,
            end_offset=node.end_pos.offset,
            start_line=node.start_pos.line + 1,  # Convert to 1-based
            end_line=node.end_pos.line + 1,
            is_atomic=True,
            metadata={
                "id": f"block_{self.block_id_counter}",
                "level": level,
                "text": text,
            },
        )

    def _create_content_block(self, node: MarkdownNode) -> LogicalBlock:
        """
        Create a LogicalBlock from content node (Phase 2 Task 7.3).

        Preserves Markdown structure by rendering from AST with proper formatting.

        Args:
            node: Content AST node (paragraph, list, code, table)

        Returns:
            LogicalBlock representing the content with preserved Markdown structure
        """
        self.block_id_counter += 1

        # Determine block type
        block_type_map = {
            NodeType.PARAGRAPH: "paragraph",
            NodeType.LIST: "list",
            NodeType.CODE_BLOCK: "code",
            NodeType.TABLE: "table",
            NodeType.BLOCKQUOTE: "blockquote",
        }
        block_type = block_type_map.get(node.type, "paragraph")

        # Render content with structure preservation
        content = self._render_node_to_markdown(node)

        return LogicalBlock(
            block_type=block_type,
            content=content,
            ast_node=node,
            start_offset=node.start_pos.offset,
            end_offset=node.end_pos.offset,
            start_line=node.start_pos.line + 1,  # Convert to 1-based
            end_line=node.end_pos.line + 1,
            is_atomic=True,
            metadata={
                "id": f"block_{self.block_id_counter}",
                "node_type": node.type.value,
            },
        )

    def _render_node_to_markdown(self, node: MarkdownNode) -> str:
        """
        Render AST node back to Markdown preserving structure (Phase 2 Task 7.3).

        Requirements 3.1-3.4: Preserve headers, lists, code blocks, tables.

        Args:
            node: AST node to render

        Returns:
            Markdown string with preserved structure
        """
        if node.type == NodeType.CODE_BLOCK:
            # Preserve code fence markers and language tag
            # Check multiple possible keys where language might be stored
            language = (
                node.metadata.get("info")  # markdown-it-py, commonmark
                or node.metadata.get("language")  # mistune with lang key
                or node.metadata.get("lang")  # direct lang key
                or ""
            )
            code_content = node.get_text_content()
            # Remove trailing newlines from code_content to avoid double newlines
            code_content = code_content.rstrip("\n")
            return f"```{language}\n{code_content}\n```"

        elif node.type == NodeType.LIST:
            # Properly render lists with structure preservation
            return self._render_list(node)

        elif node.type == NodeType.TABLE:
            # Preserve table structure
            # For now, use simple rendering
            # Full table rendering would need more context
            return node.get_text_content()

        elif node.type == NodeType.BLOCKQUOTE:
            # Preserve blockquote markers
            content = node.get_text_content()
            lines = content.split("\n")
            return "\n".join(f"> {line}" for line in lines)

        elif node.type == NodeType.PARAGRAPH:
            # Reconstruct paragraph with inline elements (links, emphasis)
            return self._render_inline_content(node)

        else:
            # Other content - reconstruct with inline elements
            return self._render_inline_content(node)
            return node.get_text_content()

    def _render_inline_content(self, node: MarkdownNode) -> str:  # noqa: C901
        """
        Render node content preserving inline elements (links, emphasis).

        This method reconstructs markdown from AST, preserving:
        - Links: [text](url)
        - Emphasis: *text* or _text_
        - Strong: **text** or __text__
        - Inline code: `code`

        Args:
            node: AST node to render

        Returns:
            Markdown string with preserved inline formatting
        """
        # If node has no children, use content directly
        if not node.children:
            if node.content and node.content.strip():
                return node.content
            return node.get_text_content()

        # Reconstruct content from children, preserving inline elements
        parts = []
        for child in node.children:
            if child.type == NodeType.LINK:
                # Reconstruct link: [text](url)
                # Check for nested IMAGE (badge pattern: [![alt](img)](url))
                href = child.metadata.get(
                    "href", child.metadata.get("hre", child.metadata.get("url", ""))
                )

                # Check if link contains an image (badge)
                image_children = [c for c in child.children if c.type == NodeType.IMAGE]
                if image_children:
                    # Badge: [![alt](img)](url)
                    img = image_children[0]
                    alt = img.content or img.metadata.get("alt", "")
                    src = img.metadata.get("src", "")
                    if href:
                        parts.append(f"[![{alt}]({src})]({href})")
                    else:
                        parts.append(f"![{alt}]({src})")
                else:
                    # Regular link: [text](url)
                    text = child.content or child.get_text_content()
                    if href:
                        parts.append(f"[{text}]({href})")
                    else:
                        parts.append(text)
            elif child.type == NodeType.IMAGE:
                # Reconstruct image: ![alt](src)
                alt = child.content or child.metadata.get("alt", "")
                src = child.metadata.get("src", "")
                parts.append(f"![{alt}]({src})")
            elif child.type == NodeType.EMPHASIS:
                # Reconstruct emphasis: *text*
                text = child.content or child.get_text_content()
                parts.append(f"*{text}*")
            elif child.type == NodeType.STRONG:
                # Reconstruct strong: **text**
                text = child.content or child.get_text_content()
                parts.append(f"**{text}**")
            elif child.type == NodeType.TEXT:
                # Plain text
                text = child.content or child.get_text_content()
                parts.append(text)
            else:
                # Other types - recurse
                parts.append(self._render_inline_content(child))

        result = "".join(parts)

        # If reconstruction failed, fall back to node.content or get_text_content
        if not result.strip():
            if node.content and node.content.strip():
                return node.content
            return node.get_text_content()

        return result

    def _render_list(self, list_node: MarkdownNode) -> str:
        """
        Render a list node with proper formatting.

        Preserves:
        - List markers (-, *, +, 1., 2., etc.)
        - Indentation for nested lists
        - Line breaks between items
        - Task list checkboxes

        Args:
            list_node: List node from AST

        Returns:
            Formatted list markdown
        """
        # Check if this is an ordered or unordered list
        list_type = list_node.metadata.get("ordered", False)
        start_number = list_node.metadata.get("start", 1)

        rendered_items = []
        item_number = start_number

        # Process direct child LIST_ITEM nodes
        for child in list_node.children:
            if child.type == NodeType.LIST_ITEM:
                rendered_item = self._render_list_item(
                    child, list_type=list_type, item_number=item_number, indent_level=0
                )
                rendered_items.append(rendered_item)
                if list_type:
                    item_number += 1

        # If no children found (fallback), use get_text_content with normalization
        if not rendered_items:
            content = list_node.get_text_content()
            # Apply basic list normalization
            from .text_normalizer import normalize_list_content

            return normalize_list_content(content)

        return "\n".join(rendered_items)

    def _render_list_item(
        self,
        item_node: MarkdownNode,
        list_type: bool,
        item_number: int,
        indent_level: int,
    ) -> str:
        """
        Render a single list item with proper marker and indentation.

        Args:
            item_node: LIST_ITEM node
            list_type: True for ordered, False for unordered
            item_number: Current item number (for ordered lists)
            indent_level: Indentation level (for nested lists)

        Returns:
            Formatted list item
        """
        indent = "  " * indent_level

        # Determine marker
        if list_type:
            marker = f"{item_number}."
        else:
            # Check for task list
            is_task = item_node.metadata.get("is_task", False)
            is_checked = item_node.metadata.get("is_checked", False)

            if is_task:
                checkbox = "[x]" if is_checked else "[ ]"
                marker = f"- {checkbox}"
            else:
                marker = "-"

        # Get item content
        content_parts = []
        nested_lists = []

        for child in item_node.children:
            if child.type == NodeType.LIST:
                # Nested list - render separately
                nested_lists.append(self._render_list(child))
            else:
                # Regular content - preserve markdown formatting (links, emphasis)
                # Use child.content if available, fall back to get_text_content()
                if child.content and child.content.strip():
                    content = child.content
                else:
                    content = child.get_text_content()
                if content.strip():
                    content_parts.append(content.strip())

        # Join content - preserve markdown formatting
        if content_parts:
            item_content = " ".join(content_parts)
        elif item_node.content and item_node.content.strip():
            # Use raw content if available (preserves links)
            item_content = item_node.content.strip()
        else:
            item_content = item_node.get_text_content().strip()

        # Format the item
        result = f"{indent}{marker} {item_content}"

        # Add nested lists
        if nested_lists:
            nested_content = "\n".join(nested_lists)
            result = f"{result}\n{nested_content}"

        return result
