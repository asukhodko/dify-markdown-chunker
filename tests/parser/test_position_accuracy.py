"""
Tests for position accuracy in element detection.
Validates that all elements have precise position information for Stage 2.
"""

from markdown_chunker.parser import extract_fenced_blocks
from markdown_chunker.parser.elements import detect_elements


class TestHeaderPositionAccuracy:
    """Test header position accuracy."""

    def test_header_line_numbers_accurate(self):
        """Test that header line numbers are accurate."""
        content = """Line 0
# Header at line 1
Line 2
## Header at line 3
Line 4
"""
        elements = detect_elements(content)

        assert len(elements.headers) == 2
        assert elements.headers[0].line == 1
        assert elements.headers[1].line == 3

    def test_header_offset_accurate(self):
        """Test that header offsets are accurate."""
        content = """First line
# Header
Third line"""
        elements = detect_elements(content)

        assert len(elements.headers) == 1
        # Offset should be after "First line\n" (11 chars)
        assert elements.headers[0].offset == 11

    def test_multiple_headers_positions(self):
        """Test positions of multiple headers."""
        content = """# H1
## H2
### H3
#### H4
"""
        elements = detect_elements(content)

        assert len(elements.headers) == 4
        for i, header in enumerate(elements.headers):
            assert header.line == i
            assert header.level == i + 1


class TestListPositionAccuracy:
    """Test list position accuracy."""

    def test_list_item_line_numbers(self):
        """Test that list item line numbers are accurate."""
        content = """Text before
- Item 1
- Item 2
- Item 3
Text after"""
        elements = detect_elements(content)

        assert len(elements.lists) == 1
        assert len(elements.lists[0].items) == 3

        for i, item in enumerate(elements.lists[0].items):
            assert item.line == 1 + i

    def test_nested_list_positions(self):
        """Test positions of nested list items."""
        content = """- Level 0
  - Level 1
    - Level 2
  - Level 1 again
- Level 0 again"""
        elements = detect_elements(content)

        assert len(elements.lists) == 1
        items = elements.lists[0].items

        assert items[0].line == 0
        assert items[0].level == 0
        assert items[1].line == 1
        assert items[1].level == 1
        assert items[2].line == 2
        assert items[2].level == 2

    def test_list_start_end_lines(self):
        """Test list start and end line numbers."""
        content = """Text before

- Item 1
- Item 2
- Item 3

Text after"""
        elements = detect_elements(content)

        assert len(elements.lists) == 1
        lst = elements.lists[0]

        assert lst.start_line == 2
        assert lst.end_line == 4


class TestTablePositionAccuracy:
    """Test table position accuracy."""

    def test_table_line_numbers(self):
        """Test that table line numbers are accurate."""
        content = """Text before

| Header |
|--------|
| Cell 1 |
| Cell 2 |

Text after"""
        elements = detect_elements(content)

        assert len(elements.tables) == 1
        table = elements.tables[0]

        assert table.start_line == 2
        assert table.end_line == 5

    def test_multiple_tables_positions(self):
        """Test positions of multiple tables."""
        content = """| Table 1 |
|---------|
| Data 1  |

Some text

| Table 2 |
|---------|
| Data 2  |
"""
        elements = detect_elements(content)

        assert len(elements.tables) == 2
        assert elements.tables[0].start_line == 0
        assert elements.tables[0].end_line == 2
        assert elements.tables[1].start_line == 6
        assert elements.tables[1].end_line == 8


class TestCodeBlockPositionAccuracy:
    """Test code block position accuracy."""

    def test_code_block_line_numbers(self):
        """Test that code block line numbers are accurate."""
        content = """Text before

```python
def test():
    pass
```

Text after"""
        blocks = extract_fenced_blocks(content)

        assert len(blocks) == 1
        # start_line points to first content line (after opening fence)
        assert blocks[0].start_line == 3
        # end_line points to closing fence line
        assert blocks[0].end_line == 6

    def test_code_block_offsets(self):
        """Test that code block offsets are accurate."""
        content = """Line 1
```python
code
```
Line 5"""
        blocks = extract_fenced_blocks(content)

        assert len(blocks) == 1
        # Start offset should be after "Line 1\n" (7 chars)
        assert blocks[0].start_offset == 7
        # End offset should include the closing fence
        assert blocks[0].end_offset > blocks[0].start_offset

    def test_multiple_code_blocks_positions(self):
        """Test positions of multiple code blocks."""
        content = """```python
code1
```

Text

```javascript
code2
```
"""
        blocks = extract_fenced_blocks(content)

        assert len(blocks) == 2
        # start_line points to first content line (after opening fence)
        assert blocks[0].start_line == 1
        assert blocks[0].end_line == 3
        assert blocks[1].start_line == 7
        assert blocks[1].end_line == 9


class TestMixedElementPositions:
    """Test positions when multiple element types are present."""

    def test_headers_and_lists_positions(self):
        """Test positions when headers and lists are mixed."""
        content = """# Header 1

- List item 1
- List item 2

## Header 2

- List item 3
"""
        elements = detect_elements(content)

        assert len(elements.headers) == 2
        assert len(elements.lists) == 2

        # Check header positions
        assert elements.headers[0].line == 0
        assert elements.headers[1].line == 5

        # Check list positions
        assert elements.lists[0].start_line == 2
        assert elements.lists[1].start_line == 7

    def test_all_element_types_positions(self):
        """Test positions when all element types are present."""
        content = """# Header

Some text

```python
code
```

- List item

| Table |
|-------|
| Cell  |
"""
        elements = detect_elements(content)
        blocks = extract_fenced_blocks(content)

        # Verify all elements detected
        assert len(elements.headers) == 1
        assert len(blocks) == 1
        assert len(elements.lists) == 1
        assert len(elements.tables) == 1

        # Verify positions don't overlap
        header_line = elements.headers[0].line
        code_start = blocks[0].start_line
        list_start = elements.lists[0].start_line
        table_start = elements.tables[0].start_line

        assert header_line < code_start < list_start < table_start


class TestPositionConsistency:
    """Test consistency of position information."""

    def test_line_and_offset_consistency(self):
        """Test that line numbers and offsets are consistent."""
        content = """Line 0
Line 1
# Header at line 2
Line 3
"""
        elements = detect_elements(content)
        lines = content.split("\n")

        assert len(elements.headers) == 1
        header = elements.headers[0]

        # Calculate expected offset
        expected_offset = sum(len(line) + 1 for line in lines[: header.line])
        assert header.offset == expected_offset

    def test_start_end_line_consistency(self):
        """Test that start and end lines are consistent."""
        content = """| Header |
|--------|
| Row 1  |
| Row 2  |
| Row 3  |
"""
        elements = detect_elements(content)

        assert len(elements.tables) == 1
        table = elements.tables[0]

        # End line should be after start line
        assert table.end_line > table.start_line
        # Should span correct number of lines (header + separator + 3 rows)
        assert table.end_line - table.start_line == 4

    def test_nested_elements_position_hierarchy(self):
        """Test that nested elements maintain position hierarchy."""
        content = """- Parent item
  - Child item 1
  - Child item 2
    - Grandchild item
"""
        elements = detect_elements(content)

        assert len(elements.lists) == 1
        items = elements.lists[0].items

        # All items should have increasing line numbers
        for i in range(len(items) - 1):
            assert items[i].line < items[i + 1].line


class TestEdgeCasePositions:
    """Test position handling in edge cases."""

    def test_empty_lines_dont_affect_positions(self):
        """Test that empty lines don't affect position accuracy."""
        content = """

# Header


- List item


| Table |
|-------|
| Cell  |


"""
        elements = detect_elements(content)

        # Positions should still be accurate despite empty lines
        assert elements.headers[0].line == 2
        assert elements.lists[0].start_line == 5
        assert elements.tables[0].start_line == 8

    def test_windows_line_endings(self):
        """Test position handling with Windows line endings."""
        content = "# Header\r\n\r\n- List item\r\n"
        # Normalize to Unix line endings for testing
        normalized = content.replace("\r\n", "\n")

        elements = detect_elements(normalized)

        assert len(elements.headers) == 1
        assert len(elements.lists) == 1
        assert elements.headers[0].line == 0
        assert elements.lists[0].start_line == 2

    def test_unicode_content_positions(self):
        """Test position handling with Unicode content."""
        content = """# 测试标题

- 列表项 1
- 列表项 2

| 表头 |
|------|
| 单元格 |
"""
        elements = detect_elements(content)

        # Positions should be accurate regardless of Unicode
        assert len(elements.headers) == 1
        assert len(elements.lists) == 1
        assert len(elements.tables) == 1

        assert elements.headers[0].line == 0
        assert elements.lists[0].start_line == 2
        assert elements.tables[0].start_line == 5
