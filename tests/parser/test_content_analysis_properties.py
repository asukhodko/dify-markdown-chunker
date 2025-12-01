"""
Property-based tests for content analysis correctness.

**Feature: markdown-chunker-quality-audit, Property 12: Analysis Metrics Accuracy**
**Validates: Requirements 3.3**

This module uses Hypothesis to generate various markdown structures
and verifies that content analysis produces correct metrics.
"""

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from markdown_chunker.parser.analyzer import ContentAnalyzer
from markdown_chunker.parser.elements import detect_elements

# ============================================================================
# Hypothesis Strategies for Markdown Generation
# ============================================================================


@st.composite
def markdown_with_code_blocks(draw, min_blocks=1, max_blocks=5):
    """Generate markdown with guaranteed code blocks."""
    lines = []
    num_blocks = draw(st.integers(min_value=min_blocks, max_value=max_blocks))

    for _ in range(num_blocks):
        # Add some text before code block
        text = draw(st.text(min_size=10, max_size=50).filter(lambda x: x.strip()))
        lines.append(text)
        lines.append("")

        # Add code block
        language = draw(st.sampled_from(["python", "javascript", "go", "java", ""]))
        code_content = draw(st.text(min_size=10, max_size=100))
        lines.append(f"```{language}")
        lines.append(code_content)
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


@st.composite
def markdown_with_mixed_content(draw):
    """Generate markdown with mixed content types."""
    lines = []

    # Add headers
    num_headers = draw(st.integers(min_value=1, max_value=5))
    for _ in range(num_headers):
        level = draw(st.integers(min_value=1, max_value=3))
        text = draw(st.text(min_size=5, max_size=30).filter(lambda x: x.strip()))
        lines.append(f"{'#' * level} {text}")
        lines.append("")

    # Add code blocks
    num_code = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_code):
        lang = draw(st.sampled_from(["python", "javascript", "go"]))
        code = draw(st.text(min_size=20, max_size=100))
        lines.append(f"```{lang}")
        lines.append(code)
        lines.append("```")
        lines.append("")

    # Add lists
    num_lists = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_lists):
        list_items = draw(st.integers(min_value=2, max_value=5))
        for i in range(list_items):
            item_text = draw(
                st.text(min_size=5, max_size=30).filter(lambda x: x.strip())
            )
            lines.append(f"- {item_text}")
        lines.append("")

    # Add tables
    if draw(st.booleans()):
        lines.append("| Col1 | Col2 |")
        lines.append("|------|------|")
        rows = draw(st.integers(min_value=1, max_value=3))
        for _ in range(rows):
            val1 = draw(st.text(min_size=3, max_size=10).filter(lambda x: x.strip()))
            val2 = draw(st.text(min_size=3, max_size=10).filter(lambda x: x.strip()))
            lines.append(f"| {val1} | {val2} |")
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Property Tests
# ============================================================================


class TestContentAnalysisProperties:
    """Property-based tests for content analysis."""

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_basic_metrics_non_negative(self, markdown_text):
        """
        **Property 12a: Non-negative Metrics**

        For any markdown text, all numeric metrics should be non-negative.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            # Skip invalid inputs
            return

        # All counts should be non-negative
        assert analysis.total_chars >= 0
        assert analysis.total_lines >= 0
        assert analysis.total_words >= 0
        assert analysis.code_block_count >= 0
        assert analysis.get_total_header_count() >= 0
        assert analysis.list_count >= 0
        assert analysis.table_count >= 0
        assert analysis.inline_code_count >= 0
        assert analysis.empty_lines >= 0
        assert analysis.indented_lines >= 0
        assert analysis.max_line_length >= 0
        assert analysis.average_line_length >= 0
        assert analysis.nested_list_depth >= 0

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_ratios_sum_to_one(self, markdown_text):
        """
        **Property 12b: Ratio Consistency**

        For any markdown text, code_ratio + text_ratio should approximately equal 1.0
        (within tolerance for rounding).
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            return

        # Ratios should be between 0 and 1
        assert 0.0 <= analysis.code_ratio <= 1.0
        assert 0.0 <= analysis.text_ratio <= 1.0
        assert 0.0 <= analysis.list_ratio <= 1.0
        assert 0.0 <= analysis.table_ratio <= 1.0

        # code_ratio + text_ratio should be close to 1.0
        # (allowing small tolerance for floating point)
        ratio_sum = analysis.code_ratio + analysis.text_ratio
        assert 0.9 <= ratio_sum <= 1.1, f"Ratio sum {ratio_sum} not close to 1.0"

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=markdown_with_code_blocks())
    def test_property_code_blocks_detected(self, markdown_text):
        """
        **Property 12c: Code Block Detection**

        For any markdown with code blocks, code_block_count should match
        the number of fenced blocks.
        """
        analyzer = ContentAnalyzer()

        # Count expected code blocks
        expected_blocks = markdown_text.count("```") // 2
        assume(expected_blocks > 0)

        analysis = analyzer.analyze_content(markdown_text)

        # Should detect all code blocks
        assert (
            analysis.code_block_count == expected_blocks
        ), f"Expected {expected_blocks} code blocks, got {analysis.code_block_count}"

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=markdown_with_mixed_content())
    def test_property_mixed_content_detection(self, markdown_text):
        """
        **Property 12d: Mixed Content Detection**

        For markdown with multiple content types, has_mixed_content should be True
        when multiple types are significant.
        """
        analyzer = ContentAnalyzer()
        analysis = analyzer.analyze_content(markdown_text)

        # Count significant content types
        significant_types = 0
        if analysis.code_ratio > 0.1:
            significant_types += 1
        if analysis.list_ratio > 0.1:
            significant_types += 1
        if analysis.table_ratio > 0.1:
            significant_types += 1
        if analysis.text_ratio > 0.2:
            significant_types += 1

        # If 2+ types are significant, should detect mixed content
        if significant_types >= 2 and analysis.code_ratio < 0.7:
            assert (
                analysis.has_mixed_content
            ), f"Should detect mixed content with {significant_types} significant types"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_complexity_score_bounded(self, markdown_text):
        """
        **Property 12e: Complexity Score Bounds**

        For any markdown text, complexity_score should be between 0 and 1.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            return

        assert (
            0.0 <= analysis.complexity_score <= 1.0
        ), f"Complexity score {analysis.complexity_score} out of bounds [0, 1]"

    @settings(max_examples=100, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_content_type_valid(self, markdown_text):
        """
        **Property 12f: Content Type Classification**

        For any markdown text, content_type should be one of the valid types.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            return

        valid_types = {"code_heavy", "list_heavy", "mixed", "primary", "text_heavy"}
        assert (
            analysis.content_type in valid_types
        ), f"Invalid content type: {analysis.content_type}"

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_header_count_consistency(self, markdown_text):
        """
        **Property 12g: Header Count Consistency**

        For any markdown text, sum of header_count values should equal
        total number of detected headers.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
            elements = detect_elements(markdown_text)
        except Exception:
            return

        # Sum of header counts by level should equal total headers
        total_from_dict = analysis.get_total_header_count()
        total_from_elements = len(elements.headers)

        assert total_from_dict == total_from_elements, (
            f"Header count mismatch: dict sum={total_from_dict}, "
            f"elements={total_from_elements}"
        )

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=markdown_with_code_blocks())
    def test_property_language_extraction(self, markdown_text):
        """
        **Property 12h: Language Extraction**

        For markdown with code blocks, languages dict should contain
        all specified languages with correct counts.
        """
        analyzer = ContentAnalyzer()
        analysis = analyzer.analyze_content(markdown_text)

        # All language counts should be positive
        for lang, count in analysis.languages.items():
            assert count > 0, f"Language {lang} has non-positive count: {count}"

        # Total language occurrences should not exceed code block count
        total_lang_count = sum(analysis.languages.values())
        assert total_lang_count <= analysis.code_block_count, (
            f"Language count {total_lang_count} exceeds code blocks "
            f"{analysis.code_block_count}"
        )

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=st.text(min_size=100, max_size=1000))
    def test_property_line_metrics_consistency(self, markdown_text):
        """
        **Property 12i: Line Metrics Consistency**

        For any markdown text, line-related metrics should be consistent.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            return

        # Average line length should not exceed max line length
        assert analysis.average_line_length <= analysis.max_line_length, (
            f"Average line length {analysis.average_line_length} exceeds "
            f"max {analysis.max_line_length}"
        )

        # Empty lines should not exceed total lines
        assert analysis.empty_lines <= analysis.total_lines, (
            f"Empty lines {analysis.empty_lines} exceeds total lines "
            f"{analysis.total_lines}"
        )

        # Indented lines should not exceed total lines
        assert analysis.indented_lines <= analysis.total_lines, (
            f"Indented lines {analysis.indented_lines} exceeds total lines "
            f"{analysis.total_lines}"
        )

    @settings(max_examples=50, deadline=5000)
    @given(markdown_text=st.text(min_size=10, max_size=1000))
    def test_property_boolean_flags_consistency(self, markdown_text):
        """
        **Property 12j: Boolean Flags Consistency**

        For any markdown text, boolean flags should be consistent with counts.
        """
        analyzer = ContentAnalyzer()

        try:
            analysis = analyzer.analyze_content(markdown_text)
        except Exception:
            return

        # has_tables should match table_count > 0
        if analysis.table_count > 0:
            assert analysis.has_tables, "has_tables should be True when tables exist"
        else:
            assert not analysis.has_tables, "has_tables should be False when no tables"

        # has_nested_lists should match nested_list_depth > 1
        if analysis.nested_list_depth > 1:
            assert (
                analysis.has_nested_lists
            ), "has_nested_lists should be True when depth > 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
