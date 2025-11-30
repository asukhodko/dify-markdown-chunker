#!/usr/bin/env python3
"""
Test script for MixedStrategy Stage 1 integration fixes.

This script tests the critical fixes for MixedStrategy:
- List detection from Stage1Results
- Table detection from Stage1Results
- Fallback to regex when Stage 1 data unavailable
- Mixed content preservation with all element types
- Proper indivisible marking for lists and tables
"""

from unittest.mock import Mock

from markdown_chunker.chunker.strategies.mixed_strategy import (
    MixedStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import (
    ContentAnalysis,
    ElementCollection,
    ListItem,
    MarkdownList,
    Stage1Results,
    Table,
)


def create_mock_stage1_results(lists=None, tables=None, fenced_blocks=None):
    """Create mock Stage1Results for testing."""
    mock_results = Mock(spec=Stage1Results)

    # Create mock elements collection
    mock_elements = Mock(spec=ElementCollection)
    mock_elements.lists = lists or []
    mock_elements.tables = tables or []

    mock_results.elements = mock_elements
    mock_results.fenced_blocks = fenced_blocks or []

    return mock_results


def test_mixed_strategy_uses_stage1_lists():
    """Test that MixedStrategy uses Stage1Results lists instead of regex."""
    md = """# Features

- Feature 1: Authentication
- Feature 2: Authorization
- Feature 3: Logging"""

    # Create real Stage1Results with list data
    from markdown_chunker.parser.types import ListItem, MarkdownList

    list_items = [
        ListItem(
            content="Feature 1: Authentication", level=0, marker="-", line=3, offset=20
        ),
        ListItem(
            content="Feature 2: Authorization", level=0, marker="-", line=4, offset=50
        ),
        ListItem(content="Feature 3: Logging", level=0, marker="-", line=5, offset=80),
    ]

    real_list = MarkdownList(
        type="unordered",  # Correct field name
        items=list_items,  # Real items
        start_line=3,
        end_line=5,
        max_nesting_level=0,
    )

    stage1_results = create_mock_stage1_results(lists=[real_list])

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have list element from Stage 1
    list_elements = [e for e in elements if e.element_type == "list"]
    assert len(list_elements) == 1
    assert list_elements[0].is_indivisible is True
    assert list_elements[0].metadata["source"] == "stage1_analysis"
    assert list_elements[0].metadata["item_count"] == 3
    assert list_elements[0].metadata["list_type"] == "unordered"


def test_mixed_strategy_uses_stage1_tables():
    """Test that MixedStrategy uses Stage1Results tables instead of regex."""
    md = """# API Reference

| Method | Description |
|--------|-------------|
| GET    | Retrieve    |
| POST   | Create      |"""

    # Create real Stage1Results with table data
    from markdown_chunker.parser.types import Table

    real_table = Table(
        headers=["Method", "Description"],  # Real headers list
        rows=[["GET", "Retrieve"], ["POST", "Create"]],  # Real rows
        start_line=3,
        end_line=6,
        column_count=2,
        alignment=["left", "left"],
    )

    stage1_results = create_mock_stage1_results(tables=[real_table])

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have table element from Stage 1
    table_elements = [e for e in elements if e.element_type == "table"]
    assert len(table_elements) == 1
    assert table_elements[0].is_indivisible is True
    assert table_elements[0].metadata["source"] == "stage1_analysis"
    assert table_elements[0].metadata["columns"] == 2
    assert table_elements[0].metadata["rows"] == 2  # Real table has 2 data rows
    assert table_elements[0].metadata["has_header"] is True


def test_mixed_strategy_fallback_to_regex_lists():
    """Test fallback to regex when Stage 1 list data unavailable."""
    md = """# Features

- Feature 1: Authentication
- Feature 2: Authorization
- Feature 3: Logging"""

    # Mock Stage1Results without list data
    stage1_results = create_mock_stage1_results(lists=None)

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have list element from regex fallback
    list_elements = [e for e in elements if e.element_type == "list"]
    assert len(list_elements) == 1
    assert list_elements[0].is_indivisible is True
    assert list_elements[0].metadata["source"] == "regex_fallback"
    assert list_elements[0].metadata["list_type"] == "unordered"
    assert list_elements[0].metadata["item_count"] == 3


def test_mixed_strategy_fallback_to_regex_tables():
    """Test fallback to regex when Stage 1 table data unavailable."""
    md = """# API Reference

| Method | Description |
|--------|-------------|
| GET    | Retrieve    |
| POST   | Create      |"""

    # Mock Stage1Results without table data
    stage1_results = create_mock_stage1_results(tables=None)

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have table element from regex fallback
    table_elements = [e for e in elements if e.element_type == "table"]
    assert len(table_elements) == 1
    assert table_elements[0].is_indivisible is True
    assert table_elements[0].metadata["source"] == "regex_fallback"
    assert table_elements[0].metadata["has_header"] is True


def test_mixed_content_preserves_all_structure():
    """Test that mixed content preserves structure from Stage 1."""
    md = """# Documentation

Some introductory text.

```python
def example():
    return "code"
```

| Column 1 | Column 2 |
|----------|----------|
| Data     | More     |

- List item 1
- List item 2

Final paragraph."""

    # Mock complete Stage 1 results
    mock_fenced_block = Mock()
    mock_fenced_block.raw_content = '```python\ndef example():\n    return "code"\n```'
    mock_fenced_block.start_line = 5
    mock_fenced_block.end_line = 8
    mock_fenced_block.language = "python"
    mock_fenced_block.fence_type = "```"

    # Create real Table
    real_table = Table(
        headers=["Column 1", "Column 2"],
        rows=[["Data", "More"]],
        start_line=10,
        end_line=12,
        column_count=2,
        alignment=["left", "left"],
    )

    # Create real MarkdownList
    list_items = [
        ListItem(content="List item 1", level=0, marker="-", line=14, offset=100),
        ListItem(content="List item 2", level=0, marker="-", line=15, offset=120),
    ]
    real_list = MarkdownList(
        type="unordered",
        items=list_items,
        start_line=14,
        end_line=15,
        max_nesting_level=0,
    )

    stage1_results = create_mock_stage1_results(
        lists=[real_list], tables=[real_table], fenced_blocks=[mock_fenced_block]
    )

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have all element types
    element_types = {e.element_type for e in elements}
    assert "header" in element_types
    assert "text" in element_types
    assert "code" in element_types
    assert "table" in element_types
    assert "list" in element_types

    # Verify indivisible elements
    indivisible_elements = [e for e in elements if e.is_indivisible]
    indivisible_types = {e.element_type for e in indivisible_elements}
    assert "code" in indivisible_types
    assert "table" in indivisible_types
    assert "list" in indivisible_types

    # Verify Stage 1 sources
    stage1_elements = [
        e for e in elements if e.metadata.get("source") == "stage1_analysis"
    ]
    assert len(stage1_elements) == 2  # table + list (code doesn't have source metadata)


def test_mixed_strategy_empty_stage1_results():
    """Test behavior with empty Stage1Results."""
    md = """# Simple Document

Just some text with no special elements."""

    # Empty Stage1Results
    stage1_results = create_mock_stage1_results()

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have header and text elements
    element_types = {e.element_type for e in elements}
    assert "header" in element_types
    assert "text" in element_types

    # No indivisible elements
    indivisible_elements = [e for e in elements if e.is_indivisible]
    assert len(indivisible_elements) == 0


def test_mixed_strategy_stage1_priority_over_regex():
    """Test that Stage 1 data takes priority over regex detection."""
    md = """# Document

- This is a list item
- Another list item

| Table | Header |
|-------|--------|
| Data  | Value  |"""

    # Create real Stage1Results with partial data (only list, no table)
    list_items = [
        ListItem(content="This is a list item", level=0, marker="-", line=3, offset=20),
        ListItem(content="Another list item", level=0, marker="-", line=4, offset=45),
    ]
    real_list = MarkdownList(
        type="unordered",
        items=list_items,
        start_line=3,
        end_line=4,
        max_nesting_level=0,
    )

    stage1_results = create_mock_stage1_results(lists=[real_list], tables=None)

    strategy = MixedStrategy()
    elements = strategy._detect_all_elements(md, stage1_results)

    # Should have both list and table
    list_elements = [e for e in elements if e.element_type == "list"]
    table_elements = [e for e in elements if e.element_type == "table"]

    assert len(list_elements) == 1
    assert len(table_elements) == 1

    # List should be from Stage 1, table from regex fallback
    assert list_elements[0].metadata["source"] == "stage1_analysis"
    assert table_elements[0].metadata["source"] == "regex_fallback"


def test_mixed_strategy_integration_with_chunking():
    """Test complete integration with chunking process."""
    md = """# API Documentation

This document describes our REST API.

## Authentication

Use API keys for authentication:

```bash
curl -H "Authorization: Bearer YOUR_KEY" https://api.example.com
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | List users  |
| POST   | /users   | Create user |

## Features

- User management
- Role-based access
- Rate limiting

That's all for now."""

    # Mock comprehensive Stage1Results
    mock_fenced_block = Mock()
    mock_fenced_block.raw_content = (
        '```bash\ncurl -H "Authorization: Bearer YOUR_KEY" https://api.example.com\n```'
    )
    mock_fenced_block.start_line = 9
    mock_fenced_block.end_line = 11
    mock_fenced_block.language = "bash"
    mock_fenced_block.fence_type = "```"

    # Create real Table
    real_table = Table(
        headers=["Method", "Endpoint", "Description"],
        rows=[["GET", "/users", "List users"], ["POST", "/users", "Create user"]],
        start_line=15,
        end_line=18,
        column_count=3,
        alignment=["left", "left", "left"],
    )

    # Create real MarkdownList
    list_items = [
        ListItem(content="User management", level=0, marker="-", line=22, offset=200),
        ListItem(content="Role-based access", level=0, marker="-", line=23, offset=220),
        ListItem(content="Rate limiting", level=0, marker="-", line=24, offset=245),
    ]
    real_list = MarkdownList(
        type="unordered",
        items=list_items,
        start_line=22,
        end_line=24,
        max_nesting_level=0,
    )

    stage1_results = create_mock_stage1_results(
        lists=[real_list], tables=[real_table], fenced_blocks=[mock_fenced_block]
    )

    # Mock analysis for strategy selection
    mock_analysis = Mock(spec=ContentAnalysis)
    mock_analysis.code_ratio = 0.2
    mock_analysis.list_ratio = 0.15
    mock_analysis.table_ratio = 0.15
    mock_analysis.text_ratio = 0.5
    mock_analysis.complexity_score = 0.5

    config = ChunkConfig(max_chunk_size=1000)
    config.min_complexity = 0.3  # Add missing attribute

    strategy = MixedStrategy()

    # Test strategy selection
    can_handle = strategy.can_handle(mock_analysis, config)
    assert can_handle is True

    # Test chunking
    chunks = strategy.apply(md, stage1_results, config)
    assert len(chunks) > 0

    # Verify chunks contain structured elements
    all_content = " ".join(chunk.content for chunk in chunks)
    assert "```bash" in all_content  # Code preserved
    assert "| Method |" in all_content  # Table preserved
    assert "- User management" in all_content  # List preserved


if __name__ == "__main__":  # noqa: C901
    # Run tests manually for debugging
    # Complexity justified: Test runner with sequential execution and error handling
    print("🔍 Testing MixedStrategy Stage 1 Integration...")

    try:
        test_mixed_strategy_uses_stage1_lists()
        print("✅ Stage 1 lists integration")
    except Exception as e:
        print(f"❌ Stage 1 lists test failed: {e}")

    try:
        test_mixed_strategy_uses_stage1_tables()
        print("✅ Stage 1 tables integration")
    except Exception as e:
        print(f"❌ Stage 1 tables test failed: {e}")

    try:
        test_mixed_strategy_fallback_to_regex_lists()
        print("✅ Regex fallback for lists")
    except Exception as e:
        print(f"❌ Regex fallback lists test failed: {e}")

    try:
        test_mixed_strategy_fallback_to_regex_tables()
        print("✅ Regex fallback for tables")
    except Exception as e:
        print(f"❌ Regex fallback tables test failed: {e}")

    try:
        test_mixed_content_preserves_all_structure()
        print("✅ Mixed content structure preservation")
    except Exception as e:
        print(f"❌ Mixed content test failed: {e}")

    try:
        test_mixed_strategy_stage1_priority_over_regex()
        print("✅ Stage 1 priority over regex")
    except Exception as e:
        print(f"❌ Priority test failed: {e}")

    print("\n🎉 MixedStrategy Stage 1 Integration testing completed!")
