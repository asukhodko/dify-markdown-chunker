"""Tests for basic data structures."""

import pytest

from markdown_chunker.parser.types import FencedBlock, MarkdownNode, NodeType, Position


class TestPosition:
    """Test Position data structure."""

    def test_valid_position(self):
        """Test creating valid position."""
        pos = Position(line=1, column=5, offset=10)
        assert pos.line == 1
        assert pos.column == 5
        assert pos.offset == 10

    def test_invalid_line(self):
        """Test invalid line number."""
        with pytest.raises(ValueError):
            Position(line=-1, column=0, offset=0)

    def test_invalid_column(self):
        """Test invalid column number."""
        with pytest.raises(ValueError):
            Position(line=0, column=-1, offset=0)

    def test_invalid_offset(self):
        """Test invalid offset."""
        with pytest.raises(ValueError):
            Position(line=0, column=0, offset=-1)


class TestMarkdownNode:
    """Test MarkdownNode data structure."""

    def test_create_node(self):
        """Test creating a markdown node."""
        start_pos = Position(0, 0, 0)
        end_pos = Position(1, 10, 20)

        node = MarkdownNode(
            type=NodeType.HEADER,
            content="# Test Header",
            start_pos=start_pos,
            end_pos=end_pos,
        )

        assert node.type == NodeType.HEADER
        assert node.content == "# Test Header"
        assert node.start_pos == start_pos
        assert node.end_pos == end_pos
        assert len(node.children) == 0
        assert len(node.metadata) == 0

    def test_find_children(self):
        """Test finding child nodes."""
        parent = MarkdownNode(
            type=NodeType.DOCUMENT,
            content="",
            start_pos=Position(0, 0, 0),
            end_pos=Position(10, 0, 100),
        )

        header = MarkdownNode(
            type=NodeType.HEADER,
            content="# Header",
            start_pos=Position(0, 0, 0),
            end_pos=Position(0, 8, 8),
        )

        paragraph = MarkdownNode(
            type=NodeType.PARAGRAPH,
            content="Text",
            start_pos=Position(2, 0, 10),
            end_pos=Position(2, 4, 14),
        )

        parent.children = [header, paragraph]

        headers = parent.find_children(NodeType.HEADER)
        assert len(headers) == 1
        assert headers[0] == header

        paragraphs = parent.find_children(NodeType.PARAGRAPH)
        assert len(paragraphs) == 1
        assert paragraphs[0] == paragraph

    def test_get_text_content(self):
        """Test getting text content."""
        node = MarkdownNode(
            type=NodeType.PARAGRAPH,
            content="Hello world",
            start_pos=Position(0, 0, 0),
            end_pos=Position(0, 11, 11),
        )

        assert node.get_text_content() == "Hello world"

    def test_get_line_range(self):
        """Test getting line range."""
        node = MarkdownNode(
            type=NodeType.PARAGRAPH,
            content="Multi\nline\ntext",
            start_pos=Position(1, 0, 10),
            end_pos=Position(3, 4, 25),
        )

        assert node.get_line_range() == (1, 3)

    def test_is_leaf(self):
        """Test leaf node detection."""
        leaf = MarkdownNode(
            type=NodeType.TEXT,
            content="text",
            start_pos=Position(0, 0, 0),
            end_pos=Position(0, 4, 4),
        )

        parent = MarkdownNode(
            type=NodeType.PARAGRAPH,
            content="",
            start_pos=Position(0, 0, 0),
            end_pos=Position(0, 4, 4),
            children=[leaf],
        )

        assert leaf.is_leaf()
        assert not parent.is_leaf()


class TestFencedBlock:
    """Test FencedBlock data structure."""

    def test_create_fenced_block(self):
        """Test creating a fenced block."""
        block = FencedBlock(
            content="print('hello')",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=1,
            end_line=3,
            start_offset=10,
            end_offset=50,
            nesting_level=0,
            is_closed=True,
            raw_content="```python\nprint('hello')\n```",
        )

        assert block.content == "print('hello')"
        assert block.language == "python"
        assert block.fence_type == "```"
        assert block.is_valid()

    def test_get_hash(self):
        """Test getting content hash."""
        block = FencedBlock(
            content="print('hello')",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=1,
            end_line=3,
            start_offset=0,
            end_offset=20,
            nesting_level=0,
            is_closed=True,
            raw_content="",
        )

        hash_value = block.get_hash()
        assert hash_value.startswith("python_")
        assert len(hash_value) == 15  # "python_" + 8 char hash

    def test_invalid_block(self):
        """Test invalid block detection."""
        invalid_block = FencedBlock(
            content="unclosed",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=1,
            end_line=1,  # Same line
            start_offset=0,
            end_offset=10,
            nesting_level=0,
            is_closed=False,
            raw_content="",
        )

        assert not invalid_block.is_valid()
