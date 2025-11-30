"""Tests for element detector."""

from markdown_chunker.parser.elements import ElementDetector, detect_elements

from .test_data import (
    COMPLEX_LISTS,
    EDGE_CASES,
    SIMPLE_MARKDOWN,
    TABLES_MARKDOWN,
)


class TestElementDetector:
    """Test element detection."""

    def test_simple_detection(self):
        """Test detecting elements in simple markdown."""
        elements = detect_elements(SIMPLE_MARKDOWN)

        # Should find header, list, and table
        assert len(elements.headers) >= 1
        assert len(elements.lists) >= 1
        assert len(elements.tables) >= 1

        # Check header
        header = elements.headers[0]
        assert header.level == 1
        assert "Simple Header" in header.text
        assert header.anchor is not None

    def test_complex_lists(self):
        """Test detecting complex nested lists."""
        elements = detect_elements(COMPLEX_LISTS)

        assert len(elements.lists) >= 3  # Unordered, ordered, task lists

        # Check for different list types
        list_types = {lst.type for lst in elements.lists}
        assert "unordered" in list_types
        assert "ordered" in list_types
        assert "task" in list_types

        # Check nesting levels
        max_nesting = max(lst.max_nesting_level for lst in elements.lists)
        assert max_nesting >= 2  # Should have nested items

    def test_tables_detection(self):
        """Test detecting tables with different alignments."""
        elements = detect_elements(TABLES_MARKDOWN)

        assert len(elements.tables) >= 2

        # Check table structure
        for table in elements.tables:
            assert len(table.headers) > 0
            assert len(table.rows) > 0
            assert table.column_count == len(table.headers)
            assert len(table.alignment) == table.column_count

    def test_header_hierarchy(self):
        """Test header hierarchy building."""
        markdown = """# Level 1
## Level 2
### Level 3
## Another Level 2
# Another Level 1"""

        elements = detect_elements(markdown)
        headers = elements.headers

        assert len(headers) == 5

        # Check levels
        levels = [h.level for h in headers]
        assert levels == [1, 2, 3, 2, 1]

        # Check hierarchy paths
        level3_header = headers[2]  # ### Level 3
        path = level3_header.get_hierarchy_path(headers)
        assert "Level 1" in path
        assert "Level 2" in path
        assert "Level 3" in path

    def test_task_lists(self):
        """Test task list detection."""
        task_markdown = """- [x] Completed task
- [ ] Incomplete task
  - [x] Completed subtask
  - [ ] Incomplete subtask"""

        elements = detect_elements(task_markdown)

        assert len(elements.lists) == 1
        task_list = elements.lists[0]

        assert task_list.type == "task"

        # Check task states
        completed_tasks = [item for item in task_list.items if item.is_checked]
        incomplete_tasks = [item for item in task_list.items if not item.is_checked]

        assert len(completed_tasks) >= 1
        assert len(incomplete_tasks) >= 1

    def test_malformed_table(self):
        """Test handling malformed tables."""
        elements = detect_elements(EDGE_CASES["malformed_table"])

        # Should either detect no tables or handle gracefully
        # The exact behavior depends on implementation robustness
        assert isinstance(elements.tables, list)

    def test_empty_headers(self):
        """Test handling empty headers."""
        elements = detect_elements(EDGE_CASES["empty_headers"])

        # Should detect headers even if text is empty
        assert len(elements.headers) >= 1

    def test_anchor_generation(self):
        """Test anchor generation for headers."""
        detector = ElementDetector()

        # Test various header texts
        test_cases = [
            ("Simple Header", "simple-header"),
            ("Header with Spaces", "header-with-spaces"),
            ("Header-with-Hyphens", "header-with-hyphens"),
            ("Header with Special!@# Characters", "header-with-special-characters"),
            ("Multiple   Spaces", "multiple-spaces"),
        ]

        for text, expected in test_cases:
            anchor = detector._generate_anchor(text)
            assert anchor == expected

    def test_list_item_parsing(self):
        """Test parsing individual list items."""
        detector = ElementDetector()

        # Test different list item formats
        test_cases = [
            ("- Simple item", "unordered", "Simple item", 0),
            ("  - Nested item", "unordered", "Nested item", 1),
            ("1. Ordered item", "ordered", "Ordered item", 0),
            ("  2. Nested ordered", "ordered", "Nested ordered", 1),
            ("- [x] Completed task", "task", "Completed task", 0),
            ("- [ ] Incomplete task", "task", "Incomplete task", 0),
        ]

        for line, expected_type, expected_content, expected_level in test_cases:
            item = detector._parse_list_item(line, 0)

            if expected_type == "task":
                assert item.is_task
                assert item.content == expected_content
                assert item.level == expected_level
            else:
                assert not item.is_task
                assert item.content == expected_content
                assert item.level == expected_level


class TestElementDetectorClass:
    """Test ElementDetector class directly."""

    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = ElementDetector()

        assert detector.header_pattern is not None
        assert "unordered" in detector.list_patterns
        assert "ordered" in detector.list_patterns
        assert "task" in detector.list_patterns
        assert detector.table_separator_pattern is not None
        assert detector.table_row_pattern is not None

    def test_table_alignment_parsing(self):
        """Test table alignment parsing."""
        detector = ElementDetector()

        test_cases = [
            ("|:-----|:-----:|------:|", ["left", "center", "right"]),
            ("|------|-------|-------|", ["left", "left", "left"]),
            ("|:-----|-------|:------|", ["left", "left", "left"]),
        ]

        for separator, expected in test_cases:
            alignment = detector._parse_table_alignment(separator, len(expected))
            assert alignment == expected

    def test_list_type_determination(self):
        """Test list type determination."""
        detector = ElementDetector()

        from markdown_chunker.parser.types import ListItem

        # Create test items
        unordered_item = ListItem(
            content="test", level=0, marker="-", line=0, offset=0, is_task=False
        )

        ordered_item = ListItem(
            content="test", level=0, marker="1.", line=0, offset=0, is_task=False
        )

        task_item = ListItem(
            content="test", level=0, marker="- [ ]", line=0, offset=0, is_task=True
        )

        assert detector._determine_list_type(unordered_item) == "unordered"
        assert detector._determine_list_type(ordered_item) == "ordered"
        assert detector._determine_list_type(task_item) == "task"
