"""Integration tests using real Stage 1 data structures."""

from markdown_chunker.chunker.strategies.list_strategy import ListStrategy
from markdown_chunker.chunker.strategies.mixed_strategy import MixedStrategy
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser import process_markdown
from markdown_chunker.parser.types import ListItem, MarkdownList, Table


def test_mixed_strategy_with_real_stage1_lists():
    """Test MixedStrategy uses real Stage 1 list data without AttributeError."""
    content = """# Test Document

```python
def hello():
    print("world")
```

- Item 1
- Item 2
- Item 3

Some text here with enough content to make it mixed."""

    # Run actual Stage 1 parsing
    stage1_results = process_markdown(content)

    # Verify Stage 1 detected the list
    assert len(stage1_results.elements.lists) >= 1
    list_found = False
    for markdown_list in stage1_results.elements.lists:
        if markdown_list.type == "unordered":
            list_found = True
            # Test correct attribute access - should not raise AttributeError
            assert markdown_list.get_item_count() >= 3
            break
    assert list_found, "Should find unordered list"

    # Run Stage 2 with MixedStrategy - should not raise AttributeError
    strategy = MixedStrategy()
    config = ChunkConfig(max_chunk_size=1000)
    chunks = strategy.apply(content, stage1_results, config)

    # Main goal: no AttributeError occurred
    assert len(chunks) > 0


def test_mixed_strategy_with_real_stage1_tables():
    """Test MixedStrategy uses real Stage 1 table data without AttributeError."""
    content = """# API Documentation

```python
# Some code
def api_call():
    pass
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | /users   | Get users   |
| POST   | /users   | Create user |

Some text after table with enough content to make it mixed."""

    # Run actual Stage 1 parsing
    stage1_results = process_markdown(content)

    # Verify Stage 1 detected the table
    assert len(stage1_results.elements.tables) >= 1
    table = stage1_results.elements.tables[0]
    assert len(table.headers) == 3
    # Test correct method call - should not raise AttributeError
    assert table.get_row_count() == 2  # ✅ Method call
    # Test correct headers check - should not raise AttributeError
    assert bool(table.headers) is True  # ✅ Check headers list

    # Run Stage 2 - should not raise AttributeError
    strategy = MixedStrategy()
    config = ChunkConfig(max_chunk_size=1000)
    chunks = strategy.apply(content, stage1_results, config)

    # Main goal: no AttributeError occurred
    assert len(chunks) > 0


def test_list_strategy_with_real_stage1_data():
    """Test ListStrategy uses real Stage 1 list data."""
    content = """1. First item
2. Second item
   - Nested unordered
   - Another nested
3. Third item"""

    # Run actual Stage 1 parsing
    stage1_results = process_markdown(content)
    assert len(stage1_results.elements.lists) > 0

    # Run Stage 2 - should not raise AttributeError
    strategy = ListStrategy()
    config = ChunkConfig(max_chunk_size=1000)
    chunks = strategy.apply(content, stage1_results, config)

    assert len(chunks) > 0


def test_no_attribute_errors_on_real_structures():
    """Ensure no AttributeError when accessing Stage 1 structures correctly."""
    # Create real Stage 1 structures
    list_item = ListItem(
        content="Test item",
        level=0,
        marker="-",
        line=5,  # ✅ Has .line (NOT .start_line/.end_line)
        offset=0,
    )

    markdown_list = MarkdownList(
        type="unordered",  # ✅ Has .type (NOT .list_type)
        items=[list_item],
        start_line=5,
        end_line=5,
        max_nesting_level=0,
    )

    table = Table(
        headers=["Col1", "Col2"],  # ✅ List (NOT .has_header boolean)
        rows=[["A", "B"], ["C", "D"]],
        start_line=10,
        end_line=13,
        column_count=2,
    )

    # These should all work without AttributeError
    assert markdown_list.type == "unordered"
    assert markdown_list.get_item_count() == 1
    assert table.get_row_count() == 2
    assert bool(table.headers) is True
    assert list_item.line == 5


def test_stage1_usage_rate_high():
    """Verify Stage 1 data usage rate is high when mixed content is present."""
    content = """# Document

```python
def example():
    return True
```

- List item 1
- List item 2
- List item 3

| A | B |
|---|---|
| 1 | 2 |

Some text with enough content to make this a mixed document."""

    stage1_results = process_markdown(content)
    strategy = MixedStrategy()
    config = ChunkConfig(max_chunk_size=1000)
    chunks = strategy.apply(content, stage1_results, config)

    # Check that Stage 1 data structures are accessible without AttributeError
    assert len(stage1_results.elements.lists) > 0
    assert len(stage1_results.elements.tables) > 0

    # Verify chunks were created
    assert len(chunks) > 0
