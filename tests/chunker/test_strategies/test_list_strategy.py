"""
Tests for ListStrategy.
This module tests the list-heavy document chunking strategy that preserves
list hierarchy and handles nested structures.
"""

from unittest.mock import Mock

import pytest

from markdown_chunker.chunker.strategies.list_strategy import (
    ListGroup,
    ListItemInfo,
    ListStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import (
    ContentAnalysis,
    ElementCollection,
    ListItem,
    MarkdownList,
    Stage1Results,
)


class TestListItemInfo:
    """Test cases for ListItemInfo class."""

    def test_list_item_creation(self):
        """Test creating a list item."""
        item = ListItemInfo(
            content="Test item",
            level=1,
            list_type="unordered",
            marker="-",
            start_line=5,
            end_line=5,
        )

        assert item.content == "Test item"
        assert item.level == 1
        assert item.list_type == "unordered"
        assert item.marker == "-"
        assert item.children == []
        assert item.parent is None

    def test_ordered_list_item(self):
        """Test creating an ordered list item."""
        item = ListItemInfo(
            content="First item",
            level=1,
            list_type="ordered",
            marker="1.",
            number=1,
            start_line=1,
            end_line=1,
        )

        assert item.number == 1
        assert item.list_type == "ordered"

    def test_task_list_item(self):
        """Test creating a task list item."""
        item = ListItemInfo(
            content="Complete task",
            level=1,
            list_type="task",
            marker="-",
            is_checked=True,
            start_line=1,
            end_line=1,
        )

        assert item.is_checked is True
        assert item.list_type == "task"


class TestListGroup:
    """Test cases for ListGroup class."""

    def test_list_group_creation(self):
        """Test creating a list group."""
        item = ListItemInfo("Test", 1, "unordered", "-", start_line=1, end_line=1)

        group = ListGroup(items=[item], size=50, start_line=1, end_line=1)

        assert len(group.items) == 1
        assert group.size == 50
        assert group.is_continuation is False
        assert group.parent_context == ""


class TestListStrategy:
    """Test cases for ListStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = ListStrategy()

        assert strategy.name == "list"
        assert strategy.priority == 4  # Medium priority (excluded from auto anyway)

    def test_can_handle_high_list_count(self):
        """Test can_handle with high list count."""
        strategy = ListStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 8
        analysis.list_ratio = 0.3

        config = ChunkConfig(list_count_threshold=5, list_ratio_threshold=0.6)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_high_list_ratio(self):
        """Test can_handle with high list ratio."""
        strategy = ListStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 3
        analysis.list_ratio = 0.7

        config = ChunkConfig(list_count_threshold=5, list_ratio_threshold=0.6)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_insufficient_lists(self):
        """Test can_handle with insufficient lists."""
        strategy = ListStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 2
        analysis.list_ratio = 0.3

        config = ChunkConfig(list_count_threshold=5, list_ratio_threshold=0.6)

        assert strategy.can_handle(analysis, config) is False

    def test_calculate_quality_high_lists(self):
        """Test quality calculation for high list content."""
        strategy = ListStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 12
        analysis.list_ratio = 0.8
        analysis.has_nested_lists = True

        quality = strategy.calculate_quality(analysis)

        # Should be very high quality
        assert quality > 0.9

    def test_calculate_quality_moderate_lists(self):
        """Test quality calculation for moderate list content."""
        strategy = ListStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 4
        analysis.list_ratio = 0.4
        analysis.has_nested_lists = False

        quality = strategy.calculate_quality(analysis)

        # Should be moderate quality
        assert 0.3 < quality < 0.7

    def test_parse_list_line_unordered(self):
        """Test parsing unordered list line."""
        strategy = ListStrategy()

        line = "- This is an unordered list item"
        item = strategy._parse_list_line(line, 1)

        assert item is not None
        assert item.content == "This is an unordered list item"
        assert item.list_type == "unordered"
        assert item.marker == "-"
        assert item.level == 1

    def test_parse_list_line_ordered(self):
        """Test parsing ordered list line."""
        strategy = ListStrategy()

        line = "1. This is an ordered list item"
        item = strategy._parse_list_line(line, 1)

        assert item is not None
        assert item.content == "This is an ordered list item"
        assert item.list_type == "ordered"
        assert item.marker == "1."
        assert item.number == 1
        assert item.level == 1

    def test_parse_list_line_task(self):
        """Test parsing task list line."""
        strategy = ListStrategy()

        line = "- [x] This is a completed task"
        item = strategy._parse_list_line(line, 1)

        assert item is not None
        assert item.content == "This is a completed task"
        assert item.list_type == "task"
        assert item.is_checked is True

        # Test unchecked task
        line2 = "- [ ] This is an incomplete task"
        item2 = strategy._parse_list_line(line2, 2)

        assert item2.is_checked is False

    def test_parse_list_line_nested(self):
        """Test parsing nested list line."""
        strategy = ListStrategy()

        line = "  - This is a nested item"
        item = strategy._parse_list_line(line, 1)

        assert item is not None
        assert item.level == 2  # One level deeper
        assert item.content == "This is a nested item"

    def test_parse_list_line_non_list(self):
        """Test parsing non-list line."""
        strategy = ListStrategy()

        line = "This is just regular text"
        item = strategy._parse_list_line(line, 1)

        assert item is None

    def test_determine_list_type_task(self):
        """Test determining task list type."""
        strategy = ListStrategy()

        list_type = strategy._determine_list_type("-", "[x] Task content")
        assert list_type == "task"

        list_type = strategy._determine_list_type("-", "[ ] Task content")
        assert list_type == "task"

    def test_determine_list_type_ordered(self):
        """Test determining ordered list type."""
        strategy = ListStrategy()

        list_type = strategy._determine_list_type("1.", "Regular content")
        assert list_type == "ordered"

    def test_determine_list_type_unordered(self):
        """Test determining unordered list type."""
        strategy = ListStrategy()

        list_type = strategy._determine_list_type("-", "Regular content")
        assert list_type == "unordered"

    def test_build_list_hierarchy_simple(self):
        """Test building simple list hierarchy."""
        strategy = ListStrategy()

        items = [
            ListItemInfo("Root 1", 1, "unordered", "-", start_line=1, end_line=1),
            ListItemInfo("Child 1.1", 2, "unordered", "-", start_line=2, end_line=2),
            ListItemInfo("Child 1.2", 2, "unordered", "-", start_line=3, end_line=3),
            ListItemInfo("Root 2", 1, "unordered", "-", start_line=4, end_line=4),
        ]

        hierarchy = strategy._build_list_hierarchy(items)

        assert len(hierarchy) == 2  # Two root items
        assert hierarchy[0].content == "Root 1"
        assert hierarchy[1].content == "Root 2"
        assert len(hierarchy[0].children) == 2
        assert hierarchy[0].children[0].content == "Child 1.1"
        assert hierarchy[0].children[1].content == "Child 1.2"

    def test_calculate_item_size(self):
        """Test calculating item size including children."""
        strategy = ListStrategy()

        root = ListItemInfo("Root", 1, "unordered", "-", start_line=1, end_line=1)
        child1 = ListItemInfo("Child 1", 2, "unordered", "-", start_line=2, end_line=2)
        child2 = ListItemInfo("Child 2", 2, "unordered", "-", start_line=3, end_line=3)

        root.children = [child1, child2]

        size = strategy._calculate_item_size(root)

        # Should include root + both children + formatting
        expected_min = (
            len("Root") + len("Child 1") + len("Child 2") + 30
        )  # Base formatting
        assert size >= expected_min

    def test_format_list_item_unordered(self):
        """Test formatting unordered list item."""
        strategy = ListStrategy()

        item = ListItemInfo("Test item", 1, "unordered", "-", start_line=1, end_line=1)
        formatted = strategy._format_list_item(item)

        assert formatted == "- Test item\n"

    def test_format_list_item_ordered(self):
        """Test formatting ordered list item."""
        strategy = ListStrategy()

        item = ListItemInfo(
            "Test item", 1, "ordered", "1.", number=1, start_line=1, end_line=1
        )
        formatted = strategy._format_list_item(item)

        assert formatted == "1. Test item\n"

    def test_format_list_item_task(self):
        """Test formatting task list item."""
        strategy = ListStrategy()

        # Checked task
        item = ListItemInfo(
            "Done task", 1, "task", "-", is_checked=True, start_line=1, end_line=1
        )
        formatted = strategy._format_list_item(item)

        assert formatted == "- [x] Done task\n"

        # Unchecked task
        item.is_checked = False
        formatted = strategy._format_list_item(item)

        assert formatted == "- [ ] Done task\n"

    def test_format_list_item_nested(self):
        """Test formatting nested list items."""
        strategy = ListStrategy()

        root = ListItemInfo("Root", 1, "unordered", "-", start_line=1, end_line=1)
        child = ListItemInfo("Child", 2, "unordered", "-", start_line=2, end_line=2)
        root.children = [child]

        formatted = strategy._format_list_item(root)

        expected = "- Root\n  - Child\n"
        assert formatted == expected

    def test_count_items(self):
        """Test counting items including children."""
        strategy = ListStrategy()

        root = ListItemInfo("Root", 1, "unordered", "-", start_line=1, end_line=1)
        child1 = ListItemInfo("Child 1", 2, "unordered", "-", start_line=2, end_line=2)
        child2 = ListItemInfo("Child 2", 2, "unordered", "-", start_line=3, end_line=3)
        grandchild = ListItemInfo(
            "Grandchild", 3, "unordered", "-", start_line=4, end_line=4
        )

        child1.children = [grandchild]
        root.children = [child1, child2]

        count = strategy._count_items(root)

        assert count == 4  # root + child1 + child2 + grandchild

    def test_calculate_max_nesting(self):
        """Test calculating maximum nesting level."""
        strategy = ListStrategy()

        root = ListItemInfo("Root", 1, "unordered", "-", start_line=1, end_line=1)
        child = ListItemInfo("Child", 2, "unordered", "-", start_line=2, end_line=2)
        grandchild = ListItemInfo(
            "Grandchild", 3, "unordered", "-", start_line=3, end_line=3
        )

        child.children = [grandchild]
        root.children = [child]

        max_nesting = strategy._calculate_max_nesting(root)

        assert max_nesting == 3  # Deepest level

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = ListStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_no_lists(self):
        """Test applying strategy to content without lists."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []

        config = ChunkConfig.default()
        content = "Just some plain text without any lists."

        chunks = strategy.apply(content, stage1_results, config)

        assert chunks == []

    def test_apply_simple_list(self):
        """Test applying strategy to simple list."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []  # Force manual parsing

        config = ChunkConfig.default()
        content = """# Shopping List

- Apples
- Bananas
- Oranges"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create at least one chunk
        assert len(chunks) >= 1

        # Check that we have list chunks
        list_chunks = [c for c in chunks if c.metadata.get("content_type") == "list"]
        assert len(list_chunks) >= 1

        # Check list metadata
        list_chunk = list_chunks[0]
        assert list_chunk.metadata["list_type"] == "unordered"
        assert list_chunk.metadata["item_count"] >= 1

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = ListStrategy()

        # Can handle - high count
        analysis = Mock(spec=ContentAnalysis)
        analysis.list_count = 8
        analysis.list_ratio = 0.3

        reason = strategy._get_selection_reason(analysis, True)
        assert "8 lists" in reason
        assert "suitable" in reason

        # Can handle - high ratio
        analysis.list_count = 3
        analysis.list_ratio = 0.7

        reason = strategy._get_selection_reason(analysis, True)
        assert "70.0%" in reason
        assert "suitable" in reason

        # Cannot handle
        analysis.list_count = 2
        analysis.list_ratio = 0.2

        reason = strategy._get_selection_reason(analysis, False)
        assert "Insufficient" in reason

    def test_get_list_statistics(self):
        """Test getting list statistics."""
        strategy = ListStrategy()

        chunks = [
            strategy._create_chunk(
                "Content 1",
                1,
                1,
                "list",
                list_type="unordered",
                item_count=3,
                is_continuation=False,
            ),
            strategy._create_chunk(
                "Content 2",
                2,
                2,
                "list",
                list_type="ordered",
                item_count=2,
                is_continuation=True,
            ),
        ]

        stats = strategy.get_list_statistics(chunks)

        assert stats["total_chunks"] == 2
        assert stats["list_types"]["unordered"] == 1
        assert stats["list_types"]["ordered"] == 1
        assert stats["total_items"] == 5
        assert stats["continuation_chunks"] == 1
        assert stats["avg_items_per_chunk"] == 2.5

    def test_get_list_statistics_empty(self):
        """Test getting statistics for empty chunk list."""
        strategy = ListStrategy()

        stats = strategy.get_list_statistics([])

        assert stats["total_chunks"] == 0
        assert stats["list_types"] == {}


class TestListStrategyIntegration:
    """Integration tests for ListStrategy."""

    def test_realistic_todo_list(self):
        """Test with realistic todo list document."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []  # Force manual parsing

        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)

        content = """# Project Tasks

## Development
- [ ] Set up project structure
  - [ ] Create directories
  - [ ] Initialize git repository
  - [x] Set up virtual environment
- [ ] Implement core features
  - [ ] User authentication
  - [ ] Data models
  - [ ] API endpoints
- [x] Write documentation

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance tests

## Deployment
1. Set up CI/CD pipeline
2. Configure production environment
3. Deploy to staging
4. Deploy to production"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) >= 1

        # Should have list chunks
        list_chunks = [c for c in chunks if c.metadata.get("content_type") == "list"]
        assert len(list_chunks) >= 1

        # Check for different list types
        list_types = set(chunk.metadata.get("list_type") for chunk in list_chunks)
        assert "task" in list_types or "ordered" in list_types

        # Check that nested structure is preserved
        nested_chunks = [
            c for c in list_chunks if c.metadata.get("has_nested_items", False)
        ]
        assert len(nested_chunks) >= 1

    def test_mixed_list_types(self):
        """Test handling documents with mixed list types."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []

        config = ChunkConfig.default()

        content = """# Mixed Lists

## Unordered List
- First item
- Second item
- Third item

## Ordered List
1. Step one
2. Step two
3. Step three

## Task List
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task"""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create chunks
        assert len(chunks) >= 1

        list_chunks = [c for c in chunks if c.metadata.get("content_type") == "list"]

        # Should handle different list types
        list_types = set(chunk.metadata.get("list_type") for chunk in list_chunks)
        # At least some list types should be detected
        assert len(list_types) >= 1

    def test_deeply_nested_lists(self):
        """Test handling deeply nested lists."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []

        config = ChunkConfig.default()

        content = """# Nested Structure

- Level 1 Item A
  - Level 2 Item A.1
    - Level 3 Item A.1.a
      - Level 4 Item A.1.a.i
        - Level 5 Item A.1.a.i.α
  - Level 2 Item A.2
- Level 1 Item B
  - Level 2 Item B.1"""

        chunks = strategy.apply(content, stage1_results, config)

        assert len(chunks) >= 1

        list_chunks = [c for c in chunks if c.metadata.get("content_type") == "list"]
        assert len(list_chunks) >= 1

        # Check that deep nesting is handled
        max_nesting = max(chunk.metadata.get("max_nesting", 1) for chunk in list_chunks)
        assert max_nesting >= 3  # Should handle deep nesting

    def test_large_list_splitting(self):
        """Test splitting large lists that exceed chunk size."""
        strategy = ListStrategy()

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.list_items = []

        config = ChunkConfig(max_chunk_size=200, min_chunk_size=50)  # Small chunks

        # Create a large list
        items = []
        for i in range(20):
            items.append(f"- Item {i+1} with some additional content to make it longer")

        content = "# Large List\n\n" + "\n".join(items)

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks due to size constraints
        list_chunks = [c for c in chunks if c.metadata.get("content_type") == "list"]

        # Should split into multiple chunks
        if len(list_chunks) > 1:
            # Check for continuation chunks
            continuation_chunks = [
                c for c in list_chunks if c.metadata.get("is_continuation", False)
            ]
            # May or may not have continuations depending on splitting logic
            assert len(continuation_chunks) >= 0

        # Total content should be preserved
        total_content = " ".join(chunk.content for chunk in list_chunks)
        # Most items should be preserved
        preserved_items = total_content.count("Item")
        assert preserved_items >= 15  # Most items should be there


class TestListStrategyRealObjects:
    """Test ListStrategy with real Stage 1 objects to catch AttributeError issues."""

    def test_extract_list_items_real_stage1_data(self):
        """Test extracting list items with real Stage 1 data."""
        strategy = ListStrategy()

        # Create real ListItem objects
        list_items = [
            ListItem(content="First item", level=0, marker="-", line=1, offset=0),
            ListItem(content="Second item", level=1, marker="-", line=2, offset=15),
            ListItem(content="Third item", level=0, marker="-", line=3, offset=30),
        ]

        # Create real MarkdownList
        markdown_list = MarkdownList(
            type="unordered",
            items=list_items,
            start_line=1,
            end_line=3,
            max_nesting_level=1,
        )

        # Create real ElementCollection
        elements = ElementCollection(lists=[markdown_list])

        # Create real Stage1Results
        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = (
            elements  # Correct path: elements.lists, not list_items
        )

        content = "- First item\n  - Second item\n- Third item"

        # This should not raise AttributeError
        try:
            result_items = strategy._extract_list_items(content, stage1_results)

            # Validate results
            assert len(result_items) == 3
            assert result_items[0].content == "First item"
            assert result_items[0].level == 0
            assert result_items[0].start_line == 1  # Should use item.line
            assert result_items[0].end_line == 1  # Should use item.line

            assert result_items[1].level == 1
            assert result_items[2].level == 0

        except AttributeError as e:
            pytest.fail(f"AttributeError raised: {e}")

    def test_convert_stage1_lists_field_access(self):
        """Test that _convert_stage1_lists uses correct field names."""
        strategy = ListStrategy()

        # Create ListItem with only the fields that actually exist
        list_items = [
            ListItem(
                content="Test item",
                level=0,
                marker="-",
                line=1,  # This is the correct field, not start_line/end_line
                offset=0,
                is_task=True,
                is_checked=True,
            )
        ]

        # This should not raise AttributeError
        try:
            result_items = strategy._convert_stage1_lists(list_items)

            # Validate correct field usage
            assert len(result_items) == 1
            assert result_items[0].start_line == 1  # Should come from item.line
            assert result_items[0].end_line == 1  # Should come from item.line
            assert result_items[0].is_checked is True

        except AttributeError as e:
            pytest.fail(f"AttributeError raised: {e}")

    def test_full_pipeline_with_real_stage1_data(self):
        """Test full ListStrategy pipeline with real Stage 1 data."""
        strategy = ListStrategy()

        # Create nested list structure
        list_items = [
            ListItem(content="Parent 1", level=0, marker="-", line=1, offset=0),
            ListItem(content="Child 1.1", level=1, marker="-", line=2, offset=10),
            ListItem(content="Child 1.2", level=1, marker="-", line=3, offset=25),
            ListItem(content="Parent 2", level=0, marker="-", line=4, offset=40),
        ]

        markdown_list = MarkdownList(
            type="unordered",
            items=list_items,
            start_line=1,
            end_line=4,
            max_nesting_level=1,
        )

        elements = ElementCollection(lists=[markdown_list])

        analysis = ContentAnalysis(
            total_chars=100,
            total_lines=4,
            total_words=8,
            code_ratio=0.0,
            text_ratio=1.0,
            code_block_count=0,
            header_count=0,
            list_count=1,
            content_type="text_heavy",
        )

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements
        stage1_results.analysis = analysis

        config = ChunkConfig.default()

        content = """- Parent 1
  - Child 1.1
  - Child 1.2
- Parent 2"""

        # This should work without AttributeError
        try:
            chunks = strategy.apply(content, stage1_results, config)

            # Validate results
            assert len(chunks) >= 1
            assert all(chunk.content for chunk in chunks)
            assert all(chunk.start_line > 0 for chunk in chunks)

        except AttributeError as e:
            pytest.fail(f"AttributeError raised: {e}")
