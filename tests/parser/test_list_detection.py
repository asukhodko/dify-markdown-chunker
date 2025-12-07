"""
Tests for list detection in parser.
"""

from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import ListType


class TestBasicListParsing:
    """Test basic list parsing functionality."""

    def test_parse_bullet_list(self):
        """Basic bullet list parsing."""
        text = """- Item 1
- Item 2
- Item 3"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 1
        assert analysis.list_item_count == 3
        assert len(analysis.list_blocks) == 1

        block = analysis.list_blocks[0]
        assert block.item_count == 3
        assert block.list_type == ListType.BULLET
        assert block.max_depth == 0
        assert not block.has_nested

        assert block.items[0].content == "Item 1"
        assert block.items[1].content == "Item 2"
        assert block.items[2].content == "Item 3"

    def test_parse_numbered_list(self):
        """Numbered list parsing."""
        text = """1. First item
2. Second item
3. Third item"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 1
        assert analysis.list_item_count == 3

        block = analysis.list_blocks[0]
        assert block.list_type == ListType.NUMBERED
        assert block.items[0].marker == "1."
        assert block.items[1].marker == "2."
        assert block.items[2].marker == "3."

    def test_parse_checkbox_list(self):
        """Checkbox detection and state."""
        text = """- [ ] Unchecked task
- [x] Checked task
- [X] Also checked"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 1
        assert analysis.has_checkbox_lists

        block = analysis.list_blocks[0]
        assert block.list_type == ListType.CHECKBOX

        assert block.items[0].is_checked is False
        assert block.items[1].is_checked is True
        assert block.items[2].is_checked is True


class TestNestedLists:
    """Test nested list parsing."""

    def test_nested_list_depth(self):
        """Depth calculation accuracy."""
        text = """- Parent
  - Child 1
  - Child 2
    - Grandchild"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 1
        block = analysis.list_blocks[0]

        assert block.has_nested
        assert block.max_depth == 2
        assert analysis.max_list_depth == 2

        assert block.items[0].depth == 0
        assert block.items[1].depth == 1
        assert block.items[2].depth == 1
        assert block.items[3].depth == 2

    def test_deep_nesting(self):
        """Maximum depth support."""
        text = """- Level 0
  - Level 1
    - Level 2
      - Level 3
        - Level 4"""
        parser = Parser()
        analysis = parser.analyze(text)

        block = analysis.list_blocks[0]
        assert block.max_depth == 4
        assert block.items[4].depth == 4


class TestListBoundaries:
    """Test list block boundary detection."""

    def test_list_continuation_lines(self):
        """Multi-line item handling."""
        text = """- Item with
  continuation line
- Another item"""
        parser = Parser()
        analysis = parser.analyze(text)

        block = analysis.list_blocks[0]
        assert block.item_count == 2
        assert "continuation line" in block.items[0].content

    def test_list_block_boundaries(self):
        """Block start/end detection."""
        text = """- List 1 Item 1
- List 1 Item 2

- List 2 Item 1
- List 2 Item 2"""
        parser = Parser()
        analysis = parser.analyze(text)

        # Single empty line doesn't break same-type lists (markdown standard)
        # Lists of same type are continuous unless separated by 2+ empty lines
        assert analysis.list_count == 1
        assert analysis.list_blocks[0].item_count == 4

    def test_adjacent_lists(self):
        """Multiple block detection."""
        text = """- Bullet list

1. Numbered list
2. Second item"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 2
        assert analysis.list_blocks[0].list_type == ListType.BULLET
        assert analysis.list_blocks[1].list_type == ListType.NUMBERED


class TestMixedListTypes:
    """Test handling of mixed list types."""

    def test_mixed_list_types(self):
        """Multiple types in one document."""
        text = """- Bullet item

1. Numbered item

- [ ] Checkbox item"""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 3
        types = [block.list_type for block in analysis.list_blocks]
        assert ListType.BULLET in types
        assert ListType.NUMBERED in types
        assert ListType.CHECKBOX in types


class TestListMetrics:
    """Test list ratio and metrics calculation."""

    def test_list_ratio_calculation(self):
        """Metric computation."""
        text = """Some text before.

- List item 1
- List item 2
- List item 3

More text after."""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_ratio > 0.0
        assert analysis.list_ratio < 1.0
        assert analysis.list_item_count == 3

    def test_lists_in_code_excluded(self):
        """Code block exclusion."""
        text = """Normal list:
- Item 1

```markdown
This is code:
- Not a list item
- Still not a list
```

- Item 2"""
        parser = Parser()
        analysis = parser.analyze(text)

        # Should only detect the real list items, not those in code block
        assert analysis.list_count == 2  # Two separate blocks
        total_items = sum(b.item_count for b in analysis.list_blocks)
        assert total_items == 2  # Only Item 1 and Item 2


class TestEdgeCases:
    """Test edge cases in list parsing."""

    def test_empty_document(self):
        """Empty document handling."""
        parser = Parser()
        analysis = parser.analyze("")

        assert analysis.list_count == 0
        assert analysis.list_item_count == 0
        assert analysis.list_ratio == 0.0

    def test_no_lists(self):
        """Document without lists."""
        text = """# Just a heading

Some paragraph text."""
        parser = Parser()
        analysis = parser.analyze(text)

        assert analysis.list_count == 0
        assert analysis.list_blocks == []

    def test_mixed_markers(self):
        """Different bullet markers in same list."""
        text = """- Item 1
* Item 2
+ Item 3"""
        parser = Parser()
        analysis = parser.analyze(text)

        # Should still be treated as one bullet list block
        assert analysis.list_count == 1
        assert analysis.list_blocks[0].list_type == ListType.BULLET
        assert analysis.list_blocks[0].item_count == 3
