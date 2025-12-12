"""
Integration tests for LaTeX formula handling across all strategies.

Tests that LaTeX formulas (display math and environments) are preserved
as atomic blocks and never split across chunks, regardless of which
chunking strategy is used.
"""

import pytest

from markdown_chunker_v2.chunker import MarkdownChunker
from markdown_chunker_v2.config import ChunkConfig


class TestCodeAwareStrategyLatex:
    """Test LaTeX preservation in CodeAwareStrategy."""

    def test_latex_with_code_blocks(self):
        """LaTeX and code blocks both preserved as atomic."""
        text = """# Mixed Content

Here's some code:

```python
def hello():
    print("world")
```

And a formula:

$$
E = mc^2
$$

More text here.
"""
        config = ChunkConfig(max_chunk_size=200, overlap_size=0)
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "code_aware"

        # Verify formulas not split
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert (
                display_count % 2 == 0
            ), f"Formula split across chunks! Count: {display_count}"

    def test_latex_corpus_machine_learning(self):
        """Test with ML equations corpus file."""
        with open("tests/corpus/scientific/machine-learning-equations.md") as f:
            text = f.read()

        config = ChunkConfig(
            max_chunk_size=1500, overlap_size=0, strategy_override="code_aware"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "code_aware"
        assert len(chunks) > 0

        # Verify all formulas balanced
        for i, chunk in enumerate(chunks):
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0, f"Chunk {i} has unbalanced formulas"


class TestStructuralStrategyLatex:
    """Test LaTeX preservation in StructuralStrategy."""

    def test_latex_in_structured_document(self):
        """LaTeX formulas preserved when splitting structured sections."""
        text = """# Chapter 1

## Section 1.1

Some introduction text here that goes on for a while.

$$
x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}
$$

More text after the formula.

## Section 1.2

Another section with content.

$$
F = ma
$$

Final text.
"""
        config = ChunkConfig(
            max_chunk_size=150, overlap_size=0, strategy_override="structural"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "structural"

        # Verify formulas not split
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0

    def test_latex_corpus_physics(self):
        """Test with physics equations corpus file."""
        with open("tests/corpus/scientific/physics-equations.md") as f:
            text = f.read()

        config = ChunkConfig(
            max_chunk_size=1200, overlap_size=0, strategy_override="structural"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "structural"

        # Verify all formulas balanced
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0

    def test_latex_corpus_calculus(self):
        """Test with calculus corpus file."""
        with open("tests/corpus/scientific/calculus-analysis.md") as f:
            text = f.read()

        config = ChunkConfig(
            max_chunk_size=1000, overlap_size=0, strategy_override="structural"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "structural"

        # Verify all formulas balanced
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0


class TestFallbackStrategyLatex:
    """Test LaTeX preservation in FallbackStrategy."""

    def test_latex_in_simple_document(self):
        """LaTeX formulas preserved in simple documents."""
        text = """Some text here.

$$
a^2 + b^2 = c^2
$$

More text.

$$
e^{i\\pi} + 1 = 0
$$

Final paragraph.
"""
        config = ChunkConfig(
            max_chunk_size=100, overlap_size=0, strategy_override="fallback"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert chunks[0].metadata["strategy"] == "fallback"

        # Verify formulas not split
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0

    def test_latex_chunks_marked_atomic(self):
        """LaTeX chunks have correct metadata."""
        text = """Text before.

$$
x = 1
$$

Text after.
"""
        config = ChunkConfig(
            max_chunk_size=50, overlap_size=0, strategy_override="fallback"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        # Find LaTeX chunks
        latex_chunks = [c for c in chunks if c.metadata.get("content_type") == "latex"]
        assert len(latex_chunks) > 0

        # Verify atomic metadata
        for chunk in latex_chunks:
            assert chunk.metadata.get("is_atomic") is True


class TestListAwareStrategyLatex:
    """Test LaTeX preservation in ListAwareStrategy."""

    def test_latex_in_list_introduction(self):
        """LaTeX in introduction paragraph preserved with list."""
        text = """The quadratic formula is $$x = \\frac{-b}{2a}$$

- First item
- Second item with formula $$y = mx + b$$ inline
- Third item
- Fourth item
- Fifth item
- Sixth item
- Seventh item
"""
        config = ChunkConfig(
            max_chunk_size=200, overlap_size=0, strategy_override="list_aware"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        # Verify formulas not split
        for chunk in chunks:
            display_count = chunk.content.count("$$")
            assert display_count % 2 == 0


class TestLatexAcrossAllCorpus:
    """Test LaTeX handling with all scientific corpus files."""

    @pytest.mark.parametrize(
        "filename",
        [
            "machine-learning-equations.md",
            "statistics-fundamentals.md",
            "calculus-analysis.md",
            "linear-algebra-essentials.md",
            "physics-equations.md",
            "neural-network-backprop.md",
        ],
    )
    def test_corpus_file_no_split_formulas(self, filename):
        """Verify no LaTeX formulas split in corpus file."""
        filepath = f"tests/corpus/scientific/{filename}"
        with open(filepath) as f:
            text = f.read()

        # Use default strategy selection
        config = ChunkConfig(max_chunk_size=1500, overlap_size=0)
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        assert len(chunks) > 0

        # Verify all formulas balanced
        for i, chunk in enumerate(chunks):
            display_count = chunk.content.count("$$")
            assert (
                display_count % 2 == 0
            ), f"{filename} chunk {i} has unbalanced formulas"

    @pytest.mark.parametrize(
        "filename",
        [
            "machine-learning-equations.md",
            "statistics-fundamentals.md",
            "calculus-analysis.md",
            "linear-algebra-essentials.md",
            "physics-equations.md",
            "neural-network-backprop.md",
        ],
    )
    def test_corpus_file_environments_not_split(self, filename):
        """Verify LaTeX environments not split."""
        filepath = f"tests/corpus/scientific/{filename}"
        with open(filepath) as f:
            text = f.read()

        config = ChunkConfig(max_chunk_size=1000, overlap_size=0)
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        # Check for split environments
        for i, chunk in enumerate(chunks):
            content = chunk.content
            # Count begin/end pairs
            begin_count = content.count("\\begin{align}")
            end_count = content.count("\\end{align}")
            assert (
                begin_count == end_count
            ), f"{filename} chunk {i} has unbalanced align environment"


class TestLatexMetadata:
    """Test LaTeX-specific metadata."""

    def test_latex_chunk_has_correct_content_type(self):
        """LaTeX chunks marked with content_type='latex'."""
        text = """Text.

$$
x = 1
$$

More text.
"""
        config = ChunkConfig(
            max_chunk_size=50, overlap_size=0, strategy_override="code_aware"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        latex_chunks = [
            c for c in chunks if "$$" in c.content and c.content.count("$$") == 2
        ]

        # At least one chunk should be LaTeX
        assert len(latex_chunks) > 0

        # Check metadata
        for chunk in latex_chunks:
            if chunk.metadata.get("is_atomic"):
                assert chunk.metadata.get("content_type") in ["latex", "section"]

    def test_oversize_latex_marked_correctly(self):
        """Very large LaTeX formulas get oversize metadata."""
        # Create a large formula
        large_formula = "$$\n" + "x + " * 200 + "y\n$$"
        text = f"Text.\n\n{large_formula}\n\nMore text."

        config = ChunkConfig(
            max_chunk_size=100, overlap_size=0, strategy_override="fallback"
        )
        chunker = MarkdownChunker(config=config)
        chunks = chunker.chunk(text)

        # Find the LaTeX chunk
        latex_chunks = [c for c in chunks if "$$" in c.content]
        assert len(latex_chunks) > 0

        # Check for oversize metadata
        for chunk in latex_chunks:
            if chunk.size > config.max_chunk_size:
                assert chunk.metadata.get("allow_oversize") is True
                assert chunk.metadata.get("oversize_reason") == "latex_integrity"
