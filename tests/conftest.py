#!/usr/bin/env python3
"""
Shared test configuration and Hypothesis strategies for property-based testing.

This module provides:
- Hypothesis configuration (100+ iterations per property)
- Reusable markdown generators (headers, lists, code blocks, tables)
"""

from hypothesis import settings
from hypothesis import strategies as st

# Configure Hypothesis globally
settings.register_profile("default", max_examples=100, deadline=5000)
settings.load_profile("default")


# ============================================================================
# Markdown Structure Generators
# ============================================================================


@st.composite
def markdown_header(draw, min_level=1, max_level=6):
    """Generate a markdown header."""
    level = draw(st.integers(min_value=min_level, max_value=max_level))
    text = draw(
        st.text(
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
            min_size=3,
            max_size=50,
        ).filter(lambda x: x.strip())
    )
    return f"{'#' * level} {text}"


@st.composite
def markdown_paragraph(draw, min_size=20, max_size=200):
    """Generate a markdown paragraph."""
    text = draw(
        st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"),
                whitelist_characters=" .,!?-",
            ),
            min_size=min_size,
            max_size=max_size,
        ).filter(lambda x: x.strip())
    )
    return text


@st.composite
def markdown_list(draw, min_items=1, max_items=10):
    """Generate a markdown list."""
    num_items = draw(st.integers(min_value=min_items, max_value=max_items))
    items = []
    for _ in range(num_items):
        item = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")),
                min_size=5,
                max_size=50,
            ).filter(lambda x: x.strip())
        )
        items.append(f"- {item}")
    return "\n".join(items)


@st.composite
def markdown_code_block(draw, min_lines=1, max_lines=10):
    """Generate a markdown code block."""
    language = draw(st.sampled_from(["python", "javascript", "java", "go", ""]))
    num_lines = draw(st.integers(min_value=min_lines, max_value=max_lines))
    lines = []
    for _ in range(num_lines):
        line = draw(
            st.text(
                alphabet="abcdefghijklmnopqrstuvwxyz0123456789 (){}[].,;",
                min_size=5,
                max_size=80,
            )
        )
        lines.append(line)
    code = "\n".join(lines)
    return f"```{language}\n{code}\n```"


@st.composite
def markdown_table(draw, min_rows=2, max_rows=5, min_cols=2, max_cols=4):
    """Generate a markdown table."""
    num_rows = draw(st.integers(min_value=min_rows, max_value=max_rows))
    num_cols = draw(st.integers(min_value=min_cols, max_value=max_cols))

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

    # Separator row
    separator = "|" + "|".join(["---"] * num_cols) + "|"

    # Data rows
    rows = []
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
        rows.append("|" + "|".join(row_data) + "|")

    header_line = "|" + "|".join(headers) + "|"
    return "\n".join([header_line, separator] + rows)


@st.composite
def markdown_document(draw, min_sections=1, max_sections=5):
    """Generate a complete markdown document with various structures."""
    elements = []

    # Add title
    title = draw(markdown_header(min_level=1, max_level=1))
    elements.append(title)
    elements.append("")

    # Add sections
    num_sections = draw(st.integers(min_value=min_sections, max_value=max_sections))
    for _ in range(num_sections):
        # Section header
        header = draw(markdown_header(min_level=2, max_level=3))
        elements.append(header)
        elements.append("")

        # Section content (mix of different elements)
        content_type = draw(
            st.sampled_from(["paragraph", "list", "code", "table", "mixed"])
        )

        if content_type == "paragraph":
            para = draw(markdown_paragraph())
            elements.append(para)
            elements.append("")
        elif content_type == "list":
            lst = draw(markdown_list())
            elements.append(lst)
            elements.append("")
        elif content_type == "code":
            code = draw(markdown_code_block())
            elements.append(code)
            elements.append("")
        elif content_type == "table":
            table = draw(markdown_table())
            elements.append(table)
            elements.append("")
        else:  # mixed
            para = draw(markdown_paragraph())
            elements.append(para)
            elements.append("")
            lst = draw(markdown_list(min_items=1, max_items=3))
            elements.append(lst)
            elements.append("")

    return "\n".join(elements)


@st.composite
def nested_markdown_document(draw, max_depth=3):
    """Generate a markdown document with nested headers."""
    elements = []

    # Add title
    elements.append("# Main Title")
    elements.append("")

    def add_section(current_level, max_level):
        if current_level > max_level:
            return

        # Add header at current level
        header_text = draw(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                min_size=5,
                max_size=30,
            ).filter(lambda x: x.strip())
        )
        elements.append(f"{'#' * current_level} {header_text}")
        elements.append("")

        # Add content
        para = draw(markdown_paragraph(min_size=10, max_size=100))
        elements.append(para)
        elements.append("")

        # Maybe add subsections
        if current_level < max_level:
            num_subsections = draw(st.integers(min_value=0, max_value=2))
            for _ in range(num_subsections):
                add_section(current_level + 1, max_level)

    # Add top-level sections
    num_sections = draw(st.integers(min_value=1, max_value=3))
    for _ in range(num_sections):
        add_section(2, max_depth)

    return "\n".join(elements)
