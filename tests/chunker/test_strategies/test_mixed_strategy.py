"""
Tests for MixedStrategy.
This module tests the mixed content strategy that handles documents with
multiple element types in significant proportions.
"""

from unittest.mock import Mock

import pytest

from markdown_chunker.chunker.strategies.mixed_strategy import (
    ContentElement,
    LogicalSection,
    MixedStrategy,
)
from markdown_chunker.chunker.types import ChunkConfig
from markdown_chunker.parser.types import (
    ContentAnalysis,
    ElementCollection,
    FencedBlock,
    ListItem,
    MarkdownList,
    Stage1Results,
    Table,
)


class TestContentElement:
    """Test cases for ContentElement class."""

    def test_content_element_creation(self):
        """Test creating a content element."""
        element = ContentElement(
            element_type="text",
            content="Test content",
            start_line=1,
            end_line=3,
            is_indivisible=False,
        )

        assert element.element_type == "text"
        assert element.content == "Test content"
        assert element.is_indivisible is False
        assert element.metadata == {}


class TestLogicalSection:
    """Test cases for LogicalSection class."""

    def test_logical_section_creation(self):
        """Test creating a logical section."""
        header = ContentElement("header", "# Title", 1, 1, False)
        element = ContentElement("text", "Content", 2, 3, False)

        section = LogicalSection(
            header=header, elements=[element], start_line=1, end_line=3
        )

        assert section.header == header
        assert len(section.elements) == 1

    def test_calculate_size(self):
        """Test calculating section size."""
        header = ContentElement("header", "# Title", 1, 1, False)
        element1 = ContentElement("text", "Content 1", 2, 2, False)
        element2 = ContentElement("text", "Content 2", 3, 3, False)

        section = LogicalSection(
            header=header, elements=[element1, element2], start_line=1, end_line=3
        )

        size = section.calculate_size()
        expected = len("# Title") + len("Content 1") + len("Content 2")
        assert size == expected

    def test_get_element_types(self):
        """Test getting element types."""
        header = ContentElement("header", "# Title", 1, 1, False)
        element1 = ContentElement("text", "Text", 2, 2, False)
        element2 = ContentElement("code", "code", 3, 3, True)

        section = LogicalSection(
            header=header, elements=[element1, element2], start_line=1, end_line=3
        )

        types = section.get_element_types()
        assert "header" in types
        assert "text" in types
        assert "code" in types


class TestMixedStrategy:
    """Test cases for MixedStrategy."""

    def test_strategy_properties(self):
        """Test basic strategy properties."""
        strategy = MixedStrategy()

        assert strategy.name == "mixed"
        assert strategy.priority == 2

    def test_can_handle_mixed_content(self):
        """Test can_handle with mixed content."""
        strategy = MixedStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.4
        analysis.list_ratio = 0.2
        analysis.table_ratio = 0.1
        analysis.text_ratio = 0.3
        analysis.complexity_score = 0.5

        config = ChunkConfig(min_complexity=0.3)

        assert strategy.can_handle(analysis, config) is True

    def test_can_handle_code_dominates(self):
        """Test can_handle when code dominates."""
        strategy = MixedStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.8  # Too high
        analysis.list_ratio = 0.1
        analysis.text_ratio = 0.1
        analysis.complexity_score = 0.5

        config = ChunkConfig(min_complexity=0.3)

        assert strategy.can_handle(analysis, config) is False

    def test_can_handle_insufficient_text(self):
        """Test can_handle with insufficient text."""
        strategy = MixedStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.5
        analysis.list_ratio = 0.4
        analysis.text_ratio = 0.1  # Too low
        analysis.complexity_score = 0.5

        config = ChunkConfig(min_complexity=0.3)

        assert strategy.can_handle(analysis, config) is False

    def test_calculate_quality_high_mixed(self):
        """Test quality calculation for highly mixed content."""
        strategy = MixedStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.4
        analysis.list_ratio = 0.2
        analysis.table_ratio = 0.1
        analysis.text_ratio = 0.3

        quality = strategy.calculate_quality(analysis)

        # Should be high quality
        assert quality > 0.8

    def test_calculate_quality_code_dominates(self):
        """Test quality calculation when code dominates."""
        strategy = MixedStrategy()

        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.8
        analysis.list_ratio = 0.1
        analysis.table_ratio = 0.05
        analysis.text_ratio = 0.05

        quality = strategy.calculate_quality(analysis)

        # Should be low quality (anti-pattern)
        assert quality <= 0.3

    def test_apply_empty_content(self):
        """Test applying strategy to empty content."""
        strategy = MixedStrategy()
        stage1_results = Mock(spec=Stage1Results)
        config = ChunkConfig.default()

        chunks = strategy.apply("", stage1_results, config)

        assert chunks == []

    def test_apply_simple_mixed_content(self):
        """Test applying strategy to simple mixed content."""
        strategy = MixedStrategy()

        # Real code block
        code_block = FencedBlock(
            content="def test(): pass",
            language="python",
            fence_type="```",
            fence_length=3,
            start_line=5,
            end_line=7,
            start_offset=50,
            end_offset=80,
            nesting_level=0,
            is_closed=True,
            raw_content="```python\ndef test(): pass\n```",
        )

        # Real Stage1Results with empty elements
        elements = ElementCollection()
        analysis = ContentAnalysis(
            total_chars=100,
            total_lines=10,
            total_words=20,
            code_ratio=0.4,
            text_ratio=0.6,
            code_block_count=1,
            header_count=1,
            content_type="mixed",
        )

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = [code_block]
        stage1_results.elements = elements
        stage1_results.analysis = analysis

        config = ChunkConfig.default()

        content = """# Introduction

This is some text.

```python
def test(): pass
```

More text here."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create at least one chunk
        assert len(chunks) >= 1

        # Check metadata
        for chunk in chunks:
            assert chunk.metadata["content_type"] == "mixed"
            assert "element_types" in chunk.metadata

    def test_group_into_logical_sections(self):
        """Test grouping elements into logical sections."""
        strategy = MixedStrategy()

        elements = [
            ContentElement("header", "# Title", 1, 1, False),
            ContentElement("text", "Text 1", 2, 2, False),
            ContentElement("code", "code", 3, 3, True),
            ContentElement("header", "## Subtitle", 4, 4, False),
            ContentElement("text", "Text 2", 5, 5, False),
        ]

        sections = strategy._group_into_logical_sections(elements)

        # Should create 2 sections (one per header)
        assert len(sections) == 2
        assert sections[0].header.content == "# Title"
        assert sections[1].header.content == "## Subtitle"

    def test_has_indivisible_elements(self):
        """Test checking for indivisible elements."""
        strategy = MixedStrategy()

        section = LogicalSection(
            header=None,
            elements=[
                ContentElement("text", "Text", 1, 1, False),
                ContentElement("code", "code", 2, 2, True),
            ],
            start_line=1,
            end_line=2,
        )

        assert strategy._has_indivisible_elements(section) is True

        section_no_indivisible = LogicalSection(
            header=None,
            elements=[
                ContentElement("text", "Text 1", 1, 1, False),
                ContentElement("text", "Text 2", 2, 2, False),
            ],
            start_line=1,
            end_line=2,
        )

        assert strategy._has_indivisible_elements(section_no_indivisible) is False

    def test_get_selection_reason(self):
        """Test selection reason generation."""
        strategy = MixedStrategy()

        # Can handle
        analysis = Mock(spec=ContentAnalysis)
        analysis.code_ratio = 0.4
        analysis.list_ratio = 0.2
        analysis.text_ratio = 0.4

        reason = strategy._get_selection_reason(analysis, True)
        assert "Mixed content" in reason
        assert "suitable" in reason

        # Cannot handle - code dominates
        analysis.code_ratio = 0.8
        reason = strategy._get_selection_reason(analysis, False)
        assert "dominates" in reason


class TestMixedStrategyIntegration:
    """Integration tests for MixedStrategy."""

    def test_realistic_tutorial_document(self):
        """Test with realistic tutorial document."""
        strategy = MixedStrategy()

        # Mock code blocks
        code_blocks = [
            Mock(
                content="def greet(name):\n    print(f'Hello, {name}')",
                raw_content="```python\ndef greet(name):\n    print(f'Hello, {name}')\n```",
                language="python",
                start_line=7,
                end_line=9,
            ),
            Mock(
                content="greet('Alice')",
                raw_content="```python\ngreet('Alice')\n```",
                language="python",
                start_line=15,
                end_line=17,
            ),
        ]

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = code_blocks

        config = ChunkConfig(max_chunk_size=800, min_chunk_size=200)

        content = """# Python Functions

## Introduction

Functions are reusable blocks of code.

```python
def greet(name):
    print(f'Hello, {name}')
```

## Usage

You can call functions like this:

```python
greet('Alice')
```

This will print "Hello, Alice"."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) >= 1

        # All chunks should be mixed type
        for chunk in chunks:
            assert chunk.metadata["content_type"] == "mixed"
            assert "element_types" in chunk.metadata

        # At least one chunk should have multiple element types
        multi_type_chunks = [
            c for c in chunks if len(c.metadata["element_types"].split(",")) >= 2
        ]
        assert len(multi_type_chunks) >= 1

    def test_mixed_content_with_indivisible_elements(self):
        """Test handling indivisible elements."""
        strategy = MixedStrategy()

        # Large code block
        large_code = "def large_function():\n" + "    # line\n" * 100 + "    pass"

        code_block = Mock(spec=FencedBlock)
        code_block.content = large_code
        code_block.raw_content = f"```python\n{large_code}\n```"
        code_block.language = "python"
        code_block.fence_type = "```"  # Add missing fence_type attribute
        code_block.start_line = 5
        code_block.end_line = 107

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = [code_block]

        config = ChunkConfig(max_chunk_size=500, min_chunk_size=100)

        content = """# Large Code Example

Text before code.

```python
{large_code}
```

Text after code."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create multiple chunks
        assert len(chunks) >= 2

        # Code block should be in separate chunk (indivisible)
        code_chunks = [
            c for c in chunks if "code" in c.metadata.get("element_types", "")
        ]
        assert len(code_chunks) >= 1

    def test_real_stage1_list_and_table_integration(self):
        """Test MixedStrategy with real Stage 1 list and table objects."""
        strategy = MixedStrategy()

        # Create real ListItem objects
        list_items = [
            ListItem(content="First item", level=0, marker="-", line=3, offset=20),
            ListItem(content="Second item", level=0, marker="-", line=4, offset=35),
        ]

        # Create real MarkdownList
        markdown_list = MarkdownList(
            type="unordered",
            items=list_items,
            start_line=3,
            end_line=4,
            max_nesting_level=0,
        )

        # Create real Table
        table = Table(
            headers=["Column A", "Column B"],
            rows=[["Value 1", "Value 2"], ["Value 3", "Value 4"]],
            start_line=6,
            end_line=9,
            column_count=2,
            alignment=["left", "left"],
        )

        # Create real ElementCollection
        elements = ElementCollection(lists=[markdown_list], tables=[table])

        # Create real ContentAnalysis
        analysis = ContentAnalysis(
            total_chars=200,
            total_lines=10,
            total_words=30,
            code_ratio=0.2,
            text_ratio=0.8,
            code_block_count=0,
            header_count=1,
            list_count=1,
            table_count=1,
            content_type="mixed",
        )

        # Create Stage1Results with real objects
        stage1_results = Mock(spec=Stage1Results)
        stage1_results.fenced_blocks = []
        stage1_results.elements = elements
        stage1_results.analysis = analysis

        config = ChunkConfig.default()

        content = """# Document

- First item
- Second item

| Column A | Column B |
|----------|----------|
| Value 1  | Value 2  |
| Value 3  | Value 4  |

Some text content."""

        chunks = strategy.apply(content, stage1_results, config)

        # Should create chunks
        assert len(chunks) >= 1

        # Note: This test validates that the integration works without AttributeError
        # The actual Stage 1 usage depends on the strategy's internal logic

        # Validate no AttributeError occurred by checking chunk creation succeeded
        assert all(chunk.content for chunk in chunks)
        assert all(chunk.start_line > 0 for chunk in chunks)


class TestMixedStrategyRealObjects:
    """Test MixedStrategy with real Stage 1 objects to catch AttributeError issues."""

    def test_list_processing_no_attribute_error(self):
        """Test that list processing doesn't cause AttributeError."""
        strategy = MixedStrategy()

        # Create real objects that would cause AttributeError with wrong field access
        list_items = [
            ListItem(content="Test item", level=0, marker="-", line=1, offset=0)
        ]
        markdown_list = MarkdownList(
            type="unordered",  # This is the correct field, not list_type
            items=list_items,
            start_line=1,
            end_line=1,
            max_nesting_level=0,
        )

        elements = ElementCollection(lists=[markdown_list])

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements
        stage1_results.fenced_blocks = []

        # This should not raise AttributeError
        try:
            strategy._detect_all_elements("- Test item", stage1_results)
            # If we get here, no AttributeError was raised
            assert True
        except AttributeError as e:
            pytest.fail(f"AttributeError raised: {e}")

    def test_table_processing_no_attribute_error(self):
        """Test that table processing doesn't cause AttributeError."""
        strategy = MixedStrategy()

        # Create real table that would cause AttributeError with wrong field access
        table = Table(
            headers=["A", "B"],  # This exists, not has_header
            rows=[["1", "2"]],
            start_line=1,
            end_line=3,
            column_count=2,
            alignment=["left", "left"],
        )

        elements = ElementCollection(tables=[table])

        stage1_results = Mock(spec=Stage1Results)
        stage1_results.elements = elements
        stage1_results.fenced_blocks = []

        # This should not raise AttributeError
        try:
            strategy._detect_all_elements(
                "| A | B |\n|---|---|\n| 1 | 2 |", stage1_results
            )
            # If we get here, no AttributeError was raised
            assert True
        except AttributeError as e:
            pytest.fail(f"AttributeError raised: {e}")
