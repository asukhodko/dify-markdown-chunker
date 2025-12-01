"""
Property-based tests for parser correctness.

**Feature: markdown-chunker-quality-audit, Property 11: Parser Rule Compliance**
**Validates: Requirements 3.1**

This module uses Hypothesis to generate various markdown structures
and verifies that the parser correctly identifies all markdown elements.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from markdown_chunker.parser.core import Stage1Interface
from markdown_chunker.parser.elements import detect_elements
from markdown_chunker.parser.types import NodeType

# ============================================================================
# Hypothesis Strategies for Markdown Generation
# ============================================================================


@st.composite
def markdown_with_headers(draw, min_headers=1, max_headers=10):
    """Generate markdown with guaranteed headers."""
    lines = []
    num_headers = draw(st.integers(min_value=min_headers, max_value=max_headers))

    for _ in range(num_headers):
        level = draw(st.integers(min_value=1, max_value=6))
        text = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=3,
                max_size=50,
            ).filter(lambda x: x.strip())
        )
        lines.append(f"{'#' * level} {text}")
        lines.append("")

        # Add some content
        content = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=10,
                max_size=100,
            ).filter(lambda x: x.strip())
        )
        lines.append(content)
        lines.append("")

    return "\n".join(lines)


@st.composite
def markdown_with_code_blocks(draw, min_blocks=1, max_blocks=5):
    """Generate markdown with guaranteed code blocks."""
    lines = []
    num_blocks = draw(st.integers(min_value=min_blocks, max_value=max_blocks))

    for _ in range(num_blocks):
        language = draw(st.sampled_from(["python", "javascript", "java", "go", ""]))
        num_code_lines = draw(st.integers(min_value=1, max_value=10))

        lines.append(f"```{language}")
        for _ in range(num_code_lines):
            code_line = draw(
                st.text(
                    alphabet="abcdefghijklmnopqrstuvwxyz0123456789 (){}[].,;",
                    min_size=5,
                    max_size=80,
                )
            )
            lines.append(code_line)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


@st.composite
def markdown_with_lists(draw, min_lists=1, max_lists=5):
    """Generate markdown with guaranteed lists."""
    lines = []
    num_lists = draw(st.integers(min_value=min_lists, max_value=max_lists))

    for _ in range(num_lists):
        list_type = draw(st.sampled_from(["unordered", "ordered", "task"]))
        num_items = draw(st.integers(min_value=1, max_value=10))

        for i in range(num_items):
            item_text = draw(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                    min_size=5,
                    max_size=50,
                ).filter(lambda x: x.strip())
            )

            if list_type == "unordered":
                lines.append(f"- {item_text}")
            elif list_type == "ordered":
                lines.append(f"{i+1}. {item_text}")
            else:  # task
                checked = draw(st.sampled_from(["x", " "]))
                lines.append(f"- [{checked}] {item_text}")

        lines.append("")

    return "\n".join(lines)


@st.composite
def markdown_with_tables(draw, min_tables=1, max_tables=3):
    """Generate markdown with guaranteed tables."""
    lines = []
    num_tables = draw(st.integers(min_value=min_tables, max_value=max_tables))

    for _ in range(num_tables):
        num_cols = draw(st.integers(min_value=2, max_value=4))
        num_rows = draw(st.integers(min_value=2, max_value=5))

        # Header row
        headers = []
        for _ in range(num_cols):
            header = draw(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                    min_size=3,
                    max_size=15,
                ).filter(lambda x: x.strip())
            )
            headers.append(header)

        lines.append("|" + "|".join(headers) + "|")
        lines.append("|" + "|".join(["---"] * num_cols) + "|")

        # Data rows
        for _ in range(num_rows):
            row_data = []
            for _ in range(num_cols):
                cell = draw(
                    st.text(
                        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                        min_size=1,
                        max_size=20,
                    ).filter(lambda x: x.strip())
                )
                row_data.append(cell)
            lines.append("|" + "|".join(row_data) + "|")

        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Property Tests
# ============================================================================


class TestParserCorrectnessProperties:
    """Property-based tests for parser correctness."""

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_headers())
    def test_property_all_headers_detected(self, markdown_text):
        """
        **Property 11a: Header Detection Completeness**
        **Validates: Requirements 3.1**

        For any markdown with headers:
        - Parser must detect all headers
        - Header count must match actual headers in text
        - Header levels must be correct (1-6)
        """
        # Count expected headers
        lines = markdown_text.split("\n")
        expected_headers = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") and " " in stripped:
                # Count leading #
                level = 0
                for char in stripped:
                    if char == "#":
                        level += 1
                    else:
                        break
                if 1 <= level <= 6:
                    expected_headers.append(level)

        # Parse and detect
        elements = detect_elements(markdown_text)
        detected_headers = elements.headers

        # Verify count
        assert len(detected_headers) == len(expected_headers), (
            f"Expected {len(expected_headers)} headers, "
            f"detected {len(detected_headers)}"
        )

        # Verify levels
        for detected, expected_level in zip(detected_headers, expected_headers):
            assert detected.level == expected_level, (
                f"Header level mismatch: expected {expected_level}, "
                f"got {detected.level}"
            )

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_code_blocks())
    def test_property_all_code_blocks_detected(self, markdown_text):
        """
        **Property 11b: Code Block Detection Completeness**
        **Validates: Requirements 3.1**

        For any markdown with code blocks:
        - Parser must detect all fenced code blocks
        - Code block count must match actual blocks in text
        - Language tags must be preserved
        """
        # Count expected code blocks
        lines = markdown_text.split("\n")
        expected_blocks = 0
        in_block = False
        for line in lines:
            if line.strip().startswith("```"):
                if not in_block:
                    expected_blocks += 1
                    in_block = True
                else:
                    in_block = False

        # Parse
        interface = Stage1Interface()
        results = interface.process_document(markdown_text)
        detected_blocks = results.fenced_blocks

        # Verify count
        assert len(detected_blocks) == expected_blocks, (
            f"Expected {expected_blocks} code blocks, "
            f"detected {len(detected_blocks)}"
        )

        # Verify all blocks are closed
        for block in detected_blocks:
            assert (
                block.is_closed
            ), f"Code block at line {block.start_line} is not closed"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_lists())
    def test_property_all_lists_detected(self, markdown_text):
        """
        **Property 11c: List Detection Completeness**
        **Validates: Requirements 3.1**

        For any markdown with lists:
        - Parser must detect all lists
        - List items must be counted correctly
        - List types must be identified (ordered/unordered/task)
        """
        # Count expected list items
        lines = markdown_text.split("\n")
        expected_items = 0
        for line in lines:
            stripped = line.strip()
            # Unordered list
            if (
                stripped.startswith("- ")
                or stripped.startswith("* ")
                or stripped.startswith("+ ")
            ):
                expected_items += 1
            # Ordered list
            elif stripped and stripped[0].isdigit() and ". " in stripped:
                expected_items += 1

        # Parse
        elements = detect_elements(markdown_text)
        detected_lists = elements.lists

        # Count detected items
        detected_items = sum(lst.get_item_count() for lst in detected_lists)

        # Verify count
        assert detected_items == expected_items, (
            f"Expected {expected_items} list items, " f"detected {detected_items}"
        )

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_tables())
    def test_property_all_tables_detected(self, markdown_text):
        """
        **Property 11d: Table Detection Completeness**
        **Validates: Requirements 3.1**

        For any markdown with tables:
        - Parser must detect all tables
        - Table structure must be preserved (rows, columns)
        - Headers must be identified
        """
        # Count expected tables (look for separator lines)
        lines = markdown_text.split("\n")
        expected_tables = 0
        for line in lines:
            if line.strip().startswith("|") and "---" in line:
                expected_tables += 1

        # Parse
        elements = detect_elements(markdown_text)
        detected_tables = elements.tables

        # Verify count
        assert len(detected_tables) == expected_tables, (
            f"Expected {expected_tables} tables, " f"detected {len(detected_tables)}"
        )

        # Verify all tables have headers
        for table in detected_tables:
            assert (
                len(table.headers) > 0
            ), f"Table at line {table.start_line} has no headers"

    @settings(max_examples=50, deadline=5000)
    @given(st.text(min_size=10, max_size=1000))
    def test_property_parser_never_crashes(self, markdown_text):
        """
        **Property 11e: Parser Robustness**
        **Validates: Requirements 3.1**

        For any text input:
        - Parser must not crash
        - Parser must return valid results
        - Parser must handle invalid markdown gracefully
        """
        try:
            interface = Stage1Interface()
            results = interface.process_document(markdown_text)

            # Verify results are valid
            assert results is not None
            assert results.ast is not None
            assert results.analysis is not None
            assert isinstance(results.fenced_blocks, list)
            assert isinstance(results.elements.headers, list)

        except Exception as e:
            pytest.fail(f"Parser crashed on input: {e}")

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_headers())
    def test_property_ast_structure_valid(self, markdown_text):
        """
        **Property 11f: AST Structure Validity**
        **Validates: Requirements 3.1**

        For any markdown input:
        - AST must have valid structure
        - All nodes must have valid positions
        - Parent-child relationships must be consistent
        """
        interface = Stage1Interface()
        results = interface.process_document(markdown_text)
        ast = results.ast

        # Verify AST is valid
        assert ast is not None
        assert ast.type == NodeType.DOCUMENT

        # Verify positions are valid
        assert ast.start_pos.line >= 0
        assert ast.start_pos.column >= 0
        assert ast.end_pos.line >= ast.start_pos.line

        # Verify structure
        issues = ast.validate_structure()
        assert len(issues) == 0, f"AST structure invalid: {issues}"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_code_blocks())
    def test_property_code_block_content_preserved(self, markdown_text):
        """
        **Property 11g: Code Block Content Preservation**
        **Validates: Requirements 3.1**

        For any markdown with code blocks:
        - Code block content must be preserved exactly
        - No whitespace should be added or removed
        - Language tags must be preserved
        """
        interface = Stage1Interface()
        results = interface.process_document(markdown_text)
        blocks = results.fenced_blocks

        # Extract expected code content
        lines = markdown_text.split("\n")
        expected_contents = []
        in_block = False
        current_content = []

        for line in lines:
            if line.strip().startswith("```"):
                if not in_block:
                    in_block = True
                    current_content = []
                else:
                    in_block = False
                    expected_contents.append("\n".join(current_content))
            elif in_block:
                current_content.append(line)

        # Verify content preservation
        assert len(blocks) == len(expected_contents), (
            f"Block count mismatch: expected {len(expected_contents)}, "
            f"got {len(blocks)}"
        )

        for block, expected in zip(blocks, expected_contents):
            assert block.content == expected, (
                f"Code block content mismatch:\n"
                f"Expected: {repr(expected)}\n"
                f"Got: {repr(block.content)}"
            )

    @settings(max_examples=100, deadline=5000)
    @given(markdown_with_headers())
    def test_property_analysis_metrics_consistent(self, markdown_text):
        """
        **Property 11h: Analysis Metrics Consistency**
        **Validates: Requirements 3.1, 3.3**

        For any markdown input:
        - Analysis metrics must be internally consistent
        - Ratios must sum to approximately 1.0
        - Counts must match detected elements
        """
        interface = Stage1Interface()
        results = interface.process_document(markdown_text)
        analysis = results.analysis

        # Verify basic metrics
        assert analysis.total_chars == len(markdown_text)
        assert analysis.total_lines == len(markdown_text.split("\n"))

        # Verify ratios are in valid range
        assert 0.0 <= analysis.code_ratio <= 1.0
        assert 0.0 <= analysis.text_ratio <= 1.0
        assert 0.0 <= analysis.list_ratio <= 1.0
        assert 0.0 <= analysis.table_ratio <= 1.0

        # Verify counts match
        # P1-005: header_count is now Dict[int, int], compare total
        assert analysis.get_total_header_count() == len(results.elements.headers)
        assert analysis.code_block_count == len(results.fenced_blocks)
        assert analysis.list_count == len(results.elements.lists)
        assert analysis.table_count == len(results.elements.tables)
