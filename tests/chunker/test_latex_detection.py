"""Unit tests for LaTeX formula detection in Parser.

Tests extraction of:
- Display math ($$...$$)
- LaTeX environments (equation, align, gather, etc.)
- Edge cases (unclosed formulas, LaTeX in code blocks)
"""

from markdown_chunker_v2.parser import Parser
from markdown_chunker_v2.types import LatexType


class TestDisplayMathExtraction:
    """Tests for display math ($$...$$) extraction."""

    def test_single_line_display_math(self):
        """Single-line display math is extracted."""
        text = "Here is a formula: $$x^2 + y^2 = z^2$$ and more text."
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        assert len(result.latex_blocks) == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.DISPLAY
        assert "$$x^2 + y^2 = z^2$$" in block.content

    def test_multiline_display_math(self):
        """Multiline display math is extracted."""
        text = """Formula:

$$
x = \\frac{-b \\pm \\sqrt{b^2}}{2a}
$$

Done."""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.DISPLAY
        assert block.start_line == 3
        assert block.end_line == 5
        assert "$$" in block.content
        assert "\\frac" in block.content

    def test_multiple_display_formulas(self):
        """Multiple display formulas are extracted."""
        text = """First: $$a^2$$

Second:

$$
b = c
$$"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 2
        assert all(b.latex_type == LatexType.DISPLAY for b in result.latex_blocks)


class TestEnvironmentExtraction:
    """Tests for LaTeX environment extraction."""

    def test_equation_environment(self):
        """Equation environment is extracted."""
        text = """Text before

\\begin{equation}
E = mc^2
\\end{equation}

Text after"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.ENVIRONMENT
        assert block.environment_name == "equation"
        assert "E = mc^2" in block.content

    def test_align_environment(self):
        """Align environment is extracted."""
        text = """\\begin{align}
a &= b \\\\
c &= d
\\end{align}"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.ENVIRONMENT
        assert block.environment_name == "align"

    def test_starred_environment(self):
        """Starred environment (equation*) is extracted."""
        text = """\\begin{equation*}
x = 1
\\end{equation*}"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.ENVIRONMENT
        assert block.environment_name == "equation"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_latex_in_code_block_ignored(self):
        """LaTeX inside code blocks is not extracted."""
        text = """```latex
$$
x = 1
$$
```"""
        parser = Parser()
        result = parser.analyze(text)

        # Should have 1 code block, 0 LaTeX blocks
        assert result.code_block_count == 1
        assert result.latex_block_count == 0

    def test_unclosed_display_math(self):
        """Unclosed display math extends to document end."""
        text = """$$
x = 1
# This is still in the unclosed formula"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_block_count == 1
        block = result.latex_blocks[0]
        assert block.latex_type == LatexType.DISPLAY
        # Should include everything to the end
        assert "# This is still" in block.content

    def test_empty_display_math_with_content(self):
        """Display math with only delimiters on separate lines."""
        text = """$$
$$"""
        parser = Parser()
        result = parser.analyze(text)

        # Should still extract it even though empty
        assert result.latex_block_count == 1

    def test_latex_ratio_calculated(self):
        """LaTeX ratio metric is calculated."""
        text = """Short text.

$$
This is a much longer LaTeX formula that takes up more space
$$"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.latex_ratio > 0
        # LaTeX content should be significant portion
        assert result.latex_ratio > 0.3


class TestMixedContent:
    """Tests for mixed LaTeX and other content."""

    def test_latex_and_code_blocks(self):
        """LaTeX and code blocks coexist."""
        text = """Formula: $$x=1$$

```python
print("hello")
```

Another formula:

\\begin{equation}
y = 2
\\end{equation}"""
        parser = Parser()
        result = parser.analyze(text)

        assert result.code_block_count == 1
        assert result.latex_block_count == 2

    def test_latex_with_headers(self):
        """LaTeX blocks with markdown headers."""
        text = """# Math Section

## Quadratic Formula

$$x = \\frac{-b}{2a}$$

### Explanation

Text here."""
        parser = Parser()
        result = parser.analyze(text)

        assert result.header_count == 3
        assert result.latex_block_count == 1
